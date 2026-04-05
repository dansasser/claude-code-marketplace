# remotion-gorombo

AI video production pipeline using Remotion. Turns simple prompts into fully produced short-form videos with voiceover, b-roll, animated captions, and YouTube upload.

## Getting Started

### 1. Create a Remotion project

```bash
npx create-video@latest my-videos
cd my-videos
npm install
```

This gives you a blank Remotion project with the standard structure (`src/`, `public/`, `remotion.config.ts`).

### 2. Add your API keys

Create a `.env` file in the project root:

```
ELEVENLABS_API_KEY=your-key-here
KREA_API_KEY=your-key-here
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

Keys are loaded from `.env` automatically by the production scripts. Never pass keys on the command line.

### 3. Install the plugin

```bash
/plugin marketplace add dansasser/claude-code-marketplace
/plugin install remotion-gorombo
```

### 4. Install system dependencies

```bash
# Required
apt-get install -y ffmpeg

# Required for emoji rendering on Linux
apt-get install -y fonts-noto-color-emoji

# Optional — Google Drive upload
npm install -g @googleworkspace/cli
gws auth login -s drive

# Optional — YouTube upload
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

Whisper.cpp is auto-installed on first caption generation — no manual setup needed.

## Preview Server

Remotion Studio lets you preview compositions in the browser before rendering.

```bash
npx remotion studio
```

This launches a local server (default port 3000) where you can:
- Select compositions from the sidebar
- Scrub through the timeline
- Preview animations, transitions, and captions
- Check content positioning within safe zones

Preview may be jerky with heavy compositions (multiple video layers + zoom effects). Always render to verify the final output.

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

## Dependencies

### Required

| Dependency | Purpose | Install |
|---|---|---|
| **Remotion 4.x** | Video framework | `npx create-video@latest` |
| **ElevenLabs API** | Voiceover generation | [elevenlabs.io](https://elevenlabs.io) — API key in `.env` |
| **Krea.ai API** | B-roll video generation | [krea.ai](https://krea.ai) — API key in `.env` |
| **ffmpeg** | Audio conversion, clip extension | `apt-get install ffmpeg` |
| **Whisper.cpp** | Caption transcription | Auto-installed on first use |
| **Noto Color Emoji** | Emoji rendering on Linux | `apt-get install fonts-noto-color-emoji` |

### Optional

| Dependency | Purpose | Install |
|---|---|---|
| **gws CLI** | Google Drive upload | `npm install -g @googleworkspace/cli` |
| **YouTube Data API v3** | YouTube upload | Enable in Google Cloud Console + OAuth desktop app |
| **google-api-python-client** | YouTube upload script | `pip install google-api-python-client google-auth-oauthlib` |

## Cost Estimate — B-Roll (Krea.ai)

The default model (Kling 2.5) uses ~550 compute units per clip.

| Plan | Monthly CU | Clips/month | Productions/month (~3 clips each) |
|---|---|---|---|
| Free | Limited | ~2 | ~1 |
| Pro ($39/mo) | ~20,000 | ~36 | ~12 |

A typical 30-second video uses 2-4 b-roll clips. At the Pro plan, that's roughly 12 productions per month.

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
- **Emoji on Linux:** Install `fonts-noto-color-emoji` or emojis render as blank boxes

## License

MIT
