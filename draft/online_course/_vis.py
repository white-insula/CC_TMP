# -*- coding: utf-8 -*-
"""配图公共工具:素材来源、拼图、中文角标、合成场景、登记 vis.json。
每个模块的配图脚本在 _visuals/mN.py,函数 vNN() 生成第 NN 节的图并登记。
登记结果写在 NN/img/vis.json:{slide标题: [图片相对路径, 图注]},_ppt.py 自动读取。
"""
import os, json, glob
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
GAP = 24

# ---------- 素材来源(出处见 plan/COURSE_SCRIPTS.md 三) ----------
PI = r"E:\teaching\Linux for Raspi\references\example_code\python-raspberry-pi-bilibili"
OC = r"E:\teaching\openCV"
SRC = {
    "shapes": PI + r"\EXP-OpenCV-shape\shapes.png",            # [PI] 彩色形状图
    "paper": PI + r"\EXP-Opencv-Scan\paper.jpg",               # [PI] 斜拍文档
    "room": PI + r"\EXP-Base-Opencv\test.mp4",                 # [PI] 室内视频
    "class": OC + r"\Body_Detct\recordings\recording_20250926_165242.mp4",   # [OC] 教室坐姿录像
    "hand": OC + r"\Finger_Guess_Game\recording_20250917_084946.avi",       # [OC] 教师手势录像
    "trash": OC + r"\lajifenlei_demo\trashnet-master\data\dataset-resized",  # [OC] trashnet(MIT)
    "card_dir": r"E:\下载\Group A （最终版）\Group A （最终版）\代码集\Answer Card Recognition\答题卡扫描文件",
    "helmet_run": os.path.join(HERE, "assets", "60_helmet_run"),
    "yolo": os.path.join(HERE, "assets", "models", "yolov8n.pt"),
}
try:
    import ultralytics
    _UA = os.path.join(os.path.dirname(ultralytics.__file__), "assets")
    SRC["bus"] = os.path.join(_UA, "bus.jpg"); SRC["zidane"] = os.path.join(_UA, "zidane.jpg")
except ImportError:
    pass


def imread(path, flag=cv2.IMREAD_COLOR):
    return cv2.imdecode(np.fromfile(path, np.uint8), flag)


def src(name):
    return imread(SRC[name])


def frame_of(name, t=0.3):
    cap = cv2.VideoCapture(SRC[name])
    n = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * t))
    ok, f = cap.read(); cap.release()
    assert ok, name
    return f


def frames_of(name, ts):
    return [frame_of(name, t) for t in ts]


# ---------- 拼图 ----------
def bgr(g):
    return cv2.cvtColor(g, cv2.COLOR_GRAY2BGR) if g.ndim == 2 else g


def fit(img, w=None, h=None):
    ih, iw = img.shape[:2]
    s = (w / iw) if w else (h / ih)
    return cv2.resize(img, (int(iw * s), int(ih * s)), interpolation=cv2.INTER_AREA if s < 1 else cv2.INTER_CUBIC)


def border(img, color=(200, 200, 200), t=2):
    return cv2.copyMakeBorder(bgr(img), t, t, t, t, cv2.BORDER_CONSTANT, value=color)


def row(imgs, gap=GAP, bg=255):
    imgs = [bgr(i) for i in imgs]
    h = max(i.shape[0] for i in imgs)
    parts = []
    for k, i in enumerate(imgs):
        if i.shape[0] < h:
            i = cv2.copyMakeBorder(i, 0, h - i.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(bg,) * 3)
        parts.append(i)
        if k < len(imgs) - 1:
            parts.append(np.full((h, gap, 3), bg, np.uint8))
    return np.hstack(parts)


def col(imgs, gap=GAP, bg=255):
    imgs = [bgr(i) for i in imgs]
    w = max(i.shape[1] for i in imgs)
    parts = []
    for k, i in enumerate(imgs):
        if i.shape[1] < w:
            i = cv2.copyMakeBorder(i, 0, 0, 0, w - i.shape[1], cv2.BORDER_CONSTANT, value=(bg,) * 3)
        parts.append(i)
        if k < len(imgs) - 1:
            parts.append(np.full((gap, w, 3), bg, np.uint8))
    return np.vstack(parts)


