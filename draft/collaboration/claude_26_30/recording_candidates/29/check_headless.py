# -*- coding: utf-8 -*-
"""第 29 讲无界面核对：打印面积、周长、外接框与中心，保存结果图，不打开窗口。
用法：python check_headless.py [--shapes 图片] [--blocks 图片] [--outdir 输出目录]
"""
import argparse
import os
import cv2
from core import load, contours_of_shapes, red_mask, MIN_AREA

ap = argparse.ArgumentParser()
ap.add_argument("--shapes", default="shapes_dust_synthetic.png")
ap.add_argument("--blocks", default="blocks_synthetic.png")
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)

img = load(args.shapes)
out = img.copy()
kept, skipped = [], []
for c in contours_of_shapes(img):
    area = cv2.contourArea(c); peri = cv2.arcLength(c, True)
    if area < MIN_AREA:
        skipped.append(round(area, 1)); continue
    x, y, w, h = cv2.boundingRect(c)
    cx, cy = x + w // 2, y + h // 2
    m = cv2.moments(c)
    mx, my = m["m10"] / m["m00"], m["m01"] / m["m00"]
    kept.append((round(area, 1), round(peri, 1), (x, y, w, h), (cx, cy)))
    print(f"P6 面积 {area:.1f}  周长 {peri:.1f}  框 {(x, y, w, h)}  外接框中心 {(cx, cy)}  （对照：矩质心 ({mx:.1f}, {my:.1f})）")
    cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.circle(out, (cx, cy), 5, (0, 0, 255), -1)
print("P6 被面积过滤跳过的轮廓面积:", skipped)
cv2.imwrite(os.path.join(args.outdir, "29_p6_out.png"), out)
if os.path.basename(args.shapes) == "shapes_dust_synthetic.png":
    assert len(kept) == 6 and len(skipped) == 6 and max(skipped) < 100

b = load(args.blocks)
mask = red_mask(b)
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
out2 = b.copy(); boxes = []
for c in contours:
    area = cv2.contourArea(c)
    if area < MIN_AREA: continue
    x, y, w, h = cv2.boundingRect(c)
    boxes.append((int(area), (x, y, w, h)))
    cv2.rectangle(out2, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(out2, f"red {int(area)}", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
print("P7 红色物体（面积, 外接框）:", sorted(boxes))
cv2.imwrite(os.path.join(args.outdir, "29_p7_mask.png"), mask)
cv2.imwrite(os.path.join(args.outdir, "29_p7_out.png"), out2)
if os.path.basename(args.blocks) == "blocks_synthetic.png":
    assert len(boxes) == 3
print("OK 29")
