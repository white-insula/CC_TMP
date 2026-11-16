# -*- coding: utf-8 -*-
"""生成第 26–35 讲的录屏程序与素材(模块四)。只在制作工程包时运行。"""
import os, shutil, json, glob
import cv2, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
A = "assets"
GA = r"E:\下载\Group A （最终版）\Group A （最终版）\代码集\Answer Card Recognition"


def put(d, files, assets=()):
    os.makedirs(d, exist_ok=True)
    for src, dst in assets:
        if os.path.isdir(src):
            if not os.path.exists(os.path.join(d, dst)): shutil.copytree(src, os.path.join(d, dst))
        else:
            shutil.copy(src if os.path.exists(src) else os.path.join(A, src), os.path.join(d, dst))
    for name, code in files.items():
        open(os.path.join(d, name), "w", encoding="utf-8").write(code.lstrip("\n"))


# ---------- 素材 ----------
def make_assets():
    rng = np.random.default_rng(7)
    # 第 28 讲:三个带孔垫片(白底黑色圆环)
    w = np.full((360, 640, 3), 245, np.uint8)
    for cx in (130, 320, 510):
        cv2.circle(w, (cx, 180), 80, (40, 40, 40), -1); cv2.circle(w, (cx, 180), 32, (245, 245, 245), -1)
    cv2.imwrite(f"{A}/washers.png", w)
    # 第 29 讲:形状图上撒几粒“灰尘”(面积只有十几、几十的小轮廓)
    sh = cv2.imread(f"{A}/shapes.png")
    for _ in range(6):
        cv2.circle(sh, (int(rng.integers(20, sh.shape[1] - 20)), int(rng.integers(20, sh.shape[0] - 20))), int(rng.integers(2, 4)), (60, 60, 60), -1)
    cv2.imwrite(f"{A}/shapes_dust.png", sh)
    # 第 31 讲:合成电路板 —— 6 个一样的芯片 + 电阻,每个芯片亮度略有差别,整张加噪声
    pcb = np.zeros((420, 700, 3), np.uint8); pcb[:] = (40, 110, 30)
    chip = np.zeros((60, 90, 3), np.uint8); chip[:] = (25, 25, 25)
    for i in range(6):
        cv2.line(chip, (8 + i * 15, 0), (8 + i * 15, 6), (190, 190, 190), 3); cv2.line(chip, (8 + i * 15, 53), (8 + i * 15, 59), (190, 190, 190), 3)
    cv2.circle(chip, (14, 18), 4, (90, 90, 90), -1)
    k = 0
    for y in (60, 250):
        for x in (60, 270, 480):
            pcb[y:y + 60, x:x + 90] = np.clip(chip.astype(int) + [0, 6, 12, 18, 24, 30][k], 0, 255).astype(np.uint8); k += 1
    for (x, y) in ((200, 170), (420, 170), (600, 360), (150, 360)):
        cv2.rectangle(pcb, (x, y), (x + 40, y + 16), (90, 160, 210), -1)
    for i in range(12):
        cv2.line(pcb, (0, 30 * i + 15), (700, 30 * i + 15), (60, 140, 50), 1)
    pcb = np.clip(pcb + rng.normal(0, 8, pcb.shape), 0, 255).astype(np.uint8)
    cv2.imwrite(f"{A}/pcb.png", pcb)


make_assets()
FRUIT = ("photo_fruit.jpg", "fruit.jpg"); SHAPES = ("shapes.png", "shapes.png")

put("26", {
"hsv_click.py": r'''
# 第 26 讲 p7 录屏:转换到 HSV;打印纯红/纯绿/纯蓝的 HSV;再用鼠标点图取 HSV 值
# 预期:打印 [[[0 255 255]]] [[[60 255 255]]] [[[120 255 255]]];点一点红色图形,H 是 179(红色跨两端)
import cv2
import numpy as np
img = cv2.imread("shapes.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
for bgr in ([0, 0, 255], [0, 255, 0], [255, 0, 0]):
    print(cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV))


def on_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN: print(hsv[y, x])


cv2.imshow("img", img)
cv2.setMouseCallback("img", on_click)
cv2.waitKey(0)
''',
"hsv_trackbar.py": r'''
# 第 26 讲 p8 录屏:6 个滑动条找颜色范围,按 q 退出
# 预期:拖动滑动条到只剩目标颜色为白,记下 6 个数(例:红色图形 H 170~179)
import cv2
img = cv2.imread("shapes.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.namedWindow("mask")
for name, init, mx in [("H1", 0, 179), ("S1", 80, 255), ("V1", 50, 255), ("H2", 179, 179), ("S2", 255, 255), ("V2", 255, 255)]:
    cv2.createTrackbar(name, "mask", init, mx, lambda x: None)
while True:
    h1, s1, v1, h2, s2, v2 = [cv2.getTrackbarPos(n, "mask") for n in ("H1", "S1", "V1", "H2", "S2", "V2")]
    mask = cv2.inRange(hsv, (h1, s1, v1), (h2, s2, v2))
    cv2.imshow("mask", mask); cv2.imshow("img", img)
    if cv2.waitKey(30) & 0xFF == ord("q"): break
print("范围:", (h1, s1, v1), (h2, s2, v2))
'''}, [SHAPES])

