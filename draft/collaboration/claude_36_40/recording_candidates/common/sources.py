# -*- coding: utf-8 -*-
"""打开画面来源：默认读视频文件；只有显式给出 --camera 编号时才打开摄像头。

后端参数只对摄像头有效：Windows 上可选 dshow（DirectShow）或 msmf（Media Foundation）；
打开视频文件时不传后端参数——36 讲“把 0 换成文件名”时，不要把摄像头专用的 CAP_DSHOW 一起带过去。
"""
import math
import cv2

BACKENDS = {"default": cv2.CAP_ANY, "dshow": cv2.CAP_DSHOW, "msmf": cv2.CAP_MSMF}


def add_source_args(ap, default_input):
    ap.add_argument("--input", default=default_input, help="视频文件（默认是合成测试视频）")
    ap.add_argument("--camera", type=int, default=None, help="摄像头编号；不给就不打开摄像头")
    ap.add_argument("--backend", choices=sorted(BACKENDS), default="default", help="只对摄像头有效")
    return ap


def open_source(args):
    if args.camera is not None:
        return cv2.VideoCapture(args.camera, BACKENDS[args.backend]), f"摄像头 {args.camera}（后端 {args.backend}）"
    return cv2.VideoCapture(args.input), f"视频文件 {args.input}"


def describe(cap):
    """读回实际属性；读不到时 OpenCV 返回 0，原样报告"""
    try:
        backend = cap.getBackendName()
    except cv2.error:
        backend = "未知"
    return {"width": cap.get(cv2.CAP_PROP_FRAME_WIDTH), "height": cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
            "fps": cap.get(cv2.CAP_PROP_FPS), "frame_count": cap.get(cv2.CAP_PROP_FRAME_COUNT), "backend": backend}


def request_size(cap, w, h):
    """37 讲：请求分辨率后读回实际值；set 的返回值和读回值都如实报告（不用 resize 冒充）"""
    ok_w = cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    ok_h = cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    got = (cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return {"requested": (w, h), "set_returned": (ok_w, ok_h), "read_back": got,
            "effective": got == (float(w), float(h))}


def playback_delay(fps, fallback=25.0):
    """36-P7：帧率读不到（≤0、NaN、无穷大）时按示例帧率 25；waitKey 至少等 1 毫秒。
    这只是按标称帧率“近似原速”：实际每帧还要加上读帧、处理、显示的耗时。"""
    if fps is None or not math.isfinite(fps) or fps <= 0:
        fps = fallback
    return max(1, int(1000 / fps)), fps
