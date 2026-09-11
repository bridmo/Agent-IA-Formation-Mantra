# Le format canonique du document de direction

Le format convergé sur la Stratégie H2 2026 (référence vivante : l'artefact « Stratégie H2 2026 »). Huit sections, dans cet ordre. Chaque section attaque sur son contenu (tableau ou liste), pas sur un chapô descriptif.

## Ossature

1. **Titre + intro (2 paragraphes max).** L'objectif chiffré en gras dès la première phrase, comparé à une base. Le sujet du semestre surligné. Second paragraphe : le socle non négociable (conformité) s'il existe. Sommaire vertical numéroté.
2. **Où nous en sommes.** Un tableau : indicateur / période courante / même période N-1 / lecture. Uniquement des indicateurs qui ont une vraie comparaison. Puis « ce qui a marché » / « ce qui n'a pas marché » en listes courtes, chiffrées.
3. **Le détail des chiffres.** La base tendancielle (comment on l'estime, prudemment). Le bridge : base + chaque ligne de nouveauté (mécanique, montant, owner) = objectif. La trajectoire mensuelle en tuiles.
4. **Axes de développement.** Un bloc par axe : titre qui ouvre sur un fait ou un chiffre, owner en pastille + soutiens, contribution chiffrée, puis les champs mécanique / métrique / gate (date + critère) / contre-mesure.
5. **Ce qu'on ne fait pas.** La liste qui protège l'équipe des demandes de dernière minute. Une raison par ligne.
6. **Budget.** Tableau média (poste / aujourd'hui / cible / condition) + tableau équipe. Une règle d'arbitrage chiffrée (seuil de marge par canal). Distinguer budget de performance (jugé au ratio) et budget d'apprentissage (jugé aux questions tranchées).
7. **Tableau de bord.** Six nombres, pas douze. Un par axe + le résultat. Colonne « qui ». Aujourd'hui vers cible.
8. **Risques + RH.** Risque / signal d'alerte chiffré / ce qu'on fait ce jour-là. Un risque est parable ; une incertitude de chiffrage n'est pas un risque. RH : chaque poste avec ce qu'il débloque.

## Règles de rédaction

- **Chaque phrase a un objectif.** Test : vraie ? apporte une info absente du tableau ? descriptive ? Si descriptive ou redondante, couper.
- **Pas de chapô décoratif.** Une section commence par son titre puis son tableau. Un chapô ne survit que s'il porte une règle d'arbitrage ou un chiffre.
- **Le chiffre porte l'insistance**, pas l'adverbe. Bannir « sans que ce soit négociable », « de très loin », « mort et enterré ».
- **Zéro cadratin**, nulle part, y compris dans les tableaux.
- **Owner + date + contre-mesure** sur chaque axe. Sans les trois, c'est une intention.
- Les remarques de lecture (« le vrai goulot », « sain ») sont du commentaire : les couper des tableaux.

## Design

Direction artistique : celle de `brain/design-system.md`. Thème clair et sombre gérés. Les tableaux défilent dans leur propre cadre sur mobile, le corps de page ne défile jamais horizontalement. Publier en artefact, et pousser dans votre outil de documentation si vous en avez un.

## Vérification avant livraison

- Repasser chaque phrase au test ci-dessus.
- Revérifier chaque chiffre contre son pull (jamais de chiffre de mémoire).
- Contrôler que le bridge boucle et que la trajectoire somme à l'objectif.
- Contrôler la cohérence des owners entre bridge, axes et tableau de bord.
- Relecture visuelle avant remise ; si le pane navigateur blanchit au scroll, valider par lecture DOM et le dire.
