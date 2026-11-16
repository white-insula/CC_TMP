# -*- coding: utf-8 -*-
# 第 35 讲 P6 录屏：解析答案文件 → os.listdir 遍历 → recognize → 对比算分 → 失败的卡记入列表
# 用法：python p6_batch_score.py [--folder 答题卡文件夹] [--answers 答案.txt] [--template 模板.json]
# 默认是合成教学样本（cards_synthetic/、答案_synthetic.txt、../34/template_synthetic.json），不是学生真实答题卡
import argparse
import json
from core import load_answers, batch

ap = argparse.ArgumentParser()
ap.add_argument("--folder", default="cards_synthetic")
ap.add_argument("--answers", default="答案_synthetic.txt")
ap.add_argument("--template", default="../34/template_synthetic.json")
args = ap.parse_args()

with open(args.template, encoding="utf-8") as f: t = json.load(f)
answers = load_answers(args.answers)
results, failed = batch(args.folder, answers, t)
for r in results:
    print(r["sid"], r["total"])
print("识别失败:", failed)
