# -*- coding: utf-8 -*-
# 第 29 讲 P6 录屏：打印面积、周长 → 面积 < 500 跳过 → boundingRect 画绿框 → 外接框中心画红点
# 预期：打印里有几个面积只有十几、几十的（灰尘噪点），画框时被跳过
# 用法：python p6_features.py [--input 带灰尘的形状图.png]
import argparse
import cv2
from core import load, contours_of_shapes

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="shapes_dust_synthetic.png")
args = ap.parse_args()

img = load(args.input)
contours = contours_of_shapes(img)
out = img.copy()
for c in contours:
    area = cv2.contourArea(c); peri = cv2.arcLength(c, True)
    print(area, peri)
    if area < 500: continue
    x, y, w, h = cv2.boundingRect(c)
    cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cx, cy = x + w // 2, y + h // 2
    cv2.circle(out, (cx, cy), 5, (0, 0, 255), -1)
cv2.imshow("out", out)
cv2.waitKey(0)
cv2.destroyAllWindows()
