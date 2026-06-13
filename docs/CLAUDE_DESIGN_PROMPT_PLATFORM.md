# Claude Design — `/platform` clinic workspace (the ONLY prompt to send)

**Surface to attach when pasting:** `out/platform/index.html` + `out/platform/styles.css` +
`out/platform/app.js` (+ optionally a screenshot of the current state).

**Do not send `/`** — it was already cleared (8 viewport-locked scenes, 3 resolutions, 0 overflow).

---

```
Design only the `/platform` clinic workspace.

Do not redesign `/`.
Do not change copy claims or invent numbers.
Do not use fixture data.
Do not add new product areas.
Do not assume backend changes.

Context:
- This is a live operator/demo workspace for a Bolna + Cartesia clinic scheduling agent.
- Final agent:
  - Aarogya Clinic & Diagnostics — Aarav
  - Cartesia Devansh / sonic-3
  - Hinglish-first
  - KB attached
- Need a clean, impressive, founder-grade product surface for demo.
- Audience is technical founders/engineers and product/FDE people.
- Must feel serious, not generic SaaS.

Goals:
- Make `/platform` feel like a real operator workspace.
- Highlight:
  - agent status
  - KB attached
  - latest live calls
  - extracted booking fields
  - transcript
  - deterministic signals
  - judge evidence
  - improvement recommendation
- Preserve clear provenance:
  - LIVE · UNCALIBRATED
  - FROZEN · CALIBRATED
- Light theme only.
- Clean typography, restrained palette, strong hierarchy.
- No horizontal clipping, no giant empty areas, no decorative excess.
- Keep it implementable against existing DOM/classes.

Output:
- CSS-only or minimal DOM-safe adjustments
- no data contract changes
- no fake features
- no fixture copy
- note any exact classes/selectors targeted
```

## Existing classes Claude must respect (do NOT invent markup)

**Layout:** `#platform`, `.topbar`, `.mode-tabs`, `.mode-btn`, `.mode-btn.active`, `.rail`,
`#rail-list`, `#rail-count`, `#search`, `#filters`, `.main`, `.view-title`, `.subtitle`.

**Clinic cards (new this turn):** `.cl-card`, `.cl-card.cl-agent`, `.cl-card.cl-kb`, `.cl-head`,
`.cl-kicker`, `.cl-prov`, `.cl-prov.ok`, `.cl-prov.uncal`, `.cl-title`, `.cl-meta`, `.cl-k`, `.cl-v`,
`.cl-v.mono`, `.cl-v.prov.ok`, `.cl-v.prov.uncal`.

**Call list + tags:** `.call-card`, `.call-card.sel`, `.cid`, `.meta`, `.ph`, `.dot`, `.dot.ok`,
`.dot.bad`, `.dot.unsure`, `.live-tag`, `.before-tag`, `.live-pip`.

**Live empty + helper:** `.live-empty`, `.cmd-helper`, `.cmd-box`, `.cmd-text`, `.cmd-note`,
`.copy`, `#exec-id`.

**Detail view:** `.call-head`, `.pills`, `.pill`, `.pill.ok`, `.pill.bad`, `.pill.uncal`,
`.pill.arch`, `.grid2`, `.transcript`, `.turn`, `.turn.agent`, `.turn.user`, `.turn.cited`, `.tid`,
`.bubble`, `.who`, `.dim`, `.dh`, `.dn`, `.dscore`, `.dtype`, `.dtype.deterministic`,
`.dtype.judge`, `.dr`, `.cites`, `.rec`, `.rh`, `.rt`, `.prov`, `.placeholder`, `.unmeasured`.

## QA gate (paste this with the prompt)
- Light theme only · no horizontal scrollbar at 1920×1080 · provenance pills semantically distinct
  (LIVE·UNCALIBRATED vs FROZEN·CALIBRATED never swapped) · no decorative gradients hiding text · no
  external `http`/`@import` in returned CSS · ≤500 lines · returns CSS only.

## When the design comes back
1. Save as `out/platform/styles.css` candidate; do NOT replace silently.
2. DOM-coverage diff against the class list above (rounds 1/2 missed 5 then 35 — paste the full list).
3. Browser-verify at 1920×1080: 0 horizontal overflow, 0 console errors, agent/KB cards readable,
   transcript readable in Hindi, judge evidence pills distinct.
4. Frozen artifact re-hash check (must be byte-identical).
