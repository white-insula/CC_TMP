# -*- coding: utf-8 -*-
"""生成第 26—30 讲录屏候选程序的合成输入（文件名一律带 synthetic）。

这些图只用于在没有真实素材时跑通程序、自动核对数值；不是 shapes.png、积木照片、垫片照片等真实素材，
也不冒充 cat.jpg / fruit.jpg。真实图片用各程序的 --input 参数指定。
用法：python make_synthetic_inputs.py        （在本目录运行，输出写到 26/ … 30/）
兼容 OpenCV 4.11 与 NumPy 1.x。
"""
import os
import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# 颜色均为 BGR；括号内为 cv2.COLOR_BGR2HSV 实测的 H
RED_179 = (5, 0, 250)       # H 179：红色在色轮末端
RED_4 = (0, 30, 230)        # H 4：偏橙的红
RED_176 = (40, 10, 220)     # H 176：偏紫的红
GREEN_56 = (40, 180, 60)    # H 56
GREEN_66 = (60, 170, 30)    # H 66
YELLOW_25 = (30, 200, 230)  # H 25
BLUE_104 = (200, 120, 30)   # H 104
TABLE = (150, 150, 145)     # S 8：灰色桌面


def save(lesson, name, img):
    d = os.path.join(HERE, lesson)
    os.makedirs(d, exist_ok=True)
    cv2.imwrite(os.path.join(d, name), img)
    print("  ", lesson + "/" + name, img.shape)


def hsv_shapes():
    """26 讲：白底彩色图形。红色两种：H 179（点击取值演示）和 H 4。"""
    img = np.full((400, 640, 3), 255, np.uint8)
    cv2.circle(img, (110, 120), 70, RED_179, -1)
    cv2.rectangle(img, (230, 50), (370, 190), RED_4, -1)
    cv2.circle(img, (520, 120), 70, YELLOW_25, -1)
    cv2.rectangle(img, (40, 240), (200, 360), GREEN_56, -1)
    pts = np.array([[320, 230], [400, 370], [240, 370]], np.int32)
    cv2.fillPoly(img, [pts], BLUE_104)
    cv2.circle(img, (530, 300), 70, (120, 120, 120), -1)          # 灰色：S≈0，用来说明 H 不可靠
    return img


def blocks():
    """27、29 讲：灰色桌面上的彩色积木（带上下明暗渐变），外加零星偏红小点（背景杂色）。"""
    rng = np.random.RandomState(27)
    img = np.full((500, 800, 3), TABLE, np.uint8)

    def block(x, y, w, h, color, outline=True):
        for i in range(h):                                      # 上亮下暗，模拟光照
            k = 1.0 - 0.25 * i / h
            img[y + i, x:x + w] = np.clip(np.array(color) * k, 0, 255).astype(np.uint8)
        if outline:
            cv2.rectangle(img, (x, y), (x + w - 1, y + h - 1), (60, 60, 60), 2)

    block(60, 60, 140, 100, GREEN_56)
    block(260, 60, 100, 140, GREEN_66)
    block(430, 60, 150, 110, YELLOW_25)
    block(620, 60, 120, 120, BLUE_104)
    block(60, 260, 160, 120, RED_4)                              # 只在 0—10 段
    block(280, 260, 120, 160, RED_176)                           # 只在 170—179 段
    # 一块“边缘发紫”的红积木：中间 H 4，四周一圈 H 176
    block(470, 250, 220, 170, RED_176)
    block(500, 280, 160, 110, RED_4, outline=False)              # 内部无描边，与外圈连成一块
    for _ in range(25):                                          # 背景偏红杂点（2×2），开运算应去掉
        x, y = rng.randint(10, 790), rng.randint(440, 495)
        img[y:y + 2, x:x + 2] = RED_176
    for _ in range(15):
        x, y = rng.randint(10, 790), rng.randint(200, 240)
        img[y:y + 2, x:x + 2] = RED_4
    return img


def shapes(dust=False):
    """28—30 讲：白底黑色图形（三角形、正方形、长方形、五边形、圆、再一个圆），共 6 个。"""
    img = np.full((420, 760, 3), 255, np.uint8)
    cv2.fillPoly(img, [np.array([[110, 40], [190, 180], [30, 180]], np.int32)], (30, 30, 30))
    cv2.rectangle(img, (250, 50), (380, 180), (30, 30, 30), -1)                # 正方形 131×131
    cv2.rectangle(img, (450, 70), (700, 170), (30, 30, 30), -1)                # 长方形 251×101
    pent = [(110 + 80 * np.cos(np.radians(-90 + 72 * i)), 320 + 80 * np.sin(np.radians(-90 + 72 * i))) for i in range(5)]
    cv2.fillPoly(img, [np.round(pent).astype(np.int32)], (30, 30, 30))
    cv2.circle(img, (330, 320), 80, (30, 30, 30), -1)
    cv2.circle(img, (580, 320), 60, (30, 30, 30), -1)
    if dust:                                                                   # 29 讲：几粒“灰尘”，面积只有十几、几十
        for (x, y, r) in ((230, 240, 2), (420, 30, 3), (720, 250, 4), (460, 390, 2), (30, 400, 3), (690, 30, 4)):
            cv2.circle(img, (x, y), r, (60, 60, 60), -1)
    return img


def washers():
    """28 讲：浅色底上 3 个深色带孔垫片。"""
    img = np.full((360, 640, 3), 245, np.uint8)
    for cx in (130, 320, 510):
        cv2.circle(img, (cx, 180), 80, (40, 40, 40), -1)
        cv2.circle(img, (cx, 180), 32, (245, 245, 245), -1)
    return img


def main():
    save("26", "hsv_shapes_synthetic.png", hsv_shapes())
    save("27", "blocks_synthetic.png", blocks())
    save("28", "shapes_synthetic.png", shapes())
    save("28", "washers_synthetic.png", washers())
    save("29", "shapes_dust_synthetic.png", shapes(dust=True))
    save("29", "blocks_synthetic.png", blocks())
    save("30", "shapes_synthetic.png", shapes())


if __name__ == "__main__":
    main()
