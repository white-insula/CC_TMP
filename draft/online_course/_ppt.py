# -*- coding: utf-8 -*-
"""PPT 版式 v2(2026-11-05,第 21 节样板)。
仍以《Linux基础》课 pptx 为母版(保证与学校课程包兼容),版式在此用代码画:
  cover   片头             SEG 中 bullets 为 None
  goals   学习目标卡片     标题含「学习目标」
  demo    录屏演示(深色)   镜头 = 录屏演示
  summary 内容总结卡片     标题 = 内容总结
  tasks   课后任务         标题含「课后任务」
  content 普通讲解页       其余;content.py 的 VIS 给了图 → 左文右图
要点写法约定:
  「术语：解释」  → 术语加粗着色      以全角空格「　」开头 → 次级要点
  像代码的一行(含 = 或 ( 且基本是英文) → 放进代码框
每节可选 VIS = {slide标题: (图片相对路径, 图注)}。
"""
import os, re
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from PIL import Image

# ---- 主题 ----
W, H = 13.333, 7.5                  # 16:9;改回 4:3 只需 W = 10
INK = RGBColor(0x1F, 0x2A, 0x37)    # 深石墨:标题、深色页底
AMBER = RGBColor(0xF2, 0xA9, 0x00)  # 琥珀:编号、强调(“打光”的意象)
TEAL = RGBColor(0x0E, 0x7C, 0x72)   # 青绿:术语、对勾
MUTED = RGBColor(0x6B, 0x77, 0x85)
PANEL = RGBColor(0xF1, 0xF4, 0xF7)
TINT = RGBColor(0xE6, 0xF3, 0xF1)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
CODEBG = RGBColor(0x26, 0x32, 0x40)
CODEFG = RGBColor(0xE8, 0xED, 0xF2)
FONT, MONO = "微软雅黑", "Consolas"
M = 0.6                             # 页边距
LAYOUT_TITLE_ONLY = 5


# ---------- 基础绘制 ----------
def _font(run, size, color=INK, bold=False, mono=False):
    f = run.font
    f.size = Pt(size); f.bold = bold; f.color.rgb = color
    name = MONO if mono else FONT
    f.name = name
    rPr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = rPr.makeelement(qn(tag), {}); rPr.append(el)
        el.set("typeface", MONO if (mono and tag == "a:cs") else (FONT if tag == "a:ea" else name))


def _box(slide, x, y, w, h, name=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, Inches(0.04))
    if name:
        tb.name = name
    return tb, tf


def _rect(slide, x, y, w, h, fill, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = fill
    s.line.fill.background(); s.shadow.inherit = False
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    return s


def _circle_num(slide, x, y, d, text, fill=AMBER, color=INK, size=18):
    c = _rect(slide, x, y, d, d, fill, MSO_SHAPE.OVAL)
    tf = c.text_frame
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, side, 0)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    r = p.add_run(); r.text = text; _font(r, size, color, True)
    return c


def _bg(slide, color):
    f = slide.background.fill; f.solid(); f.fore_color.rgb = color


def _title(slide, text, color=INK, y=0.42, size=30):
    t = slide.shapes.title
    t.left, t.top, t.width, t.height = Inches(M), Inches(y), Inches(W - 2 * M), Inches(0.85)
    tf = t.text_frame; tf.word_wrap = True; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for side in ("margin_left", "margin_right"):
        setattr(tf, side, 0)
    tf.text = ""
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    r = p.add_run(); r.text = text; _font(r, size, color, True)


def _footer(slide, c, k, n, dark=False):
    col = RGBColor(0xA9, 0xB4, 0xC0) if dark else MUTED
    _, tf = _box(slide, M, H - 0.5, 8, 0.3)
    r = tf.paragraphs[0].add_run(); r.text = f"《机器视觉技术应用实践》 · {c.NO} {c.NAME}"; _font(r, 10, col)
    _, tf = _box(slide, W - M - 1.5, H - 0.5, 1.5, 0.3)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
    r = p.add_run(); r.text = f"{k} / {n}"; _font(r, 10, col)


