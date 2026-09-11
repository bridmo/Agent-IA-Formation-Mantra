---
name: content-ia-search
description: >-
  Transforme un mot-clé en brief de contenu puis en article optimisés pour le
  search à l'ère de l'IA — pensés pour ranker sur Google ET se faire citer par
  les AI Overviews, ChatGPT et Perplexity. Le skill commence TOUJOURS par poser
  et comprendre la question centrale et l'intention de recherche avant d'écrire
  la moindre ligne. Couvre : analyse d'intention, recherche des questions
  "People Also Ask" (PAA), bloc de réponse AEO, structure en H2 autonomes,
  recherche de l'angle différenciant (the edge), brief structuré, rédaction de
  l'article, et checklist de pré-publication à 5 gates. À utiliser dès que
  l'utilisateur veut un brief SEO, un brief de contenu, rédiger ou optimiser un
  article, produire du contenu AEO / GEO, du contenu cité par l'IA, parle d'AI
  Overviews, d'answer engine optimization, ou demande comment ranker et se faire
  citer. Déclencher même quand l'utilisateur dit simplement "écris un article
  sur X" ou "fais-moi un brief sur le mot-clé Y" — le skill apporte le cadrage
  et le raisonnement qui manquent à une rédaction directe.
---

# Content IA Search — brief & article pour le search à l'ère de l'IA

## Ce que ce skill produit, et pourquoi il existe

Deux livrables, dans cet ordre :

1. **Un brief** — la réflexion structurée qui décide *quoi* dire, *à qui*, et *en quoi cette page est unique*.
2. **L'article** — l'exécution du brief.

On peut s'arrêter au brief (livrable autonome) ou enchaîner sur l'article.

L'objectif n'est pas seulement de plaire à l'algorithme Google classique. C'est de produire une page qui réussit deux épreuves simultanées :

- **Ranker sur Google** (résultats classiques + featured snippets).
- **Se faire citer par les moteurs de réponse** — AI Overviews de Google, ChatGPT search, Perplexity, Copilot — qui extraient, recomposent et citent des passages plutôt que d'envoyer un clic.

Ces deux épreuves récompensent les mêmes choses : une réponse directe en tête, des sections autonomes et citables, une donnée vérifiable par idée, et **une information que personne d'autre n'a**. Le détail du *pourquoi* est dans `references/principes-aeo.md` — à lire si tu veux comprendre la mécanique d'extraction et de citation avant de rédiger.

## Principe directeur : comprendre avant de produire

La plus grosse erreur en rédaction de contenu, c'est d'écrire la réponse avant d'avoir compris la question. Ce skill l'interdit structurellement.

Chaque phase a un **gate** : une condition à remplir avant de passer à la suite. Si le gate n'est pas franchi, on ne produit pas — on retourne chercher l'information manquante. Un brief bâclé produit un article bâclé ; le coût d'un aller-retour de cadrage est dérisoire comparé à celui d'un article qui ne rank ni ne se fait citer.

Ne saute jamais une phase, même quand l'utilisateur fournit déjà le mot-clé et semble pressé. Le cadrage prend quelques minutes ; il décide de tout le reste.

---

## PHASE 0 — Cadrage : poser et comprendre la question

**But : ne pas écrire de réponse tant qu'on ne maîtrise pas la question et l'intention.**

C'est la phase la plus importante et la plus négligée. Travaille-la sérieusement.

### 0.1 — Récupérer le point de départ

Il te faut au minimum :
- **Le mot-clé / sujet** visé.
- **L'objectif business** de la page (générer des leads ? éduquer ? convertir vers un produit ? construire de l'autorité ?). Si l'utilisateur ne l'a pas donné, **demande-le** — un contenu sans objectif mesurable est ingérable.

### 0.2 — Décoder l'intention de recherche

Avant de formuler quoi que ce soit, comprends ce que la personne qui tape ce mot-clé veut *vraiment*. Regarde la SERP réelle (voir `references/recherche-serp-paa.md` pour les méthodes selon tes outils disponibles) et tranche :

- **Intention** : informationnelle / commerciale / transactionnelle / navigationnelle ?
- **Format dominant** dans le top 10 : guide long ? réponse courte ? comparatif ? page produit ? vidéo ? Le format qui rank te dit le format attendu.
- **Niveau de la personne** : débutante qui découvre, ou experte qui compare des détails ?

Si la SERP ne correspond pas au format que l'utilisateur imaginait, **signale-le maintenant**. Écrire un guide de 2000 mots sur un mot-clé où Google ne sert que des réponses courtes, c'est se condamner d'avance.

### 0.3 — Formuler LA question centrale

Une page = une question principale. Pas trois.

1. Liste 2 à 4 formulations candidates de la question, **dans les mots de la personne qui cherche** (pas dans le jargon métier).
2. Choisis la plus juste : celle qui colle à l'intention décodée en 0.2.
3. Reformule-la explicitement et **confirme-la avec l'utilisateur** avant d'avancer. Cette question pilotera le bloc de réponse, le titre, et le premier gate de pré-publication.

