# scripts/train_audio_from_csv.py
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--csv", type=str, default="data/raw/parkinson_source/parkinsons.data")
parser.add_argument("--label_col", type=str, default="status")
parser.add_argument("--output", type=str, default="outputs/audio_rf.joblib")
args = parser.parse_args()

df = pd.read_csv(args.csv)
print("Columns:", df.columns.tolist())

# prepare features & label
label_col = args.label_col
X = df.drop(columns=[label_col])
X = X.select_dtypes(include=[np.number]).fillna(0.0)
y = df[label_col].values

print("Using features:", list(X.columns))

# stratified split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# pipeline: scaler + RF
pipe = make_pipeline(
    StandardScaler(),
    RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced')
)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="f1_macro")
print("CV F1-macro scores:", np.round(scores,4), "mean:", np.round(scores.mean(),4))

# fit and evaluate
pipe.fit(X_train, y_train)
y_pred = pipe.predict(X_test)
print("\nTest classification report:")
print(classification_report(y_test, y_pred))
print("Confusion matrix:")
print(confusion_matrix(y_test, y_pred))

# save model
Path(args.output).parent.mkdir(parents=True, exist_ok=True)
joblib.dump(pipe, args.output)
print("Saved trained audio model to", args.output)
