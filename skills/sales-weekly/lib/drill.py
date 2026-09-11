"""Drill mode — analyse qualitative à la demande quand un KPI craque.

Pas exécuté automatiquement. Le user invoque :
    python3 sales_weekly.py drill --loss-pattern "Budget" --week 2026-W20
    python3 sales_weekly.py drill --stagnant-stage "RDV planifié"
    python3 sales_weekly.py drill --zero-call-open --week 2026-W20

Output : JSON avec deals concernés + call summaries (hs_call_summary, déjà résumé par HubSpot AI)
+ liens vers recording / dealname / owner.

Le user (ou Claude) lit ensuite ce JSON pour analyse qualitative.
"""
from __future__ import annotations
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
sys.path.insert(0, str(Path(__file__).parent))

from hubspot import search_deals, _post, fetch_calls_for_deals, PIPELINE_ID, STAGE, STAGE_LABEL
from transcription import transcribe_call

# Constants {{COMPANY}}
HUBSPOT_PORTAL_ID = "{{HUBSPOT_PORTAL_ID}}"
HUBSPOT_DEAL_URL_TPL = f"https://app.hubspot.com/contacts/{HUBSPOT_PORTAL_ID}/record/0-3/{{deal_id}}"


def deal_url(deal_id: str) -> str:
    return HUBSPOT_DEAL_URL_TPL.format(deal_id=deal_id)


# Stage "freshness" thresholds (days) — below this, le deal n'est pas considéré "ignoré abandonné"
# Au-delà, il devrait avoir été retravaillé
STAGE_FRESH_DAYS = {
    "Prospection": 7,
    "A candidaté": 5,
    "RDV planifié": 5,
    "R1": 7,
    "R2": 7,
    "Long conversion": 30,  # long par nature
    "Decision": 7,
    "Paiement": 7,
}


def analyze_open_deal_why(deal: dict, stage_label: str, owners_map: dict = None) -> dict:
    """Génère l'analyse data-driven pour un deal open (ignoré ou stagnant).

    Returns:
        {
            "category": "🔴 alarm" / "🟡 mid-tenure" / "🟢 fresh-normal",
            "signals": [list of identified data causes],
            "text": "string concaténé des causes"
        }
    """
    from activity import fetch_owners
    owners_map = owners_map or fetch_owners()
    p = deal["properties"]

    # Time-in-stage
    stage_id_entered_prop = f"hs_v2_date_entered_{deal['properties'].get('dealstage')}"
    entered_str = p.get(stage_id_entered_prop)
    days_in_stage = 0
    if entered_str:
        try:
            entered_dt = datetime.fromisoformat(entered_str.replace("Z", "+00:00"))
            days_in_stage = (datetime.now(timezone.utc) - entered_dt).days
        except ValueError:
            pass

    own_id = p.get("hubspot_owner_id")
    own_name = owners_map.get(own_id) if own_id else None
    has_owner = bool(own_id and own_name)
    next_str = p.get("notes_next_activity_date") or ""
    has_next = bool(next_str)
    src = p.get("source") or "(vide)"
    amount = float(p.get("amount") or 0)
    name = p.get("dealname") or ""
    fresh_threshold = STAGE_FRESH_DAYS.get(stage_label, 7)

    signals = []

    # Categorize first
    has_red_flag = False

    if not has_owner:
        signals.append("**Deal orphelin** : aucun owner assigné")
        has_red_flag = True

    if days_in_stage >= 180:
        signals.append(f"**Stuck en {stage_label} depuis {days_in_stage}j** (>6 mois) — close-lost probable")
        has_red_flag = True
    elif days_in_stage >= 60:
        signals.append(f"Stagne en {stage_label} depuis {days_in_stage}j (>2 mois)")
    elif days_in_stage >= 30:
        signals.append(f"En {stage_label} depuis {days_in_stage}j (>1 mois) — mid-tenure")
    elif days_in_stage <= fresh_threshold:
        signals.append(f"Entré en {stage_label} il y a {days_in_stage}j seulement (≤{fresh_threshold}j seuil fresh) — pattern normal")

    if has_next:
        signals.append(f"Tâche programmée le {next_str[:10]}")
    else:
        if days_in_stage > fresh_threshold:
            signals.append("⚠️ **Aucune next activity** programmée")
            has_red_flag = True

    if "ghost" in name.lower():
        signals.append("Dealname annoté 'ghost' = signal d'abandon implicite")
        has_red_flag = True
    elif "plateforms" in name.lower():
        signals.append("Dealname annoté 'plateforms' (cohort ghost-prone)")

    if src == "Nouvelles plateformes" and days_in_stage > 14:
        signals.append("Source Nouvelles plateformes + tenure >14j (canal ghost-prone)")

    if amount == 0:
        signals.append("Amount = 0€ (deal mal saisi côté HubSpot)")
        has_red_flag = True

    # Determine category
    if has_red_flag:
        category = "🔴 alarm"
    elif days_in_stage > fresh_threshold:
        category = "🟡 mid-tenure"
    else:
        category = "🟢 fresh-normal"

    return {
        "category": category,
        "signals": signals,
        "text": " ; ".join(signals) if signals else "Pas de signal data particulier",
        "days_in_stage": days_in_stage,
        "owner_name": own_name or "(aucun owner)",
        "url": deal_url(deal["id"]),
        "name": name,
        "amount": amount,
        "source": src,
        "has_next_activity": has_next,
        "next_activity_date": next_str[:10] if next_str else None,
    }


