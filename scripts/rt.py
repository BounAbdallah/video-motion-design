"""Images de test : capture la page à des instants précis.

    python3 rt.py page.html 1.5 4 8.2 [--w 1920 --h 1080] [--out tests]
Produit tests/t_1.5.jpg, tests/t_4.0.jpg, ... puis une planche tests/sheet.jpg.
"""
import argparse, asyncio, os, subprocess
from playwright.async_api import async_playwright

ap = argparse.ArgumentParser()
ap.add_argument('html'); ap.add_argument('times', nargs='+', type=float)
ap.add_argument('--w', type=int, default=1920); ap.add_argument('--h', type=int, default=1080)
ap.add_argument('--out', default='tests'); ap.add_argument('--cols', type=int, default=5)
a = ap.parse_args()

async def main():
    os.makedirs(a.out, exist_ok=True); files = []
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width': a.w, 'height': a.h})
        pg.on('pageerror', lambda e: print('ERREUR JS :', e))
        await pg.goto('file://' + os.path.abspath(a.html)); await pg.wait_for_timeout(800)
        for t in a.times:
            f = os.path.join(a.out, f't_{t}.jpg')
            await pg.evaluate(f'render({t})'); await pg.screenshot(path=f, type='jpeg', quality=80); files.append(f)
        await b.close()
    # planche contact, dans l'ordre chronologique
    n = len(files); tw, th = (640, 360) if a.w >= a.h else (270, 480)
    ins = sum([['-i', f] for f in files], [])
    if n == 1:
        return
    fc = ''.join(f'[{i}]scale={tw}:{th}[v{i}];' for i in range(n)) + ''.join(f'[v{i}]' for i in range(n))
    fc += f"xstack=inputs={n}:layout=" + '|'.join(f'{(i % a.cols) * tw}_{(i // a.cols) * th}' for i in range(n)) + ':fill=black'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', *ins, '-filter_complex', fc, '-frames:v', '1', os.path.join(a.out, 'sheet.jpg')], check=True)
    print('Planche :', os.path.join(a.out, 'sheet.jpg'))

asyncio.run(main())
