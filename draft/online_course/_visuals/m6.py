# -*- coding: utf-8 -*-
"""模块六 MediaPipe:人脸·手·人体(42–49)配图。
素材:[OC]Finger_Guess_Game 教师自录手势视频、[OC]Body_Detct 教室坐姿录像(出版前需确认肖像授权)。"""
import cv2, numpy as np
import mediapipe as mp
from _vis import *

AMB = (0, 169, 242)
mph, mpf, mpp, mpd = mp.solutions.hands, mp.solutions.face_mesh, mp.solutions.pose, mp.solutions.drawing_utils
EYE = [33, 160, 158, 133, 153, 144]


def rgb(f):
    return cv2.cvtColor(f, cv2.COLOR_BGR2RGB)


def count_fingers(lm):
    """与第 46 讲完全相同的规则。"""
    n = 1 if lm[4].x > lm[3].x else 0
    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:
        if lm[tip].y < lm[pip].y: n += 1
    return n


def up_list(lm):
    return [lm[t].y < lm[p].y for t, p in [(8, 6), (12, 10), (16, 14), (20, 18)]]


def gesture(lm):
    """第 48 讲规则。"""
    n = count_fingers(lm); u = up_list(lm)
    if n <= 1: return "石头"
    if n == 2 and u[0] and u[1]: return "剪刀"
    if n >= 4: return "布"
    return "？"


def ear(lm, w, h):
    p = [np.array((lm[i].x * w, lm[i].y * h)) for i in EYE]
    return (np.linalg.norm(p[1] - p[5]) + np.linalg.norm(p[2] - p[4])) / (2 * np.linalg.norm(p[0] - p[3]))


def hand_scan(step=2):
    """扫一遍手势视频,返回 [(帧号, 帧, 手列表)]。"""
    cap = cv2.VideoCapture(SRC["hand"]); out = []; k = 0
    with mph.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.6) as H:
        while True:
            ok, f = cap.read()
            if not ok: break
            if k % step == 0:
                r = H.process(rgb(f))
                if r.multi_hand_landmarks: out.append((k, f, r.multi_hand_landmarks))
            k += 1
    return out


_HS = None


def hands():
    global _HS
    if _HS is None: _HS = hand_scan()
    return _HS


def draw_hand(f, hl, numbers=False):
    o = f.copy()
    mpd.draw_landmarks(o, hl, mph.HAND_CONNECTIONS, mpd.DrawingSpec((0, 169, 242), 3, 4), mpd.DrawingSpec((255, 255, 255), 2))
    if numbers:
        h, w = o.shape[:2]
        for i, p in enumerate(hl.landmark):
            cv2.putText(o, str(i), (int(p.x * w) + 6, int(p.y * h) - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2, cv2.LINE_AA)
    return o


def upright(lm):
    """手掌竖直、手指朝上(第 46 讲规则的前提):手腕明显低于中指根部。"""
    return lm[0].y - lm[9].y > 0.12 and abs(lm[0].x - lm[9].x) < 0.6 * (lm[0].y - lm[9].y)


def best_hand(pred):
    """在扫描结果里找第一个满足条件、且手指朝上的(帧, 一只手)。"""
    for k, f, hs in hands():
        for hl in hs:
            if upright(hl.landmark) and pred(hl.landmark): return k, f, hl
    return None


def face_of(f):
    with mpf.FaceMesh(static_image_mode=True, refine_landmarks=False) as F:
        r = F.process(rgb(f))
    return r.multi_face_landmarks[0] if r.multi_face_landmarks else None


def pose_of(f):
    with mpp.Pose(static_image_mode=True, model_complexity=1) as P:
        r = P.process(rgb(f))
    return r.pose_landmarks


def angle(a, b, c):
    a, b, c = map(np.array, (a, b, c)); ba, bc = a - b, c - b
    return np.degrees(np.arccos(np.clip(ba @ bc / (np.linalg.norm(ba) * np.linalg.norm(bc)), -1, 1)))


def _class_frame():
    return frame_of("class", 0.3)


_EARS = None


def ear_series():
    global _EARS
    if _EARS is None:
        cap = cv2.VideoCapture(SRC["hand"]); vals, frames = [], []
        with mpf.FaceMesh(static_image_mode=False) as F:
            while True:
                ok, fr = cap.read()
                if not ok: break
                r = F.process(rgb(fr)); H, W = fr.shape[:2]
                vals.append(ear(r.multi_face_landmarks[0].landmark, W, H) if r.multi_face_landmarks else np.nan); frames.append(fr)
        _EARS = (np.array(vals), frames, cap.get(cv2.CAP_PROP_FPS))
    return _EARS


def _face_frame():
    """正脸、Haar 也能检出、EAR 接近整段中位数(正常睁眼)的一帧。"""
    vals, frames, _ = ear_series()
    med = np.nanmedian(vals)
    cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    for i in np.argsort(np.abs(np.nan_to_num(vals, nan=9) - med)):
        f = frames[i]
        if len(cas.detectMultiScale(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), 1.1, 5, minSize=(60, 60))):
            return f
    return frames[int(np.nanargmin(np.abs(vals - med)))]


