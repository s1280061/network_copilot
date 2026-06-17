"""
Generate the third-angle projection illustration.
Output: frontend/public/images/charts/third-angle-projection.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import os

OUT_DIR = "/home/user/network_copilot/frontend/public/images/charts"
os.makedirs(OUT_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 140, "font.size": 11,
    "font.family": "IPAGothic", "axes.unicode_minus": False,
})

BLUE = "#4C72B0"
ORANGE = "#DD8452"
GREEN = "#55A868"
GRAY = "#888888"

# L字形（段付き）ブロックを定義：第三角法の説明によく使う形
# 直方体ベース(4x3x1) + 上に小さい直方体(2x1x1) を左奥に乗せた形
def block_faces():
    # base box: x:[0,4], y:[0,3], z:[0,1]
    base = dict(x=(0, 4), y=(0, 3), z=(0, 1))
    # top box: x:[0,2], y:[0,1], z:[1,2]
    top = dict(x=(0, 2), y=(0, 1), z=(1, 2))
    return base, top


def box_faces(x, y, z):
    x0, x1 = x
    y0, y1 = y
    z0, z1 = z
    v = {
        "000": (x0, y0, z0), "100": (x1, y0, z0), "110": (x1, y1, z0), "010": (x0, y1, z0),
        "001": (x0, y0, z1), "101": (x1, y0, z1), "111": (x1, y1, z1), "011": (x0, y1, z1),
    }
    faces = [
        [v["000"], v["100"], v["110"], v["010"]],  # bottom
        [v["001"], v["101"], v["111"], v["011"]],  # top
        [v["000"], v["100"], v["101"], v["001"]],  # front (y0)
        [v["010"], v["110"], v["111"], v["011"]],  # back (y1)
        [v["000"], v["010"], v["011"], v["001"]],  # left (x0)
        [v["100"], v["110"], v["111"], v["101"]],  # right (x1)
    ]
    return faces


def chart_third_angle_projection():
    base, top = block_faces()

    fig = plt.figure(figsize=(11, 9))

    # 1) 3D view of the L-shaped block
    ax3d = fig.add_subplot(2, 2, 1, projection="3d")
    for b, color in [(base, BLUE), (top, ORANGE)]:
        faces = box_faces((b["x"][0], b["x"][1]), (b["y"][0], b["y"][1]), (b["z"][0], b["z"][1]))
        poly = Poly3DCollection(faces, facecolor=color, edgecolor="k", linewidths=0.8, alpha=0.85)
        ax3d.add_collection3d(poly)
    ax3d.set_xlim(0, 4); ax3d.set_ylim(0, 4); ax3d.set_zlim(0, 3)
    ax3d.set_xlabel("X (幅)"); ax3d.set_ylabel("Y (奥行き)"); ax3d.set_zlabel("Z (高さ)")
    ax3d.set_title("① 立体（L字形ブロック）", fontsize=12)
    ax3d.view_init(elev=22, azim=-60)

    # 2) front view (正面図): looking along -Y axis -> X-Z plane
    ax = fig.add_subplot(2, 2, 2)
    ax.add_patch(plt.Rectangle((0, 0), 4, 1, facecolor=BLUE, edgecolor="k"))
    ax.add_patch(plt.Rectangle((0, 1), 2, 1, facecolor=ORANGE, edgecolor="k"))
    ax.set_xlim(-0.5, 4.5); ax.set_ylim(-0.5, 2.5)
    ax.set_aspect("equal")
    ax.set_title("② 正面図（Front View）\n物体を正面（−Y方向）から見た図", fontsize=11)
    ax.set_xlabel("X (幅)"); ax.set_ylabel("Z (高さ)")

    # 3) top view (平面図): looking along -Z axis -> X-Y plane, placed above front view
    ax = fig.add_subplot(2, 2, 3)
    ax.add_patch(plt.Rectangle((0, 0), 4, 3, facecolor=BLUE, edgecolor="k", alpha=0.6))
    ax.add_patch(plt.Rectangle((0, 0), 2, 1, facecolor=ORANGE, edgecolor="k"))
    ax.set_xlim(-0.5, 4.5); ax.set_ylim(-0.5, 3.5)
    ax.set_aspect("equal")
    ax.set_title("③ 平面図（Top View）\n物体を上（+Z方向）から見た図", fontsize=11)
    ax.set_xlabel("X (幅)"); ax.set_ylabel("Y (奥行き)")
    ax.invert_yaxis()

    # 4) right side view (右側面図): looking along -X axis -> Y-Z plane
    ax = fig.add_subplot(2, 2, 4)
    ax.add_patch(plt.Rectangle((0, 0), 3, 1, facecolor=BLUE, edgecolor="k"))
    ax.add_patch(plt.Rectangle((0, 1), 1, 1, facecolor=ORANGE, edgecolor="k"))
    ax.set_xlim(-0.5, 3.5); ax.set_ylim(-0.5, 2.5)
    ax.set_aspect("equal")
    ax.set_title("④ 右側面図（Right Side View）\n物体を右側（+X方向）から見た図", fontsize=11)
    ax.set_xlabel("Y (奥行き)"); ax.set_ylabel("Z (高さ)")

    fig.suptitle("第三角投影法：立体と三面図の対応", fontsize=14, y=0.995)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/third-angle-projection.png", bbox_inches="tight")
    plt.close(fig)


def chart_third_angle_layout():
    """第三角法のガラス箱モデル（投影面の配置）を示す図。"""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(-1, 9)
    ax.set_ylim(-1, 9)
    ax.set_aspect("equal")
    ax.axis("off")

    # 配置: 正面図中央、平面図は正面図の上、右側面図は正面図の右
    def draw_box(x0, y0, w, h, label, color):
        ax.add_patch(plt.Rectangle((x0, y0), w, h, facecolor=color, edgecolor="k", alpha=0.5, linewidth=1.5))
        ax.text(x0 + w / 2, y0 + h / 2, label, ha="center", va="center", fontsize=12, fontweight="bold")

    draw_box(2, 2, 4, 3, "正面図\n(Front View)", BLUE)
    draw_box(2, 5.3, 4, 2.2, "平面図\n(Top View)\n※正面図の上に配置", GREEN)
    draw_box(6.3, 2, 2.2, 3, "右側面図\n(Right Side View)\n※正面図の右に配置", ORANGE)

    # guide lines
    ax.plot([2, 8.5], [2, 2], color=GRAY, lw=0.8, ls="--")
    ax.plot([2, 2], [2, 7.5], color=GRAY, lw=0.8, ls="--")
    ax.plot([6.3, 6.3], [2, 7.5], color=GRAY, lw=0.8, ls="--")

    ax.set_title("第三角投影法の配置ルール\n（正面図を中心に、上＝平面図、右＝右側面図）", fontsize=12)
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/third-angle-layout.png", bbox_inches="tight")
    plt.close(fig)


chart_third_angle_projection()
chart_third_angle_layout()
print("done: third-angle-projection.png, third-angle-layout.png")
