# -*- coding: utf-8 -*-
# 第 30 讲 P6 录屏：二值化 → 找轮廓 → 面积过滤 → approxPolyDP(0.02 × 周长) → 按角点数判断 → 红线画近似多边形并写名称
# 用法：python p6_shapes.py [--input shapes.png]    （默认合成形状图；课程素材为 [PI]EXP-OpenCV-shape/shapes.png）
import argparse
import cv2
from core import load, contours_of_shapes

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="shapes_synthetic.png")
args = ap.parse_args()

img = load(args.input)
out = img.copy()
for c in contours_of_shapes(img):
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    n = len(approx); x, y, w, h = cv2.boundingRect(approx)
    if n == 3: name = "triangle"
    elif n == 4: name = "square" if 0.95 <= w / h <= 1.05 else "rectangle"
    elif n == 5: name = "pentagon"
    elif n >= 6: name = "circle"
    else: name = "unknown"
    cv2.polylines(out, [approx], True, (0, 0, 255), 2)
    cv2.putText(out, name, (x, y + h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 160, 255), 2)
    print(n, name)
cv2.imshow("out", out)
cv2.waitKey(0)
cv2.destroyAllWindows()