def v42():
    with Lesson("42") as L:
        k, f, hl = best_hand(lambda lm: count_fingers(lm) >= 4)
        hd = draw_hand(f, hl)
        ff = _face_frame(); fm = face_of(ff); fo = ff.copy()
        mpd.draw_landmarks(fo, fm, mpf.FACEMESH_TESSELATION, None, mpd.DrawingSpec((0, 220, 120), 1, 1))
        cf = _class_frame(); pl = pose_of(cf); po = cf.copy()
        mpd.draw_landmarks(po, pl, mpp.POSE_CONNECTIONS, mpd.DrawingSpec((0, 169, 242), 3, 4), mpd.DrawingSpec((255, 255, 255), 2))
        panels = same([hd, fo, po], h=360)
        L.add("课程导入", row(tagged(list(zip(panels, ["手部 21 点", "人脸网格 468 点", "人体姿态 33 点"])), 22)), "MediaPipe 现成模型，装好就能用（教师自录视频 / 教室录像，实际运行结果）")
        L.add("MediaPipe 能做什么", row(tagged(list(zip(panels, ["手势", "人脸网格", "人体姿态"])), 22)), "不用自己训练，几行代码得到关键点")
        h, w = f.shape[:2]; p = hl.landmark[8]; o = hd.copy()
        cv2.circle(o, (int(p.x * w), int(p.y * h)), 12, (0, 0, 255), 3)
        o = text(o, f"8 号点 x={p.x:.2f}, y={p.y:.2f}", (int(p.x * w) - 60, max(int(p.y * h) - 110, 5)), 24, (255, 255, 255), (0, 0, 180), 4)
        o = text(o, f"像素坐标 = ({int(p.x * w)}, {int(p.y * h)})", (int(p.x * w) - 60, max(int(p.y * h) - 66, 50)), 24, (55, 42, 31), (0, 220, 255), 4)
        L.add("关键点", o, f"关键点给的是 0–1 的比例；× 画面宽 {w}、高 {h} 才是像素坐标")


def v43():
    with Lesson("43") as L:
        f = _face_frame()
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        o1 = f.copy()
        for x, y, w, h in cas.detectMultiScale(g, 1.1, 5, minSize=(60, 60)):
            cv2.rectangle(o1, (x, y), (x + w, y + h), (0, 255, 0), 3)
        with mp.solutions.face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as D:
            r = D.process(rgb(f))
        o2 = f.copy(); H, W = f.shape[:2]; boxes = []
        for d in r.detections or []:
            b = d.location_data.relative_bounding_box
            x, y, w, h = int(b.xmin * W), int(b.ymin * H), int(b.width * W), int(b.height * H); boxes.append((x, y, w, h))
            cv2.rectangle(o2, (x, y), (x + w, y + h), (0, 255, 0), 3)
            o2 = text(o2, f"face {d.score[0]:.2f}", (x, max(y - 36, 2)), 24, (255, 255, 255), (0, 150, 0), 4)
        L.add("实操一", o1, "OpenCV 自带的 Haar 级联检测器：快，但侧脸、遮挡时容易漏检")
        L.add("实操二", o2, "MediaPipe 人脸检测：框 + 置信度")
        o3 = f.copy()
        for x, y, w, h in boxes:
            x, y = max(x, 0), max(y, 0); roi = o3[y:y + h, x:x + w]
            o3[y:y + h, x:x + w] = cv2.resize(cv2.resize(roi, (12, 12)), (roi.shape[1], roi.shape[0]), interpolation=cv2.INTER_NEAREST)
        L.add("人脸检测的应用与规范", row(tagged([(o2, "检测到人脸"), (o3, "自动打码保护隐私")], 22)), "检测出人脸后自动打马赛克：发布视频前保护他人隐私")


