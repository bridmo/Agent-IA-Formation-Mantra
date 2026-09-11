# Équations de funnel et recettes data par canal

Pour chaque canal : l'équation, les facteurs, la source exacte de chaque facteur, et les seuils de lecture. Toujours mesurer W, S-1 et baseline 4 semaines.

## Paid (Google Ads)

**Équation** : `SQL = demande marché x part d'impressions (IS) x CTR x conversion clic vers SQL`

Les 3 questions de {{OWNER}} et comment y répondre :

### 1. Est-ce le budget ?
- `metrics.search_budget_lost_impression_share` par campagne (GAQL, `FROM campaign`). C'est la part du marché perdue UNIQUEMENT faute de budget.
- Lecture : si lost_budget monte fortement WoW (ex. 17 % vers 56 % sur Growth en S36), le goulot est le budget, pas le compte. Le levier est un arbitrage de spend, pas une optimisation.
- Compléter avec `search_rank_lost_impression_share` : si c'est le rang qui perd les impressions, le levier est QS / enchères, pas le budget.

### 2. Est-ce la conversion ?
- Conversion vraie = leads qualifiés payants HubSpot / clics Google, par campagne (matcher `utm_campaign` du deal avec la campagne). Jamais les conversions Google agrégées (mix offline empilé) ; les actions offline segmentées (`segments.conversion_action_name`) servent de contrôle de profondeur funnel (RDV planifié, R1...).
- Si la conversion chute : décomposer clic vers lead (form LP) et lead vers SQL (qualité). Croiser Clarity sur la LP (rage clicks, scroll, abandons form) et le QS décomposé (composante « expérience LP », voir `reference_quality_score`).

### 3. Est-ce le volume de recherche ?
- Demande marché estimée = impressions / IS, par campagne. Si la demande baisse à IS constante, c'est le marché.
- Tendance de fond : Ahrefs `keywords-explorer-volume-history` sur les mots-clés cœur (formation ia générative, formation growth marketing, formation n8n...). Rappel mémoire : certains volumes s'effondrent structurellement (formation agent ia -78 %), le volume Ahrefs affiché masque la trajectoire.
- Search terms (GAQL `search_term_view`) pour voir si de nouvelles requêtes apparaissent ou si le mix se dégrade.

## Paid Social (Meta)

**Équation** : `SQL = reach x fréquence x CTR (créa) x conversion LP x qualité lead vers SQL`

### 1. Est-ce le volume / la saturation d'audience ?
- `reach`, `frequency`, CPM par campagne et adset (`meta_ads.py adset ...`). Fréquence qui monte à reach stagnant = audience saturée : le levier est élargir, pas pousser.
- CPM en forte hausse = pression enchères (rentrée, concurrence), coût du volume qui monte.

### 2. Est-ce les créas ?
- CTR par ad (`meta_ads.py ad ...`), tendance 3 semaines. Créa fatiguée = CTR qui glisse pendant que la fréquence monte.
- Vidéo : `--video` (3s, thruplay, p25-p100) pour voir où le hook perd les gens.
- Rappel : le classement des formats (LP / form natif / RTG) est un diagnostic daté à re-mesurer, jamais une loi.

### 3. Est-ce la conversion ?
- Conversion vraie = leads qualifiés payants Social HubSpot / clics sortants Meta, par campagne (utm_campaign, ex. ACQ_LPIAMaestro). Le CPL natif Meta ne rentre jamais dans le verdict.
- Si la conversion LP chute : Clarity sur la LP concernée, et vérifier que le tracking (Zapier utm_campaign / source_data_1) n'a pas cassé avant d'accuser la page (une jointure vide donne 0 %, mémoire vérifier-la-date).

## Inbound (SEO / LP / direct)

**Équation** : `SQL = volume de requêtes x positions x CTR SERP x conversion site/LP`

### 1. Est-ce qu'il y a moins de gens sur le site ?
- Clics et impressions GSC WoW : Ahrefs `gsc-performance-history` (site), puis `gsc-pages-history` pour voir QUELLES pages perdent ou gagnent.

