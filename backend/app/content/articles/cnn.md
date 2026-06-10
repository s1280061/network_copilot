---
slug: cnn
title: CNN（畳み込みニューラルネットワーク）
level: 3
category: DL
related: [pytorch, deep-learning, opencv, rnn-lstm]
next: [rnn-lstm]
tags: [cnn, deep-learning, pytorch, image, computer-vision]
---

## 概要
CNN（Convolutional Neural Network）は画像データに特化したニューラルネットワークです。畳み込み層・プーリング層を積み重ね、画像の局所パターン（エッジ→テクスチャ→形状→物体）を階層的に学習します。画像分類・物体検出・セグメンテーションの基盤技術です。

## なぜ全結合層ではダメか
256×256の画像を全結合層に入力すると入力次元が65,536になり、パラメータ数が爆発します。CNNは**局所受容野（畳み込み）と重み共有**で、位置によらず同じフィルタを適用するため、大幅にパラメータ数を削減できます。

## 畳み込みの仕組み

```mermaid
graph LR
  A[入力 H×W×C] --> B[Conv Layer<br/>フィルタK×K×C×F]
  B --> C[特徴マップ H'×W'×F]
  C --> D[Pooling<br/>空間サイズを縮小]
  D --> E[次のConv...]
  E --> F[Flatten → FC]
  F --> G[出力（クラス確率）]
```

## PyTorchでCNNを実装

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN(nn.Module):
    def __init__(self, n_classes: int = 10):
        super().__init__()
        # 畳み込みブロック1
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.bn1   = nn.BatchNorm2d(32)
        # 畳み込みブロック2
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2   = nn.BatchNorm2d(64)
        # 畳み込みブロック3
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3   = nn.BatchNorm2d(128)
        # プーリング・ドロップアウト
        self.pool    = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout2d(0.3)
        # 全結合層（入力32×32 → 3回pool → 4×4×128）
        self.fc1 = nn.Linear(128 * 4 * 4, 256)
        self.fc2 = nn.Linear(256, n_classes)

    def forward(self, x):
        # (B, 3, 32, 32) → (B, 32, 32, 32) → (B, 32, 16, 16)
        x = self.pool(F.relu(self.bn1(self.conv1(x))))
        # → (B, 64, 8, 8)
        x = self.pool(F.relu(self.bn2(self.conv2(x))))
        # → (B, 128, 4, 4)
        x = self.pool(F.relu(self.bn3(self.conv3(x))))
        x = self.dropout(x)
        x = x.view(x.size(0), -1)       # Flatten
        x = F.relu(self.fc1(x))
        return self.fc2(x)

model = CNN(n_classes=10)
x = torch.randn(8, 3, 32, 32)          # バッチ8枚・3ch・32×32
print(model(x).shape)                   # (8, 10)
print(f"パラメータ数: {sum(p.numel() for p in model.parameters()):,}")
```

## CIFAR-10 でのトレーニング

```python
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
import torch.optim as optim

transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),      # データ拡張
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(0.2, 0.2, 0.2),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465),
                         (0.2023, 0.1994, 0.2010)),
])
transform_val = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465),
                         (0.2023, 0.1994, 0.2010)),
])

train_set = torchvision.datasets.CIFAR10(root="./data", train=True,
                                          download=True, transform=transform_train)
val_set   = torchvision.datasets.CIFAR10(root="./data", train=False,
                                          download=True, transform=transform_val)
train_loader = DataLoader(train_set, batch_size=128, shuffle=True,  num_workers=2)
val_loader   = DataLoader(val_set,   batch_size=256, shuffle=False, num_workers=2)

device    = "cuda" if torch.cuda.is_available() else "cpu"
model     = CNN(10).to(device)
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-3)
scheduler = optim.lr_scheduler.OneCycleLR(
    optimizer, max_lr=3e-3, epochs=50, steps_per_epoch=len(train_loader)
)
```

## 転移学習（Transfer Learning）

```python
import torchvision.models as models

# ImageNetで事前学習済みのResNet18を使う
backbone = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

# 最終層だけ自分のクラス数に置き換える
n_classes = 5
backbone.fc = nn.Linear(backbone.fc.in_features, n_classes)

# バックボーンを固定して最終層だけ学習（Fine-tuning）
for param in backbone.parameters():
    param.requires_grad = False
for param in backbone.fc.parameters():
    param.requires_grad = True

optimizer_ft = optim.Adam(filter(lambda p: p.requires_grad, backbone.parameters()),
                          lr=1e-3)

# --- 数エポック後に全層を解放して細かくチューニング ---
for param in backbone.parameters():
    param.requires_grad = True
optimizer_full = optim.AdamW(backbone.parameters(), lr=1e-4, weight_decay=1e-3)
```

## フィルタの可視化

```python
import matplotlib.pyplot as plt
import numpy as np

# 最初の畳み込み層のフィルタを可視化
filters = model.conv1.weight.data.cpu().numpy()  # (32, 3, 3, 3)

fig, axes = plt.subplots(4, 8, figsize=(12, 6))
for i, ax in enumerate(axes.flatten()):
    if i >= len(filters):
        ax.axis("off")
        continue
    f = filters[i]
    f = (f - f.min()) / (f.max() - f.min() + 1e-8)
    ax.imshow(f.transpose(1, 2, 0))
    ax.axis("off")
plt.suptitle("Conv1 フィルタ（32個）")
plt.tight_layout()
plt.show()
```

## 代表的なCNNアーキテクチャ

| モデル | 年 | 特徴 |
|---|---|---|
| AlexNet | 2012 | Deep Learning ブレイクスルー |
| VGG16 | 2014 | 3×3畳み込みの積み重ね |
| ResNet | 2015 | スキップ接続で100層超え可能 |
| EfficientNet | 2019 | 精度・速度のトレードオフが最良 |
| ConvNeXt | 2022 | Transformerの設計思想をCNNに |

## 次に学ぶべき内容
時系列・系列データを扱う [[rnn-lstm]] を学びましょう。
