#!/usr/bin/env bash
# Décale la voix (offset en s) et la complète jusqu'à la durée totale de la vidéo, en 44,1 kHz mono.
#   ./voice_prep.sh voice44.wav 0.6 64.0   -> voice48.wav
set -e
MS=$(python3 -c "print(int(float('$2')*1000))")
ffmpeg -y -loglevel error -i "$1" -af "adelay=${MS}|${MS},apad=whole_dur=$3" -t "$3" -ar 44100 -ac 1 voice48.wav
echo "voice48.wav prêt ($3 s, offset $2 s)"
