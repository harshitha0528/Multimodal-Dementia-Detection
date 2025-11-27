# src/datasets_image.py
import os
from pathlib import Path
from PIL import Image
from torch.utils.data import Dataset
import torchvision.transforms as T

CLASS_NAMES = ["MildDemented", "ModerateDemented", "NonDemented", "VeryMildDemented"]

'''def default_transforms(image_size=224, train=True):
    if train:
        return T.Compose([
            T.RandomResizedCrop(image_size, scale=(0.8,1.0)),
            T.RandomHorizontalFlip(),
            T.RandomRotation(10),
            T.ToTensor(),
            T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
        ])
    else:
        return T.Compose([
            T.Resize((image_size, image_size)),
            T.ToTensor(),
            T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
        ])
'''
def default_transforms(image_size=224, train=True):
    if train:
        return T.Compose([
            T.RandomResizedCrop(image_size, scale=(0.6, 1.0), ratio=(0.9, 1.1)),
            T.RandomHorizontalFlip(p=0.5),
            T.RandomApply([T.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.15, hue=0.05)], p=0.5),
            T.RandomRotation(15),
            T.RandomAffine(degrees=0, translate=(0.05,0.05), shear=5),
            T.RandomPerspective(distortion_scale=0.1, p=0.2),
            T.ToTensor(),
            T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
        ])
    else:
        return T.Compose([
            T.Resize((image_size, image_size)),
            T.ToTensor(),
            T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
        ])

class MRIImageDataset(Dataset):
    """
    Expects folder structure:
    data/processed/{train,val,test}/{class_name}/*.jpg
    """
    def __init__(self, root_dir, split="train", transform=None):
        self.root_dir = Path(root_dir) / split
        self.transform = transform
        self.samples = []
        for idx, cls in enumerate(CLASS_NAMES):
            cls_folder = self.root_dir / cls
            if not cls_folder.exists():
                continue
            for p in cls_folder.iterdir():
                if p.is_file():
                    self.samples.append((str(p), idx))
        # basic shuffle is left to DataLoader
    def __len__(self):
        return len(self.samples)
    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label
