---
slug: linear-regression
title: 線形回帰
level: 2
category: ML
related: [ml-basics, scikit-learn, classification]
next: [classification]
tags: [ml, regression, python, data-science]
---

## 概要
線形回帰は「入力 X から連続値 y を予測する」最もシンプルな機械学習モデルです。数値の予測（売上・気温・価格など）に使います。モデルの解釈性が高く、まず試すべきベースラインです。

```mermaid
graph LR
  X["入力 X"] --> M["線形モデル<br/>y = wᵀx + b"]
  M --> Y["連続値 ŷ を予測"]
  Y -. "誤差で w を更新" .-> M
```

## 主要な数式

**予測モデル**：

$$\hat{y} = w_0 + w_1 x_1 + \cdots + w_d x_d = \mathbf{w}^\top \mathbf{x}$$

**損失関数（平均二乗誤差 MSE）**：

$$\mathcal{L}(\mathbf{w}) = \frac{1}{n}\sum_{i=1}^{n}\left(y_i - \mathbf{w}^\top \mathbf{x}_i\right)^2$$

**勾配降下法**による更新（学習率 $\eta$）：

$$\mathbf{w} \leftarrow \mathbf{w} - \eta\,\nabla_{\mathbf{w}}\mathcal{L}$$

**正則化**（Ridge は L2、Lasso は L1）：

$$\mathcal{L}_{\text{Ridge}} = \mathrm{MSE} + \lambda\sum_j w_j^2, \qquad \mathcal{L}_{\text{Lasso}} = \mathrm{MSE} + \lambda\sum_j |w_j|$$

## なぜ必要か
複雑なモデル（ランダムフォレスト・ニューラルネット）は精度は高いが解釈が難しい。線形回帰は「どの特徴量がどれだけ予測に効いているか」が係数から直接読み取れ、ビジネス上の説明責任を果たしやすいという強みがあります。

## 単回帰（特徴量が1つ）

```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

np.random.seed(42)
# 広告費（万円）→ 売上（万円）
ad_spend = np.random.uniform(10, 100, 80).reshape(-1, 1)
sales    = 3.2 * ad_spend.ravel() + np.random.randn(80) * 40 + 50

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    ad_spend, sales, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)

print(f"傾き（係数）: {model.coef_[0]:.2f}")   # 広告費1万円増 → 売上+??万円
print(f"切片        : {model.intercept_:.2f}")

y_pred = model.predict(X_test)
print(f"RMSE: {mean_squared_error(y_test, y_pred)**0.5:.2f}")
print(f"R²  : {r2_score(y_test, y_pred):.3f}")

# 可視化
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(X_test, y_test, alpha=0.6, label="実測値")
ax.plot(np.sort(X_test, axis=0),
        model.predict(np.sort(X_test, axis=0)),
        color="tomato", linewidth=2, label="回帰直線")
ax.set_xlabel("広告費（万円）")
ax.set_ylabel("売上（万円）")
ax.set_title("単回帰：広告費 vs 売上")
ax.legend()
plt.tight_layout()
plt.show()
```

## 重回帰（特徴量が複数）

```python
import pandas as pd
from sklearn.linear_model import LinearRegression

df = pd.DataFrame({
    "広告費":     np.random.uniform(10, 100, 200),
    "店舗面積":   np.random.uniform(50, 300, 200),
    "スタッフ数": np.random.randint(2, 20, 200),
})
df["売上"] = (
    3.0 * df["広告費"]
  + 0.5 * df["店舗面積"]
  + 15  * df["スタッフ数"]
  + np.random.randn(200) * 50
  + 100
)

X = df[["広告費", "店舗面積", "スタッフ数"]]
y = df["売上"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)

# 係数を見て「どの変数が効いているか」を確認
coef_df = pd.Series(model.coef_, index=X.columns).sort_values(key=abs, ascending=False)
print(coef_df)
```

## 過学習・正則化パスの可視化

![モデル複雑度とRidge/Lasso係数パス](/images/charts/linear-regression-paths.png)

## 正則化 — Ridge（L2）と Lasso（L1）

```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

# 特徴量が多い・多重共線性がある場合は正則化が有効

# Ridge: 全係数を小さく抑える（特徴量が多い場合）
ridge = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
ridge.fit(X_train, y_train)

# Lasso: 不要な特徴量の係数を0にする（自動特徴量選択）
lasso = make_pipeline(StandardScaler(), Lasso(alpha=0.1))
lasso.fit(X_train, y_train)

# ElasticNet: RidgeとLassoの混合
enet = make_pipeline(StandardScaler(), ElasticNet(alpha=0.1, l1_ratio=0.5))
enet.fit(X_train, y_train)

for name, m in [("Ridge", ridge), ("Lasso", lasso), ("ElasticNet", enet)]:
    r2 = r2_score(y_test, m.predict(X_test))
    print(f"{name}: R²={r2:.3f}")
```

## 残差分析（モデルの診断）

```python
y_pred    = model.predict(X_test)
residuals = y_test - y_pred

fig, axes = plt.subplots(1, 2, figsize=(11, 4))

# 残差プロット（ランダムに散らばっていれば正常）
axes[0].scatter(y_pred, residuals, alpha=0.5)
axes[0].axhline(0, color="red", linestyle="--")
axes[0].set_xlabel("予測値")
axes[0].set_ylabel("残差")
axes[0].set_title("残差プロット")

# 残差の分布（正規分布に近いほど良い）
axes[1].hist(residuals, bins=25, color="steelblue", edgecolor="white")
axes[1].set_title("残差のヒストグラム")

plt.tight_layout()
plt.show()
```

## 多項式回帰（非線形関係を線形モデルで近似）

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

X_nl  = np.linspace(-3, 3, 100).reshape(-1, 1)
y_nl  = X_nl.ravel() ** 2 + np.random.randn(100) * 0.5

model_poly = make_pipeline(
    PolynomialFeatures(degree=2, include_bias=False),
    LinearRegression()
)
model_poly.fit(X_nl, y_nl)
print(f"R²: {model_poly.score(X_nl, y_nl):.3f}")
```

## 評価指標のまとめ

| 指標 | 数式の意味 | 特徴 |
|---|---|---|
| MSE | 誤差の二乗平均 | 大きな誤差にペナルティ |
| RMSE | MSEの平方根 | y と同じ単位で解釈しやすい |
| MAE | 誤差の絶対値平均 | 外れ値に強い |
| R² | 1 − SS_res/SS_tot | 0〜1、1が完全予測 |

## 次に学ぶべき内容
カテゴリを予測する [[classification]] へ進みましょう。
