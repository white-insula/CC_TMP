# -*- coding: utf-8 -*-
"""GUI 入口的“替身冒烟测试”：用假函数替换 OpenCV 的窗口函数后运行 GUI 程序，只检查代码路径不报错。

不是真正的界面测试：imshow 只记录窗口名；waitKey 直接返回 'q'；setMouseCallback 注册后立即模拟在图片中心点击一次；
createTrackbar/getTrackbarPos 返回初值。真实的窗口、拖动和点击仍需在本机桌面环境录屏时操作。
用法：python gui_smoke.py NN/脚本.py [脚本参数…]
"""
import os
import runpy
import sys
import cv2

shown, bars = [], {}
_img_for_click = {}


def imshow(name, img):
    shown.append(name); _img_for_click[name] = img


def setMouseCallback(name, fn, param=None):
    img = _img_for_click.get(name)
    h, w = (img.shape[:2] if img is not None else (2, 2))
    fn(cv2.EVENT_LBUTTONDOWN, w // 2, h // 2, 0, param)


def createTrackbar(name, win, init, mx, cb):
    bars[name] = init


cv2.imshow = imshow
cv2.namedWindow = lambda *a, **k: None
cv2.setMouseCallback = setMouseCallback
cv2.createTrackbar = createTrackbar
cv2.getTrackbarPos = lambda name, win: bars[name]
cv2.waitKey = lambda *a: ord("q")
cv2.destroyAllWindows = lambda *a: None

script = os.path.abspath(sys.argv[1])
os.chdir(os.path.dirname(script))
sys.path.insert(0, os.path.dirname(script))
sys.argv = [script] + sys.argv[2:]
runpy.run_path(script, run_name="__main__")
print(f"[替身冒烟] {os.path.basename(script)} 运行结束；记录到的窗口: {shown}")
