# VoiceForge Engineering Research Plan - June 13

Status: research and isolated experiments only. The active frontend, frozen
labels, judge run, normalized pool, and committed demo artifacts remain
untouched until Codex audits a result and explicitly approves integration.

## Why This Round

VoiceForge already proves the core loop:

raw calls -> deterministic signals -> blind labels -> evidence-cited judge ->
binary calibration -> phenotypes -> improvement queue.

The next engineering question is not "can we add more scores?" It is:

> Can VoiceForge tell a team which evaluation signals are trustworthy, which
> calls require human review, and whether the outcome metric itself is grounded?

This round should improve trustworthiness and actionability without adding
generic features or touching the design work.

## Protected Boundary

Do not edit, regenerate, or rewrite:

- `web/dashboard_app.js`
- `web/dashboard_skin.css`
- `pipeline/dashboard.py`
- `out/dashboard.html`
- `claude_design_handoff/`
- `voiceforge_design_*/`
- `eval/labels_spike.csv`
- `eval/label_snapshot.json`
- `eval/label_manifest.json`
- `out/judge_results.json`
- `out/calls.json`
- `out/analytics.json`
- `out/demo_report_data.json`
- `data/normalized/`
- `rubric.yaml`

First-wave experiments write only under:

- `experiments/jun13_eval/<agent-name>/`
- `reports/research_jun13/`

No external API calls, model runs, package installs, dataset downloads, or
frontend work in the first wave.

## Immediate Truth Correction

The current calibration caption says that because 9 of 13 disagreements are
code-switched, the judge is least reliable there. That conclusion ignores the
sample denominator.

Read-only reproduction from the frozen artifacts currently gives:

- hi-en: 22/31 agreement = 71.0%;
- English: 9/13 agreement = 69.2%;
- Telugu-English: 1/1, too small to interpret.

Therefore this sample does **not** establish a code-switch reliability penalty.

The stronger observed slice is annotation confidence:

- high-confidence human labels: 24/29 agreement = 82.8%;
- medium-confidence human labels: 8/16 agreement = 50.0%.

This also needs careful wording: human confidence is available after annotation,
so it supports a second-rater review queue, not an automated deployment router.

The first engineering deliverable must reproduce these counts, add tests, and
prepare a truth-only patch to `pipeline/demo_report.py`. Do not regenerate the
dashboard until that patch is separately audited.

## Ranked Work

### P0 - Judge Reliability Audit

Build an isolated, deterministic reliability audit over the frozen labels and
judge results.

Required metrics:

- confusion matrix with `fail` treated as the risk class;
- raw agreement and Cohen's kappa with existing CI;
- balanced accuracy and Youden's J;
- failure recall, failure precision, specificity, F1, and MCC;
- exact counts and bootstrap intervals where meaningful;
- slice tables by language, source, stress profile, call length bucket, human
  confidence, and archetype;
- a minimum-n rule so tiny slices are never ranked as findings;
- explicit separation of counts from rate-normalized conclusions.

Current values to reproduce, not trust blindly:

- balanced accuracy approximately 0.628;
- failure recall 0.500;
- failure precision 0.308;
- specificity 0.757;
- MCC approximately 0.217.

Output:

- `experiments/jun13_eval/reliability/reliability_audit.py`
- `experiments/jun13_eval/reliability/reliability_audit.json`
- `experiments/jun13_eval/reliability/reliability_audit.md`
- tests using small fixtures, including prevalence imbalance.

The report must say that kappa, balanced accuracy, and the confusion matrix
answer different questions. Do not replace an uncomfortable kappa with a more
flattering metric.

### P1 - Source-Grounded Outcome Probe

The current keyword task-completion heuristic agrees with the human label on
only 25/45 calls. The highest-value core improvement is a stronger, inspectable
outcome contract.

Investigate without modifying normalized records:

#### SpokenWOZ

Use the already-cached raw fields:

- `goal`;
- per-turn `dialog_act`;
- system-turn `metadata` / final belief state;
- booking `booked` state;
- requested-slot informs.

Prototype field-level evidence:

- constraint supplied by user;
- constraint preserved in state;
- requested information supplied by agent;
- booking confirmed where required;
- terminal resolution.

#### Code-Mixed-Dialog

Use the already-cached hidden backend trace:

- `api_call ...`;
- `api_call no result`;
- `R_<slot>` knowledge-base rows;
- the spoken system response.

Prototype checks for:

- requested constraints represented in the API call;
- selected entity consistent with KB attributes;
- requested information actually spoken;
- no-result recovery;
- agent claims contradicting the backend trace.

Output:

- a coverage report over the 44 public-data calls in the frozen manifest;
- a proposed additive `outcome_evidence` contract;
- 10 manually inspectable examples;
- a disagreement table: keyword heuristic vs grounded probe vs human;
- a list of unsupported cases that must stay `unknown`.

Do not replace the production outcome field in this phase.

### P2 - Threshold Sensitivity Audit

