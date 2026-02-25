import os
import librosa
import soundfile as sf
from tqdm import tqdm

INPUT_FOLDER = "audio_dataset/normal"
OUTPUT_FOLDER = "audio_dataset/normal_wav"
TARGET_SR = 16000


def get_all_flac_files(folder):
    flac_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".flac"):
                flac_files.append(os.path.join(root, file))
    return flac_files


def convert_flac_to_wav():
    if not os.path.exists(INPUT_FOLDER):
        print(f"❌ Input folder not found: {INPUT_FOLDER}")
        return

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    flac_files = get_all_flac_files(INPUT_FOLDER)

    print(f"Found {len(flac_files)} FLAC files")

    for file_path in tqdm(flac_files):
        filename = os.path.basename(file_path)
        output_path = os.path.join(
            OUTPUT_FOLDER, filename.replace(".flac", ".wav")
        )

        audio, sr = librosa.load(file_path, sr=TARGET_SR)
        sf.write(output_path, audio, TARGET_SR)

    print("✅ Conversion completed.")


if __name__ == "__main__":
    convert_flac_to_wav()