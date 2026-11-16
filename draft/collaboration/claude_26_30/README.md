# Claude 云端协作：第26—30讲素材与录屏代码候选

日期：2026-11-16 · 分支：`claude/optimistic-sagan-l44esv`（基于 67a9c43）

## 完成内容

1. **三项主缺口候选**（待审）：
   - 26-P4 HSV 色轮/浓淡/明暗分步 GIF（uint8：H 0—179，S/V 0—255；红在两端；S/V 过低时 H 不可靠）
   - 30-P4 同一合成轮廓在 0.005/0.02/0.08 × 周长下的近似 GIF（实测顶点 15/8/4）
   - 30-P5 形状判断流程图课堂版（1280×720）＋ 规则实测核对附件
2. **10 个录屏页代码候选**：`recording_candidates/26—30`，GUI 入口供本机录屏，`check_headless.py` 无窗口核对，参数与脚本一致；两个独立环境（含 NumPy 1.26.4）全部通过。
3. **核对发现**：现有配图代码与正式参数的差异，见 [review.md](review.md) 第三节（绿色范围、29 讲中心点定义、30 讲判断规则、27 讲输入图等）。
4. 出处见 [sources.json](sources.json)；运行记录与完整 SHA256 见 `previews/run_log.txt`，录屏核对日志见 `previews/recording_checks/run_log_main.txt`、`run_log_compat.txt`。

## 待审文件

| 页 | 主文件 | 审阅辅助 |
|---|---|---|
| 26-P4 | `previews/26/26-p4-anim-HSV色轮浓淡明暗_候选.gif` | `26-p4-anim-关键帧拼图_审阅用.png` |
| 30-P4 | `previews/30/30-p4-anim-原始轮廓与近似多边形_候选.gif` | `30-p4-anim-关键帧拼图_审阅用.png` |
| 30-P5 | `previews/30/30-p5-diag-形状判断流程图_课堂版_候选.png`（建议上课件） | `30-p5-ref-形状判断规则实测_核对附件.png`（不进课件） |
| 录屏候选 | `recording_candidates/`（见该目录 README） | `previews/recording_checks/NN/*.png` |

## 未做的事

- 没有修改 content.py、公共生成器、素材登记总表、交付台账或 out，没有生成或重建 PPT。
- 没有运行 `_build_m4.py`，没有写共享 recording_kit/26—35。
- 没有把候选标为“通过”；代码候选和云端核对不等于录屏完成。
- 没有查看任何现有图片或录屏；没有在本机教学环境安装依赖。
- 没有给每个录屏页做替身拼图。

## 仍缺的输入

- [PI] shapes.png（26、28、29、30 讲录屏）
- 彩色积木照片（27、29 讲录屏；`_build_m4.py` 现用 fruit.jpg，与脚本不符，需用户决定）
- 现有 img/26—30、PPTX、正式归档 Word/PDF

## 运行说明（独立环境）

```bash
python -m venv .venv-claude && . .venv-claude/bin/activate
pip install opencv-python-headless==4.11.0.86 numpy pillow
python draft/collaboration/claude_26_30/scripts/run_all.py
```

设置 `COMPAT_PYTHON=<另一个解释器>` 会用它再跑一遍录屏核对，并比较两次输出图的哈希。
