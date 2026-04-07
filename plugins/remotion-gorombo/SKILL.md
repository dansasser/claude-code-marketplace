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
- `npx tsx src/YOUR_COMP/generate-voiceover.ts` — generates voiceover audio
- `npx tsx src/generate-broll.ts --output "public/your-comp/broll/" --prompts prompts.json` — generates b-roll clips
- `npx tsx src/YOUR_COMP/generate-captions.ts` — transcribes voiceover to captions

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
Run the scaffold script from the Remotion project root:

```bash
python3 scripts/scaffold.py <CompositionName>
```

This automatically creates the full composition structure:
- `src/<Name>/` — index.tsx, Scene1.tsx (placeholder), get-audio-duration.ts, generate-voiceover.ts (reads scenes from project.json), generate-captions.ts (reads scenes from project.json), Captions.tsx, project.json
- `public/<name>/voiceover/`, `public/<name>/broll/`, `public/<name>/captions/`
- Registers the composition in `src/Root.tsx`

The composition is immediately previewable in Remotion Studio with a placeholder scene. Do NOT manually create these files — use the script.

The scaffold also creates `project.json` in the composition directory. As you work through the following steps, update this file with the creative decisions (scene headlines, voiceover text, visual descriptions, b-roll choices, background music, render/publish approval status).

### Step 2: Script and questionnaire
Write the voiceover script per scene first. All videos should have voiceover — audio durations drive scene lengths (not the other way around).

When presenting the script for approval, ALWAYS show for every scene:
- Headline (what appears on screen)
- Voiceover (exact words the narrator says)
- Visual description

After the script, ask the user:
- Background music? (yes/no, mood: upbeat/corporate/cinematic/ambient)
- Auto-render when complete? (defaults to no)
- Auto-publish to YouTube? (defaults to no)

Use these exact values in project.json: `"render"` and `"youtube_publish"` must be `"pending"` (wait for approval) or `"approved"` (auto-proceed). After render completes, set `"render"` to `"completed"`. Do not use booleans or yes/no.

**Update project.json:** Fill in each scene's `headline`, `voiceover`, and `visual` fields. Update `background_music`, `render`, and `youtube_publish` with the user's answers. If the scene count changed, duplicate scene entries in the `scenes` array to match. Also duplicate the placeholder Scene1.tsx for each additional scene and update index.tsx to import and wire them all into the TransitionSeries.

### Step 3: Voiceover generation
The voiceover script reads directly from `project.json` — no need to edit the script itself. Just make sure the voiceover text is filled in for each scene in project.json (Step 2), then run:

```bash
npx tsx src/<Name>/generate-voiceover.ts
```

Load [./rules/voiceover.md](./rules/voiceover.md) for dynamic duration details and calculateMetadata patterns.

### Step 4: B-roll
Decide which scenes get b-roll backgrounds. Allocate ~2 b-roll clips per 30 seconds of video. Any scene can have b-roll — it's a background layer independent of the foreground content (text, charts, animated diagrams, anything). Load [./rules/b-roll.md](./rules/b-roll.md) for generation, zoom effects, and layering details.

**Update project.json:** For each scene, fill in `broll.type` ("image", "video", or "none") and `broll.prompt`.

### Step 5: Transitions
The scaffold already sets up TransitionSeries with fade transitions. Use `fade()` between scenes at 1-1.5 seconds (30-45 frames at 30fps). `PADDING_FRAMES` (silence after voiceover) MUST be >= `TRANSITION_DURATION` or voiceovers will overlap during transitions. Audio stays inside `TransitionSeries.Sequence` — do not separate it into its own layer.

### Step 6: Captions
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

### Step 7: Background music
If `background_music.enabled` is true in project.json, generate a background music track:

```bash
npx tsx src/<Name>/generate-background-music.ts
```

The script reads the mood from project.json, measures total voiceover duration, and generates an instrumental track via ElevenLabs Music API. The track saves to `public/<name>/background-music.mp3` and plays automatically in the composition at 15% volume. Set `hasBackgroundMusic: true` in the composition's defaultProps in Root.tsx.

If background music is disabled, skip this step.

### Step 8: Preview
Launch Remotion Studio (`npx remotion studio`) if it isn't already running so the user can review in the browser.

**Update project.json:** Set each completed scene's `status` to "coded".

### Step 9: Render and deliver
If `render` is "approved" in project.json, render automatically when all scenes are coded. Otherwise wait for user approval.

```bash
npx remotion render <CompositionId> out/<name>.mp4 --port 3100
```

After render completes, upload to Google Drive automatically (default delivery). If `youtube_publish` is "approved" in project.json, generate a YouTube description from the voiceover text and upload via `python3 youtube-upload.py`. Include any links the user has configured in their project or .env.

**Update project.json:** Set `render` to "completed" after successful render.

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
