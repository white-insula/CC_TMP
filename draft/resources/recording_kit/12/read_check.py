# 第 12 讲 p6 录屏:彩色读、灰度读,读完先判断是否成功
# 预期:两个窗口 color(彩色)和 gray(灰度);把文件名改成 catt.jpg 再运行,打印 None 和“读取失败”
import cv2
img = cv2.imread("cat.jpg")
gray = cv2.imread("cat.jpg", cv2.IMREAD_GRAYSCALE)
if img is None:
    print("读取失败，请检查文件名和路径")
    exit()
cv2.imshow("color", img)
cv2.imshow("gray", gray)
cv2.waitKey(0)
