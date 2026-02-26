from pathlib import Path
import time

import joblib
import librosa
import numpy as np
import soundfile as sf
import torch
from PIL import Image
from torchvision import models, transforms

# ----------------------------------------
# CONFIG
# ----------------------------------------

CLASS_NAMES = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]
DEVICE = "cpu"

AUDIO_TARGET_SR = 16000
AUDIO_MAX_DURATION_SEC = 8.0
AUDIO_MAX_SAMPLES = int(AUDIO_TARGET_SR * AUDIO_MAX_DURATION_SEC)
N_MFCC = 40

BASE_DIR = Path(__file__).resolve().parents[1]
MRI_MODEL_PATH = BASE_DIR / "outputs" / "best_model.pth"
AUDIO_MODEL_PATH = BASE_DIR / "models" / "audio_model.pkl"


# ----------------------------------------
# LOAD MODELS ONCE
# ----------------------------------------

def build_resnet18():
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, len(CLASS_NAMES))
    return model


def load_mri_model():
    model = build_resnet18()
    ckpt = torch.load(MRI_MODEL_PATH, map_location=DEVICE)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model


MRI_MODEL = load_mri_model()
AUDIO_MODEL = joblib.load(AUDIO_MODEL_PATH)

MRI_TRANSFORM = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])


# ----------------------------------------
# MRI
# ----------------------------------------

def predict_mri_probs(image: Image.Image):
    img_tensor = MRI_TRANSFORM(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = MRI_MODEL(img_tensor)
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()
    return probs


# ----------------------------------------
# AUDIO
# ----------------------------------------

def load_audio_fast(audio_path):
    with sf.SoundFile(audio_path) as f:
        src_sr = f.samplerate
        frames_to_read = int(AUDIO_MAX_DURATION_SEC * src_sr)
        y = f.read(frames=frames_to_read, dtype="float32", always_2d=False)

    if y.ndim == 2:
        y = np.mean(y, axis=1)

    if y.size == 0:
        return np.zeros(AUDIO_MAX_SAMPLES, dtype=np.float32)

    if src_sr != AUDIO_TARGET_SR:
        y = librosa.resample(
            y,
            orig_sr=src_sr,
            target_sr=AUDIO_TARGET_SR,
            res_type="kaiser_fast",
        )

    if y.shape[0] < AUDIO_MAX_SAMPLES:
        y = librosa.util.fix_length(y, size=AUDIO_MAX_SAMPLES)
    elif y.shape[0] > AUDIO_MAX_SAMPLES:
        y = y[:AUDIO_MAX_SAMPLES]

    return y.astype(np.float32, copy=False)


def extract_mfcc(audio_path):
    y = load_audio_fast(audio_path)
    mfcc = librosa.feature.mfcc(
        y=y,
        sr=AUDIO_TARGET_SR,
        n_mfcc=N_MFCC,
        n_fft=1024,
        hop_length=256,
    )
    return np.mean(mfcc.T, axis=0)


def predict_audio_probs(audio_path):
    features = extract_mfcc(audio_path).reshape(1, -1)
    prob = AUDIO_MODEL.predict_proba(features)[0]  # [healthy, impaired]

    out = np.zeros(4)
    out[2] = prob[0]  # NonDemented
    out[1] = prob[1]  # ModerateDemented
    return out


# ----------------------------------------
# COGNITIVE
# ----------------------------------------

def predict_cognitive_from_score(score: float) -> np.ndarray:
    s = float(score)
    non = s
    moderate = 1 - s

    out = np.zeros(4)
    out[2] = non
    out[1] = moderate
    return out


# ----------------------------------------
# FUSION
# ----------------------------------------

def fuse_predictions(mri, cog, aud,
                     wm=0.6, wc=0.25, wa=0.15):
    final = wm * np.array(mri) + wc * np.array(cog) + wa * np.array(aud)
    total = final.sum()
    if total <= 0:
        return np.ones(4) / 4
    return final / total


# ----------------------------------------
# MAIN PREDICT FUNCTION
# ----------------------------------------

def predict_all(mri_path, audio_path, cognitive_score):
    t0 = time.perf_counter()

    image = Image.open(mri_path).convert("RGB")
    mri_probs = predict_mri_probs(image)
    t1 = time.perf_counter()

    audio_probs = predict_audio_probs(audio_path)
    t2 = time.perf_counter()

    cognitive_probs = predict_cognitive_from_score(cognitive_score)
    final_probs = fuse_predictions(mri_probs, cognitive_probs, audio_probs)

    final_class = CLASS_NAMES[np.argmax(final_probs)]
    confidence = float(np.max(final_probs))

    print(
        f"[predict_all] total={t2 - t0:.2f}s mri={t1 - t0:.2f}s audio={t2 - t1:.2f}s",
        flush=True,
    )

    return {
        "predicted_class": final_class,
        "confidence": round(confidence, 4),
        "fused_probs": {
            CLASS_NAMES[i]: round(float(final_probs[i]), 4)
            for i in range(4)
        }
    }


# Warm up MFCC path so first user request is faster.
_ = librosa.feature.mfcc(
    y=np.zeros(AUDIO_MAX_SAMPLES, dtype=np.float32),
    sr=AUDIO_TARGET_SR,
    n_mfcc=N_MFCC,
    n_fft=1024,
    hop_length=256,
)
