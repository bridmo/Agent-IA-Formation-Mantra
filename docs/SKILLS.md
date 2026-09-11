# Les skills

## Ce que c'est

Un skill est une méthode écrite une fois, rejouée à chaque fois. Concrètement : un dossier avec un `SKILL.md` que l'agent charge quand la tâche correspond.

La différence avec un prompt : un prompt vit dans une conversation, un skill vit dans le repo, s'améliore, et se déclenche tout seul quand le sujet arrive.

## Anatomie

```
skills/mon-skill/
├── SKILL.md              # obligatoire : l'en-tête et la méthode
├── references/           # facultatif : le détail chargé à la demande
│   └── gabarits.md
└── lib/                  # facultatif : les scripts
    └── outil.py
```

L'en-tête `SKILL.md` :

```yaml
---
name: mon-skill
description: >
  Ce que fait le skill, et surtout QUAND le déclencher. Listez les phrases
  réelles que vous employez : "optimise la page", "pourquoi ça convertit mal".
  C'est ce texte qui décide du déclenchement : s'il est vague, le skill dort.
---
```

**La description est la partie la plus importante.** Un excellent skill avec une description floue ne se déclenche jamais.

## Les 68 livrés

| Catégorie | Combien | État |
|---|---|---|
| Conversion, copy, SEO, cycle de vie, vente, analyse | 51 | Génériques, utilisables tels quels |
| Stratégie, publicité, rédaction SEO, créations, rapports | 15 | Méthode éprouvée, **calibration à faire** |

Les 15 calibrables ont une section **Calibration** en tête de fichier. Ils portent une méthode durcie par l'usage réel : les pièges qu'ils listent ont chacun coûté quelque chose. Ce qui manque, ce sont vos chiffres.

Index complet : [../skills/README.md](../skills/README.md).

## Calibrer un skill existant

1. Ouvrez son `SKILL.md`, lisez la section Calibration.
2. Remplacez les `{{PLACEHOLDER}}` par vos valeurs.
3. Vérifiez les fichiers de `brain/` qu'il référence : s'ils sont vides, le skill tournera à vide.
4. Lancez-le sur un cas réel, notez ce qui manque, complétez.

Le troisième point est celui qu'on oublie. Un skill qui dit « croise avec l'ICP » et un `brain/icp.md` vide produit du marketing générique avec beaucoup d'assurance.

## En écrire un nouveau

**Quand :** à la troisième fois que vous réexpliquez la même méthode. Pas avant : vous ne connaissez pas encore la méthode.

**Comment :**

1. Faites la tâche à la main une fois de plus, en notant ce que vous décidez et pourquoi.
2. Écrivez le `SKILL.md` : d'abord quand le déclencher, ensuite les étapes, ensuite les pièges.
3. Ajoutez la section « anti-patterns » : ce qu'il ne faut PAS faire est souvent plus utile que la marche à suivre.
4. Testez-le sur un cas que vous connaissez : si le résultat est moins bon que le vôtre, le skill n'est pas fini.

**Structure qui marche :**

```markdown
## Quand ce skill se déclenche
## Contexte à charger      (les fichiers de brain/ à ouvrir, explicitement)
## Étapes                  (numérotées, avec les gates)
## Anti-patterns           (ce qui a déjà échoué)
## Sorties attendues       (à quoi ressemble un bon résultat)
```

## Le rendre découvrable

Claude Code découvre les skills du dossier `.claude/skills/`. Le kit utilise des liens symboliques pour éviter de dupliquer les fichiers :

```bash
ln -s ../../skills/mon-skill .claude/skills/mon-skill
```

Sans ce lien, votre skill existe mais ne se déclenche pas.

## Entretenir

Un skill qu'on n'utilise jamais est du bruit à chaque déclenchement. Tous les trimestres : supprimez ceux que vous n'avez pas lancés une seule fois.
