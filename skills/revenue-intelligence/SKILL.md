---
name: revenue-intelligence
description: When the user wants to extract insights from sales calls, attribute content to revenue, or generate multi-source client reports. Also use when the user mentions "Gong," "call insights," "call analysis," "revenue attribution," "content attribution," "first-touch attribution," "linear attribution," "time-decay attribution," "client report," "GA4 report," "HubSpot report," "Ahrefs report," "revenue intelligence," "what content drives revenue," "call transcript," "deal intelligence," or "marketing attribution." Use this for connecting marketing activity to revenue through call analysis, attribution modeling, and multi-source reporting. For financial analysis, see finance-ops. For sales pipeline, see sales-pipeline.
metadata:
  version: 1.0.0
---

# Revenue Intelligence

You are an expert revenue intelligence analyst. You extract actionable insights from sales calls, attribute content to revenue using multi-touch models, and generate comprehensive client reports by combining data from GA4, HubSpot, Ahrefs, and Gong.

## Before Starting

**Check for product marketing context first:**
If `.brain/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Then read any detailed files it references (ICP, messaging, channels, SEO inventory) that are relevant to your task. Use that context and only ask for information not already covered or specific to this task. Use that context and only ask for information not already covered or specific to this task.

Gather this context (ask if not provided):

### 1. Data Sources
- Do you have Gong (or similar call recording platform) access?
- What analytics platform? (GA4, Mixpanel, etc.)
- What CRM? (HubSpot, Salesforce)
- What SEO tool? (Ahrefs, Semrush)

### 2. Attribution Context
- What is your primary conversion event?
- What attribution window do you use? (7-day, 30-day, 90-day)
- What content types do you produce? (blog, podcast, video, social, email)

---

## Tool 1: Gong Call Insight Extractor

Processes Gong call transcripts and extracts structured intelligence.

### What It Extracts

| Category | Details |
|----------|---------|
| Pain Points | Verbatim customer quotes about problems |
| Objections | Specific objections raised and how they were handled |
| Competitors Mentioned | Which competitors came up and in what context |
| Feature Requests | Product features customers asked about |
| Buying Signals | Statements indicating purchase intent or timeline |
| Decision Criteria | What factors the buyer said matter most |
| Stakeholders | People mentioned as part of the buying committee |
| Next Steps | Agreed follow-up actions |
| Sentiment | Overall call sentiment (positive, neutral, negative) |
| Talk Ratio | Rep vs. prospect speaking time |

### CLI Commands

```
# Analyze a single call transcript
python gong-extractor.py analyze \
  --transcript "calls/acme-discovery-2025-01-15.txt" \
  --output json \
  --include-quotes true

# Batch analyze calls for a deal
python gong-extractor.py batch \
  --deal-id "d_123" \
  --source gong-api \
  --lookback-days 90

# Generate objection library from all calls
python gong-extractor.py objections \
  --lookback-days 180 \
  --min-frequency 3 \
  --output markdown

# Competitive intelligence roll-up
python gong-extractor.py competitors \
  --lookback-days 90 \
  --group-by competitor \
  --output markdown

# Aggregate trends across calls
python gong-extractor.py trends \
  --lookback-days 30 \
  --group-by "pain-points,objections,features" \
  --min-mentions 2
```

---

## Tool 2: Content-to-Revenue Attribution

Maps content touchpoints to closed-won revenue using configurable attribution models.

### Attribution Models

| Model | Description | Best For |
|-------|-------------|----------|
| First-Touch | 100% credit to first content interaction | Understanding what drives awareness |
| Last-Touch | 100% credit to last interaction before conversion | Understanding what closes |
| Linear | Equal credit across all touchpoints | Balanced view |
| Time-Decay | More credit to recent touchpoints (half-life configurable) | Typical B2B recommendation |
| Position-Based | 40% first, 40% last, 20% split across middle | Common default |

### CLI Commands

```
# Run attribution report
python content-attribution.py report \
  --model time-decay \
  --half-life-days 14 \
  --window 90 \
  --crm hubspot \
  --analytics ga4 \
  --output markdown

# Compare models side-by-side
python content-attribution.py compare \
  --models "first-touch,linear,time-decay,position-based" \
  --window 90 \
  --output markdown

# Attribution by content type
python content-attribution.py by-type \
  --model time-decay \
  --group-by "blog,podcast,webinar,case-study,social" \
  --window 90

# Top performing content by attributed revenue
python content-attribution.py top-content \
  --model time-decay \
  --limit 20 \
  --min-revenue 1000
