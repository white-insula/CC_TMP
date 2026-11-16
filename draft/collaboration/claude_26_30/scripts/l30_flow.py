# -*- coding: utf-8 -*-
"""30-P5《按角点数判断形状》候选：判断流程图（课堂版）＋ 规则核对附件。

规则严格按第 30 讲脚本录屏1：
  n == 3 → triangle；n == 4 → 0.95 ≤ w/h ≤ 1.05 为 square，否则 rectangle（w、h 来自 boundingRect(approx)）；
  n == 5 → pentagon；n ≥ 6 → circle（本练习暂判）；其他 → unknown。
这是本课标准示例（分开摆放、摆正的规则图形）上的简化规则，不是通用判据。

输出（previews/30/）：
  30-p5-diag-形状判断流程图_课堂版_候选.png        1280×720 大字版
  30-p5-ref-形状判断规则实测_核对附件.png          合成形状逐个跑脚本流程，含六边形、旋转矩形等局限示例（不进课件）
"""
import math
import cv2
import numpy as np
from _common import *

L = "30"
C_DEC, C_RES, C_UNK = (250, 238, 220), (225, 245, 228), (235, 235, 235)


def classify(c):
    """第 30 讲录屏1 流程：周长 → approxPolyDP(0.02) → 角点数 → 判断。"""
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    n = len(approx); x, y, w, h = cv2.boundingRect(approx)
    if n == 3: name = "triangle"
    elif n == 4: name = "square" if 0.95 <= w / h <= 1.05 else "rectangle"
    elif n == 5: name = "pentagon"
    elif n >= 6: name = "circle"
    else: name = "unknown"
    return n, name, w / h, approx


