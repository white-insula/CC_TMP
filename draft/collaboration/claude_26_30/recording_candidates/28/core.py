# -*- coding: utf-8 -*-
"""第 28 讲 轮廓的查找与绘制：录屏程序与无界面核对共用的核心代码（写法与正式脚本一致）。
约定：二值图白色是目标、黑色是背景；白底黑图形要用 THRESH_BINARY_INV。"""
import cv2


def load(path):
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"读不到图片：{path}（检查文件名和路径）")
    return img


def binarize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return binary


def draw_numbered(img, contours):
    """28-P7：逐个画轮廓并在第一个点处写编号"""
    out = img.copy()
    for i, c in enumerate(contours):
        cv2.drawContours(out, [c], -1, (0, 0, 255), 2)
        x, y = c[0][0]
        cv2.putText(out, str(i + 1), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    return out