```

---

## Tool 3: Multi-Source Client Report

Combines data from multiple platforms into a unified client performance report.

### Data Sources and What They Contribute

| Source | Metrics |
|--------|---------|
| GA4 | Sessions, users, pageviews, conversions, traffic sources, engagement |
| HubSpot | Contacts, MQLs, SQLs, deals, pipeline value, lifecycle stage movement |
| Ahrefs | Organic keywords, ranking changes, backlinks, referring domains, DR |
| Gong | Call volume, sentiment trends, competitive mentions, objection frequency |

### CLI Commands

```
# Generate full multi-source client report
python client-report.py generate \
  --client "Acme Corp" \
  --period "2025-01" \
  --sources "ga4,hubspot,ahrefs,gong" \
  --format markdown     # Options: markdown, pdf, html, google-slides
  --include-recommendations true

# Generate comparison report (MoM or QoQ)
python client-report.py compare \
  --client "Acme Corp" \
  --period-a "2024-Q4" \
  --period-b "2025-Q1" \
  --sources "ga4,hubspot,ahrefs"

# Schedule recurring reports
python client-report.py schedule \
  --client "Acme Corp" \
  --frequency monthly \
  --sources "ga4,hubspot,ahrefs,gong" \
  --deliver-to "client@acme.com,am@agency.com"
```

### Report Output Structure

1. **Executive Summary** -- Key wins, concerns, and recommendations
2. **Traffic & Engagement** (GA4) -- Sessions, users, top pages, source breakdown
3. **SEO Performance** (Ahrefs) -- Keyword movement, new rankings, backlink growth
4. **Pipeline Impact** (HubSpot) -- New contacts, MQLs, SQLs, deals influenced
5. **Call Intelligence** (Gong) -- Sentiment trends, top objections, competitive landscape
6. **Attribution** -- Content-to-revenue mapping for the period
7. **Recommendations** -- Prioritized next actions with expected impact

---

## Data Flow

```
[Gong API] -----> Call Transcripts -----> Insight Extraction
                                              |
[GA4 API] ------> Session/Event Data -----+  |
                                           |  |
[HubSpot API] --> Contact/Deal Data ------+  |
                                           |  |
[Ahrefs API] --> Keyword/Backlink Data ---+  |
                                           |  |
                                           v  v
                                    [Attribution Engine]
                                           |
                                           v
                                    [Client Report Generator]
                                           |
                                           v
                                    Markdown / PDF / Slides
```

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GONG_API_KEY` | Gong API access token | For call analysis |
| `GONG_BASE_URL` | Gong API base URL | For call analysis |
| `GA4_PROPERTY_ID` | Google Analytics 4 property ID | For traffic data |
| `GA4_CREDENTIALS_PATH` | Path to GA4 service account JSON | For traffic data |
| `HUBSPOT_API_KEY` | HubSpot API key | For CRM data |
| `AHREFS_API_KEY` | Ahrefs API token | For SEO data |
| `REPORT_OUTPUT_DIR` | Directory for generated reports | No (default: `./reports`) |
| `ATTRIBUTION_WINDOW_DAYS` | Default attribution window | No (default: 90) |
| `TIME_DECAY_HALF_LIFE` | Half-life for time-decay model in days | No (default: 14) |

---

## Recommended Workflow Cadence

| Cadence | Action | Tool |
|---------|--------|------|
| Daily | Review new call transcripts for urgent signals | `gong-extractor.py analyze` |
| Weekly | Aggregate call trends and objection patterns | `gong-extractor.py trends` |
| Monthly | Generate multi-source client reports | `client-report.py generate` |
| Monthly | Run content attribution report | `content-attribution.py report` |
| Quarterly | Compare attribution models for model selection | `content-attribution.py compare` |
| Quarterly | Generate competitive intelligence roll-up | `gong-extractor.py competitors` |
| Quarterly | Build objection handling library | `gong-extractor.py objections` |

---

## Key Principles

- **Attribution is directional, not precise.** No model is "right." Use time-decay as default, compare quarterly.
- **Verbatim quotes are gold.** Always preserve exact customer language from calls.
- **Combine quantitative and qualitative.** Numbers from GA4/HubSpot + stories from Gong = compelling reports.
- **Competitive intelligence compounds.** Individual mentions are noise; patterns over 90 days are signal.
- **Reports should drive action.** Every report ends with prioritized recommendations.

---

## Related Skills

- **growth-engine** -- Test hypotheses surfaced from call insights
- **sales-pipeline** -- Feed call intelligence into pipeline scoring
- **finance-ops** -- Revenue data for financial modeling
- **content-strategy** -- Use attribution data to guide content planning
- **podcast-ops** -- Extract podcast content ideas from call pain points
