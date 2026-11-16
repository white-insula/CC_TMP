# 第 19 讲 p7 录屏:convertScaleAbs 调亮度和对比度,再修复一张很暗的照片
# 预期:bright 整体变亮;contrast 亮的更亮、暗的更暗;fix 把 dark.jpg 原本看不清的细节找回来
import cv2
img = cv2.imread("cat.jpg")
dark = cv2.imread("dark.jpg")
bright = cv2.convertScaleAbs(img, alpha=1.0, beta=50)
contrast = cv2.convertScaleAbs(img, alpha=1.5, beta=0)
fix = cv2.convertScaleAbs(dark, alpha=1.3, beta=40)
cv2.imshow("bright", bright); cv2.imshow("contrast", contrast)
cv2.imshow("dark", dark); cv2.imshow("fix", fix)
cv2.waitKey(0)
