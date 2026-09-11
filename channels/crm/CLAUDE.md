# channels/crm/ — Cellule CRM et cycle de vie

## Objectif
Que chaque contact arrive dans le CRM avec sa source, et que personne ne se perde entre le formulaire et la vente.

## Contexte à charger
`brain/icp.md`, `brain/messaging.md`, la structure de votre CRM (étapes, propriétés, propriétaires).

## Pièges
- **Ne jamais modifier des contacts déjà créés.** Un problème de données se corrige à la source, jamais par une mise à jour rétroactive de l'historique. Vous perdriez la capacité de comparer avant et après.
- **Un « envoyé avec succès » n'est pas une preuve d'arrivée.** Vérifiez côté CRM que l'enregistrement existe, pas seulement que l'automatisation a répondu oui.
- **Vérifiez la date avant toute analyse.** Ancrez la fenêtre sur la donnée disponible, pas sur l'horloge. Un résultat à 0 % ou 100 % signale presque toujours une jointure vide.
- **Deux axes d'attribution ne se mélangent pas.** La source déclarée et la source technique répondent à deux questions différentes. Les additionner produit du double comptage.
- **Mesurez en clients, pas en contacts.** Un contact créé n'est pas une valeur.

## Outils
Skills : `email-sequence`, `churn-prevention`, `revops`, `sales-pipeline`. Client d'API dans `tools/`.

## Qui tranche
Tout envoi à une liste : vous. Toute écriture en masse dans le CRM : vous, après simulation.
