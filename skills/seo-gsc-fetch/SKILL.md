---
name: seo-gsc-fetch
description: >
  Récupère les données brutes de Google Search Console via l'API : performances globales, pages,
  requêtes, et croisements page × requête. Déclencher quand l'utilisateur demande "les données
  Search Console", "ce que Google nous envoie vraiment", "les vraies requêtes", "exporte la GSC",
  ou avant tout diagnostic SEO qui a besoin de données réelles plutôt que d'estimations d'outil tiers.
---

# Récupération des données Search Console

## Pourquoi ce skill existe

Les outils SEO du marché **estiment** votre trafic. La Search Console le **mesure**. Quand les deux se
contredisent, c'est la Search Console qui a raison, parce qu'elle vient de Google.

C'est la source déterministe à brancher en premier sur n'importe quel diagnostic SEO.

## Configuration

Quatre variables d'environnement, dans `.env` :

```
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REFRESH_TOKEN=
SEARCH_CONSOLE_SITE_URL=sc-domain:votre-domaine.fr
```

Le jeton de rafraîchissement s'obtient une fois via le parcours OAuth de Google, avec la portée
`https://www.googleapis.com/auth/webmasters.readonly`.

## Usage

```bash
python3 skills/seo-gsc-fetch/fetch_gsc.py 2026-01-01 2026-03-31
python3 skills/seo-gsc-fetch/fetch_gsc.py 2026-01-01 2026-03-31 --compare 2025-01-01 2025-03-31
```

Sortie dans `channels/seo/gsc-data/` : quatre fichiers JSON (performances, pages, requêtes, croisements).

## Pièges de lecture

1. **La position moyenne d'une page n'est pas un classement.** Elle bouge avec le mix de requêtes qui
   ramènent sur la page. Une page peut « chuter » en moyenne alors qu'aucune requête n'a bougé.
   Vérifiez toujours requête par requête avant d'annoncer un décrochage.
2. **Les données ont deux à trois jours de retard.** Une fenêtre qui inclut hier est incomplète.
3. **Les requêtes à faible volume sont masquées** pour raisons de confidentialité. La somme des requêtes
   est toujours inférieure au total : c'est normal, ce n'est pas un bug.
4. **Un clic n'est pas un client.** Poussez jusqu'au CRM avant de conclure sur la valeur d'une page.
