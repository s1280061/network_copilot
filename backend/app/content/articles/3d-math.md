---
slug: 3d-math
title: 3次元の数学（座標系・変換行列・回転）
level: 3
category: CAD/設計
related: [cad-basics, orthographic-projection]
prereq: [cad-basics]
tags: [cad, math, matrix, 3d, rotation, coordinate]
---

## なぜ3次元数学が必要か

CADソフトが3Dモデルを表示・操作・変換するとき、内部では**行列演算**が絶え間なく走っています。「部品を90°回転させる」「別の座標系に変換する」「カメラ視点を計算する」——これらはすべて行列の積で表現されます。

ロボット工学・コンピュータグラフィックス・自動車シミュレーション・点群処理（LiDAR）でも同じ数学が使われます。

## 座標系の基礎

### 直交座標系（デカルト座標系）

3D空間は **X軸・Y軸・Z軸** の3本の直交する軸で定義されます。

```
右手座標系（CAD・数学で一般的）:
  右手の親指 → X軸（右方向）
  人差し指   → Y軸（上方向）
  中指       → Z軸（手前方向）

左手座標系（DirectXなど一部のゲームエンジン）:
  Z軸が奥方向に向く
```

点 P の位置は \((x, y, z)\) の3つの数値で表されます。

### 同次座標（ホモジニアス座標）

3D変換（平行移動を含む）を**行列の積**だけで統一的に扱うため、\((x, y, z)\) に \(w=1\) を加えた **4次元ベクトル** を使います。

$$\mathbf{p} = \begin{pmatrix} x \\ y \\ z \\ 1 \end{pmatrix}$$

これにより平行移動・回転・スケーリングをすべて \(4\times4\) 行列で表現できます。

## 3つの基本変換

### 1. 平行移動（Translation）

点を \((t_x, t_y, t_z)\) だけ動かす：

$$T = \begin{pmatrix} 1 & 0 & 0 & t_x \\ 0 & 1 & 0 & t_y \\ 0 & 0 & 1 & t_z \\ 0 & 0 & 0 & 1 \end{pmatrix}$$

