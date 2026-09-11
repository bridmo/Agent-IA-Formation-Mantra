# Référence — Rédaction RSA (voix de marque)

Règles de rédaction des Responsive Search Ads. Croiser systématiquement `brain/voice-tone.md`,
`brain/editorial-guide.md`, `brain/messaging.md` et `brain/offre.md`.

## Contraintes Google (dures — le writer les valide)

- **Titre ≤ 30 caractères**, **description ≤ 90 caractères** (espaces et accents comptent).
- RSA : **min 3 / max 15 titres**, **min 2 / max 4 descriptions** par ad group.
- Plus de titres/descriptions = meilleure « ad strength ». 6 titres / 2 desc = « Poor/Average ».
- Le writer (`google_ads_write.py build-adgroups`) refuse de pousser si une longueur dépasse — il liste les fautifs.

## Principe de structure (lié au Quality Score)

Chaque groupe serré a son annonce : **trois à quatre titres reprennent l'intention exacte du mot-clé**, puis des
titres « offre » communs à tous les groupes (durée, garantie, preuve, prix). C'est ce qui fait monter le score.

## voix de marque — à appliquer

- **Vouvoiement.** Ton praticien, expert accessible, motivant **sans hype**.
- **Preuves récurrentes à décliner selon votre offre :** durée, format, garantie, certification, nombre de clients,
  « Claude, ChatGPT & Gemini », « 20% de théorie, 80% de pratique », « Les méthodes du top 1% des startups françaises ».
- **Bénéfices concrets et chiffrés :** « Automatisez 50% de votre job », « Déployez vos assistants IA »,
  « Construisez de vrais agents », « Vibecoding ».
- **Faits produit uniquement depuis `brain/offre.md`.** Une certification ou un agrément est une **allégation
  réglementée** :
  ne jamais en inventer/mélanger. Confirmer lequel s'applique à l'offre.

## Anti-patterns (vécus, à ne pas refaire)

- ❌ **Vocabulaire de douleur brut.** « sans bricoler » vient du vocabulaire *que le prospect se dit à lui-même*
  (`voice-tone.md` liste « ne plus bricoler ») — ça ne se met **pas** tel quel dans une annonce, ça sonne négatif/cheap.
  Préférer une formulation positive (« 20% théorie, 80% pratique », « concret et actionnable »).
- ❌ Une seule annonce générique pour des intentions multiples (tue le QS).
- ❌ Hype / promesses de revenus garantis.
- ❌ Anglais quand un équivalent français courant existe.
- ❌ Un libellé d'offre inventé ou approximatif. Coller au nom exact de l'offre tel qu'il figure dans `brain/offre.md`.

## Process de validation (RÈGLE)

Le copy est une **décision de l'utilisateur (CEO/marque)**, pas la mienne. Avant tout `--execute` :
1. Afficher **l'intégralité du copy en clair** — titres ET descriptions, **ligne par ligne**, avec le compteur de
   caractères, par ad group.
2. Demander une **validation séparée du texte**, distincte du go/no-go d'exécution. Un « ok on pousse » sur la
   logistique ≠ approbation du copy. (Cf. `memory/feedback_ad_copy_validation.md`.)
3. Pour modifier une RSA déjà live : une RSA ne s'édite pas → on crée la corrigée + on retire l'ancienne
   (ou on supprime/recrée l'ad group si refonte large).

## Format de travail : le plan JSON

Le copy se formalise dans un plan (`channels/paid/google-ads/plans/ia-gen-plan.json`) : par ad group, `keywords` (texte + match type),
`headlines`, `descriptions`. Le writer le lit, valide les longueurs, et crée ad group + mots-clés + RSA de façon
atomique. Éditer le JSON puis re-dry-run.
