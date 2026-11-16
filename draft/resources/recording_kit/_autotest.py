# -*- coding: utf-8 -*-
"""录屏工程包 · 自动预演器(只给检查用,录屏时不用它)。

用法:python _autotest.py NN/某段.py [--cam 视频文件] [--keys 键序列] [--frames N]
  - 不改录屏程序本身;运行时把 cv2.imshow 换成“记下画面”,cv2.waitKey 换成自动按键,
    把摄像头 VideoCapture(数字) 换成读 --cam 指定的视频(没给就用 assets/cam_room.mp4);
  - 运行结束把每个窗口最后一帧存到 _out/NN/,并打印窗口清单和程序输出,供核对讲解里描述的现象。
  - --keys:按第几次 waitKey 返回什么键,如 "5:2,10:3,20:q" 表示第 5 次按 2、第 10 次按 3、第 20 次按 q;
    没安排的调用返回 255(无按键);到 --frames 次还没退出就自动按 q。
"""
import argparse, os, runpy, sys, builtins
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("script"); ap.add_argument("--cam", default=os.path.join(HERE, "assets", "cam_room.mp4"))
ap.add_argument("--keys", default=""); ap.add_argument("--frames", type=int, default=60)
a = ap.parse_args()
script = os.path.abspath(a.script)
out = os.path.join(HERE, "_out", os.path.basename(os.path.dirname(script)))
os.makedirs(out, exist_ok=True)
stem = os.path.splitext(os.path.basename(script))[0]

keys = {int(k): (27 if v == "esc" else 32 if v == "space" else 13 if v == "enter" else ord(v))
        for k, v in (p.split(":") for p in a.keys.split(",") if p)}
shown, calls, trackbars, mouse = {}, [0], {}, {}

def imshow(name, img):
    shown[name] = img.copy()

def waitKey(delay=0):
    calls[0] += 1
    n = calls[0]
    if n in keys: return keys[n]
    if delay == 0 or n >= a.frames: return ord("q")
    return 255

_VC = cv2.VideoCapture
class VideoCapture(_VC):
    def __init__(self, src=0, *rest):
        if isinstance(src, int):
            print(f"[autotest] 摄像头 {src} → 视频 {os.path.basename(a.cam)}")
            super().__init__(a.cam)
        else:
            super().__init__(src, *rest)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as _plt
def _plt_show(*x, **k):
    n = len([f for f in os.listdir(out) if f.startswith(stem + "__plot")])
    _plt.savefig(os.path.join(out, f"{stem}__plot{n + 1}.png"), dpi=80); _plt.close("all")
    print(f"[autotest] plt.show() → 存为 {stem}__plot{n + 1}.png")
_plt.show = _plt_show

cv2.imshow = imshow; cv2.waitKey = waitKey; cv2.VideoCapture = VideoCapture
cv2.destroyAllWindows = lambda: None; cv2.destroyWindow = lambda *x: None
cv2.namedWindow = lambda *x, **k: None
cv2.createTrackbar = lambda name, win, val, mx, cb=None: trackbars.__setitem__((name, win), val)
cv2.getTrackbarPos = lambda name, win: trackbars.get((name, win), 0)
cv2.setMouseCallback = lambda win, cb, *x: mouse.__setitem__(win, cb)

os.chdir(os.path.dirname(script)); sys.path.insert(0, os.path.dirname(script))
sys.argv = [script]
code = 0
try:
    runpy.run_path(script, run_name="__main__")
except SystemExit as e:
    code = e.code
except Exception as e:
    import traceback; traceback.print_exc(); code = "EXCEPTION"
for name, img in shown.items():
    fn = os.path.join(out, f"{stem}__{''.join(ch if ch.isalnum() else '_' for ch in name)}.png")
    cv2.imencode(".png", img)[1].tofile(fn)
print(f"[autotest] 结束 code={code}  waitKey 调用 {calls[0]} 次  窗口: " +
      ", ".join(f"{n} {getattr(i, 'shape', '')}" for n, i in shown.items()))
if mouse: print("[autotest] 注册了鼠标回调:", list(mouse))
