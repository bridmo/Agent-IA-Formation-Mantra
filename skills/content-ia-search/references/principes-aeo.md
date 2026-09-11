# Principes AEO / GEO — le pourquoi derrière chaque règle

À lire avant de rédiger si tu veux comprendre *pourquoi* le skill impose ce qu'il impose. Chaque règle de la checklist découle d'un mécanisme concret côté Google et côté moteurs de réponse (AI Overviews, ChatGPT search, Perplexity, Copilot). Comprendre le mécanisme te permet d'appliquer l'esprit de la règle, pas juste sa lettre.

## Table des matières
1. Le double jeu : ranker vs se faire citer
2. Extraction : pourquoi le bloc de réponse en tête
3. Retrieval par passage : pourquoi chaque section doit tenir seule
4. Gain d'information : pourquoi l'edge est un gate dur
5. PAA : pourquoi partir des vraies questions
6. Citabilité & EEAT : pourquoi une donnée sourcée par section
7. La valeur résiduelle : pourquoi réserver quelque chose au lecteur humain
8. Intention : pourquoi poser la question avant d'y répondre

---

## 1. Le double jeu : ranker vs se faire citer

Deux systèmes lisent la page, avec des logiques différentes mais des récompenses convergentes :

- **Le classement classique** (10 liens bleus + featured snippets) : Google évalue pertinence, autorité, expérience, et sert un lien sur lequel l'utilisateur clique.
- **Les moteurs de réponse** : ils ne servent pas un lien, ils **synthétisent une réponse** à partir de plusieurs sources et citent celles qu'ils ont utilisées. Le « trafic » devient une mention/citation, parfois un clic.

Optimiser pour l'un sans l'autre, c'est laisser la moitié de la visibilité sur la table. La bonne nouvelle : les deux récompensent les mêmes propriétés — réponse claire et extractible, structure modulaire, information unique et vérifiable. Ce skill optimise les deux à la fois.

## 2. Extraction : pourquoi le bloc de réponse en tête

Les moteurs de réponse extraient un passage concis et auto-suffisant, généralement situé **haut dans la page**, immédiatement après le titre ou la question. Si ta réponse est noyée après 400 mots d'introduction, elle ne sera ni extraite ni mise en snippet.

D'où la règle : **100-150 mots de réponse directe en tête, première phrase nette en ~40 mots.** La structure « pyramide inversée » (conclusion d'abord, détails ensuite) n'est pas un choix de style — c'est la forme que les extracteurs préfèrent. L'intro de mise en bouche (« Dans un monde où… ») n'aide aucun système et fait fuir le lecteur.

## 3. Retrieval par passage : pourquoi chaque section doit tenir seule

Google indexe et récupère au niveau du **passage**, pas seulement de la page entière. Les LLM, eux, découpent les sources en *chunks* qu'ils retrouvent et recomposent indépendamment. Conséquence : **une section peut être servie hors de son contexte.**

Si ta section 4 dit « comme nous l'avons vu plus haut, cette méthode… », elle est inutilisable isolément — l'extracteur ne « voit » pas le plus haut. D'où la règle : chaque H2 répond à sa question dès sa première phrase, redéfinit les termes nécessaires, et ne dépend pas des sections voisines. Pense « briques autonomes », pas « récit linéaire ».

## 4. Gain d'information : pourquoi l'edge est un gate dur

Google possède un brevet de « gain d'information » : à requête égale, un document qui apporte une information **nouvelle** par rapport à ce que l'utilisateur a déjà vu est valorisé. Les moteurs de réponse, eux, n'ont aucune raison de citer une source qui répète ce que trois autres disent déjà mieux — ils citent la source qui apporte l'élément unique.

Donc une page redondante perd sur les deux tableaux. L'**edge** (donnée originale, ICP spécifique, framework nommé, sous-sujet profond) est ce qui rend la page non substituable. C'est pour ça que c'est un gate dur : sans information nouvelle, le reste du travail est cosmétique.

## 5. PAA : pourquoi partir des vraies questions

La boîte « Autres questions posées » est générée par Google à partir des **requêtes réelles** qui gravitent autour du mot-clé. C'est une carte gratuite de la demande : les sous-intentions que les internautes expriment vraiment, et que les moteurs s'attendent à voir traitées.

Mapper chaque H2 sur une question PAA, c'est :
- couvrir les sous-intentions réelles (donc matcher plus de requêtes),
- devenir éligible aux featured snippets et à l'expansion « People also ask »,
- offrir aux moteurs de réponse des paires question→réponse propres, faciles à extraire.

Inventer des H2 « logiques » mais déconnectés des PAA, c'est répondre à des questions que personne ne pose.

## 6. Citabilité & EEAT : pourquoi une donnée sourcée par section

EEAT = Experience, Expertise, Authoritativeness, Trust. Les systèmes qualité de Google et les moteurs de réponse cherchent des signaux de fiabilité. Une **donnée concrète et attribuable** par section en est un puissant :
- elle donne au moteur quelque chose de précis à citer (on cite « 63 % selon l'étude X », pas « beaucoup d'entreprises »),
- elle prouve que l'auteur a fait le travail,
- elle ancre l'affirmation dans le vérifiable.

Une donnée first-party (ta propre mesure, ton propre cas) vaut mieux qu'une stat recopiée : elle est unique (gain d'information, cf. §4) ET prouve l'expérience (le « E » d'EEAT).

## 7. La valeur résiduelle : pourquoi réserver quelque chose au lecteur humain

Si l'intégralité de ta page tient dans le résumé que l'AI Overview affiche, l'utilisateur a sa réponse sans cliquer : zéro trafic, et à terme zéro raison d'exister pour la page. Le contenu qui survit à l'ère des moteurs de réponse garde une **valeur résiduelle** que la synthèse ne capture pas :
- un modèle / template réutilisable,
- un outil interactif ou un calcul,
- un arbre de décision,
- un retour d'expérience first-hand,
- une nuance de jugement, un arbitrage que seule une personne ayant fait le travail peut formuler.

C'est le gate n°5 de pré-publication. C'est aussi, paradoxalement, ce qui rend la page **plus** citable : les moteurs aiment pointer vers la source qui a l'actif que le résumé ne remplace pas.

## 8. Intention : pourquoi poser la question avant d'y répondre

Tout l'édifice repose sur une seule chose : avoir correctement identifié **la question que la personne pose vraiment** et **dans quel but**. Un bloc de réponse parfait à la mauvaise question ne rank pas. Une structure impeccable sur une intention mal lue ne convertit pas.

C'est pourquoi le skill force la Phase 0 (cadrage) avant tout : décoder l'intention sur preuve SERP, formuler une seule question centrale dans les mots du lecteur, et définir une personne précise. Écrire la réponse trop tôt, c'est répondre à la question qu'on imagine plutôt qu'à celle qui est posée — l'erreur la plus coûteuse et la plus fréquente.
