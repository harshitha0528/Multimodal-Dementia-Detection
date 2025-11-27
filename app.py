# app.py (final, robust + beautiful UI)
import streamlit as st
import numpy as np
from PIL import Image
import torch
from torchvision import transforms, models

# ---------------------------
# BEAUTIFUL UI CUSTOM CSS
# ---------------------------
st.set_page_config(page_title="Multimodal Dementia Detection", page_icon="🧠", layout="wide")
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #4c6ef5, #15aabf, #12b886);
    background-size: 400% 400%;
    animation: gradientBG 13s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

.logo-container {
    display: flex;
    justify-content: center;
    margin-top: -10px;
}

.header-title {
    font-size: 40px;
    color: white;
    text-align: center;
    font-weight: 700;
    margin-bottom: 0px;
    text-shadow: 2px 2px 5px rgba(0,0,0,0.3);
}

.glass-card {
    background: rgba(255, 255, 255, 0.18);
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 25px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    backdrop-filter: blur(12px);
}

input[type="file"] {
    background-color: #ffffffcc !important;
    padding: 6px;
    border-radius: 8px;
}

.stButton>button {
    background-color: #ffffff;
    color: #333;
    border-radius: 10px;
    padding: 10px 22px;
    border: none;
    font-size: 16px;
    font-weight: 600;
    box-shadow: 0 5px 12px rgba(0,0,0,0.18);
    transition: 0.3s;
}

.stButton>button:hover {
    background-color: #15aabf;
    color: white;
    transform: scale(1.08);
}

.result-box {
    background: rgba(255,255,255,0.55);
    padding: 18px;
    border-radius: 15px;
    text-align: center;
    color: #333;
    font-size: 22px;
    font-weight: 600;
    margin-top: 20px;
}

.result-prob {
    background: rgba(255,255,255,0.7);
    padding: 10px 15px;
    border-radius: 12px;
    margin-top: 8px;
}

.footer {
    text-align: center;
    margin-top: 40px;
    font-size: 13px;
    color: #f1f1f1;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------
# HEADER + LOGO
# ---------------------------
st.markdown('<p class="header-title">🧠 Multimodal Dementia Detection System</p>', unsafe_allow_html=True)
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
try:
    st.image("assets/logo.avif", width=180)
except Exception:
    # don't crash if logo missing
    st.write("")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------
# MODEL / CONSTANTS
# ---------------------------
DEVICE = "cpu"
CLASS_NAMES = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]
CHECKPOINT_PATH = "outputs/best_model.pth"

# ---------------------------
# ResNet18 builder and safe loader
# ---------------------------
def build_resnet18(num_classes=len(CLASS_NAMES)):
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    return model

def load_resnet_checkpoint_safe(ckpt_path=CHECKPOINT_PATH, device="cpu"):
    model = build_resnet18(num_classes=len(CLASS_NAMES))
    try:
        ck = torch.load(ckpt_path, map_location=device)
    except Exception as e:
        print(f"[MRI] Could not load checkpoint file '{ckpt_path}': {e}")
        return model  # return uninitialized model; will at least allow forward pass

    # Determine candidate state dict
    if isinstance(ck, dict) and "model_state" in ck:
        state = ck["model_state"]
    elif isinstance(ck, dict) and all(isinstance(v, torch.Tensor) for v in ck.values()):
        # appears to already be a state dict
        state = ck
    else:
        # fallback: if ck is a dict but not a state_dict, try to find nested
        if isinstance(ck, dict):
            # try common keys
            for key in ("state_dict", "model", "net", "model_state_dict"):
                if key in ck and isinstance(ck[key], dict):
                    state = ck[key]; break
            else:
                state = ck  # try to use it anyway
        else:
            state = ck

    model_state = model.state_dict()
    matched = {}
    for k, v in state.items():
        if k in model_state and isinstance(v, torch.Tensor) and v.shape == model_state[k].shape:
            matched[k] = v
    # update and load
    model_state.update(matched)
    model.load_state_dict(model_state)
    print(f"[MRI] Loaded {len(matched)} parameter tensors into ResNet18 from '{ckpt_path}' (out of {len(model_state)}).")
    return model

# load model once
mri_model = load_resnet_checkpoint_safe(CHECKPOINT_PATH, device=DEVICE)

