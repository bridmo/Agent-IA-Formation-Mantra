"""
SEO Strategy Pipeline Orchestrator

This is the master execution script. It defines the 7 phases,
enforces sequential execution, and runs gate validations between phases.

Usage within Claude Code:
    The LLM reads this file to understand the pipeline structure,
    then executes each phase following the defined sequence.
    Gate checks are run after each phase — if a gate fails,
    the phase must be redone before proceeding.

This is NOT a standalone script — it's a blueprint that the LLM follows.
The MCP tools (Ahrefs, Notion) are called by the LLM at each phase.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PhaseStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    GATE_FAILED = "gate_failed"
    COMPLETED = "completed"


@dataclass
class Phase:
    number: int
    name: str
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    deliverable: Optional[str] = None
    gate_errors: list[str] = field(default_factory=list)

    # What files to read before this phase
    required_reads: list[str] = field(default_factory=list)

    # What MCP tools to call
    ahrefs_calls: list[str] = field(default_factory=list)

    # What the deliverable must contain (checked by gate)
    required_outputs: list[str] = field(default_factory=list)


# ── Pipeline definition ───────────────────────────────────────

PIPELINE = [
    Phase(
        number=1,
        name="Objectives & Feasibility",
        required_reads=[
            "brain/product-marketing-context.md",
            "brain/offre.md",
            "brain/icp.md",
            "brain/messaging.md",
            "brain/channels.md",
        ],
        ahrefs_calls=[
            "site-explorer-metrics ({{DOMAIN}}, FR)",
            "site-explorer-domain-rating ({{DOMAIN}})",
            "site-explorer-metrics-history (6 mois)",
        ],
        required_outputs=[
            "products: list of formations with themes, tools, % deals",
            "icp: personas with triggers, pain points, search queries",
            "baseline: current traffic, DR, keywords count",
            "objectives: numbered, measurable, tied to business goals",
            "scope_in: what's in scope for this quarter",
            "scope_out: what's explicitly excluded",
        ],
    ),
    Phase(
        number=2,
        name="Keyword Universe by Product Cluster",
        required_reads=[
            "brain/offre.md (extract ALL themes/tools/methods)",
            "brain/messaging.md (search queries by persona)",
        ],
        ahrefs_calls=[
            "keywords-explorer-overview (all keyword batches, country=fr)",
            "keywords-explorer-volume-by-country (for English keywords)",
        ],
        required_outputs=[
            "lp_keywords: keywords for landing page optimization",
            "blog_keywords: organized by product and category (tool/comparison/method/concept/problem/career)",
            "each keyword has: volume_fr, kd, category, product, product_bridge, personas, icp_pain_point",
            "ICP crossing: every keyword mapped to persona(s) + trigger/pain point",
            "gap analysis: product X = Y% revenue but Z% SEO coverage",
        ],
    ),
    Phase(
        number=3,
        name="Competitive Intelligence",
        required_reads=[
            "channels/seo/competitors.md",
        ],
        ahrefs_calls=[
            "serp-overview (for each top keyword, country=fr)",
        ],
        required_outputs=[
            "serp_results: top 5 for each target keyword",
            "each result has: dominant_format, angle_gap, school_competitor_present",
            "opportunity map: first mover / weak competition / strong competition",
        ],
    ),
    Phase(
        number=4,
        name="Map Existing Content",
        required_reads=[
            "channels/seo/inventaire.md",
        ],
        ahrefs_calls=[
            "site-explorer-top-pages ({{DOMAIN}})",
            "site-explorer-organic-keywords ({{DOMAIN}})",
        ],
        required_outputs=[
            "content classified as PROTECT / REFRESH / ABANDON / MISSING",
            "refresh candidates with URL + specific action",
            "coverage map by product (which products have 0 content)",
        ],
    ),
    Phase(
        number=5,
        name="Keywords to Articles (5 Filters)",
        required_reads=[],  # uses outputs from phases 1-4
        ahrefs_calls=[],   # SERP already checked in phase 3
        required_outputs=[
            "articles list with: title (FULL, from formula), keyword, type, product, personas, serp_angle, cluster",
            "FILTER 1: product bridge validated",
            "FILTER 2: SERP analyzed (format + angle gap)",
            "FILTER 3: content type chosen based on SERP",
            "FILTER 4: title uses a proven formula (never raw keyword)",
            "FILTER 5: cluster expansion (all variants listed, Q2 vs Q3+)",
        ],
    ),
    Phase(
        number=6,
        name="Score, Prioritize & Build Backlog",
        required_reads=[],
        ahrefs_calls=[],
        required_outputs=[
            "scored backlog: Product x Demand x Intent x Effort + adjustments",
            "score_breakdown shown for each article",
            "format mix table (no single format > 45%)",
            "persona coverage table (P1 and P2 must be served)",
            "calendar with week assignments",
            "Q3 backlog (what's deferred)",
        ],
    ),
    Phase(
        number=7,
        name="Handoff & Publish to Notion",
        required_reads=[],
        ahrefs_calls=[],
        required_outputs=[
            "strategy page: context > objectives > axes > backlog > next actions",
            "1 brief page per article (NEVER grouped)",
            "1 annex page (analysis data)",
            "all tables use <table> tags with <tr>/<td> on separate lines",
            "all page refs use www.notion.so (not app.notion.com)",
        ],
    ),
]


# ── Execution logic ───────────────────────────────────────────

def get_current_phase(pipeline: list[Phase]) -> Optional[Phase]:
    """Get the next phase to execute."""
    for phase in pipeline:
        if phase.status != PhaseStatus.COMPLETED:
            return phase
    return None  # all done


def can_proceed(pipeline: list[Phase], target_phase: int) -> bool:
    """Check if all previous phases are completed."""
    for phase in pipeline:
        if phase.number < target_phase and phase.status != PhaseStatus.COMPLETED:
            return False
    return True


def run_phase(pipeline: list[Phase], phase_number: int) -> Phase:
    """
    Execute a phase. This is called by the LLM after doing the work.
    The gate validation determines if we can proceed.
    """
    phase = pipeline[phase_number - 1]

    if not can_proceed(pipeline, phase_number):
        incomplete = [p for p in pipeline if p.number < phase_number and p.status != PhaseStatus.COMPLETED]
        raise RuntimeError(
            f"Cannot run Phase {phase_number}. "
            f"Phases {[p.number for p in incomplete]} are not completed."
        )

    phase.status = PhaseStatus.IN_PROGRESS
    return phase


def complete_phase(phase: Phase, deliverable: str) -> None:
    """Mark a phase as completed after gate validation passes."""
    phase.deliverable = deliverable
    phase.status = PhaseStatus.COMPLETED


def fail_phase(phase: Phase, errors: list[str]) -> None:
    """Mark a phase as failed. Must be redone."""
    phase.gate_errors = errors
    phase.status = PhaseStatus.GATE_FAILED


# ── Summary ───────────────────────────────────────────────────

def pipeline_summary(pipeline: list[Phase]) -> str:
    """Print pipeline status."""
    lines = ["SEO Strategy Pipeline Status:", ""]
    for p in pipeline:
        icon = {
            PhaseStatus.NOT_STARTED: "⬜",
            PhaseStatus.IN_PROGRESS: "🔄",
            PhaseStatus.GATE_FAILED: "❌",
            PhaseStatus.COMPLETED: "✅",
        }[p.status]
        line = f"  {icon} Phase {p.number}: {p.name}"
        if p.gate_errors:
            line += f" — ERRORS: {len(p.gate_errors)}"
        lines.append(line)
    return "\n".join(lines)
