# -*- coding: utf-8 -*-
"""模块七 物体检测:YOLO(50–60)配图。yolov8n 实际推理;训练结果来自 assets/60_helmet_run(2026-11-05 实测)。"""
import cv2, numpy as np, os, glob
from _vis import *

AMB = (0, 169, 242)
RUN = SRC["helmet_run"]
_M = None


def model():
    global _M
    if _M is None:
        from ultralytics import YOLO
        _M = YOLO(SRC["yolo"])
    return _M


def det(im, **kw):
    return model()(im, verbose=False, **kw)[0]


def draw(im, r, keep=None, zh=True):
    names = {0: "人", 5: "公交车", 2: "汽车", 56: "椅子", 62: "显示器", 63: "笔记本", 66: "键盘", 64: "鼠标", 39: "瓶子", 41: "杯子"}
    o = im.copy()
    for b, k, cf in zip(r.boxes.xyxy.numpy().astype(int), r.boxes.cls.numpy().astype(int), r.boxes.conf.numpy()):
        if keep is not None and k not in keep: continue
        x1, y1, x2, y2 = b
        cv2.rectangle(o, (x1, y1), (x2, y2), (0, 200, 0), 3)
        lab = f"{names.get(k, r.names[k]) if zh else r.names[k]} {cf:.2f}"
        o = text(o, lab, (x1 + 3, max(y1 - 32, 2)), 22, (255, 255, 255), (0, 150, 0), 3)
    return o


def trash_imgs(cls, n):
    return [imread(f) for f in sorted(glob.glob(os.path.join(SRC["trash"], cls, "*.jpg")))[:n]]


def v50():
    with Lesson("50") as L:
        ims = trash_imgs("glass", 12)
        L.add("课程导入", grid([border(cv2.resize(i, (256, 192)), (230, 230, 230), 1) for i in ims], 6, 8),
              "同样是“玻璃瓶”，形状、颜色、角度千差万别——很难写规则，但可以让机器看例子学（trashnet 数据集，MIT 许可）")


def v51():
    with Lesson("51") as L:
        cls = [("cardboard", "纸板"), ("glass", "玻璃"), ("metal", "金属"), ("paper", "纸"), ("plastic", "塑料"), ("trash", "其他垃圾")]
        L.add("分类", grid(tagged([(cv2.resize(trash_imgs(c, 3)[2], (320, 240)), f"类别：{z}") for c, z in cls], 22), 3),
              "分类只回答“整张图是什么”，不管东西在哪（垃圾分类数据集 trashnet）")
        im = fit(src("bus"), w=720); r = det(im)
        o = draw(im, r)
        L.add("检测", o, "检测回答“有什么、在哪里”：每个目标一个框 + 类别 + 置信度（yolov8n 实际结果）")


def v52():
    with Lesson("52") as L:
        im = src("bus"); r = det(im)
        L.add("实操", fit(r.plot(), w=720), f"三行代码的检测结果：yolov8n 在 bus.jpg 上找到 {len(r.boxes)} 个目标（ultralytics 自带示例图）")
        L.add("课程导入", fit(r.plot(), w=720), "YOLO：只看一眼，就把画面里的物体都框出来")
        names = model().names
        canvas = np.full((900, 1600, 3), 255, np.uint8)
        for i in range(80):
            c, rr = divmod(i, 20)
            canvas = text(canvas, f"{i:>2} {names[i]}", (20 + c * 395, 18 + rr * 44), 24, (0, 0, 180) if i in (0, 2, 5, 39, 41, 67) else (40, 40, 40))
        L.add("COCO", canvas, "COCO 数据集的 80 个类别和编号（红色为常用：0 人、2 汽车、5 公交车、39 瓶子、41 杯子、67 手机）")


def v53():
    with Lesson("53") as L:
        im = src("bus"); r = det(im)
        lines = ["for b in r.boxes:", "    print(r.names[int(b.cls)], float(b.conf), b.xyxy.tolist())", ""]
        for b in r.boxes:
            x1, y1, x2, y2 = [int(v) for v in b.xyxy[0].tolist()]
            lines.append(f"{r.names[int(b.cls)]:<8} {float(b.conf):.2f}  [{x1}, {y1}, {x2}, {y2}]")
        con = np.full((60 + 40 * len(lines), 1100, 3), (40, 32, 26), np.uint8)
        for k, l in enumerate(lines):
            cv2.putText(con, l, (24, 50 + 40 * k), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (180, 230, 120) if k < 2 else (235, 235, 235), 2, cv2.LINE_AA)
        L.add("实操一", con, "逐个打印类别、置信度和框的左上、右下坐标（真实输出）")
        n = sum(int(c) == 0 for c in r.boxes.cls)
        o = draw(fit(im, w=720), det(fit(im, w=720)))
        o = text(o, f"人数：{n}", (14, 14), 34, (255, 255, 255), (0, 0, 180), 6)
        L.add("实操二", o, "自己用 rectangle + 中文标签画框，并统计“人”的数量")


