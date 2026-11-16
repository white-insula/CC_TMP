# -*- coding: utf-8 -*-
"""26-P4《H、S、V 是什么》候选动画：H 色轮 → S 浓淡 → V 明暗 → 亮暗对比 → H 不可靠的情况。

全部按课程用的 cv2.COLOR_BGR2HSV / COLOR_HSV2BGR（uint8）：H = 0—179（角度 ÷ 2），S、V = 0—255；
不使用 HSV_FULL，也不使用浮点 HSV。所有色块均由 HSV 数值经 cv2.cvtColor 转回 BGR 显示，示例数值由 OpenCV 实算。

输出（previews/26/）：
  26-p4-anim-HSV色轮浓淡明暗_候选.gif
  26-p4-anim-关键帧拼图_审阅用.png
"""
import math
import cv2
import numpy as np
from _common import *

L = "26"
R_OUT, R_IN = 230, 150          # 色环外径、内径（像素）
CX, CY = 330, 400               # 色轮中心


def hsv2bgr(h, s, v):
    return cv2.cvtColor(np.uint8([[[h, s, v]]]), cv2.COLOR_HSV2BGR)[0, 0]


def bgr2hsv(b, g, r):
    return cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0, 0]


def verify():
    got = {n: bgr2hsv(*b).tolist() for n, b in (("红", (0, 0, 255)), ("黄", (0, 255, 255)), ("绿", (0, 255, 0)), ("蓝", (255, 0, 0)))}
    assert got == {"红": [0, 255, 255], "黄": [30, 255, 255], "绿": [60, 255, 255], "蓝": [120, 255, 255]}, got
    # H 只有 0—179：把 0—179 全部转回 BGR 再转回 HSV，H 不变
    hs = np.arange(180, dtype=np.uint8)
    strip = np.dstack([hs, np.full(180, 255, np.uint8), np.full(180, 255, np.uint8)])   # 形状 (1, 180, 3)
    back = cv2.cvtColor(cv2.cvtColor(strip, cv2.COLOR_HSV2BGR), cv2.COLOR_BGR2HSV)
    assert int(back[..., 0].max()) <= 179
    print("    纯色 HSV（COLOR_BGR2HSV，uint8）：", got)
    return got


def wheel(s_mode=False, v=255):
    """色轮：角度 → H（0—179）。s_mode=False 时为 S=255 的色环；True 时为实心圆盘，半径 → S（中心 0、边缘 255）。"""
    size = 2 * R_OUT + 4
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) - (R_OUT + 2)
    r = np.sqrt(xx ** 2 + yy ** 2)
    ang = (np.degrees(np.arctan2(-yy, xx)) + 360) % 360          # 0° 在右侧，逆时针增加
    h = np.clip((ang / 2).astype(np.int32), 0, 179).astype(np.uint8)
    if s_mode:
        s = np.clip(r / R_OUT * 255, 0, 255).astype(np.uint8)
        inside = r <= R_OUT
    else:
        s = np.full_like(h, 255)
        inside = (r <= R_OUT) & (r >= R_IN)
    hsv = np.dstack([h, s, np.full_like(h, v)])
    img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    out = np.full_like(img, 255)
    out[inside] = img[inside]
    return out


def put_wheel(c, w, ticks=True, hi_red=False):
    paste(c, w, CX - R_OUT - 2, CY - R_OUT - 2)
    if not ticks:
        return c
    for hval, name in ((0, "红 0"), (30, "黄 30"), (60, "绿 60"), (90, "90"), (120, "蓝 120"), (150, "150"), (179, "179")):
        a = math.radians(hval * 2)
        x1, y1 = CX + (R_OUT + 4) * math.cos(a), CY - (R_OUT + 4) * math.sin(a)
        x2, y2 = CX + (R_OUT + 18) * math.cos(a), CY - (R_OUT + 18) * math.sin(a)
        cv2.line(c, (int(x1), int(y1)), (int(x2), int(y2)), INK, 2, cv2.LINE_AA)
        tx, ty = CX + (R_OUT + 48) * math.cos(a), CY - (R_OUT + 48) * math.sin(a)
        if hval == 179:
            ty += 22
        elif hval == 0:
            ty -= 14
        c = text(c, name, (int(tx), int(ty)), 22, RED if hval in (0, 179) and hi_red else INK, anchor="mm")
    if hi_red:
        # 首尾相接处：0 与 179 相邻
        cv2.ellipse(c, (CX, CY), (R_OUT + 8, R_OUT + 8), 0, -26, 26, RED, 6, cv2.LINE_AA)
    return c


