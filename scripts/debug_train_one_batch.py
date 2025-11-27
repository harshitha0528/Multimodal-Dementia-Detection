# scripts/debug_train_one_batch.py
import torch, sys
from pathlib import Path
from src.datasets_fusion import FusionDataset
from src.models_fusion import FusionModel
from torch.utils.data import DataLoader
import torch.nn.functional as F
from torch import optim
import numpy as np

torch.manual_seed(0)
ds = FusionDataset(index_csv="data/fusion_index.csv", split="train", img_size=128)
print("Full train size:", len(ds))
# take first 8 samples
indices = list(range(min(8, len(ds))))
sub = torch.utils.data.Subset(ds, indices)
loader = DataLoader(sub, batch_size=4, shuffle=False, num_workers=0)

device = torch.device("cpu")
model = FusionModel()
model = model.to(device)

opt = optim.Adam(model.parameters(), lr=1e-6)
model.train()
torch.autograd.set_detect_anomaly(True)
for imgs, audio_probs, cog, labels in loader:
    imgs = imgs.to(device)
    audio_probs = audio_probs.to(device)
    cog = cog.to(device)
    labels = labels.to(device)
    print("Batch shapes:", imgs.shape, audio_probs.shape, cog.shape, labels.shape)
    # check for NaN in inputs
    print("NaN in imgs:", torch.isnan(imgs).any().item(), "NaN in audio:", torch.isnan(audio_probs).any().item(), "NaN in cog:", torch.isnan(cog).any().item())
    out = model(imgs, audio_probs, cog)
    print("Output sample:", out.detach().cpu().numpy())
    loss = F.cross_entropy(out, labels)
    print("Loss before backward:", loss.item())
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    opt.step()
    print("Backward + step done")
    break

print("Debug run finished")
