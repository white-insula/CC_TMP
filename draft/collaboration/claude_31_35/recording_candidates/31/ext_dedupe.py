# -*- coding: utf-8 -*-
"""【扩展，不是 31 讲正式讲解内容】把 np.where 得到的重叠框合并成每个目标一个框。
做法：按分数从高到低取位置，离已保留框太近（小于模板宽高的一半）的就丢掉——一种简化的非极大值抑制。
正式录屏仍用 p7_match_many.py 的原写法，本文件只供课后拓展或老师参考。
"""
import numpy as np


def dedupe(res, thr, tw, th):
    ys, xs = np.where(res >= thr)
    order = np.argsort(-res[ys, xs])
    kept = []
    for i in order:
        x, y = int(xs[i]), int(ys[i])
        if all(abs(x - a) >= tw // 2 or abs(y - b) >= th // 2 for a, b, _ in kept):
            kept.append((x, y, float(res[y, x])))
    return kept
