---
slug: rnn-lstm
title: RNN・LSTM（系列データのモデリング）
level: 3
category: DL
related: [deep-learning, pytorch, transformer]
next: [transformer]
tags: [rnn, lstm, deep-learning, pytorch, time-series, nlp]
---

## 概要
「昨日の気温と一週間の傾向から今日の気温を予測したい」――過去の情報を記憶しながら系列を処理するのがRNN・LSTMです。前のタイムステップの出力を次のステップに引き継ぐことで「文脈」を保持しますが、長い系列ではRNNが勾配消失を起こす問題がありました。LSTMは「忘却・入力・出力」の3つのゲートで記憶を制御し、長期依存を学習できるように改良された版です。現在はTransformerに置き換えられつつありますが、軽量なエッジデバイスや時系列回帰では今もLSTMが実用的です。

## 活用シーン
- **時系列予測**: センサー値・株価・エネルギー消費量の次ステップ予測
- **テキスト分類**: 短いシーケンスの感情分析や意図分類（Transformerより軽量）
- **異常検知**: 通常パターンを学習したLSTMが「予測と大きく外れた＝異常」として検出

## 主要な数式

**RNN の隠れ状態更新**：

$$\mathbf{h}_t = \tanh\!\left(\mathbf{W}_{hh}\mathbf{h}_{t-1} + \mathbf{W}_{xh}\mathbf{x}_t + \mathbf{b}_h\right)$$

**LSTM のゲート**（忘却・入力・出力）：

$$\mathbf{f}_t = \sigma(\mathbf{W}_f[\mathbf{h}_{t-1}, \mathbf{x}_t] + \mathbf{b}_f), \quad \mathbf{i}_t = \sigma(\mathbf{W}_i[\cdot] + \mathbf{b}_i), \quad \mathbf{o}_t = \sigma(\mathbf{W}_o[\cdot] + \mathbf{b}_o)$$

**セル状態と隠れ状態の更新**：

$$\mathbf{c}_t = \mathbf{f}_t \odot \mathbf{c}_{t-1} + \mathbf{i}_t \odot \tilde{\mathbf{c}}_t, \qquad \mathbf{h}_t = \mathbf{o}_t \odot \tanh(\mathbf{c}_t)$$

忘却ゲート \(\mathbf{f}_t\) が過去の情報をどれだけ残すかを制御し、勾配消失を緩和する。

## 可視化

![ルックバックウィンドウと1ステップ予測](/images/charts/rnn-lstm.png)

## RNN vs LSTM vs GRU

```mermaid
graph TD
  A[系列データ] --> B{長期依存が必要?}
  B -->|No・短い系列| C[SimpleRNN]
  B -->|Yes| D{パラメータ節約?}
  D -->|No| E[LSTM<br/>入力・忘却・出力ゲート]
  D -->|Yes| F[GRU<br/>リセット・更新ゲート]
```

## LSTM の仕組み（直感的理解）

LSTMは3つのゲートで「何を覚え・何を忘れ・何を出力するか」を制御します：

| ゲート | 役割 |
|---|---|
| 忘却ゲート | 過去の記憶をどれだけ捨てるか |
| 入力ゲート | 新しい情報をどれだけ追加するか |
| 出力ゲート | セル状態からどれだけ出力するか |

## PyTorchで時系列予測

```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# サインカーブにノイズを加えた時系列データ
t     = np.linspace(0, 8 * np.pi, 1000)
data  = np.sin(t) + 0.1 * np.random.randn(len(t))

# スライディングウィンドウでサンプル作成
def make_sequences(data, seq_len=50):
    X, y = [], []
    for i in range(len(data) - seq_len):
        X.append(data[i : i + seq_len])
        y.append(data[i + seq_len])
    return (torch.tensor(np.array(X), dtype=torch.float32).unsqueeze(-1),
            torch.tensor(np.array(y), dtype=torch.float32))

X, y  = make_sequences(data)
split = int(len(X) * 0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

class LSTMForecaster(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=dropout
        )
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :]).squeeze(-1)  # 最終タイムステップだけ使う

model     = LSTMForecaster()
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

from torch.utils.data import TensorDataset, DataLoader
loader = DataLoader(TensorDataset(X_train, y_train), batch_size=64, shuffle=True)

for epoch in range(50):
    model.train()
    for Xb, yb in loader:
        optimizer.zero_grad()
        loss = criterion(model(Xb), yb)
        loss.backward()
        optimizer.step()
    if (epoch + 1) % 10 == 0:
        model.eval()
        with torch.no_grad():
            val_loss = criterion(model(X_test), y_test).item()
        print(f"Epoch {epoch+1}: val_loss={val_loss:.4f}")
```

