# -*- coding: utf-8 -*-
"""第 32 讲 二维码的生成与识别：录屏程序与无界面核对共用的核心代码（写法与正式脚本一致）。"""
import os
import cv2
import numpy as np

CONTENT = "PART-2026-0001 | 批次A | 质检合格"
# 图上写中文时按顺序找可用字体：Windows 黑体 → Windows 雅黑 → Linux 文泉驿正黑
FONT_CANDIDATES = [r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\msyh.ttc",
                   "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"]


def make_qr(content=CONTENT, path="part.png"):
    import qrcode                                   # pip install qrcode（本机课程环境请按 06 讲统一安装）
    qrcode.make(content).save(path)
    return path


def read_qr(img):
    det = cv2.QRCodeDetector()
    data, points, _ = det.detectAndDecode(img)
    return data, points


def draw_qr(img, data, points, font=None):
    """画四边形框；OpenCV putText 写不了中文，中文用 PIL + 中文字体画（找不到字体就只画框）"""
    out = img.copy()
    if not data:
        return out, None
    pts = points.astype(int).reshape(-1, 2)
    cv2.polylines(out, [pts], True, (0, 255, 0), 3)
    font = font or next((f for f in FONT_CANDIDATES if os.path.exists(f)), None)
    if font:
        from PIL import Image, ImageDraw, ImageFont
        pil = Image.fromarray(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))
        ImageDraw.Draw(pil).text((10, 5), data, font=ImageFont.truetype(font, 20), fill=(0, 140, 0))
        out = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
    return out, font
