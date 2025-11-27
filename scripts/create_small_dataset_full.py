# scripts/create_small_dataset_full.py
from pathlib import Path
import random, shutil

SRC_ROOT = Path("data/processed")       # original full processed data
DST_ROOT = Path("data/processed_small") # destination small dataset
N_TRAIN = 200   # per class
N_VAL = 50      # per class
N_TEST = 50     # per class
random.seed(42)

for split, n in [("train", N_TRAIN), ("val", N_VAL), ("test", N_TEST)]:
    for cls_folder in (SRC_ROOT / split).iterdir():
        if not cls_folder.is_dir():
            continue
        dst_dir = DST_ROOT / split / cls_folder.name
        dst_dir.mkdir(parents=True, exist_ok=True)
        imgs = list(cls_folder.iterdir())
        random.shuffle(imgs)
        # protect if dataset has fewer images than requested
        for img in imgs[:min(n, len(imgs))]:
            shutil.copy2(img, dst_dir / img.name)

print("Done. Created small dataset at:", DST_ROOT)
