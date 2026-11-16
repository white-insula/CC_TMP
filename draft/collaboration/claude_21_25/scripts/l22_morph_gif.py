# -*- coding: utf-8 -*-
"""22-P4《腐蚀与膨胀》候选动画。

- 合成二值图：白色 = 目标，黑色 = 背景；含大目标、目标内小黑洞、背景小白点、细笔画、留缝的断线。
- 腐蚀和膨胀**各自从同一张原图出发**（两路分支），不是先腐蚀再膨胀；
  核 np.ones((5, 5), np.uint8)，iterations = 1 和 3，均用 OpenCV 实算并断言预期现象。
- 结果图上的橙色细线是原图白色区域的外轮廓，只作对照，不是运算结果的一部分。

输出（previews/22/）：
  22-p4-anim-腐蚀与膨胀两路对比_候选.gif
  22-p4-anim-关键帧拼图_审阅用.png
  22-p4-diag-腐蚀与膨胀两路对比_静态_候选.png   （GIF 最后一帧，可作静态版本）
"""
import cv2
import numpy as np
from _common import *

L = "22"
K = np.ones((5, 5), np.uint8)
S = 1.25                       # 显示放大倍数（最近邻，不改变像素关系）


def make_binary():
    b = np.zeros((220, 320), np.uint8)
    cv2.rectangle(b, (30, 40), (150, 180), 255, -1)                 # 大目标
    for (x, y) in ((70, 80), (110, 130), (60, 150)):
        cv2.circle(b, (x, y), 2, 0, -1)                              # 目标里的小黑洞（直径 5）
    b[40:181, 190:200] = 255                                         # 细笔画，宽 10
    b[100:112, 215:256] = 255                                        # 断线左段
    b[100:112, 260:301] = 255                                        # 断线右段，缝宽 4（x 256…259）
    for (x, y) in ((175, 20), (240, 50), (290, 170), (15, 200), (230, 190), (300, 30), (170, 205), (260, 140)):
        cv2.circle(b, (x, y), 2, 255, -1)                            # 背景小白点（直径 5）
    return b


def verify(b):
    e1 = cv2.erode(b, K, iterations=1); e3 = cv2.erode(b, K, iterations=3)
    d1 = cv2.dilate(b, K, iterations=1); d3 = cv2.dilate(b, K, iterations=3)
    # iterations=3 等于连续做 3 次
    assert (e3 == cv2.erode(cv2.erode(cv2.erode(b, K), K), K)).all()
    assert (d3 == cv2.dilate(cv2.dilate(cv2.dilate(b, K), K), K)).all()
    specks = ((175, 20), (240, 50), (290, 170), (15, 200))
    assert all(e1[y, x] == 0 for x, y in specks), "腐蚀 1 次应吃掉小白点"
    assert e1[110, 194] == 255 and e3[110, 194] == 0, "细笔画：腐蚀 1 次还在、3 次消失"
    assert all(d1[y, x] == 255 for x, y in ((70, 80), (110, 130), (60, 150))), "膨胀 1 次应填上小黑洞"
    assert b[105, 257] == 0 and d1[105, 257] == 255, "膨胀 1 次应连上断线"
    n = lambda im: int((im > 0).sum())
    info = {"原图": n(b), "erode×1": n(e1), "erode×3": n(e3), "dilate×1": n(d1), "dilate×3": n(d3)}
    print("    白色像素数:", info)
    return e1, e3, d1, d3, info


