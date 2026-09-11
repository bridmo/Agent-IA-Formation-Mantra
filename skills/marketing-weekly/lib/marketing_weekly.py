#!/usr/bin/env python3
"""marketing_weekly.py : pull data pour le recap marketing / acquisition hebdo {{COMPANY}}.

Sortie : JSON unique sur stdout avec 3 blocs (hubspot, google_ads, meta_ads).
Chaque bloc echoue independamment (cle "error" si un pull casse, le reste sort quand meme).

Sources :
- HubSpot   : deals crees par semaine x source, pipeline Prio & Performance (15000467).
              Auth via ~/.config/{{SLUG}}/.env (HUBSPOT_TOKEN), reutilise skills/sales-weekly/lib/hubspot.py
- Google Ads: spend / clics / impressions / conversions segmentees par action, par campagne.
              Reutilise channels/paid/google-ads/google_ads.py (creds .env projet)
- Meta Ads  : spend / impressions / clics / actions par campagne.
              Reutilise ads/meta/meta_ads.py (creds .env projet)

Usage :
    python3 marketing_weekly.py                  # defaut : derniere semaine complete (lun-dim Europe/Paris)
    python3 marketing_weekly.py --week 2026-W36  # semaine ISO precise
    python3 marketing_weekly.py --no-ads         # HubSpot uniquement (debug rapide)

Fenetres produites : semaine analysee (W), semaine precedente (W-1),
baseline = moyenne des 4 semaines precedant W.
"""
from __future__ import annotations
import argparse
import datetime as dt
import importlib.util
import json
import os
import sys
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Paris")
HERE = Path(__file__).resolve().parent

# Racine du repo par recherche ascendante (robuste aux symlinks / deplacements)
_d = HERE
while _d != Path("/") and not (_d / "skills" / "sales-weekly").is_dir():
    _d = _d.parent
ROOT = _d

PIPELINE_ID = "15000467"
SOURCES_ORDER = [
    "Paid", "Paid Social", "Inbound", "Nouvelles plateformes", "Maformation",
    "Referral", "Webinar", "Emailing", "Outbound", "Sales effort", "Affiliates",
]


def _import(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------- fenetres ----------

def week_bounds(iso_week: str | None):
    """Retourne (week_start, week_end) datetime Europe/Paris de la semaine analysee.

    iso_week au format 2026-W36, sinon derniere semaine complete (lun 00:00 -> dim 23:59:59).
    """
    if iso_week:
        year, wk = iso_week.upper().split("-W")
        monday = dt.date.fromisocalendar(int(year), int(wk), 1)
    else:
        today = dt.datetime.now(TZ).date()
        this_monday = today - dt.timedelta(days=today.weekday())
        monday = this_monday - dt.timedelta(days=7)  # derniere semaine COMPLETE
    start = dt.datetime.combine(monday, dt.time.min, tzinfo=TZ)
    end = start + dt.timedelta(days=7) - dt.timedelta(seconds=1)
    return start, end


def ms(d: dt.datetime) -> int:
    return int(d.timestamp() * 1000)


# ---------- HubSpot ----------

def pull_hubspot(week_start: dt.datetime, week_end: dt.datetime) -> dict:
    hs = _import(ROOT / "skills" / "sales-weekly" / "lib" / "hubspot.py", "hubspot")
    pull_start = week_start - dt.timedelta(days=35)  # W + 5 semaines d'historique
    deals = hs.search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "createdate", "operator": "GTE", "value": str(ms(pull_start))},
            {"propertyName": "createdate", "operator": "LTE", "value": str(ms(week_end))},
        ],
        properties=["dealname", "source", "utm_source", "utm_campain", "utm_campaign",
                    "createdate", "amount", "deal_currency_code", "dealstage"],
    )
    # Groupement par semaine ISO x source
    by_week_source: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    week_deals: dict[str, list[dict]] = defaultdict(list)
    week_key = week_start.date().isocalendar()
    week_label = f"{week_key[0]}-W{week_key[1]:02d}"
    for d in deals:
        p = d.get("properties", {})
        created = p.get("createdate")
        if not created:
            continue
        try:
            when = dt.datetime.fromisoformat(created.replace("Z", "+00:00")).astimezone(TZ)
        except ValueError:
            continue
        iso = when.date().isocalendar()
        wk = f"{iso[0]}-W{iso[1]:02d}"
        src = p.get("source") or "(sans source)"
        by_week_source[wk][src] += 1
        if wk == week_label:
            week_deals[src].append({
                "dealname": p.get("dealname"),
                "utm_source": p.get("utm_source"),
                "utm_campaign": p.get("utm_campain") or p.get("utm_campaign"),
                "created": when.strftime("%Y-%m-%d %H:%M"),
            })

    # Semaines de reference
    def wk_of(offset_weeks: int) -> str:
        d0 = (week_start + dt.timedelta(weeks=offset_weeks)).date().isocalendar()
        return f"{d0[0]}-W{d0[1]:02d}"

    prev_label = wk_of(-1)
    baseline_labels = [wk_of(-i) for i in range(1, 5)]

    all_sources = sorted(
        {s for wk in by_week_source.values() for s in wk},
        key=lambda s: SOURCES_ORDER.index(s) if s in SOURCES_ORDER else 99,
    )
    table = []
    for src in all_sources:
        cur = by_week_source[week_label].get(src, 0)
        prev = by_week_source[prev_label].get(src, 0)
        base = sum(by_week_source[lbl].get(src, 0) for lbl in baseline_labels) / 4
        table.append({
            "source": src, "week": cur, "prev_week": prev,
            "baseline_4w": round(base, 1),
            "wow_pct": round((cur - prev) / prev * 100) if prev else None,
        })
    return {
        "week_label": week_label,
        "prev_week_label": prev_label,
        "total_week": sum(by_week_source[week_label].values()),
        "total_prev_week": sum(by_week_source[prev_label].values()),
        "baseline_4w_total": round(
            sum(sum(by_week_source[lbl].values()) for lbl in baseline_labels) / 4, 1),
        "by_source": table,
        "history_by_week": {k: dict(v) for k, v in sorted(by_week_source.items())},
        "deals_of_week": {k: v for k, v in week_deals.items()},
    }


