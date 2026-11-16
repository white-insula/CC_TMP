# 录屏演示代码目录与准备进度

核查日期：2026-11-13。本目录用于准备微课演示代码、输入素材和预演结果；文件存在不代表已按最新脚本验收或正式录制。

## 目录用途

| 路径 | 用途 |
|---|---|
| `NN/` | 对应讲次的演示程序和输入图片；程序头部通常注明页码、操作及预期现象 |
| `assets/` | 共用输入图片、测试视频等素材，不是依赖安装包 |
| `_out/NN/` | 自动预演保存的结果图；属于历史运行结果，不是正式录屏或当前验收证明 |
| `_autotest.py` | 自动预演器：模拟按键、保存窗口画面，可用测试视频代替摄像头；正式录屏不使用它 |
| `_build_m3.py` | 16–25 讲工程生成器；已有逐讲代码，重新运行前注意可能覆盖修改 |
| `_build_m4.py` | 26–35 讲工程生成器；对应逐讲目录尚未生成，且依赖脚本中指定的外部答题卡项目路径 |
| `_verify_cards.py` | 34/35 讲答题卡结果比对工具，需要外部学生项目与参考结果 |

## 当前代码准备范围

已有 **16 个讲次目录、34 个逐讲 Python 文件**（不含根目录的工具脚本）。

| 讲次 | 现有程序 |
|---|---|
| 07 | `first.py`、`change.py` |
| 11 | `numpy_image.py`、`colors.py` |
| 12 | `read_check.py`、`read_fail.py`、`save.py` |
| 13 | `identity.py` |
| 14 | `blue_block.py`、`red_block.py`、`center.py` |
| 15 | `split.py`、`merge.py`、`gray.py` |
| 16 | `crop.py`、`resize.py` |
| 17 | `flip_rotate.py`、`rotate30.py` |
| 18 | `draw.py`、`label.py` |
| 19 | `overflow.py`、`scale_abs.py` |
| 20 | `denoise.py`、`bilateral.py`、`cartoon.py` |
| 21 | `threshold.py`、`adaptive.py` |
| 22 | `erode_dilate.py`、`open_close.py` |
| 23 | `canny.py`、`trackbar.py` |
| 24 | `histogram.py`、`equalize.py` |
| 25 | `warp.py` |

- **26–35 讲**：只有工程生成器，待检查外部依赖、生成逐讲工程，再按归档脚本验证。
- **36–60 讲**：本目录尚无逐讲工程；不据此判断其他位置是否有零散示例。
- **01–06、08–10 讲**：本目录无逐讲程序；理论画面、安装操作不必强行编写 Python。项目根目录 `VS_test/` 另有第 06/07 讲测试文件。

## 如何检索和运行

先按讲号进入目录，再看 `.py` 顶部注释，确认对应页码与输入文件。直接演示时从该讲目录运行，避免相对路径读图失败。例如，从项目根目录执行：

```powershell
Set-Location draft/resources/recording_kit/07
python first.py
```

自动预演则在 `recording_kit/` 下运行：

```powershell
python _autotest.py 07/first.py
```

后续每讲按“代码已准备 → 对照归档复核 → 预演/实测 → 正式录制 → 审核登记”推进。总待办见项目根目录 `draft/production_01_60_todo.md`；01–60 的正式依据是 `out/reports/micro_lessons_01_60_script_final_2026-11-12.docx`。

本目录没有课程依赖离线包。项目历史记录中的 `~/wheelhouse/` 位于树莓派，不能当作 Windows 安装包使用。
