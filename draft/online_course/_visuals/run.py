# -*- coding: utf-8 -*-
"""生成配图:python _visuals/run.py 08 09 ... | m2 | all"""
import os, sys, re, importlib, traceback
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)
MODS = [m[:-3] for m in sorted(os.listdir(os.path.dirname(os.path.abspath(__file__)))) if re.fullmatch(r"m\d+\.py", m)]
funcs = {}
for m in MODS:
    mod = importlib.import_module(m)
    for k, v in vars(mod).items():
        if re.fullmatch(r"v\d\d", k):
            funcs[k[1:]] = (m, v)
args = sys.argv[1:] or ["all"]
todo = []
for a in args:
    if a == "all": todo += sorted(funcs)
    elif a.startswith("m"): todo += sorted(k for k, (m, _) in funcs.items() if m == a)
    else: todo.append(a)


def gen_hash(mod, no):
    """该节配图的"生成代码指纹":所在 mN.py 去掉其他 vXX 函数后的源码 + _vis.py。只改别的节,不影响本节指纹。"""
    import hashlib
    here = os.path.dirname(os.path.abspath(__file__))
    src = open(os.path.join(here, mod + ".py"), encoding="utf-8").read()
    parts = re.split(r"(?m)^(?=def v\d\d\()", src)
    keep = [p for p in parts if not re.match(r"def v\d\d\(", p) or p.startswith(f"def v{no}(")]
    vis = open(os.path.join(HERE, "_vis.py"), encoding="utf-8").read()
    return hashlib.md5(("".join(keep) + vis).encode("utf-8")).hexdigest()


bad = []
for no in todo:
    try:
        funcs[no][1]()
        with open(os.path.join(HERE, no, "img", ".gen_hash"), "w") as f:
            f.write(gen_hash(funcs[no][0], no))
    except Exception:
        bad.append(no); traceback.print_exc()
print("done", len(todo) - len(bad), "failed", bad)
