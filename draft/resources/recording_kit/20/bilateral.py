# 第 20 讲 p7 录屏:高斯滤波与双边滤波对比
# 预期:高斯整体变糊;双边滤波表面变光滑、边缘仍清晰
# ⚠ 脚本讲的是“一张人像”(美颜磨皮),这里先用果盘;录屏时换成老师自己的人像照片
import cv2
img = cv2.imread("cat.jpg")
g = cv2.GaussianBlur(img, (9, 9), 0)
bi = cv2.bilateralFilter(img, 9, 75, 75)
cv2.imshow("gaussian", g); cv2.imshow("bilateral", bi)
cv2.waitKey(0)
