# -*- coding: utf-8 -*-
"""机器转写核对（不是人工试听）：用独立的离线 ASR 模型（sherpa-onnx paraformer-zh-small 或 SenseVoice，16 kHz）转写合成音频，
看技术词、数字是否能被另一个模型“听出来”。ASR 本身也会出错，结果只作参考。
用法：python asr_check.py --asr-dir <sherpa-onnx-paraformer-zh-small-2024-03-09 目录> --audio-dir ../audio
"""
import argparse
import glob
import os
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import sherpa_onnx

ap = argparse.ArgumentParser()
ap.add_argument("--asr-dir", required=True)
ap.add_argument("--audio-dir", required=True)
ap.add_argument("--kind", choices=["paraformer", "sensevoice"], default="paraformer")
args = ap.parse_args()
d = args.asr_dir.rstrip("/") + "/"
if args.kind == "paraformer":
    rec = sherpa_onnx.OfflineRecognizer.from_paraformer(paraformer=d + "model.int8.onnx", tokens=d + "tokens.txt", num_threads=4)
else:   # SenseVoice：中英日韩粤多语种，英文技术词识别比 paraformer-zh-small 好
    rec = sherpa_onnx.OfflineRecognizer.from_sense_voice(model=d + "model.int8.onnx", tokens=d + "tokens.txt",
                                                         language="auto", use_itn=False, num_threads=4)
for p in sorted(glob.glob(os.path.join(args.audio_dir, "*.wav"))):
    if os.path.basename(p) == "narration.wav":
        continue
    x, sr = sf.read(p, dtype="float32")
    x = resample_poly(x, 1, 3).astype(np.float32) if sr == 48000 else x
    s = rec.create_stream(); s.accept_waveform(16000, x); rec.decode_stream(s)
    print(f"{os.path.basename(p)}：{s.result.text}")
