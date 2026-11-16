# -*- coding: utf-8 -*-
"""核对第 34/35 讲答题卡识别:40 张扫描卡逐张识别,和学长程序的结果 test_1.xlsx 逐题比对。
用法:python _verify_cards.py <学长项目目录> [定位块面积下限 上限]"""
import cv2, numpy as np, glob, os, sys, json
import openpyxl

G = sys.argv[1]
AMIN, AMAX = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (300, 600)
T = json.load(open(os.path.join(G, "settings", "template.json"), encoding="utf-8"))


def imread(p): return cv2.imdecode(np.fromfile(p, np.uint8), 1)


def locate(img):
    """第 34 讲 p6:找四个定位块 → 透视拉正成 600×800"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    marks = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if 1.6 <= w / h <= 2.3 and AMIN <= cv2.contourArea(c) <= AMAX:
            marks.append((x, y, w, h))
    if len(marks) != 4:
        return None, len(marks)
    marks.sort(key=lambda m: m[1])                       # 先按 y 分上下
    top = sorted(marks[:2], key=lambda m: m[0]); bot = sorted(marks[2:], key=lambda m: m[0])   # 再按 x 分左右
    (x0, y0, w0, h0), (x1, y1, w1, h1) = top; (x2, y2, w2, h2), (x3, y3, w3, h3) = bot
    src = np.float32([[x0, y0], [x1 + w1, y1], [x3 + w3, y3 + h3], [x2, y2 + h2]])   # 左上、右上、右下、左下
    M = cv2.getPerspectiveTransform(src, np.float32([[0, 0], [599, 0], [599, 799], [0, 799]]))
    return cv2.warpPerspective(img, M, (600, 800)), 4


def read_card(card):
    """第 34 讲 p8:按模板坐标数白色像素"""
    _, b = cv2.threshold(cv2.cvtColor(card, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY_INV)
    x, y, w, h = T["choice_roi_rect"]
    choice = cv2.resize(b[y:y + h, x:x + w], (600, 400))       # 学长程序:先裁选择题区域,再缩放到 600×400
    answers = []
    for group in T["choice_pos_list"]:
        picked = ""
        for j, (cx, cy, cw, ch) in enumerate(group):
            if cv2.countNonZero(choice[cy:cy + ch, cx:cx + cw]) >= 100:
                picked += "ABCD"[j]
        answers.append(picked)
    x, y, w, h = T["number_roi_rect"]
    num = cv2.resize(b[y:y + h, x:x + w], (400, 300))
    sid = ""
    for col in T["number_pos_list"]:
        cnt = [cv2.countNonZero(num[cy:cy + ch, cx:cx + cw]) for cx, cy, cw, ch in col]
        sid += str(int(np.argmax(cnt)))
    return sid, answers


ref = {}
ws = openpyxl.load_workbook(os.path.join(G, "test_1.xlsx")).active
for r in list(ws.iter_rows(values_only=True))[1:]:
    ref[str(r[0])] = [(v or "") for v in r[1:81]]

files = sorted(glob.glob(os.path.join(G, "答题卡扫描文件", "*.jpg")))
ok_loc = ok_id = 0; q_total = q_same = 0; bad = []
for f in files:
    card, n = locate(imread(f))
    if card is None:
        bad.append((os.path.basename(f), f"定位块 {n} 个")); continue
    ok_loc += 1
    sid, ans = read_card(card)
    if sid in ref:
        ok_id += 1
        same = sum(a == b for a, b in zip(ans, ref[sid])); q_total += len(ans); q_same += same
        if same < len(ans):
            diff = [(i + 1, a, b) for i, (a, b) in enumerate(zip(ans, ref[sid])) if a != b]
            bad.append((os.path.basename(f), f"学号 {sid} 有 {len(diff)} 题不同: {diff[:5]}"))
    else:
        bad.append((os.path.basename(f), f"学号识别为 {sid},不在参考表里"))
print(f"定位块面积 {AMIN}-{AMAX}: 定位成功 {ok_loc}/{len(files)}  学号对上 {ok_id}/{len(files)}  "
      f"逐题一致 {q_same}/{q_total} ({q_same / max(q_total, 1) * 100:.1f}%)")
for b in bad[:12]:
    print("  ", *b)
