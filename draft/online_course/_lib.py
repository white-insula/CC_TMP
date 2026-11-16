# -*- coding: utf-8 -*-
"""在线课微课生成器(全课共用)。
每节微课目录 NN/ 下放一个 content.py,定义 NO / NAME / MODULE / SEG,然后:
    python _lib.py 01 02 ...      生成指定节
    python _lib.py all            生成全部
产物(按《Linux基础》在线课命名规范):
    NN/脚本NN.docx               镜头表:序号 / 镜头 / 解说词 / 画面;开场与结尾句加粗标红
    NN/NN-<知识点名>.pptx         套 Linux 课模板;一个镜头一页;解说词写入备注
SEG 每项:(镜头, slide标题, slide要点列表[None=片头], 解说词[TTS 适配], 画面)
"""
import os, re, sys, importlib.util
from pptx import Presentation
from docx import Document
from docx.shared import RGBColor, Pt
from docx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
REF = r"E:\《Linux基础》在线课（负责人：张于思）\process\E_1\32\32-SSH服务安装与配置_最终版.pptx"
COURSE = "《机器视觉技术应用实践》"
OPEN = "大家好，欢迎来到《机器视觉技术应用实践》课程！"
CLOSE = "本讲的内容就到这里！"
RATE = 250          # TTS 语速估算:字/分钟(拿到数字人成片后用实测值校准)
MIN_T, MAX_T, HARD_T = 3.0, 5.0, 6.0   # 最佳 3–5 分钟;内容确实多可略超;>6 分钟需复核


