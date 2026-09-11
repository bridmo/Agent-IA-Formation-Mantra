#!/usr/bin/env python3
"""
pre_flight.py — Pre-flight check avant push Webflow (Phase A Step 1 de seo-deploy).

Orchestre les 7 scripts de seo-writer + vérifications additionnelles :
  - Frontmatter complet (Title SEO, Slug, Meta description, Keyword principal, Auteur)
  - Section FAQ présente (min 3 questions)
  - Les 7 checks seo-writer (voice, meta, title, links, facts, rhythm, hook)

Usage:
  python3 pre_flight.py <article.md>
  python3 pre_flight.py <article.md> --json
  python3 pre_flight.py <article.md> --strict   (fail si <45 % paras 1-phrase dans check_rhythm)

Exit: 0 pass, 1 fail, 2 invocation error.
"""

import json
import re
import subprocess
import sys
from pathlib import Path


# Paths auto-détectés depuis la position du script
# pre_flight.py dans skills/seo-deploy/scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
WRITER_SCRIPTS = PROJECT_ROOT / "skills" / "seo-writer" / "scripts"
CHANNELS_SEO = PROJECT_ROOT / "agents" / "channels-seo.md"
FORMATIONS = PROJECT_ROOT / "agents" / "formations.md"


def extract_metadata(text):
    """Extract frontmatter-like metadata from article body."""
    patterns = {
        "h1": r'^#\s+(.+?)$',
        "title_seo": r'^\*\*Title SEO\s*:?\s*\*\*\s*:?\s*(.+?)$',
        "slug": r'^\*\*Slug\s*:?\s*\*\*\s*:?\s*(.+?)$',
        "meta_description": r'^\*\*Meta description\s*:?\s*\*\*\s*:?\s*(.+?)$',
        "keyword_principal": r'^\*\*Keyword principal\s*:?\s*\*\*\s*:?\s*(.+?)$',
        "auteur": r'^\*\*Auteur(?: proposé)?\s*:?\s*\*\*\s*:?\s*(.+?)$',
    }
    out = {}
    for key, pat in patterns.items():
        m = re.search(pat, text, re.MULTILINE | re.IGNORECASE)
        out[key] = m.group(1).strip() if m else None
    return out


def check_frontmatter(meta):
    required = ["h1", "title_seo", "slug", "meta_description", "keyword_principal", "auteur"]
    return [k for k in required if not meta.get(k)]


def check_faq(text):
    faq_match = re.search(r'^##[ \t]+FAQ(?:[ \t]*:[^\n]+)?[ \t]*$', text, re.MULTILINE | re.IGNORECASE)
    if not faq_match:
        return {"present": False, "question_count": 0}
    faq_text = text[faq_match.end():]
    next_h2 = re.search(r'\n##\s+', faq_text)
    if next_h2:
        faq_text = faq_text[:next_h2.start()]
    # SEO Writer uses H3 questions; older articles use standalone bold questions.
    questions = re.findall(r'^(?:###[ \t]+[^\n]+\?|\*\*[^*\n]+\?\*\*)[ \t]*$', faq_text, re.MULTILINE)
    return {"present": True, "question_count": len(questions)}


def run_script(script_name, article, extra_args=None):
    script_path = WRITER_SCRIPTS / script_name
    if not script_path.exists():
        return (False, 0, {"error": f"Script introuvable : {script_path}"})
    args = ["python3", str(script_path), str(article), "--json"]
    if extra_args:
        args.extend(extra_args)
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        if result.stdout:
            data = json.loads(result.stdout)
            return (data.get("pass", False), data.get("issues_count", 0), data)
        return (False, 0, {"error": result.stderr or "no output"})
    except Exception as e:
        return (False, 0, {"error": str(e)})


