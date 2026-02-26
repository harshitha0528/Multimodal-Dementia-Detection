# src/train_fusion.py
import argparse, time, torch, os
from pathlib import Path
import torch.nn.functional as F
from torch import optim
from torch.utils.data import DataLoader
from src.datasets_fusion import FusionDataset
from src.models_fusion import FusionModel
from collections import Counter
import numpy as np

def build_class_weights(train_ds, num_classes):
    labels = []
    for _, _, _, lab in train_ds:
        labels.append(int(lab))
    counts = np.bincount(labels, minlength=num_classes).astype(np.float32)
    counts[counts == 0] = 1.0
    weights = counts.sum() / (num_classes * counts)
    return torch.tensor(weights, dtype=torch.float32)

def train_epoch(model, loader, opt, loss_fn, device, grad_clip=1.0):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    skipped = 0
    for imgs, audio_probs, cog, labels in loader:
        imgs = imgs.to(device)
        audio_probs = audio_probs.to(device)
        cog = cog.to(device)
        labels = labels.to(device)
        imgs = torch.nan_to_num(imgs, nan=0.0, posinf=0.0, neginf=0.0)
        audio_probs = torch.nan_to_num(audio_probs, nan=0.0, posinf=0.0, neginf=0.0)
        cog = torch.nan_to_num(cog, nan=0.0, posinf=0.0, neginf=0.0)

        preds = model(imgs, audio_probs, cog)
        preds = torch.nan_to_num(preds, nan=0.0, posinf=0.0, neginf=0.0)
        loss = loss_fn(preds, labels)
        if not torch.isfinite(loss):
            skipped += 1
            continue
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=grad_clip)
        opt.step()
        running_loss += loss.item() * imgs.size(0)
        _, p = preds.max(1)
        correct += (p == labels).sum().item()
        total += imgs.size(0)
    total = max(total, 1)
    return running_loss / total, correct / total, skipped

@torch.no_grad()
def eval_epoch(model, loader, loss_fn, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    skipped = 0
    for imgs, audio_probs, cog, labels in loader:
        imgs = imgs.to(device)
        audio_probs = audio_probs.to(device)
        cog = cog.to(device)
        labels = labels.to(device)
        imgs = torch.nan_to_num(imgs, nan=0.0, posinf=0.0, neginf=0.0)
        audio_probs = torch.nan_to_num(audio_probs, nan=0.0, posinf=0.0, neginf=0.0)
        cog = torch.nan_to_num(cog, nan=0.0, posinf=0.0, neginf=0.0)

        preds = model(imgs, audio_probs, cog)
        preds = torch.nan_to_num(preds, nan=0.0, posinf=0.0, neginf=0.0)
        loss = loss_fn(preds, labels)
        if not torch.isfinite(loss):
            skipped += 1
            continue
        running_loss += loss.item() * imgs.size(0)
        _, p = preds.max(1)
        correct += (p == labels).sum().item()
        total += imgs.size(0)
    total = max(total, 1)
    return running_loss / total, correct / total, skipped

def load_image_checkpoint_into_backbone(model, ckpt_path, device):
    # expects ckpt to contain "model_state" mapping (as in outputs/best_model.pth) from your image training
    if not Path(ckpt_path).exists():
        print("Image checkpoint not found:", ckpt_path)
        return
    ckpt = torch.load(ckpt_path, map_location=device)
    state = ckpt.get("model_state", ckpt)
    # the saved image state likely matches a ResNet18-based model's state_dict keys
    # load into backbone (need to adapt key names if saved with module prefix)
    backbone_state = model.backbone.state_dict()
    # try direct load
    common = {k: v for k, v in state.items() if k in backbone_state and v.shape == backbone_state[k].shape}
    backbone_state.update(common)
    model.backbone.load_state_dict(backbone_state)
    print(f"Loaded {len(common)} params into image backbone from {ckpt_path}")

def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    print("Using device:", device)
    train_ds = FusionDataset(index_csv=args.index_csv, split="train", img_size=args.img_size)
    val_ds = FusionDataset(index_csv=args.index_csv, split="val", img_size=args.img_size)
    print("Train size:", len(train_ds), "Val size:", len(val_ds))
    print("Train class counts:", Counter([lab for _,_,_,lab in train_ds]))

    train_loader = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True, num_workers=args.num_workers)
    val_loader = DataLoader(val_ds, batch_size=max(1,args.batch_size//2), shuffle=False, num_workers=0)

    model = FusionModel(img_emb_dim=args.img_emb_dim, cog_dim=args.cog_dim, audio_dim=2, hidden_dim=args.hidden_dim, num_classes=args.num_classes, freeze_image=args.freeze_image)
    model = model.to(device)

    # optionally initialize backbone from image-only checkpoint
    if args.image_ckpt:
        load_image_checkpoint_into_backbone(model, args.image_ckpt, device)

    class_weights = build_class_weights(train_ds, args.num_classes).to(device)
    print("Class weights:", class_weights.detach().cpu().tolist())
    loss_fn = torch.nn.CrossEntropyLoss(weight=class_weights, label_smoothing=args.label_smoothing)

    opt = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=args.lr, weight_decay=args.weight_decay)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(1, args.epochs))
    best_val = 0.0
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    start = time.time()
    for epoch in range(1, args.epochs+1):
        t0 = time.time()
        tr_loss, tr_acc, tr_skipped = train_epoch(model, train_loader, opt, loss_fn, device, grad_clip=args.grad_clip)
        val_loss, val_acc, val_skipped = eval_epoch(model, val_loader, loss_fn, device)
        t1 = time.time()
        scheduler.step()
        print(
            f"Epoch {epoch}/{args.epochs} time:{t1-t0:.1f}s "
            f"train_loss:{tr_loss:.4f} train_acc:{tr_acc:.3f} skipped:{tr_skipped} "
            f"val_loss:{val_loss:.4f} val_acc:{val_acc:.3f} skipped:{val_skipped}"
        )
        if val_acc > best_val:
            best_val = val_acc
            torch.save({"model_state": model.state_dict(), "epoch": epoch, "val_acc": val_acc}, Path(args.output_dir)/"best_fusion.pth")
    total = (time.time() - start)/60.0
    print(f"Training finished in {total:.2f} minutes. Best val acc: {best_val:.3f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--index_csv", type=str, default="data/fusion_index.csv")
    parser.add_argument("--image_ckpt", type=str, default="outputs/best_model.pth", help="optional image-only checkpoint to initialize backbone")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--img_size", type=int, default=128)
    parser.add_argument("--num_workers", type=int, default=0)
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--cpu", action="store_true")
    parser.add_argument("--img_emb_dim", type=int, default=512)
    parser.add_argument("--cog_dim", type=int, default=7)
    parser.add_argument("--hidden_dim", type=int, default=256)
    parser.add_argument("--num_classes", type=int, default=4)
    parser.add_argument("--freeze_image", action="store_true", help="freeze image backbone weights")
    parser.add_argument("--label_smoothing", type=float, default=0.05)
    parser.add_argument("--weight_decay", type=float, default=1e-4)
    parser.add_argument("--grad_clip", type=float, default=1.0)
    args = parser.parse_args()
    main(args)
