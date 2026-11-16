# -*- coding: utf-8 -*-
"""模块四 颜色与形状识别(26–35)配图。"""
import cv2, numpy as np, os, glob
from _vis import *

AMB = (0, 169, 242)
ZH = {"red": "红", "green": "绿", "blue": "蓝", "yellow": "黄"}
HSV_RANGES = {"red": [((0, 100, 80), (10, 255, 255)), ((170, 100, 80), (179, 255, 255))],
              "yellow": [((20, 100, 100), (35, 255, 255))], "green": [((40, 80, 60), (85, 255, 255))],
              "blue": [((100, 100, 60), (130, 255, 255))]}


def mask_of(hsv, color):
    m = None
    for lo, hi in HSV_RANGES[color]:
        x = cv2.inRange(hsv, np.array(lo), np.array(hi)); m = x if m is None else cv2.bitwise_or(m, x)
    return cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))


def shape_name(c):
    n = len(cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True))
    if n == 3: return "三角形"
    if n == 4:
        x, y, w, h = cv2.boundingRect(c); return "正方形" if 0.9 < w / h < 1.1 else "矩形"
    if n in (5, 6): return f"{n}边形"
    return "圆形"


def _shapes():
    return src("shapes")


def v26():
    plt = plt_setup()
    with Lesson("26") as L:
        items = [("circle", "red", (230, 300), 110, 0, None), ("circle", "red", (730, 300), 110, 0, None)]
        im, _ = parts_scene(items, light="side", noise=2)
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        out = im.copy()
        for k, (x, y) in enumerate(((230, 300), (730, 300))):
            b, g, r = im[y, x]; h, s, v = hsv[y, x]
            cv2.circle(out, (x, y), 6, (255, 255, 255), -1)
            out = text(out, f"{'暗处' if k == 0 else '亮处'}  BGR=({b},{g},{r})", (x - 200, y + 125), 24, (255, 255, 255), (55, 42, 31), 4)
            out = text(out, f"HSV=({h},{s},{v})", (x - 200, y + 170), 24, (55, 42, 31), (0, 220, 255), 4)
        L.add("课程导入", out, "同一种红色：亮暗不同，BGR 三个数都变了；HSV 里 H 几乎不变")
        L.add("为什么识别颜色要用 HSV", out, "光照只改变 V（亮度），H（色相）保持稳定 → 用 H 识别颜色更可靠")
        bar = np.zeros((70, 900, 3), np.uint8)
        for x in range(900):
            bar[:, x] = (int(x / 900 * 180), 255, 255)
        bar = cv2.cvtColor(bar, cv2.COLOR_HSV2BGR)
        canvas = np.full((190, 960, 3), 255, np.uint8); canvas[20:90, 30:930] = bar
        for hval, name in ((0, "红"), (30, "黄"), (60, "绿"), (120, "蓝"), (179, "红")):
            x = 30 + int(hval / 180 * 900)
            cv2.line(canvas, (x, 90), (x, 112), (0, 0, 0), 2)
            canvas = text(canvas, f"{hval}", (x - 14, 114), 22, (40, 40, 40)); canvas = text(canvas, name, (x - 10, 146), 24, (0, 0, 200) if name == "红" else (40, 40, 40))
        L.add("OpenCV 中的 HSV 范围", canvas, "OpenCV 的 H 取 0–179（角度除以 2）；红色在两端，要分两段")
        sh = _shapes(); hs = cv2.cvtColor(sh, cv2.COLOR_BGR2HSV); H, S, V = cv2.split(hs)
        L.add("实操一", row(tagged([(sh, "原图"), (H, "H 色相"), (S, "S 饱和度"), (V, "V 亮度")], 20)), "白色背景 S 接近 0；四种颜色在 H 通道里深浅各不相同")
        L.add("H、S、V 是什么", row(tagged([(sh, "原图"), (H, "H：哪种颜色"), (S, "S：颜色多纯"), (V, "V：多亮")], 20)), "H 定颜色，S 定浓淡，V 定明暗")
        m = mask_of(hs, "yellow")
        L.add("实操二", row(tagged([(sh, "原图"), (m, "H 20–35、S≥100、V≥100：只剩黄色")], 20)), "滑动条把范围调到只剩目标颜色，记下这 6 个数")


