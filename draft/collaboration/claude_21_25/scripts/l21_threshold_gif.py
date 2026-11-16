# -*- coding: utf-8 -*-
"""21-P4《阈值：一条分界线》候选动画：灰度渐变条 → 阈值线 → 逐值判定 → 二值结果。

判定规则以 OpenCV 实测为准：THRESH_BINARY 中 像素值 > 阈值 → 255（白），等于或小于阈值 → 0（黑）。
渐变条为合成输入：0…255 每个灰度值各占 4 像素宽，输出条由 cv2.threshold 实际计算后逐段显示。

输出（previews/21/）：
  21-p4-anim-阈值线把渐变条一分为二_候选.gif
  21-p4-anim-关键帧拼图_审阅用.png
"""
import cv2
import numpy as np
from _common import *

L = "21"
T = 127
CELL = 4                      # 每个灰度值的像素宽度
BW, BH = 256 * CELL, 80       # 渐变条尺寸 1024×80
X0 = 128                      # 渐变条左边界
Y_IN, Y_OUT = 200, 420        # 原灰度条、输出条的纵坐标


def verify():
    row_ = np.arange(256, dtype=np.uint8)[None, :]
    ret, out = cv2.threshold(row_, T, 255, cv2.THRESH_BINARY)
    out = out.ravel()
    assert ret == T
    assert out[T] == 0 and out[T - 1] == 0 and out[T + 1] == 255, out[T - 1:T + 2]
    assert set(np.unique(out).tolist()) == {0, 255}
    first_white = int(np.argmax(out == 255))
    print(f"    cv2.threshold(…, {T}, 255, THRESH_BINARY)：126→{out[126]}，127→{out[127]}，128→{out[128]}；"
          f"首个白色灰度值 = {first_white}；输出只含 {sorted(set(out.tolist()))}")
    others = {}
    for t in (80, 180):
        _, o = cv2.threshold(row_, t, 255, cv2.THRESH_BINARY)
        others[t] = o.ravel()
        assert o.ravel()[t] == 0 and o.ravel()[t + 1] == 255
    return out, others


def bar(values):
    return bgr(np.repeat(np.repeat(values.astype(np.uint8)[None, :], BH, 0), CELL, 1))


