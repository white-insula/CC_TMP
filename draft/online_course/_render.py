# -*- coding: utf-8 -*-
"""用本机 PowerPoint 把 pptx 每页导出成 PNG,并拼一张缩略总览图,供版式检查。
用法:python _render.py <pptx> <输出目录> [宽度px]
"""
import os, sys, glob
import win32com.client
from PIL import Image


def render(pptx, outdir, width=1280):
    pptx = os.path.abspath(pptx); outdir = os.path.abspath(outdir)
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, "slide*.png")):
        os.remove(f)
    app = win32com.client.Dispatch("PowerPoint.Application")
    pres = app.Presentations.Open(pptx, ReadOnly=True, Untitled=False, WithWindow=False)
    try:
        ratio = pres.PageSetup.SlideHeight / pres.PageSetup.SlideWidth
        files = []
        for i, s in enumerate(pres.Slides, 1):
            f = os.path.join(outdir, f"slide{i:02d}.png")
            s.Export(f, "PNG", width, int(width * ratio))
            files.append(f)
    finally:
        pres.Close()
    # 缩略总览(3 列)
    ims = [Image.open(f) for f in files]
    tw = 420; th = int(tw * ratio); cols = 3; rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (tw + 10) + 10, rows * (th + 10) + 10), "white")
    for k, im in enumerate(ims):
        sheet.paste(im.resize((tw, th)), (10 + k % cols * (tw + 10), 10 + k // cols * (th + 10)))
    sheet.save(os.path.join(outdir, "overview.png"))
    print(len(files), "slides ->", outdir)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1280)
