# -*- coding: utf-8 -*-
"""第17讲《图像的翻转与旋转》候选素材。

输出（previews/17/）：
  17-p6-diag-旋转矩阵两步流程图_候选.png        P6 缺项（素材需求标“待找/待做”）
  17-p7-shot-翻转与90度旋转预览_替身图.png      P7 录屏静态参考：flip 1/0/-1、rotate 90 的 shape、hv 与 r180 是否一致
  17-p8-shot-旋转30与负30与缩放0.5_替身图.png   P8 录屏静态参考：脚本要求的三次对比（现有 img/17_3 只有 +30°）
  17-p8-ref-扩大画布完整旋转_参考.png            课后任务3的参考思路（仅参考，不建议进PPT）
输入：scikit-image coffee.png（CC0）作为 cat.jpg 的替身。
"""
import cv2
import numpy as np
from _common import *

L = "17"


def _box(c, x, y, w, h, fill, edge):
    cv2.rectangle(c, (x, y), (x + w, y + h), fill, -1)
    cv2.rectangle(c, (x, y), (x + w, y + h), edge, 3)


def p6_flow():
    img = stand_in("coffee")
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), 30, 1.0)
    rot = cv2.warpAffine(img, M, (w, h))
    print("    M =", np.round(M, 3).tolist())

    W, H = 1600, 760
    c = canvas(W, H)
    c = text(c, "旋转任意角度：两步走", (40, 48), 38, INK)
    # 输入缩略图
    thumb_in = border(fit(img, w=260))
    paste(c, thumb_in, 40, 300)
    c = text(c, "原图 img", (40 + 130, 300 + thumb_in.shape[0] + 26), 24, INK, anchor="mm")
    # 第一步
    _box(c, 360, 150, 520, 230, (250, 244, 232), BLUE)
    c = text(c, "① 求旋转矩阵", (380, 190), 30, BLUE)
    c = text(c, "M = cv2.getRotationMatrix2D(", (380, 245), 24, INK)
    c = text(c, "(cx, cy), 角度, 缩放)", (420, 285), 24, INK)
    c = text(c, "M 是 2×3 的数字矩阵", (380, 335), 22, GRAY)
    # 第二步
    _box(c, 360, 450, 520, 200, (232, 246, 236), GREEN)
    c = text(c, "② 应用矩阵", (380, 490), 30, GREEN)
    c = text(c, "rot = cv2.warpAffine(img, M, (宽, 高))", (380, 550), 24, INK)
    c = text(c, "把 M 作用到每个像素上", (380, 600), 22, GRAY)
    # 箭头
    cv2.arrowedLine(c, (310, 330), (355, 270), INK, 3, tipLength=0.25)
    cv2.arrowedLine(c, (620, 385), (620, 445), INK, 3, tipLength=0.25)
    c = text(c, "M", (635, 400), 26, INK)
    cv2.arrowedLine(c, (885, 550), (1010, 450), INK, 3, tipLength=0.08)
    # 输出缩略图
    thumb_out = border(fit(rot, w=300))
    paste(c, thumb_out, 1020, 300)
    c = text(c, "rot：逆时针转 30°", (1020 + 150, 300 + thumb_out.shape[0] + 26), 24, INK, anchor="mm")
    c = text(c, "转出画面的部分被裁掉，四角补黑", (1020 + 150, 300 + thumb_out.shape[0] + 62), 20, GRAY, anchor="mm")
    # 三条注意
    notes = [("旋转中心写 (x, y)：x 在前", RED), ("角度为正 = 逆时针，负 = 顺时针", RED), ("输出尺寸写 (宽, 高)：宽在前", RED)]
    y0 = 150
    for i, (s, colr) in enumerate(notes):
        c = text(c, f"注意{i + 1}：{s}", (960, y0 + i * 44), 24, colr)
    # 实际 M 数值
    m = np.round(M, 2)
    c = text(c, f"本例 (w//2, h//2)=({w//2}, {h//2})，30°，1.0 → M ≈ [[{m[0,0]}, {m[0,1]}, {m[0,2]}], [{m[1,0]}, {m[1,1]}, {m[1,2]}]]",
             (40, H - 40), 20, GRAY)
    save(stamp(c, "候选 · 流程示意图 · 缩略图为替身图 coffee(CC0)"), L, "17-p6-diag-旋转矩阵两步流程图_候选.png")


