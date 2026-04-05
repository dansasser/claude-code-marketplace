# remotion-gorombo

AI video production pipeline using Remotion. Turns simple prompts into fully produced short-form videos with voiceover, b-roll, animated captions, and YouTube upload.

## Installation

```bash
/plugin install remotion-gorombo
```

Or via marketplace:

```bash
/plugin marketplace add dansasser/claude-code-marketplace
/plugin install remotion-gorombo
```

## Commands

| Command | Description | Example |
|---|---|---|
| `/remotion-gorombo:explainer` | Teach a topic in 5 animated scenes | `/remotion-gorombo:explainer How DNS works` |
| `/remotion-gorombo:product-promo` | Promote a product/service from its URL | `/remotion-gorombo:product-promo https://example.com/product` |
| `/remotion-gorombo:data-visualization` | Animate data as a 4-panel dashboard | `/remotion-gorombo:data-visualization public/sales.csv` |
| `/remotion-gorombo:research-report` | Research a topic, find stats, visualize | `/remotion-gorombo:research-report AI adoption in small business` |
| `/remotion-gorombo:testimonial` | Social proof from review platforms | `/remotion-gorombo:testimonial "Gorombo LLC"` |
| `/remotion-gorombo:blog-promo` | Tease a blog post to drive clicks | `/remotion-gorombo:blog-promo https://example.com/blog/my-post` |
| `/remotion-gorombo:before-after` | Old way vs new way comparison | `/remotion-gorombo:before-after https://example.com/product` |

## How It Works

Each command triggers a questionnaire (2-3 questions), then follows a 7-step production pipeline:

1. **Composition structure** — creates isolated asset directories
2. **Voiceover** — generates speech via ElevenLabs, audio durations drive scene lengths
3. **B-roll** — generates video clips via Krea.ai with Ken Burns zoom effect
4. **Transitions** — fade transitions between scenes (1-1.5 seconds)
5. **Captions** — transcribes voiceover with Whisper, TikTok-style word highlighting
6. **Preview** — launches Remotion Studio for review
7. **Delivery** — render, upload to Google Drive and/or YouTube (when prompted)

## Prerequisites

- **Remotion 4.x** — `npx create-video@latest`
- **ElevenLabs API key** — voiceover generation (`ELEVENLABS_API_KEY`)
- **Krea.ai API key** — b-roll video generation (`KREA_API_KEY`)
- **ffmpeg** — clip extension and audio conversion
- **Whisper.cpp** — auto-installed on first caption generation
- **Optional:** `gws` CLI for Google Drive upload
- **Optional:** YouTube Data API v3 for YouTube upload

## Content Safe Zones

All content defaults to portrait (9:16) with cross-platform safe zones:

| Edge | Margin | Why |
|---|---|---|
| Top | 210px | Status bar, search, platform header |
| Bottom | 320px | Action buttons, captions, CTA overlays |
| Left | 60px | Edge padding |
| Right | 120px | Action icons (TikTok/Reels) |

Safe area: **900x1400px centered** in 1080x1920 canvas. B-roll and backgrounds fill the full frame — only main content (headlines, text, CTAs) is restricted.

## Key Technical Patterns

- **B-roll zoom:** `overflow: hidden` on parent AbsoluteFill, `transform: scale()` on OffthreadVideo
- **Video looping:** `ffmpeg -stream_loop` (OffthreadVideo has no loop prop)
- **Caption timing:** `SWITCH_CAPTIONS_EVERY_MS = 1800` for breathing room after sentences
- **Last caption:** persists until scene ends
- **Transitions:** `PADDING_FRAMES >= TRANSITION_DURATION` or voiceovers overlap
- **B-roll is independent:** any scene can have b-roll regardless of foreground content

## License

MIT
