# 第 13 讲 p7 录屏:查看图像的“身份证”,算出中心和四个角
# 预期:打印 shape、dtype、size;中心和四个角的 BGR 值(位置都由 shape 算出,换图不用改代码)
import cv2
img = cv2.imread("cat.jpg")
print(img.shape, img.dtype, img.size)
h, w = img.shape[:2]
cy, cx = h // 2, w // 2
print("中心:", img[cy, cx])
print("左上:", img[0, 0], "右上:", img[0, w-1])
print("左下:", img[h-1, 0], "右下:", img[h-1, w-1])
