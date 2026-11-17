# -*- coding: utf-8 -*-
# 第 39 讲 P6 录屏：在特效相机上显示 FPS（正式写法 time.time()）；切换 4 种模式观察变化
# 计时范围：本次 now 与上次 now 之间——读帧、处理、显示、waitKey 等待全部算在内，是“整个循环的吞吐”
# 用法：python p6_show_fps.py [--camera 0 --backend dshow] [--clock perf]   （--clock perf 为扩展：time.perf_counter）
import argparse
import time
import cv2
import _path  # noqa: F401
from common.sources import add_source_args, open_source
from common.effects import apply_mode, to_bgr, NAMES
from common.keys import update_mode

ap = add_source_args(argparse.ArgumentParser(), "../media/synthetic_test.avi")
ap.add_argument("--clock", choices=["time", "perf"], default="time")
args = ap.parse_args()
clock = time.time if args.clock == "time" else time.perf_counter
cap, what = open_source(args)
if not cap.isOpened():
    raise SystemExit(f"打不开：{what}")
mode, fps = 1, 0.0
prev = clock()
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        out = to_bgr(apply_mode(cv2.flip(frame, 1), mode))
        now = clock()
        if now - prev > 0:                       # 时钟精度不足时两次读数可能相同，跳过这一帧的计算
            fps = 1 / (now - prev)
        prev = now
        cv2.putText(out, f"FPS: {fps:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.putText(out, f"Mode {mode}: {NAMES[mode]}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("fps", out)
        mode, quit_ = update_mode(mode, cv2.waitKey(1) & 0xFF)
        if quit_: break
finally:
    cap.release()
    cv2.destroyAllWindows()