# ---------------- 课堂版流程图 ----------------
def diamond(c, cx, cy, w, h, s, size=26):
    pts = np.array([[cx, cy - h // 2], [cx + w // 2, cy], [cx, cy + h // 2], [cx - w // 2, cy]], np.int32)
    cv2.fillPoly(c, [pts], C_DEC); cv2.polylines(c, [pts], True, BLUE, 3, cv2.LINE_AA)
    return text(c, s, (cx, cy), size, INK, anchor="mm")


def box(c, cx, cy, w, h, s, fill=C_RES, edge=GREEN, size=28, tc=INK):
    cv2.rectangle(c, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), fill, -1)
    cv2.rectangle(c, (cx - w // 2, cy - h // 2), (cx + w // 2, cy + h // 2), edge, 3)
    return text(c, s, (cx, cy), size, tc, anchor="mm")


def arrow(c, p, q, lab=None, lab_at=None):
    cv2.arrowedLine(c, p, q, INK, 3, cv2.LINE_AA, tipLength=min(0.3, 18 / max(1, math.dist(p, q))))
    if lab:
        c = text(c, lab, lab_at, 22, INK, anchor="mm")
    return c


def classroom():
    c = canvas(1280, 690)                       # 加 30 像素候选条后为 1280×720
    c = text(c, "按角点数判断形状（本课标准示例的简化规则）", (40, 40), 32, INK, anchor="lm")
    c = box(c, 250, 104, 360, 52, "n = len(approx)", fill=(245, 245, 245), edge=INK, size=26)
    DX, W, H = 250, 220, 84
    rows = [190, 300, 410, 520]
    labels = ["n == 3 ?", "n == 4 ?", "n == 5 ?", "n ≥ 6 ?"]
    c = arrow(c, (DX, 130), (DX, rows[0] - H // 2))
    for i, (y, s) in enumerate(zip(rows, labels)):
        c = diamond(c, DX, y, W, H, s)
        if i < 3:
            c = arrow(c, (DX, y + H // 2), (DX, rows[i + 1] - H // 2), "否", (DX + 24, (y + rows[i + 1]) // 2))
    # 是 → 结果
    RX = 560
    c = arrow(c, (DX + W // 2, rows[0]), (RX - 110, rows[0]), "是", ((DX + W // 2 + RX - 110) // 2, rows[0] - 18))
    c = box(c, RX, rows[0], 220, 60, "三角形")
    # n == 4 → 宽高比
    D2X = 560
    c = arrow(c, (DX + W // 2, rows[1]), (D2X - 160, rows[1]), "是", ((DX + W // 2 + D2X - 160) // 2, rows[1] - 18))
    c = diamond(c, D2X, rows[1], 320, 96, "0.95 ≤ w / h ≤ 1.05 ?", 24)
    c = arrow(c, (D2X + 160, rows[1]), (900, rows[1] - 34), "是", (820, rows[1] - 42))
    c = box(c, 1000, rows[1] - 34, 200, 52, "正方形")
    c = arrow(c, (D2X + 160, rows[1]), (900, rows[1] + 34), "否", (820, rows[1] + 40))
    c = box(c, 1000, rows[1] + 34, 200, 52, "长方形")
    c = arrow(c, (DX + W // 2, rows[2]), (RX - 110, rows[2]), "是", ((DX + W // 2 + RX - 110) // 2, rows[2] - 18))
    c = box(c, RX, rows[2], 220, 60, "五边形")
    c = arrow(c, (DX + W // 2, rows[3]), (RX - 150, rows[3]), "是", ((DX + W // 2 + RX - 150) // 2, rows[3] - 18))
    c = box(c, RX + 40, rows[3], 380, 60, "圆形（本练习暂判）", size=26)
    c = arrow(c, (DX, rows[3] + H // 2), (DX, 600), "否", (DX + 24, rows[3] + H // 2 + 20))
    c = box(c, DX, 626, 220, 48, "unknown", fill=C_UNK, edge=GRAY, size=24)
    # 右下说明
    nx = 820
    c = text(c, "w、h 来自 boundingRect(approx)", (nx, 430), 22, GRAY, anchor="lm")
    c = text(c, "只适用于：分开摆放、摆正的规则图形", (nx, 500), 22, RED, anchor="lm")
    c = text(c, "六边形等 ≥ 6 个角点也会被判成圆", (nx, 540), 22, RED, anchor="lm")
    c = text(c, "旋转的矩形不能直接用 w/h 判断", (nx, 580), 22, RED, anchor="lm")
    out = stamp(c, "候选 · 课堂版 · 规则与第 30 讲脚本一致")
    assert out.shape[:2] == (720, 1280)
    save(out, L, "30-p5-diag-形状判断流程图_课堂版_候选.png")


# ---------------- 核对附件：合成形状实测 ----------------
def poly(n, r, cx, cy, rot_deg=-90):
    return np.array([[cx + r * math.cos(math.radians(rot_deg + 360 * i / n)), cy + r * math.sin(math.radians(rot_deg + 360 * i / n))] for i in range(n)], np.int32)


def rect_pts(cx, cy, w, h, ang):
    return cv2.boxPoints(((cx, cy), (w, h), ang)).astype(np.int32)


def attachment():
    # 白底黑形状（与录屏素材同类：白纸上的黑色图形），每格 260×260
    cases = [  # (名称, 预期, 画法)
        ("三角形", "triangle", lambda im, cx, cy: cv2.fillPoly(im, [poly(3, 95, cx, cy)], 0)),
        ("正方形 160×160", "square", lambda im, cx, cy: cv2.rectangle(im, (cx - 80, cy - 80), (cx + 80, cy + 80), 0, -1)),
        ("长方形 200×110", "rectangle", lambda im, cx, cy: cv2.rectangle(im, (cx - 100, cy - 55), (cx + 100, cy + 55), 0, -1)),
        ("正五边形", "pentagon", lambda im, cx, cy: cv2.fillPoly(im, [poly(5, 95, cx, cy)], 0)),
        ("圆", "circle", lambda im, cx, cy: cv2.circle(im, (cx, cy), 90, 0, -1)),
        ("局限：正六边形", "hexagon", lambda im, cx, cy: cv2.fillPoly(im, [poly(6, 95, cx, cy, 0)], 0)),
        ("局限：长方形转 30°", "rectangle", lambda im, cx, cy: cv2.fillPoly(im, [rect_pts(cx, cy, 180, 100, 30)], 0)),
        ("局限：长方形转 45°", "rectangle", lambda im, cx, cy: cv2.fillPoly(im, [rect_pts(cx, cy, 170, 110, 45)], 0)),
    ]
    G = 260
    img = np.full((2 * G, 4 * G), 255, np.uint8)
    for i, (_, _, fn) in enumerate(cases):
        fn(img, (i % 4) * G + G // 2, (i // 4) * G + G // 2)
    # 按脚本流程：二值化（白底黑图 → INV + OTSU）→ EXTERNAL → 面积过滤 → 判断
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cnts, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = [c for c in cnts if cv2.contourArea(c) >= 500]
    assert len(cnts) == len(cases)
    found = {}
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        k = (y + h // 2) // G * 4 + (x + w // 2) // G
        found[k] = classify(c)
    out = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    rows = []
    for i, (name, exp, _) in enumerate(cases):
        n, got, ratio, approx = found[i]
        cv2.polylines(out, [approx], True, (40, 40, 220), 3, cv2.LINE_AA)
        for p in approx.reshape(-1, 2):
            cv2.circle(out, tuple(int(v) for v in p), 6, (60, 170, 60), -1, cv2.LINE_AA)
        rows.append((name, exp, n, ratio, got))
        print(f"    {name}: n={n}, w/h={ratio:.2f} → {got}")
    # 前 5 个标准示例应全部正确；局限示例如实记录
    assert [r[4] for r in rows[:5]] == ["triangle", "square", "rectangle", "pentagon", "circle"]
    assert rows[5][4] == "circle" and rows[7][4] == "square"   # 局限示例的实测结果
    tiles = []
    for i, (name, exp, n, ratio, got) in enumerate(rows):
        x0, y0 = (i % 4) * G, (i // 4) * G
        t = out[y0:y0 + G, x0:x0 + G].copy()
        ok = (got == exp)
        colr = GREEN if ok else RED
        t = caption_below(border(t), f"{name}", 20)
        info = canvas(t.shape[1], 96)
        info = text(info, f"n = {n}，w/h = {ratio:.2f}", (t.shape[1] // 2, 16), 18, GRAY, anchor="mm")
        info = text(info, f"→ {got}", (t.shape[1] // 2, 46), 22, colr, anchor="mm")
        if not ok:
            info = text(info, f"实际是 {exp}：误判", (t.shape[1] // 2, 78), 18, RED, anchor="mm")
        elif i == 6:
            info = text(info, "判对属巧合：w/h 不在 0.95–1.05", (t.shape[1] // 2, 78), 18, GRAY, anchor="mm")
        tiles.append(np.vstack([t, info]))
    body = col([row(tiles[:4], gap=20), row(tiles[4:], gap=20)], gap=16)
    head = canvas(body.shape[1], 150)
    head = text(head, "30-P5 核对附件：按第 30 讲流程实测", (10, 28), 24, INK, anchor="lm")
    head = text(head, "二值化 INV+OTSU → EXTERNAL → 面积 ≥ 500 → approxPolyDP(0.02 × 周长) → 判断", (10, 64), 20, INK, anchor="lm")
    head = text(head, "红线 = 近似多边形，绿点 = 顶点。前 5 个是标准示例；后 3 个展示简化规则的局限（如实记录实际判断）。", (10, 98), 18, GRAY, anchor="lm")
    head = text(head, "合成输入：白底黑色图形，不是 [PI] shapes.png", (10, 130), 18, GRAY, anchor="lm")
    save(stamp(col([head, body], gap=0), "核对附件 · 不进课件 · 合成形状"), L, "30-p5-ref-形状判断规则实测_核对附件.png")
    return rows


if __name__ == "__main__":
    print("[30] 形状识别 · P5")
    classroom()
    attachment()
