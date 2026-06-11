---
slug: time-series-analysis
title: 時系列分析（ARIMA・予測・異常検知）
level: 3
category: Python
related: [statistics, pandas, numpy, anomaly-detection]
next: []
tags: [time-series, python, statsmodels, arima, forecasting]
---

## 概要
時系列分析は時間順に並んだデータのパターンを発見・予測する手法です。車載ネットワークのトラフィック量の変化、ECU温度のトレンド、センサーデータの周期性など、ネットワーク診断・予兆保全に不可欠です。PythonではStatsmodels・Prophet・scikit-learnが主要ツールです。

```mermaid
graph LR
  TS["時系列データ"] --> DC["トレンド/季節/残差<br/>に分解"]
  DC --> MO["ARIMA等で<br/>モデル化"]
  MO --> FC["将来を予測"]
```

## 時系列データの構造

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

np.random.seed(42)

# 車載CANバスのトラフィック量（1時間ごと、30日間）
dates = pd.date_range("2024-01-01", periods=720, freq="h")
trend     = np.linspace(100, 150, 720)                    # 上昇トレンド
seasonal  = 20 * np.sin(2 * np.pi * np.arange(720) / 24) # 日次周期
noise     = np.random.normal(0, 5, 720)
traffic   = trend + seasonal + noise

ts = pd.Series(traffic, index=dates, name="CAN traffic (msg/s)")

fig, axes = plt.subplots(3, 1, figsize=(12, 8))
ts.plot(ax=axes[0], title="元の時系列")
ts.rolling(24).mean().plot(ax=axes[1], title="移動平均（24h）")
ts.diff(24).plot(ax=axes[2], title="季節差分（24h）")
plt.tight_layout()
plt.show()
```

## 時系列の分解

```python
from statsmodels.tsa.seasonal import seasonal_decompose

result = seasonal_decompose(ts, model="additive", period=24)

fig, axes = plt.subplots(4, 1, figsize=(12, 10))
result.observed.plot(ax=axes[0],  title="元データ")
result.trend.plot(ax=axes[1],     title="トレンド")
result.seasonal.plot(ax=axes[2],  title="季節性")
result.resid.plot(ax=axes[3],     title="残差")
plt.tight_layout()
plt.show()

print(f"季節成分の振幅: {result.seasonal.max() - result.seasonal.min():.2f}")
print(f"残差の標準偏差: {result.resid.dropna().std():.2f}")
```

## 定常性の検定（ADF検定）

```python
from statsmodels.tsa.stattools import adfuller, kpss

def check_stationarity(series, name=""):
    adf_stat, adf_p, _, _, crit, _ = adfuller(series.dropna())
    print(f"=== {name} ===")
    print(f"ADF統計量: {adf_stat:.4f}  p値: {adf_p:.4f}")
    print(f"臨界値(5%): {crit['5%']:.4f}")
    print("→ 定常" if adf_p < 0.05 else "→ 非定常（差分が必要）")

check_stationarity(ts, "元データ")
check_stationarity(ts.diff(1).dropna(), "1階差分")
check_stationarity(ts.diff(24).dropna(), "24h季節差分")
```

## ARIMAモデル

```python
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

# ACF/PACFでパラメータのヒントを得る
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
plot_acf(ts.diff(1).dropna(), lags=48, ax=axes[0])
plot_pacf(ts.diff(1).dropna(), lags=48, ax=axes[1])
plt.tight_layout()
plt.show()

# 学習データ: 最初の700点、テスト: 残り20点
train, test = ts[:700], ts[700:]

model  = ARIMA(train, order=(2, 1, 2))
result = model.fit()
print(result.summary())

# 予測
forecast = result.forecast(steps=20)
mae = np.abs(forecast.values - test.values).mean()
print(f"\nMAE: {mae:.2f}")

plt.figure(figsize=(12, 4))
train[-100:].plot(label="学習データ")
test.plot(label="実データ", color="green")
forecast.plot(label="予測", color="red", linestyle="--")
plt.legend()
plt.title("ARIMAによる予測")
plt.show()
```

## SARIMAXモデル（季節性あり）

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX

# SARIMA(p,d,q)(P,D,Q,s)
# s=24 → 24時間周期の季節性
model_sarima = SARIMAX(
    train,
    order=(1, 1, 1),
    seasonal_order=(1, 1, 1, 24),
    enforce_stationarity=False,
    enforce_invertibility=False,
)
result_sarima = model_sarima.fit(disp=False)
forecast_sarima = result_sarima.forecast(steps=20)

mae_sarima = np.abs(forecast_sarima.values - test.values).mean()
print(f"SARIMA MAE: {mae_sarima:.2f}  (ARIMA MAE: {mae:.2f})")
```

## Prophetによる予測

```python
# pip install prophet
from prophet import Prophet

df = ts.reset_index()
df.columns = ["ds", "y"]

m = Prophet(
    yearly_seasonality=False,
    weekly_seasonality=False,
    daily_seasonality=True,
    changepoint_prior_scale=0.05,
)
m.fit(df[:700])

future   = m.make_future_dataframe(periods=20, freq="h")
forecast = m.predict(future)

fig = m.plot(forecast)
fig2 = m.plot_components(forecast)
plt.show()

mae_prophet = np.abs(
    forecast["yhat"].iloc[700:].values - ts[700:].values
).mean()
print(f"Prophet MAE: {mae_prophet:.2f}")
```

## 時系列クロスバリデーション

```python
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import Ridge

# 特徴量エンジニアリング
def make_features(series, lags=24):
    df = pd.DataFrame({"y": series})
    for lag in range(1, lags + 1):
        df[f"lag_{lag}"] = df["y"].shift(lag)
    df["hour"]    = series.index.hour
    df["dayofweek"] = series.index.dayofweek
    return df.dropna()

feat_df = make_features(ts)
X = feat_df.drop("y", axis=1)
y = feat_df["y"]

tscv = TimeSeriesSplit(n_splits=5)
scores = []
for train_idx, test_idx in tscv.split(X):
    model = Ridge()
    model.fit(X.iloc[train_idx], y.iloc[train_idx])
    pred  = model.predict(X.iloc[test_idx])
    mae   = np.abs(pred - y.iloc[test_idx].values).mean()
    scores.append(mae)

print(f"時系列CV MAE: {np.mean(scores):.2f} ± {np.std(scores):.2f}")
```

## 次に学ぶべき内容
時系列データの異常検知は [[anomaly-detection]] で学びましょう。
