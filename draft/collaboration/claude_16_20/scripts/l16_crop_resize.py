# -*- coding: utf-8 -*-
"""第16讲《图像的裁剪与缩放》候选素材。

输出（previews/16/）：
  16-p4-diag-ROI坐标与切片对应_候选.png   P4 整幅画面与 ROI 框选示意（带坐标轴、两角点、切片代码）
  16-p5-diag-resize参数宽在前_候选.png      P5 resize 参数说明，“宽在前”红色高亮
  16-p6-shot-裁剪结果预览_替身图.png        P6 录屏静态参考：脚本坐标 [80:250, 100:300] 实跑结果
  16-p7-shot-三种缩放与压扁对比_替身图.png  P7 录屏静态参考：(320,240) / fx=fy=0.5 / 保持宽高比宽400 / 写反(240,320)
输入：scikit-image coffee.png（CC0）作为 cat.jpg（果盘）的替身。
"""
import cv2
import numpy as np
from _common import *

L = "16"


def p4_roi():
    img = stand_in("coffee")                        # 400×600
    x1, y1, x2, y2 = 100, 80, 300, 250              # 与第16讲脚本 P6 的示例坐标一致
    roi = img[y1:y2, x1:x2]
    assert roi.shape == (170, 200, 3)

    M = 70                                          # 留出坐标轴空间
    show = img.copy()
    cv2.rectangle(show, (x1, y1), (x2, y2), AMB, 3)
    for (px, py) in ((x1, y1), (x2, y2)):
        cv2.circle(show, (px, py), 7, RED, -1)
    big = canvas(img.shape[1] + M + 20, img.shape[0] + M + 90)
    paste(big, show, M, M)
    # 坐标轴：x 向右、y 向下
    cv2.arrowedLine(big, (M, M - 30), (M + img.shape[1], M - 30), INK, 2, tipLength=0.02)
    cv2.arrowedLine(big, (M - 30, M), (M - 30, M + img.shape[0]), INK, 2, tipLength=0.03)
    big = text(big, "x（列）→", (M + img.shape[1] - 120, M - 58), 22, INK)
    big = text(big, "y（行）↓", (M - 40, M + img.shape[0] + 14), 22, INK)
    big = text(big, "(0, 0)", (M - 8, M - 52), 18, GRAY)
    big = text(big, f"左上 ({x1}, {y1})", (M + x1 + 10, M + y1 + 6), 20, WHITE, bg=RED, pad=4)
    big = text(big, f"右下 ({x2}, {y2})", (M + x2 + 10, M + y2 - 12), 20, WHITE, bg=RED, pad=4)

    # 右侧：代码与结果
    right = canvas(560, big.shape[0])
    right = text(right, "roi = img[", (10, 40), 30, INK)
    w0, _ = text_size("roi = img[", 30)
    right = text(right, f"{y1}:{y2}", (10 + w0, 40), 30, BLUE)
    w1, _ = text_size(f"{y1}:{y2}", 30)
    right = text(right, ", ", (10 + w0 + w1, 40), 30, INK)
    w2, _ = text_size(", ", 30)
    right = text(right, f"{x1}:{x2}", (10 + w0 + w1 + w2, 40), 30, GREEN)
    w3, _ = text_size(f"{x1}:{x2}", 30)
    right = text(right, "]", (10 + w0 + w1 + w2 + w3, 40), 30, INK)
    right = text(right, "先 y（行范围）", (10, 100), 24, BLUE)
    right = text(right, "后 x（列范围）", (220, 100), 24, GREEN)
    roi_b = border(fit(roi, w=300), AMB, 3)
    paste(right, roi_b, 10, 150)
    right = text(right, f"roi.shape → ({y2 - y1}, {x2 - x1}, 3)", (10, 150 + roi_b.shape[0] + 16), 24, INK)
    right = text(right, "高 = 250 - 80 = 170，宽 = 300 - 100 = 200", (10, 150 + roi_b.shape[0] + 56), 20, GRAY)
    right = text(right, "需要单独修改时：img[80:250, 100:300].copy()", (10, 150 + roi_b.shape[0] + 96), 20, RED)
    out = row([big, right], gap=10)
    out = title_bar(out, "裁剪 = 切片：整幅画面中只取感兴趣区域 ROI")
    save(stamp(out, "候选 · 示意图 · 替身图 coffee(CC0)"), L, "16-p4-diag-ROI坐标与切片对应_候选.png")


