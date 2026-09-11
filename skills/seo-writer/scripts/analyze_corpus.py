#!/usr/bin/env python3
"""
analyze_corpus.py — Extrait 16 métriques quantitatives sur un corpus d'articles {{COMPANY}}.

Métriques :
  Structure : word_count, h2/h3_count, paragraphs_count, avg/median_paragraph_words,
              pct_single_sentence_paragraphs, sentences_count, avg_sentence_words
  SEO       : h1_length, title_seo_length, meta_length, internal_blog_links,
              formation_links, external_links, image_placeholders
  Voix      : cadratins_total, cadratins_per_1000_words, anaphora_count,
              pct_sentences_with_precise_numbers
  Intro     : hook_first_sentence_words, hook_has_non_rounded_number,
              first_non_rounded_number_position

Agrégats : min / p20 / médiane / p80 / p90 / max par métrique.

Usage :
  python3 analyze_corpus.py file1.md file2.md ...
  python3 analyze_corpus.py content/blog/*.md --output references/corpus-baseline.md --json references/corpus-baseline.json --name "Corpus référence"
"""
import json
import re
import statistics
import sys
from pathlib import Path


# ---------- Parsing ----------

def extract_metadata(text):
    h1_m = re.search(r'^#\s+(.+?)$', text, re.MULTILINE)
    title_m = re.search(r'^\*\*Title SEO\s*:?\s*\*\*\s*:?\s*(.+?)$', text, re.MULTILINE | re.IGNORECASE)
    meta_m = re.search(r'^\*\*Meta description\s*:?\s*\*\*\s*:?\s*(.+?)$', text, re.MULTILINE | re.IGNORECASE)
    kw_m = re.search(r'^\*\*Keyword principal\s*:?\s*\*\*\s*:?\s*(.+?)$', text, re.MULTILINE | re.IGNORECASE)
    return {
        "h1": h1_m.group(1).strip() if h1_m else "",
        "title_seo": title_m.group(1).strip() if title_m else "",
        "meta": meta_m.group(1).strip() if meta_m else "",
        "keyword": kw_m.group(1).strip() if kw_m else "",
    }


def strip_code(text):
    text = re.sub(r'```[\s\S]*?```', '', text)
    text = re.sub(r'`[^`]+`', '', text)
    return text


def get_body(text):
    """Body starts after the first --- separator following metadata block."""
    parts = re.split(r'\n---+\n', text, maxsplit=1)
    return parts[1] if len(parts) > 1 else text


def extract_paragraphs(body):
    """Keep only narrative paragraphs (not headers, tables, lists, images, metadata)."""
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


# ---------- Precise numbers ----------

def is_precise_number(n):
    if 2020 <= n <= 2035:  # year
        return True
    if n < 100:
        return True
    s = str(n)
    trailing_zeros = len(s) - len(s.rstrip('0'))
    return trailing_zeros < 2


def has_non_rounded_number(text):
    for num_str in re.findall(r'\b(\d{2,})\b', text):
        if is_precise_number(int(num_str)):
            return True
    return False


# ---------- Anaphora detection ----------

def detect_anaphoras(paragraphs):
    """3+ consecutive paragraphs starting with the same 1st word (normalized)."""
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


# ---------- Article analysis ----------

def analyze_article(path):
    text = path.read_text(encoding='utf-8')
    meta = extract_metadata(text)
    body = get_body(text)
    body_stripped = strip_code(body)

    paragraphs = extract_paragraphs(body)
    paragraph_lengths = [count_words(p) for p in paragraphs]

    all_sentences = []
    for p in paragraphs:
        all_sentences.extend(split_sentences(p))
    sentence_lengths = [count_words(s) for s in all_sentences]

    word_count = sum(paragraph_lengths)
    h2_count = len(re.findall(r'^##\s+(?!#)', body, re.MULTILINE))
    h3_count = len(re.findall(r'^###\s+', body, re.MULTILINE))

    links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', body)
    internal_blog = [(a, u) for a, u in links if '/blog/' in u]
    formation = [(a, u) for a, u in links if '/formation-' in u or '/bootcamp-' in u]
    external = [(a, u) for a, u in links if u.startswith('http')]

    image_placeholders = len(re.findall(r'\[IMAGE\s*:', body, re.IGNORECASE))
    cadratins = len(re.findall(r'—', body_stripped))

    anaphoras = detect_anaphoras(paragraphs)
    sentences_with_precise = sum(1 for s in all_sentences if has_non_rounded_number(s))
    single_sentence_paras = sum(1 for p in paragraphs if len(split_sentences(p)) == 1)

    hook_sentence = split_sentences(paragraphs[0])[0] if paragraphs else ""
    first_num_pos = None
    for idx, s in enumerate(all_sentences):
        if has_non_rounded_number(s):
            first_num_pos = idx + 1
            break

    return {
        "file": path.name,
        "word_count": word_count,
        "h1_length": len(meta["h1"]),
        "title_seo_length": len(meta["title_seo"]),
        "meta_length": len(meta["meta"]),
        "h2_count": h2_count,
        "h3_count": h3_count,
        "paragraphs_count": len(paragraphs),
        "avg_paragraph_words": round(statistics.mean(paragraph_lengths), 1) if paragraph_lengths else 0,
        "median_paragraph_words": round(statistics.median(paragraph_lengths), 1) if paragraph_lengths else 0,
        "pct_single_sentence_paragraphs": round((single_sentence_paras / len(paragraphs) * 100) if paragraphs else 0, 1),
        "sentences_count": len(all_sentences),
        "avg_sentence_words": round(statistics.mean(sentence_lengths), 1) if sentence_lengths else 0,
        "internal_blog_links": len(internal_blog),
        "formation_links": len(formation),
        "external_links": len(external),
        "image_placeholders": image_placeholders,
        "cadratins_total": cadratins,
        "cadratins_per_1000_words": round((cadratins / word_count * 1000) if word_count > 0 else 0, 2),
        "anaphora_count": len(anaphoras),
        "pct_sentences_with_precise_numbers": round((sentences_with_precise / len(all_sentences) * 100) if all_sentences else 0, 1),
        "hook_first_sentence_words": count_words(hook_sentence),
        "hook_has_non_rounded_number": has_non_rounded_number(hook_sentence),
        "first_non_rounded_number_position": first_num_pos,
    }


