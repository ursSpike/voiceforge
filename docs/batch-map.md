# Batch map — canonical reference (what each batch is FOR)

The authoritative answer to "which batch does X." Encodes GPT's two rulings (Jun 11):
1. **The SF/YC product UI is Batch 5 ONLY** — and it does not start until the output contract +
   failure clusters + improvement examples exist on disk. No beautiful cards over mocked/unstable data.
2. **Research is woven into the BUILD (Batches 2–4), verified in Batch 6.** Do not defer research
   ideas to Batch 6 — Batch 6 is verification + citation + mapping, not core implementation.

## The map
| batch | purpose | status | produces | gated by |
|---|---|---|---|---|
| 0 | schema freeze + repo audit | ✅ done | `schemas/json/*`, `pipeline/schemas.py`, current_state | — |
| 1 | real Bolna/provider ingest | ✅ done | `pipeline/ingest_bolna.py`, `data/normalized/bolna_*` | Bolna key |
| 1.5 | repair pass (GPT review) | ✅ done | contract tightening, hero provenance, hygiene | — |
| 2 | **public dataset slice (research impl)** — SpokenWOZ backbone | ✅ done | 44 `swz_*`, `dataset_card.md` | data on disk |
| 3 | **deterministic eval core (research impl)** — lit-inspired measured signals | ✅ done | `score.py`, `out/calls.json` (46), `out/analytics.json` | Batch 2 |
| 4 | **LLM judge (research impl)** — +2 semantic dims, evidence-cited, cached, bias-safeguarded | ⬜ next | judged dims in scorecards, `judge_card.md` | out/calls.json ✓; **calibrated scores gated behind blind labels** |
| — | **Block 4: blind labels (SPIKE)** — ≥40, one binary dim, BEFORE seeing judge output | ⬜ his task | `eval/labels_spike.csv` | label booth (no judge exposure, code-enforced) |
| — | DPO export / improvement examples | ⬜ | `out/queue.jsonl`, improvement_examples | failures (have) + labels |
| — | kappa / calibration | ⬜ | kappa + CI + confusion + 2 disagreements | labels + judge |
| 5 | **SF/YC DASHBOARD UI** | ⬜ **do not start yet** | Overview → Calls → Call Detail → Failure Clusters → Improvement Queue | **needs out/calls.json (✓) + failure clusters (✓) + improvement examples (✗ not yet)** |
| 6A | **research cite-card (VERIFICATION)** | ✅ done | `docs/cite_card.md` + `docs/papers/<slug>.md` ×6 + `_decisions.md` (6/6 verified from primary sources) | papers verified live |
| 7 | demo hardening | ⬜ | slides, screenshots, **fallback recording**, submit | everything above |

## Batch 4 — the judge (next, when approved)
Adds the +2 ruling dims (`conciseness`, `user_frustration`) plus the existing 3 judge dims
(`language_match`, `faithfulness`, `repair_quality`) to each scorecard. Deterministic stays PRIMARY;
judge is semantic interpretation only. Strict JSON, temp 0, disk-cached, every score cites evidence
turn ids. **Bias-safeguard:** calibrated/credible judge scores are NOT presented until blind human
labels exist; until then judge dims are marked "uncalibrated." (LLM-as-judge has documented
bias/reliability issues — arXiv:2411.15594, 2410.02736.)

## Batch 5 — the UI (NOT YET; the most-requested but most-gated)
Starts ONLY after the data spine is real AND improvement examples exist. Reads `out/calls.json` +
`out/analytics.json` ONLY — never invents fields. Restrained SF/YC aesthetic (Linear/Vercel/OpenAI-
evals energy), decision-support not decorative shell, drill-down (answer the next question). Five
screens, nothing else (no auth/billing/teams/settings). Built on the existing local server (no
Next.js, 90-min reliability cap). Missing field → "unknown", never fabricated.
**Current blocker:** improvement examples don't exist yet → the Improvement Queue screen can't be
real. So Batch 5 waits on the improvement/DPO step (which itself waits on labels). Overview/Calls/
Call Detail/Failure Clusters *could* be built on today's `out/`, but per the ruling we hold the
whole UI until its data is complete, to avoid a half-real dashboard.

## Batch 6 — the cite-card (verification, not impl)
Verify each paper live, then map to product / demo-framing / Q&A-armor:
- **SpokenWOZ** (arXiv:2305.13040) — the public backbone (product, Batch 2): spoken task-oriented
  dialogue, ~5.7k dialogues / 203k turns / 249h audio.
- **τ-Voice** — the "why voice evals matter" stat (~30–45% of text capability retained).
- **VoiceAgentBench** (arXiv:2510.07978) — multilingual/Indic agentic-voice framing (Q&A armor).
- **WildSpeech-Bench** — real-world speech-LLM eval need (Q&A).
- **LLM-as-judge bias** (2411.15594 / 2410.02736) — justifies deterministic-primary stance (Batch 4).

## Where we are (Jun 11 ~22:10)
Batches 0–3 done; `out/calls.json` (46 validated records) + analytics exist. **Blind-label booth v2
(phenotype) COMPLETE** — human labels pending (Spike's task, 0/46). **Batch 6A (cite-card) DONE.**
Next per audit-master plan: **Batch 8A** (one deterministic chart from analytics) → **Batch 4A**
(judge machinery, quarantined — no real-call scoring until labels). UI (Batch 5) held until its data
(incl. improvement examples) is complete.