> Exemple : mot-clé « automatisation facturation ». Question candidate trop large : « Qu'est-ce que l'automatisation de la facturation ? ». Question juste, alignée sur une intention commerciale : « Comment automatiser ma facturation sans changer d'outil comptable ? ».

### 0.4 — Définir le lecteur précis

« Tout le monde » n'est pas un lecteur. Décris **une personne** :
- Qui est-elle ? (rôle, situation, niveau)
- Que sait-elle déjà ? (pour ne pas la prendre de haut ni survoler)
- Quelle décision ou action essaie-t-elle de prendre après avoir lu ?

Cette personne détermine le vocabulaire, le niveau de preuve attendu, et le CTA.

**🚦 Gate 0 :** tu as (a) l'intention décodée sur preuve SERP, (b) une seule question centrale confirmée, (c) un lecteur précis. Sinon, ne passe pas à la recherche.

---

## PHASE 1 — Recherche : rassembler les intrants déterministes

**But : ne pas inventer ce qui se mesure.**

La structure et la crédibilité de la page reposent sur des données réelles, pas sur de l'intuition. Avant de raisonner sur l'angle, va chercher :

### 1.1 — Les questions People Also Ask (PAA)

La boîte « Autres questions posées » de Google est la carte, dressée par Google lui-même, des sous-questions qui gravitent autour du mot-clé. Chacune deviendra un H2.

Récupère les **vraies** questions PAA — la méthode dépend de tes outils, et **se dégrade proprement** :
- **Tu as un MCP SEO** (Ahrefs, DataForSEO, Semrush…) ou un outil de recherche web → utilise-le pour extraire PAA + questions liées.
- **Tu n'as qu'un navigateur / l'utilisateur** → guide-le pour capturer la boîte PAA et les « recherches associées » manuellement.
- **Aucun accès SERP** → génère des questions candidates par raisonnement, mais **dis explicitement à l'utilisateur qu'elles sont inférées, non vérifiées**, et recommande de les valider.

Détails et requêtes prêtes à l'emploi : `references/recherche-serp-paa.md`.

### 1.2 — Ce que fait le top 5

Lis (ou fais lire) les 5 premiers résultats. Note ce qu'ils couvrent **tous** — c'est le socle attendu — et surtout ce qu'ils **négligent tous**. Ce vide est la matière première de l'edge (Phase 2).

### 1.3 — Une donnée citable par section pressentie

Pour chaque H2 envisagé, identifie au moins une donnée concrète et attribuable : statistique sourcée, résultat d'étude, donnée first-party, exemple chiffré. Une affirmation vague ne se fait pas citer ; un chiffre avec sa source, oui.

**🚦 Gate 1 :** tu as une liste de questions PAA (vérifiées ou explicitement marquées comme inférées), une lecture du top 5, et au moins un candidat de donnée par section. Sinon, complète avant d'avancer.

---

## PHASE 2 — The Edge : trouver l'angle que personne n'a

**But : garantir un gain d'information. Sans edge, la page est redondante — ni rankée, ni citée.**

