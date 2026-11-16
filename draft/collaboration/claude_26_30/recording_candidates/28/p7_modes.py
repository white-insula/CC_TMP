# -*- coding: utf-8 -*-
# 第 28 讲 P7 录屏：垫片图 EXTERNAL 与 TREE 数量对比 → for 循环逐个画轮廓并编号
# 预期（合成垫片图）：EXTERNAL 3 个，TREE 6 个（中间的孔也算）；每个垫片标 1、2、3
# 用法：python p7_modes.py [--input 垫片照片.jpg]
import argparse
import cv2
from core import load, binarize

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="washers_synthetic.png")
args = ap.parse_args()

img = load(args.input)
binary = binarize(img)                                    # 灰度 + INV + OTSU，同 P6
ext, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
tree, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print("EXTERNAL:", len(ext), " TREE:", len(tree))
out = img.copy()
for i, c in enumerate(ext):
    cv2.drawContours(out, [c], -1, (0, 0, 255), 2)
    x, y = c[0][0]
    cv2.putText(out, str(i + 1), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
cv2.imshow("binary", binary); cv2.imshow("out", out)
cv2.waitKey(0)
cv2.destroyAllWindows()
