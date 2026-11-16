# -*- coding: utf-8 -*-
"""25-P4《原理：四个点对四个点》候选动画：梯形四角 ↔ 矩形四角逐对连线 → 拉正 → 顺序写错的后果。

与 recording_kit/25/warp.py 保持一致：
  src = [[151, 58], [489, 104], [417, 612], [41, 538]]（左上、右上、右下、左下）
  W, H = 420, 594；dst = [[0, 0], [W-1, 0], [W-1, H-1], [0, H-1]]
  错误顺序 wrong = 左上、右上互换。
输入为**合成**的“斜拍作业纸”：先画一张 420×594 的端正纸张，再用逆变换贴到 560×660 的桌面上，
使四个角正好落在 src 坐标；它不是 paper.jpg 实拍（paper.jpg 未上传）。
用 cv2.getPerspectiveTransform / cv2.perspectiveTransform / cv2.warpPerspective 核对点映射和拉正结果。

输出（previews/25/）：
  25-p4-anim-四点对四点透视矫正_候选.gif
  25-p4-anim-关键帧拼图_审阅用.png
"""
import cv2
import numpy as np
from _common import *

L = "25"
SRC = np.float32([[151, 58], [489, 104], [417, 612], [41, 538]])
W, H = 420, 594
DST = np.float32([[0, 0], [W - 1, 0], [W - 1, H - 1], [0, H - 1]])
WRONG = np.float32([[489, 104], [151, 58], [417, 612], [41, 538]])
NAMES = ["①左上", "②右上", "③右下", "④左下"]
PW, PH = 560, 660                    # 合成照片尺寸
PX, PY = 40, 130                     # 照片在画面中的位置
RX, RY = 960, 140                   # 目标矩形在画面中的位置
PAIR_COLORS = [(40, 40, 220), (200, 110, 30), (60, 160, 60), (160, 60, 160)]


