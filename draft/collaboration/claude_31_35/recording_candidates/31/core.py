# -*- coding: utf-8 -*-
"""第 31 讲 模板匹配：录屏程序与无界面核对共用的核心代码（写法与正式脚本一致）。"""
import cv2
import numpy as np

# 合成电路板上左上那个芯片（含上下引脚）的位置，用于裁模板：x, y, w, h
DEFAULT_CROP = (56, 50, 98, 80)


def load(path, flag=cv2.IMREAD_COLOR):
    img = cv2.imread(path, flag)
    if img is None:
        raise SystemExit(f"读不到图片：{path}（检查文件名和路径）")
    return img


def match(gray, tpl):
    """31-P6：大图、模板都是单通道灰度 uint8；TM_CCOEFF_NORMED 要求模板不是纯色（方差不为 0）"""
    assert gray.ndim == 2 and tpl.ndim == 2 and gray.dtype == tpl.dtype == np.uint8
    assert float(tpl.std()) > 0, "模板是纯色，TM_CCOEFF_NORMED 无法比较"
    res = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    return res, max_val, max_loc


def where_boxes(res, thr):
    """31-P7：脚本原写法 np.where(res >= 阈值)，每个位置一个框（不去重）"""
    ys, xs = np.where(res >= thr)
    return list(zip(xs, ys))
