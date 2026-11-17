# -*- coding: utf-8 -*-
"""第 11 讲 P6 配音候选：MeloTTS 中英混合模型（sherpa-onnx，CPU，离线）合成试音小样、五段配音、完整音轨和字幕。

流程：
  1. 把 lexicon_extra.txt 的 5 个技术词读法追加到模型词典副本（不改原模型文件）；
  2. 每句单独合成（模型输出 44.1 kHz），句间插入 sentence_gap_seconds 静音，句首尾各 10 ms 淡入淡出；
  3. 全部语音用同一个增益统一响度（语音 RMS 目标 -20 dBFS，峰值不超过 -1.5 dBFS），重采样到 48 kHz 单声道 16 位；
  4. 按 tts_input.json 的起始时间放进 114.866633 秒的完整音轨；若某段超出下一段开始前的窗口，
     先把该段语速逐步提高（最多 1.15 倍），仍超出则报错停止，不截断内容；
  5. 字幕时间取自实际合成出的每句音频（句级粒度，不是逐字对齐）。
用法：python synthesize.py --model-dir <vits-melo-tts-zh_en 目录> --out <输出根目录>
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
import sherpa_onnx

HERE = os.path.dirname(os.path.abspath(__file__))
SR_OUT = 48000
TARGET_RMS_DB, PEAK_DB = -20.0, -1.5


def make_tts(model_dir, lexicon_path, noise_scale=0.667, noise_scale_w=0.8):
    m = model_dir.rstrip("/") + "/"
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(model=m + "model.onnx", lexicon=lexicon_path,
                                                       tokens=m + "tokens.txt", dict_dir=m + "dict",
                                                       noise_scale=noise_scale, noise_scale_w=noise_scale_w),
            num_threads=4, debug=False, provider="cpu"),
        rule_fsts=f"{m}phone.fst,{m}date.fst,{m}number.fst,{m}new_heteronym.fst", max_num_sentences=1)
    return sherpa_onnx.OfflineTts(cfg)


def merged_lexicon(model_dir, tmpdir):
    base = open(os.path.join(model_dir, "lexicon.txt"), encoding="utf-8").read()
    extra = open(os.path.join(HERE, "lexicon_extra.txt"), encoding="utf-8").read()
    words = {l.split()[0] for l in extra.splitlines() if l.strip()}
    kept = [l for l in base.splitlines() if l.split(" ", 1)[0] not in words]
    p = os.path.join(tmpdir, "lexicon_merged.txt")
    open(p, "w", encoding="utf-8").write("\n".join(kept) + "\n" + extra)
    return p, sorted(words)


def fade(x, sr, ms=10):
    n = int(sr * ms / 1000)
    if len(x) > 2 * n:
        r = np.linspace(0, 1, n, dtype=np.float32)
        x[:n] *= r; x[-n:] *= r[::-1]
    return x


def synth_block(tts, sentences, speed, gap):
    """返回 (44.1k 音频, 采样率, 每句 [起, 止] 秒)"""
    parts, spans, t = [], [], 0.0
    sr = None
    for i, s in enumerate(sentences):
        a = tts.generate(s["spoken"], sid=0, speed=speed)
        sr = a.sample_rate
        x = fade(np.asarray(a.samples, dtype=np.float32).copy(), sr)
        # 去掉模型输出两端的近似静音（低于峰值 1%），句间停顿由 gap 统一控制
        thr = 0.01 * np.abs(x).max()
        idx = np.where(np.abs(x) > thr)[0]
        x = x[max(0, idx[0] - int(0.03 * sr)): idx[-1] + int(0.06 * sr)]
        if i:
            parts.append(np.zeros(int(gap * sr), np.float32)); t += gap
        spans.append([t, t + len(x) / sr]); t += len(x) / sr
        parts.append(x)
    return np.concatenate(parts), sr, spans


def to48k(x, sr):
    assert sr == 44100, sr
    return resample_poly(x, 160, 147).astype(np.float32)


def db(v):
    return 20 * np.log10(max(v, 1e-12))


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def mp3(wav, out):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-codec:a", "libmp3lame", "-b:a", "128k", out], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-dir", required=True)
    ap.add_argument("--out", default=os.path.dirname(HERE))
    args = ap.parse_args()
    cfg = json.load(open(os.path.join(HERE, "tts_input.json"), encoding="utf-8"))
    gap = cfg["sentence_gap_seconds"]
    tmp = tempfile.mkdtemp()
    lex, extra = merged_lexicon(args.model_dir, tmp)
    print("追加读法词条：", extra)
    v = cfg["voice"]
    tts = make_tts(args.model_dir, lex, v.get("noise_scale", 0.667), v.get("noise_scale_w", 0.8))
    print(f"噪声参数 noise_scale={v.get('noise_scale', 0.667)}，noise_scale_w={v.get('noise_scale_w', 0.8)}（VITS 采样有随机性，每次合成略有差异）")
    adir = os.path.join(args.out, "audio"); os.makedirs(adir, exist_ok=True)

    # 1. 合成（44.1k）
    blocks = {}
    x, sr, spans = synth_block(tts, cfg["sample"]["sentences"], 1.0, gap)
    blocks["sample"] = (x, spans, 1.0)
    for seg in cfg["segments"]:
        window = seg["end_before"] - seg["start"]
        speed = 1.0
        while True:
            x, sr, spans = synth_block(tts, seg["sentences"], speed, gap)
            if len(x) / sr <= window or speed >= 1.15 - 1e-9:
                break
            speed = round(speed + 0.05, 2)
        if len(x) / sr > window:
            raise SystemExit(f"第 {seg['id']} 段 {len(x) / sr:.2f} 秒，语速 1.15 仍超过窗口 {window:.2f} 秒，停止")
        blocks[seg["id"]] = (x, spans, speed)

    # 2. 统一增益：所有语音拼起来算 RMS（只算非静音部分）
    allv = np.concatenate([b[0] for b in blocks.values()])
    voiced = allv[np.abs(allv) > 0.01 * np.abs(allv).max()]
    gain = 10 ** ((TARGET_RMS_DB - db(np.sqrt(np.mean(voiced ** 2)))) / 20)
    peak = np.abs(allv).max() * gain
    if db(peak) > PEAK_DB:
        gain *= 10 ** ((PEAK_DB - db(peak)) / 20)
    print(f"统一增益 {db(gain):+.2f} dB")

    # 3. 输出：小样、五段、完整音轨（48k 单声道 16 位）
    def write(name, x):
        y = np.clip(to48k(x * gain, 44100), -1, 1)
        p = os.path.join(adir, name + ".wav"); sf.write(p, y, SR_OUT, subtype="PCM_16")
        return p, y

    p, y = write("voice_sample", blocks["sample"][0]); mp3(p, p[:-4] + ".mp3")
    print(f"试音小样 voice_sample.wav：{len(y) / SR_OUT:.2f} 秒")
    total = int(round(cfg["total_seconds"] * SR_OUT))
    track = np.zeros(total, np.float32)
    cues, report = [], []
    for seg in cfg["segments"]:
        x, spans, speed = blocks[seg["id"]]
        p, y = write(f"segment_{seg['id']:02d}", x)
        s0 = int(round(seg["start"] * SR_OUT))
        end = seg["start"] + len(y) / SR_OUT
        assert s0 + len(y) <= total and end < seg["end_before"], (seg["id"], end)
        track[s0:s0 + len(y)] += y
        report.append({"id": seg["id"], "start": seg["start"], "duration": round(len(y) / SR_OUT, 3), "end": round(end, 3),
                       "end_before": seg["end_before"], "margin": round(seg["end_before"] - end, 3), "speed": speed})
        for s, (a, b) in zip(seg["sentences"], spans):
            cues.append((seg["start"] + a, seg["start"] + b, s["display"]))
    for r in report:
        print(f"第 {r['id']} 段：{r['start']:.1f}s 起，时长 {r['duration']:.2f}s，止于 {r['end']:.2f}s，距下一段 {r['margin']:.2f}s，语速 {r['speed']}")
    # 段间不得重叠
    for a, b in zip(report, report[1:]):
        assert a["end"] < b["start"], (a, b)
    p = os.path.join(adir, "narration.wav")
    sf.write(p, np.clip(track, -1, 1), SR_OUT, subtype="PCM_16"); mp3(p, os.path.join(adir, "narration.mp3"))
    print(f"完整音轨 narration.wav：{total} 采样 = {total / SR_OUT:.6f} 秒（目标 {cfg['total_seconds']}）")
    with open(os.path.join(args.out, "subtitle.srt"), "w", encoding="utf-8") as f:
        for i, (a, b, t) in enumerate(cues, 1):
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n\n")
    print(f"字幕 subtitle.srt：{len(cues)} 条（句级，时间取自实际合成音频）")
    json.dump({"segments": report, "gain_db": round(float(db(gain)), 2), "sample_rate": SR_OUT, "total_samples": total,
               "cues": [{"start": round(float(a), 3), "end": round(float(b), 3), "text": t} for a, b, t in cues]},
              open(os.path.join(args.out, "timing_actual.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    # TTS 实际输入另存为纯文本
    with open(os.path.join(args.out, "texts", "tts_input_spoken.txt"), "w", encoding="utf-8") as f:
        f.write("# 试音小样（不是正文）\n" + "\n".join(s["spoken"] for s in cfg["sample"]["sentences"]) + "\n\n")
        for seg in cfg["segments"]:
            f.write(f"# 第 {seg['id']} 段（{seg['start']} 秒起）\n" + "\n".join(s["spoken"] for s in seg["sentences"]) + "\n\n")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
