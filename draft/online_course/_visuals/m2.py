# -*- coding: utf-8 -*-
"""模块一(01)、模块二 图像的秘密(08–15)配图。"""
import cv2, numpy as np, os, tempfile
from _vis import *


FRUIT = os.path.join(HERE, "assets", "fruit_ai_doubao.png")   # 豆包 AI 生成(原 E:/teaching/openCV/lajifenlei_demo/不可回收垃圾/水果.png);裁剪后由 _photo() 重新标注"豆包AI生成"


def _photo():
    """通用照片:AI 生成的果盘(无人脸;红/绿/蓝三色鲜明,便于讲通道)。原用 bus.jpg(含路人正脸),2026-11-10 替换。"""
    im = cv2.resize(imread(FRUIT), (810, 810), interpolation=cv2.INTER_AREA)
    im = im[150:770, :]   # 裁成横向 810×620:高≠宽,讲 (高, 宽) 顺序时才看得出区别
    return text(cv2.rectangle(im, (660, 585), (809, 619), (90, 90, 90), -1), "豆包AI生成", (690, 590), 20, (255, 255, 255))   # 裁剪切掉了原标识,重新标注(AI 内容须显式标识)


def v01():
    with Lesson("01") as L:
        im = src("shapes")
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        _, b = cv2.threshold(g, 240, 255, cv2.THRESH_BINARY_INV)
        cnts, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ana = im.copy(); cv2.drawContours(ana, cnts, -1, (0, 0, 0), 4)
        out = im.copy()
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            n = len(cv2.approxPolyDP(c, 0.03 * cv2.arcLength(c, True), True))
            name = {3: "三角", 4: "四边"}.get(n, "圆")
            cv2.rectangle(out, (x, y), (x + w, y + h), (0, 0, 0), 2)
            out = text(out, name, (x + 2, y + 2), 22, (255, 255, 255), (0, 0, 0), pad=3)
        L.add("机器视觉怎样工作", row(tagged([(im, "① 采集"), (b, "② 处理：分出目标"), (ana, "③ 分析：找轮廓"), (out, "④ 输出：给出结论")], 30)),
              "一张形状图走完四步（OpenCV 实际运行结果）")


