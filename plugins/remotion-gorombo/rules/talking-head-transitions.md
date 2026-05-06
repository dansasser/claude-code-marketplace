---
name: talking-head-transitions
description: Professional video dissolve transitions for talking-head content — two-layer pattern with video-only dissolve and audio straight cut
metadata:
  tags: transitions, dissolve, crossfade, talking-head, audio, video, split-edit, professional
---

# Talking-Head Transitions

When editing talking-head content (a person speaking directly to camera), video and audio require different transition handling. This is verified against Adobe Premiere Pro and DaVinci Resolve documentation and is standard professional practice.

## The Rule

**Video dissolve + audio straight cut.** Always.

- **Video layer:** Overlapping clips with opacity dissolve (true crossfade between segments)
- **Audio layer:** Sequential clips with straight cuts at natural speech pauses (no overlap, no crossfade)

Never crossfade audio from the same speaker across a dissolve. The overlapping handle frames contain duplicate source audio, causing words to double/echo.

## Why Audio Crossfade Fails for Talking Heads

When you extend video clips by 0.5s for dissolve handles, both clips contain the same 0.5s of source audio at the edit point. During the overlap:

- Outgoing clip plays: "...that only" (fading out)
- Incoming clip plays: "...that only" (fading in)
- Result: the viewer hears "that only" twice — a doubling artifact

This does not happen with music beds, ambient audio, or TTS voiceover because those tracks don't contain duplicate speech at the edit point. It only happens when the same speaker's continuous recording is split and both halves play simultaneously.

## How Professional NLEs Handle It

**Adobe Premiere Pro:**
- `Ctrl+D` / `Cmd+D` = video-only Cross Dissolve (default)
- `Shift+D` = both video AND audio transitions (avoid for talking heads)
- Morph Cut = AI-powered talking-head transition, video-only by design

**DaVinci Resolve:**
- `Alt+T` / `Option+T` = video-only transition
- `T` = both video and audio (avoid for talking heads)
- Smooth Cut = video-only optical flow transition for interviews

Both NLEs default to video-only when applying transitions with their standard shortcut. The combined video+audio shortcut is a separate, deliberate action.

## Asset Organization

Segment clips must be organized for both hard-cut and crossfade workflows:

```
assets/
  video/
    full.mp4                    (source video, uncut)
    10s-clips/                  (exact-cut segments for hard cuts)
      segment-01.mp4 ... segment-NN.mp4
    crossfade/                  (extended segments with handles for dissolves, audio stripped)
      segment-01.mp4 ... segment-NN.mp4
  audio/
    full.mp3                    (source audio, uncut)
    10s-clips/                  (exact-cut audio matching video segments)
      segment-01.mp3 ... segment-NN.mp3
    crossfade/                  (extended audio with handles, for future use)
      segment-01.mp3 ... segment-NN.mp3
  transcript/
    source-split-transcript.srt
    source-split-transcript.json
```

- Full source files at the top of each asset type
- Clips organized by purpose in named subfolders
- Video crossfade clips have audio stripped (`-an` flag in ffmpeg)
- Audio and video directories mirror each other — every video clip has a matching audio clip
- Hard cut = use `10s-clips/` pairs. Dissolve = use `crossfade/` video + `10s-clips/` audio.

## Extended Handles

Crossfade video clips extend 0.5 seconds (15 frames at 30fps) beyond each audio cut point:

- **First segment:** extended on END only (0.5s past the audio cut into the pause)
- **Middle segments:** extended on BOTH sides (0.5s before audio start, 0.5s after audio end)
- **Last segment:** extended on START only (0.5s before the audio cut)

These extra frames are the "handles" that provide visual content during the dissolve. Since cuts land on natural speech pauses, the handle frames show the speaker in silence — providing a clean visual transition without interrupting speech.

## Segment Cutting Workflow

1. **Transcribe** the source video with sentence-level output (whisper, default mode — NOT word-level)
2. **Read the sentences** and identify natural break points (sentence endings, pauses) closest to every ~10 seconds
3. **Cut video segments** at those boundaries using ffmpeg with re-encoding for precise cuts:
   ```bash
   ffmpeg -y -ss <start> -to <end> -i source.mp4 -c:v libx264 -preset fast -crf 20 -c:a aac -b:a 192k segment-NN.mp4
   ```
