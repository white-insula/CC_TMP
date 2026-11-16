# -*- coding: utf-8 -*-
"""生成第 16–25 讲的录屏程序(模块三)。只在制作工程包时运行一次。"""
import os, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
A = "assets"


def put(d, files, assets=()):
    os.makedirs(d, exist_ok=True)
    for src, dst in assets:
        shutil.copy(os.path.join(A, src), os.path.join(d, dst))
    for name, code in files.items():
        open(os.path.join(d, name), "w", encoding="utf-8").write(code.lstrip("\n"))


FR = [("photo_fruit.jpg", "cat.jpg")]

put("16", {
"crop.py": r'''
# 第 16 讲 p6 录屏:裁剪出一块区域(坐标先用画图软件读出)
# 预期:打印 (170, 200, 3) —— 高 170、宽 200,正好是两个坐标之差;窗口显示裁出的那一块,保存 roi.jpg
import cv2
img = cv2.imread("cat.jpg")
roi = img[80:250, 100:300]
print(roi.shape)
cv2.imshow("roi", roi); cv2.imwrite("roi.jpg", roi)
cv2.waitKey(0)
''',
"resize.py": r'''
# 第 16 讲 p7 录屏:三种缩放
# 预期:打印 (240, 320, 3);三个窗口:a 宽 320 高 240、b 缩小一半、c 宽 400 且不变形
# 再演示:把 (320, 240) 写成 (240, 320),画面被压扁(见 squashed 窗口)
import cv2
img = cv2.imread("cat.jpg")
a = cv2.resize(img, (320, 240)); print(a.shape)
b = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
h, w = img.shape[:2]; new_w = 400; new_h = int(h * new_w / w)
c = cv2.resize(img, (new_w, new_h))
cv2.imshow("a", a); cv2.imshow("b", b); cv2.imshow("c", c)
cv2.imshow("squashed", cv2.resize(img, (240, 320)))
cv2.waitKey(0)
'''}, FR)

put("17", {
"flip_rotate.py": r'''
# 第 17 讲 p7 录屏:翻转与 90° 旋转
# 预期:h_flip 左右镜像、v_flip 上下颠倒;打印 (620, 810, 3) (810, 620, 3) —— 高宽对调;hv 和 r180 完全一样
import cv2
img = cv2.imread("cat.jpg")
h_flip = cv2.flip(img, 1); v_flip = cv2.flip(img, 0); hv = cv2.flip(img, -1)
r90 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
print(img.shape, r90.shape)
r180 = cv2.rotate(img, cv2.ROTATE_180)
cv2.imshow("h_flip", h_flip); cv2.imshow("v_flip", v_flip); cv2.imshow("hv", hv); cv2.imshow("r180", r180)
print("hv 与 r180 完全一样:", (hv == r180).all())
cv2.waitKey(0)
''',
"rotate30.py": r'''
# 第 17 讲 p8 录屏:绕中心旋转 30 度,再改 -30、再改缩放 0.5
# 预期:rot30 逆时针、四角发黑被裁;rot_minus30 顺时针;rot30_scale05 整张图完整显示、没被裁掉
import cv2
img = cv2.imread("cat.jpg")
h, w = img.shape[:2]
for name, angle, scale in [("rot30", 30, 1.0), ("rot_minus30", -30, 1.0), ("rot30_scale05", 30, 0.5)]:
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, scale)
    rot = cv2.warpAffine(img, M, (w, h))
    cv2.imshow(name, rot)
cv2.waitKey(0)
'''}, FR)

