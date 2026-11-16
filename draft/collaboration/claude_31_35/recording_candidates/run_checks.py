# -*- coding: utf-8 -*-
"""一次跑完第 31—35 讲录屏候选的无界面核对（不打开任何窗口）。

步骤：重新生成 *_synthetic.png → 编译检查全部 .py（含 GUI 入口，只检查语法、不运行）→
逐讲运行 check_headless.py，结果图写到 --outdir/NN/，数值输出写到 --log。
用法：python run_checks.py --outdir 输出目录 --log 日志文件
GUI 程序（p5_/p6_/p7_/p8_ 开头）的窗口、摄像头、手机扫码需要在本机实际操作；本脚本只做语法检查和替身冒烟。
"""
import argparse
import glob
import os
import platform
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LESSONS = ["31", "32", "33", "34", "35"]
GENERATED = ["31/template_synthetic.png", "32/part.png", "35/成绩单_synthetic.xlsx"]   # GUI 冒烟时由 p6/p5 生成的文件，结束后删除


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=os.path.join(HERE, "check_out"))
    ap.add_argument("--log", default=os.path.join(HERE, "check_out", "run_log.txt"))
    args = ap.parse_args()
    import cv2
    import numpy
    lines = [f"Python {platform.python_version()} | numpy {numpy.__version__} | opencv {cv2.__version__}"]
    r = subprocess.run([sys.executable, "make_synthetic_inputs.py"], cwd=HERE, capture_output=True, text=True)
    lines.append("[生成合成输入]\n" + r.stdout.rstrip())
    if r.returncode:
        raise SystemExit(r.stderr)
    r = subprocess.run([sys.executable, "make_synthetic_cards.py"], cwd=os.path.join(HERE, "34"), capture_output=True, text=True)
    lines.append(r.stdout.rstrip())
    if r.returncode:
        raise SystemExit(r.stderr)
    for f in sorted(glob.glob(os.path.join(HERE, "*", "*.py")) + glob.glob(os.path.join(HERE, "*.py"))):
        compile(open(f, encoding="utf-8").read(), f, "exec")       # 只检查语法，不写 .pyc
    lines.append("[语法检查] 全部 .py 编译通过（GUI 入口只做语法检查，未运行）")
    ok = True
    for n in LESSONS:
        od = os.path.join(args.outdir, n)
        r = subprocess.run([sys.executable, "check_headless.py", "--outdir", od], cwd=os.path.join(HERE, n),
                           capture_output=True, text=True)
        lines.append(f"[{n}] 退出码 {r.returncode}\n" + r.stdout.rstrip() + ("\n" + r.stderr.rstrip() if r.returncode else ""))
        ok &= r.returncode == 0
    # GUI 入口替身冒烟：假窗口函数，只确认代码路径不报错（不是界面测试）
    for f in sorted(glob.glob(os.path.join(HERE, "*", "p[5678]_*.py"))):
        if os.path.basename(f) == "p7_scan_cam.py":
            lines.append("[GUI 替身冒烟] 32/p7_scan_cam.py 跳过：需要摄像头，云端不连接摄像头")
            continue
        r = subprocess.run([sys.executable, os.path.join(HERE, "gui_smoke.py"), f], cwd=HERE, capture_output=True, text=True)
        rel = os.path.relpath(f, HERE)
        lines.append(f"[GUI 替身冒烟] {rel} 退出码 {r.returncode}\n" + r.stdout.rstrip() + ("\n" + r.stderr.rstrip() if r.returncode else ""))
        ok &= r.returncode == 0
    for g in GENERATED:
        p = os.path.join(HERE, g)
        if os.path.exists(p):
            os.remove(p)
    lines.append("全部通过" if ok else "有失败项")
    os.makedirs(os.path.dirname(os.path.abspath(args.log)), exist_ok=True)
    with open(args.log, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
