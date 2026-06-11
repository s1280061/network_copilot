---
slug: time-series-statistics
title: 時系列統計（自己相関・定常性・ARIMAモデル）
level: 3
category: Statistics
related: [statistics, regression-analysis, anomaly-detection, time-series-analysis]
next: []
tags: [time-series, arima, acf, pacf, stationarity, forecasting, statsmodels]
---

## 概要
時系列データは「時間的に連続して観測されたデータ」です。通常の回帰分析では独立性の仮定が崩れるため、専用の手法が必要です。定常性の確認・自己相関の分析・ARIMAモデルの構築が時系列分析の基本的な流れです。

## 時系列の構成要素

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

# 時系列を 4 要素に分解
# 1. トレンド (Trend)     : 長期的な増減傾向
# 2. 季節性 (Seasonal)   : 周期的なパターン
# 3. 周期 (Cyclic)       : 不規則な長期波動（景気サイクルなど）
# 4. 不規則変動 (Residual): 説明できないランダムノイズ

np.random.seed(42)
n = 120
t = np.arange(n)

trend    = 0.05 * t
seasonal = 5 * np.sin(2 * np.pi * t / 12)   # 12ヶ月周期
noise    = np.random.normal(0, 1, n)
series   = trend + seasonal + noise + 20

idx = pd.date_range("2014-01", periods=n, freq="ME")
ts  = pd.Series(series, index=idx)

# 加法モデルで分解
result = seasonal_decompose(ts, model="additive", period=12)

fig, axes = plt.subplots(4, 1, figsize=(10, 8))
ts.plot(ax=axes[0], title="観測値")
result.trend.plot(ax=axes[1], title="トレンド")
result.seasonal.plot(ax=axes[2], title="季節性")
result.resid.plot(ax=axes[3], title="残差")
plt.tight_layout()
plt.show()
```

## 定常性の確認

```python
from statsmodels.tsa.stattools import adfuller, kpss

def check_stationarity(series, name=""):
    """ADF 検定と KPSS 検定で定常性を確認"""

    # ADF 検定: H0 = 単位根あり（非定常）
    adf_result = adfuller(series.dropna(), autolag="AIC")
    adf_p = adf_result[1]

    # KPSS 検定: H0 = 定常
    kpss_result = kpss(series.dropna(), regression="c", nlags="auto")
    kpss_p = kpss_result[1]

    print(f"\n--- {name} ---")
    print(f"ADF  検定: p={adf_p:.4f}  {'→ 定常' if adf_p < 0.05 else '→ 非定常（単位根あり）'}")
    print(f"KPSS 検定: p={kpss_p:.4f}  {'→ 非定常' if kpss_p < 0.05 else '→ 定常'}")

    # 両検定の組み合わせで判断
    if adf_p < 0.05 and kpss_p > 0.05:
        conclusion = "✓ 定常"
    elif adf_p > 0.05 and kpss_p < 0.05:
        conclusion = "✗ 非定常（差分が必要）"
    else:
        conclusion = "△ 判断困難"
    print(f"結論: {conclusion}")
    return adf_p < 0.05

# 元の系列（非定常）
stationary = check_stationarity(ts, "元の系列")

# 1階差分を取ると定常になることが多い
ts_diff = ts.diff().dropna()
check_stationarity(ts_diff, "1階差分")

# ログ変換（分散が増大するトレンドに有効）
ts_log = np.log(ts)
ts_log_diff = ts_log.diff().dropna()
check_stationarity(ts_log_diff, "対数差分")
```

## ACF / PACF の読み方

```python
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# ACF: 自己相関関数 → MA(q) の次数 q を特定
# PACF: 偏自己相関関数 → AR(p) の次数 p を特定

fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# AR(2) プロセスの例
ar_coefs = [1, -0.6, -0.3]   # AR(2): y_t = 0.6*y_{t-1} + 0.3*y_{t-2} + ε_t
from statsmodels.tsa.arima_process import arma_generate_sample
ar2_series = arma_generate_sample(ar=ar_coefs, ma=[1], nsample=300, seed=42)

plot_acf(ar2_series,  lags=20, ax=axes[0, 0], title="AR(2) - ACF\n（指数減衰 → AR プロセス）")
plot_pacf(ar2_series, lags=20, ax=axes[0, 1], title="AR(2) - PACF\n（2次以降でカットオフ → p=2）")

# MA(2) プロセスの例
ma_coefs = [1, 0.7, 0.4]
ma2_series = arma_generate_sample(ar=[1], ma=ma_coefs, nsample=300, seed=42)

plot_acf(ma2_series,  lags=20, ax=axes[1, 0], title="MA(2) - ACF\n（2次以降でカットオフ → q=2）")
plot_pacf(ma2_series, lags=20, ax=axes[1, 1], title="MA(2) - PACF\n（指数減衰 → MA プロセス）")

plt.tight_layout()
plt.show()

