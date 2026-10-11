"""Bande son complète : musique 120 BPM + effets synchronisés + voix off, mixée dans audio.wav.

    python3 sound.py --dur 64 --voice voice48.wav --transitions 6.6,20.1,40.3 \
        --pops 9.2,11.4,13.0 --dings 30.1 --end 58.7 [--out audio.wav]

--transitions : changements de scène (riser + impact + whoosh + shimmer, break musical juste avant)
--pops        : apparitions d'éléments (whoosh court + pop)
--dings       : moments de validation (ding)
--end         : début de l'écran final (accord long, la rythmique s'arrête)
Pour aller plus loin, ajouter des appels S.click/S.blip/S.tone_up… dans la section EFFETS PERSO.
"""
import argparse
import numpy as np
from scipy import signal
from scipy.io import wavfile
import sfxlib as S

ap = argparse.ArgumentParser()
ap.add_argument('--dur', type=float, required=True); ap.add_argument('--voice', default=None)
ap.add_argument('--transitions', default=''); ap.add_argument('--pops', default=''); ap.add_argument('--dings', default='')
ap.add_argument('--end', type=float, default=None); ap.add_argument('--intro', type=float, default=None,
    help="fin de l'intro calme (par défaut : première transition)")
ap.add_argument('--out', default='audio.wav'); ap.add_argument('--music', type=float, default=0.42)
a = ap.parse_args()
lst = lambda s: [float(x) for x in s.split(',') if x.strip()]
TR, POPS, DINGS = lst(a.transitions), lst(a.pops), lst(a.dings)

S.init(a.dur)
SR, N, DUR = S.SR, S.N, S.DUR
rng = np.random.default_rng(5)
END = a.end if a.end else DUR - 4
G0 = a.intro if a.intro is not None else (TR[0] if TR else 4.0)
BRK = [(t - 0.5, t) for t in TR[1:]]
inbrk = lambda t: any(x <= t < y for x, y in BRK)
addm = lambda x, t, pan=0.0, g=1.0: S.add(S.L, S.R, x, t, pan, g)

