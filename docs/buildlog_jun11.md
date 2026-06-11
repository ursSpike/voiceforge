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

**Result:** the REPAIRED SUBSET passes (preflight hero/Bolna/pool/cartesia all PASS); pool 12/12
valid; call_record self-test passes; no untracked files; rubric loads, weights = 1.0.
**Honest scope:** global preflight is NOT green — it still shows the expected ~6 FAILs for
not-yet-built batches (out/calls.json, DPO, labels, kappa, analytics, fallback). Those are the
remaining batch targets, not regressions.

**Broke:** rubric YAML spacing typo (`key:{` → `key: {`) — caught by the verification run, fixed.

**Next:** Batch 2 + 3 now safe to proceed on a solid contract — awaiting GPT approval.

---

## BATCH 6A — Research verification + documentation truth sweep · Jun 11 ~21:55 IST

**Objective:** build a cite-card from PRIMARY sources only, with per-paper files + a decision log;
plus a documentation truth sweep. No downloads/APIs/model runs/UI/architecture changes.

**Inputs:** 6 arXiv abstract pages (verified live, not from memory).

**Outputs:**
- `docs/papers/<slug>.md` × 6 — one per paper (full citation, quoted finding, what VoiceForge can
  use, demo/Q&A use, explicit non-claim). Written by 6 parallel verifier agents (one per paper).
- `docs/cite_card.md` — consolidated card, grouped: dataset-dependency / motivation / judge-bias.
- `docs/papers/_decisions.md` — the decision log: what each paper is FOR and why, + hard non-claims.

**Commands:** Workflow (6 agents, WebFetch per paper) → synthesis. **6/6 verified from primary sources.**

**Verified findings (quoted from each abstract):** SpokenWOZ 8 domains/203k turns/5.7k dialogues/249h
(DST 25.65% JGA, SOTA e2e 52.1% completion) · τ-Voice voice agents retain **30–45%** of text capability
(85% text vs 31–51% clean / 26–38% realistic; 79–90% failures agent-behavior) · VoiceAgentBench 6,000+
queries EN+6 Indic, ≤60.6% param-filling EN, sharper Indic degradation · WildSpeech-Bench: a lack of
specialized and comprehensive end-to-end speech-LLM benchmarks (it positions itself as the first such) ·
LLM-judge survey: judge reliability "remains a significant challenge" ·
Justice-or-Prejudice: 12 biases quantified (CALM framework).

