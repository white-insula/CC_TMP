# -*- coding: utf-8 -*-
"""把 87 节 content.py 合成一个 Word 文件,方便连续阅读与批注。
用法:python _merge.py   → 生成 全部微课脚本汇总.docx
结构:封面说明 → 目录(打开时自动更新) → 总览表 → 按模块分章(标题1),每节一个标题2 + 镜头表。
"""
import os, re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.section import WD_ORIENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import _lib

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "全部微课脚本汇总.docx")


def set_cn_font(style, size=None, name="宋体"):
    style.font.name = name
    style.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), name)
    if size:
        style.font.size = Pt(size)


def add_toc(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    for tag, text in (("begin", None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ("separate", None), ("end", None)):
        if tag:
            el = OxmlElement("w:fldChar"); el.set(qn("w:fldCharType"), tag); run._r.append(el)
            if tag == "separate":
                t = OxmlElement("w:t"); t.text = "（目录：打开文件时选“是”自动更新；或右键此处 → 更新域）"; run._r.append(t)
        else:
            el = OxmlElement("w:instrText"); el.set(qn("xml:space"), "preserve"); el.text = text; run._r.append(el)
    # 打开时提示更新域
    settings = doc.settings.element
    uf = OxmlElement("w:updateFields"); uf.set(qn("w:val"), "true"); settings.append(uf)


def narr_cell(cell, text):
    _lib._narr_cell(cell, text)


RED = RGBColor(0xC0, 0, 0)
SKIP_IN_BASELINE = ("模块九", "模块十")   # 硬件/实测未完成,基线版暂不收录


def red_line(cell, text):
    r = cell.add_paragraph().add_run(text); r.bold = True; r.font.color.rgb = RED


def main(baseline=False, final60=False):
    nos = sorted(d for d in os.listdir(HERE) if re.fullmatch(r"\d\d", d))
    lessons = []
    for no in nos:
        if final60 and not 1 <= int(no) <= 60:
            continue
        c = _lib.load(no)
        if baseline and c.MODULE.startswith(SKIP_IN_BASELINE):
            continue
        n = sum(len(re.sub(r"\s", "", s[3])) for s in c.SEG if s[3])
        lessons.append((c, n, n / _lib.RATE))
    # 待确认项:content.py 里的 PENDING = {页号: "说明"}
    pend = [(c.NO, k, v) for c, _, _ in lessons for k, v in sorted(getattr(c, "PENDING", {}).items())]
    out = OUT.replace(".docx", "_v1基线.docx") if baseline else OUT
    if final60:
        from datetime import date
        assert [c.NO for c, _, _ in lessons] == [f"{n:02}" for n in range(1, 61)]
        assert not pend, "前 60 讲仍有 PENDING，不能生成脚本定稿归档"
        out = os.path.join(HERE, "..", "..", "out", "reports",
                           f"micro_lessons_01_60_script_final_{date.today().isoformat()}.docx")
        os.makedirs(os.path.dirname(out), exist_ok=True)

    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = sec.page_height, sec.page_width
    for m in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, m, Cm(1.8))
    set_cn_font(doc.styles["Normal"], 10.5)
    for s, size in (("Title", 22), ("Heading 1", 16), ("Heading 2", 13)):
        set_cn_font(doc.styles[s], size, "黑体")
        doc.styles[s].font.color.rgb = RGBColor(0, 0, 0)

    doc.add_paragraph(
        f"{_lib.COURSE}在线课 · " +
        ("第 01–60 讲脚本定稿归档" if final60 else "全部微课脚本汇总" + ("（v1 基线版）" if baseline else "")),
        style="Title")
    total = sum(x[2] for x in lessons)
    doc.add_paragraph(
        f"共 {len(lessons)} 节微课，估算总时长约 {total:.0f} 分钟（按 TTS 约 {_lib.RATE} 字/分钟估算）。"
        "每节为一个镜头表：序号 / 镜头 / 解说词 / 画面；开场与结尾统一句加粗标红。")
    if final60:
        doc.add_paragraph(
            f"归档版本：v1 · {date.today().isoformat()}。收录模块一至七，第 01–60 讲；不收录第 61–87 讲。"
            "本次完成脚本文字、技术表述与规划口径的静态核对；未新增模拟或录屏验证。"
            "PPT、图片、截图与录屏另行制作和同步，不作为本次脚本归档的完成条件。"
            "各讲 content.py 为源文件，后续修订应同步源文件并另存新版归档，不直接改写本归档。")
    elif baseline:
        doc.add_paragraph(
            "本版为 v1 基线：各节代码已在课程统一环境（Python 3.11 + opencv-contrib-python 4.11.0.86 + "
            "mediapipe 0.10.21 + ultralytics）中核对或实跑；实时摄像头类演示（读帧、实时处理、帧率、"
            "人脸检测、人脸网格、姿态、YOLO 实时检测）在笔记本摄像头上实跑，手部关键点用录制视频验证。"
            "本版收录模块一至八（第 01–69 讲）。模块九（第 70–79 讲，海康设备）因硬件未到位、"
            "模块十（第 80–87 讲，树莓派）因个别步骤尚待实测，本版均不收录，完成实测后补充。"
            + (f"无法在本版确认的内容共 {len(pend)} 处，已在对应镜头的“画面”栏用红字【待确认】标出。" if pend
               else "本版没有待确认的内容。"))
    else:
        doc.add_paragraph(
            "本文件由各节 content.py 自动汇总生成，仅供审阅批注；修改意见请注明“第几节、第几个镜头”，"
            "改动落在 content.py 后重新生成，请勿直接在本文件中定稿。")
    if pend:
        doc.add_heading("待确认清单", level=1)
        t = doc.add_table(rows=1, cols=3); t.style = "Table Grid"
        for cell, h in zip(t.rows[0].cells, ["节号", "镜头", "待确认内容"]):
            cell.text = ""; r = cell.paragraphs[0].add_run(h); r.bold = True
        for no, k, v in pend:
            row = t.add_row().cells
            row[0].text = no; row[1].text = str(k); row[2].text = v
        for row in t.rows:
            for cell, w in zip(row.cells, (2, 2, 20)):
                cell.width = Cm(w)

    doc.add_heading("目录", level=1)
    add_toc(doc)
    doc.add_page_break()

    # 总览表
    doc.add_heading("总览", level=1)
    t = doc.add_table(rows=1, cols=5); t.style = "Table Grid"
    for cell, h in zip(t.rows[0].cells, ["节号", "模块", "微课名称", "镜头数", "时长估算"]):
        cell.text = ""; r = cell.paragraphs[0].add_run(h); r.bold = True
    for c, n, m in lessons:
        row = t.add_row().cells
        row[0].text = c.NO; row[1].text = c.MODULE; row[2].text = c.NAME
        row[3].text = str(len(c.SEG)); row[4].text = f"{m:.1f} 分钟"
    for row in t.rows:
        for cell, w in zip(row.cells, (1.5, 6, 10, 2, 2.5)):
            cell.width = Cm(w)

    cur = None
    for c, n, m in lessons:
        if c.MODULE != cur:
            cur = c.MODULE
            doc.add_page_break()
            doc.add_heading(cur, level=1)
        doc.add_heading(f"{c.NO}  {c.NAME}", level=2)
        p = doc.add_paragraph(f"镜头 {len(c.SEG)} 个 · 解说 {n} 字 · 约 {m:.1f} 分钟")
        cp = getattr(c, "PENDING", {})
        if cp:
            r = p.add_run(f"　本节有 {len(cp)} 处待确认（红字标出）"); r.bold = True; r.font.color.rgb = RED
        t = doc.add_table(rows=1, cols=4); t.style = "Table Grid"
        for cell, h in zip(t.rows[0].cells, ["序号", "镜头", "解说词", "画面"]):
            cell.text = ""; r = cell.paragraphs[0].add_run(h); r.bold = True
        for i, (shot, title, bullets, narr, screen) in enumerate(c.SEG, 1):
            row = t.add_row().cells
            row[0].text = str(i)
            row[1].text = shot + (f"\n【{title}】" if title and bullets is not None else "")
            narr_cell(row[2], narr)
            row[3].text = screen
            if i in cp:
                red_line(row[3], "【待确认】" + cp[i])
        for row in t.rows:
            for cell, w in zip(row.cells, (1.2, 3.0, 15.0, 6.8)):
                cell.width = Cm(w)
        doc.add_paragraph()

    doc.save(out)
    print("->", out, f"({len(lessons)} 节, 约 {total:.0f} 分钟, 待确认 {len(pend)} 处)")


if __name__ == "__main__":
    import sys
    if "--baseline" in sys.argv and "--final60" in sys.argv:
        raise SystemExit("--baseline 与 --final60 不能同时使用")
    main(baseline="--baseline" in sys.argv, final60="--final60" in sys.argv)
