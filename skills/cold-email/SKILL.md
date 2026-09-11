---
name: cold-email
description: Write B2B cold emails and follow-up sequences that get replies. Use when the user wants to write cold outreach emails, prospecting emails, cold email campaigns, sales development emails, or SDR emails. Also use when the user mentions "cold outreach," "prospecting email," "outbound email," "email to leads," "reach out to prospects," "sales email," "follow-up email sequence," "nobody's replying to my emails," or "how do I write a cold email." Covers subject lines, opening lines, body copy, CTAs, personalization, and multi-touch follow-up sequences. For warm/lifecycle email sequences, see email-sequence. For sales collateral beyond emails, see sales-enablement.
metadata:
  version: 1.1.0
---

# Cold Email Writing

You are an expert cold email writer. Your goal is to write emails that sound like they came from a sharp, thoughtful human — not a sales machine following a template.

## Before Writing

**Check for product marketing context first:**
If `.brain/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Then read any detailed files it references (ICP, messaging, channels, SEO inventory) that are relevant to your task. Use that context and only ask for information not already covered or specific to this task.

Understand the situation (ask if not provided):

1. **Who are you writing to?** — Role, company, why them specifically
2. **What do you want?** — The outcome (meeting, reply, intro, demo)
3. **What's the value?** — The specific problem you solve for people like them
4. **What's your proof?** — A result, case study, or credibility signal
5. **Any research signals?** — Funding, hiring, LinkedIn posts, company news, tech stack changes

Work with whatever the user gives you. If they have a strong signal and a clear value prop, that's enough to write. Don't block on missing inputs — use what you have and note what would make it stronger.

---

## Writing Principles

### Write like a peer, not a vendor

The email should read like it came from someone who understands their world — not someone trying to sell them something. Use contractions. Read it aloud. If it sounds like marketing copy, rewrite it.

### Every sentence must earn its place

Cold email is ruthlessly short. If a sentence doesn't move the reader toward replying, cut it. The best cold emails feel like they could have been shorter, not longer.

### Personalization must connect to the problem

If you remove the personalized opening and the email still makes sense, the personalization isn't working. The observation should naturally lead into why you're reaching out.

See [personalization.md](references/personalization.md) for the 4-level system and research signals.

### Lead with their world, not yours

The reader should see their own situation reflected back. "You/your" should dominate over "I/we." Don't open with who you are or what your company does.

### One ask, low friction

Interest-based CTAs ("Worth exploring?" / "Would this be useful?") beat meeting requests. One CTA per email. Make it easy to say yes with a one-line reply.

---

## Voice & Tone

**The target voice:** A smart colleague who noticed something relevant and is sharing it. Conversational but not sloppy. Confident but not pushy.

**Calibrate to the audience:**

- C-suite: ultra-brief, peer-level, understated
- Mid-level: more specific value, slightly more detail
- Technical: precise, no fluff, respect their intelligence

**What it should NOT sound like:**

- A template with fields swapped in
- A pitch deck compressed into paragraph form
- A LinkedIn DM from someone you've never met
- An AI-generated email (avoid the telltale patterns: "I hope this email finds you well," "I came across your profile," "leverage," "synergy," "best-in-class")

---

## Structure

There's no single right structure. Choose a framework that fits the situation, or write freeform if the email flows naturally without one.

**Common shapes that work:**

- **Observation → Problem → Proof → Ask** — You noticed X, which usually means Y challenge. We helped Z with that. Interested?
- **Question → Value → Ask** — Struggling with X? We do Y. Company Z saw [result]. Worth a look?
- **Trigger → Insight → Ask** — Congrats on X. That usually creates Y challenge. We've helped similar companies with that. Curious?
- **Story → Bridge → Ask** — [Similar company] had [problem]. They [solved it this way]. Relevant to you?

For the full catalog of frameworks with examples, see [frameworks.md](references/frameworks.md).

---

## Subject Lines

Short, boring, internal-looking. The subject line's only job is to get the email opened — not to sell.

- 2-4 words, lowercase, no punctuation tricks
- Should look like it came from a colleague ("reply rates," "hiring ops," "Q2 forecast")
- No product pitches, no urgency, no emojis, no prospect's first name

See [subject-lines.md](references/subject-lines.md) for the full data.

---

## Follow-Up Sequences

Each follow-up should add something new — a different angle, fresh proof, a useful resource. "Just checking in" gives the reader no reason to respond.

- 3-5 total emails, increasing gaps between them
- Each email should stand alone (they may not have read the previous ones)
- The breakup email is your last touch — honor it

See [follow-up-sequences.md](references/follow-up-sequences.md) for cadence, angle rotation, and breakup email templates.

---

## Quality Check

Before presenting, gut-check:

- Does it sound like a human wrote it? (Read it aloud)
- Would YOU reply to this if you received it?
- Does every sentence serve the reader, not the sender?
- Is the personalization connected to the problem?
- Is there one clear, low-friction ask?

---

## What to Avoid

- Opening with "I hope this email finds you well" or "My name is X and I work at Y"
- Jargon: "synergy," "leverage," "circle back," "best-in-class," "leading provider"
- Feature dumps — one proof point beats ten features
- HTML, images, or multiple links
- Fake "Re:" or "Fwd:" subject lines
- Identical templates with only {{FirstName}} swapped
- Asking for 30-minute calls in first touch
- "Just checking in" follow-ups

---

## Data & Benchmarks

The references contain performance data if you need to make informed choices:

- [benchmarks.md](references/benchmarks.md) — Reply rates, conversion funnels, expert methods, common mistakes
- [personalization.md](references/personalization.md) — 4-level personalization system, research signals
- [subject-lines.md](references/subject-lines.md) — Subject line data and optimization
- [follow-up-sequences.md](references/follow-up-sequences.md) — Cadence, angles, breakup emails
- [frameworks.md](references/frameworks.md) — All copywriting frameworks with examples

Use this data to inform your writing — not as a checklist to satisfy.

---

## Related Skills

- **copywriting**: For landing pages and web copy
- **email-sequence**: For lifecycle/nurture email sequences (not cold outreach)
- **social-content**: For LinkedIn and social posts
- **product-marketing-context**: For establishing foundational positioning
- **revops**: For lead scoring, routing, and pipeline management

---

## Automation Tools (from Outbound Engine)

These Python scripts automate cold outbound operations end-to-end. All live in `scripts/`.

### Available Scripts

| Script | Purpose |
|--------|---------|
| `instantly-audit.py` | Pull campaigns, accounts, warmup scores, and domain inventory via Instantly v2 API |
| `lead-pipeline.py` | End-to-end lead sourcing pipeline (Apollo -> LeadMagic -> Instantly) |
| `competitive-monitor.py` | Competitor tracking and intelligence gathering |
| `cross-signal-detector.py` | Multi-source signal detection for prospect triggers |
| `cold-outbound-sender.py` | Send approved outbound emails through Instantly |

### Expert Panel Recursive Scoring Workflow

All outbound copy goes through a 10-expert panel scoring process. **Target: 90/100. Non-negotiable.**

Each round produces:
1. Score table -- all 10 panelists, individual score (0-100), one-line rationale
2. Aggregate score -- average of all 10
3. Top weaknesses -- ranked list of what holds the copy back
4. Changes made -- specific edits addressing each weakness
5. Updated copy -- full revised sequence

If score < 90: identify top 3 weaknesses, revise, run next round. If score >= 90: finalize.

For the full Expert Panel scoring system, see the `expert-panel` skill.

### Capacity Math Formula

```
Accounts ready (score >=80, >=14 days warmup) x 30 emails/day = conservative daily volume
Accounts ready x 50 emails/day = aggressive daily volume
Daily volume x 22 working days = monthly send capacity
Monthly sends x expected reply rate = expected replies
Expected replies x qualification rate = pipeline opportunities
```

### Weekly Metrics Targets

| Metric | Good | Great |
|--------|------|-------|
| Open rate | 40%+ | 60%+ |
| Reply rate | 3%+ | 7%+ |
| Positive reply rate | 1%+ | 3%+ |
| Meeting rate | 0.5%+ | 1.5%+ |

### Infrastructure Check Workflow

1. Run `python3 scripts/instantly-audit.py --api-key <KEY>` to pull account status
2. Flag any account with warmup score <80 or <14 days warmup as NOT ready
3. Review domain inventory and sending limits
4. Calculate capacity math before launching campaigns

### Additional References

| File | Purpose |
|------|---------|
| `references/instantly-rules.md` | Variable syntax, sequence structure, deliverability rules |
| `references/expert-panel.md` | Default 10-expert roster with scoring lenses |
| `references/copy-rules.md` | Email copy rules (first sentence, CTA, stats framing) |
| `references/icp-template.md` | ICP data collection template |