put("27", {
"extract_green.py": r'''
# 第 27 讲 p7 录屏:提取绿色
# 预期:mask 里绿色的猕猴桃、薄荷叶变白,其他全黑;result 里只剩绿色部分
import cv2
img = cv2.imread("fruit.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, (35, 80, 50), (85, 255, 255))
result = cv2.bitwise_and(img, img, mask=mask)
cv2.imshow("img", img); cv2.imshow("mask", mask); cv2.imshow("result", result)
cv2.waitKey(0)
''',
"extract_red.py": r'''
# 第 27 讲 p8 录屏:只用 0~10 一段 → 红色不完整;两段合并 → 完整;再开运算去小白点
# 预期:one_band 里草莓边缘缺了一圈;two_bands 完整;opened 零星小白点消失
import cv2
import numpy as np
img = cv2.imread("fruit.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
m1 = cv2.inRange(hsv, (0, 100, 80), (10, 255, 255))
m2 = cv2.inRange(hsv, (170, 100, 80), (179, 255, 255))
mask = cv2.bitwise_or(m1, m2)
opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
print("只用一段:", cv2.countNonZero(m1), " 两段合并:", cv2.countNonZero(mask), " 开运算后:", cv2.countNonZero(opened))
cv2.imshow("one_band", m1); cv2.imshow("two_bands", mask); cv2.imshow("opened", opened)
cv2.waitKey(0)
'''}, [FRUIT])

put("28", {
"contours.py": r'''
# 第 28 讲 p6 录屏:找出并画出轮廓
# 预期:打印“轮廓数: 16”,正好等于图形数量;每个图形描上绿边
import cv2
img = cv2.imread("shapes.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
print("轮廓数:", len(contours))
out = img.copy(); cv2.drawContours(out, contours, -1, (0, 255, 0), 2)
cv2.imshow("binary", binary); cv2.imshow("out", out)
cv2.waitKey(0)
''',
"modes.py": r'''
# 第 28 讲 p7 录屏:垫片图 EXTERNAL 和 TREE 对比;再逐个画轮廓并编号
# 预期:EXTERNAL 3 个(一个垫片一个),TREE 6 个(中间的孔也算);out 里每个垫片有编号 1、2、3
import cv2
img = cv2.imread("washers.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
ext, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
tree, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
print("EXTERNAL:", len(ext), " TREE:", len(tree))
out = img.copy()
for i, c in enumerate(ext):
    cv2.drawContours(out, [c], -1, (0, 0, 255), 2)
    x, y = c[0][0]
    cv2.putText(out, str(i + 1), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
cv2.imshow("out", out)
cv2.waitKey(0)
'''}, [SHAPES, ("washers.png", "washers.png")])

put("29", {
"features.py": r'''
# 第 29 讲 p6 录屏:打印面积和周长 → 面积小于 500 跳过 → 画识别框和中心点
# 预期:打印里有几个面积只有十几、几十的(灰尘噪点);画框时它们被跳过;每个图形有绿框和红色中心点
import cv2
img = cv2.imread("shapes_dust.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
out = img.copy()
for c in contours:
    area = cv2.contourArea(c); peri = cv2.arcLength(c, True)
    print(area, peri)
    if area < 500: continue
    x, y, w, h = cv2.boundingRect(c)
    cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cx, cy = x + w // 2, y + h // 2
    cv2.circle(out, (cx, cy), 5, (0, 0, 255), -1)
cv2.imshow("out", out)
cv2.waitKey(0)
''',
"red_boxes.py": r'''
# 第 29 讲 p7 录屏:颜色识别 + 轮廓,框出红色物体并写面积
# 预期:每个红色图形一个框,框上写 red 和面积;越大的图形面积越大
import cv2
import numpy as np
img = cv2.imread("shapes.png")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mask = cv2.bitwise_or(cv2.inRange(hsv, (0, 100, 80), (10, 255, 255)), cv2.inRange(hsv, (170, 100, 80), (179, 255, 255)))
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
out = img.copy()
for c in contours:
    area = cv2.contourArea(c)
    if area < 500: continue
    x, y, w, h = cv2.boundingRect(c)
    cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.putText(out, f"red {int(area)}", (x, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
cv2.imshow("out", out)
cv2.waitKey(0)
'''}, [SHAPES, ("shapes_dust.png", "shapes_dust.png")])