4. **Extract audio** from each segment into a standalone mp3:
   ```bash
   ffmpeg -y -i segment-NN.mp4 -vn -c:a libmp3lame -b:a 192k segment-NN.mp3
   ```
5. **Cut crossfade video clips** with extended handles and no audio:
   ```bash
   ffmpeg -y -ss <start - 0.5> -to <end + 0.5> -i source.mp4 -an -c:v libx264 -preset fast -crf 20 segment-NN.mp4
   ```
6. **Organize** into the asset directory structure above

## Remotion Implementation — Two-Layer Pattern

```tsx
const DISSOLVE_FRAMES = 15; // 0.5s at 30fps

// Video dissolve component — opacity fades, no audio
const DissolveVideo: React.FC<{
  src: string;
  isFirst: boolean;
  isLast: boolean;
}> = ({ src, isFirst, isLast }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const fadeIn = isFirst ? 1
    : interpolate(frame, [0, DISSOLVE_FRAMES], [0, 1],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  const fadeOut = isLast ? 1
    : interpolate(frame, [durationInFrames - DISSOLVE_FRAMES, durationInFrames], [1, 0],
        { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ opacity: fadeIn * fadeOut }}>
      <OffthreadVideo muted src={staticFile(src)}
        style={{ width: "100%", height: "100%", objectFit: "cover" }} />
    </AbsoluteFill>
  );
};

// Composition with two independent layers
export const Composition: React.FC = () => {
  return (
    <AbsoluteFill>
      {/* LAYER 1 — Video: crossfade clips, overlapping Sequences, opacity dissolve */}
      <AbsoluteFill>
        {segments.map((seg, i) => {
          const isFirst = i === 0;
          const isLast = i === segments.length - 1;
          const cfStart = isFirst ? seg.audioStart : seg.audioStart - HANDLE_SECONDS;
          const cfEnd = isLast ? seg.audioEnd : seg.audioEnd + HANDLE_SECONDS;

          return (
            <Sequence key={seg.id}
              from={Math.round(cfStart * FPS)}
              durationInFrames={Math.round((cfEnd - cfStart) * FPS)}>
              <DissolveVideo src={seg.crossfadeVideo} isFirst={isFirst} isLast={isLast} />
            </Sequence>
          );
        })}
      </AbsoluteFill>

      {/* LAYER 2 — Audio: 10s-clips, sequential, straight cuts, no overlap */}
      <AbsoluteFill>
        {segments.map((seg) => (
          <Sequence key={`${seg.id}-audio`}
            from={Math.round(seg.audioStart * FPS)}
            durationInFrames={Math.round((seg.audioEnd - seg.audioStart) * FPS)}>
            <Audio src={staticFile(seg.audio)} />
          </Sequence>
        ))}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
```

**Key points:**
- Video uses crossfade clips from `assets/video/crossfade/` — these are muted and have extended handles
- Audio uses exact-cut clips from `assets/audio/10s-clips/` — no overlap, straight cuts
- Video Sequences overlap in time (adjacent clips share DISSOLVE_FRAMES). Audio Sequences do not overlap.
- Composition total duration = sum of original audio segment durations (no compression from overlaps — the video overlaps are visual only)
- Each segment can independently have its own zoom/pan/effects applied inside the DissolveVideo wrapper

## When NOT to Use This Pattern

- **TTS voiceover + b-roll compositions:** Audio is generated separately from video. No lip sync to maintain. Use `TransitionSeries` with `fade()` directly — audio inside the sequence is fine because it's not duplicated source audio.
- **Music-only transitions:** Crossfade audio is fine for music beds. The doubling problem only affects speech.
- **Hard cuts:** If no dissolve is needed, use the `10s-clips/` for both video and audio with regular sequential Sequences. No handles, no overlap, no fade.

## References

- [Adobe Premiere Pro — Transition Overview](https://helpx.adobe.com/premiere-pro/using/transition-overview-applying-transitions.html)
- [DaVinci Resolve 18 Manual — Smooth Cut](https://www.steakunderwater.com/VFXPedia/__man/Resolve18-6/DaVinciResolve18_Manual_files/part752.htm)
- [Wikipedia — Split Edit](https://en.wikipedia.org/wiki/Split_edit)
- [Remotion — fade() Presentation](https://www.remotion.dev/docs/transitions/presentations/fade)
