---
name: growth-experiment
description: "Gestion des expériences growth de votre entreprise, de la fiche projet au readout. Deux modes. FICHE : ouvrir une expérience avec une hypothèse falsifiable, un levier, une métrique primaire en deals ou CA (jamais en leads), un seuil de succès, une fenêtre de lecture, un budget, un owner et une date de gate ; sans ces champs, le test ne se lance pas. READOUT : clôturer avec la donnée réelle (HubSpot, régies, Ahrefs), verdict vs seuil, proposition garder / couper / scaler, learning archivé en mémoire. Tient le registre des expériences en cours et relance celles dont la gate est passée. Use when user says 'fiche projet', 'fiche d'expérience', 'document d'expérience', 'cadre le test', 'lance une expérience', 'ouvre une expérience', 'readout', 'clôture le test', 'résultat de l'expérience', 'on garde ou on coupe', 'où en sont les tests', '/growth-experiment'. Pour le diagnostic causal d'un canal, voir marketing-analysis ; pour dater les actions, voir roadmap ; pour cadrer un lancement avant le test, voir gtm-strategy."
metadata:
  version: 0.1.0
  references:
    - references/fiche-template.md  # Le gabarit de fiche, les champs obligatoires, la convention de rangement
---

## Calibration (à faire avant le premier usage)

Ce skill porte une méthode. Il lui manque votre contexte. Renseignez :

| À remplir | Où |
|---|---|
| Votre unité de mesure (lead, client, chiffre d'affaires) | `brain/channels.md` |
| Votre effectif minimum pour trancher un test | à calculer, voir `skills/ab-test-setup` |

Tant que ces cases sont vides, le résultat sera correct dans la forme et creux sur le fond.

# Growth Experiment, du pari à la décision

Tu tiens le cycle de vie des expériences growth de {{COMPANY}} : ouvrir proprement, lire à date fixe, décider, capitaliser. Un test sans fiche est un pari ; un test sans readout est un test perdu deux fois.

## Avant de démarrer (obligatoire)

Charger le contexte de l'entreprise, un subagent ne le voit pas seul :
1. `AGENTS.md` et `brain/offre.md` (jamais d'affirmation produit sans vérification).
2. Le registre : lister les fiches existantes dans `channels/*/experiences/` et `strategy/experiences/` avant d'en créer une, pour ne pas dupliquer un test déjà ouvert ou déjà tranché.
3. Mémoires (index : `memory/MEMORY.md`) : `feedback_mesurer_en_deals_pas_en_leads`, `feedback_pas_de_verdict_sur_une_limite`, `feedback_verifier_la_date_avant_toute_analyse`.

## Mode FICHE (ouvrir)

1. **Écrire l'hypothèse en une phrase falsifiable** : « si on fait X sur [segment], alors [métrique] atteint [seuil] en [fenêtre] ». Si on ne peut pas la formuler, le test n'est pas prêt.
2. **Remplir le gabarit** (`references/fiche-template.md`). Champs bloquants : métrique primaire en deals ou CA, seuil de succès chiffré, fenêtre de lecture, budget, owner, date de gate, décision prévue à la gate (garder / couper / scaler, avec le critère).
3. **Ranger la fiche** : `channels/<cellule>/experiences/AAAA-MM-slug.md` pour un test mono-canal, `strategy/experiences/` pour un test transverse.
4. **Inscrire la gate** : proposer la ligne correspondante dans `ROADMAP.md` (via le skill `roadmap`, {{OWNER}} arbitre).

Une expérience dont la métrique primaire est un volume de leads est refusée : reformuler en deals ou CA (mémoire `feedback_mesurer_en_deals_pas_en_leads`). Le CPL peut vivre en métrique secondaire, jamais en juge.

## Mode READOUT (clôturer)

1. **Relire la fiche** : hypothèse, seuil, fenêtre. La lecture se fait à la date de gate, pas quand le résultat a l'air bon.
2. **Puller la donnée réelle** : deals HubSpot (`skills/sales-weekly/lib/hubspot.py`), spend régies (`channels/paid/google-ads/google_ads.py`, `ads/meta/meta_ads.py`), SEO (Ahrefs MCP). Fenêtre ancrée sur la donnée, cohortes suivies jusqu'à leur issue ; le dire si la cohorte est encore immature.
3. **Verdict vs seuil** : atteint / manqué / illisible. Sur un effectif < 5, citer les deals un par un, pas des pourcentages. Si le tracking ne permet pas de lire, le verdict est « illisible » et l'action est de réparer la mesure, pas de conclure.
4. **Si le pourquoi n'est pas évident**, appeler `marketing-analysis` pour la décomposition causale. Pour un A/B avec assez de volume, les outils statistiques de `growth-engine` (fork, non calibré) peuvent servir : les utiliser en flaggant leur origine.
5. **Proposer la décision** : garder / couper / scaler, avec le critère de la fiche. {{OWNER}} arbitre.
6. **Capitaliser** : compléter la fiche (résultat, décision, learning en 3 lignes) ; si le learning dépasse l'expérience (un piège de mesure, un fait de marché), l'écrire en mémoire projet ; passer la ligne roadmap en livré.

## Registre

Sur « où en sont les tests » : lister toutes les fiches avec statut (en cours / gate dépassée / clôturée), owner, date de gate. Toute gate dépassée sans readout est signalée en premier : c'est la dette la plus chère du système.

## Règles absolues

- Pas de fiche sans seuil et sans date : c'est ce qui distingue une expérience d'une intention.
- Pas de readout avant la fenêtre, sauf signal d'arrêt d'urgence défini dans la fiche.
- La décision appartient à {{OWNER}} ; le skill propose et documente.
- Un test coupé avec un learning propre est un succès du système, pas un échec.

## Skills et mémoires liés

- `gtm-strategy` : cadre le lancement en amont ; son go devient une fiche ici.
- `marketing-strategy` : le bridge du plan liste les expériences majeures ; leurs readouts nourrissent le plan suivant.
- `roadmap` : porte les dates de gate ; `marketing-weekly` rappelle les gates de la semaine.
- `marketing-analysis` : la décomposition causale quand le verdict demande un pourquoi.
- `growth-engine` (fork, non calibré) : outillage statistique A/B, à flagger si utilisé.
- Mémoires : `feedback_mesurer_en_deals_pas_en_leads`, `feedback_pas_de_verdict_sur_une_limite`, `feedback_verifier_la_date_avant_toute_analyse`, `project_economie_canaux`.
