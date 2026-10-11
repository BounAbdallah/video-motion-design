"""Montage court : segments (en temps du montage complet) à garder, coupés dans des silences.
Utilisé par rf.py --map seg_example.py et par le script son (fonction M).
"""
SEG = [(0, 9.85), (18.85, 23.7), (34.3, 37.95), (49.2, 61.5), (72.9, 104.8)]
OFF = []; _o = 0
for a, b in SEG: OFF.append(_o); _o += b - a
DUR_S = round(_o, 3)

def W(ts):  # temps court -> temps complet
    for (a, b), f in zip(SEG, OFF):
        if ts < f + (b - a) or (a, b) == SEG[-1]: return a + ts - f

def M(t):   # temps complet -> temps court (None si coupé)
    for (a, b), f in zip(SEG, OFF):
        if a <= t < b: return f + t - a
    return None

if __name__ == '__main__':
    print('Durée courte :', DUR_S, 's')
