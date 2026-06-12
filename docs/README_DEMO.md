# VoiceForge — demo runbook (Jun 13)

**Thesis (one breath):** Most voice-agent demos stop when the call ends. VoiceForge starts there —
it turns call logs into deterministic measurements, blind-calibrated judgments, call phenotypes,
failure clusters, and an improvement queue.

## Launch (canonical repo: `/Users/varsh/voiceforge`)

```bash
cd /Users/varsh/voiceforge
.venv/bin/python web/recorder/serve.py            # booth + /shot + /label on :7861
open http://localhost:7861/shot                   # money-shot page (hero call, click-to-seek)
open out/demo_report.html                         # static report — works with NO server
```

Regenerate everything from committed artifacts (deterministic):

```bash
.venv/bin/python pipeline/score.py                # out/calls.json + analytics.json (76 calls)
.venv/bin/python pipeline/demo_report.py          # out/demo_report.{md,html}
.venv/bin/python pipeline/chart.py                # reports/charts/business_value.png
.venv/bin/python pipeline/validate_labels.py      # label CSV integrity (out/label_validation.json)
.venv/bin/python pipeline/preflight.py            # the executable checklist
```

## Offline fallback (in failure order)
1. **`out/demo_report.html`** — fully self-contained static page; open from Finder, zero network.
2. **Fallback screen recording** (made Batch H) — plays the money shot if live audio dies.
3. **Screenshots** in `reports/screenshots/` (Batch H) — report page, /shot, booth, chart.
4. Markdown: `out/demo_report.md` readable in any editor; chart PNG in `reports/charts/`.

The demo NEVER requires network: judge results are cached to disk; all pages are local.

## Screenshot checklist (capture in Batch H, after real labels)
- [ ] `out/demo_report.html` — headline cards (labels + kappa populated)
- [ ] phenotype bars + archetype table sections
- [ ] representative-call cards + improvement queue
- [ ] `/shot` with the failure table visible (0:15 barge-in / 0:48 gap)
- [ ] booth `/label` mid-annotation (shows blindness + review gate)
- [ ] `reports/charts/business_value.png`
- [ ] terminal: `preflight.py` output green

## Architecture (say it in this order)
```
provider logs (Bolna real call · SpokenWOZ · Code-Mixed-Dialog · constructed hero)
   └─ normalize (schema constitution · all-or-none timing invariant · provenance)
        └─ deterministic signals (FTO: barge-in, latency; never judged)
             └─ blind human labels (46-call frozen manifest · phenotype tags)
                  └─ quarantined LLM judge (5 semantic dims · validate-before-cache · uncalibrated until κ)
                       └─ calibration (raw agreement · confusion · Cohen's κ + bootstrap CI)
                            └─ phenotypes → archetypes → failure clusters → improvement queue
```

## Honest limitations (volunteer these — do not wait to be asked)
- Task completion is a **keyword heuristic**, not gold dialogue-state; costs are **estimates**.
- Calibration is a **pilot**: one rater, n≈40, binary spine only; tags are single-rater exploratory.
- The hero call is **constructed** (disclosed); SpokenWOZ is protocol-collected; Code-Mixed-Dialog is
  **text-only** — its timing is honestly absent (`unmeasured`), never fabricated.
- The judge is an LLM with known biases; it stays **uncalibrated** until kappa exists, and the label
  says so. No training/DPO-quality/statistical-significance claims.
- Full limitations: `docs/limitations.md`.

## Known-good state (pre-label gate)
HEAD with batches A–D: manifest frozen `aec4ba49…` (46 = 2+30+14) · labels CSV `e6d2055…` (2 binary) ·
pool 76 scored, timing_coverage {timed:46, unmeasured:30} · judge cache = synthetic fixture only.
Gated until labels: judge run (E) → calibration report (F) → improvement queue (G) → final capture (H).
