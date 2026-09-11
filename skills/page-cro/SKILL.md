---
name: page-cro
description: When the user wants to optimize, improve, or increase conversions on any marketing page — including homepage, landing pages, pricing pages, feature pages, or blog posts. Also use when the user says "CRO," "conversion rate optimization," "this page isn't converting," "improve conversions," "why isn't this page working," "my landing page sucks," "nobody's converting," "low conversion rate," "bounce rate is too high," "people leave without signing up," or "this page needs work." Use this even if the user just shares a URL and asks for feedback — they probably want conversion help. For signup/registration flows, see signup-flow-cro. For post-signup activation, see onboarding-cro. For forms outside of signup, see form-cro. For popups/modals, see popup-cro.
metadata:
  version: 1.1.0
---

# Page Conversion Rate Optimization (CRO)

You are a conversion rate optimization expert. Your goal is to analyze marketing pages and provide actionable recommendations to improve conversion rates.

## Initial Assessment

**Check for product marketing context first:**
If `.brain/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Then read any detailed files it references (ICP, messaging, channels, SEO inventory) that are relevant to your task. Use that context and only ask for information not already covered or specific to this task.

Before providing recommendations, identify:

1. **Page Type**: Homepage, landing page, pricing, feature, blog, about, other
2. **Primary Conversion Goal**: Sign up, request demo, purchase, subscribe, download, contact sales
3. **Traffic Context**: Where are visitors coming from? (organic, paid, email, social)

---

## CRO Analysis Framework

Analyze the page across these dimensions, in order of impact:

### 1. Value Proposition Clarity (Highest Impact)

**Check for:**
- Can a visitor understand what this is and why they should care within 5 seconds?
- Is the primary benefit clear, specific, and differentiated?
- Is it written in the customer's language (not company jargon)?

**Common issues:**
- Feature-focused instead of benefit-focused
- Too vague or too clever (sacrificing clarity)
- Trying to say everything instead of the most important thing

### 2. Headline Effectiveness

**Evaluate:**
- Does it communicate the core value proposition?
- Is it specific enough to be meaningful?
- Does it match the traffic source's messaging?

**Strong headline patterns:**
- Outcome-focused: "Get [desired outcome] without [pain point]"
- Specificity: Include numbers, timeframes, or concrete details
- Social proof: "Join 10,000+ teams who..."

### 3. CTA Placement, Copy, and Hierarchy

**Primary CTA assessment:**
- Is there one clear primary action?
- Is it visible without scrolling?
- Does the button copy communicate value, not just action?
  - Weak: "Submit," "Sign Up," "Learn More"
  - Strong: "Start Free Trial," "Get My Report," "See Pricing"

**CTA hierarchy:**
- Is there a logical primary vs. secondary CTA structure?
- Are CTAs repeated at key decision points?

### 4. Visual Hierarchy and Scannability

**Check:**
- Can someone scanning get the main message?
- Are the most important elements visually prominent?
- Is there enough white space?
- Do images support or distract from the message?

### 5. Trust Signals and Social Proof

**Types to look for:**
- Customer logos (especially recognizable ones)
- Testimonials (specific, attributed, with photos)
- Case study snippets with real numbers
- Review scores and counts
- Security badges (where relevant)

**Placement:** Near CTAs and after benefit claims

### 6. Objection Handling

**Common objections to address:**
- Price/value concerns
- "Will this work for my situation?"
- Implementation difficulty
- "What if it doesn't work?"

**Address through:** FAQ sections, guarantees, comparison content, process transparency

### 7. Friction Points

**Look for:**
- Too many form fields
- Unclear next steps
- Confusing navigation
- Required information that shouldn't be required
- Mobile experience issues
- Long load times

---

## Output Format

Structure your recommendations as:

### Quick Wins (Implement Now)
Easy changes with likely immediate impact.

### High-Impact Changes (Prioritize)
Bigger changes that require more effort but will significantly improve conversions.

### Test Ideas
Hypotheses worth A/B testing rather than assuming.

### Copy Alternatives
For key elements (headlines, CTAs), provide 2-3 alternatives with rationale.

---

## Page-Specific Frameworks

### Homepage CRO
- Clear positioning for cold visitors
- Quick path to most common conversion
- Handle both "ready to buy" and "still researching"

### Landing Page CRO
- Message match with traffic source
- Single CTA (remove navigation if possible)
- Complete argument on one page

### Pricing Page CRO
- Clear plan comparison
- Recommended plan indication
- Address "which plan is right for me?" anxiety

### Feature Page CRO
- Connect feature to benefit
- Use cases and examples
- Clear path to try/buy

### Blog Post CRO
- Contextual CTAs matching content topic
- Inline CTAs at natural stopping points

---

## Experiment Ideas

When recommending experiments, consider tests for:
- Hero section (headline, visual, CTA)
- Trust signals and social proof placement
- Pricing presentation
- Form optimization
- Navigation and UX

**For comprehensive experiment ideas by page type**: See [references/experiments.md](references/experiments.md)

---

## Task-Specific Questions

1. What's your current conversion rate and goal?
2. Where is traffic coming from?
3. What does your signup/purchase flow look like after this page?
4. Do you have user research, heatmaps, or session recordings?
5. What have you already tried?

---

## Quality gate

Before finalizing any content output, consider running the `expert-panel` skill for recursive scoring with the humanizer (24-pattern AI writing detector, weighted 1.5x). Target: 90/100.

## Related Skills

- **signup-flow-cro**: If the issue is in the signup process itself
- **form-cro**: If forms on the page need optimization
- **popup-cro**: If considering popups as part of the strategy
- **copywriting**: If the page needs a complete copy rewrite
- **ab-test-setup**: To properly test recommended changes
- **expert-panel**: For recursive scoring of content quality

---

## CRO Automation Tools

Python scripts for automated landing page auditing and survey-driven lead magnet generation. All live in `scripts/`.

### CRO Audit (`cro_audit.py`)

```bash
# Single URL audit
python3 scripts/cro_audit.py --url https://example.com/landing-page

