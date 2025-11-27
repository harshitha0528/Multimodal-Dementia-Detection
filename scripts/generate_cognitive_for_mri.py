# scripts/generate_cognitive_for_mri.py
import csv
from pathlib import Path
import random
import argparse
import os, glob

parser = argparse.ArgumentParser()
parser.add_argument("--img_root", type=str, default="data/processed/train", help="root folder containing train/val/test splits with class subfolders")
parser.add_argument("--out_csv", type=str, default="data/raw/cognitive/cognitive.csv")
parser.add_argument("--num_per_class", type=int, default=50, help="max rows per class (cap by available images)")
parser.add_argument("--seed", type=int, default=42)
args = parser.parse_args()

random.seed(args.seed)
img_root = Path(args.img_root)
rows = []
classes = [p.name for p in img_root.iterdir() if p.is_dir()]
print("Found classes:", classes)
for cls in classes:
    files = list((img_root/cls).glob("*"))
    random.shuffle(files)
    files = files[:args.num_per_class]
    for f in files:
        stem = f.stem
        # plausible synthetic cognitive values
        age = random.randint(55,85)
        edu = random.randint(0,20)
        orientation = random.choice([0,1])
        recall = random.randint(0,3)
        serial7 = random.randint(0,5)
        naming = random.choice([0,1])
        clock = random.choice([0,1])
        rows.append({
            "subject_id": stem,
            "class": cls,
            "split": "train",
            "age": age,
            "education_years": edu,
            "orientation_year_correct": orientation,
            "recall_3": recall,
            "serial7_correct": serial7,
            "naming_correct": naming,
            "clock_ok": clock
        })

out = Path(args.out_csv)
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", newline="", encoding="utf-8") as fh:
    fieldnames = ["subject_id","class","split","age","education_years","orientation_year_correct","recall_3","serial7_correct","naming_correct","clock_ok"]
    writer = csv.DictWriter(fh, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

print(f"Wrote {len(rows)} cognitive rows to {out}")
