# Recherche SERP & PAA — le comment, selon tes outils

Ce skill a besoin de trois intrants réels avant de raisonner : l'**intention** (lire la SERP), les **questions PAA** (la carte de la demande), et **ce que fait le top 5** (pour trouver le vide). Voici comment les obtenir selon ce dont tu disposes. Le principe : **utilise le niveau le plus fiable accessible, et dégrade proprement** — sans jamais faire passer de la donnée inférée pour de la donnée mesurée.

## Détecte ton niveau d'accès

1. **MCP SEO connecté** (Ahrefs, DataForSEO, Semrush, Moz…) → niveau le plus riche : volumes, difficulté, questions, SERP structurée. Privilégie-le.
2. **Outil de recherche web** (WebSearch, navigateur headless, fetch) → tu peux lire la vraie SERP et la boîte PAA.
3. **Rien d'automatique** → mode manuel guidé : tu fais capturer la SERP par l'utilisateur, ou tu infères en le disant clairement.

---

## Niveau 1 — MCP SEO

Le plus déterministe. Selon le serveur connecté, vise ces données :

- **Questions / PAA** : la plupart des MCP SEO exposent un endpoint « questions » ou « matching terms » filtrable sur les formulations interrogatives (qui/quoi/comment/pourquoi/combien). C'est ta source de H2.
- **Volume & intention** : récupère le volume de recherche et, si disponible, le « parent topic » ou l'intention classée. Sers-t'en pour confirmer que la question centrale a une demande réelle.
- **SERP overview** : la liste des URL qui rankent + les features SERP (featured snippet, PAA, AI Overview présent ou non). Indispensable pour la Phase 0.2 (format dominant) et la Phase 1.2 (top 5).
- **Keywords du top 5** : les mots-clés sur lesquels rankent les pages concurrentes révèlent les sous-sujets qu'elles couvrent — et, en creux, ceux qu'elles ignorent (matière à edge).

> Note de portabilité : ne code pas en dur un nom de tool. Repère le MCP SEO disponible dans la session, lis sa doc si besoin, et mappe ses endpoints sur les trois intrants ci-dessus.

## Niveau 2 — Recherche web

Sans MCP SEO mais avec accès web :

1. **Lire la SERP** : recherche le mot-clé exact. Note les 10 premiers résultats, leur format (guide / réponse courte / comparatif / produit / vidéo), et la présence d'un AI Overview ou d'un featured snippet.
2. **Récupérer les PAA** : la boîte « Autres questions posées » apparaît dans les résultats. Liste-en 4 à 8. Astuce : déplier une question PAA en révèle souvent de nouvelles — tu peux élargir la carte.
3. **Recherches associées** : le bloc en bas de SERP complète les sous-intentions.
4. **Lire le top 5** : ouvre les 5 premières pages, relève leur plan (leurs H2) et repère ce qu'elles couvrent toutes vs ce qu'elles négligent toutes.

Croise toujours avec le bon sens : une question PAA hors-sujet par rapport à l'intention de ta page n'a pas à devenir un H2.

## Niveau 3 — Mode manuel guidé

Sans accès SERP automatique, deux options, à combiner :

**A. Faire capturer par l'utilisateur (préféré — c'est de la vraie donnée).** Demande-lui de :
- chercher le mot-clé sur Google (en navigation privée, dans la bonne langue/pays),
- te copier les titres des 5 premiers résultats,
- te copier les questions de la boîte « Autres questions posées »,
- te dire s'il voit un AI Overview ou un encadré de réponse en haut.

**B. Inférer, en le déclarant.** Si l'utilisateur ne peut/veut pas capturer, génère des questions candidates et une hypothèse d'intention **par raisonnement** — puis écris noir sur blanc : « Ces questions sont inférées, non vérifiées sur la SERP réelle ; à valider avant publication. » Ne maquille jamais de l'inféré en mesuré : c'est la règle d'honnêteté du skill, et c'est ce qui sépare un brief fiable d'un brief décoratif.

---

## Bonnes pratiques transverses

- **Langue & pays comptent.** La SERP de « facturation automatique » en français-France diffère de l'anglais-US. Aligne la recherche sur l'audience cible.
- **Filtre les PAA sur l'intention.** Toutes les questions PAA ne servent pas ta page. Garde celles qui prolongent la question centrale ; écarte les digressions.
- **Cherche le vide, pas seulement le plein.** L'analyse du top 5 sert autant à voir ce qui manque (matière à edge) qu'à connaître le socle attendu.
- **Une donnée par section dès la recherche.** Pendant que tu lis les sources, note les chiffres et leurs origines : tu en auras besoin en Phase 1.3 et au gate n°4.
