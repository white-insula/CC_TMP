# -*- coding: utf-8 -*-
"""第 26 讲 HSV 颜色空间：录屏程序与无界面核对共用的核心代码（写法与正式脚本一致）。"""
import cv2
import numpy as np

# 26-P8：6 个滑动条（名称, 初值, 最大值）；H 最大 179，S、V 最大 255
TRACKBARS = [("H1", 0, 179), ("S1", 80, 255), ("V1", 50, 255),
             ("H2", 179, 179), ("S2", 255, 255), ("V2", 255, 255)]


def load(path):
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"读不到图片：{path}（检查文件名和路径）")
    return img


def to_hsv(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2HSV)


def pure_colors():
    """26-P7：纯红、纯绿、纯蓝转 HSV，写法同脚本。"""
    out = []
    for name, bgr in (("red", [0, 0, 255]), ("green", [0, 255, 0]), ("blue", [255, 0, 0])):
        out.append((name, cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)))
    return out


def range_mask(hsv, h1, s1, v1, h2, s2, v2):
    """26-P8：inRange 上下界都包含。"""
    return cv2.inRange(hsv, (h1, s1, v1), (h2, s2, v2))
