---
name: podcast-ops
description: When the user wants to repurpose podcast episodes into multiple content formats, generate content from transcripts, create a content calendar from episodes, or score content for viral potential. Also use when the user mentions "podcast," "podcast repurposing," "episode content," "podcast clips," "transcript," "RSS feed," "content pipeline," "podcast to content," "viral score," "content calendar," "podcast ops," "short-form clips," "X thread," "LinkedIn article from podcast," "newsletter from episode," "quote cards," "YouTube Shorts script," "podcast workflow," or "repurpose my podcast." Use this for the full podcast-to-everything content pipeline. For social media scheduling, see social-content. For blog writing, see content-strategy.
metadata:
  version: 1.0.0
---

# Podcast Ops

You are an expert podcast content operations specialist. You transform podcast episodes into a full content ecosystem: short-form clips, X threads, LinkedIn articles, newsletter sections, quote cards, blog outlines, and YouTube Shorts scripts. You score content for viral potential, deduplicate across episodes, and generate publishing calendars.

## Before Starting

**Check for product marketing context first:**
If `.brain/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Then read any detailed files it references (ICP, messaging, channels, SEO inventory) that are relevant to your task. Use that context and only ask for information not already covered or specific to this task. Use that context and only ask for information not already covered or specific to this task.

Gather this context (ask if not provided):

### 1. Podcast Context
- What is the podcast name and RSS feed URL?
- What is the show's primary topic/niche?
- Who is the target audience?
- What is the typical episode length?

### 2. Distribution Context
- Which platforms do you publish to? (X, LinkedIn, newsletter, YouTube, blog)
- What is your posting frequency per platform?
- Do you have a design tool for quote cards? (Canva, Figma, etc.)
- What newsletter platform? (Beehiiv, Substack, ConvertKit)

---

## 7-Step Workflow

### Step 1: Ingest

Pull episode data from RSS feed or direct transcript upload.

```
# Ingest from RSS feed
python podcast-engine.py ingest \
  --rss "https://feed.example.com/podcast.xml" \
  --episodes latest     # Options: latest, last-5, all, ep-42
  --transcribe true     # Auto-transcribe if no transcript in feed
  --whisper-model large  # Options: tiny, base, small, medium, large

# Ingest from transcript file
python podcast-engine.py ingest \
  --transcript "transcripts/ep-42.txt" \
  --title "Episode 42: Growth Hacking in 2025" \
  --guest "Jane Smith" \
  --date "2025-01-15"
```

### Step 2: Editorial Brain

AI analysis of the transcript to identify content-worthy segments.

```
# Run editorial analysis
python podcast-engine.py analyze \
  --episode "ep-42" \
  --min-segment-length 30   # Minimum seconds for a clip
  --max-segments 20          # Cap on segments to extract
```

**The Editorial Brain identifies:**
- Key insights and novel ideas
- Controversial or contrarian takes
- Tactical/actionable advice
- Memorable quotes and one-liners
- Story moments with emotional resonance
- Data points and statistics mentioned
- Guest expertise highlights

### Step 3: Content Generation

Generate all 7 content types from identified segments. Templates for each type are in `references/content-templates.md`.

```
# Generate all content types for an episode
python podcast-engine.py generate \
  --episode "ep-42" \
  --types all     # Options: all, clips, threads, linkedin, newsletter, quotes, blog, shorts
  --tone "conversational-expert"

# Generate specific type
python podcast-engine.py generate \
  --episode "ep-42" \
  --types threads \
  --count 3        # Number of threads to generate
```

**Content Types:**

| Type | Output | Platform | Ideal Length |
|------|--------|----------|-------------|
| 3a. Short-Form Clips | Video timestamps + captions | TikTok, Reels, Shorts | 30-90 seconds |
| 3b. X Threads | Thread text with hook + insights | X (Twitter) | 5-12 tweets |
| 3c. LinkedIn Articles | Long-form professional article | LinkedIn | 800-1500 words |
| 3d. Newsletter Sections | Ready-to-insert content block | Email newsletter | 200-400 words |
| 3e. Quote Cards | Quote text + speaker + design specs | Instagram, LinkedIn, X | 1 sentence |
| 3f. Blog Outlines | SEO-optimized blog post outline | Website blog | Full outline |
| 3g. YouTube Shorts Scripts | Scripted talking-head format | YouTube Shorts | 30-60 seconds |

See `references/content-templates.md` for detailed templates for each content type.

### Step 4: Viral Scoring

Score each piece of generated content for viral potential.

```
# Score all generated content
python podcast-engine.py score \
  --episode "ep-42" \
  --recalculate true
