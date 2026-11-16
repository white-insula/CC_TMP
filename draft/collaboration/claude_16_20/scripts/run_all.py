# -*- coding: utf-8 -*-
"""一次生成第16—20讲全部候选预览，并把运行环境与输出写入 previews/run_log.txt。
用法（任意目录）：python draft/collaboration/claude_16_20/scripts/run_all.py
依赖：opencv-python(-headless) 4.11、numpy、Pillow、scikit-image（提供 CC0/公有领域替身图）、中文字体。
"""
import contextlib
import datetime
import hashlib
import io
import os
import platform
import runpy
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)
SCRIPTS = ["l16_crop_resize.py", "l17_flip_rotate.py", "l18_draw_text.py", "l19_brightness.py", "l20_filter.py"]


def main():
    import cv2, numpy, PIL, skimage
    from _common import FONT_PATH, PREV
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print("运行时间(UTC):", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
        print("Python", platform.python_version(), "|", platform.platform())
        print("opencv", cv2.__version__, "| numpy", numpy.__version__, "| Pillow", PIL.__version__, "| scikit-image", skimage.__version__)
        print("中文字体:", FONT_PATH)
        for s in SCRIPTS:
            runpy.run_path(os.path.join(HERE, s), run_name="__main__")
        print("\n文件 SHA256（前16位）:")
        for root, _, files in sorted(os.walk(PREV)):
            for f in sorted(files):
                if f == "run_log.txt":
                    continue
                p = os.path.join(root, f)
                h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
                print(f"  {os.path.relpath(p, PREV)}  {os.path.getsize(p)} B  {h}")
    log = buf.getvalue()
    sys.stdout.write(log)
    with open(os.path.join(PREV, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write(log)


if __name__ == "__main__":
    main()
