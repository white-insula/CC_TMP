# -*- coding: utf-8 -*-
"""生成 36—40 讲 GUI 入口的默认输入：media/synthetic_test.avi（XVID，640×480，25 帧/秒，60 帧，约 2.4 秒）。
这是合成技术测试视频，不是用户录屏、摄像头画面或产线视频。编码器不可用时如实报错。
用法：python make_synthetic_video.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common.synth import write_video          # noqa: E402

out = os.path.join(HERE, "media", "synthetic_test.avi")
os.makedirs(os.path.dirname(out), exist_ok=True)
if not write_video(out, n=60, fps=25.0, fourcc="XVID"):
    raise SystemExit("XVID 编码器不可用，未生成测试视频")
print("  media/synthetic_test.avi", os.path.getsize(out), "字节")
