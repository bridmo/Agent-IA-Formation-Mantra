---
name: meta-ad-video
description: >
  Production de vidéos créa (motion design / kinetic text) via Remotion, pour
  Meta/social. Compositions React animées — texte cinétique sur fond de marque, end card
  certifications, formats 9:16 + 4:5 — rendues en MP4 prêt à diffuser. Couvre le choix/adaptation
  d'une composition, la musique (ducking, choix de piste), le rendu et la validation. Déclencher
  quand l'utilisateur dit "vidéo créa", "créa vidéo", "vidéo Meta", "kinetic text", "motion",
  "monter une vidéo", "vidéo 42%", "vidéo agents", "Remotion", "changer la musique de la vidéo",
  "rendre la vidéo", "décliner en 4:5". Pour les créas IMAGE (remix concurrents) → meta-ad-remix.
---

## Calibration (à faire avant le premier usage)

Ce skill porte une méthode. Il lui manque votre contexte. Renseignez :

| À remplir | Où |
|---|---|
| Votre charte animée | `brain/design-system.md` |
| Vos gabarits de vidéo | la table des compositions de ce fichier |
| Votre musique sous licence | à sourcer, ne jamais utiliser une piste non libérée |

Tant que ces cases sont vides, le résultat sera correct dans la forme et creux sur le fond.

# Meta Ad Video — créas vidéo motion {{COMPANY}} (Remotion)

**Objectif mesurable par défaut :** à définir avant de produire. Sans objectif chiffré, une création ne se juge pas.
Si {{OWNER}} vise une autre offre / un autre objectif (notoriété, trafic), le demander avant de produire.

## contexte de l'entreprise à charger AVANT toute action

Ce skill tourne sans CLAUDE.md. Lire obligatoirement :

| Fichier | Pourquoi |
|---|---|
| `brain/design-system.md` | Votre palette. **Les valeurs de ce fichier sont un exemple de charte, pas la vôtre.** |
| `brain/voice-tone.md` + `brain/editorial-guide.md` | voix de marque pour le texte à l'écran |
| `brain/offre.md` | Vérité produit (prix, durées, stats) — ne JAMAIS inventer un chiffre |
| `brain/messaging.md` | Hooks par persona |
| `skills/meta-ad-remix/references/design-rules.md` | Règles design figées partagées (golden ratio, zone morte, bandeau de labels officiels, Trustpilot) |
| `channels/social/creatives/README.md` | Carte du studio (engine / assets / tests / final) |
| memory `feedback_design_system`, `project_logo_compliance`, `project_video` | Pièges connus |

## Le moteur — où ça vit

Tout est dans **`channels/social/creatives/engine/remotion/`** (projet Remotion autonome). On rend d'ici.

| Élément | Chemin |
|---|---|
| Compositions (1 fichier par créa) | `engine/remotion/src/*.tsx` |
| Registre des compositions (durées, formats, props défaut) | `engine/remotion/src/Root.tsx` |
| Primitives de marque partagées | `engine/remotion/src/TextEvolve.tsx` exporte `BRAND`, `mark`, `EndCard`, `useFonts`, `GAP` |
| Assets runtime (fonts, logos, badges, pistes audio) | `engine/remotion/public/` (chargés via `staticFile()`) |
| Sources design (logos couleur outils, badges officiels) | `channels/social/creatives/assets/` |

⚠️ Un subagent Remotion ne voit que ces fichiers — pour la voix/ICP, charger explicitement les `agents/*.md` ci-dessus.

## Compositions existantes

| id | Durée | Format | Sujet | Musique défaut |
|---|---|---|---|---|
| `TextEvolve` | 410f | 1080×1920 | Kinetic text « 42% des offres… mentionnent l'IA » → CTA vers l’offre | `music-lofi.mp3` |
| `TextEvolve-4x5` | 410f | 1080×1350 | Idem, format feed | `music-lofi.mp3` |
| `TextEvolveAgent` | 450f | 1080×1920 | Variante « Cette pub a été créée par un Agent IA » | `music-positive.mp3` |
| `AgentDemo` | 370f | 1080×1920 | Terminal Claude Code qui automatise un process marketing | `music-corporate.mp3` |
| `Agents` | 356f | 1080×1920 | Constellation d'outils → « Déployez vos agents IA » | — |

(Hors scope : `VoxPop` et `Cosmonaute` = expérimentaux, voir « Hors scope » en bas.)

## Formats & durées par réseau (cibles de diffusion)

Référence pour décliner au bon ratio/durée selon le placement. **30 fps · H.264** partout (forcé par `remotion.config.ts`).

| Réseau · placement | Ratio | Dimensions | Durée idéale / max |
|---|---|---|---|
| Instagram / Facebook **Reels** | 9:16 | 1080×1920 | idéal 15-30 s · max 90 s |
| Instagram / Facebook **Stories** | 9:16 | 1080×1920 | 15 s / segment · max 2 min |
| Instagram / Facebook **Feed** | 4:5 | 1080×1350 | idéal < 30 s · max 2 min |
| Feed **carré** | 1:1 | 1080×1080 | max 2 min |
| **TikTok** | 9:16 | 1080×1920 | idéal 9-21 s · max 60 s (pub) |
| **YouTube Shorts** | 9:16 | 1080×1920 | max 60 s |
| **YouTube** in-stream | 16:9 | 1920×1080 | bumper 6 s · skippable ≥ 12 s |
| **LinkedIn** | 1:1 ou 4:5 | 1080×1080 / 1080×1350 | idéal < 30 s · max 10 min |
| **X / Twitter** | 16:9 ou 1:1 | 1920×1080 / 1080×1080 | max 2 min 20 |
| **Pinterest** | 9:16 ou 1:1 | 1080×1920 / 1080×1080 | max 60 s |

