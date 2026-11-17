# -*- coding: utf-8 -*-
# 第 37 讲 P5 录屏：读帧 → 灰度 → 大津法二值化 → frame / gray / binary 三个窗口同时显示，按 q 退出
# 用法：python p5_gray_binary.py                       （默认播放合成测试视频）
#       python p5_gray_binary.py --camera 0 --backend dshow --width 640 --height 480
import argparse
import cv2
import _path  # noqa: F401
from common.sources import add_source_args, open_source, request_size

ap = add_source_args(argparse.ArgumentParser(), "../media/synthetic_test.avi")
ap.add_argument("--width", type=int); ap.add_argument("--height", type=int)
args = ap.parse_args()

cap, what = open_source(args)
if not cap.isOpened():
    raise SystemExit(f"打不开：{what}")
if args.width and args.height:
    print("分辨率设置：", request_size(cap, args.width, args.height))   # 以读回值为准
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cv2.imshow("frame", frame); cv2.imshow("gray", gray); cv2.imshow("binary", binary)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
