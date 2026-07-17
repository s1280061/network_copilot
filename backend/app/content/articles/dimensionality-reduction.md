---
slug: dimensionality-reduction
title: 次元削減（PCA・t-SNE・UMAP）
level: 2
category: ML
related: [ml-basics, clustering, scikit-learn, numpy]
next: []
tags: [pca, tsne, umap, dimensionality-reduction, python, scikit-learn]
---

## 概要
「500次元のデータをグラフで見たい」「特徴量が多すぎてモデルが遅い」――次元削減はこの2つの問題を解決します。高次元データを低次元空間に圧縮することで、可視化・クラスタリング・計算高速化が可能になります。PCA（線形・高速・解釈可能）、t-SNE（非線形・可視化に最適）、UMAP（非線形・大規模対応）の3つを目的に合わせて使い分けましょう。

## 活用シーン
- **ECUグループの可視化**: 数百の通信特徴量を2次元に圧縮してグループを散布図で確認
- **ノイズ除去**: PCAで主要な情報を保持しつつノイズとなる小さな変動を除去
- **特徴量圧縮**: 機械学習モデルへの入力次元を減らして学習速度を向上

## 主要な数式

**PCA**：共分散行列 \(\mathbf{\Sigma}\) の固有値分解で分散最大の軸を求める。

$$\mathbf{\Sigma}\mathbf{v}_k = \lambda_k \mathbf{v}_k, \qquad \text{累積寄与率} = \frac{\sum_{k=1}^{m}\lambda_k}{\sum_{j=1}^{d}\lambda_j}$$

**t-SNE**：高次元の類似度を条件付き確率で、低次元を t 分布で表し KL ダイバージェンスを最小化。

$$p_{j|i} = \frac{\exp(-\lVert \mathbf{x}_i - \mathbf{x}_j \rVert^2 / 2\sigma_i^2)}{\sum_{k\ne i}\exp(-\lVert \mathbf{x}_i - \mathbf{x}_k \rVert^2 / 2\sigma_i^2)}$$

$$q_{ij} = \frac{(1 + \lVert \mathbf{y}_i - \mathbf{y}_j \rVert^2)^{-1}}{\sum_{k\ne l}(1 + \lVert \mathbf{y}_k - \mathbf{y}_l \rVert^2)^{-1}}, \qquad \mathrm{KL}(P\Vert Q) = \sum_{i\ne j} p_{ij}\log\frac{p_{ij}}{q_{ij}}$$

## PCA（主成分分析）

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

np.random.seed(42)

# 車載ECU通信ログの特徴量（10次元）
n_samples  = 500
n_features = 10
labels_true = np.repeat([0, 1, 2, 3, 4], n_samples // 5)   # 5種類のECUグループ

# 各グループは異なる中心を持つ
centers = np.random.randn(5, n_features) * 3
X = np.vstack([
    np.random.randn(n_samples // 5, n_features) + centers[i]
    for i in range(5)
])

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# PCA
pca = PCA()
pca.fit(X_scaled)

# 寄与率
explained = pca.explained_variance_ratio_
cumsum    = np.cumsum(explained)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].bar(range(1, n_features+1), explained * 100)
axes[0].set_xlabel("主成分")
axes[0].set_ylabel("寄与率 (%)")
axes[0].set_title("各主成分の寄与率")

axes[1].plot(range(1, n_features+1), cumsum * 100, "bo-")
axes[1].axhline(90, color="red", linestyle="--", label="90%ライン")
axes[1].set_xlabel("主成分数")
axes[1].set_ylabel("累積寄与率 (%)")
axes[1].set_title("累積寄与率")
axes[1].legend()
plt.tight_layout()
plt.show()

n_components_90 = (cumsum >= 0.90).argmax() + 1
print(f"90%の分散を説明するのに必要な主成分: {n_components_90}")
```

**数式で表すと**

$$
\mathbf{\Sigma} = \frac{1}{n-1}\mathbf{X}^\top \mathbf{X}, \qquad \mathbf{\Sigma}\mathbf{v}_k = \lambda_k \mathbf{v}_k, \qquad \text{寄与率}_k = \frac{\lambda_k}{\sum_{j=1}^{d}\lambda_j}
$$

`explained_variance_ratio_` は共分散行列 \(\mathbf{\Sigma}\) の固有値 \(\lambda_k\) を全体で正規化した値です。その累積和が 90% を超える最小の主成分数を採用します。

## PCAで2次元に圧縮・可視化

```python
pca2 = PCA(n_components=2)
X_pca = pca2.fit_transform(X_scaled)

plt.figure(figsize=(8, 6))
colors = plt.cm.tab10(np.linspace(0, 1, 5))
for i, color in enumerate(colors):
    mask = labels_true == i
    plt.scatter(X_pca[mask, 0], X_pca[mask, 1], c=[color], label=f"ECUグループ {i}", alpha=0.6, s=30)
plt.xlabel(f"PC1 ({explained[0]*100:.1f}%)")
plt.ylabel(f"PC2 ({explained[1]*100:.1f}%)")
plt.legend()
plt.title("PCA 2次元可視化")
plt.show()

# 主成分の負荷量（どの特徴量が重要か）
loadings = pd.DataFrame(
    pca2.components_.T,
    columns=["PC1", "PC2"],
    index=[f"Feature_{i}" for i in range(n_features)]
)
print(loadings.abs().sort_values("PC1", ascending=False))
```

**数式で表すと**

$$
\mathbf{Z} = \mathbf{X}\mathbf{W}, \qquad \mathbf{W} = [\mathbf{v}_1\ \mathbf{v}_2]
$$

`fit_transform` は上位 2 固有ベクトル（負荷量 `components_`）を並べた射影行列 \(\mathbf{W}\) にデータを掛け、各点を主成分座標 \(\mathbf{Z}\) に変換します。

## PCA・t-SNEによる次元削減の可視化

![PCA累積寄与率とt-SNE（手書き数字データ）](/images/charts/dimensionality-reduction.png)

## t-SNE（非線形次元削減）

```python
tsne = TSNE(
    n_components=2,
    perplexity=30,
    n_iter=1000,
    random_state=42,
    learning_rate="auto",
    init="pca",
)
X_tsne = tsne.fit_transform(X_scaled)

plt.figure(figsize=(8, 6))
for i, color in enumerate(colors):
    mask = labels_true == i
    plt.scatter(X_tsne[mask, 0], X_tsne[mask, 1], c=[color], label=f"ECUグループ {i}", alpha=0.6, s=30)
plt.legend()
plt.title("t-SNE 2次元可視化")
plt.show()
```

**数式で表すと**

$$
p_{ij} = \frac{p_{j|i} + p_{i|j}}{2n}, \qquad \mathrm{KL}(P\Vert Q) = \sum_{i\ne j} p_{ij}\log\frac{p_{ij}}{q_{ij}}
$$

t-SNE は高次元での対称化類似度 \(p_{ij}\) と、低次元で t 分布に基づく \(q_{ij}\) の KL ダイバージェンスを勾配降下で最小化し、埋め込み座標 \(\mathbf{y}_i\) を求めます。

## UMAP（高速・グローバル構造保持）

```python
# pip install umap-learn
import umap

reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=15, min_dist=0.1)
X_umap  = reducer.fit_transform(X_scaled)

