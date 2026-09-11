"""HubSpot API client minimal pour le skill sales-weekly {{COMPANY}}.

Auth via Private App token stocké dans ~/.config/{{SLUG}}/.env
Pas de dépendance externe (urllib stdlib uniquement). Python 3.9+.

Usage:
    from hubspot import search_deals

    deals = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ", "value": STAGE["DEAL_GAGNE"]},
            {"propertyName": "closedate", "operator": "GTE", "value": since_ms},
        ],
        properties=["dealname", "amount", "source", "closedate"],
    )

Les IDs de pipeline et d'étapes viennent de pipeline.config.json (voir plus bas).
"""
from __future__ import annotations
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Iterable, List, Dict, Optional

API_BASE = "https://api.hubapi.com"
ENV_PATH = Path.home() / ".config" / "{{SLUG}}" / ".env"


def _load_token() -> str:
    """Read HUBSPOT_TOKEN from ~/.config/{{SLUG}}/.env"""
    if not ENV_PATH.exists():
        raise RuntimeError(
            f"Token file not found at {ENV_PATH}. "
            f"Create it with: echo 'HUBSPOT_TOKEN=pat-xxx' > {ENV_PATH} && chmod 600 {ENV_PATH}"
        )
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("HUBSPOT_TOKEN="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("HUBSPOT_TOKEN not found in env file")


_TOKEN = None


def _token() -> str:
    global _TOKEN
    if _TOKEN is None:
        _TOKEN = _load_token()
    return _TOKEN


def _post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        API_BASE + path,
        data=json.dumps(body).encode(),
        method="POST",
        headers={
            "Authorization": f"Bearer {_token()}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_err = e.read().decode() if e.fp else ""
        raise RuntimeError(f"HubSpot API {e.code} {e.reason}: {body_err}") from e


def search_deals(
    filters: list[dict],
    properties: list[str],
    sorts: list[dict] | None = None,
    limit: int = 100,
) -> list[dict]:
    """Search deals with auto-pagination. Returns flat list of deal records.

    Each deal record = {"id": str, "properties": {...}, "createdAt": str, "updatedAt": str}.

    filters: list of HubSpot filter dicts, ANDed within one filter group.
    properties: properties to return. Include "deal_currency_code" if asking "amount".
    sorts: optional [{"propertyName": str, "direction": "ASCENDING"|"DESCENDING"}].
    """
    all_results = []
    after = None
    while True:
        body = {
            "filterGroups": [{"filters": filters}],
            "properties": properties,
            "limit": limit,
        }
        if sorts:
            body["sorts"] = sorts
        if after:
            body["after"] = after
        data = _post("/crm/v3/objects/deals/search", body)
        all_results.extend(data.get("results", []))
        paging = data.get("paging", {}).get("next", {})
        after = paging.get("after")
        if not after:
            break
    return all_results


def _batch_assoc(from_object: str, to_object: str, ids: list) -> Dict[str, List[str]]:
    """V4 batch associations: from_object id → list of to_object IDs.

    Returns: {from_id: [to_id, ...]}
    """
    out: Dict[str, List[str]] = {fid: [] for fid in ids}
    if not ids:
        return out
    BATCH = 100
    for i in range(0, len(ids), BATCH):
        batch = ids[i : i + BATCH]
        try:
            data = _post(
                f"/crm/v4/associations/{from_object}/{to_object}/batch/read",
                {"inputs": [{"id": fid} for fid in batch]},
            )
            for r in data.get("results", []):
                fid = r["from"]["id"]
                for to in r.get("to", []):
                    out[fid].append(str(to["toObjectId"]))
        except RuntimeError:
            pass
    return out


def fetch_calls_for_deals(deal_ids: Iterable[str], via_contacts: bool = True) -> Dict[str, List[dict]]:
    """Fetch all calls associated with each deal (full call info: ts + duration).

    Union of two paths:
    - Direct: deal → calls
    - Indirect: deal → contacts → calls (if via_contacts=True, default)

    This catches calls logged on the contact record (which would be missed by direct-only).

    Returns: {deal_id: [{"id": str, "ts_ms": int, "duration_ms": int}, ...]} with deduplication.
    """
    from datetime import datetime
    deal_ids = list(deal_ids)
    if not deal_ids:
        return {}

    # 1) Direct deal → calls
    deal_to_calls = _batch_assoc("deal", "calls", deal_ids)

    # 2) Via contacts: deal → contacts, then contact → calls
    if via_contacts:
        deal_to_contacts = _batch_assoc("deal", "contacts", deal_ids)
        all_contact_ids = list({cid for cids in deal_to_contacts.values() for cid in cids})
        contact_to_calls = _batch_assoc("contact", "calls", all_contact_ids)
        # Merge: for each deal, add the calls of each associated contact
        for did, contact_ids in deal_to_contacts.items():
            for cid in contact_ids:
                deal_to_calls[did].extend(contact_to_calls.get(cid, []))

    # 3) Dedupe call IDs per deal
    deal_to_call_set: Dict[str, set] = {did: set(cids) for did, cids in deal_to_calls.items()}
    all_call_ids = list({cid for cset in deal_to_call_set.values() for cid in cset})

    if not all_call_ids:
        return {did: [] for did in deal_ids}

    # 4) Batch read calls (ts + duration + recording_url)
    call_meta: Dict[str, dict] = {}
    BATCH = 100
    for i in range(0, len(all_call_ids), BATCH):
        batch = all_call_ids[i : i + BATCH]
        try:
            data = _post(
                "/crm/v3/objects/calls/batch/read",
                {"inputs": [{"id": cid} for cid in batch],
                 "properties": ["hs_timestamp", "hs_call_duration", "hs_call_recording_url"]},
            )
            for r in data.get("results", []):
                props = r.get("properties", {})
                ts_str = props.get("hs_timestamp")
                dur_str = props.get("hs_call_duration")
                ts_ms = None
                if ts_str:
                    try:
                        ts_ms = int(datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp() * 1000)
                    except ValueError:
                        pass
                dur_ms = int(dur_str) if dur_str else 0
                call_meta[r["id"]] = {
                    "id": r["id"], "ts_ms": ts_ms, "duration_ms": dur_ms,
                    "recording_url": props.get("hs_call_recording_url"),
                }
        except RuntimeError:
            continue

    # 5) Assemble
    out = {}
    for did, cset in deal_to_call_set.items():
        out[did] = [call_meta[cid] for cid in cset if cid in call_meta]
    return out


def count_calls_per_deal(deal_ids: Iterable[str], start_ms: int, end_ms: int) -> Dict[str, int]:
    """Count calls logged on each deal between start_ms and end_ms.

    Uses V4 batch associations (1 call per 100 deals) + V3 batch read calls (1 call per 100 calls).
    Much faster than per-deal lookups (2*K API calls vs N*2 where N=nb deals).

    Returns: {deal_id: nb_calls}
    """
    from datetime import datetime
    deal_ids = list(deal_ids)
    if not deal_ids:
        return {}
    counts = {did: 0 for did in deal_ids}

    # Step 1: V4 batch associations deal → calls (max 100 inputs per batch)
    deal_to_call_ids: Dict[str, List[str]] = {did: [] for did in deal_ids}
    all_call_ids: set = set()
    BATCH = 100
    for i in range(0, len(deal_ids), BATCH):
        batch = deal_ids[i : i + BATCH]
        data = _post(
            "/crm/v4/associations/deal/calls/batch/read",
            {"inputs": [{"id": did} for did in batch]},
        )
        for r in data.get("results", []):
            did = r["from"]["id"]
            for to in r.get("to", []):
                cid = str(to["toObjectId"])
                deal_to_call_ids[did].append(cid)
                all_call_ids.add(cid)

    if not all_call_ids:
        return counts

    # Step 2: V3 batch read calls with timestamps (max 100 per batch)
    call_ts: Dict[str, str] = {}
    call_id_list = list(all_call_ids)
    for i in range(0, len(call_id_list), BATCH):
        batch = call_id_list[i : i + BATCH]
        data = _post(
            "/crm/v3/objects/calls/batch/read",
            {"inputs": [{"id": cid} for cid in batch], "properties": ["hs_timestamp"]},
        )
        for r in data.get("results", []):
            ts = r.get("properties", {}).get("hs_timestamp")
            if ts:
                call_ts[r["id"]] = ts

    # Step 3: count per deal, filter on window
    for did, cids in deal_to_call_ids.items():
        n = 0
        for cid in cids:
            ts = call_ts.get(cid)
            if not ts:
                continue
            try:
                ts_ms = int(datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() * 1000)
            except ValueError:
                continue
            if start_ms <= ts_ms <= end_ms:
                n += 1
        counts[did] = n

    return counts


# === Configuration du pipeline ===
# Les IDs HubSpot sont propres à CHAQUE portail : ils ne peuvent pas être livrés en dur.
# Copiez pipeline.config.example.json en pipeline.config.json et remplissez-le.
# Où trouver les IDs : Settings > Objects > Deals > Pipelines, l'ID est dans l'URL ;
# ou appelez GET /crm/v3/pipelines/deals avec votre token.
_CONFIG_PATH = Path(__file__).resolve().parent / "pipeline.config.json"

if not _CONFIG_PATH.exists():
    raise SystemExit(
        "Configuration manquante : "
        f"{_CONFIG_PATH.name}\n"
        "  cp pipeline.config.example.json pipeline.config.json\n"
        "  puis renseignez l'ID de votre pipeline et de vos étapes."
    )

_CFG = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))

