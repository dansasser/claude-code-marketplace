---
name: vertical-layout
description: CSS layout patterns for 1080x1920 vertical short-form video
metadata:
  tags: layout, css, flexbox, grid, safe-zone, vertical, 9:16
---

# Vertical Video Layout Guide (1080x1920)

Layout patterns for 9:16 portrait video scenes in Remotion. Every pattern uses inline styles (no CSS classes) and respects the safe zone.

## Safe Zone

The safe area is **900x1400px** centered within the 1080x1920 frame.

```
+--1080px--+
|   60px   |  <- left margin
|  +900px+ |
|  |      ||  <- 120px right margin (platform UI overlaps more on right)
|  |      ||
|  +------+|
|  320px   |  <- bottom margin (nav bar, swipe-up, home indicator)
+----------+
```

**Exact margins:**
- Top: 210px
- Bottom: 310px
- Left: 60px
- Right: 120px

Apply safe zone padding on every AbsoluteFill:

```tsx
<AbsoluteFill
  style={{
    backgroundColor: "#0a0a0a",
    padding: "210px 120px 310px 60px",
  }}
>
```

The padding shorthand is `top right bottom left`. This gives you a 900x1400 content area.

If you need the safe zone as a nested container instead (useful when you also need absolute-positioned elements outside it):

```tsx
<AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
  {/* Absolute-positioned elements outside safe zone go here */}

  {/* Safe zone container */}
  <div
    style={{
      position: "absolute",
      top: 210,
      left: 60,
      right: 120,
      bottom: 310,
      display: "flex",
      flexDirection: "column",
    }}
  >
    {/* All content inside safe zone */}
  </div>
</AbsoluteFill>
```

---

## Pattern 1: Centered Block with Left-Aligned Content

The most common layout. A group of items (numbered list, bullet points, feature rows) is visually centered on screen as a block, but the items inside are left-aligned relative to each other.

### WRONG: Hardcoded left position

```tsx
// BAD — items hug the left edge of the screen, not centered
<AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
  <div style={{ position: "absolute", left: 140, top: 400 }}>
    <div>1. Deploy in 48 hours</div>
    <div>2. No code required</div>
    <div>3. Full audit trail</div>
  </div>
</AbsoluteFill>
```

This pins the list to an arbitrary pixel position. It is not centered and looks off-balance.

### RIGHT: Centered flex container, left-aligned children

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate, Sequence } from "remotion";

