# 第 14 讲 p7 录屏:在正中央涂一个 50×50 的绿色方块
# 预期:绿色方块正好在图片中央;换一张不同尺寸的图,方块仍居中
import cv2
img = cv2.imread("cat.jpg")
h, w = img.shape[:2]
cy, cx = h // 2, w // 2
img[cy-25:cy+25, cx-25:cx+25] = [0, 255, 0]
cv2.imshow("center", img); cv2.waitKey(0)
