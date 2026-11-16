# 第 24 讲 p6 录屏:计算并画出直方图,对比暗 / 亮 / 正常三张图
# 预期:暗图山峰挤在左边、亮图挤在右边、正常图铺得较开
import cv2
import matplotlib.pyplot as plt
for name in ("gray_dark.jpg", "gray_bright.jpg", "gray_normal.jpg"):
    gray = cv2.imread(name, 0)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    plt.plot(hist, label=name)
plt.xlim([0, 256]); plt.legend(); plt.show()
