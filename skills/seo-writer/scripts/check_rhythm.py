#!/usr/bin/env python3
"""
check_rhythm.py — Vérifie le rythme d'un article {{COMPANY}}.

Basé sur les seuils du corpus baseline (skills/seo-writer/references/corpus-baseline.md).

Checks :
  - pct_single_sentence_paragraphs — cible ≥ 45 %, min 30 %, fail < 20 %
  - avg_paragraph_words — cible ≤ 28, warning > 32, fail > 40
  - Paragraphes trop longs (> 5 phrases) — flag individuel (murs de texte)
  - Compte les anaphores (3+ paragraphes consécutifs avec même mot d'ouverture) — info

Usage:
  python3 check_rhythm.py <article.md>
  python3 check_rhythm.py <article.md> --json
  python3 check_rhythm.py <article.md> --strict   (fail si <45 % paras 1-ph)

Exit: 0 pass, 1 fail, 2 invocation error.
"""

import json
import re
import statistics
import sys
from pathlib import Path


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


def detect_anaphoras(paragraphs):
    """3+ consecutive paragraphs starting with same 1st word (normalized)."""
    out = []
    i = 0
    while i < len(paragraphs):
        words = paragraphs[i].split()
        if not words:
            i += 1
            continue
        first = words[0].lower().strip(',.:;"`*_-')
        if len(first) < 2:
            i += 1
            continue
        j = i + 1
        while j < len(paragraphs):
            wj = paragraphs[j].split()
            if not wj:
                break
            fj = wj[0].lower().strip(',.:;"`*_-')
            if fj == first:
                j += 1
            else:
                break
        if j - i >= 3:
            out.append({"start_para": i, "length": j - i, "word": first})
            i = j
        else:
            i += 1
    return out


def check(path, strict=False):
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

    # Metric 1: % single-sentence paragraphs
    sent_counts = [len(split_sentences(p)) for p in paragraphs]
    single = sum(1 for c in sent_counts if c == 1)
    pct_single = (single / len(paragraphs) * 100)

    if pct_single < 20:
        issues.append({
            "rule": "rhythm_too_flat",
            "severity": "high",
            "value": round(pct_single, 1),
            "message": f"{pct_single:.1f} % de paragraphes à 1 phrase (minimum 30 %, cible 45 %).",
            "fix": "Fragmenter les idées-punch en paragraphes courts. Voir `brain/editorial-guide.md` §5.",
        })
    elif pct_single < 30:
        issues.append({
            "rule": "rhythm_low",
            "severity": "medium",
            "value": round(pct_single, 1),
            "message": f"{pct_single:.1f} % de paragraphes à 1 phrase (cible 45 %).",
            "fix": "Identifier 3-5 idées fortes à fragmenter en lignes distinctes.",
        })
    elif strict and pct_single < 45:
        issues.append({
            "rule": "rhythm_below_target",
            "severity": "low",
            "value": round(pct_single, 1),
            "message": f"{pct_single:.1f} % de paragraphes à 1 phrase (cible édition humaine : 45 %).",
            "fix": "Si le sujet s'y prête, fragmenter davantage les transitions fortes.",
        })

    # Metric 2: avg paragraph length
    p_lens = [count_words(p) for p in paragraphs]
    avg_words = statistics.mean(p_lens)

    if avg_words > 40:
        issues.append({
            "rule": "paragraphs_too_long",
            "severity": "high",
            "value": round(avg_words, 1),
            "message": f"Paragraphes moyens {avg_words:.1f} mots (max 40, cible ≤ 32).",
            "fix": "Réduire la longueur moyenne en splittant les paragraphes longs.",
        })
    elif avg_words > 32:
        issues.append({
            "rule": "paragraphs_long",
            "severity": "medium",
            "value": round(avg_words, 1),
            "message": f"Paragraphes moyens {avg_words:.1f} mots (cible ≤ 32).",
            "fix": "Optionnel — splitter les paragraphes longs pour améliorer le rythme.",
        })

    # Metric 3: oversized paragraphs
    over = [(i, c) for i, c in enumerate(sent_counts) if c > 5]
    if over:
        issues.append({
            "rule": "paragraphs_oversized",
            "severity": "medium",
            "count": len(over),
            "examples": [f"paragraphe #{i+1} = {c} phrases" for i, c in over[:3]],
            "message": f"{len(over)} paragraphe(s) avec > 5 phrases (mur de texte).",
            "fix": "Couper en paragraphes plus courts (1-3 phrases max par défaut).",
        })

    # Anaphoras (info, pas d'issue)
    anaphoras = detect_anaphoras(paragraphs)

    return {
        "path": str(path),
        "metrics": {
            "paragraphs_count": len(paragraphs),
            "pct_single_sentence_paragraphs": round(pct_single, 1),
            "avg_paragraph_words": round(avg_words, 1),
            "paragraphs_oversized_count": len(over),
            "anaphora_count": len(anaphoras),
        },
        "pass": len(issues) == 0,
        "issues_count": len(issues),
        "issues": issues,
    }


def print_human(result):
    p = result["path"]
    if "metrics" not in result:
        print(f"❌ {p} — pas de corps détecté")
        return
    m = result["metrics"]
    status = "✅" if result["pass"] else "❌"
    print(f"{status} {p} — {m['pct_single_sentence_paragraphs']}% paras 1-ph | {m['avg_paragraph_words']} mots/para moy | {m['anaphora_count']} anaphore(s) | {result['issues_count']} issue(s)")
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

    strict = "--strict" in sys.argv
    result = check(path, strict=strict)

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_human(result)

    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
