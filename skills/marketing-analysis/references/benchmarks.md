# Benchmarks et seuils de diagnostic (minés des skills installés + GitHub)

Compilé le 07/09/2026 depuis la suite `~/.claude/skills/ads/` (46+74 checks, synthèses de recherche LLM datées 2026-02, données WordStream/LocaliQ 2025 et Triple Whale 2025), la suite `~/.claude/skills/seo/` (AgriciDaniel/claude-seo v1.8.2) et les repos GitHub cités dans canaux.md.

**Avertissement de fiabilité** : benchmarks 100 % US en USD, sans ligne CVR/CPL pour l'éducation FR. La suite ads n'a pas de source primaire traçable. À traiter comme des ordres de grandeur pour cadrer un diagnostic, jamais comme des cibles {{COMPANY}}. Les cibles {{COMPANY}} viennent du P&L et de nos baselines.

## Paid Google Search

### Question budget
- Top performers en « Limited by Budget » = goulot budget confirmé (check G39).
- Pacing : plusieurs campagnes qui tapent leur cap avant midi = FAIL (G09).
- IS > 80 % = rendements décroissants, remettre du budget ne rapporte presque plus : diversifier (mots-clés, campagnes) plutôt que pousser.
- Cause fréquente de « chute de volume » qui n'est PAS la demande : cible tCPA irréaliste (FAIL si tCPA < 50 % du CPA réel, G37) ou > 40 % des campagnes en learning (G38).
- Scaling : +20 % max par palier puis 3-5 jours d'attente ; si le CPA monte de > 15 % après une hausse, c'est la hausse la cause : rollback, 7 jours, puis scaling horizontal.
- Données minimales enchères : < 15 conv/30 j = pas de Smart Bidding fiable ; tCPA se pose à 1,1-1,2x le CPA historique, ajustements de 10 % max tous les 14 jours.

### Question conversion
- QS décomposé (le bon ordre de lecture, G22-G24) : composante « expérience LP » Below Average sur > 30 % des mots-clés = FAIL ; expected CTR et ad relevance : FAIL > 35 %.
- Avant de conclure « la conversion baisse », vérifier le tracking : Consent Mode v2 absent en EU = jusqu'à 90-95 % des métriques en moins ; ~31 % d'acceptation cookies.
- Kill rule : spend > 3x le CPA cible et 0 conversion = pause. Suffisance avant de tuer : au moins 7 jours ET 20 clics (ou 50 clics à 0 conversion).
- Fraîcheur : aucune nouvelle annonce depuis > 90 jours = FAIL ; CTR < 50 % du benchmark sectoriel = FAIL.

### Question volume
- Les suites installées n'ont RIEN sur le plafond de demande : notre lecture impressions/IS + IS perdue budget vs rang (canaux.md) reste la seule décomposition. Seul seuil existant : IS > 80 % = marché saturé.
- Repères US toutes industries : CTR Search 6,66 %, CVR 7,52 %. CPC Education US : 6,23 $.

## Paid Social Meta

### Question créas (le bloc le plus solide du corpus)
- **Fatigue confirmée = chute de CTR > 20 % sur 14 jours ET fréquence > 3** (M28). Chute 10-20 % = surveillance.
- Fréquence 7 jours : prospecting > 3 = alerte, > 5 = FAIL ; retargeting > 8 = alerte, > 12 = FAIL.
- Durée de vie d'une créa : 3-4 semaines en prospection, 6-7 en retargeting ; la conversion chute d'environ 45 % à partir de 4 expositions. Cadence de refresh : 2-4 semaines.
- Diversité : au moins 5 créas par ad set et 3 formats actifs ; hook vidéo : > 70 % de skip sur les 3 premières secondes = FAIL.
- CTR plancher : < 0,5 % = FAIL, < 1 % = alerte.

