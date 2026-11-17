# -*- coding: utf-8 -*-
# 第 40 讲 P6 录屏：在特效相机里按 s 截图，文件名用当前时间（秒级）；imwrite 成功才打印“已保存”
# 注意：同一秒内按两次 s，正式写法会得到同名文件并覆盖；加 --safe-names 使用“微秒+序号”扩展命名
# 用法：python p6_snapshot.py [--camera 0 --backend dshow] [--safe-names]
import argparse
import cv2
import _path  # noqa: F401
from common.sources import add_source_args, open_source
from core import State, step

ap = add_source_args(argparse.ArgumentParser(), "../media/synthetic_test.avi")
ap.add_argument("--safe-names", action="store_true")
args = ap.parse_args()
cap, what = open_source(args)
if not cap.isOpened():
    raise SystemExit(f"打不开：{what}")
st = State(safe_names=args.safe_names)
key = 255
try:
    while not st.quit:
        ret, frame = cap.read()
        if not ret:
            break
        shown = step(st, frame, key)
        cv2.imshow("camera", shown)
        key = cv2.waitKey(30) & 0xFF
finally:
    st.rec.stop()
    cap.release()
    cv2.destroyAllWindows()
