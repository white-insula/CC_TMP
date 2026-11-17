# -*- coding: utf-8 -*-
"""合成测试帧与测试视频（合成教学样本，不是摄像头画面或用户录屏）。

每帧包含：白纸黑字（37 讲二值化）、移动的蓝色方块（37 讲颜色提取，BGR (200,120,30) ≈ H 104）、
移动的红球、帧号文字，以及左下角 10 个黑白方格组成的二进制帧号（压缩后仍可读回，用于核对帧顺序）。
"""
import cv2
import numpy as np

BLUE = (200, 120, 30)
RED = (40, 40, 210)
BITS = 10
CELL = 14


def make_frame(k, w=640, h=480):
    yy, xx = np.mgrid[0:h, 0:w]
    f = np.dstack([110 + 40 * xx / w, 115 + 30 * yy / h, 120 + 20 * xx / w]).astype(np.uint8)
    cv2.rectangle(f, (40, 40), (300, 200), (245, 245, 245), -1)                 # 白纸
    cv2.putText(f, "OpenCV", (60, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (20, 20, 20), 4)
    cv2.putText(f, "2026", (60, 175), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (20, 20, 20), 4)
    bx = 340 + (k * 7) % (w - 440)
    cv2.rectangle(f, (bx, 60), (bx + 90, 150), BLUE, -1)                       # 蓝色方块
    rx = 60 + (k * 11) % (w - 120)
    cv2.circle(f, (rx, 300), 30, RED, -1, cv2.LINE_AA)                        # 红球
    cv2.putText(f, f"frame {k:04d}", (w - 210, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    for b in range(BITS):                                                     # 二进制帧号（低位在左）
        v = 255 if (k >> b) & 1 else 0
        x0 = 10 + b * CELL
        f[h - 10 - CELL:h - 10, x0:x0 + CELL] = v
    return f


def decode_index(frame):
    h = frame.shape[0]
    g = frame if frame.ndim == 2 else cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    k = 0
    for b in range(BITS):
        x0 = 10 + b * CELL
        if g[h - 10 - CELL + 3:h - 10 - 3, x0 + 3:x0 + CELL - 3].mean() > 127:
            k |= 1 << b
    return k


class SyntheticSource:
    """行为类似 VideoCapture 的合成来源：read() 依次给出 n 帧，之后返回 (False, None)。"""

    def __init__(self, n=60, w=640, h=480, fps=25.0):
        self.n, self.w, self.h, self.fps, self.k, self.released = n, w, h, fps, 0, False

    def isOpened(self):
        return not self.released

    def read(self):
        if self.k >= self.n:
            return False, None
        f = make_frame(self.k, self.w, self.h); self.k += 1
        return True, f

    def get(self, prop):
        return {cv2.CAP_PROP_FRAME_WIDTH: float(self.w), cv2.CAP_PROP_FRAME_HEIGHT: float(self.h),
                cv2.CAP_PROP_FPS: float(self.fps), cv2.CAP_PROP_FRAME_COUNT: float(self.n)}.get(prop, 0.0)

    def release(self):
        self.released = True


def write_video(path, n=60, fps=25.0, fourcc="XVID", w=640, h=480):
    """写一段合成测试视频；编码器不可用时如实返回 False"""
    wr = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
    if not wr.isOpened():
        return False
    try:
        for k in range(n):
            wr.write(make_frame(k, w, h))
    finally:
        wr.release()
    return True