def p7_flip_rot90():
    img = stand_in("coffee")
    h_flip = cv2.flip(img, 1); v_flip = cv2.flip(img, 0); hv = cv2.flip(img, -1)
    r90 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    r180 = cv2.rotate(img, cv2.ROTATE_180)
    same = bool((hv == r180).all())
    print("    img.shape, r90.shape =", img.shape, r90.shape, "| hv == r180:", same)
    s = 0.5
    t = lambda im, cap, colr=INK: caption_below(border(fit(im, w=int(im.shape[1] * s))), cap, 20, colr)
    top = row([t(img, "原图"), t(h_flip, "flip(img, 1) 水平"), t(v_flip, "flip(img, 0) 垂直"), t(hv, "flip(img, -1) 都翻")], gap=16)
    bottom = row([t(r90, f"顺时针90°  shape {r90.shape}"), t(r180, "ROTATE_180"),
                  t(hv, "flip(img, -1)")], gap=16)
    info = canvas(top.shape[1], 50)
    info = text(info, f"print(img.shape, r90.shape) → {img.shape} {r90.shape}；hv 与 r180 完全一样：{same}",
                (top.shape[1] // 2, 25), 22, INK, anchor="mm")
    out = col([top, bottom, info], gap=16)
    save(stamp(out, "候选 · 替身图 coffee(CC0)，非 cat.jpg 实拍"), L, "17-p7-shot-翻转与90度旋转预览_替身图.png")


def p8_rot_three():
    img = stand_in("coffee")
    h, w = img.shape[:2]
    outs = []
    for angle, scale, cap in [(30, 1.0, "角度 30，缩放 1.0：逆时针"), (-30, 1.0, "角度 -30：顺时针"),
                              (30, 0.5, "角度 30，缩放 0.5：四角不再被裁")]:
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, scale)
        outs.append(caption_below(border(fit(cv2.warpAffine(img, M, (w, h)), w=420)), cap, 22))
    out = row(outs, gap=20)
    note = canvas(out.shape[1], 46)
    note = text(note, "缩放 0.5 只对这张宽高比的示例图刚好够用；要完整保留任意图片，应扩大输出画布（见课后任务参考图）",
                (out.shape[1] // 2, 23), 20, GRAY, anchor="mm")
    out = col([out, note], gap=4)
    save(stamp(out, "候选 · 替身图 coffee(CC0)，非 cat.jpg 实拍"), L, "17-p8-shot-旋转30与负30与缩放0.5_替身图.png")


def ref_expand_canvas(angle=45):
    """课后任务3：旋转 45° 且四角不被裁掉。参考写法：按旋转后外接矩形扩大画布并平移。"""
    img = stand_in("coffee")
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(h * sin + w * cos), int(h * cos + w * sin)
    M[0, 2] += nw / 2 - w / 2
    M[1, 2] += nh / 2 - h / 2
    full = cv2.warpAffine(img, M, (nw, nh))
    # 对照：只调缩放
    s = min(w / nw, h / nh)
    M2 = cv2.getRotationMatrix2D((w // 2, h // 2), angle, s)
    fit_scale = cv2.warpAffine(img, M2, (w, h))
    print(f"    45°：扩大画布 {w}x{h} → {nw}x{nh}；或缩放 {s:.3f} 保持原画布")
    out = row([caption_below(border(fit(fit_scale, w=420)), f"缩放 {s:.2f}，画布不变", 20),
               caption_below(border(fit(full, w=int(420 * nw / w))), f"扩大画布到 {nw}×{nh}", 20)], gap=20)
    save(stamp(out, "仅参考 · 课后任务3思路 · 替身图 coffee(CC0)"), L, "17-p8-ref-扩大画布完整旋转_参考.png")


if __name__ == "__main__":
    print("[17] 图像的翻转与旋转")
    p6_flow()
    p7_flip_rot90()
    p8_rot_three()
    ref_expand_canvas()
