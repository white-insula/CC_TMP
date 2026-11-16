# -*- coding: utf-8 -*-
# 第 31 讲 P7 录屏：np.where(res >= 阈值) → 循环画框；阈值 0.8 → 改 0.5 / 0.95 对比
# 注意：每个超过阈值的位置都会画一个框，同一目标上会有好几个重叠框（脚本原写法，未去重）
# 用法：python p7_match_many.py [--input 大图] [--template 模板] [--thr 0.8 0.5 0.95]
import argparse
import cv2
import numpy as np
from core import load

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="pcb_synthetic.png")
ap.add_argument("--template", default="template_synthetic.png", help="先运行 p6_match_one.py 生成")
ap.add_argument("--thr", type=float, nargs="+", default=[0.8, 0.5, 0.95])
args = ap.parse_args()

img0 = load(args.input)
gray = cv2.cvtColor(img0, cv2.COLOR_BGR2GRAY)
tpl = cv2.imread(args.template, 0); th, tw = tpl.shape
res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
for t in args.thr:
    img = img0.copy()
    ys, xs = np.where(res >= t)
    for x, y in zip(xs, ys):
        cv2.rectangle(img, (x, y), (x + tw, y + th), (0, 255, 0), 1)
    print(f"阈值 {t}: {len(xs)} 个位置")
    cv2.imshow(f"thr_{t}", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
