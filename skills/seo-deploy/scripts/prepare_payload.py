#!/usr/bin/env python3
"""
prepare_payload.py — Convert a {{COMPANY}} blog article (markdown) to a Webflow CMS payload.

Output: JSON with the `fieldData` object ready for data_cms_tool.create_collection_items.

Mapping dérivé de memory/webflow_config.md :
  name, slug, blog-post-excerpt, author-name, categorie-afficher,
  blog-post-categories, sommaire-2, blog-post-content, blog-post-content-pt2,
  blog-post-reading-time, blog-post-featured

Usage:
  python3 prepare_payload.py <article.md>
  python3 prepare_payload.py <article.md> --category outils|metier|growth_marketing|news_ia
"""
import json
import math
import re
import sys
from pathlib import Path


# IDs from memory/webflow_config.md
CATEGORIE_FILTER = {
    "outils": "38d9d7ace7825ded9cab1817df4ead67",
    "metier": "70cbe239f7cf96d5c2141b4bb993f15b",
    "growth_marketing": "9ff562763a0c3745cba798d5d2d47499",
    "news_ia": "628d12274fdfd373bb78e86739a97b88",
    "podcasts": "9f8277055bb61b0557b7000cbb6ca8ab",
    "success_stories": "b6b08abaf6e6822d2c1f706f5eebc19e",
}
CATEGORIES_MULTIREF = {
    "outils": "692c9a1d937c5e652dd51d44",
    "metier": "692c99fe3fd8217ac4eebf85",
    "growth_marketing": "692c9a49a7d5a8847c1b9c13",
    "news_ia": "692c9b69ddd2e695edf9ac8f",
    "podcasts": "692c9b554d9648112bb49387",
    "success_stories": "690389291e34c9f32b2c071f",
}


def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def inline_md(text):
    """Convert inline markdown (links, bold, italic, code) to HTML."""
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^\*\n]+)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return text


def render_table(rows):
    if len(rows) < 2:
        return '\n'.join(rows)
    out = ['<table>']
    header = [c.strip() for c in rows[0].strip('|').split('|')]
    out.append('<thead><tr>')
    out.extend(f'<th>{inline_md(c)}</th>' for c in header)
    out.append('</tr></thead><tbody>')
    for row in rows[2:]:  # skip separator
        if not row.strip('|').strip():
            continue
        cells = [c.strip() for c in row.strip('|').split('|')]
        out.append('<tr>')
        out.extend(f'<td>{inline_md(c)}</td>' for c in cells)
        out.append('</tr>')
    out.append('</tbody></table>')
    return '\n'.join(out)


def markdown_to_html(body):
    """Minimal md → HTML for Webflow Rich Text.

    NOTE: Webflow Rich Text V2 silently strips <ol> tags (verified 2026-05-25).
    Workaround: render ordered lists as <ul> with manual <strong>N.</strong>
    numbering inside each <li>. Loses semantics but preserves visual output.
    """
    lines = body.split('\n')
    parts = []
    i = 0
    in_ul, in_ol, in_table = False, False, False
    ol_counter = 0
    table_rows = []

    def close_ul():
        nonlocal in_ul
        if in_ul:
            parts.append('</ul>')
            in_ul = False

    def close_ol():
        nonlocal in_ol, ol_counter
        if in_ol:
            # Use </ul> because Webflow ate the matching opening <ul> we wrote
            parts.append('</ul>')
            in_ol = False
            ol_counter = 0

    def close_table():
        nonlocal in_table, table_rows
        if in_table:
            parts.append(render_table(table_rows))
            table_rows = []
            in_table = False

    def _peek_next_nonempty(idx):
        """Return the next non-empty line after idx, or '' if EOF."""
        j = idx + 1
        while j < len(lines):
            nxt = lines[j].rstrip()
            if nxt:
                return nxt
            j += 1
        return ''

    while i < len(lines):
        line = lines[i].rstrip()

        if not line:
            # Don't close ol/ul if the next non-empty line continues the same list type.
            # This preserves a single <ol> across markdown items separated by blank lines.
            nxt = _peek_next_nonempty(i)
            if in_ol and re.match(r'^\d+\.\s+', nxt):
                i += 1
                continue
            if in_ul and (nxt.startswith('- ') or nxt.startswith('* ')):
                i += 1
                continue
            close_ul(); close_ol(); close_table()
            i += 1
            continue

        # H1 skipped (goes to name field)
        if line.startswith('# ') and not line.startswith('## '):
            i += 1
            continue

        if line.startswith('## '):
            close_ul(); close_ol(); close_table()
            parts.append(f'<h2>{escape_html(line[3:])}</h2>')
            i += 1
            continue

        if line.startswith('### '):
            close_ul(); close_ol(); close_table()
            parts.append(f'<h3>{escape_html(line[4:])}</h3>')
            i += 1
            continue

        if re.match(r'^-{3,}$', line):
            close_ul(); close_ol(); close_table()
            i += 1
            continue

        if line.startswith('|'):
            close_ul(); close_ol()
            in_table = True
            table_rows.append(line)
            i += 1
            continue

        if line.startswith('- ') or line.startswith('* '):
            close_ol(); close_table()
            if not in_ul:
                parts.append('<ul>')
                in_ul = True
            parts.append(f'<li>{inline_md(line[2:])}</li>')
            i += 1
            continue

        m = re.match(r'^(\d+)\.\s+(.+)$', line)
        if m:
            close_ul(); close_table()
            if not in_ol:
                # Webflow strips <ol>, use <ul> with manual numbering
                parts.append('<ul>')
                in_ol = True
            # Use the explicit number from markdown source (preserves global numbering across sections)
            parts.append(f'<li><strong>{m.group(1)}.</strong> {inline_md(m.group(2))}</li>')
            i += 1
            continue

        close_ul(); close_ol(); close_table()

        # Image placeholder
        if line.startswith('[IMAGE'):
            desc_m = re.match(r'^\[IMAGE[^:]*:\s*([^\]]+)\]', line)
            desc = desc_m.group(1).strip() if desc_m else 'placeholder'
            # Check for Alt text on next line
            alt = ''
            if i + 1 < len(lines) and lines[i + 1].strip().lower().startswith('alt text'):
                alt_m = re.match(r'^alt\s*text\s*:?\s*"?([^"\n]+)"?$', lines[i + 1].strip(), re.IGNORECASE)
                if alt_m:
                    alt = alt_m.group(1)
                i += 1  # skip alt text line
            parts.append(
                f'<blockquote><p>🖼️ <strong>IMAGE À AJOUTER</strong> : {escape_html(desc)}<br/>'
                f'<em>Alt :</em> {escape_html(alt)}</p></blockquote>'
            )
            i += 1
            continue

        # Metadata lines (Title SEO, Slug, Meta description, etc.) should already be stripped
        # by the frontmatter separator. Skip if seen anyway.
        if re.match(r'^\*\*(Publié|Auteur|Mis à jour|Title SEO|Slug|Meta description|Keyword)', line):
            i += 1
            continue

        # Paragraph
        parts.append(f'<p>{inline_md(line)}</p>')
        i += 1

    close_ul(); close_ol(); close_table()
    return '\n'.join(parts)


