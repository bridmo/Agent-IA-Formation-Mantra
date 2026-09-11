---
name: meta-ad-remix
description: >
  Veille créative Meta Ads concurrents et remix à votre marque. Scanne la Meta Ad Library des
  concurrents (brain/competitors.md), identifie les annonces qui performent (longévité,
  variantes), en extrait l'angle et la structure, puis recrée des annonces votre entreprise :
  copy réécrite (voix de marque, claims autorisés) + visuels régénérés en PNG aux formats
  Meta (1:1, 4:5, 9:16) avec la palette du design system. Déclencher quand l'utilisateur
  dit "remix concurrents", "veille Meta Ads", "créas Meta", "images Meta Ads",
  "s'inspirer des concurrents", "ad library".
---

## Calibration (à faire avant le premier usage)

Ce skill porte une méthode. Il lui manque votre contexte. Renseignez :

| À remplir | Où |
|---|---|
| Votre charte de création | `references/design-rules.md` et `brain/design-system.md` |
| Vos concurrents à surveiller | `references/ad-library-urls.md` |
| Vos preuves affichables | `brain/offre.md` |
| Vos logos officiels | un dossier d'assets, avec les fichiers fournis par les émetteurs |

Tant que ces cases sont vides, le résultat sera correct dans la forme et creux sur le fond.

# Meta Ad Remix — veille concurrents → créas {{COMPANY}}

**Objectif mesurable par défaut :** à définir avant de produire. Sans objectif chiffré, une création ne se juge pas.
Si {{OWNER}} vise une autre offre ou un autre objectif, le demander en phase 0.

## contexte de l'entreprise à charger AVANT toute action

Ce skill tourne sans CLAUDE.md. Lire obligatoirement :

| Fichier | Pourquoi |
|---|---|
| `brain/competitors.md` | Liste des concurrents + différenciation {{COMPANY}} |
| `ads/meta/meta-ia-marketing-copy.md` | Cadrage Meta validé : vouvoiement, claims autorisés/INTERDITS, offre, concepts existants |
| `brain/design-system.md` | Votre palette. **Les valeurs de ce fichier sont un exemple de charte, pas la vôtre.** |
| `brain/voice-tone.md` | voix de marque |
| `brain/messaging.md` | Hooks Meta par persona |
| `brain/offre.md` | Vérité produit (prix, durées, stats) — ne JAMAIS inventer un chiffre |

Règles mémoire critiques :
- **Hooks Meta** : tension concrète + résolution. Jamais observation + réassurance, jamais
  d'impératif-devoir (« relisez les offres »), jamais de jargon tech (« couche IA »).
  Externaliser le problème (le marché, le CV) — policy Meta interdit de viser les attributs personnels.
- **Validation copy** : un go d'exécution ≠ approbation copy. AUCUN push live sans validation
  explicite de {{OWNER}} sur titres, textes ET visuels.

## Ligne rouge — remix ≠ copie

On reprend d'un concurrent : **l'angle, la structure du message, le format, la mise en page**.
On ne reprend JAMAIS : leurs photos, leurs visuels (même retouchés), leurs logos, leur copy
mot à mot, leurs témoignages. Tout visuel est régénéré de zéro avec la palette {{COMPANY}} ;
toute copy est réécrite avec les claims {{COMPANY}}. (Droits d'auteur + policy Meta + marque.)

## Process — 5 phases

### Phase 0 — Cadrage (30 s)
Confirmer : offre poussée (défaut : bundle IA Marketing), persona cible (défaut : P2 marketeurs
5+ ans en poste), nombre de concepts attendus (défaut : 3). Si déjà précisé par {{OWNER}}, ne pas redemander.

### Phase 1 — Veille Ad Library (par concurrent)
Avec le skill `/browse` (jamais Claude-in-Chrome), pour chaque concurrent de
`references/ad-library-urls.md` :
1. Ouvrir l'URL Ad Library (annonces actives, FR).
2. Identifier la **page officielle** de l'annonceur (pas les homonymes).
3. Pour chaque annonce active : screenshot, texte primaire, titre, CTA, format
   (image/vidéo/carrousel), **date de début de diffusion** (longévité = proxy n°1 de performance),
   nombre de variantes du même concept (scaling = signal fort).
4. Sauvegarder dans `ads/meta/meta-remix/veille/YYYY-MM-DD/<concurrent>/` :
   screenshots numérotés + un `inventory.md` (tableau : annonce, date début, format, hook, angle).

Concurrents sans annonces actives : le noter dans l'inventory et passer. C'est une info en soi.

### Phase 2 — Sélection & analyse
Scorer chaque annonce collectée (1-5) sur : longévité, scaling (variantes), transposabilité
à l'ICP {{COMPANY}} (croiser `icp-bible.md`). Pour les 3-5 meilleures, extraire la **structure** :
- Hook (mécanique de tension utilisée)
- Angle (pain/désir adressé)
- Preuve (chiffres, social proof, certif)
- CTA
- Structure visuelle (composition, hiérarchie texte/image, usage des couleurs — pas les couleurs elles-mêmes)

Livrable : `ads/meta/meta-remix/veille/YYYY-MM-DD/analyse.md`.

## Hiérarchie visuelle — prioriser, ne pas tout mettre au même niveau

Une créa = **UNE hiérarchie claire**. Ne jamais afficher tous les éléments avec la même importance : le scroll s'arrête sur un message dominant, pas sur un mur d'infos.

**Niveau 1 — La tagline (hook).** L'élément ULTRA important, le seul qui accroche. Il domine visuellement (gros, contraste, surligneur dessiné sur la punchline). Tout le reste lui est subordonné.

**Niveau 2 — Éléments de réassurance (secondaires, plus petits, regroupés).** Jamais en concurrence avec le hook. Deux familles :
- **Preuve sociale** : vos labels officiels (certification, agrément, partenariat) et votre plateforme d'avis. Affichez le nombre de **clients**, pas le nombre d'avis.
- **Infos produit** : logos d'outils et étiquettes courtes (constituez votre pool à partir de `brain/offre.md` : format, durée, garantie, niveau d'accompagnement). Sur les créations centrées message : **pas d'étiquettes**, la preuve officielle suffit. Voir design-rules.
- **Trustpilot (coin haut-droit)** : logo officiel + étoiles + le nombre de **clients** et non le nombre d'avis, qui est plus faible et moins parlant.

