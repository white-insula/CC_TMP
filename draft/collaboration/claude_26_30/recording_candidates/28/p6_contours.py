# -*- coding: utf-8 -*-
# 第 28 讲 P6 录屏：灰度 → INV+OTSU 二值化 → findContours(EXTERNAL) → 打印数量 → drawContours
# 预期：轮廓数等于图形个数（合成图为 6）；每个图形描上绿边
# 用法：python p6_contours.py [--input shapes.png]    （默认合成形状图；课程素材为 [PI]EXP-OpenCV-shape/shapes.png）
import argparse
import cv2
from core import load

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="shapes_synthetic.png")
args = ap.parse_args()

img = load(args.input)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print("轮廓数:", len(contours))
out = img.copy(); cv2.drawContours(out, contours, -1, (0, 255, 0), 2)
cv2.imshow("binary", binary); cv2.imshow("out", out)
cv2.waitKey(0)
cv2.destroyAllWindows()
