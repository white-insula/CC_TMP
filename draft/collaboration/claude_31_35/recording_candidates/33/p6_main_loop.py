# -*- coding: utf-8 -*-
# 第 33 讲 P6 录屏：颜色字典 → 遍历 → 多段掩膜合并 → 开运算 → 找轮廓 → 面积过滤；逐个颜色显示 mask 检查
# 用法：python p6_main_loop.py [--input 积木工件照片.jpg]    （默认合成教学样本）
import argparse
import cv2
import numpy as np
from core import load, colors, kernel

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="parts_synthetic.png")
args = ap.parse_args()

img = load(args.input)
hsv = cv2.cvtColor(cv2.GaussianBlur(img, (5, 5), 0), cv2.COLOR_BGR2HSV)
for name, ranges in colors.items():
    mask = np.zeros(hsv.shape[:2], np.uint8)
    for lo, hi in ranges:
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lo, hi))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    big = [c for c in contours if cv2.contourArea(c) >= 800]
    print(name, "轮廓", len(contours), "个，面积 ≥ 800 的", len(big), "个")
    cv2.imshow(f"mask_{name}", mask)
cv2.waitKey(0)
cv2.destroyAllWindows()
