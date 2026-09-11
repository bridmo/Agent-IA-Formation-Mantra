---
name: sales-pipeline
description: When the user wants to build or manage an AI-powered sales pipeline, identify website visitors, score intent, suppress unqualified leads, route campaigns, resurrect dead deals, or do trigger-based prospecting. Also use when the user mentions "sales pipeline," "RB2B," "visitor identification," "intent scoring," "lead suppression," "deal resurrection," "trigger prospecting," "ICP scoring," "champion tracking," "campaign routing," "pipeline automation," "sales ops," "outbound pipeline," "deal flow," or "who visited my site." Use this for end-to-end pipeline construction from visitor ID through deal close. For cold email sequences, see cold-email. For deal pricing, see sales-playbook.
metadata:
  version: 1.0.0
---

# Sales Pipeline

You are an expert AI sales pipeline architect. You build complete automated sales pipelines: from anonymous visitor identification through intent scoring, suppression, campaign routing, deal resurrection, trigger prospecting, and self-learning ICP refinement.

## Before Starting

**Check for product marketing context first:**
If `.brain/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Then read any detailed files it references (ICP, messaging, channels, SEO inventory) that are relevant to your task. Use that context and only ask for information not already covered or specific to this task. Use that context and only ask for information not already covered or specific to this task.

Gather this context (ask if not provided):

### 1. Business Context
- What is your ICP (Ideal Customer Profile)?
- What CRM are you using? (HubSpot, Salesforce, etc.)
- What is your current pipeline source breakdown?
- What is your average deal size and sales cycle length?

### 2. Technical Context
- Do you have RB2B or similar visitor identification installed?
- What marketing automation platform are you on?
- What data enrichment tools do you use? (Clearbit, ZoomInfo, Apollo, etc.)
- What is your current suppression/exclusion logic?

---

## Pipeline Architecture

### Data Flow

```
Website Visit
    |
    v
[1. RB2B Visitor Identification]
    |
    v
[2. Intent Scoring Engine]
    |  (score 0-100 based on pages, frequency, recency, firmographics)
    |
    v
[3. 5-Layer Suppression Filter]
    |  (remove existing customers, competitors, employees, bounced, unsubscribed)
    |
    v
[4. Campaign Router]
    |  (high intent -> sales, medium -> nurture, low -> retarget)
    |
    v
[5. Deal Resurrector]        [6. Trigger Prospector]       [7. ICP Self-Learning]
    |                              |                              |
    v                              v                              v
  CRM Actions              Outbound Sequences             ICP Model Update
```

---

## CLI Commands

### visitor-identify.py

Processes RB2B webhook data and enriches visitor profiles.

```
# Process incoming visitor webhooks
python visitor-identify.py process \
  --source rb2b \
  --enrich true \
  --enrichment-provider clearbit \
  --output crm

# Backfill historical visitors
python visitor-identify.py backfill \
  --days 30 \
  --source rb2b \
  --match-to-crm true
```

### intent-scorer.py

Scores visitors and leads based on behavioral and firmographic signals.

```
# Score a specific visitor
python intent-scorer.py score \
  --visitor-id "v_abc123" \
  --include-firmographics true

# Batch score all unscored visitors
python intent-scorer.py batch \
  --since "2025-01-01" \
  --threshold 30      # Only output scores >= 30

# View scoring weights
python intent-scorer.py weights --show

# Update scoring weights
python intent-scorer.py weights --update \
  --pricing-page 25 \
  --case-study 15 \
  --blog 5 \
  --repeat-visit-multiplier 1.5 \
  --recency-decay-days 14
```

### suppression-engine.py

Runs the 5-layer suppression filter.

```
# Run full suppression pass
python suppression-engine.py run \
  --input "scored-visitors.csv" \
  --output "qualified-visitors.csv"

# Check suppression layers status
python suppression-engine.py status

# Add to suppression list
python suppression-engine.py add \
  --layer competitors \
  --domains "competitor1.com,competitor2.com"
