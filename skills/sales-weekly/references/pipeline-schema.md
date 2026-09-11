# HubSpot Pipeline Schema — {{COMPANY}} Sales Weekly
> Tous les identifiants de ce document sont des jetons : les vrais vivent dans `lib/pipeline.config.json`.


Référentiel technique : pipeline, stages, sources, propriétés deal, engagements.

**Dernière mise à jour** : 2026-05-21 (V0.2 — migration MCP → API directe)
**Compte HubSpot** : devise EUR, timezone Europe/Paris, instance `na1`

À mettre à jour à chaque modification HubSpot (renommage stage, ajout source, etc.).

---

## Accès API (V0.2+)

**Auth** : Private App token stocké dans `~/.config/{{SLUG}}/.env` (chmod 600).
```
HUBSPOT_TOKEN=<VOTRE_TOKEN_CRM>
```

**Endpoints utilisés** :
- `POST https://api.hubapi.com/crm/v3/objects/deals/search` — recherche deals avec filtres
- `GET  https://api.hubapi.com/crm/v3/objects/deals/{id}/associations/calls` — calls associés à un deal
- `POST https://api.hubapi.com/crm/v3/objects/calls/batch/read` — batch lecture calls

**Pagination** : cursor `paging.next.after` (gérée auto par `lib/hubspot.py`). Pas de cap 200 hard.

**Scopes Private App requis** : `crm.objects.deals.read`, `crm.schemas.deals.read`, `crm.objects.contacts.read` (optionnel), `crm.objects.line_items.read` (futur — mapping formations).

---

---

## Pipeline cible

| Champ | Valeur |
|---|---|
| Nom | `votre pipeline principal` |
| ID | `<PIPELINE_ID>` |

**Filtre obligatoire** dans **toutes** les requêtes `search_crm_objects` :
```json
{ "propertyName": "pipeline", "operator": "EQ", "value": "<PIPELINE_ID>" }
```

Tous les autres pipelines (Bootcamp, Sales Admission, {{COMPANY}} Pro, etc.) sont **hors scope** du skill `sales-weekly` sauf demande explicite de l'user.

---

## Stages

| Label | ID | Catégorie | Rôle dans les targets |
|---|---|---|---|
| Prospection | `<STAGE_ID>` | Open — top funnel | — |
| A candidaté | `<ID_A_POSTULE>` | Open — lead qualifié top funnel | — |
| **RDV planifié** | `<STAGE_ID>` | Open — phase activité | **Target #3** (calls mesurés ici) |
| R1 | `<STAGE_ID>` | Open — middle funnel | — |
| **R2** | `<STAGE_ID>` | Open — qualifié | **Target #2 jalon : qualification** |
| Long conversion | `<STAGE_ID>` | Open — middle funnel | — |
| **Decision** | `<STAGE_ID>` | Open — bottom funnel | **Target #2 jalon : qualification (alt R2)** |
| Paiement | `<STAGE_ID>` | Open — closing admin | — |
| **Deal Gagné** | `<STAGE_ID>` | Closed-won | **Target #1 mesuré ici** |
| Deal Perdu | `<STAGE_ID>` | Closed-lost | — |
| Churn | `<STAGE_ID>` | Closed-lost post-vente | — |

### Conventions importantes

