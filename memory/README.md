# memory/ — ce que l'agent apprend

C'est la différence entre un agent qui stagne et un agent qui devient meilleur chaque semaine.

## Le principe

Quand vous corrigez l'agent sur quelque chose qui **se reproduira**, la correction doit survivre à la fin de la session. Sinon vous la retaperez.

Une mémoire = un fichier = un fait.

## Le format

```markdown
---
name: slug-en-kebab-case
description: une ligne, sert à décider si le fichier est pertinent
metadata:
  type: user | feedback | project | reference
---

Le fait.

**Pourquoi :** ce qui a motivé la règle (sans ça, elle sera mal appliquée).
**Comment l'appliquer :** concrètement, dans quelle situation.
```

Puis une ligne dans `MEMORY.md`.

## Les quatre types

| Type | Contient | Exemple |
|---|---|---|
| `user` | Qui vous êtes, vos préférences de travail | « Préfère les tableaux aux listes à puces » |
| `feedback` | Vos corrections devenues règles | « Ne jamais écrire de titre en majuscules » |
| `project` | Décisions et contraintes d'un chantier | « Le prix est gelé à 1 500 € jusqu'en mars » |
| `reference` | Pointeurs externes | « Le tableau de bord de suivi est ici » |

## Ce qui ne va pas en mémoire

- Ce que le repo dit déjà (structure, contenu de `brain/`)
- Ce qui n'intéresse que la session en cours
- Un diagnostic daté : il va dans la cellule concernée, avec sa date

## Entretien

Une mémoire fausse est pire que pas de mémoire, parce que l'agent lui fait confiance. Relisez `MEMORY.md` une fois par mois, supprimez ce qui a changé.

Détail complet et exemples : [../docs/MEMOIRE.md](../docs/MEMOIRE.md).