def split_halves(html):
    """Split HTML at the H2 closest to the midpoint (between sections, not mid-paragraph)."""
    h2_positions = [m.start() for m in re.finditer(r'<h2>', html)]
    if len(h2_positions) < 2:
        return html, ''
    mid = len(html) // 2
    # Pick H2 closest to mid, but never the first (which would leave PT1 empty)
    candidates = h2_positions[1:]
    split_pos = min(candidates, key=lambda p: abs(p - mid))
    return html[:split_pos].rstrip(), html[split_pos:].lstrip()


def build_sommaire(html, exclude=("FAQ", "Ressources", "Conclusion", "Pour aller plus loin")):
    titles = re.findall(r'<h2>([^<]+)</h2>', html)
    toc = [t for t in titles if t not in exclude]
    if not toc:
        return ''
    return '<ul>\n' + '\n'.join(f'  <li>{t}</li>' for t in toc) + '\n</ul>'


def extract_fields(text):
    """Extract frontmatter-ish metadata from article body."""
    patterns = {
        'h1': r'^#\s+(.+?)$',
        'title_seo': r'^\*\*Title SEO\s*:?\s*\*\*\s*:?\s*(.+?)$',
        'slug': r'^\*\*Slug\s*:?\s*\*\*\s*:?\s*(.+?)$',
        'meta_description': r'^\*\*Meta description\s*:?\s*\*\*\s*:?\s*(.+?)$',
        'keyword_principal': r'^\*\*Keyword principal\s*:?\s*\*\*\s*:?\s*(.+?)$',
        'auteur': r'^\*\*Auteur\s*:?\s*\*\*\s*:?\s*(.+?)$',
    }
    out = {}
    for key, pat in patterns.items():
        m = re.search(pat, text, re.MULTILINE | re.IGNORECASE)
        out[key] = m.group(1).strip() if m else None
    return out


def count_words(text):
    return len(re.findall(r'\S+', text))


def prepare(md_path, category='outils'):
    text = Path(md_path).read_text(encoding='utf-8')
    meta = extract_fields(text)

    # Get body (after first --- separator)
    parts = re.split(r'\n---+\n', text, maxsplit=1)
    body = parts[1] if len(parts) > 1 else text

    html = markdown_to_html(body)
    html_pt1, html_pt2 = split_halves(html)
    sommaire = build_sommaire(html)

    wc = count_words(body)
    reading_time = max(1, math.ceil(wc / 250))

    slug_raw = meta.get('slug') or ''
    slug = re.sub(r'^/blog/', '', slug_raw).strip('/')

    field_data = {
        'name': meta.get('h1') or '',
        'slug': slug,
        'blog-post-excerpt': meta.get('meta_description') or '',
        'author-name': meta.get('auteur') or '{{OWNER}}',
        'categorie-afficher': CATEGORIE_FILTER.get(category, CATEGORIE_FILTER['outils']),
        'blog-post-categories': [CATEGORIES_MULTIREF.get(category, CATEGORIES_MULTIREF['outils'])],
        'sommaire-2': sommaire,
        'blog-post-content': html_pt1,
        'blog-post-content-pt2': html_pt2,
        'blog-post-reading-time': reading_time,
        'blog-post-featured': False,
    }

    return {
        'article': str(md_path),
        'word_count': wc,
        'reading_time_min': reading_time,
        'html_length_pt1': len(html_pt1),
        'html_length_pt2': len(html_pt2),
        'fieldData': field_data,
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(2)
    category = 'outils'
    if '--category' in sys.argv:
        idx = sys.argv.index('--category')
        if idx + 1 < len(sys.argv):
            category = sys.argv[idx + 1]
    result = prepare(Path(sys.argv[1]), category=category)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
