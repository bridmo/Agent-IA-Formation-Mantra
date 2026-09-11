# Google Workspace — compte de service (Sheets + Slides)

Compte de service Google pour lire/écrire dans des Google Sheets et Google Slides depuis les scripts et agents {{COMPANY}}.

## Config

| Champ | Valeur |
|---|---|
| Email (à partager sur les fichiers) | `{{SA_EMAIL}}` |
| Projet GCP | `{{GCP_PROJECT}}` |
| N° de projet | `{{GCP_PROJECT_NUMBER}}` |
| Client ID | `{{SA_CLIENT_ID}}` |
| Key ID | `{{SA_KEY_ID}}` |
| Clé JSON (secret) | `~/.config/{{SLUG}}/service-account-key.json` (chmod 600, hors du repo) |
| APIs activées | Google Sheets API, Google Slides API |
| APIs **non** activées | **Drive API** (⇒ pas de création/partage/suppression de fichiers), Docs API |

La clé d'origine reste dans `~/Downloads/service-account-key.json` ; la copie de travail (celle utilisée par les scripts) est dans `~/.config/{{SLUG}}/`. Surchargeable via `GOOGLE_SA_KEY`.

## Mode d'emploi (important)

Drive API étant désactivée, **le compte de service ne peut pas créer de fichier** (sheet-create / slides-create renvoient 403). Le flux est :

1. **L'utilisateur crée** le Google Sheet / la présentation Slides dans son Drive.
2. **Il le partage** avec `{{SA_EMAIL}}` en **Éditeur**.
3. **Les scripts éditent** le fichier via son ID (dans l'URL `.../d/<ID>/edit`).

Pour un Google **Doc** : Docs API n'est pas activée → non éditable par ce compte de service (utiliser un Sheet, ou activer Docs API + Drive API si besoin).

## Outil

`tools/google/gsuite.py` :

```
python3 tools/google/gsuite.py whoami
python3 tools/google/gsuite.py sheet-tabs   --id <ID>
python3 tools/google/gsuite.py sheet-read   --id <ID> --range 'Feuille1!A1:D50'
python3 tools/google/gsuite.py sheet-write  --id <ID> --range 'Feuille1!A1' --values-json '[["a","b"],["c","d"]]'
python3 tools/google/gsuite.py sheet-append --id <ID> --range 'Feuille1!A1' --values-json '[["x","y"]]'
python3 tools/google/gsuite.py slides-add-text --id <PRESENTATION_ID> --title 'Titre' --body 'Contenu'
```

Dépendance : `google-api-python-client` + `google-auth` (déjà installés). Lecture seule ? non — l'outil écrit. Toujours vérifier la cible avant un `sheet-write` (écrase la plage).

## Écrire dans un ONGLET d'un Google Doc — `md_to_tab.py`

Rend un markdown simplifié (titres #, sous-sections ##→HEADING_4, puces -, tableaux |) dans un onglet précis. Idempotent (vide l'onglet avant, retry sur timeout).

```
python3 tools/google/md_to_tab.py <DOC_ID> <TAB_ID> <fichier.md>
```

Les onglets Google Docs **ne peuvent pas être créés ni renommés par l'API** — l'utilisateur les crée/nomme dans l'UI ; le script écrit dedans via le `tabId`. Lire les tabId : `documents.get(..., includeTabsContent=True)` → `tabs[].tabProperties.tabId`.

**Doc stratégie {{COMPANY}}** (`{{GOOGLE_DOC_ID}}`), mapping onglets :
- `t.0` = Stratégie moyen terme (édité par {{OWNER}} — NE PAS écraser)
- `t.8ldy6u59kzl` = Court terme · `t.q2m0f17faft8` = Vision · `t.k5ajo6ii5ck6` = Annexes/diagnostics
- Sources locales : `strategy/tabs/*.md`

## Création de fichiers — le compte de service n'a pas de quota Drive

Docs + Drive API sont activées, MAIS un compte de service n'a pas de stockage Drive propre → `*-create` et `doc-from-md` échouent en `storageQuotaExceeded`. Deux solutions :

### A. Domain-wide delegation (recommandé) — le SA agit « en tant que » {{OWNER_EMAIL}}
Les fichiers sont créés dans le Drive de l'utilisateur (son quota) et lui appartiennent.
1. GCP : sur le compte de service, activer « Domain-wide delegation » (client ID `{{SA_CLIENT_ID}}`).
2. Admin Workspace (https://admin.google.com/ac/owl/domainwidedelegation, super-admin) → Ajouter :
   - Client ID : `{{SA_CLIENT_ID}}`
   - Scopes : `https://www.googleapis.com/auth/documents,https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/presentations,https://www.googleapis.com/auth/drive`
3. Ensuite, lancer les scripts avec `GOOGLE_SA_SUBJECT={{OWNER_EMAIL}}` (le tool usurpe l'utilisateur via `with_subject`).

### B. Share-then-edit (marche déjà, zéro setup)
L'utilisateur crée le fichier dans son Drive, le partage en Éditeur avec l'email du SA, puis le script écrit dedans (`doc-append`, `sheet-write`, `slides-add-text`). Pas de création par le SA.

Tant que A n'est pas configuré, utiliser B.
