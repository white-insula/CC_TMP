# 第 22 讲 p6 录屏:腐蚀与膨胀,各 1 次和 3 次
# 预期:腐蚀 1 次字变细,3 次有的笔画断了;膨胀 1 次字变粗,3 次糊成一团
import cv2
import numpy as np
binary = cv2.imread("text_binary.png", 0)
kernel = np.ones((5, 5), np.uint8)
e1 = cv2.erode(binary, kernel, iterations=1)
e3 = cv2.erode(binary, kernel, iterations=3)
d1 = cv2.dilate(binary, kernel, iterations=1)
d3 = cv2.dilate(binary, kernel, iterations=3)
for n, im in [("binary", binary), ("erode1", e1), ("erode3", e3), ("dilate1", d1), ("dilate3", d3)]:
    cv2.imshow(n, im)
cv2.waitKey(0)
