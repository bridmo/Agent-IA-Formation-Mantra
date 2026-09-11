#!/usr/bin/env python3
"""
check_hook.py — Vérifie le hook d'un article {{COMPANY}}.

Basé sur les seuils du corpus baseline (skills/seo-writer/references/corpus-baseline.md).

Checks :
  - first_sentence_words ≤ 12 (cible), ≤ 20 (max)
  - first_non_rounded_number_position ≤ 3 phrases (chiffre précis tôt)
  - Pas d'ouverture corporate générique ("En 2026, l'IA...", "Dans un monde...", etc.)
  - Pas de promesse en phrase 1 ("À la fin de cet article...", "Dans ce guide,")

Usage:
  python3 check_hook.py <article.md>
  python3 check_hook.py <article.md> --json

Exit: 0 pass, 1 fail, 2 invocation error.
"""

import json
import re
import sys
from pathlib import Path


CORPORATE_OPENINGS = [
    "en 2026, l'ia",
    "en 2025, l'ia",
    "de nos jours",
    "à l'heure actuelle",
    "dans un monde où",
    "dans un monde de",
    "de plus en plus de",
    "aujourd'hui, l'ia",
    "l'intelligence artificielle est",
    "l'ia transforme",
    "l'ia révolutionne",
]

PROMISE_OPENINGS = [
    "à la fin de cet article",
    "dans ce guide,",
    "dans cet article,",
    "cet article va",
    "nous allons voir",
    "vous allez découvrir",
    "vous saurez à la fin",
]


def strip_code(text):
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    return text


def get_body(text):
    parts = re.split(r'\n---+\n', text, maxsplit=1)
    return parts[1] if len(parts) > 1 else text


def extract_paragraphs(body):
    body = strip_code(body)
    blocks = re.split(r'\n\s*\n', body)
    out = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if b.startswith('#') or b.startswith('|') or b.startswith('>'):
            continue
        if re.match(r'^[-*+]\s', b) or re.match(r'^\d+\.\s', b):
            continue
        if b.startswith('[IMAGE') or b.startswith('Alt text'):
            continue
        if re.match(r'^\*\*(Publié|Auteur|Mis à jour|Title SEO|Slug|Meta description|Keyword)', b):
            continue
        if re.match(r'^-{3,}$', b):
            continue
        out.append(b)
    return out


def split_sentences(text):
    sents = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sents if s.strip()]


def count_words(text):
    return len(text.split())


def is_precise_number(n):
    if 2020 <= n <= 2035:
        return True
    if n < 100:
        return True
    s = str(n)
    trailing = len(s) - len(s.rstrip('0'))
    return trailing < 2


def has_non_rounded_number(text):
    for num in re.findall(r'\b(\d+)\b', text):
        if is_precise_number(int(num)):
            return True
    return False


def check(path):
    text = path.read_text(encoding='utf-8')
    body = get_body(text)
    paragraphs = extract_paragraphs(body)

    issues = []

    if not paragraphs:
        return {
            "path": str(path),
            "pass": False,
            "issues_count": 1,
            "issues": [{"rule": "no_body", "severity": "critical", "message": "Aucun paragraphe narratif détecté."}],
        }

    # Scan first 5 paragraphs for opening sentences
    sentences = []
    for p in paragraphs[:5]:
        sentences.extend(split_sentences(p))

    if not sentences:
        return {
            "path": str(path),
            "pass": False,
            "issues_count": 1,
            "issues": [{"rule": "no_sentences", "severity": "critical", "message": "Aucune phrase détectée en tête d'article."}],
        }

    first = sentences[0]
    first_words = count_words(first)

    # Check 1: hook length
    if first_words > 20:
        issues.append({
            "rule": "hook_too_long",
            "severity": "high",
            "value": first_words,
            "sentence": first[:120],
            "message": f"Hook {first_words} mots (max 20, cible ≤ 12).",
            "fix": "Raccourcir. Un chiffre seul peut suffire (ex : '35 millions d'euros.').",
        })
    elif first_words > 12:
        issues.append({
            "rule": "hook_long",
            "severity": "medium",
            "value": first_words,
            "sentence": first[:120],
            "message": f"Hook {first_words} mots (cible ≤ 12).",
            "fix": "Si possible, raccourcir pour un effet staccato plus fort.",
        })

    # Check 2: precise number position
    first_num_pos = None
    for idx, s in enumerate(sentences):
        if has_non_rounded_number(s):
            first_num_pos = idx + 1
            break

    if first_num_pos is None:
        issues.append({
            "rule": "no_precise_number_in_hook",
            "severity": "high",
            "scanned": len(sentences),
            "message": f"Aucun chiffre précis non-arrondi dans les {len(sentences)} premières phrases.",
            "fix": "Ouvrir par un chiffre précis (non-arrondi) qui ancre la preuve dès la phrase 1-3.",
        })
    elif first_num_pos > 3:
        issues.append({
            "rule": "precise_number_too_late",
            "severity": "medium",
            "value": first_num_pos,
            "message": f"Premier chiffre précis en phrase #{first_num_pos} (cible ≤ #3).",
            "fix": "Remonter un chiffre chiffré dans les 3 premières phrases.",
        })

    # Check 3: generic corporate opening
    head_lower = first.lower()
    for opening in CORPORATE_OPENINGS:
        if opening in head_lower:
            issues.append({
                "rule": "generic_opening",
                "severity": "critical",
                "term": opening,
                "sentence": first[:120],
                "message": f"Ouverture corporate générique détectée : '{opening}'.",
                "fix": "Démarrer par un fait, un chiffre précis, ou une scène concrète.",
            })
            break

    # Check 4: promise in first sentence
    for opening in PROMISE_OPENINGS:
        if opening in head_lower[:60]:
            issues.append({
                "rule": "promise_in_first_sentence",
                "severity": "high",
                "term": opening,
                "sentence": first[:120],
                "message": f"Promesse en phrase 1 ('{opening}'). On accroche d'abord, on promet en phrase 2-3.",
                "fix": "Déplacer la promesse en phrase 2-3. Phrase 1 = hook concret (chiffre/fait/scène).",
            })
            break

    return {
        "path": str(path),
        "metrics": {
            "first_sentence": first[:120] + ("..." if len(first) > 120 else ""),
            "first_sentence_words": first_words,
            "first_precise_number_position": first_num_pos,
            "sentences_scanned": len(sentences),
        },
        "pass": len(issues) == 0,
        "issues_count": len(issues),
        "issues": issues,
    }


def print_human(result):
    p = result["path"]
    if "metrics" not in result:
        print(f"❌ {p}")
        for i in result.get("issues", []):
            print(f"  [{i['severity'].upper()}] {i['rule']}: {i['message']}")
        return
    m = result["metrics"]
    status = "✅" if result["pass"] else "❌"
    num_pos = m['first_precise_number_position'] if m['first_precise_number_position'] else "—"
    print(f"{status} {p} — hook {m['first_sentence_words']} mots | 1er chiffre pos {num_pos} | {result['issues_count']} issue(s)")
    print(f"   hook: {m['first_sentence']}")
    for i in result["issues"]:
        sev = i["severity"].upper()
        print(f"  [{sev}] {i['rule']}: {i['message']}")
        print(f"    fix: {i['fix']}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)

    result = check(path)

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_human(result)

    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
