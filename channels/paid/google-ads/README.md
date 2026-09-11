# Google Ads : lecture et écriture

Deux scripts sans dépendance lourde, qui parlent directement à l'API REST de Google Ads.

| Script | Rôle |
|---|---|
| `google_ads.py` | Lecture seule. Exécute une requête GAQL et renvoie le résultat |
| `google_ads_write.py` | Écriture. **Simulation par défaut**, `--execute` obligatoire pour appliquer |

## Configuration

Les identifiants viennent des variables d'environnement, jamais du code. Renseignez dans `.env` :

```
GOOGLE_ADS_DEVELOPER_TOKEN=
GOOGLE_ADS_CLIENT_ID=
GOOGLE_ADS_CLIENT_SECRET=
GOOGLE_ADS_REFRESH_TOKEN=
GOOGLE_ADS_CUSTOMER_ID=
GOOGLE_ADS_LOGIN_CUSTOMER_ID=
```

Obtenir un jeton de développeur demande une demande d'accès auprès de Google, comptez quelques jours.

## Usage

```bash
python3 channels/paid/google-ads/google_ads.py "SELECT campaign.name, metrics.cost_micros FROM campaign WHERE segments.date DURING LAST_30_DAYS"
```

Requêtes prêtes à l'emploi : `skills/paid-ads/references/gaql-cookbook.md`.

## La règle d'écriture

Simulation, puis validation humaine, puis exécution. Dans cet ordre, à chaque fois. Le script impose déjà la simulation par défaut : ne contournez pas ce garde-fou.
