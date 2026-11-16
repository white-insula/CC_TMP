# 第 19 讲 p6 录屏:亲眼看见溢出
# 预期:bad 窗口里原本最亮的地方(白色果盘)冒出深色斑块;good 正常整体变亮;打印 [[94]] [[255]]
import cv2
import numpy as np
img = cv2.imread("cat.jpg")
bad = img + 100
good = cv2.add(img, np.full_like(img, 100))
cv2.imshow("original", img); cv2.imshow("bad", bad); cv2.imshow("good", good)
a = np.uint8([[250]]); b = np.uint8([[100]])
print(a + b, cv2.add(a, b))
cv2.waitKey(0)
