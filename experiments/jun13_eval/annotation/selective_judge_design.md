# Selective-Judge Design Note (SPEC ONLY — no model run)

**Status: design specification.** Nothing here was executed. No LLM-judge run,
no API call, no new labels. This note specifies *how* a selective (escalating)
judge would work for VoiceForge and what it would take to stand it up honestly.

## What "selective judge" means here

A selective judge answers the same per-call binary outcome question the blind
annotator answered (`success` / `fail`), but is allowed to **abstain** and
escalate to a more expensive evaluator when it is not confident. The goal is to
spend cheap automated judgment on the easy calls and reserve scarce human review
(or a stronger judge) for the hard ones — at a *controlled* accuracy cost.

Grounding: **Trust-or-Escalate** (Jung et al., arXiv:2407.18370) frames LLM-judge
"selective evaluation" with confidence-based abstention and a coverage–risk
trade-off, and offers (under its assumptions) human-agreement guarantees via
simulated annotators.

> **Honesty / scope limit.** VoiceForge does **not** currently reproduce
> Trust-or-Escalate's simulated annotators or its formal human-agreement
> guarantees. We borrow the *shape* of the method (confidence → coverage–risk →
> learned threshold → cascade) as a design target. Any "guarantee" language is
> aspirational until the development-split machinery below actually exists. We
> also do not claim the judge "knows" its own correctness; confidence is a proxy
> that must be empirically calibrated against human labels.

## 1. Confidence elicitation

The current judge already emits a per-call binary `label` with `reason` and
`evidence_turn_ids` at temperature 0. To make it *selective* we add a confidence
signal. Candidate methods, in increasing trust:

1. **Verbalized confidence** — ask the judge for a `confidence ∈ {low, medium,
   high}` or a 0–1 score in the same JSON. Cheap, but uncalibrated and known to
   be overconfident; usable only after calibration (below).
2. **Self-consistency / sampling agreement** — run the judge `k` times at
   temperature > 0 and use the agreement fraction (e.g. 5/5 vs 3/5) as
   confidence. More robust, `k`× cost.
3. **Pairwise / panel agreement** — multiple distinct prompts or models vote;
   confidence = vote margin. Highest cost; closest to Trust-or-Escalate's
   simulated-annotator spirit.

Whatever the source, the raw confidence is **monotonically calibrated** (e.g.
isotonic regression) against human agreement *on the development split only*, so
that "confidence 0.8" means "~80% agreement with a human."

## 2. Coverage–risk curve

Sort calls by calibrated confidence descending. For a threshold `τ`, the judge
**auto-decides** calls with confidence `≥ τ` (coverage) and **escalates** the
rest. Two curves, both estimated on held-out data:

- **coverage(τ)** = fraction of calls auto-decided.
- **selective risk(τ)** = judge–human disagreement rate *among auto-decided
  calls only*.

As `τ` rises, coverage falls and selective risk falls. The operating point is
chosen on this curve to hit a target risk (e.g. "≤ 5% disagreement on
auto-decided calls") at maximum coverage.

## 3. Escalation threshold — learned on a DEVELOPMENT split, never the test set

This is the load-bearing methodological rule.

- Split the human-labeled calls into **dev** and **test** (by `call_id`, fixed
  seed, documented). With only 46 labeled calls today this split is too small
  to be meaningful — see "Honest gap" below.
- Fit calibration **and** pick `τ*` **only on dev**, to satisfy the target risk.
- **Never** look at the test set while choosing `τ*`. Touching test during
  threshold selection invalidates the held-out estimate (the classic selective-
  prediction leak).

## 4. Held-out evaluation

Freeze `τ*` and the calibrator from dev. On the **untouched test split**, report:
`coverage`, `selective risk` (judge–human disagreement on auto-decided),
`escalation rate`, and the resulting human-review load. The test numbers are the
only ones quoted externally. Because `τ*` was chosen on dev, test coverage/risk
is an unbiased estimate of deployment behavior.

## 5. Cost of human review

Let `N` = calls, `e = 1 − coverage(τ*)` = escalation fraction, `c_h` = minutes
of human review per call. Human cost ≈ `N · e · c_h`. The selective judge's
value proposition is the area between "review everything" (`e = 1`) and the
chosen operating point, *at* the target risk. We also track the **error budget
spent on auto-decided calls** (`N · coverage · selective_risk`) so the cost
saving is always reported next to the accuracy given up — never in isolation.

## 6. Optional cheap → strong → human cascade

A three-tier escalation, each tier passing only its low-confidence residual up:

1. **Cheap judge** (small/fast model, verbalized confidence) auto-decides the
   high-confidence majority.
2. **Strong judge** (larger model and/or self-consistency panel) takes tier-1's
   escalations; auto-decides the ones it is now confident on.
3. **Human** takes only tier-2's residual — the genuinely ambiguous calls,
   which should correlate with the LeWiDi disagreement items.

Each tier needs its **own** dev-fit threshold; thresholds are *not* shared.
Total cost = Σ (tier volume × tier unit cost); total risk is the disagreement
on whatever each tier auto-decided, measured on test.

## Tie-in to this experiment's review queue

The deterministic review queue (`review_queue.py` / `review_queue.json`) is a
**rules-based, no-model precursor** to the human tier: it surfaces the calls a
selective judge would most likely escalate (judge↔human disagreement, low/medium
human confidence, conflicting/heavy negative tags, non-decisive labels). It uses
*observed* signals, not model self-confidence, and therefore makes no calibration
claims.

## Honest gap (what does NOT exist yet)

- No confidence field on the current judge output; elicitation is unimplemented.
- No calibrator, no dev/test split fit; 46 labeled calls is too few to learn a
  stable `τ*` — a realistic build needs substantially more human labels and a
  second rater (see `labels_rater2_schema.md`).
- No simulated annotators and no formal human-agreement guarantee à la
  Trust-or-Escalate. Treat all coverage/risk targets as design parameters to be
  *measured*, not as established results.

### References
- Jung et al., "Trust or Escalate: LLM Judges with Provable Guarantees for
  Human Agreement," arXiv:2407.18370.
- Leonardelli et al., "SemEval-2023 Task 11: Learning With Disagreements
  (LeWiDi)," arXiv:2304.14803.
