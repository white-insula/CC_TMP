# -*- coding: utf-8 -*-
"""由各节素材需求汇总未完成页面（⬜ 缺素材、⚠️ 动态素材未完成）。"""
import os, re, datetime
import _lib
HERE = os.path.dirname(os.path.abspath(__file__))
mods, total = {}, 0
for no in sorted(x for x in os.listdir(HERE) if re.fullmatch(r"\d\d", x)):
    p = os.path.join(HERE, no, "素材需求.md")
    if not os.path.exists(p):
        continue
    for line in open(p, encoding="utf-8"):
        if "⬜" in line or "⚠️" in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            mods.setdefault(_lib.load(no).MODULE, []).append(f"| {no} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
            total += 1
out = [f"# 全课素材需求汇总\n\n**共 {total} 条待找。**",
       f"> 由 `_todo_summary.py` 从各节 `NN/素材需求.md` 汇总({datetime.date.today()})。下表包含 ⬜ 待找/待做及 ⚠️ 静态图已有但动态素材待做；数量按页面计，含录屏需求，不代表需要重新找同等数量的图片。",
       "> 静态配图按原流程登记。录屏由用户确认已录制后记入 `manual/录屏完成登记.json`，只更新相关素材清单并重跑本汇总，不检查视频、不触发PPT页替换。\n"]
for m, rows in mods.items():
    out += [f"## {m}（{len(rows)} 条）\n", "| 节 | 页 | 标题 | 画面要求 | 状态 |", "|---|---|---|---|---|", *rows, ""]
open(os.path.join(HERE, "素材需求汇总.md"), "w", encoding="utf-8").write("\n".join(out))
print("total", total)