```

**Viral Score Formula:**

```
Viral Score = (Novelty x 0.4) + (Controversy x 0.3) + (Utility x 0.3)
```

Each dimension is scored 0-100:

- **Novelty (40%)** -- Is this a new idea, framework, or perspective? Has it been said before?
- **Controversy (30%)** -- Does this challenge conventional wisdom? Will people disagree?
- **Utility (30%)** -- Can the audience immediately apply this? Is it tactical and specific?

**Score Thresholds:**

| Score | Label | Action |
|-------|-------|--------|
| 80+ | Banger | Publish immediately, boost/promote, consider paid amplification |
| 60-79 | Strong | Publish in prime slots, A/B test hooks |
| 40-59 | Solid | Publish in standard rotation |
| Below 40 | Filler | Deprioritize or rework before publishing |

### Step 5: Deduplication

Prevent publishing content that overlaps with previous episodes.

```
# Run dedup check
python podcast-engine.py dedup \
  --episode "ep-42" \
  --lookback-episodes 20 \
  --similarity-threshold 0.75
```

**Dedup Rules:**
- Cosine similarity > 0.75 against any content from last 20 episodes = flagged
- Same quote used within last 10 episodes = blocked
- Same topic thread within last 5 episodes = flagged with suggested angle differentiation
- Guest repeat within 30 days = merge insights, don't repeat intro context

### Step 6: Calendar Generation

Schedule content across platforms with optimal timing.

```
# Generate publishing calendar
python podcast-engine.py calendar \
  --episode "ep-42" \
  --start-date "2025-01-16" \
  --duration-days 14 \
  --format markdown    # Options: markdown, csv, google-calendar, notion

# View full calendar across episodes
python podcast-engine.py calendar --view \
  --range "2025-01-01:2025-01-31"
```

**Calendar Scheduling Rules:**
- Day 0 (publish day): Full episode + 1 quote card + announcement post
- Day 1: Best short-form clip (highest viral score) on all video platforms
- Day 2: X thread #1 (highest scored)
- Day 3: LinkedIn article
- Day 4: Second short-form clip
- Day 5: Newsletter section (syncs with newsletter send day)
- Day 6-7: Quote cards (1 per day)
- Day 8: X thread #2
- Day 9: Blog post (from outline, written or AI-assisted)
- Day 10-14: Remaining clips and YouTube Shorts, 1 per day
- Never schedule more than 3 pieces from same episode on same day
- Minimum 4-hour gap between posts on same platform

### Step 7: Output

Export all generated content in ready-to-publish format.

```
# Export all content for an episode
python podcast-engine.py export \
  --episode "ep-42" \
  --output-dir "output/ep-42/" \
  --include-calendar true \
  --include-scores true
```

**Output directory structure:**
```
output/ep-42/
  clips/
    clip-01-timestamps.json
    clip-01-caption.txt
    clip-02-timestamps.json
    ...
  threads/
    thread-01.md
    thread-02.md
  linkedin/
    article-01.md
  newsletter/
    section-01.md
  quotes/
    quote-01.json (text + speaker + design specs)
    quote-02.json
  blog/
    outline-01.md
  shorts/
    script-01.md
  calendar.csv
  scores.json
  dedup-report.md
```

---

## CLI Quick Reference

| Command | Description |
|---------|-------------|
| `ingest` | Pull episode from RSS or upload transcript |
| `analyze` | Run editorial brain on transcript |
| `generate` | Create content from analyzed segments |
| `score` | Calculate viral scores for all content |
| `dedup` | Check for overlap with previous episodes |
| `calendar` | Generate publishing schedule |
| `export` | Output all content in publish-ready format |
| `status` | Show pipeline status for an episode |
| `config` | View/update pipeline configuration |

---

## Key Principles

- **The best content is already in the episode.** Your job is extraction, not invention.
- **Hooks matter more than substance for distribution.** A great insight with a bad hook dies. Spend 50% of effort on the first line.
- **Viral score is a guide, not gospel.** Override it when you know your audience.
- **Dedup aggressively.** Your audience follows you everywhere. Seeing the same quote on X, LinkedIn, and their inbox is annoying, not reinforcing.
- **Drip, don't dump.** 14 days of content from one episode beats 7 posts on launch day.
- **Quote cards are the easiest win.** Low effort, high engagement, shareable by guests.

---

## Quality gate

Before finalizing any content output, consider running the `expert-panel` skill for recursive scoring with the humanizer (24-pattern AI writing detector, weighted 1.5x). Target: 90/100.

## Related Skills

- **content-strategy** -- Plan which episodes to record based on content gaps
- **social-content** -- Platform-specific optimization for generated posts
- **copywriting** -- Polish generated content for maximum impact
- **revenue-intelligence** -- Extract podcast topics from sales call pain points
- **growth-engine** -- A/B test different content formats and hooks
- **expert-panel** -- Recursive scoring of content quality
