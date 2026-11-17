# -*- coding: utf-8 -*-
"""36-P4《视频 = 连续的图片》候选：翻页动画 GIF。

合成教学样本：同一个橙色小球在合成传送带上匀速右移，共 12 帧原始帧（320×200），每帧印帧号；
按“标称 30 帧/秒”标注时间 t = k / 30 秒（这是概念说明，不是测得的帧率）。
GIF 分两段：
  ① 慢速讲解：每帧停 0.7 秒，上方胶片条高亮当前帧，写出帧号与标称时间；
  ② 快速连播：每帧 0.04 秒（GIF 时间单位是 1/100 秒，0.033 秒无法精确表达，所以取 0.04 秒，即约 25 帧/秒），
     实际播放快慢还取决于播放软件，不是实测帧率。

输出（previews/36/）：
  36-p4-anim-连续帧翻页动画_候选.gif
  36-p4-anim-关键帧拼图_审阅用.png
"""
import cv2
import numpy as np
from _common import *

L = "36"
N = 12
FW, FH = 320, 200
NOMINAL_FPS = 30


def make_frames():
    frames = []
    for k in range(N):
        f = np.full((FH, FW, 3), (205, 210, 205), np.uint8)
        cv2.rectangle(f, (0, 120), (FW, 160), (90, 95, 95), -1)                  # 传送带
        for x in range(0, FW, 40):
            cv2.line(f, (x, 120), (x, 160), (120, 125, 125), 2)                 # 固定刻线（不随帧移动，作参照）
        cx = 30 + k * 23
        cv2.circle(f, (cx, 100), 20, (30, 130, 245), -1, cv2.LINE_AA)             # 橙色小球
        cv2.putText(f, f"#{k + 1:02d}", (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (40, 40, 40), 2)
        frames.append(f)
    return frames


def strip(frames, cur):
    tw, th = 96, 60
    c = canvas(N * (tw + 6), th + 34)
    for k, f in enumerate(frames):
        x = k * (tw + 6)
        paste(c, cv2.resize(f, (tw, th), interpolation=cv2.INTER_AREA), x, 0)
        colr = RED if k == cur else (190, 190, 190)
        cv2.rectangle(c, (x - 2, 0), (x + tw + 1, th + 1), colr, 3 if k == cur else 1)
        c = text(c, f"第{k + 1}帧", (x + tw // 2, th + 18), 16, RED if k == cur else GRAY, anchor="mm")
    return c


def frame_slow(frames, k):
    c = canvas(1280, 720)
    c = text(c, "视频 = 一帧一帧连续的图片", (40, 40), 32, INK, anchor="lm")
    c = text(c, "① 放慢讲解：一帧一帧地看", (40, 84), 22, BLUE, anchor="lm")
    paste(c, strip(frames, k), 40, 110)
    big = cv2.resize(frames[k], (640, 400), interpolation=cv2.INTER_NEAREST)
    paste(c, border(big), 40, 230)
    x0 = 730
    c = text(c, f"第 {k + 1} 帧（frame）", (x0, 280), 34, RED, anchor="lm")
    c = text(c, f"标称 {NOMINAL_FPS} 帧/秒时：", (x0, 350), 24, INK, anchor="lm")
    c = text(c, f"t = {k} ÷ {NOMINAL_FPS} ≈ {k / NOMINAL_FPS:.3f} 秒", (x0, 394), 28, INK, anchor="lm")
    c = text(c, f"相邻两帧相隔 1/{NOMINAL_FPS} ≈ {1 / NOMINAL_FPS:.3f} 秒", (x0, 450), 22, GRAY, anchor="lm")
    c = text(c, "每一帧都是一张普通的图片", (x0, 520), 24, INK, anchor="lm")
    c = text(c, "小球每帧向右移一点", (x0, 560), 24, INK, anchor="lm")
    c = text(c, "讲解时放慢展示，不是真实播放速度", (640, 690), 20, GRAY, anchor="mm")
    return c


def frame_fast(frames, k):
    c = canvas(1280, 720)
    c = text(c, "视频 = 一帧一帧连续的图片", (40, 40), 32, INK, anchor="lm")
    c = text(c, "② 快速连播：人眼就看成了连续运动（像翻页动画）", (40, 84), 22, GREEN, anchor="lm")
    big = cv2.resize(frames[k], (800, 500), interpolation=cv2.INTER_NEAREST)
    paste(c, border(big), 240, 120)
    c = text(c, "本 GIF 每帧 0.04 秒（约 25 帧/秒）；实际快慢取决于播放软件，不是实测帧率", (640, 660), 20, GRAY, anchor="mm")
    c = text(c, "常见帧率：25、30 帧/秒", (640, 690), 20, GRAY, anchor="mm")
    return c


def main():
    frames = make_frames()
    out, durs = [], []
    for k in range(N):
        out.append(stamp(frame_slow(frames, k), "候选 · 合成教学样本（非产线实拍）")); durs.append(700 if k else 1600)
    durs[-1] = 1800
    for loop in range(3):
        for k in range(N):
            out.append(stamp(frame_fast(frames, k), "候选 · 合成教学样本（非产线实拍）")); durs.append(40)
        durs[-1] = 600
    assert all(d % 10 == 0 for d in durs)              # GIF 只能精确到 1/100 秒
    save_gif(out, L, "36-p4-anim-连续帧翻页动画_候选.gif", durs)
    keyframe_sheet(out, [0, 6, N - 1, N + 5], L, "36-p4-anim-关键帧拼图_审阅用.png",
                   labels=["放慢：第 1 帧", "放慢：第 7 帧", "放慢：第 12 帧", "快速连播（GIF 每帧 0.04 秒）"])
    print(f"    原始帧 {N} 张；GIF {len(out)} 帧：放慢段每帧 0.7 秒，连播段每帧 0.04 秒（3 遍），总时长 {sum(durs) / 1000:.2f} 秒")


if __name__ == "__main__":
    print("[36] 打开摄像头与视频文件 · P4")
    main()
