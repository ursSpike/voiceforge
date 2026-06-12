# VoiceForge — Evaluation Report

> Voice-agent demos stop when the call ends. **VoiceForge starts there**: deterministic signals → blind human labels → calibrated judge → call phenotypes → failure clusters → an improvement queue.

## 1 · Corpus & coverage
- **76 calls scored** · timing observed on 46 · text-only (timing honestly omitted) on 30
- task-success rate **0.566** *(heuristic keyword match — not gold)* · cost/successful call **$0.1188** *(estimated, prototype)*

## 2 · Deterministic failure events *(signal hits — NOT failed calls)*
- `latency_gap` × **183** (e.g. hero_001, swz_MUL0035, swz_MUL0056)
- `barge_in` × **107** (e.g. hero_001, swz_MUL0035, swz_MUL0043)

## 3 · Blind human labels
- labeled **2** of 46 · usable binary **2** (floor ≥40: **not yet** — 38 to go) · unsure 0 (excluded from calibration)
- distribution: `{'success': 2}`

## 4 · Human ↔ judge calibration
**PENDING CALIBRATION** — requires ≥40 blind binary labels **and** a judged run (quarantined until labeling completes). No number is shown because none exists yet.

## 5 · Phenotype tags *( single-rater exploratory (n=1 annotator) — NOT calibrated )*
- **positive**: `user_satisfied`×2, `understood_user`×2, `completed_or_clear_next_step`×2, `handled_confusion_well`×1
- **negative**: `wrong_language_or_tone`×2
- **context**: `mixed_languages`×2
- top co-occurring pairs: `completed_or_clear_next_step`+`mixed_languages` ×2, `completed_or_clear_next_step`+`understood_user` ×2, `completed_or_clear_next_step`+`user_satisfied` ×2, `completed_or_clear_next_step`+`wrong_language_or_tone` ×2, `mixed_languages`+`understood_user` ×2, `mixed_languages`+`user_satisfied` ×2, `mixed_languages`+`wrong_language_or_tone` ×2, `understood_user`+`user_satisfied` ×2

## 6 · Call archetypes *(Level-3 — deterministic from Level-1 outcome + Level-2 tags (precedence: workflow > language > intent/slot > repair-loop); never hand-labeled)*
- **brittle success** × 1
- **recovered success** × 1

## 7 · Representative calls
- `bolna_246cd9f3` · human **success/high** · judge pending · *recovered success* · tags ['wrong_language_or_tone']
  - → detect caller language/register in the first 2 turns and switch the response style *(template-derived from tags)*
- `hero_001` · human **success/high** · judge pending · *brittle success* · tags ['wrong_language_or_tone'] · det. failures ['barge_in', 'latency_gap']
  - → detect caller language/register in the first 2 turns and switch the response style *(template-derived from tags)*

## 8 · Improvement queue *(evidence-backed; recommendations template-derived from observed tags)*
- `bolna_246cd9f3` (success/high, recovered success): detect caller language/register in the first 2 turns and switch the response style — evidence: ['wrong_language_or_tone']
- `hero_001` (success/high, brittle success): detect caller language/register in the first 2 turns and switch the response style — evidence: ['wrong_language_or_tone']

---
*Every number above is computed from committed artifacts. Heuristic = keyword task-completion; estimated = public per-unit prices; uncalibrated = judge before kappa; pending = honestly absent.*