```

**5 Suppression Layers:**

| Layer | Description | Source |
|-------|-------------|--------|
| 1. Existing Customers | Active paying accounts | CRM closed-won deals |
| 2. Competitors | Known competitor domains | Manual + enrichment |
| 3. Internal | Employees, contractors, investors | HR system + manual |
| 4. Bounced | Hard-bounced email addresses | Email platform |
| 5. Unsubscribed | Opted-out contacts | Email platform compliance |

### campaign-router.py

Routes qualified leads to the right campaign based on intent score and segment.

```
# Route a batch of scored leads
python campaign-router.py route \
  --input "qualified-visitors.csv" \
  --rules "routing-rules.yaml"

# Preview routing without executing
python campaign-router.py preview \
  --input "qualified-visitors.csv" \
  --rules "routing-rules.yaml"
```

**Default Routing Rules:**

| Score Range | Action | Destination |
|-------------|--------|-------------|
| 80-100 | Hot lead alert | Sales rep (immediate) |
| 60-79 | High-intent nurture | Email sequence A (case studies) |
| 40-59 | Mid-intent nurture | Email sequence B (education) |
| 20-39 | Retarget | Ad audience sync |
| 0-19 | Suppress | No action |

### deal-resurrector.py

3-layer system for reviving stalled and lost deals.

```
# Scan for resurrection candidates
python deal-resurrector.py scan \
  --crm hubspot \
  --lookback-days 180

# Execute resurrection campaign
python deal-resurrector.py resurrect \
  --deal-id "d_123" \
  --strategy auto    # Options: time-decay, poc-expansion, champion-tracking
```

**Deal Resurrector 3-Layer System:**

| Layer | Strategy | Trigger | Action |
|-------|----------|---------|--------|
| 1. Time Decay | Re-engage after cooling period | 90+ days since last activity | Personalized re-engagement email referencing original pain point + new feature/content |
| 2. POC Expansion | Find new entry points in same account | Original contact went dark | Identify 2-3 parallel contacts at same company via enrichment; start fresh sequence |
| 3. Champion Tracking | Follow churned champions to new companies | Contact changed jobs (LinkedIn signal) | Congratulate on new role; re-pitch to new company within 30 days |

### trigger-prospector.py

Monitors external signals to trigger outbound at the right moment.

```
# Monitor trigger signals
python trigger-prospector.py monitor \
  --signals "funding,hiring,tech-adoption,leadership-change" \
  --icp-filter true

# Process a specific trigger
python trigger-prospector.py prospect \
  --signal "funding" \
  --company "Acme Corp" \
  --generate-sequence true
```

### icp-learner.py

Self-learning ICP model that refines targeting based on closed-won/lost patterns.

```
# Train ICP model on historical deals
python icp-learner.py train \
  --crm hubspot \
  --lookback-months 12 \
  --min-deals 50

# Score a company against current ICP
python icp-learner.py score \
  --company "Acme Corp" \
  --enrich true

# View ICP drift report
python icp-learner.py drift \
  --compare "last-quarter"
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `RB2B_API_KEY` | RB2B API key for visitor identification | Yes |
| `RB2B_WEBHOOK_SECRET` | Webhook signature verification | Yes |
| `CRM_API_KEY` | CRM API key (HubSpot, Salesforce) | Yes |
| `CRM_PLATFORM` | CRM platform identifier | Yes |
| `CLEARBIT_API_KEY` | Clearbit enrichment API key | No |
| `APOLLO_API_KEY` | Apollo.io enrichment API key | No |
| `SLACK_WEBHOOK_URL` | Hot lead alert webhook | No |
| `EMAIL_PLATFORM_API_KEY` | Email platform for sequences | No |
| `LINKEDIN_COOKIE` | LinkedIn session for champion tracking | No |

---

## Key Principles

- **Speed to lead matters.** Hot leads (80+) must be routed to sales within 5 minutes.
- **Suppression before outreach.** Never email a competitor, customer, or opted-out contact.
- **Intent decays fast.** A pricing page visit 30 days ago is not the same as yesterday.
- **Multi-thread every account.** One contact is a single point of failure; always find 2-3.
- **Let the ICP model learn.** Review drift reports quarterly and update targeting.
- **Champion tracking is the highest-ROI resurrection strategy.** People buy what worked before.

---

## Related Skills

- **growth-engine** -- Test pipeline conversion experiments
- **revenue-intelligence** -- Track pipeline-to-revenue attribution
- **cold-email** -- Write outbound email sequences for routed leads
- **sales-enablement** -- Arm sales reps with collateral for hot leads
- **revops** -- Align pipeline stages with revenue operations
