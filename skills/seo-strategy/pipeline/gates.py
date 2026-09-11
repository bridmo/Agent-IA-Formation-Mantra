"""
Gate validations for the SEO strategy pipeline.
Each gate checks that a phase produced a valid output before allowing the next phase.
A gate failure = the phase must be redone. No skipping.
"""

from models import (
    Article, Backlog, ContentType, ExistingContent, Keyword,
    Persona, SerpResult, TITLE_FORMULAS,
)


class GateFailure(Exception):
    """Raised when a gate check fails."""
    def __init__(self, phase: int, errors: list[str]):
        self.phase = phase
        self.errors = errors
        super().__init__(f"Phase {phase} gate failed:\n" + "\n".join(f"  - {e}" for e in errors))


# ── Phase 1 gate ──────────────────────────────────────────────

def gate_phase1(
    products: list[dict],
    icp_personas: list[dict],
    channel_data: dict,
    objectives: list[str],
    scope_in: list[str],
    scope_out: list[str],
) -> bool:
    errors = []
    if not products:
        errors.append("No products loaded. Read formations.md.")
    if not icp_personas:
        errors.append("No ICP personas loaded. Read icp-bible.md.")
    if not channel_data:
        errors.append("No channel data loaded. Read channels.md.")
    if not objectives:
        errors.append("No objectives defined.")
    if not scope_in or not scope_out:
        errors.append("Scope in/out not defined.")
    if errors:
        raise GateFailure(1, errors)
    return True


# ── Phase 2 gate ──────────────────────────────────────────────

def gate_phase2(keywords: list[Keyword]) -> bool:
    errors = []
    if len(keywords) < 20:
        errors.append(f"Only {len(keywords)} keywords found. Expected 30+. Did you extract ALL themes from formations.md?")

    # Check all keywords have required fields
    for kw in keywords:
        if not kw.personas:
            errors.append(f"Keyword '{kw.keyword}' has no personas assigned. ICP crossing is mandatory.")
        if kw.volume_fr == 0 and kw.kd is None:
            errors.append(f"Keyword '{kw.keyword}' has no volume data. Verify with Ahrefs.")
        if not kw.product:
            errors.append(f"Keyword '{kw.keyword}' has no product mapped. Product-first filter is mandatory.")

    # Check LP keywords are separated from BLOG keywords
    lp_keywords = [k for k in keywords if k.category.value == "LP (landing page)"]
    blog_keywords = [k for k in keywords if k.category.value != "LP (landing page)"]
    if not lp_keywords:
        errors.append("No LP keywords found. Did you forget to map 'formation X' keywords to landing pages?")
    if not blog_keywords:
        errors.append("No BLOG keywords found.")

    # Check keyword categories diversity
    categories = set(k.category for k in blog_keywords)
    if len(categories) < 4:
        errors.append(f"Only {len(categories)} keyword categories. Expected 4+. Did you cover tools, comparisons, methods, concepts?")

    if errors:
        raise GateFailure(2, errors)
    return True


# ── Phase 3 gate ──────────────────────────────────────────────

def gate_phase3(serp_results: list[SerpResult], keywords_checked: list[str]) -> bool:
    errors = []
    if len(serp_results) < 8:
        errors.append(f"Only {len(serp_results)} SERP checks. Check at least the top 10 keywords by volume.")

    for sr in serp_results:
        if not sr.dominant_format:
            errors.append(f"SERP for '{sr.keyword}': no dominant format identified.")
        if not sr.angle_gap:
            errors.append(f"SERP for '{sr.keyword}': no angle gap identified.")

    if errors:
        raise GateFailure(3, errors)
    return True


# ── Phase 4 gate ──────────────────────────────────────────────

