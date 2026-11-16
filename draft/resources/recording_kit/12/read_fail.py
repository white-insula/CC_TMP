# 第 12 讲 p6 录屏(改错文件名的那一步):故意写成 catt.jpg
# 预期:先打印 None,再打印“读取失败，请检查文件名和路径”,程序结束
import cv2
img = cv2.imread("catt.jpg")
print(img)
if img is None:
    print("读取失败，请检查文件名和路径")
    exit()