def v54():
    with Lesson("54") as L:
        im = fit(frame_of("class", 0.3), w=720)
        a = det(im, conf=0.25); b = det(im, conf=0.6); p = det(im, conf=0.25, classes=[0])
        L.add("实操二", row(tagged([(draw(im, a), f"全部类别：{len(a.boxes)} 个框"), (draw(im, p), f"classes=[0] 只看人：{len(p.boxes)} 个")], 22)),
              "classes 参数只保留需要的类别，画面清爽、速度也更快（教室录像，yolov8n 实际结果）")
        L.add("阈值怎么定", row(tagged([(draw(im, a), f"conf=0.25：{len(a.boxes)} 个"), (draw(im, b), f"conf=0.6：{len(b.boxes)} 个")], 22)),
              "阈值低：找得全但可能误报；阈值高：可靠但可能漏掉——看漏报和误报哪个代价大")
        L.add("实操一", draw(im, a), "摄像头每一帧都送进模型，框随画面实时更新")


def v55():
    with Lesson("55") as L:
        from ultralytics import YOLO
        m = YOLO(SRC["yolo"])
        cap = cv2.VideoCapture(SRC["class"]); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); shots = []
        picks = {int(n * 0.30) + k * 40 for k in range(3)}
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(n * 0.30) - 60)
        for i in range(int(n * 0.30) - 60, max(picks) + 1):
            ok, f = cap.read()
            if not ok: break
            r = m.track(f, persist=True, classes=[0], verbose=False)[0]
            if i in picks:
                o = f.copy()
                if r.boxes.id is not None:
                    for b, tid in zip(r.boxes.xyxy.numpy().astype(int), r.boxes.id.numpy().astype(int)):
                        cv2.rectangle(o, tuple(b[:2]), tuple(b[2:]), (0, 200, 0), 3)
                        o = text(o, f"ID {tid}", (b[0] + 3, max(b[1] - 32, 2)), 22, (255, 255, 255), (0, 150, 0), 3)
                shots.append((fit(o, w=520), f"第 {i} 帧"))
        L.add("跟踪", row(tagged(shots, 22)), "model.track(persist=True)：同一个人在不同帧里保持同一个 ID（教室录像，实际运行）")
        L.add("实操一", shots[-1][0], "框上显示跟踪 ID")