# ---------- MUSIQUE : 120 BPM, Am7 – Fmaj7 – C – G ----------
CH = [([57, 60, 64, 67], 45), ([53, 57, 60, 64], 41), ([55, 59, 62, 65], 43), ([52, 55, 59, 62], 40)]
chord = lambda t: CH[int(t // 2) % 4]
for bar in range(int(END // 2) + 1):
    t0 = bar * 2.0; notes, _ = chord(t0); n = int(2.6 * SR)
    pad = sum(S.saw(S.m2f(m) * (1 + d), n, 8) for m in notes for d in (-0.004, 0, 0.004))
    cut = 700 + 900 * min(1, t0 / G0) if t0 < G0 else 1700
    pad = S.lp(pad, cut) * S.env_adsr(n, 0.4, 0.3, 0.8, 0.6, 1.6) * 0.04
    addm(pad, t0, -0.3, 0.8); addm(pad, t0 + 0.012, 0.3, 0.8)

def pluck(f, dur=0.35, br=0.25):
    n = int(dur * SR); tt = np.arange(n) / SR
    return (np.sin(2*np.pi*f*tt) + br*np.sin(4*np.pi*f*tt)) * np.exp(-tt*10) * np.minimum(1, tt/0.003)

pat = [0, 0.375, 0.75, 1.0, 1.375, 1.75]          # motif 3+3+2 façon marimba
for bar in range(1, int(END // 2)):
    t0 = bar * 2.0; notes, _ = chord(t0)
    seq = [notes[0]+12, notes[2]+12, notes[1]+12, notes[3]+12, notes[2]+24, notes[1]+12]
    for k, p in enumerate(pat):
        addm(pluck(S.m2f(seq[k])), t0 + p, 0.4*np.sin(k*1.3), 0.03 if t0 < G0 else 0.042)

def kick():
    n = int(0.45*SR); tt = np.arange(n)/SR; f = 48 + 110*np.exp(-tt*32)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-tt*7.5)
def shaker():
    n = int(0.07*SR); tt = np.arange(n)/SR
    return S.bp(rng.standard_normal(n), 5000, 10000) * np.exp(-tt*45)
def conga(f=220):
    n = int(0.25*SR); tt = np.arange(n)/SR; ff = f*(1 + 0.3*np.exp(-tt*40))
    return np.sin(2*np.pi*np.cumsum(ff)/SR) * np.exp(-tt*14)

K, SH = kick(), shaker(); kicks = []
t = np.ceil(G0 * 2) / 2
while t < END - 0.3:
    if not inbrk(t):
        _, bn = chord(t); n = int(0.3*SR); tt = np.arange(n)/SR
        addm(np.sin(2*np.pi*S.m2f(bn)*tt)*np.exp(-tt*5)*np.minimum(1, tt/0.005), t, 0, 0.15)   # basse
        addm(K, t, 0, 0.36); kicks.append(t)
        for k in range(4): addm(SH, t + k*0.125, 0.3, 0.026 if k % 2 else 0.015)
    t += 0.5
for bar in range(int(G0 // 2) + 1, int(END // 2)):
    t0 = bar * 2.0
    for p, f in [(0.75, 240), (1.25, 200), (1.5, 240), (1.75, 180)]:
        if not inbrk(t0 + p) and t0 + p < END - 0.3: addm(conga(f), t0 + p, -0.4, 0.05)

side = np.ones(N); tt = np.arange(int(0.3*SR))/SR; duck = 1 - 0.35*np.exp(-tt*9)   # sidechain
for kt in kicks:
    i = int(kt*SR); j = min(N, i + len(duck)); side[i:j] = np.minimum(side[i:j], duck[:j-i])
S.L *= side; S.R *= side

nf = int(min(5, DUR - END) * SR)                     # accord final
if nf > 0:
    fin = sum(S.saw(S.m2f(m), nf, 10) for m in [45, 57, 60, 64, 67, 72])
    fin = S.lp(fin, 2400) * np.exp(-np.arange(nf)/SR*0.8) * np.minimum(1, np.arange(nf)/(0.02*SR)) * 0.035
    addm(fin, END, -0.2); addm(fin, END + 0.01, 0.2)

# ---------- EFFETS ----------
S.riser(0.0, 0.6, 0.12); S.whoosh(0.4, 0.8, 0.15, True, -0.4, 0.4)
for ts in TR:
    if ts > 0.8: S.riser(ts - 0.7, ts - 0.05, 0.18)
    S.impact(ts, 0.45, True); S.whoosh(ts - 0.1, 0.5, 0.3); S.shimmer(ts + 0.2, 0.9, 0.07)
for ts in POPS:
    S.whoosh(ts - 0.15, 0.4, 0.18); S.pop(ts + 0.15, 0.1, 1100)
for ts in DINGS:
    S.ding(ts, 1568, 0.06)
if a.end:
    S.riser(END - 0.7, END - 0.05, 0.2); S.impact(END, 0.55, True); S.shimmer(END + 0.3, 1.4, 0.1)
# --- EFFETS PERSO : ajouter ici S.click(t), S.blip(t, f), S.tone_up(t0, t1), S.ding(t, f)...

# ---------- MIX ----------
vv = np.zeros(N)
if a.voice:
    sr_v, v = wavfile.read(a.voice)
    assert sr_v == SR, f'La voix doit être en {SR} Hz (elle est en {sr_v} Hz) : utiliser voice_prep.sh'
    v = v.astype(float) / 32768.0
    if v.ndim > 1: v = v.mean(1)
    vv[:min(N, len(v))] = v[:N]
env = np.convolve(np.abs(vv), np.ones(int(0.25*SR))/int(0.25*SR), 'same'); env /= env.max() + 1e-9
duckv = 1 - 0.55*np.clip(env*4, 0, 1)                # la musique baisse quand la voix parle

def reverb(x, dur=1.8, wet=0.25):
    n = int(dur*SR); tt = np.arange(n)/SR
    ir = S.lp(rng.standard_normal(n)*np.exp(-tt*3.5), 5000); ir /= np.sqrt((ir**2).sum())
    return x + wet*signal.fftconvolve(x, ir)[:len(x)]

Lm = reverb(S.L, 2.0, 0.2)*duckv; Rm = reverb(S.R, 2.0, 0.2)*duckv
SLx = reverb(S.SL, 1.5, 0.28); SRx = reverb(S.SRr, 1.5, 0.28)
mus = np.stack([Lm*0.75 + SLx*0.8, Rm*0.75 + SRx*0.8], 1)
mus = mus/(np.abs(mus).max() + 1e-9)*a.music
mix = mus + (np.stack([vv, vv], 1)/(np.abs(vv).max() + 1e-9)*0.85 if a.voice else 0)
fade = np.ones(N); k = int(1.0*SR); fade[-k:] = np.linspace(1, 0, k)**2
mix = mix*fade[:, None]
mix = np.tanh(mix/np.abs(mix).max()*1.15)*0.92
wavfile.write(a.out, SR, (mix*32767).astype(np.int16))
print('ok :', a.out)