put("18", {
"draw.py": r'''
# 第 18 讲 p6 录屏:在黑色画布上画图写字
# 预期:蓝色对角线、绿色空心框、红色实心框、黄色圆、左下角白字 Hello Vision
import cv2
import numpy as np
canvas = np.zeros((400, 600, 3), dtype=np.uint8)
cv2.line(canvas, (0, 0), (599, 399), (255, 0, 0), 3)
cv2.rectangle(canvas, (50, 50), (200, 150), (0, 255, 0), 2)
cv2.rectangle(canvas, (400, 50), (550, 150), (0, 0, 255), -1)
cv2.circle(canvas, (300, 200), 80, (0, 255, 255), 2)
cv2.putText(canvas, "Hello Vision", (50, 370), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
cv2.imshow("canvas", canvas); cv2.waitKey(0)
''',
"label.py": r'''
# 第 18 讲 p7 录屏:在照片上框出一个物体并写标签;putText 写中文出问号,改用 put_chinese_text
# 预期:english 窗口:框 + 英文标签;question 窗口:中文变成 ???;chinese 窗口:中文正常
# ⚠ 脚本原文写的是 cat 0.95 / 小猫,素材是果盘 → 这里框的是草莓(待脚本统一,见核对清单)
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
'''}, FR)

put("19", {
"overflow.py": r'''
# 第 19 讲 p6 录屏:亲眼看见溢出
# 预期:bad 窗口里原本最亮的地方(白色果盘)冒出深色斑块;good 正常整体变亮;打印 [[94]] [[255]]
import cv2
import numpy as np
img = cv2.imread("cat.jpg")
bad = img + 100
good = cv2.add(img, np.full_like(img, 100))
cv2.imshow("original", img); cv2.imshow("bad", bad); cv2.imshow("good", good)
a = np.uint8([[250]]); b = np.uint8([[100]])
print(a + b, cv2.add(a, b))
cv2.waitKey(0)
''',
"scale_abs.py": r'''
# 第 19 讲 p7 录屏:convertScaleAbs 调亮度和对比度,再修复一张很暗的照片
# 预期:bright 整体变亮;contrast 亮的更亮、暗的更暗;fix 把 dark.jpg 原本看不清的细节找回来
import cv2
img = cv2.imread("cat.jpg")
dark = cv2.imread("dark.jpg")
bright = cv2.convertScaleAbs(img, alpha=1.0, beta=50)
contrast = cv2.convertScaleAbs(img, alpha=1.5, beta=0)
fix = cv2.convertScaleAbs(dark, alpha=1.3, beta=40)
cv2.imshow("bright", bright); cv2.imshow("contrast", contrast)
cv2.imshow("dark", dark); cv2.imshow("fix", fix)
cv2.waitKey(0)
'''}, FR + [("dark.jpg", "dark.jpg")])

put("20", {
"denoise.py": r'''
# 第 20 讲 p6 录屏:撒椒盐噪声,用三种滤波对比
# 预期:均值、高斯只是把噪点抹淡成灰斑;中值滤波几乎把噪点全部清除
import cv2
import numpy as np
img = cv2.imread("cat.jpg")
noisy = img.copy()
rnd = np.random.rand(*img.shape[:2])
noisy[rnd < 0.02] = 0; noisy[rnd > 0.98] = 255
m = cv2.blur(noisy, (5, 5))
g = cv2.GaussianBlur(noisy, (5, 5), 0)
md = cv2.medianBlur(noisy, 5)
cv2.imshow("noisy", noisy); cv2.imshow("blur", m); cv2.imshow("gaussian", g); cv2.imshow("median", md)
cv2.waitKey(0)
''',
"bilateral.py": r'''
# 第 20 讲 p7 录屏:高斯滤波与双边滤波对比
# 预期:高斯整体变糊;双边滤波表面变光滑、边缘仍清晰
# ⚠ 脚本讲的是“一张人像”(美颜磨皮),这里先用果盘;录屏时换成老师自己的人像照片
import cv2
img = cv2.imread("cat.jpg")
g = cv2.GaussianBlur(img, (9, 9), 0)
bi = cv2.bilateralFilter(img, 9, 75, 75)
cv2.imshow("gaussian", g); cv2.imshow("bilateral", bi)
cv2.waitKey(0)
''',
"cartoon.py": r'''
# 第 20 讲 p7 录屏(最后的彩蛋):运行卡通特效示例,按 q 退出
# 来源:[PI]EXP-opencv-edge/edge_cartoon.py;本包改动:摄像头编号提到开头、加了读帧失败判断
import cv2
import numpy as np

CAM = 0          # 摄像头编号:打不开就换 1、2(见第 36 讲排查)
cap = cv2.VideoCapture(CAM)
while True:
    success, img = cap.read()
    if not success:
        print("读不到画面,检查摄像头编号"); break
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.medianBlur(imgGray, 5)
    imgCanny = cv2.Canny(imgBlur, 50, 50)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    img_edge = cv2.cvtColor(255 - imgCanny, cv2.COLOR_GRAY2RGB)
    cartoon = cv2.bitwise_and(color, img_edge)
    cv2.imshow("Cartoon", cartoon)
    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
'''}, FR)

