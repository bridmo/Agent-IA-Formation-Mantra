# Méthodologie — Sales weekly {{COMPANY}}

Comment chaque métrique se calcule, comment lire le funnel, comment construire la narration.

---

## Principes non négociables

1. **Source unique = HubSpot via MCP.** Pas d'estimation, pas d'extrapolation, pas d'invention. Si une donnée n'est pas dans HubSpot, dire "non mesurable".
2. **Toujours croiser avec WoW** (semaine -1) **ET avec moyenne 4 semaines.** Une métrique seule = sans contexte = inutile.
3. **Une bonne semaine = pourquoi ça a marché.** **Une mauvaise semaine = où ça a cassé.** Pas l'inverse.
4. **Pour les métriques 🔴 à faible volume** (<5 deals concernés) : lister les deals nominativement. C'est plus utile qu'un %.
5. **Output focalisé** : les 4 targets et rien d'autre, sauf si user demande explicitement.

---

## Métriques — recettes exactes

### 1. CA closed-won (target #1)

**Requête HubSpot** :
```
objectType: "deals"
filters:
  - pipeline = "<PIPELINE_ID>"
  - dealstage = "<STAGE_ID>"            (Deal Gagné)
  - closedate >= week_start_ms
  - closedate <= week_end_ms
properties:
  - amount
  - deal_currency_code
  - dealname
  - source
  - utm_source
  - hubspot_owner_id
  - closedate
```

**Mesure principale** : `sum(amount)` (déjà en EUR, company currency).

**Comparatifs à calculer** :
- `% du target = total / 25000 * 100`
- `WoW = (total_S - total_S-1) / total_S-1 * 100`

**Drill-down si 🟠 ou 🔴** :
- Lister tous les deals gagnés (≤ 10) avec dealname, owner, amount, source
- Calculer "manque X € pour atteindre target → équivalent à Y deals moyens"
- Identifier top 1 source qui a tiré (ou top 1 source absente vs avg)

---

### 2. Pipeline pondéré créé (target #2)

**Requête HubSpot** :
```
objectType: "deals"
filters:
  - pipeline = "<PIPELINE_ID>"
  - createdate >= week_start_ms
  - createdate <= week_end_ms
properties:
  - amount
  - hs_projected_amount_in_home_currency
  - deal_currency_code
  - dealname
  - dealstage
  - source
  - utm_source
  - createdate
```

**Mesure principale** : `sum(hs_projected_amount_in_home_currency)`.

Cette propriété est calculée auto par HubSpot = `amount × probabilité_stage_pipeline`. Un deal créé directement en R2 (60% proba) pèse 6× plus qu'un Prospection à 10%.

**Comparatifs** : idem (target, WoW).

**Drill-down** :
- **Top 3 sources contributrices** au pondéré (avec leur % du total)
- **Volume vs avg deal size** : si pondéré faible, est-ce parce qu'on a moins de deals (volume) ou parce qu'on les crée à des stages très early (low proba) ?
- Si une source clé est à 0 cette semaine vs son avg 4w : flagger.

**Note technique** : si `hs_projected_amount_in_home_currency` est vide sur un deal (rare, mais possible si pas de probabilité config sur le stage), tomber sur `amount × 0.1` par défaut (= proba minimale). Le signaler dans l'output.

---

### 3. Activité RDV planifié (target #3)

**Étape 3.1 — Lister les deals en RDV planifié sur la semaine**

Définition "présent en RDV planifié pendant la semaine" :
```
objectType: "deals"
filters (OR group via filterGroups):
  Group A — actuellement en RDV planifié :
    - pipeline = "<PIPELINE_ID>"
    - dealstage = "<STAGE_ID>"
  Group B — passé en RDV planifié cette semaine (même si sorti depuis) :
    - pipeline = "<PIPELINE_ID>"
    - hs_date_entered_<ID_GO_TO_R1> >= week_start_ms
    - hs_date_entered_<ID_GO_TO_R1> <= week_end_ms
properties:
  - dealname
  - dealstage
  - hubspot_owner_id
  - source
  - hs_date_entered_<ID_GO_TO_R1>
  - hs_date_exited_<ID_GO_TO_R1>
```

Dédupliquer sur `id`.

**Étape 3.2 — Compter les calls de la semaine sur chaque deal**

Pour chaque deal_id de la liste :
```
objectType: "calls"
filters:
  - associatedWith deal_id (objectType: "deals", operator: EQUAL)
  - hs_timestamp >= week_start_ms
  - hs_timestamp <= week_end_ms
```

Si possible filtrer aussi `hs_call_status = "COMPLETED"`. Sinon prendre tous les calls loggés (à valider à la première itération).

**Mesure principale** : `% leads avec ≥ 4 calls = nb leads validant / total leads × 100`

**Drill-down si <100%** :
- Lister les deals **sous le seuil** (avec dealname, owner, nb_calls observés, depuis combien de jours en stage)
- "X leads en RDV planifié sans aucun call cette semaine" = signal fort

