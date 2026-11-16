# -*- coding: utf-8 -*-
"""第20讲《图像滤波与去噪》候选素材。

输出（previews/20/）：
  20-p5-anim-5x5邻域平均逐格滑动_候选.gif      P5 “动画/逐步展示待做”缺项：核逐格滑动、求和 ÷25、写入结果
  20-p5-anim-关键帧拼图_审阅用.png             同一动画的 3 个关键帧，便于不播放 GIF 时审阅
  20-p2-photo-高增益噪点模拟_合成.png          P2 候选替代（真实夜拍噪点照片仍建议教师自拍）
  20-p6-shot-椒盐噪声四种对比含放大_替身图.png  P6 录屏静态参考，参数与脚本一致（0.02 / 0.98，核 5）
  20-p7-shot-高斯与双边边缘放大对比_替身图.png  P7 录屏静态参考（人像替身：NASA 公有领域宇航员照片）
  20-p7-shot-卡通特效静态预览_替身图.png        P7 彩蛋：按 recording_kit/20/cartoon.py 的处理链对单张图运行
  20-hw-ref-高斯核3_7_15对比_参考.png           课后任务2参考（仅参考）
"""
import cv2
import numpy as np
from _common import *

L = "20"


# ---------------- P5 动画 ----------------
def _grid_values():
    """7 行 × 9 列的合成灰度值：左暗右亮的平缓渐变 + 1 个椒盐噪点(255)，便于看出“平均会把噪点摊开”。"""
    rng = np.random.default_rng(20)
    base = np.linspace(90, 170, 9)[None, :].repeat(7, 0) + rng.integers(-6, 7, (7, 9))
    g = np.clip(base, 0, 255).astype(np.int32)
    before = int(g[3, 4])
    g[3, 4] = 255                                   # 一颗白色噪点
    return g, before


