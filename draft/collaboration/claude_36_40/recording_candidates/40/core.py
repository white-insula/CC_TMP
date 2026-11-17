# -*- coding: utf-8 -*-
"""第 40 讲：特效相机 + 截图 + 录像的一帧处理逻辑（GUI 与无界面核对共用）。

每帧顺序：处理得到 out（统一 BGR）→ 录制中则写入 out → 显示用副本上画 REC → 处理按键（s 截图、r 开始/停止、1—4 模式、q 退出）。
· REC 红点和文字只画在显示副本上，不进入保存的视频（与正式示例“先 write 再画”的结果一致）；rec_in_video=True 为扩展，先画后写。
· s 截图保存的是处理后的 out（不含 REC 标记）；只有 imwrite 返回 True 才打印“已保存”。
· 录像尺寸取自实际写入的 out（宽, 高），不是 cap.get 的读数；out 统一转 BGR 再写。
"""
import os
import cv2
import _path  # noqa: F401
from common.effects import apply_mode, to_bgr
from common.keys import update_mode
from common.recorder import Recorder, snapshot_name, safe_snapshot_name, save_snapshot


class State:
    def __init__(self, outdir=".", fourcc="XVID", fps=20.0, rec_in_video=False, safe_names=False):
        self.mode, self.quit = 1, False
        self.rec = Recorder(fourcc, fps)
        self.outdir, self.rec_in_video, self.safe_names = outdir, rec_in_video, safe_names
        self.snapshots, self.videos, self.log = [], [], []


def draw_rec(img):
    w = img.shape[1]
    cv2.circle(img, (w - 30, 30), 10, (0, 0, 255), -1)
    cv2.putText(img, "REC", (w - 90, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


def step(st, frame, key, now=None):
    out = to_bgr(apply_mode(cv2.flip(frame, 1), st.mode))
    if st.rec.recording:
        if st.rec_in_video:
            marked = out.copy(); draw_rec(marked); st.rec.write(marked)
        elif not st.rec.write(out):
            st.log.append(st.rec.last_error)
    shown = out.copy()
    if st.rec.recording:
        draw_rec(shown)
    if key == ord("s"):
        name = safe_snapshot_name(st.outdir, now) if st.safe_names else snapshot_name(now)
        path = os.path.join(st.outdir, name)
        if save_snapshot(out, path):
            st.snapshots.append(path)
    elif key == ord("r"):
        if not st.rec.recording:
            path = os.path.join(st.outdir, snapshot_name(now).replace(".jpg", ".avi"))
            if st.rec.start(path, out):
                st.videos.append(path); st.log.append(f"开始录像 {path}")
            else:
                st.log.append(st.rec.last_error)
        else:
            st.rec.stop(); st.log.append(f"停止录像，共写入 {st.rec.frames} 帧")
    else:
        st.mode, st.quit = update_mode(st.mode, key)
    return shown
