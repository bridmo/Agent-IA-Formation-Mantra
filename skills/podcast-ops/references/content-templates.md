# Podcast Content Generation Templates

These templates are used by the `podcast-engine.py generate` command. Each template defines the structure and requirements for one of the 7 content types produced from podcast episodes.

---

## 3a. Short-Form Clips

**Platform:** TikTok, Instagram Reels, YouTube Shorts
**Length:** 30-90 seconds

### Clip Selection Criteria
- Contains a complete thought (setup + insight + conclusion)
- Speaker energy is high (pace, emphasis, emotion)
- No excessive "um/uh" or crosstalk
- Works without broader episode context
- Has a natural start and end point

### Output Format
```json
{
  "clip_id": "ep42-clip-01",
  "start_time": "00:14:32",
  "end_time": "00:15:47",
  "duration_seconds": 75,
  "speaker": "Guest Name",
  "hook_line": "First sentence that grabs attention",
  "topic": "Brief topic description",
  "caption": "Full caption text with hashtags (max 2200 chars)",
  "viral_score": 82,
  "suggested_text_overlay": "The key phrase to display on screen"
}
```

### Caption Template
```
[Hook line - restate the key insight in text]

[1-2 sentence context]

Full episode: [link]

#podcast #[topic] #[guest-name]
```

---

## 3b. X Threads

**Platform:** X (Twitter)
**Length:** 5-12 tweets

### Thread Structure
1. **Hook tweet** -- Provocative statement, surprising stat, or contrarian take. Must stand alone. No "Thread:" or "1/" prefix.
2. **Context tweet** -- Who said this and why it matters
3. **Insight tweets (3-8)** -- One insight per tweet. Each tweet must stand alone if shared individually.
4. **Tactical tweet** -- Specific actionable takeaway
5. **Closing tweet** -- Summary + link to full episode + CTA to follow

### Thread Rules
- Max 280 characters per tweet
- No tweet should start with "Thread:" or numbered prefix
- First tweet must be independently shareable
- Include line breaks for readability
- Use plain language, no jargon
- One idea per tweet maximum

### Template
```
Tweet 1 (Hook):
[Contrarian take or surprising insight from the episode]

Tweet 2 (Context):
I talked to @[guest] about [topic].

[One sentence about their credibility]

Here's what I learned:

Tweet 3-N (Insights):
[Insight in 1-2 sentences]

[Supporting detail or example]

Tweet N+1 (Tactical):
How to apply this:

- [Step 1]
- [Step 2]
- [Step 3]

Tweet N+2 (Close):
[One sentence summary]

Full conversation: [episode link]

Follow @[host] for more [topic] insights.
```

---

## 3c. LinkedIn Articles

**Platform:** LinkedIn
**Length:** 800-1500 words

### Article Structure
1. **Hook paragraph** (2-3 sentences) -- Start with a bold claim or story. No preamble.
2. **Context** (1 paragraph) -- Where this insight came from (the conversation)
3. **The Problem** (2-3 paragraphs) -- What most people get wrong
4. **The Framework/Insight** (3-5 paragraphs) -- The core content, broken into subheadings
5. **Tactical Application** (2-3 paragraphs) -- How the reader applies this today
6. **Closing** (1 paragraph) -- Restate the key takeaway + soft CTA

### LinkedIn Rules
- No hashtag spam (max 3 hashtags at the very end)
- Use line breaks liberally (LinkedIn rewards readability)
- Include a question at the end to drive comments
- Tag the guest in the post
- First 2 lines must hook because LinkedIn truncates
- Write in first person from the host's perspective
- Professional but conversational tone

### Template
```
[Bold opening statement or surprising data point]

[One sentence connecting to the episode conversation]

---

[The Problem]

Most [audience] think [common belief].

But when I talked to [Guest Name], [their role], they told me something that changed how I think about [topic]:

"[Key quote from episode]"

---

[Framework / Key Insights]

## [Subheading 1]

[2-3 paragraphs explaining the first key insight]

## [Subheading 2]

[2-3 paragraphs explaining the second key insight]

---

[Tactical Application]

Here's how to put this into practice:

1. [Step with brief explanation]
2. [Step with brief explanation]
3. [Step with brief explanation]

---

[Closing]

[One sentence restatement of the big idea]

What's your experience with [topic]? I'd love to hear in the comments.

Full episode with [Guest Name]: [link]

#[topic] #[industry] #podcast
```

---

## 3d. Newsletter Sections

**Platform:** Email newsletter (Beehiiv, Substack, ConvertKit)
**Length:** 200-400 words

### Section Structure
1. **Section header** -- Episode title or insight-driven headline
2. **TL;DR** (1 sentence) -- The single most important takeaway
3. **Key insights** (3-5 bullets) -- Scannable takeaways
4. **Pull quote** -- One memorable verbatim quote
5. **CTA** -- Link to full episode

