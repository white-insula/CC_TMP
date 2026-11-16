# -*- coding: utf-8 -*-
# 第 33 讲 P7 录屏【按当前脚本展示代码】：get_shape → 画框标注“颜色 形状” → 计数 → print(count)
# 注意：当前代码 4 个顶点一律返回 rectangle，正方形也会标成 rectangle（与 30 讲规则不同，见 review）
# 用法：python p7_label_count_current.py [--input 图片]
import argparse
import cv2
from core import load, sort_parts, get_shape_current

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="parts_synthetic.png")
args = ap.parse_args()

out, count, items, _ = sort_parts(load(args.input), get_shape_current)
print(count)
cv2.imshow("out (current code)", out)
cv2.waitKey(0)
cv2.destroyAllWindows()