def _inset(c, out, t, probe, lo=123, hi=132, cw=58, y=560):
    """放大显示 lo…hi 这几个灰度值的原值与输出，便于看清 126/127/128。"""
    n = hi - lo + 1
    x0 = 640 - n * cw // 2
    c = text(c, "放大", (x0 - 12, y + 22), 20, GRAY, anchor="rm")
    for i, v in enumerate(range(lo, hi + 1)):
        x = x0 + i * cw
        cv2.rectangle(c, (x, y), (x + cw, y + 44), (v, v, v), -1)
        o = int(out[v])
        cv2.rectangle(c, (x, y + 50), (x + cw, y + 94), (o, o, o), -1)
        for yy in (y, y + 50):
            cv2.rectangle(c, (x, yy), (x + cw, yy + 44), RED if v == probe else GRAY, 3 if v == probe else 1)
        c = text(c, str(v), (x + cw // 2, y + 22), 20, WHITE, anchor="mm")
        c = text(c, str(o), (x + cw // 2, y + 72), 20, INK if o else WHITE, anchor="mm")
    xt = x0 + (t - lo + 1) * cw
    cv2.line(c, (xt, y - 8), (xt, y + 102), AMB, 4)
    return c


def frame(out, t=T, reveal=None, probe=None, show_line=True, note=None, note_color=INK):
    """reveal：输出条已显示到的灰度值（含）；probe：当前高亮检查的灰度值。"""
    c = canvas(1280, 800)
    c = text(c, "阈值：一条分界线（THRESH_BINARY）", (40, 46), 34, INK, anchor="lm")
    c = text(c, f"规则：像素值 > {t} → 255（白）；像素值 ≤ {t} → 0（黑）", (40, 100), 26, RED, anchor="lm")
    # 原灰度条
    c = text(c, "原灰度", (X0 - 16, Y_IN + BH // 2), 22, INK, anchor="rm")
    paste(c, bar(np.arange(256)), X0, Y_IN)
    cv2.rectangle(c, (X0 - 1, Y_IN - 1), (X0 + BW, Y_IN + BH), GRAY, 1)
    for v in (0, 64, 128, 192, 255):
        x = X0 + v * CELL + CELL // 2
        cv2.line(c, (x, Y_IN + BH), (x, Y_IN + BH + 8), GRAY, 1)
        c = text(c, str(v), (x, Y_IN + BH + 22), 18, GRAY, anchor="mm")
    # 输出条（白底上画黑/白，需加框才能看出白段）
    c = text(c, "输出", (X0 - 16, Y_OUT + BH // 2), 22, INK, anchor="rm")
    cv2.rectangle(c, (X0 - 1, Y_OUT - 1), (X0 + BW, Y_OUT + BH), GRAY, 1)
    if reveal is not None:
        n = reveal + 1
        paste(c, bar(out[:n]), X0, Y_OUT)
        for x in range(X0 + n * CELL, X0 + BW, 12):          # 未计算部分画淡斜线
            cv2.line(c, (x, Y_OUT + BH - 1), (min(x + 12, X0 + BW - 1), Y_OUT + 1), (225, 225, 225), 1)
        cv2.rectangle(c, (X0 - 1, Y_OUT - 1), (X0 + BW, Y_OUT + BH), INK, 2)
    # 阈值线
    if show_line:
        xt = X0 + t * CELL + CELL           # 位于灰度值 t 与 t+1 之间
        cv2.line(c, (xt, Y_IN - 40), (xt, Y_OUT + BH + 20), AMB, 4)
        c = text(c, f"阈值 {t}", (xt, Y_IN - 56), 24, WHITE, bg=AMB, pad=5, anchor="mm")
        if reveal is not None and reveal >= 255:
            c = text(c, "0（黑）", (X0 + (xt - X0) // 2, Y_OUT + BH + 34), 24, INK, anchor="mm")
            c = text(c, "255（白）", (xt + (X0 + BW - xt) // 2, Y_OUT + BH + 34), 24, INK, anchor="mm")
    # 探针
    if probe is not None:
        x = X0 + probe * CELL + CELL // 2
        for y in (Y_IN, Y_OUT):
            cv2.rectangle(c, (x - 7, y - 10), (x + 7, y + BH + 10), RED, 3)
        cv2.arrowedLine(c, (x, Y_IN + BH + 30), (x, Y_OUT - 16), RED, 3, tipLength=0.12)
        o = int(out[probe])
        res = "是" if probe > t else "否"
        msg = f"原灰度 {probe}    {probe} > {t} ？{res}    →  输出 {o}（{'白' if o else '黑'}）"
        if abs(probe - t) <= 4:
            c = _inset(c, out, t, probe)
        c = text(c, msg, (640, 700), 30, RED if probe == t else INK, anchor="mm")
        if probe == t:
            c = text(c, "等于阈值也判为黑", (640, 748), 24, WHITE, bg=RED, pad=6, anchor="mm")
    if note:
        c = text(c, note, (640, 700), 26, note_color, anchor="mm")
    return stamp(c, "候选 · 合成渐变条；输出由 cv2.threshold 实算")


def main():
    out, others = verify()
    frames, durs = [], []

    def add(f, ms):
        frames.append(f); durs.append(ms)

    add(frame(out, show_line=False, note="一行灰度：从 0（黑）逐渐变到 255（白）"), 2200)
    add(frame(out, note=f"画一条分界线：阈值 = {T}"), 2000)
    # 输出逐段出现：先快扫到阈值附近，再逐值看 126/127/128，最后扫到底
    for v in (40, 80, 110):
        add(frame(out, reveal=v, probe=v), 900)
    for v in (126, 127, 128):
        add(frame(out, reveal=v, probe=v), 2600 if v == 127 else 2000)
    for v in (170, 220, 255):
        add(frame(out, reveal=v, probe=v), 900)
    add(frame(out, reveal=255, note="结果只剩 0 和 255 两种值：二值图（前提：先转灰度）"), 3200)
    # 对照：改阈值，分界线随之移动
    for t in (80, 180):
        add(frame(others[t], t=t, reveal=255, note=f"阈值改成 {t}：分界线移动，黑白比例随之改变", note_color=BLUE), 2200)
    save_gif(frames, L, "21-p4-anim-阈值线把渐变条一分为二_候选.gif", durs, colors=256)
    keyframe_sheet(frames, [1, 6, 11, 13], L, "21-p4-anim-关键帧拼图_审阅用.png",
                   labels=["阈值线出现", "关键：127 等于阈值 → 黑", "完成：只有 0 和 255", "对照：阈值改为 180"])
    print(f"    GIF {len(frames)} 帧，总时长 {sum(durs) / 1000:.1f} 秒")


if __name__ == "__main__":
    print("[21] 阈值分割与二值化")
    main()
