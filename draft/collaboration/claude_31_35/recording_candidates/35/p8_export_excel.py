# -*- coding: utf-8 -*-
# 第 35 讲 P8 录屏：写表头 → 每个学生一行 → 错题标红 → 失败卡单独一页 → 保存成绩单
# 用法：python p8_export_excel.py [--folder …] [--answers …] [--template …] [--out 成绩单_synthetic.xlsx]
import argparse
import json
from core import load_answers, batch, export

ap = argparse.ArgumentParser()
ap.add_argument("--folder", default="cards_synthetic")
ap.add_argument("--answers", default="答案_synthetic.txt")
ap.add_argument("--template", default="../34/template_synthetic.json")
ap.add_argument("--out", default="成绩单_synthetic.xlsx")
args = ap.parse_args()

with open(args.template, encoding="utf-8") as f: t = json.load(f)
answers = load_answers(args.answers)
results, failed = batch(args.folder, answers, t)
print("已保存", export(results, failed, answers, args.out), "；成绩", len(results), "人，识别失败", len(failed), "张")
