#!/usr/bin/env bash
# 一键复现：合成 → （可选）机器转写核对 → 技术核对；日志写入 run_log.txt
# 用法：bash scripts/run_all.sh <TTS 模型目录> [paraformer 目录] [SenseVoice 目录]
set -euo pipefail
cd "$(dirname "$0")/.."
TTS="$1"; PARA="${2:-}"; SV="${3:-}"
{
  echo "运行时间(UTC): $(date -u '+%Y-%m-%d %H:%M:%S')"
  python3 -c "import sys, platform, importlib.metadata as m; print('Python', platform.python_version(), '| sherpa-onnx', m.version('sherpa-onnx'), '| numpy', m.version('numpy'), '| scipy', m.version('scipy'), '| soundfile', m.version('soundfile'))"
  ffmpeg -version | head -1
  echo; echo "[合成]"; python3 scripts/synthesize.py --model-dir "$TTS"
  if [ -n "$PARA" ]; then echo; echo "[机器转写核对：paraformer-zh-small（不是人工试听）]"; python3 scripts/asr_check.py --kind paraformer --asr-dir "$PARA" --audio-dir audio; fi
  if [ -n "$SV" ]; then echo; echo "[机器转写核对：SenseVoice（不是人工试听）]"; python3 scripts/asr_check.py --kind sensevoice --asr-dir "$SV" --audio-dir audio; fi
  echo; echo "[技术核对]"; python3 scripts/verify.py
} 2>&1 | grep -v "^$" > run_log.txt
tail -3 run_log.txt
