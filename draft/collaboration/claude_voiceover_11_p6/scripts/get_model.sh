#!/usr/bin/env bash
# 下载并校验 MeloTTS 中英混合模型（sherpa-onnx 转换版，MIT 许可，单一女声）。用法：bash get_model.sh 目标目录
set -euo pipefail
DIR="${1:-./tts_model}"
URL=https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-melo-tts-zh_en.tar.bz2
SHA=e58351ed7149f290a54534538badd4077cdbe6fddc964b24d0bee870415d1514
mkdir -p "$DIR"; cd "$DIR"
[ -f vits-melo-tts-zh_en.tar.bz2 ] || curl -sSL -o vits-melo-tts-zh_en.tar.bz2 "$URL"
echo "$SHA  vits-melo-tts-zh_en.tar.bz2" | sha256sum -c -
tar xjf vits-melo-tts-zh_en.tar.bz2
echo "模型目录：$(pwd)/vits-melo-tts-zh_en"
