#!/usr/bin/env python3
"""
drive_push.py — Pousse les articles .md locaux vers Google Drive en Google Docs.
Route automatiquement par statut Webflow : publié -> dossier Publiés, draft -> dossier IA SEO.

Auth : refresh token Drive (scope drive) + client OAuth des Ads, dans .env.

Usage :
  python3 drive_push.py                # publiés -> Publiés (défaut)
  python3 drive_push.py --drafts       # drafts/non publiés -> IA SEO
  python3 drive_push.py --all          # tout, routé par statut
  python3 drive_push.py --dry          # n'uploade rien, montre le routage
"""
import os, sys, json, re, glob, requests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
from webflow_deploy import WebflowDeployer, load_env
from pathlib import Path

# Racine du repo, déduite de l'emplacement de ce fichier
REPO_ROOT = Path(__file__).resolve().parents[3]

load_env()

BLOG_DIR = str(REPO_ROOT / "channels/content/blog")
FOLDER_DRAFTS = os.environ["GOOGLE_DRIVE_FOLDER_DRAFTS"]
FOLDER_PUB = os.environ["GOOGLE_DRIVE_FOLDER_PUBLISHED"]

# Déjà dans Drive (3 drafts manuels + 9 publiés) -> ne pas re-pousser
ALREADY_PUSHED_SLUGS = {
    "notebook-lm-marketing", "claude-artifacts-marketing", "ia-emploi-marketing",
    "agent-ia-definition", "agent-ia-seo", "chatgpt-gratuit-ou-payant-marketing",
    "chatgpt-vs-claude-marketing", "claude-skills-marketing", "formations-ia-marketing-gratuites",
    "ia-act-marketing", "prompt-engineering-marketing", "prompts-chatgpt-marketing",
}


