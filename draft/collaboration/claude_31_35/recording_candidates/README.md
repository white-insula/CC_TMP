# 第31—35讲 录屏工程候选

本目录是**候选代码**，供本机准备录屏；不是正式 recording_kit，不代表已经录屏。所有默认输入都是**合成教学样本**（文件名带 synthetic）。

## 目录

```
recording_candidates/
├── make_synthetic_inputs.py      31 电路板、33 工件图（及真值）
├── run_checks.py                 无界面核对：生成输入 → 语法检查 → 各讲 check_headless → GUI 替身冒烟
├── gui_smoke.py                  GUI 替身冒烟（假窗口函数，只查代码路径，不是交互测试）
├── 31/ core.py · p6_match_one.py · p7_match_many.py · ext_dedupe.py（扩展，非正式讲解）· check_headless.py
├── 32/ core.py · p5_make_qr.py · p7_read_qr.py · p7_scan_cam.py（摄像头，云端未测）· check_headless.py
├── 33/ core.py · p6_main_loop.py · p7_label_count_current.py（照抄当前脚本）· p7_label_count_rule30_alt.py（备选）· check_headless.py
├── 34/ make_synthetic_cards.py · card_lib.py · p6_locate.py · p8_read_answers.py · check_headless.py · template_synthetic.json · card_synthetic_*.jpg
└── 35/ core.py（复用 ../34/card_lib.py）· p6_batch_score.py · p8_export_excel.py · check_headless.py · cards_synthetic/ · 答案_synthetic.txt
```

## 本机使用

进入讲次目录运行；真实素材用参数替换：

```powershell
Set-Location draft/collaboration/claude_31_35/recording_candidates/31
python p6_match_one.py --input 电路板照片.jpg --crop 120 80 90 60
```

- 31：先运行 p6（会保存模板），再运行 p7。
- 32：先运行 p5 生成 part.png，再运行 p7_read_qr.py；摄像头版 `python p7_scan_cam.py --cam 0`。
- 34/35：真实答题卡必须配合真实模板 `--template 原template.json`；`template_synthetic.json` 只适用于合成卡。
- 需要 `qrcode`（32 讲）和 `openpyxl`（35 讲），按课程统一安装方式在本机准备；不要为这些候选在已锁定的教学环境里升级 OpenCV/NumPy。

## 核对（无窗口）

```bash
python run_checks.py --outdir check_out --log check_out/run_log.txt
```

云端已在 NumPy 2.5.3 与 NumPy 1.26.4（均为 OpenCV 4.11.0）两个独立环境各跑一遍，全部通过；结果见 `../previews/recording_checks/`。