SHAPE_CODE = r'''
import cv2
img = cv2.imread("shapes.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
out = img.copy()
for c in contours:
    if cv2.contourArea(c) < 500: continue
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, EPS * peri, True)
    n = len(approx); x, y, w, h = cv2.boundingRect(approx)
    if n == 3: name = "triangle"
    elif n == 4: name = "square" if 0.95 <= w / h <= 1.05 else "rectangle"
    elif n == 5: name = "pentagon"
    else: name = "circle"
    cv2.polylines(out, [approx], True, (0, 0, 255), 2)
    cv2.putText(out, name, (x, y + h // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
cv2.imshow(f"eps={EPS}", out)
cv2.waitKey(0)
'''
put("30", {
"shapes_id.py": "# 第 30 讲 p6 录屏:识别并标注形状\n# 预期:三角形、正方形、长方形、圆都标对\nEPS = 0.02\n" + SHAPE_CODE,
"shapes_eps008.py": "# 第 30 讲 p7 录屏:误差参数改成 0.08\n# 预期:圆被拉成四边形,判成 square / rectangle\nEPS = 0.08\n" + SHAPE_CODE,
"shapes_eps0005.py": "# 第 30 讲 p7 录屏:误差参数改成 0.005\n# 预期:角点明显变多,但这张图边缘干净,判断结果不变\nEPS = 0.005\n" + SHAPE_CODE,
}, [SHAPES])

put("31", {
"match_one.py": r'''
# 第 31 讲 p6 录屏:从电路板图里裁出一个芯片当模板,找到最佳匹配
# 预期:打印最高分接近 0.99(就是模板被裁出来的那个芯片);用红框框出来
# ⚠ 脚本讲的是“电路板照片”,本包用合成的电路板 pcb.png(6 个相同芯片);有真实照片时替换即可
import cv2
img = cv2.imread("pcb.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite("template.png", img[60:120, 60:150])      # 第 16 讲的切片:裁出左上那个芯片
tpl = cv2.imread("template.png", 0); th, tw = tpl.shape
res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
_, max_val, _, max_loc = cv2.minMaxLoc(res)
print(max_val)
x, y = max_loc; cv2.rectangle(img, (x, y), (x + tw, y + th), (0, 0, 255), 2)
cv2.imshow("match", img)
cv2.waitKey(0)
''',
"match_many.py": r'''
# 第 31 讲 p7 录屏:用阈值 0.8 找出所有相同芯片;再改 0.5、0.95 对比
# 预期:0.8 六个芯片全框出(同一芯片上有几个重叠框);0.5 出现框错的地方;0.95 有漏掉的
import cv2
import numpy as np
img0 = cv2.imread("pcb.png")
gray = cv2.cvtColor(img0, cv2.COLOR_BGR2GRAY)
tpl = cv2.imread("template.png", 0); th, tw = tpl.shape
res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
for t in (0.8, 0.5, 0.95):
    img = img0.copy()
    ys, xs = np.where(res >= t)
    for x, y in zip(xs, ys):
        cv2.rectangle(img, (x, y), (x + tw, y + th), (0, 255, 0), 1)
    print(f"阈值 {t}: {len(xs)} 个位置")
    cv2.imshow(f"thr_{t}", img)
cv2.waitKey(0)
'''}, [("pcb.png", "pcb.png")])