Les moteurs classiques (gain d'information) comme les moteurs de réponse (synthèse) pénalisent le contenu qui ne fait que répéter ce qui existe déjà. Si ta page dit la même chose que les cinq premières, elle n'a aucune raison d'exister.

À partir du vide repéré en 1.2, choisis **un** angle différenciant :

- **Donnée originale** — une stat, un benchmark, un sondage, un retour d'expérience chiffré que tu es seul à avoir.
- **ICP spécifique** — la réponse vue depuis un profil précis que les pages génériques ignorent.
- **Framework nommé** — une méthode structurée et baptisée, mémorisable et citable.
- **Sous-sujet plus profond** — descendre d'un cran là où les autres restent en surface.

Formule l'edge en une phrase : **« Cette page fait ___ que personne d'autre ne fait. »**

**🚦 Gate 2 (gate dur) :** si tu ne peux pas compléter cette phrase honnêtement, **le brief n'est pas prêt**. Ne passe pas à la rédaction. Retourne chercher de la donnée, interroge l'utilisateur sur son expérience terrain, ou resserre l'angle. Un edge bidon (« on est plus complets ») n'en est pas un.

---

## PHASE 3 — Le brief

**But : figer la réflexion dans un document que l'on peut exécuter — ou remettre tel quel.**

Remplis le template `assets/template-brief.md`. Champs obligatoires :

| Champ | Contenu |
|---|---|
| **Mot-clé** | Le mot-clé visé |
| **Intention** | Type d'intention + format dominant constaté en SERP |
| **Question centrale** | La question confirmée en 0.3, dans les mots du lecteur |
| **Lecteur** | La personne précise définie en 0.4 |
| **Bloc de réponse AEO** | La vraie réponse de 100-150 mots (voir Phase 4.1), rédigée dès le brief |
| **Carte des H2** | Chaque H2 ← une question PAA. Chaque H2 doit pouvoir se lire seul |
| **Edge** | La phrase « cette page fait ___ que personne n'a » |
| **Donnée par section** | Le point de donnée citable assigné à chaque H2 |
| **CTA** | UNE seule action attendue du lecteur |
| **Signal EEAT** | La preuve d'expérience/expertise : citation, donnée first-party, méthode, exemple vécu |

Le bloc de réponse AEO se rédige **dès le brief**, pas plus tard : c'est le cœur de la page, et l'écrire tôt valide qu'on a vraiment compris la question (Phase 0). S'il sonne creux, c'est que le cadrage est à revoir.

**Point d'arrêt :** présente le brief à l'utilisateur. S'il ne veut que le brief, on s'arrête ici. Sinon, on enchaîne — après son feu vert.

---

## PHASE 4 — Rédaction de l'article

**But : exécuter le brief sans le trahir.** Ne réinvente pas l'angle au moment d'écrire ; le brief a déjà tranché.

### 4.1 — Le bloc de réponse (en tête de page)

Juste sous le titre, avant toute introduction :
- **100 à 150 mots**, réponse directe à la question centrale.
- **Aucune intro, aucun délayage** (« Dans cet article, nous allons voir… » est interdit).
- Première phrase = réponse nette en ~40 mots (la portion la plus extractible), puis nuance/précision sur les ~100 mots suivants.

C'est ce bloc que les AI Overviews extraient. Il doit se suffire à lui-même.

### 4.2 — Les sections (H2)

- **Un H2 = une question PAA.** Le H2 peut être la question elle-même ou sa reformulation claire.
- **Chaque section se lit seule.** Les moteurs récupèrent des passages isolés : pas de « comme vu plus haut », redéfinis les termes au besoin, chaque section répond à sa question dès sa première phrase.
- **Une donnée citable par section** (celle assignée dans le brief), avec sa source.
- **Réserve de la valeur humaine.** Si toute la section tient dans le résumé de l'IA, le lecteur n'a aucune raison de cliquer. Garde quelque chose que le résumé ne peut pas remplacer : un exemple travaillé, un modèle réutilisable, un arbre de décision, un retour d'expérience, une nuance de jugement.

### 4.3 — La clôture

- **Un seul CTA**, l'action définie dans le brief. Pas trois.
- Le **signal EEAT** doit être visible : qui parle, sur quelle expérience, avec quelle preuve.

Pour le ton, les tournures et les anti-patterns rédactionnels, applique les consignes éditoriales du contexte dans lequel le skill tourne s'il en existe ; sinon, écris clair, direct, sans remplissage.

---

## PHASE 5 — Check de pré-publication (gate réel)

**But : refuser de déclarer l'article « terminé » s'il échoue à une seule épreuve.**

Passe les 5 questions une par une, **honnêtement**. Ce n'est pas une formalité : c'est le moment où l'on attrape les défauts avant qu'ils ne coûtent du trafic. Pour chaque gate, cite la preuve dans le texte (pas un simple « oui »).

1. **Le bloc de réponse de 150 mots répond-il directement à la question centrale ?** (pas de tour de chauffe, pas de hors-sujet)
2. **Chaque H2 mappe-t-il une vraie question PAA ?** (sinon : soit la question existe et le H2 doit s'y aligner, soit le H2 ne sert pas l'intention)
3. **Chaque section tient-elle seule ?** (lue isolément, hors contexte, elle répond toujours)
4. **Y a-t-il une donnée citée par section ?** (chiffre + source ou donnée first-party)
5. **Le lecteur humain obtient-il quelque chose que le résumé IA ne donne pas ?** (sinon, la page ne mérite pas le clic)

**🚦 Gate 5 :** **tout doit être OUI.** Un seul NON → corrige avant de publier. Ne maquille pas un NON en OUI ; remonte le problème à l'utilisateur avec ce qu'il faut corriger.

---

## Posture d'exécution

- **Interactif par défaut.** Confirme la question centrale (0.3), présente l'edge (Phase 2) et le brief (Phase 3) avant de rédiger. Ce sont les points où une erreur coûte cher.
- **Honnête sur les intrants.** Distingue toujours donnée vérifiée et donnée inférée. Ne présente jamais des questions PAA inventées comme réelles.
- **Adaptatif sur les outils.** Le skill marche avec un MCP SEO, avec une simple recherche web, ou en mode manuel guidé. Détecte ce dont tu disposes et dégrade proprement (voir `references/recherche-serp-paa.md`).
- **Lis les références au bon moment.** `references/principes-aeo.md` pour le *pourquoi* (mécanique d'extraction/citation, gain d'information, retrieval par passage). `references/recherche-serp-paa.md` pour le *comment* de la recherche SERP/PAA selon tes outils. `assets/template-brief.md` pour la sortie. `assets/exemple-complet.md` pour voir une cible concrète (brief rempli + extrait d'article).
