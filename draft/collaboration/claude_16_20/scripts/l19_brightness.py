# -*- coding: utf-8 -*-
"""第19讲《亮度与对比度调整》候选素材。

输出（previews/19/）：
  19-p4-diag-公式与alpha_beta作用_候选.png   P4 缺项；旧图 19-p4-diag-加法公式与权重.png 为“需改”（画成 addWeighted）
  19-p5-diag-uint8溢出表盘_候选.png          P5 缺项；旧图对策漏 np.clip，已按审核意见改为 cv2.add / convertScaleAbs
  19-p6-shot-溢出黑斑与cv2.add对比_替身图.png P6 录屏静态参考，含单像素 [[94]] [[255]] 实跑
  19-p7-shot-convertScaleAbs三组对比_替身图.png P7 录屏静态参考；dark.jpg 未上传，以替身图压暗合成
所有数值均由本脚本实跑得出并打印。
"""
import math
import cv2
import numpy as np
from _common import *

L = "19"


def _curve_panel(alpha, beta, title, colr, size=300):
    """新像素 = clip(α·原 + β) 的映射曲线 + 灰度渐变条前后对比。"""
    P = 46
    c = canvas(size + P + 20, size + P + 150)
    ox, oy = P, 20 + size                      # 原点（左下）
    cv2.rectangle(c, (ox, oy - size), (ox + size, oy), (245, 245, 245), -1)
    cv2.line(c, (ox, oy), (ox + size, oy - size), (190, 190, 190), 1, cv2.LINE_AA)  # 不变线
    pts = []
    for v in range(256):
        nv = int(np.clip(alpha * v + beta, 0, 255))
        pts.append((ox + int(v / 255 * size), oy - int(nv / 255 * size)))
    cv2.polylines(c, [np.array(pts, np.int32)], False, colr, 4, cv2.LINE_AA)
    cv2.rectangle(c, (ox, oy - size), (ox + size, oy), INK, 1)
    c = text(c, "0", (ox - 8, oy + 4), 16, GRAY, anchor="ra")
    c = text(c, "255", (ox + size, oy + 4), 16, GRAY, anchor="ra")
    c = text(c, "255", (ox - 6, oy - size), 16, GRAY, anchor="rt")
    c = text(c, "原像素 →", (ox + size // 2, oy + 6), 16, GRAY, anchor="ma")
    c = text(c, "新", (ox - 30, oy - size // 2), 16, GRAY, anchor="mm")
    # 渐变条
    grad = np.tile(np.linspace(0, 255, size).astype(np.uint8), (26, 1))
    after = cv2.convertScaleAbs(grad, alpha=alpha, beta=beta) if beta >= 0 else np.clip(grad.astype(np.float32) * alpha + beta, 0, 255).astype(np.uint8)
    paste(c, bgr(grad), ox, oy + 34)
    paste(c, bgr(after), ox, oy + 66)
    c = text(c, "原", (ox - 8, oy + 47), 16, GRAY, anchor="rm")
    c = text(c, "新", (ox - 8, oy + 79), 16, GRAY, anchor="rm")
    c = text(c, title, (ox + size // 2, oy + 116), 22, colr, anchor="mm")
    return c


def p4_formula():
    panels = [_curve_panel(1.0, 50, "β = +50：整体变亮", BLUE),
              _curve_panel(1.0, -50, "β = -50：整体变暗", BLUE),
              _curve_panel(1.5, 0, "α = 1.5：差距拉大", GREEN),
              _curve_panel(0.5, 0, "α = 0.5：差距缩小（也变暗）", GREEN)]
    body = row(panels, gap=16)
    head = canvas(body.shape[1], 120)
    head = text(head, "新像素 = ", (40, 50), 40, INK, anchor="lm")
    x = 40 + text_size("新像素 = ", 40)[0]
    for s, colr in [("α", GREEN), (" × 原像素 + ", INK), ("β", BLUE)]:
        head = text(head, s, (x, 50), 40, colr, anchor="lm")
        x += text_size(s, 40)[0]
    head = text(head, "β 加减 → 调亮度（正亮负暗）     α 乘法 → 调对比度（>1 增强，<1 减弱）     结果超出 0–255 时封顶/封底",
                (40, 100), 20, GRAY, anchor="lm")
    out = col([head, body], gap=0)
    save(stamp(out, "候选 · 示意图 · 程序绘制（β<0 一栏用 float + np.clip 计算）"), L, "19-p4-diag-公式与alpha_beta作用_候选.png")


def p5_dial():
    a, b = np.uint8([[250]]), np.uint8([[10]])
    wrap = int((a + b)[0, 0]); sat = int(cv2.add(a, b)[0, 0])
    print(f"    NumPy 250+10 = {wrap}；cv2.add 250+10 = {sat}")
    assert (wrap, sat) == (4, 255)
    W, H = 1400, 680
    c = canvas(W, H)
    c = text(c, "uint8 只能存 0 ~ 255：超出后会“绕回去”", (40, 46), 34, INK, anchor="lm")
    cx, cy, R = 360, 380, 230
    cv2.circle(c, (cx, cy), R, (235, 235, 235), -1)
    cv2.circle(c, (cx, cy), R, INK, 3, cv2.LINE_AA)
    ang = lambda v: math.radians(-90 + v / 256 * 360)          # 0 在正上方，顺时针增加
    P = lambda v, r: (int(cx + r * math.cos(ang(v))), int(cy + r * math.sin(ang(v))))
    for v in range(0, 256, 16):
        cv2.line(c, P(v, R - 16), P(v, R), INK, 2, cv2.LINE_AA)
    for v in (0, 64, 128, 192):
        c = text(c, str(v), P(v, R - 44), 22, GRAY, anchor="mm")
    # 表盘上只标起点 250 与终点 4
    for v, lab, off in [(250, "250", (-34, -18)), (4, "4", (26, -18))]:
        p = P(v, R)
        cv2.circle(c, p, 9, RED, -1, cv2.LINE_AA)
        c = text(c, lab, (p[0] + off[0], p[1] + off[1]), 24, RED, anchor="mm")
    # 表盘中央：放大的数字条 247…255 | 0…5，逐格 +1
    vals = list(range(247, 256)) + list(range(0, 6))
    cw, ch = 26, 40
    sx, sy = cx - len(vals) * cw // 2, cy - 100
    c = text(c, "放大看：每 +1 前进一格", (cx, sy - 30), 20, GRAY, anchor="mm")
    for i, v in enumerate(vals):
        x = sx + i * cw
        fill = (200, 200, 250) if v in (250, 4) else ((255, 255, 255) if v != 255 else (225, 225, 225))
        cv2.rectangle(c, (x, sy), (x + cw, sy + ch), fill, -1)
        cv2.rectangle(c, (x, sy), (x + cw, sy + ch), INK, 1)
        c = text(c, str(v), (x + cw // 2, sy + ch // 2), 11 if v > 99 else 15, RED if v in (250, 4) else INK, anchor="mm")
    i0, i1 = vals.index(250), vals.index(4)
    y_arc = sy + ch + 18
    cv2.arrowedLine(c, (sx + i0 * cw + cw // 2, y_arc), (sx + i1 * cw + cw // 2, y_arc), RED, 3, cv2.LINE_AA, tipLength=0.06)
    c = text(c, "+10", (sx + (i0 + i1) * cw // 2 + cw // 2, y_arc + 22), 24, RED, anchor="mm")
    xb = sx + vals.index(0) * cw
    cv2.line(c, (xb, sy - 8), (xb, sy + ch + 8), RED, 3)
    c = text(c, "250 → 255 → 0 → 4", (cx, cy + 110), 30, INK, anchor="mm")
    # 右侧对照
    x0 = 720
    wrap_s, sat_s = (a + b).tolist(), cv2.add(a, b).tolist()        # 实跑结果，直接写进图里
    scalar = cv2.add(250, 10)                                         # 对照：标量调用不是 uint8 饱和
    print(f"    对照：cv2.add(250, 10) 返回 {scalar.dtype} {scalar.ravel().tolist()}（不是 uint8 饱和，图中不使用）")
    cv2.rectangle(c, (x0, 110), (W - 40, 220), (243, 243, 243), -1)
    c = text(c, "a = np.uint8([[250]])", (x0 + 20, 145), 26, INK, anchor="lm")
    c = text(c, "b = np.uint8([[10]])", (x0 + 20, 190), 26, INK, anchor="lm")
    cv2.rectangle(c, (x0, 245), (W - 40, 395), (238, 238, 252), -1)
    c = text(c, "NumPy 直接相加：绕回", (x0 + 20, 278), 28, RED, anchor="lm")
    c = text(c, f"print(a + b)  →  {wrap_s}", (x0 + 20, 328), 26, INK, anchor="lm")
    c = text(c, "后果：本该最亮的地方出现黑斑", (x0 + 20, 372), 22, GRAY, anchor="lm")
    cv2.rectangle(c, (x0, 420), (W - 40, 570), (232, 246, 236), -1)
    c = text(c, "OpenCV 函数：封顶（饱和运算）", (x0 + 20, 453), 28, GREEN, anchor="lm")
    c = text(c, f"print(cv2.add(a, b))  →  {sat_s}", (x0 + 20, 503), 26, INK, anchor="lm")
    c = text(c, "对策：用 cv2.add / cv2.convertScaleAbs", (x0 + 20, 547), 22, GRAY, anchor="lm")
    c = text(c, "注意：要写成二维 uint8 数组；直接写 cv2.add(250, 10) 得不到 255", (x0, 610), 20, GRAY, anchor="lm")
    save(stamp(c, "候选 · 示意图 · 数值经实跑核对"), L, "19-p5-diag-uint8溢出表盘_候选.png")


def p6_overflow():
    img = stand_in("coffee")
    bad = img + 100
    good = cv2.add(img, np.full_like(img, 100))
    a = np.uint8([[250]]); b = np.uint8([[100]])
    log = f"print(a + b, cv2.add(a, b)) → {(a + b).tolist()} {cv2.add(a, b).tolist()}"
    print("   ", log)
    t = lambda im, s, colr=INK: caption_below(border(fit(im, w=400)), s, 22, colr)
    out = row([t(img, "原图"), t(bad, "bad = img + 100：亮处变暗、出现怪色", RED), t(good, "good = cv2.add(...)：正常变亮", GREEN)], gap=16)
    info = text(canvas(out.shape[1], 46), log, (out.shape[1] // 2, 23), 22, INK, anchor="mm")
    out = col([out, info], gap=4)
    save(stamp(out, "候选 · 替身图 coffee(CC0)，非 cat.jpg 实拍"), L, "19-p6-shot-溢出黑斑与cv2.add对比_替身图.png")


def p7_scale_abs():
    img = stand_in("coffee")
    dark = cv2.convertScaleAbs(img, alpha=0.3, beta=0)       # 合成暗图（dark.jpg 未上传）
    bright = cv2.convertScaleAbs(img, alpha=1.0, beta=50)
    contrast = cv2.convertScaleAbs(img, alpha=1.5, beta=0)
    fix = cv2.convertScaleAbs(dark, alpha=1.3, beta=40)
    print(f"    合成暗图均值 {dark.mean():.1f} → fix 均值 {fix.mean():.1f}；原图均值 {img.mean():.1f}")
    t = lambda im, s: caption_below(border(fit(im, w=300)), s, 20)
    out = row([t(img, "原图"), t(bright, "alpha=1.0, beta=50"), t(contrast, "alpha=1.5, beta=0"),
               t(dark, "暗图（合成：原图×0.3）"), t(fix, "暗图 alpha=1.3, beta=40")], gap=12)
    note = text(canvas(out.shape[1], 44), "alpha=1.5：未饱和区域亮度差增大，整体也变亮，并不是暗处变得更暗",
                (out.shape[1] // 2, 22), 20, GRAY, anchor="mm")
    out = col([out, note], gap=4)
    save(stamp(out, "候选 · 替身图 coffee(CC0)；暗图为程序合成，非 dark.jpg"), L, "19-p7-shot-convertScaleAbs三组对比_替身图.png")


if __name__ == "__main__":
    print("[19] 亮度与对比度调整")
    p4_formula()
    p5_dial()
    p6_overflow()
    p7_scale_abs()
