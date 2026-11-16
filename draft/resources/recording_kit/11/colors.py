# 第 11 讲 p7 录屏:变成白色、红色,再故意写成 (255, 0, 0)
# 预期:三个窗口 white 白色、red 红色、blue 蓝色(OpenCV 是 B-G-R 顺序)
import cv2
import numpy as np
img = np.zeros((300, 400, 3), dtype=np.uint8)
img[:] = 255
cv2.imshow("white", img.copy())
cv2.moveWindow("white", 40, 180)
img[:] = (0, 0, 255)
cv2.imshow("red", img.copy())
cv2.moveWindow("red", 480, 180)
img[:] = (255, 0, 0)
cv2.imshow("blue", img.copy())
cv2.moveWindow("blue", 920, 180)
cv2.waitKey(0)
