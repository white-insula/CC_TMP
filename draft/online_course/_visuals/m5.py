# -*- coding: utf-8 -*-
"""模块五 让摄像头动起来(36–41)配图。"""
import cv2, numpy as np, time
from collections import deque
from _vis import *
from m4 import mask_of

AMB = (0, 169, 242)


def _cartoon(f):
    g = cv2.medianBlur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), 7)
    e = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
    c = cv2.bilateralFilter(f, 9, 75, 75)
    return cv2.bitwise_and(c, c, mask=e)


def _effects(f):
    g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
    return [(f, "按 1：原画面"), (g, "按 2：灰度"), (255 - cv2.Canny(g, 60, 150), "按 3：边缘"), (_cartoon(f), "按 4：卡通")]


def ball_frames(n=60, w=800, h=480):
    """合成视频:红球沿曲线滚过工作台(用于实时颜色追踪演示)。"""
    bg, _ = parts_scene([("square", "blue", (650, 120), 90, 20, None), ("triangle", "yellow", (130, 380), 80, 0, None)], w=w, h=h, noise=0)
    rng = np.random.default_rng(0)
    for k in range(n):
        t = k / (n - 1)
        x = int(80 + t * (w - 160)); y = int(h / 2 + 140 * np.sin(t * 2 * np.pi * 1.2))
        f = bg.copy().astype(np.float32)
        m = np.zeros((h, w), np.uint8); cv2.circle(m, (x, y), 34, 255, -1, cv2.LINE_AA)
        mf = m.astype(np.float32)[..., None] / 255
        f = f * (1 - mf) + np.array((40, 40, 210), np.float32) * mf
        f += rng.normal(0, 4, f.shape)
        yield np.clip(f, 0, 255).astype(np.uint8)


def track_demo(n=60):
    pts = deque(maxlen=30); out = None
    for f in ball_frames(n):
        m = mask_of(cv2.cvtColor(f, cv2.COLOR_BGR2HSV), "red")
        cs = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        out = f.copy()
        if cs:
            c = max(cs, key=cv2.contourArea); x, y, w, h = cv2.boundingRect(c)
            M = cv2.moments(c); cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
            pts.appendleft((cx, cy)); cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 3)
        for i in range(1, len(pts)):
            cv2.line(out, pts[i - 1], pts[i], AMB, int(np.sqrt(30 / i) * 3))
    return out, m


def v36():
    with Lesson("36") as L:
        fs = frames_of("room", [0.1, 0.3, 0.5, 0.7, 0.9])
        strip = row([border(text(fit(f, h=360), f"第 {int(t * 139)} 帧", (12, 12), 24, (255, 255, 255), (55, 42, 31), 4))
                     for f, t in zip(fs, [0.1, 0.3, 0.5, 0.7, 0.9])], 14)
        L.add("视频 = 连续的图片", strip, "一段 139 帧、约 27 帧/秒的视频，就是一张张图片快速翻过（[PI]test.mp4）")
        f = fit(frame_of("room", 0.5), h=480)
        f = text(f, "frame 70 / 139", (12, 12), 26, (255, 255, 255), (55, 42, 31), 5)
        L.add("实操二", f, "VideoCapture 读视频文件：每次 read() 取出一帧显示")


def v37():
    with Lesson("37") as L:
        f = fit(frame_of("class", 0.3), w=560)
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY); _, b = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        L.add("实操一", row(tagged([(f, "读到的一帧"), (g, "实时灰度"), (b, "实时二值化")], 22)), "在读帧循环的中间，对每一帧做处理（[OC]Body_Detct 教室录像）")
        fr = list(ball_frames(30))[12]; m = mask_of(cv2.cvtColor(fr, cv2.COLOR_BGR2HSV), "red")
        L.add("实操二", row(tagged([(fr, "画面"), (m, "红色掩膜"), (cv2.bitwise_and(fr, fr, mask=m), "只留红色")], 22)), "把第 27 讲的颜色提取放进循环，每一帧都提一次")


def v38():
    with Lesson("38") as L:
        f = fit(frame_of("class", 0.3), w=560)
        L.add("课程导入", grid(tagged(_effects(f), 22), 2), "一个程序，按键切换四种实时特效")
        L.add("实操一", grid(tagged(_effects(f), 22), 2), "mode 变量记住当前模式，按 1–4 改 mode")
        o = _cartoon(f)
        o = text(o, "模式：卡通 | 1 原画 2 灰度 3 边缘 4 卡通 | q 退出", (10, 10), 20, (255, 255, 255), (55, 42, 31), 5)
        L.add("实操二", fit(o, w=900), "把当前模式和按键提示写在画面上，用户一看就会")


def v39():
    plt = plt_setup()
    with Lesson("39") as L:
        f = frame_of("class", 0.3)
        res = []
        for name, (w, h) in (("640×480", (640, 480)), ("1280×720", (1280, 720))):
            im = cv2.resize(f, (w, h)); t0 = time.perf_counter(); n = 20
            for _ in range(n): _cartoon(im)
            res.append((name, n / (time.perf_counter() - t0)))
        im = cv2.resize(f, (1280, 720)); t0 = time.perf_counter()
        for _ in range(20): _cartoon(cv2.resize(im, None, fx=0.5, fy=0.5))
        res.append(("1280×720\n先缩小一半", 20 / (time.perf_counter() - t0)))
        fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=120)
        bars = ax.bar([r[0] for r in res], [r[1] for r in res], color=["#0E7C72", "#6B7785", "#F2A900"])
        for b_, (_, v) in zip(bars, res):
            ax.text(b_.get_x() + b_.get_width() / 2, v, f"{v:.0f} FPS", ha="center", va="bottom", fontsize=14)
        ax.set_ylabel("卡通模式帧率", fontsize=13); ax.spines[["top", "right"]].set_visible(False); ax.tick_params(labelsize=12)
        ax.set_title("本机实测（i7-1165G7 笔记本，只计处理耗时）", fontsize=13)
        L.add("实操二", fig2img(fig), "分辨率越高越慢；先缩小再处理，速度明显回升（数值以各自电脑实测为准）")
        o = fit(f, w=800); o = text(o, f"FPS: {res[0][1]:.1f}", (14, 14), 34, (0, 255, 0), (0, 0, 0), 6)
        L.add("实操一", o, "每帧用 time.time() 计时，FPS = 1 ÷ 这一帧用的秒数")


def v41():
    with Lesson("41") as L:
        out, m = track_demo()
        L.add("案例导入", out, "红球的追踪框 + 彩色拖尾轨迹（合成视频，OpenCV 实际运行）")
        L.add("实操二", out, "deque(maxlen=30) 存最近 30 个中心点，越新的线越粗")
        L.add("实操一", row(tagged([(m, "红色掩膜"), (out, "取最大轮廓画框")], 22)), "每帧：HSV → inRange → 开运算 → 最大轮廓 → 外接框")