def v27():
    with Lesson("27") as L:
        sh = _shapes(); hs = cv2.cvtColor(sh, cv2.COLOR_BGR2HSV)
        g = mask_of(hs, "green")
        L.add("掩膜", row(tagged([(sh, "原图"), (g, "mask：白=要，黑=不要"), (cv2.bitwise_and(sh, sh, mask=g), "bitwise_and 抠出")], 20)), "掩膜就像镂空的喷漆模板：只有白色的“洞”透出来")
        L.add("实操一", row(tagged([(g, "inRange 绿色范围"), (cv2.bitwise_and(sh, sh, mask=g), "只保留绿色")], 20)), "绿色：H 40–85")
        sh2 = sh.copy(); red = mask_of(hs, "red").astype(bool); red[:, sh.shape[1] // 2:] = False
        sh2[red] = (30, 45, 225)        # 左半边的红色偏橙一点(H≈2),右半边偏紫一点(H≈179)
        hs2 = cv2.cvtColor(sh2, cv2.COLOR_BGR2HSV)
        lo = cv2.inRange(hs2, np.array((0, 100, 80)), np.array((10, 255, 255))); hi = cv2.inRange(hs2, np.array((170, 100, 80)), np.array((179, 255, 255)))
        L.add("红色要分两段", row(tagged([(sh2, "两种红：偏橙 / 偏紫"), (lo, "H 0–10"), (hi, "H 170–179"), (cv2.bitwise_or(lo, hi), "bitwise_or 合并")], 18)), "红色跨在色带两端，只用一段会漏掉一部分，两段合起来才完整")
        im, _ = parts_scene(noise=7)
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        raw = cv2.bitwise_or(cv2.inRange(hsv, np.array((0, 100, 80)), np.array((10, 255, 255))), cv2.inRange(hsv, np.array((170, 100, 80)), np.array((179, 255, 255))))
        L.add("实操二", row(tagged([(im, "工件照片"), (raw, "红色掩膜（有噪点）"), (mask_of(hsv, "red"), "开运算去噪后")], 20)), "掩膜里零星的白点，用第 22 讲的开运算去掉")


def v28():
    with Lesson("28") as L:
        sh = _shapes(); g = cv2.cvtColor(sh, cv2.COLOR_BGR2GRAY)
        _, b = cv2.threshold(g, 240, 255, cv2.THRESH_BINARY_INV)
        cnts, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        d = sh.copy(); cv2.drawContours(d, cnts, -1, (0, 0, 0), 4)
        L.add("轮廓", row(tagged([(b, "二值图"), (d, f"找到 {len(cnts)} 个轮廓")], 22)), "轮廓 = 白色区域的边界线（先二值化，白色为目标）")
        L.add("实操一", row(tagged([(sh, "原图"), (d, "drawContours 画出全部轮廓")], 22)), f"findContours 返回列表，len(contours) = {len(cnts)}")
        w = np.full((360, 620), 0, np.uint8)
        for cx in (150, 460):
            cv2.circle(w, (cx, 180), 120, 255, -1); cv2.circle(w, (cx, 180), 50, 0, -1)
        ce, _ = cv2.findContours(w, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        ct, _ = cv2.findContours(w, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        a = bgr(w).copy(); cv2.drawContours(a, ce, -1, (0, 0, 255), 5)
        t = bgr(w).copy(); cv2.drawContours(t, ct, -1, (0, 0, 255), 5)
        L.add("实操二", row(tagged([(a, f"RETR_EXTERNAL：{len(ce)} 个"), (t, f"RETR_TREE：{len(ct)} 个（含内孔）")], 22)), "两个垫片：只要外轮廓用 EXTERNAL；内孔也要用 TREE")


def v29():
    with Lesson("29") as L:
        sh = _shapes(); g = cv2.cvtColor(sh, cv2.COLOR_BGR2GRAY)
        _, b = cv2.threshold(g, 240, 255, cv2.THRESH_BINARY_INV)
        cnts, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        c = max(cnts, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c); M = cv2.moments(c); cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
        pad = 60
        crop = sh[max(y - pad, 0):y + h + pad, max(x - pad, 0):x + w + pad].copy(); ox, oy = max(x - pad, 0), max(y - pad, 0)
        crop = cv2.resize(crop, None, fx=2, fy=2); s = 2
        cv2.drawContours(crop, [(c - [ox, oy]) * s], -1, (0, 0, 0), 3)
        cv2.rectangle(crop, ((x - ox) * s, (y - oy) * s), ((x - ox + w) * s, (y - oy + h) * s), (0, 200, 0), 3)
        cv2.circle(crop, ((cx - ox) * s, (cy - oy) * s), 8, (0, 0, 255), -1)
        info = np.full((crop.shape[0], 700, 3), 255, np.uint8)
        for k, l in enumerate([f"面积 contourArea = {cv2.contourArea(c):.0f}", f"周长 arcLength = {cv2.arcLength(c, True):.0f}",
                               f"外接框 boundingRect = ({x}, {y}, {w}, {h})", f"中心点 = ({cx}, {cy})"]):
            info = text(info, l, (20, 40 + k * 70), 26, (40, 40, 40))
        L.add("四个常用特征", row([border(crop), info]), "同一个轮廓上的面积、周长、外接框（绿）和中心点（红）")
        out = sh.copy()
        for c in cnts:
            x, y, w, h = cv2.boundingRect(c); cv2.rectangle(out, (x, y), (x + w, y + h), (0, 0, 0), 2)
            out = text(out, f"{cv2.contourArea(c):.0f}", (x + 2, y + 2), 18, (255, 255, 255), (0, 0, 0), 2)
        L.add("实操一", out, "每个轮廓画外接框并标出面积")
        im, _ = parts_scene(noise=7); hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV); m = mask_of(hsv, "red")
        out = im.copy()
        for c in cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
            if cv2.contourArea(c) < 500: continue
            x, y, w, h = cv2.boundingRect(c); cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 3)
            out = text(out, "红色", (x, y - 34), 24, (255, 255, 255), (0, 150, 0), 3)
        L.add("实操二", row(tagged([(m, "红色掩膜"), (out, "面积过滤后画框")], 22)), "颜色识别 + 轮廓：把红色工件框出来")
        items = [("rect", "blue", (480, 300), (300, 120), 30, None)]
        im, _ = parts_scene(items, noise=2); hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV); m = mask_of(hsv, "blue")
        c = max(cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c); out = im.copy()
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 200, 0), 3)
        cv2.drawContours(out, [cv2.boxPoints(cv2.minAreaRect(c)).astype(np.int32)], -1, (0, 0, 255), 3)
        out = text(out, "绿：boundingRect（正框）", (20, 20), 26, (0, 140, 0)); out = text(out, "红：minAreaRect（最小外接，可旋转）", (20, 60), 26, (0, 0, 200))
        L.add("更多特征", out, "工件歪放时，minAreaRect 更贴合，测尺寸更准（模块八会用到）")


