# -*- coding: utf-8 -*-
"""第 21 节配图:全部用 OpenCV 真实处理生成(效果图即实际运行结果)。
用法:python visuals.py   → img/*.png
"""
import os
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "img")
CARD = r"E:\下载\Group A （最终版）\Group A （最终版）\代码集\Answer Card Recognition\答题卡扫描文件\212001.jpg"
GAP = 24                     # 拼图间距
BG = (255, 255, 255)


def save(name, img):
    os.makedirs(OUT, exist_ok=True)
    cv2.imencode(".png", img)[1].tofile(os.path.join(OUT, name))
    print("  img/" + name, img.shape[1], "x", img.shape[0])


def bgr(g):
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR) if g.ndim == 2 else g


def row(imgs, gap=GAP):
    h = max(i.shape[0] for i in imgs)
    parts = []
    for k, i in enumerate(imgs):
        i = bgr(i)
        if i.shape[0] < h:
            i = cv2.copyMakeBorder(i, 0, h - i.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=BG)
        parts.append(i)
        if k < len(imgs) - 1:
            parts.append(np.full((h, gap, 3), 255, np.uint8))
    return np.hstack(parts)


def grid(imgs, cols, gap=GAP):
    rows = [row(imgs[i:i + cols], gap) for i in range(0, len(imgs), cols)]
    w = max(r.shape[1] for r in rows)
    out = []
    for k, r in enumerate(rows):
        out.append(cv2.copyMakeBorder(r, 0, 0, 0, w - r.shape[1], cv2.BORDER_CONSTANT, value=BG))
        if k < len(rows) - 1:
            out.append(np.full((gap, w, 3), 255, np.uint8))
    return np.vstack(out)


def frame(img, color=(200, 200, 200)):
    return cv2.copyMakeBorder(bgr(img), 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=color)


# ---------- 合成「白纸黑字」照片 ----------
def paper(shadow=False, w=900, h=420, seed=7):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # 纸面:中间亮四周略暗,带少量纸纹
    base = 200 - 26 * (((xx - w * 0.55) / w) ** 2 + ((yy - h * 0.45) / h) ** 2) * 4
    base += cv2.GaussianBlur(rng.normal(0, 3, (h, w)).astype(np.float32), (5, 5), 0)   # 手机照片噪声已被平滑
    ink = np.zeros((h, w), np.uint8)
    lines = ["Machine Vision", "threshold = 127", "Otsu  2026"]
    for k, t in enumerate(lines):
        cv2.putText(ink, t, (50, 120 + k * 120), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                    2.6 if k == 0 else 2.2, 255, 5, cv2.LINE_AA)
    ink = cv2.GaussianBlur(ink, (5, 5), 0).astype(np.float32) / 255
    img = base * (1 - ink * 0.58)              # 字迹灰度约 80–100,边缘渐变
    # 一道浅阴影(折痕)让高阈值时混进背景
    img -= 22 * np.exp(-((xx - w * 0.78) ** 2) / (2 * 40 ** 2))
    if shadow:                                  # 左半边罩上深阴影(台灯斜照)
        m = 1 / (1 + np.exp((xx - w * 0.45) / 30))
        img = img * (1 - 0.62 * m)
    return np.clip(img, 0, 255).astype(np.uint8)


def gradient():
    w, h = 1024, 90
    g = np.tile(np.linspace(0, 255, w).astype(np.uint8), (h, 1))
    _, b = cv2.threshold(g, 127, 255, cv2.THRESH_BINARY)
    gap = np.full((40, w), 255, np.uint8)
    img = bgr(np.vstack([g, gap, b]))
    x = int(127 / 255 * (w - 1))
    cv2.line(img, (x, 0), (x, img.shape[0] - 1), (0, 169, 242), 4)   # 琥珀色阈值线(BGR)
    return cv2.copyMakeBorder(img, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(180, 180, 180))


def card():
    im = cv2.imdecode(np.fromfile(CARD, np.uint8), cv2.IMREAD_COLOR)
    h, w = im.shape[:2]
    roi = im[int(h * 0.591):int(h * 0.722), int(w * 0.05):int(w * 0.47)]   # 只取答题区,避开姓名栏
    roi = cv2.resize(roi, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    _, inv = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # 在二值图上框出“被涂黑的格子”:白色成块、面积较大的区域
    k = cv2.morphologyEx(inv, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    cnts, _ = cv2.findContours(k, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    marked = bgr(inv).copy()
    n = 0
    for c in cnts:
        x, y, bw, bh = cv2.boundingRect(c)
        if bw * bh > 250 and 0.8 < bw / bh < 4:
            cv2.rectangle(marked, (x - 4, y - 4), (x + bw + 4, y + bh + 4), (60, 180, 75), 3)
            n += 1
    print("  涂黑格子框出:", n)
    return roi, inv, marked


def main():
    save("21_gradient.png", gradient())

    roi, inv, marked = card()
    save("21_card_pair.png", row([frame(roi), frame(inv)]))
    save("21_card_marked.png", row([frame(roi), frame(marked)]))

    p = paper()
    t = {}
    for v in (80, 127, 180):
        _, t[v] = cv2.threshold(p, v, 255, cv2.THRESH_BINARY)
    ret, otsu = cv2.threshold(p, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, inv127 = cv2.threshold(p, 127, 255, cv2.THRESH_BINARY_INV)
    print("  Otsu 阈值(无阴影):", ret)
    save("21_paper.png", frame(p))
    save("21_binary_inv.png", grid([frame(t[127]), frame(inv127)], 1))
    save("21_fixed_vs_otsu.png", grid([frame(p), frame(t[80]), frame(t[180]), frame(otsu)], 2))

    s = paper(shadow=True)
    ret2, so = cv2.threshold(s, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ad = cv2.adaptiveThreshold(s, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    print("  Otsu 阈值(半边阴影):", ret2)
    save("21_adaptive.png", row([frame(s), frame(so), frame(ad)]))
    return {"otsu": ret, "otsu_shadow": ret2}


if __name__ == "__main__":
    main()
