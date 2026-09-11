"""Activity layer — Layer 2 du framework {{COMPANY}}.

Mesure ce que les commerciaux FONT (effort, vitesse, qualité d'outreach).
Source : calls + tasks + owners depuis HubSpot.

Métriques produites :
- Volume calls / jour ouvré, global et par rep
- % calls connectés (≥120s) par rep
- Speed-to-first-call : temps médian entre createdate du deal et 1er call
- Per-rep breakdown : qui tire, qui décroche
- Comparaison vs baseline 4w
"""
from __future__ import annotations
import json
import urllib.request
import statistics
from datetime import datetime, timedelta, timezone, date
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Optional

from hubspot import _post, _token, API_BASE, fetch_calls_for_deals


# === Owners cache (fetched once per script run)
_OWNERS_CACHE: Optional[Dict[str, str]] = None


def fetch_owners() -> Dict[str, str]:
    """Return {owner_id: 'Firstname Lastname'} or 'id:X' if unnamed."""
    global _OWNERS_CACHE
    if _OWNERS_CACHE is not None:
        return _OWNERS_CACHE
    req = urllib.request.Request(
        API_BASE + "/crm/v3/owners?limit=200",
        headers={"Authorization": f"Bearer {_token()}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
        _OWNERS_CACHE = {
            str(o["id"]): (
                f"{o.get('firstName','')} {o.get('lastName','')}".strip()
                or f"id:{o['id']}"
            )
            for o in data.get("results", [])
        }
    except Exception:
        _OWNERS_CACHE = {}
    return _OWNERS_CACHE


def working_days_in_range(start: date, end: date) -> int:
    """Count Monday-Friday days in [start, end] inclusive."""
    d = start
    n = 0
    while d <= end:
        if d.weekday() < 5:
            n += 1
        d += timedelta(days=1)
    return n


def search_calls_in_window(start_ms: int, end_ms: int) -> List[dict]:
    """Pull all calls with hs_timestamp in [start_ms, end_ms]. Auto-paginate."""
    all_results: List[dict] = []
    after = None
    while True:
        body = {
            "filterGroups": [{"filters": [
                {"propertyName": "hs_timestamp", "operator": "GTE", "value": str(start_ms)},
                {"propertyName": "hs_timestamp", "operator": "LTE", "value": str(end_ms)},
            ]}],
            "properties": [
                "hs_timestamp", "hs_call_duration", "hs_call_status",
                "hubspot_owner_id", "hs_call_direction",
            ],
            "limit": 100,
        }
        if after:
            body["after"] = after
        data = _post("/crm/v3/objects/calls/search", body)
        all_results.extend(data.get("results", []))
        nxt = data.get("paging", {}).get("next", {}).get("after")
        if not nxt:
            break
        after = nxt
    return all_results


def aggregate_calls_by_owner(
    calls: List[dict],
    working_days: int,
    min_quality_duration_ms: int = 120_000,
) -> dict:
    """Aggregate calls into per-owner metrics + global totals."""
    owners_map = fetch_owners()
    by_owner = defaultdict(lambda: {
        "name": "", "total": 0, "connected": 0, "duration_sum_ms": 0,
    })
    total = 0
    connected_total = 0
    duration_total = 0

    for c in calls:
        p = c["properties"]
        dur = int(p.get("hs_call_duration") or 0)
        own = p.get("hubspot_owner_id") or "(none)"
        by_owner[own]["total"] += 1
        by_owner[own]["duration_sum_ms"] += dur
        if dur >= min_quality_duration_ms:
            by_owner[own]["connected"] += 1
        total += 1
        duration_total += dur
        if dur >= min_quality_duration_ms:
            connected_total += 1

    # Resolve names
    for own_id, agg in by_owner.items():
        agg["name"] = owners_map.get(own_id, f"id:{own_id}")
        agg["calls_per_wd"] = agg["total"] / working_days if working_days else 0
        agg["connect_rate_pct"] = (agg["connected"] / agg["total"] * 100) if agg["total"] else 0
        agg["avg_duration_min"] = (agg["duration_sum_ms"] / agg["total"] / 60_000) if agg["total"] else 0

    return {
        "total_calls": total,
        "connected_120s": connected_total,
        "connect_rate_pct": (connected_total / total * 100) if total else 0,
        "duration_total_h": duration_total / 3_600_000,
        "calls_per_wd": total / working_days if working_days else 0,
        "working_days": working_days,
        "by_owner": dict(by_owner),
    }


def compute_calls_per_lead_distribution(
    deals: List[dict],
    deal_calls_map: Dict[str, List[dict]],
) -> dict:
    """For each lead in cohort, count total calls received. Output: bucketed distribution.

    Buckets: 0 / 1-2 / 3-5 / 6+
    """
    counts = []
    by_source = defaultdict(list)
    by_owner = defaultdict(list)
    for d in deals:
        p = d["properties"]
        n_calls = len(deal_calls_map.get(d["id"], []))
        counts.append(n_calls)
        by_source[p.get("source") or "(vide)"].append(n_calls)
        by_owner[p.get("hubspot_owner_id") or "(none)"].append(n_calls)

    def bucketize(lst):
        b = {"0": 0, "1-2": 0, "3-5": 0, "6+": 0}
        for n in lst:
            if n == 0:
                b["0"] += 1
            elif n <= 2:
                b["1-2"] += 1
            elif n <= 5:
                b["3-5"] += 1
            else:
                b["6+"] += 1
        total = len(lst)
        return {
            "buckets": b,
            "buckets_pct": {k: (v / total * 100 if total else 0) for k, v in b.items()},
            "total": total,
            "mean": (sum(lst) / total) if total else 0,
            "median": statistics.median(lst) if lst else 0,
        }

    out = {"global": bucketize(counts), "by_source": {}, "by_source_for_won": {}}
    for src, lst in by_source.items():
        if len(lst) >= 3:
            out["by_source"][src] = bucketize(lst)
    # Per owner (named)
    owners_map = fetch_owners()
    out["by_owner"] = {}
    for own_id, lst in by_owner.items():
        if len(lst) >= 3:
            name = owners_map.get(own_id, f"id:{own_id}")
            out["by_owner"][name] = bucketize(lst)
    return out


def compute_stagnant_deals(open_deals: List[dict], thresholds_days: Optional[Dict[str, int]] = None) -> dict:
    """Find deals stuck in their current stage longer than threshold.

    Default thresholds_days:
      Prospection: 30, A candidaté: 14, RDV planifié: 14, R1: 14, R2: 21,
      Long conversion: 60, Decision: 21, Paiement: 30
    """
    from hubspot import STAGE_LABEL, STAGE
    defaults = {
        "Prospection": 30,
        "A candidaté": 14,
        "RDV planifié": 14,
        "R1": 14,
        "R2": 21,
        "Long conversion": 60,
        "Decision": 21,
        "Paiement": 30,
    }
    if thresholds_days:
        defaults.update(thresholds_days)
    now = datetime.now(timezone.utc)
    stagnant_by_stage = defaultdict(list)

    for d in open_deals:
        p = d["properties"]
        stage_id = p.get("dealstage")
        stage_label = STAGE_LABEL.get(stage_id)
        if not stage_label:
            continue
        threshold = defaults.get(stage_label)
        if threshold is None:
            continue
        # Get hs_v2_date_entered_<current_stage>
        entered_prop = f"hs_v2_date_entered_{stage_id}"
        entered_str = p.get(entered_prop)
        if not entered_str:
            continue
        try:
            entered = datetime.fromisoformat(entered_str.replace("Z", "+00:00"))
            days_in_stage = (now - entered).total_seconds() / 86400
        except ValueError:
            continue
        if days_in_stage > threshold:
            owners_map = fetch_owners()
            stagnant_by_stage[stage_label].append({
                "id": d["id"],
                "dealname": p.get("dealname"),
                "amount": float(p.get("amount") or 0),
                "source": p.get("source"),
                "owner": owners_map.get(p.get("hubspot_owner_id"), f"id:{p.get('hubspot_owner_id')}"),
                "days_in_stage": round(days_in_stage),
                "threshold_days": threshold,
            })

    # Sort each stage by days descending
    out = {"thresholds_days": defaults, "by_stage": {}, "total_count": 0, "total_amount": 0}
    for stage, deals in stagnant_by_stage.items():
        deals.sort(key=lambda x: -x["days_in_stage"])
        out["by_stage"][stage] = {
            "count": len(deals),
            "amount_eur": sum(d["amount"] for d in deals),
            "top_deals": deals[:5],  # show 5 worst per stage
            "all_deals": deals,
        }
        out["total_count"] += len(deals)
        out["total_amount"] += sum(d["amount"] for d in deals)
    return out


def compute_open_deals_call_coverage(open_deals: List[dict], start_ms: int, end_ms: int) -> dict:
    """% des deals open du pipeline qui ont reçu ≥1 call PENDANT la fenêtre.

    Inversement : % de deals open IGNORÉS (0 calls) cette semaine.
    Distingue par stage pour identifier où le silence est concentré.
    """
    from hubspot import STAGE_LABEL
    if not open_deals:
        return {"total_open": 0, "with_call_in_window": 0, "without_call_in_window": 0,
                "pct_without_call": 0, "pct_with_call": 0, "by_stage": {}}

    deal_ids = [d["id"] for d in open_deals]
    # Pull all calls (we'll filter in window)
    deal_calls = fetch_calls_for_deals(deal_ids, via_contacts=True)

    with_call = 0
    without_call = 0
    by_stage = defaultdict(lambda: {"total": 0, "with_call": 0, "without_call": 0})

    for d in open_deals:
        p = d["properties"]
        stage_id = p.get("dealstage")
        stage_label = STAGE_LABEL.get(stage_id, f"?{stage_id}")
        calls = deal_calls.get(d["id"], [])
        # Has any call with ts_ms in [start_ms, end_ms] ?
        had_call = any(
            c.get("ts_ms") is not None and start_ms <= c["ts_ms"] <= end_ms
            for c in calls
        )
        by_stage[stage_label]["total"] += 1
        if had_call:
            with_call += 1
            by_stage[stage_label]["with_call"] += 1
        else:
            without_call += 1
            by_stage[stage_label]["without_call"] += 1

    total = with_call + without_call
    return {
        "total_open": total,
        "with_call_in_window": with_call,
        "without_call_in_window": without_call,
        "pct_with_call": (with_call / total * 100) if total else 0,
        "pct_without_call": (without_call / total * 100) if total else 0,
        "by_stage": {
            stage: {
                **counts,
                "pct_without_call": (counts["without_call"] / counts["total"] * 100) if counts["total"] else 0,
            }
            for stage, counts in by_stage.items()
        },
    }


def compute_dormant_deals(open_deals: List[dict], days_threshold: int = 14) -> dict:
    """Find deals not touched (no logged activity) for more than `days_threshold` days.

    Uses hs_lastactivitydate (auto-updated by HubSpot when any activity is logged).
    """
    now = datetime.now(timezone.utc)
    owners_map = fetch_owners()
    dormant = []
    no_activity_ever = []
    for d in open_deals:
        p = d["properties"]
        last_str = p.get("hs_lastactivitydate")
        amt = float(p.get("amount") or 0)
        owner = owners_map.get(p.get("hubspot_owner_id"), f"id:{p.get('hubspot_owner_id')}")
        if not last_str:
            no_activity_ever.append({
                "id": d["id"], "dealname": p.get("dealname"), "amount": amt,
                "stage": p.get("dealstage"), "owner": owner, "source": p.get("source"),
            })
            continue
        try:
            last_dt = datetime.fromisoformat(last_str.replace("Z", "+00:00"))
            days_silent = (now - last_dt).total_seconds() / 86400
        except ValueError:
            continue
        if days_silent > days_threshold:
            dormant.append({
                "id": d["id"], "dealname": p.get("dealname"), "amount": amt,
                "stage": p.get("dealstage"), "owner": owner, "source": p.get("source"),
                "days_silent": round(days_silent),
            })
    dormant.sort(key=lambda x: -x["days_silent"])
    by_owner = Counter()
    for d in dormant:
        by_owner[d["owner"]] += 1
    return {
        "threshold_days": days_threshold,
        "dormant_count": len(dormant),
        "dormant_amount_eur": sum(d["amount"] for d in dormant),
        "no_activity_ever_count": len(no_activity_ever),
        "no_activity_ever_amount_eur": sum(d["amount"] for d in no_activity_ever),
        "by_owner": dict(by_owner),
        "top_dormant": dormant[:10],
    }


def compute_overdue_activities(open_deals: List[dict]) -> dict:
    """Find deals open where notes_next_activity_date is in the past = overdue task."""
    now = datetime.now(timezone.utc)
    overdue = []
    owners_map = fetch_owners()
    for d in open_deals:
        p = d["properties"]
        next_str = p.get("notes_next_activity_date")
        if not next_str:
            continue
        try:
            next_dt = datetime.fromisoformat(next_str.replace("Z", "+00:00"))
        except ValueError:
            continue
        if next_dt < now:
            days_overdue = (now - next_dt).total_seconds() / 86400
            overdue.append({
                "id": d["id"],
                "dealname": p.get("dealname"),
                "amount": float(p.get("amount") or 0),
                "stage": p.get("dealstage"),
                "owner": owners_map.get(p.get("hubspot_owner_id"), f"id:{p.get('hubspot_owner_id')}"),
                "days_overdue": round(days_overdue),
                "next_activity_date": next_str,
            })
    overdue.sort(key=lambda x: -x["days_overdue"])
    by_owner = defaultdict(int)
    for o in overdue:
        by_owner[o["owner"]] += 1
    return {
        "total_count": len(overdue),
        "total_amount_eur": sum(o["amount"] for o in overdue),
        "by_owner": dict(by_owner),
        "top_overdue": overdue[:10],
    }


def compute_speed_to_first_call(
    new_deals: List[dict],
    deal_calls_map: Dict[str, List[dict]],
) -> dict:
    """For each new deal, compute time (hours) between createdate and first call.

    Returns distribution + buckets (<1h, 1-24h, 1-3d, 3-7d, >7d, never).
    """
    def parse(s):
        if not s:
            return None
        return datetime.fromisoformat(s.replace("Z", "+00:00"))

    deltas_hours = []
    never = 0
    buckets = Counter({"<1h": 0, "1-24h": 0, "1-3d": 0, "3-7d": 0, ">7d": 0, "never": 0})

    for d in new_deals:
        p = d["properties"]
        created = parse(p.get("createdate"))
        if not created:
            continue
        calls = deal_calls_map.get(d["id"], [])
        if not calls:
            never += 1
            buckets["never"] += 1
            continue
        # Earliest call ts
        timestamps = [c.get("ts_ms") for c in calls if c.get("ts_ms")]
        if not timestamps:
            never += 1
            buckets["never"] += 1
            continue
        first_call_ms = min(timestamps)
        first_call = datetime.fromtimestamp(first_call_ms / 1000, tz=timezone.utc)
        delta_hours = (first_call - created).total_seconds() / 3600
        if delta_hours < 0:
            continue  # skip weird negative deltas
        deltas_hours.append(delta_hours)
        if delta_hours < 1:
            buckets["<1h"] += 1
        elif delta_hours < 24:
            buckets["1-24h"] += 1
        elif delta_hours < 72:
            buckets["1-3d"] += 1
        elif delta_hours < 168:
            buckets["3-7d"] += 1
        else:
            buckets[">7d"] += 1

    total = len(new_deals)
    return {
        "cohort_size": total,
        "with_call": total - buckets["never"],
        "without_any_call": buckets["never"],
        "median_hours": statistics.median(deltas_hours) if deltas_hours else None,
        "p25_hours": (sorted(deltas_hours)[len(deltas_hours) // 4]
                      if len(deltas_hours) >= 4 else None),
        "p75_hours": (sorted(deltas_hours)[(3 * len(deltas_hours)) // 4]
                      if len(deltas_hours) >= 4 else None),
        "buckets": dict(buckets),
        "buckets_pct": {k: (v / total * 100 if total else 0) for k, v in buckets.items()},
    }


def compute_activity_layer(
    window_start_ms: int,
    window_end_ms: int,
    new_deals: List[dict],
    open_deals: Optional[List[dict]] = None,
    baseline_4w_start_ms: Optional[int] = None,
) -> dict:
    """Full activity layer aggregation for a window + optional 4w baseline.

    new_deals: list of deals created in the window (already fetched upstream)
    open_deals: list of currently open deals (for stagnation + overdue analysis)
    """
    # 1) All calls in the window
    calls = search_calls_in_window(window_start_ms, window_end_ms)

    # 2) Working days in window
    start_d = datetime.fromtimestamp(window_start_ms / 1000, tz=timezone.utc).date()
    end_d = datetime.fromtimestamp(window_end_ms / 1000, tz=timezone.utc).date()
    wd = working_days_in_range(start_d, end_d)
    # Weeks span in window (for /week metrics)
    days_total = (end_d - start_d).days + 1
    weeks_span = days_total / 7.0

    # 3) Aggregate calls by owner (day + week views)
    activity = aggregate_calls_by_owner(calls, wd)
    activity["weeks_in_window"] = weeks_span
    activity["calls_per_week"] = activity["total_calls"] / weeks_span if weeks_span else 0
    for own_id, agg in activity["by_owner"].items():
        agg["calls_per_week"] = agg["total"] / weeks_span if weeks_span else 0

    # 4) Speed-to-first-call + Calls per lead on new deals
    if new_deals:
        deal_ids = [d["id"] for d in new_deals]
        deal_calls = fetch_calls_for_deals(deal_ids, via_contacts=True)
        speed = compute_speed_to_first_call(new_deals, deal_calls)
        calls_per_lead = compute_calls_per_lead_distribution(new_deals, deal_calls)
    else:
        speed = {"cohort_size": 0, "without_any_call": 0, "median_hours": None, "buckets": {}, "buckets_pct": {}}
        calls_per_lead = {"global": {}, "by_source": {}, "by_owner": {}}

    # 5) Discipline metrics on open deals (stagnation + dormant + overdue)
    if open_deals:
        stagnant = compute_stagnant_deals(open_deals)
        dormant = compute_dormant_deals(open_deals, days_threshold=14)
        overdue = compute_overdue_activities(open_deals)
        open_call_coverage = compute_open_deals_call_coverage(open_deals, window_start_ms, window_end_ms)
    else:
        stagnant = {"total_count": 0, "total_amount": 0, "by_stage": {}}
        dormant = {"dormant_count": 0, "dormant_amount_eur": 0, "no_activity_ever_count": 0, "by_owner": {}, "top_dormant": []}
        overdue = {"total_count": 0, "total_amount_eur": 0, "by_owner": {}, "top_overdue": []}
        open_call_coverage = {"total_open": 0, "pct_without_call": 0, "without_call_in_window": 0}

    # 6) Baseline 4w (compute calls/wd over the 4 prior weeks)
    baseline = None
    if baseline_4w_start_ms is not None:
        prior_calls = search_calls_in_window(baseline_4w_start_ms, window_start_ms - 1)
        prior_start_d = datetime.fromtimestamp(baseline_4w_start_ms / 1000, tz=timezone.utc).date()
        prior_end_d = start_d - timedelta(days=1)
        prior_wd = working_days_in_range(prior_start_d, prior_end_d)
        baseline_aggr = aggregate_calls_by_owner(prior_calls, prior_wd)
        baseline = {
            "calls_per_wd_4w_avg": baseline_aggr["calls_per_wd"],
            "connect_rate_pct_4w_avg": baseline_aggr["connect_rate_pct"],
            "working_days_4w": prior_wd,
            "total_calls_4w": baseline_aggr["total_calls"],
        }
        activity["delta_vs_baseline"] = {
            "calls_per_wd_pct": (
                (activity["calls_per_wd"] - baseline["calls_per_wd_4w_avg"])
                / baseline["calls_per_wd_4w_avg"] * 100
            ) if baseline["calls_per_wd_4w_avg"] else 0,
            "connect_rate_pp": activity["connect_rate_pct"] - baseline["connect_rate_pct_4w_avg"],
        }

    return {
        "calls": activity,
        "calls_per_lead": calls_per_lead,
        "speed_to_first_call": speed,
        "discipline": {
            "stagnant_deals": stagnant,
            "dormant_deals": dormant,
            "overdue_activities": overdue,
            "open_call_coverage": open_call_coverage,  # KPI 5 V0.9.1
        },
        "baseline_4w": baseline,
    }


if __name__ == "__main__":
    # Self-test on W20
    from datetime import datetime as dt, timezone as tz
    start = int(dt(2026, 5, 10, 22, 0, 0, tzinfo=tz.utc).timestamp() * 1000)
    end = int(dt(2026, 5, 17, 21, 59, 59, tzinfo=tz.utc).timestamp() * 1000)
    baseline_start = int(dt(2026, 4, 12, 22, 0, 0, tzinfo=tz.utc).timestamp() * 1000)
    # Skip new_deals for self-test
    result = compute_activity_layer(start, end, [], baseline_start)
    print(json.dumps(result, indent=2, default=str)[:2000])