def show(img, ref):
    """放大显示，并在上面画原图白色区域外轮廓（橙色细线）作对照。"""
    v = cv2.resize(bgr(img), None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST)
    if ref is not None:
        big = cv2.resize(ref, None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST)
        cnts, _ = cv2.findContours(big, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(v, cnts, -1, AMB, 1, cv2.LINE_AA)
    return border(v, (120, 120, 120), 2)


def placeholder(w, h):
    c = canvas(w, h, (246, 246, 246))
    cv2.rectangle(c, (0, 0), (w - 1, h - 1), (210, 210, 210), 2)
    return c


def main():
    b = make_binary()
    e1, e3, d1, d3, info = verify(b)
    tw, th = int(320 * S) + 4, int(220 * S) + 4
    cells = [  # (结果, 标题, 代码, 位置列, 位置行, 颜色)
        (e1, "腐蚀 1 次：白色缩一圈，小白点被吃掉", "cv2.erode(binary, kernel, iterations=1)", 0, 0, BLUE),
        (e3, "腐蚀 3 次：细笔画、断线整段被吃没", "cv2.erode(binary, kernel, iterations=3)", 1, 0, BLUE),
        (d1, "膨胀 1 次：白色长一圈，小黑洞填上、断线连上", "cv2.dilate(binary, kernel, iterations=1)", 0, 1, GREEN),
        (d3, "膨胀 3 次：越长越胖，细节糊在一起", "cv2.dilate(binary, kernel, iterations=3)", 1, 1, GREEN),
    ]
    GX, GY, GW, GH = 640, 150, tw + 40, th + 92

    def frame(k_shown, note=None):
        c = canvas(1560, 960)
        c = text(c, "腐蚀与膨胀（约定：白色 = 目标，黑色 = 背景）", (40, 46), 32, INK, anchor="lm")
        c = text(c, "kernel = np.ones((5, 5), np.uint8)    两路都从同一张原图出发", (40, 96), 24, GRAY, anchor="lm")
        oy = GY + (2 * GH - th) // 2 - 40
        paste(c, show(b, None), 40, oy)
        c = text(c, "原图 binary", (40 + tw // 2, oy + th + 24), 24, INK, anchor="mm")
        c = text(c, "小黑洞 ×3、小白点 ×8、细笔画、断线（缝 4 像素）", (40 + tw // 2, oy + th + 58), 18, GRAY, anchor="mm")
        for i, (im, title, code, cx, cy, colr) in enumerate(cells):
            x, y = GX + cx * GW, GY + cy * GH
            if i < k_shown:
                paste(c, show(im, b), x, y)
                c = text(c, title, (x, y + th + 22), 20, colr, anchor="lm")
                c = text(c, code, (x, y + th + 52), 17, GRAY, anchor="lm")
            else:
                paste(c, placeholder(tw, th), x, y)
        # 两路分支箭头：原图 → 腐蚀行、原图 → 膨胀行
        sx, sy = 40 + tw + 6, oy + th // 2
        ex = sx + 34                                     # 分叉点
        cv2.line(c, (sx, sy), (ex, sy), INK, 3, cv2.LINE_AA)
        for ty, colr, lab in ((GY + th // 2, BLUE, "腐蚀 erode"), (GY + GH + th // 2, GREEN, "膨胀 dilate")):
            cv2.line(c, (ex, sy), (ex, ty), colr, 3, cv2.LINE_AA)
            cv2.arrowedLine(c, (ex, ty), (GX - 10, ty), colr, 3, cv2.LINE_AA, tipLength=0.12)
            c = text(c, lab, ((ex + GX) // 2, ty - 22), 20, colr, anchor="mm")
        if note:
            c = text(c, note, (780, 922), 22, INK, anchor="mm")
        else:
            c = text(c, "橙色细线 = 原图白色区域的轮廓，用来对比缩了还是长了", (780, 922), 20, AMB, anchor="mm")
        return stamp(c, "候选 · 合成二值图；结果由 cv2.erode / cv2.dilate 实算")

    frames, durs = [], []
    seq = [(0, "先看原图：白色是目标，黑色是背景", 2600),
           (1, None, 2600), (2, None, 2600), (3, None, 2800), (4, None, 2600),
           (4, "腐蚀和膨胀是两个独立操作，都从原图出发；次数要适度", 4000)]
    for k, note, ms in seq:
        frames.append(frame(k, note)); durs.append(ms)
    save_gif(frames, L, "22-p4-anim-腐蚀与膨胀两路对比_候选.gif", durs)
    keyframe_sheet(frames, [0, 2, 5], L, "22-p4-anim-关键帧拼图_审阅用.png",
                   labels=["原图", "腐蚀 1 次、3 次", "完成：两路结果并列"])
    save(frames[-1], L, "22-p4-diag-腐蚀与膨胀两路对比_静态_候选.png")
    print(f"    GIF {len(frames)} 帧，总时长 {sum(durs) / 1000:.1f} 秒")


if __name__ == "__main__":
    print("[22] 形态学操作")
    main()