---

### 4. Hygiène tâches (target #4)

**Requête HubSpot** :
```
objectType: "deals"
filters:
  - pipeline = "<PIPELINE_ID>"
  - dealstage NOT IN ["<STAGE_ID>", "<STAGE_ID>", "<STAGE_ID>"]
    (exclut Deal Gagné, Deal Perdu, Churn → garde uniquement open)
properties:
  - dealname
  - dealstage
  - hubspot_owner_id
  - amount
  - deal_currency_code
  - notes_next_activity_date
  - hs_lastactivitydate
```

**Mesure principale** : `% deals avec notes_next_activity_date NOT NULL`.

`notes_next_activity_date` est auto-rempli par HubSpot dès qu'une tâche, un call ou un meeting futur est loggé sur le deal.

**Drill-down si <100%** :
- Lister les deals SANS next activity (dealname, owner, stage, amount, date dernière activité)
- Total amount à risque = `sum(amount)` des deals fantômes
- **Insight clé** : un deal open sans next step = un deal qui meurt en silence. C'est le risque opérationnel pur.

---

## Lecture du funnel (bonus conditionnel)

À ajouter en sortie **uniquement si une des 4 métriques est 🔴 ET que le funnel explique la cause.**

**Snapshot par stage (open uniquement)** :
- Compter `nb_deals` par `dealstage` (open seulement)
- Comparer à la semaine -1 et à la moyenne 4 semaines

**Patterns à détecter** :
- **Goulot** : un stage qui grossit semaine après semaine (deals qui stagnent) → vélocité cassée
- **Tarissement amont** : Prospection / A candidaté en chute brutale → problème lead gen marketing
- **Vélocité globale** : si `days_to_close` moyen augmente → ralentissement systémique

**Présenter en mini-tableau** :
```
| Stage         | Open | vs S-1 | vs 4w avg |
|---------------|------|--------|-----------|
| Prospection   | 12   | -3     | -25%      |
| RDV planifié      | 8    | +1     | ~          |
| R1            | 6    | =      | +20%      |
| R2            | 11   | +4     | +50% ⚠️   |
| Decision      | 4    | -1     | ~          |
| Long convers. | 7    | =      | ~          |
| Paiement      | 2    | =      | ~          |
```

---

## V0.4 — Métriques avancées

### Funnel diagnostics (cohorte de leads créés dans la fenêtre)

**Définition cohorte** : tous les deals créés dans la fenêtre (`createdate` in window).

Pour chaque deal de la cohorte, on calcule **4 flags** :
1. **Contacted** = `True` si au moins un call associé au deal a `hs_call_duration ≥ 120000` ms (= 2 min). **Pas limité à la fenêtre** : on compte tout call depuis création.
2. **Reached R2** = `hs_v2_date_entered_<ID_R2>` non null
3. **Reached Decision** = `hs_v2_date_entered_<ID_DECISION>` non null
4. **Won** = `dealstage == <STAGE_ID>` (état actuel)
5. **Lost** = `dealstage == <STAGE_ID>` (état actuel)

**Sortie** : counts + % global ET par source (uniquement sources avec ≥3 deals pour stat-sig).

**Pourquoi 120s** : un call <2 min est généralement un "no answer / voicemail / quick hi". À partir de 2 min on a un vrai échange. Statut HubSpot (`hs_call_status`) pas fiable côté {{COMPANY}}.

**Targets** : Contacting 70%, R2 38%, Decision 25% (cf `objectifs.md` § Funnel).

**Lecture** :
- Si Contacting < target : problème d'activité sales (pas assez de relances)
- Si Contacting OK mais R2 faible : problème de qualif (calls ne convertissent pas en RDV qualifié)
- Si R2 OK mais Decision faible : problème de closing
- Si Won faible alors que Decision OK : problème admin (financement OPCO/financement public, paiement)

**À segmenter par source** : un funnel d'Inbound n'a rien à voir avec un funnel de Nouvelles plateformes. Toujours lire par canal.

### Cycle length par source

**Définition** : `closedate - createdate` en jours, sur les deals Gagné dans la fenêtre. Calculé par source + global.

**Sortie** : n, médian, p25, p75, min, max.

**Lecture {{COMPANY}}** :
- Inbound médian ~7-14 jours = sain
- Maformation / Nouvelles plateformes / Paid ~30-90 jours = OPCO/financement public
- Outliers >180j à creuser (relance long dormante)

**Use case** : permet de fixer des **SLA différenciés** pour chaque canal. Un deal Inbound qui n'a pas closé à J+14 = anomalie. Un deal OPCO qui n'a pas closé à J+14 = normal.

### Pipeline velocity (Roberge)

**Formule** : `(N opps Gagné × Avg Deal Size × Win Rate) / Median Cycle Length (jours)` → **€/jour de revenu prévisible**.

