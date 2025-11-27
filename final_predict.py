import torch
from torchvision import transforms, models
from PIL import Image
import numpy as np
import joblib
import pandas as pd

# ---------------------------------------------
# CLASS LABELS (must match MRI trained model)
# ---------------------------------------------
CLASS_NAMES = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]


# =====================================================
# PART 1 — MRI PREDICTION
# =====================================================

def load_mri_model(model_path="outputs/best_model.pth"):
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, len(CLASS_NAMES))
    ckpt = torch.load(model_path, map_location="cpu")
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    return model

def preprocess_mri(image_path, img_size=128):
    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485,0.456,0.406],
                             [0.229,0.224,0.225])
    ])
    img = Image.open(image_path).convert("RGB")
    return transform(img).unsqueeze(0)

def predict_mri(model, img_tensor):
    with torch.no_grad():
        logits = model(img_tensor)
        probs = torch.softmax(logits, dim=1).numpy()[0]
    return probs



# =====================================================
# PART 2 — COGNITIVE PREDICTION
# =====================================================

COG_FEATURES = [
    "age",
    "education_years",
    "orientation_year_correct",
    "recall_3",
    "serial7_correct",
    "naming_correct",
    "clock_ok"
]

def load_cognitive_model(path="outputs/cognitive_model.joblib"):
    return joblib.load(path)

def load_cognitive_row(cog_csv, subject_id):
    df = pd.read_csv(cog_csv)
    row = df[df["subject_id"] == subject_id]
    if row.empty:
        print(f"[WARNING] No cognitive test found for: {subject_id}. Using zeros.")
        return {f: 0 for f in COG_FEATURES}
    row = row.iloc[0]
    return {f: row[f] for f in COG_FEATURES}

def predict_cognitive(model, cog_row):
    X = np.array([[cog_row[f] for f in COG_FEATURES]])
    # cognitive model is binary (0=healthy, 1=impaired)
    prob = model.predict_proba(X)[0]   # [prob_healthy, prob_impaired]

    final = np.zeros(4)
    final[2] = prob[0]   # NonDemented
    final[1] = prob[1]   # ModerateDemented
    return final



# =====================================================
# PART 3 — AUDIO PREDICTION
# =====================================================

def load_audio_probs(audio_csv, subject_id):
    df = pd.read_csv(audio_csv)
    row = df[df["name"] == subject_id]

    if row.empty:
        print(f"[WARNING] No audio features for: {subject_id}. Using neutral probs.")
        return np.array([0.25, 0.25, 0.25, 0.25])  # equal probability

    row = row.iloc[0]
    mod = row["prob_ModerateDemented"]
    non = row["prob_NonDemented"]

    out = np.zeros(4)
    out[2] = non           # NonDemented
    out[1] = mod           # ModerateDemented
    return out



# =====================================================
# PART 4 — FINAL MULTIMODAL FUSION
# =====================================================

def fuse_predictions(mri, cog, aud,
                     wm=0.7, wc=0.2, wa=0.1):
    final = wm*np.array(mri) + wc*np.array(cog) + wa*np.array(aud)
    return final / final.sum()   # normalize to 1.0



# =====================================================
# PART 5 — MAIN FUNCTION
# =====================================================

def predict_all(mri_path, subject_id,
                cog_csv="data/raw/cognitive/cognitive.csv",
                audio_csv="outputs/audio_probs.csv"):

    # MRI
    mri_model = load_mri_model()
    img_tensor = preprocess_mri(mri_path)
    mri_probs = predict_mri(mri_model, img_tensor)

    # Cognitive
    cog_model = load_cognitive_model()
    cog_row = load_cognitive_row(cog_csv, subject_id)
    cog_probs = predict_cognitive(cog_model, cog_row)

    # Audio
    audio_probs = load_audio_probs(audio_csv, subject_id)

    # Fuse
    final_probs = fuse_predictions(mri_probs, cog_probs, audio_probs)
    final_class = CLASS_NAMES[np.argmax(final_probs)]

    print("\n=== MRI Probabilities ===")
    print(dict(zip(CLASS_NAMES, mri_probs)))

    print("\n=== Cognitive Probabilities ===")
    print(dict(zip(CLASS_NAMES, cog_probs)))

    print("\n=== Audio Probabilities ===")
    print(dict(zip(CLASS_NAMES, audio_probs)))

    print("\n=== FINAL FUSED RESULT ===")
    print("Predicted:", final_class)
    print("Final Probabilities:", dict(zip(CLASS_NAMES, final_probs)))

    return final_class, final_probs



# =====================================================
# RUN DIRECTLY FROM TERMINAL
# =====================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument("--mri", type=str, required=True,
                        help="Path to MRI image (.jpg)")
    parser.add_argument("--id", type=str, required=True,
                        help="Subject ID (file stem)")
    args = parser.parse_args()

    predict_all(args.mri, args.id)
