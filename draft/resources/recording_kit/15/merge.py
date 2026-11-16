# 第 15 讲 p6 录屏:合并通道的小魔术
# 预期:no_blue 画面偏黄(只剩红+绿);swap 里红草莓变成蓝草莓
import cv2
import numpy as np
img = cv2.imread("fruit.jpg")
b, g, r = cv2.split(img)
zero = np.zeros_like(b)
no_blue = cv2.merge([zero, g, r])
swap = cv2.merge([r, g, b])
cv2.imshow("original", img); cv2.imshow("no_blue", no_blue); cv2.imshow("swap", swap)
cv2.waitKey(0)