export const CenteredListScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const items = [
    { number: "01", text: "Deploy in 48 hours" },
    { number: "02", text: "No code required" },
    { number: "03", text: "Full audit trail" },
    { number: "04", text: "$500/month flat rate" },
  ];

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
        padding: "210px 120px 310px 60px",
      }}
    >
      {/* Headline — centered */}
      <div
        style={{
          textAlign: "center",
          marginBottom: 80,
        }}
      >
        <h1
          style={{
            color: "white",
            fontSize: 64,
            fontWeight: 800,
            fontFamily: "Inter",
            lineHeight: 1.2,
            margin: 0,
          }}
        >
          What You <span style={{ color: "#6366f1" }}>Get</span>
        </h1>
      </div>

      {/* 
        This is the key pattern:
        - The OUTER div uses flexbox to center the block horizontally
        - The INNER div uses alignItems: "flex-start" so items left-align
      */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",  // centers the block horizontally
          width: "100%",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-start",  // items left-align within the block
            gap: 32,
          }}
        >
          {items.map((item, index) => {
            const delay = 15 + index * 10;
            const progress = spring({ frame, fps, delay, config: { damping: 200 } });
            const opacity = interpolate(progress, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
            const translateX = interpolate(progress, [0, 1], [-40, 0]);

            return (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 24,
                  opacity,
                  transform: `translateX(${translateX}px)`,
                }}
              >
                <span
                  style={{
                    color: "#6366f1",
                    fontSize: 48,
                    fontWeight: 800,
                    fontFamily: "Inter",
                    fontVariantNumeric: "tabular-nums",
                    minWidth: 80,
                  }}
                >
                  {item.number}
                </span>
                <span
                  style={{
                    color: "white",
                    fontSize: 40,
                    fontWeight: 600,
                    fontFamily: "Inter",
                  }}
                >
                  {item.text}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

**Why this works:** The outer `div` with `justifyContent: "center"` centers the inner block. The inner `div` with `alignItems: "flex-start"` keeps items left-aligned relative to each other. The block width shrinks to fit the widest item, and the whole block sits centered.

**Alternative — using `margin: "0 auto"` instead of an outer flex wrapper:**

```tsx
<div
  style={{
    display: "flex",
    flexDirection: "column",
    alignItems: "flex-start",
    gap: 32,
    margin: "0 auto",  // centers this block within its parent
  }}
>
  {/* items here */}
</div>
```

Both approaches produce the same result. Use whichever reads clearer in context.

---

## Pattern 2: Pure Centered Text

For headlines, subtitles, taglines, and single-line callouts. Centered both horizontally and vertically within the safe zone.

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

export const CenteredTextScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headlineProgress = spring({ frame, fps, delay: 5, config: { damping: 200 } });
  const subtitleProgress = spring({ frame, fps, delay: 20, config: { damping: 200 } });

  const headlineOpacity = interpolate(headlineProgress, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
  const headlineY = interpolate(headlineProgress, [0, 1], [60, 0]);

  const subtitleOpacity = interpolate(subtitleProgress, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
  const subtitleY = interpolate(subtitleProgress, [0, 1], [40, 0]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
        padding: "210px 120px 310px 60px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",  // vertically centers the text group
        alignItems: "center",      // horizontally centers the text group
      }}
    >
      <h1
        style={{
          color: "white",
          fontSize: 72,
          fontWeight: 800,
          fontFamily: "Inter",
          lineHeight: 1.2,
          margin: 0,
          textAlign: "center",
          opacity: headlineOpacity,
          transform: `translateY(${headlineY}px)`,
        }}
      >
        Your AI Team,
        <br />
        <span style={{ color: "#6366f1" }}>Deployed Today</span>
      </h1>

      <p
        style={{
          color: "#94a3b8",
          fontSize: 36,
          fontWeight: 400,
          fontFamily: "Inter",
          lineHeight: 1.5,
          margin: "40px 0 0 0",
          textAlign: "center",
          opacity: subtitleOpacity,
          transform: `translateY(${subtitleY}px)`,
        }}
      >
        No hiring. No training. No waiting.
      </p>
    </AbsoluteFill>
  );
};
```

**When to use `justifyContent: "center"` + `alignItems: "center"` on AbsoluteFill:**
ONLY when you have a simple text-only layout (headline + optional subtitle) with nothing else on screen. This stacks elements vertically and centers them. If you have multiple distinct sections (headline at top, visual in middle, subtitle at bottom), do NOT use this approach — use Pattern 3 instead.

---

## Pattern 3: Vertical Section Spacing

When a scene has distinct sections (headline at top, visual element in the middle, subtitle at bottom), use absolute positioning with calculated top values. Do NOT use `justifyContent: "center"` because it stacks all children at the same vertical center point.

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate, Sequence } from "remotion";

export const SectionedScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headlineProgress = spring({ frame, fps, delay: 5, config: { damping: 200 } });
  const visualProgress = spring({ frame, fps, delay: 15, config: { damping: 200 } });
  const subtitleProgress = spring({ frame, fps, delay: 40, config: { damping: 200 } });

  const headlineOpacity = interpolate(headlineProgress, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
  const visualScale = interpolate(visualProgress, [0, 1], [0.7, 1]);
  const visualOpacity = interpolate(visualProgress, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
  const subtitleOpacity = interpolate(subtitleProgress, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
  const subtitleY = interpolate(subtitleProgress, [0, 1], [30, 0]);

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      {/* SECTION 1: Headline — pinned near top of safe zone */}
      <div
        style={{
          position: "absolute",
          top: 240,              // inside safe zone (210px + 30px breathing room)
          left: 60,
          right: 120,
          textAlign: "center",
          opacity: headlineOpacity,
        }}
      >
        <h1
          style={{
            color: "white",
            fontSize: 64,
            fontWeight: 800,
            fontFamily: "Inter",
            lineHeight: 1.2,
            margin: 0,
          }}
        >
          How It <span style={{ color: "#6366f1" }}>Works</span>
        </h1>
      </div>

      {/* SECTION 2: Visual element — centered vertically */}
      <div
        style={{
          position: "absolute",
          top: 500,              // calculated: below headline, above subtitle
          left: 60,
          right: 120,
          display: "flex",
          justifyContent: "center",
          opacity: visualOpacity,
          transform: `scale(${visualScale})`,
        }}
      >
        <div
          style={{
            width: 300,
            height: 300,
            borderRadius: 40,
            backgroundColor: "#1a1a1a",
            border: "2px solid #333",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 120,
          }}
        >
          🤖
        </div>
      </div>

      {/* SECTION 3: Subtitle — pinned near bottom of safe zone */}
      <div
        style={{
          position: "absolute",
          bottom: 380,           // inside safe zone (310px + 70px breathing room)
          left: 60,
          right: 120,
          textAlign: "center",
          opacity: subtitleOpacity,
          transform: `translateY(${subtitleY}px)`,
        }}
      >
        <p
          style={{
            color: "#94a3b8",
            fontSize: 36,
            fontWeight: 400,
            fontFamily: "Inter",
            lineHeight: 1.5,
            margin: 0,
          }}
        >
          One agent. Infinite possibilities.
        </p>
      </div>
    </AbsoluteFill>
  );
};
```

**Vertical spacing reference for 1080x1920:**

| Section | Position | Notes |
|---------|----------|-------|
| Headline | `top: 240px` | Safe zone top (210) + 30px breathing room |
| Visual center | `top: 500-700px` | Depends on headline height and visual size |
| Subtitle | `bottom: 380px` | Safe zone bottom (310) + 70px breathing room |
| CTA / tagline | `bottom: 340px` | Just inside safe zone bottom |

When using absolute positioning, always set `left: 60` and `right: 120` on each section to maintain safe zone side margins.

**Alternative — flex column with spacer divs:**

If the exact vertical positions are hard to calculate, use a flex column with `flex: 1` spacers:

```tsx
<AbsoluteFill
  style={{
    backgroundColor: "#0a0a0a",
    padding: "210px 120px 310px 60px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  }}
>
  {/* Headline */}
  <h1 style={{ /* ... */ }}>Title</h1>

  {/* Spacer pushes visual to center */}
  <div style={{ flex: 1 }} />

  {/* Visual */}
  <div>{ /* visual content */ }</div>

  {/* Spacer pushes subtitle to bottom */}
  <div style={{ flex: 1 }} />

  {/* Subtitle */}
  <p style={{ /* ... */ }}>Subtitle text</p>
</AbsoluteFill>
```

---

## Pattern 4: Two-Column Grid

For feature pills, comparison cards, icon grids, or stat pairs. The grid is centered as a group.

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate, Sequence } from "remotion";

export const TwoColumnGridScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const items = [
    { icon: "📧", label: "Email" },
    { icon: "📅", label: "Calendar" },
    { icon: "📊", label: "Reports" },
    { icon: "🔍", label: "Research" },
    { icon: "💬", label: "Support" },
    { icon: "📝", label: "Documents" },
  ];

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0a",
        padding: "210px 120px 310px 60px",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      {/* Headline */}
      <h1
        style={{
          color: "white",
          fontSize: 56,
          fontWeight: 800,
          fontFamily: "Inter",
          lineHeight: 1.2,
          margin: "0 0 60px 0",
          textAlign: "center",
        }}
      >
        What It <span style={{ color: "#22c55e" }}>Handles</span>
      </h1>

      {/* Two-column grid — centered as a block */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 24,
          width: "100%",
          maxWidth: 750,  // constrains grid width so it stays centered
        }}
      >
        {items.map((item, index) => {
          const delay = 15 + index * 8;
          const progress = spring({ frame, fps, delay, config: { damping: 200 } });
          const opacity = interpolate(progress, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
          const scale = interpolate(progress, [0, 1], [0.8, 1]);

          return (
            <div
              key={index}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 16,
                padding: "20px 24px",
                backgroundColor: "rgba(255, 255, 255, 0.05)",
                borderRadius: 16,
                border: "1px solid rgba(255, 255, 255, 0.1)",
                opacity,
                transform: `scale(${scale})`,
              }}
            >
              <span style={{ fontSize: 36 }}>{item.icon}</span>
              <span
                style={{
                  color: "white",
                  fontSize: 32,
                  fontWeight: 600,
                  fontFamily: "Inter",
                }}
              >
                {item.label}
              </span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
```

**Grid sizing tips:**
- `maxWidth: 750` keeps the grid from stretching edge-to-edge (the safe zone is 900px wide)
- `gap: 24` provides breathing room between pills
- For 3-column grids, use `gridTemplateColumns: "1fr 1fr 1fr"` and `maxWidth: 800`
- For icon-only grids (no labels), use equal fixed columns: `gridTemplateColumns: "repeat(2, 160px)"` with `justifyContent: "center"` on the parent

**Glass-morphism card style** (reusable across pills and cards):

```tsx
const glassCard = {
  backgroundColor: "rgba(255, 255, 255, 0.05)",
  borderRadius: 16,
  border: "1px solid rgba(255, 255, 255, 0.1)",
  padding: "20px 24px",
};
```

---

## Pattern 5: Full Scene Template

A complete scene combining all patterns: headline at top, centered content block with left-aligned items, subtitle at bottom.

```tsx
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate, Sequence } from "remotion";

export const FullScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headlineProgress = spring({ frame, fps, delay: 5, config: { damping: 200 } });
  const headlineOpacity = interpolate(headlineProgress, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
  const headlineY = interpolate(headlineProgress, [0, 1], [40, 0]);

  const features = [
    { icon: "⚡", text: "Deploys in 48 hours" },
    { icon: "🔒", text: "Enterprise-grade security" },
    { icon: "📊", text: "Weekly performance reports" },
    { icon: "🎯", text: "Custom-trained for your business" },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>

      {/* HEADLINE — absolute, top of safe zone */}
      <div
        style={{
          position: "absolute",
          top: 240,
          left: 60,
          right: 120,
          textAlign: "center",
          opacity: headlineOpacity,
          transform: `translateY(${headlineY}px)`,
        }}
      >
        <h1
          style={{
            color: "white",
            fontSize: 60,
            fontWeight: 800,
            fontFamily: "Inter",
            lineHeight: 1.2,
            margin: 0,
          }}
        >
          Why Choose{" "}
          <span style={{ color: "#6366f1" }}>Managed AI</span>
        </h1>
      </div>

      {/* FEATURE LIST — centered block, left-aligned items */}
      <div
        style={{
          position: "absolute",
          top: 480,
          left: 60,
          right: 120,
          display: "flex",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-start",
            gap: 40,
          }}
        >
          {features.map((feature, index) => {
            const delay = 20 + index * 10;
            const progress = spring({ frame, fps, delay, config: { damping: 200 } });
            const opacity = interpolate(progress, [0, 0.5], [0, 1], { extrapolateRight: "clamp" });
            const translateX = interpolate(progress, [0, 1], [-30, 0]);

            return (
              <div
                key={index}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 20,
                  opacity,
                  transform: `translateX(${translateX}px)`,
                }}
              >
                <div
                  style={{
                    width: 64,
                    height: 64,
                    borderRadius: 16,
                    backgroundColor: "rgba(99, 102, 241, 0.15)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 32,
                    flexShrink: 0,
                  }}
                >
                  {feature.icon}
                </div>
                <span
                  style={{
                    color: "white",
                    fontSize: 36,
                    fontWeight: 600,
                    fontFamily: "Inter",
                  }}
                >
                  {feature.text}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* SUBTITLE — absolute, bottom of safe zone */}
      <Sequence from={60}>
        <div
          style={{
            position: "absolute",
            bottom: 380,
            left: 60,
            right: 120,
            textAlign: "center",
          }}
        >
          <p
            style={{
              color: "#94a3b8",
              fontSize: 32,
              fontWeight: 400,
              fontFamily: "Inter",
              lineHeight: 1.5,
              margin: 0,
            }}
          >
            Enterprise AI without the enterprise price tag
          </p>
        </div>
      </Sequence>
    </AbsoluteFill>
  );
};
```

---

## Common Mistakes

### Mistake 1: Using justifyContent + alignItems center on AbsoluteFill with multiple sections

```tsx
// BAD — all three sections stack on top of each other at the center point
<AbsoluteFill
  style={{
    backgroundColor: "#0a0a0a",
    justifyContent: "center",
    alignItems: "center",
  }}
>
  <h1>Title</h1>        {/* these all overlap at vertical center */}
  <div>Visual</div>
  <p>Subtitle</p>
</AbsoluteFill>
```

**Fix:** Use absolute positioning for multi-section layouts (Pattern 3), or add `flexDirection: "column"` with spacing between items (but this only works when you want them evenly stacked, not spread across the screen).

### Mistake 2: Left-aligning list items to the screen edge

```tsx
// BAD — list hugs the left margin, looks unbalanced
<div style={{ position: "absolute", left: 140, top: 500 }}>
  <div>Step 1: Sign up</div>
  <div>Step 2: Configure</div>
  <div>Step 3: Launch</div>
</div>
```

**Fix:** Use Pattern 1 — wrap the list in a flex container with `justifyContent: "center"`, then set `alignItems: "flex-start"` on the inner list container.

### Mistake 3: Not enough vertical space between sections

```tsx
// BAD — headline and visual are only 20px apart, looks cramped
<div style={{ position: "absolute", top: 240 }}>
  <h1>Title</h1>
</div>
<div style={{ position: "absolute", top: 340 }}>
  {/* visual — way too close to headline */}
</div>
```

**Fix:** Leave at least 100-120px between the bottom of a headline and the top of the next section. Headline at `top: 240` means content below should start at `top: 450+` minimum. A 64px headline with lineHeight 1.2 is ~77px tall, plus you want 100px+ gap.

### Mistake 4: Forgetting safe zones

```tsx
// BAD — content extends to raw edges, gets clipped by platform UI
<AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
  <div style={{ position: "absolute", top: 40, left: 20 }}>
    <h1>Title</h1>
  </div>
  <div style={{ position: "absolute", bottom: 30 }}>
    <p>CTA text</p>
  </div>
</AbsoluteFill>
```

**Fix:** Nothing above `top: 210`, nothing below `bottom: 310`, nothing left of `left: 60`, nothing right of `right: 120`. When using padding on AbsoluteFill: `padding: "210px 120px 310px 60px"`. When using absolute positioning, always include `left: 60, right: 120` on each positioned element.

### Mistake 5: Using CSS transitions or keyframe animations

```tsx
// BAD — CSS transitions are not frame-synchronized, will not render correctly
<div style={{ transition: "opacity 0.5s ease" }}>
```

**Fix:** All motion must use `useCurrentFrame()` + `spring()` + `interpolate()`. See the animations rule.

### Mistake 6: Fixed-width containers that break on different content lengths

```tsx
// BAD — if text is longer than 400px the container clips it
<div style={{ width: 400, textAlign: "left" }}>
  <div>Short text</div>
  <div>This text is much longer and will overflow or wrap awkwardly</div>
</div>
```

**Fix:** Use `maxWidth` instead of `width` for text containers, or let the container size to its content naturally when using the centered-block pattern.

---

## The 9-Quadrant Grid (for overlay-heavy scenes)

When building scenes with multiple distinct overlay elements (as opposed to simple headline+subtitle layouts), use the 9-quadrant grid model:

```
1080x1920 frame
================

+----------+  above the fold (atmospheric / decorative)
|          |  ~0-300px — scan lines, tickers, accents
+----------+
|  SAFE    |  row 1:  ~350-700px    (top content)
|   ZONE   |  row 2:  ~750-1100px   (middle / hero content)
|          |  row 3:  ~1150-1500px  (bottom content)
+----------+
|          |  below the fold (atmospheric / decorative)
|          |  ~1500-1920px — bokeh, particles, grids
+----------+
```

Every overlay-heavy scene must fill all 5 zones with something, not just the safe zone. An unused above-fold or below-fold area makes the frame feel empty and wastes the extra vertical real estate that the portrait format gives you.

### Specific pixel anchors per row

These are the working positions for elements in each row, not strict boundaries:

| Zone | Y position | Typical content |
|------|------------|-----------------|
| Above fold | top: 120-280 | Scan bars, stock tickers, warning strips, scanning line sweeps, digital rain |
| Safe row 1 | top: 350-700 | HUD elements, headline, stat counters, brackets + framed content |
| Safe row 2 | top: 750-1100 | Hero text, center visual, logo, 3D objects — the ONE BIG thing |
| Safe row 3 | top: 1150-1500 | Secondary info, slash dividers, progress bars, callouts |
| Below fold | top: 1500-1900 | Bokeh dots, particles, network nodes, atmospheric elements |

### Common mistake: content too high

When something "feels too high" the fix is almost always to bias the whole scene DOWN by 75-150px. The default instinct is to place content near the top of the safe zone, but for vertical video the eye sits closer to the center-bottom on mobile.

If the user says "move it down 50 pixels", do it literally. If they say "looks too high" without a number, try +100px first.

### Above and below the fold are NOT decoration-only

Above-fold and below-fold elements should relate to the scene's concept, not just be generic particles:

- If the scene is about surveillance, above-fold can be a radar sweep and below-fold can be a targeting crosshair
- If the scene is about finance, above-fold can be a stock ticker and below-fold can be dollar-sign rain
- If the scene is about conditioning, above-fold can be scan lines and below-fold can be "They Live" style subliminal words

These secondary-zone elements carry thematic weight. Use them intentionally.

### Row spacing

Minimum 80px between the bottom of one row and the top of the next. For "feels cramped" fixes, bump to 120-150px. See [sizing-and-weight.md](./sizing-and-weight.md) for the full spacing guidance.

---

## Quick Reference: Positioning Cheat Sheet

```
1080x1920 frame
================

Safe zone boundaries:
  top:    210px
  bottom: 310px (from bottom, i.e. max y = 1610)
  left:   60px
  right:  120px (from right, i.e. max x = 960)

Common absolute positions:
  Headline:         top: 240,  left: 60, right: 120
  Content area:     top: 480,  left: 60, right: 120
  Bottom subtitle:  bottom: 380, left: 60, right: 120
  Bottom CTA:       bottom: 340, left: 60, right: 120

9-quadrant anchors (for overlay-heavy scenes):
  Above fold:  top: 120-280
  Safe row 1:  top: 350-700
  Safe row 2:  top: 750-1100  (hero)
  Safe row 3:  top: 1150-1500
  Below fold:  top: 1500-1900

Content area height: ~1130px (from top: 480 to bottom: 380)
Safe zone total:     900px wide x 1400px tall

Font sizes:
  Hero headline:    96-120px, weight 900  (center hero element)
  Scene headline:   56-72px,  weight 800
  Body/feature:     36-40px,  weight 600
  Subtitle/caption: 32-36px,  weight 400
  Label/small:      28px minimum (anything smaller is unreadable on mobile)
  Monospace/log:    14-18px,  weight 500-600
```
