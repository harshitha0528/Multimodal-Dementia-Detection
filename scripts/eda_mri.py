# scripts/eda_mri.py
import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

ROOT = Path("data/raw/mri_alzheimer")
OUT_IMG = Path("data/processed/eda_mri_samples.png")
CLASS_NAMES = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]
SAMPLES_PER_CLASS = 8  # how many sample images to show per class

def get_image_files(folder):
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}
    files = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in exts]
    files.sort()
    return files

def main():
    if not ROOT.exists():
        print(f"ERROR: expected folder {ROOT} not found. Check that you copied images into data/raw/mri_alzheimer/")
        return

    counts = {}
    samples = {}
    for cls in CLASS_NAMES:
        p = ROOT / cls
        if not p.exists():
            counts[cls] = 0
            samples[cls] = []
            continue
        files = get_image_files(p)
        counts[cls] = len(files)
        samples[cls] = files[:SAMPLES_PER_CLASS]

    # Print counts
    print("Image counts per class:")
    for cls in CLASS_NAMES:
        print(f"  {cls}: {counts[cls]}")

    # Create a montage: rows = classes, cols = samples per class
    cols = SAMPLES_PER_CLASS
    rows = len(CLASS_NAMES)
    fig_h = rows * 2.0
    fig_w = cols * 2.0
    fig, axes = plt.subplots(rows, cols, figsize=(fig_w, fig_h))
    for r, cls in enumerate(CLASS_NAMES):
        for c in range(cols):
            ax = axes[r, c] if rows > 1 else axes[c]
            ax.axis('off')
            try:
                img_path = samples[cls][c]
                img = mpimg.imread(img_path)
                # If grayscale, imshow handles it; else convert
                ax.imshow(img)
            except IndexError:
                # no image for this slot
                ax.set_facecolor((0.95,0.95,0.95))
            except Exception as e:
                ax.text(0.5,0.5, "error\n"+str(e), ha='center', va='center', fontsize=8)
    # Add class labels on left
    for r, cls in enumerate(CLASS_NAMES):
        y = (rows - r - 1) / rows  # not used with suptitle; instead put on the first column
        axes[r,0].text(-0.2, 0.5, cls, transform=axes[r,0].transAxes,
                       fontsize=12, weight='bold', va='center', ha='right')
    plt.tight_layout()
    OUT_IMG.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUT_IMG, dpi=150, bbox_inches='tight')
    print(f"\nSaved sample montage to: {OUT_IMG.resolve()}")
    print("Open this image to visually inspect the dataset samples.")

if __name__ == "__main__":
    main()
