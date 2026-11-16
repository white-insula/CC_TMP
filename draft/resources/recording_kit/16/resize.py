# 第 16 讲 p7 录屏:三种缩放
# 预期:打印 (240, 320, 3);三个窗口:a 宽 320 高 240、b 缩小一半、c 宽 400 且不变形
# 再演示:把 (320, 240) 写成 (240, 320),画面被压扁(见 squashed 窗口)
import cv2
img = cv2.imread("cat.jpg")
a = cv2.resize(img, (320, 240)); print(a.shape)
b = cv2.resize(img, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
h, w = img.shape[:2]; new_w = 400; new_h = int(h * new_w / w)
c = cv2.resize(img, (new_w, new_h))
cv2.imshow("a", a); cv2.imshow("b", b); cv2.imshow("c", c)
cv2.imshow("squashed", cv2.resize(img, (240, 320)))
cv2.waitKey(0)
