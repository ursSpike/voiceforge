# VoiceForge Design Integration — Round 1

## Decision

The Fable design bundle in `voiceforge_design_1/` is a visual reference only. Its
`overview_artifact.js` contains fixture values and must never be used in the demo.
The production dashboard continues to be generated from VoiceForge's committed
artifacts through `pipeline/demo_report.py` and `pipeline/dashboard.py`.

## What Was Integrated

- Warm off-white canvas, ink typography, restrained emerald, and selective glass.
- Editorial overview hierarchy with a short product thesis.
- A deterministic "What to fix first" block backed by human phenotype tags and
  estimated prototype call costs.
- Four product metrics with visible provenance and caveats.
- A Success x Friction matrix derived from blind human labels.
- Binary judge calibration with confusion matrix, raw agreement, kappa, and CI.
- Evidence-linked call detail: clicking a score highlights cited transcript turns.
- Sponsor proof that separates the real Bolna ingest, live Cartesia-in-Bolna
  configuration, and cached Cartesia hero audio.
- A guided demo path that changes attention only, never data or caveats.

## Data Contract

The dashboard reads:

1. `out/analytics.json`
2. `out/calls.json`
3. `out/demo_report_data.json`
4. `out/judge_results.json`
5. `out/bolna_cartesia_proof.json`
6. `eval/labels_spike.csv`
7. `eval/label_manifest.json`

Product-facing cost values are labeled estimated prototype values. The
per-1,000 exposure is a modeled extrapolation, not observed savings. Phenotype
tags are single-rater exploratory labels. Kappa calibrates only the binary
outcome judge; the five semantic dimensions remain uncalibrated diagnostics.

## Verification

- `pipeline/demo_report.py --selftest`: 15/15 passed.
- Python compilation and JavaScript syntax checks passed.
- Browser verification at 1440 x 900:
  - overview and call-detail layouts render correctly;
  - evidence clicks highlight the expected transcript turns;
  - guided demo path opens and navigates;
  - no browser console errors.
- The dashboard uses real artifacts. No design fixture was copied into the
  runtime path.

## Next Design Round

Keep further work tightly scoped:

1. Capture final overview and call-detail screenshots after the final judge
   artifact is committed.
2. Rehearse the seven-step demo path and trim any section that slows the story.
3. Add motion only where it explains state change; preserve reduced-motion mode.
4. Do not add auth, billing, settings, team management, or generic SaaS chrome.