def drive_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["GOOGLE_ADS_CLIENT_ID"],
        "client_secret": os.environ["GOOGLE_ADS_CLIENT_SECRET"],
        "refresh_token": os.environ["GOOGLE_DRIVE_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    })
    r.raise_for_status()
    return r.json()["access_token"]


def webflow_status_map():
    d = WebflowDeployer()
    out = {}
    offset = 0
    while True:
        r = requests.get(f"{d.base}/collections/{d.coll_id}/items",
                         headers={"Authorization": f"Bearer {d.token}"},
                         params={"limit": 100, "offset": offset})
        r.raise_for_status()
        p = r.json()
        for it in p.get("items", []):
            slug = it.get("fieldData", {}).get("slug")
            if slug:
                out[slug] = {"isDraft": it.get("isDraft", False), "isArchived": it.get("isArchived", False)}
        total = p.get("pagination", {}).get("total", 0)
        offset += len(p.get("items", []))
        if offset >= total or not p.get("items"):
            break
    return out


def extract(md_path):
    txt = open(md_path, encoding="utf-8").read()
    h1 = re.search(r'^#\s+(.+)$', txt, re.M)
    title = h1.group(1).strip() if h1 else os.path.basename(md_path).replace(".md", "")
    s = re.search(r'^\*\*Slug\s*:?\*\*\s*:?\s*(\S+)', txt, re.M | re.I)
    slug = None
    if s:
        slug = re.sub(r'^/?(blog/)?', '', s.group(1)).strip('/')
    return title, slug, txt


def upload_doc(title, content, folder, access):
    meta = {"name": title, "parents": [folder], "mimeType": "application/vnd.google-apps.document"}
    b = "===md2doc==="
    body = (f"--{b}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n" + json.dumps(meta) +
            f"\r\n--{b}\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n" + content +
            f"\r\n--{b}--")
    r = requests.post("https://www.googleapis.com/upload/drive/v3/files",
                      params={"uploadType": "multipart", "supportsAllDrives": "true"},
                      headers={"Authorization": f"Bearer {access}", "Content-Type": f"multipart/related; boundary={b}"},
                      data=body.encode("utf-8"))
    r.raise_for_status()
    return r.json()


def main():
    mode = "published"
    if "--drafts" in sys.argv: mode = "drafts"
    if "--all" in sys.argv: mode = "all"
    if "--dump" in sys.argv: mode = "dump"
    dry = "--dry" in sys.argv

    # Mode dump : tout le reste -> IA SEO, sans routage Webflow
    if mode == "dump":
        access = None if dry else drive_token()
        files = sorted(glob.glob(os.path.join(BLOG_DIR, "*.md")))
        rows = []
        pushed_slugs = set()
        for f in files:
            title, slug, txt = extract(f)
            base = os.path.basename(f)
            if slug and slug in ALREADY_PUSHED_SLUGS:
                rows.append((base, "déjà dans Drive", "skip")); continue
            if slug and slug in pushed_slugs:
                rows.append((base, "doublon slug", "skip")); continue
            if dry:
                rows.append((base, slug or "(sans slug)", "-> IA SEO (dry)"));
                if slug: pushed_slugs.add(slug)
                continue
            try:
                res = upload_doc(title, txt, FOLDER_DRAFTS, access)
                rows.append((base, slug or "(sans slug)", f"-> IA SEO OK ({res['id'][:10]}…)"))
                if slug: pushed_slugs.add(slug)
            except Exception as e:
                rows.append((base, slug or "(sans slug)", f"ERREUR {str(e)[:50]}"))
        print(f"{'fichier':52} | {'slug':38} | action")
        print("-" * 120)
        for b, s, a in rows:
            print(f"{b[:52]:52} | {str(s)[:38]:38} | {a}")
        return

    print("Fetching Webflow status map...")
    wf = webflow_status_map()
    print(f"  {len(wf)} items Webflow\n")

    # Collect files, dedupe by slug (prefer non -edited)
    files = sorted(glob.glob(os.path.join(BLOG_DIR, "*.md")))
    by_slug = {}
    no_slug = []
    for f in files:
        title, slug, txt = extract(f)
        if not slug:
            no_slug.append(os.path.basename(f)); continue
        is_edited = "-edited" in os.path.basename(f)
        if slug not in by_slug or (by_slug[slug]["edited"] and not is_edited):
            by_slug[slug] = {"file": f, "title": title, "txt": txt, "edited": is_edited}

    access = None if dry else drive_token()
    rows = []
    for slug, info in sorted(by_slug.items()):
        st = wf.get(slug)
        published = bool(st) and not st["isDraft"] and not st["isArchived"]
        status = "PUBLIÉ" if published else ("DRAFT" if st else "ABSENT-WF")
        # routing
        if mode == "published" and not published:
            rows.append((slug, status, "skip", os.path.basename(info["file"]))); continue
        if mode == "drafts" and published:
            rows.append((slug, status, "skip", os.path.basename(info["file"]))); continue
        if slug in ALREADY_PUSHED_SLUGS:
            rows.append((slug, status, "déjà poussé", os.path.basename(info["file"]))); continue
        folder = FOLDER_PUB if published else FOLDER_DRAFTS
        dest = "Publiés" if published else "IA SEO"
        if dry:
            rows.append((slug, status, f"-> {dest} (dry)", os.path.basename(info["file"]))); continue
        try:
            res = upload_doc(info["title"], info["txt"], folder, access)
            rows.append((slug, status, f"-> {dest} OK ({res['id'][:10]}…)", os.path.basename(info["file"])))
        except Exception as e:
            rows.append((slug, status, f"ERREUR {str(e)[:60]}", os.path.basename(info["file"])))

    print(f"{'slug':45} | {'statut':10} | action")
    print("-" * 110)
    for slug, status, action, fn in rows:
        print(f"{slug[:45]:45} | {status:10} | {action}")
    if no_slug:
        print(f"\nSans slug (ignorés) : {', '.join(no_slug)}")


if __name__ == "__main__":
    main()
