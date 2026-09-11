#!/usr/bin/env python3
"""
Wisepops API puller (REST, lecture seule) pour {{COMPANY}}.

API Wisepops (api2) — doc : https://support.wisepops.com/en/articles/9897479-wisepops-api-documentation
  Base    : https://app.wisepops.com/api2/
  Auth    : header  Authorization: WISEPOPS-API key="<CLE>"
  Plan    : Pro et au-dessus. ~1 500 appels / 30 jours (relevable via Customer Success).
  Read-only : GET /contacts, GET /wisepops, GET/POST/DELETE /hooks, DELETE /data-privacy.
              ⚠️ AUCUN endpoint de création de contact ou de pop-up (voir README).

Clé API : variable d'env WISEPOPS_API_KEY, sinon lue dans ~/.config/{{SLUG}}/.env
(1 clé par site Wisepops — si plusieurs sites, exporter la bonne clé).

Usage :
    python3 tools/wisepops/wisepops.py contacts                       # tous les contacts (JSON)
    python3 tools/wisepops/wisepops.py contacts --wisepop-id <ID_POPUP>   # 1 pop-up
    python3 tools/wisepops/wisepops.py contacts --after 2026-05-01 --csv
    python3 tools/wisepops/wisepops.py performance                    # perf des pop-ups
    python3 tools/wisepops/wisepops.py hooks                          # webhooks configurés
"""
import sys
import os
import csv
import json
import argparse

try:
    import requests
except ImportError:
    sys.exit("Il faut le module `requests` (pip install requests).")

BASE = "https://app.wisepops.com/api2"


def load_api_key():
    """WISEPOPS_API_KEY depuis l'env, sinon depuis ~/.config/{{SLUG}}/.env."""
    key = os.environ.get("WISEPOPS_API_KEY")
    if key:
        return key.strip().strip('"').strip("'")
    env_path = os.path.expanduser("~/.config/{{SLUG}}/.env")
    if os.path.exists(env_path):
        with open(env_path) as fh:
            for line in fh:
                line = line.strip()
                if line.startswith("WISEPOPS_API_KEY"):
                    _, _, val = line.partition("=")
                    return val.strip().strip('"').strip("'")
    sys.exit(
        "Clé API introuvable. Exporte WISEPOPS_API_KEY ou ajoute une ligne\n"
        '  WISEPOPS_API_KEY="..."  dans ~/.config/{{SLUG}}/.env'
    )


def _headers(key):
    return {"Authorization": f'WISEPOPS-API key="{key}"'}


def _get(path, key, params=None):
    r = requests.get(f"{BASE}{path}", headers=_headers(key), params=params or {})
    if r.status_code == 401:
        sys.exit("401 : clé API refusée (mauvais site ou plan < Pro).")
    r.raise_for_status()
    return r.json()


def get_contacts(key, wisepop_id=None, after=None, page_size=1000, max_pages=100):
    """
    Récupère les contacts collectés. Pagination par `collected_after` :
    on avance le curseur sur le dernier collected_at de chaque page.
    (À confirmer sur données réelles : Wisepops peut exposer un token de page.)
    """
    out = []
    cursor = after
    for _ in range(max_pages):
        params = {"page_size": page_size}
        if wisepop_id:
            params["wisepop_id"] = wisepop_id
        if cursor:
            params["collected_after"] = cursor
        data = _get("/contacts", key, params)
        rows = data if isinstance(data, list) else data.get("contacts", data.get("data", []))
        if not rows:
            break
        out.extend(rows)
        if len(rows) < page_size:
            break
        last = rows[-1].get("collected_at")
        if not last or last == cursor:
            break  # garde-fou anti-boucle
        cursor = last
    return out


def flatten_contact(c):
    """Aplati la structure {collected_at, wisepop_id, ip, country_code, fields:{...}}."""
    flat = {
        "collected_at": c.get("collected_at"),
        "wisepop_id": c.get("wisepop_id"),
        "country_code": c.get("country_code") or c.get("country"),
        "ip": c.get("ip"),
    }
    fields = c.get("fields") or {}
    if isinstance(fields, dict):
        flat.update(fields)
    return flat


def cmd_contacts(args):
    key = load_api_key()
    contacts = get_contacts(
        key,
        wisepop_id=args.wisepop_id,
        after=args.after,
        page_size=args.page_size,
    )
    flat = [flatten_contact(c) for c in contacts]
    if args.csv:
        if not flat:
            return
        cols = []
        for row in flat:
            for k in row:
                if k not in cols:
                    cols.append(k)
        w = csv.DictWriter(sys.stdout, fieldnames=cols)
        w.writeheader()
        w.writerows(flat)
    else:
        print(json.dumps(flat, ensure_ascii=False, indent=2))
    print(f"\n{len(flat)} contacts.", file=sys.stderr)


def cmd_performance(args):
    key = load_api_key()
    print(json.dumps(_get("/wisepops", key), ensure_ascii=False, indent=2))


def cmd_hooks(args):
    key = load_api_key()
    print(json.dumps(_get("/hooks", key), ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description="Puller Wisepops (lecture seule).")
    sub = p.add_subparsers(dest="cmd", required=True)

    pc = sub.add_parser("contacts", help="Lister les contacts collectés")
    pc.add_argument("--wisepop-id", help="Filtrer sur un pop-up (ex. 604521)")
    pc.add_argument("--after", help="collected_after (UTC, ex. 2026-05-01 ou ISO)")
    pc.add_argument("--page-size", type=int, default=1000, help="1-1000 (défaut 1000)")
    pc.add_argument("--csv", action="store_true", help="Sortie CSV au lieu de JSON")
    pc.set_defaults(func=cmd_contacts)

    pp = sub.add_parser("performance", help="Perf des pop-ups (GET /wisepops)")
    pp.set_defaults(func=cmd_performance)

    ph = sub.add_parser("hooks", help="Lister les webhooks (GET /hooks)")
    ph.set_defaults(func=cmd_hooks)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