put("21", {
"threshold.py": r'''
# 第 21 讲 p6 录屏:固定阈值 127、80、180,反向 INV,再用 Otsu
# 预期:80 时字迹变细甚至断开;180 时背景阴影也混进来;INV 变成黑底白字;打印 Otsu 自动找到的阈值
import cv2
img = cv2.imread("page.jpg")            # 只拍纸面的“白纸黑字”照片
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
for t in (127, 80, 180):
    _, b1 = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
    cv2.imshow(f"thr_{t}", b1)
_, inv = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
cv2.imshow("inv", inv)
ret, b2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
print("Otsu 阈值:", ret)
cv2.imshow("otsu", b2)
cv2.waitKey(0)
''',
"adaptive.py": r'''
# 第 21 讲 p7 录屏:半边阴影的作业纸,Otsu 失败,自适应阈值成功
# 预期:otsu 窗口里阴影一侧的字看不清或糊成一片;adaptive 窗口里阴影里的字也清清楚楚
import cv2
img = cv2.imread("page_shadow.jpg")     # 左半边在阴影里的作业纸
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, b = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
ad = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
cv2.imshow("otsu", b); cv2.imshow("adaptive", ad)
cv2.waitKey(0)
'''}, [("page.jpg", "page.jpg"), ("page_shadow.jpg", "page_shadow.jpg")])

put("22", {
"erode_dilate.py": r'''
# 第 22 讲 p6 录屏:腐蚀与膨胀,各 1 次和 3 次
# 预期:腐蚀 1 次字变细,3 次有的笔画断了;膨胀 1 次字变粗,3 次糊成一团
import cv2
import numpy as np
binary = cv2.imread("text_binary.png", 0)
kernel = np.ones((5, 5), np.uint8)
e1 = cv2.erode(binary, kernel, iterations=1)
e3 = cv2.erode(binary, kernel, iterations=3)
d1 = cv2.dilate(binary, kernel, iterations=1)
d3 = cv2.dilate(binary, kernel, iterations=3)
for n, im in [("binary", binary), ("erode1", e1), ("erode3", e3), ("dilate1", d1), ("dilate3", d3)]:
    cv2.imshow(n, im)
cv2.waitKey(0)
''',
"open_close.py": r'''
# 第 22 讲 p7 录屏:开运算去小白点,闭运算补小黑洞
# 预期:opened 背景小白点全部消失、大目标几乎不变;closed 目标里的小黑洞被填上
import cv2
import numpy as np
kernel = np.ones((5, 5), np.uint8)
noisy_bin = cv2.imread("noisy_bin.png", 0)
hole_bin = cv2.imread("hole_bin.png", 0)
opened = cv2.morphologyEx(noisy_bin, cv2.MORPH_OPEN, kernel)
closed = cv2.morphologyEx(hole_bin, cv2.MORPH_CLOSE, kernel)
cv2.imshow("noisy_bin", noisy_bin); cv2.imshow("opened", opened)
cv2.imshow("hole_bin", hole_bin); cv2.imshow("closed", closed)
cv2.waitKey(0)
'''}, [("text_binary.png", "text_binary.png"), ("noisy_bin.png", "noisy_bin.png"), ("hole_bin.png", "hole_bin.png")])

