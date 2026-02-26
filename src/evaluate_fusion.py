import argparse
from collections import Counter

import torch
from torch.utils.data import DataLoader

from src.datasets_fusion import FusionDataset
from src.models_fusion import FusionModel


def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    print("Using device:", device)

    ds = FusionDataset(index_csv=args.index_csv, split=args.split, img_size=args.img_size, cog_dim=args.cog_dim)
    loader = DataLoader(ds, batch_size=args.batch_size, shuffle=False, num_workers=0)
    print(f"{args.split} samples:", len(ds))

    model = FusionModel(
        img_emb_dim=args.img_emb_dim,
        cog_dim=args.cog_dim,
        audio_dim=2,
        hidden_dim=args.hidden_dim,
        num_classes=args.num_classes,
        freeze_image=False,
    ).to(device)

    ckpt = torch.load(args.ckpt, map_location=device)
    state = ckpt.get("model_state", ckpt)
    model.load_state_dict(state, strict=True)
    model.eval()

    correct = 0
    total = 0
    pred_counter = Counter()
    true_counter = Counter()

    with torch.no_grad():
        for imgs, aud, cog, labels in loader:
            imgs = torch.nan_to_num(imgs, nan=0.0, posinf=0.0, neginf=0.0).to(device)
            aud = torch.nan_to_num(aud, nan=0.0, posinf=0.0, neginf=0.0).to(device)
            cog = torch.nan_to_num(cog, nan=0.0, posinf=0.0, neginf=0.0).to(device)
            labels = labels.to(device)

            out = model(imgs, aud, cog)
            out = torch.nan_to_num(out, nan=0.0, posinf=0.0, neginf=0.0)
            preds = out.argmax(1)

            correct += (preds == labels).sum().item()
            total += labels.size(0)
            pred_counter.update(preds.detach().cpu().tolist())
            true_counter.update(labels.detach().cpu().tolist())

    acc = 100.0 * correct / max(total, 1)
    print(f"{args.split} accuracy: {acc:.2f}%")
    print("True distribution:", dict(true_counter))
    print("Pred distribution:", dict(pred_counter))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--index_csv", type=str, default="data/fusion_index.csv")
    parser.add_argument("--split", type=str, default="test", choices=["train", "val", "test"])
    parser.add_argument("--ckpt", type=str, default="outputs/best_fusion.pth")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--img_size", type=int, default=128)
    parser.add_argument("--img_emb_dim", type=int, default=512)
    parser.add_argument("--cog_dim", type=int, default=7)
    parser.add_argument("--hidden_dim", type=int, default=256)
    parser.add_argument("--num_classes", type=int, default=4)
    parser.add_argument("--cpu", action="store_true")
    args = parser.parse_args()
    main(args)

