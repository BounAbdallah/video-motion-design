"""Génère un fichier .srt depuis le tableau CAP=[[début,fin,"texte"],...] de la page HTML.
    python3 srt.py page.html sous-titres.srt
"""
import re, sys, json
s = open(sys.argv[1], encoding='utf-8').read()
caps = json.loads(re.search(r'const CAP=(\[.*?\]);', s, re.S).group(1))
f = lambda t: '%02d:%02d:%02d,%03d' % (t // 3600, t % 3600 // 60, int(t % 60), round((t % 1) * 1000) % 1000)
open(sys.argv[2], 'w', encoding='utf-8').write('\n'.join(f"{i+1}\n{f(a)} --> {f(b)}\n{c}\n" for i, (a, b, c) in enumerate(caps)))
print(len(caps), 'sous-titres écrits')
