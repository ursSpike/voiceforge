# VoiceForge — current state (living doc; updated through Batch 3 + label booth, Jun 11)

Snapshot of what already exists, so no batch rebuilds or forks what's here. **The repo is the
constitution.** Where GPT's plan used different names, the mapping table reconciles them.

> **Canonical batch reference: [docs/batch-map.md](batch-map.md)** — what each batch is FOR, status,
> and gating. Key rulings: the SF/YC product **UI is Batch 5 only** (gated on real out/calls.json +
> clusters + improvement examples); **research is woven into Batches 2–4** (impl) and **verified in
> Batch 6** (cite-card) — research ideas are NOT deferred to Batch 6.

## What exists and works (verified)
| area | files | state |
|---|---|---|
| schemas (specs) | `schemas/*.md` (call_log, task_outcome, scorecard, cost, improvement_example) | authored |
| schemas (machine-checkable) | `schemas/json/*.schema.json` (**9**, via `pipeline/schemas.py`) | pool validates **76/76** (incl. nullable-timing invariant) |
| normalize | `pipeline/normalize.py` (spokenwoz + hero) + `pipeline/ingest_cmd.py` (Code-Mixed-Dialog hi-en) + `pipeline/ingest_bolna.py` | works |
| deterministic signals | `pipeline/signals.py` (FTO core: barge-in, latency, p50/p90, failure table) | works, notebook-referenced |
| LLM judge | `pipeline/judge.py` (Gemini, temp 0, JSON, {score,reason,evidence_turn_ids}, disk cache) | **5-dim judge RUN COMPLETE** — all 46 manifest calls judged (gemini-3.1-flash-lite, 276 judgments, 0 failures), validate-before-cache; out/judge_results.json |
| label booth | `web/label.html` + `/label*` routes | **labeling COMPLETE** — 46/46 labeled (45 binary 37/8, 1 unsure), CSV frozen b3884f9e…, snapshot pinned d592782a…, manifest aec4ba49… |
| rubric | `rubric.yaml` (8 dims: 3 deterministic, 5 judge; weights sum 1.0) | live config |
| normalized pool | `data/normalized/*.json` | **76 calls** (44 SpokenWOZ + hero + Bolna + 30 Code-Mixed-Dialog hi-en) — label slice = 46-call frozen manifest |
| eval core | `pipeline/score.py` → `out/calls.json` (76 call_records) + `out/analytics.json` (timing_coverage 46 timed/30 unmeasured) | **DONE**; 76/76 valid |
| public data | `data/spokenwoz/data.json` (246MB, 4700 dialogues, word-level ms) | **already downloaded** — slice, don't re-fetch |
| hero call | `data/hero/hero_001.wav` (Cartesia Devansh) + `turns.json` | failures 0:15 barge-in 800ms / 0:48 gap 1620ms |
| money-shot UI + booths | `web/shot.html` + `web/recorder/serve.py` (local server :7861; validates labels via jsonschema, so not pure-stdlib) | click-to-seek verified |
| Bolna | agent `199b03e7…` with **Cartesia inside its synthesizer** (provider=cartesia/Devansh/sonic-3) + 1 completed execution `246cd9f3…` (predates that Cartesia config) | ingested (`data/normalized/bolna_246cd9f3.json`) |
| keys | required: `.env` GEMINI ✓, BOLNA ✓. Cartesia runs inside Bolna → **no separate Cartesia key needed**; CARTESIA_API_KEY is optional/historical (direct-TTS reproduction utilities only) | gitignored |
| plan + checks | `docs/SUBMISSION-PLAN.md`, `pipeline/preflight.py` | the executable checklist |
| learning | `notebooks/` 36 books (P00–P04, 00–30), all gate+review clean | reference the schema field names below |

## Stubs (not yet built — these are the batch targets)
`pipeline/dpo_export.py` (needs labels), `eval/kappa.py` (needs labels) — `raise SystemExit`.
`pipeline/costs.py` + `pipeline/crosscut.py` are **absorbed into `score.py`** (cost = `build_cost()`,
analytics/clusters = `build_analytics()`); their stubs now just point to `score.py` as the canonical
eval-core entrypoint. Chart *images* (from analytics) are Batch 8.
`out/` holds: `calls.json` (76 records) + per-call jsons + `analytics.json` + `judge_results.json` (real judged run) + `demo_report.{md,html,_data.json}` (κ 0.206 calibration + metric-trap) + `dashboard.html` (the demo surface) + `bolna_cartesia_proof.json` (sponsor proof).

## Name-mapping table (GPT plan's names → repo constitution)
| GPT plan name | repo (canonical) | note |
|---|---|---|
| `outcome.schema.json` | `task_outcome` | same concept |
| `eval_scorecard.schema.json` | `scorecard` | same concept |
| `cost_quality.schema.json` | `cost` (per-call) + `analytics` (aggregate) | split: per-call cost vs cost-per-success cross-cut. No separate cost_quality file. |
| `failure.schema.json` | `failure` | **added this batch** (genuinely needed for clusters) |
| `improvement.schema.json` | `improvement_example` | same concept |
| `data/calls/` | `data/normalized/` | canonical normalized-call dir; do NOT fork |
| `out/judge_scores.json` | merged into `out/calls.json` per-call `scorecard` | one source of truth |
| `out/failure_clusters.json` | `out/analytics.json` → `failure_clusters[]` | folded into analytics |
| `out/summary_metrics.json` | `out/analytics.json` | folded |
| `docs/buildlog_jun11.md` | same | structured per GPT format |

## Output contract (the ONLY thing the dashboard reads)
`out/calls.json` = array of `call_record` (schemas/json/call_record.schema.json): each is a
`call_log` + nested `outcome` + `scorecard` + `cost` + `failures[]` + `signals` summary.
`out/analytics.json` = `analytics` schema (success rate, cost-per-success, by-stress-profile,
failure_clusters). Dashboard shows real fields or "unknown" — never fabricated values.

## Judge dimensions (ruling: yes / +2 / yes)
Deterministic (signals.py, never judged): `barge_in`, `latency_gap`, `task_completion`.
Judge (semantic only): `language_match`, `faithfulness`, `repair_quality`, **+ `conciseness`,
`user_frustration`** (the +2). **Now settled in `rubric.yaml`: 8 dims (3 deterministic + 5 judge),
weights sum to 1.00.** `judge.py` wires the two new judge dims at Batch 4; until then they're
declared config. Timing/interruption/silence/turn-count/slots stay measured — that's the differentiator.

## Hero provenance (single source of truth)
`data/hero/turns.json` is canonical (the `/shot` page reads it live). After the Cartesia re-voice:
voice = **Cartesia Devansh** (`metadata.voice_provider: cartesia`), failures **0:15 barge-in 800ms /
0:48 latency 1,620ms**. `data/normalized/hero_001.json` is regenerated from it (now byte-identical
turns). `timeline.json` keeps `agent_voice` (edge-tts) only as the documented fallback; the active
voice is the `cartesia` block. Historical buildlog/RESUME entries may quote pre-re-voice numbers
(0:18/0:53, 0:14/0:41) as dated records — turns.json is the live truth.
