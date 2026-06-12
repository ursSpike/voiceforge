# VoiceForge — demo runbook (Jun 13)

**Thesis (one breath):** Most voice-agent demos stop when the call ends. VoiceForge starts there —
it turns call logs into deterministic measurements, blind-calibrated judgments, call phenotypes,
failure clusters, and an improvement queue.

## Launch (canonical repo: `/Users/varsh/voiceforge`)

```bash
cd /Users/varsh/voiceforge
open out/dashboard.html                           # ★ PRIMARY demo surface — self-contained, NO server
.venv/bin/python web/recorder/serve.py            # booth + /shot + /label on :7861 (for the live audio beat)
open http://localhost:7861/shot                   # money-shot page (hero call, click-to-seek)
```

**`out/dashboard.html` is the demo.** It is the full editorial dashboard (overview · metric trap · Success×Friction ·
calibration · failure intelligence · improvement queue · sponsor proof), self-contained and offline. Run it from Finder.

Regenerate everything from committed artifacts (deterministic):

```bash
.venv/bin/python pipeline/score.py                # out/calls.json + analytics.json (76 calls)
.venv/bin/python pipeline/demo_report.py          # out/demo_report.{md,html} + _data.json (report data)
.venv/bin/python pipeline/dashboard.py            # out/dashboard.html  ← the demo surface
.venv/bin/python pipeline/chart.py                # reports/charts/business_value.png
.venv/bin/python pipeline/validate_labels.py      # label CSV integrity (out/label_validation.json)
.venv/bin/python pipeline/preflight.py            # the executable checklist
```

## Offline fallback (in failure order)
1. **`out/dashboard.html`** — the primary surface itself is fully self-contained (no server, no network); open from Finder.
2. **`out/demo_report.html`** — static report, same numbers (corpus, metric trap, calibration, archetypes, queue).
3. **Fallback screen recording** of `/shot` (pending — Spike records) — plays the money-shot audio if the live booth dies.
4. **Screenshots** in `reports/screenshots/` — dashboard sections + /shot + chart.
5. **`out/demo_report.md`** readable in any editor; chart PNG in `reports/charts/`.

The demo NEVER requires network: judge results + sponsor proof are cached to disk; all pages are local.

## Screenshot checklist (Phase H capture → reports/screenshots/)
- [ ] `out/dashboard.html` overview — hero + metric-trap signature stat
- [ ] calibration view — confusion matrix + κ + disagreement list
- [ ] Success × Friction matrix + phenotype/archetype bars
- [ ] a call-detail drill-down (transcript + scorecard + judge panel)
- [ ] Calls table (human vs heuristic columns — the metric trap, per row)
- [ ] sponsor proof chain (Bolna → Cartesia)
- [ ] `/shot` with the failure table visible (0:15 barge-in / 0:48 gap)
- [ ] terminal: `preflight.py` output

## Architecture (say it in this order)
```
provider logs (Bolna real call · SpokenWOZ · Code-Mixed-Dialog · constructed hero)
   └─ normalize (schema constitution · all-or-none timing invariant · provenance)
        └─ deterministic signals (FTO: barge-in, latency; never judged)
             └─ blind human labels (46-call frozen manifest · phenotype tags)
                  └─ quarantined LLM judge (5 semantic dims = uncalibrated diagnostics · + 1 binary outcome judgment · validate-before-cache)
                       └─ calibration (raw agreement · confusion · Cohen's κ + bootstrap CI)
                            └─ phenotypes → archetypes → failure clusters → improvement queue
```

## Honest limitations (volunteer these — do not wait to be asked)
- Task completion is a **keyword heuristic**, not gold dialogue-state; costs are **estimates**.
- Calibration is a **pilot**: one rater, n≈40, binary spine only; tags are single-rater exploratory.
- The hero call is **constructed** (disclosed); SpokenWOZ is protocol-collected; Code-Mixed-Dialog is
  **text-only** — its timing is honestly absent (`unmeasured`), never fabricated.
- The judge is an LLM with known biases. **κ calibrates only its dedicated binary outcome judgment**
  (the same question the human answered); the 5 semantic dimensions have no per-dimension human gold
  and remain **uncalibrated diagnostics** — labeled so. No training/DPO-quality/significance claims.
- Full limitations: `docs/limitations.md`.

## Known-good state (post-judge, demo-ready)
Labels **complete + frozen**: CSV `b3884f9e…` (46 labeled · 45 binary 37/8 · 1 unsure), snapshot pinned `d592782a…`,
manifest `aec4ba49…`. Pool 76 scored. **Judge run complete** (`out/judge_results.json` — 46/46, 276 judgments, 0
failures, gemini-3.1-flash-lite). **Calibration: κ 0.206, raw agreement 0.711, n=45, CI [-0.108, 0.499]** (the finding,
framed honestly). Metric trap: heuristic agrees with human on 25/45. Sponsor proof cached (`cartesia/Devansh/sonic-3`).
Dashboard built, self-contained. Remaining: Phase H capture (screenshots + the /shot fallback recording).