$$\mathbf{p'} = T \mathbf{p} = \begin{pmatrix} x + t_x \\ y + t_y \\ z + t_z \\ 1 \end{pmatrix}$$

### 2. スケーリング（Scaling）

各軸方向に \(s_x, s_y, s_z\) 倍に拡大・縮小：

$$S = \begin{pmatrix} s_x & 0 & 0 & 0 \\ 0 & s_y & 0 & 0 \\ 0 & 0 & s_z & 0 \\ 0 & 0 & 0 & 1 \end{pmatrix}$$

### 3. 回転（Rotation）

#### X軸周りの回転（角度 \(\theta\)）

$$R_x(\theta) = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & \cos\theta & -\sin\theta & 0 \\ 0 & \sin\theta & \cos\theta & 0 \\ 0 & 0 & 0 & 1 \end{pmatrix}$$

#### Y軸周りの回転

$$R_y(\theta) = \begin{pmatrix} \cos\theta & 0 & \sin\theta & 0 \\ 0 & 1 & 0 & 0 \\ -\sin\theta & 0 & \cos\theta & 0 \\ 0 & 0 & 0 & 1 \end{pmatrix}$$

#### Z軸周りの回転

$$R_z(\theta) = \begin{pmatrix} \cos\theta & -\sin\theta & 0 & 0 \\ \sin\theta & \cos\theta & 0 & 0 \\ 0 & 0 & 1 & 0 \\ 0 & 0 & 0 & 1 \end{pmatrix}$$

## 変換の合成（行列の積）

複数の変換を**行列の積**で合成できます。ただし**順番が大事**（行列の積は非可換）。

「Z軸で45°回転してから \((2, 0, 0)\) 平行移動」：

$$M = T \cdot R_z(45°)$$

```python
import numpy as np

def rotation_z(deg):
    r = np.radians(deg)
    return np.array([
        [np.cos(r), -np.sin(r), 0, 0],
        [np.sin(r),  np.cos(r), 0, 0],
        [0,          0,         1, 0],
        [0,          0,         0, 1],
    ])

def translation(tx, ty, tz):
    return np.array([
        [1, 0, 0, tx],
        [0, 1, 0, ty],
        [0, 0, 1, tz],
        [0, 0, 0,  1],
    ])

# 点 P = (1, 0, 0)
P = np.array([1, 0, 0, 1])

Rz = rotation_z(45)
T  = translation(2, 0, 0)

# 先に回転 → 後に平行移動
M = T @ Rz
P_new = M @ P
print(f"変換後: ({P_new[0]:.3f}, {P_new[1]:.3f}, {P_new[2]:.3f})")
# 変換後: (2.707, 0.707, 0.000)
```

> ⚠️ \(T \cdot R \neq R \cdot T\)。「回転してから移動」と「移動してから回転」では結果が異なります。

## オイラー角

回転を「X, Y, Z 軸周りの3つの角度」で表す方法を **オイラー角** と言います。CADや航空（ピッチ・ロール・ヨー）でよく使われます。

```
ヨー（Yaw）   ψ : Z軸（鉛直）周りの回転 → 左右を向く
ピッチ（Pitch）θ : Y軸周りの回転         → 上下を向く
ロール（Roll） φ : X軸周りの回転         → 傾く
```

$$R = R_z(\psi) \cdot R_y(\theta) \cdot R_x(\phi)$$

> ⚠️ **ジンバルロック問題**：特定の角度の組み合わせで1自由度が失われる現象。アニメーション・ロボットでは**クォータニオン**（四元数）が使われることが多い。

## クォータニオン（四元数）

回転をジンバルロックなく表現する方法。単位クォータニオン \(\mathbf{q} = (w, x, y, z)\)、\(|\mathbf{q}|=1\) で回転を表します。

$$\mathbf{q} = \cos\frac{\theta}{2} + \sin\frac{\theta}{2}(x\mathbf{i} + y\mathbf{j} + z\mathbf{k})$$

回転軸 \(\hat{n} = (n_x, n_y, n_z)\) の周りに角度 \(\theta\) 回転する場合：

$$w = \cos\frac{\theta}{2}, \quad (x,y,z) = \sin\frac{\theta}{2}(n_x, n_y, n_z)$$

```python
import numpy as np

def quaternion_from_axis_angle(axis, angle_deg):
    """軸ベクトルと角度からクォータニオンを生成"""
    axis = np.array(axis, dtype=float)
    axis /= np.linalg.norm(axis)  # 単位ベクトル化
    r = np.radians(angle_deg) / 2
    return np.array([np.cos(r), *(np.sin(r) * axis)])

def quaternion_to_matrix(q):
    """クォータニオン → 3×3回転行列"""
    w, x, y, z = q
    return np.array([
        [1-2*(y*y+z*z),   2*(x*y-w*z),   2*(x*z+w*y)],
        [  2*(x*y+w*z), 1-2*(x*x+z*z),   2*(y*z-w*x)],
        [  2*(x*z-w*y),   2*(y*z+w*x), 1-2*(x*x+y*y)],
    ])

# Z軸周りに45°回転
q = quaternion_from_axis_angle([0, 0, 1], 45)
R = quaternion_to_matrix(q)
print("回転行列:\n", np.round(R, 3))
```

## 点群への応用（LiDAR・3Dスキャン）

自動車のLiDARや3Dスキャナは大量の点群データを出力します。センサーの取り付け位置・姿勢に合わせて変換行列を適用することで、車両座標系に統合できます。

```python
import numpy as np

def transform_pointcloud(points, R, t):
    """
    points: (N, 3) の点群
    R: 3x3 回転行列
    t: (3,) 平行移動ベクトル
    """
    return (R @ points.T).T + t

# センサーが車両後方2m・高さ1.5mに取り付け
R_sensor = rotation_z(180)[:3, :3]   # 180°回転（後ろ向き）
t_sensor  = np.array([-2.0, 0.0, 1.5])

# ダミー点群
points = np.array([
    [1.0, 0.0, 0.0],
    [2.0, 1.0, 0.0],
    [3.0, 0.0, 0.5],
])

transformed = transform_pointcloud(points, R_sensor, t_sensor)
print("変換後の点群:\n", np.round(transformed, 3))
```

## 投影変換（3D→2D）

3D空間の点を2Dスクリーンに映す変換です。CADのビューポートや正投影図でも使われます。

### 平行投影（正投影）

$$\begin{pmatrix} u \\ v \end{pmatrix} = \begin{pmatrix} x \\ y \end{pmatrix}$$

（Z成分を捨てるだけ。CAD図面の正面図・側面図がこれ）

### 透視投影

$$u = \frac{f \cdot x}{z}, \quad v = \frac{f \cdot y}{z}$$

焦点距離 \(f\)、物体が遠いほど小さく見える（遠近法）。

## まとめ

| 概念 | 表現 | 用途 |
|------|------|------|
| 平行移動 | \(4\times4\) 行列 | 位置変更 |
| 回転（軸別） | \(4\times4\) 行列 | 向き変更 |
| スケーリング | \(4\times4\) 行列 | 拡大縮小 |
| オイラー角 | 3つの角度 | 直感的な回転表現 |
| クォータニオン | \((w,x,y,z)\) | ジンバルロック回避 |
| 変換合成 | 行列の積 \(M_2 \cdot M_1\) | 複数変換の合成 |
| 正投影 | Z成分を捨てる | CAD投影図 |

次は「**正投影図・第一角法・第三角法**」でCAD図面の読み書きを学びます。
