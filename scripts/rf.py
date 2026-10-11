"""Rendu final : capture render(t) à 60 i/s, flou de mouvement, sortie H.264 30 i/s.

    python3 rf.py page.html --dur 60 [--w 1920 --h 1080] [--out video_only.mp4] [--map seg.py]
--map : fichier Python définissant W(t_court) -> t_complet (montage court, voir seg_example.py).
Long : lancer en arrière-plan →  nohup python3 rf.py ... > rf.log 2>&1 &   (le log finit par "done 0").
"""
import argparse, asyncio, os, subprocess, runpy
from playwright.async_api import async_playwright

ap = argparse.ArgumentParser()
ap.add_argument('html'); ap.add_argument('--dur', type=float, required=True)
ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
ap.add_argument('--fps', type=int, default=60); ap.add_argument('--out', default='video_only.mp4')
ap.add_argument('--map', default=None); ap.add_argument('--crf', default='16')
a = ap.parse_args()
W = runpy.run_path(a.map)['W'] if a.map else (lambda t: t)
N = int(a.dur * a.fps)

async def main():
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(a.fps), '-i', '-',
        '-vf', "tmix=frames=2:weights='1 1',fps=30", '-c:v', 'libx264', '-preset', 'slow', '-crf', a.crf,
        '-pix_fmt', 'yuv420p', a.out], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': a.w, 'height': a.h})
        await pg.goto('file://' + os.path.abspath(a.html)); await pg.wait_for_timeout(1500)
        for i in range(N):
            await pg.evaluate(f'render({W(i / a.fps):.4f})')
            ff.stdin.write(await pg.screenshot(type='jpeg', quality=94))
            if i % 300 == 0: print(i, '/', N, flush=True)
        await b.close()
    ff.stdin.close(); ff.wait(); print('done', ff.returncode, flush=True)

asyncio.run(main())
