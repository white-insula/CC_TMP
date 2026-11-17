# -*- coding: utf-8 -*-
"""第 39 讲无界面核对：
A. 确定性时钟（模拟时间，不是实测性能）验证 FPS 公式、dt ≤ 0 保护、两种平滑的区别；
B. 云端独立环境的算法计时基准（只计 cartoon 处理，不含读帧/显示/摄像头），只代表本云端环境。
用法：python check_headless.py [--outdir 输出目录] [--samples 20]
"""
import argparse
import os
import platform
import time
import cv2
import numpy as np
import _path  # noqa: F401
from common.fps import FpsMeter
from common.effects import cartoon
from common.synth import make_frame

ap = argparse.ArgumentParser()
ap.add_argument("--outdir", default="check_out")
ap.add_argument("--samples", type=int, default=20)
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)


def fake_clock(ts):
    it = iter(ts)
    return lambda: next(it)


# A1：每帧 0.05 秒 → 20 FPS
m = FpsMeter(fake_clock([0.0, 0.05, 0.10, 0.15]))
v = [m.tick() for _ in range(3)]
print("A1 每帧 0.05 秒 → FPS", [round(x, 6) for x in v])
assert all(abs(x - 20) < 1e-9 for x in v)
# A2：dt = 0 与 dt < 0 不计算
m = FpsMeter(fake_clock([1.0, 1.0, 0.9, 1.0]))
print("A2 dt=0、dt<0、dt=0.1 →", [m.tick() for _ in range(3)])
# A3：两种平滑在耗时不均匀时不同
dts = [0.02] * 5 + [0.2] * 5                      # 5 帧快、5 帧慢
ts = np.concatenate([[0.0], np.cumsum(dts)]).tolist()
m = FpsMeter(fake_clock(ts), window=10)
for _ in dts:
    m.tick()
a, b = m.mean_of_inst(), m.frames_over_time()
print(f"A3 10 帧耗时 5×0.02 + 5×0.2 秒：瞬时 FPS 平均 = {a:.2f}；帧数 ÷ 总时间 = {b:.2f}（=10/1.1）")
assert abs(a - 27.5) < 1e-9 and abs(b - 10 / 1.1) < 1e-9
# A4：窗口只保留最近 10 帧
m = FpsMeter(fake_clock([i * 0.1 for i in range(13)] + [1.2 + 0.05 * i for i in range(1, 11)]), window=10)
for _ in range(22):
    m.tick()
print(f"A4 先 12 帧每帧 0.1 秒、再 10 帧每帧 0.05 秒：最近 10 帧平滑 = {m.frames_over_time():.2f}")
assert abs(m.frames_over_time() - 20) < 1e-6
print("A 以上为模拟时间，只验证公式，不是实测性能")

# B：算法计时（暖机 3 次，取 samples 次的中位数）
def bench(fn, img, n):
    for _ in range(3):
        fn(img)
    t = []
    for _ in range(n):
        t0 = time.perf_counter(); fn(img); t.append(time.perf_counter() - t0)
    return float(np.median(t))


f640 = cv2.resize(make_frame(0), (640, 480))
f720 = cv2.resize(make_frame(0), (1280, 720))
half = lambda im: cv2.resize(cartoon(cv2.resize(im, None, fx=0.5, fy=0.5)), (im.shape[1], im.shape[0]))
default_threads = cv2.getNumThreads()
for threads in (default_threads, 1):
    cv2.setNumThreads(threads)
    r = {"640×480 cartoon": bench(cartoon, f640, args.samples),
         "1280×720 cartoon": bench(cartoon, f720, args.samples),
         "1280×720 先缩小一半": bench(half, f720, args.samples)}
    print(f"B 云端独立环境基准（{platform.machine()}，{os.cpu_count()} 逻辑核，OpenCV {cv2.__version__}，线程数 {threads}，"
          f"暖机 3 次，样本 {args.samples}，取中位数；只计 cartoon 处理耗时）：")
    for k, t in r.items():
        print(f"   {k}：{t * 1000:.2f} 毫秒/帧（约 {1 / t:.1f} 帧/秒的纯处理能力）")
cv2.setNumThreads(default_threads)
print("B 多线程时 OpenCV 对不同尺寸的并行程度不同，耗时不一定与像素数成正比；单线程更接近像素比例。")
print("B 以上只代表本云端环境，不代表用户电脑或摄像头实测；实际循环 FPS 还受读帧、显示、waitKey 和摄像头出帧限制")
print("OK 39")
