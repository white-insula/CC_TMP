# 第 22 讲 p7 录屏:开运算去小白点,闭运算补小黑洞
# 预期:opened 背景小白点全部消失、大目标几乎不变;closed 目标里的小黑洞被填上
import cv2
import numpy as np
kernel = np.ones((5, 5), np.uint8)
noisy_bin = cv2.imread("noisy_bin.png", 0)
hole_bin = cv2.imread("hole_bin.png", 0)
opened = cv2.morphologyEx(noisy_bin, cv2.MORPH_OPEN, kernel)
closed = cv2.morphologyEx(hole_bin, cv2.MORPH_CLOSE, kernel)
cv2.imshow("noisy_bin", noisy_bin); cv2.imshow("opened", opened)
cv2.imshow("hole_bin", hole_bin); cv2.imshow("closed", closed)
cv2.waitKey(0)
