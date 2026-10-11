# 🎬 video-motion-design — un skill Claude pour créer des vidéos en motion design

Ce skill apprend à Claude à produire des **vidéos promo en motion design** à partir d'une simple voix off. Il ne faut aucun logiciel de montage : tout est généré par le code.

```
Script voix off  →  MP3 (ElevenLabs…)  →  Animation HTML  →  Musique + effets  →  MP4 16:9 · 9:16 · 60 s
```

👉 Aperçu : [`example/apercu.mp4`](example/apercu.mp4) (10 s, généré entièrement par les scripts du dépôt)

## Ce que fait le skill
- Il écrit le **script de la voix off** au bon rythme (≈ 2,5 mots par seconde).
- Il analyse ton MP3 et **cale chaque scène et chaque sous-titre** sur les phrases.
- Il code l'animation dans une page HTML : textes, interfaces, cartes, mouvements 3D, sous-titres.
- Il **génère la musique** (120 BPM, marimba, percussions) et **les effets sonores** (whoosh, impact, pop, ding…), puis mixe le tout avec la voix.
- Il produit le MP4 final, la **version verticale** pour TikTok, Reels et WhatsApp, une **version courte** de 60 s, les sous-titres `.srt` et une version web légère.

## Installation

**Comme skill Claude**
- Sur Claude : importer le dossier `video-motion-design` (zippé) dans la section Skills des paramètres.
- Avec Claude Code : copier le dossier dans `~/.claude/skills/`.

Ensuite, il suffit de demander : *« Fais-moi une vidéo de 60 s pour présenter mon application »*.

**Prérequis pour exécuter les scripts**
```bash
pip install -r requirements.txt
playwright install chromium
# + ffmpeg installé sur la machine
```

## Essayer l'exemple
```bash
cd example
python3 ../scripts/rt.py index.html 1.5 4.2 6 8.6 --out tests          # images de test
python3 ../scripts/sound.py --dur 10 --transitions 0.4,3.2,7.0 \
        --pops 3.9,4.7,5.5 --dings 8.0 --end 7.0                       # bande son
python3 ../scripts/rf.py index.html --dur 10                           # rendu
../scripts/mux.sh video_only.mp4 audio.wav exemple.mp4                 # assemblage
```

## Contenu du dépôt
| Fichier | Rôle |
|---|---|
| `SKILL.md` | La méthode complète que Claude suit |
| `scripts/timing.sh` | Minutage de la voix off (détection des silences) |
| `scripts/voice_prep.sh` | Décalage et mise à la durée de la voix (44,1 kHz) |
| `scripts/rt.py` | Images de test + planche contact |
| `scripts/rf.py` | Rendu vidéo 60 i/s avec flou de mouvement |
| `scripts/sound.py` | Musique + effets + mix avec la voix |
| `scripts/sfxlib.py` | Bibliothèque de synthèse sonore |
| `scripts/mux.sh` | Assemblage image + son, version web 720p |
| `scripts/srt.py` | Sous-titres `.srt` depuis la page |
| `scripts/seg_example.py` | Modèle pour un montage court |
| `example/` | Exemple complet de 10 s |

## Principe technique
La page HTML expose une fonction `render(t)` qui dessine l'image exacte à l'instant `t`. Playwright appelle `render(0)`, `render(1/60)`, `render(2/60)`… et capture chaque image. ffmpeg assemble le tout. Le rendu est donc **déterministe** : même code, même vidéo, à l'image près.

## Auteur
**Bouna Bin Abdallah Dramé**, fondateur et CTO de NWS, développeur full-stack (Dakar, Sénégal).
Cette méthode est enseignée dans la formation **Motion Design avec l'IA** (Claude, ChatGPT, Gemini, ElevenLabs).

Licence MIT. Polices incluses dans `example/assets` : Space Grotesk et DM Sans (SIL Open Font License).
