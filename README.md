# Multimodal Dementia Detection

MRI + audio + cognitive score based dementia prediction with:
- FastAPI backend (`backend/`)
- React + Vite frontend (`frontend/`)

## Project structure

- `backend/main.py`: API endpoints (`/health`, `/predict`)
- `backend/inference.py`: model loading and fusion logic
- `final_predict.py`: original offline/CLI prediction pipeline
- `frontend/`: React UI that calls backend API

## Backend setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
npm install
npm run install:frontend
npm run dev
```

`npm run dev` starts both backend (`:8000`) and frontend (`:5173`) in one terminal.

## Individual start commands

```bash
npm run dev:backend
npm run dev:frontend
```

Frontend runs on `http://localhost:5173` and proxies `/api/*` to backend `http://127.0.0.1:8000`.

## API request

`POST /predict` with `multipart/form-data`:
- `mri_file` (required): jpg/jpeg/png
- `audio_file` (optional): wav/mp3
- `cognitive_score` (optional, default `10`, range `0-20`)

## Notes

- Current audio path is placeholder (`dummy` probabilities), same as the previous Streamlit behavior.
- Existing Streamlit app file (`app.py`) is kept for reference, but new UI flow is React + FastAPI.
