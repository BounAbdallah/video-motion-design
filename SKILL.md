---
name: video-motion-design
description: Créer une vidéo promo en motion design (16:9, 9:16, version courte) calée sur une voix off MP3 — script, animation HTML codée, musique et effets générés, rendu MP4 sous-titré.
---

# Vidéo motion design calée sur une voix off

Tout est fait en code, sans logiciel de montage :
animation HTML déterministe → captures Playwright → ffmpeg ; musique et effets synthétisés en Python.
Les scripts sont dans `scripts/`, un exemple complet dans `example/`.

## 0. Règles de contenu
- Ne montrer que des fonctionnalités réelles : la description fournie par l'utilisateur fait foi.
- Jamais de clients, témoignages, chiffres ou résultats inventés. Les exemples fictifs doivent être clairement génériques (« Boulangerie du quartier », « Votre marque »).
- Coordonnées, dates, prix : uniquement ceux donnés par l'utilisateur. S'ils manquent, le dire au lieu d'inventer.
- Écrire dans la langue de l'utilisateur, ton chaleureux et direct, exemples ancrés dans son marché.

## 1. Déroulé
1. **Script de la voix off d'abord** (ne pas coder avant). ≈ 2,5 mots/s → 60 s ≈ 150 mots. Une idée par phrase, phrases courtes, appel à l'action final. Livrer le texte prêt à coller dans ElevenLabs (ou autre), avec la durée estimée.
2. L'utilisateur envoie le MP3 → minutage (section 2).
3. Coder les scènes dans `index.html` sur ce minutage (section 3).
4. Images de test → corriger chevauchements, débordements, lisibilité (section 4).
5. Bande son → `audio.wav` (section 5).
6. Rendu complet en arrière-plan → assemblage → livraison (section 6).
7. Version verticale 9:16, et version courte si la vidéo est longue (sections 7–8).
8. Optionnel : SRT, version web 720p, descriptions et hashtags (section 9).

Suivre l'avancement avec une liste de tâches : script, minutage, scènes, tests, son, rendu, vertical, livraison.

## 2. Minutage de la voix
```bash
scripts/timing.sh voix.mp3            # -> voice44.wav + liste des silences
scripts/timing.sh voix.mp3 -32 0.08   # passe plus fine si des phrases sont collées
```
Construire une table phrase → (début, fin). Décaler la voix de 0,5–0,6 s (temps vidéo = temps brut + offset) et la compléter jusqu'à la durée totale (≈ fin de la voix + offset + 4–5 s d'écran final) :
```bash
scripts/voice_prep.sh voice44.wav 0.6 64.0   # -> voice48.wav
```
**Toujours 44 100 Hz** : une voix en 48 kHz désynchronise le son.
Pour raccourcir des pauses : ffmpeg `atrim` + `asetpts` + `afade` + `adelay` par segment, puis `amix=normalize=0` et `apad`.

## 3. Page d'animation (`index.html`)
Partir de `example/index.html`.
- 1920×1080 (ou 1080×1920), polices locales en woff2 (`@font-face`), palette en variables CSS. Textes ≥ 28 px en 16:9, ≥ 36 px en 9:16.
- **Fonction déterministe `render(t)`** exposée sur `window` : aucune animation CSS ni minuterie, tout est calculé à partir de `t`. Appeler `render(0)` au chargement.
- Helpers fournis dans l'exemple : `clamp`, `prog`, `lerp`, easings `eo`, `eo5`, `eio`, `back`, puis `scene()` (fondu + zoom + flou d'entrée/sortie), `pin()` (pop avec rebond), `rise()` (montée + fondu), `typ()` (frappe au clavier).
- **Sous-titres** : tableau `CAP=[[début,fin,"texte"],...]` en temps vidéo, bandeau sombre en bas, fondu de 0,12 s. Il sert aussi à générer le SRT.
- Calage : chaque élément apparaît sur le mot qui le nomme (± 0,1 s), et les changements de scène tombent dans les silences.
- Idées qui marchent :
  - interfaces maquettées (chat IA, tableau de bord, fiche produit, timeline de montage) ;
  - chiffres qui défilent, jauges qui se remplissent ;
  - badges qui « popent » ;
  - barre de progression des étapes ;
  - en-tête affiché en grand au centre, puis épinglé en haut à gauche ;
  - légère 3D (`perspective`, `translate3d`, `rotateX/Y`) ;
  - particules et halos flous en fond ;
  - écran final avec titre, badges, bouton d'appel à l'action et signature.
- Pièges :
  - un `innerHTML` réécrit après coup efface le texte déjà placé ;
  - pas de `${}` littéral dans le HTML statique ;
  - noms de fichiers de test en float (`t_11.0.jpg`).

