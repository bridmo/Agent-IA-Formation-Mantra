#!/usr/bin/env python3
"""Fetch Google Search Console data directly via API for {{DOMAIN}}.

Usage:
  python3 fetch_gsc.py YYYY-MM-DD YYYY-MM-DD [--compare YYYY-MM-DD YYYY-MM-DD]

Outputs JSON files in agents/gsc-data/:
  - performance-{start}-{end}.json     totals + daily
  - pages-{start}-{end}.json           top 500 pages
  - queries-{start}-{end}.json         top 500 queries
  - pages+queries-{start}-{end}.json   page x query combos top 1000

Identifiants lus dans l'environnement (voir .env.example). Jamais en dur dans ce fichier :
  GOOGLE_CLIENT_ID
  GOOGLE_CLIENT_SECRET
  GOOGLE_REFRESH_TOKEN
  SEARCH_CONSOLE_SITE_URL  (defaults to sc-domain:{{DOMAIN}})

Ces valeurs ne doivent jamais être commitées : .env est ignoré par git.
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

# Racine du repo, déduite de l'emplacement de ce fichier
REPO_ROOT = Path(__file__).resolve().parents[2]


# Identifiants : UNIQUEMENT depuis l'environnement. Aucune valeur par défaut en dur.
# Le script s'arrête net si une variable manque, plutôt que de tourner avec un secret commité.
def _env(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise SystemExit(
            f"Variable d'environnement manquante : {name}\n"
            "  Renseignez-la dans .env (ignoré par git), jamais dans ce fichier.\n"
            "  Variables requises : GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN."
        )
    return v


CLIENT_ID = _env("GOOGLE_CLIENT_ID")
CLIENT_SECRET = _env("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN = _env("GOOGLE_REFRESH_TOKEN")
SITE_URL = os.environ.get("SEARCH_CONSOLE_SITE_URL", "sc-domain:{{DOMAIN}}")

OUT_DIR = str(REPO_ROOT / "channels/seo/gsc-data")
os.makedirs(OUT_DIR, exist_ok=True)


def get_access_token():
    """Exchange refresh_token for a fresh access_token."""
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read())
    return body["access_token"]


def gsc_query(access_token, body):
    """Call Search Console API searchAnalytics.query."""
    site_encoded = urllib.parse.quote(SITE_URL, safe="")
    url = f"https://searchconsole.googleapis.com/webmasters/v3/sites/{site_encoded}/searchAnalytics/query"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="ignore")
        print(f"  HTTP {e.code} : {err[:500]}")
        return None


def fetch_period(access_token, start_date, end_date, suffix):
    """Fetch performance / pages / queries / page+query for one period."""
    print(f"\n=== Period {start_date} to {end_date} ===")

    # 1. Totals (no dimensions)
    print("  totals...")
    totals = gsc_query(access_token, {
        "startDate": start_date,
        "endDate": end_date,
    })

    # 2. Daily performance
    print("  daily...")
    daily = gsc_query(access_token, {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["date"],
        "rowLimit": 1000,
    })
    perf_out = {"totals": totals, "daily": daily}
    with open(os.path.join(OUT_DIR, f"performance-{suffix}.json"), "w") as f:
        json.dump(perf_out, f, indent=2, ensure_ascii=False)

    # 3. Top pages
    print("  pages...")
    pages = gsc_query(access_token, {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["page"],
        "rowLimit": 500,
    })
    with open(os.path.join(OUT_DIR, f"pages-{suffix}.json"), "w") as f:
        json.dump(pages, f, indent=2, ensure_ascii=False)

    # 4. Top queries
    print("  queries...")
    queries = gsc_query(access_token, {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query"],
        "rowLimit": 500,
    })
    with open(os.path.join(OUT_DIR, f"queries-{suffix}.json"), "w") as f:
        json.dump(queries, f, indent=2, ensure_ascii=False)

    # 5. Page x query combo (for top pages drilldown)
    print("  page+query...")
    page_query = gsc_query(access_token, {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["page", "query"],
        "rowLimit": 1000,
    })
    with open(os.path.join(OUT_DIR, f"pages+queries-{suffix}.json"), "w") as f:
        json.dump(page_query, f, indent=2, ensure_ascii=False)

    # Summary
    if totals and "rows" in totals and totals["rows"]:
        t = totals["rows"][0]
        print(f"  TOTAL : {t['clicks']} clics | {t['impressions']} impressions | CTR {t['ctr']*100:.2f}% | position {t['position']:.2f}")
    elif totals:
        print(f"  TOTAL : pas de rows (probable 0 trafic)")


def main():
    if len(sys.argv) < 3:
        # Default : mai et avril 2026
        periods = [
            ("2026-05-01", "2026-05-31", "mai-2026"),
            ("2026-04-01", "2026-04-30", "avril-2026"),
        ]
    else:
        periods = [(sys.argv[1], sys.argv[2], f"{sys.argv[1]}_to_{sys.argv[2]}")]
        if "--compare" in sys.argv:
            idx = sys.argv.index("--compare")
            periods.append((sys.argv[idx+1], sys.argv[idx+2], f"{sys.argv[idx+1]}_to_{sys.argv[idx+2]}"))

    print(f"Fetching GSC data for {SITE_URL}")
    print(f"Periods: {[p[2] for p in periods]}")

    access_token = get_access_token()
    print(f"Access token obtained: {access_token[:30]}...")

    for start, end, suffix in periods:
        fetch_period(access_token, start, end, suffix)

    print(f"\nDONE. All files saved in {OUT_DIR}")


if __name__ == "__main__":
    main()
