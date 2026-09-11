# Agent Formation IA — École Mantra

Le squelette d'un agent marketing qui travaille avec vous dans Claude Code, et qui s'améliore à mesure que vous l'utilisez.

Construit par l'École Mantra à partir de son propre repo de production, puis vidé de toute donnée d'entreprise pour que vous le remplissiez avec la vôtre.

Ce dépôt n'est pas une bibliothèque de prompts. C'est une **structure de repo** : un endroit où votre agent trouve le contexte de votre entreprise, des boucles de travail explicites, 68 skills réutilisables, et une mémoire qui capitalise vos corrections au lieu de les perdre à chaque session.

Il est livré vide de tout contenu d'entreprise. Vous le remplissez avec le vôtre.

---

## Ce qu'il y a dedans

| Zone | Rôle | État à la livraison |
|---|---|---|
| `brain/` | Les sources de vérité : qui vous êtes, à qui vous vendez, comment vous parlez, ce que vous vendez | Templates à remplir |
| `channels/` | Une cellule de travail par canal (SEO, paid, CRO, CRM, social, contenu, sales), chacune avec son contexte local et sa boucle | 7 cellules, boucles d'exemple |
| `skills/` | 68 machines réutilisables, du cadrage stratégique à la rédaction d'annonces | Prêtes, 15 à calibrer |
| `memory/` | La boucle d'auto-amélioration : ce que l'agent apprend de vos corrections | Vide, avec le mode d'emploi |
| `tools/` | Clients d'API, fiches de 60+ intégrations, scripts Google Workspace | Prêts, clés à fournir |
| `security/` | Scanner de données sensibles + hook pre-commit | Prêt à installer |
| `docs/` | Pourquoi le repo est rangé ainsi, comment écrire une boucle, un skill, une mémoire | À lire |

## Démarrer

Si vous n'avez jamais utilisé Claude Code, commencez par [ONBOARDING.md](ONBOARDING.md) : c'est un parcours en quatre étapes, de l'installation à votre première boucle qui tourne.

Si vous êtes déjà à l'aise :

```bash
git clone <votre-fork> mon-agent && cd mon-agent
grep -rl '{{' brain/ CLAUDE.md AGENTS.md
```

Chaque `{{PLACEHOLDER}}` est un trou à combler. Remplissez `brain/` d'abord, le reste en dépend.

Puis, dans le dossier :

```bash
claude
```

et demandez-lui : `lis CLAUDE.md et AGENTS.md, puis dis-moi ce qui manque dans brain/ pour que tu puisses travailler`.

## Le principe

Un agent qui produit du bon travail marketing a besoin de quatre choses, et un chat ne lui en donne aucune durablement :

1. **Du contexte stable** (votre ICP, votre voix, votre offre) qu'il relit à chaque session plutôt que vous le retaper. C'est `brain/`.
2. **Des boucles explicites** avec des points d'arrêt où un humain valide. C'est `LOOP.md` dans chaque cellule.
3. **Des machines réutilisables** pour les tâches qui reviennent. C'est `skills/`.
4. **Une mémoire** qui transforme une correction en règle permanente. C'est `memory/`.

Le reste du repo existe pour que ces quatre choses restent séparées et lisibles. Le détail du raisonnement est dans [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Ce que ce kit n'est pas

- Ce n'est pas un agent autonome. Les boucles ont des **gates** : des points où le travail s'arrête tant qu'un humain n'a pas validé. C'est volontaire.
- Ce n'est pas une garantie de résultat. Les skills encodent une méthode, pas votre marché.
- Ce n'est pas prêt à l'emploi sans travail. Comptez une demi-journée pour remplir `brain/` correctement. C'est la demi-journée la plus rentable du kit.

## Licence

Kit fourni par l'**École Mantra** (Mediabros) à ses élèves. Utilisez-le, modifiez-le, adaptez-le à votre
entreprise sans restriction. Ne le revendez pas tel quel.

Les 15 skills marqués 🔧 ont été construits et durcis sur un compte réel, puis vidés de toute donnée
d'entreprise avant d'arriver ici. Ce qui reste, c'est la méthode et les pièges : les chiffres, les
identifiants et les noms sont à vous.

Le dépôt intègre aussi des skills publiés sous licences ouvertes par des tiers, dont les mentions
sont conservées dans [LICENSE](LICENSE).
