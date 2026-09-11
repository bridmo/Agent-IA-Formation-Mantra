---
name: design-brand
description: >
  Doctrine graphisme et design de VOTRE marque, toutes surfaces. À charger AVANT de produire ou
  retoucher un visuel : page web, création publicitaire, schéma, email, visuel de contenu.
  Route vers la source de vérité de chaque surface (ne jamais improviser une couleur ou un style),
  impose les règles transverses et le processus de validation. Déclencher quand l'utilisateur dit
  "design", "graphisme", "direction artistique", "premium", "la couleur ne va pas", "bouton",
  "charte", "ça ne fait pas nous".
---

# Design de marque : doctrine toutes surfaces

**Socle générique : charger AUSSI `skills/design/`** (principes, philosophies, workflow de variations).
Ce fichier-ci est la **calibration de votre marque** par-dessus. En cas de conflit, votre charte gagne.
Exemple : si le socle déconseille une police très répandue mais que c'est votre police de marque, votre
charte l'emporte.

## Calibration (à faire avant le premier usage)

Ce skill ne sert à rien tant que le tableau ci-dessous est vide. Remplissez-le, puis remplissez
`brain/design-system.md`.

**Votre boussole**, en une phrase : `{{À quoi doit ressembler votre marque, formulé comme un curseur entre
deux références que vous connaissez. Exemple : « la chaleur de X avec la rigueur de Y ». }}`

**La référence du bon niveau :** `{{Le produit ou la page qui, chez vous, fait déjà autorité.}}`

## Étape 0 : identifier la surface, charger SA source de vérité

Chaque surface a sa charte. On ne mélange jamais les registres : les règles d'un visuel social ne
s'appliquent pas à un schéma pédagogique, et inversement.

| Surface | Source de vérité | Registre |
|---|---|---|
| Pages web | `brain/design-system.md` | {{polices, couleurs d'action, espacements}} |
| Créations publicitaires | `skills/meta-ad-remix/references/design-rules.md` | {{fonds, accent unique, zones mortes}} |
| Schémas et illustrations | `brain/design-system.md` | {{fond, traits, un seul accent}} |
| Emails | {{votre gabarit}} | {{largeur d'image, clients à supporter}} |
| Produit / application | {{votre design system produit}} | {{jetons, composants}} |

## Règles transverses (valables quelle que soit la charte)

1. **Retirer avant d'ajouter.** On prend la mécanique d'une référence, jamais son esthétique.
   L'accumulation de gadgets fait enfantin, le dépouillement total fait vide. La cible : chaque
   élément de la palette présent, chacun dans un rôle clair.
2. **Un seul accent par visuel.** Si deux éléments crient, il n'y a plus de hiérarchie.
3. **Jamais inventer une couleur.** Le bouton a une valeur, une seule. Un « bleu un peu plus clair »
   improvisé sera rejeté, et à raison : c'est ce qui fait qu'une marque se délite.
4. **Liseré fin plutôt qu'ombre dure.** Cartes et pastilles : une bordure de 1 à 2 pixels. Ombres douces
   et profondes si vraiment nécessaire, **jamais d'ombre colorée décalée**.
5. **Remplacer, pas empiler.** Une itération remplace un élément par un meilleur, elle n'ajoute pas une
   couche par-dessus. Si ça déborde du cadre, on coupe quelque chose.
6. **Le dessin complet ou rien.** Quand on reprend un visuel existant, on reprend sa version complète
   avec ses zones et ses libellés, pas une version simplifiée automatiquement.
7. **Cohérence interne.** Tous les libellés d'un même visuel dans la même couleur, tous les cercles avec
   le même trait. Une seule logique de couleur par état.
8. **Typographie.** Pas d'emojis dans une interface produit (des pictogrammes en traits à la place),
   pas de tiret long, pas de ligne orpheline.
9. **Les logos officiels ne se retouchent pas.** Jamais recréés, recolorés, détourés ni déformés.
   Les chartes d'usage l'interdisent, et une infraction peut coûter le droit d'usage.

## Processus obligatoire

1. Identifier la surface, lire sa source de vérité.
2. Produire, puis **vérifier au rendu réel** : capture d'écran, aperçu navigateur, aperçu email.
   Jamais « ça devrait aller ». Une relecture de texte ne voit pas une géométrie cassée.
3. Présenter le rendu et obtenir une validation explicite. **Aucune mise en ligne sans validation
   des visuels.**
4. Itérer par remplacement. Consigner chaque retour de design nouveau dans ce fichier ou en mémoire,
   sinon vous le réapprendrez.

## Pièges techniques courants

- Les clients email réinterprètent le CSS : tester, ne pas supposer.
- Conversion d'un SVG en image : passer par du HTML et un navigateur sans interface, avec la police
  chargée localement, sinon la police de secours s'applique silencieusement.
- En émulation mobile, les éléments en `position: fixed` peuvent être invisibles sur une capture.
- Un aperçu peut être en retard d'une itération : rechargez avant de juger.
