# -*- coding: utf-8 -*-
"""23-P5《Canny 边缘检测》候选：双阈值判定（低 50、高 150）。

判定边界（与 OpenCV 4.11.0 canny.cpp 中 m > low、m > high 的写法一致，并已用梯度重载实测）：
  变化强度 ≤ 50         → 删除（不进入候选）
  50 < 变化强度 ≤ 150   → 弱候选：只有经弱边缘链与强边缘相连才保留
  变化强度 > 150        → 强边缘，保留
阈值比较的是边缘变化强度（梯度幅值），不是原图亮度。示意格子的数值为手工构造，
不是 cv2.Canny 的真实中间输出（真实 Canny 还包括 Sobel 求梯度、非极大值抑制等步骤）；连通判定用 8 邻域。

输出（previews/23/）：
  23-p5-diag-Canny双阈值判定_课堂版_候选.png       16:9 单页课堂版，只讲强 / 相连弱 / 孤立弱三种情况，大字
  23-p5-diag-Canny双阈值判定_详细审阅版_候选.png   完整数值网格、图例、说明与合成图实测（供审阅，不建议直接上课件）
  23-p5-ref-Canny实测对照与边界核对_附件.png       独立核对附件：合成图四张实测 + 49/50/51、149/150/151 边界实测
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
    g += np.random.default_rng(23).integers(0, 20, g.shape)                  # 背景：弱小变化（≤ 50）
    # 一条边：左段强（> 150），右段弱（50 < 强度 ≤ 150），连在一起
    g[3, 1:6] = [210, 230, 220, 190, 170]
    g[3, 6:11] = [120, 95, 110, 90, 80]
    g[4, 11] = 75                                                             # 斜向相连（8 邻域）
    # 孤立的弱边缘（噪声或纹理）：没有任何强点相连
    g[6, 2:5] = [70, 100, 85]
    g[0, 9:11] = [60, 90]
    return g


def classify(g):
    strong = g > HIGH                                        # > 150：强
    cand = g > LOW                                           # > 50：强 + 弱；≤ 50 直接删除
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


def scale_bar(c, x0, y0, w=760, h=34):
    vmax = 260
    xl, xh = x0 + int(LOW / vmax * w), x0 + int(HIGH / vmax * w)
    cv2.rectangle(c, (x0, y0), (xl, y0 + h), C_NONE, -1)
    cv2.rectangle(c, (xl, y0), (xh, y0 + h), C_WEAK, -1)
    cv2.rectangle(c, (xh, y0), (x0 + w, y0 + h), C_STRONG, -1)
    cv2.rectangle(c, (x0, y0), (x0 + w, y0 + h), GRAY, 1)
    c = text(c, "≤50 删除", ((x0 + xl) // 2, y0 + h // 2), 18, INK, anchor="mm")
    c = text(c, "50<强度≤150 弱候选：看是否相连", ((xl + xh) // 2, y0 + h // 2), 17, INK, anchor="mm")
    c = text(c, ">150 强边缘", ((xh + x0 + w) // 2, y0 + h // 2), 18, WHITE, anchor="mm")
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
    c = scale_bar(c, 520, 150)

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
    c = text(c, "红：强度 > 150，强边缘 → 保留", (x1, gy0 + 10), 20, C_STRONG, anchor="lm")
    c = text(c, "黄：50 < 强度 ≤ 150，经弱边缘链连到红色 → 保留", (x1, gy0 + 42), 20, (20, 140, 200), anchor="lm")
    c = text(c, "×：50 < 强度 ≤ 150，但孤立 → 删除", (x1, gy0 + 74), 20, (90, 90, 90), anchor="lm")
    c = text(c, "灰：强度 ≤ 50，直接删除", (x1 + 360, gy0 + 74), 20, GRAY, anchor="lm")
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
    c = title_bar(c, "【详细审阅版】供核对，不建议直接放入课件；课堂请用课堂版", 22)
    save(stamp(c, "候选 · 详细审阅版 · ①② 手工示意 · ③ 合成图实测 cv2.Canny"), L, "23-p5-diag-Canny双阈值判定_详细审阅版_候选.png")
    return img, e, e_hi, e_lo


# ---------------- 课堂版：16:9，大字，只讲三种情况 ----------------
def classroom_grid():
    """3 行 × 11 列的小网格：强 2 格 → 弱链 3 格（相连）；隔开的孤立弱 2 格；含一个恰好等于 50 的格子。"""
    g = np.array([
        [20, 25, 30, 20, 25, 20, 30, 20, 25, 20, 20],
        [20, 210, 180, 120, 90, 70, 30, 20, 95, 60, 20],
        [25, 20, 30, 25, 20, 50, 25, 20, 30, 25, 20],
    ], np.int32)
    return g


def classroom():
    g = classroom_grid()
    strong, weak, kept = classify(g)
    exp_strong = {(1, 1), (1, 2)}; exp_chain = {(1, 3), (1, 4), (1, 5)}; exp_iso = {(1, 8), (1, 9)}
    on = lambda m: {(int(r), int(q)) for r, q in zip(*np.nonzero(m))}
    assert on(strong) == exp_strong and on(weak & kept) == exp_chain and on(weak & ~kept) == exp_iso
    assert g[2, 5] == 50 and not (weak | strong)[2, 5]
    print("    课堂版网格：强", sorted(exp_strong), "相连弱", sorted(exp_chain), "孤立弱", sorted(exp_iso), "；等于 50 的格子不进入候选")

    c = canvas(1280, 690)                     # 加 30 像素底部候选条后正好 1280×720
    c = text(c, "Canny 双阈值：看“变化强度”，连到强边的弱边才保留", (40, 44), 34, INK, anchor="lm")
    # 规则条
    y = 92
    rules = [("强度 ≤ 50：删除", C_NONE, INK), ("50 < 强度 ≤ 150：弱，连到强边才保留", C_WEAK, INK), ("强度 > 150：强边缘，保留", C_STRONG, WHITE)]
    widths = [290, 560, 350]
    x = 40
    for (s_, colr, tc), w in zip(rules, widths):
        cv2.rectangle(c, (x, y), (x + w, y + 54), colr, -1)
        c = text(c, s_, (x + w // 2, y + 27), 26, tc, anchor="mm")
        x += w + 0
    c = text(c, "cv2.Canny(gray, 50, 150)", (40, y + 84), 24, BLUE, anchor="lm")
    # 网格
    cs = 100
    R, C = g.shape
    x0, y0 = (1280 - C * cs) // 2, 222
    for r in range(R):
        for q in range(C):
            xx, yy = x0 + q * cs, y0 + r * cs
            if strong[r, q]:
                colr = C_STRONG
            elif weak[r, q]:
                colr = C_WEAK
            else:
                colr = C_NONE
            cv2.rectangle(c, (xx, yy), (xx + cs, yy + cs), colr, -1)
            cv2.rectangle(c, (xx, yy), (xx + cs, yy + cs), (205, 205, 205), 2)
            if weak[r, q] and not kept[r, q]:
                cv2.line(c, (xx + 14, yy + 14), (xx + cs - 14, yy + cs - 14), (70, 70, 70), 4, cv2.LINE_AA)
                cv2.line(c, (xx + cs - 14, yy + 14), (xx + 14, yy + cs - 14), (70, 70, 70), 4, cv2.LINE_AA)
            big = strong[r, q] or weak[r, q] or g[r, q] == 50
            c = text(c, str(int(g[r, q])), (xx + cs // 2, yy + cs // 2), 34 if big else 24,
                     WHITE if strong[r, q] else (INK if big else (150, 150, 150)), anchor="mm")
    # 链条示意：强 → 弱 → 弱 → 弱
    # 分组说明（网格下方）
    yb = y0 + R * cs + 22

    def bracket(q0, q1, label, colr):
        xa, xb = x0 + q0 * cs + 6, x0 + (q1 + 1) * cs - 6
        cv2.line(c, (xa, yb), (xb, yb), colr, 4); cv2.line(c, (xa, yb), (xa, yb - 14), colr, 4); cv2.line(c, (xb, yb), (xb, yb - 14), colr, 4)
        return text(c, label, ((xa + xb) // 2, yb + 34), 26, colr, anchor="mm")
    c = bracket(1, 2, "强边缘：保留", C_STRONG)
    c = bracket(3, 5, "弱，连成链到强边：保留", (20, 130, 200))
    c = bracket(8, 9, "弱，但孤立：删除", (70, 70, 70))
    c = text(c, "50 不大于低阈值：不进入候选", (x0 + 5 * cs + cs // 2, yb + 74), 22, GRAY, anchor="mm")
    c = text(c, "简化示意：格中数字是手工构造的变化强度，不是 cv2.Canny 的真实中间输出", (640, 664), 20, GRAY, anchor="mm")
    out = stamp(c, "候选 · 课堂版 · 简化示意")
    assert out.shape[:2] == (720, 1280)
    save(out, L, "23-p5-diag-Canny双阈值判定_课堂版_候选.png")


# ---------------- 独立核对附件 ----------------
def boundary_check():
    """用 cv2.Canny(dx, dy, 50, 150) 梯度重载直接给定变化强度，核对等号边界。
    每列单独一组（列间留空，互不连通）；同一组内为同一列相邻行，横向梯度，均通过非极大值抑制。"""
    groups = [("一条链：151 150 51 50 49", [151, 150, 51, 50, 49]),
              ("孤立 150", [150]), ("孤立 151", [151]), ("孤立 51", [51]), ("149 紧挨 151", [149, 151])]
    H = 9; Wd = len(groups) * 4 + 3
    dx = np.zeros((H, Wd), np.int16); dy = np.zeros_like(dx)
    for k, (_, vals) in enumerate(groups):
        for i, v in enumerate(vals):
            dx[2 + i, 2 + k * 4] = v
    e = cv2.Canny(dx, dy, LOW, HIGH, L2gradient=False)
    res = [(name, vals, [int(e[2 + i, 2 + k * 4]) for i in range(len(vals))]) for k, (name, vals) in enumerate(groups)]
    exp = [[255, 255, 255, 0, 0], [0], [255], [0], [255, 255]]
    assert [r[2] for r in res] == exp, res
    for name, vals, out in res:
        print(f"    边界实测 {name}: {vals} → {out}")
    return res


def attachment(img, e, e_hi, e_lo):
    res = boundary_check()
    c = canvas(1600, 1240)
    c = text(c, "23-P5 核对附件：cv2.Canny 实测（OpenCV 4.11.0）", (40, 44), 32, INK, anchor="lm")
    c = text(c, "① 合成灰度图实测：输出反显，黑线 = 边缘；仅为显示把线条加粗 3 像素，不改变判定", (40, 100), 22, INK, anchor="lm")
    thick = lambda m: 255 - cv2.dilate(m, np.ones((3, 3), np.uint8))
    big = lambda m: border(cv2.resize(bgr(m), None, fx=1.6, fy=1.6, interpolation=cv2.INTER_NEAREST))
    tiles = [
        caption_below(big(img), "合成图：下边界左强右弱，右上淡圆孤立", 22),
        caption_below(big(thick(e)), "Canny(50, 150)：右段弱边保留，淡圆删除", 22, GREEN),
        caption_below(big(thick(e_hi)), "只用高阈值 (150, 150)：右段弱边丢了", 22, RED),
        caption_below(big(thick(e_lo)), "只用低阈值 (50, 50)：孤立淡圆也混进来", 22, RED),
    ]
    grid_ = col([row(tiles[:2], gap=40), row(tiles[2:], gap=40)], gap=20)
    paste(c, grid_, 40, 130)
    yb = 130 + grid_.shape[0] + 30
    c = text(c, "② 等号边界实测：cv2.Canny(dx, dy, 50, 150) 直接给定变化强度（每组互不相连）", (40, yb), 22, INK, anchor="lm")
    x = 40; yb += 34
    for name, vals, out in res:
        cw = 64
        w = max(len(vals) * cw, text_size(name, 18)[0] + 10)
        c = text(c, name, (x, yb + 12), 18, GRAY, anchor="lm")
        for i, (v, o) in enumerate(zip(vals, out)):
            xx = x + i * cw
            colr = C_STRONG if v > HIGH else (C_WEAK if v > LOW else C_NONE)
            cv2.rectangle(c, (xx, yb + 30), (xx + cw - 4, yb + 70), colr, -1)
            c = text(c, str(v), (xx + cw // 2 - 2, yb + 50), 20, WHITE if v > HIGH else INK, anchor="mm")
            cv2.rectangle(c, (xx, yb + 76), (xx + cw - 4, yb + 116), (o, o, o), -1)
            cv2.rectangle(c, (xx, yb + 76), (xx + cw - 4, yb + 116), GRAY, 1)
            c = text(c, str(o), (xx + cw // 2 - 2, yb + 96), 20, INK if o else WHITE, anchor="mm")
        x += w + 36
    c = text(c, "上排：给定变化强度；下排：Canny 输出。150 = 高阈值，不算强边，孤立时删除；50 = 低阈值，不进入候选。",
             (40, yb + 150), 20, INK, anchor="lm")
    c = c[:yb + 180]
    save(stamp(c, "核对附件 · 不进课件 · 合成输入"), L, "23-p5-ref-Canny实测对照与边界核对_附件.png")


if __name__ == "__main__":
    print("[23] 边缘检测")
    img, e, e_hi, e_lo = main()
    classroom()
    attachment(img, e, e_hi, e_lo)
