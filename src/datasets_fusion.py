# src/datasets_fusion.py  (PATCHED - robust/sanitizing)
from pathlib import Path
from PIL import Image
import numpy as np
import torch
from torch.utils.data import Dataset
import torchvision.transforms as T
import pandas as pd

CLASS_NAMES = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]

def default_img_transform(image_size=128, train=False):
    if train:
        return T.Compose([
            T.RandomResizedCrop(image_size, scale=(0.8,1.0)),
            T.RandomHorizontalFlip(),
            T.RandomRotation(8),
            T.ToTensor(),
            T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
        ])
    else:
        return T.Compose([
            T.Resize((image_size, image_size)),
            T.ToTensor(),
            T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
        ])

class FusionDataset(Dataset):
    def __init__(self, index_csv="data/fusion_index.csv", split="train", img_transform=None, img_size=128, cog_dim=7):
        self.index_csv = Path(index_csv)
        self.split = split
        self.samples = []
        self.img_transform = img_transform or default_img_transform(img_size, train=(split=="train"))
        self.cog_dim = cog_dim

        df = pd.read_csv(self.index_csv)
        df = df[df['split'] == split]
        for _, r in df.iterrows():
            img_path = r.get('img_path', "")
            if not isinstance(img_path, str) or img_path.strip() == "":
                continue
            img_path = str(img_path)
            # audio probs
            prob_mod = r.get('prob_ModerateDemented', "")
            prob_non = r.get('prob_NonDemented', "")
            # robust parse
            try:
                prob_mod = float(prob_mod) if str(prob_mod).strip() != "" else 0.0
            except:
                prob_mod = 0.0
            try:
                prob_non = float(prob_non) if str(prob_non).strip() != "" else 0.0
            except:
                prob_non = 0.0
            # clip and ensure finite
            if not np.isfinite(prob_mod):
                prob_mod = 0.0
            if not np.isfinite(prob_non):
                prob_non = 0.0
            prob_mod = float(max(0.0, min(1.0, prob_mod)))
            prob_non = float(max(0.0, min(1.0, prob_non)))

            # cognitive path
            cog_path = r.get('cog_path', "")
            cog_path = str(cog_path) if isinstance(cog_path, str) else ""
            cls = r.get('class', "")

            self.samples.append({
                "img_path": img_path,
                "cog_path": cog_path,
                "audio_probs": [prob_mod, prob_non],
                "class": cls
            })

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        s = self.samples[idx]
        # load image safely
        img_path = s["img_path"]
        try:
            img = Image.open(img_path).convert("RGB")
            img = self.img_transform(img)
        except Exception as e:
            # if image fails, return a zero tensor image to avoid NaN
            img = torch.zeros((3, self.img_transform.transforms[0].size if hasattr(self.img_transform.transforms[0],'size') else 128, self.img_transform.transforms[0].size if hasattr(self.img_transform.transforms[0],'size') else 128))
        
        # audio probs
        audio_probs = s["audio_probs"]
        audio_probs = [0.0 if (not isinstance(x, (int,float)) or not np.isfinite(x)) else float(x) for x in audio_probs]
        audio_probs = torch.tensor(audio_probs, dtype=torch.float32)

        # cognitive
        cog_path = s["cog_path"]
        if cog_path and Path(cog_path).exists():
            try:
                cog = np.load(cog_path).astype("float32")
                cog = np.nan_to_num(cog, nan=0.0, posinf=0.0, neginf=0.0)
                if cog.ndim != 1:
                    cog = cog.reshape(-1)[: self.cog_dim]
                if cog.shape[0] < self.cog_dim:
                    pad = self.cog_dim - cog.shape[0]
                    cog = np.concatenate([cog, np.zeros(pad, dtype="float32")])
                cog = cog[: self.cog_dim]
            except Exception:
                cog = np.zeros(self.cog_dim, dtype="float32")
        else:
            cog = np.zeros(self.cog_dim, dtype="float32")
        cog = torch.tensor(cog, dtype=torch.float32)

        # label index
        cls = s.get("class", "")
        try:
            label = CLASS_NAMES.index(cls)
        except ValueError:
            # fallback: match substring or default 0
            label = 0
            for i,cname in enumerate(CLASS_NAMES):
                if cname.lower() in str(cls).lower():
                    label = i
                    break

        return img, audio_probs, cog, label
