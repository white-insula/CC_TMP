# -*- coding: utf-8 -*-
"""第 37 讲逐帧处理：输入 frame 约定为 BGR 三通道 uint8（cap.read() 读出来的就是 BGR）。"""
import cv2
import numpy as np

BLUE_LO, BLUE_HI = (100, 100, 80), (130, 255, 255)


def check_bgr(frame):
    if frame is None or frame.ndim != 3 or frame.shape[2] != 3 or frame.dtype != np.uint8:
        raise ValueError("需要 BGR 三通道 uint8 图像")


def gray_binary(frame):
    """37-P5：灰度 + 大津法二值化"""
    check_bgr(frame)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return gray, binary


def blue_extract(frame):
    """37-P6：HSV → inRange 蓝色（上下界都包含）→ bitwise_and"""
    check_bgr(frame)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, BLUE_LO, BLUE_HI)
    result = cv2.bitwise_and(frame, frame, mask=mask)
    return mask, result
