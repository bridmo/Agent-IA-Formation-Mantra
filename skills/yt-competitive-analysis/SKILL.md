---
name: yt-competitive-analysis
description: >
  YouTube channel outlier detection and packaging pattern analysis. Scans predefined channel sets,
  calculates view multipliers to find breakout videos, and extracts proven title/thumbnail format
  skeletons for long-form and Shorts. Trigger: "youtube analysis", "yt competitive", "outlier
  detection", "youtube packaging", "channel analysis", "view multiplier", "video research".
  For content strategy from findings, see content-strategy. For ad creative, see ad-creative.
metadata:
  version: 1.0.0
---

You are an expert YouTube strategist specializing in outlier detection and packaging pattern analysis.

If `.brain/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Then read any detailed files it references (ICP, messaging, channels, SEO inventory) that are relevant to your task. Use that context and only ask for information not already covered or specific to this task.

## Overview

This skill analyzes YouTube channels to find outlier videos (those that dramatically outperform the channel's average), reverse-engineers their packaging (title + thumbnail patterns), and provides proven format skeletons you can adapt for your own content.

---

## CLI Commands

### Scan a Channel Set

```bash
python scripts/analyze.py \
  --channel-set "ai-creators" \
  --lookback-days 90 \
  --min-multiplier 3.0 \
  --output outliers.md
```

### Analyze a Single Channel

```bash
python scripts/analyze.py \
  --channel-id "UC_x5XG1OV2P6uZZ5FSM9Ttw" \
  --lookback-days 180 \
  --output channel_report.md
```

### Extract Packaging Patterns

```bash
python scripts/analyze.py \
  --input outliers.md \
  --format "long-form" \
  --output skeletons.md
```

### Compare Your Channel to Competitors

```bash
python scripts/analyze.py \
  --your-channel "UC_YOUR_ID" \
  --competitor-set "ai-creators" \
  --output comparison.md
```

---

## Predefined Channel Sets

### AI Creators
| Channel | Focus | Avg Views | Why Included |
|---------|-------|-----------|-------------|
| Fireship | Dev + AI news, fast-paced | 1-3M | Master of information density |
| Matt Wolfe | AI tools and news | 200-500K | Consistent packaging patterns |
| AI Explained | Deep technical AI | 300-800K | Long-form outlier factory |
| The AI Advantage | AI tutorials | 100-300K | Strong how-to packaging |
| Two Minute Papers | Research papers explained | 200-600K | Proven curiosity-gap titles |
| Yannic Kilcher | ML paper reviews | 50-150K | Technical audience benchmark |
| Wes Roth | AI news and commentary | 100-400K | High engagement rate |
| Matthew Berman | AI product reviews | 100-400K | Review format benchmark |

### Business Creators
| Channel | Focus | Avg Views | Why Included |
|---------|-------|-----------|-------------|
| Alex Hormozi | Business growth | 500K-2M | Hook mastery, contrarian angles |
| My First Million | Business ideas | 200-600K | Story-driven packaging |
| Noah Kagan | Entrepreneurship | 200-500K | Challenge/experiment format |
| Greg Isenberg | Startup ideas | 100-400K | Idea-format outliers |
| Colin and Samir | Creator economy | 200-500K | Documentary packaging |
| Pat Flynn | Online business | 50-200K | Evergreen how-to benchmark |
| Dan Martell | SaaS | 50-150K | B2B content benchmark |

---

## Output Interpretation Guide

### View Multiplier

The core metric. Calculated as:

```
View Multiplier = Video Views / Channel's Median Views (last 90 days)
```

| Multiplier | Classification | What It Means |
|-----------|---------------|---------------|
| < 0.5x | Underperformer | Packaging or topic missed the audience |
| 0.5-1.5x | Normal | Expected performance |
| 1.5-3x | Above Average | Good packaging or trending topic boost |
| 3-5x | Outlier | Strong signal -- analyze packaging pattern |
| 5-10x | Breakout | Exceptional -- likely hit algorithm + packaging sweet spot |
| 10x+ | Viral | Rare -- external factor or perfect storm. Study but don't expect to replicate |

### What to Look For in Outliers

1. **Title pattern** -- What structure does the title follow? (Question? Number list? Contrarian claim? News hook?)
2. **Thumbnail pattern** -- Face? Text overlay? Before/after? Contrast colors?
3. **Topic timing** -- Was this riding a news cycle or trend?
4. **Length** -- Is the outlier significantly longer or shorter than the channel's average?
5. **First 30 seconds** -- What hook type opens the video?

---

## Packaging Skeletons

### Long-Form Title Formats

| # | Skeleton | Example | When to Use |
|---|----------|---------|-------------|
| 1 | `[Authority] just [unexpected action]` | "Google just mass-deleted AI projects" | Breaking news, industry moves |
| 2 | `I [did X] for [time period]. Here's what happened.` | "I used only AI tools for 30 days. Here's what happened." | Personal experiment |
| 3 | `The [adjective] truth about [topic]` | "The ugly truth about AI coding tools" | Contrarian take |
| 4 | `How [specific person/company] [achieved result]` | "How Notion grew to $10B with no sales team" | Case study |
| 5 | `[Number] [things] that will [change/transform] [your X]` | "7 AI tools that will replace your entire workflow" | Listicle |
| 6 | `Why [everyone/nobody] is [wrong/right] about [topic]` | "Why nobody is talking about this AI breakthrough" | Contrarian + news |
| 7 | `[Topic] is [dead/over/changing]. Here's why.` | "Traditional SEO is dead. Here's why." | Paradigm shift |
| 8 | `I asked [expert/AI] to [task]. The result was [adj].` | "I asked GPT-5 to build my entire app. The result was shocking." | Experiment + authority |
| 9 | `Stop [doing X]. Do [Y] instead.` | "Stop learning Python. Do this instead." | Direct advice |
| 10 | `[Year] complete guide to [topic]` | "2026 complete guide to AI video editing" | Evergreen/SEO |

### Shorts Title Formats

| # | Skeleton | Example |
|---|----------|---------|
| 1 | `[Topic] in [X] seconds` | "Prompt engineering in 60 seconds" |
| 2 | `POV: you [scenario]` | "POV: you just discovered Claude can code" |
| 3 | `[Hot take] #[topic]` | "AI won't take your job. Lazy people will. #ai" |
| 4 | `Wait for it... #[topic]` | "Wait for it... #aitools" |
| 5 | `[Number] [thing] you're [doing wrong/missing]` | "3 AI prompts you're writing wrong" |

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `YOUTUBE_API_KEY` | Yes | YouTube Data API v3 key |
| `YT_CHANNEL_SETS_PATH` | No | Path to custom channel sets JSON (default: `./config/channel_sets.json`) |
| `YT_CACHE_DIR` | No | Cache directory for API responses (default: `./cache/yt/`) |
| `YT_LOOKBACK_DAYS` | No | Default lookback period (default: 90) |

---

## Related skills:

- `x-longform-post` -- Repurpose outlier findings into X long-form posts about content strategy.
- `autoresearch` -- Optimize your own video titles/thumbnails through variant testing.
- `expert-panel` -- Score your video concepts before production.
