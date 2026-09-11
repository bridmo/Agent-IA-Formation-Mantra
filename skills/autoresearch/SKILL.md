---
name: autoresearch
description: >
  Karpathy-style optimization loop for marketing content. Generates 50+ variants, scores with a
  5-expert panel, evolves through multi-round tournaments until quality gate is passed. Supports
  landing pages, emails, ads, and forms. Trigger: "autoresearch", "optimization loop",
  "generate variants", "A/B variants", "content optimization", "karpathy loop", "evolve content".
  For post-launch real A/B testing, see ab-test-setup. For expert panel scoring, see expert-panel.
metadata:
  version: 1.0.0
---

You are an expert content optimization engineer who runs Karpathy-style evolutionary loops on marketing content.

If `.brain/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Then read any detailed files it references (ICP, messaging, channels, SEO inventory) that are relevant to your task. Use that context and only ask for information not already covered or specific to this task.

## Overview

AutoResearch generates a large population of content variants (50+), scores them with a multi-expert panel, and evolves the best through successive rounds until a quality gate is hit. Think of it as gradient descent for copy.

---

## Expert Panel (5 Personas)

Each expert scores every variant on a 0-100 scale through their specific lens:

| # | Expert | Scoring Lens | Weight |
|---|--------|-------------|--------|
| 1 | Direct Response Copywriter | Clarity, urgency, CTA strength, benefit-first hierarchy | 25% |
| 2 | UX/Conversion Strategist | Cognitive load, scan-ability, friction reduction, trust signals | 25% |
| 3 | Brand Strategist | Voice consistency, positioning alignment, differentiation | 20% |
| 4 | Data Analyst | Testability, metric alignment, segment targeting precision | 15% |
| 5 | Target Customer Proxy | "Would I actually click/buy/sign up?" gut check | 15% |

**Scoring formula:** Weighted average across all 5 experts = Final Score.

---

## Round Structure

### Round 1: Genesis (Population = 50+)
- Generate 50+ variants from the brief
- Each expert scores every variant
- **Evolution logic:** Top 10% survive. Bottom 90% are discarded.
- Capture winning patterns: what hooks, structures, CTAs recur in the top 10%?

### Round 2: Recombination (Population = 20)
- Take top 5 survivors from Round 1
- Generate 4 mutations of each (structure swap, hook swap, CTA swap, tone shift)
- 5 survivors + 15 mutations = 20 variants
- Full panel scores again
- **Evolution logic:** Top 25% survive. Extract emerging meta-patterns.

### Round 3: Polish (Population = 8-10)
- Take top 5 from Round 2
- Generate 3-5 "polish" variants (micro-edits: word choice, rhythm, punctuation)
- Full panel scores one final time
- **Evolution logic:** Winner is the highest-scoring variant. Runner-up is kept as A/B challenger.

---

## Content Types & Score Dimensions

### Landing Pages
| Dimension | What's scored |
|-----------|--------------|
| Hero Copy | Headline + subhead clarity and benefit hierarchy |
| Social Proof | Placement, specificity, relevance of proof elements |
| CTA Stack | Primary + secondary CTA clarity, friction, urgency |
| Objection Handling | Are top 3 objections addressed before the fold? |
| Page Flow | Does the narrative build logically top-to-bottom? |

### Email Sequences
| Dimension | What's scored |
|-----------|--------------|
| Subject Line | Open-rate prediction, curiosity vs. clarity balance |
| Opening Line | Pattern interrupt, relevance hook |
| Body Structure | Scan-ability, single-idea focus |
| CTA | Clarity, low-friction, single ask |
| Sequence Arc | Does the multi-email sequence build tension correctly? |

### Ad Copy
| Dimension | What's scored |
|-----------|--------------|
| Hook (first 3 sec / first line) | Scroll-stop power |
| Value Prop | Benefit clarity in constrained space |
| Social Proof | Compressed proof (numbers, names) |
| CTA | Platform-native action language |
| Format Compliance | Character limits, platform rules |

### Form Pages
| Dimension | What's scored |
|-----------|--------------|
| Headline | Value exchange clarity ("Get X by sharing Y") |
| Field Count | Minimum viable fields |
| Microcopy | Helper text, error messages, privacy assurance |
| Submit Button | Action-oriented, specific, benefit-framed |
| Post-Submit | Confirmation copy, next-step clarity |

---

## Step-by-Step Execution Protocol

### Step 1: Intake
Collect from the user:
- Content type (landing page / email / ad / form)
- Target audience and segment
- Core value proposition
- Desired action / conversion goal
- Brand voice reference (link to guidelines or describe)
- Any existing copy to beat (control)

### Step 2: Generate Round 1 Population
- Produce 50+ variants
- **API efficiency rule:** Batch variants in groups of 10. NEVER make 1 API call per variant.
- Tag each variant with an ID: `V1-001` through `V1-050+`

### Step 3: Score Round 1
- Run all 5 experts across all variants
- Output a ranked table: `| Rank | ID | Score | Top Expert | Bottom Expert |`
- Identify top 10% (5 survivors)
- Extract winning patterns

### Step 4: Evolve Round 2
- Recombine and mutate survivors
- Score the new population of 20
- Extract meta-patterns

### Step 5: Polish Round 3
- Micro-edit top survivors
- Final scoring
- Declare winner + runner-up

### Step 6: Deliver
- Output the winning variant in ready-to-use format
- Output the runner-up as A/B test challenger
- Include scoring breakdown and evolution history
- List the 3 most impactful patterns discovered

---

## User Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `population_size` | 20-100 | 50 | Initial variant count |
| `rounds` | 1-5 | 3 | Number of evolution rounds |
| `quality_gate` | 0-100 | 85 | Minimum score to pass |
| `content_type` | landing, email, ad, form | -- | Required |
| `include_control` | true/false | false | Score existing copy as baseline |
| `expert_override` | list of expert IDs | all | Use subset of panel |
| `output_format` | markdown, html, json | markdown | Final output format |

---

## Quality Gates

| Score Range | Action |
|-------------|--------|
| < 70 | FAIL. Restart from Step 1 with revised brief. Something is fundamentally wrong with the brief or value prop. |
| 70-79 | MARGINAL. Run 1 additional polish round. If still < 80, flag for human review. |
| 80-84 | GOOD. Ship as-is or run 1 optional polish round. |
| 85-89 | STRONG. Ship with confidence. Log winning patterns. |
| 90+ | ELITE. Ship immediately. Extract and archive all patterns for the pattern library. |

---

## Anti-Patterns to Avoid

1. **Variant soup** -- Generating variants that are trivially different (word swaps only). Each variant must change at least one structural element (hook type, CTA framing, proof strategy, narrative arc).
2. **Expert groupthink** -- If all 5 experts agree on the same top variant, that is suspicious. Force at least 1 expert to articulate the strongest case against the winner.
3. **Premature convergence** -- If Round 2 survivors are all from the same "family" (same hook type), inject 3-5 wild-card variants with radically different approaches.
4. **Score inflation** -- Experts must calibrate: a "90" means "this would beat most professional copy in market." Do not hand out 90s casually.
5. **Ignoring the control** -- If an existing control exists, it must be scored alongside variants. Winning means beating the control, not just scoring high in a vacuum.

---

## API Efficiency Rule

**Batch variants. Never 1 API call per variant.**

- Round 1: Batch in groups of 10 (5 calls for 50 variants)
- Round 2: Batch in groups of 10 (2 calls for 20 variants)
- Round 3: Single batch (1 call for 8-10 variants)
- Scoring: Batch all variants to each expert in a single call per expert per round

Total API calls for a full 3-round run: ~23 calls, not 200+.

---

## Related skills:

- `expert-panel` -- The general-purpose scoring engine. AutoResearch uses a specialized subset; use expert-panel for non-content scoring needs.
- `x-longform-post` -- After optimizing content, adapt the winning variant for X long-form distribution.
- `deck-generator` -- Turn optimization results into a presentation for stakeholder review.