def strip(kind, h=0, n=256, w=520, hgt=60):
    vals = np.linspace(0, 255, w).astype(np.uint8)
    if kind == "S":
        hsv = np.dstack([np.full(w, h, np.uint8), vals, np.full(w, 255, np.uint8)])
    else:
        hsv = np.dstack([np.full(w, h, np.uint8), np.full(w, 255, np.uint8), vals])
    return np.repeat(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR), hgt, 0)   # hsv 形状 (1, w, 3)


def frame(title, sub, body_fn, note=None, note_color=INK):
    c = canvas(1280, 780)
    c = text(c, "H、S、V 是什么（OpenCV：COLOR_BGR2HSV）", (40, 44), 32, INK, anchor="lm")
    c = text(c, sub, (40, 92), 24, BLUE, anchor="lm")
    c = body_fn(c)
    if note:
        c = text(c, note, (640, 748), 24, note_color, anchor="mm")
    return stamp(c, "候选 · HSV 色块由 cv2.cvtColor(uint8) 实算 · H 0—179，S/V 0—255")


def right_panel(c, lines, x0=720, y0=200, size=26):
    for i, (s, colr) in enumerate(lines):
        c = text(c, s, (x0, y0 + i * 52), size, colr, anchor="lm")
    return c


def main():
    verify()
    ring = wheel(False)
    disk = wheel(True)
    frames, durs = [], []

    def add(f, ms):
        frames.append(f); durs.append(ms)

    # 1 H 色轮
    add(frame("", "① H 色调：是什么颜色 —— 绕一圈就是色轮", lambda c: right_panel(put_wheel(c, ring), [
        ("角度 0°—360° 除以 2 → H = 0—179", INK),
        ("（为了装进 uint8，最大只能 255）", GRAY),
        ("红 0、黄 30、绿 60、蓝 120", INK)])), 3200)
    # 2 红在两端
    add(frame("", "① H 是一个圈：179 的下一个就是 0", lambda c: right_panel(put_wheel(c, ring, hi_red=True), [
        ("红色正好在首尾交界处", RED),
        ("0 附近和 179 附近都是红", RED),
        ("下一讲提取红色要分两段：", INK),
        ("0—10 与 170—179", INK)]), note="同一圈红色，H 读数可能是 2，也可能是 177", note_color=RED), 3600)
    # 3 S 圆盘
    s_strip = strip("S", h=0)

    def body_s(c):
        c = put_wheel(c, disk)
        c = right_panel(c, [("圆盘：角度 = H，离中心越远 S 越大", INK),
                            ("中心 S = 0：发白、发灰", INK), ("边缘 S = 255：最纯", INK)], y0=170)
        paste(c, s_strip, 720, 360)
        c = text(c, "H = 0 时，S 从 0 到 255（V = 255）", (720, 444), 22, GRAY, anchor="lm")
        c = text(c, "0", (720, 470), 20, GRAY, anchor="lm"); c = text(c, "255", (1240, 470), 20, GRAY, anchor="rm")
        return c
    add(frame("", "② S 饱和度：颜色有多纯 —— 像兑水，越小越淡", body_s), 3600)
    # 4–6 V 逐级变暗（圆柱的高度）
    v_strip = strip("V", h=0)
    for v in (255, 170, 85):
        dv = wheel(True, v=v)

        def body_v(c, dv=dv, v=v):
            c = put_wheel(c, dv, ticks=False)
            c = right_panel(c, [(f"同一个圆盘，V = {v}", INK), ("V 越小越黑；V = 0 时全黑", INK),
                                ("把不同 V 的圆盘叠起来 = HSV 圆柱", GRAY)], y0=170)
            paste(c, v_strip, 720, 360)
            x = 720 + int(v / 255 * (v_strip.shape[1] - 1))
            cv2.line(c, (x, 350), (x, 430), (255, 255, 255) if v < 128 else INK, 4)
            c = text(c, "H = 0、S = 255 时，V 从 0 到 255", (720, 444), 22, GRAY, anchor="lm")
            return c
        add(frame("", "③ V 明度：有多亮 —— 像调灯光", body_v), 1800 if v != 85 else 2600)

    # 7 同一颜色亮暗适度变化
    pairs = [(40, 40, 200), (30, 30, 150), (20, 20, 100)]
    vals = [(p, bgr2hsv(*p).tolist()) for p in pairs]
    print("    同一红色亮暗：", vals)
    assert len({h for _, (h, s, v) in vals}) == 1

    def body_light(c):
        c = text(c, "同一种红色，在灯下和阴影里（数值由 cv2.cvtColor 实算）", (40, 150), 24, INK, anchor="lm")
        for i, (p, (h, s, v)) in enumerate(vals):
            x = 60 + i * 400
            sw = np.full((150, 300, 3), p, np.uint8)
            paste(c, border(sw), x, 200)
            c = text(c, f"BGR = ({p[0]}, {p[1]}, {p[2]})", (x, 380), 24, INK, anchor="lm")
            c = text(c, f"HSV = ({h}, {s}, {v})", (x, 420), 26, BLUE, anchor="lm")
        c = text(c, "BGR 三个数一起变；H、S 不变，变的主要是 V", (640, 500), 28, GREEN, anchor="mm")
        c = text(c, "所以识别颜色时：卡紧 H，放宽 S 和 V", (640, 550), 26, INK, anchor="mm")
        return c
    add(frame("", "④ 为什么用 HSV：亮暗变化主要改的是 V", body_light,
              note="这里是同一颜色按比例变暗；真实光照还会带来偏色、反光，H 只是“相对稳定”", note_color=GRAY), 4200)

    # 8 H 不可靠
    grays = [(102, 100, 100), (100, 100, 102), (100, 102, 100)]
    darks = [(3, 2, 4), (2, 3, 2)]
    gv = [(p, bgr2hsv(*p).tolist()) for p in grays]
    dv_ = [(p, bgr2hsv(*p).tolist()) for p in darks]
    print("    接近灰色：", gv, "；接近黑色：", dv_)

    def body_bad(c):
        c = text(c, "S 很低（接近灰）或 V 很低（接近黑）时，H 会乱跳", (40, 150), 26, RED, anchor="lm")
        for i, (p, (h, s, v)) in enumerate(gv + dv_):
            x = 60 + i * 238
            paste(c, border(np.full((120, 200, 3), p, np.uint8)), x, 200)
            c = text(c, f"BGR ({p[0]},{p[1]},{p[2]})", (x, 350), 20, INK, anchor="lm")
            c = text(c, f"H = {h}", (x, 390), 28, RED, anchor="lm")
            c = text(c, f"S = {s}, V = {v}", (x, 428), 20, GRAY, anchor="lm")
        c = text(c, "肉眼几乎一样的灰或黑，H 却是 0、60、120、165……", (640, 510), 26, INK, anchor="mm")
        c = text(c, "所以 inRange 要给 S、V 设下限（如 S ≥ 80、V ≥ 50），把发灰、发黑的区域排除", (640, 560), 24, INK, anchor="mm")
        return c
    add(frame("", "⑤ 注意：H 不是任何情况下都可靠", body_bad), 4400)

    save_gif(frames, L, "26-p4-anim-HSV色轮浓淡明暗_候选.gif", durs, colors=256)
    keyframe_sheet(frames, [1, 2, 4, 6, 7], L, "26-p4-anim-关键帧拼图_审阅用.png",
                   labels=["H 色轮：红在首尾两端", "S：越靠中心越淡", "V：越暗越黑（圆柱高度）", "同一红色亮暗：H 不变、V 变", "S/V 很低时 H 不可靠"])
    print(f"    GIF {len(frames)} 帧，总时长 {sum(durs) / 1000:.1f} 秒")


if __name__ == "__main__":
    print("[26] HSV 颜色空间")
    main()
