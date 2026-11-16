# 第 18 讲 p7 录屏:在照片上框出一个物体并写标签;putText 写中文出问号,改用 put_chinese_text
# 预期:english 窗口:框 + 英文标签;question 窗口:中文变成 ???;chinese 窗口:中文正常
# 与第 18 讲脚本统一:手工框出草莓;strawberry 0.95 是标注样式示例,不是模型预测。
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def put_chinese_text(img, text, position, font_size=30, color=(0, 255, 0)):
    """[OC]Finger_Guess_Game 中的同名函数:PIL + 黑体写中文"""
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    font = ImageFont.truetype("C:/Windows/Fonts/simhei.ttf", font_size)
    draw.text(position, text, font=font, fill=color)
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


img = cv2.imread("cat.jpg")
x, y, w, h = 142, 305, 147, 163          # 果盘左下那颗草莓(按颜色自动找出的位置)
cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
en = img.copy(); cv2.putText(en, "strawberry 0.95", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
q = img.copy(); cv2.putText(q, "草莓 0.95", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
zh = put_chinese_text(img.copy(), "草莓", (x, y - 40), 30, (0, 255, 0))
cv2.imshow("english", en); cv2.imshow("question", q); cv2.imshow("chinese", zh)
cv2.waitKey(0)
