---
name: data-visualization
description: Create an animated data dashboard video from a CSV file or data source. 4-panel layout with charts and KPIs.
user-invocable: true
argument-hint: [CSV path or data description]
---

Use the Remotion best practices skill (SKILL.md at the plugin root). Follow its scene planning algorithm for all production steps.

# Data Visualization Dashboard

## Input
$ARGUMENTS

## Questionnaire
If not answered by the input, ask:
1. **What data?** — CSV file path, API endpoint, or should I generate sample data?
2. **What story?** — What's the key takeaway from this data?
3. **Style?** — Default: dark glass-morphism dashboard. Other options: clean/minimal, corporate, neon.

## Script
Analyze the data and propose:
- A dashboard title
- The single most impressive KPI stat (hero card)
- Best chart types for the data (bar, donut, line, etc.)
- Layout of 4 panels

Present for approval before building.

## Panel Structure
- **Panel 1:** Hero KPI — large count-up number with trend indicator (arrow up/down)
- **Panel 2:** Comparison chart — horizontal bars or grouped bars
- **Panel 3:** Composition chart — donut or pie showing parts of a whole
- **Panel 4:** Trend chart — line chart with gradient fill showing change over time

## Visual Approach
- 4-panel vertical stack with padding between panels
- Glass-morphism card backgrounds (semi-transparent, subtle border, blur)
- SVG-based charts — bars grow with spring animation, donut segments draw clockwise, line draws left-to-right
- Key numbers use count-up animation with `tabular-nums` font variant
- Staggered panel entrances — each panel animates in after the previous one