PIPELINE_ID = _CFG["pipeline_id"]
# STAGE : nom logique (stable, utilisé par le code) -> ID HubSpot (propre à votre portail)
STAGE = {name: cfg["id"] for name, cfg in _CFG["stages"].items()}
# STAGE_LABEL : ID -> libellé lisible (affiché dans les rapports)
STAGE_LABEL = {cfg["id"]: cfg["label"] for cfg in _CFG["stages"].values()}
CLOSED_STAGES = [STAGE[n] for n in _CFG.get("closed_stages", [])]
QUALIF_STAGES = [STAGE[n] for n in _CFG.get("qualified_stages", [])]

STANDARD_DEAL_PROPS = [
    "dealname",
    "amount",
    "deal_currency_code",
    "hs_projected_amount_in_home_currency",
    "dealstage",
    "pipeline",
    "source",
    "utm_source",
    "hubspot_owner_id",
    "createdate",
    "closedate",
    "notes_next_activity_date",
    "hs_lastactivitydate",
    "num_contacted_notes",
]

# Dates d'entrée dans les étapes suivies (déclarées dans pipeline.config.json sous
# "tracked_stage_entries") : HubSpot expose une propriété hs_date_entered_<stage_id>.
STANDARD_DEAL_PROPS += [
    f"hs_date_entered_{STAGE[name]}"
    for name in _CFG.get("tracked_stage_entries", [])
    if name in STAGE
]


def _seven_days_ago_ms() -> str:
    """Timestamp en millisecondes d'il y a 7 jours (format attendu par HubSpot)."""
    import time
    return str(int((time.time() - 7 * 86400) * 1000))


if __name__ == "__main__":
    # Quick self-test
    print(f"Token loaded: {_token()[:15]}...")
    deals = search_deals(
        filters=[
            {"propertyName": "pipeline", "operator": "EQ", "value": PIPELINE_ID},
            {"propertyName": "dealstage", "operator": "EQ", "value": STAGE["DEAL_GAGNE"]},
            {"propertyName": "closedate", "operator": "GTE", "value": _seven_days_ago_ms()},
        ],
        properties=["dealname", "amount", "source", "closedate"],
        limit=10,
    )
    print(f"Deals closed-won this week: {len(deals)}")
    for d in deals[:3]:
        p = d["properties"]
        print(f"  {p['dealname']} — {p['amount']}€ — {p.get('source')}")
