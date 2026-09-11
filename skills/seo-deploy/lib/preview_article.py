#!/usr/bin/env python3
"""
Preview local d'un article {{COMPANY}} avant push Webflow.

Rend l'article markdown en HTML avec la charte de marque (Oswald + Inter, cream + navy),
inline les SVG présents localement, et ouvre dans le navigateur par défaut.

Usage:
    python3 preview_article.py content/blog/claude-design-anthropic.md
    # ou via le module:
    from preview_article import preview_article
    preview_article("content/blog/claude-design-anthropic.md")
"""
import sys, re, pathlib, subprocess
import markdown
from pathlib import Path

# Racine du repo, déduite de l'emplacement de ce fichier
REPO_ROOT = Path(__file__).resolve().parents[3]


BRAND_CSS = """
:root {
  --cream: #FAF9F5;
  --warm: #F0E9E3;
  --navy-deep: #282C4B;
  --navy-medium: #394E8A;
  --royal-blue: #103ACD;
  --mustard: #EFC222;
  --text: #000000;
  --muted: #3D3A35;
}
* { box-sizing: border-box; }
body {
  background: var(--cream);
  color: var(--text);
  font-family: Inter, -apple-system, system-ui, sans-serif;
  max-width: 760px;
  margin: 0 auto;
  padding: 40px 24px 120px;
  line-height: 1.7;
  font-size: 17px;
}
.preview-banner {
  background: var(--navy-deep);
  color: white;
  padding: 14px 20px;
  border-radius: 12px;
  margin-bottom: 48px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-family: Inter;
}
.preview-banner strong { font-family: Oswald; letter-spacing: 1px; font-weight: 600; }
.preview-banner span { color: var(--warm); }
.frontmatter {
  background: var(--warm);
  border-left: 4px solid var(--navy-deep);
  padding: 16px 20px;
  margin: 0 0 40px 0;
  font-size: 14px;
  border-radius: 4px;
}
.frontmatter p { margin: 6px 0; }
.frontmatter strong { color: var(--navy-deep); }
h1 {
  font-family: Oswald, sans-serif;
  font-size: 44px;
  line-height: 1.15;
  margin: 0 0 24px 0;
  font-weight: 700;
  letter-spacing: -0.5px;
}
h2 {
  font-family: Oswald, sans-serif;
  font-size: 30px;
  line-height: 1.25;
  margin: 72px 0 24px 0;
  font-weight: 600;
  letter-spacing: 0.3px;
}
h3 {
  font-family: Oswald, sans-serif;
  font-size: 22px;
  line-height: 1.3;
  margin: 48px 0 16px 0;
  font-weight: 500;
}
p { margin: 16px 0; }
a {
  color: var(--royal-blue);
  text-decoration: underline;
  text-underline-offset: 3px;
  text-decoration-thickness: 1px;
}
a:hover { text-decoration-thickness: 2px; }
strong { font-weight: 600; }
em { font-style: italic; color: var(--muted); }
ul, ol { margin: 16px 0; padding-left: 24px; }
li { margin: 6px 0; }
blockquote {
  border-left: 4px solid var(--navy-deep);
  padding: 8px 20px;
  color: var(--muted);
  font-style: italic;
  margin: 28px 0;
  background: var(--warm);
  border-radius: 0 8px 8px 0;
}
hr {
  border: 0;
  border-top: 1px solid #D0C8BC;
  margin: 48px 0;
}
code {
  background: var(--warm);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.88em;
  font-family: 'SFMono-Regular', Menlo, monospace;
}
figure {
  margin: 40px 0;
  text-align: center;
}
figure img, img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
  border-radius: 8px;
}
figure.w-richtext-figure-type-table table,
table {
  width: 100%;
  border-collapse: collapse;
  margin: 24px 0;
  font-size: 15px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}
th, td {
  border-bottom: 1px solid #E6DFD2;
  padding: 12px 16px;
  text-align: left;
}
th {
  background: var(--navy-deep);
  color: white;
  font-family: Oswald;
  font-weight: 500;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  font-size: 13px;
}
tr:last-child td { border-bottom: none; }
"""


