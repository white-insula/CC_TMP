# 第 12 讲 p7 录屏:同一张图存成 jpg 和 png,对比文件大小
# 预期:文件夹里多出 cat_copy.jpg、cat_copy.png;PNG 通常更大(终端也打印出两个大小)
import cv2, os
img = cv2.imread("cat.jpg")
cv2.imwrite("cat_copy.jpg", img)
cv2.imwrite("cat_copy.png", img)
print("jpg:", os.path.getsize("cat_copy.jpg") // 1024, "KB   png:", os.path.getsize("cat_copy.png") // 1024, "KB")