def _enrich_deals_with_calls(deals: List[dict], with_transcripts: bool = False,
                             min_duration_for_transcript_ms: int = 60_000,
                             verbose: bool = False) -> List[dict]:
    """For each deal, fetch its calls with summaries + body + recording URL.

    Si with_transcripts=True : transcrit aussi les calls (Whisper API) ≥ min_duration_for_transcript_ms
    (default 60s — skip les voicemails très courts).
    Coût ~$0.006/min. Cache local dans ~/.cache/{{SLUG}}/transcripts/.
    """
    deal_ids = [d["id"] for d in deals]
    if not deal_ids:
        return deals
    # V4 batch associations deal → calls
    deal_to_call_ids: Dict[str, List[str]] = {did: [] for did in deal_ids}
    all_call_ids: set = set()
    BATCH = 100
    for i in range(0, len(deal_ids), BATCH):
        batch = deal_ids[i : i + BATCH]
        data = _post("/crm/v4/associations/deal/calls/batch/read",
                     {"inputs": [{"id": did} for did in batch]})
        for r in data.get("results", []):
            did = r["from"]["id"]
            for to in r.get("to", []):
                cid = str(to["toObjectId"])
                deal_to_call_ids[did].append(cid)
                all_call_ids.add(cid)

    # Batch read calls avec summaries/body
    call_meta: Dict[str, dict] = {}
    cid_list = list(all_call_ids)
    for i in range(0, len(cid_list), BATCH):
        batch = cid_list[i : i + BATCH]
        data = _post("/crm/v3/objects/calls/batch/read",
                     {"inputs": [{"id": cid} for cid in batch],
                      "properties": ["hs_timestamp", "hs_call_duration", "hs_call_summary",
                                     "hs_call_body", "hs_call_recording_url", "hubspot_owner_id"]})
        for r in data.get("results", []):
            p = r.get("properties", {})
            call_meta[r["id"]] = {
                "id": r["id"],
                "ts": p.get("hs_timestamp"),
                "duration_ms": int(p.get("hs_call_duration") or 0),
                "summary": (p.get("hs_call_summary") or "").replace("<h5>Summary</h5>", "").strip(),
                "recording_url": p.get("hs_call_recording_url"),
                "owner_id": p.get("hubspot_owner_id"),
            }

    # Attach calls list to each deal, sorted chronologically
    out = []
    n_to_transcribe = 0
    if with_transcripts:
        # Count first for cost estimate
        for d in deals:
            for cid in deal_to_call_ids.get(d["id"], []):
                if cid in call_meta and call_meta[cid].get("duration_ms", 0) >= min_duration_for_transcript_ms:
                    n_to_transcribe += 1
        if verbose:
            print(f"  [transcripts] {n_to_transcribe} calls éligibles à transcrire (≥{min_duration_for_transcript_ms//1000}s)", flush=True)

    transcribed = 0
    for d in deals:
        deal_calls = []
        for cid in deal_to_call_ids.get(d["id"], []):
            if cid in call_meta:
                call = dict(call_meta[cid])
                # Transcrire si demandé et call assez long
                if with_transcripts and call.get("duration_ms", 0) >= min_duration_for_transcript_ms and call.get("recording_url"):
                    transcribed += 1
                    if verbose:
                        print(f"  [{transcribed}/{n_to_transcribe}] call {cid} ({call['duration_ms']/1000:.0f}s)...", flush=True)
                    tr = transcribe_call(cid, call["recording_url"])
                    call["transcript"] = tr.get("text", "")
                    call["transcript_cached"] = tr.get("cached", False)
                    call["transcript_error"] = tr.get("error")
                deal_calls.append(call)
        deal_calls.sort(key=lambda c: c.get("ts") or "")
        enriched = dict(d)
        enriched["calls"] = deal_calls
        enriched["nb_calls"] = len(deal_calls)
        out.append(enriched)
    return out


