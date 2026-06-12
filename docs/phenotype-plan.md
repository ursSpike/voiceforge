# Call-phenotype labeling — booth v2 (AUDIT-CONFIRMED spec, Jun 11)

GPT verdict: **proceed with the narrowed booth-v2 annotation layer.** This doc reflects the rulings;
the build matches this doc exactly.

## The idea
Each call gets a **phenotype**: the binary outcome PLUS independent transcript-observable primitives
(positive / negative / context). Capture primitives truthfully; the system derives composites
(A+B = observed co-occurrence) later. Demo line: **"not call labels — call phenotypes."**

**The binary `success/fail/unsure` is the calibration spine (human↔judge kappa). Phenotype tags are
a single-rater EXPLORATORY layer — no kappa on tags this sprint.** Binary ships standalone if needed.

## Hard rulings applied
1. **No unobservable tags.** Only the hero call has audio (Bolna `audio_path: null`). So the booth
   offers ONLY transcript-observable SEMANTIC tags. **No audio / latency / overlap / silence / accent
   / noise / mic / network / weather tags** — and **no tag that duplicates a deterministic signal**
   (timing, overlap, slot-capture, silence are already measured by `signals.py`/`score.py`). Schema
   stays extensible for post-hackathon audio work.
2. **Blindness (tightened).** Hide `source`, `stress_profile`, AND raw `call_id` (`swz_`/`hero_`/
   `bolna_` leaks source). Annotator sees a neutral **"Call N of 46"**, plus `workflow_type` +
   `language` (needed to understand the task). Stratification is SERVER-side; `/label/calls` returns
   the already-ordered calls by opaque `ref`, with the hidden fields stripped. No score/flag/suggested-tag.
3. **Scope/time.** Collect the additive layer NOW (re-reading transcripts later is wasteful). **No
   training, no model comparison, no polished analytics.** After labeling: a small DETERMINISTIC summary.

## Approved tag taxonomy (use EXACTLY these allowlists, server-validated)
- **positive (7):** clear_and_concise · good_clarification_or_repair · appropriate_language_adaptation ·
  recovered_after_confusion · user_expressed_satisfaction · good_handoff_or_next_step · good_closing
- **negative (12):** language_mismatch · code_switching_handling_failure · register_mismatch ·
  misunderstood_user_intent · missing_required_information · bad_clarification_or_repair ·
  tool_or_workflow_failure · unsupported_or_hallucinated_answer · user_goal_ambiguous ·
  user_expressed_frustration · overly_verbose_or_unclear · repeated_request_or_repair_loop
- **context (5):** code_switching_present · user_hesitation_or_self_repair · multi_domain_task ·
  transcript_quality_uncertain · explicit_external_interruption
- Removed per ruling: `rural_urban_register_mismatch` (demographic inference) + all audio/timing/
  overlap/silence/noise tags (unobservable or deterministic-duplicates).

## Record / CSV schema (`eval/labels_spike.csv`)
Columns: `call_id, primary_label, confidence, positive_tags, negative_tags, context_tags, note, timestamp`.
- `primary_label` ∈ {success, fail, unsure} — **mandatory**.
- `confidence` ∈ {high, medium, low} — **required**.
- tag columns: pipe-separated, each tag from its allowlist — **optional**.
- `note`: free text — **optional**.
- Written with Python's `csv` module (notes may contain commas/newlines → proper quoting, NO string
  concat). **Last-label-wins** by call_id (revision preserved). call_id is stored (needed to join
  with the judge for kappa) but never shown to the annotator.

## Implementation conditions (all from the ruling)
- Mandatory binary spine; required confidence; optional tags/note.
- POST **JSON** body (not query params). Server validates `primary_label`, `confidence`, and every
  tag against fixed allowlists; rejects unknowns.
- Server-side deterministic stratified order → stable `ref`→`call_id` mapping across requests.
  ⚠️ Refs are stable ONLY while `data/normalized/` is frozen — do NOT add/remove pool calls during a
  labeling session (would re-map refs). Pool is set; labeling can proceed.
- Failed/network saves must NOT advance (show retryable error); guard double-submit; taxonomy served
  from `/label/tags` (no client duplication); save validated against the `phenotype_label` schema.
- Target the **existing 46 calls**, floor **40 usable binary** labels. Do NOT claim 60 unless more
  calls are added before labeling.
- Don't tune the sample after seeing labels; don't force class balance; label truthfully.

## Booth-v2.1 — one-pass hierarchy clarification (Jun 12, audit-master spec)
Wording/UX repair only — **no schema, allowlist, blindness, CSV-format, or quarantine change.**
Annotation is **one pass per call, one save** — not a label-then-listen second pass.
- **Level 1 — Outcome:** exactly one of `success/fail/unsure`. *Did the caller ultimately achieve the goal?*
- **Level 2 — Phenotype primitives:** review **every** group, select all that apply. Positive and
  negative tags may coexist (success-with-friction, fail-despite-good-handling); judge each independently.
  "Optional" was reframed to **"select all that apply; zero is valid only after deliberate review."**
- **Level 3 — Derived archetypes:** **NOT manually labeled.** VoiceForge derives them later,
  reproducibly, from Level-1 outcome + Level-2 primitives + deterministic signals (e.g. brittle_success,
  multilingual_failure, recovered_success, well_handled_workflow_failure). Hand-labeling Level 3 would
  duplicate information and create contradictions — so the booth offers no Level-3 fields.
- **Group headings** now read *"What was good? / What went wrong? / Context present? — Select all that apply."*
- **Mandatory review checkbox** before Save: *"I reviewed all three phenotype groups; zero tags means none applied."*
  Save stays disabled until **outcome + confidence + review-checkbox** are all set. On reopening a saved
  call, every prior label is restored but the checkbox **resets → reconfirmation required** (no labels lost).
- **Scope warning** (prominent, honesty-corrected): *transcript-only view. Do not infer audio quality,
  accent, noise, network conditions, or voice naturalness — **unavailable for nearly all current calls**.
  Do not hand-label latency or overlap; where timestamp data permits, VoiceForge computes **those two**
  deterministically elsewhere.* (Earlier wording wrongly implied ALL excluded signals are "measured
  elsewhere" — only latency/overlap are; audio/accent/noise/network/naturalness are simply absent.)
- Verified in-browser (throwaway CSV, real `eval/labels_spike.csv` untouched): save-gating on each of the
  three requirements, pos+neg coexistence, zero-tag save after confirm, mixed-tag persist+restore,
  failed-save-no-advance, `unsure` excluded from usable count, blind API exposes only language/ref/turns/workflow_type.

## After labeling — small deterministic summary (extends `eval/kappa.py`)
total labeled · usable binary · unsure count · success/fail distribution · kappa + CI + confusion
(binary spine, vs judge once Batch 4 exists) · positive/negative/context tag frequencies · top
co-occurring tag pairs · archetype examples (seamless success · brittle success · language/register
failure · recovered-after-confusion). Framing: directional, **single-rater, n≈46**.

## Post-hackathon (schema preserved, NOT built now)
Train small tag predictors, compare judge models, add audio-derived tags, test the research seed:
*"do multi-dimensional call phenotypes predict success/improvement better than flat pass/fail?"*
(M4 24GB + Colab T4 = small classifiers / LoRA / clustering, not a speech foundation model.)
