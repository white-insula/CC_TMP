# -*- coding: utf-8 -*-
"""24-P5 补充候选（可选）：“两个明显山峰 → 阈值选在山谷”。

依据：24-P5 画面要求“五种典型直方图与对应图像”，要点含“两个明显山峰 → 目标和背景容易分开”；
现有 _visuals/m3.py v24 只画了偏暗/偏亮/对比度低/正常四种（据代码，未看图），缺双峰一种。
本图用合成灰度图（暗背景 + 亮零件，带噪声）实算 calcHist 与 Otsu 阈值，验证 Otsu 阈值落在两峰之间的山谷。

输出（previews/24/）：24-p5-diag-双峰直方图与Otsu山谷_补充候选.png
"""
import cv2
import numpy as np
from _common import *

L = "24"


def synth():
    rng = np.random.default_rng(24)
    g = np.full((260, 360), 70, np.float32)
    cv2.rectangle(g, (40, 50), (150, 200), 180, -1)          # 亮零件 1
    cv2.circle(g, (260, 130), 70, 185, -1)                   # 亮零件 2
    g += rng.normal(0, 12, g.shape)
    return np.clip(g, 0, 255).astype(np.uint8)


def hist_panel(g, t, w=620, h=300):
    hist = cv2.calcHist([g], [0], None, [256], [0, 256]).ravel()
    c = canvas(w + 80, h + 80)
    ox, oy = 50, 20 + h
    m = hist.max()
    for v in range(256):
        x = ox + int(v / 255 * w)
        y = oy - int(hist[v] / m * (h - 10))
        cv2.line(c, (x, oy), (x, y), (80, 80, 80) if v <= t else (170, 170, 170), 3)
    cv2.line(c, (ox, oy), (ox + w, oy), INK, 2)
    xt = ox + int(t / 255 * w)
    cv2.line(c, (xt, 20), (xt, oy), RED, 3)
    c = text(c, f"Otsu 阈值 {t:.0f}：落在山谷", (xt + 8, 34), 20, RED, anchor="lm")
    for v in (0, 128, 255):
        c = text(c, str(v), (ox + int(v / 255 * w), oy + 18), 16, GRAY, anchor="mm")
    c = text(c, "背景（暗）", (ox + int(70 / 255 * w), oy + 46), 18, INK, anchor="mm")
    c = text(c, "零件（亮）", (ox + int(182 / 255 * w), oy + 46), 18, INK, anchor="mm")
    return c, hist


def main():
    g = synth()
    t, b = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    panel, hist = hist_panel(g, t)
    p1, p2 = int(np.argmax(hist[:128])), 128 + int(np.argmax(hist[128:]))
    valley = p1 + int(np.argmin(hist[p1:p2 + 1]))
    print(f"    两峰位置 {p1}、{p2}；山谷最低处 {valley}；Otsu 阈值 {t:.0f}")
    assert p1 < t < p2
    out = row([caption_below(border(g), "合成灰度图：暗背景 + 亮零件", 20), panel,
               caption_below(border(b), f"threshold(gray, 0, 255, BINARY + OTSU)", 18)], gap=20, valign="center")
    out = title_bar(out, "两个明显山峰：目标和背景容易分开，阈值选在两峰之间的山谷（第21讲大津法的思路）", 24)
    save(stamp(out, "补充候选 · 合成灰度图；直方图与 Otsu 由 OpenCV 实算"), L, "24-p5-diag-双峰直方图与Otsu山谷_补充候选.png")


if __name__ == "__main__":
    print("[24] 图像直方图与均衡化")
    main()