**数式で表すと**

LSTM が各タイムステップで隠れ状態を更新し、最終ステップ \(\mathbf{h}_T\) を線形層に通して1ステップ先を予測します：

$$
\mathbf{c}_t = \mathbf{f}_t \odot \mathbf{c}_{t-1} + \mathbf{i}_t \odot \tilde{\mathbf{c}}_t, \quad \mathbf{h}_t = \mathbf{o}_t \odot \tanh(\mathbf{c}_t), \quad \hat{y} = \mathbf{w}^\top \mathbf{h}_T + b
$$

損失は平均二乗誤差 \(\mathcal{L} = \frac{1}{N}\sum_n (\hat{y}_n - y_n)^2\) を用います。

## テキスト分類への応用

```python
import torch.nn as nn

class TextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_size, n_classes):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm  = nn.LSTM(embed_dim, hidden_size, batch_first=True,
                             bidirectional=True, num_layers=2, dropout=0.3)
        self.fc    = nn.Linear(hidden_size * 2, n_classes)  # bidirectional×2
        self.drop  = nn.Dropout(0.4)

    def forward(self, x):
        emb  = self.drop(self.embed(x))           # (B, T, embed_dim)
        out, (hn, _) = self.lstm(emb)
        # 順方向と逆方向の最終隠れ状態を結合
        hn   = torch.cat([hn[-2], hn[-1]], dim=-1)  # (B, hidden*2)
        return self.fc(self.drop(hn))

model = TextClassifier(vocab_size=10000, embed_dim=128,
                       hidden_size=256, n_classes=2)
x = torch.randint(0, 10000, (32, 100))   # バッチ32・長さ100
print(model(x).shape)                    # (32, 2)
```

**数式で表すと**

双方向LSTMは系列を順・逆両方向に処理し、それぞれの最終隠れ状態を結合して分類します：

$$
\mathbf{h} = \left[\overrightarrow{\mathbf{h}}_T;\, \overleftarrow{\mathbf{h}}_1\right], \qquad \mathbf{y} = W\mathbf{h} + \mathbf{b}
$$

結合により隠れ次元が2倍になるため、線形層の入力は \(\text{hidden}\times 2\) になります。

## 予測結果の可視化

```python
model.eval()
with torch.no_grad():
    preds = model(X_test).numpy()

actual = y_test.numpy()
time   = np.arange(len(actual))

plt.figure(figsize=(12, 4))
plt.plot(time, actual, label="実測値", alpha=0.8)
plt.plot(time, preds,  label="予測値", alpha=0.8, linestyle="--")
plt.title("LSTMによる時系列予測")
plt.legend()
plt.tight_layout()
plt.show()
```

## よくある間違いと対処法

1. **`batch_first=True` を忘れる** → PyTorchのLSTMはデフォルトで `(seq_len, batch, input_size)` の順序。`batch_first=True` を設定すると `(batch, seq_len, input_size)` になり直感的に使いやすい。
2. **勾配クリッピングを忘れる** → RNN/LSTMは勾配爆発が起きやすい。`torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)` をoptimizerの前に追加する。
3. **スケーリングなしで時系列を学習する** → LSTMは入力のスケールに敏感。`MinMaxScaler` または `StandardScaler` で前処理し、予測値を逆変換して評価する。
4. **`out[:, -1, :]` と `(hn, cn)[-1]` の混同** → 1ステップ先の予測には最終タイムステップの出力 `out[:, -1, :]` を使う。`hn` はすべての層の最終状態なので双方向LSTMでは注意が必要。

## まとめ

- RNN: シンプルだが長い系列で勾配消失。短い系列や軽量モデルに使用
- LSTM: 3つのゲートで記憶を制御・長期依存を学習できる
- GRU: LSTMよりパラメータ少なく高速・精度は同等かやや低い
- `batch_first=True` + `clip_grad_norm_` + スケーリングが実装の3原則
- 長い系列・大規模データでは Transformer への移行を検討する

## 次に学ぶべき内容
系列モデルの現在の主流となった [[transformer]] を学びましょう。
