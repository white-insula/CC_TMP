# -*- coding: utf-8 -*-
# 第 34 讲 P8 录屏：读模板 → 裁出选择题区域缩放到 600×400 → 逐格 countNonZero（≥ 100 判为已涂）→ 打印每题答案 → 被涂格子画绿框
# 用法：python p8_read_answers.py [--input 答题卡.jpg] [--template 模板.json] [--counts]
# 默认模板是 template_synthetic.json（合成卡专用），不能用于学生真实答题卡
import argparse
import json
import cv2
from card_lib import imread, locate, read_choices, choice_counts

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="card_synthetic_01.jpg")
ap.add_argument("--template", default="template_synthetic.json")
ap.add_argument("--counts", action="store_true", help="先打印每个格子的白色像素数")
args = ap.parse_args()

with open(args.template, encoding="utf-8") as f: t = json.load(f)
card, _ = locate(imread(args.input))
if card is None:
    raise SystemExit("定位失败，无法判答案")
if args.counts:
    for q, c in enumerate(choice_counts(card, t)[0]):
        print(q + 1, c)
picks, view = read_choices(card, t, show=True)
cv2.imshow("choice", view)
cv2.waitKey(0)
cv2.destroyAllWindows()
