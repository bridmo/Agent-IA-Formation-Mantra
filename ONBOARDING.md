# Onboarding

Parcours en quatre étapes. Chacune se termine par quelque chose qui tourne. Ne sautez pas l'étape 1 : tout le reste en dépend.

Durée réaliste : une demi-journée pour les étapes 1 et 2, puis une semaine d'usage pour les étapes 3 et 4.

---

## Étape 0 : installer

```bash
npm install -g @anthropic-ai/claude-code
```

Puis dans le dossier du kit :

```bash
claude
```

Claude Code lit automatiquement `CLAUDE.md` à la racine au démarrage de chaque session. C'est le fichier qui lui dit où il est et comment travailler ici. Tout le reste du repo est atteignable depuis lui.

Vérifiez que ça marche : demandez `résume-moi comment ce repo est rangé`. S'il vous répond avec les cinq zones, la lecture du contexte fonctionne.

---

## Étape 1 : remplir le cerveau

**C'est l'étape qui détermine la qualité de tout ce que l'agent produira ensuite.** Un agent sans contexte produit du marketing générique, et vous passerez plus de temps à le corriger qu'à écrire vous-même.

Ouvrez `brain/` et remplissez dans cet ordre :

| Fichier | La question à laquelle il répond | Si vous le bâclez |
|---|---|---|
| `identite.md` | Qui êtes-vous, que vendez-vous, à quel prix | L'agent invente des chiffres |
| `icp.md` | À qui vous vendez, quels problèmes réels | Tout le copy tombe à côté |
| `voice-tone.md` | Comment vous parlez, ce que vous ne dites jamais | Ça sonne comme une IA |
| `offre.md` | Le détail de vos produits, prix, formats | L'agent promet ce que vous ne vendez pas |
| `personas.md` | Les 2 ou 3 profils qui achètent vraiment | Le messaging reste flou |
| `messaging.md` | Quel argument sur quel canal pour quel persona | Vous répétez le même angle partout |
| `competitors.md` | Contre qui vous êtes comparé, et sur quoi | Aucune différenciation |
| `design-system.md` | Vos couleurs, polices, règles visuelles | Chaque visuel est un nouveau style |

Deux conseils qui font la différence :

**Écrivez des faits, pas des intentions.** « Notre ICP est une PME de 10 à 50 personnes, le décideur est le dirigeant lui-même, le budget se décide en une réunion » est utile. « Nous visons l'excellence » ne sert à rien.

**Faites-vous aider.** Ouvrez `claude` et dites : `je vais remplir brain/icp.md. Pose-moi les questions une par une, et écris le fichier au fur et à mesure de mes réponses.` Vous répondez à l'oral, l'agent structure. C'est cinq fois plus rapide que la page blanche.

**Vérification de fin d'étape :** `relis brain/ et liste ce qu'un rédacteur externe ne pourrait toujours pas deviner sur nous`. Ce qu'il liste, c'est ce qui manque.

---

## Étape 2 : faire tourner une boucle

Une **boucle** est un enchaînement d'étapes qui revient, avec des points d'arrêt. Chaque cellule de `channels/` a la sienne dans son `LOOP.md`.

Exemple, la boucle SEO :

```
Déclencheur (chute de position, nouveau mot-clé)
  → Recherche (sous-agent isolé, données live)
  → Brief croisé avec l'ICP
  → GATE : vous validez le brief
  → Rédaction
  → GATE : vous validez l'article
  → Publication
  → Mesure à 30 et 60 jours
  → Ce qu'on a appris part en mémoire
```

Les **GATE** sont le cœur du système. Un agent qui publie sans validation est un risque, pas un gain de temps. Un agent qui s'arrête au bon endroit avec un livrable propre vous fait gagner la journée.

Choisissez la cellule qui correspond à votre chantier le plus pressant. Lisez son `CLAUDE.md` (le contexte local) et son `LOOP.md` (la boucle). Puis lancez :

```
lis channels/seo/CLAUDE.md et channels/seo/LOOP.md, et déroule la boucle pour <votre sujet>. Arrête-toi au premier gate.
```

**Vérification de fin d'étape :** l'agent s'est arrêté et vous demande de valider quelque chose. S'il est allé jusqu'au bout tout seul, votre `LOOP.md` n'a pas de gates assez explicites.

---

## Étape 3 : calibrer un skill

Un **skill** est une machine réutilisable : une méthode écrite une fois, rejouée à chaque fois. Il y en a 68 dans `skills/`.

51 sont génériques et marchent tels quels. 15 sont marqués `calibration: à faire` dans leur en-tête : ils portent une méthode éprouvée mais attendent vos chiffres et vos contraintes.

Ouvrez celui dont vous avez besoin, cherchez la section **Calibration** en haut, et remplissez-la. Exemple avec `skills/paid-ads/` : vos objectifs de CPA, vos mots-clés négatifs, vos conversions à suivre.

Pour en créer un nouveau, lisez [docs/SKILLS.md](docs/SKILLS.md). La règle courte : un skill vaut la peine d'être écrit à partir de la troisième fois que vous expliquez la même chose.

**Vérification de fin d'étape :** vous lancez le skill sans réexpliquer votre contexte, et le résultat est utilisable au premier jet.

---

## Étape 4 : brancher la mémoire

C'est ce qui sépare un agent qui stagne d'un agent qui s'améliore.

À chaque fois que vous corrigez l'agent sur quelque chose qui **se reproduira**, la correction doit devenir un fichier dans `memory/`. Sinon vous la retaperez la semaine prochaine.

En session, tapez simplement :

```
# ne jamais écrire de titre en majuscules dans nos emails, notre audience trouve ça agressif
```

Le `#` en début de message écrit la règle en mémoire. Vous pouvez aussi demander : `écris ça en mémoire avec le pourquoi`.

Le format et les quatre types de mémoire (`user`, `feedback`, `project`, `reference`) sont dans [docs/MEMOIRE.md](docs/MEMOIRE.md).

**Vérification de fin d'étape :** ouvrez une session neuve et demandez `qu'est-ce que tu as appris sur notre façon de travailler ?`. S'il cite vos corrections, la boucle est fermée.

---

## Après

Vous avez un agent qui connaît votre entreprise, qui suit des boucles avec des gates, et qui capitalise. À partir de là, le travail consiste à :

- ajouter une cellule quand un nouveau canal devient sérieux ;
- écrire un skill quand une tâche revient pour la troisième fois ;
- brancher une source de données déterministe (MCP) plutôt que laisser l'agent estimer, voir [docs/DONNEES.md](docs/DONNEES.md) ;
- relire `memory/MEMORY.md` une fois par mois et supprimer ce qui est devenu faux.

Et lire [docs/SECURITE.md](docs/SECURITE.md) **avant** votre premier `git push`, pas après.
