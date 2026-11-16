# -*- coding: utf-8 -*-
"""脚本改动后的下游同步检查(只检查、不修改)。

原则:课程脚本 NN/content.py 是一切工作的起点;脚本一改,下游全部资源都要查、都要跟着更新。
用法:python _sync_check.py        → 逐环列出 ✅ 同步 / ❌ 过期(附修复命令)/ ⚠️ 需人工

检查链:
  1 content.py      → 脚本NN.docx、NN-*.pptx、素材需求.md        (python _lib.py NN)
  2 _visuals/mX.py  → NN/img/*.png + vis.json                    (python _visuals/run.py NN,再 _lib.py NN)
  3 各节素材需求    → 素材需求汇总.md                            (python _todo_summary.py)
  4 全部 content.py → 全部微课脚本汇总.docx                      (python _merge.py)
  5 NN-*.pptx       → PPT_collection/ 拷贝 → PPT_collection.zip/.rar
  6 课程配图        → 教材插图 draft/ 与 out/chapters/img/      (python ../../tools/collect_figures.py chNN [--to out/chapters/img])
  7 教材 .md/插图   → out/chapters/*.html 阅读页                 (python ../../tools/build_reading_html.py …)
  8 PPT_collection 内的手改版(流程外的改动,重新生成会丢)
  9 manual/ 手工素材:命名、登记表、页号合规;审核「通过」的是否已生成进 PPT  (python _lib.py NN)
"""
import glob, hashlib, io, os, re, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
os.chdir(HERE)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

mt = os.path.getmtime
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()
LESSONS = sorted(x for x in os.listdir(HERE) if re.fullmatch(r"\d\d", x))
bad = warn = 0


def report(ok, msg, fix=None, manual=False):
    global bad, warn
    if ok:
        return
    if manual:
        warn += 1
        print(f"  ⚠️ {msg}" + (f"\n       → {fix}" if fix else ""))
    else:
        bad += 1
        print(f"  ❌ {msg}" + (f"\n       → {fix}" if fix else ""))


def pptx_of(no):
    g = glob.glob(os.path.join(no, f"{no}-*.pptx"))
    return g[0] if g else None


print("1) content.py → 脚本docx / pptx / 素材需求.md")
for no in LESSONS:
    c = os.path.join(no, "content.py")
    if not os.path.exists(c):
        continue
    outs = [os.path.join(no, f"脚本{no}.docx"), pptx_of(no), os.path.join(no, "素材需求.md")]
    stale = [os.path.basename(o) if o else "pptx" for o in outs if not o or not os.path.exists(o) or mt(o) < mt(c)]
    report(not stale, f"{no}: {'、'.join(stale)} 比 content.py 旧", f"python _lib.py {no}")

print("2) _visuals → 配图")
sys.path.insert(0, os.path.join(HERE, "_visuals"))
import importlib.util  # noqa: E402
_spec = importlib.util.spec_from_file_location("_run_hash", os.path.join(HERE, "_visuals", "run.py"))
_src = open(os.path.join(HERE, "_visuals", "run.py"), encoding="utf-8").read()
_ns = {"os": os, "re": re, "HERE": HERE, "__file__": os.path.join(HERE, "_visuals", "run.py")}
exec(_src[_src.index("def gen_hash"):_src.index("bad = []")], _ns)
gen_hash = _ns["gen_hash"]
owner = {}
for m in glob.glob(os.path.join("_visuals", "m*.py")):
    for no in re.findall(r"^def v(\d\d)\(", open(m, encoding="utf-8").read(), re.M):
        owner[no] = os.path.basename(m)[:-3]
