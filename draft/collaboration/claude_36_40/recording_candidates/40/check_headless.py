# -*- coding: utf-8 -*-
"""第 40 讲无界面核对：用模拟键序列驱动同一套 step()（逻辑测试，不是真实键盘、窗口或摄像头测试），
真实写入 XVID 视频后重新解码核对；另测命名冲突、写入器打开失败、录制中尺寸变化、异常退出时释放。
用法：python check_headless.py [--outdir 输出目录]
"""
import argparse
import os
import shutil
from datetime import datetime, timedelta
import cv2
import numpy as np
import _path  # noqa: F401
from common.synth import SyntheticSource
from common.recorder import Recorder, save_snapshot, safe_snapshot_name, snapshot_name
from core import State, step

ap = argparse.ArgumentParser()
ap.add_argument("--outdir", default="check_out")
args = ap.parse_args()
work = os.path.join(args.outdir, "40_session")
shutil.rmtree(work, ignore_errors=True); os.makedirs(work)


def run(keys, rec_in_video=False, safe=False, n=40, sub="a"):
    d = os.path.join(work, sub); os.makedirs(d, exist_ok=True)
    st = State(outdir=d, rec_in_video=rec_in_video, safe_names=safe)
    src = SyntheticSource(n=n)
    base = datetime(2026, 11, 17, 9, 30, 0)
    k, key = 0, 255
    try:
        while not st.quit:
            ret, frame = src.read()
            if not ret:
                break
            now = base + timedelta(seconds=0.04 * k)             # 模拟时间：25 帧/秒
            step(st, frame, key, now)
            key = keys.get(k, 255); k += 1
    finally:
        st.rec.stop(); src.release()
    return st


def decode(path):
    c = cv2.VideoCapture(path); fr = []
    while True:
        r, f = c.read()
        if not r:
            break
        fr.append(f)
    fps = c.get(cv2.CAP_PROP_FPS); c.release()
    return fr, fps


# 键在“读取第 k 帧之后”生效，即作用于第 k+1 帧（与 GUI 中 waitKey 在显示之后相同）
keys = {2: ord("s"), 3: ord("s"), 5: ord("4"), 6: ord("s"), 8: ord("r"), 30: ord("r"),
        32: ord("2"), 33: ord("r"), 36: ord("r"), 38: ord("q")}
st = run(keys)
print("会话日志:", st.log)
files = sorted(os.listdir(os.path.join(work, "a")))
print("生成文件:", files)
print(f"s 按了 3 次，正式秒级命名只得到 {len([f for f in files if f.endswith('.jpg')])} 张（三次都在模拟时间第 0 秒内，同名文件后一张覆盖前一张）")
assert len(st.snapshots) == 3 and len([f for f in files if f.endswith(".jpg")]) == 1
# 两段录像：r@8→r@30 写第 9—30 帧共 22 帧（卡通）；r@33→r@36 写第 34—36 帧共 3 帧（灰度转 BGR）
vids = st.videos
print("录像文件:", [os.path.basename(v) for v in vids], "（模拟时间第 0 秒与第 1 秒开始，秒级命名不同名）")
fr_a, fps_a = decode(vids[0]); fr_b, fps_b = decode(vids[1])
print(f"重新解码：第一段 {len(fr_a)} 帧、第二段 {len(fr_b)} 帧，尺寸 {fr_a[0].shape} / {fr_b[0].shape}，写入帧率 {fps_a}，"
      f"按写入帧率换算时长 {len(fr_a) / fps_a:.2f} 秒 / {len(fr_b) / fps_b:.2f} 秒（不是采集时长：模拟采集为 25 帧/秒）")
assert len(fr_a) == 22 and len(fr_b) == 3 and fps_a == fps_b == 20.0
assert all(f.shape == (480, 640, 3) and f.mean() > 10 for f in fr_a + fr_b)
gray_like = all(np.abs(f[..., 0].astype(int) - f[..., 2].astype(int)).mean() < 3 for f in fr_b)
print("第二段（灰度模式）以三通道写入，三个通道基本相同：", gray_like)
assert gray_like
st2 = run({8: ord("r"), 30: ord("r"), 38: ord("q")}, sub="b")
fr2, fps2 = decode(st2.videos[0])
red = lambda f: int(((f[20:41, 600:621, 2] > 180) & (f[20:41, 600:621, 1] < 80)).sum())
print(f"第 9—30 帧单段录像：{len(fr2)} 帧，写入帧率 {fps2}，时长 {len(fr2) / fps2:.2f} 秒；REC 位置红色像素（每帧）{[red(f) for f in fr2[:3]]}…（正式：REC 不进视频）")
assert len(fr2) == 22 and max(red(f) for f in fr2) == 0
st3 = run({8: ord("r"), 30: ord("r"), 38: ord("q")}, rec_in_video=True, sub="c")
fr3, _ = decode(st3.videos[0])
print(f"扩展 --rec-in-video：REC 位置红色像素 {[red(f) for f in fr3[:3]]}…（标记进入视频）")
assert min(red(f) for f in fr3) > 50

st4 = run({2: ord("s"), 3: ord("s"), 38: ord("q")}, safe=True, sub="d")
print("扩展安全命名：", [os.path.basename(p) for p in st4.snapshots])
assert len(set(st4.snapshots)) == 2 and all(os.path.exists(p) for p in st4.snapshots)

# 写入器打不开：不存在的目录 / 不存在的编码器
for path, cc in ((os.path.join(work, "no_dir", "x.avi"), "XVID"), (os.path.join(work, "x.avi"), "ZZZZ")):
    r = Recorder(cc, 20.0)
    ok = r.start(path, np.zeros((480, 640, 3), np.uint8))
    print(f"VideoWriter({os.path.relpath(path, work)}, {cc})：start={ok}，recording={r.recording}，{r.last_error}")
    assert not ok and not r.recording
# 录制中尺寸变化：停止并报告，不静默丢帧
r = Recorder("XVID", 20.0); p = os.path.join(work, "size_change.avi")
r.start(p, np.zeros((480, 640, 3), np.uint8))
for _ in range(3): r.write(np.full((480, 640, 3), 128, np.uint8))
ok = r.write(np.full((240, 320, 3), 128, np.uint8))
print(f"录制中帧尺寸变化：write={ok}，recording={r.recording}，{r.last_error}；文件解码 {len(decode(p)[0])} 帧")
assert not ok and not r.recording and len(decode(p)[0]) == 3
# 异常退出时 finally 仍会释放
r = Recorder("XVID", 20.0); p = os.path.join(work, "exception.avi")
try:
    r.start(p, np.zeros((480, 640, 3), np.uint8))
    for i in range(5): r.write(np.full((480, 640, 3), 40 * i, np.uint8))
    raise RuntimeError("模拟处理中途出错")
except RuntimeError:
    pass
finally:
    r.stop()
print(f"模拟异常后 finally 释放：文件解码 {len(decode(p)[0])} 帧")
assert len(decode(p)[0]) == 5
# imwrite 失败
ok = save_snapshot(np.zeros((10, 10, 3), np.uint8), os.path.join(work, "no_dir", "x.jpg"))
assert ok is False
print("录像 fourcc 测试环境：opencv", cv2.__version__, "（FFmpeg 后端）；用户 Windows 电脑上的编码器需本机实测")
print("OK 40")
