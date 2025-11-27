# scripts/create_small_subset.py
from pathlib import Path
import random, shutil

SRC = Path("data/processed/train")
DST = Path("data/processed_small/train")
N_PER = 200
random.seed(42)
DST.mkdir(parents=True, exist_ok=True)
for cls in [d.name for d in SRC.iterdir() if d.is_dir()]:
    (DST/cls).mkdir(parents=True, exist_ok=True)
    imgs = list((SRC/cls).iterdir())
    random.shuffle(imgs)
    for img in imgs[:N_PER]:
        shutil.copy2(img, DST/cls / img.name)
print("Done. small dataset created at:", DST)