for no, m in sorted(owner.items()):
    stamp = os.path.join(no, "img", ".gen_hash")
    vj = os.path.join(no, "img", "vis.json")
    if os.path.exists(stamp):
        report(open(stamp).read().strip() == gen_hash(m, no), f"{no}: {m}.py 中本节生成代码改过,配图未重跑",
               f"python _visuals/run.py {no} && python _lib.py {no}")
    elif os.path.exists(vj):
        report(mt(vj) >= mt(os.path.join("_visuals", m + ".py")), f"{no}: 无生成指纹且配图比 {m}.py 旧",
               f"python _visuals/run.py {no} && python _lib.py {no}")
    p = pptx_of(no)
    imgs = glob.glob(os.path.join(no, "img", "*.png"))
    if imgs:
        report(p and mt(p) >= max(mt(x) for x in imgs + [vj]), f"{no}: pptx 比配图旧", f"python _lib.py {no}")

print("3) 素材需求汇总.md")
s = "素材需求汇总.md"
todo = sum(sum("⬜" in line or "⚠️" in line for line in open(f, encoding="utf-8"))
           for f in glob.glob(os.path.join("??", "素材需求.md")))
m_ = re.search(r"共 (\d+) 条", open(s, encoding="utf-8").read()) if os.path.exists(s) else None
report(m_ and int(m_.group(1)) == todo, f"汇总写 {m_.group(1) if m_ else '?'} 条,各节实际 {todo} 条", "python _todo_summary.py")

print("4) 01–60 源脚本与正式归档（旧全课汇总不作为依据）")
import subprocess
checked = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'check_script_archive_01_60.py')], capture_output=True, text=True, encoding='utf-8')
print(checked.stdout.strip())
if checked.stderr:
    print(checked.stderr.strip())
report(checked.returncode == 0, "01–60 源脚本与正式归档不一致或核对失败", "核对归档及修订记录，不得用旧汇总回填或静默覆盖归档")

print("5) PPT_collection 拷贝 / 压缩包")
col = os.path.join("stu_work", "PPT_collection")
if not os.path.isdir(col):
    print("  ℹ️ 旧 stu_work 已隔离至 quarantine/stu_work_2026-11-12，不参与当前生成与分发检查；跳过旧合集，不代表合集已验收。")
if os.path.isdir(col):
    for f in sorted(glob.glob(os.path.join(col, "*.pptx"))):
        no = os.path.basename(f)[:2]
        src = pptx_of(no)
        report(src and md5(src) == md5(f), f"{os.path.basename(f)} 与 {no}/ 生成版不一致", f"cp {no}/{no}-*.pptx {col}/")
    if os.path.exists(col + ".zip"):
        z = zipfile.ZipFile(col + ".zip")
        for n in z.namelist():
            if n.endswith(".pptx"):
                local = os.path.join(os.path.dirname(col), n.replace("/", os.sep))
                report(os.path.exists(local) and hashlib.md5(z.read(n)).hexdigest() == md5(local), f"zip 内 {n} 与文件夹不一致",
                       "7z a -tzip -mcu=on 新.zip \"PPT_collection/*.pptx\" 后替换")
    if os.path.exists(col + ".rar"):
        print("  ℹ️ stu_work/PPT_collection.rar = 教师手改版(嵌套 stu_work/PPT_collection/PPT_collection/)的打包,不是生成版拷贝,不自动重建;见第 8 项")

print("6) 教材插图 ← 课程配图")
sys.path.insert(0, os.path.join(ROOT, "tools"))
from collect_figures import FIGS  # noqa: E402
for ch, figs in FIGS.items():
    for to in ("draft/chapters/img", "out/chapters/img"):
        for no, (src, name) in figs.items():
            a, b = os.path.join(HERE, src), os.path.join(ROOT, to, name)
            report(os.path.exists(b) and md5(a) == md5(b), f"{ch} 图 {no} ({to}/{name}) 与课程配图 {src} 不一致",
                   f"python tools/collect_figures.py {ch}" + ("" if to.startswith("draft") else f" --to {to}"))

