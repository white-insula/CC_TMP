# -*- coding: utf-8 -*-
"""第 38 讲无界面核对：模拟键序列验证 mode 状态机（逻辑测试，不是真实键盘/窗口测试）；四种模式输出与叠加文字。
用法：python check_headless.py [--outdir 输出目录]
"""
import argparse
import os
import cv2
import numpy as np
import _path  # noqa: F401
from common.synth import SyntheticSource
from common.effects import apply_mode, overlay, cartoon, NAMES
from common.keys import update_mode

ap = argparse.ArgumentParser()
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
os.makedirs(args.outdir, exist_ok=True)

NOKEY = -1 & 0xFF
print("没按键：waitKey 返回 -1，& 0xFF 后 =", NOKEY, "；ord('q') =", ord("q"), "；Esc = 27，空格 = 32")
assert NOKEY == 255
seq = [NOKEY, ord("2"), NOKEY, NOKEY, ord("x"), ord("4"), ord("r"), ord("r"), NOKEY, ord("3"), 32, ord("1"), ord("q"), ord("2")]
mode, trace = 1, []
for k in seq:
    mode, q = update_mode(mode, k)
    trace.append((k, mode, q))
    if q:
        break
print("键序列 → mode：", [(("无键" if k == 255 else chr(k) if 32 < k < 127 else str(k)), m) for k, m, _ in trace])
assert [m for _, m, _ in trace] == [1, 2, 2, 2, 2, 4, 4, 4, 4, 3, 3, 1, 1] and trace[-1][2] is True
print("  按 2 后无键、按 x、按 r 都保持原模式；q 退出后不再处理后续按键")

src = SyntheticSource(n=1)
frame = cv2.flip(src.read()[1], 1)
outs = {}
for m in (1, 2, 3, 4):
    o = apply_mode(frame, m)
    outs[m] = o
    print(f"mode {m} {NAMES[m]}：shape {o.shape}，dtype {o.dtype}")
assert outs[2].ndim == 2 and outs[3].ndim == 2 and outs[1].ndim == 3 and outs[4].ndim == 3
assert set(np.unique(outs[3]).tolist()) <= {0, 255} and (outs[3] == 255).mean() > 0.8      # 白底黑线
assert (outs[1] == frame).all()                                                          # mode 1 就是镜像后的原图
tiles = []
for m in (1, 2, 3, 4):
    o = overlay(outs[m], m)
    assert o.ndim == 3
    tiles.append(cv2.resize(o, (320, 240)))
mosaic = np.vstack([np.hstack(tiles[:2]), np.hstack(tiles[2:])])
cv2.imwrite(os.path.join(args.outdir, "38_modes_overlay.png"), mosaic)
print("P7 叠加文字：四种模式都先转成 BGR 再写字，输出均为三通道")
print("卡通处理链：medianBlur(5) → Canny(50,50) → bilateralFilter(9,300,300) → 与反色边缘按位与")
print("本机未测：窗口焦点、中文输入法、真实键盘与摄像头")
print("OK 38")
