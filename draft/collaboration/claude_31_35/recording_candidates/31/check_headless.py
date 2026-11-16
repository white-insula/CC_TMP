# -*- coding: utf-8 -*-
"""第 31 讲无界面核对：裁模板、单目标匹配、三个阈值的候选框数，保存结果图，不打开窗口。
用法：python check_headless.py [--input 大图] [--crop x y w h] [--outdir 输出目录]
"""
import argparse
import os
import cv2
import numpy as np
from core import load, match, where_boxes, DEFAULT_CROP
from ext_dedupe import dedupe

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="pcb_synthetic.png")
ap.add_argument("--crop", type=int, nargs=4, default=DEFAULT_CROP)
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
synthetic = os.path.basename(args.input) == "pcb_synthetic.png"

img = load(args.input)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
x, y, w, h = args.crop
tpl = cv2.cvtColor(img[y:y + h, x:x + w], cv2.COLOR_BGR2GRAY)
res, max_val, max_loc = match(gray, tpl)
th, tw = tpl.shape
print(f"P6 大图 {gray.shape[::-1]}，模板 {tw}×{th}（方差 {tpl.var():.1f}），分数图 {res.shape[::-1]}")
print(f"P6 max_val = {max_val:.4f}，max_loc = {max_loc}")
out = img.copy(); cv2.rectangle(out, max_loc, (max_loc[0] + tw, max_loc[1] + th), (0, 0, 255), 2)
cv2.imwrite(os.path.join(args.outdir, "31_p6_match.png"), out)
assert res.shape == (gray.shape[0] - th + 1, gray.shape[1] - tw + 1)
if synthetic:
    assert max_loc == (x, y)

chips = [(60, 60), (270, 60), (480, 60), (60, 260), (270, 260), (480, 260)] if synthetic else []
for t in (0.8, 0.5, 0.95):
    boxes = where_boxes(res, t)
    v = img.copy()
    for bx, by in boxes:
        cv2.rectangle(v, (int(bx), int(by)), (int(bx) + tw, int(by) + th), (0, 255, 0), 1)
    cv2.imwrite(os.path.join(args.outdir, f"31_p7_thr_{t}.png"), v)
    kept = dedupe(res, t, tw, th)
    msg = f"P7 阈值 {t}：np.where 候选框 {len(boxes)} 个；扩展去重后 {len(kept)} 个"
    if synthetic:
        hit = sum(1 for cx, cy in chips if any(abs(bx - (cx - 4)) <= 12 and abs(by - (cy - 10)) <= 12 for bx, by in boxes))
        wrong = [k for k in kept if not any(abs(k[0] - (cx - 4)) <= 12 and abs(k[1] - (cy - 10)) <= 12 for cx, cy in chips)]
        msg += f"；6 个芯片中被框到 {hit} 个；去重后不在芯片上的框 {len(wrong)} 个"
    print(msg)
print("P7 说明：候选框数 ≠ 目标数，同一芯片附近有多个高分位置")
for name, im in (("原图", gray), ("放大1.5倍", cv2.resize(gray, None, fx=1.5, fy=1.5)),
                 ("旋转25度", cv2.warpAffine(gray, cv2.getRotationMatrix2D((gray.shape[1] / 2, gray.shape[0] / 2), 25, 1.0), gray.shape[::-1]))):
    print(f"P8 本样本 {name}：max_val = {cv2.matchTemplate(im, tpl, cv2.TM_CCOEFF_NORMED).max():.4f}")
print("OK 31")
