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

## BATCH 4A — Judge machinery (QUARANTINED) · Jun 11 ~22:45 IST

**Objective:** the 5-semantic-dim judge, fully implemented + verified, WITHOUT touching the 46 real
calls (they're what Spike labels blind; judging them now would risk leaking judge output → void calibration).

**Inputs:** `pipeline/judge.py` (Block-0 client+cache), `rubric.yaml` (the 5 judge dims).

**Outputs (machinery only):** `pipeline/judge.py` extended —
- 5 SEMANTIC dims: language_match, faithfulness, repair_quality, conciseness, user_frustration
  (timing/overlap/slots stay DETERMINISTIC in score.py, never judged here).
- `build_prompt` per dim; `_generate_json` with **retry on transient errors only** (rate-limit/5xx/
  network; malformed JSON + auth surface immediately); disk cache unchanged.
- `validate_dim`: strict shape (score∈0..1, reason, evidence list) + **evidence-turn validation** —
  ids not in the call are DROPPED and flagged `evidence_dropped` (hallucinated-turn guard); every
  dim marked **`provenance: "uncalibrated"`** (no kappa yet).
- `FIXTURE`: a canned SYNTHETIC call (not from data/normalized). `--selftest` (offline, mock
  responses) + `--fixture` (live Gemini on the fixture).

**Commands:** `judge.py --selftest` (offline ✓), `judge.py --fixture` (5 dims, live, cached).

**Verification:** offline selftest passes (good→uncalibrated; hallucinated `t99` dropped+flagged;
missing-score & out-of-range rejected). Live fixture: 5/5 dims, all uncalibrated, all evidence valid.
**`out/calls.json` md5 byte-identical before/after; judge cache holds only fixture_4a + smoke_001 —
NO real call judged.**

**Quarantine honored (forbidden, NOT done):** no scoring of the 46 real calls, no write to
out/calls.json, no real-call judge output/aggregate/distribution exposed, no kappa/DPO/dashboard/
calibration claim. Lifts only when Spike's blind labels exist.

**Broke:** nothing.

### 4A repair (GPT review) · Jun 12 ~00:05 IST
Four real defects fixed before any real-call judging:
- **Cache poisoning** — `judge_dimension` now VALIDATES BEFORE caching; an invalid response raises
  and is never persisted (verified: a `score:1.7` response raises + leaves no cache file).
- **Strict validation** — `validate_dim` now rejects boolean scores, non-numbers, out-of-range,
  non-string/empty reason, non-list/non-string evidence, and the all-evidence-dropped case; dedupes
  evidence; requires ≥1 valid unique evidence id.
- **rubric is the source of truth** — `_check_rubric_dims()` asserts JUDGE_DIMS == rubric's judge
  dims at startup (fails loudly on drift).
- **Comprehensive self-test** — a mock client now covers cache-hit, no-poison-cache, transient
  retry count, permanent no-retry, malformed-JSON no-retry, and all bad-shape rejections (offline).
- Warning: cache key now includes **temperature** (was omitted). All re-verified; out/calls.json
  still byte-untouched; cache holds only fixture_4a.

**Next:** the quarantine lifts after **Spike labels ≥40 at /label**. Then: judge the real calls →
merge into out/calls.json → kappa (judge vs blind labels) → DPO → Batch 5 dashboard. All held.

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

## Booth-v2.1 — one-pass hierarchy clarification (Jun 12, audit-master spec)
**Goal:** make the labeling booth explicitly ONE-PASS + hierarchical (Spike read "Stage 2 optional"
as "come back later / listen to audio later"). Wording + UX gate only — **no schema, allowlist,
blindness, CSV-format, or judge-quarantine change.**

**Changed (5 files, +97/-12 — 3 code/config + this buildlog + phenotype-plan; an earlier draft of this
entry undercounted as "3 files / +46-12" by tallying only the code files):**
- `web/label.html` — Level 1/2/3 explainer at top (outcome → primitives → derived-not-labeled);
  scope warning (transcript-only: don't infer audio/accent/noise/network/naturalness — *unavailable for
  nearly all calls*; don't hand-label latency/overlap — only THOSE two are computed deterministically elsewhere);
  tag headings → "What was good? / What went wrong? / Context present? — Select all that apply.";
  coexistence hint; **mandatory review checkbox** ("I reviewed all three phenotype groups; zero tags
  means none applied") — Save disabled until outcome+confidence+review all set; on reopen, labels
  restore but checkbox resets (reconfirmation required, nothing lost). Keyboard Enter + save() guard
  + double-submit guard all now also require `reviewed`.
- `web/recorder/serve.py` — one line: `LABELS_CSV` honors `VOICEFORGE_LABELS_CSV` env (default path
  UNCHANGED) so verification writes to a throwaway file, never the real CSV.
- `.claude/launch.json` — added `booth-test` config (env-wrapped) for isolated browser testing.

**Verified in a real browser (preview, test server on throwaway /tmp CSV), all 10 audit checks:**
1 save disabled w/o outcome (stage-2 hidden) · 2 disabled w/o confidence · 3 disabled w/o review-confirm ·
4 positive+negative selectable together (clear_and_concise + language_mismatch) · 5 zero tags saves
after confirm · 6 mixed tags persist through CSV + fully restore on reopen, review resets · 7 forced
500 shows retryable error + does NOT advance + persists nothing · 8 `unsure` saved → usable count
held (2 usable / 3 total) · 9 blind API serves only language/ref/turns/workflow_type (+turn_id/speaker/
text), no leaks · 10 real `eval/labels_spike.csv` ABSENT after testing (3 test rows went to /tmp).
CSV format byte-shape unchanged (same 8 columns). Level 3 NOT hand-labeled (documented as deterministic
derivation post-label).

**Next (STOP — awaiting audit-master sign-off, then Spike labels):** on "go", start the real-CSV
server (`booth` config) and Spike labels ≥40 at /label. Judge quarantine stays active until labels exist.

---

## Labeling workspace layout — light split view (Jun 12)
**Goal:** make one-pass annotation comfortable on a laptop before real labeling starts: transcript and
controls visible side by side, every phenotype group in one controls panel, explicit Previous / Save &
next navigation, and a clear completion state.

**Changed:**
- `web/label.html` only — light theme; fixed-height two-panel desktop workspace; annotation controls on
  the left; scrollable call transcript on the right; Level 1/2/3 + transcript-only guidance directly
  below the call; persistent bottom navigation with Previous at left and Save & next at right.
- All outcome, confidence, positive, negative, context, note, and review controls are visible in the
  same annotation panel (no hidden Stage 2). Save still requires outcome + confidence + deliberate
  phenotype-review confirmation.
- Previous preserves the current unsaved draft in memory. Saved annotations still restore every tag,
  confidence, and note while resetting review confirmation.
- Resume behavior keeps the canonical server order and opens the first unlabeled call. A 45/46 session
  resumes at Call 46 of 46; saving it immediately shows the completion screen.

**Verified against an isolated temporary CSV (real `eval/labels_spike.csv` remained absent):**
- Light split layout visually inspected at desktop size; transcript and label panels scroll independently.
- Positive + negative tags coexist; Save gating unchanged; Save & next advances and persists.
- Previous returns to the prior saved call and the unsaved next-call draft survives the round trip.
- A generated 45-label test state resumed at Call 46 of 46 with Previous enabled and Complete labeling
  gated until required fields were set; final save rendered "All 46 calls reviewed."
- `pipeline/schemas.py`: 46/46 normalized calls valid; call_record self-test passed.

**Contracts unchanged:** no schema, tag allowlist, CSV format, blindness route, judge output, or normalized
data change. Judge quarantine remains active.

---

## FDE-facing phenotype taxonomy (Jun 12)
**Goal:** replace the research-heavy annotation vocabulary with a smaller operational checklist that
delivery, support, and field-deployment teams can understand without learning VoiceForge internals.
The taxonomy stays provider-neutral while covering multilingual onboarding and local-workforce calls.

**Changed:**
- Reduced Level-2 primitives from 24 to **18**: 6 "worked well", 8 "needs fixing", 4 context.
- UI shows plain labels such as **Adapted language well**, **Wrong language or tone**,
  **Repeated or got stuck**, and **Workflow or tool failed**. CSV/schema retain stable snake-case ids.
- `pipeline/schemas.py` remains the source of truth for ids and display labels; `/label/tags` serves both,
  so the client does not duplicate taxonomy text.
- Regenerated `schemas/json/phenotype_label.schema.json`; no real label migration was required because
  `eval/labels_spike.csv` did not exist.

**Scope boundary:** this booth remains transcript-only. Spoken-word intelligibility, pronunciation,
accent fit, voice naturalness, noise, and microphone quality require an audio-enabled review surface
and are intentionally reserved for post-hackathon extension. Current labels describe only evidence
visible in the transcript.

**Verified with an isolated CSV:**
- All 18 human-readable labels rendered in the light split workspace.
- A mixed multilingual annotation saved the ids `adapted_language_well`,
  `wrong_language_or_tone`, and `mixed_languages`.
- An obsolete tag (`clear_and_concise`) was rejected with HTTP 400 by schema validation.
- `pipeline/schemas.py`: 9 schemas emitted, 46/46 normalized calls valid, call_record self-test passed.

**Rendering follow-up:** unselected tags now carry visible category tints (green strengths, red issues,
blue context) with solid selected states. The client also falls back to readable id text when connected
to a stale booth process that lacks the display-label map, preventing a blank left panel; restarting
the booth is still required to load the current FDE taxonomy and schema.

## BATCH 2R · Phase A — Calibration-slice source audit (Jun 12) · AUDIT ONLY
**Objective:** the label pool is 44 monolingual-English SpokenWOZ calls (turn median ≈36, max 60) — long + mismatched
with the multilingual thesis. Audit public sources for a SHORT, multilingual, goal-oriented 40-call slice. No ingest,
no normalization, no schema/label change. Full table in `docs/batch2R_source_audit.md`.

**Integrity:** `eval/labels_spike.csv` SHA-256 unchanged (`e6d2055…b4eb0`); 2 labels preserved (bolna→success, hero→success);
booth stopped; `data/normalized/` 46 calls untouched.

**Verified (primary sources):**
- **Code-Mixed-Dialog** (github.com/sumanbanerjee1/Code-Mixed-Dialog @ `9df1d4dc`, COLING 2018 Banerjee et al.):
  Hindi/Bengali/Gujarati/Tamil-English, DSTC2 restaurant, human-TRANSLATED, **text-only/no timestamps**. **NO Telugu**
  (confirmed 3 ways: paper, repo `data/` dirs, agent). License = **Apache-2.0** (repo LICENSE/SPDX) — the "CC BY 4.0" is the
  arXiv PAPER badge, not the dataset → resolved: ingest under Apache-2.0.
- Hindi-English dev split = 500 dialogues; **real conversational turns median 8 / p90 11 / max 18; 99% ≤16, 100% ≤20** — ideal.
- **Telugu-English hunt (parallel agent):** NO licensed public Telugu-English restaurant/service TOD exists. Only Telugu-English
  TOD = **Code-Mixed-TOD-Medical** (suman101112, CC BY-NC 4.0, MEDICAL domain). Tamil≠Telugu (won't substitute). Hero call
  (`te-en`) already gives Telugu representation in the slice.

**Failures/blocks:** initial `gh api …?per_page=1` zsh-globbed (no matches) — re-ran with `branches/master` for the SHA.
Telugu medical paper paywalled (Elsevier) but the CC BY-NC GitHub data is readable.

**Ruling needed (per plan "stop if Telugu unverified"):** (A) drop dataset-Telugu, reallocate to 24 Hindi-English + 14 SpokenWOZ
controls + 2 existing = 40 (Telugu via hero) — RECOMMENDED; or (B) add 8 Telugu-English medical (CC BY-NC) → 16 Hindi + 8 Tel-med
+ 14 En + 2 = 40.

**Next:** STOP for Codex audit. On approval + Telugu ruling → honest ingest of Hindi-English (Apache-2.0; `timing_observed:false`,
`stress_profile:unmeasured`, heuristic outcomes) + immutable `eval/label_manifest.json` (entries 1–2 = bolna/hero). No booth restart yet.

## BATCH 2R · Phase A repair + nullable-timing contract (Jun 12) — Codex blockers
**Codex verdict on the audit:** PASS w/ 3 blockers. Repaired all; still NO ingest, labels frozen.

**Warnings fixed (docs/batch2R_source_audit.md):** "no Telugu dataset exists" → "none found in this audit"; softened
Apache-2.0 (stock LICENSE has unfilled copyright template — no "commercial-safe" claim); disclosed the sample change as a
usability/language correction made BEFORE any judge exposure (judge quarantine still active, 2 labels frozen).

**Blocker 1 — turn-count corrected.** VoiceForge counts each *utterance* as a turn; my Phase-A median 8 counted *exchanges*
(~2× undercount). Recomputed Hindi-English dev (500 dialogues): **median 15 / p90 21 / max 35** (matches Codex), ~85–88% ≤20
turns, 423+ candidates ≤20. Selection filters on the adapter's exact per-utterance count ≤20.

**Blocker 2 — Option A ruled.** Medical Telugu (correct repo `suman101112/Code-Mixed-TOD-Medical-Dataset`) DROPPED — medical
domain + CC BY-NC, not pursued. Slice = 2 existing + 24 Hindi-English (≤20 turns, no parallel dups) + 14 SpokenWOZ controls;
Telugu via the `te-en` hero call. Fixed the misaligned/missing turn-length cell in the table.

**Blocker 3 — nullable-timing contract BUILT + TESTED (no synthetic timestamps):**
- `schemas.py`: turn `start_ms` → `["integer","null"]`; `stress_profile` += `unmeasured`; `source` += `code_mixed_dialog`;
  cost `duration_s` → `["number","null"]`; new self-test (null record validates, non-int start_ms rejected).
- `signals.py`: `turn_metrics` drops untimed turns → all-untimed call = no events/barge-ins/failures, latency None.
- `score.py`: barge_in + latency_gap emitted ONLY when timing observed (else omitted, never faked 1.0); `overall`
  re-normalizes over present dims; `cost.duration_s` null when no clock.
- `pipeline/test_nullable_timing.py` (new, committed): untimed → {task_completion} only, duration null, no failures;
  timed → all 3 dims + real duration. PASS.
- **Proof real pool untouched:** `schemas.py` pool 46/46 valid; `score.py` re-run → `out/calls.json`+`out/analytics.json`
  BYTE-IDENTICAL (hash `9e68bab5…`, git shows no out/ diff). `eval/labels_spike.csv` SHA unchanged; normalized still 46.

**Next:** STOP for Codex re-audit. On clear → Phase B: `code_mixed_dialog` ingest adapter + immutable `eval/label_manifest.json`
(entries 1–2 = bolna/hero). No ingest / no booth restart until re-audit clears.

## BATCH 2R · nullable-timing repair round 2 (Jun 12) — Codex 4 blockers
Still NO ingest, labels frozen (SHA e6d2055), pool 46, booth down. All four fixed + tested.

**B1 false-adjacency / partial-timing.** `signals.turn_metrics` previously filtered untimed turns then joined the
remainder → a fake `t1→t3` gap across an untimed `t2`; `score.py` used `any(start_ms)` so a partial call wrongly got both
timing dims. Fix: `signals.timing_mode()` (timed / unmeasured / mixed) is the single invariant; `turn_metrics` computes events
ONLY for a fully-timed call (no join across gaps); `score.py` grants timing dims only when `timing_mode=='timed'`.
**B2 boundary.** `normalize.validate_call` now accepts all-timed AND all-null calls, REJECTS mixed, and couples all-null ⇔
`stress_profile:'unmeasured'`. **B3 docs.** `schemas/call_log.md` (source/profile/nullable start_ms + all-or-none) and
`schemas/cost.md` (duration_s int|null) de-staled. **B4 analytics/chart.** `analytics` gains `timing_coverage{timed,unmeasured}`
and `avg_overall` is over TIMED calls only (timed=3 dims vs unmeasured=task_completion only — never blended); `chart.py` is
null-safe (`_safe_max` ignores null cost; unmeasured-no-success profile → "n/a" bar) and refactored importable.

**Tests** (`pipeline/test_nullable_timing.py`, extended): untimed / timed / **mixed-rejected + no false adjacency** / profile
coupling / coverage-aware analytics / chart null-cost render — all PASS. Warning fixed: Hindi ≤20 count marked a pre-adapter
estimate (final from the adapter). **Proof real pool untouched:** pool 46/46 valid; `out/calls.json` + chart PNG BYTE-IDENTICAL;
`out/analytics.json` changes only by the additive `timing_coverage`; CSV SHA unchanged; normalized 46.

**Next:** STOP for Codex re-audit. On clear → Phase B ingest + immutable `eval/label_manifest.json`. No ingest/booth restart until clear.

## BATCH 2R · nullable-timing repair round 3 (Jun 12) — Codex 3 schema blockers
Closed the gap between the Python enforcement and the SCHEMA CONSTITUTION. Still NO ingest, labels frozen, pool 46.

**B1 — schema now encodes the timing/profile invariant.** `_TIMING_INVARIANT` (a `oneOf`) added to `call_log` AND `call_record`
via `allOf`: branch (a) every `start_ms` integer + measured `stress_profile`; branch (b) every `start_ms`/`end_ms` null +
`stress_profile=='unmeasured'`. A mixed/partial clock matches NEITHER → rejected by JSON Schema itself; also couples all-null↔unmeasured.
**B2 — `build_record()` refuses mixed.** Raises `ValueError` on `timing_mode=='mixed'` before scoring; `score.py` main loop now
builds inside the try so a bad call is counted, never crashes or silently scored. **B3 — `timing_coverage` defined + required in
`ANALYTICS`** (`{timed,unmeasured}` non-negative ints, `additionalProperties:false`) — string/negative/missing counts now rejected.

**Tests:** `schemas.py` self-tests gained mixed-`call_log` rejection, all-null+wrong-profile rejection, malformed-`timing_coverage`
rejection (all fire). `test_nullable_timing.py` gained JSON-Schema mixed rejection + `build_record` refusal + analytics malformed-coverage
rejection; chart test now uses an auto-cleaned `tempfile` dir. ALL PASS. Pool 46/46 still valid against the new invariant.
**Real pool untouched:** `out/calls.json` + `out/analytics.json` BYTE-IDENTICAL; CSV SHA e6d2055 frozen; normalized 46.
(Note re Codex warning: last round's `analytics.json` note text DID change alongside the added field — intentional, documents the
timed-only `avg_overall` scope.)

**Next:** STOP for Codex re-audit. On clear → Phase B ingest + immutable `eval/label_manifest.json`.

## BATCH 2R · nullable-timing repair round 4 (Jun 12) — Codex end_ms blocker
Final contract-consistency fix. Still NO ingest, labels frozen, pool 46.

**Blocker:** `end_ms` was not in the turn's `required`, so a turn with the key ABSENT (vs present-null) passed `call_log`
validation + `validate_call`, then KeyError'd in `build_cost`. Fix: `end_ms` added to call_log turn `required` (present, may be
null — "absent" is never valid); `normalize.validate_call` asserts the key present for every turn; `build_cost` uses
`last.get("end_ms")`/`get("start_ms")` defensively. Fixed the schemas.py self-test `sample` (its turn omitted end_ms).
Test added: a turn missing `end_ms` is rejected by JSON Schema AND by `validate_call` (before scoring).

**Verify:** schemas.py self-tests all pass (exit 0), pool 46/46 valid, full nullable suite PASS; `out/calls.json`+`out/analytics.json`
BYTE-IDENTICAL; CSV SHA e6d2055 frozen; normalized 46. (Codex warning acknowledged: `timed+unmeasured==n_calls` is guaranteed by
`build_analytics`, not the schema — acceptable.)

**Next:** STOP for Codex re-audit. On clear → Phase B ingest + immutable `eval/label_manifest.json`.

## BATCH 2R · Phase B — Code-Mixed-Dialog ingest + immutable manifest (Jun 12) — Codex CLEARED
Booth NOT restarted yet (per protocol). Labels frozen (e6d2055), 44 swz_ intact, existing 46 outputs byte-identical.

**Ingest** (`pipeline/ingest_cmd.py`): cached Hindi dev split @9df1d4dc (`data/code_mixed_dialog/`, Apache-2.0, committed for
reproducible/offline ingest) → **24** `cmd_hi_*` call_logs. bAbI parse keeps only real user/agent NL utterances (skips `<SILENCE>`,
`api_call` actions, `R_` KB rows), merges same-speaker, filters 4≤turns≤20 (got 7–17, median 11), dedups by transcript, deterministic
file order. All timing **null**, `stress_profile:unmeasured`, `source:code_mixed_dialog`, `hi-en`, full provenance; each
`validate_call()`'d before write. **Heuristic outcome:** `restaurant_reservation` added to `WORKFLOW_FIELDS` (cuisine/area/price/contact)
— new calls only (20/24 completed); existing 46 untouched.

**Manifest** (`pipeline/build_manifest.py` → `eval/label_manifest.json`, immutable + idempotent): 40 = 2 frozen (bolna,hero) + 24 cmd +
14 shortest swz controls (20–32 turns). Booth (`serve.py label_order`) now reads the manifest, **fails loudly on dup/missing**, serves in
manifest order, resumes at ref 2 = cmd_hi_0000, UI "Call N of 40", blind-strip intact.

**Verify:** pool 70/70 call_log-valid (24 unmeasured against the timing invariant); existing 46 per-call outputs byte-identical;
analytics `timing_coverage{timed:46,unmeasured:24}`; nullable suite PASS; manifest idempotent; dup/missing rejected; CSV SHA frozen.
**Open (flagged for audit):** 40 calls vs ≥40-binary floor = zero unsure-slack; recommend bumping controls to 20 → 46 (one-line). No
judge calls; source fetch was one cached GitHub-raw text pull at the pinned SHA.

**Next:** STOP for Codex audit of the new pool + manifest (+ slack ruling). No booth restart until clear.

## BATCH 2R · Phase B repair — 46-call manifest + warning fixes (Jun 12) — Codex slack ruling
Codex chose 6 SHORT Hinglish reserves over longer English controls (those run 32–36 turns, off-thesis). Booth still NOT restarted.

**Blocker (slack):** ingest --n 30 → 30 cmd_hi_* (first 24 BYTE-IDENTICAL, 6 appended cmd_hi_0026..0031, all ≤20 turns, span 7–19).
build_manifest N_CMD=30 → eval/label_manifest.json = 2 frozen + 30 cmd + 14 swz = **46**; frozen prefix + first 24 cmd order preserved.
**Manifest FROZEN, SHA-256 aec4ba49000c9f4fdfa203cfca4bc787b71004abb47e4a7eff899175446cae33** (idempotent).
**Warnings:** (1) .gitattributes `data/code_mixed_dialog/** -whitespace` (git diff --check clean, data stays byte-faithful);
(2) cached upstream Apache-2.0 LICENSE at data/code_mixed_dialog/LICENSE; (3) serve.py /label/calls comments → "manifest-ordered".
Confirmed canonical repo (toplevel /Users/varsh/voiceforge), booth launches from here.

**Verify:** pool 76/76 valid; existing 70 per-call outputs byte-identical; timing_coverage{timed:46,unmeasured:30}; nullable suite PASS;
manifest idempotent + dup/missing rejected + resumes ref2=cmd_hi_0000; CSV e6d2055 frozen; 44 swz intact.

**Next:** STOP for Codex audit of the 46-call pool + frozen manifest. On clear → restart booth from /Users/varsh/voiceforge.

## BATCH A — Labeling readiness + data safety (Jun 12 ~18:00) · FINAL EXECUTION PLAN
**Status at start:** HEAD 594698e · manifest aec4ba49 (46 = 2+30+14) · CSV e6d2055 (2 binary, 0 unsure) ·
pool 76 scored, timing_coverage{timed:46,unmeasured:30} · booth DOWN · judge cache = fixture_4a only (quarantine intact) ·
preflight 4 FAIL (the gated back-half) / 2 WARN.

**Built `pipeline/validate_labels.py`** (read-only; writes out/label_validation.json): exact column set/order ·
call_id uniqueness · membership in the FROZEN manifest + manifest-SHA check (aec4ba49) · primary/confidence/tag
allowlists from schemas.py · csv-quoting integrity · binary-vs-unsure counts vs the ≥40 floor · the two frozen
annotations preserved exactly (bolna+hero success/high). Absent CSV = valid empty state. Exit 0/1 for scripting.
Verified: 9/9 checks green on the real CSV; 5 negative tests (bad enum, unknown tag, non-manifest call, frozen-label
drift, duplicate row) each correctly rejected via temp byte-level injections; real CSV restored byte-exact.

**INCIDENT (disclosed): line-ending corruption + recovery.** My first negative-test harness used Path.read_text()/
write_text(), which normalized the CSV's CRLF terminators (csv module default) to LF — content identical, bytes not
(SHA drifted to e2479e3f). Caught immediately by the post-test hash check; reconstructed LF→CRLF (notes empty → unambiguous),
verified the reconstruction matched the frozen e6d2055 BEFORE writing, restored. Harness rewritten to read_bytes/write_bytes.
Rule adopted: all label-CSV handling is BYTES-only.

**Booth NOT restarted** (waits for Codex clearing Batch A). Manifest untouched. Next: Batch B (report engine, fixture-only).

## BATCH B+C — Report engine (fixture-tested) + static demo shell (Jun 12 ~18:40)
**`pipeline/demo_report.py`** → out/demo_report.md + .html (self-contained static page, no JS deps/no network — survives
server death) + _data.json. Reads GENERATED artifacts only (analytics, calls, labels CSV, frozen manifest, and
out/judge_results.json when Batch E produces it — contract documented in the module docstring). HONESTY ENFORCED:
calibration (raw agreement/confusion/kappa+bootstrap CI) renders ONLY at ≥40 binary + judged run, else explicit
"PENDING CALIBRATION"; tags labeled single-rater exploratory; archetypes DERIVED deterministically (documented precedence:
workflow > language > intent/slot > repair-loop; success: seamless/brittle/recovered; unsure → ambiguous) never hand-labeled;
"failure EVENTS not failed calls"; costs "estimated, prototype"; task completion "heuristic"; judge provenance carried.
Representative calls = algorithmic first-per-archetype in manifest order (no cherry-picking); improvement queue =
evidence-backed (negative tags → documented template recommendations, marked template-derived).
**Fixture selftest 15/15**: no-labels → all pending/nothing invented · sub-floor → still pending, tags/archetypes correct ·
floor+judge fixtures → agreement 0.9 exact, kappa inside its CI, html renders, byte-deterministic output.
**Real render** = honest gated state (2 labels, calibration PENDING). CSV untouched (e6d2055).
Batch C satisfied by the same artifact: light-theme single page in the demo presentation order (thesis/corpus →
deterministic signals → calibration → phenotypes → clusters → representatives/queue), pending sections show gated state.

## BATCH D — Demo + submission materials (Jun 12 ~19:00)
**docs/README_DEMO.md**: launch commands (canonical repo), deterministic regen commands, 4-level offline fallback
(static html → recording → screenshots → md+png), screenshot checklist (deferred to Batch H so shots show REAL numbers),
architecture diagram, volunteer-first limitations, known-good state + gates. **docs/demo_script.md**: 7–8 min script with
⟨slots⟩ for real numbers (rule: never speak a number not in a committed artifact), 60-second compressed pitch, judge Q&A
with artifact-grounded answers (judge-trust, heuristic honesty, constructed-hero disclosure, no-fake-timing, n≈40 pilot
framing, solo-vs-team). No claims of training/DPO-quality/significance anywhere.
Batches E–H remain GATED on Spike's labels. Booth still down pending Codex clearance of Batch A.

## SELF-AUDIT of Batches A–D (Jun 12 ~19:30, audit-master style — Codex away; Spike delegated)
**BLOCKER found+fixed:** validate_labels.py hashed read_text()-normalized content → out/label_validation.json recorded
e2479e3f (LF hash) instead of the file's byte hash e6d2055 — the validator's own evidence didn't match the disk bytes
(same read_text class as the Batch A harness incident). Fixed: read_bytes() for hashing, decode for parsing; regenerated
artifact; recorded hash now == byte hash ✓.
**Adversarial re-verification:** all suites re-run from scratch (schemas exit 0, nullable PASS, report selftest 15/15);
demo_report regeneration byte-deterministic; SAVE ROUND-TRIP SIMULATED on an isolated copy (write_label of ref-2 row with
comma+quote note → frozen rows 1-2 byte-identical, CRLF preserved, proper quoting, validator exit 0 on the 3-row file);
static report page RENDERED in a browser (cards/pending banner/bars/archetypes correct, 0 console errors); archetype
derivation verified on the 2 real seeds (bolna→recovered_success via handled_confusion_well+neg, hero→brittle_success).
**WARNINGS fixed:** docs/current_state.md de-staled (pool 46→76, judge 'smoke only'→4A done+quarantined, booth→manifest,
bolna ingested). **WARNINGS noted (accepted):** eval/labels_spike.csv deliberately untracked (commit decision deferred to
submission packaging); improvement queue includes unsure-outcome calls when they carry negative tags (evidence-backed
either way); missing-analytics path untested (renders PENDING by construction).
**Integrity at verdict:** CSV e6d2055 ✓ · manifest aec4ba49 ✓ · judge cache fixture-only ✓ · all pushed.
**Verdict: PASS — booth restart authorized (Batch A clear). Labeling opens; E-H stay gated on ≥40 binary labels.**
