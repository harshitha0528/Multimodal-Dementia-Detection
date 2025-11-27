# scripts/create_fusion_index.py
import pandas as pd
from pathlib import Path
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--img_root", type=str, default="data/processed")
parser.add_argument("--audio_probs", type=str, default="outputs/audio_probs.csv")
parser.add_argument("--cog_root", type=str, default="data/processed/cognitive")
parser.add_argument("--out", type=str, default="data/fusion_index.csv")
args = parser.parse_args()

img_root = Path(args.img_root)

# Load audio probabilities (if available)
audio_df = pd.read_csv(args.audio_probs)
audio_index = {str(r['name']): r for _, r in audio_df.iterrows()}

rows = []

for split in ["train", "val", "test"]:
    split_dir = img_root / split
    if not split_dir.exists():
        continue

    for cls_dir in split_dir.iterdir():
        if not cls_dir.is_dir():
            continue

        cls = cls_dir.name
        for img_path in cls_dir.glob("*"):
            stem = img_path.stem

            # audio match (may be missing)
            arow = audio_index.get(stem)

            # cognitive path
            cog_file = Path(args.cog_root) / split / cls / (stem + ".npy")
            cog_exists = cog_file.exists()

            rows.append({
                "split": split,
                "img_path": str(img_path),
                "audio_name": stem if arow is not None else "",
                "prob_ModerateDemented": arow["prob_ModerateDemented"] if arow is not None else "",
                "prob_NonDemented": arow["prob_NonDemented"] if arow is not None else "",
                "cog_path": str(cog_file) if cog_exists else "",
                "class": cls
            })

df = pd.DataFrame(rows)
out_path = Path(args.out)
out_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(out_path, index=False)

print("Saved fusion index to:", out_path)
print(df.head(10).to_string())
