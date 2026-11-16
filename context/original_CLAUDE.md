# 《机器视觉技术应用实践》· 数字教材项目

双高任务 **5-2-7-7**,交付一部机器视觉数字教材(面向职高 + 成人教育)。
截止:**2026 年 11 月**。详见 `plan/PLAN.md`。

## 目录结构(输入 / 规则 / 过程 / 输出)

| 目录 | 角色 | 内容 |
|---|---|---|
| `in/` | 输入 | 学校下发的原始材料(只读,不改) |
| `plan/` | 规则 | `PLAN.md` 蓝图决策、`OUTLINE.md` 章节骨架、`NAMING.md` 命名规范 |
| `draft/` | 过程 | 在写的章节初稿(`chapters/`)、在做的资源(`resources/`) |
| `out/` | 输出 | 章节定稿(`chapters/`)、月度提报/佐证(`reports/`) |

## 从哪读起

1. `plan/PLAN.md` —— 项目蓝图、硬约束、进度日志(**resume 时先读这个**)
2. `plan/OUTLINE.md` —— 10 章内容骨架(v2.0,与 87 节微课对齐)
3. `plan/NAMING.md` —— 文件结构与命名规范
4. `plan/METHOD.md` —— 每章编写检查单(动笔前先过)
5. `out/chapters/` —— 章节定稿(当前:**`ch02` 样章已定稿 2026-11-10**,检查记录见 `out/reports/ch02_finalize_check.md`;后续各章以它为模板)

## 常用工具

- `tools/collect_figures.py chNN [--to 目录]` —— 从在线课配图(`draft/online_course/NN/img/`)复制成教材插图,单一来源防漂移
- `tools/build_reading_html.py --md … --out …` —— Markdown → 单文件离线阅读页(代码高亮、插图内嵌)
- 在线课:`draft/online_course/_visuals/run.py NN` 生成配图 → `_lib.py NN` 生成 PPT+脚本 → `_todo_summary.py` 汇总待找素材 → `_merge.py` 脚本汇总 docx
- **手工素材入口 `draft/online_course/manual/`**:找的图/截图/录屏/动画按 `NN-pP-类型-简述` 命名放 `manual/NN/`,登记 `manual/素材登记.csv`,审核「通过」才自动进 PPT;**不手改 PPT**(说明 `manual/README.md`)
- **⭐ 课程脚本(`NN/content.py`)是一切工作的起点:脚本一改,下游全部资源(docx/pptx/汇总/PPT_collection+zip/配图/教材正文与插图/阅读页)都要查、都要更新;改完跑 `python draft/online_course/_sync_check.py`**(详见 `plan/COURSE_SCRIPTS.md` 一)
