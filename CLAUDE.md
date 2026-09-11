# {{COMPANY}} — contexte agent

Fichier racine, chargé automatiquement à chaque session Claude Code. Il dit où sont les choses et comment on travaille ici. Il ne duplique jamais le contenu des autres fichiers : il pointe vers eux.

> **À remplir.** Cherchez les `{{PLACEHOLDER}}` et remplacez-les. Supprimez ce bloc quand c'est fait.

**Projet :** {{COMPANY}}, {{ONE_LINER}}.
**Site :** {{DOMAIN}}
**Utilisateur :** {{OWNER}}, {{ROLE}}. Langue de travail : {{LANGUE}}.

Contexte produit portable (identité, ICP résumé, stack) : [AGENTS.md](AGENTS.md).

## Carte du repo

| Zone | Rôle |
|---|---|
| `brain/` | Sources de vérité : identité, ICP, voix, offre, concurrents, design |
| `channels/<cellule>/` | Cellules de travail : chacune a son `CLAUDE.md` (contexte local + pièges) et son `LOOP.md` (la boucle) |
| `skills/` | Machines réutilisables, index dans `skills/README.md` |
| `memory/` | Ce que l'agent a appris de vos corrections |
| `tools/` | Clients d'API et fiches d'intégration |
| `docs/` | Comment ce repo fonctionne : architecture, boucles, skills, mémoire, sécurité |
| `.scratch/` | Jetable, non versionné |

**Règle des cellules :** avant de travailler dans une cellule, lire son `CLAUDE.md` local, puis suivre sa boucle. Plan avant exécution, gate humain aux points de bascule.

## Sources de vérité

| Besoin | Fichier |
|---|---|
| Identité, positionnement | [brain/identite.md](brain/identite.md) |
| Offre, prix, formats | [brain/offre.md](brain/offre.md) |
| ICP | [brain/icp.md](brain/icp.md) |
| Personas | [brain/personas.md](brain/personas.md) |
| Messaging par canal | [brain/messaging.md](brain/messaging.md) |
| Voix et ton | [brain/voice-tone.md](brain/voice-tone.md) |
| Guide rédactionnel | [brain/editorial-guide.md](brain/editorial-guide.md) |
| Design system | [brain/design-system.md](brain/design-system.md) |
| Concurrents | [brain/competitors.md](brain/competitors.md) |

## Règles transverses

1. **Langue : {{LANGUE}}** pour tout contenu produit.
2. **Vérifier `brain/offre.md`** avant toute affirmation produit. Ne jamais inventer un prix, une durée, une statistique.
3. **ICP d'abord :** toute recommandation se croise avec l'ICP avant d'être proposée.
4. **Objectif d'abord :** toute action se valide contre un objectif mesurable. Si l'objectif n'est pas clair, le demander avant d'agir.
5. **Voix :** appliquer `brain/voice-tone.md` sans exception.
6. **Modifications chirurgicales :** ne changer que ce qui est demandé. Si vous repérez un problème ailleurs, le signaler sans le corriger de vous-même.

## Choisir la bonne couche : déterministe ou jugement

Avant d'estimer ou d'inférer, vérifier s'il existe une **donnée déterministe** accessible :

| Question | Source déterministe |
|---|---|
| Positions, volumes, backlinks | {{OUTIL_SEO}} (MCP) |
| Comportement des visiteurs | {{OUTIL_ANALYTICS}} (MCP) |
| Pipeline, contacts, deals | {{CRM}} (MCP) |
| Prix, durées, contenus produit | `brain/offre.md` |

**Déterministe** = calcul, lookup, exécution. On ne laisse pas le modèle deviner.
**Jugement** = synthèse, arbitrage, rédaction. Ce n'est pas un substitut à la donnée.

## Sous-agents : contrainte importante

Un sous-agent ne voit **pas** automatiquement ce fichier ni `AGENTS.md`. Il ne voit que le skill qu'on lui donne. Pour toute tâche qui demande la voix, l'ICP ou l'offre, le skill doit **référencer explicitement** les fichiers de `brain/` dans ses instructions.

## Mémoire

Index chargé à chaque session : [memory/MEMORY.md](memory/MEMORY.md).

Quand une correction se reproduira, elle devient un fichier dans `memory/` plus une ligne dans l'index. Format et types : [docs/MEMOIRE.md](docs/MEMOIRE.md).

## Skills actifs

Les skills découvrables sont ceux liés dans `.claude/skills/`. Index complet : [skills/README.md](skills/README.md).

| Quand l'utilisateur dit | Skill |
|---|---|
| {{« optimise la page », « ça convertit mal »}} | `page-cro` |
| {{« rédige un article », « brief SEO »}} | `seo-writer`, `seo-strategy` |
| {{« les campagnes », « le CPA »}} | `paid-ads` |
| {{« écris la stratégie », « challenge le plan »}} | `marketing-strategy` |

Complétez ce tableau avec vos propres déclencheurs : c'est lui qui évite de chercher le bon skill à chaque fois.

## Anti-patterns

- Inventer un chiffre produit au lieu d'ouvrir `brain/offre.md`
- Parler produit sans avoir croisé l'ICP
- Produire un livrable sans objectif mesurable associé
- Supprimer ou déplacer des fichiers de `brain/` sans validation
- Dupliquer dans ce fichier le contenu de `brain/` : toujours pointer
