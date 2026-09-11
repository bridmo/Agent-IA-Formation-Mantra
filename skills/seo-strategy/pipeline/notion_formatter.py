"""
Notion formatting helpers.
Generates correct Notion-flavored markdown/HTML for tables, pages, and structure.
Prevents all the formatting errors we've encountered.
"""

from models import Article, Backlog, ExistingContent, Priority


def notion_table(headers: list[str], rows: list[list[str]]) -> str:
    """
    Generate a Notion table with correct formatting.

    Rules:
    - Uses <table> tags, NOT markdown pipes
    - Each <tr> and <td> on its own line
    - Never put multiple <td> on one line (columns will merge)
    """
    lines = ['<table header-row="true">']

    # Header row
    lines.append("<tr>")
    for h in headers:
        lines.append(f"<td>{h}</td>")
    lines.append("</tr>")

    # Data rows
    for row in rows:
        lines.append("<tr>")
        for cell in row:
            lines.append(f"<td>{cell}</td>")
        lines.append("</tr>")

    lines.append("</table>")
    return "\n".join(lines)


def notion_page_ref(page_id: str, title: str) -> str:
    """
    Generate a page reference for Notion content.

    Rules:
    - Use www.notion.so, NOT app.notion.com/p/
    - ID without dashes
    """
    clean_id = page_id.replace("-", "")
    return f'<page url="https://www.notion.so/{clean_id}">{title}</page>'


# ── Strategy page ─────────────────────────────────────────────

def format_strategy_page(
    context: str,
    objectives: list[str],
    axes: list[dict],  # [{name, description, personas, impact}]
    backlog: Backlog,
    next_actions: list[str],
    brief_pages: list[dict],  # [{id, title}]
    annex_page: dict,  # {id, title}
) -> str:
    """
    Format the main strategy page.
    Structure: Context → Objectives → Axes → Backlog → Next actions → Sub-pages
    NEVER put analysis first.
    """
    sections = []

    # Context
    sections.append(f"## Contexte\n\n{context}")
    sections.append("---")

    # Objectives
    obj_lines = "\n".join(f"{i+1}. {o}" for i, o in enumerate(objectives))
    sections.append(f"## Objectifs Q2\n\n{obj_lines}")
    sections.append("---")

    # Axes
    sections.append("## Axes de travail")
    for ax in axes:
        sections.append(f"\n### {ax['name']}\n\n{ax['description']}\n\n*Personas : {ax['personas']}. Impact : {ax['impact']}*")
    sections.append("---")

    # Backlog table
    sections.append("## Backlog priorisé")
    backlog_headers = ["Prio", "#", "Article", "Type", "Keyword", "Vol", "KD", "Score", "Sem.", "Personas"]
    backlog_rows = []

    # Refreshes first
    for r in backlog.refreshes:
        backlog_rows.append([
            Priority.URGENT.value, "R", f"Refresh : {r.action}",
            "Refresh", r.keyword, str(r.traffic), "—", "—", "S1-S2",
            "P1 P2",
        ])

    # Then articles
    for a in sorted(backlog.articles, key=lambda x: x.score, reverse=True):
        personas_str = " ".join(p.value for p in a.personas)
        backlog_rows.append([
            a.priority.value, str(a.number), a.title,
            a.content_type.value, a.keyword, str(a.volume_fr),
            str(a.kd) if a.kd is not None else "~0", str(a.score),
            a.week, personas_str,
        ])

    sections.append(notion_table(backlog_headers, backlog_rows))

    # Format mix table
    sections.append("\n### Mix des formats")
    mix = backlog.format_mix
    mix_headers = ["Format", "Nb articles", "% du backlog"]
    mix_rows = []
    total = len(backlog.articles)
    for ct, count in sorted(mix.items(), key=lambda x: x[1], reverse=True):
        pct = f"{count/total:.0%}" if total > 0 else "0%"
        mix_rows.append([ct.value, str(count), pct])
    mix_rows.append(["**TOTAL**", f"**{total}**", "**100%**"])
    sections.append(notion_table(mix_headers, mix_rows))

    sections.append("---")

    # Next actions
    actions_lines = "\n".join(f"{i+1}. {a}" for i, a in enumerate(next_actions))
    sections.append(f"## Prochaines actions\n\n{actions_lines}")
    sections.append("---")

    # Sub-pages
    sections.append("*Briefs détaillés :*\n")
    for bp in brief_pages:
        sections.append(notion_page_ref(bp["id"], bp["title"]))
    sections.append(notion_page_ref(annex_page["id"], annex_page["title"]))

    return "\n\n".join(sections)


# ── Brief page ────────────────────────────────────────────────

def format_brief_page(article: Article) -> str:
    """
    Format a single article brief page.
    One page per article. Never group briefs.
    """
    personas_str = " ".join(p.value for p in article.personas)
    kd_str = str(article.kd) if article.kd is not None else "~0"

    sections = []

    # Header metadata
    sections.append(f"""**Keyword** : `{article.keyword}` ({article.volume_fr}/mo | KD {kd_str})
**Keywords secondaires** : {', '.join(article.keyword_secondary)}
**Intent** : {article.serp_angle}
**Format** : {article.content_type.value} (~{int(article.effort_hours * 400)} mots)
**Semaine** : {article.week}
**Score** : {article.score} ({article.score_breakdown})
**Formation servie** : {article.product}
**Personas** : {personas_str}""")

    sections.append("---")

    # SERP analysis
    sections.append(f"### SERP actuel\n\n{article.serp_angle}")

    # Editorial angle
    sections.append(f"### Angle éditorial\n\n{article.icp_justification}")

    # Internal links
    links_in = "\n".join(f"- Entrant : {l}" for l in article.internal_links_in) if article.internal_links_in else "- (à configurer)"
    links_out = "\n".join(f"- Sortant : {l}" for l in article.internal_links_out)
    sections.append(f"### Maillage interne\n\n{links_in}\n{links_out}")

    # Checklist
    sections.append("""### Checklist qualité

- [ ] Keyword dans H1, premier H2, meta description
- [ ] Réponse directe en intro (40-60 mots)
- [ ] CTA vers la formation
- [ ] 1 lien interne entrant configuré dès publication
- [ ] Titre suit une formule prouvée (pas un keyword brut)""")

    return "\n\n".join(sections)
