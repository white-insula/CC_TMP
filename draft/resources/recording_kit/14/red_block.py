# 第 14 讲 p6 录屏:读一个像素,再把一块涂成红色
# 预期:打印 img[100, 50] 的 BGR 值;窗口里出现红色方块(第 100~149 行、第 50~99 列)
import cv2
img = cv2.imread("cat.jpg")
print(img[100, 50])
img[100:150, 50:100] = [0, 0, 255]
cv2.imshow("red block", img); cv2.waitKey(0)