def drill_loss_reason(pattern: str, start_ms: int, end_ms: int, limit: int = 100,
                      with_transcripts: bool = False) -> dict:
    """Pull deals lost dans la fenêtre dont dealname contient `pattern` (case-insensitive).
    Le pattern est la taxonomie interne : Budget / Ghost / Programme mal adapté / Hors-cible / etc.
    """
    PERDU = f"hs_v2_date_entered_{STAGE['DEAL_PERDU']}"
    deals = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ", "value": STAGE["DEAL_PERDU"]},
            {"propertyName": PERDU, "operator": "GTE", "value": str(start_ms)},
            {"propertyName": PERDU, "operator": "LTE", "value": str(end_ms)},
        ],
        properties=["dealname", "amount", "source", "utm_source", "hubspot_owner_id",
                    "createdate", "product", "product_offert",
                    "closed_lost_reason_dropdown", PERDU],
    )
    pat = pattern.lower()
    filtered = [d for d in deals if pat in (d["properties"].get("dealname") or "").lower()][:limit]
    enriched = _enrich_deals_with_calls(filtered, with_transcripts=with_transcripts, verbose=True)
    return {
        "pattern": pattern,
        "window_start_ms": start_ms,
        "window_end_ms": end_ms,
        "total_lost_in_window": len(deals),
        "matched_count": len(filtered),
        "deals": enriched,
    }


def drill_stagnant_in_stage(stage_label: str, threshold_days: Optional[int] = None,
                            analyze_why: bool = False) -> dict:
    """Pull current open deals stagnants in a given stage > threshold_days.
    Si analyze_why=True : ajoute l'analyse data-driven par deal (category + signals + url)."""
    # Find stage_id from label
    stage_id = None
    for sid, lbl in STAGE_LABEL.items():
        if lbl.lower() == stage_label.lower():
            stage_id = sid
            break
    if not stage_id:
        return {"error": f"stage_label '{stage_label}' not found"}

    entered_prop = f"hs_v2_date_entered_{stage_id}"
    deals = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ", "value": stage_id},
        ],
        properties=["dealname", "amount", "source", "hubspot_owner_id", "createdate",
                    "product", "product_offert", "notes_next_activity_date", entered_prop],
    )

    # Filter by stagnation
    DEFAULT_THRESHOLDS = {"Prospection": 30, "A candidaté": 14, "RDV planifié": 14, "R1": 14,
                         "R2": 21, "Long conversion": 60, "Decision": 21, "Paiement": 30}
    threshold = threshold_days or DEFAULT_THRESHOLDS.get(stage_label, 14)
    now = datetime.now(timezone.utc)
    stagnant = []
    for d in deals:
        entered = d["properties"].get(entered_prop)
        if not entered:
            continue
        try:
            entered_dt = datetime.fromisoformat(entered.replace("Z", "+00:00"))
        except ValueError:
            continue
        days = (now - entered_dt).total_seconds() / 86400
        if days > threshold:
            d_with_days = dict(d)
            d_with_days["days_in_stage"] = round(days)
            stagnant.append(d_with_days)

    stagnant.sort(key=lambda d: -d["days_in_stage"])
    enriched = _enrich_deals_with_calls(stagnant)
    if analyze_why:
        from activity import fetch_owners
        owners_map = fetch_owners()
        for d in enriched:
            d["analysis"] = analyze_open_deal_why(d, stage_label, owners_map)
    return {
        "stage": stage_label,
        "threshold_days": threshold,
        "total_open_in_stage": len(deals),
        "stagnant_count": len(stagnant),
        "deals": enriched,
    }


