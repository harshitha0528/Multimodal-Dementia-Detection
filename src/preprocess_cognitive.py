# src/preprocess_cognitive.py
import pandas as pd
import numpy as np
from pathlib import Path
import argparse

FEATURE_NAMES = [
    "age",
    "education_years",
    "orientation_year_correct",
    "recall_3",
    "serial7_correct",
    "naming_correct",
    "clock_ok"
]

parser = argparse.ArgumentParser()
parser.add_argument("--csv", type=str, default="data/raw/cognitive/cognitive.csv")
parser.add_argument("--out_root", type=str, default="data/processed/cognitive")
args = parser.parse_args()

df = pd.read_csv(args.csv)

out_root = Path(args.out_root)

for _, row in df.iterrows():
    subj = str(row["subject_id"])
    cls = str(row["class"])
    split = str(row.get("split", "train"))

    # extract cognitive feature values
    arr = row[FEATURE_NAMES].fillna(0).astype(float).values.astype("float32")

    # write npy file
    dst = out_root / split / cls
    dst.mkdir(parents=True, exist_ok=True)
    np.save(dst / f"{subj}.npy", arr)

print("Saved cognitive npy files to:", out_root)
