# -*- coding: utf-8 -*-
"""第 37 讲无界面核对：合成帧（可重复）上验证灰度/二值/蓝色掩膜；视频文件上请求分辨率并读回。
用法：python check_headless.py [--outdir 输出目录]
"""
import argparse
import os
import cv2
import numpy as np
import _path  # noqa: F401
from common.synth import SyntheticSource, make_frame, write_video, BLUE
from common.sources import request_size
from core import gray_binary, blue_extract, BLUE_LO, BLUE_HI

ap = argparse.ArgumentParser()
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)

src = SyntheticSource(n=20)
n = 0
while True:
    ret, frame = src.read()
    if not ret:
        break
    gray, binary = gray_binary(frame)
    mask, result = blue_extract(frame)
    assert gray.shape == binary.shape == mask.shape == frame.shape[:2]
    assert set(np.unique(binary).tolist()) <= {0, 255} and set(np.unique(mask).tolist()) <= {0, 255}
    k = n
    bx = 340 + (k * 7) % (640 - 440)
    assert mask[105, bx + 45] == 255 and mask[300, 20] == 0           # 蓝块中心白，背景黑
    assert binary[80, 280] == 255 and gray[80, 280] > 200             # 白纸在二值图中为白
    if n == 0:
        for name, im in (("frame", frame), ("gray", gray), ("binary", binary), ("mask", mask), ("result", result)):
            cv2.imwrite(os.path.join(args.outdir, f"37_{name}.png"), im)
    n += 1
src.release()
print(f"P5/P6 合成帧 {n} 帧：gray、binary、mask 与原帧同为 480×640；binary、mask 只含 0 和 255；蓝块中心 mask=255、背景 0")
print("P6 蓝色 BGR", BLUE, "→ HSV", cv2.cvtColor(np.uint8([[BLUE]]), cv2.COLOR_BGR2HSV).ravel().tolist())

edge = np.uint8([[[100, 100, 80], [130, 255, 255], [99, 100, 80], [131, 255, 255], [115, 99, 200], [115, 200, 79]]])
r = cv2.inRange(edge, BLUE_LO, BLUE_HI).ravel().tolist()
print("P6 inRange 边界 (100,100,80)(130,255,255)(99,…)(131,…)(S=99)(V=79) →", r)
assert r == [255, 255, 0, 0, 0, 0]

try:
    gray_binary(np.zeros((10, 10), np.uint8)); raise AssertionError("应拒绝单通道输入")
except ValueError as e:
    print("P5 单通道输入被拒绝：", e)

# P7 分辨率：对视频文件请求 1280×720，读回仍是文件本身尺寸（文件不能改分辨率；摄像头需本机实测）
path = os.path.join(args.outdir, "37_synthetic.avi")
assert write_video(path, n=5)
cap = cv2.VideoCapture(path)
rep = request_size(cap, 1280, 720)
ret, fr = cap.read()
cap.release(); os.remove(path)
print("P7 对视频文件请求分辨率：", rep, "；read() 得到", fr.shape[1], "×", fr.shape[0])
assert not rep["effective"]
print("P7 摄像头分辨率设置：云端未连接摄像头，未测试")
print("OK 37")
