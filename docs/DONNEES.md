# Brancher des données réelles

## La règle

Avant d'estimer, d'inférer ou de brainstormer : vérifier s'il existe une **donnée déterministe** accessible.

| Couche | Sert à | Ne sert pas à |
|---|---|---|
| Déterministe (API, MCP, fichier) | Calculer, chercher, exécuter | Juger |
| Jugement (le modèle) | Synthétiser, arbitrer, rédiger | Deviner un chiffre |

Un modèle à qui on demande « combien de visites a fait cette page » produira un nombre plausible. C'est le pire des résultats : faux et crédible.

## Comment brancher une source

Claude Code se connecte à des sources externes via des serveurs MCP. Une fois branché, l'agent interroge la source lui-même.

```bash
claude mcp add <nom> -- <commande du serveur>
claude mcp list
```

Selon les outils, la connexion se fait aussi depuis les réglages de connecteurs de votre compte. Vérifiez avec `/mcp` en session que la source répond avant de compter dessus.

## Les sources qui changent tout

| Question | Source à brancher |
|---|---|
| Combien de clients, quel pipeline, quelle source | Votre CRM |
| Positions, volumes, backlinks | Votre outil SEO |
| Ce que Google vous envoie vraiment | Search Console |
| Ce que les visiteurs font sur la page | Enregistrements de sessions, cartes de clics |
| Ce que coûte un client par canal | Régies publicitaires + CRM |

Sans CRM branché, tous vos arbitrages entre canaux se font au ressenti.

## Quand il n'y a pas de MCP

Un script suffit. Le dossier `tools/` contient des clients d'API prêts à adapter et des fiches pour une soixantaine d'outils marketing.

Le principe : le script sort un fichier, l'agent lit le fichier. Pas besoin d'intégration sophistiquée pour supprimer 90 % des approximations.

## Le piège de la mesure

Trois erreurs de lecture qui reviennent partout :

1. **Ancrer la fenêtre sur l'horloge plutôt que sur la donnée.** Si votre export s'arrête au 3, une analyse « sur les 7 derniers jours » compare 4 jours à 7.
2. **Lire un taux sur un petit effectif.** À 40 visites, un taux de conversion ne veut rien dire.
3. **Un résultat à 0 % ou 100 %.** C'est presque toujours une jointure vide, pas un fait.

Quand un chiffre surprend, vérifiez la requête avant de construire l'histoire qui l'explique.
