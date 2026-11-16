# -*- coding: utf-8 -*-
NO = "06"
NAME = "开发环境搭建"
MODULE = "模块一 走进机器视觉"

# (镜头, slide标题, slide要点[None=片头], 解说词[TTS适配], 画面)
SEG = [
 ("", "开发环境搭建", None, "", "片头；PPT1"),

 ("教师加PPT", "课程导入",
  ["工欲善其事，必先利其器", "三件套：Python + VS Code + OpenCV"],
  "大家好，欢迎来到《机器视觉技术应用实践》课程！从这一讲开始我们要动手了，第一步是搭好开发环境，需要三件套：Python、V-S Code 和 Open C-V。跟着视频一步一步做就行。",
  "教师半身；PPT2"),

 ("PPT", "本讲学习目标",
  ["1. 安装 Python 并配置好环境变量", "2. 把 pip 换成国内源，安装 OpenCV", "3. 安装 VS Code 并能运行 Python", "4. 会排查最常见的安装问题"],
  "本讲的学习目标有四个：第一，安装 Python，并配置好环境变量；第二，把下载工具 pip 换成国内源，安装 Open C-V；第三，安装 V-S Code，并能在里面运行 Python；第四，学会排查最常见的几个安装问题。",
  "PPT3"),

 ("PPT", "三件套各管什么",
  ["Python：编程语言，简单易学，视觉领域最常用", "OpenCV：开源视觉库，读图、处理、识别的“工具箱”", "VS Code：写代码、运行代码的编辑器", "课程统一版本：Python 3.11 + OpenCV 4.11"],
  "三件套各管一件事：Python 是编程语言，简单易学，视觉领域用得最多；Open C-V 是开源视觉库，像一个功能齐全的工具箱；V-S Code 是写代码、运行代码的编辑器。为了避免版本不同带来的麻烦，本课程统一使用 Python 三点一一和 Open C-V 四点一一。",
  "PPT4；三件套图标与关系图"),

 ("录屏演示", "实操一：安装 Python",
  ["[ 录屏：python.org 下载 3.11 → 勾选 Add python.exe to PATH → 安装 → 命令行验证 ]"],
  "下面开始安装。打开 Python 官网，进入下载页，选择三点一一版本的 Windows 安装包。双击运行，注意，第一个界面最下面有一个选项，Add python dot exe to PATH，一定要勾上，它的作用是让电脑在任何位置都能找到 Python，然后点击立即安装，等进度条走完。安装好以后，按 Win 加 R，输入 c-m-d 打开命令行，输入 python 空格 杠杠 version，回车，如果显示出 Python 三点一一和版本号，就说明安装成功了。",
  "录屏1：浏览器打开 python.org/downloads → 下载 Python 3.11.x Windows installer (64-bit) → 安装首页**勾选 Add python.exe to PATH**（红框放大）→ Install Now → cmd 输入 `python --version` 显示 Python 3.11.x"),

 ("录屏演示", "实操二：pip 换源并安装 OpenCV",
  ["[ 录屏：pip config 设置清华源 → pip install opencv-contrib-python==4.11.0.86 → 验证版本 ]"],
  "接下来安装 Open C-V。Python 自带一个下载工具叫 pip，它默认从国外服务器下载，速度很慢，所以我们先把它换成国内的清华源。在命令行里输入画面上这条 pip config 命令，回车。然后输入 pip install opencv dash contrib dash python，等号等号，四点一一点零点八六，回车。这里装的是 Open C-V 的完整版，它包含基础版的全部功能，后面学人脸识别和 Media Pipe 都要用到它。注意只装完整版，以后装 YOLO 时顺带装上的基础版，第五十二讲再处理。最后验证一下：输入 python 进入交互模式，输入 import c-v-2，再输入 print 括号 c-v-2 点 下划线下划线 version 下划线下划线，屏幕上显示四点一一，就说明 Open C-V 装好了。",
  "录屏2：cmd 依次输入 `pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple` → `pip install opencv-contrib-python==4.11.0.86`（完整版；若已装过 opencv-python，先 `pip uninstall opencv-python`） → `python` → `import cv2` → `print(cv2.__version__)` 显示 4.11.0 → `exit()`"),

 ("录屏演示", "实操三：安装 VS Code",
  ["[ 录屏：安装 VS Code → 装中文包与 Python 扩展 → 选择解释器 → 运行 hello.py ]"],
  "第三步安装 V-S Code。从官网下载安装包，一路下一步装好。打开后在左边的扩展商店里，安装中文语言包和微软出品的 Python 扩展。然后新建一个文件夹，比如叫 m-v 下划线 course，用 V-S Code 打开它，新建一个文件叫 hello 点 p-y，写一行 print 你好机器视觉。按 Ctrl 加 Shift 加 P，选择 Python 选择解释器，选中刚才装的三点一一。点右上角的运行按钮，终端显示出你好机器视觉，环境就搭好了。",
  "录屏3：code.visualstudio.com 下载安装 → 扩展商店安装 Chinese (Simplified) 与 Python (Microsoft) → 新建文件夹 mv_course 并打开 → 新建 hello.py：`print(\"你好，机器视觉\")` → Ctrl+Shift+P「Python: 选择解释器」选 3.11 → 点运行，终端输出"),

 ("PPT", "常见问题排查",
  ["“python 不是内部或外部命令”：没勾 PATH → 重装并勾选", "输入 python 弹出应用商店：关闭系统“应用执行别名”", "pip 下载很慢或报 403：换国内源；清华源出错时改用阿里云源 mirrors.aliyun.com/pypi/simple", "VS Code 提示找不到 cv2：解释器没选对"],
  "安装过程中最常见的问题有四个。第一，命令行提示 python 不是内部或外部命令，多半是没勾选添加到 PATH，重新运行安装包修改一下就行。第二，输入 python 却弹出了应用商店，需要到系统设置里关闭应用执行别名中的 Python 选项。第三，pip 下载很慢或者报错，检查一下是不是已经换了国内源，如果清华源报四零三错误，就换成阿里云的源再试。第四，V-S Code 里提示找不到 c-v-2，说明解释器没选对，重新选择三点一一那一个。",
  "PPT8；问题—原因—解决 对照表"),

 ("教师加PPT", "内容总结",
  ["安装 Python 3.11，勾选 PATH", "pip 换清华源，安装 OpenCV 完整版 4.11", "VS Code + Python 扩展，选对解释器"],
  "我们来总结一下。安装 Python 三点一一，一定勾选添加到 PATH；pip 换成清华源，安装 Open C-V 四点一一；安装 V-S Code 和 Python 扩展，并选对解释器。做完这三步，你的电脑就具备了机器视觉开发的能力。",
  "教师半身；PPT9"),

 ("教师加PPT", "课后任务",
  ["1. 在自己电脑上完成三件套安装", "2. 截图：命令行显示 Python 和 OpenCV 版本号", "3. 截图：VS Code 成功运行 hello.py"],
  "课后请大家在自己的电脑上完成全部安装，并提交两张截图：一张是命令行里显示出 Python 和 Open C-V 的版本号，一张是 V-S Code 成功运行 hello 点 p-y 的画面。遇到问题，先对照今天的排查表试一试。本讲的内容就到这里！",
  "教师半身；PPT10"),
]
