---
name: testimonial
description: Create a testimonial video by pulling real reviews from Google Maps, Facebook, Yelp, and other platforms. Animated star ratings and review cards.
user-invocable: true
argument-hint: [business name or URL]
---

Use the Remotion best practices skill (SKILL.md at the plugin root). Follow its scene planning algorithm for all production steps.

# Testimonial / Social Proof

## Input
$ARGUMENTS

## Questionnaire
If not answered by the input, ask:
1. **What business?** — Business name and/or URL
2. **Where are the reviews?** — Google Maps, Facebook, Yelp, Trustpilot, G2, App Store, or should I search all?
3. **How many reviews to feature?** — Default: 3-5 best ones

## Script
Research reviews across all available platforms. Find:
- Overall star rating per platform
- Total review count
- Top 3-5 reviews (highest rated, most compelling quotes)
- Reviewer names (first name + last initial for privacy)
- Any common themes across reviews

Present the findings and proposed script for approval before building.

## Scene Structure
- **Scene 1:** Hook — star rating reveal with count-up animation (e.g. "4.9 stars from 127 reviews")
- **Scene 2-4:** Featured reviews — one review per scene, show the quote, reviewer name, star rating, and platform icon
- **Scene 5:** Social proof stack — all platforms side by side with ratings, CTA

## Visual Approach
- Review cards with star ratings (gold #f59e0b)
- Quotation mark decorative elements
- Platform icons/logos for source attribution
- Count-up animation for star rating and review count
- Review cards animate in with spring, stagger between reviews
- B-roll backgrounds matching the business type
