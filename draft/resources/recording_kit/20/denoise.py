# 第 20 讲 p6 录屏:撒椒盐噪声,用三种滤波对比
# 预期:均值、高斯只是把噪点抹淡成灰斑;中值滤波几乎把噪点全部清除
import cv2
import numpy as np
img = cv2.imread("cat.jpg")
noisy = img.copy()
rnd = np.random.rand(*img.shape[:2])
noisy[rnd < 0.02] = 0; noisy[rnd > 0.98] = 255
m = cv2.blur(noisy, (5, 5))
g = cv2.GaussianBlur(noisy, (5, 5), 0)
md = cv2.medianBlur(noisy, 5)
cv2.imshow("noisy", noisy); cv2.imshow("blur", m); cv2.imshow("gaussian", g); cv2.imshow("median", md)
cv2.waitKey(0)