**Détails chiffrés (tailles, positions, golden, 4:5) → [references/design-rules.md](references/design-rules.md), source de vérité.**

**Faire des choix — on ne peut pas tout mettre.**
- Max **2 logos** de réassurance ensemble dans un bandeau (3 = trop, ça prend trop de place et ça noie). Le 3e (souvent Trustpilot) se sort ailleurs, ex. coin haut-droit.
- Tags : en sélectionner **quelques-uns pertinents**, pas une liste exhaustive ; mixer thématiques + format/durée.
- Si un élément n'aide pas la conversion de CE visuel précis → le couper.

**Lisibilité mobile (impératif).** Cible = écran iPhone 6-7". Hooks et tags généreux, jamais de micro-texte. Dans le doute, plus gros.

**Zone morte.** Les 20 % du bas ne sont pas visibles (UI Meta/feed) → aucun élément important n'y est placé.

> **Règles design figées (tailles, positions, couleurs, hiérarchie) → [references/design-rules.md](references/design-rules.md).**
> Pipeline de production text-driven (hook + tags + bandeaux, HTML→PNG via Chrome headless, formats 4:5 + 9:16) : un moteur de rendu HTML vers PNG (Chrome sans interface) et un dossier d'assets contenant vos logos officiels. Règles logos officiels → votre mémoire de conformité des logos.

### Phase 3 — Remix {{COMPANY}}
Pour chaque structure retenue, écrire un brief :
- **Copy** : hook réécrit (règles hooks ci-dessus), texte court + long, titre ≤ 40c,
  description ≤ 30c, CTA. Uniquement les claims autorisés de `ads/meta/meta-ia-marketing-copy.md`.
- **Visuel** : prompt de génération décrivant la composition empruntée, exécutée en palette
  {{COMPANY}}. Texte sur image : minimal (un hook court max), centré dans la safe zone
  (marges 14 % en 9:16 pour l'UI stories).

Livrable : `ads/meta/meta-remix/briefs/YYYY-MM-DD-<concept>.md` + manifest JSON pour la génération.

### Phase 4 — Génération des images
```bash
python3 skills/meta-ad-remix/scripts/generate_ad_images.py <manifest.json>
```
Le script lit `OPENAI_API_KEY` dans le `.env` projet, génère via gpt-image-2, puis produit
les formats Meta exacts en PNG : `1080x1080` (feed carré), `1080x1350` (feed 4:5),
`1080x1920` (stories/reels). Sortie : `ads/meta/meta-remix/output/YYYY-MM-DD/<concept>/`.

Format du manifest :
```json
{
  "output_dir": "ads/meta/meta-remix/output/2026-06-11/concept-juniors",
  "images": [
    {"name": "juniors-v1", "prompt": "...", "formats": ["square", "portrait", "story"]}
  ]
}
```

### Phase 5 — Validation & push
1. Présenter à {{OWNER}} : tableau concept → annonce source (concurrent, screenshot) → copy → visuels.
2. Attendre validation explicite copy + visuels (memory `feedback_ad_copy_validation`).
3. Push **manuel** dans Meta Ads Manager (v1 — pas d'API Meta branchée).
4. Logger les apprentissages dans `memory/feedback_meta_ad_hooks.md` si {{OWNER}} corrige.

## Anti-patterns

- Réutiliser un asset concurrent (photo, visuel, logo) même « un peu modifié » → ligne rouge.
- Inventer un chiffre produit → vérifier `brain/offre.md`.
- Prix dans l'annonce → interdit (test premium, prix révélé en R1).
- Hook observation + réassurance → réécrire avec tension concrète.
- Pousser sur Meta sans validation explicite de {{OWNER}}.