def make_page():
    p = canvas(W, H, (250, 250, 250))
    p = text(p, "作业纸（合成示意）", (W // 2, 46), 28, INK, anchor="mm")
    cv2.line(p, (30, 80), (W - 30, 80), INK, 2)
    for i in range(9):
        y = 120 + i * 48
        cv2.line(p, (30, y + 26), (W - 30, y + 26), (200, 200, 200), 1)
        p = text(p, f"{i + 1}.", (36, y + 10), 20, INK, anchor="lm")
        L_ = [260, 300, 210, 330, 280, 240, 310, 190, 270][i]
        cv2.rectangle(p, (70, y + 2), (70 + L_, y + 16), (90, 90, 90), -1)
    for k in range(4):                                       # 底部 4 个方框，便于看出是否被拉正
        cv2.rectangle(p, (40 + k * 90, 540), (100 + k * 90, 570), INK, 2)
    cv2.rectangle(p, (0, 0), (W - 1, H - 1), (150, 150, 150), 2)
    return p


def make_photo(page):
    yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
    desk = np.dstack([60 + 20 * xx / PW, 95 + 25 * yy / PH, 140 + 20 * xx / PW]).astype(np.uint8)   # 木色桌面（BGR）
    Mf = cv2.getPerspectiveTransform(DST, SRC)
    warped = cv2.warpPerspective(page, Mf, (PW, PH))
    mask = cv2.warpPerspective(np.full((H, W), 255, np.uint8), Mf, (PW, PH))
    photo = desk.copy()
    photo[mask > 127] = warped[mask > 127]
    return photo


def verify(page, photo):
    M = cv2.getPerspectiveTransform(SRC, DST)
    mapped = cv2.perspectiveTransform(SRC.reshape(-1, 1, 2), M).reshape(-1, 2)
    err = float(np.abs(mapped - DST).max())
    assert err < 1e-3, err
    out = cv2.warpPerspective(photo, M, (W, H))
    diff = float(np.abs(out[8:-8, 8:-8].astype(int) - page[8:-8, 8:-8].astype(int)).mean())
    wrong = cv2.warpPerspective(photo, cv2.getPerspectiveTransform(WRONG, DST), (W, H))
    print("    src 经 M 映射后:", np.round(mapped, 3).tolist(), f"（与 dst 最大误差 {err:.2e}）")
    print(f"    拉正结果与原始合成纸张平均灰度差 {diff:.2f}（重采样造成，0–255 量级）")
    assert diff < 12
    return M, out, wrong


def frame(photo, n_pairs, result=None, wrong=False, note=None, note_color=INK):
    c = canvas(1580, 900)
    c = text(c, "透视变换：四个点对四个点", (40, 46), 32, INK, anchor="lm")
    c = text(c, "顺序必须一致：左上 → 右上 → 右下 → 左下", (40, 92), 24, RED, anchor="lm")
    paste(c, photo, PX, PY)
    c = text(c, "原图：斜拍的纸 = 梯形（合成输入）", (PX + PW // 2, PY + PH + 22), 20, GRAY, anchor="mm")
    # 目标矩形
    if result is not None:
        paste(c, result, RX, RY)
    cv2.rectangle(c, (RX, RY), (RX + W - 1, RY + H - 1), GREEN if not wrong else RED, 3)
    c = text(c, f"目标：端正的矩形 W×H = {W}×{H}", (RX + W // 2, RY + H + 42), 20, GRAY, anchor="mm")
    srcs = WRONG if wrong else SRC
    for i in range(n_pairs):
        colr = PAIR_COLORS[i]
        sp = (int(PX + srcs[i][0]), int(PY + srcs[i][1]))
        dp = (int(RX + DST[i][0]), int(RY + DST[i][1]))
        cv2.line(c, sp, dp, RED if wrong and i < 2 else colr, 2, cv2.LINE_AA)
        cv2.circle(c, sp, 10, colr, -1, cv2.LINE_AA)
        cv2.circle(c, dp, 10, colr, -1, cv2.LINE_AA)
        x, y = int(srcs[i][0]), int(srcs[i][1])
        lab = f"src[{i}] ({x}, {y})"
        off = [(-10, -24, "rm"), (12, -24, "lm"), (14, 22, "lm"), (-4, 30, "lm")][i]
        c = text(c, lab, (sp[0] + off[0], sp[1] + off[1]), 18, WHITE, bg=colr, pad=4, anchor=off[2])
        dx, dy = int(DST[i][0]), int(DST[i][1])
        doff = [(14, 22, "lm"), (14, -6, "lm"), (14, 6, "lm"), (14, -22, "lm")][i]
        c = text(c, f"{NAMES[i]} [{dx}, {dy}]", (dp[0] + doff[0], dp[1] + doff[1]), 18, colr, bg=WHITE, pad=3, anchor=doff[2])
    if note:
        c = text(c, note, (790, 862), 24, note_color, anchor="mm")
    return stamp(c, "候选 · 合成斜拍纸张（非 paper.jpg）；点映射与拉正由 OpenCV 实算")


def main():
    page = make_page()
    photo = make_photo(page)
    M, out, wrong = verify(page, photo)
    frames, durs = [], []

    def add(f, ms):
        frames.append(f); durs.append(ms)

    add(frame(photo, 0, note="斜着拍的纸：近大远小，成了一个梯形"), 2400)
    for i in range(4):
        add(frame(photo, i + 1, note=f"第 {i + 1} 对：原图{NAMES[i][1:]}角 → 矩形{NAMES[i][1:]}角"), 2000)
    add(frame(photo, 4, note="M = cv2.getPerspectiveTransform(src, dst)：由 4 对点算出变换矩阵"), 2600)
    add(frame(photo, 4, result=out, note="out = cv2.warpPerspective(img, M, (W, H))：整张纸被拉正", note_color=GREEN), 3400)
    add(frame(photo, 4, result=wrong, wrong=True,
              note="把左上、右上写反（warp.py 中的 wrong）：对应关系错乱，画面严重扭曲，几乎看不到纸", note_color=RED), 3600)
    save_gif(frames, L, "25-p4-anim-四点对四点透视矫正_候选.gif", durs)
    keyframe_sheet(frames, [0, 4, 6, 7], L, "25-p4-anim-关键帧拼图_审阅用.png",
                   labels=["原图梯形", "四对点全部连好", "warpPerspective 拉正", "顺序写错的后果"])
    print(f"    GIF {len(frames)} 帧，总时长 {sum(durs) / 1000:.1f} 秒")


if __name__ == "__main__":
    print("[25] 透视变换：文档扫描矫正")
    main()
