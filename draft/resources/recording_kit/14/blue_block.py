# 第 14 讲 p6 录屏(故意犯错那一步):颜色写成 [255, 0, 0]
# 预期:方块变成蓝色 —— OpenCV 是 B-G-R,红色应写 [0, 0, 255]
import cv2
img = cv2.imread("cat.jpg")
img[100:150, 50:100] = [255, 0, 0]
cv2.imshow("red block", img); cv2.waitKey(0)
