# -*- coding: utf-8 -*-
# 第 38 讲 P7 录屏：在 P6 基础上，左上角显示当前模式名，底部显示按键说明；单通道画面先转回三通道再写彩色字
# 用法：python p7_overlay.py [--camera 0 --backend dshow]
import argparse
import cv2
import _path  # noqa: F401
from common.sources import add_source_args, open_source
from common.effects import apply_mode, NAMES
from common.keys import update_mode

ap = add_source_args(argparse.ArgumentParser(), "../media/synthetic_test.avi")
args = ap.parse_args()
cap, what = open_source(args)
if not cap.isOpened():
    raise SystemExit(f"打不开：{what}")
mode = 1
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out = apply_mode(cv2.flip(frame, 1), mode)
        if out.ndim == 2: out = cv2.cvtColor(out, cv2.COLOR_GRAY2BGR)
        cv2.putText(out, f"Mode {mode}: {NAMES[mode]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(out, "1-4: switch  q: quit", (10, out.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("effects", out)
        mode, quit_ = update_mode(mode, cv2.waitKey(30) & 0xFF)
        if quit_: break
finally:
    cap.release()
    cv2.destroyAllWindows()
