# -*- coding: utf-8 -*-
"""第 29 讲 轮廓特征：录屏程序与无界面核对共用的核心代码（写法与正式脚本一致）。
注意：本课的“中心”是外接框中心 (x + w // 2, y + h // 2)，不是 cv2.moments 求的质心。"""
import cv2
import numpy as np

MIN_AREA = 500


def load(path):
    img = cv2.imread(path)
    if img is None:
        raise SystemExit(f"读不到图片：{path}（检查文件名和路径）")
    return img


def contours_of_shapes(img):
    """承接第 28 讲：灰度 → INV+OTSU → EXTERNAL"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours


def red_mask(img):
    """第 27 讲的方法：两段红色 OR 合并，再 5×5 开运算去噪"""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m1 = cv2.inRange(hsv, (0, 100, 80), (10, 255, 255))
    m2 = cv2.inRange(hsv, (170, 100, 80), (179, 255, 255))
    mask = cv2.bitwise_or(m1, m2)
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
