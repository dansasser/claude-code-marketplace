---
name: remotion-best-practices
description: Best practices for Remotion - Video creation in React
metadata:
  tags: remotion, video, react, animation, composition
---

## When to use

Use this skills whenever you are dealing with Remotion code to obtain the domain-specific knowledge.

## Scene planning

Before implementing any scenes, follow this sequence.

**API keys** (ElevenLabs, Krea, etc.) are loaded from `.env` by the scripts automatically. NEVER pass API keys on the command line — they will be visible in terminal output. Always use the provided scripts:
- `npx tsx src/<Name>/generate-voiceover.ts` — generates voiceover audio
- `npx tsx src/generate-broll.ts --output public/<name>/broll/ --prompts prompts.json` — generates b-roll clips
- `npx tsx src/<Name>/generate-captions.ts` — transcribes voiceover to captions

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

### Step 1: Composition structure
Each composition gets its own directories:
- `public/<name>/voiceover/` — audio files
- `public/<name>/broll/` — video clips
- `public/<name>/captions/` — transcription JSON files
- `src/<Name>/` — components, generate-voiceover.ts, generate-captions.ts

### Step 2: Voiceover
All videos should have voiceover. Write the voiceover script per scene first, generate audio via ElevenLabs, then use the audio durations to drive scene lengths (not the other way around). Load [./rules/voiceover.md](./rules/voiceover.md) for generation and dynamic duration details.

When presenting the script for approval, ALWAYS show for every scene:
- Headline (what appears on screen)
- Voiceover (exact words the narrator says)
- Visual description

### Step 3: B-roll
Decide which scenes get b-roll backgrounds. Allocate ~2 b-roll clips per 30 seconds of video. Any scene can have b-roll — it's a background layer independent of the foreground content (text, charts, animated diagrams, anything). Load [./rules/b-roll.md](./rules/b-roll.md) for generation, zoom effects, and layering details.

### Step 4: Transitions
Use `fade()` transitions between scenes at 1-1.5 seconds (30-45 frames at 30fps). `PADDING_FRAMES` (silence after voiceover) MUST be >= `TRANSITION_DURATION` or voiceovers will overlap during transitions. Audio stays inside `TransitionSeries.Sequence` — do not separate it into its own layer.

### Step 5: Captions
All videos should have animated subtitles with word highlighting. Follow this sequence:

1. **Transcribe** — Use whisper.cpp to transcribe each scene's voiceover audio to get word-level timestamps. Output to `public/<name>/captions/`.
2. **Proofread (MANDATORY)** — Whisper always mangles brand names, proper nouns, and punctuation. Before using transcripts:
   - Fix brand names (e.g. "Garrombo" → "Gorombo", "SIM 1" → "SIM-ONE")
   - Fix punctuation — add missing commas, periods
   - Merge split words ("busy work" → "busywork", "50 plus" → "50+")
   - Fix URLs ("managedai" → "managed-ai")
   - Compare transcript against the original voiceover script you wrote
3. **Display** — Use TikTok-style word highlighting. `SWITCH_CAPTIONS_EVERY_MS = 1800` gives breathing room after sentences. Lower values (1200ms) feel rushed with no pause after periods. The spacing after punctuation makes a huge difference in how captions read.
4. **Last caption persists** — The final caption in each scene stays on screen until the scene ends.
5. **Placement** — Add `<Captions>` at composition level inside each `TransitionSeries.Sequence`, not inside individual scene components.

Load [./rules/subtitles.md](./rules/subtitles.md) for technical details on the Caption type, transcription, and display components.

### Step 6: Preview
Launch Remotion Studio (`npx remotion studio`) if it isn't already running so the user can review in the browser. Do not render or deliver unless the prompt or the user says to.

## Using FFmpeg

For some video operations, such as trimming videos or detecting silence, FFmpeg should be used. Load the [./rules/ffmpeg.md](./rules/ffmpeg.md) file for more information.

## Audio visualization

When needing to visualize audio (spectrum bars, waveforms, bass-reactive effects), load the [./rules/audio-visualization.md](./rules/audio-visualization.md) file for more information.

## Sound effects

When needing to use sound effects, load the [./rules/sound-effects.md](./rules/sound-effects.md) file for more information.

## How to use

Read individual rule files for detailed explanations and code examples:

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
