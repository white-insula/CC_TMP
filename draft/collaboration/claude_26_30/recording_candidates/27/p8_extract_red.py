# -*- coding: utf-8 -*-
# 第 27 讲 P8 录屏：只用 0—10 一段 → 红色不完整；两段 OR 合并 → 完整；5×5 开运算 → 零星白点消失
# 用法：python p8_extract_red.py [--input 彩色积木照片.jpg]
import argparse
import cv2
import numpy as np
from core import load

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="blocks_synthetic.png")
args = ap.parse_args()

img = load(args.input)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
m1 = cv2.inRange(hsv, (0, 100, 80), (10, 255, 255))
m2 = cv2.inRange(hsv, (170, 100, 80), (179, 255, 255))
mask = cv2.bitwise_or(m1, m2)
opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
print("只用一段:", cv2.countNonZero(m1), " 两段合并:", cv2.countNonZero(mask), " 开运算后:", cv2.countNonZero(opened))
cv2.imshow("one_band", m1); cv2.imshow("two_bands", mask); cv2.imshow("opened", opened)
cv2.waitKey(0)
cv2.destroyAllWindows()
