# 第 15 讲 p7 录屏:一键转灰度
# 预期:打印 (620, 810, 3) (620, 810);窗口显示黑白照片;文件夹里多出 gray.jpg
import cv2
img = cv2.imread("fruit.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print(img.shape, gray.shape)
cv2.imshow("gray", gray); cv2.waitKey(0)
cv2.imwrite("gray.jpg", gray)
