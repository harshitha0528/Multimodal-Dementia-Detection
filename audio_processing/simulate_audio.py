import os
import librosa
import soundfile as sf
import numpy as np
from tqdm import tqdm

INPUT_FOLDER = "audio_dataset/normal_wav"
OUTPUT_FOLDER = "audio_dataset/simulated"
TARGET_SR = 16000


def simulate_speech():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".wav")]

    print(f"Found {len(files)} WAV files")

    for file in tqdm(files):
        input_path = os.path.join(INPUT_FOLDER, file)
        output_path = os.path.join(OUTPUT_FOLDER, file)

        audio, sr = librosa.load(input_path, sr=TARGET_SR)

        # 1️⃣ Slow down more
        audio = librosa.effects.time_stretch(audio, rate=0.6)

        # 2️⃣ Add small white noise
        noise = np.random.normal(0, 0.003, len(audio))
        audio = audio + noise

        # 3️⃣ Insert pause in middle
        pause = np.zeros(int(0.5 * sr))
        mid = len(audio) // 2
        audio = np.concatenate([audio[:mid], pause, audio[mid:]])

        sf.write(output_path, audio, TARGET_SR)

    print("✅ Strong Simulation completed.")


if __name__ == "__main__":
    simulate_speech()