# -*- coding: utf-8 -*-
"""第 27 讲 颜色提取与掩膜：录屏程序与无界面核对共用的核心代码（参数与正式脚本一致）。"""
import cv2
import numpy as np

GREEN_LO, GREEN_HI = (35, 80, 50), (85, 255, 255)
RED1_LO, RED1_HI = (0, 100, 80), (10, 255, 255)
RED2_LO, RED2_HI = (170, 100, 80), (179, 255, 255)
KERNEL = np.ones((5, 5), np.uint8)


def load(path):
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"读不到图片：{path}（检查文件名和路径）")
    return img


def extract_green(img):
    """27-P7"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, GREEN_LO, GREEN_HI)
    result = cv2.bitwise_and(img, img, mask=mask)
    return hsv, mask, result


def extract_red(img):
    """27-P8：单段 → 两段 OR 合并 → 5×5 开运算去噪"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m1 = cv2.inRange(hsv, RED1_LO, RED1_HI)
    m2 = cv2.inRange(hsv, RED2_LO, RED2_HI)
    mask = cv2.bitwise_or(m1, m2)
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, KERNEL)
    return m1, m2, mask, opened
