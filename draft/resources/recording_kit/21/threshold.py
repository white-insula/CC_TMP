# 第 21 讲 p6 录屏:固定阈值 127、80、180,反向 INV,再用 Otsu
# 预期:80 时字迹变细甚至断开;180 时背景阴影也混进来;INV 变成黑底白字;打印 Otsu 自动找到的阈值
import cv2
img = cv2.imread("page.jpg")            # 只拍纸面的“白纸黑字”照片
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
for t in (127, 80, 180):
    _, b1 = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)
    cv2.imshow(f"thr_{t}", b1)
_, inv = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
cv2.imshow("inv", inv)
ret, b2 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
print("Otsu 阈值:", ret)
cv2.imshow("otsu", b2)
cv2.waitKey(0)
