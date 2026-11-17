# -*- coding: utf-8 -*-
"""只用 timing_actual.json 中的实际句子时间，按 tts_input.json 的 display 文字重写字幕（不重新合成音频）。"""
import json
import os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(R, "scripts", "tts_input.json"), encoding="utf-8"))
tim = json.load(open(os.path.join(R, "timing_actual.json"), encoding="utf-8"))
texts = [s["display"] for g in cfg["segments"] for s in g["sentences"]]
assert len(texts) == len(tim["cues"])


def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


with open(os.path.join(R, "subtitle.srt"), "w", encoding="utf-8") as f:
    for i, (c, t) in enumerate(zip(tim["cues"], texts), 1):
        c["text"] = t
        f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{t}\n\n")
json.dump(tim, open(os.path.join(R, "timing_actual.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"字幕已按实际时间重写：{len(texts)} 条")
