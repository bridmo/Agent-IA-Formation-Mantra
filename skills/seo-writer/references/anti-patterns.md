# Anti-patterns (references for seo-writer)

Source : SKILL.md section "Anti-Patterns" + [brain/editorial-guide.md](../../../brain/editorial-guide.md) §5.

**Source unique** : à jour ici ne pas dupliquer ailleurs.

## Voix & narration

- **Never use tutoiement.** voix de marque = VOUVOIEMENT (vous, votre, vos). "Tu as testé ChatGPT ?" = fail immédiat. Aucune exception, pas même FAQ ou CTA.
- **Le "nous" = moi (auteur) + vous (lecteur).** Jamais "nous l'équipe {{COMPANY}}" (institutionnel, n'intéresse pas le lecteur). Pour citer {{COMPANY}} : "chez {{COMPANY}}", "en formation {{COMPANY}}".
- **"Je" pour l'anecdote personnelle ou l'opinion tranchée** (vraiment vécu).
- **Never declare thesis explicitly.** La thèse se prouve par les choix éditoriaux. H2 "Ce qu'on croit", "Notre position", "Ma thèse", phrases "Nous pensons que...", encadrés "Notre conviction" = fail. Le lecteur doit pouvoir reformuler la thèse seul, sans qu'elle ait été écrite.

## Ouvertures d'intro

- **Never start with the promise itself.** "À la fin de cet article, vous saurez..." = fail. L'intro démarre par un élément concret (chiffre non-arrondi, fait, scène). La promesse arrive en phrase 2-3.
- **Never use generic opening.** "En 2026, l'IA transforme...", "Dans un monde où...", "De plus en plus de...", "De nos jours", "À l'heure actuelle" = fail immédiat.
- **Never use "tout le monde nous dit" trick.** "Tous les RH nous disent ça", "Tous les marketeurs qu'on forme nous disent..." = facilité. Remplacer par UN chiffre précis ou UN verbatim exact.
- **Never open with a rounded or vague number.** "55 362 €" > "55 000 €" > "55K" > "beaucoup". Un chiffre non-arrondi sonne vrai. "Beaucoup de marketeurs" = poubelle.
- **Never skip PPP/PAS structure.** PPP = **hook element** + preview outcome + proof {{COMPANY}} + preview structure. PAS = chiffre non-arrondi + agitate + solution avec proof. Les 4 étapes doivent être présentes dans l'ordre.
- **Never confuse preview outcome with preview structure.** Preview outcome = LE RÉSULTAT obtenu ("vous aurez un workflow qui ramène 2h à 20 min"). Preview structure = CE QUE L'ARTICLE COUVRE ("on va voir X, puis Y, enfin Z"). Ne pas substituer.

## Titres, H1, H2, slug

- **Never use descriptive verbs in titles/H1/H2.** "Comment faire", "Comment comprendre", "Découvrez", "Apprenez à" = mou. Remplacer par : automatiser, maîtriser, déployer, construire, décoder, doubler, scaler, orchestrer, industrialiser.
- **Never put the year in the slug.** On doit pouvoir refresh l'article sans changer l'URL. L'année peut être dans le title/H1 pour signal fraîcheur, JAMAIS dans le slug.
- **Never write vague H2s.** "Introduction", "Conclusion", "Pour aller plus loin", "Quelques mots sur", "Les différents aspects de X" = fail. Chaque H2 doit dire quelque chose d'utile lu isolément.
- **Never use superlatifs creux en H2.** "Qui changent tout", "qui tuent 80 %", "ultime", "incontournable". Un H2 est un teaser, pas une promo. Préférer "4 éléments indispensables" à "4 leviers qui changent tout".
- **Put the tool name first in a tool guide title.** "Le guide complet pour automatiser avec n8n" enterre le keyword. Default : nom d'outil en première position (Pattern A).
- **Avoid risky metaphors in titles.** "Transformer Claude en stagiaire", "ChatGPT comme votre collègue IA" = éviter. Rester concret ("créer un agent IA", "automatiser un workflow"). Métaphores OK dans le corps, pas dans le titre.
- **Avoid comparatifs vendeurs.** "Match honnête", "vrai comparatif sans langue de bois" = sonne forcé. Default "X vs Y" : neutre et direct.
- **Don't merge "fiche métier" and "devenir [métier]" in a single article.** Un article = un intent. 2 articles séparés dans le backlog.

## Meta description

- **Never write a descriptive meta.** La meta fait CLIQUER, elle ne résume pas. "Installer et configurer X pour Y : 5 cas d'usage" = fail (descriptif). "Déléguez Y à X : 3h/semaine récupérées" = OK.
- **Never stack multiple chiffres in meta.** "3h/semaine + 15 min setup + 200 alumnis" dilue le message. Un chiffre fort + 1 proof max.
- **Never copy the first line of the article into the meta.** Le lecteur ne doit pas lire deux fois la même phrase.
- **Never use "Découvrez", "Apprenez à", "Tout savoir sur" in meta.** Verbe d'action en tête : Déléguez, Automatisez, Divisez, Récupérez.

## Body / tournures

- **Never write corporate or AI-generic phrasing.** "Il est important de noter", "Dans le cadre de", "Afin de maximiser", "En outre / Par ailleurs / De surcroît / Néanmoins" = signature IA immédiate. Remplacer par "Et / Mais / Sauf que / Le truc, c'est que".
- **Never stack triplets like "rapide, efficace et performant".** Signature IA générique. Un adjectif précis > trois adjectifs vagues.
- **Never use em dashes `—` more than once per article.** Signature IA la plus évidente. Remplacer par virgules, points, parenthèses.
- **Never use adverbes de remplissage.** "Véritablement, réellement, particulièrement" → inutiles 95 % du temps.
- **Never write walls of text.** Paragraphes 1-3 phrases max. Sauts de ligne fréquents. Bullets, tables, numbered lists, bold.
- **Never affirm without evidence.** Toute affirmation importante doit suivre chiffre vérifiable → conséquence logique → effet observable pour le lecteur. Pas de "on sait que", "il est évident que", "tout le monde dit".
- **Never over-dramatize factual claims.** "Premier X au monde", "révolutionne tout", "sans précédent", ou un mot rare quand un mot simple marche = sur-dramatisation. Une description simple et juste bat une description hyperbolique. Ex : *"le règlement européen dédié à l'IA"* > *"le premier règlement horizontal au monde dédié à l'intelligence artificielle"*.
- **Avoid niche professional jargon.** Les termes d'une spécialité (journalistique, juridique, tech dev) peuvent être opaques pour le lecteur marketeur. Préférer des formulations accessibles. Ex : *"byline"* → *"processus éditorial"*, *"retainer"* → *"mission récurrente"*, *"SLA"* → *"engagement de service"*. Les termes marketing standard (A/B test, funnel, CRO, growth, lead) passent.

## ICP & pains

- **Never write without checking ICP anchoring.** Tout article connecte à un pain documenté dans `brain/icp.md`. Pas d'anchoring = contenu générique qui ne convertit pas.
- **Never cite pain verbatims in the article.** Les pains sont un **input éditorial** pour choisir les thématiques, pas un élément à montrer au lecteur. Pas de blockquote "Pain terrain", pas d'étiquette "Voici un pain que vous vivez".
- **Never mix pain universes.** Article IA = pains IA (chaos outils, peur de l'obsolescence). Article growth = pains opérationnels. Pas de cross-pollination forcée.

## Produit & chiffres

- **Never invent product numbers.** Durée formation, prix, intitulés, stats alumnis → vient d'un fichier source (`brain/offre.md`, `brain/product-marketing-context.md`) ou d'une info explicitement fournie. Sinon ne pas écrire.
- **Never round or approximate product data.** `formations.md` a les durées et prix exacts. Pas d'arrondissage.
- **Never fix model versions.** "Utilisez Opus 4.7 pour X, Sonnet 4.6 sinon" = à éviter. Préférer "le modèle le plus puissant de votre plan" ou rester silencieux. Exception : articles dédiés à une version (launch, benchmark).
- **Prefer "agents IA" over "assistants IA" in 2026.** Vocabulaire du moment. "Assistants" sonne déjà daté.

## CTA & liens

- **Never force a product mention.** Si le CTA sonne forcé, le subtiliser ou le déplacer. Un CTA forcé coûte plus en crédibilité qu'un CTA manquant.
- **Never link to deprecated free courses.** Pas de liens vers cours gratuits (Growth 101 etc.) datés. Seuls liens {{COMPANY}} acceptables : LP formations payantes + articles de blog du cluster.
- **Never use "click here" anchors.** Anchors descriptifs obligatoires : "notre comparatif n8n vs Make", "guide ChatGPT prompts".

## Thèse & argumentation

- **Never write an article without a thesis.** Article sans thèse = guide neutre = commodity. Chaque article a une thèse documentée dans le brief (Step 1bis), même si elle ne sera jamais écrite.
- **Never declare thesis explicitly.** Voir section "Voix & narration" — la thèse se prouve par les choix éditoriaux.

## Divers

- **Never skip the competitive tear-down.** On ne peut pas écrire du 10x content sans savoir ce qu'est le 1x actuel.
- **Never invent quotes or data.** Verbatims → `brain/icp.md` ou source explicite. Stats → sourcées ou clairement marquées "data interne {{COMPANY}}".
