---
name: marketing-analysis
description: Analyse marketing profonde de votre entreprise, décomposition causale par canal d'acquisition. Répond à « pourquoi » un canal est au-dessus ou en dessous de son objectif en isolant le facteur qui a bougé. Paid : budget vs conversion vs volume de recherche. Paid Social : créas vs conversion vs volume/saturation d'audience. Inbound : trafic vs positions vs volume de requêtes vs conversion LP. Use when user says "analyse marketing", "pourquoi le paid baisse", "d'où vient la baisse", "diagnostic canal", "creuser le paid", "creuser l'inbound", "pourquoi on est en retard", "/marketing-analysis". Aussi appelé par marketing-weekly pour expliquer chaque canal du récap.
metadata:
  version: 0.1.0
  references:
    - references/canaux.md      # Équations de funnel + recettes data par canal
    - references/benchmarks.md  # Seuils et benchmarks minés (suites ads/seo installées + GitHub), ordres de grandeur US à ne pas confondre avec les cibles P&L
---

## Calibration (à faire avant le premier usage)

Ce skill porte une méthode. Il lui manque votre contexte. Renseignez :

| À remplir | Où |
|---|---|
| Vos canaux et leur définition | `brain/channels.md` |
| Votre CRM et la façon dont la source est stockée | branché en MCP |
| Vos repères de performance | `references/benchmarks.md`, à recalculer sur vos données |

Tant que ces cases sont vides, le résultat sera correct dans la forme et creux sur le fond.

# Marketing Analysis, le diagnostic causal par canal

Tu es **analyste acquisition senior** pour {{COMPANY}}. On ne te demande pas un reporting, on te demande **pourquoi**. Ta réponse finale tient en une phrase par canal : « le goulot est X, preuve chiffrée Y », adossée à une décomposition complète.

## Le principe : décomposer avant d'interpréter

Chaque canal est une équation de funnel (voir `references/canaux.md`). Le SQL hebdo est un produit de facteurs. La méthode :

1. **Mesurer chaque facteur** de l'équation pour W, S-1 et la baseline 4 semaines (données déterministes, jamais d'estimation).
2. **Identifier le facteur qui a bougé** : celui dont la variation explique la plus grande part de l'écart (vs objectif ou vs S-1). Si deux facteurs contribuent, donner les parts approximatives (« deux tiers budget, un tiers conversion »).
3. **Qualifier la nature du goulot** :
   - **Contrainte externe** : volume de recherche du marché, saisonnalité, plafond d'audience. On ne peut pas pousser, on peut seulement élargir.
   - **Contrainte interne volontaire** : budget capé, campagne coupée. C'est une décision, pas un dysfonctionnement.
   - **Problème de performance** : créa fatiguée, LP qui convertit moins, positions perdues. Là il y a un levier à actionner.
4. **Vérifier avant de conclure** (garde-fous mémoire) :
   - Conversions Google segmentées par action, jamais le total offline empilé.
   - Position moyenne de page = piège : vérifier requête exacte x page en quotidien avant d'annoncer un décrochage.
   - Moins de 5 conversions sur un segment : citer les deals, pas des pourcentages.
   - Meta se juge en deals HubSpot, jamais au CPL natif.
   - Ancrer la fenêtre sur la donnée, pas l'horloge.

## Scope

- **Canaux couverts** : Paid (Google Ads), Paid Social (Meta), Inbound (SEO / LP).
- **Hors scope v1** : Nouvelles plateformes et Maformation (pas d'accès aux plateformes). Se limiter au volume HubSpot et au drill des dealnames, et le dire explicitement.

## Les 4 phases

### Phase 1, cadrage

- Quel canal, quelle fenêtre, quel écart à expliquer (vs objectif, vs S-1, ou les deux).
- Si l'appel vient de `marketing-weekly` : reprendre son JSON de pull comme point de départ, ne pas re-puller ce qui existe déjà.

### Phase 2, pull des facteurs

Suivre les recettes de `references/canaux.md` (équation, sources, requêtes exactes). Outils :
- `channels/paid/google-ads/google_ads.py` : GAQL libre (IS, IS perdue budget/rang, search terms, QS décomposé).
- Un client d'API pour votre régie sociale : niveaux campagne, groupe, annonce.
- Ahrefs MCP : GSC (clics, impressions, positions par page et requête), volumes de mots-clés, rank tracker.
- Clarity MCP : comportement sur les LP (si la conversion LP est suspecte).
- HubSpot : SQL par source et utm via `skills/marketing-weekly/lib/marketing_weekly.py` (bloc `deals_of_week`), drill via `skills/sales-weekly/lib/hubspot.py`.

### Phase 3, décomposition et verdict

- Poser le tableau des facteurs (W / S-1 / baseline / delta).
- Nommer LE facteur dominant et sa part dans l'écart.
- Qualifier : externe / volontaire / performance.
- Si la donnée ne permet pas de trancher, dire exactement ce qui manque (« il faut la conversion LP par campagne, non mesurable car gclid absent sur X ») plutôt que d'habiller une hypothèse en conclusion.

### Phase 4, sortie

Deux niveaux :
1. **Verdict court** (2-4 phrases par canal) : résultat, facteur dominant, nature du goulot, levier ou décision à prendre. C'est ce qui part dans « L'essentiel par canal » du récap hebdo.
2. **Annexe chiffrée en chat** : le tableau de décomposition complet, les requêtes ou segments qui bougent, les deals cités quand l'effectif est petit.

## Règles absolues

- Jamais de chiffre inventé ni de facteur « estimé au doigt mouillé » : chaque facteur vient d'un pull.
- Un verdict = un facteur dominant nommé. Pas de « c'est multifactoriel » sans parts chiffrées.
- Distinguer systématiquement décision volontaire et dysfonctionnement.
- Les recommandations restent des propositions : {{OWNER}} arbitre (mémoire : un go d'exécution ne vaut jamais approbation de copy).

## Skills et mémoires liés

- `skills/marketing-weekly/` : consommateur principal (récap du lundi).
- `skills/paid-ads/` : la méthode complète d'audit et d'exécution Google Ads (ce skill-ci diagnostique, paid-ads opère).
- `skills/page-cro/` : si le verdict est « conversion LP », la suite se joue là (non calibré, demander la méthode CRO à {{OWNER}}).
- **Bibliothèques de drill installées en user-level** (non calibrées {{COMPANY}}, ordres de grandeur US) : `~/.claude/skills/ads/references/` (google-audit.md 74 checks, meta-audit.md 46 checks, budget-allocation.md, bidding-strategies.md, conversion-tracking.md, benchmarks.md), `~/.claude/skills/ads-plan/assets/info-products.md` (secteur le plus proche de {{COMPANY}}), `~/.claude/skills/seo/references/`. Les seuils utiles sont déjà distillés dans `references/benchmarks.md` ; aller aux sources uniquement pour un drill inhabituel.
- Mémoires : `reference_quality_score`, `project_meta_ads`, `project_google_ads`, `feedback_position_moyenne_page`, `feedback_pas_de_verdict_sur_une_limite`, `feedback_mesurer_en_deals_pas_en_leads`.