put("32", {
"make_qr.py": r'''
# 第 32 讲 p5 录屏:两行代码生成二维码(先 pip install qrcode)
# 预期:生成 part.png,用手机扫码显示 PART-2026-0001 | 批次A | 质检合格
import qrcode
qrcode.make("PART-2026-0001 | 批次A | 质检合格").save("part.png")
''',
"read_qr.py": r'''
# 第 32 讲 p7 录屏(前半):识别 part.png,画出边框
# 预期:打印 PART-2026-0001 | 批次A | 质检合格;二维码四周画绿框
import cv2
img = cv2.imread("part.png")
det = cv2.QRCodeDetector()
data, points, _ = det.detectAndDecode(img)
if data:
    pts = points.astype(int).reshape(-1, 2)
    cv2.polylines(img, [pts], True, (0, 255, 0), 3)
    print(data)
cv2.imshow("qr", img)
cv2.waitKey(0)
''',
"scan_qr_cam.py": r'''
# 第 32 讲 p7 录屏(后半):摄像头实时扫码,拿手机上的二维码对准摄像头,按 q 退出
# 预期:画面里框出二维码并打印内容
import cv2
CAM = 0          # 摄像头编号,打不开就换(第 36 讲)
cap = cv2.VideoCapture(CAM)
det = cv2.QRCodeDetector()
while True:
    ok, frame = cap.read()
    if not ok: break
    data, points, _ = det.detectAndDecode(frame)
    if data:
        pts = points.astype(int).reshape(-1, 2)
        cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
        print(data)
    cv2.imshow("scan", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"): break
cap.release()
'''})

put("33", {
"sort_colors.py": r'''
# 第 33 讲 p6+p7 录屏:颜色字典 + 主循环 + get_shape + 计数
# 预期:每个红/黄/蓝图形框出并写“颜色 形状”;最后打印各类数量的字典(绿色不在字典里,不识别)
import cv2
import numpy as np
colors = {
    "red":    [((0, 100, 80), (10, 255, 255)), ((170, 100, 80), (179, 255, 255))],
    "yellow": [((20, 100, 100), (35, 255, 255))],
    "blue":   [((100, 100, 80), (130, 255, 255))],
}
kernel = np.ones((5, 5), np.uint8)


def get_shape(c):
    peri = cv2.arcLength(c, True); n = len(cv2.approxPolyDP(c, 0.02 * peri, True))
    return {3: "triangle", 4: "rectangle"}.get(n, "circle" if n > 6 else "other")


img = cv2.imread("shapes.png")
hsv = cv2.cvtColor(cv2.GaussianBlur(img, (5, 5), 0), cv2.COLOR_BGR2HSV)
out = img.copy(); count = {}
for name, ranges in colors.items():
    mask = np.zeros(hsv.shape[:2], np.uint8)
    for lo, hi in ranges:
        mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lo, hi))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    cv2.imshow(f"mask_{name}", mask)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c) < 800: continue
        label = f"{name} {get_shape(c)}"; count[label] = count.get(label, 0) + 1
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 0, 0), 2)
        cv2.putText(out, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
print(count)
cv2.imshow("out", out)
cv2.waitKey(0)
'''}, [SHAPES])

CARD_LIB = r'''
import cv2, json
import numpy as np


def imread(path):
    return cv2.imdecode(np.fromfile(path, np.uint8), 1)      # 路径里有中文也能读


def locate(img):
    """第 34 讲 p6:找四个定位块 → 拉正成 600×800;找不到返回 None"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    marks = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if 1.6 <= w / h <= 2.3 and 300 <= cv2.contourArea(c) <= 600: marks.append((x, y, w, h))
    if len(marks) != 4:
        return None, marks
    marks.sort(key=lambda m: m[1])
    (x0, y0, w0, h0), (x1, y1, w1, h1) = sorted(marks[:2]); (x2, y2, w2, h2), (x3, y3, w3, h3) = sorted(marks[2:])
    src = np.float32([[x0, y0], [x1 + w1, y1], [x3 + w3, y3 + h3], [x2, y2 + h2]])      # 左上、右上、右下、左下
    dst = np.float32([[0, 0], [599, 0], [599, 799], [0, 799]])
    return cv2.warpPerspective(img, cv2.getPerspectiveTransform(src, dst), (600, 800)), marks


def read_choices(card, t, show=False):
    """第 34 讲 p8:先裁出选择题区域、缩放到 600×400,再按模板坐标数白色像素"""
    _, binary = cv2.threshold(cv2.cvtColor(card, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY_INV)
    x0, y0, w0, h0 = t["choice_roi_rect"]
    choice = cv2.resize(binary[y0:y0+h0, x0:x0+w0], (600, 400))
    view = cv2.resize(card[y0:y0+h0, x0:x0+w0], (600, 400))
    picks = []
    for q, group in enumerate(t["choice_pos_list"]):
        picked = ""
        for j, (x, y, w, h) in enumerate(group):
            if cv2.countNonZero(choice[y:y+h, x:x+w]) >= 100:
                picked += "ABCD"[j]; cv2.rectangle(view, (x, y), (x+w, y+h), (0, 255, 0), 1)
        if show: print(q + 1, picked)
        picks.append(picked)
    return picks, view


def read_number(card, t):
    """第 35 讲 p5:学号区域按列看涂了 0~9 中的哪个"""
    _, binary = cv2.threshold(cv2.cvtColor(card, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY_INV)
    x0, y0, w0, h0 = t["number_roi_rect"]
    num = cv2.resize(binary[y0:y0+h0, x0:x0+w0], (400, 300))
    sid = ""
    for col in t["number_pos_list"]:
        cnt = [cv2.countNonZero(num[y:y+h, x:x+w]) for x, y, w, h in col]
        sid += str(int(np.argmax(cnt)))
    return sid


def recognize(path, t):
    """第 35 讲 p5:封装 —— 传入图片路径,返回 (学号, 答案列表);定位失败返回 None"""
    card, _ = locate(imread(path))
    if card is None:
        return None
    return read_number(card, t), read_choices(card, t)[0]
'''

