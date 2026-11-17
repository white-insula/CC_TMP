# -*- coding: utf-8 -*-
# 第 36 讲 P7 录屏：播放视频文件（只把 0 换成文件名，不带摄像头专用的 CAP_DSHOW）
# 读出帧率，读不到（≤0、NaN、无穷大）按示例 25；waitKey 等 max(1, int(1000 / fps)) 毫秒——只是“近似原速”，处理耗时会让播放更慢
# 用法：python p7_play_file.py [--input test.mp4]      （默认是合成测试视频 ../media/synthetic_test.avi）
import argparse
import cv2
import _path  # noqa: F401
from common.sources import playback_delay

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="../media/synthetic_test.avi")
args = ap.parse_args()

cap = cv2.VideoCapture(args.input)
if not cap.isOpened():
    print("视频打不开：检查文件名、路径，或文件是否损坏")
    raise SystemExit(1)
delay, fps = playback_delay(cap.get(cv2.CAP_PROP_FPS))
total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
print(f"帧率 {fps}，每帧等待 {delay} 毫秒，文件标称帧数 {total:.0f}")
n = 0
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        n += 1
        cv2.imshow("video", frame)
        if cv2.waitKey(delay) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
print(f"共读到 {n} 帧" + ("（读到结尾）" if total > 0 and n >= total else "（提前停止：按了 q，或文件可能不完整）"))
