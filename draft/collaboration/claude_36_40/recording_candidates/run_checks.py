# -*- coding: utf-8 -*-
"""一次跑完第 36—40 讲录屏候选的无界面核对（不打开摄像头，不弹窗口）。

步骤：生成合成测试视频 → 全部 .py 语法检查 → 逐讲运行 check_headless.py（结果写到 --outdir/NN/）。
GUI 入口（p5_/p6_/p7_ 开头）只做语法检查：真实窗口、键盘、摄像头、录屏都需要在本机操作；本批不用假窗口冒充交互验证。
用法：python run_checks.py --outdir 输出目录 --log 日志文件
"""
import argparse
import glob
import os
import platform
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LESSONS = ["36", "37", "38", "39", "40"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(HERE, "check_out"))
    ap.add_argument("--log", default=os.path.join(HERE, "check_out", "run_log.txt"))
    args = ap.parse_args()
    import cv2
    import numpy
    lines = [f"Python {platform.python_version()} | numpy {numpy.__version__} | opencv {cv2.__version__}"]
    r = subprocess.run([sys.executable, "make_synthetic_video.py"], cwd=HERE, capture_output=True, text=True)
    lines.append("[生成合成测试视频]\n" + r.stdout.rstrip())
    if r.returncode:
        raise SystemExit(r.stderr)
    files = sorted(glob.glob(os.path.join(HERE, "*", "*.py")) + glob.glob(os.path.join(HERE, "*.py")))
    for f in files:
        compile(open(f, encoding="utf-8").read(), f, "exec")
    gui = [os.path.relpath(f, HERE) for f in files if os.path.basename(f).startswith(("p5_", "p6_", "p7_"))]
    lines.append(f"[语法检查] {len(files)} 个 .py 全部通过；其中 GUI 入口 {len(gui)} 个只做语法检查、未运行：{gui}")
    ok = True
    for n in LESSONS:
        r = subprocess.run([sys.executable, "check_headless.py", "--outdir", os.path.join(args.outdir, n)],
                           cwd=os.path.join(HERE, n), capture_output=True, text=True)
        out = r.stdout.rstrip().replace(os.path.abspath(args.outdir) + os.sep, "")
        lines.append(f"[{n}] 退出码 {r.returncode}\n" + out + ("\n" + r.stderr.rstrip() if r.returncode else ""))
        ok &= r.returncode == 0
    lines.append("全部通过" if ok else "有失败项")
    os.makedirs(os.path.dirname(os.path.abspath(args.log)), exist_ok=True)
    with open(args.log, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
