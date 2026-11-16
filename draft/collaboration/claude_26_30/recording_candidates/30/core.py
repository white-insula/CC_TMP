# -*- coding: utf-8 -*-
"""第 30 讲 形状识别：录屏程序与无界面核对共用的核心代码（规则与正式脚本录屏1一致）。
简化规则只适用于本课分开摆放、摆正的规则图形：≥6 个角点暂判 circle，六边形等也会被误判。"""
import cv2


def load(path):
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"读不到图片：{path}（检查文件名和路径）")
    return img


def contours_of_shapes(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return [c for c in contours if cv2.contourArea(c) >= 500]          # 按面积过滤（第 29 讲）


def classify(c, eps=0.02):
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, eps * peri, True)
    n = len(approx); x, y, w, h = cv2.boundingRect(approx)
    if n == 3: name = "triangle"
    elif n == 4: name = "square" if 0.95 <= w / h <= 1.05 else "rectangle"
    elif n == 5: name = "pentagon"
    elif n >= 6: name = "circle"
    else: name = "unknown"
    return name, approx, (x, y, w, h)


def label_all(img, eps=0.02):
    out = img.copy(); names = []
    for c in sorted(contours_of_shapes(img), key=lambda c: (cv2.boundingRect(c)[1] // 100, cv2.boundingRect(c)[0])):
        name, approx, (x, y, w, h) = classify(c, eps)
        names.append((name, len(approx)))
        cv2.polylines(out, [approx], True, (0, 0, 255), 2)
        cv2.putText(out, name, (x, y + h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 160, 255), 2)
    return out, names
