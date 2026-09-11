"""Sales weekly analyzer {{COMPANY}} — via HubSpot API directe.

Modes:
    weekly   — analyse une semaine (lun-dim Europe/Paris). Défaut = semaine écoulée.
    trend    — analyse une période multi-semaines, sortie semaine par semaine.

Sortie : JSON sur stdout pour que Claude le lise et compose le narratif.

Usage:
    python3 sales_weekly.py weekly                       # semaine écoulée
    python3 sales_weekly.py weekly --week 2026-W20
    python3 sales_weekly.py trend --from 2026-04-01 --to 2026-05-21

Champs de la sortie JSON:
    {
      "mode": "weekly" | "trend",
      "windows": [{"label": "2026-W20", "start_iso": "...", "end_iso": "...", "start_ms": ..., "end_ms": ...}, ...],
      "targets": { "ca": 25000, "weighted_pipeline": 25000, "hygiene_pct": 100 },
      "metrics_by_window": {
          "2026-W20": {
              "ca_closed_won": {"total_eur": ..., "deals": [...], "by_source": {...}},
              "new_pipeline": {"count": ..., "weighted_eur": ..., "by_source": {...}},
              ...
          }
      },
      "open_snapshot": {
          "total_deals": ..., "by_stage": {...}, "hygiene_pct": ...,
          "ghosts": {"count": ..., "amount_eur": ..., "by_stage": {...}}
      }
    }
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow standalone execution
sys.path.insert(0, str(Path(__file__).parent))
from hubspot import (
    search_deals,
    count_calls_per_deal,
    fetch_calls_for_deals,
    PIPELINE_ID,
    STAGE,
    STAGE_LABEL,
    CLOSED_STAGES,
    QUALIF_STAGES,
)
from activity import compute_activity_layer
from economics import compute_economics, detect_structural_break, compute_target_decomposition
import re
import statistics

# Properties that hold the timestamp when a deal entered a given stage.
# Use hs_v2_date_entered_<stage_id> (the v2 version is searchable AND returns values).
def v2_entered(stage_id: str) -> str:
    return f"hs_v2_date_entered_{stage_id}"

# === Objectifs ===
# Vos objectifs commerciaux vivent dans targets.config.json (hors code, car ils changent).
# Copiez targets.config.example.json en targets.config.json et mettez VOS chiffres.
_TARGETS_PATH = Path(__file__).resolve().parent / "targets.config.json"

if not _TARGETS_PATH.exists():
    raise SystemExit(
        f"Configuration manquante : {_TARGETS_PATH.name}\n"
        "  cp targets.config.example.json targets.config.json\n"
        "  puis renseignez vos objectifs (CA hebdo, panier moyen, taux de conversion...)."
    )

TARGETS = {k: v for k, v in json.loads(_TARGETS_PATH.read_text(encoding="utf-8")).items()
           if not k.startswith("_")}

# Europe/Paris offset. DST: CEST (UTC+2) from last Sun of March to last Sun of October.
def paris_offset(dt: datetime) -> timedelta:
    year = dt.year
    # Last Sunday of March
    march_last_sun = datetime(year, 3, 31)
    while march_last_sun.weekday() != 6:
        march_last_sun -= timedelta(days=1)
    # Last Sunday of October
    oct_last_sun = datetime(year, 10, 31)
    while oct_last_sun.weekday() != 6:
        oct_last_sun -= timedelta(days=1)
    if march_last_sun <= dt < oct_last_sun:
        return timedelta(hours=2)  # CEST
    return timedelta(hours=1)  # CET


def paris_dt(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0) -> datetime:
    local = datetime(year, month, day, hour, minute, second)
    return local - paris_offset(local)  # in UTC


def to_ms(utc_dt: datetime) -> int:
    return int(utc_dt.replace(tzinfo=timezone.utc).timestamp() * 1000)


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def week_bounds_from_iso_week(iso_year: int, iso_week: int) -> tuple[datetime, datetime]:
    """Return (utc_start, utc_end) for a given ISO year/week (Mon 00:00 → Sun 23:59:59 Paris)."""
    # Find Monday of that ISO week
    jan4 = datetime(iso_year, 1, 4)
    monday_of_w01 = jan4 - timedelta(days=jan4.weekday())
    mon = monday_of_w01 + timedelta(weeks=iso_week - 1)
    week_start = paris_dt(mon.year, mon.month, mon.day, 0, 0, 0)
    sun = mon + timedelta(days=6)
    week_end = paris_dt(sun.year, sun.month, sun.day, 23, 59, 59)
    return week_start, week_end


def previous_completed_week_label(today: datetime) -> str:
    """Return ISO label like '2026-W20' for the last completed week (Mon-Sun) in Europe/Paris."""
    # Use today's date in Paris
    paris_today = today + paris_offset(today)
    # If today is Monday, previous week = last week. Otherwise also use last week.
    days_to_mon = paris_today.weekday()  # 0 = Monday
    this_monday = paris_today - timedelta(days=days_to_mon)
    last_monday = this_monday - timedelta(days=7)
    y, w, _ = last_monday.isocalendar()
    return f"{y}-W{w:02d}"


def parse_week_label(label: str) -> tuple[int, int]:
    """Parse '2026-W20' → (2026, 20)."""
    y_str, w_str = label.split("-W")
    return int(y_str), int(w_str)


# === Aggregations
def fetch_closed_won(start_ms: int, end_ms: int) -> list[dict]:
    return search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ", "value": STAGE["DEAL_GAGNE"]},
            {"propertyName": "closedate", "operator": "GTE", "value": str(start_ms)},
            {"propertyName": "closedate", "operator": "LTE", "value": str(end_ms)},
        ],
        properties=["dealname", "amount", "deal_currency_code", "source", "utm_source", "closedate", "createdate", "hubspot_owner_id", "product", "product_offert"],
    )


def fetch_new_deals(start_ms: int, end_ms: int) -> list[dict]:
    return search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "createdate", "operator": "GTE", "value": str(start_ms)},
            {"propertyName": "createdate", "operator": "LTE", "value": str(end_ms)},
        ],
        properties=["dealname", "amount", "deal_currency_code", "hs_projected_amount_in_home_currency", "dealstage", "source", "utm_source", "createdate", "hubspot_owner_id", "product", "product_offert"],
    )


def fetch_open_snapshot() -> list[dict]:
    """Pull all currently-open deals in the configured pipeline — includes stage-entry timestamps."""
    # Toutes les étapes sauf les terminales (gagné / perdu / churn), d'après pipeline.config.json
    OPEN_STAGE_IDS = [sid for sid in STAGE.values() if sid not in CLOSED_STAGES]
    extra_props = [f"hs_v2_date_entered_{sid}" for sid in OPEN_STAGE_IDS]
    return search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "NOT_IN", "values": CLOSED_STAGES},
        ],
        properties=["dealname", "amount", "deal_currency_code", "hs_projected_amount_in_home_currency", "dealstage", "source", "utm_source", "createdate", "notes_next_activity_date", "hs_lastactivitydate", "hubspot_owner_id"] + extra_props,
    )


def fetch_qualified_entries(start_ms: int, end_ms: int) -> list[dict]:
    """Deals that entered R2 OR Decision during the window.

    Uses hs_v2_date_entered_<stage_id> (searchable + readable).
    Two queries (OR), dedupe on id.
    """
    r2_prop = v2_entered(STAGE["R2"])
    decision_prop = v2_entered(STAGE["DECISION"])
    props = [
        "dealname", "amount", "deal_currency_code", "source", "utm_source",
        r2_prop, decision_prop, "dealstage", "hubspot_owner_id",
    ]
    a = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": r2_prop, "operator": "GTE", "value": str(start_ms)},
            {"propertyName": r2_prop, "operator": "LTE", "value": str(end_ms)},
        ],
        properties=props,
    )
    b = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": decision_prop, "operator": "GTE", "value": str(start_ms)},
            {"propertyName": decision_prop, "operator": "LTE", "value": str(end_ms)},
        ],
        properties=props,
    )
    seen = set()
    merged = []
    for d in a + b:
        if d["id"] in seen:
            continue
        seen.add(d["id"])
        merged.append(d)
    return merged


def fetch_go_to_r1_cohort(start_ms: int, end_ms: int) -> list[dict]:
    """Deals that were in stage RDV planifié at some point during the window.

    Includes:
    - Deals currently in RDV planifié (dealstage = STAGE["GO_TO_R1"])
    - Deals that entered RDV planifié during the window (hs_v2_date_entered_<GO_TO_R1> in window)
      → covers deals that already moved on but were RDV planifié part of the week
    """
    g2r1_prop = v2_entered(STAGE["GO_TO_R1"])
    props = [
        "dealname", "amount", "deal_currency_code", "source", "utm_source",
        "dealstage", "hubspot_owner_id",
        g2r1_prop, v2_entered(STAGE["R1"]),  # to detect "exited to R1"
    ]
    # A) currently in RDV planifié
    current = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ", "value": STAGE["GO_TO_R1"]},
        ],
        properties=props,
    )
    # B) entered RDV planifié during window (even if now in another stage)
    entered = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": g2r1_prop, "operator": "GTE", "value": str(start_ms)},
            {"propertyName": g2r1_prop, "operator": "LTE", "value": str(end_ms)},
        ],
        properties=props,
    )
    seen = set()
    merged = []
    for d in current + entered:
        if d["id"] in seen:
            continue
        seen.add(d["id"])
        merged.append(d)
    return merged


def aggregate_closed_won(deals: list[dict]) -> dict:
    total = 0.0
    by_source = Counter()
    by_owner = Counter()
    rows = []
    for d in deals:
        p = d["properties"]
        amt = float(p.get("amount") or 0)
        total += amt
        by_source[p.get("source") or "(vide)"] += amt
        by_owner[p.get("hubspot_owner_id") or "(none)"] += amt
        rows.append({
            "id": d["id"],
            "dealname": p.get("dealname"),
            "amount": amt,
            "source": p.get("source"),
            "utm_source": p.get("utm_source"),
            "closedate": p.get("closedate"),
            "createdate": p.get("createdate"),
            "owner": p.get("hubspot_owner_id"),
        })
    return {
        "total_eur": total,
        "deals_count": len(deals),
        "by_source": dict(by_source),
        "by_owner_top": dict(by_owner.most_common(10)),
        "deals": rows,
    }


def aggregate_new_pipeline(deals: list[dict]) -> dict:
    """V0.9.2 — Pipeline pondéré utilise formule interne :
       weighted_eur = nb_deals × avg_deal_for_weighting (1800€) × lead_to_won_conv (9%) = nb_deals × 162€.

    On garde aussi la version HubSpot (sum hs_projected_amount_in_home_currency) en référence sous
    `weighted_eur_hubspot` pour comparaison.
    """
    total_amount = 0.0
    total_weighted_hubspot = 0.0  # référence : sum HubSpot projection
    by_source_count = Counter()
    by_source_hubspot_w = Counter()
    by_stage = Counter()
    for d in deals:
        p = d["properties"]
        amt = float(p.get("amount") or 0)
        w = float(p.get("hs_projected_amount_in_home_currency") or 0)
        total_amount += amt
        total_weighted_hubspot += w
        src = p.get("source") or "(vide)"
        by_source_count[src] += 1
        by_source_hubspot_w[src] += w
        by_stage[STAGE_LABEL.get(p.get("dealstage"), "?")] += 1

    # formule interne
    per_deal_weighted = TARGETS["avg_deal_for_weighting_eur"] * (TARGETS["lead_to_won_conversion_pct"] / 100)
    weighted_flat = len(deals) * per_deal_weighted
    by_source_weighted_flat = {src: cnt * per_deal_weighted for src, cnt in by_source_count.items()}

    return {
        "deals_count": len(deals),
        "amount_eur": total_amount,
        "weighted_eur": weighted_flat,  # principal — formule interne
        "weighted_eur_hubspot": total_weighted_hubspot,  # référence
        "weighting_formula": f"N × {TARGETS['avg_deal_for_weighting_eur']}€ × {TARGETS['lead_to_won_conversion_pct']}% = N × {per_deal_weighted:.0f}€",
        "by_source_weighted": by_source_weighted_flat,
        "by_source_hubspot_weighted": dict(by_source_hubspot_w),
        "by_source_count": dict(by_source_count),
        "by_starting_stage": dict(by_stage),
    }


def aggregate_qualifications(deals: list[dict], start_ms: int, end_ms: int) -> dict:
    """V0.12 — Qualifications pondérées (le KPI cible).

    Pour chaque deal unique entré en R2 OU Decision dans la fenêtre :
      - Si entré en Decision dans la fenêtre → pondéré à 50% × 1800€ = 900€ (catégorie 'Decision')
      - Sinon (entré seulement en R2 dans la fenêtre) → pondéré à 33% × 1800€ = 594€ (catégorie 'R2-only')

    Logique dédup :
      Un deal qui passe R2 ET Decision dans la même fenêtre = compté 1× en Decision (stage le plus avancé).
      Le pondéré reflète la probabilité de signature du stage le plus avancé atteint.

    Target = 25 000€ weighted/semaine.
    """
    R2_PROB = 0.33
    DEC_PROB = 0.50
    AVG_DEAL = 1800
    R2_WEIGHT = AVG_DEAL * R2_PROB    # 594€
    DEC_WEIGHT = AVG_DEAL * DEC_PROB  # 900€

    R2_PROP = f"hs_v2_date_entered_{STAGE['R2']}"
    DEC_PROP = f"hs_v2_date_entered_{STAGE['DECISION']}"

    seen = set()
    rows = []
    r2_only_count = 0
    decision_count = 0
    weighted_total = 0.0
    amount_total = 0.0  # somme amounts (informationnel)

    for d in deals:
        if d["id"] in seen:
            continue
        seen.add(d["id"])
        p = d["properties"]
        amt = float(p.get("amount") or 0)
        amount_total += amt

        # Vérifier si Decision in window
        dec_in_window = False
        r2_in_window = False
        dec_str = p.get(DEC_PROP)
        r2_str = p.get(R2_PROP)
        if dec_str:
            try:
                dec_ms = int(datetime.fromisoformat(dec_str.replace("Z","+00:00")).timestamp() * 1000)
                dec_in_window = start_ms <= dec_ms <= end_ms
            except ValueError:
                pass
        if r2_str:
            try:
                r2_ms = int(datetime.fromisoformat(r2_str.replace("Z","+00:00")).timestamp() * 1000)
                r2_in_window = start_ms <= r2_ms <= end_ms
            except ValueError:
                pass

        # Decision wins (stage le plus avancé)
        if dec_in_window:
            category = "Decision"
            weight = DEC_WEIGHT
            decision_count += 1
        else:
            category = "R2-only"
            weight = R2_WEIGHT
            r2_only_count += 1
        weighted_total += weight

        rows.append({
            "id": d["id"],
            "dealname": p.get("dealname"),
            "amount": amt,
            "source": p.get("source"),
            "stage_current": STAGE_LABEL.get(p.get("dealstage"), "?"),
            "category": category,
            "weight_eur": weight,
            "entered_r2": r2_str,
            "entered_decision": dec_str,
        })

    return {
        "count": len(rows),
        "weighted_eur": weighted_total,           # ⭐ KPI principal
        "amount_eur": amount_total,                # somme amounts (référence)
        "avg_deal_eur": (amount_total / len(rows)) if rows else 0,
        "r2_only_count": r2_only_count,
        "decision_count": decision_count,
        "r2_only_weighted": r2_only_count * R2_WEIGHT,
        "decision_weighted": decision_count * DEC_WEIGHT,
        "formula": f"R2-only × {R2_WEIGHT:.0f}€ ({int(R2_PROB*100)}% × {AVG_DEAL}€) + Decision × {DEC_WEIGHT:.0f}€ ({int(DEC_PROB*100)}% × {AVG_DEAL}€)",
        "deals": rows,
    }


def aggregate_open(deals: list[dict]) -> dict:
    by_stage = defaultdict(lambda: {"count": 0, "amount": 0.0, "weighted": 0.0})
    by_source_w = Counter()
    no_next = []
    ghosts_60d = []
    now_utc = datetime.now(timezone.utc)
    total_w = 0.0
    total_amt = 0.0
    for d in deals:
        p = d["properties"]
        stage_lbl = STAGE_LABEL.get(p.get("dealstage"), "?")
        amt = float(p.get("amount") or 0)
        w = float(p.get("hs_projected_amount_in_home_currency") or 0)
        by_stage[stage_lbl]["count"] += 1
        by_stage[stage_lbl]["amount"] += amt
        by_stage[stage_lbl]["weighted"] += w
        by_source_w[p.get("source") or "(vide)"] += w
        total_w += w
        total_amt += amt
        if not p.get("notes_next_activity_date"):
            no_next.append({
                "id": d["id"],
                "dealname": p.get("dealname"),
                "stage": stage_lbl,
                "amount": amt,
                "source": p.get("source"),
                "createdate": p.get("createdate"),
            })
            create_str = p.get("createdate")
            if create_str:
                try:
                    cdt = parse_iso(create_str)
                    if (now_utc - cdt).days > 60:
                        ghosts_60d.append({
                            "id": d["id"],
                            "stage": stage_lbl,
                            "amount": amt,
                            "source": p.get("source"),
                            "createdate": create_str,
                        })
                except ValueError:
                    pass
    hyg_pct = (len(deals) - len(no_next)) / len(deals) * 100 if deals else 0
    return {
        "total_deals": len(deals),
        "total_amount_eur": total_amt,
        "total_weighted_eur": total_w,
        "by_stage": {k: dict(v) for k, v in by_stage.items()},
        "by_source_weighted": dict(by_source_w),
        "hygiene_pct": hyg_pct,
        "no_next_count": len(no_next),
        "no_next_amount_eur": sum(d["amount"] for d in no_next),
        "ghosts_60d_count": len(ghosts_60d),
        "ghosts_60d_amount_eur": sum(d["amount"] for d in ghosts_60d),
        "no_next_by_stage": dict(Counter(d["stage"] for d in no_next)),
    }


def aggregate_calls_activity(cohort: list[dict], call_counts: dict, target: int) -> dict:
    """Compute % of leads in cohort that meet the calls target."""
    rows = []
    n_meeting = 0
    total_calls = 0
    for d in cohort:
        p = d["properties"]
        n = call_counts.get(d["id"], 0)
        total_calls += n
        meets = n >= target
        if meets:
            n_meeting += 1
        rows.append({
            "id": d["id"],
            "dealname": p.get("dealname"),
            "owner": p.get("hubspot_owner_id"),
            "source": p.get("source"),
            "calls_in_window": n,
            "meets_target": meets,
            "current_stage": STAGE_LABEL.get(p.get("dealstage"), "?"),
        })
    total = len(cohort)
    pct = (n_meeting / total * 100) if total else 0
    return {
        "cohort_size": total,
        "leads_meeting_target": n_meeting,
        "pct_meeting_target": pct,
        "avg_calls_per_lead": (total_calls / total) if total else 0,
        "total_calls_logged": total_calls,
        "target_calls_per_lead": target,
        "deals_below_target": [r for r in rows if not r["meets_target"]],
    }


# === V0.4 metrics ===

def fetch_lost_deals(start_ms: int, end_ms: int) -> list:
    """Deals lost in window (Deal Perdu stage entered during window).

    Uses hs_v2_date_entered_<DEAL_PERDU> for accurate "lost during window".
    """
    perdu_prop = v2_entered(STAGE["DEAL_PERDU"])
    return search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": perdu_prop, "operator": "GTE", "value": str(start_ms)},
            {"propertyName": perdu_prop, "operator": "LTE", "value": str(end_ms)},
        ],
        properties=["dealname", "amount", "source", "utm_source", "createdate", "hubspot_owner_id",
                    perdu_prop, "lost_reason__1_2_", "closed_lost_reason_dropdown"],
    )


def compute_funnel_diagnostics(new_deals: list, start_ms: int, end_ms: int) -> dict:
    """For each deal created in window, check if it reached:
    - Contacted (≥1 call ≥120s)
    - R2 (hs_v2_date_entered_<R2> non null)
    - Decision (hs_v2_date_entered_<DECISION> non null)
    - Won (currently in Deal Gagné)
    Per source breakdown included.

    Note: contacting rate uses calls SINCE CREATION (not limited to the analysis window),
    because we want to know if the lead has been contacted at all by now.
    """
    if not new_deals:
        return {"cohort_size": 0, "by_source": {}, "global": {}}

    # 1) Pull the v2 entry properties for these deals (they may already be in props if requested)
    # We need them — re-search to ensure
    deal_ids = [d["id"] for d in new_deals]
    # Properties we need
    r2_prop = v2_entered(STAGE["R2"])
    dec_prop = v2_entered(STAGE["DECISION"])
    g2r1_prop = v2_entered(STAGE["GO_TO_R1"])
    perdu_prop = v2_entered(STAGE["DEAL_PERDU"])

    # Re-fetch deals with stage history properties (batched)
    BATCH = 100
    enriched = {}
    for i in range(0, len(deal_ids), BATCH):
        batch = deal_ids[i : i + BATCH]
        data = _batch_read_deals(batch, [r2_prop, dec_prop, g2r1_prop, perdu_prop, "dealstage", "source"])
        for r in data:
            enriched[r["id"]] = r["properties"]

    # 2) Pull all calls associated to these deals (any time, not just in window)
    calls_per_deal = fetch_calls_for_deals(deal_ids)

    # 3) Compute per-deal flags
    rows = []
    now_utc = datetime.now(timezone.utc)
    for d in new_deals:
        did = d["id"]
        p = d["properties"]
        eprops = enriched.get(did, {})
        calls = calls_per_deal.get(did, [])
        # V0.5: deux mesures distinctes
        call_tried = len(calls) > 0  # any call attempt logged (effort metric)
        call_quality = any(c.get("duration_ms", 0) >= TARGETS["min_call_duration_ms"] for c in calls)  # real exchange (cohort metric)
        reached_r2 = bool(eprops.get(r2_prop))
        reached_decision = bool(eprops.get(dec_prop))
        won = eprops.get("dealstage") == STAGE["DEAL_GAGNE"]
        lost = eprops.get("dealstage") == STAGE["DEAL_PERDU"]
        # Cohort age (jours depuis création du deal) — utile pour interpréter quality
        age_days = None
        create_str = p.get("createdate")
        if create_str:
            try:
                cdt = parse_iso(create_str)
                age_days = (now_utc - cdt).total_seconds() / 86400
            except ValueError:
                pass
        rows.append({
            "id": did,
            "source": p.get("source") or "(vide)",
            "age_days": age_days,
            "call_tried": call_tried,
            "call_quality": call_quality,
            "reached_r2": reached_r2,
            "reached_decision": reached_decision,
            "won": won,
            "lost": lost,
        })

    # 4) Aggregate global + per source
    def aggr(group):
        n = len(group)
        if n == 0:
            return {}
        ages = [r["age_days"] for r in group if r["age_days"] is not None]
        return {
            "cohort_size": n,
            "median_age_days": statistics.median(ages) if ages else None,
            "call_tried": sum(1 for r in group if r["call_tried"]),
            "call_tried_pct": sum(1 for r in group if r["call_tried"]) / n * 100,
            "call_quality": sum(1 for r in group if r["call_quality"]),
            "call_quality_pct": sum(1 for r in group if r["call_quality"]) / n * 100,
            "reached_r2": sum(1 for r in group if r["reached_r2"]),
            "reached_r2_pct": sum(1 for r in group if r["reached_r2"]) / n * 100,
            "reached_decision": sum(1 for r in group if r["reached_decision"]),
            "reached_decision_pct": sum(1 for r in group if r["reached_decision"]) / n * 100,
            "won": sum(1 for r in group if r["won"]),
            "won_pct": sum(1 for r in group if r["won"]) / n * 100,
            "lost": sum(1 for r in group if r["lost"]),
            "lost_pct": sum(1 for r in group if r["lost"]) / n * 100,
        }

    by_source = {}
    sources = set(r["source"] for r in rows)
    for src in sources:
        group = [r for r in rows if r["source"] == src]
        if len(group) >= 3:  # only show sources with enough volume
            by_source[src] = aggr(group)

    return {
        "global": aggr(rows),
        "by_source": by_source,
        "targets": {
            "call_tried_pct": TARGETS["call_tried_rate_pct"],
            "call_quality_pct": TARGETS["call_quality_rate_pct"],
            "reached_r2_pct": TARGETS["r2_reach_rate_pct"],
            "reached_decision_pct": TARGETS["decision_reach_rate_pct"],
        },
        "note": (
            "Cohorte = leads créés dans la fenêtre. "
            "call_tried = ≥1 call attempt loggué (any duration) — mesure d'effort sales. "
            "call_quality = ≥1 call ≥120s — mesure cohort à lire avec l'âge du lead (jeune <7j = quality faible normale ; mature ≥14j = quality doit approcher target). "
            "Sources contacts (deal direct + via contacts associés) unionnés pour ne rien manquer."
        ),
    }


def _batch_read_deals(deal_ids: list, properties: list) -> list:
    """Batch read deals using V3 batch endpoint."""
    from hubspot import _post
    if not deal_ids:
        return []
    data = _post(
        "/crm/v3/objects/deals/batch/read",
        {"inputs": [{"id": did} for did in deal_ids], "properties": properties},
    )
    return data.get("results", [])


def compute_cycle_length_by_source(closed_won_deals: list) -> dict:
    """For deals closed-won in the window, compute days from createdate to closedate, by source."""
    if not closed_won_deals:
        return {}
    by_source = defaultdict(list)
    for d in closed_won_deals:
        p = d["properties"]
        create_str = p.get("createdate")
        close_str = p.get("closedate")
        if not (create_str and close_str):
            continue
        try:
            cdt = parse_iso(create_str)
            ddt = parse_iso(close_str)
            days = (ddt - cdt).total_seconds() / 86400
            by_source[p.get("source") or "(vide)"].append(days)
        except ValueError:
            continue

    out = {}
    for src, days_list in by_source.items():
        days_list.sort()
        out[src] = {
            "n": len(days_list),
            "median_days": statistics.median(days_list),
            "mean_days": statistics.mean(days_list),
            "p25_days": days_list[len(days_list) // 4] if len(days_list) >= 4 else days_list[0],
            "p75_days": days_list[(3 * len(days_list)) // 4] if len(days_list) >= 4 else days_list[-1],
            "min_days": days_list[0],
            "max_days": days_list[-1],
        }
    # Global
    all_days = [d for days in by_source.values() for d in days]
    all_days.sort()
    if all_days:
        out["__global__"] = {
            "n": len(all_days),
            "median_days": statistics.median(all_days),
            "mean_days": statistics.mean(all_days),
            "p25_days": all_days[len(all_days) // 4],
            "p75_days": all_days[(3 * len(all_days)) // 4],
            "min_days": all_days[0],
            "max_days": all_days[-1],
        }
    return out


def compute_pipeline_velocity(closed_won_count: int, avg_deal_size: float, win_rate_pct: float, cycle_days: float) -> dict:
    """Pipeline velocity = (N opps × avg deal size × win rate) / cycle length (days).
    Returns €/day predictable revenue.
    """
    if cycle_days <= 0:
        return {"value_eur_per_day": None, "error": "cycle_days <= 0"}
    val = (closed_won_count * avg_deal_size * (win_rate_pct / 100)) / cycle_days
    return {
        "n_opps_won": closed_won_count,
        "avg_deal_size_eur": avg_deal_size,
        "win_rate_pct": win_rate_pct,
        "cycle_days": cycle_days,
        "value_eur_per_day": val,
        "value_eur_per_week": val * 7,
    }


# === Loss reason parsing (specific to your setup dealname taxonomy) ===
LOSS_REASON_PATTERNS = [
    # (regex, canonical label)
    (re.compile(r"\bghost\s+apr[èe]s\s+qualification\b", re.I), "Ghost après qualification"),
    (re.compile(r"\bghost\b", re.I), "Ghost (no-reply)"),
    (re.compile(r"\bprogramme\s+mal\s+adapt[ée]\b", re.I), "Programme mal adapté"),
    (re.compile(r"\bbudget\b", re.I), "Budget"),
    (re.compile(r"\bhors[- ]cible\b", re.I), "Hors-cible"),
    (re.compile(r"\bdates?\s+de\s+session\s+mal\s+adapt[ée]\b", re.I), "Dates de session mal adaptées"),
    (re.compile(r"\bdur[ée]e\s+mal\s+adapt[ée]\b", re.I), "Durée mal adaptée"),
    (re.compile(r"\bplateforms?\b", re.I), "Plateforms cohort"),  # cohort tag, not loss reason
    (re.compile(r"\bhigh\s+intent\b", re.I), "High intent cohort"),  # cohort tag
]


def parse_loss_reasons(lost_deals: list) -> dict:
    """V0.11+ : utilise le champ HubSpot structuré `lost_reason__1_2_` (créé 2025-11-03,
    multi-checkbox séparé par `;`) en source primaire. Fallback dealname parsing si le
    champ est vide. Cohort tags (high intent / plateforms) toujours détectés via dealname.

    Returns counts (flattened multi-valeurs) + by_source breakdown.
    """
    reason_counts = Counter()
    cohort_counts = Counter()
    by_source_reasons = defaultdict(Counter)
    no_reason_logged = []  # deals sans aucune raison (ni champ structuré ni dealname pattern)
    via_structured_field = 0
    via_dealname_fallback = 0

    for d in lost_deals:
        p = d["properties"]
        name = p.get("dealname") or ""
        src = p.get("source") or "(vide)"
        structured = p.get("lost_reason__1_2_") or ""

        # Cohort tags : toujours via dealname
        for regex, label in LOSS_REASON_PATTERNS:
            if "cohort" in label.lower() and regex.search(name):
                cohort_counts[label] += 1

        # Reasons : priorité au champ structuré
        if structured:
            via_structured_field += 1
            for raw in structured.split(";"):
                v = raw.strip()
                if v:
                    reason_counts[v] += 1
                    by_source_reasons[src][v] += 1
        else:
            # Fallback dealname
            matched = False
            for regex, label in LOSS_REASON_PATTERNS:
                if "cohort" in label.lower():
                    continue
                if regex.search(name):
                    reason_counts[label] += 1
                    by_source_reasons[src][label] += 1
                    matched = True
            if matched:
                via_dealname_fallback += 1
            else:
                no_reason_logged.append({"id": d["id"], "dealname": name, "source": src})

    unparsed = no_reason_logged  # backward compat naming

    total = len(lost_deals)
    return {
        "total_lost": total,
        "reason_breakdown": dict(reason_counts),
        "reason_breakdown_pct": {k: v / total * 100 if total else 0 for k, v in reason_counts.items()},
        "cohort_tags": dict(cohort_counts),
        "by_source_top_reason": {
            src: dict(reasons.most_common(3)) for src, reasons in by_source_reasons.items()
        },
        "via_structured_field_count": via_structured_field,
        "via_dealname_fallback_count": via_dealname_fallback,
        "no_reason_logged_count": len(unparsed),
        "no_reason_logged_sample": unparsed[:10],
        "data_quality_pct": ((via_structured_field + via_dealname_fallback) / total * 100) if total else 0,
        "_source": "lost_reason__1_2_ (primary) + dealname pattern (fallback)",
    }


def compute_pipeline_coverage(open_snapshot: dict) -> dict:
    """Pipeline coverage = open weighted pipeline / monthly CA target.
    Simplified: no closedate filter ({{COMPANY}} sales don't fill closedate estimé).
    """
    open_weighted = open_snapshot.get("total_weighted_eur", 0)
    target = TARGETS["monthly_ca_target_eur"]
    ratio = open_weighted / target if target else 0
    return {
        "open_weighted_eur": open_weighted,
        "monthly_target_eur": target,
        "ratio": ratio,
        "ratio_target": TARGETS["pipeline_coverage_ratio_target"],
        "interpretation": (
            "Vert ≥ 3.5×" if ratio >= 3.5 else
            "Orange 2.0-3.5×" if ratio >= 2.0 else
            "Rouge < 2×"
        ),
        "note": "Simplifié : pas de filtre sur closedate estimé (non rempli côté sales). Borne supérieure du pipeline réellement closable next month.",
    }


# === V0.6 — Layer 1 Acquisition (with baseline 4w) ===
def compute_acquisition_layer(start_ms: int, end_ms: int, baseline_4w_start_ms: int) -> dict:
    """Layer 1 : volume leads créés dans la fenêtre, par source, vs baseline 4w."""
    # Leads dans la fenêtre
    window_deals = fetch_new_deals(start_ms, end_ms)
    by_source = Counter()
    for d in window_deals:
        by_source[d["properties"].get("source") or "(vide)"] += 1
    total = len(window_deals)

    # Baseline 4w
    baseline_deals = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "createdate", "operator": "GTE", "value": str(baseline_4w_start_ms)},
            {"propertyName": "createdate", "operator": "LTE", "value": str(start_ms - 1)},
        ],
        properties=["source", "createdate"],
    )
    baseline_by_source = Counter()
    for d in baseline_deals:
        baseline_by_source[d["properties"].get("source") or "(vide)"] += 1
    baseline_weeks = 4  # convention
    baseline_per_week_total = len(baseline_deals) / baseline_weeks
    baseline_per_week_by_source = {s: c / baseline_weeks for s, c in baseline_by_source.items()}

    # Delta
    delta_total_pct = ((total - baseline_per_week_total) / baseline_per_week_total * 100) if baseline_per_week_total else 0
    delta_by_source = {}
    for src in set(list(by_source.keys()) + list(baseline_per_week_by_source.keys())):
        observed = by_source.get(src, 0)
        baseline_v = baseline_per_week_by_source.get(src, 0)
        delta_abs = observed - baseline_v
        delta_pct = (delta_abs / baseline_v * 100) if baseline_v > 0 else (100 if observed > 0 else 0)
        delta_by_source[src] = {
            "observed": observed,
            "baseline_4w_avg": baseline_v,
            "delta_abs": delta_abs,
            "delta_pct": delta_pct,
        }

    return {
        "total_leads": total,
        "by_source": dict(by_source),
        "baseline_4w": {
            "total_per_week_avg": baseline_per_week_total,
            "by_source_avg": baseline_per_week_by_source,
            "baseline_window_start_ms": baseline_4w_start_ms,
            "baseline_window_end_ms": start_ms - 1,
        },
        "delta_total_pct": delta_total_pct,
        "delta_by_source": delta_by_source,
    }


# === Main per-window orchestrator ===
def analyze_window(label: str, start_utc: datetime, end_utc: datetime, with_calls: bool = True, with_activity: bool = True) -> dict:
    start_ms = to_ms(start_utc)
    end_ms = to_ms(end_utc)
    cw = fetch_closed_won(start_ms, end_ms)
    new_d = fetch_new_deals(start_ms, end_ms)
    quals = fetch_qualified_entries(start_ms, end_ms)
    quals_agg = aggregate_qualifications(quals, start_ms, end_ms)

    # Calls activity on RDV planifié cohort (target #3)
    calls_agg = None
    if with_calls:
        cohort = fetch_go_to_r1_cohort(start_ms, end_ms)
        cohort_ids = [d["id"] for d in cohort]
        try:
            counts = count_calls_per_deal(cohort_ids, start_ms, end_ms)
        except RuntimeError as e:
            counts = {}
        calls_agg = aggregate_calls_activity(cohort, counts, TARGETS["calls_per_lead_go_to_r1"])

    # V0.4: funnel diagnostics on the new_deals cohort
    funnel = compute_funnel_diagnostics(new_d, start_ms, end_ms)

    # V0.4: cycle length (days create→close) on closed-won deals
    cycle = compute_cycle_length_by_source(cw)

    # V0.4: pipeline velocity (per-window)
    # avg deal size = avg amount on closed-won
    avg_deal = (sum(float(d["properties"].get("amount") or 0) for d in cw) / len(cw)) if cw else 0
    # win rate = won / (won + lost) using cohort of new deals → BUT we'd need to know what lost in this window came from this cohort
    # Simpler: use this window's cw count vs lost count in same window as proxy
    lost = fetch_lost_deals(start_ms, end_ms)
    won_count = len(cw)
    lost_count = len(lost)
    win_rate = (won_count / (won_count + lost_count) * 100) if (won_count + lost_count) > 0 else 0
    cycle_global = cycle.get("__global__", {}).get("median_days", 0)
    velocity = compute_pipeline_velocity(won_count, avg_deal, win_rate, cycle_global) if cycle_global > 0 else None

    # V0.4: loss reasons on deals lost in window
    loss_reasons = parse_loss_reasons(lost)

    # V0.6 — 4-Layer Framework
    # Baseline 4w starts 28 days before window start
    baseline_4w_start_ms = start_ms - (28 * 24 * 3600 * 1000)
    layer_1 = compute_acquisition_layer(start_ms, end_ms, baseline_4w_start_ms)
    # V0.7: pass open_deals snapshot to activity layer for stagnation + overdue
    open_for_activity = fetch_open_snapshot() if with_activity else None
    layer_2 = compute_activity_layer(start_ms, end_ms, new_d, open_for_activity, baseline_4w_start_ms) if with_activity else None

    # V0.8 — Economics decomposition (CA = Volume × Panier)
    economics = compute_economics(cw)
    # Baseline 3 months for structural break detection
    baseline_3m_start_ms = start_ms - (3 * 30 * 24 * 3600 * 1000)
    baseline_cw = fetch_closed_won(baseline_3m_start_ms, start_ms - 1)
    baseline_econ = compute_economics(baseline_cw)
    structural_break = detect_structural_break(
        economics["avg_deal"],
        baseline_econ["avg_deal"],
        threshold_pct=10,
    )
    # Target decomposition (weekly target = 25k€)
    target_decomp = compute_target_decomposition(
        ca_observed=economics["ca_total"],
        avg_deal_observed=economics["avg_deal"],
        deal_count_observed=economics["deal_count"],
        target_ca=TARGETS["ca_weekly_eur"],
    )

    result = {
        "label": label,
        "start_iso": start_utc.isoformat(),
        "end_iso": end_utc.isoformat(),
        "start_ms": start_ms,
        "end_ms": end_ms,
        # V0.6 — 4-Layer structure
        "layer_1_acquisition": layer_1,
        "layer_2_activity": layer_2,
        "layer_3_conversion": {
            "funnel_diagnostics": funnel,
            "qualifications": quals_agg,
            "calls_activity_go_to_r1": calls_agg,
            "cycle_length_days": cycle,
        },
        "layer_4_outcome": {
            "ca_closed_won": aggregate_closed_won(cw),
            "new_pipeline": aggregate_new_pipeline(new_d),
            "win_rate_in_window": {"won": won_count, "lost": lost_count, "win_rate_pct": win_rate},
            "pipeline_velocity": velocity,
            "loss_reasons": loss_reasons,
        },
        # V0.8 — Economics (Volume × Panier + bundle penetration + rupture detection)
        "layer_4b_economics": {
            "economics": economics,
            "baseline_3m": baseline_econ,
            "structural_break": structural_break,
            "target_decomposition": target_decomp,
        },
        # Backward compat aliases (V0.5 consumers)
        "ca_closed_won": aggregate_closed_won(cw),
        "new_pipeline": aggregate_new_pipeline(new_d),
        "qualifications": quals_agg,
        "calls_activity_go_to_r1": calls_agg,
        "funnel_diagnostics": funnel,
        "cycle_length_days": cycle,
        "win_rate_in_window": {"won": won_count, "lost": lost_count, "win_rate_pct": win_rate},
        "pipeline_velocity": velocity,
        "loss_reasons": loss_reasons,
    }
    return result


def cmd_weekly(args):
    if args.week:
        y, w = parse_week_label(args.week)
        start, end = week_bounds_from_iso_week(y, w)
        label = args.week
    else:
        label = previous_completed_week_label(datetime.utcnow())
        y, w = parse_week_label(label)
        start, end = week_bounds_from_iso_week(y, w)

    # Previous week for WoW context
    prev_y, prev_w = parse_week_label(label)
    prev_w -= 1
    if prev_w < 1:
        prev_w = 52
        prev_y -= 1
    prev_label = f"{prev_y}-W{prev_w:02d}"
    prev_start, prev_end = week_bounds_from_iso_week(prev_y, prev_w)

    open_snap = aggregate_open(fetch_open_snapshot())
    out = {
        "mode": "weekly",
        "targets": TARGETS,
        "windows": [
            {"label": label, "start_iso": start.isoformat(), "end_iso": end.isoformat()},
            {"label": prev_label, "start_iso": prev_start.isoformat(), "end_iso": prev_end.isoformat()},
        ],
        "metrics_by_window": {
            label: analyze_window(label, start, end),
            prev_label: analyze_window(prev_label, prev_start, prev_end),
        },
        "open_snapshot": open_snap,
        "pipeline_coverage": compute_pipeline_coverage(open_snap),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))


def cmd_trend(args):
    start_date = datetime.fromisoformat(args.from_date)
    end_date = datetime.fromisoformat(args.to_date)
    # Walk ISO weeks
    weeks = []
    cursor = start_date
    while cursor <= end_date:
        y, w, _ = cursor.isocalendar()
        weeks.append((y, w))
        cursor += timedelta(days=7)
    # Dedupe and build window list
    seen = set()
    windows = []
    for y, w in weeks:
        if (y, w) in seen:
            continue
        seen.add((y, w))
        start, end = week_bounds_from_iso_week(y, w)
        windows.append((f"{y}-W{w:02d}", start, end))

    open_snap = aggregate_open(fetch_open_snapshot())
    out = {
        "mode": "trend",
        "targets": TARGETS,
        "windows": [{"label": l, "start_iso": s.isoformat(), "end_iso": e.isoformat()} for l, s, e in windows],
        # trend mode : skip activity layer per-week (too expensive). Only on the last week.
        "metrics_by_window": {
            l: analyze_window(l, s, e, with_activity=(i == len(windows) - 1))
            for i, (l, s, e) in enumerate(windows)
        },
        "open_snapshot": open_snap,
        "pipeline_coverage": compute_pipeline_coverage(open_snap),
    }
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))


def cmd_drill(args):
    """Drill mode — analyse qualitative à la demande."""
    from drill import drill_loss_reason, drill_stagnant_in_stage, drill_zero_call_open
    if args.loss_pattern:
        # Window resolution
        if args.week:
            y, w = parse_week_label(args.week)
            start, end = week_bounds_from_iso_week(y, w)
        else:
            label = previous_completed_week_label(datetime.utcnow())
            y, w = parse_week_label(label)
            start, end = week_bounds_from_iso_week(y, w)
        out = drill_loss_reason(args.loss_pattern, to_ms(start), to_ms(end),
                                with_transcripts=args.with_transcripts)
    elif args.stagnant_stage:
        out = drill_stagnant_in_stage(args.stagnant_stage, args.threshold_days,
                                      analyze_why=args.analyze_why)
    elif args.zero_call_open:
        if args.week:
            y, w = parse_week_label(args.week)
            start, end = week_bounds_from_iso_week(y, w)
        else:
            label = previous_completed_week_label(datetime.utcnow())
            y, w = parse_week_label(label)
            start, end = week_bounds_from_iso_week(y, w)
        out = drill_zero_call_open(to_ms(start), to_ms(end), args.stage_filter,
                                   analyze_why=args.analyze_why)
    else:
        out = {"error": "specify one of --loss-pattern / --stagnant-stage / --zero-call-open"}
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))


def main():
    parser = argparse.ArgumentParser(description="{{COMPANY}} Sales Weekly Analyzer")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_w = sub.add_parser("weekly", help="Analyse une semaine (lun-dim)")
    p_w.add_argument("--week", help="Format YYYY-WXX (défaut: dernière sem complète)")
    p_w.set_defaults(func=cmd_weekly)

    p_t = sub.add_parser("trend", help="Analyse multi-semaines")
    p_t.add_argument("--from", dest="from_date", required=True, help="Date début YYYY-MM-DD")
    p_t.add_argument("--to", dest="to_date", required=True, help="Date fin YYYY-MM-DD")
    p_t.set_defaults(func=cmd_trend)

    p_d = sub.add_parser("drill", help="Drill mode — analyse qualitative à la demande")
    p_d.add_argument("--loss-pattern", help="Pattern à matcher dans dealname pour deals lost (ex: Budget, Ghost, Programme mal adapté)")
    p_d.add_argument("--stagnant-stage", help="Étape du pipeline, telle que nommée dans pipeline.config.json")
    p_d.add_argument("--threshold-days", type=int, help="Custom seuil de stagnation (sinon défaut par stage)")
    p_d.add_argument("--zero-call-open", action="store_true", help="Deals open sans aucun call dans la fenêtre")
    p_d.add_argument("--stage-filter", help="Pour --zero-call-open : filtrer sur un stage précis")
    p_d.add_argument("--week", help="Format YYYY-WXX pour cibler la fenêtre")
    p_d.add_argument("--with-transcripts", action="store_true", help="Transcrire les calls ≥60s via Whisper API (coût ~$0.006/min, cache local)")
    p_d.add_argument("--analyze-why", action="store_true", help="Pour chaque deal du résultat : analyse data-driven (category 🔴/🟡/🟢 + signals + URL HubSpot). Compatible avec --zero-call-open et --stagnant-stage.")
    p_d.set_defaults(func=cmd_drill)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
