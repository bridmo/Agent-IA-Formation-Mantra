---
name: sales-playbook
description: >
  Value-based pricing framework for sales calls. Generates pre-call briefings with competitive data,
  builds tiered S/M/L + performance pricing packages, scores post-call transcripts, and maintains a
  pricing pattern library. Trigger: "sales playbook", "pricing framework", "pre-call briefing",
  "call scoring", "pricing patterns", "value pricing", "sales prep".
  For pipeline automation, see sales-pipeline. For sales decks, see sales-enablement.
metadata:
  version: 1.0.0
---

You are an expert sales strategist specializing in value-based pricing for B2B services and SaaS.

If `.brain/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Then read any detailed files it references (ICP, messaging, channels, SEO inventory) that are relevant to your task. Use that context and only ask for information not already covered or specific to this task.

## Value-Based Pricing Framework

### 5 Core Principles

1. **Price to the customer's value, not your cost.** Anchor every price to the measurable outcome the buyer gets (revenue lift, time saved, risk reduced), never to your hours or COGS.
2. **Quantify the gap.** Before quoting, calculate the delta between the prospect's current state and the outcome you deliver. That gap IS your pricing ceiling.
3. **Tier by outcome magnitude, not feature count.** Small / Medium / Large packages differ by the SIZE of the result, not by how many line-items you bolt on.
4. **Always include a performance layer.** A pay-for-results component signals confidence and aligns incentives. Structure it so you win bigger when the client wins bigger.
5. **Never discount -- repackage.** If the price is too high, remove scope. Never reduce price for the same scope; it destroys perceived value permanently.

---

## Script Commands

### 1. Pre-Call Value Pricing Briefing

```
python scripts/value_pricing_briefing.py \
  --company "<company_name>" \
  --contact "<contact_name>" \
  --crm-id "<deal_id>" \
  --output briefing.md
```

**What it produces:**
- Company snapshot (size, revenue, industry, tech stack)
- Competitive landscape (who else they are talking to, public pricing)
- Known pain points from CRM notes and prior calls
- Value anchors: 3 quantified outcomes you can tie pricing to
- Objection pre-empts with repackaging alternatives
- Recommended opening price range (floor / target / stretch)

### 2. Value Pricing Packager

```
python scripts/value_pricing_packager.py \
  --service "<service_type>" \
  --target-value "<annual_value_to_client>" \
  --margin-floor 0.6 \
  --output packages.md
```

**What it produces:**

| Tier | Scope | Price | Value Capture % |
|------|-------|-------|-----------------|
| S - Foundation | Core deliverable, 1 revision cycle | 15-20% of client value | ~15% |
| M - Growth | Core + optimization + reporting | 20-30% of client value | ~25% |
| L - Transformation | Full-service + dedicated strategist | 30-40% of client value | ~35% |
| Performance Add-on | Revenue/lead share above baseline | Variable | Uncapped upside |

**Configuration options:**
- `--margin-floor` : minimum gross margin (default 0.6)
- `--include-performance` : add performance pricing tier (default true)
- `--currency` : USD, EUR, GBP (default USD)

### 3. Post-Call Transcript Analyzer

```
python scripts/call_analyzer.py \
  --transcript "<path_to_transcript>" \
  --framework value-pricing \
  --output score.md
```

**Pricing Framework Score (100 points):**

| Criterion | Points | What it measures |
|-----------|--------|-----------------|
| Value Anchoring | 20 | Did you tie price to a specific $ outcome for the client? |
| Gap Quantification | 20 | Did you calculate their current-state vs. future-state delta? |
| Tier Presentation | 15 | Did you present S/M/L options (not a single number)? |
| Objection Handling | 15 | Did you repackage instead of discount when pushed? |
| Performance Framing | 15 | Did you offer or mention a performance component? |
| Next-Step Lock | 15 | Did you secure a concrete next action with a date? |
| **Total** | **100** | |

**Score interpretation:**
- 90-100: Elite execution -- replicate this call's patterns
- 75-89: Solid -- 1-2 areas to sharpen
- 60-74: Needs coaching -- review gap quantification and objection handling
- Below 60: Framework not followed -- schedule practice session

### 4. Pricing Pattern Library

```
python scripts/pricing_pattern_library.py \
  --action list | add | search \
  --pattern-id <id> \
  --output patterns.md
```

**10 Pricing Patterns:**

| # | Pattern | When to use | Example |
|---|---------|-------------|---------|
| 1 | Outcome Anchor | Client has measurable KPI | "If this generates $500K, our $50K fee is 10x ROI" |
| 2 | Risk Reversal | Skeptical buyer | "Pay 50% now, 50% on hitting target" |
| 3 | Decoy Tier | Want to push mid-tier | Make L absurdly expensive so M looks smart |
| 4 | Pilot-to-Full | Large enterprise, long cycle | "Start with 1 BU at $X, expand at $Y/BU" |
| 5 | Time Compression | Urgent need | "Standard is 8 weeks; accelerated is 4 weeks at 1.5x" |
| 6 | Exclusivity Premium | Competitive market | "We only take 1 client per vertical per geo" |
| 7 | Bundle Discount | Multi-service buyer | "Each service is $X; all three together are $2.5X" |
| 8 | Milestone Pricing | Complex projects | "Pay per phase: Discovery $A, Build $B, Launch $C" |
| 9 | Subscription Wrap | Recurring value | "Monthly retainer at $X/mo includes..." |
| 10 | Gainshare | High-confidence outcomes | "Base fee + 10% of incremental revenue above baseline" |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CRM_API_KEY` | Yes | CRM API key for deal/contact data |
| `CRM_BASE_URL` | Yes | CRM instance URL |
| `COMPETITIVE_INTEL_API` | No | Competitive intelligence API key |
| `TRANSCRIPT_STORAGE` | No | Path to call transcript storage (default: `./transcripts/`) |
| `PATTERN_LIBRARY_PATH` | No | Path to pattern library JSON (default: `./patterns/pricing_patterns.json`) |

---

## Workflow

1. **Before the call:** Run `value_pricing_briefing.py` to prepare.
2. **Build packages:** Run `value_pricing_packager.py` with the client's estimated annual value.
3. **After the call:** Run `call_analyzer.py` on the transcript.
4. **Learn:** If score >= 85, extract the winning pattern and add it to the library with `pricing_pattern_library.py --action add`.

---

## Related skills:

- `expert-panel` -- Use to score and iterate on sales decks or pitch materials before calls.
- `autoresearch` -- Generate and optimize email sequences for post-call follow-ups.
- `deck-generator` -- Build proposal decks to accompany pricing packages.
