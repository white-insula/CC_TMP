# -*- coding: utf-8 -*-
# 第 40 讲 P7 录屏：按 r 开始 / 停止录像（XVID + .avi，写入帧率 20.0），录制中画面右上角显示 REC；s 截图；1—4 切换；q 退出
# VideoWriter 打开成功才进入录制；无论 q、视频结束还是出错，都会 release
# 用法：python p7_record.py [--camera 0 --backend dshow] [--fourcc mp4v] [--rec-in-video]
#   --rec-in-video 为扩展：把 REC 标记也写进视频（正式示例只显示在窗口里）
import argparse
import cv2
import _path  # noqa: F401
from common.sources import add_source_args, open_source
from core import State, step

ap = add_source_args(argparse.ArgumentParser(), "../media/synthetic_test.avi")
ap.add_argument("--fourcc", default="XVID")
ap.add_argument("--fps", type=float, default=20.0)
ap.add_argument("--rec-in-video", action="store_true")
args = ap.parse_args()
cap, what = open_source(args)
if not cap.isOpened():
    raise SystemExit(f"打不开：{what}")
st = State(fourcc=args.fourcc, fps=args.fps, rec_in_video=args.rec_in_video)
key = 255
try:
    while not st.quit:
        ret, frame = cap.read()
        if not ret:
            break
        shown = step(st, frame, key)
        while st.log:
            print(st.log.pop(0))
        cv2.imshow("camera", shown)
        key = cv2.waitKey(30) & 0xFF
finally:
    st.rec.stop()                 # 正在录制时也会释放，文件可正常打开
    cap.release()
    cv2.destroyAllWindows()
