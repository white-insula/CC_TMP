# -*- coding: utf-8 -*-
# 第 29 讲 P7 录屏：红色 mask（第 27 讲方法）→ findContours → 面积过滤 → 画框并写 red 和面积
# 预期：每个红色物体一个框，框上写 red 面积；越大的物体面积数字越大
# 用法：python p7_red_boxes.py [--input 彩色积木照片.jpg]
import argparse
import cv2
from core import load, red_mask

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="blocks_synthetic.png")
args = ap.parse_args()

img = load(args.input)
mask = red_mask(img)
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
out = img.copy()
for c in contours:
    area = cv2.contourArea(c)
    if area < 500: continue
    x, y, w, h = cv2.boundingRect(c)
    cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(out, f"red {int(area)}", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
cv2.imshow("mask", mask); cv2.imshow("out", out)
cv2.waitKey(0)
cv2.destroyAllWindows()
