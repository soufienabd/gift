# Limo — cadeaux 3D en Reel

Ce dépôt contient un script Blender qui génère deux vidéos promotionnelles verticales MP4 :

- `limo-cadeaux-5s.mp4` — 5 secondes
- `limo-cadeaux-8s.mp4` — 8 secondes

Les vidéos sont en 1080 × 1920, 30 images/seconde, avec un cadeau 3D animé, une couronne, des pierres brillantes, un décor violet/or et des textes en français. Les éléments 3D sont créés de façon procédurale : aucun fichier source supplémentaire n'est requis.

## Génération

Installez Blender avec la prise en charge FFmpeg, puis exécutez à la racine du dépôt :

```bash
blender -b -P render_reels.py -- --output-dir exports
```

Les fichiers MP4 seront écrits dans `exports/`. Le rendu nécessite Blender et peut prendre plusieurs minutes selon la machine.

## Personnalisation

Les textes, couleurs, durée, résolution et modèles sont définis dans `render_reels.py`. Les captures d'écran fournies dans la conversation ne sont pas incluses automatiquement dans le rendu ; pour les utiliser comme images ou références visuelles, ajoutez-les au dépôt et adaptez le script.
