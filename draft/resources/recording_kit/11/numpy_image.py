# 第 11 讲 p6 录屏:创建一张黑色图像
# 预期:终端输出 <class 'numpy.ndarray'> (300, 400, 3) uint8;弹出黑色窗口(高 300、宽 400)
import cv2
import numpy as np
img = np.zeros((300, 400, 3), dtype=np.uint8)
print(type(img), img.shape, img.dtype)
cv2.imshow("black", img); cv2.waitKey(0)
