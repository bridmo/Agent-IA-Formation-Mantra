#!/usr/bin/env python3
"""
check_meta.py — Vérifie la meta description d'un article {{COMPANY}}.

Checks déterministes :
  - Présence : une ligne `**Meta description:** ...` existe
  - Longueur : 150-160 caractères
  - Action verb en tête (liste blanche)
  - Pas de verbe mou en tête (Découvrez, Apprenez, Comprendre, Tout savoir)
  - Pas de point d'exclamation
  - Keyword principal présent (si --keyword fourni)
  - Différente de la première phrase de l'article

Usage:
  python3 check_meta.py <article.md>
  python3 check_meta.py <article.md> --keyword "veille marketing ia"
  python3 check_meta.py <article.md> --json

Exit: 0 pass, 1 fail, 2 invocation error.
"""

import json
import re
import sys
from pathlib import Path

ACTION_VERBS = [
    # Impératifs fort vouvoiement
    "déléguez", "automatisez", "récupérez", "divisez", "générez",
    "maîtrisez", "construisez", "déployez", "transformez", "orchestrez",
    "industrialisez", "doublez", "passez", "basculez", "scalez", "produisez",
    "décodez", "capturez", "optimisez", "boostez", "multipliez",
    "économisez", "raccourcissez", "simplifiez", "accélérez",
]

SOFT_VERBS = [
    "découvrez", "apprenez", "comprendre", "tout savoir", "apprenez à",
    "découvrez comment", "tout comprendre",
]


def extract_meta(text):
    """Extract meta description from article text. Returns str or None.

    Accepte les formats:
      - **Meta description:** ...
      - **Meta description :** ...
      - **Meta description** : ...
      - meta_description: "..." (frontmatter)
    """
    # Markdown bold with optional colon inside or outside
    m = re.search(
        r"^\*\*Meta description\s*:?\s*\*\*\s*:?\s*(.+?)$",
        text, re.MULTILINE | re.IGNORECASE,
    )
    if m:
        return m.group(1).strip()
    # Frontmatter YAML
    m = re.search(r"^meta_description:\s*[\"']?(.+?)[\"']?$", text, re.MULTILINE | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None


def first_sentence(text):
    """Return first meaningful sentence after H1."""
    # Strip H1 and empty lines, find first paragraph
    lines = text.split("\n")
    in_body = False
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            in_body = True
            continue
        if not in_body or not line:
            continue
        if line.startswith("**") or line.startswith("---"):
            continue
        # First content line → split on first period
        parts = re.split(r"(?<=[.!?])\s", line, maxsplit=1)
        return parts[0] if parts else line
    return ""


def check(path, keyword=None):
    text = path.read_text(encoding="utf-8")
    issues = []
    meta = extract_meta(text)

    if not meta:
        return {
            "path": str(path),
            "meta": None,
            "pass": False,
            "issues_count": 1,
            "issues": [{
                "rule": "meta_present",
                "severity": "critical",
                "message": "Aucune ligne `**Meta description:**` trouvée.",
                "fix": "Ajouter `**Meta description:** <texte 150-160 chars>` sous le H1.",
            }],
        }

    # 1. Longueur — plage 140-170 (dérivée du corpus-baseline : p20=144, p80=166 sur corpus référence)
    length = len(meta)
    if length < 140 or length > 170:
        issues.append({
            "rule": "meta_length",
            "severity": "high" if length < 130 or length > 180 else "medium",
            "value": length,
            "message": f"Longueur {length} chars (cible 140-170, optimum 150-160).",
            "fix": "Ajuster pour rentrer dans 140-170 chars (tronqué en SERP au-delà de 170).",
        })

    # 2. Premier mot = action verb ?
    first_word = meta.split()[0] if meta.split() else ""
    first_word_clean = first_word.lower().strip(",:.")
    if first_word_clean in SOFT_VERBS:
        issues.append({
            "rule": "soft_verb_head",
            "severity": "high",
            "value": first_word,
            "message": f"Verbe mou en tête : '{first_word}'.",
            "fix": f"Remplacer par un verbe d'action : {', '.join(ACTION_VERBS[:6])}...",
        })
    elif first_word_clean not in ACTION_VERBS:
        # Pas dans la liste — warning (peut être acceptable si nom propre d'outil, etc.)
        issues.append({
            "rule": "action_verb_head",
            "severity": "low",
            "value": first_word,
            "message": f"Premier mot '{first_word}' pas dans la liste des verbes d'action.",
            "fix": f"Vérifier manuellement. Suggestions : {', '.join(ACTION_VERBS[:6])}.",
        })

    # 3. Point d'exclamation interdit
    if "!" in meta:
        issues.append({
            "rule": "exclamation",
            "severity": "medium",
            "count": meta.count("!"),
            "message": f"{meta.count('!')} point(s) d'exclamation (sent le marketing pushy).",
            "fix": "Supprimer.",
        })

    # 4. Soft verbs n'importe où (moins strict que en tête)
    for sv in SOFT_VERBS:
        if re.search(rf"\b{re.escape(sv)}\b", meta, re.IGNORECASE):
            if sv.lower() != first_word_clean:  # already flagged above
                issues.append({
                    "rule": "soft_verb_anywhere",
                    "severity": "medium",
                    "term": sv,
                    "message": f"Verbe mou présent : '{sv}'.",
                    "fix": "Remplacer par un verbe d'action.",
                })

    # 5. Keyword présent si fourni
    if keyword:
        if keyword.lower() not in meta.lower():
            issues.append({
                "rule": "keyword_missing",
                "severity": "high",
                "keyword": keyword,
                "message": f"Keyword principal '{keyword}' absent de la meta.",
                "fix": "Inclure le keyword (bold en SERP).",
            })

    # 6. Meta ≠ première phrase de l'article
    fs = first_sentence(text)
    if fs and meta and fs[:80].lower().strip() == meta[:80].lower().strip():
        issues.append({
            "rule": "meta_duplicates_first_sentence",
            "severity": "medium",
            "message": "La meta description duplique la première phrase de l'article.",
            "fix": "Formuler différemment — le lecteur ne doit pas lire 2 fois la même phrase.",
        })

    return {
        "path": str(path),
        "meta": meta,
        "meta_length": length,
        "pass": len(issues) == 0,
        "issues_count": len(issues),
        "issues": issues,
    }


def print_human(result):
    p = result["path"]
    if result["meta"] is None:
        print(f"❌ {p} — pas de meta description trouvée")
        return
    status = "✅" if result["pass"] else "❌"
    print(f"{status} {p} — meta {result['meta_length']} chars, {result['issues_count']} issue(s)")
    print(f"   meta: {result['meta']}")
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
    if "--keyword" in sys.argv:
        idx = sys.argv.index("--keyword")
        if idx + 1 < len(sys.argv):
            keyword = sys.argv[idx + 1]

    result = check(path, keyword=keyword)

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_human(result)

    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
