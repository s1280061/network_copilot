---
slug: clustering
title: クラスタリング（K-Means・DBSCAN・階層型）
level: 2
category: ML
related: [ml-basics, scikit-learn, dimensionality-reduction, anomaly-detection]
next: []
tags: [clustering, unsupervised, kmeans, dbscan, python, scikit-learn]
---

## 概要
クラスタリングはラベルなしデータをグループに分ける教師なし学習です。車載ネットワークでは「同じ挙動パターンのECUをグループ化」「通信フローの分類」「異常なパケットの検出」に活用されます。PythonではScikit-learnが主要ライブラリです。

## K-Meansクラスタリング

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

np.random.seed(42)

# 車載ネットワークの通信フロー特徴量（例）
n = 300
data = np.vstack([
    np.random.normal([10, 100],  [2, 20],  (n//3, 2)),   # 制御系
    np.random.normal([50, 500],  [5, 50],  (n//3, 2)),   # 診断系
    np.random.normal([200, 50],  [20, 5],  (n//3, 2)),   # センサー系
])
feature_names = ["packet_rate", "payload_size"]

scaler = StandardScaler()
X = scaler.fit_transform(data)

# K-Meansでk=3
km = KMeans(n_clusters=3, random_state=42, n_init=10)
labels_km = km.fit_predict(X)
print(f"シルエット係数: {silhouette_score(X, labels_km):.3f}")

plt.figure(figsize=(8, 5))
for k in range(3):
    mask = labels_km == k
    plt.scatter(data[mask, 0], data[mask, 1], label=f"Cluster {k}", alpha=0.6)
centers = scaler.inverse_transform(km.cluster_centers_)
plt.scatter(centers[:, 0], centers[:, 1], marker="*", s=200, c="red", zorder=5, label="重心")
plt.xlabel("Packet Rate")
plt.ylabel("Payload Size")
plt.legend()
plt.title("K-Means クラスタリング")
plt.show()
```

## エルボー法とシルエット分析

```python
inertias   = []
silhouettes = []
k_range = range(2, 10)

for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X, labels))

fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(k_range, inertias, "bo-")
axes[0].set_xlabel("k")
axes[0].set_ylabel("慣性（Inertia）")
axes[0].set_title("エルボー法")

axes[1].plot(k_range, silhouettes, "ro-")
axes[1].set_xlabel("k")
axes[1].set_ylabel("シルエット係数")
axes[1].set_title("シルエット分析（高いほど良い）")

plt.tight_layout()
plt.show()
```

## DBSCANクラスタリング

```python
# 密度ベース: 外れ値を自動検出できる
db = DBSCAN(eps=0.3, min_samples=5)
labels_db = db.fit_predict(X)

n_clusters = len(set(labels_db)) - (1 if -1 in labels_db else 0)
n_noise    = (labels_db == -1).sum()
print(f"検出クラスタ数: {n_clusters}")
print(f"外れ値（ノイズ）: {n_noise} 点")

plt.figure(figsize=(8, 5))
unique = set(labels_db)
colors = plt.cm.tab10(np.linspace(0, 1, len(unique)))
for k, col in zip(sorted(unique), colors):
    mask = labels_db == k
    label = "ノイズ（異常）" if k == -1 else f"Cluster {k}"
    marker = "x" if k == -1 else "o"
    plt.scatter(data[mask, 0], data[mask, 1], c=[col], label=label, marker=marker, alpha=0.6)
plt.legend()
plt.title("DBSCAN クラスタリング")
plt.show()
```

## 階層型クラスタリング（デンドログラム）

```python
from scipy.cluster.hierarchy import dendrogram, linkage

# サンプル数を減らしてデンドログラムを見やすくする
sample = X[:50]
Z = linkage(sample, method="ward")

plt.figure(figsize=(14, 5))
dendrogram(Z, leaf_rotation=90, leaf_font_size=8)
plt.title("階層型クラスタリング（Ward法）")
plt.ylabel("距離")
plt.tight_layout()
plt.show()

# 指定クラスタ数でラベル付け
agg = AgglomerativeClustering(n_clusters=3, linkage="ward")
labels_agg = agg.fit_predict(X)
print(f"Agglomerative シルエット: {silhouette_score(X, labels_agg):.3f}")
```

## クラスタリングの比較

```mermaid
graph LR
  A[クラスタリング手法] --> B[K-Means]
  A --> C[DBSCAN]
  A --> D[階層型]

  B --> B1["✅ 高速・スケーラブル\n❌ k を事前指定\n❌ 外れ値に弱い"]
  C --> C1["✅ 外れ値を自動検出\n✅ 非球形クラスタ対応\n❌ 高次元データに弱い"]
  D --> D1["✅ kを決めなくてよい\n✅ デンドログラムで可視化\n❌ 大規模データに遅い"]
```

## 実用例：ネットワークフロー分類

```python
from sklearn.pipeline import Pipeline
from sklearn.decomposition import PCA

# パイプラインで前処理+次元削減+クラスタリング
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("pca",    PCA(n_components=2)),
    ("km",     KMeans(n_clusters=4, random_state=42, n_init=10)),
])

# より多くの特徴量があると仮定
np.random.seed(0)
X_multi = np.random.randn(500, 8)  # 8次元特徴量
pipe.fit(X_multi)
cluster_labels = pipe.named_steps["km"].labels_

print("クラスタ別件数:")
for k, count in zip(*np.unique(cluster_labels, return_counts=True)):
    print(f"  Cluster {k}: {count} 件")
```
