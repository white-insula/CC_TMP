# -*- coding: utf-8 -*-
"""模块八 综合项目:工业分拣与质检(61–69)配图。
统一用合成的“传送带俯拍工件”场景:比例 4 像素 = 1 毫米;标准件为直径 40 mm 圆片。所有数值由 OpenCV 实际计算。"""
import cv2, numpy as np, csv, io
from _vis import *
from m4 import mask_of, ZH

PX_PER_MM = 4.0
SPEC_D, TOL = 40.0, 1.0
AMB = (0, 169, 242)
CONFIG = {"roi": (40, 40, 920, 520), "min_area": 2000, "solidity_min": 0.95, "circularity_min": 0.85}


def line_items():
    r = int(SPEC_D / 2 * PX_PER_MM)            # 80 px
    return [("circle", "red", (160, 170), r, 0, None), ("circle", "yellow", (400, 170), r, 0, None), ("circle", "blue", (640, 170), r, 0, None),
            ("circle", "red", (160, 410), int(36 / 2 * PX_PER_MM), 0, None), ("circle", "yellow", (400, 410), r, 0, "notch"),
            ("circle", "blue", (640, 410), r, 0, "dent"), ("circle", "red", (850, 290), r, 0, None)]


def scene(**kw):
    return parts_scene(line_items(), w=980, h=580, **kw)[0]


def separate(im):
    g = cv2.GaussianBlur(cv2.cvtColor(im, cv2.COLOR_BGR2HSV)[..., 1], (5, 5), 0)   # 用饱和度分离彩色工件和灰色传送带
    _, b = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    b = cv2.morphologyEx(b, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    cs = [c for c in cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0] if cv2.contourArea(c) > CONFIG["min_area"]]
    return g, b, cs


def hsv_mean(im, c):
    """第 64 讲的做法:先求掩膜内平均 BGR,再转 HSV(直接平均 H 会把红色算错)。"""
    m = np.zeros(im.shape[:2], np.uint8); cv2.drawContours(m, [c], -1, 255, -1)
    m = cv2.erode(m, np.ones((9, 9), np.uint8))
    b, g, r, _ = cv2.mean(im, mask=m)
    return cv2.cvtColor(np.uint8([[[b, g, r]]]), cv2.COLOR_BGR2HSV)[0, 0], m


def color_of(im, c):
    (h, s, v), _ = hsv_mean(im, c)
    if s < 60: return "unknown"
    return "red" if h < 10 or h > 170 else "yellow" if 20 <= h < 35 else "blue" if 100 <= h < 130 else "unknown"


def inspect(im, c):
    a = cv2.contourArea(c); p = cv2.arcLength(c, True)
    sol = a / cv2.contourArea(cv2.convexHull(c)); circ = 4 * np.pi * a / p ** 2
    (_, _), (w, h), _ = cv2.minAreaRect(c); d = (w + h) / 2 / PX_PER_MM
    reasons = []
    if abs(d - SPEC_D) > TOL: reasons.append(f"尺寸 {d:.1f}mm")
    if sol < CONFIG["solidity_min"]: reasons.append("缺口")
    if circ < CONFIG["circularity_min"]: reasons.append("变形")
    return dict(color=color_of(im, c), d=d, sol=sol, circ=circ, ok=not reasons, reasons=reasons)


def annotate(im, results):
    o = im.copy()
    for c, r in results:
        x, y, w, h = cv2.boundingRect(c); col = (0, 200, 0) if r["ok"] else (0, 0, 230)
        cv2.drawContours(o, [c], -1, col, 4)
        o = text(o, f"{ZH.get(r['color'], '?')} {r['d']:.1f}mm {'OK' if r['ok'] else 'NG'}", (x, y + h + 6), 20, (255, 255, 255), col, 3)
        if r["reasons"]:
            o = text(o, "/".join(x_ for x_ in r["reasons"] if not x_.startswith("尺寸")) or "尺寸超差", (x, y + h + 40), 18, (255, 255, 255), col, 3)
    return o


