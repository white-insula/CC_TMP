# 第36—40讲 录屏工程候选

**候选代码**，供本机准备录屏；不是正式 recording_kit，也不代表已经录屏。默认输入是合成测试视频 `media/synthetic_test.avi`（由 `make_synthetic_video.py` 生成，不是用户录屏或摄像头画面）。

## 目录

```
recording_candidates/
├── make_synthetic_video.py   生成 media/synthetic_test.avi（XVID，640×480，25 帧/秒，60 帧）
├── run_checks.py             无界面核对（不开摄像头、不弹窗口）
├── common/                   共用核心：sources（打开来源、帧率回退、分辨率读回）、synth（合成帧）、
│                             effects（四种模式）、keys（按键状态机）、fps（帧率）、recorder（截图录像）
├── 36/ p6_camera.py · p7_play_file.py · check_headless.py
├── 37/ core.py · p5_gray_binary.py · p6_blue.py · check_headless.py
├── 38/ p6_effects.py · p7_overlay.py · check_headless.py
├── 39/ p6_show_fps.py · p7_resolution.py · check_headless.py
└── 40/ core.py · p6_snapshot.py · p7_record.py · check_headless.py
```

## 本机使用

在讲次目录运行。**只有给出 `--camera` 时才会打开摄像头**：

```powershell
Set-Location draft/collaboration/claude_36_40/recording_candidates/38
python p6_effects.py --camera 0 --backend dshow
```

- `--backend` 只对摄像头生效：`dshow` 为 Windows DirectShow，`msmf` 为 Media Foundation，`default` 为自动选择。画面纯色或打不开时换一种试。
- 播放视频文件：`--input 你的视频.mp4`。播放文件时不需要也不传后端参数。
- 窗口按键：先用鼠标点一下图像窗口，输入法切到英文。
- 40 讲录像默认 `XVID` + `.avi`。如果本机打不开写入器，程序会报告，可用 `--fourcc mp4v` 再试（文件仍是 .avi 名，必要时自行改扩展名）。
- 不需要在本机已锁定的教学环境安装或升级任何包。

## 核对（无窗口）

```bash
python run_checks.py --outdir check_out --log check_out/run_log.txt
```

云端已在 NumPy 2.5.3 与 NumPy 1.26.4（都是 OpenCV 4.11.0、headless 版、FFmpeg 后端）两个独立环境各跑一遍。GUI 入口只做语法检查，真实窗口、键盘、摄像头均未测试。
