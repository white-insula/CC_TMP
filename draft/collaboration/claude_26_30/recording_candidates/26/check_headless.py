# -*- coding: utf-8 -*-
"""第 26 讲无界面核对：不打开窗口，打印数值并保存结果图。
用固定坐标代替鼠标点击、用固定范围代替拖动滑动条；这只是核对逻辑，不等于录屏。
用法：python check_headless.py [--input 图片] [--outdir 输出目录]
"""
import argparse
import os
import cv2
import numpy as np
from core import load, to_hsv, pure_colors, range_mask, TRACKBARS

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="hsv_shapes_synthetic.png")
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
synthetic = os.path.basename(args.input) == "hsv_shapes_synthetic.png"
os.makedirs(args.outdir, exist_ok=True)

# P7：纯色
vals = {name: v.ravel().tolist() for name, v in pure_colors()}
for name, v in pure_colors():
    print("P7 纯色", name, v.tolist())
assert vals == {"red": [0, 255, 255], "green": [60, 255, 255], "blue": [120, 255, 255]}

img = load(args.input)
hsv = to_hsv(img)
# P7：模拟点击（合成图各图形中心）
points = {"红圆(H179)": (110, 120), "红方(H4)": (300, 120), "黄圆": (520, 120), "绿方": (120, 300),
          "蓝三角": (320, 330), "灰圆": (530, 300)} if synthetic else {"中心": (img.shape[1] // 2, img.shape[0] // 2)}
got = {}
for name, (x, y) in points.items():
    got[name] = hsv[y, x].tolist()
    print(f"P7 点击 {name} (x={x}, y={y}) → hsv[y, x] = {got[name]}")
if synthetic:
    assert got["红圆(H179)"][0] == 179 and got["红方(H4)"][0] == 4
    assert got["绿方"][0] == 56 and got["蓝三角"][0] == 104 and got["灰圆"][1] == 0

# P8：滑动条初值及两组示例范围（代替拖动）
init = [v for _, v, _ in TRACKBARS]
cases = {"trackbar_init": init, "red_high_170_179": [170, 100, 80, 179, 255, 255], "red_low_0_10": [0, 100, 80, 10, 255, 255]}
for name, r in cases.items():
    m = range_mask(hsv, *r)
    cv2.imwrite(os.path.join(args.outdir, f"26_p8_mask_{name}.png"), m)
    print(f"P8 范围 {name} {tuple(r[:3])}—{tuple(r[3:])}：白色像素 {cv2.countNonZero(m)}")
    if synthetic and name.startswith("red"):
        x, y = (110, 120) if "high" in name else (300, 120)
        assert m[y, x] == 255
# inRange 上下界均包含
p = np.uint8([[[179, 100, 80]]])
assert range_mask(p, 170, 100, 80, 179, 255, 255)[0, 0] == 255
print("P8 inRange 边界：(179,100,80) 落在 (170,100,80)—(179,255,255) 内 → 255（上下界都包含）")
cv2.imwrite(os.path.join(args.outdir, "26_input.png"), img)
print("OK 26")