def _draw_grid(c, vals, x0, y0, cs, hi=None, hi_color=AMB, center=None, empty=None, num_size=20):
    rows, cols = vals.shape
    for r in range(rows):
        for q in range(cols):
            x, y = x0 + q * cs, y0 + r * cs
            if empty is not None and empty[r, q]:
                cv2.rectangle(c, (x, y), (x + cs, y + cs), (248, 248, 248), -1)
                cv2.rectangle(c, (x, y), (x + cs, y + cs), (210, 210, 210), 1)
                continue
            v = int(vals[r, q])
            cv2.rectangle(c, (x, y), (x + cs, y + cs), (v, v, v), -1)
            cv2.rectangle(c, (x, y), (x + cs, y + cs), (160, 160, 160), 1)
    if hi is not None:
        r0, q0, n = hi
        cv2.rectangle(c, (x0 + q0 * cs, y0 + r0 * cs), (x0 + (q0 + n) * cs, y0 + (r0 + n) * cs), hi_color, 4)
    if center is not None:
        r, q = center
        cv2.rectangle(c, (x0 + q * cs + 3, y0 + r * cs + 3), (x0 + (q + 1) * cs - 3, y0 + (r + 1) * cs - 3), RED, 3)
    out = c
    for r in range(rows):
        for q in range(cols):
            if empty is not None and empty[r, q]:
                continue
            v = int(vals[r, q])
            out = text(out, str(v), (x0 + q * cs + cs // 2, y0 + r * cs + cs // 2), num_size,
                       (255, 255, 255) if v < 128 else INK, anchor="mm")
    return out


def p5_animation():
    g, before = _grid_values()
    R, C = g.shape
    delta = (255 - before) / 25                    # 噪点给每个包含它的结果带来的增量
    k = 5
    oh, ow = R - k + 1, C - k + 1                   # 有效输出 3 × 5
    res = np.zeros((oh, ow), np.int32)
    filled = np.ones((oh, ow), bool)               # True = 尚未计算
    # 核对：与 cv2.blur 在有效区域的结果一致（四舍五入）
    ref = cv2.blur(g.astype(np.float32), (k, k))[k // 2:R - k // 2, k // 2:C - k // 2]

    W, H, cs = 1440, 740, 62
    gx, gy = 40, 150
    frames, durs = [], []
    order = [(r, q) for r in range(oh) for q in range(ow)]
    for idx, (r, q) in enumerate(order + [(None, None)]):
        c = canvas(W, H)
        c = text(c, "滤波的思想：和邻居商量（5×5 均值）", (40, 46), 34, INK, anchor="lm")
        c = text(c, "原图像素（合成数值，含 1 颗白色噪点 255）", (gx, gy - 28), 20, GRAY, anchor="lm")
        if r is not None:
            win = g[r:r + k, q:q + k]
            s = int(win.sum()); m = s / (k * k)
            res[r, q] = int(round(m)); filled[r, q] = False
            assert abs(m - ref[r, q]) < 1e-3
            c = _draw_grid(c, g, gx, gy, cs, hi=(r, q, k), center=(r + 2, q + 2))
        else:
            c = _draw_grid(c, g, gx, gy, cs)
        # 右侧：结果网格
        rx, ry = gx + C * cs + 90, gy + 2 * cs        # 与核中心所在行对齐
        c = text(c, "结果（只算核能完整放下的位置）", (rx, gy - 28), 20, GRAY, anchor="lm")
        c = _draw_grid(c, res, rx, ry, cs, empty=filled, center=(r, q) if r is not None else None)
        cv2.arrowedLine(c, (gx + C * cs + 20, gy + 3 * cs), (rx - 20, gy + 3 * cs), INK, 3, tipLength=0.15)
        # 算式
        fy = gy + R * cs + 50
        if r is not None:
            c = text(c, f"第 {idx + 1}/{len(order)} 步：橙框里 25 个数相加 = {s}，÷ 25 = {m:.1f} ≈ {res[r, q]}，写到红框中心位置",
                     (gx, fy), 24, INK, anchor="lm")
        else:
            c = text(c, f"完成：噪点 255（原本约 {before}）被摊进 15 个结果，每格都多了约 {delta:.1f}",
                     (gx, fy), 24, INK, anchor="lm")
            c = text(c, "噪点没有消失，只是变淡、变大 —— 这就是均值滤波把噪点抹成一片灰斑的原因", (gx, fy + 36), 22, RED, anchor="lm")
        c = text(c, "边缘一圈的处理方式（填充/复制边界）本示意从略；cv2.blur 默认会补边，输出与原图同样大小。",
                 (gx, fy + 80), 18, GRAY, anchor="lm")
        frames.append(stamp(c, "候选 · 动画示意 · 合成数值，已与 cv2.blur 核对"))
        durs.append(1100 if r is not None else 3500)
    durs[0] = 2000
    save_gif(frames, L, "20-p5-anim-5x5邻域平均逐格滑动_候选.gif", durs)
    key = [frames[0], frames[len(order) // 2], frames[-1]]
    sheet = col([fit(f, w=960) for f in key], gap=12)
    save(sheet, L, "20-p5-anim-关键帧拼图_审阅用.png")
    print("    结果网格:", res.tolist())


# ---------------- P2 高增益噪点模拟 ----------------
def p2_gain_noise():
    img = stand_in("coffee").astype(np.float32)
    rng = np.random.default_rng(2)
    low = img * 0.12                                         # 光线很暗：信号只有原来的 12%
    shot = rng.poisson(np.clip(low, 0, None) * 2.0) / 2.0   # 光子散粒噪声（近似）
    read = rng.normal(0, 2.0, img.shape)                     # 读出噪声
    gain = 7.0                                               # 相机提高增益：信号与噪声一起放大
    noisy = np.clip((shot + read) * gain, 0, 255).astype(np.uint8)
    clean = np.clip(low * gain, 0, 255).astype(np.uint8)
    y, x, s = 120, 330, 110
    z = lambda a: cv2.resize(a[y:y + s, x:x + s], (330, 330), interpolation=cv2.INTER_NEAREST)
    left = caption_below(border(fit(noisy, w=500)), "暗光 + 高增益（合成模拟）", 22)
    a = caption_below(border(z(clean)), "理想：无噪声（局部放大）", 20)
    b = caption_below(border(z(noisy)), "实际：颗粒、彩色噪点（局部放大）", 20, RED)
    out = row([left, a, b], gap=16)
    save(stamp(out, "候选 · 合成模拟，不是夜间实拍；替身图 coffee(CC0)"), L, "20-p2-photo-高增益噪点模拟_合成.png")


# ---------------- P6 四种对比 ----------------
def p6_denoise():
    img = stand_in("coffee")
    np.random.seed(0)                                         # 仅为预览可复现；录屏代码无需固定种子
    noisy = img.copy()
    rnd = np.random.rand(*img.shape[:2])
    noisy[rnd < 0.02] = 0; noisy[rnd > 0.98] = 255
    m = cv2.blur(noisy, (5, 5))
    g = cv2.GaussianBlur(noisy, (5, 5), 0)
    md = cv2.medianBlur(noisy, 5)
    y, x, s = 140, 140, 120
    tiles = []
    for im, cap, colr in [(noisy, "noisy 椒盐噪声", INK), (m, "blur 均值 5×5", INK),
                          (g, "GaussianBlur 5×5", INK), (md, "medianBlur 5", GREEN)]:
        full = fit(im, w=360)
        crop = cv2.resize(im[y:y + s, x:x + s], (180, 180), interpolation=cv2.INTER_NEAREST)
        show = full.copy()
        k = 360 / im.shape[1]
        cv2.rectangle(show, (int(x * k), int(y * k)), (int((x + s) * k), int((y + s) * k)), AMB, 2)
        tiles.append(caption_below(row([border(show), border(crop, AMB)], gap=8), cap, 22, colr))
    out = col([row(tiles[:2], gap=20), row(tiles[2:], gap=20)], gap=10)
    save(stamp(out, "候选 · 替身图 coffee(CC0)，非 cat.jpg；右侧小图为橙框处最近邻放大"), L, "20-p6-shot-椒盐噪声四种对比含放大_替身图.png")


# ---------------- P7 高斯 vs 双边 ----------------
def p7_bilateral():
    img = stand_in("astronaut")                               # 512×512 人像（NASA 公有领域）
    g = cv2.GaussianBlur(img, (9, 9), 0)
    bi = cv2.bilateralFilter(img, 9, 75, 75)
    y, x, s = 90, 170, 150                                    # 面部与发际线区域
    tiles = []
    for im, cap, colr in [(img, "原图", INK), (g, "GaussianBlur (9, 9)：整体糊", RED), (bi, "bilateralFilter 9, 75, 75：平滑保边", GREEN)]:
        show = fit(im, w=340); k = 340 / im.shape[1]
        cv2.rectangle(show, (int(x * k), int(y * k)), (int((x + s) * k), int((y + s) * k)), AMB, 2)
        crop = cv2.resize(im[y:y + s, x:x + s], (340, 340), interpolation=cv2.INTER_CUBIC)
        tiles.append(caption_below(col([border(show), border(crop, AMB)], gap=8), cap, 20, colr))
    out = row(tiles, gap=18)
    save(stamp(out, "候选 · 人像替身：NASA 宇航员照片(公有领域)；正式录屏建议用教师本人照片"), L, "20-p7-shot-高斯与双边边缘放大对比_替身图.png")


def p7_cartoon():
    """与 recording_kit/20/cartoon.py 相同处理链，只把摄像头帧换成单张图片。"""
    img = stand_in("astronaut")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.medianBlur(imgGray, 5)
    imgCanny = cv2.Canny(imgBlur, 50, 50)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    img_edge = cv2.cvtColor(255 - imgCanny, cv2.COLOR_GRAY2RGB)
    cartoon = cv2.bitwise_and(color, img_edge)
    out = row([caption_below(border(fit(img, w=420)), "img", 22),
               caption_below(border(fit(cartoon, w=420)), "Cartoon：双边滤波 + 边缘线", 22)], gap=20)
    save(stamp(out, "候选 · 单张图运行 cartoon.py 处理链 · 替身图 NASA(公有领域)"), L, "20-p7-shot-卡通特效静态预览_替身图.png")


def hw_kernels():
    img = stand_in("coffee")
    outs = [caption_below(border(fit(img, w=300)), "原图", 20)]
    for k in (3, 7, 15):
        outs.append(caption_below(border(fit(cv2.GaussianBlur(img, (k, k), 0), w=300)), f"GaussianBlur ({k}, {k})", 20))
    save(stamp(row(outs, gap=12), "仅参考 · 课后任务2 · 替身图 coffee(CC0)"), L, "20-hw-ref-高斯核3_7_15对比_参考.png")


if __name__ == "__main__":
    print("[20] 图像滤波与去噪")
    p5_animation()
    p2_gain_noise()
    p6_denoise()
    p7_bilateral()
    p7_cartoon()
    hw_kernels()
