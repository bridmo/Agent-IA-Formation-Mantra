#!/usr/bin/env python3
"""
Google Ads API puller (REST, no library) for {{COMPANY}}.
Creds in project .env. Connection verified on API v21 (2026-05).

Usage:
    python3 channels/paid/google-ads/google_ads.py            # default: campaigns last 30 days
    python3 channels/paid/google-ads/google_ads.py "<GAQL>"   # custom GAQL query -> raw JSON
"""
import sys, json, requests, os
# Racine du repo par recherche ascendante (robuste aux déplacements/symlinks — réorg 2026-08)
_d = os.path.dirname(os.path.realpath(__file__))
while _d != "/" and not os.path.isdir(os.path.join(_d, "skills", "seo-deploy")):
    _d = os.path.dirname(_d)
sys.path.insert(0, os.path.join(_d, "skills", "seo-deploy", "lib"))
from webflow_deploy import load_env
load_env()

API_VERSION = "v25"  # v21 déprécié (writes bloqués) le 2026-07-21 → bumpé v25 (dernière supportée)
CID = os.environ["GOOGLE_ADS_CUSTOMER_ID"]
MCC = os.environ["GOOGLE_ADS_LOGIN_CUSTOMER_ID"]
DEV = os.environ["GOOGLE_ADS_DEVELOPER_TOKEN"]

DEFAULT_QUERY = (
    "SELECT campaign.name, campaign.status, campaign.advertising_channel_type, "
    "metrics.cost_micros, metrics.impressions, metrics.clicks, metrics.conversions, "
    "metrics.conversions_value, metrics.average_cpc "
    "FROM campaign WHERE segments.date DURING LAST_30_DAYS "
    "AND campaign.status != 'REMOVED' "
    "ORDER BY metrics.cost_micros DESC"
)


def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_ADS_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    })
    r.raise_for_status()
    return r.json()["access_token"]


def search(query, access=None):
    """Run a GAQL query, return list of result rows (dicts)."""
    access = access or get_access_token()
    url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{CID}/googleAds:searchStream"
    headers = {
        "Authorization": f"Bearer {access}",
        "developer-token": DEV,
        "login-customer-id": MCC,
        "Content-Type": "application/json",
    }
    r = requests.post(url, headers=headers, json={"query": query})
    r.raise_for_status()
    rows = []
    for chunk in r.json():
        rows.extend(chunk.get("results", []))
    return rows


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_QUERY
    rows = search(query)
    if len(sys.argv) > 1:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    # Pretty print campaigns
    print(f"{len(rows)} campagnes (30j, hors REMOVED)\n")
    print(f"{'Campagne':45} | {'Statut':9} | {'Coût':>9} | {'Clics':>6} | {'Conv':>7} | {'CPA':>8}")
    print("-" * 100)
    for row in rows:
        c = row.get("campaign", {})
        m = row.get("metrics", {})
        cost = int(m.get("costMicros", 0)) / 1_000_000
        conv = float(m.get("conversions", 0))
        cpa = cost / conv if conv else 0
        print(f"{c.get('name','?')[:45]:45} | {c.get('status','?'):9} | {cost:8.2f}€ | {m.get('clicks','0'):>6} | {conv:7.1f} | {cpa:7.2f}€")


if __name__ == "__main__":
    main()
