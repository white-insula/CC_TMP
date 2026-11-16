# -*- coding: utf-8 -*-
"""第 35 讲 批量阅卷：共用核心（候选）。识别部分直接复用第 34 讲候选的 card_lib.py。

与脚本/参考工程的差别（见 review）：
  · Excel 列按题号从小到大排列，每列取 picks[题号 - 1]，题号不连续、答案文件乱序也不会错位；
  · 识别失败的卡写到单独的“识别失败”工作表（文件名 + 原因），不计 0 分，不进成绩表统计；
  · 学号作为字符串写入，保留前导 0。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "34"))
from card_lib import recognize, diagnose          # noqa: E402  第 34 讲候选的识别函数


def load_answers(path):
    """35-P6：每行“题号-答案-分值”；返回 {题号: (答案, 分值)}"""
    answers = {}
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        no, ans, score = line.strip().split("-"); answers[int(no)] = (ans, int(score))
    return answers


def score(picks, answers):
    """纯评分：picks 是按题号 1、2、3… 排列的作答列表；返回 (总分, 错题题号列表)"""
    total, wrong = 0, []
    for q in sorted(answers):
        ans, pts = answers[q]
        if q - 1 < len(picks) and picks[q - 1] == ans:
            total += pts
        else:
            wrong.append(q)
    return total, wrong


def batch(folder, answers, t):
    """35-P6：遍历文件夹，只处理 .jpg；识别失败记入 failed 并继续"""
    results, failed = [], []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".jpg"):
            continue
        path = os.path.join(folder, name)
        r = recognize(path, t)
        if r is None:
            failed.append((name, diagnose(path))); continue
        sid, picks = r
        total, wrong = score(picks, answers)
        results.append({"file": name, "sid": sid, "picks": picks, "total": total, "wrong": wrong})
    return results, failed


def export(results, failed, answers, path):
    """35-P8：openpyxl 写成绩单；错题标红；失败卡写单独工作表"""
    import openpyxl
    from openpyxl.styles import Font
    qs = sorted(answers)
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "成绩"
    ws.append(["学号", "总分"] + [f"第{q}题" for q in qs])
    for r in results:
        ws.append([str(r["sid"]), r["total"]] + [r["picks"][q - 1] for q in qs])
        for i, q in enumerate(qs):
            if q in r["wrong"]:
                ws.cell(row=ws.max_row, column=3 + i).font = Font(color="FF0000")
    wf = wb.create_sheet("识别失败")
    wf.append(["文件名", "原因（请人工检查）"])
    for name, why in failed:
        wf.append([name, why])
    wb.save(path)
    return path
