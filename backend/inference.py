from pathlib import Path
import numpy as np
import torch
from torchvision import models, transforms
from PIL import Image
import joblib
import librosa
import soundfile as sf

# ----------------------------------------
# CONFIG
# ----------------------------------------

CLASS_NAMES = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]
DEVICE = "cpu"

BASE_DIR = Path(__file__).resolve().parents[1]
MRI_MODEL_PATH = BASE_DIR / "outputs" / "best_model.pth"
AUDIO_MODEL_PATH = BASE_DIR / "models" / "audio_model.pkl"
COG_MODEL_PATH = BASE_DIR / "outputs" / "cognitive_model.joblib"


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
COG_MODEL = joblib.load(COG_MODEL_PATH)


MRI_TRANSFORM = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],
                         [0.229,0.224,0.225])
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

def extract_mfcc(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
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

COG_FEATURES = [
    "cognitive_score"
]


def predict_cognitive_from_score(score: float) -> np.ndarray:
    s = float(score)

    # Assume score between 0 and 1
    # Higher score = healthier

    non = s
    moderate = 1 - s

    out = np.zeros(4)
    out[2] = non               # NonDemented
    out[1] = moderate          # ModerateDemented

    return out


# ----------------------------------------
# FUSION
# ----------------------------------------

def fuse_predictions(mri, cog, aud,
                     wm=0.6, wc=0.25, wa=0.15):
    final = wm*np.array(mri) + wc*np.array(cog) + wa*np.array(aud)
    return final / final.sum()


# ----------------------------------------
# MAIN PREDICT FUNCTION
# ----------------------------------------

def predict_all(mri_path, audio_path, cognitive_score):

    image = Image.open(mri_path).convert("RGB")

    mri_probs = predict_mri_probs(image)
    audio_probs = predict_audio_probs(audio_path)
    cognitive_probs = predict_cognitive_from_score(cognitive_score)

    final_probs = fuse_predictions(mri_probs, cognitive_probs, audio_probs)
    final_class = CLASS_NAMES[np.argmax(final_probs)]
    confidence = float(np.max(final_probs))

    return {
        "predicted_class": final_class,
        "confidence": round(confidence, 4),
        "fused_probs": {
            CLASS_NAMES[i]: round(float(final_probs[i]), 4)
            for i in range(4)
        }
    }