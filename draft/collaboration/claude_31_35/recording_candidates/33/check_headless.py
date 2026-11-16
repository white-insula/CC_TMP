# -*- coding: utf-8 -*-
"""第 33 讲无界面核对：两套形状判断分别跑，与合成样本真值逐项比对，保存 mask 与标注图。
用法：python check_headless.py [--input 图片] [--outdir 输出目录]
"""
import argparse
import json
import os
import cv2
from core import load, sort_parts, get_shape_current, get_shape_rule30

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="parts_synthetic.png")
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
synthetic = os.path.basename(args.input) == "parts_synthetic.png"
img = load(args.input)

res = {}
for tag, fn in (("current", get_shape_current), ("rule30_alt", get_shape_rule30)):
    out, count, items, masks = sort_parts(img, fn)
    res[tag] = (count, items)
    cv2.imwrite(os.path.join(args.outdir, f"33_p7_{tag}.png"), out)
    print(f"P7 [{tag}] print(count) → {count}")
for name, m in masks.items():
    cv2.imwrite(os.path.join(args.outdir, f"33_p6_mask_{name}.png"), m)
    print(f"P6 mask_{name}：白色像素 {cv2.countNonZero(m)}，面积 ≥ 800 的轮廓 {sum(1 for c in cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0] if cv2.contourArea(c) >= 800)} 个")

if synthetic:
    truth = json.load(open("parts_synthetic_truth.json", encoding="utf-8"))["items"]
    print("真值：红圆 2、蓝方 3、黄三角 1")
    for tag, (count, items) in res.items():
        rows = []
        for t in truth:
            m = min(items, key=lambda it: (it["center"][0] - t["center"][0]) ** 2 + (it["center"][1] - t["center"][1]) ** 2)
            rows.append((t["color"], t["shape"], m["label"], m["n"], m["w_h"]))
        print(f"  [{tag}] 逐项：", rows)
    assert res["current"][0] == {"red circle": 2, "yellow triangle": 1, "blue rectangle": 3}
    assert res["rule30_alt"][0] == {"red circle": 2, "yellow triangle": 1, "blue square": 3}
    print("差异：当前代码把 3 个蓝色正方形标为 'blue rectangle'；30 讲规则备选标为 'blue square'。数量都正确。")
print("OK 33")
