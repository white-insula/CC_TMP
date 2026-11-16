# -*- coding: utf-8 -*-
"""32-P8、33-P4、35-P4 课堂版流程图（1280×720，大字、少文字）。

32-P8 产线扫码追溯：零件编号与记录均为虚构示意数据；不是工厂实拍。
33-P4 颜色形状分拣五步：形状判断写“approxPolyDP 判断形状”，不在流程图里预先决定 33 讲用哪套规则（见 review 冲突说明）。
35-P4 批量阅卷五步：识别失败分支记录文件名与原因后继续下一张，不计 0 分、不混入正常得分统计。

输出（previews/32、33、35/）：
  32-p8-diag-产线扫码追溯流程图_课堂版_候选.png
  33-p4-diag-颜色形状分拣五步流程图_课堂版_候选.png
  35-p4-diag-批量阅卷五步流程图_课堂版_候选.png
"""
import cv2
import numpy as np
from _common import *

C_STEP, C_LOOP, C_FAIL, C_NOTE = (250, 238, 220), (238, 246, 236), (232, 232, 252), (245, 245, 245)


def box(c, x, y, w, h, lines, fill=C_STEP, edge=BLUE, size=24, tc=INK, sub=None, sub_size=18):
    cv2.rectangle(c, (x, y), (x + w, y + h), fill, -1)
    cv2.rectangle(c, (x, y), (x + w, y + h), edge, 3)
    n = len(lines) + (1 if sub else 0)
    lh = size + 10
    y0 = y + h // 2 - (n - 1) * lh // 2
    for i, s in enumerate(lines):
        c = text(c, s, (x + w // 2, y0 + i * lh), size, tc, anchor="mm")
    if sub:
        c = text(c, sub, (x + w // 2, y0 + len(lines) * lh), sub_size, GRAY, anchor="mm")
    return c


def arrow(c, p, q, colr=INK, lab=None, at=None, size=20):
    cv2.arrowedLine(c, p, q, colr, 3, cv2.LINE_AA, tipLength=min(0.35, 16 / max(1.0, float(np.hypot(q[0] - p[0], q[1] - p[1])))))
    if lab:
        c = text(c, lab, at, size, colr, anchor="mm")
    return c


def finish(c, lesson, name, note):
    out = stamp(c, note)
    assert out.shape[:2] == (720, 1280)
    save(out, lesson, name)


# ---------------- 32-P8 ----------------
def flow32():
    import qrcode
    c = canvas(1280, 690)
    c = text(c, "产线扫码追溯：一物一码，每道工序扫码记录", (40, 40), 32, INK, anchor="lm")
    steps = [("① 一物一码", "零件贴码"), ("② 各工序扫码", "下料→加工→检验"), ("③ 记录", "时间·工位·结果"),
             ("④ 关联批次", "零件号 ↔ 批次"), ("⑤ 异常追溯", "扫码查批次·工位·检验员")]
    x, y, w, h, gap = 40, 90, 216, 120, 25
    for i, (a, b) in enumerate(steps):
        c = box(c, x + i * (w + gap), y, w, h, [a], sub=b, size=26, sub_size=19,
                fill=C_FAIL if i == 4 else C_STEP, edge=RED if i == 4 else BLUE)
        if i < 4:
            c = arrow(c, (x + i * (w + gap) + w + 2, y + h // 2), (x + (i + 1) * (w + gap) - 2, y + h // 2))
    # 示例记录（虚构）
    c = text(c, "扫码记录示例（虚构数据）", (40, 250), 24, INK, anchor="lm")
    hdr = ["零件编号", "工序", "工位", "时间", "结果", "批次"]
    rows = [["PART-2026-0001", "下料", "A-01", "08:12", "合格", "批次A"],
            ["PART-2026-0001", "加工", "B-03", "09:40", "合格", "批次A"],
            ["PART-2026-0001", "检验", "Q-02", "10:05", "合格", "批次A"],
            ["PART-2026-0002", "检验", "Q-02", "10:07", "不合格", "批次A"]]
    cw = [190, 80, 80, 90, 90, 90]
    tx, ty, rh = 40, 280, 44
    for r, rowv in enumerate([hdr] + rows):
        xx = tx
        for k, v in enumerate(rowv):
            fill = (225, 225, 225) if r == 0 else ((232, 232, 252) if v == "不合格" else (255, 255, 255))
            cv2.rectangle(c, (xx, ty + r * rh), (xx + cw[k], ty + (r + 1) * rh), fill, -1)
            cv2.rectangle(c, (xx, ty + r * rh), (xx + cw[k], ty + (r + 1) * rh), (180, 180, 180), 1)
            c = text(c, v, (xx + cw[k] // 2, ty + r * rh + rh // 2), 18 if k == 0 else 20, RED if v == "不合格" else INK, anchor="mm")
            xx += cw[k]
    c = text(c, "出问题时：扫 PART-2026-0002 → 查到批次A、检验工位 Q-02", (40, ty + 5 * rh + 26), 20, RED, anchor="lm")
    # 码的类型
    nx = 700
    q = cv2.cvtColor(np.array(qrcode.make("PART-2026-0001").convert("RGB")), cv2.COLOR_RGB2BGR)
    q = cv2.resize(q, (120, 120), interpolation=cv2.INTER_NEAREST)
    paste(c, border(q), nx, 260)
    c = text(c, "QR 码：本课 cv2.QRCodeDetector 可识别", (nx + 140, 290), 22, INK, anchor="lm")
    c = text(c, "（左图为 qrcode 生成的 PART-2026-0001）", (nx + 140, 324), 18, GRAY, anchor="lm")
    c = text(c, "Data Matrix（DM 码）：常直接刻印在零件上；", (nx, 420), 22, INK, anchor="lm")
    c = text(c, "QRCodeDetector 不能解 DM 码，需专用读码器或其他库", (nx, 454), 20, RED, anchor="lm")
    c = text(c, "一维条码：包装、标签上常见；", (nx, 510), 22, INK, anchor="lm")
    c = text(c, "OpenCV 有 cv2.barcode.BarcodeDetector", (nx, 544), 20, GRAY, anchor="lm")
    c = text(c, "示意图：流程与数据均为虚构，非工厂实拍", (640, 664), 20, GRAY, anchor="mm")
    finish(c, "32", "32-p8-diag-产线扫码追溯流程图_课堂版_候选.png", "候选 · 课堂版 · 示意图（虚构数据）")


# ---------------- 33-P4 ----------------
def flow33():
    c = canvas(1280, 690)
    c = text(c, "颜色形状分拣：五步方案（每步都是学过的知识）", (40, 40), 32, INK, anchor="lm")
    c = box(c, 40, 90, 1200, 74, ["① 读图 → 高斯滤波 → 转 HSV"], sub="第 20 讲（高斯滤波）· 第 26 讲（HSV）", size=26)
    # 外层循环：每种颜色
    cv2.rectangle(c, (40, 196), (1240, 600), C_LOOP, -1)
    cv2.rectangle(c, (40, 196), (1240, 600), GREEN, 3)
    c = text(c, "对 colors 字典里的每一种颜色循环：for name, ranges in colors.items()", (60, 222), 24, GREEN, anchor="lm")
    c = arrow(c, (640, 164), (640, 196))
    c = box(c, 70, 250, 520, 120, ["② inRange 掩膜（多段 OR 合并）", "→ 开运算去噪"],
            sub="第 27 讲（inRange、红色两段合并）· 第 22 讲（开运算）", size=24)
    c = box(c, 690, 250, 520, 120, ["③ 在掩膜上找轮廓", "→ 面积 < 800 跳过"], sub="第 28 讲（findContours）· 第 29 讲（面积）", size=24)
    c = arrow(c, (592, 310), (688, 310))
    # 内层循环：每个轮廓
    cv2.rectangle(c, (70, 400), (1210, 580), (250, 250, 245), -1)
    cv2.rectangle(c, (70, 400), (1210, 580), AMB, 2)
    c = text(c, "对每个保留下来的轮廓：", (90, 424), 22, (0, 130, 200), anchor="lm")
    c = box(c, 100, 444, 480, 116, ["④ approxPolyDP 判断形状"], sub="第 30 讲（多边形近似、角点数）", size=24)
    c = box(c, 700, 444, 480, 116, ["⑤ 画框，标注“颜色 + 形状”", "计数 +1"], sub="第 29 讲（外接框）· 第 18 讲（写字）", size=24)
    c = arrow(c, (582, 502), (698, 502))
    c = arrow(c, (950, 372), (950, 398))
    c = text(c, "红色：两段 inRange 先 OR 合并成一张掩膜，再开运算、找轮廓", (40, 624), 22, RED, anchor="lm")
    c = text(c, "全部颜色循环结束 → print(count)：各类工件数量清单", (40, 660), 22, INK, anchor="lm")
    finish(c, "33", "33-p4-diag-颜色形状分拣五步流程图_课堂版_候选.png", "候选 · 课堂版 · 讲次对应据 content.py")


# ---------------- 35-P4 ----------------
def flow35():
    c = canvas(1280, 690)
    c = text(c, "批量阅卷：五步流程（遇到坏卡不中断）", (40, 40), 32, INK, anchor="lm")
    c = box(c, 40, 90, 520, 90, ["① 读标准答案 答案.txt"], sub="每行“题号-答案-分值”，如 1-A-1", size=26)
    c = arrow(c, (300, 180), (300, 214))
    c = box(c, 40, 216, 520, 90, ["② 遍历文件夹 os.listdir"], sub="只处理 .jpg；取下一张卡", size=26)
    c = arrow(c, (300, 306), (300, 340))
    c = box(c, 40, 342, 520, 90, ["③ 逐张识别 recognize(path)"], sub="返回 (学号, 答案列表)；失败返回 None", size=26)
    # 判断
    pts = np.array([[300, 452], [430, 500], [300, 548], [170, 500]], np.int32)
    c = arrow(c, (300, 432), (300, 452))
    cv2.fillPoly(c, [pts], (250, 244, 232)); cv2.polylines(c, [pts], True, BLUE, 3, cv2.LINE_AA)
    c = text(c, "识别成功？", (300, 500), 24, INK, anchor="mm")
    c = arrow(c, (300, 548), (300, 576), lab="是", at=(322, 560))
    c = box(c, 40, 578, 520, 80, ["④ 对答案算分 → ⑤ 写成绩单一行"], sub="答错的格子标红", size=24, fill=C_LOOP, edge=GREEN)
    # 失败分支
    c = arrow(c, (430, 500), (640, 500), colr=RED, lab="否（None）", at=(535, 482))
    c = box(c, 640, 440, 560, 120, ["记入失败列表：文件名（+ 原因）"], sub="示例：某张卡.jpg · 定位块只找到 3 个", size=24, fill=C_FAIL, edge=RED, tc=RED)
    # 继续下一张
    cv2.line(c, (560, 618), (600, 618), INK, 3); cv2.line(c, (600, 618), (600, 261), INK, 3)
    c = arrow(c, (600, 261), (562, 261))
    cv2.line(c, (920, 440), (920, 400), RED, 3); cv2.line(c, (920, 400), (600, 400), RED, 3)
    c = text(c, "continue：继续下一张", (760, 384), 20, RED, anchor="mm")
    c = text(c, "下一张", (640, 600), 20, INK, anchor="lm")
    # 说明
    c = text(c, "失败的卡：", (700, 120), 24, RED, anchor="lm")
    c = text(c, "· 不当作 0 分，不进入正常得分统计", (700, 160), 22, INK, anchor="lm")
    c = text(c, "· 单独列出，提醒老师人工检查", (700, 196), 22, INK, anchor="lm")
    c = text(c, "· 脚本写法 failed.append(name)；记录原因为可选扩展", (700, 232), 18, GRAY, anchor="lm")
    c = text(c, "全部处理完 → wb.save(\"成绩单.xlsx\")", (700, 290), 22, GREEN, anchor="lm")
    finish(c, "35", "35-p4-diag-批量阅卷五步流程图_课堂版_候选.png", "候选 · 课堂版 · 失败分支不计分")


if __name__ == "__main__":
    print("[32/33/35] 流程图")
    flow32()
    flow33()
    flow35()
