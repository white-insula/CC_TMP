# -*- coding: utf-8 -*-
"""38 讲四种模式（39、40 讲沿用）。

mode 1 原画面；2 灰度；3 素描：灰度 → GaussianBlur(5,5) → Canny(50,150) → 255 减边缘（白底黑线）；
4 卡通：按正式脚本所指 [PI]EXP-opencv-edge/edge_cartoon.py 的处理链（与第 20 讲录屏 cartoon.py 相同）：
  medianBlur(灰度, 5) → Canny(50, 50) → bilateralFilter(9, 300, 300) → 与反色边缘按位与。
（现有 _visuals/m5.py 的卡通用 adaptiveThreshold + bilateral(9,75,75)，参数不同，见 review。）
"""
import cv2

NAMES = {1: "Original", 2: "Gray", 3: "Sketch", 4: "Cartoon"}


def cartoon(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(cv2.medianBlur(gray, 5), 50, 50)
    color = cv2.bilateralFilter(frame, 9, 300, 300)
    return cv2.bitwise_and(color, cv2.cvtColor(255 - edges, cv2.COLOR_GRAY2BGR))


def apply_mode(frame, mode):
    """frame 必须是 BGR 三通道；返回的 out 在 mode 2、3 时是单通道"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if mode == 2:
        return gray
    if mode == 3:
        return 255 - cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
    if mode == 4:
        return cartoon(frame)
    return frame


def to_bgr(img):
    """单通道画面写彩色字之前先转回三通道"""
    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if img.ndim == 2 else img


def overlay(out, mode, extra=None):
    """38-P7：左上角模式名，底部按键说明"""
    out = to_bgr(out).copy()
    cv2.putText(out, f"Mode {mode}: {NAMES[mode]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(out, extra or "1-4: switch  q: quit", (10, out.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    return out