def p5_resize_params():
    W, H = 1280, 720
    c = canvas(W, H)
    c = text(c, "cv2.resize 的两种写法", (40, 50), 36, INK)
    # 写法一
    y = 140
    c = text(c, "① 按尺寸：", (40, y), 30, INK)
    seg = [("cv2.resize(img, (", INK), ("宽", RED), (", ", INK), ("高", BLUE), ("))", INK)]
    x = 210
    for s, col_ in seg:
        c = text(c, s, (x, y), 34, col_)
        if s == "宽":
            kx, kw = x, text_size(s, 34)[0]
        x += text_size(s, 34)[0] + (6 if s in ("宽", "高") else 0)
    cv2.rectangle(c, (kx - 6, y - 6), (kx + kw + 6, y + 46), RED, 3)
    c = text(c, "宽在前！", (kx + kw // 2, y + 80), 26, WHITE, bg=RED, pad=6, anchor="mm")
    # 对照 shape
    c = text(c, "对照：img.shape → (", (720, y + 4), 28, GRAY)
    x = 720 + text_size("对照：img.shape → (", 28)[0]
    for s, col_ in [("高", BLUE), (", ", GRAY), ("宽", RED), (", 通道)", GRAY)]:
        c = text(c, s, (x, y + 4), 28, col_)
        x += text_size(s, 28)[0]
    c = text(c, "shape 高在前，resize 宽在前 —— 正好相反", (720, y + 62), 22, GRAY)
    # 写法二
    y = 340
    c = text(c, "② 按比例：", (40, y), 30, INK)
    c = text(c, "cv2.resize(img, None, fx=0.5, fy=0.5)", (210, y), 34, INK)
    c = text(c, "尺寸写 None；fx = 横向倍数，fy = 纵向倍数；0.5 = 缩小一半", (210, y + 60), 24, GRAY)
    # 插值
    y = 500
    c = text(c, "③ 插值 interpolation：", (40, y), 30, INK)
    cv2.rectangle(c, (60, y + 60), (600, y + 160), (240, 240, 240), -1)
    cv2.rectangle(c, (660, y + 60), (1220, y + 160), (240, 240, 240), -1)
    c = text(c, "缩小", (80, y + 75), 26, INK)
    c = text(c, "cv2.INTER_AREA", (80, y + 115), 28, GREEN)
    c = text(c, "放大", (680, y + 75), 26, INK)
    c = text(c, "cv2.INTER_LINEAR / INTER_CUBIC", (680, y + 115), 28, GREEN)
    save(stamp(c, "候选 · 示意图 · 程序绘制"), L, "16-p5-diag-resize参数宽在前_候选.png")


def p6_crop_preview():
    img = stand_in("coffee")
    roi = img[80:250, 100:300]
    log = f"print(roi.shape) → {roi.shape}"
    print("   ", log)
    show = img.copy()
    cv2.rectangle(show, (100, 80), (300, 250), AMB, 3)
    a = caption_below(border(show), "原图（替身图）上的裁剪范围")
    b = caption_below(border(roi), "roi = img[80:250, 100:300]")
    out = row([a, b], valign="top")
    out = col([out, text(canvas(out.shape[1], 50), log, (out.shape[1] // 2, 25), 26, INK, anchor="mm")], gap=6)
    save(stamp(out, "候选 · 替身图 coffee(CC0)，非 cat.jpg 实拍"), L, "16-p6-shot-裁剪结果预览_替身图.png")


def p7_resize_preview():
    img = stand_in("coffee")                        # 宽600 高400
    a = cv2.resize(img, (320, 240))
    b = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]
    new_w = 400
    new_h = int(h * new_w / w)
    c = cv2.resize(img, (new_w, new_h))
    sq = cv2.resize(img, (240, 320))               # 宽高写反
    logs = [f"a.shape = {a.shape}", f"b.shape = {b.shape}", f"c.shape = {c.shape}", f"写反.shape = {sq.shape}"]
    for s in logs:
        print("   ", s)
    # 按真实像素等比例排列（不再统一缩放），保留大小差异
    tiles = [
        caption_below(border(a), "(320, 240) → 宽320 高240", 20),
        caption_below(border(b), "fx=fy=0.5 → 300×200", 20),
        caption_below(border(c), f"保持宽高比：宽400 → 高{new_h}", 20),
        caption_below(border(sq, RED, 3), "写反 (240, 320)：被压扁", 20, RED),
    ]
    top = row(tiles, gap=20, valign="top")
    note = canvas(top.shape[1], 60)
    note = text(note, f"原图 {w}×{h}（宽×高）；打印 a.shape 得到 {a.shape}：高在前，别看糊涂", (top.shape[1] // 2, 30), 22, INK, anchor="mm")
    out = col([top, note], gap=4)
    save(stamp(out, "候选 · 替身图 coffee(CC0)，非 cat.jpg 实拍"), L, "16-p7-shot-三种缩放与压扁对比_替身图.png")


if __name__ == "__main__":
    print("[16] 图像的裁剪与缩放")
    p4_roi()
    p5_resize_params()
    p6_crop_preview()
    p7_resize_preview()