print("7) 定稿阅读页")
for mdp in glob.glob(os.path.join(ROOT, "out", "chapters", "ch*.md")):
    html = mdp[:-3] + ".html"
    deps = [mdp] + glob.glob(os.path.join(ROOT, "out", "chapters", "img", os.path.basename(mdp)[:4] + "_*"))
    report(os.path.exists(html) and mt(html) >= max(mt(x) for x in deps), f"{os.path.basename(html)} 比 .md/插图旧",
           f"python tools/build_reading_html.py --md out/chapters/{os.path.basename(mdp)} --out out/chapters/{os.path.basename(html)}")
    dr = os.path.join(ROOT, "draft", "chapters", os.path.basename(mdp))
    report(not os.path.exists(dr) or md5(dr) == md5(mdp), f"draft 与 out 的 {os.path.basename(mdp)} 不一致(定稿后又改了草稿?)",
           "确认后把 draft 复制到 out 并重建阅读页", manual=True)
print("   (提示)脚本改动若涉及教材已写内容,须人工对照教材正文;本脚本只能查文件,查不了语义。")

print("8) 流程外的手改版(教师手动插图)")
if not os.path.isdir(col):
    print("  ℹ️ 旧教师手改版已隔离，不扫描隔离区；需要复用时先审核登记到 manual/。")
from pptx import Presentation  # noqa: E402


def pics(path):
    out = {}
    for i, sl in enumerate(Presentation(path).slides, 1):
        for sh in sl.shapes:
            if sh.shape_type == 13:
                out.setdefault(i, set()).add(hashlib.md5(sh.image.blob).hexdigest())
    return out


def page_done(no, page):
    f = os.path.join(no, "素材需求.md")
    if os.path.exists(f):
        for line in open(f, encoding="utf-8"):
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if len(c) >= 4 and c[0] == str(page):
                return "✅" in c[3]
    return False


for f in sorted(glob.glob(os.path.join(col, "**", "*.pptx"), recursive=True)):
    if os.path.dirname(f) == col:
        continue
    no = os.path.basename(f)[:2]
    src = pptx_of(no)
    if not src:
        continue
    gen, man = pics(src), pics(f)
    gen_all = set().union(*gen.values()) if gen else set()
    import _manual
    man_files = {md5(p): os.path.basename(p) for p in _manual.files().values()}
    reg_ = _manual.registry()
    for page, hs in sorted(man.items()):
        extra = hs - gen_all
        if not extra:
            continue
        known = [man_files[h] for h in extra if h in man_files]
        if known and len(known) == len(extra):
            st = "、".join(f"{k}({reg_.get(k, {}).get('状态', '未登记')})" for k in known)
            print(f"  ✅ {no} 第 {page} 页:手插图已登记在 manual/ → {st}")
        elif page_done(no, page):
            print(f"  ✅ {no} 第 {page} 页:手改版有 {len(extra)} 张图与生成版不同(手插图或旧配图),该页已由流程配图接管")
        else:
            report(False, f"{no} 第 {page} 页:手改版有 {len(extra)} 张图不在流程里(该页素材需求仍是 ⬜),重新生成会丢",
                   f"把原图按规则放进 manual/{no}/ 并在 素材登记.csv 审核通过(示意图也可交程序重画),再 python _lib.py {no}", manual=True)

print("9) manual/ 手工素材(命名、登记、接入)")
import _manual  # noqa: E402
for lvl, msg in _manual.problems(set(LESSONS)):
    report(False, msg, manual=(lvl == "⚠️"))
for no in LESSONS:
    stamp = os.path.join(no, ".manual_hash")
    cur = _manual.fingerprint(no)
    old = open(stamp).read().strip() if os.path.exists(stamp) else None
    report(old == cur, f"{no}: manual/ 里本节审核通过的素材有变化(新增/改图/改登记),PPT 未重新生成", f"python _lib.py {no}")
reg = _manual.registry()
cnt = {}
for r in reg.values():
    cnt[r.get("状态", "").strip()] = cnt.get(r.get("状态", "").strip(), 0) + 1
print("   登记 {} 个:".format(len(reg)) + "、".join(f"{k} {v}" for k, v in cnt.items()))

print(f"\n结果:❌ {bad} 项过期,⚠️ {warn} 项需人工")
