# Claude 云端协作：第31—35讲素材与录屏代码候选

日期：2026-11-16 · 分支：`claude/optimistic-sagan-l44esv`（基于 3aeb572）

## 完成内容

1. **四项主缺口候选**（待审）：
   - 31-P4 模板滑动 + 真实 TM_CCOEFF_NORMED 分数图 GIF，附阈值 0.5/0.8/0.95 候选框数核对附件
   - 32-P8 产线扫码追溯流程图（虚构数据；区分 QR / Data Matrix / 一维条码）
   - 33-P4 颜色形状分拣五步流程图（标讲次；颜色循环与轮廓循环分层画出）
   - 35-P4 批量阅卷五步流程图（失败分支不计分、继续下一张）
2. **10 个录屏页代码候选**：`recording_candidates/31—35`，全部能在合成教学样本上运行；34/35 真正读图识别、算分、导出 Excel 并重读核对。
3. **脚本冲突**：33-P7 形状判断（当前代码与 30 讲规则两版并列）、34 讲“黑色小方块”与 2:1 定位块、“超过”与 `>= 100`、35 讲参考代码的列错位与失败行混入，详见 [review.md](review.md) 第二节。
4. 出处见 [sources.json](sources.json)；运行记录与完整 SHA256 见 `previews/run_log.txt`；录屏核对日志见 `previews/recording_checks/run_log_main.txt`、`run_log_compat.txt`。

## 待审文件

| 页 | 主文件 | 审阅辅助 |
|---|---|---|
| 31-P4 | `previews/31/31-p4-anim-模板滑动与分数图_候选.gif` | `31-p4-anim-关键帧拼图_审阅用.png`、`31-p4-ref-阈值框数与变换实测_核对附件.png`（不进课件） |
| 32-P8 | `previews/32/32-p8-diag-产线扫码追溯流程图_课堂版_候选.png` | — |
| 33-P4 | `previews/33/33-p4-diag-颜色形状分拣五步流程图_课堂版_候选.png` | — |
| 35-P4 | `previews/35/35-p4-diag-批量阅卷五步流程图_课堂版_候选.png` | — |
| 录屏候选 | `recording_candidates/`（见该目录 README） | `previews/recording_checks/NN/` |

## 未做 / 不能宣称

- 没有修改 content.py、公共生成器、素材登记总表、交付台账或 out，没有生成或重建 PPT；没有运行 `_build_m4.py`。
- 没有查看任何真实照片、答题卡、视频；没有复现 40/40、3199/3200 或真实成绩。
- 没有测试摄像头、手机扫码或 GUI 交互（替身冒烟不是交互验证）；不登记录屏完成。
- 34-P2 学生毕设视频仍缺，没有制作替代视频。
- 全部候选待审，没有标为“通过”。

## 运行说明（独立环境）

```bash
python -m venv .venv-claude && . .venv-claude/bin/activate
pip install opencv-python-headless==4.11.0.86 numpy pillow qrcode openpyxl
python draft/collaboration/claude_31_35/scripts/run_all.py
```

设置 `COMPAT_PYTHON=<另一个解释器>` 会再跑一遍录屏核对，并比较两次输出图的哈希。
