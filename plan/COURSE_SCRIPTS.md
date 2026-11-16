# 在线课 · 知识点方案与脚本生产规范(COURSE_SCRIPTS)

> 2026-11-05 建。《机器视觉技术应用实践》智慧课程的**微视频脚本 + PPT** 生产蓝图。
> 仿《Linux基础》在线课(`E:\《Linux基础》在线课（负责人：张于思）\in\`)口径:**一个知识点 = 一个脚本 + 一份 PPT = 一个微课**。
> 已定决策(2026-11-05):① 按知识点切,**独立微课 ≥80**(本方案 87 个,不靠录屏片段凑数);② 综合项目 = **工业分拣/质检(简化)**;③ **本轮只出脚本 + PPT,暂不产 demo 代码**;④ 案例优先复用教师已有教学素材(见三)。

---

## 一、生产规范(每个脚本都要满足)

> ### ⭐ 总原则(2026-11-10,用户强调):课程脚本是一切工作的起点
> `NN/content.py` 一改,**下游所有关联资源都必须检查并同步更新**,不能只改直接生成物。下游链:
> `content.py` → `脚本NN.docx` / `NN-*.pptx` / `素材需求.md`(`_lib.py NN`)→ `素材需求汇总.md`(`_todo_summary.py`)→ `全部微课脚本汇总.docx`(`_merge.py`)→ `stu_work/PPT_collection/` 拷贝 + `.zip` → 配图(`_visuals/`)→ 教材正文与插图(`tools/collect_figures.py`)→ 定稿阅读页(`tools/build_reading_html.py`)→ `OUTLINE.md`/本文件记录。
> **手工素材(找的图/截图/录屏/动画)一律走 `draft/online_course/manual/`**:`NN-pP-类型-简述` 命名 + `素材登记.csv` 登记,审核「通过」才由 `_manual.py` 自动接入 PPT;**不再手改 PPT**;示意图以程序画(`_visuals/`)为主。说明见 `manual/README.md`。
> **每次改完跑 `python _sync_check.py`**,逐环报告 ✅/❌/⚠️;教材正文的语义一致性需人工对照。教师手动插进 PPT 的图在流程外(`stu_work/PPT_collection/PPT_collection/` 与 `.rar`),重新生成会丢 → 要审查后登记进 `_visuals/` 或 `VIS`。

1. **开场**统一:「大家好，欢迎来到《机器视觉技术应用实践》课程！」
2. **结尾**统一:「本讲的内容就到这里！」
3. **数字人 + TTS** 适配:解说词口语化;英文缩写/函数名按念法写(`Open C-V`、`im read`、`B-G-R`、`Y-O-L-O`);少括号少符号。
4. **按时长控制,不卡死字数**:每节最佳 **3–5 分钟**(按 TTS 约 250 字/分钟估算 ≈ 750–1250 字);个别内容确实多的可适度超出(≤6 分钟左右),**不为压字数砍掉必要内容**。语速待拿到数字人成片后实测校准。镜头表四列:序号 / 镜头 / 解说词 / 画面。
5. **PPT 版式 v2**(2026-11-05,第 21 节样板):仍以 Linux 课 pptx 为母版,改 **16:9**;版式由 `_ppt.py` 按页型自动画(封面 / 学习目标卡片 / 图文讲解 / 录屏演示深色页 / 总结卡片 / 课后任务);每页 = 脚本里一个镜头。配图:每节 `NN/visuals.py` 用 OpenCV 实际运行生成 → `NN/img/`,在 content.py 的 `VIS = {slide标题: (图, 图注)}` 登记;未配的素材自动列入 `NN/素材需求.md`(全课约 118 条待找)。检查用 `_render.py`(本机 PowerPoint 导出 PNG)。
6. **实操类**脚本的录屏镜头:「画面」列写清录屏要演示的操作步骤与关键代码行,并注明可复用的素材文件,供后续补 demo 与录屏;**本轮不产 demo 代码**。
8. **课程统一环境**(2026-11-05 定):Python 3.11 + **`opencv-contrib-python==4.11.0.86`(完整版,第 06 讲先单独安装;第 52 讲因 ultralytics 依赖会引入同版本基础包,按两条命令安装并最后重装 contrib,保证实际加载完整版;不要分别随意升级两包)** + `mediapipe==0.10.21`(用 `mp.solutions` 经典接口,与教师素材一致)。完整版含 `cv2.face`(45 讲 LBPH)且为 MediaPipe 的依赖。**⚠️ 版本约束(2026-11-05 实测)**:mediapipe 0.10.21 要求 `protobuf<5`,而最新 onnx(1.23)要求 protobuf≥6.31,二者冲突;ultralytics 导出 ONNX 时若自动装 onnx 会把 protobuf 升上去、MediaPipe 立即报错。统一钉死 **`onnx==1.17.0` + `protobuf>=4.25.3,<5`**(已验证 MediaPipe 手部识别 + YOLO 导出 ONNX + ONNX 推理同时可用,`pip check` 无冲突),写入 85 讲。
7. 生产方式沿用 ch02 的 `_build.py`:内容只定义一次 → 同时生成 PPT + TTS 脚本 docx。

**产物命名**(沿 Linux 课规范,交付件用中文名):
```
draft/online_course/NN/
  ├── 脚本NN-<知识点名>.docx
  ├── NN-<知识点名>.pptx
  └── _build.py
```

---

## 二、知识点总表(10 模块 · 87 个)

素材缩写:**[OC]** = `E:\teaching\openCV\` · **[PI]** = `E:\teaching\Linux for Raspi\references\example_code\python-raspberry-pi-bilibili\` · **[PIref]** = `E:\teaching\Linux for Raspi\references\`

| 模块 | # | 知识点名称 | 知识点说明 | 类型 | 参考素材 |
|---|---|---|---|---|---|
| **模块一 走进机器视觉** | 01 | 什么是机器视觉 | 定义;人眼 vs 机器视觉;为什么需要机器视觉 | 理论 | |
| | 02 | 机器视觉的发展与产业现状 | 发展简史;产业链;国产厂商(海康等)崛起;岗位方向 | 理论 | |
| | 03 | 典型应用(一):工业制造 | 四大任务:识别、测量、定位、检测;质检/分拣/引导案例 | 理论 | |
| | 04 | 典型应用(二):生活与交通 | 人脸识别、车牌/二维码、自动驾驶、垃圾分类、坐姿监测、自动阅卷 | 理论 | [OC]lajifenlei_demo、Body_Detct;[GA]成果展示.mp4(作演示画面) |
| | 05 | 机器视觉系统的组成 | 光源 → 镜头 → 相机 → 处理器 → 算法 → 执行 | 理论 | |
| | 06 | 开发环境搭建 | 安装 Python、VS Code、pip 换源、安装 OpenCV | 理论+实操 | |
| | 07 | 第一个视觉程序 | 打印版本;读图显示;运行与常见报错 | 理论+实操 | [PI]EXP-Base-Opencv/img_read_show.py |
| **模块二 图像的秘密** | 08 | 像素与数字图像 | 像素;图像=数字矩阵;灰度 0–255 | 理论 | ch02 教材 |
| | 09 | 分辨率与图像文件格式 | 分辨率与数据量;JPG/PNG/BMP;有损与无损压缩 | 理论 | ch02 教材 |
| | 10 | 颜色模型与通道 | RGB 三原色;通道;⚠️OpenCV 的 BGR 顺序 | 理论 | ch02 教材 |
| | 11 | NumPy 数组:图像的数据容器 | ndarray;shape/dtype;创建全黑/全白图像 | 理论+实操 | |
| | 12 | 图像的读取、显示与保存 | imread / imshow+waitKey / imwrite;读图失败排查 | 理论+实操 | ch02 教材实验 1 |
| | 13 | 图像的坐标系与身份信息 | 原点左上;(高,宽,通道);img[y,x];用 shape 算中心/四角 | 理论+实操 | ch02 教材 2.4 |
| | 14 | 访问与修改像素 | 读改单个像素;切片批量改一块区域;BGR 坑现场演示 | 理论+实操 | ch02 教材实验 4 |
| | 15 | 通道拆分与灰度转换 | split / merge;cvtColor 转灰度;为何先转灰度 | 理论+实操 | ch02 教材实验 5、6 |
| **模块三 图像处理基础** | 16 | 图像的裁剪与缩放 | ROI 切片;resize 与插值;按比例缩放 | 理论+实操 | [PI]EXP-Base-Opencv/img_resize_crop.py |
| | 17 | 图像的翻转与旋转 | flip;rotate;getRotationMatrix2D + warpAffine | 理论+实操 | |
| | 18 | 在图像上画图写字 | line / rectangle / circle / putText;用 PIL 显示中文 | 理论+实操 | [PI]EXP-Base-Opencv/opencv_draw.py;[OC]put_chinese_text 函数 |
| | 19 | 亮度与对比度调整 | 像素加减乘;⚠️uint8 溢出;convertScaleAbs | 理论+实操 | |
| | 20 | 图像滤波与去噪 | 噪声来源;均值 / 高斯 / 中值 / 双边滤波对比 | 理论+实操 | [PI]EXP-opencv-edge/edge_cartoon.py |
| | 21 | 阈值分割与二值化 | threshold;Otsu 自动阈值;自适应阈值 | 理论+实操 | [OC]recognize_anwser_sheet/src/core/image_processor.py |
| | 22 | 形态学操作 | 腐蚀 / 膨胀 / 开运算 / 闭运算;去小噪点、补小洞 | 理论+实操 | [PI]EXP-Opencv-Scan/scan.py(preProcessing) |
| | 23 | 边缘检测 | 边缘是什么;Canny 及其两个阈值;滑块调参;卡通特效 | 理论+实操 | [PI]EXP-opencv-edge/edge.py、edge_cartoon.py |
| | 24 | 图像直方图与均衡化 | calcHist 画直方图;equalizeHist 增强暗图 | 理论+实操 | |
| | 25 | 透视变换:文档扫描矫正 | 手动读四角坐标 → 按序对应 → getPerspectiveTransform → 拉正 | 理论+实操 | [PI]EXP-Opencv-Scan/scan.py;[OC]perspective_corrector.py |
| **模块四 颜色与形状识别** | 26 | HSV 颜色空间 | H/S/V 含义;为何用 HSV 识色;OpenCV 中 H 为 0–179;滑块取色 | 理论+实操 | |
| | 27 | 颜色提取与掩膜 | inRange;红色两段 H;bitwise_and 抠色 | 理论+实操 | |
| | 28 | 轮廓的查找与绘制 | findContours;drawContours;外轮廓 vs 全部轮廓 | 理论+实操 | [PI]EXP-OpenCV-shape/shape.py |
| | 29 | 轮廓特征:面积、周长与外接框 | contourArea / arcLength / boundingRect / 中心点;按面积过滤 | 理论+实操 | [PI]EXP-OpenCV-shape/shape.py |
| | 30 | 形状识别 | approxPolyDP 角点数 → 三角形/矩形/圆 | 理论+实操 | [PI]EXP-OpenCV-shape/shape.py、EXP-shape-detection/shape_det.py |
| | 31 | 模板匹配 | matchTemplate;找图中图;阈值与多目标 | 理论+实操 | |
| | 32 | 二维码的生成与识别 | qrcode 生成;QRCodeDetector 扫描;工业追溯应用 | 理论+实操 | [PI]EXP-QRcode/QRcode_creat.py、QRcode_scan.py |
| | 33 | 单元案例:颜色形状分拣(图片版) | HSV + 轮廓 + 形状 → 给每个物体标注颜色与形状 | 综合实践 | |
| | 34 | 单元案例:答题卡识别(单张) | 定位 → 透视矫正 → 二值化 → 按格统计涂黑像素 → 判答案 → 红色标错 | 综合实践 | [GA]代码集/utils/opencv_utils.py、答题卡模板;[OC]recognize_anwser_sheet |
| | 35 | 单元案例:批量阅卷与成绩导出 | 遍历文件夹批量识别;读标准答案与分值(答案.txt);openpyxl 写成绩单;学生毕设成果展示 | 综合实践 | [GA]答题卡扫描文件(40 张)、答案.txt、成绩单.xlsx、成果展示.mp4 |
| **模块五 让摄像头动起来** | 36 | 打开摄像头与视频文件 | VideoCapture;帧循环;release;打不开排查 | 理论+实操 | [PI]EXP-Base-Opencv/video_read_show.py;[OC]Finger_Guess_Game/1_load_video.py |
| | 37 | 视频的逐帧处理 | 视频=连续的帧;把图片处理套到每一帧 | 理论+实操 | |
| | 38 | 键盘交互与实时特效 | waitKey 键值;按键切换 灰度/边缘/卡通 | 理论+实操 | [PI]EXP-opencv-edge/edge_cartoon.py |
| | 39 | 帧率计算与性能观察 | FPS 计算与显示;分辨率对帧率的影响 | 理论+实操 | |
| | 40 | 视频录制与截图保存 | VideoWriter 与编码器;按键开始/停止录像;截图 | 理论+实操 | [OC]Finger_Guess_Game/0_record_video.py |
| | 41 | 单元案例:实时颜色追踪 | 33 的方法搬到实时视频;追踪框 + 中心轨迹 | 综合实践 | |
| **模块六 AI 现成模型:人脸·手·人体** | 42 | 预训练模型与 MediaPipe | 什么是预训练模型;MediaPipe 能做什么;安装 | 理论 | |
| | 43 | 人脸检测 | Haar、YuNet、MediaPipe 方案对比;实时人脸框 | 理论+实操 | [PI]Opencv-facedetection/*;[PIref]models/opencv_face_detection |
| | 44 | 人脸关键点与疲劳检测 | 人脸网格关键点;眼睛纵横比 EAR → 闭眼;嘴部张合 → 打哈欠;驾驶疲劳应用 | 理论+实操 | [PI]Opencv-eye-blink/dlib_blinks.py、Opencv-facedetection/dlib_landmarks.py;[AI]论文《机器视觉驾驶疲劳度检测模型的开发与实现研究》 |
| | 45 | 人脸识别:认出是谁 | 检测≠识别;采集人脸 → 训练 LBPH → 识别姓名 | 理论+实操 | [PI]OPencv-face-recognition/* |
| | 46 | 手部关键点检测 | 21 个关键点编号;归一化坐标 → 像素坐标;数手指 | 理论+实操 | [OC]Finger_Guess_Game/2_single_hand_recognition |
| | 47 | 人体姿态估计 | 33 个姿态点;关节角度计算;判断举手 | 理论+实操 | [OC]Body_Detct/0_body_detect.py |
| | 48 | 单元案例:石头剪刀布猜拳游戏 | 双手识别 → 手势判定 → 定格 → 判胜负 | 综合实践 | [OC]Finger_Guess_Game/3、4 |
| | 49 | 单元案例:坐姿健康监测 | 颈部/腰部角度 → 坐姿评估 → 提醒 | 综合实践 | [OC]Body_Detct/1_、2_posture_monitor.py |
| **模块七 物体检测:YOLO** | 50 | 深度学习入门 | 从规则到学习;神经网络直观理解;训练与推理(无公式) | 理论 | |
| | 51 | 分类、检测与分割 | 三类任务对比;边框/类别/置信度;垃圾分类=分类任务 | 理论 | [OC]lajifenlei_demo(分类演示) |
| | 52 | 认识 YOLO 与环境安装 | YOLO 为何快;ultralytics 安装;yolov8n 权重;COCO 80 类 | 理论+实操 | |
| | 53 | 图片目标检测与结果解读 | 推理;boxes.xyxy / cls / conf;自己画框 | 理论+实操 | |
| | 54 | 实时检测与结果筛选 | 摄像头实时检测;置信度阈值;只看某一类 | 理论+实操 | |
| | 55 | 目标跟踪与越线计数 | model.track;跟踪 ID;越线计数思路 | 理论+实操 | |
| | 56 | 数据采集与标注 | 采集原则(合法/客观/可靠/相关)与数据安全;定时采图;标注工具(LabelMe/X-AnyLabeling);标注规范 | 理论+实操 | [PI]EXP-ONNX/img_collection.py |
| | 57 | 标注格式转换与数据集整理 | LabelMe JSON → YOLO txt;训练/验证划分;data.yaml | 理论+实操 | [PI]EXP-ONNX/lablemetoyolo.py、dic_lab.py |
| | 58 | 训练自己的 YOLO 模型 | 训练命令与超参数(epochs/batch/imgsz);看懂 loss 曲线;过拟合与早停 | 理论+实操 | [AI]二级实操 yolov5 训练 |
| | 59 | 模型评估:看懂混淆矩阵与 PR 曲线 | 精确率/召回率/F1/mAP 直观含义;混淆矩阵;PR 曲线;验证集预测对比 | 理论+实操 | [AI]二级实操「验证图片检测结果」(confusion_matrix / PR / F1 曲线) |
| | 60 | 单元案例:安全帽佩戴检测 | 现成安全帽数据集 → 训练 → 评估 → 视频检测;工地安全应用 | 综合实践 | [AI]一级实操/提交/datasets-安全帽.zip(含 safe.yaml);[PI]EXP-ONNX 流程 |
| **模块八 综合项目:工业分拣与质检** | 61 | 项目需求分析与方案设计 | 流水线分拣场景;输入/输出;模块拆分;技术选型 | 理论 | |
| | 62 | 检测环境搭建:光源与相机摆放 | 固定相机、背景、打光;为何环境决定成败 | 理论+实操 | |
| | 63 | 图像采集与预处理 | 检测区 ROI;去噪;二值化;参数集中管理 | 理论+实操 | |
| | 64 | 按颜色分拣工件 | 多颜色 HSV 判定;分拣结果输出 | 理论+实操 | |
| | 65 | 尺寸测量与合格判定 | 像素 → 毫米标定;外接框尺寸;公差判定 | 理论+实操 | |
| | 66 | 形状缺陷检测 | 形状匹配 / 面积差异 → 缺角、变形判定 | 理论+实操 | [PI]EXP-shape-detection/shape_det.py |
| | 67 | 训练并引入工件识别模型 | 按 56–60 流程训练工件模型;传统方法与深度学习结合 | 理论+实操 | |
| | 68 | 结果输出与统计记录 | 画面叠加结果;分类计数;写 CSV 记录 | 理论+实操 | [OC]recognize_anwser_sheet(CSV/JSON 导出) |
| | 69 | 系统整合与演示 | 主循环整合;联调排错;项目演示与说明 | 综合实践 | |
| **模块九 走近工业相机:海康设备** | 70 | 认识海康威视与视觉产品线 | 网络摄像机 / 工业相机 / 智能相机 / VM 平台;适用场景 | 理论 | |
| | 71 | 工业镜头与光源选型基础 | 焦距、视野、工作距离;常见光源与打光方式 | 理论 | |
| | 72 | 网络摄像机配置与 RTSP 地址 | 激活与 IP 配置;用户名/密码/通道/主子码流;RTSP 地址构造 | 理论+实操 | [OC]RTSP_Test/RTSP.py |
| | 73 | OpenCV 接入 RTSP 视频流 | VideoCapture 取流;延迟与丢帧;断线重连;录像 | 理论+实操 | [OC]RTSP_Test/RTSP.py、Body_Detct/rtsp_recorder.py |
| | 74 | 在网络摄像机画面上跑识别 | RTSP 画面 + YOLO / MediaPipe 实时识别 | 理论+实操 | [OC]Body_Detct/1_posture_monitor.py(RTSP 输入) |
| | 75 | 工业相机基础:接口与快门 | GigE / USB3;全局 vs 卷帘快门;与普通摄像头对比 | 理论 | |
| | 76 | 工业相机参数:曝光、增益与触发 | 曝光与运动模糊;增益与噪声;软/硬触发 | 理论+实操 | |
| | 77 | MVS 客户端与 SDK 取图 | MVS 安装与预览;SDK 取一帧 → numpy → OpenCV | 理论+实操 | |
| | 78 | 海康 VM 算法平台初识 | 图形化拖拽式视觉方案;与写代码方式的对比 | 理论+实操 | |
| | 79 | 单元案例:工业相机接入分拣系统 | 把 69 的输入源换成海康工业相机 | 综合实践 | |
| **模块十 搬上树莓派** | 80 | 认识树莓派与系统准备 | 树莓派简介;烧录系统;联网;固定 IP | 理论+实操 | [PIref]textbooks/raspberry-pi-beginners-guide-zh-cn;[PI]多wifi固定IP |
| | 81 | 远程登录与文件传输 | SSH / VNC;scp 传文件 | 理论+实操 | |
| | 82 | 树莓派安装 OpenCV 与 MediaPipe | apt / pip 安装;版本验证;常见问题 | 理论+实操 | [PI]EXP-Base-Opencv/树莓派-OPenCV的安装.pdf、OpenCV+Mediapipe安装全过程 |
| | 83 | 接入 USB 与 CSI 摄像头 | 两类摄像头连接与测试;取流 | 理论+实操 | |
| | 84 | 网页远程查看画面 | Flask 推送视频流;手机/电脑浏览器看实时识别结果 | 理论+实操 | [PI]EXP-FLASK(视频监控/视频特效) |
| | 85 | 性能优化与 ONNX 轻量部署 | 降分辨率、跳帧;导出 ONNX;轻量模型 FPS 对比 | 理论+实操 | [PI]EXP-ONNX、EXP-yolov5-lite |
| | 86 | GPIO 输出:用灯和蜂鸣器报结果 | GPIO 基础;LED / 蜂鸣器 / PWM;识别结果驱动硬件 | 理论+实操 | [PI]PWM-LED、PWM-Buzzer、EXP-mediapipe_gesture |
| | 87 | 单元案例:树莓派分拣质检终端 | 把 69 部署到 Pi,开机自启,结果用灯光/蜂鸣器报警,脱离电脑运行 | 综合实践 | [PI]EXP-shape-detection(形状检测+LCD) |

**统计**:10 模块 / 87 个;理论 15 · 理论+实操 58 · 综合实践 14。比 ≥80 下限多 7 个,可删可调。

---

## 三、素材复用说明(2026-11-05 盘点)

| 素材 | 内容 | 用在 |
|---|---|---|
| [GA]学生毕设·答题卡识别系统 | 40 张真实扫描卡 → 批量识别 → Excel 成绩单,红色标错;PyQt 界面;成果展示视频;论文与答辩 PPT(⚠️原环境 Py3.8 + OpenCV 4.5,录屏前需在新环境验证) | 34、35;04 演示画面 |
| [OC]recognize_anwser_sheet | 答题卡识别(四角定位 → 透视矫正 → 二值化 → 判答案 → CSV/JSON 导出,tkinter 界面) | 21、25、34、68 |
| [OC]Finger_Guess_Game | 录像 → 读视频 → 单手/双手识别 → 猜拳游戏,0–4 步递进 | 36、40、46、48 |
| [OC]Body_Detct | MediaPipe 姿态 → 坐姿监测(颈/腰角度);RTSP 录像 | 47、49、72、73 |
| [OC]RTSP_Test | RTSP 视频流查看器(tkinter) | 71、72 |
| [OC]4_Quadrants_of_Emotion | 人脸情绪四象限演示 | 04 演示画面(⚠️情绪判定为特征规则,不作正式知识点) |
| [OC]lajifenlei_demo | 浏览器端垃圾分类(TF.js,React 网页) | 04、51 演示画面 |
| [PI]EXP-Base-Opencv / edge / Scan / shape / QRcode | OpenCV 基础、边缘与卡通、文档扫描、形状检测、二维码 | 07、16–25、28–32 |
| [PI]Opencv-facedetection / eye-blink / face-recognition | Haar/SSD/YuNet 人脸检测、dlib 眨眼、LBPH 人脸识别 | 43、44、45 |
| [PI]EXP-ONNX / yolov5-lite | 采图 → LabelMe → YOLO 格式 → 训练 → ONNX 在 Pi 上推理 + 灯/蜂鸣器 | 56–60、85、86 |
| [PI]EXP-FLASK / PWM-* / mediapipe_gesture | 网页视频监控、PWM 灯与蜂鸣器、手势控硬件 | 84、86 |

| [AI]人工智能训练师(二级/一级) | 职业技能等级考试:理论样题、YOLOv5 训练实操、评估图表、安全帽数据集、疲劳检测论文 | 44、56–60;**作为职业标准对标依据**(补 METHOD 缺口④) |

- ⚠️ **[AI]安全帽数据集 safe.yaml 类别写反**(2026-11-05 画框核实):实际 0=戴安全帽、1=未戴(与 classes.txt 的 wear/no_wear 一致),yaml 却写 0: no_mask / 1: mask(照抄口罩模板)。57 讲作反面案例,60 讲用修正后的 helmet.yaml。另:该集仅 50 张且为 AI 生成图(带“豆包AI生成”水印),出版用图需注意。

**注意**:
- [PI] 素材基于 **树莓派 3B + bullseye(armhf) + RPi.GPIO**;课程若用 Pi 4B/新系统,写脚本时按新环境口径讲,素材只作流程参考。
- [OC] 素材中的网络摄像机**为海康威视**(2026-11-05 确认),RTSP 写作 `rtsp://admin:***@IP:554/stream1`;模块九同时讲海康标准格式 `/Streaming/Channels/101`(主码流)/`102`(子码流)与该简写形式。**手上有海康设备可录屏**(2026-11-05 确认)。
- 素材里的账号密码**不得出现在脚本/PPT 画面中**,录屏时须打码或改为示例值。

---

## 四、与指标/教材的关系

- **微视频 ≥80**:87 个独立微课即达标,不依赖录屏片段计数。
- **教材章节需同步扩展**:原 OUTLINE 第 3 章「玩转图像处理」拆为 **模块三 图像处理基础 + 模块四 颜色与形状识别**,教材由 9 章变为 **10 章**(其后章号顺延);新增点需补进 `OUTLINE.md`。
- **ch02 旧脚本**(原 `draft/online_course/ch02/`,单脚本 2186 字;现已移入 `abandon/`)→ 拆入 08–15 重做,旧件保留作参照。
- **顺序取舍**:脚本先于教材正文,直接依据本表;教材正文后补时**以脚本为准对齐**。

## 五、生产进度

| 模块 | 一 | 二 | 三 | 四 | 五 | 六 | 七 | 八 | 九 | 十 |
|---|---|---|---|---|---|---|---|---|---|---|
| 个数 | 7 | 8 | 10 | 10 | 6 | 8 | 11 | 9 | 10 | 8 |
| 脚本+PPT | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| demo 代码 | 后补 | 后补 | 后补 | 后补 | 后补 | 后补 | 后补 | 后补 | 后补 | 后补 |

## 六、完成情况(2026-11-05)

- **87 节脚本 + PPT 全部生成**(`draft/online_course/NN/`):总时长估算约 429 分钟(≈7.2 小时),均 4.9 分钟/节,范围 3.6–6.0,无超 6 分钟。
- **本机实测验证过的代码**:OpenCV 各函数(19 讲 cv2.add 一维数组坑已修正)、颜色形状分拣逻辑、凸度/圆度/matchShapes(66 讲圆度实测约 0.89 已修正说法)、LBPH、录像、pointPolygonTest;**YOLO**(ultralytics 8.4.202):检测/COCO 编号/track/训练/val/ONNX 导出与推理均跑通。
- **未能本机验证(需真实设备,录屏前必须实跑)**:MediaPipe 实时人脸/手/姿态(42–49)、海康 RTSP/MVS SDK/VM(72–79)、树莓派 Picamera2/GPIO/systemd(80–87)。
- **安全帽实训跑通记录**:`draft/online_course/assets/60_helmet_run/`(修正后 helmet.yaml、训练曲线、混淆矩阵、PR/F1 曲线、验证对比图、标签画框核查图 check.jpg、训练脚本)。CPU 30 轮 ≈8.4 分钟,mAP50 0.80。
- **环境注意**:清华 pip 镜像在本机两次 403 → 06 讲已加"换阿里云源"兜底;ultralytics 首次 track/export 会自动联网装依赖(lap / onnx 等),课前预装。
- **下一步**:PPT 版式升级(页面类型 + 程序生成效果图 + 外找图片清单,见对话中三层方案);教材正文按 10 章结构同步 OUTLINE。

## 七、PPT v2 全量生成与配图(2026-11-05)

- **87 节全部按 v2 版式重新生成**(16:9,用户确认样板与配色)。配图:**59 节 / 179 张**,全部由 `_visuals/m2–m8.py` 用 OpenCV / MediaPipe / YOLO **实际运行**生成,登记在 `NN/img/vis.json`(第 21 节在 content.py 的 `VIS`)。重新生成:`python _visuals/run.py all|m3|08` → `python _lib.py all`;总览检查:`python _visuals/sheet.py out.jpg 08 09 …`。
- **待找素材 109 条** → `draft/online_course/素材需求汇总.md`:主要是模块一(行业/应用实拍)、模块九(海康设备与软件界面)、模块十(树莓派实物与接线)、各节"教师半身/录屏"之外的照片、动画需求,以及第 48 讲需**教师正对镜头重录石头/剪刀/布**(现有视频手势多为侧向,判定结果会误导,已不配图)。第 67 讲需真实训练的工件模型,暂不配。
- **素材来源**:ultralytics 示例图 bus.jpg、[PI] shapes.png / paper.jpg / test.mp4、[OC] 教师自录手势视频 + 教室坐姿录像、trashnet(MIT)、[GA] 学生毕设答题卡(只裁答题区/遮挡姓名栏)、安全帽实测训练结果、课程合成场景(纸张、工件、红球)。⚠️ **出版前需确认**:教师/学生肖像授权、安全帽 AI 生成图(带水印)替换、bus.jpg 版权(ultralytics 仓库 AGPL,图片来源待核)。
- **配图过程中发现并修正的脚本问题**:
  1. **第 64 讲判色 bug**:原脚本 `cv2.mean(hsv, mask)` 直接平均 H——红色像素 H 分布在 0 附近和 179 附近,平均成 ~90,红色会被认错(实测复现)。改为**先平均 BGR、再转 HSV**,并写进解说词作为知识点。
  2. **环境冲突**:onnx 1.23 要求 protobuf≥6.31,mediapipe 0.10.21 要求 protobuf<5;ultralytics 导出 ONNX 时自动装最新 onnx 会让 MediaPipe 报 `FieldDescriptor ... label`。钉死 `onnx==1.17.0` + `protobuf<5`(本机验证三者共存),写入一、8 与第 85 讲。
  3. 第 59 讲录屏要点文件名(PR_curve → BoxPR_curve)。
- 配图中如实呈现、不美化的地方:Haar 漏检、Otsu 在阴影下失败、模板匹配在缩放/旋转后相似度 0.39/0.35、帧率为本机实测(i7-1165G7)。


## 八、模块二(08–15)整改 · 配合 ch02 定稿(2026-11-10)

- **换底图**:模块二配图原用 `bus.jpg`(含可识别路人正脸、来源待核)→ 改用 `assets/fruit_ai_doubao.png`(豆包 AI 生成果盘,无人脸,红绿蓝三色鲜明);裁成横向 810×620(高≠宽,讲 `(高, 宽)` 时才看得出区别),裁剪后在右下角**重新标注"豆包AI生成"**(AI 内容须显式标识)。第 15 讲原用 [PI] 室内视频帧(窗外过曝,"哪个通道最亮"看不出)→ 同换果盘:草莓在 R 通道最亮、B 通道很暗。
- **图文不一致修正**:08 的 3×3 数字表与脚本/教材对齐(52 80 120 / 90 128 200 / 150 190 255);10 图注"红色的车变蓝"→"红草莓变蓝";13 坐标图标注从 `(x, y)` 改为 `img[y, x]`(与教材、解说一致);14 实操一涂色位置对齐 `img[100:150, 50:100]`,实操二 100×100 → **50×50**(脚本、教材练习 3 均为 50×50);15 实操二补"蓝色通道换成全 0 → 偏黄"(原图只有红蓝对调);12 柱状图标签压标题。
- **接入教师收集素材**(`stu_work/module2--m4/`):08 p4 十字绣/马赛克/LED 三图拼图 ✅。13 p8 越界:教师两张图未直接采用(真实截图中文输出乱码 `����`;示意图写"宽 100 的图,最大合法**行号**是 99",应为高)→ 由 `_visuals/m2.py` 真实运行 `img[0, w]` 取报错原文重画 ✅。模块二待找素材 2 → **0**;全课 109 → **107**(新增 `_todo_summary.py` 从各节重新汇总)。
- **脚本内容修正**:第 12 讲"后缀写错时 imwrite 返回 False"**不实**——OpenCV 4.11 实测后缀写错直接抛 `cv2.error`,只有"文件夹不存在"才返回 False,已改要点与解说;第 13 讲第 8 页要点 `index 640` 与配图实测值不符 → 改为通用写法。
- **模块三、四收集素材(17–34 节,13 条)未接入**,审查意见待处理:19-p4 公式图画成了 `addWeighted`(两图叠加,β=第二张图权重),与该页"新像素 = α×原像素 + β"(β=亮度)冲突;19-p5 对策"转 float 再转回 uint8"漏了 `np.clip`;22-p4 箭头串联易误读为开运算;23-p5 纵轴应为"像素数量";17-p9 `gray[120][300]` 宜改 `gray[120, 300]`;LED、包装箱二维码疑为 AI 生成、其余网图需补来源授权。
- **同步机制(2026-11-10 补)**:新增 `_sync_check.py`(8 环下游检查,只查不改);`_visuals/run.py` 为每节写生成代码指纹 `NN/img/.gen_hash`(只改别的节不误报);`Lesson` 内容不变不重写文件(时间戳不再制造假"过期")。首轮全量核查:87 节配图重跑后仅第 39 讲变化(实时帧率测量,数值本就随次波动,已重建其 PPT);`PPT_collection` 08–15 已刷新、`.zip` 重建(只含 28 个顶层文件);`stu_work/PPT_collection.rar` 与嵌套文件夹 = 教师手改版,保留不动——其中 08、13 的手插图已由流程接管,**17 p9、18 p4、19 p4 仍只在手改版里**,待审查后登记。`全部微课脚本汇总.docx` 因在 Word 中打开未能重建(关闭后 `python _merge.py`)。
- **目录整理(2026-11-10 晚,用户)**:教师收集/手改类素材统一归入 `draft/online_course/stu_work/`(`module2--m4/` = `模块二三四.rar` 解压改名;`PPT_collection/` + `.zip` + `.rar`;`图片汇总.rar`;`模块七八视觉素材.7z`);旧单脚本版 ch02 移入 `abandon/`。程序路径已同步(`_visuals/m2.py` 的 `M24`、`_sync_check.py` 的 `col`),重跑核对配图零变化、同步检查 0 过期。
- **手工素材框架 manual/ 落地(2026-11-10 晚)**:全课 107 条待找素材中示意图/对照表 42 条(定:程序画为主)、录屏/实拍 23、照片 18、截图 11、动画 9。新建 `manual/`(按节号分文件夹 + `素材登记.csv` + `_inbox/` + `_sources/` + `README.md`)与 `_manual.py`(命名校验、只接入「通过」、同页多张自动拼图、程序图优先并报冲突、rec/anim 标「已就绪」);`_ppt.vis_of/needs`、`_lib.build`(写 `.manual_hash`)、`_sync_check` 第 9 项已接入。迁移 36 个文件(原 `stu_work/module2--m4/` 17 个 + `模块七八视觉素材/` 19 个,来源取自其 `素材标注清单.md`,现存 `manual/_sources/`),状态:通过 3(08 p4,已在用)/ 仅参考 2 / 需改 5 / 待审 26——**迁移不改变任何现有 PPT 内容**;08 p4 拼图改由 manual 生成(`08_m4.png`,教材图 2-1 同步)。原压缩包移入 `stu_work/archive/`。手改版(`stu_work/PPT_collection/PPT_collection/` + `.rar`)中的手插图已全部在 manual 登记,不再有不可替代内容。
- **汇总 docx 定版前复核(2026-11-10 夜)**:① 图文不符改文字配合现有图(不补图):08 p2/p6「猫」→ 果盘/草莓香蕉;15 p5/p6「红苹果」→ 红草莓;26 p2/p5/p7「红苹果」→ 红色物体/图形,p7「H 在零附近」→ 实测配图 H=179,改讲「红色跨两端,0 附近和 179 附近都是红」。② 11 课后题「300×500」→「高 300、宽 500」(09 讲刚教 1920×1080=宽×高)。③ **画面栏 PPTn 页号**:原写法没把录屏页算进去,74 节 222 处偏小 → 全部改为实际页号(= manual 命名里的 pP);`_lib.py` 生成时校验,再错即报 ⚠️。PPT 本身不含画面栏,只 08/15/26 内容变化;PPT_collection 28 份 + .zip 已刷新,同步检查 0 过期。

## 九、2026-11-11 技术复核与 v1 基线

详见 `PLAN.md` 进度日志 2026-11-11 条。要点:课程环境安装顺序改为 06 contrib 4.11.0.86 → 42 mediapipe 0.10.21 → 52 `pip install ultralytics "numpy<2" opencv-python==4.11.0.86` + `pip install --force-reinstall --no-deps opencv-contrib-python==4.11.0.86`;树莓派用 mediapipe 0.10.18 + 阿里云 CPU 版 torch + onnx 1.17.0。待确认项写在各节 `content.py` 的 `PENDING = {页号: 说明}`,`python _merge.py --baseline` 生成不含模块九的基线版。


## 十、前 60 讲脚本定稿归档（2026-11-12）

- 用户本次明确范围：只处理模块一至七（01–60）的脚本定稿与 PDF 归档。PPT、配图、截图、录屏与录屏复现验证全部后置；本条覆盖本轮“改脚本立即修补所有素材”的执行时机，素材仍须在后续制作时按定稿脚本同步。
- 当前脚本口径：Python 3.11；OpenCV contrib 4.11.0.86；MediaPipe 0.10.21；第 52 讲固定 ultralytics==8.4.202，并按原已验证方案约束 numpy<2、opencv-python==4.11.0.86，最后重装 contrib。历史实测记录保留，本次不新增模拟运行或录屏验证。
- 修订重点：18 草莓示例与 Pillow 安装；19 convertScaleAbs 的绝对值及压暗条件；20 奇数核约束；24 直方图曝光表述；29 轮廓面积与外接框中心；30 简化形状规则边界；36 故障排查与近似播放；43 检测方案分类；44 闭眼计时；52 版本；57 分组划分；59 AP/mAP50 定义。另校正 01、13、15、17、25、34、39、42、45、47、58、60 的相关表述。
- `python draft/online_course/_merge.py --final60` 单独生成 60 讲归档 Word，再由 `tools/export_script_archive_pdf.py` 直接排版为嵌入中文字体的 PDF（本机 Word/Edge 自动导出失败，使用纯 Python 导出）；不改变旧 `--baseline` 的 69 讲定义。新归档文件为 `out/reports/micro_lessons_01_60_script_final_2026-11-12.{docx,pdf}`；旧 77 讲 PDF 是历史版本，不代表本次定稿。
- 本次重新生成 01–60 的单讲脚本 docx；素材需求、PPT、PPT_collection、zip、教材图片和阅读页待后续按定稿脚本同步。旧 87/69 讲汇总也不作为本轮交付依据。
- 静态核对、归档覆盖、源文件指纹及导出检查见 `out/reports/script_01_60_finalize_check.md`。前 60 讲以新归档版本为本轮脚本定稿，发现新的事实错误时走修订并另存新版，不能把本轮静态核对解释为所有设备或素材均已复测通过。

## 2026-11-12：01–60 讲版本依据（现行补充规则）

- 正式依据：`out/reports/micro_lessons_01_60_script_final_2026-11-12.docx`。旧 `draft/online_course/全部微课脚本汇总.docx` 禁止作为 01–60 更新依据或用于回填源脚本；本规则优先于旧通用下游链说明。
- 当前 01–60 content.py 镜头表与正式归档一致；旧汇总有 21 讲不同：13、15、17、18、19、20、24、25、29、30、34、36、42、43、44、45、47、52、57、59、60。
- 资源生成仍读取 content.py；更新前运行 `python tools/check_script_archive_01_60.py` 核对。正式修订记录差异并另存修订版，不静默覆盖归档。镜头表核对涵盖镜头、解说词与画面说明，不涵盖归档未保存的 PPT 要点列表及版式。

## 2026-11-12：旧合集隔离（现行规则）
- 用户要求将 draft/online_course/stu_work 整体移至 quarantine/stu_work_2026-11-12，隔离区不得参与自动生成、扫描或分发。上文指向 stu_work/PPT_collection 的旧下游链暂停使用。
- 当前使用各讲 NN/ 下生成版；后续分发合集另建输出路径。教师手改素材需先审核登记到 manual 再复用，不直接回填。


## 2026-11-12：汇总版本职责（现行规则）
- 统一说明见 draft/online_course/脚本版本说明.md。全部微课脚本汇总.docx 为历史全课审阅件；全部微课脚本汇总_v1基线.docx 当前为 01–69 历史基线快照；两者均不得作为 01–60 当前制作、审核或回填依据，也不要求例行重建。
- 当前正式归档为 out/reports/micro_lessons_01_60_script_final_2026-11-12.docx 及同名 PDF。生成使用经核对的 content.py。历史基线中的验证声明不能推定为当前版本全部验证通过；61–87 不在本轮正式归档内。
- _merge.py 默认及 --baseline 仍会覆盖旧文件名，不应为消除过期提示而运行；新审阅版本使用独立名称。已归档文件不得静默覆盖。

