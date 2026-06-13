# PROJECT BIBLE — VoiceForge

> The single file that lets **Spike** understand his entire project before walking into the
> Bolna × Cartesia Voc-a-thon (Bengaluru, demo **June 13, 2026**). You built this fast and skipped
> the learning notebooks — this doc is the *understanding* layer. It is distinct from
> [`docs/demo_script.md`](docs/demo_script.md) (the *performance* script). Every claim below cites a
> real file you can click. Numbers are verified against `out/demo_report_data.json`; anything I could
> not pin is marked ⟨verify⟩.

---

## 1 · The story in 10 lines

1. **Most voice-agent demos stop when the call ends. VoiceForge starts there.** (`README.md` line 3)
2. It is an **eval lab** for voice agents: it takes raw call logs from *any* voice stack (vendor-neutral) and turns them into measurements, calibrated judgments, and a fix list.
3. It is built for two audiences at once: founders who need to *feel* a failure, and ML engineers who need to *trust* a number (`SPEC.md` §1).
4. The core belief: **judge the conversation *trace*, not just the transcript** — timing, overlap, language, task outcome, cost, repair quality. Transcript-only evals miss voice-native failures.
5. **Rule one:** never ask an LLM what you can measure. Barge-ins and latency are arithmetic on timestamps (`pipeline/signals.py`), not model opinions.
6. **Rule two:** never let the judge grade before a human sets the bar **blind**. You labeled 46 calls success/fail without seeing any judge output (`eval/labels_spike.csv`), froze them (`eval/label_snapshot.json`), then ran the judge against a locked gate (`pipeline/judge_run.py`).
7. The loop it closes: **provider logs → normalize → deterministic signals → blind human labels → quarantined LLM judge → calibration (Cohen's κ + imbalance-aware metrics) → phenotypes/archetypes → an evidence-backed improvement queue → one static dashboard.**
8. The signature finding: a plain task-completion heuristic — the metric most teams ship — agrees with blind human judgment on only **25 of 45 calls (56%)**. "A success-rate dashboard is blind exactly where it costs money."
9. **Honesty is the product.** Every score carries a reason + evidence turn IDs; the hero call is disclosed as constructed; costs are labeled estimates; the calibration is a single-rater pilot.
10. **Bolna runs the calls. Cartesia gives them a voice (sonic-3, voice "Devansh", *inside* the Bolna synthesizer). VoiceForge tells you which calls worked, which limped, and what to fix first.**

---

## 2 · End-to-end data flow (every file named)

```
provider logs / corpus files
  │
  │  ADAPTERS (one per source; all output schemas/call_log.md JSON → data/normalized/)
  ├── pipeline/ingest_bolna.py   real Bolna execution → call_log (timing reconstructed from /log)
  ├── pipeline/ingest_cmd.py     Code-Mixed-Dialog (Hindi-English, TEXT-ONLY → unmeasured timing)
  ├── pipeline/normalize.py      SpokenWOZ slice + hero call → call_log (word-timestamp turn bounds)
  │
  ▼  THE CONSTITUTION
  pipeline/schemas.py            validate(obj, schema_name) — boundary-checks every record;
  rubric.yaml                    THE config: dimensions, weights, thresholds (read by everything)
  │
  ▼  DETERMINISTIC SIGNALS
  pipeline/signals.py            FTO math: overlap/gap per turn pair → barge-in + latency failures
  pipeline/score.py              merges signals + task-outcome heuristic + cost → out/calls.json,
                                 out/call_<id>.json, out/analytics.json
  │
  ▼  BLIND LABEL BOOTH (the calibration anchor)
  web/label.html                 the booth: strips call IDs/sources/scores, serves manifest order
  eval/label_manifest.json       FROZEN 46-call order (immutable)
  eval/labels_spike.csv          your 46 blind labels (success/fail/unsure + phenotype tags)
  eval/label_snapshot.json       the freeze: byte-hash of the CSV + manifest, annotation_status
  pipeline/validate_labels.py    proves the CSV is sound + matches the frozen snapshot
  │
  ▼  QUARANTINED JUDGE (Gemini, gated)
  pipeline/judge.py              5 SEMANTIC dims, validate-before-cache, re-validate-on-cache-hit
  pipeline/judge_run.py          THE gated run: frozen-snapshot gate → binary outcome judgment
                                 per call → out/judge_results.json
  │
  ▼  CALIBRATION + PHENOTYPES + PRESENT SURFACE
  pipeline/demo_report.py        κ + balanced accuracy + the metric trap + archetypes + queue
                                 → out/demo_report_data.json + .md + .html
  pipeline/dashboard.py          → out/dashboard.html (self-contained, offline)
  pipeline/cache_bolna_cartesia_proof.py → out/bolna_cartesia_proof.json (sponsor chain)
  pipeline/preflight.py          executable submission checklist
```

### Stage by stage

**1. Sources → adapters → `data/normalized/`.** Three adapters, all producing the same `call_log` shape so every downstream tool is vendor-blind (`docs/architecture.md` "vendor-neutral by contract"):

- **`pipeline/ingest_bolna.py`** — one real Bolna execution (`bolna_246cd9f3`). Turns and timing are **reconstructed from the `/log` component events' `created_at` diffs**, *never* the top-level transcript (which is role-less and whose "precise" mode scrubs interrupted content). `transcriber.response` = a user turn ended; `synthesizer.request` = an agent turn began; `synthesizer.response` = agent audio ready. Latency gap = agent.start − user.end.
- **`pipeline/ingest_cmd.py`** — 30 Hindi-English code-switched restaurant bookings (bAbI/DSTC2 "Code-Mixed-Dialog", `cmd_hi_0000…`). **Text-only**, so every turn is `start_ms: null` and the call is `stress_profile: unmeasured` — the nullable-timing contract; no ms is ever fabricated.
- **`pipeline/normalize.py`** — SpokenWOZ slice (`swz_MUL*`) + the constructed hero call (`hero_001`). Turn bounds synthesized from word-level ASR timestamps; `stress_profile` (clean / pause_heavy / interruption) assigned by a **deterministic timing rule**, never by judgment.

**2. The schema constitution.** `pipeline/schemas.py:validate()` is the boundary. The five schemas are documented in `schemas/{call_log,task_outcome,scorecard,cost,improvement_example}.md`. The hard invariant (`normalize.py:validate_call`): a call is **all-timed or all-null — never mixed**. A partial clock is *rejected*, because bridging across untimed turns would manufacture fake floor-transfer offsets.

**3. Deterministic signals — the FTO math (`pipeline/signals.py`).** FTO = "floor transfer offset" = the gap between one turn ending and the next starting:

```
fto_ms = next.start_ms − prev.end_ms     (negative = overlap, positive = gap)
overlap_ms = max(0, −fto)                  gap_ms = max(0, fto)
```

- **Barge-in** = `overlap_ms > 100` (≤100 ms is a backchannel, ignored). Agent-interrupts-user and user-interrupts-agent are tracked **separately**; only agent-interrupts-user counts against the agent in scoring (`score.py`). Threshold lives in `rubric.yaml` (`barge_in.threshold_overlap_ms: 100`).
- **Latency** = `gap_ms` on **user→agent** transitions only. Bands: ≤300 snappy · ≤800 ok · >800 laggy (`rubric.yaml` `latency_gap.laggy_ms: 800`). Reported as **median + p90, never mean**.
- **Safety rails:** an unmeasured or mixed call yields *zero* timing events (the math just returns `[]`); a turn with no `end_ms` is skipped (latency-only, overlap never faked).

**4. Blind label booth + frozen manifest.** You labeled in `web/label.html`, which hides call IDs, sources, and any score, serving the **immutable** order in `eval/label_manifest.json` (46 calls). Output: `eval/labels_spike.csv` (one binary `primary_label` ∈ {success, fail, unsure} + confidence + phenotype tags per call). `pipeline/validate_labels.py` runs 9 checks (exact columns, unique IDs, manifest membership, frozen SHA, allowlists from `schemas.py`, CSV-quoting integrity, ≥40 floor, two seed annotations preserved). `eval/label_snapshot.json` is the **freeze**: it pins the CSV's raw-byte SHA + the manifest SHA + counts, with `annotation_status: complete`. After this point the labels are immutable.

**5. Quarantined judge (`pipeline/judge.py`).** Gemini (`gemini-3.1-flash-lite`, temperature 0, JSON mode). It scores **5 semantic dimensions only** (the judge-type dims in `rubric.yaml`): `language_match, faithfulness, repair_quality, conciseness, user_frustration`. Every response is:
- **validated before caching** — a malformed/out-of-range response never lands in `data/.judge_cache/` (no poisoned cache);
- **re-validated on every cache hit** against the current call — a corrupted/stale entry is deleted and re-fetched;
- required to cite **≥1 real evidence turn ID** (hallucinated turn IDs are dropped and flagged).
These 5 dims are marked `provenance: "uncalibrated"` **permanently this sprint** — there is no per-dimension human gold, so κ can never calibrate them.

**6. The gated outcome judge (`pipeline/judge_run.py`).** This is the only thing κ calibrates. It asks **one binary success/fail question per call — the same question you answered blind** — separate from the 5 semantic dims. Before any paid call it runs the **gate** (must pass *all*): rubric unchanged → `validate_labels.py` exits 0 → snapshot exists and `annotation_status=complete` → snapshot SHA == the pinned audited SHA → CSV byte-SHA == snapshot's → manifest SHA == snapshot's → the 3 frozen artifacts are byte-identical to git HEAD → exactly 46 rows / 45 binary → only manifest calls are judged. The real run produced `out/judge_results.json`: **46 calls × (5 dims + 1 outcome) = 276 judgments, 276 validated, 0 failures, 178 cache hits** (`demo_report_data.json` `judge_run`).

**7. Calibration (`pipeline/demo_report.py:kappa_block`).** Pairs your blind binary labels with the judge's binary outcome (45 binary calls; the 1 `unsure` is excluded). Computes Cohen's κ + a deterministic seeded bootstrap CI, **plus** balanced accuracy, Youden's J, failure recall/precision/specificity, F1, MCC — because the 37/8 success/fail imbalance makes raw accuracy and κ alone misleading. The **truth correction** (commit referenced in the caption; `reports/research_jun13/STATUS_REPORT.md`) removed a false "code-switching is least reliable" claim: hi-en 71% ≈ English 69% — language is *not* the reliability axis; annotator confidence is.

**8. Phenotypes → archetypes → improvement queue (`demo_report.py`).** Three levels:
- **Level 1:** the blind binary outcome (success/fail/unsure).
- **Level 2:** phenotype **tags** you applied while labeling (positive/negative/context) — single-rater **exploratory**, never "calibrated".
- **Level 3:** **archetypes**, *derived deterministically* from L1+L2 with a documented precedence (workflow > language > intent/slot > repair-loop) — **never hand-labeled** (`demo_report.py:archetype`). The **improvement queue** is every call carrying ≥1 negative tag, each mapped to a concrete template fix (`RECOMMEND`) + expected mechanism (`MECHANISM`), flagged `needs_human_review`.

**9. Present surface.** `out/dashboard.html` (built by `pipeline/dashboard.py`, self-contained/offline) and `out/demo_report.html` are the demo surfaces. `web/shot.html` is the money-shot audio player. Everything reads committed `out/*.json` — no backend, no DB.

---

## 3 · Every metric in 2 lines + its caveat

All values verified against `out/demo_report_data.json` unless flagged. The calibration set is **n=45** binary calls (37 success / 8 fail; 1 unsure excluded).

| Metric | Value | What it means + caveat |
|---|---|---|
| **Cohen's κ** | **0.206** | Chance-corrected human↔judge agreement on the binary outcome. "Slight" (Landis–Koch). Bootstrap 95% CI **[−0.108, 0.499] includes 0** — at n=45 with 82% success prevalence, the prevalence paradox compresses κ. It is honest, not flattering. |
| **Raw agreement** | **0.711** | 32/45 calls agree. Looks fine, but ignores that "always say success" would already score ~82%. |
| **Balanced accuracy** | **0.628** | Mean of failure-recall and specificity — reports the same 45 calls **without** the imbalance penalty that crushes κ. The honest "how good is it really" number. |
| **Youden's J** | **+0.257** | balanced accuracy expressed as lift over chance (recall + specificity − 1). Positive = better than a coin flip. |
| **Failure recall** | **0.500** | Of 8 real failures, the judge caught 4. **The most actionable number for a risk surface** — half of failures slip past. |
| **Failure precision** | **0.308** | When the judge says "fail," it's right ~31% of the time (4 of 13 fail-calls). Noisy positive class. |
| **Specificity** | **0.757** | Of 37 real successes, 28 correctly called success. The judge is better at confirming success than catching failure. |
| **F1 (fail class)** | **0.381** | Harmonic mean of failure precision/recall. Low — reflects the hard, rare positive class. |
| **MCC** | **0.217** | Matthews correlation — a single balanced score across the whole 2×2; ~κ here, consistent with "slight." |
| **The metric trap** | **25/45 (56%)** | The deterministic task-completion **heuristic** agrees with blind humans on only 25 of 45 calls. It **missed 13 real successes** and **passed 7 of 8 real failures**. This is the signature stat. |
| **Confusion matrix** | h_fail\|j_fail **4** · h_fail\|j_succ **4** · h_succ\|j_fail **9** · h_succ\|j_succ **28** | (fail = the risk/positive class.) 13 total disagreements — exactly the calls "a team trusting this judge uncalibrated would be wrong on and never know." |
| **Human success rate** | **0.822** | 37 of 45 binary calls were successes by *your blind* judgment (vs the 0.566 heuristic rate over the full 76-call scored corpus — they measure different things). |
| **Cost / human success (est.)** | **$0.0511** | Estimated prototype cost per call you judged successful. Costs are turn-count × public per-unit price (~$0.005/turn, anchored to Bolna's observed ~5.96¢/13 turns). **Estimated, prototype — no real billing data** except the one Bolna call's real cost. |
| **Friction-or-failure spend share** | **0.421** | 42% of binary-call spend went to calls that failed *or* carried a negative tag — i.e. money spent on calls that didn't go cleanly. |
| **Brittle share of successes** | **0.135** | ~14% of successes were "brittle" — the task completed but the caller fought for it (5 of 37). A success-rate dashboard hides this; a phenotype distribution doesn't. |
| **Failure event clusters** | latency_gap **183**, barge_in **107** | Deterministic **signal hits** (NOT failed calls) across the timed slice. These are events the timing math flagged, over the 46 timed calls. |

**Slice rates** (calibration, language is NOT the axis): hi-en 22/31 ≈ 71% vs English 9/13 ≈ 69% — statistically indistinguishable. The defensible split is **annotator confidence**: high 24/29 ≈ 83% vs medium 8/16 = 50% — but that's known only *post*-annotation, so it supports a **second-rater review queue, not an auto-router**.

> ⟨verify⟩ note on n: the corpus scored end-to-end is **76 calls** (`out/analytics.json` `n_calls: 76`, `out/demo_report_data.json` `corpus.n_scored: 76`); the **frozen label/calibration slice is 46 calls** (`eval/label_manifest.json`), of which **45 are binary** (1 unsure). Both are correct and refer to different things — see the corpus note in §4. No number is unverified, but be ready to explain the 76-vs-46-vs-45 layering if a judge probes.

---

## 4 · Every honest limitation — and why it's a strength in the room

From `docs/limitations.md` (written *before* the first line of pipeline code, on purpose).

1. **Small n (45 binary labels).** *Strength:* you report it as a **pilot calibration** with a bootstrap CI, not a claim. "The booth, validator, and κ machinery don't care whether n is 40 or 4,000" — the design scales; the honesty is the moat.
2. **Single rater.** Only you labeled. *Strength:* you never claim a human-human ceiling, you ship a **second-rater review queue spec** (`experiments/jun13_eval/annotation/`), and the confidence-slice finding (50% vs 83%) tells you *exactly which calls a second rater should see first*.
3. **Uncalibrated semantic dimensions.** The 5 judge dims have no per-dimension human gold, so they stay labeled `uncalibrated` **forever this sprint**. *Strength:* this is intellectual discipline — κ calibrates the binary outcome **only**, and you say so. You don't launder one calibrated number into five.
4. **Estimated costs.** Turn-count × public per-unit prices; only the one Bolna call has a real provider cost. *Strength:* labeled "estimated, prototype" everywhere; the *relative* ordering across stress profiles is the point, and it's reproducible byte-for-byte.
5. **Heuristic task completion.** "Captured" = a keyword appears in the text; "completed" = ≥70% captured. *Strength:* this *is* the metric trap — you ship the weak metric **on purpose** to show it fails (25/45), which is the demo's most memorable moment. (And `experiments/jun13_eval/grounded/` shows a source-grounded probe lifts it to **33/41 ≈ 81%** — roadmap, not shipped.)
6. **Reconstructed / synthesized timing.** SpokenWOZ turn bounds come from word timestamps; hero bounds from the assembly timeline; Bolna timing from `/log` diffs. *Strength:* exact *given* the source, never faked — and where there is no clock (the Hindi text calls), timing is **omitted, not invented** (the schema rejects a partial clock).
7. **Constructed hero call.** `hero_001` is a scripted, assembled scenario. *Strength:* disclosed on its own slide; it demonstrates *detection*, not prevalence — validity comes from the public-data calibration, not that call.

> **Stale-doc heads-up (⟨verify⟩-adjacent, factual):** `docs/limitations.md` and `docs/dataset_card.md` still say the pool is "44 SpokenWOZ + hero + Bolna" and English-heavy. That described an earlier build. The **actual frozen label manifest** (`eval/label_manifest.json`) is **14 SpokenWOZ + 30 Hindi-English code-mixed + hero + Bolna = 46**, and the full scored corpus is **44 SpokenWOZ + 30 cmd_hi + Bolna + hero = 76**. The `demo_script.md` (line 18) already states the current truth ("44 SpokenWOZ … 30 Hindi-English … 76 calls"). If a judge reads the older docs, point them at the manifest as the source of truth.

---

## 5 · The audit-trail story

**What's frozen, and how (`pipeline/judge_run.py:gate`, `pipeline/validate_labels.py`):**
- **Labels CSV** SHA-256 `b3884f9e…` — pinned in `eval/label_snapshot.json` and re-checked byte-for-byte.
- **Manifest** SHA-256 `aec4ba49…` — the 46-call order is immutable.
- **Snapshot** SHA-256 `d592782a…` — itself pinned. This is the clever bit: editing the CSV *and* rewriting the snapshot to match **cannot** open the gate, because a re-written snapshot is no longer the *audited* artifact (`judge_run.py` has an explicit adversarial selftest for exactly this — "consistent CSV+snapshot rewrite still closes").
- **Git anchor:** every real run also requires the 3 frozen artifacts to be byte-identical to git HEAD.

**The gates (in order):** rubric unchanged → labels validate → snapshot complete → snapshot SHA == pinned → CSV SHA == snapshot → manifest SHA == snapshot → git-clean → exact row/binary counts → manifest-only calls. **Any miss refuses to spend a single Gemini call.** Paid work is never the default — a bare invocation prints help and exits 2.

**What "calibrated" does and does NOT mean here:**
- **DOES:** the *binary success/fail outcome judge* has been measured against your blind human labels — you know its κ, its CI, its failure recall, and the exact 13 calls where it disagrees with you.
- **Does NOT:** it does **not** mean the judge is accurate (κ=0.206 is "slight," CI includes 0). It does **not** mean the 5 semantic dimensions are validated — they never are this sprint. It does **not** mean "substantial agreement" — you only claim that if the number *and* CI land in 0.61–0.80, which they don't.
- The mature one-liner: *"I'm not pretending this judge is magic; I tested where it agrees with humans and where it fails."*

**Reproducibility:** `out/judge_results.json` records model, temperature, `rubric_hash`, `judge_prompt_hash`, the frozen CSV/manifest hashes, expected vs validated judgment counts, cache hits, and timestamps. Outputs are written atomically; runs are resumable from cache. An independent audit wave (`reports/research_jun13/STATUS_REPORT.md`) re-hashed every protected artifact and re-derived κ=0.206 and the 25/45 trap from scratch — they match.

---

## 6 · The Bolna × Cartesia architecture

**There is no separate Cartesia API key, and VoiceForge never calls `api.cartesia.ai`.** Cartesia runs **inside** the Bolna agent: the agent's *synthesizer* is configured with `provider = cartesia`, voice **Devansh**, model **sonic-3**. You reach it through the **Bolna** agent endpoint with `BOLNA_API_KEY`.

Three honest links (the answer to "where exactly are Bolna and Cartesia?", `demo_script.md` Q&A):
1. **A real Bolna execution** (`bolna_246cd9f3`) pulled from the Bolna API into the pipeline — timing reconstructed from the conversation trace, its **real provider cost** used. It *predates* your Cartesia voice swap (its synthesizer was elevenlabs at the time), so you say that plainly (`ingest_bolna.py` metadata note).
2. **The live Bolna agent is configured with Cartesia Devansh (sonic-3) today** — config shown on request.
3. **The hero call** is synthesized with that same Cartesia voice.

**The proof artifact (`out/bolna_cartesia_proof.json`, built by `pipeline/cache_bolna_cartesia_proof.py`):** one authorized GET to the Bolna agent endpoint caches a **sanitized 5-field snapshot** — exactly `agent_id, fetched_at, synthesizer_provider, cartesia_voice, cartesia_model` and **nothing else** (no API key, no prompts, no webhooks, no tools). The validator **refuses to write** unless: the fetched agent *is* your configured agent, provider == cartesia, voice is a non-empty string, and `fetched_at` is timezone-aware. `model` may be null **only** if Bolna genuinely omits it (disclosed, never invented). A forged blob like `{"synthesizer_provider":"cartesia"}` is rejected by the strict exact-keys check. `pipeline/preflight.py --offline` re-validates this cached proof so the demo shows the sponsor chain **without a live call**.

Current proof contents: `synthesizer_provider: cartesia`, `cartesia_voice: Devansh`, `cartesia_model: sonic-3`, fetched `2026-06-12T22:19:32+05:30`.

---

## 7 · Glossary (everything a judge might probe)

- **FTO (floor-transfer offset)** — the ms between one turn ending and the next beginning. Negative = the speakers overlapped; positive = a silent gap. The single primitive behind both barge-in and latency (`signals.py`).
- **Barge-in** — one party starts talking while the other is still speaking (overlap > 100 ms). VoiceForge tracks agent-interrupts-user (an agent sin) separately from user-interrupts-agent (often normal). ≤100 ms overlap is treated as a backchannel ("mm-hm") and ignored.
- **Latency / response gap** — silence on a **user→agent** handoff: how long the caller waited for the agent to respond. Bands ≤300 snappy / ≤800 ok / >800 laggy. Reported as median + p90.
- **Prevalence paradox (a.k.a. base-rate / imbalance trap)** — when one class dominates (here 82% success), high *raw* agreement is cheap and Cohen's κ gets *compressed* even for a decent classifier. The fix: report **balanced accuracy, failure recall, MCC** alongside κ (paper arXiv:2512.08121, `STATUS_REPORT.md`). Note: an *earlier* version of the demo made a genuine **base-rate fallacy** ("9 of 13 disagreements are code-switched → judge fails there") — that claim was **corrected and removed**; hi-en 71% ≈ English 69%.
- **Cohen's κ** — agreement between two raters corrected for the agreement you'd expect by chance. 0 = chance-level; 1 = perfect. Landis–Koch bands: <0.21 slight, 0.21–0.40 fair, 0.41–0.60 moderate, 0.61–0.80 substantial. Yours: **0.206 (slight)**.
- **Youden's J** — `recall + specificity − 1`. A one-number summary of how far a binary classifier beats chance (0 = chance, 1 = perfect). Yours: **+0.257**.
- **Balanced accuracy** — the average of the two per-class recalls; immune to class imbalance. Yours: **0.628**.
- **MCC (Matthews correlation coefficient)** — a single −1…+1 score over the whole confusion matrix that stays honest under imbalance. Yours: **0.217**.
- **Bootstrap CI** — resample the 45 label-pairs *with replacement* many times (2,000×, seeded for determinism), recompute κ each time, take the 2.5th/97.5th percentiles → a 95% confidence interval **[−0.108, 0.499]**. Because it includes 0, you cannot rule out chance-level agreement at this n.
- **Code-switching / Hinglish / Tenglish** — mixing two languages in one utterance (Hindi+English = Hinglish; Telugu+English = Tenglish). The hero call (te-en) and the Bolna call (hi-en) plus 30 cmd_hi calls exercise this; `language_match` is the rubric dimension that scores whether the agent adapts.
- **Phenotype** — an independent, transcript-observable **tag** you applied while labeling (e.g. `poor_clarification_or_recovery`, `wrong_language_or_tone`). Single-rater, exploratory, NOT calibrated. Allowlists in `schemas.py` (`PHENO_POSITIVE/NEGATIVE/CONTEXT`).
- **Archetype** — a **call-level shape** derived *deterministically* from the binary outcome + phenotype tags with a fixed precedence (e.g. `seamless_success`, `brittle_success`, `recovered_success`, `workflow_failure`, `intent_or_slot_loss_failure`). Never hand-labeled — the derivation is code (`demo_report.py:archetype`). **Phenotype = the input tag; archetype = the derived category.**
- **Brittle success** — a call that *succeeded* but carried negative tags: the task got done, the caller fought for it. 5 of 37 successes (13.5%).
- **Improvement queue** — the fix list: every labeled call with a negative tag → evidence turns + archetype + a concrete template recommendation + expected mechanism. An engineering backlog, not vibes. (Note: this is the *shipped* deliverable; the DPO-pair export described in early specs is **roadmap**.)
- **DPO (Direct Preference Optimization)** — a way to fine-tune a model from (chosen, rejected) response pairs. The early SPEC framed each detected failure as a future DPO pair. **It is roadmap, NOT shipped** — `pipeline/dpo_export.py` is a deliberate stub (`raise SystemExit`), and `pipeline/preflight.py` explicitly states "DPO pair export is roadmap, not this sprint." Say "improvement queue," not "DPO dataset," unless you're talking about the future.
- **Grounded-outcome probe** — a roadmap **investigation** (`experiments/jun13_eval/grounded/grounded_probe.py`) that decides success/fail by reading each dataset's hidden backend ground truth (SpokenWOZ belief-state/booking acts; DSTC2 KB rows + api_calls) instead of keyword-matching the transcript. Agrees with humans on **33/41 (81%)** vs the heuristic's 25/45 (56%), and even catches backend failures the human missed (e.g. a hallucinated restaurant). **Additive, not integrated** — it would change the demo's outcome story, so it's queued for a separate audited round.
- **`unmeasured` / nullable timing** — a call with no timestamps (the Hindi text corpus). All turn times are null, `stress_profile` is `unmeasured`, and timing dimensions are *omitted* — never a fake 0. The schema's all-or-none invariant rejects any partial clock.
- **The two-clock rule** — every timestamp in a call shares one clock (ms from call start); cross-source ingestion re-zeros to it; sources without end-times get latency-only treatment.

---

## Where to click first (the 3 files that hold the whole truth)

1. **`out/demo_report_data.json`** — every headline number lives here, computed from committed artifacts. If you can explain this file, you can answer almost any question.
2. **`pipeline/signals.py`** + **`rubric.yaml`** — the deterministic heart (FTO math + the thresholds you can live-edit).
3. **`pipeline/judge_run.py`** — the gate + the binary outcome judge: the audit-trail story that makes "calibrated" mean something.
