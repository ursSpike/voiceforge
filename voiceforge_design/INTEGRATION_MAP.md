# VoiceForge — Integration Map

## Files

| File | Role |
|---|---|
| `index.html` | Static shell: nine chapter sections, spine nav, call-sheet and demo-path containers. Contains **no product numbers**. |
| `styles.css` | Full visual system. No external fonts, no imports. |
| `app.js` | All rendering and interaction. Reads only `window.__DATA__`. |
| `design_data.js` | **Byte-identical copy** of `current_frontend/design_data.js` — the unmodified data contract. Swap in the production-generated equivalent at integration time. |

## Data bindings (contract → surface)

| Contract path | Surface |
|---|---|
| `analytics.n_calls`, `analytics.timing_coverage` | Hero stats; Ch.01 pipeline stages 1 & 3; method limits (text-only count) |
| `val.binary`, `val.unsure` | Hero stats; gate chip; Ch.01 stage 4 |
| `judge_run.*` (model, temperature, n_calls, expected/validated_judgments, failures, cache_hits, hashes, binary_rule) | Hero stats; gate chip; Ch.03 lede; Ch.07 "Judge run, pinned" + binary-rule panel |
| `report.manifest_total` | Gate chip; Ch.07 calls judged |
| `report.metric_trap.*` (n, agree, missed_successes, false_passes, human_failures, caption, provenance) | Ch.02 numerals, 45-dot field, caption, footnote |
| `report.calibration.*` (kappa, ci95, raw_agreement, n, band, confusion, disagreements, disagreements_code_switched, caption) | Ch.01 stage 6; Ch.03 κ block, CI strip, confusion matrix, disagreement chips, caption |
| `report.product.matrix.*` | Ch.04 band, quadrant cards, n / unsure-excluded line |
| `report.product.human_success_rate`, `.brittle_share_of_successes`, `.cost_per_human_success_est`, `.friction_or_failure_spend_share`, `.caveat` | Hero stat; Ch.04 aside stats + caveat |
| `report.product.fix_first.*` | Ch.06 spotlight (phenotype, affected_calls, estimated_spend_usd, modeled_exposure_per_1k_usd, recommendation, expected_mechanism, provenance, evidence_call_ids) |
| `report.improvement_queue[]` | Ch.06 queue, grouped by `recommendation`; items open the call sheet when `call_id ∈ rows` |
| `report.archetypes.counts` | Hero "calls phenotyped"; Ch.01 stage 7 |
| `analytics.failure_clusters[]` | Ch.01 deterministic-events bars |
| `sponsor_proof.*` | Ch.07 proof chain (agent_id, cartesia_voice, cartesia_model, fetched_at) |
| `rows[]` (id, source, lang, profile, wf, turns, outcome, overall, dims, failures, transcript, judge, human) | Ch.05 table + filter; call sheet (transcript, blind label, deterministic scorecard, 5 judge dims, binary outcome, failure events, evidence_turn_ids highlighting) |
| `privacy_note` | Ch.05 lede; Ch.08 footnote |

## Behavior preserved from production

- Evidence-turn highlighting via `evidence_turn_ids` → `data-turn` match.
- One-click route from any insight (disagreement, fix-first evidence, queue
  item) to call detail.
- Call filter over id / lang / profile / workflow / source.
- Disabled (dimmed) chips for call IDs whose transcripts are excluded from
  the sanitized package — IDs are never hidden.

## Integration notes

- `app.js` builds a small derived view-model in memory; the data object is
  never mutated.
- Number formatting follows production (`pct`, `money`, weighted `overall`),
  with money precision widened below $0.10.
- If the production generator inlines assets (see
  `dashboard_generator_reference.py`), inline `styles.css` and `app.js` in the
  same order they are referenced here: data → app.
