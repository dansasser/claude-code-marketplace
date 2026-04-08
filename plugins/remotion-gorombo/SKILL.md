---
name: remotion-best-practices
description: Best practices for Remotion - Video creation in React
metadata:
  tags: remotion, video, react, animation, composition
---

## When to use

Use this skill for the complete video production pipeline — from script writing through rendering and delivery. It includes scaffolding automation, voiceover/caption/music generation scripts, and detailed rule files for every Remotion pattern you'll need.

## Prerequisites

You need a Remotion project. If you don't have one, create it with `npx create-video@latest` and select the **blank template**. The project must have a `remotion.config.ts` at its root — the scaffold script uses this to locate the project.

Required `.env` variables in the project root:
- `ELEVENLABS_API_KEY` — for voiceover and background music generation
- `ELEVENLABS_VOICE_ID` — default voice (optional if set per-project in project.json)
- `KREA_API_KEY` — for b-roll generation (if using Krea)

On first use, save the Remotion project location to memory so you can find it in future sessions.

## Scene planning

Before implementing any scenes, follow this sequence.

**API keys** (ElevenLabs, Krea, etc.) are loaded from `.env` by the scripts automatically. NEVER pass API keys on the command line — they will be visible in terminal output. Always use the provided scripts:
- `npx tsx src/<Name>/generate-voiceover.ts` — generates voiceover audio (reads scenes from project.json)
- `npx tsx src/<Name>/generate-captions.ts` — transcribes voiceover to captions (reads scene IDs from project.json)
- `npx tsx src/<Name>/generate-background-music.ts` — generates background music (reads mood from project.json)
- `npx tsx src/generate-broll.ts --output "public/<name>/broll/" --prompts prompts.json` — generates b-roll clips

### Content safe zone (default)

All main content (headlines, key text, CTAs, stats, graphics) must be **centered vertically and horizontally**, building outward from dead center. This is the default unless explicitly overridden.

B-roll, backgrounds, decorative elements, and captions are NOT restricted to the safe zone — they fill the full frame.

If the prompt doesn't specify landscape, default to portrait (9:16).

**Portrait (9:16) — 1080x1920 canvas:**

Universal cross-platform safe zone (works on TikTok, Reels, and Shorts):
- **Top:** 210px (status bar, search, platform header)
- **Bottom:** 320px (action buttons, captions, CTA overlays)
- **Left:** 60px
- **Right:** 120px (action icons on TikTok/Reels)
- **Safe area:** 900x1400px centered

Platform UI is updated frequently — these values are current as of early 2026.

**Landscape (16:9):** Full frame is usable, no safe zone restriction.

**First frame rule:** Scene 1's first animation must start at frame 0 with no delay AND start at visible values (e.g. scale 0.8, opacity 0.5). Spring animations start from 0 and take several frames to reach visible values — if starting from scale 0 or opacity 0, the first frames are blank which looks broken as a thumbnail and on autoplay.

### Step 1: Scaffold the composition
Run the scaffold script from the Remotion project root. The script is located in the plugin's `scripts/` directory:

```bash
python3 <path-to-plugin>/scripts/scaffold.py <CompositionName>
```

This automatically creates the full composition structure:
- `src/<Name>/` — index.tsx, Scene1.tsx (placeholder), get-audio-duration.ts, generate-voiceover.ts, generate-captions.ts, generate-background-music.ts, Captions.tsx, project.json
- `public/<name>/voiceover/`, `public/<name>/broll/`, `public/<name>/captions/`
- Registers the composition in `src/Root.tsx`

After scaffolding, **start (or restart) Remotion Studio** so it picks up the new composition:

```bash
npx remotion studio
```

The placeholder scene is immediately previewable. Do NOT manually create these files — use the script.

The scaffold creates `project.json` in the composition directory. This file is the **single source of truth** — all scripts read from it, and you update it at every step. Every creative decision, every configuration value, every approval status goes into this file.

### Step 2: Script and questionnaire
First, decide how many scenes the video needs (typically 3-5). Then write the voiceover script for all scenes. Audio durations drive scene lengths (not the other way around).

When presenting the script for approval, ALWAYS show for every scene:
- Headline (what appears on screen)
- Voiceover (exact words the narrator says)
- Visual description

After the script, ask the user:
- What's your company/brand name and website? (for captions proofreading and on-screen text)
- What voice should we use? (provide the ElevenLabs voice ID, or leave blank to use ELEVENLABS_VOICE_ID from .env)
- Background music? (yes/no, mood: upbeat/corporate/cinematic/ambient)
- Auto-render when complete? (defaults to no)
- Publishing to YouTube? → if yes:
  - What links should go in the description? (website, socials, relevant pages)
  - Tags and category?
  - Auto-publish or manual approval? (defaults to manual)

Use these exact values for approval gates: `"pending"` (wait for approval), `"approved"` (auto-proceed), `"completed"` (done). Do not use booleans or yes/no.

