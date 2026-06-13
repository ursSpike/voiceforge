# VoiceForge — Design Rationale

## Concept

VoiceForge is presented as **one continuous case being made**, not a dashboard.
The page is a vertical narrative of nine stacked sheets — thesis → measurement →
the metric trap → calibration → friction → evidence → action → proof → method —
mirroring the 7–8 minute demo beat-for-beat. Each sheet pulls over the previous
one with a rounded top edge and shadow, so causal progress is legible even in a
static screenshot.

The identity idea: **raw signal → forged judgment**. The mark is an open
diamond (raw) joined by a rule to a solid ember diamond (forged). No
microphones, flames, or waveforms.

## Palette and proportions

Light, warm, paper-toned. Approximate proportions:

- ~86% warm paper fields (`#FAF6EE` and nearby tones, one per chapter)
- ~8% ink text (`#221B12`, soft `#6B6052`)
- ~4% semantic provenance hues (steel, green, violet, ochre)
- ~2% ember accent (`#B4541C`) — reserved for identity, emphasis, and the
  brittle/fix-first moments

Color is **semantic before decorative**: every provenance class has one hue at
matched lightness (Measured steel, Human-labeled green, Binary-calibrated
violet, Uncalibrated/Exploratory ochre with dashed borders, Estimated ember in
italics, Not-observed gray). Estimated values are additionally italicized so
honesty survives grayscale projection.

## Typography

Offline system stacks only: a serif display voice (Iowan Old Style / Palatino /
Georgia) for thesis lines and large numerals; the system grotesque for UI and
body; monospace for call IDs, hashes, provenance chips, and axis labels.

## Information architecture for the live demo

- A fixed **chapter spine** (left) shows position and what comes next.
- **←/→ jump chapters**; `P` opens the Demo Path overlay with the nine timed
  beats; Esc closes everything.
- **Call evidence opens as a sheet over the story** — the narrative never
  scrolls away. Every call ID anywhere (disagreements, fix-first evidence,
  queue) opens the same sheet, with click-to-highlight cited turns.
- The improvement queue is staged as the destination chapter, grouped by
  recommended change.

## Motion map

- Sheets stack statically (no scroll-hijacking, no sticky traps).
- Sections rise ~26px/0.7s as they enter the viewport. Crucially, **visible is
  the base state**: hiding is applied by JS only after two animation frames
  prove the environment paints. Print, capture, reduced-motion, and any
  throttled context get the complete page.
- The call sheet slides in 320ms; reduced-motion swaps to instant.

## Truth posture

All displayed numbers are read from `window.__DATA__` at load; no product
number is hard-coded in markup. The κ confidence interval is drawn crossing
zero with the caption "shown, not smoothed". Modeled per-1,000 exposure is
marked ≈, italic, and chip-labeled "not observed savings". Excluded transcripts
render as dimmed, disabled chips rather than disappearing.