def v56():
    with Lesson("56") as L:
        ims = trash_imgs("plastic", 8)
        L.add("采集要求", grid([border(cv2.resize(i, (256, 192)), (230, 230, 230), 1) for i in ims], 4, 8),
              "同一类目标：不同角度、背景、光照都要有（trashnet 塑料类样例）")
        im = fit(src("bus"), w=640); r = det(im, classes=[0])
        b = r.boxes.xyxy.numpy().astype(int)[np.argmax(r.boxes.conf.numpy())]
        x1, y1, x2, y2 = b; w, h = x2 - x1, y2 - y1
        crop = lambda o: o[max(y1 - 80, 0):min(y2 + 60, im.shape[0]), max(x1 - 90, 0):min(x2 + 90, im.shape[1])]
        good = im.copy(); cv2.rectangle(good, (x1, y1), (x2, y2), (0, 200, 0), 3)
        loose = im.copy(); cv2.rectangle(loose, (x1 - 60, y1 - 50), (x2 + 60, y2 + 30), (0, 0, 230), 3)
        cut = im.copy(); cv2.rectangle(cut, (x1 + w // 5, y1 + h // 4), (x2 - w // 6, y2), (0, 0, 230), 3)
        L.add("标注规范", row(tagged([(crop(good), "✓ 贴边"), (crop(loose), "✗ 太松"), (crop(cut), "✗ 切掉一部分")], 22)),
              "框要正好贴住目标边缘：太松、切掉、漏标都会教坏模型")


def v57():
    with Lesson("57") as L:
        d = os.path.join(RUN, "sample"); f = glob.glob(os.path.join(d, "*.jpg"))[0]
        im = imread(f); H, W = im.shape[:2]
        c, cx, cy, bw, bh = open(f[:-4] + ".txt").read().split()[:5]
        cx, cy, bw, bh = map(float, (cx, cy, bw, bh))
        x1, y1, x2, y2 = int((cx - bw / 2) * W), int((cy - bh / 2) * H), int((cx + bw / 2) * W), int((cy + bh / 2) * H)
        o = im.copy(); cv2.rectangle(o, (x1, y1), (x2, y2), (0, 200, 0), 6); cv2.circle(o, (int(cx * W), int(cy * H)), 14, (0, 0, 255), -1)
        o = fit(o, h=560)
        info = np.full((560, 720, 3), 255, np.uint8)
        info = text(info, "标签文件里的一行：", (20, 30), 28, (40, 40, 40))
        info = text(info, f"{c}  {cx:.3f}  {cy:.3f}  {bw:.3f}  {bh:.3f}", (20, 90), 32, (255, 255, 255), (55, 42, 31), 8)
        for k, l in enumerate([f"{c}：类别编号（0 = helmet 戴安全帽）", f"{cx:.3f} {cy:.3f}：框中心（红点）÷ 图宽高",
                               f"{bw:.3f} {bh:.3f}：框的宽、高 ÷ 图宽高", f"图片 {W}×{H}，换算成像素：", f"  中心 ({int(cx * W)}, {int(cy * H)})，宽高 {int(bw * W)}×{int(bh * H)}"]):
            info = text(info, l, (20, 180 + k * 62), 24, (40, 40, 40))
        L.add("YOLO 标签格式", row([border(o), info]), "一个框 = 一行 5 个数，全部按图片宽高归一化到 0–1（[AI]安全帽数据集样本，AI 生成图）")
        L.add("实操二", fit(imread(os.path.join(RUN, "check.jpg")), h=620), "画框检查：0 号框都画在戴安全帽的人头上 → 证明 safe.yaml 的类别名写反了")


def v58():
    plt = plt_setup()
    with Lesson("58") as L:
        import csv
        rows = list(csv.DictReader(open(os.path.join(RUN, "results.csv"), encoding="utf-8")))
        ep = [int(r["epoch"]) for r in rows]; g = lambda k: [float(r[k]) for r in rows]
        fig, ax = plt.subplots(1, 2, figsize=(12, 4.2), dpi=110)
        ax[0].plot(ep, g("train/box_loss"), label="训练集 box_loss", color="#0E7C72", lw=2)
        ax[0].plot(ep, g("val/box_loss"), label="验证集 box_loss", color="#F2A900", lw=2)
        ax[0].set_title("损失：越来越低 = 在学习", fontsize=13); ax[0].legend(fontsize=11); ax[0].set_xlabel("轮次 epoch", fontsize=12)
        ax[1].plot(ep, g("metrics/mAP50(B)"), color="#1F2A37", lw=2); ax[1].set_ylim(0, 1)
        ax[1].set_title("验证集 mAP50：越来越高", fontsize=13); ax[1].set_xlabel("轮次 epoch", fontsize=12)
        for a in ax: a.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        L.add("看懂损失曲线", fig2img(fig), "安全帽模型实测曲线（CPU 训练 30 轮）：损失下降、mAP50 上升到约 0.8")
        L.add("实操二", fit(imread(os.path.join(RUN, "results.png")), w=1400), "runs/detect/train/results.png：训练自动生成的全部曲线（本机实测）")
        lab = imread(os.path.join(RUN, "val_batch0_labels.jpg")); pred = imread(os.path.join(RUN, "val_batch0_pred.jpg"))
        L.add("实操一", row(tagged(same([lab, pred], h=520) and list(zip(same([lab, pred], h=520), ["标准答案 labels", "模型预测 pred"])), 22)),
              "训练完对比验证集的标准答案和预测结果")


def v59():
    with Lesson("59") as L:
        cm = imread(os.path.join(RUN, "confusion_matrix.png"))
        L.add("混淆矩阵", fit(cm, h=620), "安全帽模型实测混淆矩阵：对角线是认对的，background 行/列是漏检和误检")
        pr = imread(os.path.join(RUN, "BoxPR_curve.png")); f1 = imread(os.path.join(RUN, "BoxF1_curve.png"))
        L.add("PR 曲线", row(same([pr, f1], h=520)), "左 PR 曲线、右 F1 曲线（ultralytics 8.4 生成的 BoxPR_curve / BoxF1_curve）")
        L.add("实操", row(tagged(list(zip(same([cm, f1], h=480), ["confusion_matrix.png", "BoxF1_curve.png"])), 22)), "model.val() 之后，到 runs/detect/val 里逐张解读")


def v60():
    with Lesson("60") as L:
        L.add("第一步", fit(imread(os.path.join(RUN, "check.jpg")), h=620), "先画框抽查：修正 yaml 后 0 = helmet、1 = no_helmet（数据为 AI 生成图，含水印，出版前替换）")
        L.add("实操一", fit(imread(os.path.join(RUN, "results.png")), w=1400), "实测：CPU 30 轮约 8.4 分钟，mAP50 = 0.80，P = 0.96，R = 0.77")
        pred = imread(os.path.join(RUN, "val_batch0_pred.jpg"))
        L.add("实操二", fit(pred, h=640), "best.pt 在验证集上的预测：helmet / no_helmet 框与置信度")