### 2. Est-ce les positions ?
- `gsc-keyword-history` sur les requêtes cœur, en quotidien, requête exacte x page. Jamais conclure sur une position moyenne de page (le mix de requêtes la fait bouger, mémoire feedback_position_moyenne_page).
- Ahrefs n'est pas la source de vérité SERP (snapshot daté, sans blocs IA) : l'observation live prime en cas de doute.
- **Règle de lecture d'une chute de clics** (source : gsc-portfolio-audit, OpenClaudia) : la position dit de quel type de chute il s'agit. Position tombée = perte de ranking. **Position tenue mais clics effondrés = quelque chose a pris les clics au-dessus (AI Overview, nouveau bloc SERP, ou la requête a changé de forme)**. Deux diagnostics, deux réponses différentes.
- **Hausse de clics** : vérifier si la position a bougé. Si non, c'est la demande qui a monté, pas le ranking. Ne pas s'attribuer le mérite.
- **CTR gap** (quick win) : page a plus de 1 500 impressions, top 10, CTR sous 2 % = réécriture title/meta, le gain le moins cher disponible.
- Toujours séparer requêtes marque et hors-marque avant de conclure.

### 3. Est-ce le volume de requêtes ?
- Impressions GSC à positions stables = demande. Croiser avec `keywords-explorer-volume-history` sur le cluster concerné pour la tendance de fond (ère IA : des requêtes entières migrent vers les LLM).

### 4. Est-ce la conversion du site / des LP ?
- SQL Inbound / clics GSC en tendance (pont clics par deal, jamais « 0 euro » sur un petit effectif).
- Drill par point d'entrée via `deals_of_week` (organique, article précis, chatgpt.com, cpf).
- Si une page qui convertissait ne convertit plus : Clarity dessus.

## Nouvelles plateformes / Maformation (hors scope v1)

Pas d'accès aux plateformes : pas de décomposition possible côté offre/visibilité.
- Se limiter au volume HubSpot (deals créés, dealnames, montants) et aux mouvements connus (campagnes coupées).
- Le dire tel quel dans le verdict : « décomposition impossible sans accès plateforme ».

## Gaspillage paid (hygiène mensuelle)

Formule de seuil (source : wasted-spend-finder, thatrebeccarae/claude-marketing) : un terme de recherche, placement ou audience est du gaspillage si les 3 conditions sont réunies :
1. Spend > CPA moyen x multiplicateur (Search hors-marque : 3x ; Search marque : 2x ; Meta : 2,5x)
2. 0 conversion
3. Minimum de clics atteint (Search hors-marque : 25 ; Meta feed : 20)

Thèmes d'exclusion à scanner dans les search terms : intent informationnel (comment, c'est quoi, tutoriel), gratuit/pas cher, concurrents, recherches d'emploi et salaire (attention {{COMPANY}} : la reconversion est la cible, mais « salaire growth marketing » ou « offre emploi » = hors intent formation), produits adjacents hors cible. Cohérent avec le socle négatifs J1 de la cellule paid (gratuit/DIY/plateformes gratuites/marque).

## Croiser l'attribution (contrôles hors modèle)

Source : skill attribution (coreyhaines31/marketingskills), adapté {{COMPANY}} :
- **Toujours lire first-touch ET last-touch côte à côte** sur les gros mouvements : la vérité est entre les deux, et l'écart entre les deux EST l'information. Chez {{COMPANY}} : `source` (attribution posée) vs `hs_analytics_source` (analytics HubSpot), sans jamais les additionner (mémoire source_vs_analytics_source).
- **La somme des conversions revendiquées par les plateformes dépasse toujours le réel** (chaque plateforme s'attribue la même vente). Réduire et expliquer l'écart, pas le faire disparaître.
- **Attribution auto-déclarée** : « comment nous avez-vous connus » posé en R1 par les sales = le signal que le tracking ne voit pas (bouche-à-oreille, ChatGPT, podcast, dark social). {{COMPANY}} a les transcripts d'appels : croiser un pic inexpliqué (ex. Nouvelles plateformes +62 %) avec ce que disent les prospects en appel avant de conclure.

## Seuils de lecture (defaults, à affiner)

- Mouvement significatif d'un facteur : plus ou moins 20 % vs baseline 4 semaines (en dessous, bruit hebdo).
- Facteur dominant : explique plus de 50 % de l'écart. Sinon, donner les parts des 2 premiers.
- Effectif minimal pour un taux : 5 conversions. En dessous, lister les deals.