def inline_svgs(body_md, base_path):
    """Replace [IMAGE-SCHEMA: ...] placeholders with inline SVG if available locally."""
    article_name = pathlib.Path(base_path).stem

    def replace(match):
        desc = match.group(1).strip()
        alt = match.group(2).strip() if match.group(2) else "Schéma"

        # Try to find a matching SVG in content/images/{article_name}/
        candidates = [
            pathlib.Path(REPO_ROOT / "channels/content/images" / article_name / "concepts").glob("*.svg"),
            pathlib.Path(REPO_ROOT / "channels/content/images" / article_name).glob("*.svg"),
        ]
        for candidate_glob in candidates:
            for svg_path in candidate_glob:
                if svg_path.exists():
                    try:
                        return f'<figure>{svg_path.read_text()}<figcaption style="color:var(--muted);font-size:13px;margin-top:8px;font-style:italic">{alt}</figcaption></figure>'
                    except Exception:
                        continue

        # Fallback: show the placeholder
        return f'<figure style="background:#F0E9E3;padding:40px;border:2px dashed #3D3A35;"><p style="margin:0;font-family:Oswald;color:#282C4B;">🖼️ IMAGE À AJOUTER</p><p style="margin:8px 0 0 0;font-size:14px;">{desc}</p><p style="margin:4px 0 0 0;font-size:12px;color:#3D3A35;">Alt: {alt}</p></figure>'

    return re.sub(
        r"\[IMAGE-SCHEMA\s*:\s*([^\]]+)\]\s*\n(?:Alt\s+text\s*:\s*\"?([^\"\n]+)\"?)?",
        replace, body_md
    )


def preview_article(md_path, open_browser=True):
    """Generate local HTML preview of a {{COMPANY}} article markdown file."""
    md_path = pathlib.Path(md_path).resolve()
    if not md_path.exists():
        raise FileNotFoundError(f"Markdown not found: {md_path}")

    raw = md_path.read_text()
    lines = raw.split("\n")

    # Extract H1 + frontmatter metadata (title, slug, meta, etc.)
    h1 = ""
    metadata = {}
    body_start = 0
    sep_count = 0
    for i, line in enumerate(lines):
        if line.startswith("# ") and not h1:
            h1 = line[2:].strip()
            continue
        m = re.match(r"\*\*([^:*]+?)\s*:\*\*\s*(.+)", line)
        if m and sep_count == 0:
            metadata[m.group(1).strip()] = m.group(2).strip()
        if line.strip() == "---":
            sep_count += 1
            if sep_count == 1:
                body_start = i + 1
                break

    body_md = "\n".join(lines[body_start:])
    body_md = inline_svgs(body_md, md_path)

    # [CAPTURE: description] → placeholder jaune visible (screenshot à ajouter par humain)
    def replace_capture(m):
        desc = m.group(1).strip()
        return (
            f'<figure style="background:#EFC222;padding:20px;border-radius:12px;margin:32px 0;text-align:center;">'
            f'<p style="margin:0;font-family:Oswald;color:#000;font-weight:600;letter-spacing:1px;">📸 CAPTURE À AJOUTER</p>'
            f'<p style="margin:8px 0 0 0;font-size:14px;color:#000;">{desc}</p>'
            f'</figure>'
        )
    body_md = re.sub(r"\[CAPTURE\s*:\s*([^\]]+)\]", replace_capture, body_md)

    html_body = markdown.markdown(body_md, extensions=["tables", "fenced_code", "sane_lists"])

    # Frontmatter card
    meta_html = "<div class='frontmatter'>"
    for k, v in metadata.items():
        meta_html += f"<p><strong>{k}:</strong> {v}</p>"
    meta_html += "</div>"

    import datetime
    doc = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Preview · {h1}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>{BRAND_CSS}</style>
</head>
<body>
<div class="preview-banner">
<strong>🔍 PREVIEW LOCAL BRAND</strong>
<span>Revue avant push Webflow · {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</span>
</div>
<h1>{h1}</h1>
{meta_html}
{html_body}
</body>
</html>"""

    # Save to /tmp/{{SLUG}}-preview/<slug>.html
    preview_dir = pathlib.Path("/tmp/{{SLUG}}-preview")
    preview_dir.mkdir(exist_ok=True)
    slug = md_path.stem
    out = preview_dir / f"{slug}.html"
    out.write_text(doc)

    if open_browser:
        try:
            subprocess.Popen(["open", str(out)])
        except Exception as e:
            print(f"Could not auto-open: {e}")

    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 preview_article.py <path/to/article.md>")
        sys.exit(1)
    out = preview_article(sys.argv[1])
    print(f"✅ Preview: {out}")
