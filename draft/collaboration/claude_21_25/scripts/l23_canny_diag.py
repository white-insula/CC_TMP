# -*- coding: utf-8 -*-
"""23-P5《Canny 边缘检测》候选：双阈值判定示意图（低 50、高 150）。

上半部分（示意）：手工构造的“变化强度”格子 → 按双阈值分类 → 与强边缘相连的弱边缘保留、孤立弱边缘删除。
  这是简化示意：阈值比较的是边缘变化强度（梯度幅值），不是原图亮度；格子数值为手工构造，
  不是 cv2.Canny 的真实中间输出（真实 Canny 还包括 Sobel 求梯度、非极大值抑制等步骤）。
  连通判定用 8 邻域（与 OpenCV 实现一致）。
下半部分（实测）：程序合成一张灰度图，直接运行 cv2.Canny，对比 (50, 150) / 只用高阈值 (150, 150) / 只用低阈值 (50, 50)。

输出（previews/23/）：23-p5-diag-Canny双阈值判定_候选.png
"""
import cv2
import numpy as np
from _common import *

L = "23"
LOW, HIGH = 50, 150
C_STRONG, C_WEAK, C_NONE = (60, 60, 215), (40, 190, 250), (235, 235, 235)


# ---------------- 示意：手工构造的变化强度 ----------------
def strength_grid():
    g = np.full((8, 13), 15, np.int32)
    g += np.random.default_rng(23).integers(0, 20, g.shape)                  # 背景：弱小变化（<50）
    # 一条边：左段强（>150），右段弱（50–150），连在一起
    g[3, 1:6] = [210, 230, 220, 190, 170]
    g[3, 6:11] = [120, 95, 110, 90, 80]
    g[4, 11] = 75                                                             # 斜向相连（8 邻域）
    # 孤立的弱边缘（噪声或纹理）：没有任何强点相连
    g[6, 2:5] = [70, 100, 85]
    g[0, 9:11] = [60, 90]
    return g


def classify(g):
    strong = g > HIGH
    cand = g > LOW                                           # 强 + 弱
    n, lab = cv2.connectedComponents(cand.astype(np.uint8), connectivity=8)
    keep_labels = set(np.unique(lab[strong]).tolist()) - {0}
    kept = np.isin(lab, list(keep_labels)) & cand
    weak = cand & ~strong
    return strong, weak, kept


