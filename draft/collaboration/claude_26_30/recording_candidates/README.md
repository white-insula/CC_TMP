# 第26—30讲 录屏工程候选

本目录是**候选代码**，供本机准备录屏使用；不是正式 recording_kit，也不代表已经录屏。

## 目录

```
recording_candidates/
├── make_synthetic_inputs.py   生成合成输入（文件名带 synthetic）
├── run_checks.py              无界面核对：生成输入 → 语法检查 → 各讲 check_headless → GUI 替身冒烟
├── gui_smoke.py               GUI 替身冒烟（假窗口函数，只查代码路径，不是界面测试）
├── 26/ core.py · p7_hsv_click.py · p8_hsv_trackbar.py · check_headless.py · hsv_shapes_synthetic.png
├── 27/ core.py · p7_extract_green.py · p8_extract_red.py · check_headless.py · blocks_synthetic.png
├── 28/ core.py · p6_contours.py · p7_modes.py · check_headless.py · shapes_synthetic.png · washers_synthetic.png
├── 29/ core.py · p6_features.py · p7_red_boxes.py · check_headless.py · shapes_dust_synthetic.png · blocks_synthetic.png
└── 30/ core.py · p6_shapes.py · p7_eps.py · check_headless.py · shapes_synthetic.png
```

## 本机录屏时怎么用

进入对应讲次目录运行 GUI 入口；默认读合成图，换真实图片用 `--input`：

```powershell
Set-Location draft/collaboration/claude_26_30/recording_candidates/27
python p7_extract_green.py --input 积木照片.jpg
```

- 26-P7：左键点击图片打印 `hsv[y, x]`，按任意键退出。
- 26-P8：拖动 6 个滑动条，按 q 退出并打印范围。
- 30-P7：依次运行 `python p7_eps.py --eps 0.08`、`--eps 0.005`、`--eps 0.02`。
- 其余程序显示窗口，按任意键退出。

GUI 入口里的核心几行与正式脚本画面要求一致，可直接作为录屏时展示或手敲的代码；`core.py` 中是同样的写法，供无界面核对共用。

## 环境

- 兼容课程环境 OpenCV 4.11.0；只用 NumPy 1.x 也有的接口（已在 NumPy 1.26.4 实测）。
- **不要**为运行这些程序在本机已锁定的教学环境里安装或升级任何包。云端核对使用的是独立环境。

## 核对命令（无窗口）

```bash
python run_checks.py --outdir check_out --log check_out/run_log.txt
```

云端已在 Python 3.13 + NumPy 2.5.3 + OpenCV 4.11.0 与 Python 3.11 + NumPy 1.26.4 + OpenCV 4.11.0 两个独立环境各跑一遍，全部通过；结果见 `../previews/recording_checks/`。
