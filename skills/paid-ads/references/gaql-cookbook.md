# Référence : recettes GAQL (Google Ads)

Requêtes prêtes à l'emploi. Exécution : `python3 channels/paid/google-ads/google_ads.py "<GAQL>"` → JSON brut.
Sans argument, `google_ads.py` sort la vue campagnes 30j formatée.

> Monétaire en **micros** (÷ 1 000 000 pour des €/$). Dates : `LAST_7_DAYS`, `LAST_30_DAYS`, `LAST_90_DAYS`, etc.

## Campagnes

Vue d'ensemble (coût/clics/conversions, hors REMOVED) :
```
SELECT campaign.name, campaign.status, campaign.advertising_channel_type, metrics.cost_micros,
       metrics.impressions, metrics.clicks, metrics.conversions, metrics.conversions_value, metrics.average_cpc
FROM campaign WHERE segments.date DURING LAST_30_DAYS AND campaign.status != 'REMOVED'
ORDER BY metrics.cost_micros DESC
```

Enchères & budget :
```
SELECT campaign.name, campaign.bidding_strategy_type, campaign_budget.amount_micros
FROM campaign WHERE campaign.status='ENABLED'
```

Part d'impressions & pertes (budget vs rang) :
```
SELECT campaign.name, metrics.search_impression_share, metrics.search_budget_lost_impression_share,
       metrics.search_rank_lost_impression_share
FROM campaign WHERE campaign.status='ENABLED' AND segments.date DURING LAST_30_DAYS
```

## Conversions (LE point critique — toujours segmenter)

Conversions réelles par action :
```
SELECT campaign.name, segments.conversion_action_name, metrics.conversions, metrics.conversions_value
FROM campaign WHERE segments.date DURING LAST_30_DAYS AND campaign.status='ENABLED' AND metrics.conversions>0
```

Anatomie des actions (type/catégorie/primaire) :
```
SELECT conversion_action.resource_name, conversion_action.name, conversion_action.type,
       conversion_action.category, conversion_action.origin, conversion_action.primary_for_goal
FROM conversion_action WHERE conversion_action.status='ENABLED'
```

Config objectif d'une campagne :
```
SELECT campaign.name, conversion_goal_campaign_config.goal_config_level,
       conversion_goal_campaign_config.custom_conversion_goal
FROM conversion_goal_campaign_config WHERE campaign.id=<CAMPAIGN_ID>
```

Custom goals existants :
```
SELECT custom_conversion_goal.id, custom_conversion_goal.name, custom_conversion_goal.conversion_actions
FROM custom_conversion_goal
```

## Ad groups, mots-clés, annonces

Ad groups (statut + primary status / motif de limitation) :
```
SELECT ad_group.name, ad_group.status, ad_group.primary_status, ad_group.primary_status_reasons
FROM ad_group WHERE campaign.name='<campagne>'
```

Mots-clés + Quality Score :
```
SELECT ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
       ad_group_criterion.quality_info.quality_score, metrics.impressions, metrics.clicks, metrics.cost_micros
FROM keyword_view WHERE campaign.name='<campagne>' AND segments.date DURING LAST_30_DAYS AND metrics.impressions>0
ORDER BY metrics.cost_micros DESC
```

RSA en place (titres/descriptions/URL) :
```
SELECT ad_group.name, ad_group_ad.ad.responsive_search_ad.headlines,
       ad_group_ad.ad.responsive_search_ad.descriptions, ad_group_ad.ad.final_urls, ad_group_ad.status
FROM ad_group_ad WHERE campaign.name='<campagne>' AND ad_group_ad.status!='REMOVED'
```

Statut d'approbation des annonces (revue Google) :
```
SELECT ad_group.name, ad_group_ad.policy_summary.approval_status, ad_group_ad.policy_summary.review_status
FROM ad_group_ad WHERE campaign.name='<campagne>' AND ad_group.status='ENABLED' AND ad_group_ad.status='ENABLED'
```

## Assets (sitelinks, callouts…)

Niveau campagne / compte :
```
SELECT campaign_asset.field_type, campaign_asset.status FROM campaign_asset WHERE campaign.name='<campagne>'
SELECT customer_asset.field_type FROM customer_asset
```

## Pièges GAQL

- Certaines métriques d'IS peuvent être absentes selon le type de campagne → coder défensif (`.get`).
- `searchStream` renvoie du **camelCase** (`costMicros`), même si la requête est en snake_case.
- Filtrer sur `metrics.*` dans `WHERE` est permis (ex. `metrics.conversions>0`).