# transform
transform_mri = transforms.Compose([
    transforms.Resize((128,128)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])

def predict_mri_probs(image, model=mri_model):
    model.eval()
    img_t = transform_mri(image).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = model(img_t)
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()
    return {cls: float(probs[i]) for i, cls in enumerate(CLASS_NAMES)}

# ---------------------------
# Cognitive predictor (simple slider-based)
# ---------------------------
def predict_cognitive_from_score(score):
    # score in [0,20] where higher = healthier
    # design simple mapping to 4-class vector
    s = float(score)
    # heuristics
    p_non = min(1.0, s / 20.0)
    p_mild = max(0.0, 1.0 - s/8.0)
    p_moderate = max(0.0, (10.0 - abs(s - 10.0)) / 20.0)
    p_very = max(0.0, s / 30.0)
    arr = np.array([p_mild, p_moderate, p_non, p_very], dtype=float)
    if arr.sum() <= 0:
        arr = np.ones_like(arr) / len(arr)
    else:
        arr = arr / arr.sum()
    return {cls: float(arr[i]) for i, cls in enumerate(CLASS_NAMES)}

# ---------------------------
# Dummy audio predictor
# ---------------------------
def predict_audio_dummy():
    # neutral probabilities (option A3)
    val = 1.0 / len(CLASS_NAMES)
    return {cls: val for cls in CLASS_NAMES}

# ---------------------------
# Fusion
# ---------------------------
def fuse_prob_dicts(mri_p, cog_p, aud_p, w_mri=0.7, w_cog=0.2, w_aud=0.1):
    fused = {}
    for cls in CLASS_NAMES:
        fused[cls] = w_mri * mri_p.get(cls, 0.0) + w_cog * cog_p.get(cls, 0.0) + w_aud * aud_p.get(cls, 0.0)
    # normalize
    total = sum(fused.values())
    if total <= 0:
        return {cls: 1.0/len(CLASS_NAMES) for cls in CLASS_NAMES}
    return {cls: fused[cls] / total for cls in CLASS_NAMES}

# ---------------------------
# UI LAYOUT
# ---------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("📤 Upload MRI Brain Scan")
mri_file = st.file_uploader("Choose MRI image", type=["jpg", "jpeg", "png"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("🎤 Upload Audio ")
audio_file = st.file_uploader("Upload speech sample ", type=["wav", "mp3"])
#st.info("Audio is optional. If no audio is provided, neutral audio probabilities will be used.")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("🧩 Cognitive Test (Quick Entry)")
cog_score = st.slider("Aggregate cognitive score (0 = low → 20 = high)", min_value=0, max_value=20, value=10)
st.markdown('</div>', unsafe_allow_html=True)

# Predict
if st.button("🔍 Predict Dementia Condition"):
    if mri_file is None:
        st.error("Please upload an MRI image to continue.")
    else:
        try:
            image = Image.open(mri_file).convert("RGB")
        except Exception as e:
            st.error(f"Failed to open image: {e}")
            image = None

        if image is not None:
            # modality predictions
            mri_probs = predict_mri_probs(image, mri_model)
            cog_probs = predict_cognitive_from_score(cog_score)
            audio_probs = predict_audio_dummy()

            fused = fuse_prob_dicts(mri_probs, cog_probs, audio_probs)
            predicted_class = max(fused, key=fused.get)
            confidence = fused[predicted_class]

            # display
            st.markdown('<div class="result-box">', unsafe_allow_html=True)
            st.write(f"### 🧠 Final Prediction: **{predicted_class}**")
            st.write(f"Confidence: **{confidence*100:.2f}%**")
            st.markdown('</div>', unsafe_allow_html=True)

            st.write("### 📊 Class Probabilities (Fused)")
            for cls in CLASS_NAMES:
                st.markdown(f'<div class="result-prob">{cls}: {fused[cls]:.3f}</div>', unsafe_allow_html=True)

            st.write("### 🔬 Modality Breakdown (raw probabilities)")
            st.json({
                "MRI": mri_probs,
                "Cognitive": cog_probs,
                "Audio (dummy)": audio_probs,
                "Fused": fused
            })

# footer
st.markdown('<p class="footer">Designed for Major Project • Multimodal Dementia Detection</p>', unsafe_allow_html=True)