**Ce que {{COMPANY}} produit** : **9:16 (1080×1920)** + **4:5 (1080×1350)**, ~12-15 s → couvre Reels/Stories/TikTok/Shorts (9:16) et Feed/LinkedIn (4:5). Le **1:1** s'ajoute au besoin (nouvelle `<Composition>` 1080×1080 dans `Root.tsx`). Toujours garder le message clé **hors zone morte basse** (20 % en 9:16). Sources : [youlovewords](https://www.youlovewords.com/reseaux-sociaux-quels-formats-pour-vos-videos/) + specs plateformes 2025.

## Règles motion (en plus des règles design partagées)

1. **Hiérarchie = 1 message dominant par beat.** Le hook domine (gros, `mark` = surligneur mustard sur la punchline) ; tout le reste lui est subordonné. Cf. design-rules.md (golden ratio, niveaux 1/2).
2. **Texte cinétique** : beats successifs (apparition spring + `interpolate`, fondu entrée/sortie), jamais un mur de texte. Une idée par beat.
3. **Format-aware** : les composants lisent la hauteur (`const nine = height > 1700`). 9:16 = zone morte 20 % en bas ; 4:5 = ~6 %. Toujours décliner les deux si demandé, et vérifier le 4:5 (le texte/end card se recalent via `s = height/1920`).
4. **Carte de fin** = la conclusion sur fond sombre : votre logo, votre preuve sociale (nombre de clients, pas nombre d'avis), l'accroche agrandie, et un bandeau clair avec vos labels officiels. **Deux logos maximum** dans le bandeau.
5. **Lisibilité mobile** : cible iPhone 6-7", typo généreuse, rien d'important dans les 20 % du bas.

## Musique

- **Ducking** : `volume` en fonction du frame (fade in au début, fade out à la fin ; baissée sous une voix/un texte clé puis remontée). Voir le pattern `vol(f)` dans les compositions.
- **`musicStart`** (en secondes) : décaler le départ pour attaquer sur une montée plutôt que sur l'attaque sèche.
- **Override propre** sans toucher les défauts : `--props '{"music":"…","musicStart":N}'`.
- **Feedbacks figés** ({{OWNER}}) : pas de musique trop agressive / « vénère » ni trop lugubre (« on dirait une news sur un meurtre »). Adapter le mood à la créa (lofi posé pour le 42%, guitare positive pour l'« Agent IA »). Toujours faire écouter avant de figer.

## Rendu & sortie

```bash
cd channels/social/creatives/engine/remotion
npx remotion render <Id> out/<nom>.mp4                                   # piste par défaut
npx remotion render <Id> out/<nom>.mp4 --props '{"music":"music-lofi.mp3","musicStart":0}'  # override musique
npx remotion still <Id> /tmp/check.png --frame=40                        # vérif rapide d'une frame
```

- Rendus **candidats / comparaisons** → restent dans `engine/remotion/out/` puis `channels/social/creatives/tests/videos/`.
- **Version figée et validée** → promue dans `channels/social/creatives/final/videos/`.
- Toujours **ouvrir le MP4** (`open`) et vérifier une frame clé avant de présenter.

## Ligne rouge — évoquer ≠ cloner

- **Logos officiels** (labels, certifications, plateformes d'avis, logos d'outils) : toujours le vrai fichier fourni par l'émetteur, **jamais** recréé, recoloré, détouré ou déformé. La plupart des chartes d'usage l'interdisent explicitement, et une infraction peut vous coûter le droit d'utiliser le label.
- **Ne pas pixel-cloner** une marque tierce (interface Claude, Welcome to the Jungle…) : on **évoque** une esthétique, on ne copie pas. Pour un employeur à l'écran → marque **fictive générique** (ex. « NEXA AI »), jamais un vrai logo concurrent.
- **Aucun faux témoignage, aucun avis inventé.** C'est illégal dans la plupart des juridictions, indépendamment du secteur.

## Validation

1. Présenter le(s) MP4 à {{OWNER}} (+ frames clés si besoin).
2. Attendre **validation explicite** du montage ET du texte à l'écran. Un go d'exécution ≠ approbation copy (memory `feedback_ad_copy_validation`).
3. Push **manuel** dans Meta Ads Manager (pas d'API Meta branchée).
4. Logger les corrections de {{OWNER}} dans `memory/` (musique, montage, voix).

## Anti-patterns

- Inventer un chiffre produit → vérifier `brain/offre.md`.
- Mur de texte / plusieurs messages au même niveau dans un beat.
- Oublier le 4:5 (ou ne pas le vérifier après le 9:16).
- Musique trop agressive ou lugubre.
- Cloner une interface / un logo tiers.
- Promouvoir dans `final/videos/` ou pousser live sans validation explicite.

## Hors scope (pour l'instant)

Génération vidéo IA (**Veo** via `engine/gen_video.py`), détourage fond vert (`engine/chroma_key.py`) et montage **vox-pop** (`VoxPop`) sont **expérimentaux et non calibrés** — pas couverts par ce skill tant qu'ils n'ont pas fait leurs preuves.
