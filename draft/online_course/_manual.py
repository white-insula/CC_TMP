# -*- coding: utf-8 -*-
"""手工素材(manual/)接入生成流程。人找的图、软件截图、录屏、动画一律走这里,不再手改 PPT。

目录:manual/NN/NN-pP-类型-简述.扩展名     (NN=节号,P=页号,对应 NN/素材需求.md 的那一行)
登记:manual/素材登记.csv                   (每个文件一行;Excel 可直接打开编辑)
类型:photo 找的图 | shot 软件截图 | diag 手工/AI 示意图 | rec 录屏/实拍视频 | anim 动画 | ref 仅参考(永不接入)
状态:待审 | 通过 | 需改 | 仅参考            —— 只有「通过」的才接入
接入:photo/shot/diag → 放进 PPT 第 P 页(同页多张自动拼图);rec/anim → 素材需求标「已就绪」,不进 PPT
冲突:同一页已有程序配图(_visuals)时,程序图优先,并报冲突让人决定
"""
import csv, hashlib, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "manual")
REG = os.path.join(ROOT, "素材登记.csv")
COLS = ["文件", "节", "页", "类型", "来源类型", "出处", "授权", "状态", "图注", "角标", "备注"]
TYPES = {"photo": "找的图", "shot": "软件截图", "diag": "示意图", "rec": "录屏/视频", "anim": "动画", "ref": "仅参考"}
STATES = ["待审", "通过", "需改", "仅参考"]
SOURCES = ["自拍/自录", "网络检索", "AI生成", "软件截图", "教师自制", "待补"]
NAME = re.compile(r"^(\d\d)-p(\d+)-(" + "|".join(TYPES) + r")-(.+)\.([A-Za-z0-9]+)$")
IMG_EXT = {"png", "jpg", "jpeg", "bmp"}
PICTURE_TYPES = {"photo", "shot", "diag"}
MEDIA_TYPES = {"rec", "anim"}


def registry():
    if not os.path.exists(REG):
        return {}
    with open(REG, encoding="utf-8-sig", newline="") as f:
        return {r["文件"].strip(): r for r in csv.DictReader(f) if r.get("文件", "").strip()}


def files():
    """manual/NN/ 下的所有素材文件 → {文件名: 完整路径}"""
    out = {}
    if not os.path.isdir(ROOT):
        return out
    for d in sorted(os.listdir(ROOT)):
        p = os.path.join(ROOT, d)
        if re.fullmatch(r"\d\d", d) and os.path.isdir(p):
            for f in sorted(os.listdir(p)):
                if not f.startswith("."):
                    out[f] = os.path.join(p, f)
    return out


def approved(no):
    """本节审核通过的素材 → {页号: [(类型, 路径, 登记行)]}"""
    reg, fs, out = registry(), files(), {}
    for f, path in fs.items():
        m = NAME.match(f)
        r = reg.get(f)
        if not m or m.group(1) != no or not r or r["状态"].strip() != "通过":
            continue
        out.setdefault(int(m.group(2)), []).append((m.group(3), path, r))
    return out


def fingerprint(no):
    """本节已接入素材的指纹(登记行 + 文件内容),用于判断 PPT 是否需要重新生成。"""
    h = hashlib.md5()
    for page, items in sorted(approved(no).items()):
        for t, path, r in sorted(items, key=lambda x: x[1]):
            h.update(f"{page}|{t}|{os.path.basename(path)}|{r.get('图注', '')}|{r.get('角标', '')}".encode("utf-8"))
            h.update(open(path, "rb").read())
    return h.hexdigest()


