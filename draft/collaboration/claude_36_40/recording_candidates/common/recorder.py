# -*- coding: utf-8 -*-
"""40 讲截图与录像。

截图：正式写法用秒级时间命名 datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"——同一秒内按两次 s 会得到同名文件，
      后一张覆盖前一张；扩展 safe_snapshot_name 加微秒并在仍然重名时追加序号。
      imwrite 返回 True 后才打印“已保存”。
录像：VideoWriter 创建后检查 isOpened()，成功才 recording=True；尺寸取自实际要写入的第一帧 (宽, 高)；
      单通道画面统一转 BGR 再写（本类始终以 isColor=True 创建）；
      录制中帧尺寸改变：停止并释放当前文件、报告原因（不静默丢帧，也不自动改尺寸）。
      写入帧率是创建时给定的数（如 20.0），与实际采集/处理频率不同时，播放时长和速度会偏差。
"""
import os
from datetime import datetime
import cv2


def snapshot_name(now=None):
    """正式写法（秒级）"""
    return (now or datetime.now()).strftime("%Y%m%d_%H%M%S") + ".jpg"


def safe_snapshot_name(folder=".", now=None):
    """【扩展】微秒 + 序号，保证不覆盖已有文件"""
    base = (now or datetime.now()).strftime("%Y%m%d_%H%M%S_%f")
    name, i = base + ".jpg", 1
    while os.path.exists(os.path.join(folder, name)):
        name = f"{base}_{i}.jpg"; i += 1
    return name


def save_snapshot(img, path):
    ok = cv2.imwrite(path, img)
    if ok:
        print("已保存", path)
    else:
        print("保存失败", path)
    return ok


class Recorder:
    def __init__(self, fourcc="XVID", fps=20.0):
        self.fourcc, self.fps = fourcc, fps
        self.writer, self.size, self.path, self.frames = None, None, None, 0
        self.recording = False
        self.last_error = None

    def start(self, path, first_frame):
        h, w = first_frame.shape[:2]
        wr = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*self.fourcc), self.fps, (w, h))
        if not wr.isOpened():
            self.last_error = f"VideoWriter 打不开（编码器 {self.fourcc} 或路径 {path} 不可用）"
            wr.release()
            return False
        self.writer, self.size, self.path, self.frames, self.recording = wr, (w, h), path, 0, True
        return True

    def write(self, frame):
        if not self.recording:
            return False
        f = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR) if frame.ndim == 2 else frame
        if (f.shape[1], f.shape[0]) != self.size:
            self.last_error = f"帧尺寸从 {self.size} 变成 {(f.shape[1], f.shape[0])}，已停止录制"
            self.stop()
            return False
        self.writer.write(f); self.frames += 1
        return True

    def stop(self):
        if self.writer is not None:
            self.writer.release()
        self.writer, self.recording = None, False
