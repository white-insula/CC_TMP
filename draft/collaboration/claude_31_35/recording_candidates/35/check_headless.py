# -*- coding: utf-8 -*-
"""第 35 讲核对，分两部分：
A. 纯评分测试（不读图）：手写作答列表，只测 score() 的题号映射与分值；
B. 端到端测试（真正读图）：对 cards_synthetic/ 里每张合成卡执行 recognize → 算分 → 导出 Excel → 重新打开逐格核对。
   真值文件只用于“事后比对”，不参与识别。
用法：python check_headless.py [--outdir 输出目录]
"""
import argparse
import json
import os
import openpyxl
from core import load_answers, score, batch, export

ap = argparse.ArgumentParser()
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)

answers = load_answers("答案_synthetic.txt")
qs = sorted(answers)
print("答案文件题号（文件顺序）:", list(answers), "；Excel 列顺序:", qs)
assert 7 not in answers and 15 not in answers and list(answers) != qs

# A. 纯评分测试
picks = [""] * 20
for q, (a, _) in answers.items():
    picks[q - 1] = a
full = sum(p for _, p in answers.values())
assert score(picks, answers) == (full, [])
picks2 = list(picks); picks2[2] = "Z"; picks2[19] = "AB"                  # 第 3、20 题错
t2, w2 = score(picks2, answers)
assert w2 == [3, 20] and t2 == full - answers[3][1] - answers[20][1]
print(f"A 纯评分测试通过：满分 {full}；第 3、20 题错 → {t2} 分，错题 {w2}（第 7、15 题不在答案里，不计）")

# B. 端到端
t = json.load(open("../34/template_synthetic.json", encoding="utf-8"))
truth = json.load(open("cards_synthetic_truth.json", encoding="utf-8"))["cards"]
results, failed = batch("cards_synthetic", answers, t)
print("B 识别成功:", [(r["file"], r["sid"], r["total"]) for r in results])
print("B 识别失败:", failed)
assert [f for f, _ in failed] == ["card_06_synthetic_bad.jpg"]
assert len(results) == 5
for r in results:
    tr = truth[r["file"]]
    assert r["sid"] == tr["sid"], (r["file"], r["sid"])
    assert r["picks"] == tr["picks"], r["file"]
print("B 5 张卡的学号与 20 题作答，读图结果与生成真值逐项一致（含前导 0 学号）")

xlsx = export(results, failed, answers, os.path.join(args.outdir, "成绩单_synthetic.xlsx"))
wb = openpyxl.load_workbook(xlsx)
ws, wf = wb["成绩"], wb["识别失败"]
hdr = [c.value for c in ws[1]]
assert hdr == ["学号", "总分"] + [f"第{q}题" for q in qs]
n_red = 0
for i, r in enumerate(results, start=2):
    row = [c.value for c in ws[i]]
    assert row[0] == r["sid"] and ws.cell(row=i, column=1).data_type == "s"
    exp_total, exp_wrong = score(truth[r["file"]]["picks"], answers)
    assert row[1] == exp_total
    for k, q in enumerate(qs):
        cell = ws.cell(row=i, column=3 + k)
        red = cell.font is not None and cell.font.color is not None and cell.font.color.rgb in ("FFFF0000", "00FF0000")
        assert cell.value == truth[r["file"]]["picks"][q - 1]
        assert red == (q in exp_wrong), (r["file"], q)
        n_red += red
assert ws.max_row == 1 + len(results)                                      # 成绩表里没有失败行
assert [c.value for c in wf[2]] == ["card_06_synthetic_bad.jpg", "定位块只找到 3 个"]
print(f"B Excel 重读核对通过：表头 {len(hdr)} 列，学生 {ws.max_row - 1} 行（学号为文本，保留前导 0），"
      f"总分全部正确，红色错题格 {n_red} 个与错题一一对应；失败卡在“识别失败”页，不在成绩表、不计 0 分")
for r in results:
    print(f"   {r['sid']}  总分 {r['total']}  错题 {r['wrong']}")
print("OK 35")
