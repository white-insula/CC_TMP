# -*- coding: utf-8 -*-
"""第18讲《在图像上画图写字》候选素材。

第18讲 P2/P4/P6/P7 在素材需求中均已有图（P4 为已通过的手工示意图），本脚本只补录屏静态参考：
  18-p6-shot-黑色画布画图写字_实跑.png       录屏1 代码原样运行结果（无外部输入，可直接对照）
  18-p7-shot-英文标签与中文问号与PIL中文_替身图.png  录屏2 三个窗口（english / question / chinese）对照
输入：P7 用 scikit-image coffee.png（CC0）替身；课程实际用果盘图 cat.jpg（豆包 AI 生成）未上传，
      草莓坐标 x, y, w, h = 142, 305, 147, 163 只适用于果盘图，替身图改框咖啡杯。
字体：课程用 C:/Windows/Fonts/simhei.ttf；云端用文泉驿正黑代替，字形与本机录屏会不同。
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from _common import *

L = "18"


def put_chinese_text(img, text_, position, font_size=30, color=(0, 255, 0)):
    """与 recording_kit/18/label.py 相同写法，只把字体路径换成云端可用的字体。"""
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font_ = ImageFont.truetype(FONT_PATH, font_size)
    draw.text(position, text_, font=font_, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


def p6_canvas():
    canvas_ = np.zeros((400, 600, 3), dtype=np.uint8)
    cv2.line(canvas_, (0, 0), (599, 399), (255, 0, 0), 3)
    cv2.rectangle(canvas_, (50, 50), (200, 150), (0, 255, 0), 2)
    cv2.rectangle(canvas_, (400, 50), (550, 150), (0, 0, 255), -1)
    cv2.circle(canvas_, (300, 200), 80, (0, 255, 255), 2)
    cv2.putText(canvas_, "Hello Vision", (50, 370), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    out = caption_below(border(canvas_), "录屏1 代码原样运行：蓝线、绿色空心框、红色实心框、黄色圆、白色英文", 20)
    save(stamp(out, "候选 · 实跑截图（无外部输入）"), L, "18-p6-shot-黑色画布画图写字_实跑.png")


def p7_labels():
    img = stand_in("coffee")
    x, y, w, h = 90, 90, 300, 240          # 替身图中咖啡杯（手工给定，不是检测结果）
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    en = img.copy(); cv2.putText(en, "cup 0.95", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    q = img.copy(); cv2.putText(q, "杯子 0.95", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    zh = put_chinese_text(img.copy(), "杯子", (x, y - 40), 30, (0, 255, 0))
    out = row([caption_below(border(fit(en, w=400)), "english：框 + 英文标签", 20),
               caption_below(border(fit(q, w=400)), "question：putText 写中文 → ???", 20, RED),
               caption_below(border(fit(zh, w=400)), "chinese：PIL + 中文字体", 20, GREEN)], gap=16)
    note = canvas(out.shape[1], 44)
    note = text(note, "标签与 0.95 均为手工示例，不是模型预测；正式录屏用果盘图框草莓（坐标 142, 305, 147, 163）",
                (out.shape[1] // 2, 22), 20, GRAY, anchor="mm")
    out = col([out, note], gap=4)
    save(stamp(out, "候选 · 替身图 coffee(CC0)，非果盘 cat.jpg；字体为文泉驿正黑"), L, "18-p7-shot-英文标签与中文问号与PIL中文_替身图.png")


if __name__ == "__main__":
    print("[18] 在图像上画图写字")
    p6_canvas()
    p7_labels()
