# Claude 云端协作：第16—20讲素材整理

日期：2026-11-16 · 分支：`claude/optimistic-sagan-l44esv`（基于 6133276）

## 完成内容

1. **逐页盘点**：对照 16—20 讲 `content.py`、`素材需求.md`、`素材登记.csv`、`展示方式确认.json`、`_visuals/m3.py` 与 `recording_kit/16—20`，逐页列出现状、缺项与建议，见 [review.md](review.md)。
2. **补缺候选**（均为待审）：
   - 17-P6 旋转矩阵两步流程图（原 ⬜）
   - 19-P4 公式与 α、β 作用示意（原 ⬜，旧图“需改”）
   - 19-P5 uint8 溢出表盘 250→255→0→4（原 ⬜，旧图“需改”）
   - 20-P5 5×5 邻域平均逐格滑动 GIF（原“动画待做”）
3. **替代/补充候选**：16-P4 ROI 坐标示意、16-P5 resize“宽在前”参数图、20-P2 高增益噪点模拟。
4. **录屏静态参考**：16、17、18、19、20 讲全部 10 个录屏页按脚本代码实跑一遍，记录实际输出（shape、像素值等）。
5. **核对发现**（只提建议，未改原文件）：现有 16_2/16_3/17_3 据代码与脚本参数不一致；20_4 卡通算法与录屏程序不同；19-P6 彩色图溢出会出现怪色；18-P7 汉字问号数量按 UTF-8 字节计；详见 review.md 各页 📝。
6. **出处与许可**：[sources.json](sources.json)。

## 目录

```
claude_16_20/
├── README.md          本文件
├── review.md          逐讲逐页待审清单
├── sources.json       出处、许可、访问日期、不确定性
├── scripts/
│   ├── _common.py     公共工具（字体、拼图、替身图、候选角标）
│   ├── l16_crop_resize.py  l17_flip_rotate.py  l18_draw_text.py
│   ├── l19_brightness.py   l20_filter.py
│   └── run_all.py     一键生成 + 写运行记录
└── previews/
    ├── 16/ 17/ 18/ 19/ 20/   实际生成的 PNG / GIF（共 21 个）
    └── run_log.txt           本次云端运行环境、实测数值、各文件 SHA256
```

文件命名沿用 `NN-p页-类型-简述`，后缀 `_候选` / `_替身图` / `_合成` / `_参考` 标明性质；每张图底部有灰色角注写明“候选”及图源。**接入前请按 manual 规则去掉后缀、改名并在登记表登记。**

## 待用户审核项（建议顺序）

1. 17-P6 流程图、19-P4、19-P5、20-P5 GIF —— 填补现有缺项。
2. 16-P7 / 17-P8 —— 现有静态图与脚本参数不一致，决定是否换用候选或在本机重跑 v16/v17。
3. 16-P4、16-P5、20-P2 —— 现有图可用，候选为可选改进。
4. review.md 中的 📝 勘误建议 —— 是否需要调整解说或录屏输入。

本次**没有**修改原始 content.py、公共生成器（_lib/_ppt/_vis/_visuals 等）、素材登记.csv、交付台账、out，也没有把任何候选标为“通过”。

## 仍需用户提供或本机完成的材料

| 项目 | 用途 | 说明 |
|---|---|---|
| `recording_kit/16—20/cat.jpg`（果盘，豆包 AI 生成） | 全部录屏输入、18-P2/P7 | 未上传；替身图效果不能代表实际录屏画面 |
| `recording_kit/19/dark.jpg` | 19-P7 暗图修复 | 未上传；本次用合成暗图 |
| 教师人像照片 | 20-P7 双边滤波“磨皮”录屏 | bilateral.py 目前用果盘，脚本要求人像 |
| 暗光实拍噪点照片（可选） | 20-P2 | 建议教师自拍，授权最清楚 |
| 现有图片 img/16—20、manual/16—20、PPTX、单讲 Word | 视觉审阅、替换判断 | 未上传，本次**未查看**，所有对现有图的意见来自生成代码 |
| 正式归档 Word/PDF（2026-11-12） | 逐字核对 | 未上传，本次以 content.py 为准 |
| bus.jpg 出处/授权 | 现有多张配图的许可 | 见 sources.json，待核实 |
| 10 个录屏 | 16-P6/P7、17-P7/P8、18-P6/P7、19-P6/P7、20-P6/P7 | 需本机录制；画图软件读坐标、摄像头卡通特效等云端无法完成 |

## 运行说明

以下命令仅用于**独立的新虚拟环境**（如云端或单独 venv）；本机课程环境已锁定，不要在其中安装、升级或替换 OpenCV / NumPy。

```bash
python -m venv .venv-claude && . .venv-claude/bin/activate
pip install opencv-python-headless==4.11.0.86 numpy pillow scikit-image
python draft/collaboration/claude_16_20/scripts/run_all.py
```

- 本机 Windows 运行时 `_common.py` 会优先使用 `C:\Windows\Fonts\msyh.ttc`，字形会与云端预览（文泉驿正黑）不同，版式需再看一遍。
- 只写入 `previews/`，不读写本机 D:/E:/F: 路径，不触碰课程工程。
- 单讲重跑：在 `scripts/` 下运行 `python l17_flip_rotate.py` 等。
- 云端实际运行环境与输出见 `previews/run_log.txt`。

## 返修记录

- 2026-11-16（按 CODEX_REVIEW.md）：19-P5 右侧代码改为实测的二维 uint8 数组写法 `a = np.uint8([[250]])`、`b = np.uint8([[10]])`，`print(a + b) → [[4]]`、`print(cv2.add(a, b)) → [[255]]`，图中数值由脚本实跑结果直接写入；删除原错误示例 `cv2.add(250, 10) → 255`（实测该标量调用返回 float64 `[260, 260, 260, 260]`，已记入 run_log）。其余 20 份预览重新运行后字节一致，未改动。
