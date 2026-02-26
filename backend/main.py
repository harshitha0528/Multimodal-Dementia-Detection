from pathlib import Path
from tempfile import NamedTemporaryFile
import ast
import os
import time
from datetime import datetime

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .database import get_all_patients, init_db, insert_patient
from .inference import predict_all


# =====================================================
# FASTAPI INIT
# =====================================================

app = FastAPI(
    title="Multimodal Dementia Detection API",
    version="1.0.0"
)

init_db()

BACKEND_DIR = Path(__file__).resolve().parent

# Allow frontend (React) access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Backend is running",
        "health": "/health",
        "predict": "/predict",
        "reports": "/reports",
        "dashboard_metrics": "/dashboard-metrics",
    }


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/health")
async def health():
    return {"status": "ok"}


# =====================================================
# REPORT HISTORY
# =====================================================

@app.get("/reports")
async def reports():
    rows = get_all_patients()
    reports_list = []

    for row in rows:
        parsed_probs = None
        try:
            parsed_probs = ast.literal_eval(row["mri_prediction"]) if row["mri_prediction"] else None
        except Exception:
            parsed_probs = None

        reports_list.append(
            {
                "id": row["id"],
                "patient_name": row["patient_name"],
                "age": row["age"],
                "gender": row["gender"],
                "mobile_number": row["mobile_number"],
                "city": row["city"],
                "mri_prediction": parsed_probs,
                "audio_prediction": row["audio_prediction"],
                "cognitive_score": row["cognitive_score"],
                "final_prediction": row["final_prediction"],
                "confidence": row["confidence"],
                "date": row["date"],
            }
        )

    return {"reports": reports_list}


@app.get("/dashboard-metrics")
async def dashboard_metrics():
    rows = get_all_patients()

    # Overall (all-time) patient metrics.
    all_patients = set()
    high_risk_patients = set()
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_screenings = 0

    for row in rows:
        patient_name = str(row["patient_name"] or "").strip()
        mobile_number = str(row["mobile_number"] or "").strip()
        final_prediction = str(row["final_prediction"] or "").strip()
        date_str = str(row["date"] or "").strip()
        key = f"{patient_name.lower()}|{mobile_number.lower()}"

        if date_str.startswith(today_str):
            today_screenings += 1

        all_patients.add(key)
        if final_prediction and final_prediction != "NonDemented":
            high_risk_patients.add(key)

    return {
        "total_patients": len(all_patients),
        "today_screenings": today_screenings,
        "high_risk_alerts": len(high_risk_patients),
    }


# =====================================================
# MULTIMODAL PREDICT ENDPOINT
# =====================================================

@app.post("/predict")
async def predict(
    patient_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    mobile_number: str = Form(...),
    city: str = Form(...),
    cognitive_score: float = Form(...),
    mri_file: UploadFile = File(...),
    audio_file: UploadFile = File(...)
):
    temp_mri_path = None
    temp_audio_path = None
    t0 = time.perf_counter()

    try:
        if not mri_file.filename:
            raise HTTPException(status_code=400, detail="MRI file is required.")
        if not audio_file.filename:
            raise HTTPException(status_code=400, detail="Audio file is required.")

        mri_suffix = Path(mri_file.filename).suffix or ".jpg"
        with NamedTemporaryFile(delete=False, suffix=mri_suffix) as temp_mri:
            mri_bytes = await mri_file.read()
            temp_mri.write(mri_bytes)
            temp_mri_path = temp_mri.name

        audio_suffix = Path(audio_file.filename).suffix or ".wav"
        with NamedTemporaryFile(delete=False, suffix=audio_suffix) as temp_audio:
            audio_bytes = await audio_file.read()
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        print(
            f"[predict] received mri={len(mri_bytes)/(1024*1024):.2f}MB "
            f"audio={len(audio_bytes)/(1024*1024):.2f}MB",
            flush=True,
        )

        t1 = time.perf_counter()
        result = predict_all(
            mri_path=temp_mri_path,
            audio_path=temp_audio_path,
            cognitive_score=cognitive_score
        )
        t2 = time.perf_counter()

        patient_data = {
            "patient_name": patient_name,
            "age": age,
            "gender": gender,
            "mobile_number": mobile_number,
            "city": city,
            "mri_prediction": str(result["fused_probs"]),
            "audio_prediction": "Used",
            "cognitive_score": cognitive_score,
            "final_prediction": result["predicted_class"],
            "confidence": result["confidence"]
        }
        insert_patient(patient_data)
        t3 = time.perf_counter()

        print(
            f"[predict] total={t3 - t0:.2f}s save={t1 - t0:.2f}s infer={t2 - t1:.2f}s db={t3 - t2:.2f}s",
            flush=True,
        )

        return result

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    finally:
        if temp_mri_path and os.path.exists(temp_mri_path):
            os.remove(temp_mri_path)
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
