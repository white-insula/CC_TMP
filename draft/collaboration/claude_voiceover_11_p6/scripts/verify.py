# -*- coding: utf-8 -*-
"""技术核对（不是人工试听）：解码全部音频，核对时长/采样率/声道、非空、响度、分段位置与重叠；输出 SHA256。
用法：python verify.py [--root ..]
"""
import argparse
import hashlib
import json
import os
import subprocess
import numpy as np
import soundfile as sf

ap = argparse.ArgumentParser()
ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
args = ap.parse_args()
R = args.root
A = os.path.join(R, "audio")
cfg = json.load(open(os.path.join(R, "scripts", "tts_input.json"), encoding="utf-8"))
tim = json.load(open(os.path.join(R, "timing_actual.json"), encoding="utf-8"))
db = lambda v: 20 * np.log10(max(float(v), 1e-12))


def probe(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,sample_rate,channels:format=duration",
                        "-of", "json", p], capture_output=True, text=True, check=True)
    j = json.loads(o.stdout)
    s = j["streams"][0]
    return s["codec_name"], int(s["sample_rate"]), s["channels"], float(j["format"]["duration"])


print("文件解码与基本参数：")
for f in sorted(os.listdir(A)):
    p = os.path.join(A, f)
    codec, sr, ch, dur = probe(p)
    line = f"  {f}: {codec} {sr} Hz {ch} 声道 {dur:.3f} 秒 {os.path.getsize(p)} 字节"
    if f.endswith(".wav"):
        x, sr2 = sf.read(p, dtype="float32")
        assert sr2 == 48000 and x.ndim == 1 and len(x) > 0
        v = x[np.abs(x) > 0.01]
        line += f"；峰值 {db(np.abs(x).max()):.1f} dBFS，语音 RMS {db(np.sqrt(np.mean(v ** 2))):.1f} dBFS"
        assert np.abs(x).max() > 0.1, f
    print(line)

x, sr = sf.read(os.path.join(A, "narration.wav"), dtype="float32")
print(f"\n完整音轨：{len(x)} 采样，{len(x) / sr:.6f} 秒（目标 {cfg['total_seconds']} 秒，差 {abs(len(x) / sr - cfg['total_seconds']) * 1e6:.1f} 微秒，小于 1 个采样）")
assert len(x) == int(round(cfg["total_seconds"] * sr))
# 有声音的位置必须都落在声明的五段内
act = np.abs(x) > 1e-4
segs = tim["segments"]
inside = np.zeros_like(act)
for s in segs:
    inside[int(s["start"] * sr): int(round(s["end"] * sr)) + 2] = True
print(f"声明段之外的非零采样数：{int((act & ~inside).sum())}")
assert int((act & ~inside).sum()) == 0
for a, b in zip(segs, segs[1:]):
    assert a["end"] < b["start"] and a["end"] < a["end_before"]
for s in segs:
    seg, _ = sf.read(os.path.join(A, f"segment_{s['id']:02d}.wav"), dtype="float32")
    i0 = int(round(s["start"] * sr))
    same = np.allclose(x[i0:i0 + len(seg)], seg, atol=1e-4)
    print(f"  第 {s['id']} 段：{s['start']:.2f}—{s['end']:.2f} 秒（窗口至 {s['end_before']} 秒，余 {s['margin']:.2f} 秒），与单段文件逐样本一致：{same}")
    assert same
print("各段无越界、无重叠")
srt = open(os.path.join(R, "subtitle.srt"), encoding="utf-8").read().strip().split("\n\n")
print(f"字幕 {len(srt)} 条，句级，时间取自 timing_actual.json")
print("\nSHA256（完整）：")
for root, _, files in sorted(os.walk(R)):
    for f in sorted(files):
        if f == "run_log.txt" or "__pycache__" in root:
            continue
        p = os.path.join(root, f)
        print(f"  {os.path.relpath(p, R)}  {os.path.getsize(p)} B  {hashlib.sha256(open(p, 'rb').read()).hexdigest()}")