# ARIMAモデルの次数選択ガイド
print("""
次数選択の目安:
  ACF: 急カットオフ → MA(q)、q = カットオフ点
  PACF: 急カットオフ → AR(p)、p = カットオフ点
  両方: 指数減衰 → ARMA(p,q)
  d: 定常化に必要な差分回数（ADF/KPSS で確認）
""")
```

## ARIMA モデル

```python
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")

# 実データ: 月次の電力消費量（シミュレーション）
np.random.seed(123)
n_obs = 120
dates = pd.date_range("2015-01", periods=n_obs, freq="ME")
elec  = (
    500
    + 0.3 * np.arange(n_obs)
    + 80 * np.sin(2 * np.pi * np.arange(n_obs) / 12)
    + np.random.normal(0, 15, n_obs)
)
ts_elec = pd.Series(elec, index=dates)

# 訓練/テスト分割
train = ts_elec[:-12]
test  = ts_elec[-12:]

# ARIMA(p, d, q) フィッティング
model_arima = ARIMA(train, order=(2, 1, 1)).fit()
print(model_arima.summary())

# 予測
forecast = model_arima.forecast(steps=12)
conf_int = model_arima.get_forecast(steps=12).conf_int()

# 精度評価
mae  = np.abs(test.values - forecast.values).mean()
rmse = np.sqrt(((test.values - forecast.values)**2).mean())
mape = (np.abs((test.values - forecast.values) / test.values)).mean() * 100

print(f"\nMAE:  {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"MAPE: {mape:.1f}%")

# 可視化
plt.figure(figsize=(12, 5))
train.plot(label="訓練データ")
test.plot(label="実測値", color="green")
forecast.plot(label="予測値", color="red", linestyle="--")
plt.fill_between(conf_int.index, conf_int.iloc[:, 0], conf_int.iloc[:, 1],
                 alpha=0.2, color="red", label="95% 予測区間")
plt.legend()
plt.title("ARIMA(2,1,1) 電力消費量予測")
plt.tight_layout()
plt.show()
```

## 自動次数選択 (auto_arima)

```python
# pmdarima を使うと AIC 最小化で自動的に最適次数を探索
# pip install pmdarima

from pmdarima import auto_arima

auto_model = auto_arima(
    train,
    seasonal=True, m=12,        # 季節性あり、12ヶ月周期
    d=None,                     # 差分次数を自動判定
    start_p=0, max_p=3,
    start_q=0, max_q=3,
    information_criterion="aic",
    stepwise=True,
    error_action="ignore",
    suppress_warnings=True,
)
print(auto_model.summary())
print(f"選択されたモデル: SARIMA{auto_model.order}x{auto_model.seasonal_order}")
```

## SARIMA（季節性 ARIMA）

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

# SARIMA(p,d,q)(P,D,Q)[s]
# s: 季節周期（月次データなら s=12）
sarima = SARIMAX(
    train,
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 12),
).fit(disp=False)

sarima_forecast = sarima.forecast(steps=12)
sarima_mae  = np.abs(test.values - sarima_forecast.values).mean()
print(f"SARIMA MAE: {sarima_mae:.2f}  (vs ARIMA: {mae:.2f})")
# 季節パターンがある場合、SARIMA の方が精度が高い
```

## 残差診断

```python
# モデルの残差が白色ノイズかどうかを確認
from statsmodels.stats.diagnostic import acorr_ljungbox

residuals = model_arima.resid

# Ljung-Box 検定: H0 = 残差に自己相関なし（白色ノイズ）
lb_result = acorr_ljungbox(residuals, lags=[10, 20], return_df=True)
print(lb_result)
# p > 0.05 なら残差は白色ノイズ → モデル適切

fig, axes = plt.subplots(2, 2, figsize=(10, 8))
pd.Series(residuals).plot(ax=axes[0, 0], title="残差系列")
axes[0, 0].axhline(0, color="red", linestyle="--")

plot_acf(residuals, lags=20, ax=axes[0, 1], title="残差の ACF")
axes[1, 0].hist(residuals, bins=20)
axes[1, 0].set_title("残差のヒストグラム")
from scipy.stats import probplot
probplot(residuals, plot=axes[1, 1])
axes[1, 1].set_title("残差の Q-Q プロット")
plt.tight_layout()
plt.show()
```

## モデル比較

| モデル | 特徴 | 使いどころ |
|---|---|---|
| AR(p) | 過去の自分の値で予測 | 慣性が強いデータ |
| MA(q) | 過去の誤差で予測 | ショック後に収束するデータ |
| ARMA(p,q) | AR + MA の組み合わせ | 定常時系列一般 |
| ARIMA(p,d,q) | 差分で定常化 + ARMA | トレンドあり非定常データ |
| SARIMA | ARIMA + 季節成分 | 月次・四半期など季節性あり |
| Prophet | トレンド + 季節 + 祝日 | ビジネスデータ、欠損値に強い |
| LSTM/Transformer | 深層学習 | 複雑な非線形パターン |
