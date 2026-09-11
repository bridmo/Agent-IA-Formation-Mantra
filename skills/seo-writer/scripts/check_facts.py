#!/usr/bin/env python3
"""
check_facts.py — Vérifie les faits produit cités dans un article vs brain/offre.md.

Checks déterministes :
  - Extrait les mentions de formations dans l'article
  - Extrait les durées/prix cités à proximité (±150 chars)
  - Cross-check avec formations.md (source de vérité)
  - Flag les incohérences (ex: article dit "6 semaines" pour IA Générative alors que formations.md dit 3 sem.)

Heuristique : sort toutes les mentions numériques près d'un nom de formation, à valider manuellement si la match n'est pas parfait.

Usage:
  python3 check_facts.py <article.md>
  python3 check_facts.py <article.md> --formations <path>
  python3 check_facts.py <article.md> --json

Exit: 0 pass, 1 warnings (non-bloquant si seulement des warnings), 2 invocation error.
"""

import json
import re
import sys
from pathlib import Path

DEFAULT_FORMATIONS_PATH = "brain/offre.md"


def parse_formations(formations_path):
    """Parse formations.md — extract {name: {duree, prix}} from the markdown table."""
    if not formations_path.exists():
        return {}
    text = formations_path.read_text(encoding="utf-8")

    formations = {}
    # Find markdown tables with Formation/Durée/Prix columns
    table_pattern = r"\|\s*([^|]+?)\s*\|\s*([0-9]+\s*semaines?|[0-9]+\s*sem\.?)\s*\|\s*([0-9\s]+\s*€)"
    for match in re.finditer(table_pattern, text, re.IGNORECASE):
        name = match.group(1).strip()
        duree = match.group(2).strip()
        prix = match.group(3).strip()
        # Normalize
        duree_weeks = int(re.search(r"(\d+)", duree).group(1))
        prix_euros = int(re.sub(r"[^\d]", "", prix))
        formations[name.lower()] = {
            "name": name,
            "duree_weeks": duree_weeks,
            "prix_euros": prix_euros,
            "duree_raw": duree,
            "prix_raw": prix,
        }
    return formations


def find_formation_mentions(article_text, formation_names):
    """Find positions of formation mentions in the article."""
    mentions = []
    for name_lower in formation_names:
        # Match full formation name, case insensitive
        for m in re.finditer(re.escape(name_lower), article_text, re.IGNORECASE):
            mentions.append({
                "name": name_lower,
                "position": m.start(),
                "matched": m.group(),
            })
    return mentions


def extract_context(text, position, radius=150):
    """Get text ±radius chars around position."""
    start = max(0, position - radius)
    end = min(len(text), position + radius)
    return text[start:end]


def check(path, formations_path):
    text = path.read_text(encoding="utf-8")
    formations = parse_formations(formations_path)

    issues = []
    warnings = []

    if not formations:
        warnings.append({
            "rule": "no_formations_parsed",
            "severity": "low",
            "message": f"Aucune formation parsée depuis {formations_path}. Check désactivé.",
            "fix": "Vérifier que formations.md contient une table Formation/Durée/Prix.",
        })
        return {
            "path": str(path),
            "formations_source": str(formations_path),
            "formations_found": [],
            "mentions_count": 0,
            "pass": True,
            "warnings": warnings,
            "issues": [],
            "issues_count": 0,
        }

    mentions = find_formation_mentions(text, list(formations.keys()))

    # For each mention, check nearby numbers
    checked = []
    for mention in mentions:
        ctx = extract_context(text, mention["position"], radius=150)
        source = formations[mention["name"]]

        # Find weeks mentioned near
        weeks_found = [int(m.group(1)) for m in re.finditer(r"(\d+)\s*semaines?\b", ctx, re.IGNORECASE)]
        prices_found = []
        for m in re.finditer(r"(\d[\d\s]{2,})\s*€", ctx):
            p = int(re.sub(r"\s", "", m.group(1)))
            if 100 <= p <= 10000:  # prix plausible de formation
                prices_found.append(p)

        mention_info = {
            "formation": source["name"],
            "source": {"duree_weeks": source["duree_weeks"], "prix_euros": source["prix_euros"]},
            "found_in_article": {"weeks": weeks_found, "prices_eur": prices_found},
        }
        checked.append(mention_info)

        # Flag mismatches
        for w in weeks_found:
            if w != source["duree_weeks"]:
                issues.append({
                    "rule": "duree_mismatch",
                    "severity": "high",
                    "formation": source["name"],
                    "article_value": f"{w} semaines",
                    "source_value": f"{source['duree_weeks']} semaines",
                    "message": f"Article cite '{w} semaines' près de '{source['name']}', source dit {source['duree_weeks']} semaines.",
                    "fix": f"Corriger : {source['name']} = {source['duree_weeks']} semaines.",
                })
        for p in prices_found:
            if p != source["prix_euros"]:
                issues.append({
                    "rule": "prix_mismatch",
                    "severity": "high",
                    "formation": source["name"],
                    "article_value": f"{p} €",
                    "source_value": f"{source['prix_euros']} €",
                    "message": f"Article cite '{p} €' près de '{source['name']}', source dit {source['prix_euros']} €.",
                    "fix": f"Corriger : {source['name']} = {source['prix_euros']} €.",
                })

    return {
        "path": str(path),
        "formations_source": str(formations_path),
        "formations_parsed": len(formations),
        "mentions_count": len(mentions),
        "checked": checked,
        "pass": len(issues) == 0,
        "issues_count": len(issues),
        "warnings_count": len(warnings),
        "issues": issues,
        "warnings": warnings,
    }


def print_human(result):
    p = result["path"]
    status = "✅" if result["pass"] else "❌"
    print(f"{status} {p} — {result['mentions_count']} mention(s) de formation, {result['issues_count']} issue(s)")
    for m in result.get("checked", []):
        print(f"   '{m['formation']}': source {m['source']['duree_weeks']}sem/{m['source']['prix_euros']}€")
        if m["found_in_article"]["weeks"] or m["found_in_article"]["prices_eur"]:
            print(f"      proximité: weeks={m['found_in_article']['weeks']}, prices={m['found_in_article']['prices_eur']}€")
    for issue in result["issues"]:
        sev = issue["severity"].upper()
        print(f"  [{sev}] {issue['rule']}: {issue['message']}")
        print(f"    fix: {issue['fix']}")
    for w in result.get("warnings", []):
        print(f"  [WARN] {w['rule']}: {w['message']}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)

    # Default: look for brain/offre.md at project root (two levels up from scripts/)
    formations_path = Path(__file__).parent.parent.parent.parent / "agents" / "formations.md"
    if "--formations" in sys.argv:
        idx = sys.argv.index("--formations")
        if idx + 1 < len(sys.argv):
            formations_path = Path(sys.argv[idx + 1])

    result = check(path, formations_path=formations_path)

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_human(result)

    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
