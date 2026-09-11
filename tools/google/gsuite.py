#!/usr/bin/env python3
"""Google Docs / Sheets / Slides / Drive via le compte de service {{COMPANY}} ({{GCP_PROJECT}}).

APIs activées sur le projet : Sheets, Slides, Docs, Drive.
→ le compte de service peut CRÉER des fichiers, ÉCRIRE dedans, et les PARTAGER.

Email du compte de service : {{SA_EMAIL}}
Clé : ~/.config/{{SLUG}}/service-account-key.json (surcharge via env GOOGLE_SA_KEY).

Deux façons de travailler :
  - CRÉER un fichier (Drive) puis le partager avec un email humain, ou
  - ÉDITER un fichier existant partagé (en Éditeur) avec le compte de service.

Commandes :
  whoami
  # Docs
  doc-create      --title T [--share EMAIL] [--role writer|reader]
  doc-append      --id ID --text 'texte'                       # insère à la fin
  doc-from-md     --file chemin.md --title T [--share EMAIL]    # markdown -> Google Doc formaté (Drive)
  # Sheets
  sheet-create    --title T [--share EMAIL]
  sheet-read      --id ID --range 'Feuille1!A1:D50'
  sheet-write     --id ID --range 'Feuille1!A1' --values-json '[["a","b"]]'
  sheet-append    --id ID --range 'Feuille1!A1' --values-json '[["x","y"]]'
  sheet-tabs      --id ID
  sheet-from-csv  --file chemin.csv --title T [--share EMAIL]   # csv -> Google Sheet (Drive)
  # Slides
  slides-create   --title T [--share EMAIL]
  slides-add-text --id ID --title 'Titre' --body 'Contenu'
  # Drive
  share           --id ID --email EMAIL [--role writer|reader] [--notify]

L'ID est dans l'URL : docs.google.com/{document|spreadsheets|presentation}/d/<ID>/edit
"""
import argparse
import json
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

KEY_PATH = os.environ.get(
    "GOOGLE_SA_KEY",
    os.path.expanduser("~/.config/{{SLUG}}/service-account-key.json"),
)
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/presentations",
    "https://www.googleapis.com/auth/drive",
]


# Le compte de service n'a pas de quota Drive propre → pour CRÉER des fichiers,
# il faut usurper un utilisateur du domaine (domain-wide delegation) : définir
# GOOGLE_SA_SUBJECT={{OWNER_EMAIL}} (les fichiers sont alors créés dans
# le Drive de cet utilisateur, avec son quota, et lui appartiennent).
SUBJECT = os.environ.get("GOOGLE_SA_SUBJECT")


def creds():
    if not os.path.exists(KEY_PATH):
        sys.exit(f"Clé introuvable : {KEY_PATH} (définir GOOGLE_SA_KEY)")
    c = service_account.Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
    if SUBJECT:
        c = c.with_subject(SUBJECT)
    return c


def svc(name, ver):
    return build(name, ver, credentials=creds(), cache_discovery=False)