def run(im):
    _, _, cs = separate(im)
    return [(c, inspect(im, c)) for c in sorted(cs, key=lambda c: (cv2.boundingRect(c)[1] // 100, cv2.boundingRect(c)[0]))]


def v61():
    with Lesson("61") as L:
        L.add("项目场景", scene(), "相机俯拍传送带：工件颜色不同，有的尺寸偏小、有缺口或变形（课程合成场景）")


def v62():
    with Lesson("62") as L:
        im = scene()
        h, w = im.shape[:2]
        M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), np.float32([[120, 40], [w - 120, 40], [w, h], [0, h]]))
        tilt = cv2.warpPerspective(im, M, (w, h), borderValue=(60, 60, 60))
        L.add("相机", row(tagged([(im, "✓ 垂直俯拍：圆还是圆"), (tilt, "✗ 倾斜：近大远小，尺寸量不准")], 20)), "相机要垂直于传送带安装并固定")
        items = [("circle", "yellow", (200, 200), 90, 0, None), ("square", "green", (460, 200), 150, 0, None)]
        light, _ = parts_scene(items, w=660, h=400, bg=(205, 205, 200), noise=3)
        dark, _ = parts_scene(items, w=660, h=400, bg=(45, 45, 45), noise=3)
        ob = lambda x: cv2.threshold(cv2.cvtColor(x, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        L.add("背景", grid(tagged([(light, "浅色背景"), (ob(light), "二值化：黄色工件消失了"), (dark, "深色背景"), (ob(dark), "二值化：两个工件都清楚")], 20), 2),
              "背景和工件反差要大：同样的 Otsu 二值化，深色背景一次分干净")
        side = scene(light="side"); even = scene(light="even")
        gs = lambda x: cv2.threshold(cv2.cvtColor(x, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        L.add("光照", grid(tagged([(side, "单灯斜照：一边亮一边暗"), (gs(side), "二值化：暗的一侧糊成一片"), (even, "对称打光：均匀"), (gs(even), "二值化：工件轮廓清楚")], 20), 2),
              "光照不均是二值化失败最常见的原因")
        L.add("实操一", row(tagged([(gs(side), "单灯"), (gs(even), "双灯对称")], 20)), "实时预览二值化，对比两种打光")
        plt = plt_setup()
        fig, ax = plt.subplots(1, 3, figsize=(13, 3.6), dpi=100)
        for a, (x, t) in zip(ax, ((cv2.convertScaleAbs(even, alpha=0.45), "欠曝：堆在左边"), (even, "合适：分布开"), (cv2.convertScaleAbs(even, alpha=1.0, beta=110), "过曝：挤在 255"))):
            hh = cv2.calcHist([cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)], [0], None, [256], [0, 256]).ravel()
            a.fill_between(range(256), hh, color="#1F2A37"); a.set_xlim(0, 255); a.set_yticks([]); a.set_title(t, fontsize=13)
            a.spines[["top", "right", "left"]].set_visible(False)
        fig.tight_layout()
        L.add("实操二", fig2img(fig), "调灯光时看实时直方图：既不堆在 0 也不挤在 255")


def v63():
    with Lesson("63") as L:
        im = scene()
        x0, y0, x1, y1 = CONFIG["roi"]
        roi = im[y0:y1, x0:x1]
        g, b, cs = separate(roi)
        sep = roi.copy()
        for k, c in enumerate(cs):
            x, y, w, h = cv2.boundingRect(c); cv2.rectangle(sep, (x, y), (x + w, y + h), AMB, 3)
            sep = text(sep, f"#{k + 1}", (x + 4, y + 4), 22, (255, 255, 255), (55, 42, 31), 3)
        steps = [(im, "① 原图"), (roi, "② 裁检测区 ROI"), (cv2.GaussianBlur(roi, (5, 5), 0), "③ 高斯去噪"), (g, "④ 取饱和度通道"), (b, "⑤ Otsu 二值化 + 开运算"), (sep, f"⑥ 分离出 {len(cs)} 个工件")]
        L.add("预处理流程", grid(tagged(steps, 20), 3), "六步预处理：每一步都可以单独显示出来检查")
        L.add("实操一", grid(tagged(steps[1:5], 20), 2), "一步步搭：每加一步就看一眼中间结果")
        L.add("实操二", sep, f"找轮廓 + 面积过滤（min_area={CONFIG['min_area']}）：每个工件一个编号")


def v64():
    with Lesson("64") as L:
        im = scene(); res = run(im); o = im.copy()
        BINS = {"red": 1, "yellow": 2, "blue": 3}
        for c, r in res:
            x, y, w, h = cv2.boundingRect(c); (hval, _, _), _ = hsv_mean(im, c)
            cv2.rectangle(o, (x, y), (x + w, y + h), (255, 255, 255), 3)
            o = text(o, f"H≈{hval:.0f} → {ZH[r['color']]}", (x - 10, y + h + 6), 20, (255, 255, 255), (55, 42, 31), 3)
        L.add("实操一", o, "掩膜内先求平均 B-G-R，再转 HSV 看 H，按范围判颜色")
        L.add("平均颜色", o, "先分离、再在工件内部求平均颜色：比逐像素判断稳定")
        o2 = im.copy()
        for c, r in res:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(o2, (x, y), (x + w, y + h), COLORS[r["color"]], 4)
            o2 = text(o2, f"{ZH[r['color']]} → {BINS[r['color']]} 号料框", (x - 10, y + h + 6), 20, (255, 255, 255), (55, 42, 31), 3)
        L.add("实操二", o2, "颜色 → 料框编号，输出分拣指令")


def v65():
    with Lesson("65") as L:
        card_mm = 50; side = int(card_mm * PX_PER_MM)
        cal, _ = parts_scene([("square", "blue", (300, 260), side, 0, None)], w=620, h=520, noise=2)
        _, b, cs = separate(cal); c = max(cs, key=cv2.contourArea)
        (_, _), (w, h), _ = cv2.minAreaRect(c); ppm = (w + h) / 2 / card_mm
        o = cal.copy(); cv2.drawContours(o, [cv2.boxPoints(cv2.minAreaRect(c)).astype(np.int32)], -1, (0, 0, 230), 3)
        o = text(o, f"标定块边长 {card_mm} mm，量得 {(w + h) / 2:.0f} 像素", (20, 20), 24, (255, 255, 255), (55, 42, 31), 4)
        o = text(o, f"→ 每毫米 {ppm:.2f} 像素", (20, 70), 26, (55, 42, 31), (0, 220, 255), 4)
        L.add("标定", o, "放一个已知尺寸的标定块：像素数 ÷ 毫米数 = 比例")
        L.add("实操一", o, "标定一次，相机和高度不变就一直有效")
        tilt, _ = parts_scene([("rect", "green", (330, 260), (int(60 * PX_PER_MM), int(25 * PX_PER_MM)), 28, None)], w=660, h=520, noise=2)
        _, _, cs = separate(tilt); c = max(cs, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c); rr = cv2.minAreaRect(c)
        o = tilt.copy(); cv2.rectangle(o, (x, y), (x + w, y + h), (0, 200, 0), 3)
        cv2.drawContours(o, [cv2.boxPoints(rr).astype(np.int32)], -1, (0, 0, 230), 3)
        L_, S_ = max(rr[1]) / PX_PER_MM, min(rr[1]) / PX_PER_MM
        o = text(o, f"boundingRect：{w / PX_PER_MM:.1f} × {h / PX_PER_MM:.1f} mm（错）", (20, 20), 24, (0, 130, 0))
        o = text(o, f"minAreaRect：{L_:.1f} × {S_:.1f} mm（实际 60 × 25）", (20, 60), 24, (0, 0, 200))
        L.add("测量工件", o, "工件歪放时，只有最小外接矩形量得准")
        res = run(scene())
        L.add("实操二", annotate(scene(), [(c, dict(r, ok=abs(r["d"] - SPEC_D) <= TOL, reasons=[] if abs(r["d"] - SPEC_D) <= TOL else [f"尺寸 {r['d']:.1f}mm"])) for c, r in res]),
              f"直径标准 {SPEC_D:.0f}±{TOL:.0f} mm：偏小的红色圆片判 NG（实测值，含合成噪声）")


def v66():
    plt = plt_setup()
    with Lesson("66") as L:
        items = [("circle", "green", (150, 150), 90, 0, None), ("circle", "green", (420, 150), 90, 0, "notch"), ("circle", "green", (690, 150), 90, 0, "dent")]
        im, _ = parts_scene(items, w=840, h=320, noise=3)
        _, _, cs = separate(im); cs = sorted(cs, key=lambda c: cv2.boundingRect(c)[0])
        o = im.copy(); vals = []
        for c, name in zip(cs, ("合格", "豁口", "变形")):
            hull = cv2.convexHull(c); cv2.drawContours(o, [hull], -1, (0, 220, 255), 3); cv2.drawContours(o, [c], -1, (0, 0, 230), 2)
            a = cv2.contourArea(c); sol = a / cv2.contourArea(hull); circ = 4 * np.pi * a / cv2.arcLength(c, True) ** 2
            ms = cv2.matchShapes(cs[0], c, cv2.CONTOURS_MATCH_I1, 0)
            vals.append((name, sol, circ, ms)); x, y, w, h = cv2.boundingRect(c)
            o = text(o, name, (x + w // 2 - 24, y + h + 8), 24, (255, 255, 255), (55, 42, 31), 4)
        L.add("课程导入", o, "合格件、豁口件、变形件")
        o1 = o.copy()
        for (name, sol, circ, _), c in zip(vals, cs):
            x, y, w, h = cv2.boundingRect(c); o1 = text(o1, f"凸度 {sol:.3f}", (x + 10, y - 2), 22, (55, 42, 31), (0, 220, 255), 3)
        L.add("方法一", o1, "黄线 = 凸包（像橡皮筋套住轮廓）；凸度 = 面积 ÷ 凸包面积，有缺口就明显变小")
        shapes = [("circle", 70, None), ("hex", 70, None), ("square", 120, None), ("triangle", 120, None)]
        pan = []
        for s_, sz, _ in shapes:
            m = np.zeros((220, 220), np.uint8)
            from _vis import _draw_shape
            _draw_shape(m, s_, (110, 115), sz, 0)
            c = max(cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea)
            circ = 4 * np.pi * cv2.contourArea(c) / cv2.arcLength(c, True) ** 2
            pan.append((cv2.cvtColor(m, cv2.COLOR_GRAY2BGR), f"圆度 {circ:.2f}"))
        L.add("方法二", row(tagged(pan, 20)), "圆度 = 4π × 面积 ÷ 周长²：越接近圆越大（像素圆实测约 0.85–0.9，不是 1）")
        fig, ax = plt.subplots(figsize=(9, 3.6), dpi=110)
        names = [v[0] for v in vals]; xs = np.arange(3)
        ax.bar(xs - 0.18, [v[1] for v in vals], 0.36, label="凸度", color="#F2A900"); ax.bar(xs + 0.18, [v[2] for v in vals], 0.36, label="圆度", color="#0E7C72")
        ax.axhline(CONFIG["solidity_min"], color="#F2A900", ls="--", lw=1.2); ax.axhline(CONFIG["circularity_min"], color="#0E7C72", ls="--", lw=1.2)
        for i, v in enumerate(vals):
            ax.text(i - 0.18, v[1] + 0.01, f"{v[1]:.2f}", ha="center", fontsize=11); ax.text(i + 0.18, v[2] + 0.01, f"{v[2]:.2f}", ha="center", fontsize=11)
        ax.set_xticks(xs, [f"{v[0]}\n与标准件差异 {v[3]:.3f}" for v in vals], fontsize=12); ax.set_ylim(0.5, 1.08); ax.legend(fontsize=11, loc="lower left"); ax.spines[["top", "right"]].set_visible(False)
        ax.set_title(f"实测指标（虚线 = 阈值：凸度 {CONFIG['solidity_min']}，圆度 {CONFIG['circularity_min']}）", fontsize=12)
        fig.tight_layout()
        L.add("实操一", fig2img(fig), "凸度、圆度、与标准件的形状差异（matchShapes，越小越像）三个指标的实测值")
        L.add("方法三", o, f"matchShapes 与标准件比对：豁口件差异 {vals[1][3]:.3f}、变形件 {vals[2][3]:.3f}（合格件为 0）")
        L.add("实操二", annotate(scene(), run(scene())), "用样本定好阈值后，逐件输出判定和原因")


def v68():
    with Lesson("68") as L:
        im = scene(); res = run(im); o = annotate(im, res)
        X = 520; cv2.line(o, (X, 0), (X, o.shape[0]), AMB, 4)
        o = text(o, "触发线", (X + 8, 8), 24, (55, 42, 31), (0, 220, 255), 4)
        L.add("触发线", o, "工件中心越过黄线的那一帧才记录，每个工件只记一次")
        L.add("实操一", o, "画出触发线，记录已计数的工件编号，避免重复")
        ok = sum(r["ok"] for _, r in res); ng = len(res) - ok
        panel = np.full((o.shape[0], 330, 3), (40, 32, 26), np.uint8)
        for k, l in enumerate(["统计", f"总数  {len(res)}", f"OK    {ok}", f"NG    {ng}", f"良率  {ok / len(res):.0%}"]):
            panel = text(panel, l, (24, 30 + k * 70), 30 if k else 34, (0, 220, 255) if k == 0 else (235, 235, 235))
        L.add("实操二", row([o, panel], 0), "画面右侧显示统计面板；NG 工件自动截图保存")
        buf = io.StringIO(); w_ = csv.writer(buf); w_.writerow(["时间", "编号", "颜色", "直径mm", "结果", "原因"])
        for i, (_, r) in enumerate(res, 1):
            w_.writerow([f"2026-11-05 10:{12 + i:02d}:0{i}", i, ZH[r["color"]], f"{r['d']:.1f}", "OK" if r["ok"] else "NG", "/".join(r["reasons"])])
        rows = [l.split(",") for l in buf.getvalue().strip().splitlines()]
        cw = [260, 80, 80, 110, 80, 200]; tb = np.full((50 * len(rows) + 10, sum(cw) + 10, 3), 255, np.uint8)
        for i, rw in enumerate(rows):
            x = 5
            for j, cell in enumerate(rw):
                cv2.rectangle(tb, (x, 5 + i * 50), (x + cw[j], 55 + i * 50), (200, 200, 200), 1)
                if i == 0: cv2.rectangle(tb, (x + 1, 6), (x + cw[j] - 1, 54), (240, 236, 230), -1)
                tb = text(tb, cell, (x + 8, 14 + i * 50), 20, (0, 0, 200) if cell == "NG" else (40, 40, 40))
                x += cw[j]
        L.add("统计与记录", tb, "每个工件一行写进 CSV，用 Excel 打开就是检测记录表（示例时间）")


def v69():
    with Lesson("69") as L:
        im = scene(); res = run(im); o = annotate(im, res)
        ok = sum(r["ok"] for _, r in res)
        o = text(o, f"工业分拣质检系统 | 总数 {len(res)}  OK {ok}  NG {len(res) - ok} | 输入：图片", (10, 8), 22, (255, 255, 255), (40, 32, 26), 6)
        L.add("课程导入", o, "整合后的系统：分离 → 颜色 → 尺寸 → 缺陷 → 输出，一屏看全")
        L.add("实操二", o, "项目演示：一张图跑完全流程（换成摄像头 / 工业相机输入见模块九、十）")
