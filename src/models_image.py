# src/models_image.py
import torch
import torch.nn as nn
import torchvision.models as models

def get_resnet18(num_classes=4, pretrained=True):
    model = models.resnet18(pretrained=pretrained)
    # replace final fc
    in_feats = model.fc.in_features
    model.fc = nn.Linear(in_feats, num_classes)
    return model

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=4):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3,16,3,padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16,32,3,padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32,64,3,padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(1)
        )
        self.classifier = nn.Linear(64, num_classes)
    def forward(self, x):
        x = self.features(x).view(x.size(0), -1)
        return self.classifier(x)
