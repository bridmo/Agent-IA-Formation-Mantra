# Pourquoi le repo est rangé comme ça

## Le problème que ça résout

Un repo d'agent marketing dérive toujours de la même façon : on crée un dossier par urgence, les livrables datés se mélangent aux sources de vérité, les brouillons finissent versionnés, et au bout de trois mois personne ne sait plus quel fichier fait autorité. L'agent non plus : il lit un document périmé et vous rend un travail faux avec assurance.

Le rangement ci-dessous n'est pas une question d'esthétique. Il sert à ce que **l'agent trouve la bonne information et ignore les autres**.

## Le principe

> Un repo = un cerveau (les vérités) + des machines (les boucles) + de la mémoire (les apprentissages). Le jetable et le legacy vivent à part.

Cinq zones aux rôles étanches :

| Zone | Rôle | Ne jamais y mettre |
|---|---|---|
| `brain/` | Sources de vérité : identité, ICP, voix, offre | Des livrables datés |
| `channels/` | Cellules de travail : contexte local, boucle, sorties | Du contexte transverse |
| `skills/` | Machines réutilisables | Des skills jamais utilisés |
| `memory/` | Ce que l'agent a appris | Des données volatiles |
| `.scratch/` | Jetable, non versionné | Quoi que ce soit d'actif |

Le test de tri tient en une question : **cette information sera-t-elle encore vraie dans six mois ?** Oui, c'est `brain/`. Non, c'est une cellule, avec une date dessus.

## Les quatre règles qui font tenir l'ensemble

### 1. Le contexte descend au niveau du travail

Claude Code lit `CLAUDE.md` à la racine. Mais un sous-agent lancé sur une tâche ne voit **que** ce qu'on lui donne : il n'hérite pas du contexte de la session principale.

D'où le `CLAUDE.md` local dans chaque cellule, et la règle : tout skill qui a besoin de la voix ou de l'ICP doit **citer explicitement** le fichier de `brain/` dans ses instructions. Un skill qui suppose que le contexte est là produira du générique.

### 2. La machine n'est pas l'artefact

Le skill (la méthode) et le livrable (l'article, la campagne) sont deux choses différentes, rangées à deux endroits différents. Mélanger les deux donne des skills qui contiennent des exemples périmés et des livrables qu'on ne sait plus reproduire.

### 3. Un agent, une tâche

Un agent chargé de dix outils fait tout moyennement. Un sous-agent spécialisé, avec un contexte réduit à ce qui lui est nécessaire, fait mieux et coûte moins cher.

Corollaire pratique : les tâches qui produisent beaucoup de texte intermédiaire (recherche, exploration, lecture de données) se délèguent à un sous-agent isolé. Le contexte principal reçoit la conclusion, pas les brouillons.

### 4. Boucler, avec un humain dedans

Une boucle sans point d'arrêt est un générateur de risque. Une boucle avec des gates au bon endroit est un multiplicateur de temps. Voir [BOUCLES.md](BOUCLES.md).

## Ce que vous pouvez changer

Tout, sauf la séparation entre stable et daté. C'est celle-là qui empêche l'agent de citer un chiffre mort.

Si vous n'avez que deux canaux, supprimez les cinq autres cellules. Si vous travaillez seul sur un seul produit, `brain/` peut tenir en quatre fichiers. La structure doit rester plus petite que votre activité réelle, jamais l'inverse.
