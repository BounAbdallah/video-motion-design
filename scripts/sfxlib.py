import numpy as np
from scipy import signal
from scipy.io import wavfile

"""sfxlib : petite bibliothèque de synthèse audio pour vidéos motion design.

Usage :
    import sfxlib as S
    S.init(60.0)                 # durée totale en secondes (à appeler en premier)
    S.whoosh(1.2); S.impact(1.5, 0.5, True)
    # S.L / S.R  = buffers musique ; S.SL / S.SRr = buffers effets
"""
SR = 44100
DUR = 0.0
N = 0
rng = np.random.default_rng(3)
L = R = SL = SRr = None


def init(dur):
    """Alloue les buffers stéréo (musique et effets) pour une durée donnée."""
    global DUR, N, L, R, SL, SRr
    DUR = float(dur); N = int(SR * DUR)
    L = np.zeros(N); R = np.zeros(N)
    SL = np.zeros(N); SRr = np.zeros(N)


def m2f(m): return 440.0 * 2 ** ((m - 69) / 12)


def add(bufL, bufR, x, t, pan=0.0, g=1.0):
    """Ajoute le signal x à l'instant t (s), avec panoramique pan (-1..1) et gain g."""
    i = int(t * SR)
    if i >= N or i + len(x) <= 0: return
    j = min(N, i + len(x)); x = x[:j - i] * g
    gl = np.cos((pan + 1) * np.pi / 4); gr = np.sin((pan + 1) * np.pi / 4)
    bufL[i:j] += x * gl * 1.414; bufR[i:j] += x * gr * 1.414


def env_adsr(n, a, d, s, r, sus_len):
    A = int(a * SR); D = int(d * SR); S = int(sus_len * SR); Rr = int(r * SR)
    e = np.concatenate([np.linspace(0, 1, max(A, 1)), np.linspace(1, s, max(D, 1)), np.full(max(S, 0), s), np.linspace(s, 0, max(Rr, 1))])
    return e[:n] if len(e) >= n else np.pad(e, (0, n - len(e)))


def saw(f, n, harm=14):
    t = np.arange(n) / SR; x = np.zeros(n)
    for k in range(1, harm + 1):
        if f * k > 12000: break
        x += np.sin(2 * np.pi * f * k * t) / k
    return x * 0.6


def lp(x, fc, order=2):
    sos = signal.butter(order, fc, 'low', fs=SR, output='sos'); return signal.sosfilt(sos, x)


def hp(x, fc, order=2):
    sos = signal.butter(order, fc, 'high', fs=SR, output='sos'); return signal.sosfilt(sos, x)


def bp(x, f1, f2, order=2):
    sos = signal.butter(order, [f1, f2], 'band', fs=SR, output='sos'); return signal.sosfilt(sos, x)


# ---------------- EFFETS SONORES ----------------
def shaped_noise(dur, fc0, fc1, width=0.6, shape=0.65, curve=1.0):
    n = int(dur * SR)
    x = rng.standard_normal(n + 2048)
    f, tfr, Z = signal.stft(x, SR, nperseg=1024)
    tn = np.clip(tfr / dur, 0, 1)
    fc = fc0 * (fc1 / fc0) ** (tn ** curve)
    lf = np.log2(np.maximum(f, 20))[:, None]
    mask = np.exp(-((lf - np.log2(fc)[None, :]) ** 2) / (2 * width ** 2))
    _, y = signal.istft(Z * mask, SR, nperseg=1024)
    y = y[:n]
    tt = np.arange(n) / n
    e = np.where(tt < shape, (tt / shape) ** 2, ((1 - tt) / (1 - shape)) ** 1.5)
    y = y * e
    return y / (np.abs(y).max() + 1e-9)


def whoosh(t, dur=0.8, g=0.5, up=True, pan0=-0.6, pan1=0.6):
    y = shaped_noise(dur, 250 if up else 3000, 3500 if up else 300, 0.7, 0.62)
    half = len(y) // 2
    add(SL, SRr, y[:half], t, pan0, g); add(SL, SRr, y[half:], t + half / SR, pan1, g)


def impact(t, g=0.6, bright=False):
    n = int(1.6 * SR); tt = np.arange(n) / SR
    f = 42 + 40 * np.exp(-tt * 12)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)
    nz = lp(rng.standard_normal(n), 1800 if not bright else 5000) * np.exp(-tt * 14) * 0.6
    y = sub + nz
    if bright:
        y += 0.25 * hp(rng.standard_normal(n), 4000) * np.exp(-tt * 5)
    add(SL, SRr, y / np.abs(y).max(), t, 0, g)


def pop(t, g=0.18, f0=1500, pan=0.0):
    n = int(0.09 * SR); tt = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-tt * 60))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 45) * np.minimum(1, tt / 0.002)
    y += 0.08 * hp(rng.standard_normal(n), 3000) * np.exp(-tt * 200)
    add(SL, SRr, y, t, pan, g)


def click(t, g=0.12, pan=0.0):
    n = int(0.03 * SR); tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * 3200 * tt) * np.exp(-tt * 260) + 0.4 * hp(rng.standard_normal(n), 5000) * np.exp(-tt * 400)
    add(SL, SRr, y, t, pan, g)


def blip(t, f=1200, g=0.1, pan=0.0, dur=0.12):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * tt + 0.8 * np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt * 30)) * np.exp(-tt * 28) * np.minimum(1, tt / 0.002)
    add(SL, SRr, y, t, pan, g)


def ding(t, f=1320, g=0.12, pan=0.0):
    n = int(1.0 * SR); tt = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt * d) for a, r, d in [(1, 1, 4), (.4, 2.76, 7), (.2, 5.4, 11)])
    add(SL, SRr, y * np.minimum(1, tt / 0.002), t, pan, g)


def riser(t0, t1, g=0.3):
    dur = t1 - t0
    y = shaped_noise(dur, 300, 7000, 0.55, 0.97, 1.6)
    n = len(y); tt = np.arange(n) / SR
    f = 200 * (8 ** (tt / dur) )
    y = y + 0.25 * np.sin(2 * np.pi * np.cumsum(f) / SR) * (tt / dur) ** 2
    add(SL, SRr, y / np.abs(y).max(), t0, 0, g)


def shimmer(t, dur=0.8, g=0.09):
    k = 0
    for i, m in enumerate([84, 88, 91, 96, 100, 103, 108]):
        tt0 = t + i * dur / 9
        n = int(0.5 * SR); tt = np.arange(n) / SR
        y = np.sin(2 * np.pi * m2f(m) * tt) * np.exp(-tt * 9) * np.minimum(1, tt / 0.003)
        add(SL, SRr, y, tt0, -0.6 + i * 0.2, g)


def tone_up(t0, t1, f0=300, f1=1000, g=0.07):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (tt / (t1 - t0))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, tt / 0.05) * np.minimum(1, (t1 - t0 - tt) / 0.08)
    add(SL, SRr, y, t0, 0, g)


