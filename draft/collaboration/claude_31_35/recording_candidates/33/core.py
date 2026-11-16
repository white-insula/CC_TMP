# -*- coding: utf-8 -*-
"""第 33 讲 颜色形状分拣：录屏程序与无界面核对共用的核心代码。

两套形状判断，分开命名，互不替换：
  get_shape_current —— 原样照抄 33 讲 P7 画面中的现行代码（4 顶点一律 rectangle，5/6 为 other，n > 6 才 circle）
  get_shape_rule30  —— 独立备选：复用 30 讲规则（4 顶点再按 0.95 ≤ w/h ≤ 1.05 分 square / rectangle，5 pentagon，n ≥ 6 circle）
正式采用哪一版由本机后续决定；本候选不修改脚本或口播。
"""
import cv2
import numpy as np

colors = {
    "red":    [((0, 100, 80), (10, 255, 255)), ((170, 100, 80), (179, 255, 255))],
    "yellow": [((20, 100, 100), (35, 255, 255))],
    "blue":   [((100, 100, 80), (130, 255, 255))],
}
kernel = np.ones((5, 5), np.uint8)
MIN_AREA = 800


def load(path):
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"读不到图片：{path}（检查文件名和路径）")
    return img


def to_hsv(img):
    return cv2.cvtColor(cv2.GaussianBlur(img, (5, 5), 0), cv2.COLOR_BGR2HSV)


def color_mask(hsv, ranges):
    """33-P6：多段 inRange 用 bitwise_or 合并，再开运算"""
    mask = np.zeros(hsv.shape[:2], np.uint8)
    for lo, hi in ranges:
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lo, hi))
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)


def get_shape_current(c):
    """原样照抄 33 讲 P7 画面代码"""
    peri = cv2.arcLength(c, True); n = len(cv2.approxPolyDP(c, 0.02 * peri, True))
    return {3: "triangle", 4: "rectangle"}.get(n, "circle" if n > 6 else "other")


def get_shape_rule30(c):
    """备选：30 讲规则"""
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    n = len(approx); x, y, w, h = cv2.boundingRect(approx)
    if n == 3: return "triangle"
    if n == 4: return "square" if 0.95 <= w / h <= 1.05 else "rectangle"
    if n == 5: return "pentagon"
    if n >= 6: return "circle"
    return "unknown"


def sort_parts(img, get_shape):
    """主循环：返回 (标注图, 计数字典, 明细列表)"""
    hsv = to_hsv(img)
    out = img.copy(); count = {}; items = []; masks = {}
    for name, ranges in colors.items():
        mask = color_mask(hsv, ranges); masks[name] = mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if cv2.contourArea(c) < MIN_AREA: continue
            label = f"{name} {get_shape(c)}"; count[label] = count.get(label, 0) + 1
            x, y, w, h = cv2.boundingRect(c)
            n = len(cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True))
            items.append({"label": label, "center": [x + w // 2, y + h // 2], "n": n, "w_h": round(w / h, 3)})
            cv2.rectangle(out, (x, y), (x + w, y + h), (0, 0, 0), 2)
            cv2.putText(out, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    return out, count, items, masks