def grid(imgs, cols, gap=GAP):
    return col([row(imgs[i:i + cols], gap) for i in range(0, len(imgs), cols)], gap)


def same(imgs, w=None, h=None):
    """统一尺寸(按宽或按高)。"""
    return [fit(bgr(i), w=w, h=h) for i in imgs]


# ---------- 中文文字 ----------
_fonts = {}


def _f(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT_PATH, size)
    return _fonts[size]


def text(img, s, xy, size=28, color=(255, 255, 255), bg=None, pad=8):
    """在图上写中文(color/bg 为 BGR)。bg 不为 None 时先画底框。"""
    img = bgr(img).copy()
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    x, y = xy
    l, t, r, b = d.textbbox((x, y), s, font=_f(size))
    if bg is not None:
        d.rectangle((l - pad, t - pad, r + pad, b + pad), fill=tuple(bg[::-1]))
    d.text((x, y), s, font=_f(size), fill=tuple(color[::-1]))
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)


def tag(img, s, size=None):
    """左上角深色角标,给拼图里的每个小图标注名称。"""
    img = bgr(img)
    size = size or max(18, img.shape[1] // 22)
    return text(img, s, (size // 2 + 4, size // 2), size, (255, 255, 255), (55, 42, 31), pad=size // 3)


def tagged(pairs, size=None):
    return [border(tag(i, s, size)) for i, s in pairs]


# ---------- 合成场景 ----------
COLORS = {"red": (40, 40, 210), "green": (60, 160, 40), "blue": (190, 110, 30), "yellow": (30, 200, 230)}


def paper(shadow=False, w=900, h=420, seed=7):
    """白纸手写字照片(与 21 讲同一合成方法)。"""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    base = 200 - 26 * (((xx - w * 0.55) / w) ** 2 + ((yy - h * 0.45) / h) ** 2) * 4
    base += cv2.GaussianBlur(rng.normal(0, 3, (h, w)).astype(np.float32), (5, 5), 0)
    ink = np.zeros((h, w), np.uint8)
    for k, t in enumerate(["Machine Vision", "threshold = 127", "Otsu  2026"]):
        cv2.putText(ink, t, (50, 120 + k * 120), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 2.6 if k == 0 else 2.2, 255, 5, cv2.LINE_AA)
    ink = cv2.GaussianBlur(ink, (5, 5), 0).astype(np.float32) / 255
    img = base * (1 - ink * 0.58)
    img -= 22 * np.exp(-((xx - w * 0.78) ** 2) / (2 * 40 ** 2))
    if shadow:
        img = img * (1 - 0.62 / (1 + np.exp((xx - w * 0.45) / 30)))
    return np.clip(img, 0, 255).astype(np.uint8)


def parts_scene(items=None, w=960, h=600, seed=3, bg=(170, 170, 165), light="even", noise=4):
    """俯拍工件场景:灰色传送带 + 彩色工件。items: [(形状, 颜色, (cx,cy), 尺寸, 角度, 缺陷)]。
    返回 (BGR 图, items)。形状:circle / square / rect / triangle / hex;缺陷:None / notch / dent。"""
    rng = np.random.default_rng(seed)
    if items is None:
        items = [("circle", "red", (170, 160), 70, 0, None), ("square", "blue", (420, 150), 120, 15, None),
                 ("triangle", "yellow", (690, 170), 140, 0, None), ("rect", "green", (200, 430), (190, 100), -10, None),
                 ("hex", "red", (480, 440), 75, 0, None), ("circle", "green", (760, 430), 80, 0, None)]
    img = np.zeros((h, w, 3), np.float32); img[:] = bg
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for shape, color, (cx, cy), size, ang, defect in items:
        m = np.zeros((h, w), np.uint8)
        _draw_shape(m, shape, (cx, cy), size, ang)
        if defect == "notch":
            cv2.circle(m, (int(cx + _r(size) * 0.85), int(cy - _r(size) * 0.2)), int(_r(size) * 0.38), 0, -1)
        elif defect == "dent":
            m2 = np.zeros_like(m); cv2.ellipse(m2, (cx, cy), (int(_r(size) * 1.18), int(_r(size) * 0.66)), ang, 0, 360, 255, -1); m = m2
        # 阴影
        sh = cv2.GaussianBlur(np.roll(np.roll(m, 6, 0), 6, 1), (21, 21), 0).astype(np.float32) / 255
        img *= (1 - 0.25 * sh[..., None])
        mf = cv2.GaussianBlur(m, (3, 3), 0).astype(np.float32)[..., None] / 255
        shade = 1 - 0.12 * ((yy - cy) / max(_r(size), 1)).clip(-1, 1)[..., None]   # 立体感
        img = img * (1 - mf) + np.array(COLORS[color], np.float32) * shade * mf
    if light == "side":
        img *= (0.45 + 0.75 * (xx / w))[..., None]
    elif light == "even":
        img *= (1.0 - 0.10 * (((xx - w / 2) / w) ** 2 + ((yy - h / 2) / h) ** 2) * 4)[..., None]
    img += rng.normal(0, noise, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8), items


def _r(size):
    return size if np.isscalar(size) else max(size) / 2


def _draw_shape(m, shape, c, size, ang):
    cx, cy = c
    if shape == "circle":
        cv2.circle(m, c, size, 255, -1, cv2.LINE_AA); return
    if shape == "rect":
        w, h = size
    else:
        w = h = size
    if shape in ("square", "rect"):
        box = cv2.boxPoints(((cx, cy), (w, h), ang)).astype(np.int32)
        cv2.fillPoly(m, [box], 255, cv2.LINE_AA); return
    n = 3 if shape == "triangle" else 6
    r = size / (np.sqrt(3) if n == 3 else 1)
    pts = [(cx + r * np.cos(np.radians(ang - 90 + 360 * k / n)), cy + r * np.sin(np.radians(ang - 90 + 360 * k / n))) for k in range(n)]
    cv2.fillPoly(m, [np.array(pts, np.int32)], 255, cv2.LINE_AA)


# ---------- matplotlib(中文) ----------
def plt_setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]; plt.rcParams["axes.unicode_minus"] = False
    return plt


def fig2img(fig):
    fig.canvas.draw()
    a = np.asarray(fig.canvas.buffer_rgba())[..., :3]
    import matplotlib.pyplot as plt
    plt.close(fig)
    return cv2.cvtColor(a, cv2.COLOR_RGB2BGR)


# ---------- 登记 ----------
class Lesson:
    """with Lesson("08") as L: L.add("标题前缀", img, "图注", name)"""

    def __init__(self, no):
        import _lib
        self.no = no
        self.c = _lib.load(no)
        self.titles = [s[1] for s in self.c.SEG if s[2] is not None]
        self.dir = os.path.join(HERE, no, "img")
        self.vis = {}

    def __enter__(self):
        # 不先删旧图:内容不变的文件不重写(保留时间戳),下游同步检查才不会误报"过期"
        os.makedirs(self.dir, exist_ok=True)
        self.old = {f for f in glob.glob(os.path.join(self.dir, f"{self.no}_*.png")) if not os.path.basename(f).startswith("21_")}
        self.written = set()
        return self

    def title(self, prefix):
        hits = [t for t in self.titles if t.startswith(prefix)]
        assert len(hits) == 1, f"{self.no}: 标题前缀 {prefix!r} 匹配 {hits}"
        return hits[0]

    @staticmethod
    def _put(path, data):
        if os.path.exists(path) and open(path, "rb").read() == data:
            return False
        with open(path, "wb") as f:
            f.write(data)
        return True

    def add(self, prefix, img, caption, name=None):
        t = self.title(prefix)
        name = name or f"{self.no}_{len(self.vis) + 1}.png"
        path = os.path.join(self.dir, name)
        self._put(path, cv2.imencode(".png", img)[1].tobytes())
        self.written.add(path)
        self.vis[t] = [f"img/{name}", caption]

    def __exit__(self, *exc):
        if exc[0] is None:
            for f in self.old - self.written:
                os.remove(f)
            self._put(os.path.join(self.dir, "vis.json"), json.dumps(self.vis, ensure_ascii=False, indent=1).replace(chr(10), os.linesep).encode("utf-8"))   # 与原文本模式写出的换行一致
            print(f"  {self.no}: {len(self.vis)} 张")
