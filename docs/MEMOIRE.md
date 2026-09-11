# La boucle d'auto-amélioration

C'est le mécanisme qui fait qu'un agent utilisé six mois travaille mieux qu'au premier jour. Sans lui, vous recommencez chaque lundi.

## Le problème

Vous corrigez l'agent : « non, on ne dit jamais ça », « le bon chiffre c'est celui-là », « on mesure en clients pas en leads ». La session se termine. La correction disparaît. Vous la retapez la semaine suivante, avec un peu moins de patience.

## Le mécanisme

Une correction qui **se reproduira** devient un fichier. Un fichier = un fait.

```
Friction en session
   → l'agent (ou vous) écrit une mémoire
   → une ligne s'ajoute dans MEMORY.md
   → la session suivante démarre en connaissant la règle
```

## Le format

```markdown
---
name: slug-en-kebab-case
description: une ligne qui sert à décider si ce fichier est pertinent
metadata:
  type: user | feedback | project | reference
---

Le fait, énoncé directement.

**Pourquoi :** ce qui a motivé la règle.
**Comment l'appliquer :** dans quelle situation, concrètement.
```

Le **pourquoi** n'est pas décoratif. Une règle sans sa raison est appliquée mécaniquement, y compris là où elle n'a pas de sens.

Les liens entre mémoires s'écrivent `[[nom-de-l-autre]]`. Un lien vers une mémoire qui n'existe pas encore est une note d'intention, pas une erreur.

## Les quatre types

| Type | Répond à | Exemple |
|---|---|---|
| `user` | Qui est la personne avec qui je travaille | « Veut le chiffre d'abord, l'explication ensuite » |
| `feedback` | Comment je dois travailler | « Ne jamais publier sans capture pleine page » |
| `project` | Quelles sont les contraintes en cours | « Prix gelés jusqu'en juin, leviers autorisés : groupage » |
| `reference` | Où se trouve telle ressource | « Le tableau de bord d'attribution est ici » |

## Écrire une mémoire en session

Le plus rapide, en début de message :

```
# on mesure toujours en clients gagnés, jamais en leads
```

Ou explicitement : `écris ça en mémoire, avec le pourquoi`.

## Ce qui ne doit pas y aller

| Non | Où ça va |
|---|---|
| Ce que le repo dit déjà | Nulle part, c'est déjà écrit |
| Un diagnostic daté | Dans la cellule, avec sa date |
| Un fait stable sur le produit | Dans `brain/` |
| Ce qui n'intéresse que cette session | Nulle part |

La confusion la plus fréquente est entre **contexte stable** et **diagnostic daté**. « Le coût d'acquisition a doublé en octobre » n'est pas une règle de travail, c'est une observation qui sera fausse en janvier. Elle va dans la cellule concernée.

## L'entretien

Une mémoire fausse est pire que pas de mémoire : l'agent lui fait confiance et vous n'êtes pas là pour le corriger.

Une fois par mois : ouvrez `MEMORY.md`, parcourez les descriptions, supprimez ce qui a changé. Cinq minutes.

## Le signe que ça marche

Ouvrez une session neuve et demandez : `qu'est-ce que tu sais de notre façon de travailler ?`

S'il cite vos corrections des semaines précédentes, la boucle est fermée. S'il répond des généralités, vos mémoires ne sont pas indexées dans `MEMORY.md`, ou `CLAUDE.md` ne pointe pas dessus.
