# src/evaluate_image.py
import torch
from torch.utils.data import DataLoader
from pathlib import Path
import argparse
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

from src.datasets_image import MRIImageDataset, default_transforms
from src.models_image import get_resnet18, SimpleCNN

CLASS_NAMES = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]

def load_model(model_path, device, simple):
    if simple:
        model = SimpleCNN(num_classes=len(CLASS_NAMES))
        state = torch.load(model_path, map_location=device)
        model.load_state_dict(state.get("model_state", state))
    else:
        model = get_resnet18(num_classes=len(CLASS_NAMES), pretrained=False)
        state = torch.load(model_path, map_location=device)
        model.load_state_dict(state.get("model_state", state))
    return model.to(device)

def evaluate(model, loader, device):
    model.eval()
    preds = []
    trues = []
    with torch.no_grad():
        for imgs, labels in loader:
            imgs = imgs.to(device)
            out = model(imgs)
            p = out.argmax(dim=1).cpu().numpy()
            preds.extend(p.tolist())
            trues.extend(labels.numpy().tolist())
    return np.array(trues), np.array(preds)

def plot_confmat(cm, labels, out_path):
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels, yticklabels=labels, cmap="Blues")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    data_root = Path(args.data_root)
    test_ds = MRIImageDataset(data_root, split="test", transform=default_transforms(args.img_size, train=False))
    test_loader = DataLoader(test_ds, batch_size=args.batch_size, shuffle=False, num_workers=0)
    print("Test samples:", len(test_ds))

    model = load_model(args.model_path, device, args.simple)
    y_true, y_pred = evaluate(model, test_loader, device)

    print("\nClassification report:\n")
    print(classification_report(y_true, y_pred, target_names=CLASS_NAMES, digits=4))
    cm = confusion_matrix(y_true, y_pred)
    out_cm = Path(args.output_dir) / "confusion_matrix.png"
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    plot_confmat(cm, CLASS_NAMES, out_cm)
    print(f"Saved confusion matrix to: {out_cm.resolve()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default="outputs/best_model.pth")
    parser.add_argument("--data_root", type=str, default="data/processed")
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--img_size", type=int, default=224)
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--simple", action="store_true", help="load SimpleCNN instead of ResNet")
    parser.add_argument("--cpu", action="store_true")
    args = parser.parse_args()
    main(args)
