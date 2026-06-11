---
slug: gradient-boosting
title: 勾配ブースティング（XGBoost・LightGBM）
level: 3
category: ML
related: [classification, scikit-learn, ml-basics]
next: []
tags: [ml, xgboost, lightgbm, boosting, python, data-science]
---

## 概要
勾配ブースティング（Gradient Boosting）は、弱い決定木を順番に積み重ねて強力なモデルを作るアンサンブル手法です。Kaggle等のデータコンペで最もよく優勝するアルゴリズムで、表形式データの精度最高峰とされています。

## 主要な数式

**加法モデル**（$M$ 本の木 $h_m$ を学習率 $\nu$ で逐次追加）：

$$F_M(\mathbf{x}) = F_0(\mathbf{x}) + \nu\sum_{m=1}^{M} h_m(\mathbf{x})$$

各ステップで損失 $L$ の負の勾配（擬似残差）を新しい木で近似する：

$$r_{im} = -\left[\frac{\partial L(y_i, F(\mathbf{x}_i))}{\partial F(\mathbf{x}_i)}\right]_{F=F_{m-1}}$$

**XGBoost の正則化付き目的関数**（2次のテイラー展開＋木の複雑さ罰則）：

$$\mathcal{L} = \sum_{i} L(y_i, \hat{y}_i) + \sum_{m}\Omega(h_m), \qquad \Omega(h) = \gamma T + \frac{1}{2}\lambda\sum_{j=1}^{T} w_j^2$$

ここで $T$ は葉の数、$w_j$ は葉の重み。

## なぜ強いか

```mermaid
graph LR
  A[Tree 1<br/>粗い予測] -->|誤差を渡す| B[Tree 2<br/>誤差を補正]
  B -->|誤差を渡す| C[Tree 3<br/>さらに補正]
  C --> D[... N本]
  D --> E[最終予測<br/>合計]
```

各木が「前の木の残差（誤差）」を学習するため、少しずつ精度が上がります。ランダムフォレストが並列で独立した木を作るのに対し、ブースティングは**直列で誤差を修正していく**点が違います。

## XGBoost

```python
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
import numpy as np

from sklearn.datasets import make_classification
X, y = make_classification(n_samples=5000, n_features=30, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 基本的な使い方（scikit-learn API）
model_xgb = xgb.XGBClassifier(
    n_estimators   = 500,
    learning_rate  = 0.05,
    max_depth      = 6,
    subsample      = 0.8,
    colsample_bytree = 0.8,
    use_label_encoder = False,
    eval_metric    = "logloss",
    random_state   = 42,
)

# early_stopping: 検証スコアが改善しなくなったら止める
model_xgb.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False,
)

y_pred  = model_xgb.predict(X_test)
y_proba = model_xgb.predict_proba(X_test)[:, 1]
print(classification_report(y_test, y_pred))
print(f"AUC: {roc_auc_score(y_test, y_proba):.4f}")
```

## LightGBM（XGBより高速）

```python
import lightgbm as lgb

model_lgb = lgb.LGBMClassifier(
    n_estimators    = 1000,
    learning_rate   = 0.05,
    num_leaves      = 31,
    max_depth       = -1,        # 制限なし（num_leavesで制御）
    subsample       = 0.8,
    colsample_bytree = 0.8,
    random_state    = 42,
    n_jobs          = -1,
)

model_lgb.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    callbacks=[lgb.early_stopping(50), lgb.log_evaluation(100)],
)

print(f"AUC: {roc_auc_score(y_test, model_lgb.predict_proba(X_test)[:,1]):.4f}")
```

## 学習曲線・特徴量重要度の可視化

![GBM vs RF 学習曲線と特徴量重要度](/images/charts/gradient-boosting.png)

## 特徴量重要度の可視化

```python
import pandas as pd
import matplotlib.pyplot as plt

feat_names = [f"feature_{i}" for i in range(30)]

# XGBoost
xgb_imp = pd.Series(model_xgb.feature_importances_, index=feat_names)
lgb_imp = pd.Series(model_lgb.feature_importances_, index=feat_names)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

xgb_imp.sort_values().tail(15).plot(kind="barh", ax=axes[0], color="steelblue")
axes[0].set_title("XGBoost 特徴量重要度")

lgb_imp.sort_values().tail(15).plot(kind="barh", ax=axes[1], color="mediumseagreen")
axes[1].set_title("LightGBM 特徴量重要度")

plt.tight_layout()
plt.show()
```

## ハイパーパラメータチューニング（Optuna）

```python
import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

def objective(trial):
    params = {
        "n_estimators":    trial.suggest_int("n_estimators", 100, 1000),
        "learning_rate":   trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "max_depth":       trial.suggest_int("max_depth", 3, 9),
        "num_leaves":      trial.suggest_int("num_leaves", 15, 127),
        "subsample":       trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree":trial.suggest_float("colsample_bytree", 0.5, 1.0),
        "random_state":    42,
        "n_jobs":          -1,
    }
    model = lgb.LGBMClassifier(**params)
    score = cross_val_score(model, X_train, y_train, cv=3, scoring="roc_auc").mean()
    return score

from sklearn.model_selection import cross_val_score
study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=50)

print(f"Best AUC: {study.best_value:.4f}")
print(f"Best params: {study.best_params}")
```

## SHAP — モデルの予測根拠を説明する

```python
import shap

explainer = shap.TreeExplainer(model_lgb)
shap_values = explainer.shap_values(X_test[:200])

# 全特徴量の影響をまとめて表示
shap.summary_plot(shap_values[1], X_test[:200],
                  feature_names=feat_names, show=False)
plt.tight_layout()
plt.show()

# 個別予測の説明
shap.force_plot(
    explainer.expected_value[1],
    shap_values[1][0],
    X_test[0],
    feature_names=feat_names,
)
```

## XGBoost vs LightGBM 比較

| 項目 | XGBoost | LightGBM |
|---|---|---|
| 学習速度 | 普通 | **速い**（Leaf-wise成長）|
| メモリ | 普通 | **少ない** |
| 大規模データ | 可 | **得意** |
| カテゴリ変数 | 手動エンコード | **ネイティブ対応** |
| 欠損値 | 自動処理 | 自動処理 |
