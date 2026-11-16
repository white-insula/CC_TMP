# -*- coding: utf-8 -*-
# 第 30 讲 P7 录屏：误差系数改 0.08 → 改 0.005 → 恢复 0.02，对比判断结果
# 用法：python p7_eps.py --eps 0.08     （录屏时依次改 0.08、0.005、0.02 再运行）
import argparse
import cv2
from core import load, label_all

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="shapes_synthetic.png")
ap.add_argument("--eps", type=float, default=0.02)
args = ap.parse_args()

img = load(args.input)
out, names = label_all(img, args.eps)
print(f"eps = {args.eps}:", names)
cv2.imshow(f"eps={args.eps}", out)
cv2.waitKey(0)
cv2.destroyAllWindows()