def out(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def do_share(drive, file_id, email, role="writer", notify=False):
    drive.permissions().create(
        fileId=file_id, sendNotificationEmail=notify,
        body={"type": "user", "role": role, "emailAddress": email}).execute()


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("whoami")

    def with_share(p):
        p.add_argument("--share", default=None, help="email humain à qui partager")
        p.add_argument("--role", default="writer", choices=["writer", "reader"])
        return p

    p = with_share(sub.add_parser("doc-create")); p.add_argument("--title", required=True)
    p = sub.add_parser("doc-append"); p.add_argument("--id", required=True); p.add_argument("--text", required=True)
    p = sub.add_parser("doc-read"); p.add_argument("--id", required=True)
    p = sub.add_parser("doc-replace"); p.add_argument("--id", required=True); p.add_argument("--find", required=True); p.add_argument("--replace", required=True); p.add_argument("--match-case", action="store_true")
    p = with_share(sub.add_parser("doc-from-md")); p.add_argument("--file", required=True); p.add_argument("--title", required=True)

    p = with_share(sub.add_parser("sheet-create")); p.add_argument("--title", required=True)
    p = sub.add_parser("sheet-read"); p.add_argument("--id", required=True); p.add_argument("--range", required=True)
    p = sub.add_parser("sheet-write"); p.add_argument("--id", required=True); p.add_argument("--range", required=True); p.add_argument("--values-json", required=True)
    p = sub.add_parser("sheet-append"); p.add_argument("--id", required=True); p.add_argument("--range", required=True); p.add_argument("--values-json", required=True)
    p = sub.add_parser("sheet-tabs"); p.add_argument("--id", required=True)
    p = with_share(sub.add_parser("sheet-from-csv")); p.add_argument("--file", required=True); p.add_argument("--title", required=True)

    p = with_share(sub.add_parser("slides-create")); p.add_argument("--title", required=True)
    p = sub.add_parser("slides-add-text"); p.add_argument("--id", required=True); p.add_argument("--title", default=""); p.add_argument("--body", default="")

    p = sub.add_parser("share"); p.add_argument("--id", required=True); p.add_argument("--email", required=True); p.add_argument("--role", default="writer", choices=["writer", "reader"]); p.add_argument("--notify", action="store_true")

    a = ap.parse_args()

    if a.cmd == "whoami":
        with open(KEY_PATH) as f:
            d = json.load(f)
        out({"client_email": d.get("client_email"), "project_id": d.get("project_id"),
             "key_path": KEY_PATH, "scopes": SCOPES})
        return

    # ---- Docs ----
    if a.cmd == "doc-create":
        docs = svc("docs", "v1")
        r = docs.documents().create(body={"title": a.title}).execute()
        fid = r["documentId"]
        if a.share:
            do_share(svc("drive", "v3"), fid, a.share, a.role)
        out({"documentId": fid, "url": f"https://docs.google.com/document/d/{fid}/edit", "shared_with": a.share})

    elif a.cmd == "doc-read":
        docs = svc("docs", "v1")
        doc = docs.documents().get(documentId=a.id).execute()
        buf = []
        for el in doc.get("body", {}).get("content", []):
            para = el.get("paragraph")
            if para:
                for e in para.get("elements", []):
                    t = e.get("textRun", {}).get("content")
                    if t:
                        buf.append(t)
            table = el.get("table")
            if table:
                for row in table.get("tableRows", []):
                    cells = []
                    for cell in row.get("tableCells", []):
                        ct = []
                        for ce in cell.get("content", []):
                            for e in ce.get("paragraph", {}).get("elements", []):
                                tt = e.get("textRun", {}).get("content", "")
                                if tt.strip():
                                    ct.append(tt.strip())
                        cells.append(" ".join(ct))
                    buf.append(" | ".join(cells) + "\n")
        print(doc.get("title", "")); print("=" * 40)
        print("".join(buf))

    elif a.cmd == "doc-replace":
        docs = svc("docs", "v1")
        r = docs.documents().batchUpdate(documentId=a.id, body={"requests": [
            {"replaceAllText": {"containsText": {"text": a.find, "matchCase": a.match_case},
                                "replaceText": a.replace}}]}).execute()
        occ = r.get("replies", [{}])[0].get("replaceAllText", {}).get("occurrencesChanged", 0)
        out({"find": a.find, "occurrencesChanged": occ})

    elif a.cmd == "doc-append":
        docs = svc("docs", "v1")
        doc = docs.documents().get(documentId=a.id).execute()
        end = doc["body"]["content"][-1]["endIndex"] - 1
        docs.documents().batchUpdate(documentId=a.id, body={"requests": [
            {"insertText": {"location": {"index": max(1, end)}, "text": a.text}}]}).execute()
        out({"ok": True, "insertedAt": max(1, end)})

    elif a.cmd == "doc-from-md":
        drive = svc("drive", "v3")
        media = MediaFileUpload(a.file, mimetype="text/markdown", resumable=False)
        r = drive.files().create(
            body={"name": a.title, "mimeType": "application/vnd.google-apps.document"},
            media_body=media, fields="id").execute()
        fid = r["id"]
        if a.share:
            do_share(drive, fid, a.share, a.role)
        out({"documentId": fid, "url": f"https://docs.google.com/document/d/{fid}/edit", "shared_with": a.share})

    # ---- Sheets ----
    elif a.cmd == "sheet-create":
        r = svc("sheets", "v4").spreadsheets().create(body={"properties": {"title": a.title}}).execute()
        fid = r["spreadsheetId"]
        if a.share:
            do_share(svc("drive", "v3"), fid, a.share, a.role)
        out({"spreadsheetId": fid, "url": r["spreadsheetUrl"], "shared_with": a.share})

    elif a.cmd == "sheet-read":
        r = svc("sheets", "v4").spreadsheets().values().get(spreadsheetId=a.id, range=a.range).execute()
        out(r.get("values", []))

    elif a.cmd == "sheet-write":
        r = svc("sheets", "v4").spreadsheets().values().update(
            spreadsheetId=a.id, range=a.range, valueInputOption="USER_ENTERED",
            body={"values": json.loads(a.values_json)}).execute()
        out({"updatedCells": r.get("updatedCells"), "updatedRange": r.get("updatedRange")})

    elif a.cmd == "sheet-append":
        r = svc("sheets", "v4").spreadsheets().values().append(
            spreadsheetId=a.id, range=a.range, valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS", body={"values": json.loads(a.values_json)}).execute()
        out({"updates": r.get("updates")})

    elif a.cmd == "sheet-tabs":
        r = svc("sheets", "v4").spreadsheets().get(spreadsheetId=a.id).execute()
        out([{"title": s["properties"]["title"], "sheetId": s["properties"]["sheetId"]} for s in r.get("sheets", [])])

    elif a.cmd == "sheet-from-csv":
        drive = svc("drive", "v3")
        media = MediaFileUpload(a.file, mimetype="text/csv", resumable=False)
        r = drive.files().create(
            body={"name": a.title, "mimeType": "application/vnd.google-apps.spreadsheet"},
            media_body=media, fields="id").execute()
        fid = r["id"]
        if a.share:
            do_share(drive, fid, a.share, a.role)
        out({"spreadsheetId": fid, "url": f"https://docs.google.com/spreadsheets/d/{fid}/edit", "shared_with": a.share})

    # ---- Slides ----
    elif a.cmd == "slides-create":
        r = svc("slides", "v1").presentations().create(body={"title": a.title}).execute()
        fid = r["presentationId"]
        if a.share:
            do_share(svc("drive", "v3"), fid, a.share, a.role)
        out({"presentationId": fid, "url": f"https://docs.google.com/presentation/d/{fid}/edit", "shared_with": a.share})

    elif a.cmd == "slides-add-text":
        import uuid
        sl = svc("slides", "v1")
        sid = "s_" + uuid.uuid4().hex[:8]
        sl.presentations().batchUpdate(presentationId=a.id, body={"requests": [
            {"createSlide": {"objectId": sid, "slideLayoutReference": {"predefinedLayout": "TITLE_AND_BODY"}}}]}).execute()
        pres = sl.presentations().get(presentationId=a.id).execute()
        slide = next(s for s in pres["slides"] if s["objectId"] == sid)
        title_id = body_id = None
        for el in slide.get("pageElements", []):
            ph = el.get("shape", {}).get("placeholder", {})
            if ph.get("type") == "TITLE":
                title_id = el["objectId"]
            elif ph.get("type") in ("BODY", "SUBTITLE"):
                body_id = el["objectId"]
        reqs = []
        if a.title and title_id:
            reqs.append({"insertText": {"objectId": title_id, "text": a.title}})
        if a.body and body_id:
            reqs.append({"insertText": {"objectId": body_id, "text": a.body}})
        if reqs:
            sl.presentations().batchUpdate(presentationId=a.id, body={"requests": reqs}).execute()
        out({"slideId": sid, "ok": True})

    # ---- Drive ----
    elif a.cmd == "share":
        do_share(svc("drive", "v3"), a.id, a.email, a.role, a.notify)
        out({"ok": True, "shared": a.id, "with": a.email, "role": a.role})


if __name__ == "__main__":
    from googleapiclient.errors import HttpError
    try:
        main()
    except HttpError as e:
        status = getattr(e, "status_code", None) or getattr(e.resp, "status", "?")
        sys.exit(f"Erreur API ({status}) : {e}")
