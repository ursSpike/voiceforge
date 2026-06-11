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
- Target the **existing 46 calls**, floor **40 usable binary** labels. Do NOT claim 60 unless more
  calls are added before labeling.
- Don't tune the sample after seeing labels; don't force class balance; label truthfully.

## After labeling — small deterministic summary (extends `eval/kappa.py`)
total labeled · usable binary · unsure count · success/fail distribution · kappa + CI + confusion
(binary spine, vs judge once Batch 4 exists) · positive/negative/context tag frequencies · top
co-occurring tag pairs · archetype examples (seamless success · brittle success · language/register
failure · recovered-after-confusion). Framing: directional, **single-rater, n≈46**.

## Post-hackathon (schema preserved, NOT built now)
Train small tag predictors, compare judge models, add audio-derived tags, test the research seed:
*"do multi-dimensional call phenotypes predict success/improvement better than flat pass/fail?"*
(M4 24GB + Colab T4 = small classifiers / LoRA / clustering, not a speech foundation model.)