def draw_grid(c, g, x0, y0, cs, colors, crosses=None, numbers=True):
    R, C = g.shape
    for r in range(R):
        for q in range(C):
            x, y = x0 + q * cs, y0 + r * cs
            cv2.rectangle(c, (x, y), (x + cs, y + cs), colors[r][q], -1)
            cv2.rectangle(c, (x, y), (x + cs, y + cs), (200, 200, 200), 1)
            if crosses is not None and crosses[r, q]:
                cv2.line(c, (x + 8, y + 8), (x + cs - 8, y + cs - 8), (90, 90, 90), 2, cv2.LINE_AA)
                cv2.line(c, (x + cs - 8, y + 8), (x + 8, y + cs - 8), (90, 90, 90), 2, cv2.LINE_AA)
    if numbers:
        for r in range(R):
            for q in range(C):
                c = text(c, str(int(g[r, q])), (x0 + q * cs + cs // 2, y0 + r * cs + cs // 2), 16,
                         WHITE if colors[r][q] == C_STRONG else INK, anchor="mm")
    return c


def scale_bar(c, x0, y0, w=600, h=34):
    vmax = 260
    xl, xh = x0 + int(LOW / vmax * w), x0 + int(HIGH / vmax * w)
    cv2.rectangle(c, (x0, y0), (xl, y0 + h), C_NONE, -1)
    cv2.rectangle(c, (xl, y0), (xh, y0 + h), C_WEAK, -1)
    cv2.rectangle(c, (xh, y0), (x0 + w, y0 + h), C_STRONG, -1)
    cv2.rectangle(c, (x0, y0), (x0 + w, y0 + h), GRAY, 1)
    c = text(c, "删除", ((x0 + xl) // 2, y0 + h // 2), 18, INK, anchor="mm")
    c = text(c, "候选（弱）：看是否相连", ((xl + xh) // 2, y0 + h // 2), 18, INK, anchor="mm")
    c = text(c, "确定是边缘（强）", ((xh + x0 + w) // 2, y0 + h // 2), 18, WHITE, anchor="mm")
    for v, x in ((LOW, xl), (HIGH, xh)):
        cv2.line(c, (x, y0 - 8), (x, y0 + h + 8), INK, 2)
        c = text(c, f"{'低' if v == LOW else '高'}阈值 {v}", (x, y0 - 22), 18, INK, anchor="mm")
    c = text(c, "变化强度 →", (x0 + w + 12, y0 + h // 2), 18, GRAY, anchor="lm")
    return c


# ---------------- 实测：合成灰度图 + cv2.Canny ----------------
def synth_image():
    H, W = 200, 420
    img = np.full((H, W), 100, np.float32)
    # 下半部分整体更亮：左侧台阶差 60（强），向右逐渐减到 20（弱），用渐变过渡避免出现竖向边缘
    step = np.interp(np.arange(W), [0, 150, 270, W], [60, 60, 20, 20])
    img[110:, :] += step[None, :]
    # 右上一个孤立的淡圆：与背景只差 18（弱），不与任何强边相连
    cv2.circle(img, (330, 50), 26, 118, -1, cv2.LINE_8)
    return np.clip(img, 0, 255).astype(np.uint8)


def canny_check(img):
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)
    mag = np.abs(gx) + np.abs(gy)                         # cv2.Canny 默认 L1 梯度
    line_mag = mag[108:112, :].max(0)
    circ_mag = mag[15:90, 290:370].max()
    print(f"    合成图梯度（L1）：边线左端 {line_mag[20]:.0f}、右端 {line_mag[400]:.0f}；孤立淡圆最大 {circ_mag:.0f}")
    assert line_mag[20] > HIGH and LOW < line_mag[400] < HIGH and LOW < circ_mag < HIGH
    e = cv2.Canny(img, LOW, HIGH)
    e_hi = cv2.Canny(img, HIGH, HIGH)
    e_lo = cv2.Canny(img, LOW, LOW)
    right = lambda m: bool(m[100:120, 360:410].any())
    circle = lambda m: bool(m[15:90, 290:370].any())
    res = {"(50,150) 右段弱边": right(e), "(50,150) 孤立圆": circle(e),
           "(150,150) 右段弱边": right(e_hi), "(50,50) 孤立圆": circle(e_lo)}
    print("    cv2.Canny 实测:", res)
    assert res == {"(50,150) 右段弱边": True, "(50,150) 孤立圆": False,
                   "(150,150) 右段弱边": False, "(50,50) 孤立圆": True}
    return e, e_hi, e_lo


def main():
    W = 1600
    c = canvas(W, 1110)
    c = text(c, "Canny 双阈值：比较的是“变化强度”，不是像素亮度", (40, 46), 32, INK, anchor="lm")
    c = text(c, f"edges = cv2.Canny(gray, {LOW}, {HIGH})", (40, 96), 26, BLUE, anchor="lm")
    c = scale_bar(c, 560, 150)

    # 上半：示意
    g = strength_grid()
    strong, weak, kept = classify(g)
    print(f"    示意格子：强 {int(strong.sum())}、弱 {int(weak.sum())}，其中与强相连保留 {int((weak & kept).sum())}、孤立删除 {int((weak & ~kept).sum())}")
    cs, y0 = 52, 270
    col_a = [[C_STRONG if strong[r, q] else C_WEAK if weak[r, q] else C_NONE for q in range(g.shape[1])] for r in range(g.shape[0])]
    c = text(c, "① 每个位置的变化强度（手工构造的示意数值）", (40, y0 - 30), 22, INK, anchor="lm")
    c = draw_grid(c, g, 40, y0, cs, col_a)
    x1 = 40 + g.shape[1] * cs + 80
    col_b = [[C_STRONG if strong[r, q] else (C_WEAK if (weak[r, q] and kept[r, q]) else C_NONE) for q in range(g.shape[1])] for r in range(g.shape[0])]
    c = text(c, "② 判定结果", (x1, y0 - 30), 22, INK, anchor="lm")
    c = draw_grid(c, g, x1, y0, cs, col_b, crosses=weak & ~kept, numbers=False)
    cv2.arrowedLine(c, (x1 - 66, y0 + 4 * cs), (x1 - 14, y0 + 4 * cs), INK, 3, tipLength=0.3)
    # 标注
    gy0 = y0 + g.shape[0] * cs + 20
    c = text(c, "红：> 150，确定是边缘", (x1, gy0 + 10), 20, C_STRONG, anchor="lm")
    c = text(c, "黄：50～150，与红色连在一起 → 保留", (x1, gy0 + 42), 20, (20, 140, 200), anchor="lm")
    c = text(c, "×：50～150，但孤立 → 删除", (x1, gy0 + 74), 20, (90, 90, 90), anchor="lm")
    c = text(c, "灰：< 50，直接删除", (x1 + 380, gy0 + 10), 20, GRAY, anchor="lm")
    c = text(c, "说明：①② 为简化示意，数值是手工构造的变化强度，不是 cv2.Canny 的真实中间输出；",
             (40, gy0 + 10), 17, GRAY, anchor="lm")
    c = text(c, "真实 Canny 还会先用 Sobel 求梯度、做非极大值抑制，把边细化成单像素线。",
             (40, gy0 + 38), 17, GRAY, anchor="lm")

    # 下半：实测
    img = synth_image()
    e, e_hi, e_lo = canny_check(img)
    yb = gy0 + 130
    cv2.line(c, (40, yb - 30), (W - 40, yb - 30), (220, 220, 220), 2)
    c = text(c, "③ 用合成灰度图实际运行 cv2.Canny 核对（输出反显：黑线 = 边缘；显示时线条加粗 3 像素）", (40, yb), 22, INK, anchor="lm")
    thick = lambda m: 255 - cv2.dilate(m, np.ones((3, 3), np.uint8))      # 仅为显示加粗，不改变判定
    tiles = [
        caption_below(border(img), "合成图：下边界左强右弱；右上淡圆孤立", 18),
        caption_below(border(thick(e)), "Canny(50, 150)：右段弱边保留，淡圆删除", 18, GREEN),
        caption_below(border(thick(e_hi)), "只用高阈值 (150, 150)：右段弱边丢了", 18, RED),
        caption_below(border(thick(e_lo)), "只用低阈值 (50, 50)：孤立淡圆也混进来", 18, RED),
    ]
    tiles = [fit(t, w=360) for t in tiles]
    print('    ③ 各输出边缘像素数：', int((e > 0).sum()), int((e_hi > 0).sum()), int((e_lo > 0).sum()))
    paste(c, row(tiles, gap=26), 40, yb + 26)
    save(stamp(c, "候选 · ①② 手工示意 · ③ 合成图实测 cv2.Canny"), L, "23-p5-diag-Canny双阈值判定_候选.png")


if __name__ == "__main__":
    print("[23] 边缘检测")
    main()
