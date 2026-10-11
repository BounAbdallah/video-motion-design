#!/usr/bin/env bash
# Minutage d'une voix off : convertit en 44,1 kHz mono et liste les silences.
#   ./timing.sh voix.mp3 [seuil_dB=-36] [durée_min=0.18]
set -e
IN="$1"; NOISE="${2:--36}"; D="${3:-0.18}"
ffmpeg -y -loglevel error -i "$IN" -ar 44100 -ac 1 voice44.wav
echo "Durée : $(ffprobe -v error -show_entries format=duration -of csv=p=0 voice44.wav) s"
ffmpeg -i voice44.wav -af "silencedetect=noise=${NOISE}dB:d=${D}" -f null - 2>&1 \
 | grep -oE "silence_(start|end): [0-9.]+" | paste - - | awk '{printf "silence %7.2f -> %7.2f\n",$2,$4}'
