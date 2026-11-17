# -*- coding: utf-8 -*-
"""第 36 讲无界面核对（不打开摄像头、不弹窗口）：
文件读帧到 EOF、帧顺序、帧率回退与等待毫秒数、打不开/空文件/损坏文件、退出后资源释放。
用法：python check_headless.py [--outdir 输出目录]
"""
import argparse
import math
import os
import cv2
import numpy as np
import _path  # noqa: F401
from common.sources import playback_delay, describe
from common.synth import write_video, decode_index

ap = argparse.ArgumentParser()
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)

# P7：生成并读回合成测试视频
path = os.path.join(args.outdir, "36_synthetic_25fps.avi")
assert write_video(path, n=50, fps=25.0, fourcc="XVID"), "XVID 不可用"
cap = cv2.VideoCapture(path)
assert cap.isOpened()
info = describe(cap)
idx = []
while True:
    ret, frame = cap.read()
    if not ret:
        break
    assert frame.shape == (480, 640, 3) and frame.dtype == np.uint8
    idx.append(decode_index(frame))
cap.release()
print("P7 读回属性:", info)
print(f"P7 读到 {len(idx)} 帧，帧号 {idx[:3]}…{idx[-3:]}，严格按顺序：{idx == list(range(50))}；第 51 次 read() 返回 False（EOF）")
assert idx == list(range(50))
cv2.imwrite(os.path.join(args.outdir, "36_p7_frame_first.png"), cv2.VideoCapture(path).read()[1])

# 帧率回退与等待时间
cases = [30.0, 25.0, 29.97, 0.0, -1.0, float("nan"), float("inf"), 2000.0, 0.5]
for f in cases:
    d, used = playback_delay(f)
    print(f"P7 fps={f!r:>6} → 使用 {used} 帧/秒，waitKey({d})")
assert playback_delay(0.0) == (40, 25.0) and playback_delay(float("nan"))[0] == 40
assert playback_delay(2000.0)[0] == 1 and playback_delay(30.0)[0] == 33 and playback_delay(0.5)[0] == 2000

# 打不开 / 空文件 / 损坏文件
bad_cases = {"不存在": os.path.join(args.outdir, "no_such_file.avi")}
empty = os.path.join(args.outdir, "empty.avi"); open(empty, "wb").close(); bad_cases["空文件"] = empty
junk = os.path.join(args.outdir, "corrupt.avi")
with open(junk, "wb") as f:
    f.write(np.random.RandomState(36).bytes(4096))
bad_cases["随机字节"] = junk
for name, p in bad_cases.items():
    c = cv2.VideoCapture(p)
    opened = c.isOpened(); ok = c.read()[0] if opened else False
    c.release()
    print(f"P7 {name}：isOpened={opened}，第一次 read()={ok}")
    assert not ok
for p in (empty, junk):
    os.remove(p)

# 截断文件：只保留前一半字节
half = os.path.join(args.outdir, "36_truncated.avi")
data = open(path, "rb").read()
open(half, "wb").write(data[:len(data) // 2])
c = cv2.VideoCapture(half); n = 0
while c.isOpened():
    r, fr = c.read()
    if not r:
        break
    n += 1
c.release(); os.remove(half)
print(f"P7 截断一半的文件：读到 {n} 帧后返回 False（与正常 EOF 一样表现为 ret=False，只能结合帧数判断是否提前结束）")

# 释放：release 后 isOpened 为 False
c = cv2.VideoCapture(path); c.release()
print("P6/P7 release() 后 isOpened():", c.isOpened())
assert not c.isOpened()
print("P6 摄像头：云端未连接摄像头，未测试（p6_camera.py 需本机 --camera 运行）")
print("OK 36")
