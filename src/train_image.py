# src/train_image.py
import torch
import torch.nn.functional as F
from torch import nn, optim
from torch.utils.data import DataLoader
from pathlib import Path
import time
import argparse
from collections import Counter
from src.datasets_image import MRIImageDataset, default_transforms
from src.models_image import get_resnet18, SimpleCNN
from torch.utils.data.sampler import WeightedRandomSampler

def train_epoch(model, loader, opt, device, class_weights_tensor):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    for imgs, labels in loader:
        imgs = imgs.to(device)
        labels = labels.to(device)
        preds = model(imgs)
        loss = F.cross_entropy(preds, labels, weight=class_weights_tensor.to(device))
        opt.zero_grad(); loss.backward(); opt.step()
        running_loss += loss.item() * imgs.size(0)
        _, p = preds.max(1)
        correct += (p == labels).sum().item()
        total += imgs.size(0)
    return running_loss/total if total>0 else 0.0, correct/total if total>0 else 0.0

@torch.no_grad()
def eval_epoch(model, loader, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    for imgs, labels in loader:
        imgs = imgs.to(device)
        labels = labels.to(device)
        preds = model(imgs)
        loss = F.cross_entropy(preds, labels)
        running_loss += loss.item() * imgs.size(0)
        _, p = preds.max(1)
        correct += (p == labels).sum().item()
        total += imgs.size(0)
    return running_loss/total if total>0 else 0.0, correct/total if total>0 else 0.0

def main(args):
    device = torch.device("cuda" if torch.cuda.is_available() and not args.cpu else "cpu")
    print("Using device:", device)
    data_root = Path(args.data_root)

    # build datasets
    train_ds = MRIImageDataset(data_root, split="train", transform=default_transforms(args.img_size, train=True))
    val_ds = MRIImageDataset(data_root, split="val", transform=default_transforms(args.img_size, train=False))

    print(f"Train size: {len(train_ds)}, Val size: {len(val_ds)}")

    # ------- compute class counts and weights -------
    train_labels = [lab for _, lab in train_ds.samples]
    counts = Counter(train_labels)
    print("Train class counts (label -> count):", counts)

    num_classes = len(set(train_labels))
    total = float(sum(counts.values())) if counts else 1.0
    class_weights = [0.0] * num_classes
    for cls in range(num_classes):
        class_weights[cls] = total / (counts.get(cls, 0) + 1e-6)

    # per-sample weights
    sample_weights = [class_weights[label] for _, label in train_ds.samples]
    sampler = WeightedRandomSampler(weights=sample_weights, num_samples=len(sample_weights), replacement=True)

    # DataLoaders
    train_loader = DataLoader(train_ds, batch_size=args.batch_size, sampler=sampler,
                              num_workers=args.num_workers, pin_memory=True)
    val_loader = DataLoader(val_ds, batch_size=max(1, args.batch_size//2), shuffle=False,
                            num_workers=0, pin_memory=True)

    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float)

    # model
    if args.simple:
        model = SimpleCNN(num_classes=num_classes)
    else:
        model = get_resnet18(num_classes=num_classes, pretrained=args.pretrained)
    model = model.to(device)

    opt = optim.Adam(model.parameters(), lr=args.lr)
    best_val_acc = 0.0
    start = time.time()
    for epoch in range(1, args.epochs+1):
        t0 = time.time()
        train_loss, train_acc = train_epoch(model, train_loader, opt, device, class_weights_tensor)
        val_loss, val_acc = eval_epoch(model, val_loader, device)
        t1 = time.time()
        print(f"Epoch {epoch}/{args.epochs}  time:{t1-t0:.1f}s  train_loss:{train_loss:.4f} train_acc:{train_acc:.3f}  val_loss:{val_loss:.4f} val_acc:{val_acc:.3f}")
        # save best
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({"model_state": model.state_dict(), "epoch": epoch, "val_acc": val_acc}, Path(args.output_dir)/"best_model.pth")
    total_time = time.time() - start
    print(f"Training finished in {total_time/60:.2f} minutes. Best val acc: {best_val_acc:.3f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", type=str, default="data/processed")
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--img_size", type=int, default=224)
    parser.add_argument("--num_workers", type=int, default=4)
    parser.add_argument("--pretrained", action="store_true")
    parser.add_argument("--simple", action="store_true", help="use small SimpleCNN instead of ResNet18")
    parser.add_argument("--output_dir", type=str, default="outputs")
    parser.add_argument("--cpu", action="store_true", help="force CPU")
    args = parser.parse_args()

    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    main(args)
