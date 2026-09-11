# Gabarit de fiche d'expérience

Rangement : `channels/<cellule>/experiences/AAAA-MM-slug.md` (mono-canal) ou `strategy/experiences/AAAA-MM-slug.md` (transverse). Une fiche = un fichier. On ne supprime jamais une fiche clôturée : c'est l'historique des paris.

```markdown
# [Nom court du test]

**Statut** : en cours | clôturé
**Owner** : [prénom] · **Ouvert le** : AAAA-MM-JJ · **Gate** : AAAA-MM-JJ
**Canal / levier** : [canal, campagne, page, segment]
**Budget** : [euros ou heures] · **Origine** : [plan, note gtm-strategy, idée, lien]

## Hypothèse
Si on [action] sur [segment], alors [métrique primaire] atteint [seuil] en [fenêtre].

## Mesure
- **Métrique primaire** (deals ou CA) : [définition exacte + requête ou source du pull]
- **Seuil de succès** : [valeur chiffrée]
- **Baseline** : [valeur avant test, datée]
- Métriques secondaires : [CPL, taux, trafic, à titre indicatif]
- **Arrêt d'urgence** : [le signal qui justifie de couper avant la gate, s'il existe]

## Décision prévue à la gate
- Seuil atteint : [scaler comment, avec quel budget]
- Seuil manqué : [couper quoi, réallouer où]
- Illisible : [quelle mesure réparer avant de retester]

## Readout (à la clôture)
- **Résultat** : [valeur mesurée, fenêtre, source du pull ; deals cités un par un si moins de 5]
- **Verdict** : atteint | manqué | illisible
- **Décision** : [garder / couper / scaler, arbitrée par {{OWNER}}, datée]
- **Learning** : [3 lignes max ; si le learning dépasse le test, il part aussi en mémoire projet]
```

## Champs bloquants à l'ouverture

Hypothèse falsifiable, métrique primaire en deals ou CA, seuil, gate datée, owner, décision prévue. Sans l'un d'eux, la fiche n'est pas ouverte et le test ne se lance pas.

## Exemples de bons et mauvais seuils

- Bon : « 5 deals gagnés attribués au point d'entrée quiz en 60 jours » (deals, fenêtre, attribution).
- Mauvais : « améliorer le CPL » (pas de seuil, pas de fenêtre, métrique en leads).
- Bon : « ratio CA gagné / spend au-dessus de 2,5 sur la cohorte à 60 jours ».
