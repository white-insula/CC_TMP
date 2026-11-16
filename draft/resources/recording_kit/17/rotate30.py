# 第 17 讲 p8 录屏:绕中心旋转 30 度,再改 -30、再改缩放 0.5
# 预期:rot30 逆时针、四角发黑被裁;rot_minus30 顺时针;rot30_scale05 整张图完整显示、没被裁掉
import cv2
img = cv2.imread("cat.jpg")
h, w = img.shape[:2]
for name, angle, scale in [("rot30", 30, 1.0), ("rot_minus30", -30, 1.0), ("rot30_scale05", 30, 0.5)]:
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, scale)
    rot = cv2.warpAffine(img, M, (w, h))
    cv2.imshow(name, rot)
cv2.waitKey(0)
