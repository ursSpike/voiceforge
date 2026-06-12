# VoiceForge — Evaluation Report

> Voice-agent demos stop when the call ends. **VoiceForge starts there**: deterministic signals → blind human labels → calibrated judge → call phenotypes → failure clusters → an improvement queue.

## 1 · Corpus & coverage
- **76 calls scored** · timing observed on 46 · text-only (timing honestly omitted) on 30
- task-success rate **0.566** *(heuristic keyword match — not gold)* · cost/successful call **$0.1188** *(estimated, prototype)*

## 1b · The metric trap *(signature finding)*
- The completion **heuristic** (the metric most teams ship) agrees with blind human judgment on only **25/45** calls (56%) — it missed **13** real successes and passed **7** of 8 real failures. *A success-rate dashboard is blind exactly where it costs money.*

## 2 · Deterministic failure events *(signal hits — NOT failed calls)*
- `latency_gap` × **183** (e.g. hero_001, swz_MUL0035, swz_MUL0056)
- `barge_in` × **107** (e.g. hero_001, swz_MUL0035, swz_MUL0043)

## 3 · Blind human labels
- labeled **46** of 46 · usable binary **45** (floor ≥40: **MET**) · unsure 1 (excluded from calibration)
- distribution: `{'success': 37, 'fail': 8, 'unsure': 1}`

## 4 · Human ↔ judge calibration
- n=45 · raw agreement **0.711** · Cohen's κ **0.206** (bootstrap 95% CI -0.108–0.499)
- confusion: `{'h_fail|j_fail': 4, 'h_fail|j_success': 4, 'h_success|j_fail': 9, 'h_success|j_success': 28}` · disagreements (13): cmd_hi_0001, cmd_hi_0006, cmd_hi_0007, cmd_hi_0009, cmd_hi_0013, cmd_hi_0014, cmd_hi_0018, cmd_hi_0022, cmd_hi_0024, swz_MUL2483, swz_MUL0247, swz_MUL1560, swz_MUL0035
- *Slight agreement (Landis–Koch); the 95% CI includes 0 — at n=45 with 82% success prevalence the prevalence paradox compresses κ. This is the gap a calibration step exists to expose: 9 of 13 disagreements are code-switched (hi-en) calls, so the judge is least reliable exactly there. Measured, not assumed — a team trusting this judge uncalibrated would be wrong on 13/45 calls and never know.*

## 5 · Phenotype tags *( single-rater exploratory (n=1 annotator) — NOT calibrated )*
- **positive**: `understood_user`×37, `adapted_language_well`×35, `user_satisfied`×34, `completed_or_clear_next_step`×31, `handled_confusion_well`×23, `easy_to_understand`×21
- **negative**: `poor_clarification_or_recovery`×11, `missing_or_wrong_information`×10, `workflow_or_tool_failed`×10, `repeated_or_stuck`×8, `misunderstood_user`×6, `wrong_language_or_tone`×4, `hard_to_understand`×4, `user_frustrated`×1
- **context**: `multi_step_request`×42, `mixed_languages`×40, `user_unclear_or_hesitant`×8, `transcript_unclear`×8
- top co-occurring pairs: `mixed_languages`+`multi_step_request` ×38, `multi_step_request`+`understood_user` ×34, `adapted_language_well`+`multi_step_request` ×33, `mixed_languages`+`understood_user` ×32, `multi_step_request`+`user_satisfied` ×32, `understood_user`+`user_satisfied` ×31, `adapted_language_well`+`mixed_languages` ×31, `mixed_languages`+`user_satisfied` ×30

## 6 · Call archetypes *(Level-3 — deterministic from Level-1 outcome + Level-2 tags (precedence: workflow > language > intent/slot > repair-loop); never hand-labeled)*
- **seamless success** × 25
- **brittle success** × 5
- **recovered success** × 7
- **intent or slot loss failure** × 3
- **workflow failure** × 5
- **ambiguous or unassessable** × 1

## 7 · Representative calls
- `bolna_246cd9f3` · human **success/high** · judge success · *recovered success* · tags ['wrong_language_or_tone']
  - → detect caller language/register in the first 2 turns and switch the response style *(template-derived from tags)*
- `hero_001` · human **success/high** · judge success · *brittle success* · tags ['wrong_language_or_tone'] · det. failures ['barge_in', 'latency_gap']
  - → detect caller language/register in the first 2 turns and switch the response style *(template-derived from tags)*
- `cmd_hi_0000` · human **fail/medium** · judge fail · *workflow failure* · tags ['missing_or_wrong_information', 'poor_clarification_or_recovery', 'workflow_or_tool_failed']
  - → require slot read-back before closing; re-ask for any unfilled required slot *(template-derived from tags)*
- `cmd_hi_0001` · human **fail/medium** · judge success · *intent or slot loss failure* · tags ['missing_or_wrong_information', 'repeated_or_stuck', 'poor_clarification_or_recovery']
  - → require slot read-back before closing; re-ask for any unfilled required slot *(template-derived from tags)*