## 4. Tests visuels
```bash
python3 scripts/rt.py index.html 1.5 4 8 12.5 20 --out tests   # images + tests/sheet.jpg
```
- Tester le milieu de chaque scène, chaque transition et l'écran final.
- Regarder la planche, puis au moins une image en pleine résolution.
- Vérifier :
  - aucun chevauchement de textes ;
  - rien de coupé ni hors cadre ;
  - un contraste suffisant ;
  - aucune erreur JS (elles s'affichent dans la console du script).

## 5. Bande son
```bash
python3 scripts/sound.py --dur 64 --voice voice48.wav \
  --transitions 0.6,9.2,21.0,40.3 --pops 10.1,11.4,13.0 --dings 30.1 --end 58.7
```
- **Musique 120 BPM**, accords Am7–Fmaj7–C–G :
  - nappes filtrées qui s'ouvrent après l'intro ;
  - marimba en motif 3+3+2, basse, kick, shaker, congas ;
  - break de 0,5 s avant chaque transition ;
  - sidechain sur le kick ;
  - accord long sur l'écran final.
- **Effets** : riser + impact + whoosh + shimmer aux transitions, whoosh + pop aux apparitions, ding aux validations. Pour le reste, ajouter des appels dans la section « EFFETS PERSO » : `S.click`, `S.blip`, `S.tone_up`, `S.ding`…
- **Mix** :
  - la musique baisse automatiquement quand la voix parle ;
  - réverbération légère, limiteur, fondu final.
- Vérifier le niveau avec `ffmpeg -i audio.wav -af volumedetect -f null -` : le max doit être autour de −2,5 dB.

`scripts/sfxlib.py` contient les fonctions de synthèse. Appeler `S.init(durée)` avant toute utilisation. Fonctions disponibles :
- `whoosh(t, dur, g, up, pan0, pan1)`
- `impact(t, g, bright)`
- `pop(t, g, f0, pan)`
- `click(t, g, pan)`
- `blip(t, f, g, pan)`
- `ding(t, f, g, pan)`
- `riser(t0, t1, g)`
- `shimmer(t, dur, g)`
- `tone_up(t0, t1, f0, f1, g)`

## 6. Rendu et assemblage
```bash
nohup python3 scripts/rf.py index.html --dur 64 > rf.log 2>&1 &
while ! grep -q done rf.log; do sleep 20; done      # ≈ 10 min par minute de vidéo
scripts/mux.sh video_only.mp4 audio.wav Ma-Video-16x9.mp4 --web   # + version 720p
```
Le rendu se fait à 60 i/s, avec un flou de mouvement (`tmix`), en sortie H.264 30 i/s (crf 16).
Avant de livrer, extraire 3 ou 4 images du MP4 final pour contrôle.

## 7. Version verticale 9:16
Copier le projet et adapter la page par remplacements de chaînes vérifiés. Écrire un petit `conv.py` avec une fonction `R(a, b)` qui signale toute chaîne introuvable. Les **timings et la bande son restent identiques**.
- Passer `body`/`#stage` en 1080×1920, recentrer la scène (x = 540, y ≈ 900–960) et replacer halos et particules.
- Panneaux larges :
  - `transform: scale(.68)` ;
  - puis agrandissement par sous-panneau selon la largeur réelle du contenu (≤ 1,4).
- Mise en page :
  - les rangées de cartes passent en colonne ;
  - les titres longs passent à la ligne ;
  - les badges s'empilent.
- Sous-titres plus grands (≈ 40 px, largeur max 960, vers y = 1580). Garder seulement les numéros dans la barre d'étapes.
- Supprimer les rotations 3D qui créent des artefacts.
- Rendu : `rt.py`/`rf.py` avec `--w 1080 --h 1920`, en réutilisant le même `audio.wav`.

## 8. Version courte (≈ 60 s) d'une vidéo longue
- Choisir les segments à garder, **coupés dans des silences** : intro, une phrase par partie, fin. Modèle : `scripts/seg_example.py`, qui définit `SEG`, `W()` (court → complet) et `M()` (complet → court).
- Image : `rf.py ... --map seg.py --dur <DUR_S>`.
- Voix : concaténer les tranches de `voice48.wav`, avec des fondus de 12 ms.
- Son :
  - régénérer la musique sur la nouvelle durée, avec les transitions remappées par `M()` ;
  - ajouter riser + whoosh + impact à chaque coupe.

## 9. Livrables annexes
- **SRT** : `python3 scripts/srt.py index.html video.srt`.
- **Version web** : option `--web` de `mux.sh` (720p, ≈ 3 Mo par minute).
- **Textes de publication** : descriptions TikTok/Instagram/WhatsApp/YouTube et hashtags adaptés au pays et à la région visés.

## 10. Livraison
Pour chaque fichier, une ligne : durée, format, usage. Puis ce que montre la vidéo en quelques puces, ce qui manque (contact, dates…) et la prochaine étape (9:16, version courte). Ne pas détailler la technique sauf si on le demande.
