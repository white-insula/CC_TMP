# -*- coding: utf-8 -*-
NO = "43"
NAME = "人脸检测"
MODULE = "模块六 AI 现成模型：人脸·手·人体"

SEG = [
 ("", "人脸检测", None, "", "片头；PPT1"),

 ("教师加PPT", "课程导入",
  ["相机对焦、美颜、门禁、考勤……", "第一步都是：找到人脸在哪里", "人脸检测：回答“有没有脸、脸在哪”"],
  "大家好，欢迎来到《机器视觉技术应用实践》课程！手机拍照自动对焦到人脸、美颜相机、刷脸门禁、考勤机，它们的第一步都一样：先找到画面里的人脸在哪里。这就是人脸检测，它只回答两个问题：有没有脸，脸在哪。至于这张脸是谁，那是人脸识别的事，我们后面再讲。",
  "教师半身；PPT2"),

 ("PPT", "本讲学习目标",
  ["1. 区分人脸检测与人脸识别", "2. 了解几种常见的人脸检测方案", "3. 会用 OpenCV 自带的 Haar 检测器", "4. 会用 MediaPipe 做实时人脸检测"],
  "本讲的学习目标有四个：第一，分清人脸检测和人脸识别；第二，了解几种常见的人脸检测方案；第三，会用 Open C-V 自带的 Haar 检测器；第四，会用 Media Pipe 做实时人脸检测。",
  "PPT3"),

 ("PPT", "人脸检测的几种常见方案",
  ["传统 Haar 级联（2001 年）：看明暗特征，OpenCV 自带，快但易误检", "深度学习小模型（如 YuNet）：更准，侧脸也能找到", "MediaPipe 轻量检测方案：又准又快，还能同时给出关键点", "演进方向：更准、更快、更能适应侧脸和遮挡"],
  "我们比较几种常见的人脸检测方案。传统方法是二零零一年提出的 Haar 级联，它利用人脸上明暗的规律，比如眼睛比脸颊暗，Open C-V 里就自带了这个检测器，速度快，但容易把别的东西误认成脸。深度学习方法中，Open C-V 支持 YuNet，Media Pipe 也提供轻量检测模型，并能返回眼睛、鼻子等位置。总的方向是：更准、更快、更能适应侧脸和遮挡。",
  "PPT4；Haar、YuNet、MediaPipe 方案对比"),

 ("录屏演示", "实操一：OpenCV 自带的 Haar 检测器",
  ["[ 录屏：加载 haarcascade 模型 → detectMultiScale → 画框 → 观察误检 ]"],
  "先体验传统 Haar 方法。Haar 的模型文件安装 Open C-V 时就自带了，用 c-v-2 点 data 点 haar cascades 加上文件名就能找到。用 cascade classifier 加载它，再对灰度图调用 detect multi scale，它会返回每张脸的 x、y、w、h，用 rectangle 画出来就行。打开摄像头试一下，正脸能找到，可是侧过脸就丢了，有时候背景里的花纹也会被框成人脸，这就是传统 Haar 方法的局限。",
  "录屏1：\n`face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + \"haarcascade_frontalface_default.xml\")`\n`faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)`\n`for (x, y, w, h) in faces: cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)`\n演示正脸、侧脸、误检（参考：[PI]Opencv-facedetection/face_det_opencv.py；YuNet 版见 face_det_opencv_yunet.py）"),

 ("PPT", "MediaPipe 人脸检测的用法",
  ["mp_face = mp.solutions.face_detection", "detector = mp_face.FaceDetection(min_detection_confidence=0.5)", "results = detector.process(rgb)", "results.detections：每张脸一项，没脸时为 None", "框：d.location_data.relative_bounding_box（xmin, ymin, width, height，归一化）", "置信度：d.score[0]"],
  "再看 Media Pipe 的用法。先创建人脸检测器，min detection confidence 是最低置信度，零点五表示把握不到百分之五十的就不要。然后把 R-G-B 图像交给 process 处理，得到 results。results 点 detections 里每张脸是一项，没有脸时是 None。每张脸的框在 relative bounding box 里，包括左上角 x min、y min 和宽、高，都是归一化坐标，要乘以画面的宽高换成像素。置信度在 score 里。",
  "PPT6"),

 ("录屏演示", "实操二：MediaPipe 实时人脸检测",
  ["[ 录屏：创建检测器 → BGR 转 RGB → process → 换算像素坐标 → 画框写置信度 → 统计人数 ]"],
  "下面动手。在摄像头循环里，先把画面转成 R-G-B，交给检测器处理。如果 detections 不是 None，就逐个取出人脸框，把 x min 乘宽、y min 乘高，宽高同样换算，转成整数，画出绿框，并在框上方写上置信度。最后在左上角显示人数，也就是 detections 的个数。运行一下，侧过脸、低下头，框依然稳稳地跟着；叫上同学一起入镜，人数也随之变化。",
  "录屏2：\n`rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)`\n`results = detector.process(rgb)`\n`if results.detections:`\n`    for d in results.detections:`\n`        b = d.location_data.relative_bounding_box`\n`        x, y, bw, bh = int(b.xmin * w), int(b.ymin * h), int(b.width * w), int(b.height * h)`\n`        cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)`\n`        cv2.putText(frame, f\"{d.score[0]:.2f}\", (x, y - 8), ...)`"),

 ("PPT", "人脸检测的应用与规范",
  ["应用：考勤人数统计、相机对焦、自动打码保护隐私", "打码：对人脸区域做强模糊即可", "规范：人脸是敏感个人信息", "课堂实验只用自己或同意者的画面，不随意保存和传播"],
  "人脸检测的应用很多：统计教室里有多少人、相机自动对焦，还有一个很有意义的用途，自动打码保护隐私，找到人脸以后，对这块区域做一次强模糊就行了。最后再强调一次规范：人脸属于敏感的个人信息，课堂实验只使用自己或者经过同意的同学的画面，不要随意保存和传播。",
  "PPT8；自动打码效果图"),

 ("教师加PPT", "内容总结",
  ["检测：有没有脸、在哪；识别：是谁", "方案对比：Haar、YuNet、MediaPipe", "MediaPipe：RGB 输入 → process → detections → 归一化框换算像素", "人脸是敏感信息，合规使用"],
  "我们来总结一下。人脸检测回答有没有脸、在哪里，人脸识别回答是谁；本讲比较了 Haar、YuNet 和 Media Pipe 几种方案；用 Media Pipe 时，输入 R-G-B，调用 process，从 detections 中取出归一化的框，再换算成像素；人脸是敏感信息，一定要合规使用。",
  "教师半身；PPT9"),

 ("教师加PPT", "课后任务",
  ["1. 分别用 Haar 和 MediaPipe 检测，对比侧脸时的效果", "2. 在画面上实时显示人数", "3. 做一个自动打码程序：给检测到的人脸加强模糊"],
  "课后请完成三个任务。第一，分别用 Haar 和 Media Pipe 检测人脸，对比侧脸时谁的效果更好。第二，在画面上实时显示检测到的人数。第三，做一个自动打码程序，给检测到的每张脸加上强模糊，提示一下，可以用高斯滤波，核取得大一些。本讲的内容就到这里！",
  "教师半身；PPT10"),
]