VoiceForge's timing signals are deterministic, but the 100 ms overlap and
800 ms latency cutoffs are VoiceForge design choices. Measure robustness instead
of pretending the thresholds are universal.

Sweep, without editing `rubric.yaml`:

- overlap thresholds: 0, 100, 200, 300, 500 ms;
- lag thresholds: 500, 800, 1000, 1500, 2000 ms.

Report:

- event counts;
- affected-call counts;
- cluster-rank stability;
- call IDs that change classification;
- overlap between threshold settings;
- coverage and source/profile breakdown.

Do not correlate these events with binary failure without noting that the timed
labeled slice contains no human failures. This is a robustness audit, not
threshold validation.

### P3 - Annotation Review Queue

Use existing annotations to prioritize a second-rater pass.

Rank calls by:

1. human `medium` or `low` confidence;
2. judge-human disagreement;
3. heuristic-human disagreement;
4. multiple negative phenotype tags;
5. conflicting positive and negative evidence.

Output a deterministic review queue with reasons. This is annotation operations,
not a claim that the model knows when it is uncertain.

Do not overwrite the frozen first-rater labels. A second rater must write a new
artifact such as `eval/labels_rater2.csv`.

### P4 - Selective Judge Design, Spec Only

Write a design note for a future judge-confidence run:

- confidence elicitation method;
- coverage-risk curve;
- escalation threshold learned only on a development split;
- held-out evaluation;
- cost of human review;
- optional cheap-judge -> strong-judge -> human cascade.

No API call in this wave. No claim of a provable guarantee unless the paper's
assumptions and evaluation protocol are actually reproduced.

### P5 - Improvement Example Mining, After P1

Do not build DPO training or synthetic preference pairs yet.

First define a reviewable improvement draft:

- source call and evidence turns;
- exact rejected agent turn;
- one failure axis;
- proposed corrected turn;
- expected mechanism;
- `needs_human_review: true`;
- validation status under the grounded outcome probe.

Only proceed after P1 shows that the failure axis is grounded. Keep generated
pairs outside `out/queue.jsonl` until human-approved.

## Primary Research Map

### Balanced judge evaluation

**Balanced Accuracy: The Right Metric for Evaluating LLM Judges**
([arXiv:2512.08121](https://arxiv.org/abs/2512.08121)).

Use: add balanced accuracy / Youden's J beside kappa because the 37/8 class
imbalance makes overall accuracy incomplete. Non-claim: this paper does not
validate VoiceForge's judge.

### Selective evaluation and escalation

**Trust or Escalate: LLM Judges with Provable Guarantees for Human Agreement**
([arXiv:2407.18370](https://arxiv.org/abs/2407.18370)).

Use: product direction for confidence-aware routing and human escalation.
Non-claim: VoiceForge does not currently reproduce its simulated annotators or
formal guarantees.

### Turn-level plus dialogue-level TOD evaluation

**TD-EVAL**
([arXiv:2504.19982](https://arxiv.org/abs/2504.19982)).

Use: motivates source-grounded turn checks for conversation cohesion, backend
knowledge consistency, and policy compliance rather than terminal success only.
Non-claim: VoiceForge does not reproduce TD-EVAL or TOD Agent Arena.

### Full-duplex interaction metrics

**Full-Duplex-Bench**
([arXiv:2503.04721](https://arxiv.org/abs/2503.04721)).

Use: taxonomy alignment for pause handling, backchannels, turn-taking, and
interruption management; motivates the threshold sensitivity audit.
Non-claim: VoiceForge does not run the benchmark or validate its thresholds.

### Multilingual judge reliability

**How Reliable is Multilingual LLM-as-a-Judge?**
([arXiv:2505.12201](https://arxiv.org/abs/2505.12201)).

Use: requires language-normalized slice reporting and prevents raw disagreement
counts from becoming unsupported multilingual-bias claims.
Non-claim: its 25-language result is not evidence about VoiceForge's current
three language labels.

### Preserving human disagreement

**SemEval-2023 Task 11: Learning With Disagreements**
([arXiv:2304.14803](https://arxiv.org/abs/2304.14803)).

Use: second-rater schema should preserve both annotations and soft disagreement,
not silently overwrite them with a reconciled label.
Non-claim: VoiceForge's current single-rater confidence is not a substitute for
multiple annotations.

## Stop Conditions

Stop and report instead of continuing when:

- a result would require modifying a protected artifact;
- a paper cannot be verified from a primary source;
- a source-grounded rule has less than 80% parse coverage;
- an experiment silently drops calls;
- a slice has too few items to interpret;
- an improvement pair changes more than one failure axis;
- an API call, new package, or dataset download becomes necessary.

## Integration Gate

After the first wave, return one report with:

- exact files created;
- commands run;
- test output;
- protected-file hashes before and after;
- findings;
- null findings;
- unsupported claims removed;
- recommendation for which **one** experiment deserves production integration.

Do not integrate automatically.

