# 第 23 讲 p7 录屏:用滑动条实时调 Canny 的两个阈值,按 q 退出
# 预期:拖动 low / high 滑动条,边缘实时变化
import cv2
img = cv2.imread("cat.jpg")
blur = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 0)
cv2.namedWindow("edge")
cv2.createTrackbar("low", "edge", 50, 255, lambda x: None)
cv2.createTrackbar("high", "edge", 150, 255, lambda x: None)
while True:
    lo = cv2.getTrackbarPos("low", "edge"); hi = cv2.getTrackbarPos("high", "edge")
    cv2.imshow("edge", cv2.Canny(blur, lo, hi))
    if cv2.waitKey(30) & 0xFF == ord("q"): break
cv2.destroyAllWindows()
