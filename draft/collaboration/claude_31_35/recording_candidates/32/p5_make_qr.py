# -*- coding: utf-8 -*-
# 第 32 讲 P5 录屏：两行代码生成二维码（先在命令行 pip install qrcode）
# 预期：生成 part.png；用手机扫码应显示 PART-2026-0001 | 批次A | 质检合格（手机扫码需在本机实测）
import qrcode
qrcode.make("PART-2026-0001 | 批次A | 质检合格").save("part.png")
