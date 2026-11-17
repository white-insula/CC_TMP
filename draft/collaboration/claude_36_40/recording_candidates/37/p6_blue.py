# -*- coding: utf-8 -*-
# 第 37 讲 P6 录屏：每帧转 HSV → inRange 蓝色 (100,100,80)—(130,255,255) → bitwise_and 抠出蓝色
# 用法：python p6_blue.py [--camera 0 --backend dshow]     （默认播放合成测试视频，其中有一个移动的蓝色方块）
import argparse
import cv2
import _path  # noqa: F401
from common.sources import add_source_args, open_source

ap = add_source_args(argparse.ArgumentParser(), "../media/synthetic_test.avi")
args = ap.parse_args()

cap, what = open_source(args)
if not cap.isOpened():
    raise SystemExit(f"打不开：{what}")
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, (100, 100, 80), (130, 255, 255))
        result = cv2.bitwise_and(frame, frame, mask=mask)
        cv2.imshow("frame", frame); cv2.imshow("mask", mask); cv2.imshow("result", result)
        if cv2.waitKey(30) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
