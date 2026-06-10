---
slug: anomaly-detection
title: 異常検知（Isolation Forest・Autoencoder・統計的手法）
level: 3
category: ML
related: [ml-basics, statistics, time-series-analysis, clustering]
next: []
tags: [anomaly-detection, isolation-forest, autoencoder, python, scikit-learn]
---

## 概要
異常検知は正常パターンから外れたデータを自動識別する技術です。車載ネットワークでは「不正なCAN IDのパケット」「異常なデータレート急上昇」「未知のECUからの通信」など、サイバー攻撃・故障の早期発見に重要です。ラベルなしデータで学習できる教師なし手法が主流です。

## 統計的手法（Z-スコア・IQR）

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler

np.random.seed(42)

# CANバスのメッセージレート（正常）+ 異常点を混入
normal   = np.random.normal(100, 10, 500)
outliers = np.array([200, 210, -50, 5, 190])
data     = np.concatenate([normal, outliers])
np.random.shuffle(data)

# Z-スコア法
z_scores = np.abs((data - data.mean()) / data.std())
anomalies_z = data[z_scores > 3]
print(f"Z-スコア法（|z|>3）: {len(anomalies_z)} 件の異常")

# IQR法（外れ値に頑健）
q1, q3 = np.percentile(data, [25, 75])
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
anomalies_iqr = data[(data < lower) | (data > upper)]
print(f"IQR法: {len(anomalies_iqr)} 件の異常")

plt.figure(figsize=(10, 4))
plt.plot(data, "b.", alpha=0.4, label="正常")
plt.axhline(upper, color="red",    linestyle="--", label=f"上限 {upper:.1f}")
plt.axhline(lower, color="orange", linestyle="--", label=f"下限 {lower:.1f}")
plt.scatter(np.where((data < lower) | (data > upper))[0], data[(data < lower) | (data > upper)],
            color="red", s=100, zorder=5, label="異常")
plt.legend()
plt.title("IQR法による異常検知")
plt.show()
```

## Isolation Forest

```python
# 2次元特徴量（パケットレート + ペイロードサイズ）
n_normal  = 400
n_anomaly = 20
X_normal  = np.random.normal([100, 200], [10, 20], (n_normal, 2))
X_anomaly = np.random.uniform([150, 300], [250, 500], (n_anomaly, 2))
X = np.vstack([X_normal, X_anomaly])
y_true = np.array([1]*n_normal + [-1]*n_anomaly)  # 1=正常, -1=異常

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

iso = IsolationForest(
    n_estimators=200,
    contamination=0.05,   # 想定異常率
    random_state=42,
)
y_pred = iso.fit_predict(X_scaled)
scores  = iso.score_samples(X_scaled)   # 低いほど異常

from sklearn.metrics import classification_report
print(classification_report(y_true, y_pred, target_names=["異常", "正常"]))

# 決定境界の可視化
xx, yy = np.meshgrid(np.linspace(-3, 3, 200), np.linspace(-3, 3, 200))
Z = iso.decision_function(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

plt.figure(figsize=(9, 6))
plt.contourf(xx, yy, Z, levels=20, cmap="RdYlGn", alpha=0.4)
plt.colorbar(label="異常スコア（低=異常）")
plt.scatter(*scaler.transform(X_normal).T, c="blue", s=20, alpha=0.5, label="正常")
plt.scatter(*scaler.transform(X_anomaly).T, c="red", s=60, marker="x", label="異常")
plt.legend()
plt.title("Isolation Forest 決定境界")
plt.show()
```

## One-Class SVM

```python
oc_svm = OneClassSVM(kernel="rbf", gamma="auto", nu=0.05)
oc_svm.fit(scaler.transform(X_normal))   # 正常データだけで学習
y_pred_svm = oc_svm.predict(X_scaled)

print("One-Class SVM:")
print(classification_report(y_true, y_pred_svm, target_names=["異常", "正常"]))
```

## オートエンコーダーによる異常検知

```python
import torch
import torch.nn as nn

class AnomalyAutoencoder(nn.Module):
    def __init__(self, in_dim=2, latent=1):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(in_dim, 16), nn.ReLU(), nn.Linear(16, latent))
        self.dec = nn.Sequential(nn.Linear(latent, 16), nn.ReLU(), nn.Linear(16, in_dim))
    def forward(self, x):
        return self.dec(self.enc(x))

model    = AnomalyAutoencoder()
opt      = torch.optim.Adam(model.parameters(), lr=1e-3)
crit     = nn.MSELoss(reduction="none")

# 正常データだけで訓練
X_train  = torch.FloatTensor(scaler.transform(X_normal))
for _ in range(500):
    loss = crit(model(X_train), X_train).mean()
    opt.zero_grad(); loss.backward(); opt.step()

# 再構成誤差で異常スコアを計算
X_all   = torch.FloatTensor(X_scaled)
with torch.no_grad():
    recon   = model(X_all)
    errors  = crit(recon, X_all).mean(dim=1).numpy()

threshold = np.percentile(errors[:n_normal], 95)
y_ae = np.where(errors > threshold, -1, 1)

print(f"再構成誤差閾値: {threshold:.4f}")
print(classification_report(y_true, y_ae, target_names=["異常", "正常"]))
```

## 時系列での異常検知（移動ウィンドウ）

```python
# ECU温度センサーの時系列
t = np.linspace(0, 50, 500)
temp = 80 + 5 * np.sin(t) + np.random.normal(0, 1, 500)
# 異常注入: 急激な温度上昇
temp[200:210] += 30

window = 30
rolling_mean = pd.Series(temp).rolling(window).mean()
rolling_std  = pd.Series(temp).rolling(window).std()
z_roll = (pd.Series(temp) - rolling_mean) / (rolling_std + 1e-6)

plt.figure(figsize=(12, 5))
plt.plot(temp, label="温度", alpha=0.8)
plt.fill_between(range(len(temp)),
                 rolling_mean - 3*rolling_std,
                 rolling_mean + 3*rolling_std,
                 alpha=0.2, color="green", label="正常範囲 ±3σ")
anomaly_idx = np.where(np.abs(z_roll) > 3)[0]
plt.scatter(anomaly_idx, temp[anomaly_idx], color="red", s=80, zorder=5, label="検知異常")
plt.legend()
plt.title("移動ウィンドウ Z-スコアによる時系列異常検知")
plt.show()
```
