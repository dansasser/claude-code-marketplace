---
name: b-roll
description: Generating and using b-roll video backgrounds via Krea.ai API in Remotion compositions
metadata:
  tags: b-roll, krea, background, video, scenes, zoom, ken-burns
---

## When to use b-roll

B-roll is a **background layer** behind any scene. It adds depth and motion regardless of what the foreground content does — text, charts, animated SVG diagrams, product demos, anything. The foreground code design and the background b-roll are independent layers.

Aim for **~2 b-roll clips per 30 seconds** of video. Not every scene needs it, but any scene CAN have it.

## How to generate b-roll

Use the Krea.ai API. The API key should be in an environment variable (`KREA_API_KEY`).

### API call

```
POST https://api.krea.ai/generate/video/{model}
Authorization: Bearer $KREA_API_KEY
Content-Type: application/json

{
  "prompt": "<descriptive prompt for the b-roll>",
  "duration": <seconds>,
  "width": <pixels>,
  "height": <pixels>
}
```

The endpoint returns a `job_id`. Poll `GET https://api.krea.ai/jobs/{job_id}` until status is `completed`, then download the video from `result.urls[0]`.

### Model selection

| Model | Slug | Best for | ~Time |
|-------|------|----------|-------|
| Veo 3.1 | `google/veo-3.1` | High quality, audio | 3-5m |
| Veo 3.1 Fast | `google/veo-3.1-fast` | Fast turnaround | 1-3m |
| Kling 2.5 | `kling/kling-2.5` | Good quality, fast | 1-2m |
| Seedance Lite | `bytedance/seedance-lite` | Cheapest/fastest | 30-60s |

For b-roll backgrounds, `kling/kling-2.5` is a good balance of quality and speed.

### Duration

Generate b-roll at the **longest supported duration** for the model (typically 10s). If scenes are longer than the clip, use ffmpeg to extend:

```bash
ffmpeg -stream_loop 1 -i clip-10s.mp4 -t 15 -c copy clip-15s.mp4
```

This loops the clip once and trims to 15 seconds. Use `-c copy` to avoid re-encoding.

### Aspect ratio

The API output may be landscape regardless of requested dimensions. Use `objectFit: "cover"` on the OffthreadVideo to handle landscape clips in portrait compositions. Do not blame the API — handle the ratio in code.

## How to layer b-roll in Remotion

Use `<OffthreadVideo>` as the background in an `<AbsoluteFill>`. The parent `<AbsoluteFill>` MUST have `overflow: "hidden"` for zoom effects to work. Dim the b-roll so text and charts remain readable.

```tsx
import { AbsoluteFill, OffthreadVideo, staticFile, useCurrentFrame, useVideoConfig, interpolate } from "remotion";

const BRollScene: React.FC<{
  bRollSrc: string;
  children: React.ReactNode;
}> = ({ bRollSrc, children }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const zoom = interpolate(
    frame,
    [0, durationInFrames / 4, durationInFrames / 2, 3 * durationInFrames / 4, durationInFrames],
    [1, 1.15, 1, 1.15, 3],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill>
      {/* B-roll background — dimmed, clipped, zoomed */}
      <AbsoluteFill style={{ filter: "brightness(0.4)", overflow: "hidden" }}>
        <OffthreadVideo
          src={bRollSrc}
          style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})` }}
        />
      </AbsoluteFill>
      {/* Content on top */}
      <AbsoluteFill>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};
```

### Critical: Zoom effect requirements

1. `overflow: "hidden"` on the parent `<AbsoluteFill>` — without this, the zoom is invisible
2. `transform: scale()` goes directly on the `<OffthreadVideo>` style — not on a wrapper div
3. `objectFit: "cover"` and `width/height: 100%` stay on the video alongside the transform
4. Do NOT use `<Video>` from `@remotion/media` — it handles sizing differently and breaks `objectFit: cover`
5. `<OffthreadVideo>` does NOT support the `loop` prop — use ffmpeg to extend clips instead

### Zoom pattern

The zoom bounces in and out, then zooms hard at the end so the scene is always moving through the transition:

```tsx
const zoom = interpolate(
  frame,
  [0, durationInFrames / 4, durationInFrames / 2, 3 * durationInFrames / 4, durationInFrames],
  [1, 1.15, 1, 1.15, 3],
  { extrapolateRight: "clamp" }
);
```

### Prompting tips

Write prompts that produce **subtle, non-distracting** footage. Good b-roll backgrounds:
- Slow camera movement (panning, dolly)
- Soft focus or shallow depth of field
- Abstract or environmental (cityscapes, nature, textures, light)
- Match the video's tone and color palette

Avoid busy or high-contrast footage that competes with the content on top.
