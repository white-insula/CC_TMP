# -*- coding: utf-8 -*-
# 第 36 讲 P6 录屏：打开摄像头 → isOpened 检查 → 打印实际宽、高、帧率 → 读帧循环 → 按 q 退出 → 释放
# 用法：python p6_camera.py --camera 0 --backend dshow      （Windows 上脚本建议 CAP_DSHOW；打不开或纯色再试 msmf / default）
# 不给 --camera 时不会打开任何摄像头。云端没有连接摄像头，本程序未在真实摄像头上测试。
import argparse
import cv2
import _path  # noqa: F401
from common.sources import BACKENDS, describe

ap = argparse.ArgumentParser()
ap.add_argument("--camera", type=int, default=None)
ap.add_argument("--backend", choices=sorted(BACKENDS), default="dshow")
args = ap.parse_args()
if args.camera is None:
    raise SystemExit("请用 --camera 0（或 1、2）指定摄像头编号；本程序默认不打开摄像头")

cap = cv2.VideoCapture(args.camera, BACKENDS[args.backend])
if not cap.isOpened():
    print("摄像头打开失败：换编号、关闭占用摄像头的软件、检查系统相机权限、换 --backend")
    raise SystemExit(1)
try:
    print("实际读回：", describe(cap))              # 宽、高、帧率；读不出帧率时显示 0，属正常
    while True:
        ret, frame = cap.read()
        if not ret:
            print("读取失败（摄像头断开或被占用）"); break
        cv2.imshow("camera", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
