# Objectifs commerciaux hebdomadaires

> **À remplir.** Les valeurs ci-dessous sont des exemples chiffrés pour montrer la forme attendue.
> Remplacez-les par les vôtres, et reportez-les aussi dans `lib/targets.config.json`.
> Un objectif qui ne vient pas de votre prévisionnel est un objectif inventé.


Targets en vigueur sur le pipeline **votre pipeline principal** (`<PIPELINE_ID>`).

**Édite directement ce fichier quand un objectif bouge.** Le skill `sales-weekly` le lit à chaque run, donc la modification est appliquée immédiatement.

**Dernière mise à jour** : 2026-05-21
**Validé par** : {{OWNER}}

---

## Les 4 targets hebdo

| # | Métrique | Target | Mesure (HubSpot) |
|---|---|---|---|
| 1 | **CA closed-won** | **{{OBJECTIF_HEBDO}} € / semaine** | Somme des `amount` des deals passés en stage *Deal Gagné* (`<ID_GAGNE>`) sur la semaine (filtre `closedate`) |
| 2 | **Pipeline pondéré créé** | **{{OBJECTIF_HEBDO}} € / semaine** | **formule interne V0.9.2** : `N deals créés × panier moyen × taux de conversion global` (les deux valeurs viennent de VOTRE historique, pas d'un benchmark). Le calcul vous donne le nombre de deals à créer par semaine pour tenir l'objectif. La version HubSpot (`sum hs_projected_amount_in_home_currency`) est conservée en référence sous `weighted_eur_hubspot`. |
| 3 | **Activité RDV planifié** | **≥ {{N}} appels / lead / semaine** | Pour chaque deal présent en stage *RDV planifié* (`STAGE["GO_TO_R1"]`) sur la semaine, ≥ 4 calls loggés. Indicateur affiché = **% leads validant la cible** (plus actionnable que la moyenne). |
| 4 | **Hygiène tâches** | **100% deals open avec next activity** | Tous les deals open du pipeline (= hors *Deal Gagné*, *Deal Perdu*, *Churn*) doivent avoir `notes_next_activity_date` non vide. |

## Funnel — taux de conversion par étape (V0.5)

Cohorte = leads créés dans la semaine (filtre `createdate`). Mesure du parcours **depuis la création** vers chaque étape clé.

### Deux mesures distinctes côté contact

| Étape | Métrique | Target | Définition | Lecture |
|---|---|---|---|---|
| **Call tried** | % leads avec ≥1 call tenté | **≥ 95%** | Au moins 1 call associé au deal OU au contact associé, peu importe la durée (y compris durée=0 manual log). | **Mesure d'effort sales.** Doit être très haut rapidement (J+2 à J+7). Si <95% sur des leads >7j → problème d'activité. |
| **Call quality** | % leads avec ≥1 call ≥120s | **≥ 70%** | Au moins 1 call de durée ≥ **120 secondes** (vrai échange). | **Mesure de cohorte rétrospective.** À lire après J+14 (un lead de 2 jours peut légitimement ne pas avoir eu encore un vrai échange). À segmenter par âge de cohorte. |

**Pourquoi cette split ?** Faire 70% de "vrais calls ≥2min" sur des leads de 2 jours n'a pas de sens — c'est mathématiquement impossible. Le call_tried mesure si on a essayé, le call_quality mesure si on a réussi. Les deux sont nécessaires.

### Reach par étape funnel

| Étape | Métrique | Target | Définition |
|---|---|---|---|
| **R2 reach** | % leads arrivés en R2 | **35-40%** | Lead avec `hs_v2_date_entered_<ID_R2>` non vide (soit actuellement en R2, soit passé par R2 même si avancé ou perdu depuis) |
| **Decision reach** | % leads arrivés en Decision | **~25%** | Lead avec `hs_v2_date_entered_<ID_DECISION>` non vide |

⚠️ **Important** : ces 2 targets sont des % sur la **cohorte totale de leads créés**, pas sur le step précédent. Si R2 = 35% et Call quality = 70%, ça veut dire que **35% du total des leads** ont atteint R2 (= ~50% des "vrais contactés" ont atteint R2).

⚠️ **À segmenter par source** : ces taux doivent être lus **par canal** (Inbound, Maformation, Paid, Nouvelles plateformes, etc.) — les benchmarks globaux ne sont pas pertinents quand le mix sources change semaine après semaine.

### Note technique — sources de calls (V0.5)

Les calls sont récupérés via **union de deux associations HubSpot** :
1. **Direct** : `deal → calls` (le sales loggue le call sur la fiche deal)
2. **Indirect** : `deal → contacts → calls` (le sales loggue le call sur la fiche contact, sans association explicite au deal)

Cette union permet de ne pas sous-estimer l'activité quand les pratiques de logging varient.

## Pipeline velocity (V0.4)

**Formule** : `(Nb opportunités × Deal size moyen × Win rate) / Cycle length (jours)` → €/jour de revenu prévisible.

Pas de target absolu ; à lire **en tendance** (hausse/baisse semaine après semaine). Calculé global + par source.

## Pipeline coverage (V0.4)

**Formule simplifiée {{COMPANY}}** : `Pipeline pondéré open total / Target mensuel (108 000 € = 25k × 4.33)`.

⚠️ **Limite acceptée** : on ne filtre PAS sur `closedate estimé` car ce champ n'est pas rempli par l'équipe sales. Le calcul est donc une **borne supérieure** (inclut tous les deals open, même ceux qui ne closeront pas dans le mois). Donne une tendance utile, pas un forecast strict.

Benchmark indicatif (à recalibrer après 8-12 semaines de données {{COMPANY}}) : ratio cible ≈ 3-4×.

---

## Seuils status

| Status | Seuil | Sens |
|---|---|---|
| 🟢 Vert | ≥ 96% du target | On délivre |
| 🟡 Jaune | 75 - 95% | À surveiller |
| 🔴 Rouge | < 75% | À expliquer dans l'analyse |

## Les 5 KPIs clés du rapport hebdo

Métriques canoniques affichées en tête de chaque rapport, avec status couleur.

| # | KPI | Target hebdo | Logique status |
|---|---|---|---|
| 1 | CA closed-won | 25 000 € | 🟢 ≥100% / 🟡 70-99% / 🔴 <70% |
| 2 | **Nouveau Pipeline (Marketing)** = nb deals créés × (panier moyen × taux de conversion global) | 25 000 € | 🟢 ≥100% / 🟡 70-99% / 🔴 <70% |
| 3 | **Qualifications pondérées** (V0.12) = RDV 2 seul × (33 % du panier) + Décision × (50 % du panier) (dédupliqué par deal_id, Decision wins) | **25 000 €** weighted/sem | 🟢 ≥96% / 🟡 75-95% / 🔴 <75% |
| 4 | **Panier Moyen** (+ bundle %) | **2 000 €** (fixe) | 🟢 ≥96% (≥1 920€) / 🟡 75-95% (1 500-1 919€) / 🔴 <75% (<1 500€) |
| 5 | **% deals open SANS call dans la semaine** | ≤20% | 🟢 ≤20% / 🟡 20-50% / 🔴 >50% |

**KPI 5 V0.9.1** : indicateur de **couverture sales du pipeline ouvert**. Pour chaque deal open du pipeline (~900 deals chez {{COMPANY}}), on regarde s'il a reçu **au moins 1 call pendant la semaine analysée**. Le % sans aucun call = % du pipeline "ignoré" cette semaine. Inclus tous les stages (Prospection à Paiement). Détail par stage disponible en Layer 2.

**Note sur call_tried (descendu en Layer 3)** : `call_tried` = % de la cohorte créée DANS la semaine ayant reçu ≥1 call depuis création. C'est une métrique cohorte (effort sur leads frais). KPI 5 V0.9.1 est complémentaire : couverture du pipeline EXISTANT pendant la semaine.

**Note sur reach_rate (anciennement call_quality)** : reste mesurable dans Layer 3 mais pas en KPI principal. Définition : % cohorte ayant eu ≥1 call ≥120s. Utile en drill quand on cherche pourquoi un objectif n'est pas atteint.

**KPI 3 — V0.12 — pondération par probabilité de signature** :
- **R2-only** (deal entré en R2 dans la fenêtre, sans atteindre Decision) → pondéré à **33% × 1 800€ = 594€**
- **Decision** (deal entré en Decision dans la fenêtre, qu'il soit passé par R2 ou pas) → pondéré à **50% × 1 800€ = 900€**
- **Dédup** : un deal qui passe R2 ET Decision dans la même semaine est compté **1 seule fois en Decision** (le stage le plus avancé "wins").
- **Target weighted = 25 000€/sem** (cohérent avec target CA hebdo).
- **Math du target** : si l'équipe génère ~25-30 deals qualif/sem avec un mix R2/Decision similaire à l'historique, le pondéré atteint ~20-25k€.

**KPI 4 — détection bundle (V0.10.1)** : un deal est compté bundle si **soit** son champ `product` HubSpot contient ≥2 produits, **soit** son amount > **{{SEUIL_PANIER}}** (capture les "stealth bundles" où l'équipe a mal rempli `product` mais le prix révèle qu'il s'agit d'un bundle). Le seuil se choisit juste au-dessus du prix de votre offre unitaire la plus chère.

**KPI 4 : objectif de panier moyen fixe.** À poser comme objectif stratégique quand vous voulez pousser la vente groupée et compenser une baisse du panier. Baseline 3m reste calculée en parallèle (information complémentaire pour détecter les ruptures structurelles), mais n'est pas le target.

## Couleur calls per lead (Layer 2 détail)

Seuils absolus simples (Option A) :

| Buckets | Couleur | Sens |
|---|---|---|
| 0 calls | 🔴 | Aucun effort sales |
| 1-2 calls | 🟡 | Effort minimum |
| 3-5 calls | 🟢 | Effort standard |
| 6+ calls | 🟢🟢🟢 | Effort fort |

Appliqué globalement (toutes sources), pas de différenciation par canal en V0.9.1.

---

## Cadence

- **Rapport produit chaque lundi matin** sur la **semaine écoulée**
- Fenêtre = **lundi 00:00 → dimanche 23:59 Europe/Paris**
- Si lancé en milieu de semaine sans précision : défaut = semaine précédente complète
- Si précision explicite (ex. "S20") : utiliser la fenêtre demandée

---

## Hors scope V1 (à ajouter plus tard)

- **Split target par source** (ex. "Inbound 8k€/sem, Paid 5k€/sem...") → à fixer après 4-6 semaines de baseline.
- **Target conversion par étape** (taux R1→R2, R2→Gagné) → à fixer après baseline observée.
- **Target par owner / par AE** → à ajouter quand l'équipe sales est stable.
- **Target par formation vendue** → nécessite mapping deal → catalogue.

---

## Historique des changements

| Date | Changement | Validé par |
|---|---|---|
