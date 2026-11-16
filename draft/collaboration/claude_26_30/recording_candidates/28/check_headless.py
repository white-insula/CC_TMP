# -*- coding: utf-8 -*-
"""第 28 讲无界面核对：打印轮廓数量与层级，保存结果图，不打开窗口。
用法：python check_headless.py [--shapes 图片] [--washers 图片] [--outdir 输出目录]
"""
import argparse
import os
import cv2
from core import load, binarize, draw_numbered

ap = argparse.ArgumentParser()
ap.add_argument("--shapes", default="shapes_synthetic.png")
ap.add_argument("--washers", default="washers_synthetic.png")
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)

img = load(args.shapes)
binary = binarize(img)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
out = img.copy(); cv2.drawContours(out, contours, -1, (0, 255, 0), 2)
print("P6 轮廓数:", len(contours), " 二值图白色占比 %.3f（白色应为图形）" % (cv2.countNonZero(binary) / binary.size))
cv2.imwrite(os.path.join(args.outdir, "28_p6_binary.png"), binary)
cv2.imwrite(os.path.join(args.outdir, "28_p6_out.png"), out)
if os.path.basename(args.shapes) == "shapes_synthetic.png":
    assert len(contours) == 6

w = load(args.washers)
b2 = binarize(w)
ext, _ = cv2.findContours(b2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
tree, hier = cv2.findContours(b2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print("P7 EXTERNAL:", len(ext), " TREE:", len(tree))
print("P7 TREE 层级 [next, prev, first_child, parent]:", hier[0].tolist())
holes = sum(1 for h in hier[0] if h[3] != -1)
print("P7 有父轮廓（孔）的数量:", holes)
cv2.imwrite(os.path.join(args.outdir, "28_p7_binary.png"), b2)
cv2.imwrite(os.path.join(args.outdir, "28_p7_numbered.png"), draw_numbered(w, ext))
if os.path.basename(args.washers) == "washers_synthetic.png":
    assert (len(ext), len(tree), holes) == (3, 6, 3)
print("OK 28")