put("34", {
"card_lib.py": "# 第 34、35 讲共用的答题卡识别函数(录屏时按讲次分段讲解)\n" + CARD_LIB,
"locate.py": r'''
# 第 34 讲 p6 录屏:找四个定位块(画红框)→ 透视拉正成 600×800
# 预期:四个角的定位块都被框出;card 窗口是拉正后的答题卡
import cv2
from card_lib import imread, locate
img = imread("212001.jpg")
card, marks = locate(img)
show = img.copy()
for x, y, w, h in marks: cv2.rectangle(show, (x, y), (x + w, y + h), (0, 0, 255), 2)
print("定位块:", marks)
cv2.imshow("marks", show); cv2.imshow("card", card)
cv2.waitKey(0)
''',
"read_answers.py": r'''
# 第 34 讲 p8 录屏:判出每道题的答案,被涂格子画绿框
# 预期:打印 1 A、2 D、3 C ……(与原卡一致);choice 窗口里被涂的格子都有绿框
import cv2, json
from card_lib import imread, locate, read_choices
with open("template.json") as f: t = json.load(f)
card, _ = locate(imread("212001.jpg"))
picks, view = read_choices(card, t, show=True)
cv2.imshow("choice", view)
cv2.waitKey(0)
'''}, [(os.path.join(GA, "答题卡扫描文件", "212001.jpg"), "212001.jpg"), (os.path.join(GA, "settings", "template.json"), "template.json")])

put("35", {
"card_lib.py": "# 第 34、35 讲共用的答题卡识别函数\n" + CARD_LIB,
"batch.py": r'''
# 第 35 讲 p6+p8 录屏:读答案、批量识别 40 张卡、算分、生成 Excel 成绩单(错题标红)
# 预期:几秒钟处理完 40 张,终端打印每个学号和分数;生成 成绩单.xlsx,错题红色
import os, json
import openpyxl
from openpyxl.styles import Font
from card_lib import recognize
with open("template.json") as f: t = json.load(f)
answers = {}
for line in open("答案.txt", encoding="utf-8"):
    no, ans, score = line.strip().split("-"); answers[int(no)] = (ans, int(score))
wb = openpyxl.Workbook(); ws = wb.active
ws.append(["学号", "总分"] + [f"第{i}题" for i in answers])
failed = []
for name in sorted(os.listdir("答题卡扫描文件")):
    if not name.endswith(".jpg"): continue
    r = recognize(os.path.join("答题卡扫描文件", name), t)
    if r is None: failed.append(name); continue
    sid, picks = r
    total = sum(answers[q][1] for q in answers if picks[q - 1] == answers[q][0])
    ws.append([sid, total] + picks)
    for q in answers:
        if picks[q - 1] != answers[q][0]:
            ws.cell(row=ws.max_row, column=2 + q).font = Font(color="FF0000")
    print(sid, total)
if failed: ws.append(["识别失败，请人工检查："] + failed)
wb.save("成绩单.xlsx")
print("共", ws.max_row - 1, "行;失败", failed)
'''}, [(os.path.join(GA, "答题卡扫描文件"), "答题卡扫描文件"), (os.path.join(GA, "答案.txt"), "答案.txt"), (os.path.join(GA, "settings", "template.json"), "template.json")])
print("module 4 written")