- `cmd_hi_0002` · human **success/high** · judge success · *seamless success* · tags ['adapted_language_well', 'user_satisfied', 'handled_confusion_well', 'understood_user', 'completed_or_clear_next_step']

## 8 · Improvement queue *(evidence-backed; recommendations template-derived from observed tags)*
- `bolna_246cd9f3` (success/high, recovered success): detect caller language/register in the first 2 turns and switch the response style — evidence: ['wrong_language_or_tone']
- `hero_001` (success/high, brittle success): detect caller language/register in the first 2 turns and switch the response style — evidence: ['wrong_language_or_tone']
- `cmd_hi_0000` (fail/medium, workflow failure): require slot read-back before closing; re-ask for any unfilled required slot — evidence: ['missing_or_wrong_information', 'poor_clarification_or_recovery', 'workflow_or_tool_failed']
- `cmd_hi_0001` (fail/medium, intent or slot loss failure): require slot read-back before closing; re-ask for any unfilled required slot — evidence: ['missing_or_wrong_information', 'repeated_or_stuck', 'poor_clarification_or_recovery']
- `cmd_hi_0004` (fail/medium, workflow failure): add a tool-failure fallback path (acknowledge, retry once, then offer human handoff) — evidence: ['workflow_or_tool_failed', 'missing_or_wrong_information', 'misunderstood_user']
- `cmd_hi_0011` (success/high, recovered success): add a tool-failure fallback path (acknowledge, retry once, then offer human handoff) — evidence: ['workflow_or_tool_failed', 'misunderstood_user', 'poor_clarification_or_recovery']
- `cmd_hi_0013` (success/medium, brittle success): require slot read-back before closing; re-ask for any unfilled required slot — evidence: ['missing_or_wrong_information', 'workflow_or_tool_failed']
- `cmd_hi_0015` (fail/medium, intent or slot loss failure): require slot read-back before closing; re-ask for any unfilled required slot — evidence: ['missing_or_wrong_information', 'repeated_or_stuck', 'poor_clarification_or_recovery', 'hard_to_understand']
- `cmd_hi_0016` (success/high, recovered success): cap repeats at 2, then rephrase with a concrete example instead of repeating verbatim — evidence: ['repeated_or_stuck', 'workflow_or_tool_failed']
- `cmd_hi_0017` (success/medium, brittle success): cap repeats at 2, then rephrase with a concrete example instead of repeating verbatim — evidence: ['repeated_or_stuck', 'workflow_or_tool_failed', 'poor_clarification_or_recovery', 'misunderstood_user']
- `cmd_hi_0020` (success/medium, recovered success): require slot read-back before closing; re-ask for any unfilled required slot — evidence: ['missing_or_wrong_information', 'hard_to_understand']
- `cmd_hi_0022` (fail/medium, workflow failure): require slot read-back before closing; re-ask for any unfilled required slot — evidence: ['missing_or_wrong_information', 'workflow_or_tool_failed', 'repeated_or_stuck', 'misunderstood_user']
- `cmd_hi_0024` (fail/medium, workflow failure): add a tool-failure fallback path (acknowledge, retry once, then offer human handoff) — evidence: ['workflow_or_tool_failed', 'poor_clarification_or_recovery', 'misunderstood_user']
- `cmd_hi_0028` (success/medium, brittle success): cap repeats at 2, then rephrase with a concrete example instead of repeating verbatim — evidence: ['repeated_or_stuck', 'hard_to_understand', 'missing_or_wrong_information', 'poor_clarification_or_recovery']
- `cmd_hi_0029` (fail/high, workflow failure): replace generic re-asks with a targeted clarifying question naming the unclear slot — evidence: ['poor_clarification_or_recovery', 'workflow_or_tool_failed', 'misunderstood_user', 'repeated_or_stuck', 'missing_or_wrong_information', 'user_frustrated']
- `cmd_hi_0030` (success/medium, brittle success): replace generic re-asks with a targeted clarifying question naming the unclear slot — evidence: ['poor_clarification_or_recovery']
- `cmd_hi_0031` (success/medium, recovered success): require slot read-back before closing; re-ask for any unfilled required slot — evidence: ['missing_or_wrong_information', 'repeated_or_stuck', 'workflow_or_tool_failed']
- `swz_MUL0815` (unsure/high, ambiguous or unassessable): replace generic re-asks with a targeted clarifying question naming the unclear slot — evidence: ['poor_clarification_or_recovery']
- `swz_MUL1560` (success/medium, recovered success): detect caller language/register in the first 2 turns and switch the response style — evidence: ['wrong_language_or_tone']
- `swz_MUL0035` (success/medium, recovered success): detect caller language/register in the first 2 turns and switch the response style — evidence: ['wrong_language_or_tone', 'hard_to_understand', 'poor_clarification_or_recovery']

---
judge run: model `gemini-3.1-flash-lite` · temp 0 · rubric c1cc81415e23 · 46 calls · cache hits 178 · failures 0

---
*Every number above is computed from committed artifacts. Heuristic = keyword task-completion; estimated = public per-unit prices; kappa calibrates the binary outcome judge ONLY — semantic dims stay uncalibrated diagnostics; pending = honestly absent.*
