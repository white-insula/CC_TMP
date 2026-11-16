# -*- coding: utf-8 -*-
NO = "40"
NAME = "视频录制与截图保存"
MODULE = "模块五 让摄像头动起来"

SEG = [
 ("", "视频录制与截图保存", None, "", "片头；PPT1"),

 ("教师加PPT", "课程导入",
  ["检测到不合格品，能不能留下证据？", "做演示，想录一段处理后的效果？", "截图与录像：给视觉系统加上“记录”功能"],
  "大家好，欢迎来到《机器视觉技术应用实践》课程！生产线上检测到一个不合格品，能不能把当时的画面拍下来，留作证据？做项目演示时，能不能把处理后的效果录成一段视频？这一讲我们就给视觉系统加上记录功能：按一个键截图，再按一个键开始录像。",
  "教师半身；PPT2"),

 ("PPT", "本讲学习目标",
  ["1. 会按键截图，并用时间命名文件", "2. 会用 VideoWriter 录制视频", "3. 会按键控制开始和停止录像", "4. 会排查录出的视频打不开的问题"],
  "本讲的学习目标有四个：第一，会按键截图，并用当前时间给文件命名；第二，会用 video writer 录制视频；第三，会用按键控制开始和停止录像；第四，会排查录出来的视频打不开的问题。",
  "PPT3"),

 ("PPT", "截图：imwrite + 时间命名",
  ["按 s 键：cv2.imwrite(文件名, frame)", "文件名用时间，不会互相覆盖：", "from datetime import datetime", "name = datetime.now().strftime(\"%Y%m%d_%H%M%S\") + \".jpg\"", "　→ 20261105_143025.jpg"],
  "截图很简单，就是在按下 s 键时，用 im write 把当前这一帧保存下来。问题是文件名：如果每次都叫同一个名字，新图会把旧图覆盖掉。好办法是用当前时间命名，用 datetime 模块，写 datetime 点 now 点 strf time，括号里是时间格式，年月日、下划线、时分秒，得到的文件名就像二零二六一一零五下划线一四三零二五点 j-p-g，每次都不一样，还能看出是什么时候拍的。",
  "PPT4"),

 ("PPT", "录像：VideoWriter 三步",
  ["① fourcc = cv2.VideoWriter_fourcc(*\"XVID\")　编码器，配 .avi", "② out = cv2.VideoWriter(\"rec.avi\", fourcc, 20.0, (宽, 高))", "③ 每一帧：out.write(frame)；结束：out.release()", "⚠️ 尺寸必须和写入的帧完全一致，宽在前"],
  "录像用 video writer，分三步。第一步，选编码器，用 fourcc 函数，XVID 编码配合点 a-v-i 文件，兼容性最好；也可以用 m-p-4-v 编码配合点 m-p-4。第二步，创建 video writer，参数依次是文件名、编码器、帧率和画面尺寸。第三步，每一帧用 out 点 write 写进去，结束时一定要 release，否则文件可能是坏的。特别注意，尺寸必须和写进去的画面完全一致，而且是宽在前，不一致的话，录出来的文件是空的。",
  "PPT5"),

 ("录屏演示", "实操一：按 s 截图",
  ["[ 录屏：导入 datetime → 按 s 保存带时间的图片 → 文件夹查看 ]"],
  "下面动手，在特效相机里加功能。导入 datetime，在按键判断里加一条：如果按了 s，就用当前时间生成文件名，用 im write 保存当前处理后的画面，同时在终端打印已保存和文件名。运行后切换到卡通模式，摆个姿势按下 s，再换个模式按一次。打开文件夹，两张截图都在，名字里带着拍摄时间。",
  "录屏1：\n`from datetime import datetime`\n`if key == ord(\"s\"):`\n`    name = datetime.now().strftime(\"%Y%m%d_%H%M%S\") + \".jpg\"`\n`    cv2.imwrite(name, out); print(\"已保存\", name)`"),

 ("录屏演示", "实操二：按 r 开始/停止录像",
  ["[ 录屏：读取宽高 → 建 VideoWriter → r 键切换录制状态 → 画面显示 REC 红点 → 播放录像 ]"],
  "再加录像功能。先用 cap 点 get 读出画面的宽和高，转成整数。用一个变量 recording 记录是否在录，初始为 False。按下 r 键时：如果没在录，就用时间命名创建一个 video writer，把 recording 设为 True；如果正在录，就 release 并设为 False。每一帧，如果 recording 为真，就把画面写进去，并在右上角画一个红点、写上 REC，提示正在录制。运行一下，按 r 开始，做几个动作，再按 r 停止，打开录好的文件播放，效果完整保存下来了。",
  "录屏2：\n`w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))`\n`if key == ord(\"r\"):`\n`    if not recording: writer = cv2.VideoWriter(name_avi, cv2.VideoWriter_fourcc(*\"XVID\"), 20.0, (w, h)); recording = True`\n`    else: writer.release(); recording = False`\n`if recording: writer.write(out); cv2.circle(out, (w - 30, 30), 10, (0, 0, 255), -1)`\n（参考：[OC]Finger_Guess_Game/0_record_video.py）"),

 ("PPT", "录出的视频打不开？",
  ["文件只有几 KB：尺寸和帧不一致", "灰度画面录不进去：先转回三通道，或创建时加 isColor=False", "程序被强行关闭，没 release：文件损坏", "播放速度不对：创建时的帧率和实际处理帧率差太多"],
  "录像最容易出问题，常见原因有四个。文件只有几 K，基本都是尺寸和帧不一致；灰度画面录不进去，要先转回三通道，或者创建时加上 is color 等于 False；程序被强行关掉，没有执行 release，文件就会损坏；播放时快时慢，是因为创建时写的帧率和程序实际的处理帧率差得太多，用上一讲测出的帧率来设置就好了。",
  "PPT8"),

 ("教师加PPT", "内容总结",
  ["截图：imwrite + datetime 时间命名", "录像：fourcc 编码器 → VideoWriter → write → release", "尺寸宽在前，且与帧一致；单通道先转三通道", "用状态变量控制开始和停止"],
  "我们来总结一下。截图用 im write，加上用时间命名的文件名；录像用 video writer，三步是选编码器、创建、逐帧写入，最后一定要 release；尺寸宽在前、必须和画面一致，单通道画面先转回三通道；用一个状态变量来控制开始和停止录像。",
  "教师半身；PPT9"),

 ("教师加PPT", "课后任务",
  ["1. 给特效相机加上截图和录像功能，录一段 10 秒的特效视频", "2. 截图保存到 snapshots 文件夹（不存在时自动创建）", "3. 在录像画面右下角显示当前时间"],
  "课后请完成三个任务。第一，给你的特效相机加上截图和录像功能，录一段十秒钟的特效视频。第二，让截图统一保存到 snapshots 文件夹，如果文件夹不存在就自动创建，提示一下，用 o-s 点 make dirs。第三，在录像画面的右下角实时显示当前时间。本讲的内容就到这里！",
  "教师半身；PPT10"),
]
