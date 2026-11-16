# -*- coding: utf-8 -*-
NO = "46"
NAME = "手部关键点检测"
MODULE = "模块六 AI 现成模型：人脸·手·人体"

SEG = [
 ("", "手部关键点检测", None, "", "片头；PPT1"),

 ("教师加PPT", "课程导入",
  ["隔空翻页、手势拍照、手语翻译", "关键：电脑能看清每一根手指", "MediaPipe Hands：每只手 21 个关键点"],
  "大家好，欢迎来到《机器视觉技术应用实践》课程！隔空挥手翻页、比个手势自动拍照、手语翻译，这些应用的关键，是电脑能看清你的每一根手指。这一讲我们用 Media Pipe 的手部模型，找到手上的二十一个关键点，并学会用它们数出伸出了几根手指。",
  "教师半身；PPT2"),

 ("PPT", "本讲学习目标",
  ["1. 认识手部 21 个关键点的编号", "2. 会检测并画出手部关键点", "3. 会把关键点换算成像素坐标", "4. 会判断手指伸直还是弯曲，数手指"],
  "本讲的学习目标有四个：第一，认识手部二十一个关键点的编号；第二，会检测并画出手部关键点；第三，会把关键点换算成像素坐标；第四，会判断每根手指是伸直还是弯曲，数出伸出的手指数。",
  "PPT3"),

 ("PPT", "21 个关键点",
  ["0：手腕", "拇指 1 ~ 4，食指 5 ~ 8，中指 9 ~ 12，无名指 13 ~ 16，小指 17 ~ 20", "指尖：4、8、12、16、20", "每根手指 4 个点，从指根到指尖编号递增"],
  "先认识这二十一个点。零号点是手腕。然后每根手指四个点，从指根到指尖依次编号：拇指是一到四，食指五到八，中指九到十二，无名指十三到十六，小指十七到二十。所以五个指尖分别是四、八、十二、十六、二十，这几个编号后面会经常用到，建议记下来。",
  "PPT4；手部 21 点编号图（大图）"),

 ("PPT", "用法",
  ["mp_hands = mp.solutions.hands", "hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)", "results = hands.process(rgb)", "results.multi_hand_landmarks：每只手一组 21 个点", "画图：mp.solutions.drawing_utils.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)"],
  "用法和人脸检测是一个套路。创建 Hands 检测器，max num hands 是最多检测几只手，min detection confidence 是最低置信度。把 R-G-B 画面交给 process，结果在 multi hand landmarks 里，每只手一组，每组二十一个点。Media Pipe 还提供了画图工具 drawing utils，调用 draw landmarks，就能把点和骨架连线一次画好，非常方便。",
  "PPT5"),

 ("录屏演示", "实操一：画出手部骨架",
  ["[ 录屏：创建 Hands → process → draw_landmarks → 食指指尖画大圆点并显示坐标 ]"],
  "下面动手。在摄像头循环里，把画面转成 R-G-B，交给 hands 处理。如果检测到了手，就对每只手调用 draw landmarks，画出点和骨架。然后单独取出八号点，也就是食指指尖，把 x 乘宽度、y 乘高度换成像素坐标，画一个大大的紫色圆点，并把坐标写在旁边。运行一下，伸出手，骨架立刻出现，移动食指，紫色圆点和坐标都紧紧跟着。",
  "录屏1：\n`results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))`\n`if results.multi_hand_landmarks:`\n`    for hand in results.multi_hand_landmarks:`\n`        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)`\n`        tip = hand.landmark[8]; px, py = int(tip.x * w), int(tip.y * h)`\n`        cv2.circle(frame, (px, py), 12, (255, 0, 255), -1)`"),

 ("PPT", "怎样判断手指伸直",
  ["四指（食指到小指）：指尖比第二关节高 → 伸直", "　即 tip.y < pip.y（y 越小越靠上）", "　指尖 8、12、16、20 对比关节 6、10、14、18", "拇指：横向张开，比较 x 坐标（4 号与 3 号）", "前提：手掌朝向摄像头、手指向上"],
  "怎么判断一根手指是伸直还是弯曲？以食指为例：手指伸直时，指尖在第二个关节的上方；弯下去时，指尖就跑到了关节下面。图像中 y 越小越靠上，所以只要比较指尖的 y 是否小于关节的 y。四根手指分别用八、十二、十六、二十号指尖，和六、十、十四、十八号关节比较。拇指不一样，它是横着张开的，所以比较四号和三号点的 x 坐标。这个方法的前提是手掌朝向摄像头、手指向上。",
  "PPT7；伸直与弯曲时指尖和关节的位置对比"),

 ("录屏演示", "实操二：数手指",
  ["[ 录屏：写 count_fingers 函数 → 画面显示手指数 → 比 0~5 测试 ]"],
  "把这个判断写成一个函数 count fingers。先判断拇指，再用一个循环判断其余四指，每伸直一根就加一，最后返回总数。在画面左上角用大字显示这个数字。运行一下，依次比出零、一、二、三、四、五，数字都能正确显示。如果换了另一只手，拇指可能判断反了，因为左右手拇指的方向相反，这个问题留给大家在课后解决。",
  "录屏2：\n`def count_fingers(lm):`\n`    n = 1 if lm[4].x > lm[3].x else 0`\n`    for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)]:`\n`        if lm[tip].y < lm[pip].y: n += 1`\n`    return n`\n（参考：[OC]Finger_Guess_Game/4_figer_guess_game.py 的 count_extended_fingers）"),

 ("教师加PPT", "内容总结",
  ["21 点：0 手腕，指尖 4、8、12、16、20", "Hands → process → multi_hand_landmarks → draw_landmarks", "四指：tip.y < pip.y 即伸直；拇指比 x", "关键点 + 简单比较 = 手势判断"],
  "我们来总结一下。手部有二十一个关键点，零是手腕，指尖是四、八、十二、十六、二十；检测流程是创建 Hands、process、取出 landmarks、画出骨架；判断伸直，四指比较指尖和关节的 y，拇指比较 x。关键点加上简单的比较，就能判断手势。",
  "教师半身；PPT9"),

 ("教师加PPT", "课后任务",
  ["1. 完成数手指程序，录一段 0 到 5 的演示", "2. 用 results.multi_handedness 区分左右手，修正拇指判断", "3. 计算拇指尖与食指尖的距离，做一个“捏合”检测"],
  "课后请完成三个任务。第一，完成数手指程序，录一段从零数到五的演示视频。第二，用 results 点 multi handedness 判断是左手还是右手，修正拇指的判断方向。第三，计算拇指尖和食指尖之间的距离，做一个捏合检测，两个指尖捏在一起时显示 pinch。本讲的内容就到这里！",
  "教师半身；PPT10"),
]
