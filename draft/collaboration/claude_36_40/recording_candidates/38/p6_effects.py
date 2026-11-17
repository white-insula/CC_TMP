# -*- coding: utf-8 -*-
# 第 38 讲 P6 录屏：镜像 → mode 1 原图 / 2 灰度 / 3 素描 / 4 卡通 → 按 1—4 切换（保持到下次按键）→ q 退出
# 用法：python p6_effects.py [--camera 0 --backend dshow]   （默认播放合成测试视频，播完自动退出）
# 本机注意：先用鼠标点一下图像窗口让它获得焦点；输入法切到英文
import argparse
import cv2
import _path  # noqa: F401
from common.sources import add_source_args, open_source
from common.effects import cartoon

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
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if mode == 2: out = gray
        elif mode == 3: out = 255 - cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 50, 150)
        elif mode == 4: out = cartoon(frame)          # 参考 [PI]EXP-opencv-edge/edge_cartoon.py
        else: out = frame
        cv2.imshow("effects", out)
        key = cv2.waitKey(30) & 0xFF
        if key in (ord("1"), ord("2"), ord("3"), ord("4")): mode = key - ord("0")
        elif key == ord("q"): break
finally:
    cap.release()
    cv2.destroyAllWindows()