def load(no):
    path = os.path.join(HERE, no, "content.py")
    spec = importlib.util.spec_from_file_location("c" + no, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def check(c):
    narr = [s[3] for s in c.SEG if s[3]]
    assert narr[0].startswith(OPEN), f"{c.NO}: 开场句不对"
    assert narr[-1].endswith(CLOSE), f"{c.NO}: 结尾句不对"
    n = sum(len(re.sub(r"\s", "", t)) for t in narr)
    return n


def build_ppt(c, out):
    """v2 版式(见 _ppt.py)。旧的纯文字版保留为 build_ppt_v1。"""
    import _delivery
    _delivery.assert_regeneration_allowed(c.NO)
    import _ppt
    _ppt.build(c, out, REF, os.path.join(HERE, c.NO))


def write_needs(c):
    """导出本节「素材需求.md」:画面里提到、但还没配图的素材。"""
    import _ppt
    rows = _ppt.needs(c, os.path.join(HERE, c.NO))
    path = os.path.join(HERE, c.NO, "素材需求.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {c.NO} {c.NAME} · 素材需求\n\n> 由 `_lib.py` 自动生成。程序配图见 `_visuals/`;手工素材放 `manual/{c.NO}/`(命名 `{c.NO}-p页号-类型-简述`),在 `manual/素材登记.csv` 审核「通过」后重新生成即自动变 ✅。\n\n")
        f.write("> 录屏例外：用户确认已录制即在 `manual/录屏完成登记.json` 登记完成；不要求视频文件或脚本检查，后期交视频制作公司剪辑，只更新清单。\n\n")
        f.write("| 页 | 标题 | 画面要求 | 状态 |\n|---|---|---|---|\n")
        f.write("\n".join(rows) + "\n")
    return sum("⬜" in r for r in rows)


def build_ppt_v1(c, out):
    import _delivery
    _delivery.assert_regeneration_allowed(c.NO)
    prs = Presentation(REF)
    lst = prs.slides._sldIdLst
    for sid in list(lst):                      # 清空模板原有页(先 drop 关系)
        prs.part.drop_rel(sid.rId)
        lst.remove(sid)
    for shot, title, bullets, narr, screen in c.SEG:
        if bullets is None:
            s = prs.slides.add_slide(prs.slide_layouts[0])
            s.shapes.title.text = title
            s.placeholders[1].text = f"{COURSE}\n{c.MODULE} · 脚本{c.NO}"
        else:
            s = prs.slides.add_slide(prs.slide_layouts[1])
            s.shapes.title.text = title
            tf = s.placeholders[1].text_frame
            tf.word_wrap = True
            for i, it in enumerate(bullets):
                p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
                p.text = it
        if narr:
            s.notes_slide.notes_text_frame.text = narr
    prs.save(out)


def _set_font(run, size=None):
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    if size:
        run.font.size = Pt(size)


def _narr_cell(cell, text):
    """解说词单元格:开场句、结尾句加粗标红(同 Linux 课示例)。"""
    cell.text = ""
    para = cell.paragraphs[0]
    parts = []
    t = text
    if t.startswith(OPEN):
        parts.append((OPEN, True)); t = t[len(OPEN):]
    tail = None
    if t.endswith(CLOSE):
        tail = CLOSE; t = t[: -len(CLOSE)]
    if t:
        parts.append((t, False))
    if tail:
        parts.append((tail, True))
    for txt, hl in parts:
        r = para.add_run(txt)
        _set_font(r)
        if hl:
            r.bold = True
            r.font.color.rgb = RGBColor(0xFF, 0x00, 0x00)


def build_docx(c, out):
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = "宋体"
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    st.font.size = Pt(10.5)
    h = doc.add_paragraph()
    _set_font(h.add_run(f"标题《{c.NAME}》"), 14)
    t = doc.add_table(rows=1, cols=4)
    t.style = "Table Grid"
    for cell, txt in zip(t.rows[0].cells, ["序号", "镜头", "解说词", "画面"]):
        cell.text = ""
        r = cell.paragraphs[0].add_run(txt); r.bold = True; _set_font(r)
    for i, (shot, title, bullets, narr, screen) in enumerate(c.SEG, 1):
        row = t.add_row().cells
        row[0].text = str(i); row[1].text = shot; row[3].text = screen
        _narr_cell(row[2], narr)
    for row in t.rows:                          # 列宽:解说词最宽
        for cell, w in zip(row.cells, (0.5, 0.9, 4.2, 1.6)):
            cell.width = int(w * 914400)
    doc.save(out)


def build(no):
    import _delivery
    _delivery.assert_regeneration_allowed(no)
    c = load(no)
    n = check(c)
    d = os.path.join(HERE, no)
    ppt = os.path.join(d, f"{no}-{c.NAME}.pptx")
    doc = os.path.join(d, f"脚本{no}.docx")
    build_ppt(c, ppt)
    build_docx(c, doc)
    todo = write_needs(c)
    import _manual
    with open(os.path.join(d, ".manual_hash"), "w") as f:   # 已接入手工素材的指纹,供 _sync_check 判断是否过期
        f.write(_manual.fingerprint(no))
    m = n / RATE
    flag = ("偏短" if m < MIN_T else "OK" if m <= MAX_T else
            "略长,可接受" if m <= HARD_T else "!! 过长,需复核")
    print(f"{no} {c.NAME}: {len(c.SEG)} 镜头 / 解说 {n} 字 ≈ {m:.1f} 分钟 [{flag}] 待找素材 {todo}")
    # 「画面」里的 PPTn 必须等于实际页号(录屏页也占一页)
    for k, s in enumerate(c.SEG, 1):
        for x in re.findall(r"PPT(\d+)", s[4]):
            if int(x) != k:
                print(f"  ⚠️ {no} 第 {k} 页「{s[1]}」画面写的是 PPT{x},应为 PPT{k}")
    return n


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["all"]:
        args = sorted(x for x in os.listdir(HERE) if re.fullmatch(r"\d\d", x))
    import _delivery
    skipped = False
    for a in args:
        try:
            build(a)
        except _delivery.ProtectedDeckError as exc:
            print(f"跳过：{exc}")
            skipped = True
    if skipped and sys.argv[1:] != ["all"]:
        sys.exit(2)
