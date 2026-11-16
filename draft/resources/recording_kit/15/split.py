# 第 15 讲 p5 录屏:拆开三个通道
# 预期:打印 (620, 810, 3) (620, 810);三个黑白窗口 B/G/R —— 红草莓在 R 里很亮、在 B 里很暗
import cv2
img = cv2.imread("fruit.jpg")
b, g, r = cv2.split(img)
print(img.shape, r.shape)
cv2.imshow("B", b); cv2.imshow("G", g); cv2.imshow("R", r)
cv2.waitKey(0)
