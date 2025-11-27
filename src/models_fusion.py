# src/models_fusion.py
import torch
import torch.nn as nn
from torchvision import models

class FusionModel(nn.Module):
    def __init__(self, img_emb_dim=512, cog_dim=7, audio_dim=2, hidden_dim=256, num_classes=4, freeze_image=False):
        super().__init__()
        # image encoder: resnet18 backbone (no fc)
        self.backbone = models.resnet18(weights=None)  # weights None by default; we'll load checkpoint if available
        # replace fc with identity to get embedding
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Identity()
        # optional projection if dims differ
        self.img_proj = nn.Sequential(nn.Linear(in_features, img_emb_dim), nn.ReLU())

        # audio small MLP (takes 2-d prob vector)
        self.audio_mlp = nn.Sequential(
            nn.Linear(audio_dim, 32),
            nn.ReLU(),
            nn.Dropout(0.1)
        )

        # cognitive MLP
        self.cog_mlp = nn.Sequential(
            nn.Linear(cog_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.1)
        )

        # fusion classifier head
        fusion_dim = img_emb_dim + 32 + 64
        self.head = nn.Sequential(
            nn.Linear(fusion_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, num_classes)
        )

        if freeze_image:
            for p in self.backbone.parameters():
                p.requires_grad = False

    def forward(self, img, audio_probs, cog):
        # image embedding
        z_img = self.backbone(img)               # (B, in_features)
        z_img = self.img_proj(z_img)             # (B, img_emb_dim)
        # audio
        z_audio = self.audio_mlp(audio_probs)
        # cognitive
        z_cog = self.cog_mlp(cog)
        # concat
        z = torch.cat([z_img, z_audio, z_cog], dim=1)
        out = self.head(z)
        return out
