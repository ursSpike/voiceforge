# VoiceForge University — the ladder (v2, CANONICAL — agreed before any generation)

31 books, 00–30. One atomic idea each. Spoon-feeding is correct. Nothing assumes prior knowledge.

## The fixed skeleton (every book, same ritual)
1. **What is this** — plain language, baby intuition first
2. **Why does it exist** — the problem it solves
3. **How it works** — tiny runnable example, toy first, real repo data second
4. **Break it / change it** — modify one variable, watch behavior flip (no break-it = no learning)
5. **Where it fails** — the limits serious engineers probe
6. **How VoiceForge uses it** — connect back to the build
7. **Teach-back** — 3 self-check questions + 3 hackathon defense questions, answers collapsed

Every code cell: PREDICT out loud → run → explain the output in one sentence before moving.
Code style: heavily commented, every line earns its place, no clever one-liners.
Exit test per book: close it and explain the concept 2 minutes, no looking — what/why/how/where-it-fails/how-VF-uses-it. Can't? The book gets rewritten, not skimmed.
Each book ends with its **clean sentence** — the one you'd say in the room.

## Tier 1 — Survival (00–09): the vocabulary of the project
- **00 · What is VoiceForge?** — in: messy call; out: outcomes, scores, failure tags, costs, improvement pairs. *"VoiceForge is the layer after the call ends."*
- **01 · What is a call log?** — turns, speakers, timestamps, metadata; trace vs transcript. *"We judge the conversation trace, not just the transcript."*
- **02 · JSON, schemas, data contracts** — ugly dict → clean normalized_call; why structure is non-negotiable. *"One schema in, every tool downstream works."*
- **03 · Python/pandas for call data** — calls as rows; group, count, filter. *"A DataFrame lets me treat calls like benchmark rows."*
- **04 · Turns, gaps, overlap, latency** — FTO (one number per handoff); barge-in vs backchannel (the 100ms line); laggy (the 800ms line); p50/p90 not mean. *"Voice failures are measurable in milliseconds, not just judgeable from text."*
- **05 · ASR / LLM / TTS — the voice stack** — the relay, simulated with strings; where latency is born. *"Every turn is a three-model relay under a time budget."*
- **06 · Task success** — required fields; the polite call that failed. *"A call can sound great and still not do the job."*
- **07 · Failure tags & stress profiles** — taxonomy (language mismatch, interruption, KB gap…); scenario difficulty classes; failure distribution chart. *"Raw chaos becomes engineering signal through categories."*
- **08 · Cost per successful call** — unit costs × turns; failed calls shrink the denominator. *"Voice quality is a money number, not a feelings number."*
- **09 · Language conditions** — same task in EN / Hinglish / Tenglish = different error profiles. *"Multilinguality is an eval dimension, not a checkbox."*

## Tier 2 — The measurement engine (10–19)
- **10 · LLM-as-judge from zero** — fake judge first, then Gemini; PLUS the reliability contract: temperature 0, JSON output, response caching. *"A judge you can rerun and get the same answer is an instrument; anything else is a mood."*
- **11 · Evidence-based scoring** — no naked scores; reason + turn references or it didn't happen. *"A score you can't audit is a vibe."*
- **12 · Calibration: why human labels** — the circularity problem; why labels must be BLIND (label before seeing the judge). *"Human labels break the circle the judge can't break itself."*
- **13 · Confusion matrix, accuracy, precision, recall** — the four cells in plain words; which error type kills a failure-detector. *"Knowing WHICH way it's wrong matters more than how often."*
- **14 · Cohen's kappa from scratch** — chance agreement, the lazy-judge demo; PLUS the prevalence trap; PLUS a bootstrap CI so the number carries error bars. *"Kappa asks: better than luck — and the interval decides what I may claim."*
- **15 · Pilot calibration, said honestly** — presenting a mediocre number without fraud or shame; Landis–Koch bands; claim rules. *"Small sample, honest framing, disagreements shown proudly."*
- **16 · Improvement examples** — failure → better response → why; PLUS which failures are trainable vs config-fixable (dead air ≠ token choice). *"Every agent-side failure can propose its own fix."*
- **17 · Preference pairs** — chosen vs rejected; the single-axis diff rule (change one thing, like an ablation). *"A clean pair teaches one lesson; a messy pair teaches confusion."*
- **18 · DPO in baby language** — human example first, format second, name last; JSONL only, no training tonight. *"DPO teaches a model to prefer chosen over rejected — VoiceForge mines those pairs from real failures."*
- **19 · RLHF / RLAIF without mythology** — feedback-based alignment in plain words; why VoiceForge doesn't train live. *"VoiceForge builds the dataset layer for safe offline optimization."*

## Tier 3 — System & defense (20–30)
- **20 · The A/B loop** — same turns, v1 vs v2 policy, rescored; demo evidence vs statistical evidence. *"One closed-loop demonstration, not statistical proof — the shape is the point."*
- **21 · rubric.yaml & config-driven evals** — change the config, rerun, everything updates. *"What 'good' means lives in one editable file."*
- **22 · User simulators** — caller personas (hesitant, angry, code-switching); sim vs real logs. *"Simulation buys coverage, never validity."*
- **23 · Dataset hierarchy** — hero (theater) / public (validity) / synthetic (coverage) / provider logs (production). *"Each data source has a job; disclosure makes them all legitimate."*
- **24 · Annotation & ground truth** — assembly-as-truth, hand-verified timestamps, disclosure ethics. *"Annotation isn't cheating if you say exactly how the numbers were made."*
- **25 · Charts that matter** — the five demo charts; reading each aloud. *"A chart you can't narrate is decoration."*
- **26 · Dashboard mental model** — call list / detail / analytics / queue mapped to founder, engineer, ML person. *"Every view exists for a specific person's question."*
- **27 · Provider adapters** — mock Bolna-ish + Cartesia-ish inputs → one schema. *"Provider-neutral is an architecture fact, not a slide claim."*
- **28 · Talking like an engineer, not a bluffer** — the honest lines, drilled; sharp-question practice. *"I tested where the judge agrees with humans — and where it fails."*
- **29 · The 3-minute demo** — rehearsal: failure → timestamp → scorecard → better response → pair → chart → calibration → close.
- **30 · Post-hackathon path** — the side-project roadmap; what makes this a lane, not a weekend.

## Build order (sprints, not all tonight)
- **Sprint 1 (first build): 00–05.** The minimum language of the project.
- Sprint 2: 06–09 + 10–11. Sprint 3: 12–15. Sprint 4: 16–19. Sprint 5: 20–27. Pre-demo: 28–30.

## Deltas vs the GPT-5.5 draft (deliberate, small)
1. pandas now taught (03) instead of avoided.
2. Percentiles + both thresholds folded into 04 (one timing book, complete).
3. 10 absorbs the determinism/caching contract; 14 absorbs prevalence trap + bootstrap CI; 17 absorbs the single-axis rule; 16 absorbs trainable-vs-config-fixable.
4. Stress profiles land in 07 with failure tags (scenario vs performance distinction).

## Already-built material (don't read now, nothing wasted)
- notebooks A1–A3, B1–B4 → **optional deep-dive appendix** (stats + ML-from-scratch beneath books 13/14/18 — for when you want the math under the floorboards).
- old notebooks 00–06 → quarry material; absorbed into 04/10/14/17/18/28 as those get built, then retired.
