import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from joblib import dump

df = pd.read_csv("data/raw/cognitive/cognitive.csv")

FEATURES = ["age","education_years","orientation_year_correct","recall_3","serial7_correct","naming_correct","clock_ok"]
X = df[FEATURES].values
y = df["class"].astype("category").cat.codes.values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=200, random_state=42)
clf.fit(X_train, y_train)

pred = clf.predict(X_test)
print(classification_report(y_test, pred))

dump(clf, "outputs/cognitive_model.joblib")
print("Saved to outputs/cognitive_model.joblib")