# ---------- Aggregates ----------

def percentile(data, p):
    if not data:
        return 0
    sd = sorted(data)
    k = (len(sd) - 1) * p / 100
    f = int(k)
    c = min(f + 1, len(sd) - 1)
    if f == c:
        return sd[f]
    return sd[f] + (sd[c] - sd[f]) * (k - f)


def compute_aggregates(articles):
    if not articles:
        return {}
    numeric_keys = [k for k, v in articles[0].items() if isinstance(v, (int, float)) and k != "file"]
    agg = {}
    for key in numeric_keys:
        values = [a[key] for a in articles if isinstance(a.get(key), (int, float))]
        if values:
            agg[key] = {
                "min": min(values),
                "p20": round(percentile(values, 20), 1),
                "median": round(statistics.median(values), 1),
                "p80": round(percentile(values, 80), 1),
                "p90": round(percentile(values, 90), 1),
                "max": max(values),
            }
    return agg


# ---------- Output ----------

def format_markdown(articles, aggregates, name=""):
    lines = []
    lines.append(f"# Corpus baseline — {name}" if name else "# Corpus baseline")
    lines.append("")
    lines.append(f"{len(articles)} articles analysés. Métriques quantitatives automatiques.")
    lines.append("")
    lines.append("## Par article — récap")
    lines.append("")
    lines.append("| Article | Mots | H2 | Meta | % paras 1ph | Cadratins | Anaph. | Liens blog | Liens ext |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for a in articles:
        lines.append(
            f"| {a['file']} | {a['word_count']} | {a['h2_count']} | {a['meta_length']} | "
            f"{a['pct_single_sentence_paragraphs']}% | {a['cadratins_total']} | {a['anaphora_count']} | "
            f"{a['internal_blog_links']} | {a['external_links']} |"
        )
    lines.append("")
    lines.append("## Distribution corpus")
    lines.append("")
    lines.append("| Métrique | min | p20 | médiane | p80 | p90 | max |")
    lines.append("|---|---|---|---|---|---|---|")
    for key, s in aggregates.items():
        lines.append(f"| {key} | {s['min']} | {s['p20']} | {s['median']} | {s['p80']} | {s['p90']} | {s['max']} |")
    lines.append("")
    return "\n".join(lines)


# ---------- CLI ----------

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    output_md, output_json, name = None, None, ""
    files = []
    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output_md = args[i + 1]; i += 2
        elif args[i] == "--json" and i + 1 < len(args):
            output_json = args[i + 1]; i += 2
        elif args[i] == "--name" and i + 1 < len(args):
            name = args[i + 1]; i += 2
        else:
            files.append(Path(args[i])); i += 1

    articles = []
    for f in files:
        if not f.exists():
            print(f"Skip missing: {f}", file=sys.stderr)
            continue
        articles.append(analyze_article(f))

    aggregates = compute_aggregates(articles)
    md = format_markdown(articles, aggregates, name)

    if output_md:
        Path(output_md).write_text(md, encoding="utf-8")
        print(f"Wrote {output_md}", file=sys.stderr)
    else:
        print(md)

    if output_json:
        Path(output_json).write_text(
            json.dumps({"corpus": name, "articles": articles, "aggregates": aggregates}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"Wrote {output_json}", file=sys.stderr)


if __name__ == "__main__":
    main()