- **Qualification effectuée** (target #2 jalon) = **passage en R2 OU passage en Decision**, peu importe l'ordre. Certains deals zappent R2 et vont direct en Decision.
- **Open deals** (utilisés pour target #4 hygiène) = **tout sauf** `<STAGE_ID>` (Gagné), `<STAGE_ID>` (Perdu), `<STAGE_ID>` (Churn).
- **Stages historiques détectés mais non utilisés** : les IDs `appointmentscheduled`, `qualifiedtobuy`, `presentationscheduled`, etc. apparaissent dans la liste HubSpot (probable héritage d'anciens pipelines). Ils ne concernent PAS le pipeline `<PIPELINE_ID>` et doivent être ignorés.

---

## Propriété `source` (enum, 11 valeurs)

Source canal d'acquisition (catégorie large).

| Valeur | Description |
|---|---|
| `Paid` | Paid search type Google Ads |
| `Paid Social` | Meta / TikTok / LinkedIn Ads |
| `Inbound` | SEO / direct / contenu |
| `Referral` | Bouche-à-oreille / partenaire |
| `Nouvelles plateformes` | Emerging channels (à clarifier — drill `utm_source`) |
| `Affiliates` | Affiliés |
| `Sales effort` | Outbound humain (SDR/AE) |
| `Maformation` | Site Maformation.fr (marketplace formations) |
| `Outbound` | Outbound froid auto (email/LinkedIn) |
| `Webinar` | Leads webinar |
| `Emailing` | Campagnes email marketing (newsletter) |

---

## Propriété `utm_source` (texte libre)

Granularité fine. Utiliser uniquement en **drill-down** dans une catégorie `source` suspecte. Pas affiché par défaut dans l'output.

Exemples observés : `linkedin`, `google`, `newsletter-mensuelle`, `tiktok`, etc.

---

## Propriétés deal à pull (set standard)

À demander dans chaque `search_crm_objects` (adapter selon la requête) :

```
"dealname",
"amount",
"deal_currency_code",                          ← obligatoire avec amount
"hs_projected_amount_in_home_currency",        ← weighted amount auto-calculé
"dealstage",
"pipeline",
"source",
"utm_source",
"hubspot_owner_id",
"createdate",
"closedate",
"notes_next_activity_date",                    ← pour target #4 hygiène
"hs_lastactivitydate",                         ← contexte pour deals fantômes
"num_contacted_notes",                         ← nb total d'activités sur le deal
"hs_date_entered_<ID_GO_TO_R1>",                    ← entrée en RDV planifié (target #3)
"hs_date_entered_<ID_R2>",                    ← entrée en R2 (target #2 jalon)
"hs_date_entered_<ID_DECISION>",                  ← entrée en Decision (target #2 jalon)
"hs_date_exited_<ID_GO_TO_R1>"                      ← sortie de RDV planifié (calcul fenêtre)
```

⚠️ **Règle MCP HubSpot** : `deal_currency_code` est obligatoire dans `properties` dès qu'on pull `amount` ou `hs_projected_amount_*`. Sinon la réponse n'est pas narrable.

---

## Propriétés stage history (V0.3+) — searchable

⚠️ **Important** : pour interroger la date à laquelle un deal est entré dans un stage, utiliser le préfixe **`hs_v2_date_entered_<stage_id>`**, **PAS** `hs_date_entered_<stage_id>` (V1, non searchable et souvent vide en réponse).

| Property | Stage | Usage |
|---|---|---|
| `hs_v2_date_entered_<ID_GO_TO_R1>` | RDV planifié | Target #3 — détection cohorte semaine |
| `hs_v2_date_entered_<ID_R2>` | R2 | Target qualif — passage en R2 |
| `hs_v2_date_entered_<ID_DECISION>` | Decision | Target qualif — passage en Decision (alt R2) |
| `hs_v2_date_entered_<ID_R1>` | R1 | Détection "exited RDV planifié vers R1" |
| `hs_v2_date_entered_<ID_GAGNE>` | Deal Gagné | Bonus — date de win effective si différent de `closedate` |

Ces propriétés sont `calculated=False` côté HubSpot, donc utilisables comme filtres dans `/crm/v3/objects/deals/search`. Type = `datetime` (ms Unix en filtre, ISO 8601 en réponse).

## Stage probabilities (référence — pour info)

Les probabilités sont configurées **côté HubSpot dans les settings du pipeline**, pas dans les propriétés deal. Elles s'appliquent automatiquement via `hs_projected_amount_in_home_currency` = `amount × probabilité_stage`.

**Probabilités HubSpot standard** (à vérifier dans HubSpot UI si on a un doute) :
- Closed-won (Deal Gagné) : 100%
- Closed-lost (Perdu / Churn) : 0%
- Open stages : config custom {{COMPANY}} (généralement progressive : Prospection ~5-10%, R1 ~30%, R2 ~50-60%, Decision ~70-80%, Paiement ~90%)

Si tu veux les % exacts, lire dans HubSpot UI > Settings > Objects > Deals > Pipelines > "votre pipeline principal".

---

## Engagements — calls (target #3)

**Pour compter les calls sur un deal sur la semaine** :

```
objectType: "calls"
filters:
  - associatedWith: { objectType: "deals", operator: "EQUAL", objectIdValues: [deal_id] }
  - hs_timestamp >= week_start_ms
  - hs_timestamp <= week_end_ms
  (optionnel) - hs_call_status = "COMPLETED"
properties:
  - hs_timestamp
  - hs_call_status
  - hs_call_duration
  - hubspot_owner_id
```

**Décision {{COMPANY}} (2026-05-21)** : on prend **tous les calls loggés**, pas de filtre sur `hs_call_status`. Raison : la qualification du statut n'est pas fiable dans HubSpot côté {{COMPANY}} — un appel "no answer" ou "left voicemail" reste un effort de relance qui compte dans la mesure d'activité.

**Implémentation V0.3** : `lib/hubspot.py::count_calls_per_deal(deal_ids, start_ms, end_ms)` utilise :
1. `POST /crm/v4/associations/deal/calls/batch/read` (max 100 deals/batch) → liste des call IDs par deal
2. `POST /crm/v3/objects/calls/batch/read` (max 100 calls/batch, propriété `hs_timestamp`) → timestamps
3. Filtrage Python sur la fenêtre `[start_ms, end_ms]`

Coût : **2 API calls pour N deals** (vs 2N en V0.2). Pour 200 deals = ~3 sec.

---

## Engagements — tasks (alternative target #4)

V1 utilise `notes_next_activity_date` (plus simple, suffisant). Si besoin de précision (savoir quel type d'action est planifiée) :

```
objectType: "tasks"
filters:
  - associatedWith: { objectType: "deals", operator: "EQUAL", objectIdValues: [deal_id] }
  - hs_task_status != "COMPLETED"
properties:
  - hs_task_subject
  - hs_task_status
  - hs_timestamp
  - hubspot_owner_id
```

---

## Trucs à savoir / pièges connus

- **Pas d'anciens stages héritages** : on ignore tous les stages avec IDs hors du pipeline `<PIPELINE_ID>`.
- **Devise** : compte EUR uniquement, pas de multi-devise. `amount` = EUR, `hs_projected_amount_in_home_currency` = EUR.
- **Timezone** : tous les `*_date` HubSpot sont en UTC (ms Unix). Toujours convertir en Europe/Paris pour calculer la fenêtre lundi-dimanche.
- **Limite pagination** : `search_crm_objects` retourne 100 par défaut (200 max). Toujours vérifier `total` dans la réponse pour s'assurer qu'on n'a pas tronqué. Paginer avec `offset` si nécessaire.
- **5 filterGroups max** (avec 6 filters max chacun, 18 total max). Construire les requêtes en conséquence.

---

## Intégration Ringover (statut : bloqué)

**Tentative V0.9.4 (mai 2026)** : intégrer les transcripts de calls Ringover dans le drill mode pour analyse qualitative riche.

**État** : API key {{COMPANY}} ne dispose pas de la scope **Empower API access**. Tous les endpoints `/v2/public/empower/call/...` retournent 403 `error code: 1010`.

**Pour débloquer** :
1. Activer "Empower API" scope sur la clé Ringover (Dashboard → Développeurs → ta clé → settings)
2. Si l'option n'existe pas → activer Empower sur l'abonnement Ringover {{COMPANY}} (paid feature)
3. Vérifier que c'est bien Empower **API** (pas seulement Empower web)

**Workflow API quand débloqué** :
```
1. POST https://public-api.ringover.com/v2/public/empower/platform/{platformname}/channel/{channel_id}
   → retourne {calluuid}
2. GET .../v2/public/empower/call/{calluuid}            → transcript complet
3. GET .../v2/public/empower/call/{calluuid}/summary    → résumé Empower (plus riche que hs_call_summary)
4. GET .../v2/public/empower/call/{calluuid}/moments    → key moments timestampés
```

**Token storage** : `~/.config/{{SLUG}}/.env` → `RINGOVER_TOKEN=...`

**Alternative si Empower jamais débloqué** : télécharger les fichiers MP3 via `hs_call_recording_url` ou le champ `record` de Ringover, transcrire avec OpenAI Whisper API. ~1 sec par minute de call audio. Coût ~$0.006/min. À évaluer si nécessaire.

**État du drill mode V0.9.3** : utilise `hs_call_summary` (résumé AI HubSpot) en attendant. Couvert ~50-70% des calls (vide sur calls courts / voicemails).

---

## Évolution prévue (V2+)

- [ ] Ajouter mapping `hubspot_owner_id` → équipe sales (pour analyse par AE)
- [ ] Identifier la propriété deal qui contient la formation vendue (`formation_*` ? `dealtype` ?) → analyse par produit
- [ ] Documenter les probabilités exactes par stage si on les change (en V1, on s'appuie sur HubSpot auto-calcul)
- [ ] Identifier propriétés OPCO / financement public / financement (souvent un blocage R2+) → analyse "deals bloqués sur financement"
