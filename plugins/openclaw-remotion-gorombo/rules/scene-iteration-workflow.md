---
name: scene-iteration-workflow
description: Per-scene review cycle - propose plan, wait for approval, build, ship to Studio, iterate before moving on
metadata:
  tags: workflow, scenes, approval, iteration, process
---

# Scene-by-Scene Iteration Workflow

Build videos one scene at a time with a strict approval cycle at each step. Do not move on to the next scene until the current scene has been reviewed and approved in Studio by the user.

This is a workflow rule, not a style rule. It exists because batch-building multiple scenes and then reviewing all of them at the end produces more rework than it saves. The user will reject early decisions that had downstream consequences, and you will redo everything.

## The cycle for each scene

For every scene after the first, follow this exact sequence:

1. **Read the voiceover line** for the scene. Find the exact start and end timestamps in the transcript.
2. **Identify the concept** the voiceover is communicating. Write it in your own words (see [match-words-not-vocabulary.md](./match-words-not-vocabulary.md)).
3. **Review used techniques** from earlier scenes (see [overlay-variety.md](./overlay-variety.md)). Cross them off the catalog.
4. **Pick 4-6 distinct techniques** from the remaining catalog, one per row of the 9-quadrant grid.
5. **Propose the plan** to the user. Describe each technique you intend to use and where it goes on the grid. Wait for approval.
6. **Build the scene** after the plan is approved. Use inline styles, staggered timing, safe zone positioning.
7. **Ship to Studio.** Tell the user it's ready to refresh and review.
8. **Iterate** on specific feedback (nudges, sizing, timing) until the user says they're happy.
9. **Move to the next scene** only after explicit approval of the current one.

Never build step 6 without completing step 5. Never build step 7 or 8 for scene N+1 while scene N is still being reviewed.

## What "proposing the plan" looks like

The plan should describe each overlay element concretely so the user can picture the scene before any code is written:

```
Scene 3 — Datacenter b-roll, 270 frames (9 seconds)
Voiceover: "choose to use these tools determines your future and can determine the future of those around you"
Concept: the decisions you make about AI ripple outward and shape what happens to you AND the people around you

ABOVE FOLD:
- Scanning line sweeps down slowly across the datacenter footage with a cyan trail

SAFE ZONE ROW 1:
- HUD targeting brackets springing inward, locking on a radial progress ring drawing itself to 100% with "TOOLS" label in the center

SAFE ZONE ROW 2 (hero):
- "FUTURE" as outline-only text (hollow white stroke, no fill) with a solid indigo offset shadow 4px behind it. No 3D perspective — flat and bold

SAFE ZONE ROW 3:
- Typewriter text reveal: "YOUR CHOICE SHAPES EVERYTHING" appearing character by character with a blinking cursor, monospace font on a dark semi-transparent bar

BELOW FOLD:
- Bokeh dot field — 15-20 soft blurred cyan/indigo circles drifting upward slowly

BACKGROUND:
- Datacenter b-roll dimmed to 0.4 with slow zoom + color shift gradient wash (blue → teal)

Every element is a technique that has NOT been used in earlier scenes.
```

After the user approves, THEN write the JSX.

## What iteration looks like

After the user refreshes Studio and reviews the scene, expect small feedback like:

- "Everything is about 100px too high"
- "The bottom row needs to drop 25 pixels"
- "The bubbles are too small, double them"
- "Can this pulsate / rotate / breathe"
- "The color is off"

Apply these literally. Don't reinterpret. Don't add extra changes you weren't asked for. Make the exact adjustment and tell the user to refresh.

If the user rejects the overall approach — "no this isn't working, let's rethink it" — go back to step 5 and propose a new plan.

## What NOT to do

- Do NOT build scenes 2-10 in one pass and then hand them all over for review
- Do NOT skip the plan proposal step because "it's obvious what this scene should do"
- Do NOT make "improvements" to a scene after the user said it was approved (unless they asked for them)
- Do NOT start scene N+1 while scene N is still being reviewed
- Do NOT change settings on scene N while fixing scene N+1 (keep edits scoped to the scene under review)

## Exception: the first scene

Scene 1 is often built as part of composition scaffolding before the full review cycle kicks in. That's fine. But from scene 2 onward, every scene follows the full cycle.

## Why this takes longer at first but saves time

Building a 10-scene video this way feels slow for the first 2-3 scenes because of the plan-approve-build-iterate cycle. By scene 4 it's faster than batch-building because:

- You catch mismatches early (wrong technique, wrong sizing) before they propagate
- You build a shared visual language with the user as you go
- The user notices patterns and refines direction ("use more like scene 3 did")
- Rework shrinks to nudges instead of full rewrites

Rework is the enemy. This workflow minimizes it.

## When the user gives you blanket approval

Sometimes the user will say "just keep going" or "do the next one" without explicit approval of the current scene. That's your signal to move on — but still propose a plan for the next scene before building it. Blanket approval means they trust your work, not that they're turning off plan review.

## Don't delegate the cycle to later

The cycle runs in real time during the session. Don't say "I'll build these 3 scenes then show you all of them" — that is not this workflow. One scene at a time.