def v30():
    with Lesson("30") as L:
        sh = _shapes(); g = cv2.cvtColor(sh, cv2.COLOR_BGR2GRAY)
        _, b = cv2.threshold(g, 240, 255, cv2.THRESH_BINARY_INV)
        cnts, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        def labeled(eps):
            out = sh.copy()
            for c in cnts:
                a = cv2.approxPolyDP(c, eps * cv2.arcLength(c, True), True)
                cv2.drawContours(out, [a], -1, (0, 0, 0), 3)
                for p in a.reshape(-1, 2): cv2.circle(out, tuple(p), 5, (0, 0, 255), -1)
                x, y, w, h = cv2.boundingRect(c)
                n = len(a); name = {3: "三角", 4: "四边"}.get(n, "圆" if n > 6 else f"{n}边")
                out = text(out, name, (x + 2, y + h // 2 - 12), 20, (255, 255, 255), (0, 0, 0), 2)
            return out
        L.add("多边形近似", labeled(0.02), "approxPolyDP 把轮廓拉直成多边形，红点是角点")
        L.add("实操一", labeled(0.02), "角点 3 → 三角形，4 → 四边形，很多 → 圆")
        L.add("实操二", row(tagged([(labeled(0.005), "0.005：太细，角点变多"), (labeled(0.02), "0.02：合适"), (labeled(0.08), "0.08：太粗，圆被判成四边形")], 20)),
              "误差系数（乘以周长）要调到合适：一般 0.02 左右")


def _icon(sh, k):
    """按轮廓从形状图里切出第 k 大的形状(带白边)。"""
    g = cv2.cvtColor(sh, cv2.COLOR_BGR2GRAY)
    _, b = cv2.threshold(g, 240, 255, cv2.THRESH_BINARY_INV)
    cs = sorted(cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0], key=lambda c: cv2.boundingRect(c)[1] * 10 + cv2.boundingRect(c)[0])
    x, y, w, h = cv2.boundingRect(cs[k]); m = 8
    return sh[y - m:y + h + m, x - m:x + w + m].copy(), (x - m, y - m)


def v31():
    with Lesson("31") as L:
        sh = _shapes()
        tpl, (tx, ty) = _icon(sh, 2)            # 第一行的小黄方块
        res = cv2.matchTemplate(sh, tpl, cv2.TM_CCOEFF_NORMED)
        _, mx, _, loc = cv2.minMaxLoc(res)
        out = sh.copy(); th, tw = tpl.shape[:2]
        cv2.rectangle(out, loc, (loc[0] + tw, loc[1] + th), (0, 200, 0), 4)
        heat = cv2.applyColorMap(cv2.normalize(res, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8), cv2.COLORMAP_JET)
        L.add("原理", row(tagged([(cv2.resize(tpl, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST), "模板"), (heat, "相似度图：越红越像"), (out, f"最高 {mx:.2f}")], 20)),
              "模板在大图上逐位置滑动比对，得到一张相似度图，最亮处就是目标")
        L.add("实操一", row(tagged([(cv2.resize(tpl, None, fx=2, fy=2), "模板"), (out, f"max_val = {mx:.2f}")], 20)), "minMaxLoc 找到相似度最大的位置，画框")
        icon, _ = _icon(sh, 0)                  # 黄三角
        ih, iw = icon.shape[:2]
        board = np.full((520, 900, 3), 255, np.uint8)
        pos = [(40, 40), (330, 70), (640, 30), (120, 300), (450, 320), (700, 290)]
        for x, y in pos: board[y:y + ih, x:x + iw] = icon
        cv2.circle(board, (300, 260), 45, (40, 40, 210), -1); cv2.rectangle(board, (560, 200), (640, 280), (190, 110, 30), -1)
        r2 = cv2.matchTemplate(board, icon, cv2.TM_CCOEFF_NORMED)
        ys, xs = np.where(r2 >= 0.8)
        out2 = board.copy(); kept = []
        for x, y in sorted(zip(xs, ys), key=lambda p: -r2[p[1], p[0]]):
            if all(abs(x - a) > iw // 2 or abs(y - b_) > ih // 2 for a, b_ in kept):
                kept.append((x, y)); cv2.rectangle(out2, (x, y), (x + iw, y + ih), (0, 200, 0), 3)
        out2 = text(out2, f"阈值 0.8：找到 {len(kept)} 个三角形", (20, 460), 28, (0, 120, 0))
        L.add("实操二", border(out2), "np.where(res >= 0.8) 取出所有足够像的位置，再去掉重叠框")
        bus = fit(src("bus")[0:620, :], w=600)
        bt = bus[285:355, 420:530].copy()                       # 车身标志
        h_, w_ = bus.shape[:2]
        same_ = bus.copy()
        big = cv2.resize(bus, None, fx=1.5, fy=1.5)[150:150 + h_, 200:200 + w_]
        rot = cv2.warpAffine(bus, cv2.getRotationMatrix2D((w_ / 2, h_ / 2), 25, 1.0), (w_, h_))
        panels = []
        for im_, name in ((same_, "原图"), (big, "放大 1.5 倍"), (rot, "旋转 25°")):
            r_ = cv2.matchTemplate(im_, bt, cv2.TM_CCOEFF_NORMED); _, v, _, lc = cv2.minMaxLoc(r_)
            o = im_.copy()
            if v >= 0.8:
                cv2.rectangle(o, lc, (lc[0] + bt.shape[1], lc[1] + bt.shape[0]), (0, 200, 0), 4)
            panels.append((o, f"{name}：相似度 {v:.2f}" + ("" if v >= 0.8 else " 找不到")))
        b2 = row([border(cv2.resize(bt, None, fx=2, fy=2))] + tagged(panels, 22), 16)
        L.add("局限", border(b2), "模板匹配只认“一模一样”：大小、角度一变就找不到")


def v32():
    import qrcode
    with Lesson("32") as L:
        content = "PART-2026-0001 | 批次A | 质检合格"
        q = cv2.cvtColor(np.array(qrcode.make(content).convert("RGB")), cv2.COLOR_RGB2BGR)
        L.add("实操一", row([border(fit(q, h=420)), border(text(np.full((420, 560, 3), 255, np.uint8), "qrcode.make(\n  \"PART-2026-0001 |\n   批次A | 质检合格\"\n).save(\"part.png\")", (20, 100), 30, (40, 40, 40)))]),
              "两行代码生成零件追溯码（qrcode 库实际生成）")
        s = q.copy(); n = s.shape[0]; box = 10 * 7
        for (x, y) in ((40, 40), (n - 40 - box, 40), (40, n - 40 - box)):
            cv2.rectangle(s, (x - 6, y - 6), (x + box + 6, y + box + 6), (0, 0, 230), 5)
        s = text(fit(s, h=480), "三个“回”字：定位", (150, 220), 26, (255, 255, 255), (0, 0, 180), 4)
        L.add("二维码的结构", border(s), "三个角上的定位图案让扫码器快速找到并摆正二维码")
        scene, _ = parts_scene([("square", "blue", (230, 300), 200, 0, None)], noise=3)
        qs = cv2.resize(q, (230, 230))
        M = cv2.getPerspectiveTransform(np.float32([[0, 0], [230, 0], [230, 230], [0, 230]]), np.float32([[560, 170], [800, 200], [790, 440], [550, 420]]))
        warped = cv2.warpPerspective(qs, M, (scene.shape[1], scene.shape[0]))
        mask = cv2.warpPerspective(np.full((230, 230), 255, np.uint8), M, (scene.shape[1], scene.shape[0]))
        scene[mask > 0] = warped[mask > 0]
        data, pts, _ = cv2.QRCodeDetector().detectAndDecode(scene)
        out = scene.copy()
        if pts is not None:
            cv2.polylines(out, [pts.astype(np.int32).reshape(-1, 2)], True, (0, 200, 0), 4)
        out = text(out, f"识别结果：{data or '（未识别）'}", (20, 20), 26, (255, 255, 255), (0, 120, 0), 5)
        L.add("实操二", out, "QRCodeDetector.detectAndDecode：歪着贴也能找到四个角并解码")


def v33():
    with Lesson("33") as L:
        im, _ = parts_scene(noise=5)
        L.add("案例导入", im, "俯拍的彩色工件：要给每个工件标出颜色和形状")
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV); out = im.copy(); cnt = {}
        for color in ("red", "green", "blue", "yellow"):
            for c in cv2.findContours(mask_of(hsv, color), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
                if cv2.contourArea(c) < 800: continue
                name = shape_name(c); x, y, w, h = cv2.boundingRect(c)
                cv2.drawContours(out, [c], -1, (255, 255, 255), 3)
                out = text(out, f"{ZH[color]}·{name}", (x, y - 38), 24, (255, 255, 255), (55, 42, 31), 4)
                cnt[ZH[color]] = cnt.get(ZH[color], 0) + 1
        out = text(out, "  ".join(f"{k}:{v}" for k, v in cnt.items()), (20, im.shape[0] - 50), 26, (255, 255, 255), (55, 42, 31), 6)
        L.add("实操二", out, "HSV 分颜色 → 轮廓 → 角点判形状 → 标注并计数（OpenCV 实际运行结果）")
        m = mask_of(hsv, "red")
        L.add("实操一", row(tagged([(im, "原图"), (m, "以红色为例：掩膜 → 轮廓")], 22)), "主循环：对字典里的每种颜色做一遍 inRange + findContours")


def _card(i=1):
    files = sorted(glob.glob(os.path.join(SRC["card_dir"], "*.jpg")))
    return imread(files[i - 1]), files


def _markers(im):
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    _, b = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cnts, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sq = []
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c); a = cv2.contourArea(c)
        if 150 < a < 3000 and 0.6 < w / h < 2.5 and a / (w * h) > 0.85:
            sq.append((x + w / 2, y + h / 2, c))
    H, W = g.shape
    corners = []
    for tx, ty in ((0, 0), (W, 0), (W, H), (0, H)):
        corners.append(min(sq, key=lambda s: (s[0] - tx) ** 2 + (s[1] - ty) ** 2))
    return b, cnts, sq, corners


def v34():
    with Lesson("34") as L:
        im, _ = _card(1)
        b, cnts, sq, corners = _markers(im)
        H, W = im.shape[:2]
        hide = lambda x: cv2.rectangle(x.copy(), (int(W * 0.05), int(H * 0.04)), (int(W * 0.5), int(H * 0.2)), (200, 200, 200), -1)  # 遮住姓名栏
        allc = hide(im); cl = cv2.findContours(b, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]; cv2.drawContours(allc, cl, -1, (0, 0, 255), 1)
        four = hide(im)
        for x, y, c in corners:
            cv2.drawContours(four, [c], -1, (0, 200, 0), -1); cv2.circle(four, (int(x), int(y)), 22, (0, 200, 0), 3)
        L.add("第①步", row(tagged([(allc, f"全部轮廓：{len(cl)} 个"), (four, "按面积/形状筛出 4 个定位块")], 22)), "用轮廓特征（面积、长宽比、实心度）筛出四角的黑方块（姓名栏已遮挡）")
        pts = np.float32([(x, y) for x, y, _ in corners])
        Wd, Hd = 720, 1000
        warp = cv2.warpPerspective(im, cv2.getPerspectiveTransform(pts, np.float32([[0, 0], [Wd, 0], [Wd, Hd], [0, Hd]])), (Wd, Hd))
        warp_h = cv2.rectangle(warp.copy(), (0, 0), (Wd // 2, int(Hd * 0.18)), (200, 200, 200), -1)
        L.add("实操一", row(tagged([(four, "定位块"), (warp_h, "按四个中心点拉正")], 22)), "透视变换后，每个格子的位置都固定了（[GA] 往届学生毕设扫描卡）")
        g = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
        _, inv = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        blobs = [cv2.boundingRect(c) for c in cv2.findContours(cv2.morphologyEx(inv, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]]
        blobs = [r for r in blobs if r[2] * r[3] > 120 and 0.8 < r[2] / r[3] < 4 and r[1] > Hd * 0.45]
        x, y, w, h = max(blobs, key=lambda r: r[2] * r[3])
        pitch = int(w * 1.55)
        x2 = x - pitch if x - pitch > 0 else x + pitch
        a = inv[y - 3:y + h + 3, x - 3:x + w + 3]; bb = inv[y - 3:y + h + 3, x2 - 3:x2 + w + 3]
        z = lambda r: cv2.resize(r, None, fx=8, fy=8, interpolation=cv2.INTER_NEAREST)
        L.add("第④步", row(tagged([(z(bb), f"未涂：白像素 {cv2.countNonZero(bb)}"), (z(a), f"已涂：白像素 {cv2.countNonZero(a)}")], 22)),
              "反向二值化后数白色像素：涂过的格子白像素多得多")
        out = warp.copy()
        for x, y, w, h in blobs:
            cv2.rectangle(out, (x - 3, y - 3), (x + w + 3, y + h + 3), (0, 0, 255), 2)
        out = cv2.rectangle(out, (0, 0), (Wd // 2, int(Hd * 0.18)), (200, 200, 200), -1)
        L.add("实操二", fit(out, h=760), f"判出所有填涂（红框，共 {len(blobs)} 处），再与标准答案比对")


def v35():
    with Lesson("35") as L:
        _, files = _card(1)
        th = []
        for f in files[:40]:
            im = imread(f); H = im.shape[0]
            th.append(border(cv2.resize(im[int(H * 0.2):, :], (150, 170)), (180, 180, 180), 1))
        L.add("案例导入", grid(th, 8, 8), "往届学生毕设：40 张真实扫描答题卡，一次性批量阅卷（缩略图已去除姓名栏）")
