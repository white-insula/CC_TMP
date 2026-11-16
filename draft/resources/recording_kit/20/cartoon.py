# 第 20 讲 p7 录屏(最后的彩蛋):运行卡通特效示例,按 q 退出
# 来源:[PI]EXP-opencv-edge/edge_cartoon.py;本包改动:摄像头编号提到开头、加了读帧失败判断
import cv2
import numpy as np

CAM = 0          # 摄像头编号:打不开就换 1、2(见第 36 讲排查)
cap = cv2.VideoCapture(CAM)
while True:
    success, img = cap.read()
    if not success:
        print("读不到画面,检查摄像头编号"); break
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.medianBlur(imgGray, 5)
    imgCanny = cv2.Canny(imgBlur, 50, 50)
    color = cv2.bilateralFilter(img, 9, 300, 300)
    img_edge = cv2.cvtColor(255 - imgCanny, cv2.COLOR_GRAY2RGB)
    cartoon = cv2.bitwise_and(color, img_edge)
    cv2.imshow("Cartoon", cartoon)
    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
