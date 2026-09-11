#!/usr/bin/env python3
"""
check_voice.py — Vérifie les règles de voix de marque dans un article Markdown.

Checks déterministes :
  - Cadratins `—` : max 1 par article
  - Vouvoiement : 0 occurrence tu/ton/tes/toi/t'
  - Connecteurs académiques : par ailleurs, en outre, de surcroît, néanmoins...
  - Adverbes de remplissage : véritablement, réellement, particulièrement
  - Ouvertures corporate génériques
  - Triplets d'adjectifs (signature IA)

Usage:
  python3 check_voice.py <article.md>
  python3 check_voice.py <article.md> --json

Exit code: 0 si pass, 1 si issues found, 2 si erreur d'invocation.
"""

import json
import re
import sys
from pathlib import Path

BANNED_CONNECTORS = [
    "par ailleurs",
    "en outre",
    "de surcroît",
    "néanmoins",
    "il est important de noter",
    "dans le cadre de",
    "afin de maximiser",
    "il convient de noter",
    "il est à souligner",
    "on peut dire que",
]

BANNED_ADVERBS = ["véritablement", "réellement", "particulièrement"]

CORPORATE_OPENINGS = [
    "En 2026, l'IA",
    "En 2026 l'IA",
    "De nos jours",
    "À l'heure actuelle",
    "Dans un monde où",
    "De plus en plus de",
]

# Tutoiement patterns — word boundaries, case insensitive
TU_PATTERNS = [r"\btu\b", r"\bton\b", r"\btes\b", r"\btoi\b", r"\bt'"]


def strip_code_blocks(text):
    """Remove fenced code blocks and inline code to avoid false positives."""
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    return text


def check_article(path):
    raw = path.read_text(encoding="utf-8")
    text = strip_code_blocks(raw)
    issues = []

    # 1. Cadratins — exclure les lignes de headers (H1-H6)
    #    Les headers type "## Étape N —" sont une convention {{COMPANY}} structurelle, pas un tic IA.
    #    Seuils dérivés du corpus-baseline : médiane réf = 0.7/1000 mots, drift = 17.8/1000 mots
    body_lines = [l for l in text.split('\n') if not re.match(r'^#{1,6}\s', l)]
    body_without_headers = '\n'.join(body_lines)
    em_dashes = re.findall(r"—", body_without_headers)
    if len(em_dashes) > 5:
        issues.append({
            "rule": "cadratins",
            "severity": "high",
            "count": len(em_dashes),
            "message": f"{len(em_dashes)} cadratins hors headers (max 5, cible ≤ 1).",
            "fix": "Remplacer par virgule, point, ou parenthèses. Les headers type '## Étape N —' sont autorisés.",
        })
    elif len(em_dashes) > 1:
        issues.append({
            "rule": "cadratins",
            "severity": "medium",
            "count": len(em_dashes),
            "message": f"{len(em_dashes)} cadratins hors headers (cible ≤ 1).",
            "fix": "Remplacer par virgule, point, ou parenthèses. Les headers type '## Étape N —' sont autorisés.",
        })

    # 2. Vouvoiement — 0 tu/ton/tes/toi
    tu_matches = []
    for pattern in TU_PATTERNS:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            tu_matches.append(m.group())
    if tu_matches:
        issues.append({
            "rule": "vouvoiement",
            "severity": "critical",
            "count": len(tu_matches),
            "examples": tu_matches[:5],
            "message": f"{len(tu_matches)} occurrence(s) de tutoiement (tu/ton/tes/toi).",
            "fix": "Remplacer par vous/votre/vos.",
        })

    # 3. Connecteurs académiques
    for conn in BANNED_CONNECTORS:
        count = len(re.findall(rf"\b{re.escape(conn)}\b", text, re.IGNORECASE))
        if count > 0:
            issues.append({
                "rule": "connecteur_academique",
                "severity": "medium",
                "term": conn,
                "count": count,
                "message": f"'{conn}' trouvé {count} fois.",
                "fix": "Remplacer par et / mais / sauf que / le truc c'est que.",
            })

    # 4. Adverbes de remplissage
    for adv in BANNED_ADVERBS:
        count = len(re.findall(rf"\b{re.escape(adv)}\b", text, re.IGNORECASE))
        if count > 0:
            issues.append({
                "rule": "adverbe_remplissage",
                "severity": "low",
                "term": adv,
                "count": count,
                "message": f"'{adv}' trouvé {count} fois.",
                "fix": "Supprimer ou remplacer par quelque chose de précis.",
            })

    # 5. Ouvertures corporate génériques (sur les 500 premiers caractères)
    head = text[:500]
    for opening in CORPORATE_OPENINGS:
        if opening.lower() in head.lower():
            issues.append({
                "rule": "ouverture_generique",
                "severity": "high",
                "term": opening,
                "message": f"Ouverture générique détectée : '{opening}'.",
                "fix": "Démarrer par un chiffre précis non-arrondi, un fait, une scène.",
            })

    # 6. Triplets d'adjectifs type "rapide, efficace et performant"
    # Detection heuristique : 3 mots séparés par virgule+espace puis "et"
    triplet_pattern = r"\b([a-zéèàâêîôûç]+),\s+([a-zéèàâêîôûç]+)\s+et\s+([a-zéèàâêîôûç]+)\b"
    triplets = re.findall(triplet_pattern, text, re.IGNORECASE)
    # Filtre : on ne garde que si les 3 finissent en "e", "s", "ent" (heuristique adjectif)
    suspicious = [t for t in triplets if all(re.search(r"(e|s|ent|if|ive|able|eux|eur)$", w) for w in t)]
    if len(suspicious) > 0:
        issues.append({
            "rule": "triplet_adjectifs",
            "severity": "medium",
            "count": len(suspicious),
            "examples": [", ".join(t) for t in suspicious[:3]],
            "message": f"{len(suspicious)} triplet(s) d'adjectifs potentiels (signature IA).",
            "fix": "Remplacer par UN adjectif précis.",
        })

    return {
        "path": str(path),
        "pass": len(issues) == 0,
        "issues_count": len(issues),
        "issues": issues,
    }


def print_human(result):
    p = result["path"]
    if result["pass"]:
        print(f"✅ {p} — voix OK ({result['issues_count']} issues)")
        return
    print(f"❌ {p} — {result['issues_count']} issue(s)")
    for issue in result["issues"]:
        sev = issue["severity"].upper()
        print(f"  [{sev}] {issue['rule']}: {issue['message']}")
        if "examples" in issue:
            print(f"    ex: {issue['examples']}")
        print(f"    fix: {issue['fix']}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)

    result = check_article(path)

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_human(result)

    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
