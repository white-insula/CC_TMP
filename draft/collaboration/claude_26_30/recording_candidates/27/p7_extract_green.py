# -*- coding: utf-8 -*-
# 第 27 讲 P7 录屏：提取绿色 → 显示原图 / mask / result
# 预期：mask 里绿色积木变白，其他全黑；result 里只剩绿色积木
# 用法：python p7_extract_green.py [--input 彩色积木照片.jpg]   （默认合成积木图，不是实拍）
import argparse
import cv2
from core import load, GREEN_LO, GREEN_HI

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="blocks_synthetic.png")
args = ap.parse_args()

img = load(args.input)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, GREEN_LO, GREEN_HI)          # (35, 80, 50) — (85, 255, 255)
result = cv2.bitwise_and(img, img, mask=mask)
cv2.imshow("img", img); cv2.imshow("mask", mask); cv2.imshow("result", result)
cv2.waitKey(0)
cv2.destroyAllWindows()
