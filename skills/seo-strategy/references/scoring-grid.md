# Scoring grid — seo-strategy references

Grille de scoring pour prioriser un backlog SEO. Chargée à la demande par `seo-strategy` Phase 6 "Score, Prioritize & Build the Backlog".

## Scoring de base : Product × Demand × Intent × Effort (max 81)

| Axe | 3 | 2 | 1 |
|---|---|---|---|
| **Product** | Pont direct : le keyword EST le produit | Pont outil : keyword = outil/compétence enseigné | Pont audience : keyword attire le bon profil mais lien indirect |
| **Demand** | >500/mo ET KD ≤10 | 100-500/mo OU KD 11-25 | <100/mo OU KD >25 |
| **Intent** | BOFU : formation, comparatif formations, prix, avis, financement public | MOFU : guide outil, tuto, comparatif outils, méthode | TOFU : définition, c'est quoi, fiche métier |
| **Effort** | Facile (comparatif, "gratuit ou payant", définition, listicle) | Moyen (guide pratique avec exemples, fiche métier enrichie) | Difficile (tutoriel technique pas-à-pas, guide outil avancé) |

## Comment évaluer l'Effort

- **3 (facile)** — structure claire et répétable, pas de screenshots, rédaction < 2h, l'IA fait 80 % du travail. Formats : comparatif A vs B, "X gratuit ou payant", définition, listicle "top N outils".
- **2 (moyen)** — recherche + exemples concrets, connaissance du sujet. L'IA fait 50 %, un humain enrichit. Formats : guide pratique, prompts par catégorie, fiche métier avec data.
- **1 (difficile)** — nécessite d'avoir utilisé l'outil, screenshots, expertise technique, tests réels. L'IA fait 30 %, praticien rédige ou valide. Formats : tutoriel technique, guide d'implémentation, deploy entreprise.

## Ajustements (+1 à +3 bonus)

- **First mover** (+3) : SERP vide = aucune concurrence, premier arrivé prend la position
- **Refresh** (+2) : article existant à mettre à jour = rapide et impact immédiat
- **Cluster** (+1) : complète un cluster existant (hub & spoke)
- **Cross-sell** (+1) : peut promouvoir plusieurs formations
- **Trending fort** (+3) : volume en hausse >100 % sur 12 mois (outils IA émergents type "Claude Skills", "agent IA", "NotebookLM")
- **Trending modéré** (+1) : volume en hausse 30-100 % sur 12 mois

## Pénalités (-1 à -5)

- **DR mur** (-3) : top 5 SERP dominé par des DR80+ sans faille (Wikipedia, Google, IBM)
- **Piège intent** (-2) : SERP montre un intent différent de ce qu'on croit (ex: "formation automatisation" = industriel)
- **Saturé** (-1) : 5+ concurrents directs ont déjà un article similaire et bien positionné
- **Declining** (-2) : peak >18 mois ET baisse 30-50 % sur 24 mois (terme qui s'essouffle)
- **Obsolète** (-5, souvent rejet direct) : peak >3 ans ET baisse >50 %. Relique de l'ère pré-IA (2015-2021) sans reformulation IA possible → on ne le cible pas.

## Règle mix longueur — OBLIGATOIRE

Un backlog 80 % long-form = velocity bloquée. Lion fait 4 705 visites/mo avec UN seul article court de 800 mots.

| Longueur | Formats concernés | Effort | Cible mix |
|---|---|---|---|
| 🟢 **Court** (800-1 200 mots) | Comparatif "A vs B", "gratuit ou payant", "c'est quoi" court, FAQ autonome, mini-listicle (3-5 items) | 2-3h | **30-40 %** |
| 🟡 **Moyen** (1 200-2 000 mots) | Listicle (7-10 items), fiche métier, méthode, tutoriel ciblé, "10 cas d'usage" | 4-5h | **30-40 %** |
| 🟣 **Long** (2 000+ mots) | Guide complet, pillar JTBD, tutoriel pas-à-pas complet | 6-8h | **20-30 %** |

Si >40 % de long-form → calendrier sous-optimal. Remplacer des long-form à score moyen par des short-form à fort volume et KD faible. Dans chaque cluster JTBD : 1 pillar long + 3-4 moyens + 3-4 courts = ratio équilibré.

## Règle mix formats — OBLIGATOIRE

Avant de finaliser le backlog, vérifier la diversité des formats. Un backlog où un seul type représente >50 % est **déséquilibré** et doit être corrigé.

Viser :
- Comparatifs outils : **max 30-40 %** du backlog
- Guides pratiques / features : 20-30 %
- Méthodes et contenus ICP-first : 20-30 %
- Pillars / définitions / TOFU : 10-20 %
- Refreshes : selon existant

Si trop homogène → remplacer des articles à faible score par des articles d'un type sous-représenté, **même si leur score est légèrement inférieur**. La diversité > le score unitaire.
