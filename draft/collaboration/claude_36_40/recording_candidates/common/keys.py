# -*- coding: utf-8 -*-
"""38 讲：按键 → mode 状态机。没按键时 waitKey(1) & 0xFF 得 255；无关按键不改变 mode。"""
MODE_KEYS = (ord("1"), ord("2"), ord("3"), ord("4"))


def update_mode(mode, key):
    """返回 (新 mode, 是否退出)"""
    if key in MODE_KEYS:
        return key - ord("0"), False
    if key == ord("q"):
        return mode, True
    return mode, False