### Template
```
## [Insight-Driven Headline]

**TL;DR:** [One sentence with the biggest takeaway]

This week I talked to [Guest], [role/credibility], about [topic]. Here's what stood out:

- **[Insight 1 label]:** [1-2 sentence explanation]
- **[Insight 2 label]:** [1-2 sentence explanation]
- **[Insight 3 label]:** [1-2 sentence explanation]

> "[Memorable quote from the episode]" -- [Guest Name]

[Listen to the full episode ->]([link])
```

---

## 3e. Quote Cards

**Platform:** Instagram, LinkedIn, X
**Format:** Image (1080x1080 or 1080x1350)

### Quote Selection Criteria
- 15 words or fewer (ideal), 25 words maximum
- Makes sense without context
- Emotionally resonant, surprising, or funny
- Attributable to a specific speaker

### Output Format
```json
{
  "quote_id": "ep42-quote-01",
  "text": "The exact quote text",
  "speaker": "Guest Name",
  "speaker_title": "CEO of Company",
  "episode": "Episode 42: Title",
  "timestamp": "00:23:14",
  "design_specs": {
    "background": "dark",
    "font_size": "large",
    "layout": "centered",
    "accent_color": "#brand-color",
    "include_headshot": true,
    "include_podcast_logo": true
  },
  "caption": "Caption text for the social post",
  "viral_score": 75
}
```

### Caption Template
```
[1-2 sentence context for the quote]

New episode with [Guest Name] is live. Link in bio.

#[podcast-name] #[topic]
```

---

## 3f. Blog Outlines

**Platform:** Website blog
**Format:** SEO-optimized outline ready for writing

### Outline Structure
1. **Target keyword** -- Primary keyword based on episode topic
2. **Title** (H1) -- SEO-optimized, includes keyword
3. **Meta description** -- 150-160 characters
4. **Introduction** -- Hook + what the reader will learn
5. **H2 sections** (3-6) -- Each maps to a key insight from the episode
6. **H3 subsections** -- Supporting details under each H2
7. **Conclusion** -- Summary + CTA
8. **Internal links** -- Suggested links to existing content

### Template
```markdown
# Blog Outline: [Episode Title/Topic]

**Target Keyword:** [primary keyword]
**Secondary Keywords:** [2-3 related keywords]
**Search Intent:** [informational/commercial/navigational]
**Estimated Word Count:** [1500-2500]

## Title Options
1. [SEO title option 1]
2. [SEO title option 2]
3. [SEO title option 3]

## Meta Description
[150-160 character meta description]

## Outline

### Introduction
- Hook: [specific hook approach]
- Context: [why this matters now]
- Promise: [what reader will learn]

### H2: [Section 1 - maps to episode insight]
- H3: [Subsection]
  - Key point from episode
  - Supporting data/example
- H3: [Subsection]
  - Key point from episode

### H2: [Section 2]
[... repeat structure]

### H2: [Section N]
[... repeat structure]

### Conclusion
- Restate key takeaway
- Actionable next step for reader
- CTA to episode

## Internal Link Opportunities
- [Existing post title] -> link from [section]
- [Existing post title] -> link from [section]

## Source: Episode [number] with [Guest], timestamp [range]
```

---

## 3g. YouTube Shorts Scripts

**Platform:** YouTube Shorts
**Length:** 30-60 seconds (75-150 words spoken)

### Script Structure
1. **Hook** (first 3 seconds) -- Text overlay + spoken hook. Must stop the scroll.
2. **Setup** (5-10 seconds) -- Brief context
3. **Payoff** (15-40 seconds) -- The insight, broken into digestible pieces
4. **CTA** (3-5 seconds) -- Subscribe or watch full episode

### Script Rules
- Write for speaking, not reading (contractions, short sentences)
- Include text overlay cues for key phrases
- Specify b-roll or visual suggestions
- Keep total word count under 150
- First sentence must create curiosity or tension

### Template
```
YOUTUBE SHORT SCRIPT
Episode: [ep number] - [title]
Duration: [estimated seconds]
Topic: [brief topic]

---

[TEXT OVERLAY: "Key phrase that hooks"]

HOOK (0-3s):
"[Opening line - question, bold claim, or surprising stat]"

SETUP (3-10s):
"[1-2 sentences of context. Who, what, why this matters.]"

PAYOFF (10-45s):
"[The core insight broken into 2-3 short paragraphs]"

"[Supporting point or example]"

"[The 'aha' moment or conclusion]"

[TEXT OVERLAY: "The key takeaway in 5 words"]

CTA (45-55s):
"[Subscribe/follow CTA + pointer to full episode]"

---

VISUAL NOTES:
- [Suggested b-roll or on-screen graphic]
- [Camera angle / energy note]
- [Any props or visual aids]
```
