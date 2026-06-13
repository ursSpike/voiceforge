# BATCH 1 — The Single Surface: demo = prototype = presentation (CONFIRMED)

**One local page, one server (or plain `open` from Finder). It IS the demo, IS the prototype, IS the
slides.** The cinematic chapter story AND the full working product (76-call explorer, call detail with
evidence clicks, calibration, metric trap, Success×Friction, improvement queue, sponsor proof) merged
into one surface. Built FROM Spike's spoken script — the screen follows the voice.

**Confirmed decisions:** key-press advance (→ / ← like slides; safer hands while speaking; scroll still
works inside a slide for the product views) · 6:30 spoken target inside the 5–7/8-min window · intro:
"Saivarshith — Spike — CSE IIT Kharagpur '25, SDE at Fujitsu Research, built this solo."

## Visual direction (the green system)
- Whole-experience background: ONE continuous **breezy green gradient** — Amazon-forest atmosphere,
  Apple-UI smoothness (soft color field, NOT a photo). Slow hue drift across chapters is allowed;
  legibility is the law.
- Each chapter: consistent internal palette (green family) chosen AGAINST the gradient — card
  surfaces, inks, accents all specified WITH contrast ratios. Clean minimal icons per chapter.
- **Projector-safe**: must hold on Spike's Mac (retina) AND a 1080p washed-out projector. AA+ contrast,
  solid data surfaces, no thin grays, test at 1440×900 and 1920×1080.
- Slides: equal rhythm — every beat = one viewport-height scene (100svh), same vertical grid. Product
  views (calls table, call detail) may scroll INTERNALLY within their fixed scene frame.
- Slide text minimal: headline + ≤3 supporting lines; the spoken script carries the rest.

## Agent fan-out (run all three in parallel, background)
- **Agent A — inspiration scout** (WebSearch/WebFetch): find 5–8 real sites/products with
  green-gradient/nature-meets-product design (think Apple event pages, linear-style gradients,
  forest/breeze palettes). Extract: exact background gradient recipes (stops + hues), which foreground
  surface treatments stay legible on them, icon style, type-on-gradient rules. Output:
  `docs/plans/_batch1_inspiration.md` with hex values + reasoning + DON'Ts.
- **Agent B — demo architect**: build the slide-by-slide spec from `docs/demo_script.md` beats +
  `docs/product_brainstorm.md` choreography + real artifact data (`out/demo_report_data.json`).
  Target **9–11 slides** incl. intro + close. Per slide: id · seconds (sums to ~390s) · spoken-beat
  summary · ON-SCREEN content (exact real numbers/components: which cards, which chart, which call) ·
  interaction available (e.g. "→ opens cmd_hi_0007 detail") · sizing rule. Output:
  `docs/plans/_batch1_slide_spec.md`.
- **Agent C — script + speech coach**: produce **`docs/demo_docs.md`** — THE one file Spike reads:
  1. word-for-word spoken script in SHORT speakable phrases (he memorizes phrases, not paragraphs);
  2. intro (self-intro above) + close (thank Bolna/Cartesia, the one-liner, invite questions);
  3. per-slide second budgets (sum 6:30) + cumulative clock;
  4. **coaching marks inline**: [PAUSE] (silence replaces filler sounds — reads as confidence),
     [SLOW — explain mode] for eval concepts (κ, calibration, metric trap, phenotypes) in
     non-engineer language, [PUNCH] on signature lines, breath points, bolded stress words,
     look-up-at-room cues;
  5. "WHAT THIS MEANS" box under every beat — plain-language breakdown so Spike *understands* each
     concept (he skipped the notebooks): what κ is, why low-κ-honest beats high-κ-fake, what the
     metric trap is, what a phenotype is, what "estimated/heuristic/uncalibrated" mean;
  6. likely Q&A with 2-line answers (reuse demo_script.md kill-list, simplified).
  Rule: every number from committed artifacts only (κ 0.206, 25/45, 33/41 grounded probe, 82%/14%
  brittle, $0.051, archetypes 25/5/7/3/5/1, hi-en≈en truth correction).

## Then (coordinator — me)
1. **Build the surface skeleton**: `pipeline/present.py` → `out/present.html` — self-contained
   (embedded real data, zero network), key-press slide engine (→ ← Home; progress dots; ESC closes
   any drawer), reusing `web/dashboard_app.js` components for the product views. DOM classes
   documented as a strict contract.
2. **Write the SINGLE-SHOT Claude-design prompt** from A+B+C: full DOM contract (every class, the
   83-class lesson learned — paste the list, "style this exact DOM, do not assume markup"), the green
   system from A, slide rhythm/sizing rules from B, projector constraints, honesty-element rules
   (.pending/caveats stay loud), reduced-motion, ≤~500 lines pure CSS, return ONLY CSS.
3. Spike fetches once → I audit (DOM-coverage diff — mandatory after rounds 1/2 missed 5 and 35
   classes), graft, browser-verify (keypress walk of all slides at 1440×900 + 1920×1080, console
   clean, contrast spot-checks), regenerate, commit.
4. Rehearsal pass: Spike reads `docs/demo_docs.md` against the surface; we trim any slide over budget.

## Gates & guards
- Frozen artifacts untouched (labels b3884f9e, judge 7b76ba48, calls 444956c8, rubric c1cc8141).
- All honesty wording survives (uncalibrated dims, estimated costs, heuristic completion, truth-corrected
  calibration caption). audit.md checked before/after.
- The old `out/dashboard.html` stays as the deep-dive fallback artifact, but **`out/present.html` is
  the demo**. README_DEMO updated to point at it once verified.

**Sequencing: TONIGHT, first.** Agents A/B/C in parallel (~30–45 min), skeleton built while they run,
prompt to Spike, integration after fetch. Sleep gate respected — if the design fetch slips, the
skeleton + default green CSS is already presentable.
