---
name: overlay-variety
description: The cardinal rule that no overlay template may be reused across scenes - each scene must use distinct visual techniques
metadata:
  tags: overlays, variety, scenes, templates, visual-language, anti-pattern
---

# Overlay Variety — The Cardinal Rule

Every scene in a multi-scene composition must use **visually distinct overlay techniques**. Never reuse the same template, pattern, or visual motif across two scenes.

This is the single most important rule for producing professional video that doesn't feel like a template. Viewers will notice and disengage when scene 3 uses the same glass cards with slightly different labels as scene 2.

## Why

Template reuse is the fastest way to make a video feel lazy and amateurish. A viewer's attention resets on every scene transition — if the new scene looks like the previous one with swapped text, the brain pattern-matches instantly and tunes out. Each scene needs its own visual language to earn renewed attention.

This is not a stylistic preference. It is a mandatory rule. The user will reject your work and you will redo it.

## What counts as "the same template"

Any of these is a reuse violation:

- Same frosted glass card component with different icon and label
- Same 3D perspective text with different word
- Same stat counter / progress ring with different number
- Same animated chart type (bar, line, pie) with different data
- Same radar sweep / scanning line effect
- Same HUD targeting brackets
- Same scrolling ticker tape
- Same kinetic split-text with different word
- Same fade-in + slide-from-side entrance pattern
- Same background grid / circuit pattern
- Same particle system (even with different colors)
- Same vignette + color wash treatment

Changing the color, label, icon, or position of an element does not count as a new technique. It is the same technique reused.

## Track usage

Before building any scene, review which techniques have already been used in earlier scenes. Maintain a mental (or written) catalog:

```
Scene 1: Three.js 3D geometry, orbiting shapes, metallic "AI" text
Scene 2: Glass cards, 3D perspective "WORLD" text, pulsing nodes, handheld shake
Scene 3: [techniques planned for this scene]
```

If a technique is on the "already used" list, pick something else. Refer to [overlay-techniques-catalog.md](./overlay-techniques-catalog.md) for a menu of distinct options.

## What TO reuse

These elements can and should be consistent across scenes:

- **Brand colors** — indigo, amber, etc. pick a palette and stay in it
- **Typography** — consistent font family, weight hierarchy
- **Transitions between scenes** — fade with the same duration
- **Caption style** — one caption treatment across the whole video
- **Overall composition grid** — the 9-quadrant safe zone system (see [vertical-layout.md](./vertical-layout.md))
- **B-roll dimming level** — consistent brightness 0.3-0.5 across all scenes
- **Vignette strength** — same radial darken

Consistency is for the foundation. Variety is for the content layer.

## Wrong approach (do not do this)

Scene 2 uses glass cards with icons + labels. Scene 3 needs to show three concepts related to the current voiceover.

**WRONG:** Copy the glass card component from scene 2 and change the labels to match the new scene. Add a different 3D perspective text in the middle.

This is template reuse. It is rejected.

## Right approach

For scene 3, pick 3-5 completely different techniques from the catalog:

- Above the fold: digital rain / binary stream
- Row 1: HUD targeting brackets + radial progress ring with counter
- Row 2: hollow outline text with offset shadow (NOT 3D perspective)
- Row 3: typewriter text reveal on a monospace bar
- Below the fold: bokeh dot field

Zero overlap with scene 2. Same 9-quadrant grid structure, different execution.

## The mindset

When proposing an overlay plan for a scene, pre-filter the catalog:

1. List techniques used in all previous scenes
2. Cross them off the catalog
3. Pick from what's left
4. If the scene's voice needs energy similar to an earlier scene, find a DIFFERENT technique that achieves that energy

Example: Scene 2 used glass cards (calm, informational). Scene 5 also needs calm informational energy. Do NOT use glass cards again. Use a bracket-frame corner technique, or bottom-third news bars, or stat counters — all calm and informational but visually distinct.

## Plan BEFORE building

Never start coding a new scene's overlays without first proposing a plan that lists the specific techniques you intend to use and confirming they are not reuses. Get user approval of the plan before writing JSX.

If you catch yourself thinking "I'll just copy this from the previous scene and change the labels" — stop. That is the exact moment you are about to violate the rule. Delete that thought and pick a different technique.
