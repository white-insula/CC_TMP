# -*- coding: utf-8 -*-
"""第 32 讲无界面核对：生成二维码 → 识别 → 比对内容（含中文）；另测透视贴图、条码检测器是否可用。
不连接摄像头、不测试手机扫码。用法：python check_headless.py [--outdir 输出目录]
"""
import argparse
import os
import cv2
import numpy as np
from core import CONTENT, make_qr, read_qr, draw_qr

ap = argparse.ArgumentParser()
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)

path = make_qr(CONTENT, os.path.join(args.outdir, "part.png"))
img = cv2.imread(path)
data, points = read_qr(img)
print(f"P5 生成 {os.path.basename(path)} {img.shape}")
print(f"P7 识别内容：{data!r}")
print(f"P7 与原文完全一致（含中文“批次A”“质检合格”）：{data == CONTENT}")
assert data == CONTENT
out, font = draw_qr(img, data, points)
print("P7 四个角点:", points.astype(int).reshape(-1, 2).tolist(), "；图上中文字体:", font)
cv2.imwrite(os.path.join(args.outdir, "32_p7_read.png"), out)

# 透视贴到灰色背景上（合成），看是否仍能识别
q = cv2.resize(img, (240, 240), interpolation=cv2.INTER_NEAREST)
scene = np.full((480, 720, 3), (150, 150, 145), np.uint8)
M = cv2.getPerspectiveTransform(np.float32([[0, 0], [240, 0], [240, 240], [0, 240]]),
                                np.float32([[380, 110], [640, 150], [620, 400], [360, 370]]))
w = cv2.warpPerspective(q, M, (720, 480)); m = cv2.warpPerspective(np.full((240, 240), 255, np.uint8), M, (720, 480))
scene[m > 0] = w[m > 0]
d2, p2 = read_qr(scene)
print(f"P7 扩展：合成场景中斜贴的二维码识别结果 {d2!r}（一致：{d2 == CONTENT}）")
cv2.imwrite(os.path.join(args.outdir, "32_p7_perspective_synthetic.png"), draw_qr(scene, d2, p2)[0] if d2 else scene)

# P8 条码检测器：只检查本环境是否有该类，不在云端做条码解码承诺
print("P8 cv2.barcode.BarcodeDetector 可用：", hasattr(cv2, "barcode") and hasattr(cv2.barcode, "BarcodeDetector"))
print("P8 Data Matrix：OpenCV QRCodeDetector 不解 DM 码；本环境未安装 DM 解码库，未测试")
print("OK 32")
