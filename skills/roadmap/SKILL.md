---
name: roadmap
description: Gestion de la roadmap marketing (ROADMAP.md à la racine du repo). Afficher l'état, ajouter ou reprioriser des projets, passer le fait en Livré, préparer les sections « Lancé cette semaine » et « Semaine prochaine » du récap hebdo. Use when user says "roadmap", "ajoute à la roadmap", "qu'est-ce qu'on lance la semaine prochaine", "passe X en livré", "où en est la roadmap", "/roadmap".
metadata:
  version: 0.1.0
---

## Calibration (à faire avant le premier usage)

Ce skill porte une méthode. Il lui manque votre contexte. Renseignez :

| À remplir | Où |
|---|---|
| Le fichier ROADMAP.md à la racine de votre repo | à créer au premier usage |
| Vos statuts et vos échéances | à définir dans ce même fichier |

Tant que ces cases sont vides, le résultat sera correct dans la forme et creux sur le fond.

# Roadmap, la gestion du plan marketing hebdo

Fichier unique : `ROADMAP.md` à la racine. Trois sections : **Semaine en cours**, **Ensuite**, **Livré** (par semaine ISO).

## Opérations

- **Afficher** : lire le fichier, résumer l'état (fait / en cours / à venir) en 5 lignes max.
- **Ajouter** : une ligne par projet, verbe d'action, pas de sous-détail (le détail vit dans `channels/`). Les propositions de l'agent sont préfixées `(proposé)` tant que {{OWNER}} n'a pas arbitré.
- **Livrer** : déplacer la ligne cochée vers `## Livré / ### S[##] (dates)`, en gardant la date si connue.
- **Rituel du lundi** (appelé par `marketing-weekly`) :
  1. Le fait de la semaine écoulée descend en Livré (avec les sessions Claude Code de la semaine comme source de rappel : `mcp ccd_session_mgmt list_sessions`).
  2. « Ensuite » remonte en « Semaine en cours » selon l'arbitrage de {{OWNER}}.
  3. Les deux listes partent dans le récap (« Lancé cette semaine » = Livré S écoulée, « Semaine prochaine » = Semaine en cours).

## Règles

- {{OWNER}} arbitre, l'agent propose. Ne jamais supprimer une ligne sans son accord, ne jamais réécrire l'historique Livré.
- Une ligne = un projet nommable dans un email d'équipe. Si ça ne se dit pas en une ligne, c'est du détail de cellule.
- Aucun cadratin.
