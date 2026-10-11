#!/usr/bin/env bash
# Assemble image + son.   ./mux.sh video_only.mp4 audio.wav Ma-Video-16x9.mp4 [--web]
set -e
ffmpeg -y -loglevel error -i "$1" -i "$2" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart "$3"
if [ "$4" == "--web" ]; then
  ffmpeg -y -loglevel error -i "$3" -vf "scale=-2:720" -c:v libx264 -crf 28 -preset slow -c:a aac -b:a 128k -movflags +faststart "${3%.mp4}-web-720p.mp4"
fi
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$3"
