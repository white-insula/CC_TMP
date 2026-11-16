# 第 25 讲 p7 录屏:用四个角点把斜拍的 A4 纸拉正;再故意交换两个点
# 预期:out 窗口是一张端正的纸;wrong 窗口画面被扭成奇怪的样子
# 四个角:按画图软件读出的实际坐标(本照片 paper.jpg 实测),顺序 左上、右上、右下、左下
import cv2
import numpy as np
img = cv2.imread("paper.jpg")
src = np.float32([[151, 58], [489, 104], [417, 612], [41, 538]])
W, H = 420, 594
dst = np.float32([[0, 0], [W-1, 0], [W-1, H-1], [0, H-1]])
M = cv2.getPerspectiveTransform(src, dst)
out = cv2.warpPerspective(img, M, (W, H))
cv2.imshow("out", out)
wrong = np.float32([[489, 104], [151, 58], [417, 612], [41, 538]])     # 左上、右上互换
cv2.imshow("wrong", cv2.warpPerspective(img, cv2.getPerspectiveTransform(wrong, dst), (W, H)))
cv2.waitKey(0)