def drill_coach_sales(owner_id: str, owner_name: str = "",
                      n_won: int = 5, n_lost: int = 5, n_stagnant: int = 5,
                      min_call_duration_s: int = 180,
                      max_calls_per_deal: int = 3,
                      with_transcripts: bool = True) -> dict:
    """Pull 5 won + 5 lost + 5 stagnant deals pour un sales donné, transcrit leurs calls.

    Output : structured dict prêt à être consommé par un skill coaching futur.
    Cache local évite re-transcription.
    """
    from hubspot import CLOSED_STAGES, STAGE_LABEL
    from activity import fetch_owners
    GAGNE = STAGE["DEAL_GAGNE"]
    PERDU = STAGE["DEAL_PERDU"]

    if not owner_name:
        owners = fetch_owners()
        owner_name = owners.get(owner_id, f"id:{owner_id}")

    # Pull recent won (top n_won × 4 pour avoir du choix après filtre call durée)
    won_deals = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ", "value": GAGNE},
            {"propertyName": "hubspot_owner_id", "operator": "EQ", "value": owner_id},
        ],
        properties=["dealname", "amount", "source", "closedate", "createdate",
                    "product", "product_offert", "lost_reason__1_2_"],
        sorts=[{"propertyName": "closedate", "direction": "DESCENDING"}],
        limit=n_won * 4,
    )

    lost_deals = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ", "value": PERDU},
            {"propertyName": "hubspot_owner_id", "operator": "EQ", "value": owner_id},
        ],
        properties=["dealname", "amount", "source", "closedate", "createdate",
                    "product", "product_offert", "lost_reason__1_2_"],
        sorts=[{"propertyName": f"hs_v2_date_entered_{PERDU}", "direction": "DESCENDING"}],
        limit=n_lost * 4,
    )

    # Stagnant : open en R2/Decision/Long conversion stuck >21j (current)
    R2_PROP = f"hs_v2_date_entered_{STAGE['R2']}"
    DEC_PROP = f"hs_v2_date_entered_{STAGE['DECISION']}"
    LC_PROP = f"hs_v2_date_entered_{STAGE['LONG_CONVERSION']}"
    stagnant_deals = []
    for stage_key, prop in [("R2", R2_PROP), ("DECISION", DEC_PROP), ("LONG_CONVERSION", LC_PROP)]:
        stage_id = STAGE[stage_key]
        ds = search_deals(
            filters=[
                {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
                {"propertyName": "dealstage", "operator": "EQ", "value": stage_id},
                {"propertyName": "hubspot_owner_id", "operator": "EQ", "value": owner_id},
            ],
            properties=["dealname", "amount", "source", "createdate", prop, "lost_reason__1_2_"],
        )
        stagnant_deals.extend(ds)

    # Garde les n premiers de chaque catégorie avec calls éligibles
    all_deal_ids = list({d["id"] for d in won_deals + lost_deals + stagnant_deals})
    calls_per_deal = fetch_calls_for_deals(all_deal_ids, via_contacts=True)

    def select_with_calls(deals_pool, n_target, category):
        selected = []
        for d in deals_pool:
            if len(selected) >= n_target:
                break
            calls = sorted(calls_per_deal.get(d["id"], []), key=lambda c: c.get("ts_ms") or 0)
            eligible = [c for c in calls if c.get("duration_ms", 0) >= min_call_duration_s * 1000 and c.get("recording_url")]
            if eligible:
                d_copy = dict(d)
                d_copy["category"] = category
                d_copy["eligible_calls"] = eligible[:max_calls_per_deal]
                selected.append(d_copy)
        return selected

    sel_won = select_with_calls(won_deals, n_won, "won")
    sel_lost = select_with_calls(lost_deals, n_lost, "lost")
    sel_stag = select_with_calls(stagnant_deals, n_stagnant, "stagnant")

    selection = sel_won + sel_lost + sel_stag

    # Transcrire si demandé
    transcripts_stats = {"total_calls": 0, "transcribed": 0, "cached": 0, "errors": 0}
    if with_transcripts:
        for d in selection:
            for c in d["eligible_calls"]:
                transcripts_stats["total_calls"] += 1
                r = transcribe_call(c["id"], c["recording_url"])
                if r.get("error"):
                    transcripts_stats["errors"] += 1
                    c["transcript"] = None
                    c["transcript_error"] = r["error"]
                else:
                    transcripts_stats["transcribed"] += 1
                    if r.get("cached"):
                        transcripts_stats["cached"] += 1
                    c["transcript"] = r["text"]

    return {
        "owner_id": owner_id,
        "owner_name": owner_name,
        "n_won_selected": len(sel_won),
        "n_lost_selected": len(sel_lost),
        "n_stagnant_selected": len(sel_stag),
        "transcripts_stats": transcripts_stats,
        "deals": selection,
    }


def drill_zero_call_open(start_ms: int, end_ms: int, stage_filter: Optional[str] = None,
                         analyze_why: bool = False) -> dict:
    """Pull les deals open qui n'ont reçu aucun call pendant [start_ms, end_ms].
    Optionnel : filtrer par stage. Si analyze_why=True : analyse data-driven par deal."""
    from hubspot import CLOSED_STAGES
    filters = [
        {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
        {"propertyName": "dealstage", "operator": "NOT_IN", "values": CLOSED_STAGES},
    ]
    stage_id_filter = None
    if stage_filter:
        for sid, lbl in STAGE_LABEL.items():
            if lbl.lower() == stage_filter.lower():
                stage_id_filter = sid
                break
        if stage_id_filter:
            filters.append({"propertyName": "dealstage", "operator": "EQ", "value": stage_id_filter})

    # Récupérer aussi les hs_v2_date_entered_* utiles pour analyze_why
    extra_props = []
    if analyze_why:
        # Toutes les étapes sauf les terminales, d'après pipeline.config.json
        OPEN_STAGE_IDS = [sid for sid in STAGE.values() if sid not in CLOSED_STAGES]
        extra_props = [f"hs_v2_date_entered_{sid}" for sid in OPEN_STAGE_IDS]

    deals = search_deals(
        filters=filters,
        properties=["dealname", "amount", "source", "hubspot_owner_id", "createdate",
                    "dealstage", "notes_next_activity_date"] + extra_props,
    )
    # Fetch all their calls and filter zero-call-in-window
    deal_calls = fetch_calls_for_deals([d["id"] for d in deals], via_contacts=True)
    zero_call = []
    for d in deals:
        calls = deal_calls.get(d["id"], [])
        had_call = any(c.get("ts_ms") is not None and start_ms <= c["ts_ms"] <= end_ms for c in calls)
        if not had_call:
            d2 = dict(d)
            d2["total_calls_ever"] = len(calls)
            zero_call.append(d2)
    # Sort by amount desc to show biggest opportunities first
    zero_call.sort(key=lambda d: -float(d["properties"].get("amount") or 0))
    enriched = []
    for d in zero_call[:50]:
        d["calls"] = sorted(deal_calls.get(d["id"], []), key=lambda c: c.get("ts_ms") or 0)[-3:]
        enriched.append(d)

    # Analyze why if requested
    if analyze_why:
        from activity import fetch_owners
        owners_map = fetch_owners()
        for d in enriched:
            stage_id = d["properties"].get("dealstage")
            stage_label = STAGE_LABEL.get(stage_id, "?")
            d["analysis"] = analyze_open_deal_why(d, stage_label, owners_map)

    # Aggregate categories for synthesis
    category_summary = {}
    if analyze_why:
        from collections import Counter as C
        cats = C(d["analysis"]["category"] for d in enriched if "analysis" in d)
        category_summary = dict(cats)

    return {
        "window_start_ms": start_ms,
        "window_end_ms": end_ms,
        "stage_filter": stage_filter,
        "total_open_examined": len(deals),
        "zero_call_count": len(zero_call),
        "category_summary": category_summary,
        "deals_top50_by_amount": enriched,
    }


if __name__ == "__main__":
    # Self-test : Budget pattern sur W20
    import json
    res = drill_loss_reason("Budget", start_ms, end_ms)  # bornes de la fenêtre à analyser
    print(f"Pattern 'Budget' W20 : {res['matched_count']} deals matchés / {res['total_lost_in_window']} lost total")
    if res["deals"]:
        d = res["deals"][0]
        print(f"\nSample deal: {d['properties']['dealname']} (amount {d['properties'].get('amount')}€)")
        print(f"  Calls: {d['nb_calls']}")
        if d["calls"]:
            for c in d["calls"][-2:]:
                print(f"  --- Call {c['ts'][:16]} (dur {c['duration_ms']/1000:.0f}s) ---")
                print(f"      Summary: {(c['summary'] or '(none)')[:300]}")
