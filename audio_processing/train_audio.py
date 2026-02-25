import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Load extracted features
X = np.load("models/X_audio.npy")
y = np.load("models/y_audio.npy")

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# Evaluate
accuracy = accuracy_score(y_test, predictions)

print("\n🎯 Audio Model Accuracy:", accuracy)
print("\n📊 Classification Report:\n")
print(classification_report(y_test, predictions))

print("\n🧩 Confusion Matrix:\n")
print(confusion_matrix(y_test, predictions))

# Save model
joblib.dump(model, "models/audio_model.pkl")

print("\n✅ Model saved as models/audio_model.pkl")