---
name: gtm-strategy
description: "Positionnement produit et go-to-market niveau direction pour votre entreprise. Sert à évaluer et cadrer un lancement (nouvelle offre, verticale métier, B2B, nouveau produit) avant d'y mettre du budget, et à armer le challenge stratégique. Couvre : énoncé de positionnement (April Dunford, FOR/WHO/THE/THAT/UNLIKE), définition et scoring de l'ICP, battlecards concurrents, choix de motion go-to-market (inbound/SEO, paid, marketplace Maformation, outbound B2B, webinaire), et sizing d'opportunité via la demande réelle (Ahrefs, données publiques du marché). Use when user says 'positionnement', 'comment on se positionne', 'go-to-market', 'GTM', 'lancer une offre', 'lancer une verticale', 'évaluer un lancement', 'quelle cible', 'ICP', 'battlecard', 'contre tel concurrent', 'quelle motion', 'est-ce que ce marché existe', '/gtm-strategy'. Pour la checklist tactique d'annonce, voir launch-strategy ; pour le doc de direction, voir marketing-strategy ; pour cadrer le test qui suit le go, voir growth-experiment."
metadata:
  version: 0.2.0
  references:
    - references/frameworks.md  # Positionnement Dunford, scoring ICP, battlecard, grille motion, sizing d'opportunité
---

## Calibration (à faire avant le premier usage)

Ce skill porte une méthode. Il lui manque votre contexte. Renseignez :

| À remplir | Où |
|---|---|
| Vos sources de demande réelle | `docs/DONNEES.md` |
| Vos contraintes de lancement | `brain/contraintes-marche.md` |
| Votre grille de qualification de segment | `references/frameworks.md` |

Tant que ces cases sont vides, le résultat sera correct dans la forme et creux sur le fond.

# GTM Strategy, positionner et cadrer un lancement chez {{COMPANY}}

Tu aides à répondre à une question de direction : **cette offre, pour qui, contre qui, par quel canal, et le marché la veut-il ?** Avant qu'un euro parte.

## Avant de démarrer (obligatoire)

Charger le contexte de l'entreprise, un subagent ne le voit pas seul :
1. `AGENTS.md`, puis `brain/icp.md`, `brain/personas.md`, `brain/messaging.md`, `brain/offre.md`, `brain/voice-tone.md`.
2. Le dossier `strategy/` à la racine du repo : les directions et le sizing déjà faits (verticales métier, demande B2B, plafonds par voie). Ne pas refaire une analyse qui existe ; la compléter ou la mettre à jour.
3. Mémoires (index : `memory/MEMORY.md`) : `project_icp_corpus`, `project_donnees_marche`, `project_funnel_partenaire`, `feedback_politique_prix`.

## Latent vs déterministe

Le positionnement est un jugement ; la demande et la concurrence sont des données. Avant d'affirmer qu'un marché existe :
- Volume et intention de recherche : Ahrefs MCP (keywords explorer, GSC), avec la trajectoire 24 mois (mémoire `feedback_keyword_momentum`).
- Entrées financement public réelles par certif, OF et mois : données publiques du marché (mémoire `project_donnees_marche`). C'est le juge de paix : une verticale à 0 entrée financement public ne se lance pas sur la foi d'une intuition.
- Ce qui convertit déjà par canal : mémoires `project_economie_canaux`, `project_funnel_partenaire`.
- Concurrents : `channels/seo/competitors.md`, Ahrefs (SERP, top pages), Brand Radar.

## Les cinq questions d'un lancement

Dans l'ordre. On ne passe à la suivante que si la précédente tient.

1. **Le marché existe-t-il ?** Sizing par la demande réelle (recherche + achats financés), pas par l'envie. Verdict : marché prouvé / à tester petit / inexistant. Voir `references/frameworks.md`.
2. **Pour qui précisément ?** ICP défini et scoré A/B/C/D (grille dans la référence). Croiser avec les personas {{COMPANY}} existants ; ne pas inventer un persona qui contredit l'`brain/icp.md`.
3. **Positionné comment ?** Énoncé Dunford FOR/WHO/THE/THAT/UNLIKE, dans la voix de marque (`voice-tone` ; vouvoiement pour la copy pub, mémoire `feedback_ad_copy_vouvoiement`).
4. **Contre qui ?** Battlecard : le concurrent réel sur cette requête, sa force, sa faille, notre angle. Concurrents en nofollow par défaut (mémoire `feedback_liens_sortants_nofollow`).
5. **Par quelle motion ?** Choisir le canal d'entrée selon ce qui convertit chez {{COMPANY}}, pas selon la mode. Grille motion dans la référence. Un lancement se teste sur la motion la moins chère à lire avant de scaler.

## Sortie

- **Note de cadrage de lancement** : les cinq réponses, un verdict go / test petit / no-go, et si go : la motion de départ, la métrique de succès, le seuil de décision.
- Si go, enchaîner : `growth-experiment` ouvre la fiche du test, `marketing-strategy` intègre la ligne au bridge, `roadmap` la date.
- Jamais de go sans métrique de succès et sans date de gate. Un lancement qu'on ne peut pas lire à 3 mois n'est pas un lancement, c'est un pari.

## Règles absolues

- Une verticale ou une offre à 0 demande prouvée ne se lance pas, quelle que soit la conviction (référence : IA et Finance, 0 entrée financement public, écartée en juillet 2026).
- Pas de nouveau persona qui contredit l'ICP bible : on étend, on ne réinvente pas.
- Vérifier `brain/offre.md` avant toute affirmation produit (prix, durée, certif).
- Le positionnement se rédige dans la voix de marque, pas en jargon PMM anglo-saxon.

## Skills et mémoires liés

- `marketing-strategy` : consomme les notes de cadrage pour arbitrer et écrire le plan.
- `growth-experiment` : transforme un go en fiche d'expérience datée et mesurable.
- `launch-strategy` (fork, non calibré) : la checklist tactique d'annonce, une fois le go pris. Croiser `agents/` avant usage.
- `competitor-alternatives` (fork, non calibré) : produire les pages vs concurrents une fois la battlecard faite.
- `marketing-analysis` : lire les résultats du lancement après coup.
- Mémoires : `project_icp_corpus`, `project_donnees_marche`, `project_funnel_partenaire`, `project_strategie`, `feedback_politique_prix`, `reference_psychologie_positions_ia`.
