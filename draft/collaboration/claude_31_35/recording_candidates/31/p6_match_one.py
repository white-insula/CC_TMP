# -*- coding: utf-8 -*-
# 第 31 讲 P6 录屏：从大图裁出一个元件当模板 → matchTemplate → minMaxLoc → 画框 → 打印最高分
# 用法：python p6_match_one.py [--input 电路板照片.jpg] [--crop x y w h | --template 已有模板.png]
# 默认输入是合成电路板（不是真实照片）；裁出的模板存为 template_synthetic.png
import argparse
import cv2
from core import load, DEFAULT_CROP

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="pcb_synthetic.png")
ap.add_argument("--template", default=None, help="已有模板文件；不给则按 --crop 从大图裁出")
ap.add_argument("--crop", type=int, nargs=4, default=DEFAULT_CROP, metavar=("X", "Y", "W", "H"))
ap.add_argument("--save-template", default="template_synthetic.png")
args = ap.parse_args()

img = load(args.input)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
if args.template is None:
    x, y, w, h = args.crop
    cv2.imwrite(args.save_template, img[y:y + h, x:x + w])        # 第 16 讲的切片
    args.template = args.save_template
tpl = cv2.imread(args.template, 0); th, tw = tpl.shape
res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc = cv2.minMaxLoc(res)
print(max_val)
x, y = max_loc; cv2.rectangle(img, (x, y), (x + tw, y + th), (0, 0, 255), 2)
cv2.imshow("match", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
