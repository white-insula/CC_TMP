# -*- coding: utf-8 -*-
"""30-P4《多边形近似：把弯弯曲曲的轮廓拉直》候选动画。

同一条合成轮廓（边缘略有起伏的圆，模拟手机照片上的不平整边缘）：
  cv2.findContours(…, CHAIN_APPROX_NONE) 得到原始轮廓 → cv2.approxPolyDP(c, k × 周长, True)，
  k = 0.005 / 0.02 / 0.08，实际顶点数由 OpenCV 计算后写入画面，并按第 30 讲脚本规则给出判断结果。
颜色：灰色细线 = 原始轮廓；红色粗线 = 近似多边形的边；绿色圆点 = 顶点。

输出（previews/30/）：
  30-p4-anim-原始轮廓与近似多边形_候选.gif
  30-p4-anim-关键帧拼图_审阅用.png
"""
import math
import cv2
import numpy as np
from _common import *

L = "30"
KS = (0.005, 0.02, 0.08)
C_RAW, C_EDGE, C_VTX = (150, 150, 150), (40, 40, 220), (60, 170, 60)


def make_contour():
    """二值图上画一个“边缘有起伏的圆”，再用 findContours 取出真实轮廓（不是手写点列）。"""
    b = np.zeros((420, 420), np.uint8)
    pts = []
    for i in range(720):
        a = 2 * math.pi * i / 720
        r = 160 + 3.0 * math.sin(7 * a) + 2.0 * math.sin(19 * a + 0.6)
        pts.append((210 + r * math.cos(a), 210 + r * math.sin(a)))
    cv2.fillPoly(b, [np.round(pts).astype(np.int32)], 255)
    cnts, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    assert len(cnts) == 1
    return b, cnts[0]


def classify(approx):
    """第 30 讲脚本规则（录屏1 原样）。"""
    n = len(approx); x, y, w, h = cv2.boundingRect(approx)
    if n == 3: name = "triangle"
    elif n == 4: name = "square" if 0.95 <= w / h <= 1.05 else "rectangle"
    elif n == 5: name = "pentagon"
    elif n >= 6: name = "circle"
    else: name = "unknown"
    return n, name, w / h


def compute(c):
    peri = cv2.arcLength(c, True)
    res = []
    for k in KS:
        a = cv2.approxPolyDP(c, k * peri, True)
        n, name, ratio = classify(a)
        res.append(dict(k=k, eps=k * peri, approx=a, n=n, name=name, ratio=ratio))
        print(f"    k={k}: epsilon = {k} × {peri:.1f} = {k * peri:.2f} 像素 → 顶点 {n} 个 → {name}（w/h={ratio:.3f}）")
    return peri, res


def draw(c, raw, approx=None, scale=1.0, show_raw=True):
    S = 440
    img = canvas(S, S)
    off = (S - 420) // 2
    if show_raw:
        cv2.polylines(img, [raw + off], True, C_RAW, 2, cv2.LINE_AA)
    if approx is not None:
        cv2.polylines(img, [approx + off], True, C_EDGE, 4, cv2.LINE_AA)
        for p in approx.reshape(-1, 2):
            cv2.circle(img, (int(p[0] + off), int(p[1] + off)), 8, C_VTX, -1, cv2.LINE_AA)
    return img


def frame(raw, peri, r=None, all3=None, note=None):
    c = canvas(1440, 820)
    c = text(c, "多边形近似：approxPolyDP 把轮廓拉直", (40, 44), 32, INK, anchor="lm")
    c = text(c, "approx = cv2.approxPolyDP(c, k * peri, True)        peri = cv2.arcLength(c, True)", (40, 92), 22, BLUE, anchor="lm")
    # 图例
    lx = 40
    for s, colr in (("灰色细线：原始轮廓", C_RAW), ("红色：近似多边形的边", C_EDGE), ("绿点：顶点（角点）", C_VTX)):
        c = text(c, s, (lx, 134), 20, colr, anchor="lm"); lx += 300
    if all3 is None:
        img = draw(c, raw, None if r is None else r["approx"])
        paste(c, border(img), 60, 170)
        x0 = 580
        if r is None:
            c = text(c, f"原始轮廓有 {len(raw)} 个点（CHAIN_APPROX_NONE）", (x0, 260), 28, INK, anchor="lm")
            c = text(c, f"周长 peri = {peri:.1f} 像素", (x0, 320), 28, INK, anchor="lm")
            c = text(c, "边上有很多小起伏，直接数点没有意义", (x0, 380), 26, GRAY, anchor="lm")
        else:
            c = text(c, f"k = {r['k']}", (x0, 230), 40, INK, anchor="lm")
            c = text(c, f"epsilon = {r['k']} × {peri:.1f} = {r['eps']:.1f} 像素", (x0, 300), 28, INK, anchor="lm")
            c = text(c, f"len(approx) = {r['n']}", (x0, 366), 36, C_VTX, anchor="lm")
            c = text(c, f"按本课规则判断 → {r['name']}", (x0, 432), 30, INK, anchor="lm")
            if r["name"] in ("square", "rectangle"):
                c = text(c, f"（4 个角点，w/h = {r['ratio']:.2f}）", (x0, 480), 24, GRAY, anchor="lm")
    else:
        for i, r_ in enumerate(all3):
            img = fit(draw(c, raw, r_["approx"]), w=400)
            x = 60 + i * 450
            paste(c, border(img), x, 170)
            colr = {0.005: INK, 0.02: GREEN, 0.08: RED}[r_["k"]]
            c = text(c, f"k = {r_['k']}：{r_['n']} 个顶点 → {r_['name']}", (x + 200, 600), 26, colr, anchor="mm")
            c = text(c, f"epsilon = {r_['eps']:.1f} 像素", (x + 200, 640), 22, GRAY, anchor="mm")
    if note:
        c = text(c, note, (720, 760), 26, INK, anchor="mm")
    return stamp(c, "候选 · 合成轮廓（边缘带起伏的圆）；顶点数由 cv2.approxPolyDP 实算")


def main():
    b, raw = make_contour()
    peri, res = compute(raw)
    ns = [r["n"] for r in res]
    assert ns[0] > ns[1] > ns[2], ns          # 系数越大，顶点越少
    frames, durs = [], []

    def add(f, ms):
        frames.append(f); durs.append(ms)

    add(frame(raw, peri, note="先找到轮廓：几百个点，边上有小弯曲"), 3000)
    notes = {0.005: "允许的误差很小：贴得更紧，顶点明显变多（本例判断结果仍是 circle）",
             0.02: "约 2% 周长：既拉直了小起伏，又保留了形状特点",
             0.08: "允许的误差太大：圆被拉成了四边形"}
    for r in res:
        add(frame(raw, peri, r=r, note=notes[r["k"]]), 3400)
    add(frame(raw, peri, all3=res, note="k 越大越粗略、顶点越少；0.08 把圆拉成了四边形。本课一般取 0.02 左右，再按图片微调"), 4600)
    save_gif(frames, L, "30-p4-anim-原始轮廓与近似多边形_候选.gif", durs)
    keyframe_sheet(frames, [0, 1, 2, 3, 4], L, "30-p4-anim-关键帧拼图_审阅用.png",
                   labels=["原始轮廓", f"k=0.005：{ns[0]} 个顶点", f"k=0.02：{ns[1]} 个顶点", f"k=0.08：{ns[2]} 个顶点", "三者对比"])
    print(f"    GIF {len(frames)} 帧，总时长 {sum(durs) / 1000:.1f} 秒；原始轮廓点数 {len(raw)}")


if __name__ == "__main__":
    print("[30] 形状识别 · P4")
    main()