def vis_entries(c, here):
    """给 _ppt.vis_of 用:{slide标题: (相对 NN/ 的图片路径, 图注)}。同页多张 → 拼成 NN/img/NN_mP.png。"""
    out = {}
    for page, items in approved(c.NO).items():
        pics = [x for x in items if x[0] in PICTURE_TYPES and x[1].rsplit(".", 1)[-1].lower() in IMG_EXT]
        if not pics or page > len(c.SEG):
            continue
        title = c.SEG[page - 1][1]
        caps = [r.get("图注", "").strip() for _, _, r in pics if r.get("图注", "").strip()]
        cap = caps[0] if caps else os.path.splitext(os.path.basename(pics[0][1]))[0].split("-", 3)[-1]
        # 07-P7 uses native PPT screenshot panels, not a raster montage.
        # Keep the first source path here as the page's availability marker.
        if len(pics) == 1 or (c.NO == "07" and page == 7):
            out[title] = (os.path.relpath(pics[0][1], here).replace("\\", "/"), cap)
        else:
            rel = f"img/{c.NO}_m{page}.png"
            order = list(registry())   # 拼图顺序 = 登记表里的行顺序
            pics.sort(key=lambda x: order.index(os.path.basename(x[1])))
            _montage([(p, r.get("角标", "").strip()) for _, p, r in pics], os.path.join(here, rel))
            out[title] = (rel, cap)
    # Explicit user-approved GIF replacements only; other animations remain
    # standalone editing assets. Keep GIF bytes intact in add_picture().
    import json
    replacements = os.path.join(ROOT, "PPT动图替换.json")
    if os.path.exists(replacements):
        with open(replacements, encoding="utf-8") as f:
            selected = json.load(f).get(c.NO, {})
        for page, filename in selected.items():
            page = int(page)
            for kind, path, row in approved(c.NO).get(page, []):
                if (kind == "anim" and os.path.basename(path) == filename
                        and path.lower().endswith(".gif") and 1 <= page <= len(c.SEG)):
                    out[c.SEG[page - 1][1]] = (
                        os.path.relpath(path, here).replace("\\", "/"), row.get("图注", ""))
    return out


def media_ready(no):
    """录屏/动画已就绪的页 → {页号: [文件名]}"""
    return {p: [os.path.basename(x[1]) for x in items if x[0] in MEDIA_TYPES]
            for p, items in approved(no).items() if any(x[0] in MEDIA_TYPES for x in items)}


def recorded_pages(no):
    """用户确认已录制的页，仅供清单使用；不读取或检查视频文件。"""
    import json
    path = os.path.join(ROOT, "录屏完成登记.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        entry = json.load(f).get(no, {})
    return {int(p): entry["状态"] for p in entry.get("页", [])}


def display_decisions(no):
    """用户确认的展示方式例外；不改写归档脚本，也不伪报动态素材就绪。"""
    import json
    path = os.path.join(ROOT, "展示方式确认.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return {int(p): note for p, note in json.load(f).get(no, {}).items()}


def _montage(items, out_path, h=300):
    import cv2, numpy as np
    from _vis import imread, tag, border, row
    ims = []
    for path, label in items:
        im = imread(path)
        im = cv2.resize(im, (int(im.shape[1] * h / im.shape[0]), h), interpolation=cv2.INTER_AREA)
        ims.append(border(tag(im, label, 24) if label else im))
    data = cv2.imencode(".png", row(ims))[1].tobytes()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    if not (os.path.exists(out_path) and open(out_path, "rb").read() == data):
        with open(out_path, "wb") as f:
            f.write(data)


def problems(lessons):
    """检查命名、登记、页号、取值是否合规 → [(级别, 说明)];级别 ❌ 必须改 / ⚠️ 提醒"""
    import importlib.util
    reg, fs, out = registry(), files(), []
    for f, path in fs.items():
        m = NAME.match(f)
        if not m:
            out.append(("❌", f"{os.path.relpath(path, HERE)}:文件名不符合「NN-pP-类型-简述.ext」(类型:{'/'.join(TYPES)})"))
            continue
        no, page = m.group(1), int(m.group(2))
        if os.path.basename(os.path.dirname(path)) != no:
            out.append(("❌", f"{f}:放错文件夹(应在 manual/{no}/)"))
        if f not in reg:
            out.append(("❌", f"{f}:未在 素材登记.csv 登记"))
        if no in lessons:
            spec = importlib.util.spec_from_file_location("c" + no, os.path.join(HERE, no, "content.py"))
            c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
            if page > len(c.SEG):
                out.append(("❌", f"{f}:第 {no} 讲只有 {len(c.SEG)} 页,没有第 {page} 页"))
        else:
            out.append(("❌", f"{f}:没有第 {no} 讲"))
    for f, r in reg.items():
        if f not in fs:
            out.append(("❌", f"素材登记.csv 有「{f}」,但 manual/ 里找不到该文件"))
            continue
        if r.get("状态", "").strip() not in STATES:
            out.append(("❌", f"{f}:状态「{r.get('状态')}」不是 {'/'.join(STATES)} 之一"))
        if r.get("来源类型", "").strip() not in SOURCES:
            out.append(("⚠️", f"{f}:来源类型「{r.get('来源类型')}」应为 {'/'.join(SOURCES)} 之一"))
        if r.get("状态", "").strip() == "通过" and not r.get("授权", "").strip():
            out.append(("⚠️", f"{f}:已通过但「授权」未填(出版前必须补)"))
    return out
