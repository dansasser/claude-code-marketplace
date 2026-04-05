---
name: product-promo
description: Create a promotional video for a product or service by researching its URL. 5 scenes with hook, solution, capabilities, trust, and CTA.
user-invocable: true
argument-hint: [product URL]
---

Use the Remotion best practices skill (SKILL.md at the plugin root). Follow its scene planning algorithm for all production steps.

# Product Promo

## Input
$ARGUMENTS

## Questionnaire
If not answered by the input, ask:
1. **What product/service?** — URL to research
2. **What's the hook?** — The pain point or attention grabber. Or should I figure it out from the page?
3. **CTA?** — What should the viewer do? (default: visit the URL)

## Script
Research the URL. Extract: what it is, who it's for, key features, pricing, differentiators, governance/trust signals, and CTA. Write a 5-scene script. Present for approval before building. Each scene needs:
- One-line headline (on screen)
- Voiceover script (natural, conversational, punchy)
- Visual description

## Scene Structure
- **Scene 1:** Hook — pain point, grab attention in 2 seconds
- **Scene 2:** The solution — what it is, key value prop, pricing if applicable
- **Scene 3:** Capabilities — what it does, features with b-roll background
- **Scene 4:** Trust — governance, security, differentiators with b-roll background
- **Scene 5:** CTA — what to do next, URL on screen, logo

## B-Roll Prompts
Generate b-roll prompts based on the product/service context:
- Scene 3: match the product's use case (office, tech, lifestyle, etc.)
- Scene 4: match the trust angle (security, data, professional, abstract)
- Scene 5: match the brand identity
