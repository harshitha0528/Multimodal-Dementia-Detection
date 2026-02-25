from pathlib import Path
from tempfile import NamedTemporaryFile
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from inference import predict_all


# =====================================================
# FASTAPI INIT
# =====================================================

app = FastAPI(
    title="Multimodal Dementia Detection API",
    version="1.0.0"
)
app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")

@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")
# Allow frontend (React) access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health():
    return {"status": "ok"}


# =====================================================
# MULTIMODAL PREDICT ENDPOINT
# =====================================================

@app.post("/predict")
async def predict(
    # Files
    mri_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),

    # Cognitive Form Data
    cognitive_score:float = Form(...),
):
    temp_mri_path = None
    temp_audio_path = None

    try:
        # -----------------------------
        # Validate file names
        # -----------------------------
        if not mri_file.filename:
            raise HTTPException(status_code=400, detail="MRI file is required.")

        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="Audio file is required.")

        # -----------------------------
        # Save MRI temporarily
        # -----------------------------
        mri_suffix = Path(mri_file.filename).suffix or ".jpg"

        with NamedTemporaryFile(delete=False, suffix=mri_suffix) as temp_mri:
            temp_mri.write(await mri_file.read())
            temp_mri_path = temp_mri.name

        # -----------------------------
        # Save Audio temporarily
        # -----------------------------
        audio_suffix = Path(audio_file.filename).suffix or ".wav"

        with NamedTemporaryFile(delete=False, suffix=audio_suffix) as temp_audio:
            temp_audio.write(await audio_file.read())
            temp_audio_path = temp_audio.name

        # -----------------------------
        # Prepare Cognitive Data
        # -----------------------------
        #cognitive_data = {
         #  cognitive_score: cognitive_score
        #}

        # -----------------------------
        # Call Multimodal Inference
        # -----------------------------
        result = predict_all(
            mri_path=temp_mri_path,
            audio_path=temp_audio_path,
            cognitive_score=cognitive_score,
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    finally:
        # -----------------------------
        # Cleanup temporary files
        # -----------------------------
        if temp_mri_path and os.path.exists(temp_mri_path):
            os.remove(temp_mri_path)

        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)