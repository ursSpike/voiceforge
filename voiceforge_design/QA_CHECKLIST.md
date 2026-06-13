# VoiceForge — QA Checklist

## Offline & determinism
- [x] No CDN, web font, analytics, or network request of any kind.
- [x] Opens from `file://` — only `styles.css`, `app.js`, `design_data.js`.
- [x] Deterministic render: same data → same page on every load.
- [x] No numeric product claim hard-coded in HTML/CSS (verified: all numerals injected from `window.__DATA__`).

## Truth labels
- [x] Every aggregate wears a provenance chip; legend in Chapter 01.
- [x] κ shown with band, raw agreement, n, and a CI strip that visibly crosses zero ("shown, not smoothed").
- [x] Estimated values are italic, ≈-prefixed where modeled, and chip-labeled "not observed savings".
- [x] Failure events labeled "signal hits, not failed calls".
- [x] Heuristic column footnoted as keyword heuristic, not gold.
- [x] Unmeasured timing shown as absent; never 0.
- [x] Hero call disclosed as constructed; Bolna/Cartesia sequence caveats in Chapter 08.
- [x] Excluded transcripts appear as dimmed disabled chips with an explanatory title — never hidden.

## Interaction
- [x] ←/→ jump chapters; `P` toggles demo path; Esc closes sheet/panel.
- [x] Spine shows current chapter; topbar appears after the title moment.
- [x] All call-ID chips, queue items, and table rows open the call sheet.
- [x] Evidence click highlights cited turns and centers the first one (container scroll, no page jump).
- [x] Closing the sheet returns focus to the triggering element; page scroll position untouched.
- [x] Call filter narrows by id / lang / profile / workflow / source.

## Accessibility
- [x] Skip link; visible `:focus-visible` ring; keyboard-openable rows (Enter).
- [x] Call sheet is `role="dialog" aria-modal="true"` and labelled.
- [x] Dot-field and band have `role="img"` text alternatives.
- [x] `prefers-reduced-motion`: all transitions/animations disabled; sheet opens instantly.

## Layout
- [ ] 1440×900: verify no horizontal overflow, spine labels visible.
- [ ] 1280×720: spine collapses to numbers; grids fold to 1–2 columns; verify trap numerals fit.
- [x] `overflow-x: hidden` guard; long hashes word-break inside panels.
- [x] Print stylesheet: fixed chrome hidden, sheets flattened, reveals forced visible.

## Capture robustness
- [x] Visible-by-default reveal strategy: a static or non-painting capture of any chapter shows complete content.

Unchecked items are environment checks to repeat on the demo machine.
