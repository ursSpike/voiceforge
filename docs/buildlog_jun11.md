# Build log — Jun 11 controlled batch loop

Structured per the leash: objective · inputs · outputs · commands · why-for-demo · discarded · broke · next.
Batches stop for mentor (GPT) review. Schema = constitution; build from files, not vibes.

---

## BATCH 0 — Schema freeze + repo audit · Jun 11 ~18:10 IST

**Objective:** lock the data contracts as machine-checkable JSON Schema (keeping repo names),
audit current state, reconcile GPT's hypothetical names to the repo, before any new building.

**Inputs:** existing `schemas/*.md` (5), `data/normalized/*.json` (11), the ruling yes/+2/yes.

**Outputs:**
- `pipeline/schemas.py` — single source defining 8 JSON Schemas + `validate()` + emitter.
- `schemas/json/*.schema.json` — call_log, task_outcome, scorecard, cost, improvement_example,
  **failure (new)**, call_record (merged dashboard unit), analytics.
- `docs/current_state.md` — repo audit + GPT→repo name-mapping table + the out/calls.json contract.
- `docs/buildlog_jun11.md` — this file.

**Commands:** `pip install jsonschema` (4.26.0) · `python pipeline/schemas.py`.

**Why for demo:** the dashboard, judge, and ingest all read one frozen shape — no field drift,
no UI inventing data. `out/calls.json` (call_record) is the single source of truth. The deterministic
vs judge `type` is baked into the scorecard schema, encoding the "measured-not-vibes" differentiator.

**Result:** 8 schemas emitted; each is a valid JSON Schema (self-checked); **pool validates 11/11
against call_log**. No code renamed, nothing forked.

**Discarded:** GPT's separate `cost_quality`, `failure_clusters.json`, `summary_metrics.json`,
`judge_scores.json`, `data/calls/` — folded into existing artifacts (see mapping table) to avoid
forking the source of truth.

**Broke:** nothing.

**Next:** Batch 1 — ingest the real Bolna execution `246cd9f3` into a `call_record`.

---

## BATCH 1 — Real Bolna ingest · Jun 11 ~18:35 IST

**Objective:** ingest the real Bolna execution `246cd9f3` into a schema-valid `call_log`, with
timing derived honestly from the `/log` (not the scrubbed transcript). Demo-safe: build from a
cached payload, no live API at demo time.

**Inputs:** Bolna API (`/v2/agent/{id}/executions`, `/executions/{id}/log`) → cached once to
`data/provider_logs/bolna_246cd9f3.json`; `schemas.py`, `signals.py`.

**Outputs:**
- `data/provider_logs/bolna_246cd9f3.json` — raw execution + 34-event log (cached; demo-safe).
- `pipeline/ingest_bolna.py` — the Bolna→call_log adapter (turns + timing from `/log` created_at diffs).
- `data/normalized/bolna_246cd9f3.json` — schema-valid call_log (13 turns, `hi-en`).
- `out/provider_ingest_report.json` — deterministic signals + real provider cost on the call.

**Commands:** inspect+cache (one-off API) · `python pipeline/ingest_bolna.py`.

**Why for demo:** "Bolna at the core" is now literally true — a real Bolna call flows through the
SAME deterministic pipeline as SpokenWOZ + the hero call. Pool 11→12. Preflight `Bolna ingested`
check flips to PASS. Timing reconstruction proves we read the conversation trace, not the transcript.

**What the data says (honest):** the call was CLEAN — agent latency median 435ms / p90 656ms, 0
laggy, booking completed → **no failures detected**. That's the correct result and a good contrast
row ("real clean Bolna call" vs the failing hero call).

**Discarded / honest caveats:**
- The top-level transcript (role-prefixed but timing-less, interruption-scrubbed) was NOT used for
  timing — only the `/log` component events. Documented in the call's `metadata.timing_source`.
- Web-call → `telephony_data: None`, no recording URL, no reliable overlap timing → overlap NOT
  computed (signals.py single-timestamp rule), latency only. Honest, not faked.
- This execution **predates the Cartesia voice swap** (its synthesizer = elevenlabs). A fresh
  Cartesia-voiced call would be on-brand; flagged for Spike (see STATUS REPORT).

**Broke:** `/log` returns `{"data":[...], "status":...}` not a bare list — fixed the extractor.

**Next (NOT started — awaiting review):** Batch 2 (SpokenWOZ slice to ~45) then Batch 3 (deterministic
eval core → out/calls.json). STOP here per the leash.

---

## BATCH 1.5 — Repair pass (GPT review fixes) · Jun 11 ~19:10 IST

**Objective:** clear every blocker + warning from GPT's audit before advancing to Batch 2, so the
output contract is solid and the repo is internally consistent.

**Blockers fixed:**
- `call_record.schema.json` was too loose → tightened: now REQUIRES + shape-validates nested
  `outcome`/`scorecard`/`cost`/`failures` (via `_embed`, dropping the implied `call_id`).
  Self-test added: well-formed record PASSES, missing-scorecard correctly REJECTED.
- `failure` schema required `call_id` but signals.py emits context-free failures → made `call_id`
  OPTIONAL (implied when embedded; injected at assembly for the clusters view). Documented.
- `preflight.py scored()` read `dimensions` at call root → fixed to `scorecard.dimensions`
  (matches the call_record contract; future out/calls.json audits correctly now).
- `dpo_export.py` had stray pasted prose after the TODO → restored to a clean valid stub.

**Warnings fixed:**
- `requirements.txt` now lists `jsonschema`.
- Hero provenance reconciled: assembler records the ACTUAL voice (`metadata.voice_provider:
  cartesia`, `agent_voice: cartesia/Devansh`); re-assembled idempotently (same Cartesia clips →
  same 0:15/0:48 timestamps); `data/normalized/hero_001.json` regenerated from turns.json (now
  byte-identical). demo-script + current_state updated to 0:15/0:48; turns.json declared canonical.
- `current_state.md` de-staled (pool 11→12, out/ contents, rubric 8 dims).
- Rubric settled: `conciseness` + `user_frustration` added (8 dims, 3 det + 5 judge, weights sum 1.0;
  judge.py wires the +2 at Batch 4). (Caught+fixed a YAML-spacing typo this introduced.)
- `pipeline/cartesia_tts_smoke.py` (proves the mandatory Cartesia *synthesis* path) committed, not stray.

**Result:** preflight clean (hero/Bolna/pool/cartesia all PASS); pool 12/12 valid; call_record
self-test passes; no untracked files; rubric loads, weights = 1.0.

**Broke:** rubric YAML spacing typo (`key:{` → `key: {`) — caught by the verification run, fixed.

**Next:** Batch 2 + 3 now safe to proceed on a solid contract — awaiting GPT approval.

---
