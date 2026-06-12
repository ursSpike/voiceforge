# `eval/labels_rater2.csv` — Second-Rater Schema (DESIGN ONLY)

**Status: specification.** This document defines the schema and merge policy for
a second rater's labels. Agent 4 does **not** create `eval/labels_rater2.csv` —
a real second human rater writes it. `eval/labels_spike.csv` (rater 1) is
**read-only** and is never edited, reconciled, or overwritten by this process.

## Core principle — disagreement is signal, not noise

We follow **SemEval-2023 Task 11, "Learning With Disagreements" (LeWiDi),
arXiv:2304.14803**: annotator disagreement carries information about genuine
item ambiguity and should be *preserved*, not silently collapsed to a single
"gold" label. Concretely:

- Each rater's labels live in their **own file** (`labels_spike.csv` =
  rater 1; `labels_rater2.csv` = rater 2). Neither overwrites the other.
- The merge step (a separate, future artifact — e.g. `labels_merged.csv`)
  records **both** labels plus an explicit `agreement` / `disagreement_type`
  field. It does **not** delete the minority label.
- "Soft" labels (the distribution over the two raters) are retained so that
  downstream calibration (kappa, soft-label metrics) can use disagreement as
  data rather than discarding it.

## `eval/labels_rater2.csv` columns

Identical column set to `labels_spike.csv` so the two files are directly
joinable on `call_id`, plus two rater-2-only review fields.

| column | type | required | notes |
|---|---|---|---|
| `call_id` | str | yes | Join key. MUST exist in `labels_spike.csv`. One row per reviewed call. |
| `primary_label` | enum `{success, fail, unsure}` | yes | Rater 2's independent binary outcome. Rater 2 does **not** see rater 1's label while annotating (blind re-annotation). |
| `confidence` | enum `{low, medium, high}` | yes | Rater 2's self-reported confidence on the re-read. |
| `positive_tags` | `\|`-joined str | no | Same vocabulary as rater 1 (`adapted_language_well`, `completed_or_clear_next_step`, `easy_to_understand`, `handled_confusion_well`, `understood_user`, `user_satisfied`). Empty allowed. |
| `negative_tags` | `\|`-joined str | no | Same vocabulary (`hard_to_understand`, `missing_or_wrong_information`, `misunderstood_user`, `poor_clarification_or_recovery`, `repeated_or_stuck`, `user_frustrated`, `workflow_or_tool_failed`, `wrong_language_or_tone`). Empty allowed. |
| `context_tags` | `\|`-joined str | no | Same vocabulary (`mixed_languages`, `multi_step_request`, `transcript_unclear`, `user_unclear_or_hesitant`). |
| `note` | str | no | Free-text rationale. |
| `timestamp` | ISO-8601 | yes | When rater 2 annotated. |
| `review_reason_codes` | `\|`-joined str | yes | Copied from `review_queue.json` for this call (e.g. `R2_JUDGE_DISAGREE\|R4_HEAVY_NEGATIVE_TAGS`). Records *why* the call entered the queue. `none` if rater 2 reviewed a non-flagged call. |
| `rater_id` | str | yes | Stable rater identifier (e.g. `rater2`). Allows >2 raters later without schema change. |

### Constraints
- `call_id` ∈ the 46 ids in `labels_spike.csv`; no new calls introduced.
- Enums are closed; tag tokens MUST be drawn from the pinned vocabularies above.
- Rater 2 annotates **blind** to rater 1 (no shared cell), so disagreement is genuine inter-annotator signal.
- The file is append-only per rater; it never mutates `labels_spike.csv`.

## Merge / agreement policy (for the future `labels_merged.csv`)

For each `call_id` present in both files:

| derived field | definition |
|---|---|
| `agree_binary` | `primary_label_r1 == primary_label_r2` (treating `unsure` as its own value, so `unsure` vs `success` counts as disagreement). |
| `disagreement_type` | one of `none`, `binary_flip` (success↔fail), `decisiveness` (unsure↔decisive), `tag_only` (binary agree, tag sets differ). |
| `soft_label` | the 2-element distribution over rater labels, e.g. `{success:1, fail:1}` → kept verbatim. **Never** argmax-collapsed at storage time. |
| `confidence_pair` | `(confidence_r1, confidence_r2)` retained as-is. |

**Cohen's kappa** between rater 1 and rater 2 on `primary_label` quantifies
human–human reliability and provides the ceiling against which the LLM-judge's
human-vs-judge kappa should be read. Items with `disagreement_type != none` are
exactly the items where a single "gold" label is least defensible — they are
retained as soft labels, consistent with LeWiDi.

> Honesty note: VoiceForge currently has only rater 1 (`labels_spike.csv`). This
> schema enables a second rater but does not assert one exists. No human–human
> kappa is claimed until `labels_rater2.csv` is actually collected.
