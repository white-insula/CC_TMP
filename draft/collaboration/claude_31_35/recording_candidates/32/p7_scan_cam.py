# -*- coding: utf-8 -*-
# 第 32 讲 P7 录屏（后半）：摄像头实时扫码，手机上的二维码对准摄像头，按 q 退出
# ⚠ 本机入口：云端没有连接摄像头，也没有测试手机扫码；摄像头编号打不开就换 1、2（第 36 讲）
import argparse
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("--cam", type=int, default=0)
args = ap.parse_args()

cap = cv2.VideoCapture(args.cam)
det = cv2.QRCodeDetector()
while True:
    ok, frame = cap.read()
    if not ok:
        print("读不到摄像头画面，检查摄像头编号"); break
    data, points, _ = det.detectAndDecode(frame)
    if data:
        pts = points.astype(int).reshape(-1, 2)
        cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
        print(data)
    cv2.imshow("scan", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()
