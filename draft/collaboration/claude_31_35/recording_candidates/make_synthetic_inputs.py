# -*- coding: utf-8 -*-
"""生成第 31、33 讲录屏候选的合成教学样本（文件名一律带 synthetic）。

- 31：pcb_synthetic.png —— 带纹理的合成电路板，6 个相同芯片（各自叠加不同噪声和轻微亮度差）、若干电阻和走线。
- 33：parts_synthetic.png —— 灰色底板上分开摆放的红圆 2 个（一个 H≈2、一个 H≈177）、蓝方 3 个、黄三角 1 个，
       另撒少量红色小杂点（应被开运算去掉）。真值写入 parts_synthetic_truth.json。
34、35 讲的合成答题卡由 34/make_synthetic_cards.py 生成。
这些都不是真实电路板照片、积木照片或学生答题卡。兼容 OpenCV 4.11 与 NumPy 1.x。
用法：python make_synthetic_inputs.py
"""
import json
import os
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def save(lesson, name, img):
    d = os.path.join(HERE, lesson)
    os.makedirs(d, exist_ok=True)
    cv2.imwrite(os.path.join(d, name), img)
    print("  ", lesson + "/" + name, img.shape)


def pcb():
    rng = np.random.RandomState(31)
    H, W = 420, 700
    tex = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 8)
    base = 1 + 0.12 * tex / (np.abs(tex).max() + 1e-6)
    img = np.dstack([40 * base, 110 * base, 30 * base])           # 绿色板（BGR）
    for (p, q) in (((0, 200), (700, 200)), ((350, 0), (350, 420)), ((0, 40), (120, 40)), ((560, 380), (700, 380))):
        cv2.line(img, p, q, (60, 150, 50), 3)

    def chip(x, y, k):
        img[y:y + 60, x:x + 90] = (25 + k, 25 + k, 25 + k)
        cv2.circle(img, (x + 13, y + 13), 5, (150, 150, 150), -1)
        cv2.ellipse(img, (x, y + 30), (8, 10), 0, -90, 90, (90, 90, 90), -1)
        img[y + 36:y + 42, x + 26:x + 76] = (130, 130, 130)
        img[y + 16:y + 24, x + 52:x + 64] = (130, 130, 130)
        for dx in (6, 24, 52, 74):
            img[y + 60:y + 68, x + dx:x + dx + 6] = (190, 190, 190)
            img[y - 8:y, x + dx:x + dx + 6] = (190, 190, 190)

    k = 0
    for y in (60, 260):
        for x in (60, 270, 480):
            chip(x, y, [0, 6, 12, 18, 24, 30][k]); k += 1
    for (x, y) in ((200, 170), (420, 150), (610, 360), (150, 360)):
        cv2.rectangle(img, (x, y), (x + 40, y + 16), (90, 160, 210), -1)
    img = img + rng.normal(0, 8, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8)


def parts():
    rng = np.random.RandomState(33)
    img = np.full((480, 800, 3), (150, 150, 145), np.uint8)       # 灰色底板（S 很低）
    truth = []
    for (cx, cy, colr) in ((130, 120, (0, 30, 230)), (420, 360, (40, 10, 220))):        # H 4 与 H 176
        cv2.circle(img, (cx, cy), 60, colr, -1); truth.append({"color": "red", "shape": "circle", "center": [cx, cy]})
    for (x, y) in ((260, 70), (560, 60), (620, 300)):
        cv2.rectangle(img, (x, y), (x + 110, y + 110), (200, 120, 30), -1)               # 蓝 H 104，正方形 111×111
        truth.append({"color": "blue", "shape": "square", "center": [x + 55, y + 55]})
    tri = np.array([[150, 290], [240, 440], [60, 440]], np.int32)
    cv2.fillPoly(img, [tri], (30, 200, 230))                                             # 黄 H 25
    truth.append({"color": "yellow", "shape": "triangle", "center": [150, 390]})
    for _ in range(20):                                                                  # 红色小杂点 2×2
        x, y = rng.randint(10, 790), rng.randint(250, 290)
        img[y:y + 2, x:x + 2] = (40, 10, 220)
    img = np.clip(img.astype(np.int16) + rng.randint(-4, 5, img.shape), 0, 255).astype(np.uint8)
    return img, truth


def main():
    save("31", "pcb_synthetic.png", pcb())
    im, truth = parts()
    save("33", "parts_synthetic.png", im)
    with open(os.path.join(HERE, "33", "parts_synthetic_truth.json"), "w", encoding="utf-8") as f:
        json.dump({"说明": "合成教学样本真值：红圆 2、蓝方 3、黄三角 1", "items": truth}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
