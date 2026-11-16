# -*- coding: utf-8 -*-
# 第 26 讲 P7 录屏：转换到 HSV → 打印纯红/纯绿/纯蓝的 HSV → 鼠标点击打印 hsv[y, x]
# 预期：打印 [[[0 255 255]]] [[[60 255 255]]] [[[120 255 255]]]；点红色图形，H 可能是 179（红色跨两端）
# 用法：python p7_hsv_click.py [--input 你的图片.jpg]     （默认使用合成图，不是课程原图）
import argparse
import cv2
from core import load, pure_colors

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="hsv_shapes_synthetic.png")
args = ap.parse_args()

img = load(args.input)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
for name, v in pure_colors():
    print(name, v)


def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print((x, y), hsv[y, x])


cv2.imshow("img", img)
cv2.setMouseCallback("img", on_click)
cv2.waitKey(0)
cv2.destroyAllWindows()
