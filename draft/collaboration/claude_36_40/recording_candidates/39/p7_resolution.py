# -*- coding: utf-8 -*-
# 第 39 讲 P7 录屏：卡通模式下比较分辨率；--half 时先 resize 缩小一半再处理（显示时放回原尺寸）
# 用法：python p7_resolution.py --camera 0 --backend dshow --width 1280 --height 720 [--half]
#       python p7_resolution.py --half                  （默认合成测试视频；文件不能改分辨率）
# FPS 用最近 10 帧“帧数 ÷ 总耗时”平滑（注明：不是瞬时值的平均）
import argparse
import time
import cv2
import _path  # noqa: F401
from common.sources import add_source_args, open_source, request_size
from common.effects import cartoon
from common.fps import FpsMeter

ap = add_source_args(argparse.ArgumentParser(), "../media/synthetic_test.avi")
ap.add_argument("--width", type=int); ap.add_argument("--height", type=int)
ap.add_argument("--half", action="store_true")
args = ap.parse_args()
cap, what = open_source(args)
if not cap.isOpened():
    raise SystemExit(f"打不开：{what}")
if args.width and args.height:
    print("分辨率设置：", request_size(cap, args.width, args.height))
meter = FpsMeter(time.time, window=10)
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if args.half:
            small = cv2.resize(frame, None, fx=0.5, fy=0.5)
            out = cv2.resize(cartoon(small), (frame.shape[1], frame.shape[0]))
        else:
            out = cartoon(frame)
        meter.tick()
        f = meter.frames_over_time()
        cv2.putText(out, f"{frame.shape[1]}x{frame.shape[0]} {'half' if args.half else 'full'}  FPS(10): {f or 0:.1f}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("resolution", out)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
