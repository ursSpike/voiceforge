# Prompt For Claude - VoiceForge Eval/Research Background Agents

You are working in `/Users/varsh/voiceforge`.

The design/frontend track is running separately. Do not touch it. This task is
core evaluation engineering and research only.

Read first:

1. `audit.md`
2. `docs/engineering_research_plan_jun13.md`
3. `docs/current_state.md`
4. `docs/limitations.md`
5. `docs/architecture.md`
6. `pipeline/demo_report.py`
7. `pipeline/score.py`
8. `pipeline/signals.py`
9. `pipeline/judge_run.py`

## Operating Mode

Run a read-only status audit first. Record SHA-256 hashes for every protected
artifact named in `docs/engineering_research_plan_jun13.md`.

Then launch five background agents with completely disjoint output directories.
Agents may read the repo and primary web sources. They may only write under
`experiments/jun13_eval/<their-name>/` and `reports/research_jun13/`.

Do not let agents edit production files or commit independently. The coordinator
audits all outputs and makes at most one docs/experiment commit after review.

No frontend work. No API calls. No packages. No dataset downloads. No changes to
frozen labels, judge artifacts, normalized calls, rubric, reports, or dashboard.

## Agent 1 - Reliability Metrics

Implement P0 from the plan:

- balanced accuracy / Youden's J;
- failure recall, precision, specificity, F1, MCC;
- kappa and raw agreement cross-check;
- deterministic bootstrap intervals;
- slice tables with minimum-n rules;
- tests for class imbalance and empty/tiny slices.

The agent must reproduce or refute these read-only observations:

- all: 32/45 agreement;
- hi-en: 22/31;
- English: 9/13;
- high human confidence: 24/29;
- medium human confidence: 8/16;
- balanced accuracy about 0.628;
- failure recall 0.500;
- failure precision about 0.308;
- MCC about 0.217.

It must explicitly flag the current unsupported sentence claiming code-switched
calls are the judge's least-reliable slice.

## Agent 2 - Grounded Outcome Probe

Implement P1 as an investigation only.

Inspect raw SpokenWOZ `goal`, `dialog_act`, system metadata, requested slots, and
booking state. Inspect Code-Mixed-Dialog `api_call`, no-result, and `R_` backend
rows. Produce:

- parse coverage;
- proposed additive contract;
- 10 examples;
- keyword-vs-grounded-vs-human comparison;
- unsupported/unknown cases.

Do not modify normalized calls or production outcomes.

## Agent 3 - Timing Sensitivity

Implement P2:

- threshold sweep;
- affected-call counts;
- event-count and rank stability;
- changed-call IDs;
- source/profile coverage;
- tests.

It must clearly state that this tests robustness, not correctness, because the
timed labeled slice has no human failures.

## Agent 4 - Annotation Operations

Implement P3:

- deterministic second-rater review queue;
- reason codes;
- no mutation of the first-rater CSV;
- summary by confidence/disagreement/tags.

Also write the P4 selective-judge design note. Do not run a model.

## Agent 5 - Primary Research Verifier

Verify the six papers in the plan from their primary pages. For each, write:

- citation and version/date;
- one short verified finding;
- exact relevance to VoiceForge;
- exact non-claim;
- one implementable experiment;
- data prerequisites;
- whether current artifacts are sufficient.

Do not use blogs, vendor marketing, search-result snippets, or secondary
summaries as evidence.

## Coordinator Audit

When all agents return:

1. verify no protected file changed;
2. run all experiment tests;
3. inspect at least three records from every generated JSON artifact;
4. reject unsupported causal or multilingual claims;
5. compare duplicated metrics across agents;
6. produce `reports/research_jun13/STATUS_REPORT.md`.

The status report must have:

- PASS;
- WARNINGS;
- BLOCKERS;
- ranked findings;
- one recommended production integration;
- exact next command, but do not execute integration.

Stop after the report and wait for Codex audit.

