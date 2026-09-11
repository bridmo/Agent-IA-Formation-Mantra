#!/usr/bin/env python3
"""
check_title.py — Vérifie le titre (H1) d'un article {{COMPANY}}.

Checks déterministes :
  - H1 présent
  - Longueur ≤ 60 chars (warning 60-70, fail >70)
  - Action verb en tête (ou nom d'outil en première position)
  - Pas de verbe descriptif en tête (Comment, Découvrez, Apprenez)
  - Keyword principal présent (si --keyword fourni)
  - Pas d'année dans le slug (si --slug fourni)

Usage:
  python3 check_title.py <article.md>
  python3 check_title.py <article.md> --keyword "veille marketing"
  python3 check_title.py <article.md> --slug "automatiser-veille-marketing-ia"
  python3 check_title.py <article.md> --json

Exit: 0 pass, 1 fail, 2 invocation error.
"""

import json
import re
import sys
from pathlib import Path

ACTION_VERBS = [
    "automatiser", "maîtriser", "déployer", "construire", "décoder",
    "doubler", "diviser", "produire", "scaler", "passer", "basculer",
    "transformer", "orchestrer", "industrialiser", "devenir", "capter",
    "choisir", "optimiser", "booster", "accélérer", "simplifier",
]

DESCRIPTIVE_VERBS = [
    "comment", "comprendre", "utiliser", "apprendre", "découvrir",
    "améliorer", "faire", "savoir", "qu'est-ce que",
]


def extract_h1(text):
    """First line starting with `# `."""
    for line in text.split("\n"):
        if line.startswith("# ") and not line.startswith("## "):
            return line[2:].strip()
    return None


def check(path, keyword=None, slug=None):
    text = path.read_text(encoding="utf-8")
    h1 = extract_h1(text)
    issues = []

    if not h1:
        return {
            "path": str(path),
            "h1": None,
            "pass": False,
            "issues_count": 1,
            "issues": [{
                "rule": "h1_present",
                "severity": "critical",
                "message": "Aucun H1 (`# ...`) trouvé.",
                "fix": "Ajouter un H1 en haut de l'article.",
            }],
        }

    length = len(h1)

    # 1. Longueur
    if length > 70:
        issues.append({
            "rule": "h1_too_long",
            "severity": "high",
            "value": length,
            "message": f"H1 {length} chars (max 70, cible ≤ 60).",
            "fix": "Raccourcir — tronqué en SERP au-delà de 60.",
        })
    elif length > 60:
        issues.append({
            "rule": "h1_long",
            "severity": "low",
            "value": length,
            "message": f"H1 {length} chars (cible ≤ 60).",
            "fix": "Si possible raccourcir — risque de troncature en SERP.",
        })

    # 2. Premier mot
    first_word = h1.split()[0] if h1.split() else ""
    first_word_clean = first_word.lower().strip(",:.")

    # Descriptive verb en tête = fail
    for dv in DESCRIPTIVE_VERBS:
        if first_word_clean == dv or h1.lower().startswith(dv + " "):
            issues.append({
                "rule": "descriptive_verb_head",
                "severity": "high",
                "value": first_word,
                "message": f"Verbe descriptif en tête : '{first_word}'.",
                "fix": f"Remplacer par un verbe d'action : {', '.join(ACTION_VERBS[:6])}...",
            })
            break

    # 3. Action verb ou nom propre en tête ? (non-strict, on ne fail pas si absent, juste info)
    first_is_action = first_word_clean in ACTION_VERBS
    # Nom propre = commence par majuscule (déjà le cas pour les noms d'outils)
    first_is_proper = first_word[0].isupper() and first_word_clean not in DESCRIPTIVE_VERBS

    if not first_is_action and not first_is_proper:
        issues.append({
            "rule": "action_verb_head",
            "severity": "low",
            "value": first_word,
            "message": f"Premier mot '{first_word}' : ni action verb ni nom propre.",
            "fix": "Vérifier que l'ouverture est forte.",
        })

    # 4. Keyword présent
    if keyword:
        if keyword.lower() not in h1.lower():
            issues.append({
                "rule": "keyword_missing_h1",
                "severity": "high",
                "keyword": keyword,
                "message": f"Keyword principal '{keyword}' absent du H1.",
                "fix": "Inclure le keyword principal dans le H1.",
            })

    # 5. Slug checks
    if slug:
        # Année dans le slug = fail
        if re.search(r"\b20\d{2}\b", slug):
            issues.append({
                "rule": "slug_has_year",
                "severity": "high",
                "slug": slug,
                "message": "Le slug contient une année.",
                "fix": "Retirer l'année du slug (doit pouvoir refresh sans changer l'URL).",
            })
        # Longueur slug
        word_count = len(slug.split("-"))
        if word_count > 5:
            issues.append({
                "rule": "slug_too_long",
                "severity": "medium",
                "value": word_count,
                "message": f"Slug {word_count} mots (cible 3-5).",
                "fix": "Raccourcir en retirant les filler words (comment, le, la, de, avec).",
            })
        # Accents ou caractères non-ASCII
        if not slug.isascii():
            issues.append({
                "rule": "slug_non_ascii",
                "severity": "high",
                "slug": slug,
                "message": "Le slug contient des caractères non-ASCII (accents).",
                "fix": "Retirer les accents.",
            })

    return {
        "path": str(path),
        "h1": h1,
        "h1_length": length,
        "slug": slug,
        "pass": len(issues) == 0,
        "issues_count": len(issues),
        "issues": issues,
    }


def print_human(result):
    p = result["path"]
    if result["h1"] is None:
        print(f"❌ {p} — pas de H1 trouvé")
        return
    status = "✅" if result["pass"] else "❌"
    print(f"{status} {p} — H1 {result['h1_length']} chars, {result['issues_count']} issue(s)")
    print(f"   H1: {result['h1']}")
    if result.get("slug"):
        print(f"   slug: {result['slug']}")
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

    keyword = None
    slug = None
    if "--keyword" in sys.argv:
        idx = sys.argv.index("--keyword")
        if idx + 1 < len(sys.argv):
            keyword = sys.argv[idx + 1]
    if "--slug" in sys.argv:
        idx = sys.argv.index("--slug")
        if idx + 1 < len(sys.argv):
            slug = sys.argv[idx + 1]

    result = check(path, keyword=keyword, slug=slug)

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_human(result)

    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
