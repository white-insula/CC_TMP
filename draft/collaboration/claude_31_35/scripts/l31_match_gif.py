# -*- coding: utf-8 -*-
"""31-P4《原理：拿着小图在大图上滑动比对》候选动画：模板滑动 + 真实 matchTemplate 分数图。

- 合成教学样本：带纹理的灰度“电路板”，3 个相同芯片（每个叠加不同的随机噪声）+ 1 个外形相近的干扰元件。
- 模板从左上那个芯片裁出（灰度、单通道、uint8，与大图类型一致；断言方差非零）。
- 分数图 res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)，尺寸 (H-h+1, W-w+1)，一次算完；
  动画只**抽样展示**滑动过程（每隔若干像素取一帧），按行优先顺序逐步“揭开”已经扫过的那部分分数图。
- 当前位置的分数直接取 res[y, x]；最大值和位置来自 cv2.minMaxLoc(res)。

输出（previews/31/）：
  31-p4-anim-模板滑动与分数图_候选.gif
  31-p4-anim-关键帧拼图_审阅用.png
  31-p4-ref-阈值框数与变换实测_核对附件.png
"""
import cv2
import numpy as np
from _common import *

L = "31"
S = 2                      # 显示放大倍数（最近邻）


def make_board(seed=31):
    """合成教学样本：不规则纹理底板 + 3 个相同芯片（特征不呈周期排列）+ 1 个干扰电阻。"""
    rng = np.random.RandomState(seed)
    H, W = 180, 300
    tex = cv2.GaussianBlur(rng.normal(0, 1, (H, W)).astype(np.float32), (0, 0), 6)
    g = 75 + 18 * tex / (np.abs(tex).max() + 1e-6)              # 平滑起伏的底板纹理
    for (x1, y1, x2, y2) in ((0, 100, 140, 100), (140, 100, 140, 170), (200, 0, 200, 90), (230, 20, 300, 20)):
        cv2.line(g, (x1, y1), (x2, y2), 115, 2)                  # 少量不规则走线

    def chip(x, y):
        g[y:y + 30, x:x + 44] = 30                               # 黑色芯片本体 44×30
        cv2.circle(g, (x + 7, y + 7), 3, 170, -1)                # 一号脚圆点
        cv2.ellipse(g, (x, y + 15), (5, 6), 0, -90, 90, 120, -1)  # 左侧缺口
        g[y + 18:y + 22, x + 14:x + 38] = 140                    # 丝印条
        g[y + 8:y + 12, x + 26:x + 32] = 140
        for dx in (4, 13, 27, 38):                               # 下方 4 个引脚（间距不等）
            g[y + 30:y + 35, x + dx:x + dx + 3] = 200

    for (x, y) in ((20, 30), (150, 40), (80, 120)):
        chip(x, y)
    g[125:143, 215:265] = 160                                    # 干扰元件：浅色电阻
    g[131:137, 205:215] = 200; g[131:137, 265:275] = 200
    g += rng.normal(0, 6, g.shape)
    return np.clip(g, 0, 255).astype(np.uint8)


def heat(res):
    v = np.clip((res + 1) / 2 * 255, 0, 255).astype(np.uint8)    # -1…1 线性映射到 0…255，不做归一化拉伸
    return cv2.applyColorMap(v, cv2.COLORMAP_JET)


