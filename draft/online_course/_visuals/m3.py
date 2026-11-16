# -*- coding: utf-8 -*-
"""模块三 图像处理基础(16–25,21 另见 21/visuals.py)配图。"""
import cv2, numpy as np
from _vis import *

AMB = (0, 169, 242)


def _bus(w=640):
    return fit(src("bus")[0:620, :], w=w)


def _room(w=None, h=420, t=0.4):
    f = frame_of("room", t)
    return fit(f, w=w) if w else fit(f, h=h)


def _scan_corners(img):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    e = cv2.Canny(cv2.GaussianBlur(g, (5, 5), 0), 50, 150)
    e = cv2.dilate(e, np.ones((3, 3), np.uint8))
    cnts, _ = cv2.findContours(e, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in sorted(cnts, key=cv2.contourArea, reverse=True)[:5]:
        a = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
        if len(a) == 4:
            p = a.reshape(4, 2).astype(np.float32)
            s, d = p.sum(1), np.diff(p, axis=1).ravel()
            return np.array([p[np.argmin(s)], p[np.argmin(d)], p[np.argmax(s)], p[np.argmax(d)]], np.float32)
    raise RuntimeError("没找到四边形")


def _warp(img, pts, W=420, H=560):
    M = cv2.getPerspectiveTransform(pts, np.float32([[0, 0], [W, 0], [W, H], [0, H]]))
    return cv2.warpPerspective(img, M, (W, H))


def v16():
    with Lesson("16") as L:
        im = _bus(720)
        x1, y1, x2, y2 = 300, 260, 600, 420
        show = im.copy(); cv2.rectangle(show, (x1, y1), (x2, y2), AMB, 4)
        show = text(show, f"img[{y1}:{y2}, {x1}:{x2}]", (x1, y1 - 40), 26, (255, 255, 255), (55, 42, 31), 4)
        roi = im[y1:y2, x1:x2]
        L.add("裁剪", row([border(show), border(fit(roi, h=show.shape[0] // 2))]), "先 y 后 x：切片 [行范围, 列范围] 取出感兴趣区域")
        L.add("实操一", row(tagged([(show, "原图上框出区域"), (fit(roi, h=320), "裁剪结果")])), "坐标可用画图软件读出，再写进切片")
        h, w = im.shape[:2]
        a = cv2.resize(im, (w // 2, h // 2)); b = cv2.resize(im, None, fx=0.25, fy=0.25)
        c = cv2.resize(im, (400, 400))
        L.add("实操二", row(tagged([(a, f"(w//2, h//2) → {a.shape[1]}×{a.shape[0]}"), (b, f"fx=fy=0.25 → {b.shape[1]}×{b.shape[0]}"), (c, "硬设 (400, 400)：变形")], 20)),
              "按比例缩放不变形；直接指定宽高可能把画面拉扁")


def v17():
    with Lesson("17") as L:
        im = _bus(480)
        L.add("翻转", grid(tagged([(im, "原图"), (cv2.flip(im, 1), "flip(img, 1) 水平"), (cv2.flip(im, 0), "flip(img, 0) 垂直"), (cv2.flip(im, -1), "flip(img, -1) 都翻")]), 2),
              "flip 的第二个参数：1 左右翻、0 上下翻、-1 两个方向都翻")
        L.add("旋转 90°", row(tagged([(im, "原图"), (cv2.rotate(im, cv2.ROTATE_90_CLOCKWISE), "顺时针 90°"), (cv2.rotate(im, cv2.ROTATE_180), "180°")])),
              "cv2.rotate 只能转 90° 的整数倍，宽高会互换")
        h, w = im.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), 30, 1.0)
        r = cv2.warpAffine(im, M, (w, h))
        L.add("实操二", row(tagged([(im, "原图"), (r, "绕中心逆时针 30°")])), "旋转后四角被裁掉、空白处补黑，这是正常现象")


def v18():
    from m2 import _photo
    with Lesson("18") as L:
        c = np.zeros((400, 600, 3), np.uint8)
        cv2.line(c, (0, 0), (599, 399), (255, 0, 0), 3)
        cv2.rectangle(c, (50, 50), (200, 150), (0, 255, 0), 2)
        cv2.rectangle(c, (400, 50), (550, 150), (0, 0, 255), -1)
        cv2.circle(c, (300, 200), 80, (0, 255, 255), 2)
        cv2.putText(c, "Hello Vision", (50, 370), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        L.add("实操一", border(c), "黑色画布：蓝线、绿色空心框、红色实心框、黄色圆、白色英文（与脚本参数一致）")
        out = _photo()
        x, y, w, h = 142, 305, 147, 163
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(out, "strawberry 0.95", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        out = text(out, "草莓", (x, y - 40), 30, (0, 255, 0))
        L.add("实操二", out, "rectangle 手工框出草莓，putText 写英文，PIL 写中文；标签和 0.95 为示例，不是模型预测")
        L.add("课程导入", out, "画框、写字：所有检测结果都靠它展示出来")


def v19():
    with Lesson("19") as L:
        im = _room(h=380)
        dark = cv2.convertScaleAbs(im, alpha=0.35, beta=0)
        L.add("课程导入", row(tagged([(dark, "曝光不足"), (cv2.convertScaleAbs(dark, alpha=2.6, beta=10), "调亮后")])), "调整亮度和对比度，暗处的细节又回来了")
        wrong = im + np.uint8(100)
        right = cv2.add(im, 100)
        L.add("实操一", row(tagged([(im, "原图"), (wrong, "img + 100：溢出"), (right, "cv2.add：封顶")])),
              "uint8 超过 255 会从 0 重新数起，亮处反而变暗、画面出现怪色")
        outs = [(cv2.convertScaleAbs(im, alpha=a, beta=b), f"α={a}, β={b}") for a, b in ((1.0, 0), (1.0, 60), (1.6, 0), (0.6, 0))]
        L.add("实操二", grid(tagged(outs, 22), 2), "β 加亮度、α 拉对比度：convertScaleAbs 自动截到 0–255")


def v20():
    with Lesson("20") as L:
        im = _bus(560)
        rng = np.random.default_rng(1)
        gau = np.clip(im + rng.normal(0, 25, im.shape), 0, 255).astype(np.uint8)
        sp = im.copy(); m = rng.random(im.shape[:2]); sp[m < 0.03] = 0; sp[m > 0.97] = 255
        L.add("噪声从哪里来", row(tagged([(gau, "高斯噪声：满屏细颗粒"), (sp, "椒盐噪声：黑白杂点")])), "暗光、高感光度、传输干扰都会带来噪声")
        y, x, s = 260, 300, 90
        z = lambda a: cv2.resize(a[y:y + s, x:x + s], (300, 300), interpolation=cv2.INTER_NEAREST)
        L.add("课程导入", row(tagged([(z(im), "干净"), (z(gau), "有噪点（放大）")])), "放大看，噪点是一颗颗随机变化的像素")
        outs = [(sp, "椒盐噪声原图"), (cv2.blur(sp, (5, 5)), "均值 blur"), (cv2.GaussianBlur(sp, (5, 5), 0), "高斯 GaussianBlur"), (cv2.medianBlur(sp, 5), "中值 medianBlur")]
        L.add("实操一", grid(tagged(outs, 22), 2), "对付椒盐噪声，中值滤波效果最好")
        bil = cv2.bilateralFilter(im, 9, 75, 75)
        g = cv2.medianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), 7)
        edge = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
        col_ = im
        for _ in range(5):
            col_ = cv2.bilateralFilter(col_, 9, 50, 50)
        cartoon = cv2.bitwise_and(col_, col_, mask=edge)
        L.add("实操二", row(tagged([(im, "原图"), (bil, "双边滤波：磨平但保边"), (cartoon, "卡通特效")], 20)), "双边滤波 + 边缘线 = 卡通画（参考：[PI]EXP-opencv-edge/edge_cartoon.py）")


def _defect_binary():
    b = np.zeros((300, 420), np.uint8)
    cv2.rectangle(b, (60, 60), (360, 240), 255, -1)
    rng = np.random.default_rng(5)
    for _ in range(60):
        cv2.circle(b, (int(rng.integers(0, 420)), int(rng.integers(0, 300))), 2, 255, -1)
    for _ in range(25):
        cv2.circle(b, (int(rng.integers(80, 340)), int(rng.integers(80, 220))), 2, 0, -1)
    return b


def v22():
    with Lesson("22") as L:
        b = _defect_binary(); k = np.ones((5, 5), np.uint8)
        L.add("课程导入", border(b), "二值化后常见的毛病：背景里的白点、目标上的小黑洞")
        L.add("实操一", row(tagged([(b, "原图"), (cv2.erode(b, k), "腐蚀：白色变瘦"), (cv2.dilate(b, k), "膨胀：白色变胖")], 20)),
              "5×5 结构元素：腐蚀吃掉小白点，膨胀填上小黑洞")
        op = cv2.morphologyEx(b, cv2.MORPH_OPEN, k); cl = cv2.morphologyEx(op, cv2.MORPH_CLOSE, k)
        L.add("实操二", row(tagged([(b, "原图"), (op, "开运算：去白点"), (cl, "再闭运算：补黑洞")], 20)), "开 = 先腐蚀后膨胀；闭 = 先膨胀后腐蚀")
        im = src("paper")
        e = cv2.Canny(cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), (5, 5), 0), 50, 150)
        d = cv2.dilate(e, np.ones((5, 5), np.uint8), iterations=2); er = cv2.erode(d, np.ones((5, 5), np.uint8), iterations=1)
        L.add("应用", row(tagged([(e, "边缘：有断线"), (d, "膨胀：连上"), (er, "腐蚀：变回细线")], 20)), "文档扫描的预处理（参考：[PI]EXP-Opencv-Scan/scan.py）")


def v23():
    plt = plt_setup()
    with Lesson("23") as L:
        im = _bus(640)
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        e = cv2.Canny(cv2.GaussianBlur(g, (3, 3), 0), 80, 180)
        L.add("课程导入", row(tagged([(im, "照片"), (255 - e, "只留边缘：像一幅简笔画")])), "边缘保留了物体的轮廓信息")
        yrow = 330
        fig, ax = plt.subplots(1, 2, figsize=(12, 3.8), dpi=110, gridspec_kw={"width_ratios": [1, 1.6]})
        show = cv2.cvtColor(im, cv2.COLOR_BGR2RGB).copy(); cv2.line(show, (0, yrow), (639, yrow), (242, 169, 0), 3)
        ax[0].imshow(show); ax[0].axis("off"); ax[0].set_title("取一行像素（黄线）", fontsize=13)
        v = g[yrow].astype(int); dv = np.abs(np.diff(v))
        ax[1].plot(v, color="#1F2A37", lw=1.5)
        jumps = np.where(dv > 60)[0]
        ax[1].scatter(jumps, v[jumps], color="#D7263D", s=24, zorder=3, label="突变处 = 边缘")
        ax[1].set_xlabel("x（列）", fontsize=12); ax[1].set_ylabel("灰度值", fontsize=12); ax[1].legend(fontsize=12)
        ax[1].spines[["top", "right"]].set_visible(False); ax[1].set_title("这一行的灰度变化", fontsize=13)
        fig.tight_layout()
        L.add("边缘：数字突变", fig2img(fig), "灰度值突然大幅跳变的地方，就是边缘")
        outs = [(255 - cv2.Canny(g, a, b), f"Canny({a}, {b})") for a, b in ((30, 80), (80, 180), (200, 400))]
        L.add("实操二", row(tagged(outs, 22)), "阈值太低：杂纹多；太高：轮廓断。滑动条实时调到合适为止")
        L.add("实操一", row(tagged([(im, "原图"), (255 - e, "Canny(80, 180)，黑白反显")])), "先转灰度、轻微模糊，再 Canny")
        col_ = im
        for _ in range(5):
            col_ = cv2.bilateralFilter(col_, 9, 50, 50)
        edge = cv2.adaptiveThreshold(cv2.medianBlur(g, 7), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)
        L.add("边缘的用途", row(tagged([(im, "原图"), (cv2.bitwise_and(col_, col_, mask=edge), "卡通特效")])), "边缘还用于找轮廓、测尺寸、做特效")


def _hist(ax, g, title, color="#1F2A37"):
    h = cv2.calcHist([g], [0], None, [256], [0, 256]).ravel()
    ax.fill_between(range(256), h, color=color, alpha=0.85); ax.set_xlim(0, 255); ax.set_yticks([])
    ax.set_title(title, fontsize=12); ax.spines[["top", "right", "left"]].set_visible(False)


def v24():
    plt = plt_setup()
    with Lesson("24") as L:
        g = cv2.cvtColor(_room(h=360), cv2.COLOR_BGR2GRAY)
        variants = [(cv2.convertScaleAbs(g, alpha=0.4), "偏暗：挤在左边"), (cv2.convertScaleAbs(g, alpha=0.5, beta=150), "偏亮：挤在右边"),
                    (cv2.convertScaleAbs(g, alpha=0.3, beta=90), "对比度低：挤在中间"), (g, "正常：铺得较开")]
        fig, axs = plt.subplots(2, 4, figsize=(14, 5.4), dpi=100, gridspec_kw={"height_ratios": [1.5, 1]})
        for k, (im, t) in enumerate(variants):
            axs[0, k].imshow(im, cmap="gray", vmin=0, vmax=255); axs[0, k].axis("off")
            _hist(axs[1, k], im, t)
        fig.tight_layout()
        L.add("看懂直方图的形状", fig2img(fig), "看直方图挤在哪儿，就知道图偏暗、偏亮还是灰蒙蒙")
        fig, axs = plt.subplots(1, 2, figsize=(12, 4), dpi=100, gridspec_kw={"width_ratios": [1, 1.4]})
        axs[0].imshow(g, cmap="gray"); axs[0].axis("off"); _hist(axs[1], g, "calcHist：横轴 0–255 亮度，纵轴 像素个数")
        fig.tight_layout()
        L.add("实操一", fig2img(fig), "数一数每个亮度有多少个像素，画成柱状")
        dark = variants[2][0]; eq = cv2.equalizeHist(dark)
        fig, axs = plt.subplots(2, 2, figsize=(11, 5.6), dpi=100, gridspec_kw={"height_ratios": [1.5, 1]})
        for k, (im, t) in enumerate(((dark, "均衡化前"), (eq, "equalizeHist 之后"))):
            axs[0, k].imshow(im, cmap="gray", vmin=0, vmax=255); axs[0, k].axis("off"); _hist(axs[1, k], im, t)
        fig.tight_layout()
        L.add("实操二", fig2img(fig), "均衡化把挤在一起的亮度摊开，对比度明显提高")


def v25():
    with Lesson("25") as L:
        im = src("paper")
        pts = _scan_corners(im)
        warped = _warp(im, pts)
        L.add("课程导入", row([border(im), border(fit(warped, h=im.shape[0]))]), "斜拍的文件 → 透视变换拉正（[PI]EXP-Opencv-Scan 素材，OpenCV 实际运行）")
        show = im.copy()
        for k, (x, y) in enumerate(pts.astype(int)):
            cv2.circle(show, (x, y), 10, (0, 0, 230), -1)
            show = text(show, f"{['①左上', '②右上', '③右下', '④左下'][k]} ({x}, {y})", (min(x + 8, im.shape[1] - 230), max(y - 40, 4)), 22, (255, 255, 255), (0, 0, 180), 3)
        L.add("实操一", border(show), "按 左上 → 右上 → 右下 → 左下 的顺序记下四个角点")
        L.add("实操二", row([border(show), border(fit(warped, h=im.shape[0]))]), "getPerspectiveTransform 求矩阵，warpPerspective 拉正")
        g = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        scan = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 10)
        L.add("再加一步", row(tagged([(warped, "矫正后"), (scan, "自适应阈值：扫描件效果")])), "拉正 + 二值化，手机照片变成“扫描件”")
        # 原理示意:四点对四点
        W, H = 420, 560
        canvas = np.full((im.shape[0], im.shape[1] + W + 120, 3), 255, np.uint8)
        canvas[:, :im.shape[1]] = im
        dst = np.float32([[0, 0], [W, 0], [W, H], [0, H]]) + [im.shape[1] + 80, (im.shape[0] - H) / 2]
        cv2.polylines(canvas, [pts.astype(np.int32)], True, (0, 0, 230), 3)
        cv2.polylines(canvas, [dst.astype(np.int32)], True, (0, 150, 0), 3)
        for a, b in zip(pts, dst):
            cv2.line(canvas, tuple(a.astype(int)), tuple(b.astype(int)), AMB, 2, cv2.LINE_AA)
            cv2.circle(canvas, tuple(a.astype(int)), 8, (0, 0, 230), -1); cv2.circle(canvas, tuple(b.astype(int)), 8, (0, 150, 0), -1)
        L.add("原理", border(canvas), "梯形的四个角（红）一一对应到矩形的四个角（绿）")