def gate_phase4(existing_content: list[ExistingContent]) -> bool:
    errors = []
    if not existing_content:
        errors.append("No existing content mapped. Read channels-seo.md and cross-reference with Ahrefs.")

    statuses = set(c.status for c in existing_content)
    if len(statuses) < 2:
        errors.append("Only one content status used. Expected mix of PROTECT/REFRESH/ABANDON/MISSING.")

    for c in existing_content:
        if c.status.value == "REFRESH" and not c.action:
            errors.append(f"Content '{c.url}' marked REFRESH but no action specified.")

    if errors:
        raise GateFailure(4, errors)
    return True


# ── Phase 5 gate ──────────────────────────────────────────────

def gate_phase5(articles: list[Article]) -> bool:
    errors = []

    for a in articles:
        # Title must not be a raw keyword
        if a.title.lower() == a.keyword.lower():
            errors.append(f"Article #{a.number} '{a.title}': title is just the raw keyword. Use a title formula.")
        if len(a.title) < 20:
            errors.append(f"Article #{a.number} '{a.title}': title too short. Likely a keyword, not a real title.")
        if ":" not in a.title and "?" not in a.title:
            errors.append(f"Article #{a.number} '{a.title}': title has no colon or question mark. Probably not a proper title formula.")

        # Must have personas
        if not a.personas:
            errors.append(f"Article #{a.number}: no personas assigned.")

        # Must have SERP angle
        if not a.serp_angle:
            errors.append(f"Article #{a.number}: no SERP angle defined. Did you run SERP analysis?")

        # Must have product bridge
        if not a.product:
            errors.append(f"Article #{a.number}: no product mapped.")

        # Must have internal links planned
        if not a.internal_links_out:
            errors.append(f"Article #{a.number}: no outgoing internal links planned.")

    if errors:
        raise GateFailure(5, errors)
    return True


# ── Phase 6 gate ──────────────────────────────────────────────

MAX_SINGLE_FORMAT_PCT = 0.45  # max 45% of articles in one format

def gate_phase6(backlog: Backlog) -> bool:
    errors = []

    # Check format mix diversity
    mix = backlog.format_mix
    total = len(backlog.articles)
    if total == 0:
        errors.append("Backlog is empty.")
        raise GateFailure(6, errors)

    for content_type, count in mix.items():
        pct = count / total
        if pct > MAX_SINGLE_FORMAT_PCT:
            errors.append(
                f"Format '{content_type.value}' represents {pct:.0%} of articles ({count}/{total}). "
                f"Max allowed: {MAX_SINGLE_FORMAT_PCT:.0%}. Diversify the mix."
            )

    # Check at least 3 different formats
    if len(mix) < 3:
        errors.append(f"Only {len(mix)} content types. Need at least 3 different formats.")

    # Check persona coverage
    coverage = backlog.persona_coverage
    if Persona.P1_SENIOR_TRANSITION not in coverage:
        errors.append("P1 (senior transition, 40-50% of deals) has ZERO articles. Critical gap.")
    if Persona.P2_RESPONSABLE_STAGNE not in coverage:
        errors.append("P2 (responsable stagne, 15-20% of deals) has ZERO articles.")

    # Check all articles have scores
    for a in backlog.articles:
        if not a.score_breakdown:
            errors.append(f"Article #{a.number}: no score breakdown. Show the calculation.")

    if errors:
        raise GateFailure(6, errors)
    return True


# ── Phase 7 gate ──────────────────────────────────────────────

def gate_phase7(
    strategy_page_id: str,
    brief_page_ids: list[str],
    annex_page_id: str,
    num_articles: int,
) -> bool:
    errors = []

    if not strategy_page_id:
        errors.append("Strategy page not published to Notion.")
    if not annex_page_id:
        errors.append("Annex page not published to Notion.")
    if len(brief_page_ids) != num_articles:
        errors.append(
            f"Expected {num_articles} individual brief pages, got {len(brief_page_ids)}. "
            f"Each article must have its own Notion page."
        )

    if errors:
        raise GateFailure(7, errors)
    return True
