# SEO Strategy Pipeline
# Structure and validation for the 7-phase SEO strategy process.
#
# Files:
#   models.py          — Data structures (Keyword, Article, Backlog, title formulas)
#   gates.py           — Gate validations between phases (blocks if requirements not met)
#   orchestrator.py    — Pipeline execution logic (sequential phases, no skipping)
#   notion_formatter.py — Notion output formatting (tables, pages, correct syntax)
#
# This pipeline is a blueprint the LLM follows, not a standalone script.
# MCP tools (Ahrefs, Notion) are called by the LLM at each phase.
# Gate checks enforce quality — a failed gate means redo the phase.
