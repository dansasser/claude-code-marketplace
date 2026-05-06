---
name: explainer
description: Create an educational explainer video that teaches a topic in 5 animated scenes with voiceover, animated visuals, and captions.
user-invocable: true
argument-hint: [topic or URL]
---

Use the Remotion best practices skill (SKILL.md at the plugin root). Follow its scene planning algorithm for all production steps.

# Education Explainer

## Input
$ARGUMENTS

## Questionnaire
If not answered by the input, ask:
1. **What topic?** — What are we explaining?
2. **Source?** — URL, doc, or should I research it?
3. **Tone?** — Default: Fireship (fast, punchy, conversational). Other options: corporate, casual, technical.

## Script
Write a 5-scene script. Present it for approval before building. Each scene needs:
- One-line headline (on screen)
- Voiceover script (exact narrator words)
- Visual description (what to animate — diagrams, flowcharts, icons, step-by-step)

## Scene Structure
- **Scene 1:** Hook — grab attention, state the problem or question
- **Scene 2:** What it is — define the concept simply
- **Scene 3:** How it works — the mechanism, with animated diagram or flowchart
- **Scene 4:** Why it matters — benefits, stats, or comparison
- **Scene 5:** CTA — what to do next, link on screen

## Visual Approach
- SVG-based diagrams and icons for primary visuals.
- If b-roll is used, treat it as a background layer that supports (not replaces) the core diagram-driven explanation.
- Diagrams draw themselves (stroke-dashoffset animation)
- Key numbers use count-up animation
- Each scene has a clear visual metaphor — not walls of text
