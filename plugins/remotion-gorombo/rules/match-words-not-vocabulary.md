---
name: match-words-not-vocabulary
description: Overlays must match the concept being said, not the literal last word - a rule against vocabulary-word hero text
metadata:
  tags: overlays, hero-text, concepts, hooks, anti-pattern, visual-meaning
---

# Match the Concept, Not the Vocabulary

When choosing hero text or a central visual element for a scene, match it to **what the voiceover actually means**, not to the literal words being spoken. In particular, never take a random vocabulary word from the line and display it alone as if it were a hook.

This is a rule against a specific failure mode where the builder reads a sentence, picks the "most interesting word" (usually the last one), and slaps it on screen as 100px text thinking it constitutes a hook. It doesn't. The viewer sees a word they don't recognize as a concept and bounces.

## The failure mode

Voice over: "Some people are using AI for ways that you could not even fathom."

Wrong instinct: Put "FATHOM" on screen as the hero text of this scene.

Why it fails:
- "FATHOM" is a vocabulary word, not a concept
- A viewer watching with sound off or distracted sees "FATHOM" and has no idea what the scene is about
- It communicates nothing about AI, government, scale, or the incomprehensible nature of what's happening
- It's the last word of the sentence, chosen because it "sounds weighty", not because it carries meaning on its own
- A viewer has to mentally reconstruct what "FATHOM" was connected to, which defeats the purpose of a visual

## The test

Before putting any word or phrase on screen as hero text, ask:

**"If someone scrubbed to this frame with the sound off, would they understand what the scene is about from this visual alone?"**

If the answer is no, the visual is not doing its job. Pick something else.

For the "fathom" scene, a better visual answer isn't a different word at all — it's a visualization of SCALE and INCOMPREHENSIBILITY:

- A hexagonal grid of cells lighting up in different colors, representing different AI applications happening simultaneously
- A stat counter flashing "1,000+ APPLICATIONS"
- A radar screen with blips appearing in every direction
- A map with data points everywhere

Any of these communicates "there is an incomprehensible amount of AI activity happening you don't know about" without relying on a single vocabulary word.

## When text IS the right answer

Hero text works when the word IS the concept:

- **"FUTURE"** for a scene about what's coming (concrete, universally understood)
- **"GOVERNMENT"** for a scene about institutional power
- **"WORLD"** for a scene about global scale
- **"MONEY"** for a scene about finance/wealth
- **"SYSTEM FAILURE"** for a scene about breakdown

These are concepts a viewer recognizes instantly. Each one is self-contained.

Hero text fails when the word is a modifier, adjective, or vocabulary flex:

- **"FATHOM"** — verb, requires context to understand
- **"INSURMOUNTABLE"** — adjective, abstract
- **"UBIQUITOUS"** — adjective, requires the noun it describes
- **"CATALYZE"** — verb, requires the object being catalyzed

## Alternatives to single-word hero text

When no single word works, use one of these patterns instead:

1. **Short phrase (2-4 words):** "THE REAL PRICE" — more context than one word
2. **Visual concept, no text:** A data visualization or graphic that IS the hook
3. **Stat counter:** A number with a small label, like "94% / COMPLIANCE RATE"
4. **Quote-style line:** A short excerpt of the voiceover displayed as a caption-style line

See [overlay-techniques-catalog.md](./overlay-techniques-catalog.md) for specific patterns.

## The discipline

Every time you plan a scene, write down the voiceover sentence and then write down the CONCEPT in your own words. The concept is what the viewer should understand from the visual. The concept is what you design for.

Voiceover: "Some people are using AI for ways that you could not even fathom."
Concept: "There is a hidden, overwhelming amount of AI activity in places you don't see."
Visual: Hex grid of activating cells + "1,000+ APPLICATIONS" counter + faded "CLASSIFIED" sidebar text.

Voiceover: "They just need you to be okay with your bank using AI."
Concept: "Institutions like banks are being handed AI and you're expected to accept it."
Visual: Biometric scan ring with "ACCESS GRANTED" flash + bank icon panel stamped "AI ENABLED".

Voiceover: "And that's how they make their money off of it."
Concept: "This is the money pipeline behind the scenes."
Visual: Animated money trail with dollar amounts ticking up along the path.

In every case, the VISUAL communicates the CONCEPT. The vocabulary word from the voiceover does not appear alone on screen.

## One more thing

When the user asks "what does that even mean in this context / how are people going to know that / how is that a hook", they are telling you that you violated this rule. The correct response is to delete the vocabulary-word visual and build a concept visual instead. Do not argue. Do not defend the choice.
