# 第 18 讲 p6 录屏:在黑色画布上画图写字
# 预期:蓝色对角线、绿色空心框、红色实心框、黄色圆、左下角白字 Hello Vision
import cv2
import numpy as np
canvas = np.zeros((400, 600, 3), dtype=np.uint8)
cv2.line(canvas, (0, 0), (599, 399), (255, 0, 0), 3)
cv2.rectangle(canvas, (50, 50), (200, 150), (0, 255, 0), 2)
cv2.rectangle(canvas, (400, 50), (550, 150), (0, 0, 255), -1)
cv2.circle(canvas, (300, 200), 80, (0, 255, 255), 2)
cv2.putText(canvas, "Hello Vision", (50, 370), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
cv2.imshow("canvas", canvas); cv2.waitKey(0)
