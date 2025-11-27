# scripts/count_dataset.py
from pathlib import Path

ROOT = Path("data/processed")
splits = ["train", "val", "test"]

def count_images():
    for s in splits:
        p = ROOT / s
        print(f"\n=== {s.upper()} ===")
        if not p.exists():
            print("  (folder not found)")
            continue
        total = 0
        for cls in sorted([d for d in p.iterdir() if d.is_dir()]):
            cnt = len([f for f in cls.iterdir() if f.is_file()])
            total += cnt
            print(f"  {cls.name}: {cnt}")
        print(f"  TOTAL {s}: {total}")

if __name__ == "__main__":
    count_images()
