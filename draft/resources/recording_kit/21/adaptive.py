# 第 21 讲 p7 录屏:半边阴影的作业纸,Otsu 失败,自适应阈值成功
# 预期:otsu 窗口里阴影一侧的字看不清或糊成一片;adaptive 窗口里阴影里的字也清清楚楚
import cv2
img = cv2.imread("page_shadow.jpg")     # 左半边在阴影里的作业纸
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ret, b = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
ad = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
cv2.imshow("otsu", b); cv2.imshow("adaptive", ad)
cv2.waitKey(0)
