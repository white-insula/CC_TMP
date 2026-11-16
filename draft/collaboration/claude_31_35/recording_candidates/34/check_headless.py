# -*- coding: utf-8 -*-
"""第 34 讲无界面核对：定位、拉正、逐格计数、判答案、学号；坏卡检测；阈值 99/100/101 边界附件。
用法：python check_headless.py [--outdir 输出目录]
"""
import argparse
import json
import os
import cv2
import numpy as np
from card_lib import imread, locate, find_marks, choice_counts, read_choices, read_number, is_filled, diagnose, FILL_MIN

ap = argparse.ArgumentParser()
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)
t = json.load(open("template_synthetic.json", encoding="utf-8"))
truth = json.load(open("card_synthetic_01_truth.json", encoding="utf-8"))

img = imread("card_synthetic_01.jpg")
card, marks = locate(img)
print("P6 定位块 (x, y, w, h):", marks)
for x, y, w, h in marks:
    print(f"   w/h = {w / h:.3f}（1.6—2.3）  外接框面积 {w * h}")
contours, _ = cv2.findContours(cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY_INV)[1], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
areas = sorted(cv2.contourArea(c) for c in contours if any(abs(cv2.boundingRect(c)[0] - m[0]) < 2 and abs(cv2.boundingRect(c)[1] - m[1]) < 2 for m in marks))
print("   定位块 contourArea:", areas, "（300—600）")
assert card is not None and card.shape[:2] == (800, 600) and len(marks) == 4
show = img.copy()
for x, y, w, h in marks:
    cv2.rectangle(show, (x, y), (x + w, y + h), (0, 0, 255), 3)
cv2.imwrite(os.path.join(args.outdir, "34_p6_marks.png"), cv2.resize(show, None, fx=0.5, fy=0.5))
cv2.imwrite(os.path.join(args.outdir, "34_p6_card_600x800.png"), card)

counts, choice_bin = choice_counts(card, t)
picks, view = read_choices(card, t)
sid, best = read_number(card, t)
cv2.imwrite(os.path.join(args.outdir, "34_p8_choice_600x400.png"), view)
cv2.imwrite(os.path.join(args.outdir, "34_p8_choice_binary.png"), choice_bin)
print("P8 每格白色像素数 / 判定 / 填涂意图：")
kinds = {}
for q in range(1, 21):
    intent = truth["marks"][str(q)]
    exp = "".join(o for o, how in intent if how in ("full", "half"))
    kind = "空白" if not intent else ("多涂" if len(intent) > 1 else {"full": "明确填涂", "light": "浅涂", "half": "只涂一半"}[intent[0][1]])
    kinds.setdefault(kind, []).append((q, counts[q - 1], picks[q - 1]))
    print(f"   第{q:2d}题 {counts[q - 1]} → '{picks[q - 1]}'  （{kind}，意图 {[o for o, _ in intent]}）")
    assert picks[q - 1] == exp, (q, picks[q - 1], exp)
print("P8 分类小结：")
for k, v in kinds.items():
    print(f"   {k}：", v)
print(f"P8 学号 {sid!r}（真值 {truth['sid']!r}），每列最大计数 {best}")
assert sid == truth["sid"]

print("坏卡检测：")
for f in ("card_synthetic_missing_locator.jpg", "card_synthetic_extra_block.jpg"):
    c2, m2 = locate(imread(f))
    print(f"   {f}：定位{'失败' if c2 is None else '成功'}，找到 {len(m2)} 个；原因：{diagnose(f)}")
    assert c2 is None

# 阈值边界附件：在 20×12 的格子里放 99 / 100 / 101 个白色像素，用 countNonZero 实数后交给 is_filled
tiles = []
for n in (99, 100, 101):
    roi = np.zeros((12, 20), np.uint8)
    roi.flat[:n] = 255
    k = cv2.countNonZero(roi)
    print(f"边界：countNonZero = {k} → is_filled = {is_filled(k)}（规则：≥ {FILL_MIN}）")
    big = cv2.cvtColor(cv2.resize(roi, None, fx=16, fy=16, interpolation=cv2.INTER_NEAREST), cv2.COLOR_GRAY2BGR)
    cv2.rectangle(big, (0, 0), (big.shape[1] - 1, big.shape[0] - 1), (0, 200, 0) if is_filled(k) else (0, 0, 220), 3)
    lab = np.full((40, big.shape[1], 3), 255, np.uint8)
    cv2.putText(lab, f"{k}: {'filled' if is_filled(k) else 'not filled'}", (6, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    tiles.append(np.vstack([big, lab]))
assert [is_filled(n) for n in (99, 100, 101)] == [False, True, True]
gap = np.full((tiles[0].shape[0], 20, 3), 255, np.uint8)
cv2.imwrite(os.path.join(args.outdir, "34_ref_threshold_99_100_101.png"), np.hstack([tiles[0], gap, tiles[1], gap, tiles[2]]))
print("OK 34")
