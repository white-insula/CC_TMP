# -*- coding: utf-8 -*-
"""37-P4《循环结构：处理放在中间》候选：读 → 处理 → 显示 循环图（课堂版 1280×720）＋ 精确代码附件。

要点：打开来源 → isOpened 检查 → read 返回 ret → 处理 frame → 显示与按键 → 回到读帧；
ret 为 False 与按 q 都进入同一个“释放清理”；文件读完与摄像头读取失败含义不同。
旧候选 manual/37/37-p4-diag-读处理显示循环.png 登记为“需改（有乱码）”，本候选未查看旧图，只是重新绘制。

输出（previews/37/）：
  37-p4-diag-读处理显示循环图_课堂版_候选.png
  37-p4-ref-循环结构精确代码_附件.png
"""
import cv2
import numpy as np
from _common import *

L = "37"
C_STEP, C_DEC, C_END = (250, 238, 220), (250, 244, 232), (232, 232, 252)


def box(c, x, y, w, h, s, sub=None, fill=C_STEP, edge=BLUE, size=26):
    cv2.rectangle(c, (x, y), (x + w, y + h), fill, -1); cv2.rectangle(c, (x, y), (x + w, y + h), edge, 3)
    if sub:
        c = text(c, s, (x + w // 2, y + h // 2 - 14), size, INK, anchor="mm")
        return text(c, sub, (x + w // 2, y + h // 2 + 20), 18, GRAY, anchor="mm")
    return text(c, s, (x + w // 2, y + h // 2), size, INK, anchor="mm")


def diamond(c, cx, cy, w, h, s, size=24):
    pts = np.array([[cx, cy - h // 2], [cx + w // 2, cy], [cx, cy + h // 2], [cx - w // 2, cy]], np.int32)
    cv2.fillPoly(c, [pts], C_DEC); cv2.polylines(c, [pts], True, BLUE, 3, cv2.LINE_AA)
    return text(c, s, (cx, cy), size, INK, anchor="mm")


def arr(c, p, q, colr=INK, lab=None, at=None):
    cv2.arrowedLine(c, p, q, colr, 3, cv2.LINE_AA, tipLength=min(0.35, 16 / max(1.0, float(np.hypot(q[0] - p[0], q[1] - p[1])))))
    return text(c, lab, at, 20, colr, anchor="mm") if lab else c


def classroom():
    c = canvas(1280, 690)
    c = text(c, "逐帧处理：读 → 处理 → 显示，循环往复", (40, 38), 32, INK, anchor="lm")
    X, W = 300, 360                       # 主列
    c = box(c, X - W // 2, 70, W, 56, "打开：cap = VideoCapture(…)", size=22)
    c = arr(c, (X, 126), (X, 142))
    c = diamond(c, X, 176, 260, 66, "cap.isOpened() ?")
    c = arr(c, (X + 130, 176), (720, 176), RED, "否", (560, 160))
    c = box(c, 720, 150, 260, 52, "提示打开失败，退出", fill=C_END, edge=RED, size=22)
    c = arr(c, (X, 209), (X, 232), lab="是", at=(X + 20, 220))
    # 循环体
    c = box(c, X - W // 2, 234, W, 66, "① 读：ret, frame = cap.read()", size=22)
    c = arr(c, (X, 300), (X, 318))
    c = diamond(c, X, 352, 200, 64, "ret ?")
    c = arr(c, (X, 384), (X, 404), lab="True", at=(X + 30, 394))
    c = box(c, X - W // 2, 406, W, 66, "② 处理：result = 处理(frame)", sub="frame 是普通图片（BGR 数组）", size=22)
    c = arr(c, (X, 472), (X, 490))
    c = box(c, X - W // 2, 492, W, 66, "③ 显示：imshow + waitKey(1)", size=22)
    c = arr(c, (X, 558), (X, 576))
    c = diamond(c, X, 610, 220, 64, "按了 q ?")
    # 回到读帧
    cv2.line(c, (X - 110, 610), (60, 610), INK, 3); cv2.line(c, (60, 610), (60, 267), INK, 3)
    c = arr(c, (60, 267), (X - W // 2 - 2, 267))
    c = text(c, "否", (172, 594), 20, INK, anchor="mm")
    c = text(c, "回到①", (72, 336), 20, INK, anchor="lm")
    c = text(c, "读下一帧", (72, 366), 20, INK, anchor="lm")
    # 两个出口 → 清理
    cx0 = 820
    c = box(c, 720, 470, 420, 90, "④ 释放：cap.release()", sub="cv2.destroyAllWindows()", fill=C_END, edge=RED, size=24)
    cv2.line(c, (X + 100, 352), (cx0, 352), RED, 3)
    c = text(c, "False：break", (560, 336), 20, RED, anchor="mm")
    c = arr(c, (cx0, 352), (cx0, 468), RED)
    cv2.line(c, (X + 110, 610), (cx0, 610), RED, 3)
    c = text(c, "是：break", (560, 594), 20, RED, anchor="mm")
    c = arr(c, (cx0, 610), (cx0, 562), RED)
    # ret=False 的两种含义
    c = text(c, "ret 为 False：", (720, 250), 22, RED, anchor="lm")
    c = text(c, "· 视频文件：读到结尾，正常结束", (720, 288), 20, INK, anchor="lm")
    c = text(c, "· 摄像头：读取失败（断开、被占用等）", (720, 322), 20, INK, anchor="lm")
    out = stamp(c, "候选 · 课堂版 · 精确代码见附件")
    assert out.shape[:2] == (720, 1280)
    save(out, L, "37-p4-diag-读处理显示循环图_课堂版_候选.png")


CODE = '''import cv2

cap = cv2.VideoCapture(0)            # 摄像头写编号；视频文件写文件名，如 "test.mp4"
if not cap.isOpened():
    print("打开失败")
    raise SystemExit
try:
    while True:
        ret, frame = cap.read()      # ① 读
        if not ret:                  # 文件：读到结尾；摄像头：读取失败
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)          # ② 处理（任何图片处理）
        cv2.imshow("frame", frame); cv2.imshow("gray", gray)    # ③ 显示
        if cv2.waitKey(1) & 0xFF == ord("q"):                   #    按 q 退出
            break
finally:
    cap.release()                    # ④ 无论哪种方式退出都会释放
    cv2.destroyAllWindows()'''


def code_attachment():
    lines = CODE.split("\n")
    c = canvas(1280, 120 + 34 * len(lines))
    c = text(c, "37-P4 附件：循环结构的精确代码（与 recording_candidates/37 写法一致）", (40, 36), 26, INK, anchor="lm")
    c = text(c, "try / finally 是为了保证异常时也释放资源；课堂录屏可按脚本写在循环之后。", (40, 76), 20, GRAY, anchor="lm")
    cv2.rectangle(c, (30, 100), (1250, 110 + 34 * len(lines)), (245, 245, 245), -1)
    for i, s in enumerate(lines):
        c = text(c, s, (50, 124 + 34 * i), 22, BLUE if s.strip().startswith(("ret", "if not ret", "break")) else INK, anchor="lm")
    compile(CODE, "<loop>", "exec")                     # 附件里的代码至少要能通过语法检查
    save(stamp(c, "核对附件 · 不进课件"), L, "37-p4-ref-循环结构精确代码_附件.png")


if __name__ == "__main__":
    print("[37] 视频的逐帧处理 · P4")
    classroom()
    code_attachment()