def v44():
    plt = plt_setup()
    with Lesson("44") as L:
        f = _face_frame(); fm = face_of(f); H, W = f.shape[:2]
        o = f.copy(); mpd.draw_landmarks(o, fm, mpf.FACEMESH_TESSELATION, None, mpd.DrawingSpec((0, 220, 120), 1, 1))
        lm = fm.landmark
        xs = [lm[i].x * W for i in EYE]; ys = [lm[i].y * H for i in EYE]
        x0, x1, y0, y1 = int(min(xs)) - 40, int(max(xs)) + 40, int(min(ys)) - 35, int(max(ys)) + 35
        eye = cv2.resize(f[y0:y1, x0:x1], None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC)
        for k, i in enumerate(EYE):
            px, py = int((lm[i].x * W - x0) * 6), int((lm[i].y * H - y0) * 6)
            cv2.circle(eye, (px, py), 9, (0, 0, 255), -1)
            eye = text(eye, f"P{k + 1}", (px + 8, py - 40 if k in (1, 2) else py + 6), 26, (255, 255, 255), (0, 0, 180), 3)
        e = ear(lm, W, H)
        eye = text(eye, f"EAR = {e:.2f}", (10, 10), 30, (255, 255, 255), (55, 42, 31), 5)
        L.add("人脸网格", row(tagged([(o, "468 个点的网格"), (eye, "眼部 6 点放大")], 22)), "人脸网格里每个点都有固定编号，取眼睛上的 6 个点计算")
        L.add("EAR", eye, f"EAR = (|P2−P6| + |P3−P5|) ÷ (2 × |P1−P4|)；这一帧睁眼，实测 {e:.2f}")
        # 整段视频的 EAR 曲线(真实眨眼)
        vals, _, fps = ear_series()
        t = np.arange(len(vals)) / fps
        fig, ax = plt.subplots(figsize=(11, 3.8), dpi=110)
        ax.plot(t, vals, color="#1F2A37", lw=1.4, label="EAR（实测）")
        ax.axhline(0.2, color="#D7263D", ls="--", lw=1.5, label="阈值 0.2")
        ax.set_xlabel("时间（秒）", fontsize=12); ax.set_ylabel("EAR", fontsize=12); ax.legend(fontsize=11, loc="lower right")
        ax.spines[["top", "right"]].set_visible(False); ax.set_title(f"教师自录视频 {len(vals)} 帧的 EAR：每个向下的尖峰就是一次眨眼", fontsize=13)
        fig.tight_layout()
        L.add("从闭眼到疲劳", fig2img(fig), "眨眼只低于阈值一两帧；疲劳是长时间压在阈值以下（再用连续帧数判断）")
        oe = f.copy(); cv2.polylines(oe, [np.array([[int(lm[i].x * W), int(lm[i].y * H)] for i in EYE], np.int32)], True, (0, 255, 0), 2)
        oe = text(oe, f"EAR: {e:.2f}", (14, 14), 34, (0, 255, 0), (0, 0, 0), 6)
        L.add("实操一", oe, "每一帧算出 EAR 显示在画面上")