**Update project.json:** Fill in:
- `branding.company`, `branding.website`, `branding.socials` — from the user's answers
- `voice.voice_id` — the user's chosen voice ID (empty = use env var)
- `background_music.enabled` and `background_music.mood` — from the user's answer
- `render` — "pending" or "approved"
- `youtube.publish` — "pending" or "approved" (only if publishing to YouTube)
- `youtube.links`, `youtube.tags`, `youtube.category` — only if publishing to YouTube
- Each scene's `headline`, `voiceover`, and `visual` fields

If the scene count changed, duplicate scene entries in the `scenes` array to match. Also duplicate the placeholder Scene1.tsx for each additional scene (rename the component export to Scene2, Scene3, etc.) and update index.tsx to import all scenes and wire them into the TransitionSeries with fade transitions between each. Load [./rules/compositions.md](./rules/compositions.md) for composition patterns and [./rules/transitions.md](./rules/transitions.md) for the TransitionSeries wiring pattern.

### Step 3: Voiceover generation
The voiceover script reads directly from `project.json` — no need to edit the script itself. Just make sure the voiceover text is filled in for each scene in project.json (Step 2), then run:

```bash
npx tsx src/<Name>/generate-voiceover.ts
```

After voiceover files are generated, **update `index.tsx`**: replace the placeholder `calculateMetadata` with one that reads actual audio durations using `getAudioDuration`. The composition duration should be driven by the voiceover audio, not hardcoded frame counts. Load [./rules/voiceover.md](./rules/voiceover.md) for the exact calculateMetadata pattern.

### Step 4: B-roll
Decide which scenes get b-roll backgrounds. Allocate ~2 b-roll clips per 30 seconds of video. Any scene can have b-roll — it's a background layer independent of the foreground content (text, charts, animated diagrams, anything). Load [./rules/b-roll.md](./rules/b-roll.md) for generation, zoom effects, and layering details.

**Update project.json:** For each scene, fill in `broll.type` ("image", "video", or "none") and `broll.prompt`.

### Step 5: Transitions
The scaffold sets up a basic TransitionSeries. When adding multiple scenes (Step 2), add `<TransitionSeries.Transition>` elements with `fade()` between each sequence at 1-1.5 seconds (30-45 frames at 30fps). Define `PADDING_FRAMES` (silence after voiceover ends) and ensure it is >= `TRANSITION_DURATION` or voiceovers will overlap during transitions. Audio stays inside `TransitionSeries.Sequence` — do not separate it into its own layer. Load [./rules/transitions.md](./rules/transitions.md) for the full transition pattern with code examples.

### Step 6: Captions
All videos should have animated subtitles with word highlighting. Follow this sequence:

1. **Transcribe** — Run the captions script to transcribe voiceover audio with word-level timestamps:

```bash
npx tsx src/<Name>/generate-captions.ts
```

Output goes to `public/<name>/captions/`.
2. **Proofread (MANDATORY)** — Whisper always mangles brand names, proper nouns, and punctuation. Before using transcripts:
   - Fix brand names — check `branding.company` in project.json and correct any misspellings Whisper introduced
   - Fix punctuation — add missing commas, periods
   - Merge split words ("busy work" → "busywork", "50 plus" → "50+")
   - Fix URLs — correct any mangled domain names or paths
   - Compare transcript against the original voiceover script in project.json
3. **Display** — Use TikTok-style word highlighting. `SWITCH_CAPTIONS_EVERY_MS = 1800` gives breathing room after sentences. Lower values (1200ms) feel rushed with no pause after periods. The spacing after punctuation makes a huge difference in how captions read.
4. **Last caption persists** — The final caption in each scene stays on screen until the scene ends.
5. **Placement** — Add `<Captions captionFile="<name>/captions/scene-01.json" />` at composition level inside each `TransitionSeries.Sequence`, not inside individual scene components. Each scene gets its own Captions component pointing to its caption JSON file.

Load [./rules/subtitles.md](./rules/subtitles.md) for the full Caption component API, transcription details, and display patterns.

### Step 7: Background music
If `background_music.enabled` is true in project.json, generate a background music track:

```bash
npx tsx src/<Name>/generate-background-music.ts
```

The script reads the mood from project.json, measures total voiceover duration, and generates an instrumental track via ElevenLabs Music API. The track saves to `public/<name>/background-music.mp3` and plays automatically in the composition at 15% volume. Set `hasBackgroundMusic: true` in the composition's defaultProps in Root.tsx.

If background music is disabled, skip this step.

### Step 8: Preview
Remotion Studio should already be running from Step 1. If not, restart it with `npx remotion studio`. The user can review the video in the browser and request changes.

**Update project.json:** Set each completed scene's `status` to "coded".

### Step 9: Render and deliver
If `render` is "approved" in project.json, render automatically when all scenes are coded. Otherwise wait for user approval.

```bash
npx remotion render <CompositionId> out/<name>.mp4 --port 3100
```

