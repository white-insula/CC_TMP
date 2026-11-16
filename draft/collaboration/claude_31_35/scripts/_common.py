# -*- coding: utf-8 -*-
"""第31—35讲候选素材公共工具（Claude 云端协作，独立于 draft/online_course/_vis.py）。

- 不读取任何本机 D:/E:/F: 路径，不下载图片；本批所有输入均由程序合成（合成电路板、二维码、流程图、
  合成答题卡等），不依赖 scikit-image 或任何外部样图。
- 合成输入只用于讲清原理和核对数值，不代表真实电路板照片、学生答题卡、模板文件等本机素材。
- 所有输出底部附灰色候选条（stamp），写明“候选”及输入性质，避免与正式素材混淆。
"""
import os
import glob
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PREV = os.path.join(ROOT, "previews")

# 字体：本机课程用 C:/Windows/Fonts/msyh.ttc / simhei.ttf；云端用文泉驿正黑代替，版式可能有细微差异
_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]
FONT_PATH = next((p for p in _FONT_CANDIDATES if os.path.exists(p)), None)
if FONT_PATH is None:
    raise SystemExit("找不到中文字体：请安装文泉驿正黑或在 _FONT_CANDIDATES 中添加路径")

# 配色（与课程配图接近：深蓝字、琥珀高亮、红色警示）
INK = (55, 42, 31)        # BGR 深蓝灰
AMB = (0, 169, 242)       # BGR 琥珀
RED = (40, 40, 220)
GREEN = (60, 160, 60)
BLUE = (200, 110, 30)
GRAY = (150, 150, 150)
WHITE = (255, 255, 255)


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def text(img, s, xy, size=28, color=INK, bg=None, pad=6, anchor="la"):
    """在 BGR 图上写中文；bg 给出时先画底色块。返回新图。"""
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    f = font(size)
    rgb = tuple(int(c) for c in color[::-1])
    if bg is not None:
        l, t, r, b = d.textbbox(xy, s, font=f, anchor=anchor)
        d.rectangle((l - pad, t - pad, r + pad, b + pad), fill=tuple(int(c) for c in bg[::-1]))
    d.text(xy, s, font=f, fill=rgb, anchor=anchor)
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def text_size(s, size):
    f = font(size)
    l, t, r, b = f.getbbox(s)
    return r - l, b - t


def canvas(w, h, color=WHITE):
    return np.full((h, w, 3), color, np.uint8)


def paste(dst, src, x, y):
    h, w = src.shape[:2]
    dst[y:y + h, x:x + w] = bgr(src)
    return dst


def bgr(g):
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR) if g.ndim == 2 else g


def fit(img, w=None, h=None):
    ih, iw = img.shape[:2]
    s = (w / iw) if w else (h / ih)
    return cv2.resize(img, (max(1, int(iw * s)), max(1, int(ih * s))),
                      interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)


def border(img, color=(200, 200, 200), t=2):
    return cv2.copyMakeBorder(bgr(img), t, t, t, t, cv2.BORDER_CONSTANT, value=color)


def caption_below(img, s, size=24, color=INK, h=46):
    """图片下方加一行说明。"""
    img = bgr(img)
    W = max(img.shape[1], text_size(s, size)[0] + 12)   # 文字比图宽时加宽画布，避免截断
    out = canvas(W, img.shape[0] + h)
    x0 = (W - img.shape[1]) // 2
    out[:img.shape[0], x0:x0 + img.shape[1]] = img
    return text(out, s, (W // 2, img.shape[0] + h // 2), size, color, anchor="mm")


def row(imgs, gap=24, bg=255, valign="top"):
    imgs = [bgr(i) for i in imgs]
    H = max(i.shape[0] for i in imgs)
    W = sum(i.shape[1] for i in imgs) + gap * (len(imgs) - 1)
    out = np.full((H, W, 3), bg, np.uint8)
    x = 0
    for i in imgs:
        y = 0 if valign == "top" else (H - i.shape[0]) // 2
        out[y:y + i.shape[0], x:x + i.shape[1]] = i
        x += i.shape[1] + gap
    return out


def col(imgs, gap=24, bg=255):
    imgs = [bgr(i) for i in imgs]
    W = max(i.shape[1] for i in imgs)
    H = sum(i.shape[0] for i in imgs) + gap * (len(imgs) - 1)
    out = np.full((H, W, 3), bg, np.uint8)
    y = 0
    for i in imgs:
        x = (W - i.shape[1]) // 2
        out[y:y + i.shape[0], x:x + i.shape[1]] = i
        y += i.shape[0] + gap
    return out


def pad_to(img, W, H, bg=255):
    """居中放到 W×H 白底（16:9 预览统一尺寸用）。"""
    img = bgr(img)
    s = min(W / img.shape[1], H / img.shape[0], 1.0)
    if s < 1:
        img = fit(img, w=int(img.shape[1] * s))
    out = np.full((H, W, 3), bg, np.uint8)
    y, x = (H - img.shape[0]) // 2, (W - img.shape[1]) // 2
    out[y:y + img.shape[0], x:x + img.shape[1]] = img
    return out


def stamp(img, note="候选 · 待用户审核"):
    """右下角小角标，标明候选身份与图源性质。"""
    img = bgr(img)
    H, W = img.shape[:2]
    foot = canvas(W, 30, (238, 238, 238))
    foot = text(foot, note, (W - 10, 15), 16, (90, 90, 90), anchor="rm")
    return np.vstack([img, foot])


def title_bar(img, s, size=30):
    img = bgr(img)
    bar = canvas(img.shape[1], 64)
    bar = text(bar, s, (20, 32), size, INK, anchor="lm")
    return np.vstack([bar, img])


def save(img, lesson, name):
    d = os.path.join(PREV, lesson)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    ok, buf = cv2.imencode(os.path.splitext(name)[1], img)
    assert ok, p
    buf.tofile(p)
    print("  saved", os.path.relpath(p, ROOT), f"{img.shape[1]}x{img.shape[0]}")
    return p


def save_gif(frames_bgr, lesson, name, durations_ms, colors=128):
    d = os.path.join(PREV, lesson)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, name)
    pil = [Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)) for f in frames_bgr]
    pal = [im.convert("P", palette=Image.ADAPTIVE, colors=colors) for im in pil]
    pal[0].save(p, save_all=True, append_images=pal[1:], duration=durations_ms, loop=0, optimize=True)
    print("  saved", os.path.relpath(p, ROOT), f"{len(frames_bgr)} frames")
    return p


def keyframe_sheet(frames, idx, lesson, name, w=960, labels=None):
    """从 GIF 帧中取若干关键帧竖排拼成一张 PNG，供不播放 GIF 时审阅。"""
    tiles = []
    for k, i in enumerate(idx):
        f = fit(frames[i], w=w)
        lab = labels[k] if labels else f"关键帧 {k + 1}（第 {i + 1}/{len(frames)} 帧）"
        bar = text(canvas(w, 40, (60, 60, 60)), lab, (12, 20), 20, (255, 255, 255), anchor="lm")
        tiles.append(np.vstack([bar, f]))
    return save(col(tiles, gap=14), lesson, name)
