# Référence : score de qualité et gisement de volume (Search)

Le QS est souvent **le plafond de volume**, pas le budget. À diagnostiquer avant de toucher au budget.

## Diagnostic : budget ou rang ?

```
SELECT campaign.name, metrics.search_impression_share,
       metrics.search_budget_lost_impression_share, metrics.search_rank_lost_impression_share
FROM campaign WHERE campaign.status='ENABLED' AND segments.date DURING LAST_30_DAYS
```

| Lecture | Signification | Levier |
|---|---|---|
| Perdu surtout **budget** | La campagne gagne les enchères mais manque de budget | Budget / efficacité enchère |
| Perdu surtout **rang/QS** | Enchère trop basse OU Quality Score faible | **Structure + pertinence annonce** (pas le budget) |

**Cas d'école :** une campagne à 11 % de part d'impressions, dont 13 % perdus pour cause de budget et **76 % perdus
pour cause de rang et de score de qualité**, qui ne dépensait même pas son budget quotidien. Le volume était bloqué
par le rang, pas par l'argent. Doubler le budget n'aurait rien débloqué, et c'est pourtant le premier réflexe.

## La cause racine du QS bas : ad group fourre-tout

Tirer le QS par mot-clé :
```
SELECT ad_group.name, ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type,
       ad_group_criterion.quality_info.quality_score, metrics.impressions, metrics.clicks
FROM keyword_view WHERE campaign.name='<campagne>' AND segments.date DURING LAST_30_DAYS
```

**Symptôme le plus fréquent :** quinze à vingt mots-clés d'intentions différentes entassés dans **un seul groupe
d'annonces**, avec **une annonce générique** pour tout le monde. Le taux de clic attendu et la pertinence tombent au
plancher, et les mots-clés cœur se retrouvent à **3 sur 10**, y compris celui qui porte le nom de la campagne.

## Le fix : ad groups serrés par intention (STAG)

Éclater en ad groups thématiques. Chaque RSA reprend l'**intention exacte** du mot-clé dans ses titres → QS ↑ →
on récupère une partie des impressions perdues au rang → **plus de volume au même CPL**.

Exemple de découpage : un groupe par intention réelle, et on supprime les groupes trop génériques (ceux dont les
requêtes ne disent rien de l'intention d'achat) plutôt que de les laisser tirer la moyenne vers le bas.

## Les 3 composantes — et laquelle bloque réellement

Toujours tirer le QS **décomposé**, jamais le score global seul :
```
SELECT ad_group.name, ad_group_criterion.keyword.text,
       ad_group_criterion.quality_info.quality_score,
       ad_group_criterion.quality_info.creative_quality_score,      -- pertinence annonce
       ad_group_criterion.quality_info.post_click_quality_score,    -- expérience LP
       ad_group_criterion.quality_info.search_predicted_ctr         -- CTR attendu
FROM keyword_view WHERE ad_group_criterion.quality_info.quality_score > 0
```

⚠️ **Le QS est RELATIF, pas absolu.** Google : le score est établi *par comparaison avec les autres annonceurs dont
les annonces se sont affichées sur exactement la même recherche, sur 90 jours*. Deux mots-clés du **même ad group
pointant sur la même page** peuvent avoir des scores différents. Cas réel : deux requêtes composées des mêmes mots
dans un ordre différent, même page de destination, scores 7 et 5. Ne jamais conclure « notre page est mauvaise » sur
un score bas : elle peut être bonne, mais plus mince que celle des concurrents sur cette requête précise.

## ⚠️ Après le découpage, c'est la page qui devient le plafond

L'ordre d'impact ci-dessus vaut **avant** le découpage en groupes serrés. Une fois le découpage fait, la mesure sur
les mots-clés actifs d'un compte réel donnait :

| Composante | État après split | Verdict |
|---|---|---|
| Pertinence annonce | au-dessus de la moyenne sur la moitié | ✅ le découpage et le titre épinglé ont réglé le problème |
| Taux de clic attendu | en dessous sur un cinquième | 🟡 chantier de rédaction résiduel |
| **Expérience de page** | **en dessous sur plus de 80 %** | 🔴 **le plafond** |

> **Régularité observée, sans exception : expérience de page « moyenne » donne un score de 6 ou 7, expérience
> « en dessous » donne 1 à 5.** Améliorer l'annonce quand la pertinence est déjà au-dessus de la moyenne ne donne
> rien. Le seul levier qui fait monter le mot-clé est l'expérience de page.

**Ce qui NE marche PAS pour l'expérience LP (vérifié, ne pas refaire) :**
1. **Optimiser la vitesse.** Page passée de 3,6 s à 0,4 s de temps de réponse, aucune ressource lourde : le score
   d'expérience de page n'a pas bougé. Chercher des kilo-octets est du temps perdu.
2. **Changer de domaine ou de sous-domaine.** Score stable avant et après deux migrations.
3. **La correspondance de message cosmétique.** Cinq pages au texte identique à 100 %, dont seuls le titre et
   l'accroche changent : aucun effet. La régie évalue le **contenu**, pas le titre.

**Ce qui reste à tester :** un contenu réellement différencié par intention de recherche, et la transparence
tarifaire (afficher le prix plutôt que de renvoyer à un devis).

## Une page par groupe d'annonces ?

Non : **une page par intention de recherche**, avec un contenu réellement différent, pas seulement le titre.
Corollaire : une page dupliquée dont on ne change que le titre n'améliore rien. Si vous déclinez une page, déclinez
le **corps** (contenu, preuves, questions fréquentes) sur l'intention visée.
Et ne bloquez jamais une refonte de groupes d'annonces en attendant que les pages soient prêtes.

## Doublons de mots-clés entre ad groups → QS 1

Un même mot-clé présent dans 2 ad groups hérite de la pertinence de l'annonce du **mauvais** groupe et se
cannibalise. Cas réel : un mot-clé ajouté « en filet » dans un groupe dont le titre épinglé parlait d'autre chose
est tombé à **1 sur 10**, contre 5 dans son groupe légitime. **Vérifiez l'absence de doublons après toute
réouverture de groupe.**

## Après une refonte

- Phase de réapprentissage d'une à deux semaines, cumulée si vous changez aussi l'objectif de conversion.
- Suivre le score des mots-clés cœur à 14 jours (objectif : sortir de 3, viser 6 à 8).
- Les nouvelles annonces passent en revue (`REVIEW_IN_PROGRESS`, statut de groupe `MOST_ADS_UNDER_REVIEW`).
  C'est normal et cela se débloque en quelques heures à un jour ouvré.
