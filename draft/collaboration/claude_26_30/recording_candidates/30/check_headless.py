# -*- coding: utf-8 -*-
"""第 30 讲无界面核对：三个误差系数分别判断并保存结果图，不打开窗口。
用法：python check_headless.py [--input 图片] [--outdir 输出目录]
"""
import argparse
import os
import cv2
from core import load, label_all

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="shapes_synthetic.png")
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)

img = load(args.input)
res = {}
for eps in (0.02, 0.08, 0.005):
    out, names = label_all(img, eps)
    res[eps] = names
    print(f"eps = {eps}: (名称, 角点数) =", names)
    cv2.imwrite(os.path.join(args.outdir, f"30_eps_{eps}.png"), out)
if os.path.basename(args.input) == "shapes_synthetic.png":
    # 合成图顺序：上排 三角形、正方形、长方形；下排 五边形、大圆、小圆
    assert [n for n, _ in res[0.02]] == ["triangle", "square", "rectangle", "pentagon", "circle", "circle"]
    print("0.02：全部判对")
    print("0.08 与 0.02 不同的位置:", [(i, a[0], b[0]) for i, (a, b) in enumerate(zip(res[0.02], res[0.08])) if a[0] != b[0]])
    print("0.005 与 0.02 不同的位置:", [(i, a[0], b[0]) for i, (a, b) in enumerate(zip(res[0.02], res[0.005])) if a[0] != b[0]])
print("OK 30")
