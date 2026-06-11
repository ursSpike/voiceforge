# VoiceForge — current state (Batch 0 repo audit, Jun 11)

Snapshot of what already exists, so no batch rebuilds or forks what's here. **The repo is the
constitution.** Where GPT's plan used different names, the mapping table reconciles them.

## What exists and works (verified)
| area | files | state |
|---|---|---|
| schemas (specs) | `schemas/*.md` (call_log, task_outcome, scorecard, cost, improvement_example) | authored |
| schemas (machine-checkable) | `schemas/json/*.schema.json` (8, via `pipeline/schemas.py`) | **NEW this batch**; pool validates 12/12 |
| normalize | `pipeline/normalize.py` (spokenwoz + hero adapters) | works |
| deterministic signals | `pipeline/signals.py` (FTO core: barge-in, latency, p50/p90, failure table) | works, notebook-referenced |
| LLM judge | `pipeline/judge.py` (Gemini, temp 0, JSON, {score,reason,evidence_turn_ids}, disk cache) | works (smoke + cache) |
| rubric | `rubric.yaml` (8 dims: 3 deterministic, 5 judge; weights sum 1.0) | live config |
| normalized pool | `data/normalized/*.json` | **12 calls** (hero + 10 SpokenWOZ + 1 real Bolna, Batch 1) |
| public data | `data/spokenwoz/data.json` (246MB, 4700 dialogues, word-level ms) | **already downloaded** — slice, don't re-fetch |
| hero call | `data/hero/hero_001.wav` (Cartesia Devansh) + `turns.json` | failures 0:15 barge-in 800ms / 0:48 gap 1620ms |
| money-shot UI | `web/shot.html` + `web/recorder/serve.py` (stdlib server, :7861) | click-to-seek verified |
| Bolna | agent `199b03e7…` (Cartesia-voiced) + 1 completed execution `246cd9f3…` | ingest target for Batch 1 |
| keys | `.env`: GEMINI ✓, BOLNA ✓, CARTESIA ✓ (all verified) | gitignored |
| plan + checks | `docs/SUBMISSION-PLAN.md`, `pipeline/preflight.py` | the executable checklist |
| learning | `notebooks/` 36 books (P00–P04, 00–30), all gate+review clean | reference the schema field names below |

## Stubs (not yet built — these are the batch targets)
`pipeline/score.py`, `pipeline/costs.py`, `pipeline/crosscut.py`, `pipeline/dpo_export.py`,
`eval/kappa.py` — all `raise SystemExit("TODO …")`. `out/` currently holds only
`provider_ingest_report.json` (Batch 1); `out/calls.json` + `out/analytics.json` arrive in Batch 3.

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