# Batch mode
python3 scripts/cro_audit.py --urls https://example.com/page1 https://example.com/page2

# URLs from file (one per line)
python3 scripts/cro_audit.py --file urls.txt

# With industry benchmark comparison
python3 scripts/cro_audit.py --url https://example.com --industry saas

# JSON output
python3 scripts/cro_audit.py --url https://example.com --json

# Save report
python3 scripts/cro_audit.py --url https://example.com --output report.json
```

**8 Scoring Dimensions (each 0-100):**

| # | Dimension | What it measures |
|---|-----------|------------------|
| 1 | Headline Clarity | Value prop obvious in <5 seconds? |
| 2 | CTA Visibility | CTAs prominent, contrasting, above fold? |
| 3 | Social Proof | Testimonials, logos, case studies, numbers? |
| 4 | Urgency | Scarcity, deadlines, limited offers? |
| 5 | Trust Signals | Security badges, guarantees, certifications? |
| 6 | Form Friction | Field count, form intimidation level? |
| 7 | Mobile Responsiveness | Viewport meta, responsive patterns, touch targets? |
| 8 | Page Speed Indicators | Image optimization, script count, resource size? |

Overall CRO Score = weighted average. Output includes per-dimension scores, priority fixes, before/after suggestions, industry benchmarks, and letter grade (A+ through F).

**Supported industries:** `saas`, `ecommerce`, `agency`, `finance`, `healthcare`, `education`, `b2b`, `general`

### Survey-to-Lead-Magnet Engine (`survey_lead_magnet.py`)

```bash
# Analyze survey CSV
python3 scripts/survey_lead_magnet.py --csv survey_responses.csv

# Specify pain point columns
python3 scripts/survey_lead_magnet.py --csv survey.csv --pain-columns "biggest_challenge" "top_frustration"

# Limit segments
python3 scripts/survey_lead_magnet.py --csv survey.csv --top-segments 5

# JSON output
python3 scripts/survey_lead_magnet.py --csv survey.csv --json
```

Produces: pain point clusters with respondent counts, segments ranked by commercial potential, lead magnet briefs per segment (title, format, hook, content outline, target CTA, distribution channel, viral/conversion potential scores), and prioritized implementation roadmap.

Works with any survey tool export (Typeform, Google Forms, SurveyMonkey, etc.).

### Recommended Workflow

1. **Weekly:** Run `cro_audit.py` on top landing pages to track CRO scores over time
2. **Post-survey:** Run `survey_lead_magnet.py` to turn survey data into content strategy
3. **Pre-launch:** Audit new landing pages before driving paid traffic
4. **Monthly:** Batch audit competitor landing pages to benchmark
