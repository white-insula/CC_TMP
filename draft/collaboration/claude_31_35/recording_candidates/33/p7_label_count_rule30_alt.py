# -*- coding: utf-8 -*-
# 第 33 讲 P7【独立备选，未采用】：形状判断复用第 30 讲规则（square / rectangle / pentagon / n ≥ 6 circle）
# 只供本机决定是否修改 33 讲时对照；不是当前正式脚本的代码
# 用法：python p7_label_count_rule30_alt.py [--input 图片]
import argparse
import cv2
from core import load, sort_parts, get_shape_rule30

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="parts_synthetic.png")
args = ap.parse_args()

out, count, items, _ = sort_parts(load(args.input), get_shape_rule30)
print(count)
cv2.imshow("out (alt: lesson 30 rule)", out)
cv2.waitKey(0)
cv2.destroyAllWindows()