### Question audience / volume
- Saturation : fréquence 7 j > 4 sur prospecting = audience épuisée, rafraîchir la créa OU élargir.
- Learning : sortie = 50 conversions/semaine/ad set ; > 50 % des ad sets en Learning Limited = FAIL. Protocole dans l'ordre : élargir, augmenter le budget, remonter l'événement d'optimisation, consolider.
- Resets à ne pas confondre avec une saturation : changement budget > 20 %, toute édition de créa ou de ciblage, pause > 7 jours.
- Budget par ad set : au moins 5x le CPA cible, sinon le signal ne sort pas.
- Overlap d'audiences > 30 % = significatif (les ad sets se cannibalisent).

### Question conversion
- Avant d'accuser la LP : CAPI absent = 30-40 % de données perdues ; EMQ cible >= 8. Chez {{COMPANY}} la conversion se lit en deals HubSpot (utm_campaign), le natif ne sert qu'au contrôle.
- Repères US lead gen : CTR objectif leads 2,59 %, CPL Meta leads 27,66 $ (~25 EUR). Info products, lead magnet : CPL 2-8 $ ; offre coeur type 97-997 $ : CPA 30-100 $. À convertir en coût par SQL {{COMPANY}} (baseline observée : ~40 EUR par SQL via LP).

## Inbound SEO / LP

- Quick wins GSC : requêtes en position 4-10 avec > 50 impressions (règle codée dans claude-seo).
- Latence GSC : 2-3 jours. Ne jamais diagnostiquer une chute sur les 2 derniers jours.
- AI Overviews : > 50 % des requêtes couvertes ; 92 % des citations viennent du top 10. Chute de clics à position tenue = bloc IA probable (règle déjà dans canaux.md).
- Core Web Vitals (p75) : LCP <= 2,5 s, INP <= 200 ms, CLS <= 0,1. Décomposition causale du LCP : TTFB (< 800 ms) + resource load delay + resource load time + render delay.
- Conversion LP : message match annonce-LP = problème n°1 des campagnes ; formulaire <= 5 champs (6-8 = alerte) ; 1 seconde de délai = environ -7 % de conversions ; CVR médiane LP inter-secteurs 6,6 %, top 10 % à 20 %+.
- QS et LP : bonne expérience LP = jusqu'à -50 % de CPC, mauvaise = jusqu'à +400 %.

## Secteur éducation / info products (le plus proche de {{COMPANY}})

Source : `~/.claude/skills/ads-plan/assets/info-products.md` (US, USD).
- Saisonnalité : pics janvier (résolutions) et **septembre (back-to-learning)**. La demande de rentrée observée en S36 est donc structurelle, pas un accident.
- Trajectoire CPL lead magnet : < 8 $ (mois 1) vers < 4 $ (mois 6) ; CPA inscription webinar : < 15 $ vers < 8 $.
- Piège listé qui nous concerne : « broad targeting trop tôt » : il faut 50+ conversions/semaine pour que le broad Meta fonctionne.
- Répartition type pour un tunnel à candidature ou demande de démo : 40 % audience froide, 40 % retargeting, 20 % clients existants. À vérifier sur vos propres données avant d'y croire.
- ATT iOS : éducation = opt-in le plus bas de tous les secteurs (7-14 %), donc le signal mobile Meta est structurellement pauvre : une raison de plus de juger en deals HubSpot.

## Incohérences relevées dans les sources (tranchées ici)

- Seuil de gaspillage Google : google-audit.md dit < 5 % du spend, ads-google/SKILL.md dit < 10 %. On retient **< 10 %** (plus réaliste sur un petit compte).
- INP : ads-landing dit < 100 ms, le référentiel CWV officiel dit <= 200 ms. On retient **200 ms** (seuil Google officiel).

## Ce que ces corpus ne couvrent pas (et que notre skill apporte)

1. La décomposition d'un écart entre facteurs (impressions x CTR x CVR, période vs période) : nulle part.
2. La lecture IS perdue budget vs IS perdue rang : nulle part, alors que c'est LE juge de paix budget vs performance.
3. La calibration sur votre marché, votre cycle de décision et la qualité de lead en aval : nulle part. C'est à vous de la produire.
