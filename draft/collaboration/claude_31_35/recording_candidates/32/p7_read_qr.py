# -*- coding: utf-8 -*-
# 第 32 讲 P7 录屏（前半）：识别 part.png → 打印内容 → 画出四边形框；图上中文用 PIL 写
# 用法：python p7_read_qr.py [--input part.png] [--font C:/Windows/Fonts/simhei.ttf]
import argparse
import cv2
from core import draw_qr

ap = argparse.ArgumentParser()
ap.add_argument("--input", default="part.png")
ap.add_argument("--font", default=None)
args = ap.parse_args()

img = cv2.imread(args.input)
det = cv2.QRCodeDetector()
data, points, _ = det.detectAndDecode(img)
if data:
    pts = points.astype(int).reshape(-1, 2)
    cv2.polylines(img, [pts], True, (0, 255, 0), 3)
    print(data)                                  # 终端打印完整内容（含中文）
    img, font = draw_qr(img, data, points, args.font)
    print("图上文字字体:", font or "未找到中文字体，只画框")
else:
    print("没有识别到二维码")
cv2.imshow("qr", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
