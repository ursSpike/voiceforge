# Call-phenotype labeling — PLAN (awaiting audit-master confirm; do NOT build yet)

## The idea (Spike's, refined)
Don't label calls flat (success/fail). Give each call a **phenotype**: a compact fingerprint of
independent primitives — positive, negative, environmental. Capture primitives *truthfully and
independently*; let the **system** derive composites/interactions later (A+B is an observed
co-occurrence, not a hand-made combo label). Demo line: **"not call labels — call phenotypes."**

**Non-negotiable:** the binary `success/fail/unsure` stays the **calibration spine** (human↔judge
kappa). Phenotype tags are an *additional* layer for the failure taxonomy + improvement queue;
they do NOT enter the kappa. If time attacks, the binary spine ships alone — phenotype degrades gracefully.

## What changes (3 pieces)
1. **Booth v2** — two-stage labeler (`/label`):
   - Stage 1 (mandatory): `success / fail / unsure` — keystroke fast, unchanged spine.
   - Stage 2 (optional, fast multi-select chips): positive / negative / context tags + `confidence`
     (high/med/low) + optional short note. Auto-advance.
2. **Schema** — add `phenotype_label` to the constitution (`pipeline/schemas.py` → `schemas/json/`).
   New CSV: `call_id, primary_label, confidence, positive_tags, negative_tags, context_tags, note, timestamp`
   (tag lists pipe-separated). Fresh file (Spike hasn't labeled → no migration).
3. **Phenotype report** — extend `eval/kappa.py` into a calibration+phenotype report: kappa+CI+confusion
   on the binary spine, plus tag-frequency tables, top co-occurring pairs, and archetype examples.

## Tag taxonomy (independent primitives — never hand-combine)
- **positive (11):** seamless_success · natural_turn_taking · good_clarification_or_repair ·
  correct_language_adaptation · robust_to_accent_or_register · robust_to_noise_or_bad_signal ·
  captured_all_required_slots · concise_and_clear · user_sounded_satisfied · good_handoff_or_next_step · good_closing
- **negative (13):** language_mismatch · code_switching_failure · accent_or_register_mismatch ·
  rural_urban_register_mismatch · asr_or_transcription_issue · misunderstood_user_intent ·
  missing_required_slot · bad_clarification_or_repair · latency_or_barge_in_issue ·
  tool_or_workflow_failure · unsupported_or_hallucinated_answer · user_goal_ambiguous · user_frustration
- **context/environmental (11):** caller_side_audio_issue · agent_side_audio_issue · both_sides_audio_issue ·
  background_noise · bad_network_or_signal · weather_or_external_disturbance · noisy_public_setting ·
  phone_mic_issue · interruption_from_other_person · long_silence_or_pause · repeated_request

## Blindness rules (tightened per GPT)
No judge score, no deterministic success score, no suggested tag, **and no stress_profile visible**.
Fix needed: move stratified ordering SERVER-side and **strip `stress_profile` from `/label/calls`**
(currently sent for client-side ordering — not displayed, but should not leave the server).

## Phenotype report (after labeling)
total labeled · usable binary · unsure count · success/fail distribution · kappa · raw agreement ·
confusion matrix · positive/negative/context tag frequencies · top co-occurring tag pairs ·
archetype examples: seamless success · brittle success (success+high friction) · language/register
failure · audio/network failure · recovered-after-confusion.

## ⚠️ Senior-engineer risk flags (where our DATA limits the vision — GPT should weigh)
1. **Environmental/audio tags can't be labeled from text.** 44/46 calls are SpokenWOZ *text* (no audio).
   `background_noise`, `bad_network`, `phone_mic_issue`, `weather`, caller/agent audio issues are
   **un-assessable from a transcript** → those tags will be ~empty except on the 2 audio calls
   (hero, bolna). *Options:* (a) keep the full taxonomy, expect context tags only on audio calls,
   disclose honestly ("context layer is forward-looking; our text pool can't populate it"); or
   (b) trim context tags to the text-inferable few (`long_silence_or_pause`, `repeated_request`,
   `interruption_from_other_person`). **My lean: (a)** — schema complete + disclosed > trimmed.
2. **Small-n sparsity.** 46–60 calls × ~35 tags → most tags 0–3 instances; "top co-occurring pairs"
   is directional, not statistical. Demo framing must say "phenotype distribution, directional, n=60".
3. **Tags have NO agreement metric this sprint.** kappa works because the JUDGE also produces the
   binary label (two raters). The 35 phenotype tags are **single-rater** (only Spike) — no kappa on
   them until a 2nd rater (friend) or the judge predicts tags (post-hackathon). So tags = a
   human-attributed taxonomy, NOT a calibrated signal. Say that plainly.
4. **Time.** Phenotype labeling ≈ 75–90s/call → ~60–90 min for 46–60 (vs ~45 binary). Booth v2 +
   report build ≈ 1.5–2h. Submission Jun 12 night. Fits IF we go now; binary spine is the safety net.

## Scope guard
Hackathon: COLLECT phenotypes (target 60), produce distributions + co-occurrence + archetypes. **No
model training.** Don't tune the sample after seeing labels; don't force class balance; label truthfully.
Post-hackathon (schema preserved): train small tag predictors, compare judge models, test the research
question — **"do multi-dimensional call phenotypes predict success/improvement better than flat
pass/fail or one quality score?"** (M4 24GB + Colab T4 = enough for small classifiers/LoRA/clustering,
NOT a speech foundation model.)

## Open questions for the audit master
1. Environmental tags: keep full taxonomy + disclose sparsity (my lean), or trim to text-inferable?
2. Also hide `source` (spokenwoz/hero/bolna) for max blindness, or keep it as benign context?
3. Confirm scope/time: proceed now as an additive layer on the binary spine (graceful degradation),
   given ~28h to submission and the binary calibration already protected?