# ---------- Google Ads ----------

def pull_google(week_start: dt.datetime, week_end: dt.datetime) -> dict:
    ga = _import(ROOT / "ads" / "google-ads" / "google_ads.py", "google_ads_puller")
    access = ga.get_access_token()

    def window(d1: dt.date, d2: dt.date) -> dict:
        rng = f"segments.date BETWEEN '{d1}' AND '{d2}'"
        rows = ga.search(
            "SELECT campaign.name, campaign.status, metrics.cost_micros, metrics.clicks, "
            "metrics.impressions, metrics.average_cpc, metrics.search_impression_share, "
            "metrics.search_budget_lost_impression_share "
            f"FROM campaign WHERE {rng} AND campaign.status != 'REMOVED'", access=access)
        camps = {}
        for r in rows:
            c, m = r.get("campaign", {}), r.get("metrics", {})
            name = c.get("name")
            e = camps.setdefault(name, {"status": c.get("status"), "cost": 0.0,
                                        "clicks": 0, "impressions": 0, "conv_by_action": {}})
            e["cost"] += float(m.get("costMicros", 0)) / 1e6
            e["clicks"] += int(float(m.get("clicks", 0)))
            e["impressions"] += int(float(m.get("impressions", 0)))
            if m.get("searchImpressionShare") is not None:
                e["impression_share"] = m.get("searchImpressionShare")
            if m.get("searchBudgetLostImpressionShare") is not None:
                e["lost_is_budget"] = m.get("searchBudgetLostImpressionShare")
        conv = ga.search(
            "SELECT campaign.name, segments.conversion_action_name, metrics.conversions "
            f"FROM campaign WHERE {rng} AND metrics.conversions > 0", access=access)
        for r in conv:
            name = r.get("campaign", {}).get("name")
            action = r.get("segments", {}).get("conversionActionName")
            val = round(float(r.get("metrics", {}).get("conversions", 0)), 1)
            if name in camps:
                camps[name]["conv_by_action"][action] = \
                    round(camps[name]["conv_by_action"].get(action, 0) + val, 1)
        for e in camps.values():
            e["cost"] = round(e["cost"], 2)
            e["cpc"] = round(e["cost"] / e["clicks"], 2) if e["clicks"] else None
        return {k: v for k, v in camps.items() if v["cost"] > 0 or v["clicks"] > 0}

    w = window(week_start.date(), week_end.date())
    p = window(week_start.date() - dt.timedelta(days=7), week_end.date() - dt.timedelta(days=7))
    return {
        "week": w, "prev_week": p,
        "total_cost_week": round(sum(c["cost"] for c in w.values()), 2),
        "total_cost_prev_week": round(sum(c["cost"] for c in p.values()), 2),
    }


# ---------- Meta Ads ----------

def pull_meta(week_start: dt.datetime, week_end: dt.datetime) -> dict:
    ma = _import(ROOT / "ads" / "meta" / "meta_ads.py", "meta_ads_puller")
    ma.load_env()

    def window(d1: dt.date, d2: dt.date) -> dict:
        rows = ma.insights("campaign", str(d1), str(d2), "all_days")
        camps = {}
        for r in rows:
            actions = {a["action_type"]: float(a["value"]) for a in r.get("actions", [])}
            leads = actions.get("lead") or actions.get("offsite_conversion.fb_pixel_lead") or 0
            camps[r.get("campaign_name")] = {
                "spend": round(float(r.get("spend", 0)), 2),
                "impressions": int(r.get("impressions", 0)),
                "clicks": int(r.get("clicks", 0)),
                "ctr": round(float(r.get("ctr", 0)), 2),
                "leads": leads,
                "actions": actions,
            }
        return camps

    w = window(week_start.date(), week_end.date())
    p = window(week_start.date() - dt.timedelta(days=7), week_end.date() - dt.timedelta(days=7))
    return {
        "week": w, "prev_week": p,
        "total_spend_week": round(sum(c["spend"] for c in w.values()), 2),
        "total_spend_prev_week": round(sum(c["spend"] for c in p.values()), 2),
    }


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--week", help="Semaine ISO, ex. 2026-W36. Defaut : derniere semaine complete.")
    ap.add_argument("--no-ads", action="store_true", help="HubSpot uniquement")
    args = ap.parse_args()

    week_start, week_end = week_bounds(args.week)
    out = {
        "window": {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "label": f"semaine du {week_start.strftime('%d/%m')} au {week_end.strftime('%d/%m')}",
        }
    }
    for key, fn in [("hubspot", pull_hubspot)] + ([] if args.no_ads else
                                                  [("google_ads", pull_google), ("meta_ads", pull_meta)]):
        try:
            out[key] = fn(week_start, week_end)
        except Exception as e:  # chaque bloc echoue independamment
            out[key] = {"error": f"{type(e).__name__}: {e}"}
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