def v08():
    with Lesson("08") as L:
        im = _photo()
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        n = 8
        # 自动挑一块明暗变化最大的 8×8 区域(车身标志附近),数字才有看头
        f = g.astype(np.float32)
        var = cv2.blur(f * f, (n, n)) - cv2.blur(f, (n, n)) ** 2
        var[:250, :] = 0; var[:, :350] = 0
        cy_, cx_ = np.unravel_index(np.argmax(var), var.shape)
        y0, x0 = cy_ - n // 2, cx_ - n // 2
        patch = g[y0:y0 + n, x0:x0 + n]
        cell = 70
        table = np.full((n * cell, n * cell, 3), 255, np.uint8)
        for i in range(n):
            for j in range(n):
                v = int(patch[i, j]); c = (v, v, v)
                cv2.rectangle(table, (j * cell, i * cell), (j * cell + cell - 1, i * cell + cell - 1), c, -1)
                cv2.putText(table, str(v), (j * cell + 8, i * cell + 44), cv2.FONT_HERSHEY_SIMPLEX, 0.75,
                            (0, 0, 0) if v > 110 else (255, 255, 255), 2, cv2.LINE_AA)
        show = im.copy(); cv2.rectangle(show, (x0 - 4, y0 - 4), (x0 + n + 4, y0 + n + 4), (0, 169, 242), 3)
        L.add("课程导入", row([border(fit(show, h=560)), border(table)]),
              "左：照片（黄框处 8×8 像素）　右：电脑“看到”的灰度数字")
        # 连续放大
        z = []
        for k, s in enumerate([1, 6, 40]):
            hh, ww = int(560 / s), int(810 / s)
            cy, cx = y0 + n // 2, x0 + n // 2
            crop = im if s == 1 else im[max(cy - hh // 2, 0):cy + hh // 2, max(cx - ww // 2, 0):cx + ww // 2]
            z.append(cv2.resize(crop, (405, 280), interpolation=cv2.INTER_NEAREST))
        L.add("像素：图像的最小方格", row(tagged([(z[0], "原图"), (z[1], "放大 6 倍"), (z[2], "放大 40 倍：方格出现")])),
              "同一位置连续放大，直到看见一个个像素方格")
        # 3×3 方格 ↔ 数字
        vals = np.array([[52, 80, 120], [90, 128, 200], [150, 190, 255]], np.uint8)   # 与脚本/教材 2.1 的 3×3 例子一致
        c = 150
        blk = np.full((3 * c, 3 * c, 3), 255, np.uint8); tab = np.full((3 * c, 3 * c, 3), 255, np.uint8)
        for i in range(3):
            for j in range(3):
                v = int(vals[i, j])
                cv2.rectangle(blk, (j * c, i * c), (j * c + c - 1, i * c + c - 1), (v, v, v), -1)
                cv2.rectangle(tab, (j * c, i * c), (j * c + c - 1, i * c + c - 1), (120, 120, 120), 2)
                cv2.putText(tab, str(v), (j * c + 35, i * c + 95), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (40, 40, 40), 3, cv2.LINE_AA)
        arrow = np.full((3 * c, 120, 3), 255, np.uint8)
        cv2.arrowedLine(arrow, (15, 3 * c // 2), (105, 3 * c // 2), (0, 169, 242), 6, tipLength=0.35)
        L.add("方格表变成数字表", row([border(blk), arrow, border(tab)], 10), "每个方格的明暗 = 一个 0–255 的数字")
        # 渐变条
        w = 1024
        bar = np.tile(np.linspace(0, 255, w).astype(np.uint8), (110, 1))
        canvas = np.full((190, w + 60, 3), 255, np.uint8)
        canvas[10:120, 30:30 + w] = bgr(bar)
        for v in (0, 128, 255):
            x = 30 + int(v / 255 * (w - 1))
            cv2.line(canvas, (x, 120), (x, 140), (0, 0, 0), 2)
            canvas = text(canvas, str(v), (x - 18, 145), 28, (40, 40, 40))
        L.add("0 到 255", canvas, "0 = 最暗（黑），255 = 最亮（白），中间是不同深浅的灰")


def v09():
    with Lesson("09") as L:
        im = _photo()
        outs = []
        for wpx in (48, 160, im.shape[1]):
            small = cv2.resize(im, (wpx, int(wpx * im.shape[0] / im.shape[1])), interpolation=cv2.INTER_AREA)
            outs.append((cv2.resize(small, (480, 368), interpolation=cv2.INTER_NEAREST), f"{small.shape[1]}×{small.shape[0]}"))
        L.add("分辨率", row(tagged(outs)), "同一画面，分辨率越高越清晰，数据量也越大")
        sizes = {}
        tmp = tempfile.mkdtemp()
        for ext, prm in ((".jpg", [cv2.IMWRITE_JPEG_QUALITY, 15]), (".png", []), (".bmp", [])):
            p = os.path.join(tmp, "t" + ext); cv2.imencode(ext, im, prm)[1].tofile(p); sizes[ext] = os.path.getsize(p) / 1024
        jpg = imread(os.path.join(tmp, "t.jpg"))
        cx, cy, s = 470, 300, 60
        zj = cv2.resize(jpg[cy:cy + s, cx:cx + s], (420, 420), interpolation=cv2.INTER_NEAREST)
        zp = cv2.resize(im[cy:cy + s, cx:cx + s], (420, 420), interpolation=cv2.INTER_NEAREST)
        L.add("三种常见格式", row(tagged([(zp, f"PNG 无损  {sizes['.png']:.0f} KB"), (zj, f"JPG 高压缩  {sizes['.jpg']:.0f} KB")], 24)),
              f"局部放大：JPG 压得狠会出现方块噪点（同图存 BMP 为 {sizes['.bmp']:.0f} KB）")


def v10():
    with Lesson("10") as L:
        im = _photo()
        im = fit(im, w=520)
        b, g, r = cv2.split(im)
        L.add("通道：三张表叠在一起", grid(tagged([(im, "彩色原图"), (b, "B 通道"), (g, "G 通道"), (r, "R 通道")]), 2),
              "彩色图 = 三张灰度表叠在一起；越亮表示该颜色成分越多")
        L.add("大坑", row(tagged([(im, "按 BGR 正确显示"), (im[..., ::-1], "把 BGR 当 RGB：红蓝互换")])),
              "同一组数字，通道顺序弄错，红草莓就变成了蓝色")
        L.add("灰度图", row(tagged([(im, "彩色"), (cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), "灰度")])), "灰度图只保留明暗，数据量是彩色的三分之一")


def v11():
    with Lesson("11") as L:
        outs = []
        for v, s in (((0, 0, 0), "img[:] = 0"), ((255, 255, 255), "img[:] = 255"), ((0, 0, 255), "img[:] = (0, 0, 255)"), ((255, 0, 0), "img[:] = (255, 0, 0)")):
            a = np.zeros((300, 400, 3), np.uint8); a[:] = v
            outs.append((a, s))
        L.add("实操二", grid(tagged(outs, 24), 2), "同一个 300×400×3 的数组，填入不同的数：黑、白、红、蓝（注意 B-G-R 顺序）")


def v12():
    plt = plt_setup()
    with Lesson("12") as L:
        im = _photo(); tmp = tempfile.mkdtemp(); names, kb = [], []
        for ext in (".jpg", ".png", ".bmp"):
            p = os.path.join(tmp, "out" + ext); cv2.imencode(ext, im)[1].tofile(p)
            names.append("out" + ext); kb.append(os.path.getsize(p) / 1024)
        fig, ax = plt.subplots(figsize=(8, 4.2), dpi=120)
        bars = ax.bar(names, kb, color=["#F2A900", "#0E7C72", "#6B7785"])
        for b_, v in zip(bars, kb):
            ax.text(b_.get_x() + b_.get_width() / 2, v, f"{v:.0f} KB", ha="center", va="bottom", fontsize=14)
        ax.set_ylim(0, max(kb) * 1.15); ax.set_ylabel("文件大小（KB）", fontsize=13); ax.spines[["top", "right"]].set_visible(False); ax.tick_params(labelsize=13)
        ax.set_title(f"同一张 {im.shape[1]}×{im.shape[0]} 图片，imwrite 存成三种格式", fontsize=14)
        L.add("实操二", fig2img(fig), "实测：JPG 最小，BMP 不压缩最大（imwrite 默认参数）")


def v13():
    with Lesson("13") as L:
        im = fit(_photo(), w=720)
        h, w = im.shape[:2]
        pad = 70
        cv = cv2.copyMakeBorder(im, pad, 40, pad, 290, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        O = (pad, pad)
        cv2.arrowedLine(cv, O, (pad + w + 120, pad), (0, 0, 220), 4, tipLength=0.03)
        cv2.arrowedLine(cv, O, (pad, pad + h + 30), (0, 140, 0), 4, tipLength=0.04)
        cv = text(cv, "x →（列）", (pad + w + 10, pad - 50), 26, (0, 0, 220))
        cv = text(cv, "y", (24, pad + h // 2 - 40), 28, (0, 140, 0)); cv = text(cv, "↓", (26, pad + h // 2 - 4), 28, (0, 140, 0))
        cv = text(cv, "原点 img[0, 0]", (pad - 10, 18), 24, (40, 40, 40))
        pts = {"中心": (w // 2, h // 2), "右下角": (w - 1, h - 1), "右上角": (w - 1, 0), "左下角": (0, h - 1)}
        for k, (x, y) in pts.items():
            cv2.circle(cv, (pad + x, pad + y), 9, (0, 169, 242), -1)
            tx = pad + x + (14 if x < w - 1 else -300); ty = pad + y + (8 if y < h - 1 else -80)
            cv = text(cv, f"{k} img[{y}, {x}]", (tx, ty), 24, (255, 255, 255), (55, 42, 31), pad=4)
        cv = text(cv, f"shape = ({h}, {w}, 3)", (pad + w + 8, pad + h // 2 - 40), 22, (55, 42, 31))
        L.add("坐标系", cv, "原点在左上角，x 向右（列）、y 向下（行）；取像素写 img[y, x]，关键位置都用 shape 算")
        # 越界:真实运行 img[0, w] 拿到报错原文
        try:
            im[0, w]
        except IndexError as e:
            msg = str(e)
        term = np.full((330, 760, 3), (36, 30, 30), np.uint8)
        lines = [("h, w = img.shape[:2]", (220, 220, 220)), (f"# h = {h}, w = {w}", (130, 150, 130)),
                 ("print(img[0, w])      # 想取右上角", (220, 220, 220)), ("", None), ("Traceback (most recent call last):", (220, 220, 220)),
                 ("IndexError: " + msg.split(" with ")[0], (110, 110, 255)), ("    with " + msg.split(" with ")[1], (110, 110, 255))]
        for i, (s_, c_) in enumerate(lines):
            if c_: term = text(term, s_, (24, 22 + i * 42), 24, c_)
        n, c = 6, 64
        gr = np.full((2 * c + 120, (n + 1) * c + 40, 3), 255, np.uint8)
        labels = ["0", "1", "2", "…", f"{w - 1}", f"{w}"]
        for j in range(n + 1):
            x0 = 20 + j * c
            if j < n:
                bad_ = j == n - 1
                cv2.rectangle(gr, (x0, 60), (x0 + c, 60 + c), (80, 80, 230) if bad_ else (150, 150, 150), 3 if bad_ else 1)
                gr = text(gr, labels[j], (x0 + 8, 20), 22, (60, 60, 220) if bad_ else (60, 60, 60))
        gr = text(gr, "↑ 不存在", (20 + (n - 1) * c - 4, 60 + c + 12), 22, (60, 60, 220))
        gr = text(gr, f"宽 w = {w}：列号只能是 0 ~ {w - 1}", (20, 60 + c + 50), 22, (40, 40, 40))
        L.add("常见错误", row([term, border(gr)], 30),
              f"右上角要写 img[0, w - 1]：宽 {w} 的图，最大列号是 {w - 1}（高同理，最大行号是 h - 1）")


def v14():
    with Lesson("14") as L:
        n, c = 10, 56
        g = np.full((n * c + 1, n * c + 1, 3), 255, np.uint8)
        y1, y2, x1, x2 = 2, 5, 3, 8
        cv2.rectangle(g, (x1 * c, y1 * c), (x2 * c, y2 * c), (0, 200, 240), -1)
        for i in range(n + 1):
            cv2.line(g, (0, i * c), (n * c, i * c), (150, 150, 150), 1); cv2.line(g, (i * c, 0), (i * c, n * c), (150, 150, 150), 1)
        g = cv2.copyMakeBorder(g, 50, 10, 50, 10, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        for i in range(n):
            cv2.putText(g, str(i), (50 + i * c + 20, 38), 0, 0.7, (0, 0, 200), 2); cv2.putText(g, str(i), (16, 50 + i * c + 36), 0, 0.7, (0, 140, 0), 2)
        g = text(g, "img[2:5, 3:8]", (50 + x1 * c + 12, 50 + y1 * c + 50), 30, (40, 40, 40))
        L.add("切片", g, "行 2、3、4（不含 5）× 列 3–7（不含 8）：一次选中一整块")
        im = fit(_photo(), w=600); h, w = im.shape[:2]
        a = im.copy(); a[100:150, 50:100] = (255, 0, 0)   # 与脚本实操一同一位置
        L.add("实操一", row(tagged([(im, "原图"), (a, "赋值 (255, 0, 0)：出来是蓝色")])), "想涂红色却写成 (255, 0, 0)——OpenCV 是 B-G-R，红色应写 (0, 0, 255)")
        b = im.copy(); cy, cx = h // 2, w // 2; b[cy - 25:cy + 25, cx - 25:cx + 25] = (0, 255, 0)
        L.add("实操二", row(tagged([(im, "原图"), (b, "正中央 50×50 绿色方块")])), "中心用 h // 2、w // 2 算出，切片一次涂满一块")


def v15():
    with Lesson("15") as L:
        im = fit(_photo(), h=420)
        b, g, r = cv2.split(im)
        L.add("实操一", row(tagged([(im, "原图"), (b, "B"), (g, "G"), (r, "R")])), "split 拆出三个通道：草莓在 R 通道最亮、在 B 通道很暗")
        noblue = cv2.merge([np.zeros_like(b), g, r])
        L.add("实操二", row(tagged([(im, "原图"), (noblue, "蓝色通道换成全 0：偏黄"), (cv2.merge([r, g, b]), "merge([r, g, b])：红蓝对调")])),
              "拿掉蓝色只剩红+绿，画面偏黄；交换 b、r，草莓变蓝")
        L.add("实操三", row(tagged([(im, "彩色"), (cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), "cvtColor 转灰度")])), "一行代码转灰度，后续处理更快")
