# Référence : suivi des conversions (Google Ads)

Le point le plus piégeux d'un compte qui remonte ses conversions depuis un CRM. À maîtriser avant tout diagnostic de performance.

## Le piège : la colonne « Conversions » ment

Situation fréquente sur un compte B2B ou à cycle long :

1. **Les conversions sont des imports hors ligne venant du CRM** (`conversion_action.type = UPLOAD_CLICKS`), pas
   des conversions web. Elles remontent plusieurs jours après le clic.
2. **Plusieurs étapes du tunnel sont primaires en même temps.** Un même prospect est alors compté à chaque étape
   (lead, rendez-vous pris, rendez-vous tenu, décision, vente) : le total est **empilé**, gonflé de trois à quatre fois.
   Le coût par acquisition affiché devient un coût par *événement de tunnel*, pas par résultat.

**Conséquence pratique :** ne jamais citer/optimiser un nombre de « conversions » brut. Toujours segmenter :

```
SELECT campaign.name, segments.conversion_action_name, metrics.conversions, metrics.conversions_value
FROM campaign
WHERE segments.date DURING LAST_30_DAYS AND campaign.status='ENABLED' AND metrics.conversions>0
```

## Anatomie des actions de conversion

Tirer le détail :
```
SELECT conversion_action.name, conversion_action.type, conversion_action.category,
       conversion_action.origin, conversion_action.primary_for_goal, conversion_action.status
FROM conversion_action WHERE conversion_action.status='ENABLED'
```

Champs clés :
- **`type`** : `UPLOAD_CLICKS` pour un import CRM, `WEBPAGE` pour du web. Sur un compte à cycle long, tout est hors ligne.
- **`category`** : la maille des objectifs de la régie. Exemple de correspondance pour un tunnel de vente classique :
  - Lead qualifié → **SUBMIT_LEAD_FORM**
  - Rendez-vous tenu → **BOOK_APPOINTMENT**
  - Opportunité en décision → **QUALIFIED_LEAD**
  - Vente → **PURCHASE**
- **`primary_for_goal`** — `True` = compté dans la colonne Conversions ET pilote les enchères. `False` = observé seulement.

## Isoler le vrai événement : Custom Conversion Goal

**Problème :** l'« objectif au niveau campagne » standard fonctionne par **catégorie × origine**, pas par action.
Or plusieurs de vos actions partagent souvent une même catégorie (deux étapes différentes classées toutes les deux
en QUALIFIED_LEAD). Un simple interrupteur de catégorie ne peut donc **pas** isoler une action précise.

**Solution :** un **Custom Conversion Goal** groupe des **actions** précises (maille action, pas catégorie), puis on
l'assigne à la campagne en `goalConfigLevel = CAMPAIGN`.

### Ce que ça donne une fois en place
- Un objectif personnalisé qui ne contient **qu'une seule action** : celle qui correspond vraiment à un lead
  qualifié chez vous.
- Assigné à la campagne au niveau `CAMPAIGN`, de sorte que la stratégie d'enchère optimise cet événement précis
  et plus l'empilement.

### Exécution (writer)
```
# 1. créer le custom goal
python3 channels/paid/google-ads/google_ads_write.py custom-goal-create \
    --name "Leads qualifiés (mon-tunnel)" \
    --actions customers/<CUSTOMER_ID>/conversionActions/<ACTION_ID> --execute

# 2. l'assigner à la campagne
python3 channels/paid/google-ads/google_ads_write.py campaign-goal-assign \
    --campaign <CAMPAIGN_ID> --custom-goal customers/<CUSTOMER_ID>/customConversionGoals/<GOAL_ID> --execute

# réversibilité : retour aux objectifs du compte
python3 channels/paid/google-ads/google_ads_write.py campaign-goal-reset --campaign <CAMPAIGN_ID> --execute
```

Vérifier après coup :
```
SELECT conversion_goal_campaign_config.goal_config_level, conversion_goal_campaign_config.custom_conversion_goal
FROM conversion_goal_campaign_config WHERE campaign.id=<CAMPAIGN_ID>
```

## Mesure : ne pas se faire avoir par la latence

- **Latence des imports :** les conversions arrivent plusieurs jours après le clic. Les chiffres récents sont donc
  toujours sous-estimés. En tenir compte avant de juger une performance « fraîche », sous peine de couper une
  campagne qui marche.
- **Un test de prix ne se juge pas au coût par lead.** Observé : cacher le prix sur la page ne change pas le coût
  par lead, mais change tout en aval. Le juge de paix est le taux lead vers vente et le coût d'acquisition client.

## Avertissement « Composant Formulaire de lead manquant »

Apparaît dès que l'objectif est de catégorie SUBMIT_LEAD_FORM. La régie propose son formulaire natif.
**Ne l'ajoutez pas :** il court-circuite votre page, donc votre argumentaire, produit des leads moins qualifiés et
mélange les sources d'attribution. Cet avertissement peut être ignoré.
