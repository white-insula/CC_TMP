# -*- coding: utf-8 -*-
# 第 34 讲 P6 录屏：读答题卡 → 127 反向二值化 → 找轮廓 → 宽高比 + 面积筛定位块（画红框）→ 排序取四角 → 透视拉正 600×800
# 用法：python p6_locate.py [--input 答题卡.jpg]       （默认是合成教学样本 card_synthetic_01.jpg，不是学生答题卡）
import argparse
import cv2
from card_lib import imread, locate

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="card_synthetic_01.jpg")
args = ap.parse_args()

img = imread(args.input)
card, marks = locate(img)
show = img.copy()
for x, y, w, h in marks:
    cv2.rectangle(show, (x, y), (x + w, y + h), (0, 0, 255), 2)
print("定位块:", marks)
cv2.imshow("marks", cv2.resize(show, None, fx=0.6, fy=0.6))
if card is None:
    print(f"定位失败：找到 {len(marks)} 个，必须恰好 4 个")
else:
    cv2.imshow("card", card)
cv2.waitKey(0)
cv2.destroyAllWindows()
