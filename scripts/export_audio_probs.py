# scripts/export_audio_probs.py
import joblib
import pandas as pd
from pathlib import Path
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--csv", type=str, default="data/raw/parkinson_source/parkinsons.data")
parser.add_argument("--model", type=str, default="outputs/audio_rf.joblib")
parser.add_argument("--out_csv", type=str, default="outputs/audio_probs.csv")
args = parser.parse_args()

df = pd.read_csv(args.csv)
model = joblib.load(args.model)

# prepare features like training script (drop non-numeric & label)
label_col = "status"
X = df.drop(columns=[label_col])
X = X.select_dtypes(include=[np.number]).fillna(0.0)

# predict probabilities (class order is model.classes_)
probs = model.predict_proba(X)  # shape (N,2)
classes = model.classes_.tolist()
# create dataframe: keep original name/stem, true label, prob columns
out = pd.DataFrame()
out["name"] = df["name"]
out["true_label"] = df[label_col]
# map class probs to readable columns
for i,c in enumerate(classes):
    out[f"prob_class_{c}"] = probs[:, i]
# convenience: map to your MRI labels:
# assuming status=1 -> ModerateDemented, status=0 -> NonDemented
out["prob_ModerateDemented"] = out[f"prob_class_{1}"] if 1 in classes else 0.0
out["prob_NonDemented"] = out[f"prob_class_{0}"] if 0 in classes else 0.0

Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
out.to_csv(args.out_csv, index=False)
print("Saved audio probabilities to", args.out_csv)
print(out.head())
