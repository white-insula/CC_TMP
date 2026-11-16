# 第 24 讲 p7 录屏:直方图均衡化,再试 CLAHE
# 预期:灰蒙蒙的图均衡化后清晰多了,直方图从窄窄一座山铺满横轴
import cv2
import matplotlib.pyplot as plt
gray = cv2.imread("gray_foggy.jpg", 0)
eq = cv2.equalizeHist(gray)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
eq2 = clahe.apply(gray)
cv2.imshow("foggy", gray); cv2.imshow("equalized", eq); cv2.imshow("clahe", eq2)
for im, n in ((gray, "before"), (eq, "equalizeHist")):
    plt.plot(cv2.calcHist([im], [0], None, [256], [0, 256]), label=n)
plt.xlim([0, 256]); plt.legend(); plt.show()
cv2.waitKey(0)
