# Frameworks GTM, calibrés {{COMPANY}}

## 1. Sizing d'opportunité (la question qui tue)

Deux sources déterministes, jamais l'intuition :
- **Recherche** : volume + tendance 24 mois sur Ahrefs. Un volume qui monte vaut mieux qu'un gros volume qui s'effondre (mémoire `feedback_keyword_momentum`).
- **Entrées financement public réelles** : données publiques du marché, par certif, OF et mois (mémoire `project_donnees_marche`). Le seul chiffre qui dit si des gens achètent vraiment cette formation, pas seulement s'ils la cherchent.

Verdict : **marché prouvé** (demande + achats réels), **à tester petit** (demande sans preuve d'achat), **inexistant** (ni l'un ni l'autre : on ne lance pas).

## 2. Scoring ICP (A/B/C/D)

On part des personas de l'`icp-bible`, on ne réinvente pas. Grille pour qualifier un segment cible :
- **A** : dans l'ICP, financement (aide publique, OPCO, employeur) disponible, intention haute, closing prouvé.
- **B** : dans l'ICP, financement à monter, intention moyenne.
- **C** : adjacent à l'ICP, financement incertain.
- **D** : hors ICP, on ne cible pas.

Un lancement se juge à la part de A/B qu'il touche, pas au volume brut.

## 3. Positionnement, April Dunford

Énoncé en une phrase, dans la voix de marque (pas de jargon) :
> Pour [segment ICP] qui [situation/besoin], [offre {{COMPANY}}] est [catégorie] qui [bénéfice différenciant], contrairement à [alternative réelle].

Tester l'énoncé sur trois questions : est-ce vrai ? est-ce défendable face au concurrent réel ? un prospect le comprend-il sans glossaire ?

## 4. Battlecard

Par concurrent réellement présent sur la requête ou dans les appels (DataBird, Lion, École Cube ; France Travail comme adversaire du financement, mémoire `project_icp_corpus`) :
- Sa force perçue (ce que le prospect cite).
- Sa faille réelle (prix, format, certif, accompagnement).
- Notre angle : le bénéfice {{COMPANY}} qui répond à la faille, chiffré si possible.
- Ne jamais linker un concurrent sans nofollow.

## 5. Grille de motion GTM

Choisir la motion d'entrée selon ce qui convertit chez {{COMPANY}}, pas selon la théorie. Les valeurs chiffrées périment : les prendre dans les mémoires citées, pas ici.

| Motion | Quand elle est la bonne | Coût de lecture | Où est la valeur courante |
|---|---|---|---|
| Inbound / SEO | Demande de recherche prouvée, intention haute | Lent (mois), meilleur CA par SQL | `project_economie_canaux` |
| Marketplace Maformation | Certif éligible, requête générique captée | Rapide | `project_funnel_partenaire` |
| Paid Google | Intention haute, ratio CA/spend au-dessus du seuil de marge | Rapide, cher | `reference_quality_score`, `project_google_ads` |
| Paid Social / Meta | Besoin de volume, création d'intention | Moyen, à tester par point d'entrée | `project_meta_ads` |
| Outbound B2B | Cible entreprise identifiée, panier élevé | Lent, humain | `project_strategie` |
| Webinaire | Sujet à démontrer, base à réchauffer | Rapide, show-up stable | `project_webinarjam` |

Règle : tester d'abord la motion la moins chère à lire pour ce segment ; scaler seulement après un signal chiffré.
