# 第 17 讲 p7 录屏:翻转与 90° 旋转
# 预期:h_flip 左右镜像、v_flip 上下颠倒;打印 (620, 810, 3) (810, 620, 3) —— 高宽对调;hv 和 r180 完全一样
import cv2
img = cv2.imread("cat.jpg")
h_flip = cv2.flip(img, 1); v_flip = cv2.flip(img, 0); hv = cv2.flip(img, -1)
r90 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
print(img.shape, r90.shape)
r180 = cv2.rotate(img, cv2.ROTATE_180)
cv2.imshow("h_flip", h_flip); cv2.imshow("v_flip", v_flip); cv2.imshow("hv", hv); cv2.imshow("r180", r180)
print("hv 与 r180 完全一样:", (hv == r180).all())
cv2.waitKey(0)
