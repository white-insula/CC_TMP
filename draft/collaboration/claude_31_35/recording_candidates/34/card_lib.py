# -*- coding: utf-8 -*-
"""第 34、35 讲共用的答题卡识别函数（候选；写法按正式脚本 34-P6/P8、35-P5）。

只在合成教学样本上测过；没有拿到 [GA] 真实答题卡、原 template.json、config.json，不能承诺兼容真实卡。
"""
import cv2
import numpy as np

THRESH = 127          # 反向二值化阈值（脚本口播：阈值一百二十七）
FILL_MIN = 100        # countNonZero ≥ 100 判为已涂（代码是“大于等于”，不是“超过”）


def imread(path):
    """路径里有中文也能读；读不到返回 None"""
    data = np.fromfile(path, np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR) if data.size else None


def binarize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, THRESH, 255, cv2.THRESH_BINARY_INV)
    return binary


def find_marks(img):
    """34-P6：找轮廓，按宽高比 1.6—2.3、面积 300—600 筛定位块，返回 [(x, y, w, h), …]"""
    contours, _ = cv2.findContours(binarize(img), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    marks = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if 1.6 <= w / h <= 2.3 and 300 <= cv2.contourArea(c) <= 600:
            marks.append((x, y, w, h))
    return marks


def locate(img):
    """恰好 4 个定位块才算成功：排序（先按 y 分上下，再按 x 分左右）→ 外角 → 拉正成 600×800。
    失败返回 (None, marks)。"""
    marks = find_marks(img)
    if len(marks) != 4:
        return None, marks
    marks.sort(key=lambda m: m[1])
    (x0, y0, w0, h0), (x1, y1, w1, h1) = sorted(marks[:2])
    (x2, y2, w2, h2), (x3, y3, w3, h3) = sorted(marks[2:])
    src = np.float32([[x0, y0], [x1 + w1, y1], [x3 + w3, y3 + h3], [x2, y2 + h2]])      # 左上、右上、右下、左下
    dst = np.float32([[0, 0], [599, 0], [599, 799], [0, 799]])
    card = cv2.warpPerspective(img, cv2.getPerspectiveTransform(src, dst), (600, 800))
    return card, marks


def is_filled(count):
    """判填涂：countNonZero ≥ 100（等于 100 也算已涂）"""
    return count >= FILL_MIN


def choice_counts(card, t):
    """34-P8：裁出选择题区域 → 缩放到 600×400 → 每格 countNonZero；返回 [[A, B, C, D], …]"""
    binary = binarize(card)
    x0, y0, w0, h0 = t["choice_roi_rect"]
    choice = cv2.resize(binary[y0:y0 + h0, x0:x0 + w0], (600, 400))
    return [[cv2.countNonZero(choice[y:y + h, x:x + w]) for x, y, w, h in group] for group in t["choice_pos_list"]], choice


def read_choices(card, t, show=False):
    """34-P8：≥ FILL_MIN 的选项记下；返回 (每题作答列表, 画了绿框的选择题区域图)"""
    counts, _ = choice_counts(card, t)
    x0, y0, w0, h0 = t["choice_roi_rect"]
    view = cv2.resize(card[y0:y0 + h0, x0:x0 + w0], (600, 400))
    picks = []
    for q, group in enumerate(t["choice_pos_list"]):
        picked = ""
        for j, (x, y, w, h) in enumerate(group):
            if is_filled(counts[q][j]):
                picked += "ABCD"[j]; cv2.rectangle(view, (x, y), (x + w, y + h), (0, 255, 0), 1)
        if show:
            print(q + 1, picked)
        picks.append(picked)
    return picks, view


def read_number(card, t):
    """35-P5：学号区域缩放到 400×300，每列取白像素最多的数字。
    注意：某列完全没涂时 argmax 会给出 0，本候选另返回每列最大计数供检查。"""
    binary = binarize(card)
    x0, y0, w0, h0 = t["number_roi_rect"]
    num = cv2.resize(binary[y0:y0 + h0, x0:x0 + w0], (400, 300))
    sid, best = "", []
    for col in t["number_pos_list"]:
        cnt = [cv2.countNonZero(num[y:y + h, x:x + w]) for x, y, w, h in col]
        sid += str(int(np.argmax(cnt))); best.append(max(cnt))
    return sid, best


def recognize(path, t):
    """35-P5：传入图片路径，返回 (学号字符串, 答案列表)；读不到图或定位失败返回 None"""
    img = imread(path)
    if img is None:
        return None
    card, _ = locate(img)
    if card is None:
        return None
    return read_number(card, t)[0], read_choices(card, t)[0]


def diagnose(path):
    """【扩展】recognize 返回 None 时说明原因，供失败列表记录；不改变 recognize 的返回约定"""
    img = imread(path)
    if img is None:
        return "图片读不出来"
    n = len(find_marks(img))
    if n < 4:
        return f"定位块只找到 {n} 个"
    if n > 4:
        return f"找到 {n} 个疑似定位块，存在干扰"
    return "未知原因"
