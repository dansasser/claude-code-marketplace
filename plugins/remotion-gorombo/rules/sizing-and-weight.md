---
name: sizing-and-weight
description: Sizing guidance for overlay elements - when things feel weak they need to be doubled and spread out, not subtly tweaked
metadata:
  tags: sizing, weight, overlays, hero-elements, spacing, visual-impact
---

# Sizing and Weight

When the user says a scene "feels weak", "feels empty", or "isn't enough", the answer is almost never "add more elements". The answer is **make the existing elements bigger and spread them further apart**.

This rule exists because the instinct when something feels weak is to add more stuff, which produces clutter instead of impact. Size and spacing carry weight. More elements at the same size feels busier without feeling stronger.

## The default response to "feels weak"

Double the hero element's size. Widen the spacing between rows by 80-100px. If there's still slack, increase the stroke/border thicknesses and glow intensity.

Specifically:

- **Hero text (center element):** 72px → 108-120px
- **Hero icon (center element):** 180px → 360px
- **Glass card title:** 28px → 32-36px
- **Stat counter number:** 64px → 96-120px
- **Progress ring / HUD element:** 240px → 440px
- **Bracket corners:** 35px → 50px with 2px → 2.5-3px borders
- **Row-to-row spacing:** 50px → 100-150px
- **Horizontal spacing in grids:** 30px → 60px
- **Glow radius:** 20px → 35-50px

## Size ranges for 1080x1920 vertical

This is the reference for sizing decisions. Use the LOWER end as a default, the HIGHER end when the user says "feels weak" or "needs to pop".

| Element type | Size range | Weight |
|--------------|------------|--------|
| Hero text (center, one per scene) | 96-120px | 900 |
| Scene headline text | 56-72px | 800 |
| Secondary headline | 40-56px | 700 |
| Glass card title / row text | 28-40px | 600-700 |
| Stat counter main number | 64-108px | 900 |
| Label text (above/below counter) | 14-22px | 600-700 |
| Ticker tape text | 14-22px | 500-600 |
| Monospace log text | 12-18px | 500-600 |
| Caption / subtitle | 40-56px | 700-800 |
| Corner accent text | 12-16px | 500-600 |

## Icon and visual element sizes

| Element | Default | "Feels weak" | Hero |
|---------|---------|--------------|------|
| Logo (brand mark) | 180x180 | 260x260 | 360x360 |
| Emoji in glass card | 48-56 | 60-72 | 80-100 |
| SVG icon (bank, shield) | 50x55 | 65x70 | 90x100 |
| Currency badge circle | 100px dia | 125px dia | 150px dia |
| Progress ring outer | 200x200 | 320x320 | 440x440 |
| Radar sweep | 180x180 | 260x260 | 360x360 |
| Hex grid cell | 60x70 | 72x82 | 90x100 |

## Spacing for room-to-breathe

Weak scenes are almost always too tight. Add space.

| Spacing type | Tight (avoid) | Default | Breathing |
|--------------|---------------|---------|-----------|
| Between safe zone rows | 40-60px | 80-100px | 120-150px |
| Between glass card + next element | 30px | 50-70px | 90-100px |
| Horizontal gap in grids/rows | 20px | 30-40px | 60-80px |
| Margin around hero element | 30px | 50-60px | 80-120px |
| Row 1 to row 2 (safe zone) | 100px | 200-250px | 300-350px |

When the user asks "can you space these out more" — add at LEAST 100px between whatever they're pointing at, not 20px.

## Glow and shadow intensity

Weak elements often need stronger light treatment to feel dimensional and alive.

```tsx
// Default glow
boxShadow: "0 0 20px rgba(99,102,241,0.3)"

// Strong glow (for "feels weak" fixes)
boxShadow: "0 0 35px rgba(99,102,241,0.4), 0 0 70px rgba(99,102,241,0.2)"

// Pulsing glow (even stronger presence)
const glowPulse = 0.3 + Math.sin(frame * 0.06) * 0.15;
boxShadow: `0 0 ${25 + glowPulse * 30}px rgba(99,102,241,${0.3 + glowPulse})`
```

Text shadows for depth:

```tsx
// Default 3D shadow (on hero text)
textShadow: "0 2px 0 #4338ca, 0 4px 0 #3730a3, 0 6px 0 #312e81, 0 0 30px rgba(99,102,241,0.4)"

// Heavier 3D shadow (for larger hero text 108-120px)
textShadow: "0 3px 0 #4338ca, 0 6px 0 #3730a3, 0 9px 0 #312e81, 0 0 40px rgba(99,102,241,0.4), 0 0 80px rgba(99,102,241,0.2)"
```

## Per-element weight rules

**Hero text** is the largest element in a scene by a wide margin. If your "hero" text is 72px and your "secondary" text is 56px, they will not feel like hero and secondary — they'll feel like two peers. The hero should be AT LEAST 1.8x the next largest text element.

**Stat counters** need to dominate. The number is the hero, the label beneath is small. Ratio: number is 4-6x the label size. A 96px counter should have a 16-20px label.

**Glass cards** should be readable at a glance. Minimum card dimensions on 1080px width: 380x140 for a single-line label, 380x150-170 for icon + two-line label.

**Logos** in final cards should be at least 260x260. At 180x180 a logo reads as a bullet point, not a brand mark.

## When to spread vs when to shrink

If the user says "everything is crammed together" — space things out, don't shrink them.

If the user says "it's too busy" — that's a different problem, usually solved by REMOVING an element entirely (not by shrinking everything).

If the user says "feels weak" or "not enough" — double the hero, spread the rows.

If the user says "too small" — the specific thing they pointed at goes up 50-100%.

If the user says "take up the whole frame" — your content is confined to the safe zone and needs to bleed into the above-fold and below-fold areas. Add atmospheric / background elements to those zones (bokeh, particles, scan lines, grid patterns).

## Don't over-correct

When fixing a weak scene, do ONE pass of enlargement. Don't keep making things bigger with every iteration — that produces cartoonish output. The ranges in the tables above are bounds, not targets to exceed.

If after doubling the hero and adding breathing room the scene STILL feels weak, the problem is probably the technique choice, not the size. Switch to a different overlay technique (see [overlay-techniques-catalog.md](./overlay-techniques-catalog.md)).
