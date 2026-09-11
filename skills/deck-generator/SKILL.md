---
name: deck-generator
description: >
  AI-generated slide decks with Imagen 4.0 API visuals and Google Slides integration. Supports
  style presets (whiteboard, corporate, minimalist, dark-tech, playful, editorial). Builds complete
  presentations from content briefs. Trigger: "deck generator", "slide deck", "build a deck",
  "create presentation", "generate slides", "pitch deck", "imagen slides".
metadata:
  version: 1.0.0
---

You are an expert presentation designer who builds high-impact slide decks using AI-generated visuals and structured storytelling.

If `.brain/product-marketing-context.md` exists (or `.claude/product-marketing-context.md` in older setups), read it before asking questions. Then read any detailed files it references (ICP, messaging, channels, SEO inventory) that are relevant to your task. Use that context and only ask for information not already covered or specific to this task.

## Overview

Deck Generator takes a content brief and produces a complete slide deck with AI-generated visuals (via Imagen 4.0 API), structured narrative flow, and optional Google Slides export. Cost: ~4 cents per image. Speed: ~2 minutes for a 14-slide deck.

---

## 4-Step Workflow

### Step 1: Content Intake
Collect from user:
- **Topic / title** of the deck
- **Audience** (investors, team, customers, conference)
- **Slide count** target (default: 12-16)
- **Key messages** (3-5 bullet points the deck must convey)
- **Style preset** (see table below)
- **Existing assets** (logos, brand colors, data charts to include)

### Step 2: Content Structure
Generate a content JSON with the narrative arc:
- **Opening** (1-2 slides): Hook + context setting
- **Problem** (2-3 slides): Pain point articulation
- **Solution** (3-4 slides): Your approach + differentiation
- **Proof** (2-3 slides): Data, testimonials, case studies
- **Close** (1-2 slides): CTA + next steps

### Step 3: Visual Generation
For each slide, generate a background or hero image using Imagen 4.0:
- Prompt constructed from slide content + style preset
- Images generated in batch (not one-by-one)
- Resolution: 1920x1080 (16:9)
- Format: PNG

### Step 4: Assembly & Export
- Assemble slides with text overlays and generated visuals
- Export to Google Slides (if integration configured) or PPTX
- Generate speaker notes for each slide

---

## Style Presets

| Preset | Visual Style | Best For | Colors |
|--------|-------------|----------|--------|
| `whiteboard` | Hand-drawn sketch aesthetic, marker-style lines | Internal brainstorms, workshops | Black on white, accent blue |
| `corporate` | Clean, professional, geometric shapes | Board meetings, enterprise sales | Navy, gray, white |
| `minimalist` | Maximum whitespace, single focal image | Keynotes, thought leadership | Monochrome + 1 accent |
| `dark-tech` | Dark backgrounds, glowing accents, futuristic | Tech conferences, product launches | Dark gray, electric blue/green |
| `playful` | Bold colors, rounded shapes, illustrations | Consumer products, social media | Bright palette, pastels |
| `editorial` | Magazine-quality photography, serif typography | Case studies, annual reports | Neutral tones, gold accents |

---

## CLI Command

```bash
python scripts/generate-deck.py \
  --title "Deck Title" \
  --audience "investors" \
  --slides 14 \
  --style "minimalist" \
  --messages "msg1" "msg2" "msg3" \
  --brand-colors "#1a1a2e,#16213e,#0f3460" \
  --logo "./assets/logo.png" \
  --output-format "gslides" \
  --output "./output/deck.pptx" \
  --imagen-model "imagen-4.0" \
  --batch-size 4 \
  --speaker-notes \
  --include-appendix
```

**Flags:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--title` | Yes | -- | Deck title |
| `--audience` | Yes | -- | Target audience |
| `--slides` | No | 14 | Number of slides |
| `--style` | No | minimalist | Style preset name |
| `--messages` | Yes | -- | Key messages (space-separated strings) |
| `--brand-colors` | No | preset default | Comma-separated hex colors |
| `--logo` | No | none | Path to logo file |
| `--output-format` | No | pptx | `pptx`, `gslides`, `pdf` |
| `--output` | No | ./output/deck.pptx | Output file path |
| `--imagen-model` | No | imagen-4.0 | Imagen model version |
| `--batch-size` | No | 4 | Images per batch call |
| `--speaker-notes` | No | false | Generate speaker notes |
| `--include-appendix` | No | false | Add data appendix slides |

---

## Content JSON Format

```json
{
  "title": "Why We're Building X",
  "style": "minimalist",
  "slides": [
    {
      "id": 1,
      "type": "title",
      "headline": "Why We're Building X",
      "subhead": "A new approach to [problem]",
      "image_prompt": "Abstract minimal landscape, single focal point, soft gradient background",
      "speaker_notes": "Welcome everyone. Today I want to walk you through..."
    },
    {
      "id": 2,
      "type": "problem",
      "headline": "The $50B Problem Nobody Talks About",
      "bullets": [
        "82% of teams waste 10+ hrs/week on [task]",
        "Current solutions cost 3x more than they should",
        "The gap is growing, not shrinking"
      ],
      "image_prompt": "Dramatic contrast image showing complexity and chaos, dark tones",
      "speaker_notes": "Let me set the stage with some numbers..."
    }
  ]
}
```

**Slide types:** `title`, `problem`, `solution`, `proof`, `data`, `quote`, `comparison`, `timeline`, `team`, `cta`, `appendix`

---

## Google Slides Integration Setup

### Prerequisites
1. Google Cloud project with Slides API enabled
2. Service account or OAuth2 credentials
3. Imagen 4.0 API access (Vertex AI)

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_SLIDES_CREDENTIALS` | For gslides output | Path to Google service account JSON |
| `GOOGLE_SLIDES_TEMPLATE_ID` | No | Template slide deck ID to clone |
| `IMAGEN_API_KEY` | Yes | Vertex AI / Imagen API key |
| `IMAGEN_PROJECT_ID` | Yes | Google Cloud project ID |
| `IMAGEN_REGION` | No | API region (default: us-central1) |

### Setup Steps
1. Enable Google Slides API in your GCP project
2. Create a service account and download credentials JSON
3. Share the target Google Drive folder with the service account email
4. Set `GOOGLE_SLIDES_CREDENTIALS` to the path of the JSON file
5. (Optional) Create a template deck and set `GOOGLE_SLIDES_TEMPLATE_ID`

---

## Cost & Speed

| Metric | Value |
|--------|-------|
| Image generation cost | ~$0.04 per image (Imagen 4.0) |
| 14-slide deck total cost | ~$0.56 |
| Generation time (14 slides) | ~2 minutes |
| Google Slides upload | ~30 seconds additional |
| Batch efficiency | 4 images per API call recommended |

---

## Related skills:

- `expert-panel` -- Score deck content before generating visuals.
- `autoresearch` -- Optimize slide copy (headlines, CTAs) through variant testing before building the deck.
- `sales-playbook` -- Use deck-generator to build proposal decks that accompany pricing packages.
