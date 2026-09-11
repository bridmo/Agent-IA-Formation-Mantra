#!/usr/bin/env python3
"""
analyze_article_diff.py — Compare 2 versions d'un article (skill vs éditée humaine).

Phase C Step 2 de seo-deploy. Produit :
  - Diff titre et meta description
  - Diff H2s (ajoutés / retirés)
  - Diff liens (ajoutés / retirés)
  - Delta metrics (word_count, paragraphs, cadratins, pct_single_sentence_paragraphs, etc.)
  - Option --template : génère un squelette `feedback_<topic>.md` pré-rempli

Usage:
  python3 analyze_article_diff.py <skill.md> <edited.md>
  python3 analyze_article_diff.py <skill.md> <edited.md> --json
  python3 analyze_article_diff.py <skill.md> <edited.md> --template

Exit: 0 OK, 2 invocation error.
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


def extract_h1(text):
    m = re.search(r'^#\s+(.+?)$', text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def extract_meta_desc(text):
    m = re.search(r'^\*\*Meta description\s*:?\s*\*\*\s*:?\s*(.+?)$', text, re.MULTILINE | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def extract_h2s(text):
    body = get_body(text)
    return [h.strip() for h in re.findall(r'^##\s+(?!#)(.+?)$', body, re.MULTILINE)]


def extract_links(text):
    return re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', text)


def article_metrics(path):
    text = path.read_text(encoding="utf-8")
    body = get_body(text)
    body_stripped = strip_code(body)
    paragraphs = extract_paragraphs(body)
    p_lens = [count_words(p) for p in paragraphs]
    all_sentences = []
    for p in paragraphs:
        all_sentences.extend(split_sentences(p))

    h1 = extract_h1(text)
    meta = extract_meta_desc(text)
    h2s = extract_h2s(text)

    single_sent = sum(1 for p in paragraphs if len(split_sentences(p)) == 1)
    cadratins = len(re.findall(r'—', body_stripped))
    links = extract_links(body)
    internal_blog = [(a, u) for a, u in links if '/blog/' in u]
    formation = [(a, u) for a, u in links if '/formation-' in u or '/bootcamp-' in u]
    external = [(a, u) for a, u in links if u.startswith('http')]

    return {
        "h1": h1,
        "h1_length": len(h1),
        "meta": meta,
        "meta_length": len(meta),
        "h2s": h2s,
        "h2_count": len(h2s),
        "word_count": sum(p_lens),
        "paragraphs_count": len(paragraphs),
        "avg_paragraph_words": round(statistics.mean(p_lens), 1) if p_lens else 0,
        "pct_single_sentence_paragraphs": round((single_sent / len(paragraphs) * 100) if paragraphs else 0, 1),
        "sentences_count": len(all_sentences),
        "cadratins_total": cadratins,
        "internal_blog_links": len(internal_blog),
        "formation_links": len(formation),
        "external_links": len(external),
        "all_links": [(a, u) for a, u in links],
    }


def diff_lists(a, b):
    """Return (removed, added) for simple lists."""
    sa, sb = set(a), set(b)
    return ([x for x in a if x not in sb], [x for x in b if x not in sa])


def analyze_diff(skill_path, edited_path):
    skill = article_metrics(skill_path)
    edited = article_metrics(edited_path)

    removed_h2s, added_h2s = diff_lists(skill["h2s"], edited["h2s"])

    skill_urls = [u for _, u in skill["all_links"]]
    edited_urls = [u for _, u in edited["all_links"]]
    removed_urls, added_urls = diff_lists(skill_urls, edited_urls)

    deltas = {}
    for key in ["word_count", "h1_length", "meta_length", "h2_count", "paragraphs_count",
                "avg_paragraph_words", "pct_single_sentence_paragraphs", "sentences_count",
                "cadratins_total", "internal_blog_links", "formation_links", "external_links"]:
        s_val = skill.get(key, 0) or 0
        e_val = edited.get(key, 0) or 0
        delta = round(e_val - s_val, 1)
        delta_pct = round(((e_val - s_val) / s_val * 100) if s_val else 0, 1)
        deltas[key] = {"skill": s_val, "edited": e_val, "delta": delta, "delta_pct": delta_pct}

    return {
        "skill_file": str(skill_path),
        "edited_file": str(edited_path),
        "title": {
            "skill": skill["h1"],
            "edited": edited["h1"],
            "changed": skill["h1"] != edited["h1"],
        },
        "meta": {
            "skill": skill["meta"],
            "edited": edited["meta"],
            "skill_length": skill["meta_length"],
            "edited_length": edited["meta_length"],
            "changed": skill["meta"] != edited["meta"],
        },
        "h2s_diff": {"removed": removed_h2s, "added": added_h2s},
        "links_diff": {"removed_urls": sorted(set(removed_urls)), "added_urls": sorted(set(added_urls))},
        "metrics_delta": deltas,
    }


def print_human(result):
    print(f"# Diff : {Path(result['skill_file']).name} → {Path(result['edited_file']).name}")
    print()
    print("## Titre")
    if result["title"]["changed"]:
        print(f"- skill  : {result['title']['skill']}")
        print(f"- edited : {result['title']['edited']}")
    else:
        print("(inchangé)")
    print()
    print("## Meta description")
    if result["meta"]["changed"]:
        print(f"- skill  ({result['meta']['skill_length']} chars) : {result['meta']['skill']}")
        print(f"- edited ({result['meta']['edited_length']} chars) : {result['meta']['edited']}")
    else:
        print("(inchangée)")
    print()
    print("## H2 diff")
    if result["h2s_diff"]["removed"]:
        print("RETIRÉS :")
        for h in result["h2s_diff"]["removed"]:
            print(f"  - {h}")
    if result["h2s_diff"]["added"]:
        print("AJOUTÉS :")
        for h in result["h2s_diff"]["added"]:
            print(f"  + {h}")
    if not result["h2s_diff"]["removed"] and not result["h2s_diff"]["added"]:
        print("(aucune modif)")
    print()
    print("## Liens diff")
    if result["links_diff"]["removed_urls"]:
        print("RETIRÉS :")
        for u in result["links_diff"]["removed_urls"]:
            print(f"  - {u}")
    if result["links_diff"]["added_urls"]:
        print("AJOUTÉS :")
        for u in result["links_diff"]["added_urls"]:
            print(f"  + {u}")
    if not result["links_diff"]["removed_urls"] and not result["links_diff"]["added_urls"]:
        print("(aucune modif)")
    print()
    print("## Metrics delta (skill → edited)")
    print()
    print(f"{'Metric':<40} {'skill':>10} {'edited':>10} {'delta':>10} {'%':>8}")
    print("-" * 82)
    for key, d in result["metrics_delta"].items():
        sign = "+" if d["delta"] >= 0 else ""
        print(f"{key:<40} {d['skill']:>10} {d['edited']:>10} {sign}{d['delta']:>9} {sign}{d['delta_pct']:>7}%")


def print_template(result):
    """Squelette feedback_<topic>.md pré-rempli."""
    print("---")
    print("name: <titre court>")
    print("description: <résumé une ligne>")
    print("type: feedback")
    print("---")
    print()
    print("# <Titre du pattern>")
    print()
    print(f"Origine : learning loop sur article `{Path(result['edited_file']).name}` (diff skill vs édité humain).")
    print()
    print("## Règle")
    print()
    print("[à compléter — une règle claire]")
    print()
    print("## Why")
    print()
    print("[raison éditoriale / commerciale / crédibilité]")
    print()
    print("## How to apply")
    print()
    print("[comment le skill doit appliquer cette règle, avec critères si possible mesurables]")
    print()
    print("## Exemple corrigé")
    print()
    if result["title"]["changed"]:
        print("**Titre :**")
        print()
        print(f"- AVANT (skill) : {result['title']['skill']}")
        print(f"- APRÈS (humain) : {result['title']['edited']}")
        print()
    if result["meta"]["changed"]:
        print("**Meta description :**")
        print()
        print(f"- AVANT (skill, {result['meta']['skill_length']} chars) : {result['meta']['skill']}")
        print(f"- APRÈS (humain, {result['meta']['edited_length']} chars) : {result['meta']['edited']}")
        print()
    if result["h2s_diff"]["removed"] or result["h2s_diff"]["added"]:
        print("**H2 restructurés :**")
        for h in result["h2s_diff"]["removed"]:
            print(f"- retiré : {h}")
        for h in result["h2s_diff"]["added"]:
            print(f"- ajouté : {h}")
        print()
    print("## Applicabilité")
    print()
    print("[transverse tous articles, ou cas spécifique type tool guide / comparatif / fiche métier / sujet légal]")


def main():
    if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    skill = Path(sys.argv[1])
    edited = Path(sys.argv[2])

    if not skill.exists():
        print(f"Fichier skill introuvable : {skill}", file=sys.stderr)
        sys.exit(2)
    if not edited.exists():
        print(f"Fichier edited introuvable : {edited}", file=sys.stderr)
        sys.exit(2)

    result = analyze_diff(skill, edited)

    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif "--template" in sys.argv:
        print_template(result)
    else:
        print_human(result)

    sys.exit(0)


if __name__ == "__main__":
    main()
