# openclaw-remotion-gorombo

A complete AI video production pipeline built on [Remotion](https://remotion.dev). Turn simple prompts into fully produced short-form videos with AI voiceover, generated b-roll, background music, animated captions, Three.js 3D visuals, and automated delivery to YouTube or Google Drive. The scaffold script automates all boilerplate so the AI focuses purely on creative content — and you can watch the video build in real time through Remotion Studio.

## Highlights

- **Automated scaffolding** — one command creates the entire composition structure with placeholder scenes, transitions, and all generation scripts ready to go
- **project.json is the single source of truth** — every creative decision is tracked in one file. Scripts read from it. Nothing is held only in AI memory
- **AI-generated video b-roll** — not stock footage. Real AI-generated video clips via Krea.ai with Ken Burns zoom effects
- **Image b-roll = no production ceiling** — video b-roll costs compute units (~36/month on Pro), but image b-roll with Ken Burns zoom is nearly free. At the Pro plan, that's ~1,300 image-based productions per month vs ~12 with video
- **Background music generation** — AI-generated instrumental tracks via ElevenLabs Music API, matched to the mood of your video
- **Three.js 3D visuals** — first-class support for 3D charts, graphs, geometric shapes, and character animations via @remotion/three. Scenes without b-roll get depth and dimension instead of flat motion graphics
- **Visible build process** — Remotion Studio lets you watch the video come together in real time as each scene gets filled in
- **Automation where it belongs, AI where it belongs** — scaffold handles boilerplate, scripts handle API calls, the AI only does creative work
- **Every asset is yours forever** — voiceover, b-roll, music, captions all saved locally. Your b-roll library grows with every production. Reuse assets across videos
- **Approval gates** — full manual control by default, or go full autopilot with auto-render and auto-publish to YouTube. Your choice per video
- **Faceless YouTube automation** — combine with Telegram, heartbeat, and cron to automate an entire YouTube channel. Script, produce, upload — hands-off
- **Full code control** — every frame is React/TSX. Pixel-level precision, version controlled, infinitely customizable

## Getting Started

### 1. Create a Remotion project

```bash
npx create-video@latest my-videos
cd my-videos
npm install
```

When prompted, select the **blank template**. This gives you the standard Remotion structure (`src/`, `public/`, `remotion.config.ts`) that the scaffold script expects. See [Remotion docs](https://remotion.dev/docs) for full setup details.

### 2. Add your API keys

Create a `.env` file in the project root:

```
ELEVENLABS_API_KEY=your-key-here
ELEVENLABS_VOICE_ID=your-default-voice-id
KREA_API_KEY=your-key-here
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

Keys are loaded from `.env` automatically by the production scripts. Never pass keys on the command line — they'll be visible in terminal output.

You can also set `voice.voice_id` per project in `project.json` to override the default.

### 3. Install the plugin

```bash
/plugin marketplace add dansasser/claude-code-marketplace
/plugin install openclaw-remotion-gorombo
```

### 4. Install system dependencies

```bash
# Required
apt-get install -y ffmpeg

# Required for emoji rendering on Linux
apt-get install -y fonts-noto-color-emoji

# Required for Three.js 3D visuals
npx remotion add @remotion/three

# Optional — Google Drive upload
npm install -g @googleworkspace/cli
gws auth login -s drive

# Optional — YouTube upload
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

Whisper.cpp is auto-installed on first caption generation — no manual setup needed.

## Preview Server

Remotion Studio lets you preview compositions in the browser before rendering. Start it after scaffolding a composition and keep it running — you can watch scenes come together in real time as the AI fills them in.

```bash
npx remotion studio
```

This launches a local server (default port 3000) where you can:
- Select compositions from the sidebar
- Scrub through the timeline
- Preview animations, transitions, 3D visuals, and captions
- Check content positioning within safe zones

Preview may be jerky with heavy compositions (multiple video layers + zoom effects). Always render to verify the final output.

## Commands

| Command | Description | Example |
|---|---|---|
| `/openclaw-remotion-gorombo:explainer` | Teach a topic in 5 animated scenes | `/openclaw-remotion-gorombo:explainer How DNS works` |
| `/openclaw-remotion-gorombo:product-promo` | Promote a product/service from its URL | `/openclaw-remotion-gorombo:product-promo https://example.com/product` |
| `/openclaw-remotion-gorombo:data-visualization` | Animate data as a 4-panel dashboard | `/openclaw-remotion-gorombo:data-visualization public/sales.csv` |
| `/openclaw-remotion-gorombo:research-report` | Research a topic, find stats, visualize | `/openclaw-remotion-gorombo:research-report AI adoption in small business` |
| `/openclaw-remotion-gorombo:testimonial` | Social proof from review platforms | `/openclaw-remotion-gorombo:testimonial "My Business Name"` |
| `/openclaw-remotion-gorombo:blog-promo` | Tease a blog post to drive clicks | `/openclaw-remotion-gorombo:blog-promo https://example.com/blog/my-post` |
| `/openclaw-remotion-gorombo:before-after` | Old way vs new way comparison | `/openclaw-remotion-gorombo:before-after https://example.com/product` |

## How It Works

Each command triggers a questionnaire, then follows a 9-step production pipeline. The scaffold automates all boilerplate — the AI focuses on creative content. Every decision is tracked in `project.json`.

1. **Scaffold** — `python3 scripts/scaffold.py <Name>` creates the full composition with two placeholder scenes, a working transition, all generation scripts, and `project.json`
2. **Script + questionnaire** — AI writes the voiceover script, asks about branding, voice, background music, render/publish preferences. Everything saved to `project.json`
3. **Voiceover** — generates speech via ElevenLabs. Audio durations drive scene lengths, not the other way around
4. **B-roll** — generates video clips via Krea.ai with Ken Burns zoom, or uses image b-roll for higher volume production
5. **Transitions** — fade transitions between scenes with PADDING_FRAMES to prevent voiceover overlap
6. **Captions** — transcribes voiceover with Whisper, AI proofreads brand names, TikTok-style word highlighting
7. **Background music** — generates an instrumental track via ElevenLabs Music API, mixed at 15% volume under voiceover
8. **Preview** — review in Remotion Studio, iterate with the AI, watch it come together in real time
9. **Render + deliver** — render to MP4, upload to Drive automatically, publish to YouTube if approved

## Three.js 3D Visuals

Scenes without b-roll don't have to be flat text on a dark background. The plugin includes full Three.js support via `@remotion/three` for:

- **3D charts and graphs** — bar charts, pie charts, line charts with depth, lighting, and camera angles
- **Geometric shapes and abstract visuals** — particle backgrounds, flowing data, tech imagery
- **3D characters and objects** — built from geometry in code, no external models needed
- **Glass and material effects** — cards with depth, reflections, and smooth animations

All 3D animations are driven by `useCurrentFrame()` — they sync perfectly with the Remotion timeline. See `rules/3d.md` for the full ThreeCanvas pattern.

## Dependencies

### Required

| Dependency | Purpose | Install |
|---|---|---|
| **Remotion 4.x** | Video framework | `npx create-video@latest` |
| **@remotion/three** | Three.js 3D support | `npx remotion add @remotion/three` |
| **ElevenLabs API** | Voiceover + background music | [elevenlabs.io](https://elevenlabs.io) — API key in `.env` |
| **Krea.ai API** | B-roll video/image generation | [krea.ai](https://krea.ai) — API key in `.env` |
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

The default model (Kling 2.5) uses ~550 compute units per video clip.

| Plan | Monthly CU | Video clips/month | Image stills/month | Video productions (~3 clips) | Image productions (~3 stills) |
|---|---|---|---|---|---|
| Free | Limited | ~2 | ~20 | ~1 | ~7 |
| Pro ($39/mo) | ~20,000 | ~36 | ~1,300 | ~12 | ~430 |

**The production ceiling depends on your b-roll choice.** Video b-roll gives cinematic quality but costs more compute. Image b-roll with Ken Burns zoom is nearly free by comparison — at the Pro plan, that's ~1,300 image-based productions per month vs ~12 with video. Every asset you generate is saved locally and reusable across future videos, so your b-roll library grows with every production.

## How We Compare — openclaw-remotion-gorombo vs Opus Agent

| | **Opus Agent Pro** | **openclaw-remotion-gorombo** |
|---|---|---|
| **Monthly cost** | $29/mo | $39/mo (Krea) + $0-5/mo (ElevenLabs) |
| **B-roll type** | Stock footage (Pexels) + AI stills | **AI-generated video** + Ken Burns zoom |
| **Background music** | Included | AI-generated via ElevenLabs Music API |
| **3D visuals** | No | Three.js — charts, shapes, characters |
| **Captions** | Included (animated) | Included (Whisper, free, unlimited, local) |
| **Voiceover** | Included | ElevenLabs (free tier ~12 videos, $5/mo for 30+) |
| **Productions/mo** | 15-30 | ~12 with video b-roll, **~1,300 with image b-roll** |
| **Model choice** | No | Yes — Kling, Veo, Seedance, Runway (quality/speed/cost tradeoffs) |
| **Creative control** | Template-based, limited adjustment | Full React/TSX — pixel-level precision |
| **Live preview** | No | Remotion Studio — watch it build in real time |
| **Scaffold automation** | No | One command creates all boilerplate |
| **Project tracking** | No | project.json tracks every decision |
| **Captions proofreading** | Automated only | AI + human review before render |
| **Custom scenes** | No | Unlimited — code anything React can render |
| **Multi-platform post** | TikTok, Reels, Shorts, LinkedIn, X | YouTube + Drive (extensible) |
| **Source control** | No | Git repo, full version history |
| **Automation** | No | Heartbeat/cron for faceless channels |
| **Ownership** | SaaS — their platform | Self-hosted — your code, your data |

### Cost Breakdown

| Component | Free path | Full path |
|---|---|---|
| Krea Pro (b-roll) | $39/mo | $39/mo |
| ElevenLabs (voiceover + music) | $0 (free tier, ~10 min/mo) | $5/mo (Starter, 30 min/mo) |
| Whisper (captions) | $0 (local) | $0 (local) |
| Rendering | $0 (local) | $0 (local) |
| YouTube/Drive upload | $0 | $0 |
| **Total** | **$39/mo** | **$44/mo** |

For $10-15 more than Opus Agent, you get AI-generated **video** b-roll (not stock footage), background music generation, Three.js 3D visuals, full code control, pixel-level precision, live preview, automated scaffolding, and the ability to automate production for faceless channels.

The extra cost also gets you **full platform access** beyond this plugin — Krea Pro includes image generation, upscaling, real-time canvas, and LoRA training. ElevenLabs gives you voiceover, music, and TTS for any project. You're paying for creative tools, not just a video maker.

## Content Safe Zones

All content defaults to portrait (9:16) with cross-platform safe zones:

| Edge | Margin | Why |
|---|---|---|
| Top | 210px | Status bar, search, platform header |
| Bottom | 320px | Action buttons, captions, CTA overlays |
| Left | 60px | Edge padding |
| Right | 120px | Action icons (TikTok/Reels) |

Safe area: **900x1400px centered** in 1080x1920 canvas. B-roll, backgrounds, and 3D visuals fill the full frame — only main content (headlines, text, CTAs) is restricted.

## Key Technical Patterns

- **B-roll zoom:** `overflow: hidden` on parent AbsoluteFill, `transform: scale()` on OffthreadVideo
- **Video looping:** `ffmpeg -stream_loop` (OffthreadVideo has no loop prop)
- **Caption timing:** `SWITCH_CAPTIONS_EVERY_MS = 1800` for breathing room after sentences
- **Last caption:** persists until scene ends
- **Transitions:** `PADDING_FRAMES >= TRANSITION_DURATION` or voiceovers overlap
- **B-roll is independent:** any scene can have b-roll regardless of foreground content
- **3D content:** wrap in `<ThreeCanvas>` with ambient + directional lighting, all animation via `useCurrentFrame()`
- **Background music:** `<Audio>` at composition level, `volume={0.15}`, conditional on `hasBackgroundMusic` prop
- **Emoji on Linux:** Install `fonts-noto-color-emoji` or emojis render as blank boxes
- **Scaffold:** `python3 scripts/scaffold.py <Name>` — creates everything, registers in Root.tsx

## Other Plugins in This Marketplace

- **[claude-ollama-agents](../claude-ollama-agents/README.md)** — Multi-agent system for delegating tasks to local Ollama models. Saves 70%+ context budget.
- **[preflight](../preflight/README.md)** — 8-gate CI/CD pipeline for Python packages. Cross-platform, multi-version, security scanning.
- **[pr-prep](../pr-prep/README.md)** — Automated PR preparation with local CI validation and smart error recovery.
- **[coderabbit-pr-fixer](../coderabbit-pr-fixer/README.md)** — Auto-apply CodeRabbit AI review suggestions to PRs.
- **[codex-pr-fixer](../codex-pr-fixer/README.md)** — Auto-apply OpenAI Codex review suggestions to PRs.

## References

- [Remotion Documentation](https://remotion.dev/docs)
- [Krea.ai API](https://docs.krea.ai)
- [ElevenLabs API](https://elevenlabs.io/docs)
- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [Google Workspace CLI](https://github.com/googleworkspace/cli)
- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp)

## Contact

Built and maintained by **Daniel T Sasser II** at [Gorombo](https://gorombo.com).

- **Website:** [gorombo.com](https://gorombo.com)
- **Email:** [contact@gorombo.com](mailto:contact@gorombo.com)
- **GitHub:** [github.com/dansasser](https://github.com/dansasser)
- **Marketplace:** [dansasser/claude-code-marketplace](https://github.com/dansasser/claude-code-marketplace)

## License

MIT
