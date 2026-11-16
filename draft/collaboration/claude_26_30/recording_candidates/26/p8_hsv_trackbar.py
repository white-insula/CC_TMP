# -*- coding: utf-8 -*-
# 第 26 讲 P8 录屏：6 个滑动条找颜色范围，inRange 实时预览，按 q 退出并打印范围
# 预期：拖到只剩目标颜色为白，记下 6 个数
# 用法：python p8_hsv_trackbar.py [--input 你的图片.jpg]
import argparse
import cv2
from core import load, to_hsv, TRACKBARS

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="hsv_shapes_synthetic.png")
args = ap.parse_args()

img = load(args.input)
hsv = to_hsv(img)
cv2.namedWindow("mask")
for name, init, mx in TRACKBARS:
    cv2.createTrackbar(name, "mask", init, mx, lambda x: None)
while True:
    h1, s1, v1, h2, s2, v2 = [cv2.getTrackbarPos(n, "mask") for n, _, _ in TRACKBARS]
    mask = cv2.inRange(hsv, (h1, s1, v1), (h2, s2, v2))
    cv2.imshow("mask", mask)
    cv2.imshow("img", img)
    if cv2.waitKey(30) & 0xFF == ord("q"):
        break
print("范围:", (h1, s1, v1), (h2, s2, v2))
cv2.destroyAllWindows()