After render completes, upload to the user's configured delivery destination (e.g. Google Drive via `gws` CLI, or another tool). Ask the user where to deliver if not previously specified.

If `youtube.publish` is "approved" in project.json, generate a YouTube description by:
- Summarizing the voiceover text from project.json scenes
- Including all links from `youtube.links`
- Using `youtube.tags` and `youtube.category`
- Adding `branding.website` and any URLs from `branding.socials`
- Incorporating any notes from `youtube.description_notes`

Then upload via `python3 youtube-upload.py`.

**Update project.json:** Set `render` to "completed" after successful render. Set `youtube.publish` to "completed" after successful upload.

## Using FFmpeg

For some video operations, such as trimming videos or detecting silence, FFmpeg should be used. Load the [./rules/ffmpeg.md](./rules/ffmpeg.md) file for more information.

## Audio visualization

When needing to visualize audio (spectrum bars, waveforms, bass-reactive effects), load the [./rules/audio-visualization.md](./rules/audio-visualization.md) file for more information.

## Sound effects

When needing to use sound effects, load the [./rules/sound-effects.md](./rules/sound-effects.md) file for more information.

## How to use

Read individual rule files for detailed explanations and code examples:

- [rules/vertical-layout.md](rules/vertical-layout.md) - **CSS layout patterns for 9:16 video** — centered lists, grids, safe zones, section spacing. READ THIS BEFORE WRITING ANY SCENE.
- [rules/3d.md](rules/3d.md) - 3D content in Remotion using Three.js and React Three Fiber
- [rules/animations.md](rules/animations.md) - Fundamental animation skills for Remotion
- [rules/assets.md](rules/assets.md) - Importing images, videos, audio, and fonts into Remotion
- [rules/audio.md](rules/audio.md) - Using audio and sound in Remotion - importing, trimming, volume, speed, pitch
- [rules/calculate-metadata.md](rules/calculate-metadata.md) - Dynamically set composition duration, dimensions, and props
- [rules/can-decode.md](rules/can-decode.md) - Check if a video can be decoded by the browser using Mediabunny
- [rules/charts.md](rules/charts.md) - Chart and data visualization patterns for Remotion (bar, pie, line, stock charts)
- [rules/compositions.md](rules/compositions.md) - Defining compositions, stills, folders, default props and dynamic metadata
- [rules/extract-frames.md](rules/extract-frames.md) - Extract frames from videos at specific timestamps using Mediabunny
- [rules/fonts.md](rules/fonts.md) - Loading Google Fonts and local fonts in Remotion
- [rules/get-audio-duration.md](rules/get-audio-duration.md) - Getting the duration of an audio file in seconds with Mediabunny
- [rules/get-video-dimensions.md](rules/get-video-dimensions.md) - Getting the width and height of a video file with Mediabunny
- [rules/get-video-duration.md](rules/get-video-duration.md) - Getting the duration of a video file in seconds with Mediabunny
- [rules/gifs.md](rules/gifs.md) - Displaying GIFs synchronized with Remotion's timeline
- [rules/images.md](rules/images.md) - Embedding images in Remotion using the Img component
- [rules/light-leaks.md](rules/light-leaks.md) - Light leak overlay effects using @remotion/light-leaks
- [rules/lottie.md](rules/lottie.md) - Embedding Lottie animations in Remotion
- [rules/measuring-dom-nodes.md](rules/measuring-dom-nodes.md) - Measuring DOM element dimensions in Remotion
- [rules/measuring-text.md](rules/measuring-text.md) - Measuring text dimensions, fitting text to containers, and checking overflow
- [rules/sequencing.md](rules/sequencing.md) - Sequencing patterns for Remotion - delay, trim, limit duration of items
- [rules/tailwind.md](rules/tailwind.md) - Using TailwindCSS in Remotion
- [rules/text-animations.md](rules/text-animations.md) - Typography and text animation patterns for Remotion
- [rules/timing.md](rules/timing.md) - Interpolation curves in Remotion - linear, easing, spring animations
- [rules/transitions.md](rules/transitions.md) - Scene transition patterns for Remotion
- [rules/transparent-videos.md](rules/transparent-videos.md) - Rendering out a video with transparency
- [rules/trimming.md](rules/trimming.md) - Trimming patterns for Remotion - cut the beginning or end of animations
- [rules/videos.md](rules/videos.md) - Embedding videos in Remotion - trimming, volume, speed, looping, pitch
- [rules/parameters.md](rules/parameters.md) - Make a video parametrizable by adding a Zod schema
- [rules/maps.md](rules/maps.md) - Add a map using Mapbox and animate it
- [rules/voiceover.md](rules/voiceover.md) - Adding AI-generated voiceover to Remotion compositions using ElevenLabs TTS
- [rules/b-roll.md](rules/b-roll.md) - Generating b-roll video backgrounds via Krea.ai API and layering behind text/chart scenes
