# VoiceForge Eval-Research — First Wave Status Report (Jun 13)

**Coordinator audit of 5 isolated background agents.** Read-only on the repo; all writes confined to
`experiments/jun13_eval/<agent>/` and `reports/research_jun13/`. No integration performed — this stops for Codex.

## PASS

- **Protected artifacts BYTE-IDENTICAL before/after** (re-hashed against `protected_hashes_before.txt`): labels CSV
  `b3884f9e…`, snapshot `d592782a…`, manifest `aec4ba49…`, judge_results `7b76ba48…`, calls `444956c8…`, analytics
  `3edc2ac…`, demo_report_data `f0372f03…`, dashboard `f29f3ea6…`, rubric `c1cc8141…`, normalized-manifest `7e76dd04…`.
  Nothing in `data/normalized/`, `out/`, `eval/`, `rubric.yaml`, `web/`, or `pipeline/dashboard.py` changed.
- **Tests pass:** reliability 8/8, timing 8/8 (incl. a consistency assert against `pipeline.signals.analyze`).
- **Re-run determinism:** reliability / timing / review_queue JSON are byte-identical on re-run; grounded_probe JSON is
  byte-identical across consecutive re-runs (the one-time delta was the agent's first write vs a clean regen — results stable).
- **Cross-agent metric consistency (independent agents agree on the frozen numbers):** κ 0.206 (reliability == demo_report);
  13 judge↔human disagreements (reliability == calibration == annotation R2); 20 heuristic↔human disagreements
  (annotation R3 == metric-trap 45−25); 107 barge-in / 183 latency events (timing default cell == analytics clusters);
  keyword baseline 25/45 (grounded == metric-trap).
- **All 6 primary papers verified** from arXiv primary pages (no fabrication, no secondary sources).

## WARNINGS

- **A live demo claim is FALSE and must be corrected.** The calibration caption ("9 of 13 disagreements are code-switched,
  so the judge is least reliable there") is a base-rate fallacy. Reproduced independently: **hi-en 22/31 = 71.0% vs English
  9/13 = 69.2% — ~equal.** This sample does NOT establish a code-switch reliability penalty. (Fix is the recommended
  integration below — prepared, not yet applied.)
- **Grounded-outcome is an INVESTIGATION, not a drop-in.** Its 33/41 agreement is strong but it abstains on 4 calls, the
  contract is additive-only, and replacing the production outcome would change the demo's outcome story — audit separately.
- **`reports/screenshots/` + fallback recording still empty** (Phase H, unchanged this wave — not in scope here).
- **`__pycache__/` dirs** were created under experiments by Python; excluded from commit via .gitignore.

## BLOCKERS

- None. All agents respected the sandbox; no stop-condition was hit that wasn't handled (P1 parse coverage ≥0.80 on every
  signal; no silent call drops; tiny slices benched by the min-n rule).

## Ranked findings

1. **The metric trap is real, and source-grounding can largely close it (P1).** Grounded outcome agrees with blind human
   labels on **33/41 (80.5%)** vs the keyword heuristic's **25/45 (55.6%)** — a ~25-pt lift — and catches backend failures
   *both the keyword rule and the human missed*: `cmd_hi_0007` (agent voiced a restaurant with no KB row = hallucination),
   `cmd_hi_0025` (claimed "south", KB says "centre"), `swz_MUL0280/1552` (booking never closed). 4 honest `unknown`s.
   *Highest product value; biggest surface; integrate later.*
2. **The "code-switched = least reliable" claim is unsupported — truth correction needed (P0).** hi-en 71.0% ≈ en 69.2%.
   The defensible slice is human confidence (high 82.8% vs medium 50.0%) — but that's known only post-annotation, so it
   supports a **review queue, not an auto-router**. **Call length is the actionable routing candidate** (knowable at
   inference; 50%→88% agreement spread).
3. **Balanced accuracy / Youden's J beside κ (P0 + paper 2512.08121).** balanced accuracy **0.628**, Youden's J 0.257,
   failure recall **0.500**, precision **0.308**, specificity 0.757, MCC **0.217**. Honest framing of the 37/8 imbalance
   that raw accuracy hides. κ, balanced accuracy, and the confusion matrix answer different questions — not interchangeable.
4. **Timing thresholds are reasonably robust (P2).** Default 100ms/800ms survives one-notch moves (Jaccard ≥0.79); only the
   far corner (500/2000) reshuffles. Robustness, NOT correctness — the timed slice has zero human failures.
5. **Second-rater review queue + selective-judge spec ready (P3/P4).** 35/46 calls flagged deterministically with reason
   codes; `rater2` schema preserves disagreement (LeWiDi-grounded); escalation threshold fit on a dev split only.

## Recommended production integration (ONE)

**Patch `pipeline/demo_report.py` for (a) the truth correction + (b) balanced-accuracy/Youden's-J/failure-recall beside κ.**
Rationale: fully deterministic, zero new data, fully executable on the frozen artifacts, paper-verified, reproduced by an
independent agent — and it *removes a false claim that is currently live in the demo*. It is the lowest-risk, highest-trust
change. The grounded-outcome probe (#1) is higher product value but is an investigation that would change the outcome story
— queue it for a separate, audited round.

This patch regenerates `out/demo_report_data.json` + `out/demo_report.html` and (downstream) `out/dashboard.html`, all of
which are PROTECTED/frozen this wave. **Therefore it is NOT applied here.** Per the plan: prepare, audit, then regenerate.

## Exact next command (DO NOT EXECUTE until Codex approves)

```bash
# After Codex approves the truth-correction + balanced-accuracy patch to pipeline/demo_report.py:
#   1) edit pipeline/demo_report.py: replace the code-switch sentence in kappa_block's caption with the
#      confidence/call-length framing; add balanced_accuracy / youden_j / failure_recall / failure_precision / mcc
#      into the calibration block (values: bal-acc 0.628, J 0.257, recall 0.500, precision 0.308, mcc 0.217).
#   2) .venv/bin/python pipeline/demo_report.py      # regenerate demo_report.{md,html,_data.json}
#   3) .venv/bin/python pipeline/dashboard.py        # regenerate out/dashboard.html
#   4) .venv/bin/python pipeline/preflight.py        # re-gate
# Then re-audit (demo_report_data.json + dashboard.html hashes will change — that is the point).
```

**Coordinator stops here and waits for Codex audit. No integration performed.**