put("23", {
"canny.py": r'''
# 第 23 讲 p6 录屏:Canny(50,150),再改 (20,60)、(100,250),最后去掉高斯滤波
# 预期:(20,60) 边缘多、连纹理都出来;(100,250) 只剩最明显轮廓;不滤波多出很多杂乱小线段
import cv2
img = cv2.imread("cat.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
for lo, hi in [(50, 150), (20, 60), (100, 250)]:
    cv2.imshow(f"canny_{lo}_{hi}", cv2.Canny(blur, lo, hi))
cv2.imshow("no_blur_50_150", cv2.Canny(gray, 50, 150))
cv2.waitKey(0)
''',
"trackbar.py": r'''
# 第 23 讲 p7 录屏:用滑动条实时调 Canny 的两个阈值,按 q 退出
# 预期:拖动 low / high 滑动条,边缘实时变化
import cv2
img = cv2.imread("cat.jpg")
blur = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 0)
cv2.namedWindow("edge")
cv2.createTrackbar("low", "edge", 50, 255, lambda x: None)
cv2.createTrackbar("high", "edge", 150, 255, lambda x: None)
while True:
    lo = cv2.getTrackbarPos("low", "edge"); hi = cv2.getTrackbarPos("high", "edge")
    cv2.imshow("edge", cv2.Canny(blur, lo, hi))
    if cv2.waitKey(30) & 0xFF == ord("q"): break
cv2.destroyAllWindows()
'''}, FR)

put("24", {
"histogram.py": r'''
# 第 24 讲 p6 录屏:计算并画出直方图,对比暗 / 亮 / 正常三张图
# 预期:暗图山峰挤在左边、亮图挤在右边、正常图铺得较开
import cv2
import matplotlib.pyplot as plt
for name in ("gray_dark.jpg", "gray_bright.jpg", "gray_normal.jpg"):
    gray = cv2.imread(name, 0)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    plt.plot(hist, label=name)
plt.xlim([0, 256]); plt.legend(); plt.show()
''',
"equalize.py": r'''
# 第 24 讲 p7 录屏:直方图均衡化,再试 CLAHE
# 预期:灰蒙蒙的图均衡化后清晰多了,直方图从窄窄一座山铺满横轴
import cv2
import matplotlib.pyplot as plt
gray = cv2.imread("gray_foggy.jpg", 0)
eq = cv2.equalizeHist(gray)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
eq2 = clahe.apply(gray)
cv2.imshow("foggy", gray); cv2.imshow("equalized", eq); cv2.imshow("clahe", eq2)
for im, n in ((gray, "before"), (eq, "equalizeHist")):
    plt.plot(cv2.calcHist([im], [0], None, [256], [0, 256]), label=n)
plt.xlim([0, 256]); plt.legend(); plt.show()
cv2.waitKey(0)
'''}, [(n, n) for n in ("gray_dark.jpg", "gray_bright.jpg", "gray_normal.jpg", "gray_foggy.jpg")])

put("25", {
"warp.py": r'''
# 第 25 讲 p7 录屏:用四个角点把斜拍的 A4 纸拉正;再故意交换两个点
# 预期:out 窗口是一张端正的纸;wrong 窗口画面被扭成奇怪的样子
# 四个角:按画图软件读出的实际坐标(本照片 paper.jpg 实测),顺序 左上、右上、右下、左下
import cv2
import numpy as np
img = cv2.imread("paper.jpg")
src = np.float32([[151, 58], [489, 104], [417, 612], [41, 538]])
W, H = 420, 594
dst = np.float32([[0, 0], [W-1, 0], [W-1, H-1], [0, H-1]])
M = cv2.getPerspectiveTransform(src, dst)
out = cv2.warpPerspective(img, M, (W, H))
cv2.imshow("out", out)
wrong = np.float32([[489, 104], [151, 58], [417, 612], [41, 538]])     # 左上、右上互换
cv2.imshow("wrong", cv2.warpPerspective(img, cv2.getPerspectiveTransform(wrong, dst), (W, H)))
cv2.waitKey(0)
'''}, [("paper.jpg", "paper.jpg")])
print("module 3 written")