def pre_flight(article_path, strict=False):
    if not article_path.exists():
        return {
            "path": str(article_path),
            "pass": False,
            "issues_count": 1,
            "issues": [{
                "rule": "file_missing",
                "severity": "critical",
                "message": f"Fichier introuvable : {article_path}",
            }],
        }

    text = article_path.read_text(encoding="utf-8")
    meta = extract_metadata(text)

    issues = []
    checks = {}

    # 1. Frontmatter
    missing = check_frontmatter(meta)
    checks["frontmatter"] = {"pass": not missing, "missing": missing}
    if missing:
        issues.append({
            "rule": "frontmatter_incomplete",
            "severity": "critical",
            "missing_fields": missing,
            "message": f"Frontmatter incomplet : {', '.join(missing)}.",
            "fix": "Compléter les champs manquants en tête du fichier.",
        })

    # 2. FAQ
    faq = check_faq(text)
    checks["faq"] = faq
    if not faq["present"]:
        issues.append({
            "rule": "faq_missing",
            "severity": "high",
            "message": "Section FAQ absente (H2 '## FAQ' introuvable).",
            "fix": "Ajouter une section FAQ avec 3-5 questions minimum.",
        })
    elif faq["question_count"] < 3:
        issues.append({
            "rule": "faq_insufficient",
            "severity": "medium",
            "count": faq["question_count"],
            "message": f"FAQ n'a que {faq['question_count']} question(s) (min 3).",
            "fix": "Ajouter des questions pour atteindre au moins 3.",
        })

    # 3. Scripts seo-writer
    keyword = meta.get("keyword_principal", "") or ""
    slug_raw = meta.get("slug", "") or ""
    slug_m = re.search(r"/blog/([a-z0-9\-]+)", slug_raw)
    slug = slug_m.group(1) if slug_m else slug_raw.lstrip("/")

    writer_checks = [
        ("check_voice.py", []),
        ("check_meta.py", ["--keyword", keyword] if keyword else []),
        ("check_title.py", (["--keyword", keyword] if keyword else []) + (["--slug", slug] if slug else [])),
        ("check_links.py", ["--channels-seo", str(CHANNELS_SEO)] if CHANNELS_SEO.exists() else []),
        ("check_facts.py", ["--formations", str(FORMATIONS)] if FORMATIONS.exists() else []),
        ("check_rhythm.py", ["--strict"] if strict else []),
        ("check_hook.py", []),
    ]

    for script_name, extra_args in writer_checks:
        key = script_name.replace(".py", "")
        passed, count, data = run_script(script_name, article_path, extra_args)
        checks[key] = {"pass": passed, "issues_count": count}
        if not passed and isinstance(data, dict) and "issues" in data:
            for sub in data["issues"]:
                issues.append({
                    "rule": f"{key}.{sub.get('rule', 'unknown')}",
                    "severity": sub.get("severity", "medium"),
                    "message": sub.get("message", ""),
                    "fix": sub.get("fix", ""),
                })

    return {
        "path": str(article_path),
        "metadata_extracted": meta,
        "checks": checks,
        "pass": len(issues) == 0,
        "issues_count": len(issues),
        "issues": issues,
    }


def print_human(result):
    p = result["path"]
    status = "✅" if result["pass"] else "❌"
    print(f"{status} {p} — {result['issues_count']} issue(s)")
    print()
    print("CHECK                    STATUS")
    print("-" * 45)
    for check_name, data in result.get("checks", {}).items():
        if check_name == "frontmatter":
            s = "✅ OK" if data.get("pass") else f"❌ missing: {','.join(data.get('missing', []))}"
            print(f"{check_name:<24} {s}")
        elif check_name == "faq":
            if not data.get("present"):
                print(f"{check_name:<24} ❌ absente")
            else:
                q = data.get("question_count", 0)
                s = "✅" if q >= 3 else "⚠️"
                print(f"{check_name:<24} {s} {q} question(s)")
        else:
            s = "✅" if data.get("pass") else "❌"
            ic = data.get("issues_count", 0)
            print(f"{check_name:<24} {s} ({ic} issue{'s' if ic != 1 else ''})")
    print()
    if result["issues"]:
        print("ISSUES DÉTAILLÉES:")
        for issue in result["issues"]:
            sev = issue["severity"].upper()
            print(f"  [{sev}] {issue['rule']}: {issue['message']}")
            if issue.get("fix"):
                print(f"    fix: {issue['fix']}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    article = Path(sys.argv[1])
    strict = "--strict" in sys.argv

    result = pre_flight(article, strict=strict)

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_human(result)

    sys.exit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
