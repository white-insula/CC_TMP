# 第 23 讲 p6 录屏:Canny(50,150),再改 (20,60)、(100,250),最后去掉高斯滤波
# 预期:(20,60) 边缘多、连纹理都出来;(100,250) 只剩最明显轮廓;不滤波多出很多杂乱小线段
import cv2
img = cv2.imread("cat.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)
for lo, hi in [(50, 150), (20, 60), (100, 250)]:
    cv2.imshow(f"canny_{lo}_{hi}", cv2.Canny(blur, lo, hi))
cv2.imshow("no_blur_50_150", cv2.Canny(gray, 50, 150))
cv2.waitKey(0)
