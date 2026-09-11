# Sécurité et données sensibles

À lire **avant** le premier `git push`, pas après. Un secret poussé sur un dépôt reste dans l'historique même après suppression du fichier.

## Ce qui ne va jamais dans le repo

| Quoi | Où ça va à la place |
|---|---|
| Clés d'API, jetons, mots de passe | Un fichier `.env` local, ignoré par git |
| Clés de compte de service (`.json`) | `~/.config/<votre-projet>/`, en `chmod 600` |
| Exports de CRM avec des noms et des emails | Hors du repo, ou dans `.scratch/` |
| Enregistrements et transcriptions d'appels clients | Hors du repo |
| Captures contenant des données clients | Hors du repo |

Le `.gitignore` livré couvre les cas courants. Il ne couvre pas votre créativité : un export nommé `contacts-mars.csv` posé à la racine passera.

## Les trois protections livrées

**1. Le `.gitignore`.** Secrets, médias lourds, dossier jetable.

**2. Le scanner.** Cherche emails, téléphones, clés, numéros de compte dans les fichiers :

```bash
python3 security/sanitizer.py --scan --dir . --recursive
```

Il sort en code 1 s'il trouve quelque chose, ce qui le rend utilisable en intégration continue.

**3. Le hook de pre-commit.** Le scanner, lancé automatiquement avant chaque commit :

```bash
cp security/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Installez-le le premier jour. C'est deux commandes, et ça vous évitera un jour de refaire un historique git.

## Les variables d'environnement

Copiez le modèle et remplissez :

```bash
cp .env.example .env
```

`.env` est ignoré par git. Ne le renommez pas, ne le déplacez pas dans un sous-dossier non couvert.

## Données personnelles

Si vous manipulez des verbatims clients, des transcriptions d'appels ou des exports de CRM :

- ces fichiers ne se commitent pas, même dans un dépôt privé ;
- un dépôt privé peut devenir public par erreur, et se partage entre plusieurs personnes ;
- anonymisez avant de vous en servir comme matière pour du contenu : un verbatim publié avec un nom d'entreprise identifiable est un problème, pas une preuve sociale.

Le scanner sait rédiger automatiquement :

```bash
python3 security/sanitizer.py --sanitize --file mon-export.csv
```

## Si un secret a déjà été poussé

1. Révoquez la clé chez le fournisseur, immédiatement. C'est la seule action qui compte vraiment.
2. Générez-en une nouvelle.
3. Nettoyez l'historique ensuite si nécessaire, mais considérez la clé compromise dans tous les cas.

L'ordre a son importance : réécrire l'historique avant de révoquer ne protège de rien.
