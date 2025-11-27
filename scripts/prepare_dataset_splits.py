# scripts/prepare_dataset_splits.py
import random
from pathlib import Path
from PIL import Image
import shutil

# Config
RAW_ROOT = Path("data/raw/mri_alzheimer")
OUT_ROOT = Path("data/processed")
CLASS_NAMES = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
SIZE = (224, 224)        # output image size (width, height)
SPLIT = (0.70, 0.15, 0.15)  # train, val, test
SEED = 42

def get_images_for_class(cls_folder):
    files = [p for p in cls_folder.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXTS]
    files.sort()
    return files

def make_dirs():
    for split in ["train", "val", "test"]:
        for cls in CLASS_NAMES:
            (OUT_ROOT / split / cls).mkdir(parents=True, exist_ok=True)

def resize_and_save(src_path, dest_path):
    try:
        img = Image.open(src_path).convert("RGB")
        img = img.resize(SIZE, Image.BILINEAR)
        img.save(dest_path)
    except Exception as e:
        print(f"Failed to process {src_path}: {e}")

def main():
    if not RAW_ROOT.exists():
        print(f"ERROR: expected raw data folder {RAW_ROOT} not found.")
        return
    make_dirs()
    random.seed(SEED)
    summary = { "train":{}, "val":{}, "test":{} }

    for cls in CLASS_NAMES:
        src_cls = RAW_ROOT / cls
        if not src_cls.exists():
            print(f"Warning: class folder not found: {src_cls}")
            images = []
        else:
            images = get_images_for_class(src_cls)

        n = len(images)
        if n == 0:
            print(f"No images found for class {cls}.")
            for s in ["train","val","test"]:
                summary[s][cls] = 0
            continue

        # shuffle and split
        random.shuffle(images)
        n_train = int(n * SPLIT[0])
        n_val = int(n * SPLIT[1])
        n_test = n - n_train - n_val

        splits = {
            "train": images[:n_train],
            "val": images[n_train:n_train + n_val],
            "test": images[n_train + n_val:]
        }

        # copy + resize
        for split_name, files in splits.items():
            for src in files:
                dest = OUT_ROOT / split_name / cls / src.name
                resize_and_save(src, dest)
            summary[split_name][cls] = len(files)

    # print summary
    print("\nDataset split summary (counts):")
    for sp in ["train","val","test"]:
        total = sum(summary[sp].values())
        print(f"  {sp}: {total} images")
        for cls in CLASS_NAMES:
            print(f"    {cls}: {summary[sp].get(cls,0)}")
    print(f"\nProcessed images saved to: {OUT_ROOT.resolve()}/{{train,val,test}}/<class>/")

if __name__ == "__main__":
    main()