plt.figure(figsize=(8, 6))
for i, color in enumerate(colors):
    mask = labels_true == i
    plt.scatter(X_umap[mask, 0], X_umap[mask, 1], c=[color], label=f"ECUグループ {i}", alpha=0.6, s=30)
plt.legend()
plt.title("UMAP 2次元可視化")
plt.show()
```

## 手法の比較

```mermaid
graph TD
  A[次元削減の目的] --> B{線形構造で\n十分か?}
  B -->|Yes| C[PCA]
  B -->|No| D{速度重視?}
  D -->|Yes| E[UMAP]
  D -->|No| F[t-SNE]

  C --> C1["✅ 高速・解釈可能\n✅ 逆変換可能\n❌ 非線形パターン苦手"]
  E --> E1["✅ 大規模データ対応\n✅ グローバル構造保持\n❌ 再現性が不安定な場合"]
  F --> F1["✅ 局所構造の可視化優秀\n❌ 低速・大規模に不向き\n❌ グローバル構造不保持"]
```

## オートエンコーダー（深層次元削減）

```python
import torch
import torch.nn as nn

class Autoencoder(nn.Module):
    def __init__(self, input_dim=10, latent_dim=2):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32), nn.ReLU(),
            nn.Linear(32, 16),        nn.ReLU(),
            nn.Linear(16, latent_dim),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 16), nn.ReLU(),
            nn.Linear(16, 32),         nn.ReLU(),
            nn.Linear(32, input_dim),
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z), z

model = Autoencoder(input_dim=10, latent_dim=2)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.MSELoss()

X_tensor = torch.FloatTensor(X_scaled)
for epoch in range(200):
    recon, z = model(X_tensor)
    loss = criterion(recon, X_tensor)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

print(f"最終損失: {loss.item():.4f}")

with torch.no_grad():
    _, X_ae = model(X_tensor)
    X_ae = X_ae.numpy()

plt.figure(figsize=(8, 6))
for i, color in enumerate(colors):
    mask = labels_true == i
    plt.scatter(X_ae[mask, 0], X_ae[mask, 1], c=[color], label=f"ECUグループ {i}", alpha=0.6, s=30)
plt.legend()
plt.title("オートエンコーダー 潜在空間")
plt.show()
```

**数式で表すと**

$$
\mathbf{z} = f_{\text{enc}}(\mathbf{x}), \quad \hat{\mathbf{x}} = f_{\text{dec}}(\mathbf{z}), \qquad \mathcal{L} = \frac{1}{n}\sum_{i=1}^{n}\lVert \mathbf{x}_i - \hat{\mathbf{x}}_i \rVert^2
$$

エンコーダで低次元の潜在表現 \(\mathbf{z}\) に圧縮し、デコーダで元の次元へ復元します。復元誤差（MSE）\(\mathcal{L}\) を最小化することで、非線形な次元削減が学習されます。

## よくある間違いと対処法

1. **スケーリングなしでPCAを使う** → PCAは分散の大きい方向を主成分にするため、スケールが違う特徴量があると大きい値の特徴量が支配する。必ず `StandardScaler` を使う。
2. **t-SNEの結果をそのまま距離として解釈する** → t-SNEは局所構造（クラスタ）を保持するが、クラスタ間の距離は意味がない。グローバルな構造を見たい場合はUMAPを使う。
3. **t-SNEを変換（transform）に使おうとする** → t-SNEは `fit_transform()` のみで、新しいデータを変換できない。本番環境での特徴量変換にはPCAまたはUMAPを使う。
4. **累積寄与率を確認しない** → PCAのコンポーネント数を決めずに使うと情報損失が大きくなる。`cumsum(explained_variance_ratio_)` で90%以上を目安にコンポーネント数を決める。

## まとめ

- PCA: 線形・高速・逆変換可能・スケーリング必須・90%累積寄与率でコンポーネント数を決める
- t-SNE: 非線形・可視化専用（変換できない）・局所構造保持・`perplexity=30` が出発点
- UMAP: 非線形・大規模データ対応・グローバル構造保持・本番環境での変換も可能
- オートエンコーダ: 非線形・深層学習による次元削減・異常検知にも応用できる
