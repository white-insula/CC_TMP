# 11-P6 普通话配音候选（Claude 云端）

日期：2026-11-17 · 分支：`claude/optimistic-sagan-l44esv`（基于 5e0f5a4）· 状态：**待用户试听**

## 结果

- **语音途径**：MeloTTS 中英混合模型（sherpa-onnx 2.0.1，离线 CPU），模型内置单一普通话女声，MIT 许可。Microsoft Edge 在线语音在云端被网络策略拒绝，未采用。
- **试音小样**：`audio/voice_sample.wav`（18.44 秒）/ `.mp3`，内容与正文分开。
- **五段配音**：`audio/segment_01.wav` … `segment_05.wav`（48 kHz 单声道 16 位）。
- **完整音轨**：`audio/narration.wav`（114.866625 秒，起点 2/24/35/61/96 秒，各段无越界、无重叠），另附 `narration.mp3`。MP3 有编码器填充，同步请用 WAV。
- **字幕**：`subtitle.srt`，10 条，句级，时间取自实际合成音频（不是逐字对齐）。`timing_actual.json` 记录各段、各句的实际时间。
- **文本**：`texts/narration_original.txt` 为正式讲解词，`texts/tts_input_spoken.txt` 为 TTS 实际输入。
- **复现与核对**：`scripts/`（get_model.sh、synthesize.py、asr_check.py、verify.py、rebuild_srt.py、run_all.sh），`run_log.txt` 含运行环境、机器转写和完整 SHA256。

详细说明、读法改动、机器转写结果和试听重点见 [review.md](review.md)；许可见 [sources.json](sources.json)。

## 仍需本机 / 用户

1. 试听，与本机 Huihui 初版比较后决定取舍。
2. 本机 Codex 对照原录屏做画面同步和最终合成。云端没有看过原视频。
3. 公开发布前核实 MeloTTS 女声训练数据与商用说明。

## 复现

```bash
pip install sherpa-onnx==2.0.1 soundfile scipy numpy    # 独立环境；另需 ffmpeg
bash scripts/get_model.sh /path/to/tts_model
bash scripts/run_all.sh /path/to/tts_model/vits-melo-tts-zh_en   # 可再加 paraformer、SenseVoice 目录做机器转写
```

合成有随机性，重新运行得到的音频会略有不同，SHA256 也会变化。