**Why for demo:** Q&A armor that's fact-checked. The honesty spine is explicit: SpokenWOZ is a real
DEPENDENCY; the benchmark papers MOTIVATE (don't validate); the judge-bias papers JUSTIFY deterministic-first.

**Documentation truth sweep (corrections, living docs only — historical logs preserved):**
- schema count 8 → **9** (`current_state.md`) · English-"only" → English-**heavy** (hero te-en, Bolna hi-en
  code-switch; `limitations.md`) · judge marked **smoke harness only**, 5-dim = Batch 4 (`current_state.md`)
  · label booth marked complete, human labels pending · `serve.py` docstring fixed ("stdlib only" was false —
  it validates via jsonschema; also now documents `/label` + blind-label role).

**Non-claims locked:** VoiceForge reproduces no paper; no paper justifies its 100ms/800ms thresholds
(those are ours); the motivation papers do not measure VoiceForge's accuracy.

**Broke:** nothing.

**Next (NOT started — awaiting audit):** Batch 8A (one deterministic chart from out/analytics.json),
then Batch 4A (judge machinery, quarantined — no real-call scoring until Spike labels). STOP per the leash.

---

## BATCH 8A — Deterministic business-value chart · Jun 11 ~22:25 IST

**Objective:** one reproducible chart from `out/analytics.json` ONLY (no labels, no judge, no raw
recompute), honest labels, output under `reports/charts/`. No dashboard.

**Inputs:** `out/analytics.json` (Batch 3 output) — `by_stress_profile[]` + `failure_clusters[]`.

**Outputs:** `pipeline/chart.py` + `reports/charts/business_value.png` (3 panels): success rate by
stress profile, est. cost per successful call by stress profile, deterministic failure EVENTS by type.

**Commands:** `python pipeline/chart.py` (run twice → byte-identical, md5 confirmed).

**Why for demo:** the founder magnet — harder calls (pause_heavy) show **lower success (20%) AND
higher cost per success ($0.330)** vs clean (40% / $0.231); latency_gap is the dominant failure
event (183 vs barge_in 107). Reads off `analytics.json`, so it stays in sync with the pipeline.

**Honest labels baked in (per audit ruling):** success = HEURISTIC task completion; cost = ESTIMATED
prototype $; panel 3 says **"failure EVENTS (not failed calls)"**; **sample size n shown on every
stress-profile bar**; title flags DETERMINISTIC (pre-judge).

**Determinism:** fixed bar order (clean→pause_heavy→interruption; clusters by count desc), fixed
colors, no randomness, PNG `Date` metadata stripped → re-run is byte-identical (verified md5 twice).

**Discarded:** no recomputation from raw calls / imaginary fields — reads only analytics fields.

**Broke:** nothing (one headroom tweak so the top bar label cleared the panel title).

**Next (NOT started — awaiting audit):** Batch 4A — judge machinery only, QUARANTINED: implement the
5 semantic dims + JSON/evidence validation + cache + retry + `uncalibrated` provenance + canned
fixture verification; FORBIDDEN until Spike labels: scoring the 46 real calls, writing judge scores
to out/calls.json, showing any judge output, kappa/DPO/dashboard. STOP per the leash.

---

## BATCH 2 — Public dataset slice · Jun 11 ~19:45 IST

**Objective:** expand the normalized pool to ≥40 calls (blind-label calibration needs ≥40), from
the already-on-disk SpokenWOZ — stratified, reproducible, no new download.

**Inputs:** `data/spokenwoz/data.json` (cached), `data/spokenwoz/dev_scan.json`, `pipeline/normalize.py`.

**Outputs:**
- 44 new/updated `data/normalized/swz_*.json` (the `cmd_spokenwoz` quota now scales to k with a
  deterministic top-up when a bucket runs dry).
- `docs/dataset_card.md` — source, CC BY-NC license, fields used/ignored, slice method, honest caveats.

**Commands:** `python pipeline/normalize.py spokenwoz --k 44`; `python pipeline/schemas.py` (validate).

**Why for demo:** the eval/dashboard now spans **46 calls** (44 SpokenWOZ + hero + Bolna), enough
for a real ≥40 blind-label calibration, and stratified so the binary label set has both pass- and
fail-prone calls. "Public dataset support" requirement satisfied with a small slice, not a 246MB grind.

**Result:** pool **46/46 valid** against call_log. Composition: interruption 21, clean 20,
pause_heavy 5. Selection is deterministic (same `--k` → same calls).

**Discarded / honest caveats:** SpokenWOZ is latency-rich, not barge-in-rich (protocol) — documented
in the dataset card; audio corpus not downloaded (word timestamps suffice); only 5 pause_heavy
calls qualified, so the stratification top-up filled from interruption (recorded, not hidden).

**Broke:** nothing.

**Next (NOT started — awaiting review):** Batch 3 — deterministic eval core (task_outcome from
goals + signals + cost → the first real `out/calls.json` validated against the tight call_record
contract, + analytics/failure-clusters). STOP here per the leash.

---

## BATCH 3 — Deterministic eval core · Jun 11 ~20:15 IST

**Objective:** produce the first real `out/calls.json` — every call merged into a validated
`call_record` (task_outcome + deterministic scorecard + cost + failures) — plus `out/analytics.json`
(summary + failure clusters). DETERMINISTIC ONLY; judge dims are Batch 4.

**Inputs:** 46 `data/normalized/*.json`, `signals.py`, `schemas.py`, `rubric.yaml`.

**Outputs:**
- `pipeline/score.py` — the eval core (outcome heuristic, 3 deterministic scorecard dims, cost,
  failures, analytics; `overall` = weighted mean over PRESENT dims, re-normalized).
- `out/calls.json` (46 records) + `out/call_<id>.json` per call + `out/analytics.json` — all
  **validated against the tight call_record / analytics contracts** (0 invalid).

**Commands:** `python pipeline/score.py`.

**Why for demo:** this is the spine the dashboard reads. The contrast story holds on real numbers:
clean calls score high + complete (bolna_246cd9f3 **1.0**, swz_MUL0265 0.82); the interruption call
fails (swz_MUL0035 **0.547**, 6/13 laggy, 4/9 fields captured, 13 failures). Hero: 0.803 with the
1 agent barge-in (800ms) + 1 laggy gap correctly scored. Every dimension carries a reason citing
the actual ms numbers + evidence turn ids. Preflight `scored` now PASS (46 calls, 0 dims missing
reason/evidence); global preflight 6→5 FAIL.

**Numbers:** success_rate 0.37 · avg_overall 0.711 · cost/successful $0.244. Failure clusters:
latency_gap 183, barge_in 107. By profile: interruption 21 (38%), clean 20 (40%), pause_heavy 5 (20%).

**Discarded / honest caveats:**
- `task_outcome` is a transparent HEURISTIC: a field is "captured" if its goal value (or workflow
  keyword) appears in the dialogue text — NOT gold dialogue-state (SpokenWOZ has belief-state
  annotations we deliberately ignore this sprint). So success_rate 0.37 likely UNDERcounts real
  completions (e.g. 16-digit `idnumber`, `reqt` slots rarely match verbatim). Documented; it's
  deterministic + reproducible, and the relative ordering (clean > failing) is the demo point.
- The `barge_in` failure cluster (107) counts BOTH agent and user barge-ins (the `label` field
  distinguishes); only AGENT barge-ins penalize the `barge_in` score. Splitting into separate
  cluster dimensions is a Batch 8 refinement, not a blocker.
- Cost is estimated at $0.005/agent-turn (anchored to Bolna's observed 5.96c/13 turns); the Bolna
  call uses its REAL provider cost. Labeled "estimated, prototype".

**Broke:** left a stray placeholder line in `deterministic_scorecard` while drafting — removed before running.

**Next (NOT started — awaiting review):** Batch 4 (LLM judge: the +2 semantic dims, evidence-cited,
cached, gated behind blind labels) OR Spike's blind labels (Block 4) which the calibration needs.
STOP here per the leash.

---