def v46():
    with Lesson("46") as L:
        k, f, hl = best_hand(lambda lm: count_fingers(lm) == 5) or best_hand(lambda lm: count_fingers(lm) >= 4)
        h, w = f.shape[:2]; lm = hl.landmark
        xs = [p.x * w for p in lm]; ys = [p.y * h for p in lm]
        x0, x1, y0, y1 = max(int(min(xs)) - 50, 0), min(int(max(xs)) + 50, w), max(int(min(ys)) - 50, 0), min(int(max(ys)) + 50, h)
        big = cv2.resize(draw_hand(f, hl)[y0:y1, x0:x1], None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        for i, p in enumerate(lm):
            px, py = int((p.x * w - x0) * 2), int((p.y * h - y0) * 2)
            cv2.putText(big, str(i), (px + 8, py - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2, cv2.LINE_AA)
        L.add("21 个关键点", big, "0 号是手腕；每根手指 4 个点，指尖分别是 4、8、12、16、20")
        L.add("实操一", draw_hand(f, hl), "draw_landmarks 画出 21 个点和骨架连线（教师自录视频）")
        r = best_hand(lambda lm: count_fingers(lm) == 5 and clear(lm, [1, 1, 1, 1]))
        if r:
            o = draw_hand(r[1], r[2]); o = text(o, "手指数：5", (14, o.shape[0] - 70), 34, (255, 255, 255), (0, 120, 0), 6)
            L.add("实操二", o, "count_fingers 在视频中的实际判定（0–4 根的清晰画面待教师补录）")


def v47():
    with Lesson("47") as L:
        f = _class_frame(); pl = pose_of(f); h, w = f.shape[:2]; lm = pl.landmark
        o = f.copy(); mpd.draw_landmarks(o, pl, mpp.POSE_CONNECTIONS, mpd.DrawingSpec((0, 169, 242), 3, 4), mpd.DrawingSpec((255, 255, 255), 2))
        for i in (0, 11, 12, 13, 14, 15, 16, 23, 24):
            p = lm[i]; cv2.putText(o, str(i), (int(p.x * w) + 6, int(p.y * h) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
        L.add("33 个关键点", o, "常用点：0 鼻子，11/12 肩，13/14 肘，15/16 腕，23/24 髋（教室录像，实际运行）")
        side = 11 if lm[11].visibility > lm[12].visibility else 12
        A, B, C = [(lm[i].x * w, lm[i].y * h) for i in (side, side + 2, side + 4)]
        ang = angle(A, B, C); o2 = o.copy()
        for P in (A, B, C): cv2.circle(o2, tuple(map(int, P)), 10, (0, 0, 255), -1)
        cv2.line(o2, tuple(map(int, A)), tuple(map(int, B)), (0, 0, 255), 4); cv2.line(o2, tuple(map(int, B)), tuple(map(int, C)), (0, 0, 255), 4)
        o2 = text(o2, f"肘部角度 {ang:.0f}°", (int(B[0]) + 15, int(B[1]) - 15), 28, (255, 255, 255), (0, 0, 180), 5)
        L.add("用法与关节角度", o2, "肩-肘-腕三个点，用向量夹角算出手肘弯曲角度")
        L.add("实操一", o2, "画出骨架，并在肘部实时显示角度")


def clear(lm, want):
    """配图选帧用的“明显”判定:伸直的指尖高出关节、弯曲的低于关节,都留出余量,避免模棱两可的画面。"""
    m = 0.04
    for (t, p), u in zip([(8, 6), (12, 10), (16, 14), (20, 18)], want):
        d = lm[p].y - lm[t].y
        if (u and d < m) or (not u and d > -m / 2): return False
    return True


def v48():
    # 现有视频里没有正对镜头、姿势清楚的石头/剪刀/布,不配图,避免误导;见 素材需求.md
    with Lesson("48") as L:
        pass


def v49():
    with Lesson("49") as L:
        f = _class_frame(); pl = pose_of(f); h, w = f.shape[:2]; lm = pl.landmark
        P = lambda i: np.array((lm[i].x * w, lm[i].y * h))
        sh = (P(11) + P(12)) / 2; hip = (P(23) + P(24)) / 2; nose = P(0)
        def tilt(a, b):   # a→b 连线与竖直方向的夹角
            v = a - b; return np.degrees(np.arctan2(abs(v[0]), abs(v[1])))
        neck, back = tilt(nose, sh), tilt(sh, hip)
        o = f.copy()
        for a, b, col in ((nose, sh, (0, 0, 255)), (sh, hip, (255, 120, 0))):
            cv2.line(o, tuple(map(int, a)), tuple(map(int, b)), col, 5)
            cv2.line(o, tuple(map(int, b)), (int(b[0]), int(b[1] - 120)), (200, 200, 200), 2)
        for p_ in (nose, sh, hip): cv2.circle(o, tuple(map(int, p_)), 9, (0, 255, 255), -1)
        o = text(o, f"颈部前倾 {neck:.0f}°", (14, 14), 28, (255, 255, 255), (0, 0, 180), 5)
        o = text(o, f"背部前倾 {back:.0f}°", (14, 64), 28, (255, 255, 255), (180, 90, 0), 5)
        L.add("把“坐姿”变成角度", o, "鼻子→肩中点、肩中点→髋中点，两条线与竖直方向的夹角（教室录像，实测）")
        L.add("实操一", o, "每帧计算两个角度并显示")
        L.add("案例导入", o, "坐姿监测：用姿态关键点量出低头、驼背（参考：[OC]Body_Detct）")
