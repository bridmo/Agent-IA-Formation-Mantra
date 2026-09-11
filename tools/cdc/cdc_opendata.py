#!/usr/bin/env python3
"""Client open data Caisse des Dépôts (Opendatasoft Explore API v2.1).

Datasets {{LABEL_FINANCEMENT}} utiles :
  - moncompteformation_catalogueformation   : offre de formation (220k) — prix, OF, certifs
  - moncompteformation_formations_engagees  : dossiers engagés (2,1M) — volume, prix moyen, financeurs
  - entree_sortie_formation                 : entrées/sorties par OF et par mois (778k)
  - moncompteformation-les-usagers          : profils usagers (âge, sexe, situation)

Usage :
  python3 cdc_opendata.py fields <dataset>
  python3 cdc_opendata.py query <dataset> --where "..." --group-by "..." --select "..." --limit N
  python3 cdc_opendata.py export <dataset> --where "..." --out fichier.csv
"""

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://opendata.caissedesdepots.fr/api/explore/v2.1/catalog/datasets"


def _get(url, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "{{SLUG}}-agent/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                raise
            sys.stderr.write(f"retry {attempt + 1} after {e}\n")
            time.sleep(2 * (attempt + 1))


def query(dataset, where=None, group_by=None, select=None, order_by=None, limit=100, offset=0):
    params = {"limit": limit, "offset": offset}
    if where:
        params["where"] = where
    if group_by:
        params["group_by"] = group_by
    if select:
        params["select"] = select
    if order_by:
        params["order_by"] = order_by
    url = f"{BASE}/{dataset}/records?" + urllib.parse.urlencode(params)
    data = json.loads(_get(url))
    if "error_code" in data:
        raise SystemExit(f"API error: {data.get('message')}")
    return data


def query_all(dataset, where=None, group_by=None, select=None, order_by=None, page=100, cap=10000):
    """Pagine jusqu'à cap résultats (limite ODS : offset+limit <= 10000)."""
    out = []
    offset = 0
    while offset < cap:
        d = query(dataset, where, group_by, select, order_by, limit=min(page, cap - offset), offset=offset)
        rows = d.get("results", [])
        out.extend(rows)
        if len(rows) < page:
            break
        offset += page
    return out


def export_csv(dataset, out_path, where=None, select=None, order_by=None):
    """Export bulk (pas de limite 10k) via /exports/csv."""
    params = {"delimiter": ";", "with_bom": "true"}
    if where:
        params["where"] = where
    if select:
        params["select"] = select
    if order_by:
        params["order_by"] = order_by
    url = f"{BASE}/{dataset}/exports/csv?" + urllib.parse.urlencode(params)
    blob = _get(url)
    with open(out_path, "wb") as f:
        f.write(blob)
    return len(blob)


def fields(dataset):
    d = json.loads(_get(f"{BASE}/{dataset}"))
    return [(f["name"], f["type"]) for f in d.get("fields", [])]


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    pf = sub.add_parser("fields")
    pf.add_argument("dataset")

    pq = sub.add_parser("query")
    pq.add_argument("dataset")
    pq.add_argument("--where")
    pq.add_argument("--group-by")
    pq.add_argument("--select")
    pq.add_argument("--order-by")
    pq.add_argument("--limit", type=int, default=100)
    pq.add_argument("--all", action="store_true", help="pagine jusqu'à 10k")

    pe = sub.add_parser("export")
    pe.add_argument("dataset")
    pe.add_argument("--where")
    pe.add_argument("--select")
    pe.add_argument("--order-by")
    pe.add_argument("--out", required=True)

    a = p.parse_args()

    if a.cmd == "fields":
        for n, t in fields(a.dataset):
            print(f"{n}\t{t}")
    elif a.cmd == "query":
        if a.all:
            rows = query_all(a.dataset, a.where, a.group_by, a.select, a.order_by)
            print(json.dumps({"count": len(rows), "results": rows}, ensure_ascii=False, indent=2))
        else:
            d = query(a.dataset, a.where, a.group_by, a.select, a.order_by, a.limit)
            print(json.dumps(d, ensure_ascii=False, indent=2))
    elif a.cmd == "export":
        n = export_csv(a.dataset, a.out, a.where, a.select, a.order_by)
        print(f"{n} bytes -> {a.out}")


if __name__ == "__main__":
    main()