def main():
    gray = make_board()
    tx, ty, tw, th = 14, 25, 52, 44                              # 含引脚的芯片区域
    tpl = gray[ty:ty + th, tx:tx + tw].copy()
    assert tpl.dtype == gray.dtype == np.uint8 and tpl.ndim == gray.ndim == 2
    assert float(tpl.std()) > 0, "模板方差为 0 时 TM_CCOEFF_NORMED 无意义"
    res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
    H, W = gray.shape
    assert res.shape == (H - th + 1, W - tw + 1)
    mn, mx, mnl, mxl = cv2.minMaxLoc(res)
    print(f"    大图 {W}×{H}，模板 {tw}×{th}，分数图 {res.shape[1]}×{res.shape[0]}（= (W-w+1)×(H-h+1)）")
    print(f"    max_val = {mx:.4f} @ max_loc {mxl}；min_val = {mn:.4f}")
    others = []
    for (cx, cy) in ((150, 40), (80, 120)):
        sub = res[max(0, cy - 5 - 8):cy - 5 + 8, max(0, cx - 6 - 8):cx - 6 + 8]
        others.append(float(sub.max()))
    print(f"    另外两个芯片附近的最高分：{[round(o, 4) for o in others]}；干扰电阻附近最高分 {float(res[110:135, 190:240].max()):.4f}")

    hm = heat(res)
    frames, durs = [], []
    # 抽样位置：行优先，y 每 14 像素一行、x 每 18 像素一格；另加最大值位置
    samples = [(x, y) for y in range(0, res.shape[0], 14) for x in range(0, res.shape[1], 18)]
    samples = samples[::3] + [mxl]
    running = -1.0

    def frame(cur, reveal_idx, final=False):
        nonlocal running
        c = canvas(1440, 820)
        c = text(c, "模板匹配：拿着小图在大图上滑动比对", (40, 40), 32, INK, anchor="lm")
        c = text(c, "res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)    分数 -1～1，越接近 1 越像", (40, 86), 22, BLUE, anchor="lm")
        big = cv2.cvtColor(cv2.resize(gray, None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST), cv2.COLOR_GRAY2BGR)
        x, y = cur
        cv2.rectangle(big, (x * S, y * S), ((x + tw) * S, (y + th) * S), (0, 200, 255) if not final else (0, 0, 255), 3)
        cv2.circle(big, (x * S, y * S), 6, RED, -1)
        paste(c, border(big), 40, 130)
        c = text(c, f"大图 gray（{W}×{H}，合成教学样本）", (40 + W * S // 2, 130 + H * S + 26), 20, GRAY, anchor="mm")
        # 模板
        tbig = cv2.cvtColor(cv2.resize(tpl, None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST), cv2.COLOR_GRAY2BGR)
        paste(c, border(tbig, (0, 200, 255), 3), 40, 130 + H * S + 60)
        c = text(c, f"模板 tpl（{tw}×{th}）", (40 + tw * S + 20, 130 + H * S + 60 + 20), 20, INK, anchor="lm")
        # 分数图：只揭开已扫过的部分
        m = hm.copy()
        if not final:
            flat = np.arange(res.size).reshape(res.shape)
            lim = y * res.shape[1] + x
            m[flat > lim] = (235, 235, 235)
        mbig = cv2.resize(m, None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST)
        cv2.circle(mbig, (x * S, y * S), 7, (255, 255, 255), -1); cv2.circle(mbig, (x * S, y * S), 7, (0, 0, 0), 2)
        if final:
            cv2.drawMarker(mbig, (mxl[0] * S, mxl[1] * S), (255, 255, 255), cv2.MARKER_CROSS, 30, 3)
        RX = 40 + W * S + 60
        paste(c, border(mbig), RX, 130)
        c = text(c, f"分数图 res（{res.shape[1]}×{res.shape[0]} = (W-w+1)×(H-h+1)）", (RX + res.shape[1] * S // 2, 130 + res.shape[0] * S + 26), 20, GRAY, anchor="mm")
        c = text(c, "颜色：蓝 = -1 … 红 = 1", (RX, 130 + res.shape[0] * S + 56), 18, GRAY, anchor="lm")
        v = float(res[y, x]); running = max(running, v)
        ix = RX; iy = 130 + res.shape[0] * S + 100
        if not final:
            c = text(c, f"当前位置 (x, y) = ({x}, {y})", (ix, iy), 26, INK, anchor="lm")
            c = text(c, f"res[{y}, {x}] = {v:.3f}", (ix, iy + 44), 26, BLUE, anchor="lm")
            c = text(c, f"目前扫过的最高分 {running:.3f}", (ix, iy + 88), 22, GRAY, anchor="lm")
        else:
            c = text(c, f"minMaxLoc：max_val = {mx:.3f}", (ix, iy), 26, RED, anchor="lm")
            c = text(c, f"max_loc = {mxl}（最佳匹配的左上角）", (ix, iy + 44), 26, RED, anchor="lm")
            c = text(c, f"右下角 = (x + {tw}, y + {th})", (ix, iy + 88), 22, INK, anchor="lm")
            c = text(c, f"模板就是从这里裁的，所以是 1.000；另两个芯片 {others[0]:.3f}、{others[1]:.3f}", (ix, iy + 132), 20, GRAY, anchor="lm")
        c = text(c, "动画为抽样展示滑动过程；matchTemplate 实际计算了分数图里的每一个位置", (720, 790), 20, GRAY, anchor="mm")
        return stamp(c, "候选 · 合成教学样本；分数图由 cv2.matchTemplate(TM_CCOEFF_NORMED) 实算")

    for i, p in enumerate(samples[:-1]):
        frames.append(frame(p, i)); durs.append(450 if i else 1500)
    frames.append(frame(mxl, len(samples), final=True)); durs.append(4500)
    save_gif(frames, L, "31-p4-anim-模板滑动与分数图_候选.gif", durs, colors=256)
    k = [0, len(frames) // 3, 2 * len(frames) // 3, len(frames) - 1]
    keyframe_sheet(frames, k, L, "31-p4-anim-关键帧拼图_审阅用.png",
                   labels=["开始：左上角", "滑动中（抽样）", "滑动中（抽样）", "完成：minMaxLoc 找最大值"])
    print(f"    GIF {len(frames)} 帧（抽样），总时长 {sum(durs) / 1000:.1f} 秒")
    attachment(gray, tpl, res, (tw, th))


def attachment(gray, tpl, res, size):
    tw, th = size
    rows = []
    tiles = []
    for t in (0.5, 0.8, 0.95):
        ys, xs = np.where(res >= t)
        n_pos = len(xs)
        n_cc = cv2.connectedComponents((res >= t).astype(np.uint8))[0] - 1
        rows.append((t, n_pos, n_cc))
        print(f"    阈值 {t}：np.where 候选框 {n_pos} 个；相邻位置合并后的连通区域 {n_cc} 个")
        v = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        for x, y in zip(xs, ys):
            cv2.rectangle(v, (int(x), int(y)), (int(x) + tw, int(y) + th), (0, 200, 0), 1)
        v = cv2.resize(v, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_NEAREST)
        tiles.append(caption_below(border(v), f"res ≥ {t}：候选框 {n_pos} 个，连通区域 {n_cc} 个", 20))
    # 本样本的缩放 / 旋转实测
    h, w = gray.shape
    big = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LINEAR)
    rot = cv2.warpAffine(gray, cv2.getRotationMatrix2D((w / 2, h / 2), 25, 1.0), (w, h), borderValue=70)
    tr = []
    for name, im in (("原图", gray), ("大图放大 1.5 倍", big), ("大图旋转 25°", rot)):
        r = cv2.matchTemplate(im, tpl, cv2.TM_CCOEFF_NORMED)
        tr.append((name, float(r.max())))
        print(f"    本样本 {name}：max_val = {r.max():.4f}")
    body = col([row(tiles[:2], gap=20), tiles[2]], gap=16)
    info = canvas(body.shape[1], 210)
    info = text(info, "说明：候选框数 = np.where(res ≥ 阈值) 的位置数；同一目标附近会有多个相邻高分位置，所以候选框数 ≠ 目标数。", (10, 24), 20, INK, anchor="lm")
    info = text(info, "“连通区域”只是把相邻高分位置合并后的计数，用于参考；正式去重方法（如非极大值抑制）属于扩展内容。", (10, 58), 20, GRAY, anchor="lm")
    info = text(info, "本样本缩放 / 旋转实测（只代表这张合成图，不推广为“必然失败”）：", (10, 100), 20, INK, anchor="lm")
    for i, (name, v) in enumerate(tr):
        info = text(info, f"{name}：max_val = {v:.3f}", (30 + i * 360, 140), 22, BLUE, anchor="lm")
    head = canvas(body.shape[1], 50)
    head = text(head, "31 讲核对附件：阈值 0.5 / 0.8 / 0.95 实测（合成教学样本，不进课件）", (10, 25), 24, INK, anchor="lm")
    save(stamp(col([head, body, info], gap=6), "核对附件 · 合成教学样本"), L, "31-p4-ref-阈值框数与变换实测_核对附件.png")


if __name__ == "__main__":
    print("[31] 模板匹配 · P4")
    main()
