# -*- coding: utf-8 -*-
"""39 讲帧率计算。

正式教学写法（FpsMeter 默认 clock=time.time）：
    now = time.time(); fps = 1 / (now - prev); prev = now
计时范围：两次 tick 之间的全部时间——读帧、处理、显示、waitKey 等待都算在内，得到的是“整个循环的吞吐”，
不是单纯的处理算法耗时，也不是摄像头标称帧率。
保护：时钟精度不足时 now - prev 可能为 0（或系统时间回拨为负），这时不计算，返回 None，避免除零或假的极大值。
平滑：本模块提供两种并注明——
    mean_of_inst：最近 N 个瞬时 FPS 的算术平均（脚本“取最近几帧的平均值”的直白做法）；
    frames_over_time：最近 N 帧的帧数 ÷ 这些帧的总耗时（等于平均耗时的倒数）。两者在耗时不均匀时会不同。
扩展：clock=time.perf_counter 精度更高、不受系统时间调整影响，单独作为扩展选项，不替代正式写法。
"""
import time
from collections import deque


class FpsMeter:
    def __init__(self, clock=time.time, window=10):
        self.clock = clock
        self.prev = clock()
        self.inst = deque(maxlen=window)
        self.dts = deque(maxlen=window)

    def tick(self):
        now = self.clock()
        dt = now - self.prev
        self.prev = now
        if dt <= 0:
            return None
        fps = 1 / dt
        self.inst.append(fps); self.dts.append(dt)
        return fps

    def mean_of_inst(self):
        return sum(self.inst) / len(self.inst) if self.inst else None

    def frames_over_time(self):
        return len(self.dts) / sum(self.dts) if self.dts else None
