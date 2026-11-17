# -*- coding: utf-8 -*-
"""一次生成第 36—40 讲全部候选预览，并跑录屏候选的无界面核对，写运行记录与完整 SHA256。

用法（任意目录，独立环境）：python draft/collaboration/claude_36_40/scripts/run_all.py
可选：设置环境变量 COMPAT_PYTHON=另一个解释器（如 Python 3.11 + NumPy 1.26 + OpenCV 4.11），
      会用它再跑一遍录屏核对，并比较两次输出图的哈希是否一致。
"""
import contextlib
import datetime
import hashlib
import io
import os
import platform
import runpy
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REC = os.path.join(ROOT, "recording_candidates")
sys.path.insert(0, HERE)
os.chdir(HERE)
SCRIPTS = ["l36_flipbook_gif.py", "l37_loop_diag.py"]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def tree_hashes(base):
    out = {}
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", "check_out")]
        for f in files:
            if f.endswith((".pyc",)) or f.startswith("run_log"):
                continue
            p = os.path.join(root, f)
            out[os.path.relpath(p, ROOT)] = (os.path.getsize(p), sha(p))
    return out


def run_checks(python, outdir, log):
    r = subprocess.run([python, os.path.join(REC, "run_checks.py"), "--outdir", outdir, "--log", log],
                       capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def main():
    import cv2, numpy, PIL
    from _common import FONT_PATH, PREV
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print("运行时间(UTC):", datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
        print("Python", platform.python_version(), "|", platform.platform())
        print("opencv", cv2.__version__, "| numpy", numpy.__version__, "| Pillow", PIL.__version__)
        print("中文字体:", FONT_PATH)
        for s in SCRIPTS:
            runpy.run_path(os.path.join(HERE, s), run_name="__main__")

        print("\n[录屏候选无界面核对] 主环境")
        chk = os.path.join(PREV, "recording_checks")
        code, out, err = run_checks(sys.executable, chk, os.path.join(chk, "run_log_main.txt"))
        print(f"  退出码 {code}；详细输出见 previews/recording_checks/run_log_main.txt")
        if code:
            print(err)
        compat = os.environ.get("COMPAT_PYTHON")
        if compat:
            print("\n[录屏候选无界面核对] 兼容环境", compat)
            tmp = tempfile.mkdtemp()
            code2, out2, err2 = run_checks(compat, tmp, os.path.join(chk, "run_log_compat.txt"))
            print(f"  退出码 {code2}；详细输出见 previews/recording_checks/run_log_compat.txt")
            same, diff = 0, []
            for root, _, files in os.walk(tmp):
                for f in files:
                    if not f.endswith(".png"):
                        continue
                    a = os.path.join(root, f)
                    b = os.path.join(chk, os.path.relpath(a, tmp))
                    if os.path.exists(b) and sha(a) == sha(b):
                        same += 1
                    else:
                        diff.append(os.path.relpath(a, tmp))
            print(f"  两个环境输出图哈希一致 {same} 个，不一致 {len(diff)} 个 {diff}")

        print("\n文件 SHA256（完整）:")
        for k, (size, h) in sorted({**tree_hashes(PREV), **tree_hashes(REC)}.items()):
            print(f"  {k}  {size} B  {h}")
    log = buf.getvalue()
    sys.stdout.write(log)
    with open(os.path.join(PREV, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write(log)


if __name__ == "__main__":
    main()
