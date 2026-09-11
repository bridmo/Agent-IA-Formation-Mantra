#!/usr/bin/env python3
"""
check_links.py — Vérifie le maillage interne d'un article {{COMPANY}}.

Checks déterministes :
  - Nombre de liens internes /blog/ : 3-5 (cible)
  - Pas d'anchor "click here" / "cliquez ici"
  - Chaque lien /blog/ pointe vers un slug existant (cross-check optional avec channels-seo.md)
  - Liens vers {{DOMAIN}}/formation-* présents (CTA produit)

Usage:
  python3 check_links.py <article.md>
  python3 check_links.py <article.md> --channels-seo <path>
  python3 check_links.py <article.md> --json

Exit: 0 pass, 1 fail, 2 invocation error.
"""

import json
import re
import sys
from pathlib import Path

GENERIC_ANCHORS = ["click here", "cliquez ici", "ici", "en savoir plus", "lire plus"]


def extract_markdown_links(text):
    """Return list of (anchor_text, url) tuples."""
    pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    return re.findall(pattern, text)


def extract_blog_slugs_from_channels(channels_path):
    """Parse channels-seo.md to extract list of existing blog slugs."""
    if not channels_path.exists():
        return None
    text = channels_path.read_text(encoding="utf-8")
    # Look for /blog/<slug> patterns
    slugs = set(re.findall(r"/blog/([a-z0-9\-]+)", text))
    return slugs


def check(path, channels_path=None):
    text = path.read_text(encoding="utf-8")
    links = extract_markdown_links(text)
    issues = []

    # Classify links
    internal_blog = []   # /blog/<slug>
    internal_formation = []  # /formation-*
    external = []

    for anchor, url in links:
        if "/blog/" in url:
            internal_blog.append((anchor, url))
        elif "/formation-" in url or "/bootcamp-" in url:
            internal_formation.append((anchor, url))
        elif url.startswith("http"):
            external.append((anchor, url))

    # 1. Internal blog links count (3-5 target)
    blog_count = len(internal_blog)
    if blog_count < 3:
        issues.append({
            "rule": "internal_blog_low",
            "severity": "high",
            "value": blog_count,
            "message": f"{blog_count} lien(s) internes /blog/ (cible 3-5).",
            "fix": "Ajouter des liens vers des articles du même cluster (voir channels/seo/inventaire.md).",
        })
    elif blog_count > 5:
        issues.append({
            "rule": "internal_blog_high",
            "severity": "low",
            "value": blog_count,
            "message": f"{blog_count} liens internes /blog/ (cible 3-5).",
            "fix": "Vérifier que chaque lien apporte vraiment de la valeur au lecteur.",
        })

    # 2. CTA formation présent ?
    if len(internal_formation) == 0:
        issues.append({
            "rule": "no_formation_cta",
            "severity": "medium",
            "message": "Aucun lien vers une LP formation.",
            "fix": "Ajouter un CTA naturel vers la formation pertinente (voir brain/offre.md).",
        })

    # 3. Generic anchors (click here, etc.)
    for anchor, url in links:
        if anchor.lower().strip() in GENERIC_ANCHORS:
            issues.append({
                "rule": "generic_anchor",
                "severity": "medium",
                "anchor": anchor,
                "url": url,
                "message": f"Anchor générique : '{anchor}'.",
                "fix": "Remplacer par un anchor descriptif (ex: 'notre comparatif n8n vs Make').",
            })

    # 4. Cross-check slugs existence si channels-seo.md fourni
    if channels_path:
        existing_slugs = extract_blog_slugs_from_channels(channels_path)
        if existing_slugs is not None:
            for anchor, url in internal_blog:
                m = re.search(r"/blog/([a-z0-9\-]+)", url)
                if m:
                    slug = m.group(1)
                    if slug not in existing_slugs:
                        issues.append({
                            "rule": "slug_not_found",
                            "severity": "high",
                            "anchor": anchor,
                            "slug": slug,
                            "message": f"Slug '/blog/{slug}' introuvable dans channels-seo.md.",
                            "fix": "Vérifier que l'article existe ou corriger le lien.",
                        })

    return {
        "path": str(path),
        "counts": {
            "internal_blog": len(internal_blog),
            "internal_formation": len(internal_formation),
            "external": len(external),
            "total": len(links),
        },
        "internal_blog": internal_blog,
        "internal_formation": internal_formation,
        "pass": len(issues) == 0,
        "issues_count": len(issues),
        "issues": issues,
    }


def print_human(result):
    p = result["path"]
    status = "✅" if result["pass"] else "❌"
    c = result["counts"]
    print(f"{status} {p} — {c['internal_blog']} blog | {c['internal_formation']} formation | {c['external']} external | {result['issues_count']} issue(s)")
    for issue in result["issues"]:
        sev = issue["severity"].upper()
        print(f"  [{sev}] {issue['rule']}: {issue['message']}")
        print(f"    fix: {issue['fix']}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)

    channels_path = None
    if "--channels-seo" in sys.argv:
        idx = sys.argv.index("--channels-seo")
        if idx + 1 < len(sys.argv):
            channels_path = Path(sys.argv[idx + 1])

    result = check(path, channels_path=channels_path)

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_human(result)

    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
