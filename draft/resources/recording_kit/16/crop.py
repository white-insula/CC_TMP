# 第 16 讲 p6 录屏:裁剪出一块区域(坐标先用画图软件读出)
# 预期:打印 (170, 200, 3) —— 高 170、宽 200,正好是两个坐标之差;窗口显示裁出的那一块,保存 roi.jpg
import cv2
img = cv2.imread("cat.jpg")
roi = img[80:250, 100:300]
print(roi.shape)
cv2.imshow("roi", roi); cv2.imwrite("roi.jpg", roi)
cv2.waitKey(0)
