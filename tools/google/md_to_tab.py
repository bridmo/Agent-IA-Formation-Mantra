#!/usr/bin/env python3
"""Rend un markdown simplifié dans un ONGLET précis d'un Google Doc (via compte de service).

Dialecte markdown supporté :
  # ...      -> Titre H1 (grande partie)
  ## ...     -> HEADING_4 (sous-section, style utilisé par {{OWNER}})
  ### ...    -> HEADING_5
  - ...      -> puce
  | a | b |  -> tableau (lignes consécutives ; ligne |---| ignorée)
  autre      -> paragraphe normal
  (le gras **...** est retiré ; mise en forme volontairement sobre)

Usage : python3 md_to_tab.py <DOC_ID> <TAB_ID> <fichier.md>
"""
import os, re, sys, socket, time
socket.setdefaulttimeout(120)
from google.oauth2 import service_account
from googleapiclient.discovery import build

KEY = os.environ.get("GOOGLE_SA_KEY", os.path.expanduser("~/.config/{{SLUG}}/service-account-key.json"))
docs = build("docs", "v1", credentials=service_account.Credentials
             .from_service_account_file(KEY, scopes=["https://www.googleapis.com/auth/documents"]),
             cache_discovery=False)

DOC, TAB, MDFILE = sys.argv[1], sys.argv[2], sys.argv[3]


def strip_md(s):
    return s.replace("**", "").rstrip()


def parse(md):
    """Retourne une liste de blocs : ('h1'|'h4'|'h5'|'bullets'|'para'|'table', payload)."""
    blocks, i, lines = [], 0, md.split("\n")
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1; continue
        if ln.startswith("| "):
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                row = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in row):  # ignore ligne séparatrice
                    rows.append([strip_md(c) for c in row])
                i += 1
            blocks.append(("table", rows)); continue
        if ln.startswith("- "):
            items = []
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                items.append(strip_md(lines[i].strip()[2:])); i += 1
            blocks.append(("bullets", items)); continue
        if ln.startswith("# "):   blocks.append(("h1", strip_md(ln[2:]))); i += 1; continue
        if ln.startswith("## "):  blocks.append(("h4", strip_md(ln[3:]))); i += 1; continue
        if ln.startswith("### "): blocks.append(("h5", strip_md(ln[4:]))); i += 1; continue
        blocks.append(("para", strip_md(ln))); i += 1
    return blocks


def tab_body(doc):
    for t in doc["tabs"]:
        if t["tabProperties"]["tabId"] == TAB:
            return t["documentTab"]["body"]["content"]
    sys.exit(f"onglet {TAB} introuvable")


def end_index():
    doc = docs.documents().get(documentId=DOC, includeTabsContent=True).execute()
    return tab_body(doc)[-1]["endIndex"] - 1


def batch(reqs):
    for attempt in range(4):
        try:
            docs.documents().batchUpdate(documentId=DOC, body={"requests": reqs}).execute()
            return
        except (socket.timeout, TimeoutError, OSError) as e:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))


def clear_tab():
    """Vide l'onglet cible (idempotence : ré-exécutable sans doublon)."""
    doc = docs.documents().get(documentId=DOC, includeTabsContent=True).execute()
    end = tab_body(doc)[-1]["endIndex"]
    if end > 2:
        batch([{"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end - 1, "tabId": TAB}}}])


STYLE = {"h1": "HEADING_1", "h4": "HEADING_4", "h5": "HEADING_5"}


def flush_text(chunk):
    """chunk = liste de (kind, text) où kind in h1/h4/h5/para/bullet. Insère + style en 2 batchs."""
    if not chunk:
        return
    start = end_index()
    text = "".join(t + "\n" for _, t in chunk)
    batch([{"insertText": {"location": {"index": start, "tabId": TAB}, "text": text}}])
    reqs, off = [], 0
    for kind, t in chunk:
        s, e = start + off, start + off + len(t) + 1
        if kind in STYLE:
            reqs.append({"updateParagraphStyle": {
                "range": {"startIndex": s, "endIndex": e, "tabId": TAB},
                "paragraphStyle": {"namedStyleType": STYLE[kind]},
                "fields": "namedStyleType"}})
        elif kind == "bullet":
            reqs.append({"createParagraphBullets": {
                "range": {"startIndex": s, "endIndex": e, "tabId": TAB},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        off += len(t) + 1
    if reqs:
        batch(reqs)


def insert_table(rows):
    start = end_index()
    r, c = len(rows), max(len(x) for x in rows)
    batch([{"insertTable": {"location": {"index": start, "tabId": TAB}, "rows": r, "columns": c}}])
    # re-fetch, trouver la dernière table, remplir cellules (du plus grand index au plus petit)
    doc = docs.documents().get(documentId=DOC, includeTabsContent=True).execute()
    tbls = [el for el in tab_body(doc) if el.get("table")]
    t = tbls[-1]["table"]
    inserts = []
    for ri, row in enumerate(t["tableRows"]):
        for ci, cell in enumerate(row["tableCells"]):
            val = rows[ri][ci] if ci < len(rows[ri]) else ""
            if val:
                idx = cell["content"][0]["startIndex"]
                inserts.append((idx, val))
    inserts.sort(key=lambda x: -x[0])
    batch([{"insertText": {"location": {"index": i, "tabId": TAB}, "text": v}} for i, v in inserts])


def main():
    md = open(MDFILE, encoding="utf-8").read()
    blocks = parse(md)
    clear_tab()
    chunk = []
    for kind, payload in blocks:
        if kind == "table":
            flush_text(chunk); chunk = []
            insert_table(payload)
        elif kind == "bullets":
            for it in payload:
                chunk.append(("bullet", it))
        else:
            chunk.append((kind, payload))
    flush_text(chunk)
    print(f"OK — {MDFILE} rendu dans l'onglet {TAB}")


if __name__ == "__main__":
    from googleapiclient.errors import HttpError
    try:
        main()
    except HttpError as e:
        sys.exit(f"Erreur API : {e}")
