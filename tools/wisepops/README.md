# Wisepops — puller API (lecture seule)

Puller Python pour l'API Wisepops (`api2`), sur le modèle des autres pullers du repo
(`ads/google-ads/google_ads.py`, `tools/google/gsuite.py`).

**Doc officielle :** https://support.wisepops.com/en/articles/9897479-wisepops-api-documentation

## Ce que l'API permet (et ne permet pas)

| Endpoint | Méthode | Rôle | Couvert ici |
|---|---|---|---|
| `/contacts` | GET | Contacts collectés (email + champs custom) | ✅ `contacts` |
| `/wisepops` | GET | Perf des pop-ups | ✅ `performance` |
| `/hooks` | GET · POST · DELETE | Gérer les webhooks | ✅ lecture (`hooks`) |
| `/data-privacy` | DELETE | Suppression RGPD | ❌ (destructif, non exposé) |

> ⚠️ **L'API Wisepops est en lecture seule côté données.** Il n'existe **aucun endpoint
> pour créer un contact/subscriber ni un pop-up**. On ne peut donc pas « créer un lead
> dans Wisepops » depuis ici — la création de leads se fait dans HubSpot (voir la routine
> de réconciliation). Le seul « write » de l'API est l'enregistrement d'un webhook
> (`POST /hooks`), non implémenté ici par défaut.

## Auth & prérequis

- **Plan Pro ou supérieur.** Quota standard : ~1 500 appels / 30 jours (relevable via le
  Customer Success Wisepops).
- **1 clé API par site** Wisepops. Header : `Authorization: WISEPOPS-API key="<CLE>"`.
- La clé est lue depuis la variable d'env `WISEPOPS_API_KEY`, sinon depuis
  `~/.config/{{SLUG}}/.env` (secret, hors repo) :

  ```
  WISEPOPS_API_KEY="votre_cle"
  ```

## Usage

```bash
# Tous les contacts (JSON sur stdout)
python3 tools/wisepops/wisepops.py contacts

# Un seul pop-up
python3 tools/wisepops/wisepops.py contacts --wisepop-id 604521

# Depuis une date, en CSV (mêmes colonnes que l'export manuel Wisepops)
python3 tools/wisepops/wisepops.py contacts --after 2026-05-01 --csv > leads.csv

# Perf des pop-ups
python3 tools/wisepops/wisepops.py performance

# Webhooks configurés
python3 tools/wisepops/wisepops.py hooks
```

## À vérifier sur données réelles (dès qu'on a la clé)

- **Pagination** : le puller boucle sur `collected_after` = dernier `collected_at` de la
  page. Si l'API renvoie un token de page (`next`/cursor), adapter `get_contacts()`.
- **Forme de la réponse** : `flatten_contact()` suppose `{collected_at, wisepop_id, ip,
  country_code, fields:{email, ...}}`. Confirmer les noms exacts des champs custom.

## Réconciliation HubSpot (piège connu)

Le flag `Sync Zapier: OK` de Wisepops **ne prouve pas** l'arrivée dans HubSpot (vérifié
2026-09-08 : 5/26 leads absents malgré « OK »). Étape suivante naturelle : croiser la
sortie `contacts` de ce puller avec HubSpot (recherche `email IN [...]`) pour lister les
manquants, sur le modèle de `reconciliation/`. Voir mémoire projet `project_wisepops`.