def _picture(slide, path, x, y, w, h, caption=None, dark=False):
    """等比放进 (x,y,w,h) 区域、水平居中;图注放在图下方。"""
    cap_h = 0.42 if caption else 0
    iw, ih = Image.open(path).size
    s = min(w / iw, (h - cap_h) / ih)
    pw, ph = iw * s, ih * s
    px = x + (w - pw) / 2
    py = y + (h - cap_h - ph) / 2
    slide.shapes.add_picture(path, Inches(px), Inches(py), Inches(pw), Inches(ph))
    if caption:
        _, tf = _box(slide, x, py + ph + 0.08, w, 0.36)
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
        r = p.add_run(); r.text = caption
        _font(r, 12, RGBColor(0xC9, 0xD2, 0xDC) if dark else MUTED)


def _aspect(path):
    w, h = Image.open(path).size
    return w / h


# ---------- 要点排版 ----------
CODE_RE = re.compile(r"^[\x00-\x7f]{6,}$")


def _is_code(b):
    b = b.strip()
    return bool(CODE_RE.match(b)) and ("=" in b or "(" in b)


def _bullets(slide, items, x, y, w, h, size=20, all_code=False):
    """普通要点 + 代码行(合并成代码框),按顺序自上而下排。返回用掉的高度。"""
    groups = []                          # [("text", [..]) | ("code", [..])]
    for b in items:
        kind = "code" if (all_code or _is_code(b)) else "text"
        if groups and groups[-1][0] == kind:
            groups[-1][1].append(b)
        else:
            groups.append((kind, [b]))
    cy = y
    for kind, lines in groups:
        if kind == "code":
            lh = 0.255
            bh = 0.3 + lh * sum(1 + len(l) // int((w - 0.4) * 8.2) for l in lines)
            _rect(slide, x, cy, w, bh, CODEBG, radius=0.04)
            _, tf = _box(slide, x + 0.2, cy + 0.12, w - 0.4, bh - 0.2)
            for i, l in enumerate(lines):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                r = p.add_run(); r.text = l; _font(r, 15, CODEFG, mono=True)
            cy += bh + 0.25
        else:
            n_lines = 0
            _, tf = _box(slide, x, cy, w, h - (cy - y))
            for i, b in enumerate(lines):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                sub = b.startswith("　")
                b = b.strip("　 ")
                p.space_after = Pt(10 if not sub else 6)
                pPr = p._p.get_or_add_pPr()
                pPr.set("marL", str(Inches(0.34))); pPr.set("indent", "0" if sub else str(-Inches(0.34)))
                if sub:
                    r = p.add_run(); r.text = b; _font(r, size - 3, MUTED)
                else:
                    dot = p.add_run(); dot.text = "■	"; _font(dot, size - 8, AMBER)
                    m = re.match(r"^(.{1,22}?)[：:](.+)$", b)
                    if m and "→" not in m.group(1):
                        r = p.add_run(); r.text = m.group(1) + "："; _font(r, size, TEAL, True)
                        r = p.add_run(); r.text = m.group(2); _font(r, size)
                    else:
                        r = p.add_run(); r.text = b; _font(r, size)
                chars = sum(2 if ord(ch) > 127 else 1 for ch in b)
                n_lines += 1 + chars // int(w * 6.6 * 20 / size)
            cy += n_lines * size * 1.55 / 72 + 0.2
    return cy - y


# ---------- 各页型 ----------
def _cover(slide, c, title, vis):
    _bg(slide, INK)
    chip = _rect(slide, M, 1.55, 0.6 + 0.2 * len(c.MODULE), 0.46, AMBER, radius=0.5)
    tf = chip.text_frame; tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    r = tf.paragraphs[0].add_run(); r.text = c.MODULE; _font(r, 14, INK, True)
    size = 44 if len(title) <= 10 else 36
    head, sep, tail = title.partition("：")
    if len(title) > 12 and tail:                       # 长标题在冒号处换行,避免孤字
        _title(slide, head + sep, WHITE, y=2.25, size=size)
        p = slide.shapes.title.text_frame.add_paragraph(); p.alignment = PP_ALIGN.LEFT
        pPr = p._p.get_or_add_pPr(); pPr.set("marL", "0"); pPr.set("indent", "0")
        r = p.add_run(); r.text = tail; _font(r, size, WHITE, True)
    else:
        _title(slide, title, WHITE, y=2.25, size=size)
    slide.shapes.title.width = Inches(W - 2 * M - 4.4)     # 给右侧大号节号让位,长标题自动换行
    slide.shapes.title.height = Inches(1.8)
    _, tf = _box(slide, M, 4.25, 7.5, 0.5)
    r = tf.paragraphs[0].add_run(); r.text = "机器视觉技术应用实践 · 智慧课程微课"; _font(r, 16, RGBColor(0xC9, 0xD2, 0xDC))
    _, tf = _box(slide, W - M - 4.2, 1.2, 4.2, 3.2)
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
    r = p.add_run(); r.text = c.NO; _font(r, 160, AMBER, True)
    _, tf = _box(slide, M, H - 0.9, 8, 0.35)
    r = tf.paragraphs[0].add_run(); r.text = f"第 {int(c.NO)} 讲"; _font(r, 12, RGBColor(0xA9, 0xB4, 0xC0))


def _goals(slide, items):
    items = [re.sub(r"^\d+\.\s*", "", b) for b in items]
    cols = 2; gw = (W - 2 * M - 0.4) / cols
    rows = (len(items) + 1) // 2; gh = min(2.1, (5.2 - 0.3 * (rows - 1)) / rows)
    for i, b in enumerate(items):
        x = M + (i % cols) * (gw + 0.4); y = 1.65 + (i // cols) * (gh + 0.3)
        _rect(slide, x, y, gw, gh, PANEL)
        _, tf = _box(slide, x + 0.3, y + 0.15, 1.2, gh - 0.3)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = tf.paragraphs[0].add_run(); r.text = f"{i + 1:02d}"; _font(r, 40, AMBER, True)
        _, tf = _box(slide, x + 1.55, y + 0.15, gw - 1.8, gh - 0.3)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = tf.paragraphs[0].add_run(); r.text = b; _font(r, 20)


def _summary(slide, items):
    cols = 2 if len(items) in (4, 6) else 1
    gw = (W - 2 * M - 0.4 * (cols - 1)) / cols
    rows = (len(items) + cols - 1) // cols
    gh = min(1.9, (5.2 - 0.3 * (rows - 1)) / rows)
    for i, b in enumerate(items):
        x = M + (i % cols) * (gw + 0.4); y = 1.65 + (i // cols) * (gh + 0.3)
        _rect(slide, x, y, gw, gh, TINT)
        _circle_num(slide, x + 0.3, y + gh / 2 - 0.3, 0.6, "✓", TEAL, WHITE, 20)
        _, tf = _box(slide, x + 1.15, y + 0.1, gw - 1.4, gh - 0.2)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        m = re.match(r"^(.{1,22}?)[：:](.+)$", b)
        p = tf.paragraphs[0]
        if m:
            r = p.add_run(); r.text = m.group(1); _font(r, 20, TEAL, True)
            p = tf.add_paragraph(); r = p.add_run(); r.text = m.group(2).strip(); _font(r, 17)
        else:
            r = p.add_run(); r.text = b; _font(r, 19)


def _tasks(slide, items):
    items = [re.sub(r"^\d+\.\s*", "", b) for b in items]
    gh = min(1.4, (5.0 - 0.25 * (len(items) - 1)) / len(items))
    for i, b in enumerate(items):
        y = 1.7 + i * (gh + 0.25)
        _rect(slide, M, y, W - 2 * M, gh, PANEL)
        _circle_num(slide, M + 0.35, y + gh / 2 - 0.35, 0.7, str(i + 1), AMBER, INK, 24)
        _, tf = _box(slide, M + 1.35, y, W - 2 * M - 1.6, gh)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        r = tf.paragraphs[0].add_run(); r.text = b; _font(r, 20)


def _demo(slide, title, bullets, screen, vis, here):
    _bg(slide, INK)
    chip = _rect(slide, M, 0.5, 1.5, 0.42, AMBER, radius=0.5)
    r = chip.text_frame.paragraphs[0].add_run(); r.text = "录屏演示"; _font(r, 13, INK, True)
    chip.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
    _title(slide, title, WHITE, y=1.05, size=30)
    raw = re.sub(r"^\[\s*(录屏[:：])?\s*|\s*\]$", "", bullets[0]) if bullets else ""
    steps = [s.strip() for s in raw.split("→") if s.strip()]
    if vis and _aspect(os.path.join(here, vis[0])) > 2.2:      # 横长图:步骤横排在上,图在下
        sw = (W - 2 * M) / max(len(steps), 1)
        for i, st in enumerate(steps):
            _circle_num(slide, M + i * sw, 2.2, 0.44, str(i + 1), AMBER, INK, 15)
            _, tf = _box(slide, M + i * sw + 0.55, 2.17, sw - 0.9, 0.9)
            r = tf.paragraphs[0].add_run(); r.text = st; _font(r, 17, WHITE)
        _picture(slide, os.path.join(here, vis[0]), M, 3.3, W - 2 * M, H - 0.75 - 3.3, vis[1], dark=True)
        return
    lw = 5.4 if vis else W - 2 * M
    y = 2.2; step_h = min(0.78, 4.5 / max(len(steps), 1))
    for i, s in enumerate(steps):
        _circle_num(slide, M, y + i * step_h + 0.04, 0.44, str(i + 1), AMBER, INK, 15)
        _, tf = _box(slide, M + 0.65, y + i * step_h, lw - 0.7, step_h)
        tf.vertical_anchor = MSO_ANCHOR.TOP
        r = tf.paragraphs[0].add_run(); r.text = s; _font(r, 18, WHITE)
    if vis:
        path, cap = vis
        x0 = M + lw + 0.4
        _picture(slide, os.path.join(here, path), x0, 2.0, W - M - x0, 4.85, cap, dark=True)
    else:
        code = [l.strip("`") for l in screen.split("\n") if l.startswith("`")]
        if code:
            yy = y + len(steps) * step_h + 0.2
            _bullets(slide, code[:9], M, yy, W - 2 * M, H - 0.8 - yy, all_code=True)


def vis_of(c, here, quiet=False):
    """配图登记:NN/img/vis.json(_visuals 程序生成)+ content.py 的 VIS + manual/ 里审核通过的手工素材(_manual.py)。
    同一页既有程序图又有手工图时,程序图优先,并报冲突。"""
    import json
    import _manual
    v = {}
    j = os.path.join(here, "img", "vis.json")
    if os.path.exists(j):
        v.update({k: tuple(x) for k, x in json.load(open(j, encoding="utf-8")).items()})
    v.update(getattr(c, "VIS", {}))
    for title, ent in _manual.vis_entries(c, here).items():
        if title in v:
            if not quiet:
                print(f"  ⚠️ {c.NO}「{title}」:程序配图与手工素材冲突,暂用程序配图;请在登记表把其一改为「仅参考」")
            continue
        v[title] = ent
    return v


def error_screenshots(slide, no, page):
    """Native PPT crops keep the user's complete screenshot bytes intact."""
    if no != "07" or page != 7:
        return False
    import _manual
    approved = {os.path.basename(path): path
                for kind, path, row in _manual.approved(no).get(page, []) if kind == "shot"}
    entries = [
        ("07-p7-shot-解释器选择错误.png", (.04, .54, .25, .25),
         "① 找不到 cv2", "原因：解释器选错或未安装", "解决：选用已安装 OpenCV 的解释器"),
        ("07-p7-shot-图片文件名错误.png", (.04, .53, .25, .16),
         "② 图片未读到", "原因：文件名或路径错误", "解决：核对文件名、位置与路径"),
        ("07-p7-shot-缺少waitKey.png", (.04, .26, .15, .27),
         "③ 窗口一闪而过", "原因：缺少等待按键语句", "解决：在关闭窗口前加 waitKey(0)"),
    ]
    if any(name not in approved for name, *_ in entries):
        return False
    for i, (name, crop, heading, cause, remedy) in enumerate(entries):
        y = 1.50 + i * 1.65
        _rect(slide, M, y, W-2*M, 1.52, PANEL)
        path = approved[name]
        with Image.open(path) as im:
            iw, ih = im.size
        left, top, right, bottom = crop
        fw, fh = iw*(1-left-right), ih*(1-top-bottom)
        scale = min(7.7/fw, 1.32/fh)
        pw, ph = fw*scale, fh*scale
        pic = slide.shapes.add_picture(path, Inches(M+.12+(7.7-pw)/2),
                                      Inches(y+.10+(1.32-ph)/2), Inches(pw), Inches(ph))
        pic.crop_left, pic.crop_top, pic.crop_right, pic.crop_bottom = crop
        for dy, label, size, color, bold in [
            (.12, heading, 20, TEAL, True),
            (.58, cause, 15, INK, False),
            (.98, remedy, 14, INK, False),
        ]:
            _, tf = _box(slide, 8.75, y+dy, W-M-8.75, .42)
            r = tf.paragraphs[0].add_run(); r.text = label
            _font(r, size, color, bold)
    return True


def build(c, out, template, here):
    import _delivery
    _delivery.assert_regeneration_allowed(c.NO)
    prs = Presentation(template)
    lst = prs.slides._sldIdLst
    for sid in list(lst):
        prs.part.drop_rel(sid.rId); lst.remove(sid)
    prs.slide_width, prs.slide_height = Inches(W), Inches(H)
    vis_map = vis_of(c, here)
    n = len(c.SEG)
    for k, (shot, title, bullets, narr, screen) in enumerate(c.SEG, 1):
        s = prs.slides.add_slide(prs.slide_layouts[LAYOUT_TITLE_ONLY])
        vis = vis_map.get(title)
        if bullets is None:
            _cover(s, c, title, vis)
        # 2026-11-14 用户要求：后期公司负责录屏剪辑，停用录屏专用占位页分支。
        # 录屏镜头仍按下方普通教学页生成，保留页号、要点与备注。
        # elif shot == "录屏演示":
        #     _demo(s, title, bullets, screen, vis, here)
        #     _footer(s, c, k, n, dark=True)
        else:
            _title(s, title)
            if error_screenshots(s, c.NO, k):
                pass
            elif "学习目标" in title:
                _goals(s, bullets)
            elif title == "内容总结":
                _summary(s, bullets)
            elif "课后任务" in title:
                _tasks(s, bullets)
            elif vis and _aspect(os.path.join(here, vis[0])) > 2.2:     # 横长图:上文下图
                used = _bullets(s, bullets, M, 1.6, W - 2 * M, 2.4, size=22)
                y0 = 1.6 + used + 0.1
                _picture(s, os.path.join(here, vis[0]), M, y0, W - 2 * M, H - 0.7 - y0, vis[1])
            elif vis:
                lw = 6.1
                _bullets(s, bullets, M, 1.7, lw, 5.0)
                _picture(s, os.path.join(here, vis[0]), M + lw + 0.4, 1.55, W - 2 * M - lw - 0.4, 5.2, vis[1])
            else:
                _bullets(s, bullets, M, 1.7, W - 2 * M, 5.0, size=22)
            _footer(s, c, k, n)
        if narr:
            s.notes_slide.notes_text_frame.text = narr
    prs.save(out)


# ---------- 素材需求清单 ----------
# 同时识别结构/流程图和逐步展示，避免仅匹配“图片/动画”漏掉画面要求。
NEED = re.compile(r"视频|截图|照片|动画|示意|草图|实拍|图解|对比|对照|效果|配图|图片|界面|实物|结构图|框图|流程图|时间轴|标志墙|卡片|逐张出现|逐行出现|依次出现|依次点亮")


def needs(c, here):
    """列出「画面」里提到、但还没有配图的素材。返回 markdown 行。"""
    import _manual
    vis_map = vis_of(c, here, quiet=True)
    media = _manual.media_ready(c.NO)
    decisions = _manual.display_decisions(c.NO)
    recorded = _manual.recorded_pages(c.NO)
    rows = []
    for k, (shot, title, bullets, narr, screen) in enumerate(c.SEG, 1):
        first = screen.split("\n")[0]
        if not NEED.search(first) and title not in vis_map and k not in media and k not in decisions and k not in recorded:
            continue
        got = vis_map.get(title)
        if k in media and not got:
            status = "✅ 录屏/动画已就绪:" + "、".join(media[k])
        else:
            status = f"✅ {got[0]}" if got else "⬜ 待找/待做"
        if got:
            # A picture cannot satisfy an animation, video or recording request.
            # Do not let the summary hide these partially fulfilled pages.
            dynamic = ("视频" if "视频" in first else
                       "动画/逐步展示" if re.search(r"动画|逐张出现|逐行出现|依次出现|依次点亮", first) else None)
            if "录屏" in first and k not in media:
                status = f"📷 静态图已有:{got[0]};录屏待做（见录屏专项清单）"
            elif dynamic and k not in media:
                status = f"⚠️ 静态图已有:{got[0]};{dynamic}待做"
            elif dynamic:
                status += "(动态素材已就绪:" + "、".join(media[k]) + ")"
        if k in decisions and (got or not NEED.search(first)):
            status = f"✅ 用户确认：{decisions[k]}" + (f"；配图:{got[0]}" if got else "")
        if k in recorded:
            status = f"✅ {recorded[k]}；交视频制作公司剪辑"
        rows.append(f"| {k} | {title} | {first.replace('|', '/')} | {status} |")
    return rows