**Inputs** dans la fenêtre :
- `N` = nombre de deals Gagné
- `Avg Deal` = sum(amount) / N
- `Win Rate` = N_gagné / (N_gagné + N_perdu) — limite : utilise la fenêtre courante, sensible aux outliers vieux deals lost
- `Cycle` = médian days create→close

**À lire en tendance**, pas en absolu. Une baisse de velocity = une des 4 variables qui craque (volume, prix, win rate, vitesse).

**Limitation connue (V0.4)** : win_rate calculé sur la fenêtre est bruité (deals lost peuvent être de cohortes anciennes). À refiner en V0.5 avec une baseline 4-8 semaines.

### Pipeline coverage ratio

**Formule** : `Open Weighted Pipeline / Monthly Target` (mensuel = 25k × 4.33 = 108 250€).

**Benchmark cible** : ≥ 3.5× pour avoir une chance crédible d'atteindre le mois prochain.

**Lecture** :
- 🟢 ≥ 3.5× : couverture saine
- 🟠 2.0-3.5× : sous-couverture, mois suivant à risque sans accélération
- 🔴 < 2.0× : red flag, pas assez de pipeline pour atteindre le target

**Limitation acceptée** : pas de filtre sur `closedate estimé` (sales ne le remplit pas). C'est donc une **borne supérieure** : tous les deals open comptent. Pour un signal plus précis, croiser avec cycle length par stage (ex. seul un deal en Paiement ou Decision a une vraie chance de closer dans le mois).

### Loss reasons parsing (taxonomie interne)

Parsing regex sur `dealname` pour les deals en Deal Perdu (`<STAGE_ID>`) entrés dans la fenêtre.

**Taxonomie identifiée** (à étendre si nouveaux patterns) :
- `Ghost (no-reply)` — silence
- `Ghost après qualification` — réponse puis silence
- `Programme mal adapté` — fit produit
- `Budget` — pricing
- `Hors-cible` — non-ICP
- `Dates de session mal adaptées` — scheduling
- `Durée mal adaptée` — format

**Cohort tags** (orthogonal aux loss reasons) :
- `high intent` — leads issus de paid acquisition
- `plateforms` — leads issus de job boards (Hellowork, LinkedIn jobs, Meteojob)

**Sortie** : counts + % par reason + breakdown par source (top 3 reasons / source).

**Use case** : feedback loop direct vers marketing (audience), produit (offre), sales (script de qualif).

---

## Comparaison vs target / WoW / 4w avg

Toujours présenter chaque métrique avec **3 ancres temporelles** :
- **vs target** (norme absolue, posée dans `objectifs.md`)
- **vs semaine précédente** (WoW — tendance court terme)
- **vs moyenne 4 semaines** (lisse la saisonnalité)

**Règle d'affichage** :
- Target + WoW = affichés en standard sur chaque métrique
- 4w avg = mentionné **seulement si écart significatif avec WoW** (sinon redondant)

---

## Croisement source × utm_source

`source` = enum à 11 valeurs (cf. `pipeline-schema.md`).
`utm_source` = texte libre (granularité fine).

**Règle** :
1. Toujours segmenter d'abord par `source` (catégorie large)
2. Si une catégorie source est anormale → drill dans `utm_source` pour identifier le sous-canal en cause
3. Ne pas afficher `utm_source` en sortie par défaut — c'est un outil de drill-down, pas une dimension de premier niveau

---

## Construction de la narration

### ❌ Mauvaise narration (à éviter)

> "Cette semaine, le CA closed-won s'élève à 18 000€, soit 72% du target de 25 000€. Le pipeline créé pondéré atteint 21 500€. L'activité RDV planifié montre une moyenne de 3,2 calls par lead..."

→ Plate, énumérative, **scannable mais pas actionnable**. Aucune hypothèse, aucun mover identifié.

### ✅ Bonne narration (à viser)

> **Semaine basse :** 18k€ closés vs 25k target (-28%). Trois deals Inbound attendus en R2 n'ont pas closé (Acme, Beta, Gamma — 15k€ cumulé), tous bloqués sur dossier OPCO. Côté lead gen, **gros trou Paid Social** : 0 deal créé cette semaine vs 4 en moyenne 4w — anomalie, à creuser avec marketing avant mercredi. Activité call OK (78% leads RDV planifié validés). Hygiène : 6 deals open sans next activity = 4,2k€ de risque silencieux à relancer.

→ Identifie les **2-3 plus gros movers**, **nomme les deals**, **propose un levier précis avec deadline**.

### Règle d'or pour la narration

Pour chaque métrique 🟠 ou 🔴, répondre à **3 questions implicites** :
1. **Combien manque-t-il ?** (en € ou en deals)
2. **D'où vient le manque ?** (source / stage / cause identifiable)
3. **Quel est le levier court terme ?** (action concrète, idéalement avec owner)

Si une question reste sans réponse → dire "cause non identifiée à ce stade — à creuser sur [point précis]". **Ne pas inventer une cause plausible.**
