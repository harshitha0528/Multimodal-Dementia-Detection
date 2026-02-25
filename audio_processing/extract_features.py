import os
import librosa
import numpy as np
from tqdm import tqdm

DATASET_PATH = "audio_dataset"
MODEL_PATH = "models"
TARGET_SR = 16000
N_MFCC = 40


def extract_mfcc(file_path):
    audio, sr = librosa.load(file_path, sr=TARGET_SR)
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=N_MFCC)
    return np.mean(mfcc.T, axis=0)


def process_dataset():
    data = []
    labels = []

    class_folders = {
        "normal_wav": 0,
        "simulated": 1
    }

    for folder, label in class_folders.items():
        folder_path = os.path.join(DATASET_PATH, folder)

        if not os.path.exists(folder_path):
            print(f"❌ Folder not found: {folder_path}")
            return

        files = [f for f in os.listdir(folder_path) if f.endswith(".wav")]
        print(f"Processing {folder} ({len(files)} files)")

        for file in tqdm(files):
            file_path = os.path.join(folder_path, file)
            features = extract_mfcc(file_path)

            data.append(features)
            labels.append(label)

    X = np.array(data)
    y = np.array(labels)

    os.makedirs(MODEL_PATH, exist_ok=True)
    np.save(os.path.join(MODEL_PATH, "X_audio.npy"), X)
    np.save(os.path.join(MODEL_PATH, "y_audio.npy"), y)

    print("✅ Feature extraction completed.")
    print("Feature shape:", X.shape)


if __name__ == "__main__":
    process_dataset()