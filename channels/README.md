# channels/ — les cellules de travail

Une cellule par fonction marketing. Chacune est autonome : son contexte, sa boucle, ses outils, ses sorties.

## Pourquoi découper comme ça

Un agent chargé de tout fait tout moyennement. Une cellule impose trois choses utiles :

1. **Un contexte local.** Un sous-agent qui travaille dans `channels/paid/` ne voit pas le `CLAUDE.md` de la racine. Il a besoin de son contexte à portée de main, dans le dossier où il travaille.
2. **Une boucle nommée.** Tant qu'un processus vit dans votre tête, il n'est ni délégable ni améliorable. Écrit dans `LOOP.md`, il devient les deux.
3. **Des pièges consignés.** Chaque canal a ses erreurs qui coûtent cher. Une fois payées, elles s'écrivent, et on ne les repaye plus.

## Les cellules livrées

| Cellule | Couvre |
|---|---|
| `seo/` | Recherche de mots-clés, briefs, rédaction, publication, mesure |
| `paid/` | Campagnes publicitaires, enchères, annonces, suivi des conversions |
| `cro/` | Pages de conversion, tests, parcours |
| `crm/` | Base de contacts, séquences, réconciliation des données |
| `content/` | Production éditoriale hors SEO |
| `social/` | Réseaux sociaux, créations publicitaires |
| `sales/` | Ce qui remonte de la vente vers le marketing |

Supprimez celles que vous n'utilisez pas. Une cellule vide qui traîne fait croire qu'un canal est travaillé alors qu'il ne l'est pas.

## En créer une

```bash
cp -r channels/_template channels/<votre-canal>
```

Puis remplissez les deux fichiers. Une cellule sans `LOOP.md` rempli n'est qu'un dossier.

## Ce qui vit dans une cellule

| Oui | Non |
|---|---|
| Le contexte propre au canal | Le contexte transverse (il va dans `brain/`) |
| La boucle de travail | Les brouillons jetables (ils vont dans `.scratch/`) |
| Les scripts propres au canal | Les skills réutilisables (ils vont dans `skills/`) |
| Les diagnostics datés | Les vérités stables |
