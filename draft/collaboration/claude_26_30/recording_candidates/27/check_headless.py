# -*- coding: utf-8 -*-
"""第 27 讲无界面核对：打印数值、保存 mask / result，不打开窗口。
用法：python check_headless.py [--input 图片] [--outdir 输出目录]
"""
import argparse
import os
import cv2
import numpy as np
from core import load, extract_green, extract_red, GREEN_LO, GREEN_HI

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="blocks_synthetic.png")
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
synthetic = os.path.basename(args.input) == "blocks_synthetic.png"
os.makedirs(args.outdir, exist_ok=True)

# inRange 上下界都包含
edge = np.uint8([[[35, 80, 50], [85, 255, 255], [34, 80, 50], [86, 255, 255]]])
r = cv2.inRange(edge, GREEN_LO, GREEN_HI).ravel().tolist()
print("inRange 边界 (35,80,50) (85,255,255) (34,80,50) (86,255,255) →", r)
assert r == [255, 255, 0, 0]

img = load(args.input)
hsv, gmask, result = extract_green(img)
m1, m2, rmask, opened = extract_red(img)
for name, im in (("p7_mask_green", gmask), ("p7_result_green", result), ("p8_one_band", m1),
                 ("p8_two_bands", rmask), ("p8_opened", opened)):
    cv2.imwrite(os.path.join(args.outdir, f"27_{name}.png"), im)
cv2.imwrite(os.path.join(args.outdir, "27_input.png"), img)
ncc = lambda m: cv2.connectedComponents(m)[0] - 1
print(f"P7 绿色 mask 白色像素 {cv2.countNonZero(gmask)}，连通块 {ncc(gmask)}")
print(f"P8 只用一段 {cv2.countNonZero(m1)}，两段合并 {cv2.countNonZero(rmask)}（连通块 {ncc(rmask)}），开运算后 {cv2.countNonZero(opened)}（连通块 {ncc(opened)}）")
if synthetic:
    assert gmask[110, 130] == 255 and gmask[130, 310] == 255          # 两块绿积木
    assert gmask[110, 500] == 0 and gmask[120, 680] == 0 and gmask[320, 140] == 0   # 黄、蓝、红不进
    assert ncc(gmask) == 2
    assert m1[260 + 5, 470 + 5] == 0 and rmask[260 + 5, 470 + 5] == 255   # 发紫的边缘：一段漏、两段补上
    assert m1[320, 340] == 0 and rmask[320, 340] == 255                 # 偏紫红积木只在 170—179
    assert ncc(rmask) > 3 and ncc(opened) == 3                           # 杂点去掉，剩 3 块红积木
print("OK 27")
