# Claude 云端协作：第21—25讲素材候选

日期：2026-11-16 · 分支：`claude/optimistic-sagan-l44esv`（基于 c00df0d；19-P5 返修已先行提交 689835a）

## 完成内容

1. **四项优先缺口全部出候选**（均为待审）：
   - 21-P4 阈值线把渐变条一分为二 GIF（127 等于阈值判黑，经 cv2.threshold 实测）
   - 22-P4 腐蚀/膨胀两路对比 GIF（同一原图分别腐蚀、膨胀，5×5 核，1/3 次）＋静态版
   - 23-P5 Canny 双阈值判定示意图（变化强度≠亮度；相连保留、孤立删除；含合成图实跑 cv2.Canny 核对）
   - 25-P4 四点对四点透视矫正 GIF（与 warp.py 的 src/dst/点序一致，含顺序写错的后果）
2. **可选补充**：24-P5 双峰直方图与 Otsu 山谷（现有图据代码只有四种形状，画面要求五种）。
3. **逐讲盘点**：[review.md](review.md) 列出 21—25 讲每页现状和核对发现。主要是现有配图代码与正式脚本参数不一致：22-P6/P7、23-P6/P7/P8、25-P2/P4/P6/P7。
4. **出处**：[sources.json](sources.json)。本批全部使用合成输入，没有新增外部图片许可。
5. **运行记录**：`previews/run_log.txt`，含运行环境、每项实测数值和全部文件的完整 SHA256。

## 待审文件

| 页 | 主文件 | 审阅辅助 |
|---|---|---|
| 21-P4 | `previews/21/21-p4-anim-阈值线把渐变条一分为二_候选.gif` | `21-p4-anim-关键帧拼图_审阅用.png` |
| 22-P4 | `previews/22/22-p4-anim-腐蚀与膨胀两路对比_候选.gif` | `22-p4-anim-关键帧拼图_审阅用.png`、`22-p4-diag-腐蚀与膨胀两路对比_静态_候选.png` |
| 23-P5 | `previews/23/23-p5-diag-Canny双阈值判定_候选.png` | — |
| 25-P4 | `previews/25/25-p4-anim-四点对四点透视矫正_候选.gif` | `25-p4-anim-关键帧拼图_审阅用.png` |
| 24-P5（可选） | `previews/24/24-p5-diag-双峰直方图与Otsu山谷_补充候选.png` | — |

每张图底部灰条写明“候选”和输入性质（合成）。接入前请按 manual 规则改名并登记；GIF 是否像 08/10 讲那样直接嵌入 PPT，由用户决定。

## 未做的事

- 没有修改 content.py、公共生成器、素材登记总表、交付台账或 out，也没有重建 PPT。
- 没有把任何候选标为“通过”。
- 没有制作 10 个录屏页的替身拼图（按任务要求）。
- 没有查看任何现有图片或录屏。凡涉及现有图的意见，均来自生成代码。

## 仍缺的输入

| 项目 | 影响 |
|---|---|
| 录屏输入：21 page.jpg / page_shadow.jpg；22 text_binary.png / noisy_bin.png / hole_bin.png；23 cat.jpg；24 gray_*.jpg；25 paper.jpg | 录屏实际效果、Otsu 阈值等数值只能本机得到 |
| 现有配图 img/21—25、manual/22—23 及 PPTX | 视觉审阅、决定是否用候选替换 |
| [GA] 学生答题卡授权与身份信息处理 | 21-P2/P8 能否使用 |
| bus.jpg、[PI] paper.jpg / test.mp4 授权 | 22—25 讲现有配图的许可 |
| 24-P4“成绩分布类比”是否需要配图 | 素材需求未列此页，需用户确认 |
| 正式归档 Word/PDF | 逐字核对 |

## 运行说明

只在**独立的新环境**中运行（如云端或单独 venv）；不要在本机已锁定的教学环境里安装、升级或替换 OpenCV / NumPy。

```bash
python -m venv .venv-claude && . .venv-claude/bin/activate
pip install opencv-python-headless==4.11.0.86 numpy pillow
python draft/collaboration/claude_21_25/scripts/run_all.py
```

单项重跑：在 `scripts/` 下运行 `python l21_threshold_gif.py` 等。脚本只写 `previews/`，不读写本机路径。
