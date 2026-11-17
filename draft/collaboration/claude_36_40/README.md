# Claude 云端协作：第36—40讲素材与录屏代码候选

日期：2026-11-17 · 分支：`claude/optimistic-sagan-l44esv`（基于 37c7f42）

## 完成内容

1. **两项主素材候选**（待审）：
   - 36-P4 连续帧翻页动画 GIF：放慢讲解与快速连播分开，标称 30 帧/秒只作概念说明，GIF 速度不标为实测。
   - 37-P4 读→处理→显示循环图（1280×720）：ret=False 与 q 退出都进入释放，文件结束与摄像头读取失败分开说明；精确代码另附。
2. **10 个实操页代码候选**：`recording_candidates/36—40`，共用核心放在 `common/`。默认读合成测试视频，只有显式 `--camera` 才打开摄像头。两个独立环境（含 NumPy 1.26.4）的无界面核对全部通过。40 讲用真实 XVID 写入再解码核对。
3. **脚本差异与勘误建议**：10 条，见 [review.md](review.md) 第三节，包括 DSHOW 不能带到文件、两种 FPS 平滑、秒级命名会覆盖、REC 不进视频等。
4. 出处见 [sources.json](sources.json)。运行记录与完整 SHA256 见 `previews/run_log.txt`；录屏核对日志见 `previews/recording_checks/run_log_main.txt`、`run_log_compat.txt`。

## 待审文件

| 页 | 主文件 | 审阅辅助 |
|---|---|---|
| 36-P4 | `previews/36/36-p4-anim-连续帧翻页动画_候选.gif` | `36-p4-anim-关键帧拼图_审阅用.png` |
| 37-P4 | `previews/37/37-p4-diag-读处理显示循环图_课堂版_候选.png` | `37-p4-ref-循环结构精确代码_附件.png`（不进课件） |
| 录屏候选 | `recording_candidates/`（见该目录 README） | `previews/recording_checks/NN/` |

## 未做 / 不能宣称

- 没有修改 content.py、公共生成器、素材登记总表、交付台账或 out，没有生成或重建 PPT，没有在公共目录生成录屏工程。
- 没有连接摄像头，没有测试真实窗口和键盘，也没有人工播放录像。云端只做了技术解码。
- 39 讲的计时数值只代表本云端环境，不代表用户电脑。
- 36-P2 产线视频、36-P8 Windows 截图仍缺，没有用合成内容冒充。
- 全部候选待审。

## 运行说明（独立环境）

```bash
python -m venv .venv-claude && . .venv-claude/bin/activate
pip install opencv-python-headless==4.11.0.86 numpy pillow
python draft/collaboration/claude_36_40/scripts/run_all.py
```

设置 `COMPAT_PYTHON=<另一个解释器>` 会再跑一遍录屏核对，并比较两次输出图的哈希。
