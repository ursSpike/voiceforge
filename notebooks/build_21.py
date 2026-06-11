#!/usr/bin/env python3
# Builds 21_rubric_config_driven.ipynb — "rubric.yaml & config-driven evals".
# The ONE atomic concept: what "good" means lives in one editable config; edit -> rerun ->
# everything updates. Same md()/code() emitter pattern as build_P00.py.
# Rerun: .venv/bin/python notebooks/build_21.py
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n")}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": s.strip("\n")}


C = []

# ============================================================ ACT 1 · ORIENTATION
C.append(md('''
# 21 · rubric.yaml & config-driven evals

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Open the real `rubric.yaml` and **read** it: every dimension, its **weight**, its **threshold**
2. State the one idea this book exists for: **what "good" means lives in one editable file**
3. Compute a call's **overall score** BY HAND as `sum(weight_i * score_i)` — then watch it move
4. Change **one weight** or **one threshold**, rerun, and predict *exactly* what shifts downstream
5. Point at the real code (`pipeline/signals.py`) that reads this file instead of hardcoding numbers

This is a config book. The whole lesson is small and sharp: a number that grades your agent
should live in **one place you can edit**, not scattered across ten Python files.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits)

`20 · the A/B loop  →  THIS: rubric.yaml & config-driven evals  →  22 · simulators`

- **Behind you (20):** you ran an A/B loop — version A vs version B, same scorecards, which won.
  But "which won" needs a definition of *winning*. Where did that definition live?
- **Here (21):** the definition. `rubric.yaml` is the single file that says which dimensions
  count, how much each weighs, and where each threshold sits. The A/B loop *read* this file.
- **Ahead (22):** simulators generate stress scenarios. The rubric you fix here is what scores
  the calls those simulators produce. Fix the ruler before you mass-produce the things it measures.

No number in this course floats in the void. This book is where the grading numbers come from.
'''))
C.append(md('''
## 3 — Baby intuition

Imagine three teachers grading the same essay. Teacher 1 cares most about grammar, Teacher 2
about argument, Teacher 3 about length. Same essay, three different grades — because each
carries a different **rubric** in their head.

Now imagine you wrote that rubric down on one sheet of paper: "grammar 50%, argument 40%,
length 10%, and 'too short' means under 200 words." Hand that sheet to any teacher and they
all produce the **same** grade. Change the sheet — bump argument to 60% — and *every* grade
recomputes the same way for everyone.

`rubric.yaml` is that sheet of paper for VoiceForge. It is the written-down answer to
"what does a good call even mean?" — and because it is one file, you can edit it on demo day.
'''))
C.append(md('''
## 4 — The formal version

A **config-driven eval** reads its definition of quality from a data file, never from numbers
typed into the scoring code. Concretely, `rubric.yaml` holds:

| piece | what it means | example from the real file |
|---|---|---|
| **dimension** | one axis you grade on | `barge_in`, `latency_gap`, `faithfulness` |
| **type** | `deterministic` (computed) or `judge` (LLM-scored) | `barge_in: deterministic` |
| **weight** | how much that dimension counts in the overall score | `barge_in: 0.20` |
| **threshold** | the cutoff a measurement is compared against | `laggy_ms: 800` |

The **overall score** of a call is `sum(weight_i × score_i)` across dimensions. Each dimension's
own `score_i` is a 0..1 number. Weights are chosen so they sum to 1, which keeps the overall
on a clean 0..1 scale. Change a weight or a threshold in the file, rerun, and every scorecard
and the dashboard recompute — no code edits.
'''))
C.append(md('''
## 5 — Why this exists (the failure it prevents)

Picture the alternative: the "laggy" cutoff of 800ms is typed directly into `signals.py`. The
weight 0.20 is typed into `score.py`. The barge-in threshold 100ms is typed into a third file.
Demo day arrives, a stakeholder says "latency matters more than that — show me" — and now you
are editing three Python files live, on stage, hoping you find every copy of the number.

Config-driven design moves all of those numbers into **one file** the code merely *reads*. The
payoff is the demo move at the heart of this book: open `rubric.yaml`, change one line, rerun,
watch the dashboard shift. That live edit only works because nothing is hardcoded. This book
is about earning that move.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In one sentence: what does `rubric.yaml` hold, and who reads it?
2. What are the three pieces attached to a dimension? (one says how it is scored, one says how
   much it counts, one is a cutoff)
3. Why would hardcoding the "laggy" cutoff into `signals.py` be a problem on demo day?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought of "the score" as something the code just computes.
After Act 1 you should hold a sharper picture: the *definition* of the score — which axes,
what weights, which cutoffs — is **data in one file**, and the code is a dumb reader of that
data. The A/B loop behind you used this file; the simulators ahead will be scored by it.

If "the rubric is the written-down meaning of good, and it lives in one editable file" feels
like your own sentence, continue.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of what rubric.yaml is. Producing the sentence is the
# learning; reading mine would only feel like it.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: read the real file, then score by hand

## First, look at it RAW

Course rule: before parsing anything, read the ugly input with your own eyes. `rubric.yaml`
is a small text file. We are going to print it verbatim — no YAML library yet — so the thing
you later parse is a thing you have already *seen*.
'''))
C.append(md('''
## PREDICT
We are about to print the raw text of `rubric.yaml`. Before you see it, commit:
roughly how many **dimensions** do you think a voice-agent rubric needs — 2, 6, or 20?
(There is no wrong answer; the point is to have a number in your head to compare against.)
'''))
C.append(code('''
# We locate the repo root by walking up until we find rubric.yaml. Hardcoding an absolute
# path would break the moment this notebook is run from a different folder.
from pathlib import Path
root = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "rubric.yaml").exists())
rubric_path = root / "rubric.yaml"

# Print the file verbatim. Reading raw text BEFORE parsing means the parsed object later has
# nothing hidden in it - you will recognise every key because you saw it as plain text first.
raw_text = rubric_path.read_text()
print(raw_text)
'''))
C.append(md('''
## Read it like a human (not like a parser)

Three things to notice in that text, in order:
- `dimensions:` is the heart — six lines under it, one per axis you grade on.
- Each dimension line carries a small `{...}` with a `type`, a `weight`, and sometimes a
  threshold like `threshold_overlap_ms` or `laggy_ms`.
- The comments (the `#` parts) are not decoration — they encode the *meaning* of each cutoff
  (`<=100ms = backchannel, ignored`). The file is written to be read by a human on demo day.

The header comment even says it out loud: *"Edit → rerun → every scorecard and the dashboard
update. Live-editable on demo day."* That sentence is this whole book.
'''))
C.append(md('''
## Now parse it — and see it is just a dict

YAML is a text format for nested key→value data. Parsing it gives back plain Python dicts and
lists — nothing exotic. We use the same loader the real pipeline uses (`yaml.safe_load`), so
what you get here is byte-for-byte what `signals.py` and `score.py` get.
'''))
C.append(code('''
# yaml.safe_load turns the text into nested dicts/lists. We use safe_load (not load) because
# it refuses to execute arbitrary tags - the same choice pipeline/signals.py makes.
import yaml
rubric = yaml.safe_load(raw_text)

# Show the top-level keys first. A config is just nested data; seeing the OUTERMOST layer
# before drilling in keeps you oriented (top-down beats getting lost in a deep print).
print("top-level keys:", list(rubric.keys()))
print("version:", rubric["version"])
'''))
C.append(code('''
# Drill into the part that matters: the dimensions block. type(...) confirms it is a dict
# keyed by dimension name - so dimension names are the keys you will index by everywhere.
dims = rubric["dimensions"]
print("type of dims:", type(dims).__name__)
print("dimension names:", list(dims.keys()))
print("how many dimensions:", len(dims))
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
You predicted a dimension count earlier. How many are actually there? Name two of them.
And: when you parsed the YAML, what plain Python type did `dimensions` turn out to be?
'''))
C.append(md('''
## Read ONE dimension fully

Tables and configs are read the same way: never as a wall. Pick one row, read every field of
it aloud. We will fully unpack `barge_in` — type, weight, threshold — so the *shape* of a
dimension is concrete before we loop over all six.
'''))
C.append(code('''
# Pull a single dimension out and look at all of its fields. Reading ONE fully (not skimming
# all six) is how you learn the shape every other dimension shares.
barge = dims["barge_in"]
print("barge_in raw:", barge)
print("  type      :", barge["type"])                 # deterministic = computed from timings, not judged
print("  weight    :", barge["weight"])               # how much barge_in counts toward the overall score
print("  threshold :", barge["threshold_overlap_ms"]) # overlap beyond this many ms counts as a barge-in
'''))
C.append(md('''
## PREDICT
The next cell prints all six dimensions as a neat table of `name | type | weight`.
Before you see it: do you expect the six weights to **sum to exactly 1.0**, or to something
random like 0.83? Write your guess in the YOUR TURN cell after.
'''))
C.append(code('''
# Walk every dimension and print its name, type, and weight in aligned columns. Looping (not
# hand-copying six lines) means this stays correct if someone adds a 7th dimension to the file.
print(f"{'dimension':<16} {'type':<14} {'weight':>6}")
print("-" * 38)
for name, spec in dims.items():
    # .get('type') / spec['weight']: every dimension is guaranteed type+weight by the file's
    # contract, so indexing weight directly is safe; type we read the same way for symmetry.
    print(f"{name:<16} {spec['type']:<14} {spec['weight']:>6}")
'''))
C.append(code('''
# YOUR TURN - PREDICT the weight sum BEFORE the next cell adds them up.
# Weights that sum to 1.0 keep the overall score on a clean 0..1 scale - but DO they here?
my_weight_sum_guess = None   # <- replace None with your guess, e.g. 1.0 or 0.83

if my_weight_sum_guess is None:
    print("fill in my_weight_sum_guess above, then re-run this cell.")
else:
    print("guess locked:", my_weight_sum_guess)
'''))
C.append(code('''
# Sum every weight. We collect them into a list first so we can SEE the addends, not just the
# total - a bare sum() hides which numbers went in (and a typo in the file would hide too).
weights = [spec["weight"] for spec in dims.values()]
print("the six weights:", weights)
total_weight = sum(weights)
print("sum of weights:", round(total_weight, 4))

# Compare against your committed guess - this is the metal-detector reading for your model.
if my_weight_sum_guess is not None:
    verdict = "matched" if abs(my_weight_sum_guess - total_weight) < 1e-9 else "DIFFERED"
    print("your guess", verdict, "- a sum of 1.0 is a DESIGN choice, not an accident")
'''))
C.append(md('''
## Why "sum to 1.0" matters

If the weights sum to 1.0 and every dimension's own score is between 0 and 1, then
`sum(weight × score)` is automatically between 0 and 1 too. That is what makes "0.74 overall"
mean something — it sits on the same scale as each part. If the weights summed to 1.7, an
"overall" could exceed 1 and the number would stop being comparable across calls.

So the weights summing to 1.0 is not luck — it is the invariant that keeps the overall score
honest. (Later, when you edit a weight, you will see this invariant is easy to break by hand.)
'''))
C.append(md('''
## The two kinds of dimension (deterministic vs judge)

Look back at the `type` column. Two values appeared:
- **deterministic** — scored by *arithmetic on the timings*. `barge_in`, `latency_gap`,
  `task_completion`. A computer measures overlaps and gaps; no opinion involved. This is the
  `pipeline/signals.py` territory you met in book 04.
- **judge** — scored by an *LLM reading the transcript*. `language_match`, `faithfulness`,
  `repair_quality`. These need a reader, not a stopwatch. This is `pipeline/judge.py` territory.

The rubric is where these two worlds are declared side by side with a shared weight scale, so
a stopwatch-measured dimension and an LLM-judged dimension can be combined into one number.
'''))
C.append(code('''
# Split the dimensions by type and total each side's weight. Grouping by type shows how much
# of the final grade is "machine-measured" vs "LLM-judged" - a real trust question for a demo.
det_weight = sum(s["weight"] for s in dims.values() if s["type"] == "deterministic")
judge_weight = sum(s["weight"] for s in dims.values() if s["type"] == "judge")
print("deterministic dimensions weigh:", round(det_weight, 4))
print("judge dimensions weigh:        ", round(judge_weight, 4))
print("together:", round(det_weight + judge_weight, 4))   # must equal the 1.0 we found above
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. What is the difference between a `deterministic` dimension and a `judge` dimension?
   Name one of each.
2. What fraction of the overall score is decided by deterministic dimensions vs judge ones?
3. Why does it matter that all the weights sum to 1.0?
'''))
C.append(md('''
## Manual-before-function: score a toy call BY HAND

Now the core move of the whole book. We have a definition of "good" (the weights). Let us
apply it to a single pretend call. Course rule: compute the overall score **by hand** first,
with every intermediate printed, before we wrap it in a function.

Our toy call already has a 0..1 score for each dimension (in a later book those scores come
from `signals.py` and `judge.py`; today we hand them to ourselves so we can focus on the
*combining*, which is the rubric's job).
'''))
C.append(md('''
## PREDICT
Here are the per-dimension scores for one toy call:

`barge_in=1.0, latency_gap=0.5, task_completion=1.0, language_match=1.0, faithfulness=0.8, repair_quality=0.6`

The weights are `0.20, 0.20, 0.20, 0.15, 0.15, 0.10`. The overall is `sum(weight × score)`.
Will the overall land closer to **0.5**, **0.8**, or **0.9**? Commit before the next cell.
'''))
C.append(code('''
# A toy call's per-dimension scores, each already on the 0..1 scale. We write them as a plain
# dict keyed by dimension name so each score lines up with its weight by NAME, not by position
# (position-matching is how a reordered file silently corrupts a score).
toy_scores = {
    "barge_in":        1.0,   # no barge-ins detected -> perfect on this axis
    "latency_gap":     0.5,   # one laggy reply dragged this down
    "task_completion": 1.0,   # all required fields captured
    "language_match":  1.0,   # answered in the caller's language
    "faithfulness":    0.8,   # mostly grounded, one small embellishment
    "repair_quality":  0.6,   # acknowledged the partial answer but over-asked once
}
for name, sc in toy_scores.items():
    print(f"{name:<16} score={sc}")
'''))
C.append(code('''
# YOUR TURN - PREDICT the overall score and lock it before we compute it.
# overall = sum(weight * score). You have all six weights and six scores above.
my_overall_guess = None   # <- replace None with your number, e.g. 0.5 / 0.8 / 0.9

if my_overall_guess is None:
    print("fill in my_overall_guess above, then re-run this cell.")
else:
    print("overall guess locked:", my_overall_guess)
'''))
C.append(code('''
# Manual weighted sum, every term printed so NOTHING is hidden inside one sum() call.
# We multiply each dimension's weight (from the rubric) by its toy score, and accumulate.
overall = 0.0
print(f"{'dimension':<16} {'weight':>6} x {'score':>5} = {'term':>6}")
print("-" * 40)
for name, spec in dims.items():
    w = spec["weight"]              # the weight comes from rubric.yaml - the single source of truth
    sc = toy_scores[name]          # the score comes from our toy call, matched by NAME
    term = w * sc                  # this dimension's contribution to the overall
    overall += term                # accumulate term by term so the running idea is visible
    print(f"{name:<16} {w:>6} x {sc:>5} = {term:>6.3f}")
print("-" * 40)
print("OVERALL (by hand):", round(overall, 4))

# Compare to your committed prediction - mismatch marks exactly where your mental model bent.
if my_overall_guess is not None:
    verdict = "matched" if abs(my_overall_guess - overall) < 0.05 else "DIFFERED"
    print("your guess", verdict)
'''))
C.append(md('''
## EXPLAIN gate
One sentence, out loud, in this shape: "the overall was ___ because the dimension that pulled
it down most was ___, which has weight ___." (Look at the `term` column — the smallest terms
tell the story.)
'''))
C.append(md('''
## Only NOW the function

You have done the weighted sum by hand and seen every term. The function below does *exactly*
that — no magic, just the loop you already ran, wrapped so we can call it repeatedly when we
start changing the rubric. Meeting the wrapper after the hand version means the wrapper holds
no mystery.
'''))
C.append(code('''
# The function is just the by-hand loop, parameterised by (rubric, scores) so we can feed it a
# DIFFERENT rubric in a moment and watch the answer move. That re-feeding is the whole demo.
def overall_score(rubric_dims, scores):
    # sum(weight_i * score_i) over every dimension - the exact arithmetic you did above.
    return sum(spec["weight"] * scores[name] for name, spec in rubric_dims.items())

# Confirm the function reproduces the hand number - a wrapper that disagrees with the hand
# version is a bug, and you would never know without this check.
print("function overall:", round(overall_score(dims, toy_scores), 4))
print("matches by-hand:", abs(overall_score(dims, toy_scores) - overall) < 1e-9)
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before Act 2 "the rubric" was an abstraction. Now you have: opened the real file, parsed it
into a plain dict, found six dimensions split into deterministic and judge, confirmed the
weights sum to 1.0, and combined per-dimension scores into one overall **by hand** before
wrapping it in a function. You can now read `rubric.yaml` and compute what it implies.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (the weighted-sum, or the det-vs-judge split)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: the live edit, the thresholds, and a trap

## The demo move: change ONE weight, rerun

This is the moment the whole book has been building to. We are going to *edit the rubric* —
in memory, the same effect as editing the file — and rerun the scorer. The atomic concept made
physical: **edit → rerun → the number updates, with zero changes to the scoring code.**

The change-one-thing rule applies: we move exactly one weight and watch the overall shift, so
we can attribute the shift to that one knob.
'''))
C.append(md('''
## PREDICT
We will make `latency_gap` matter more: raise its weight from `0.20` to `0.40`, and lower
`barge_in` from `0.20` to `0.0` to keep the weights summing to 1.0. Our toy call scored
**low on latency (0.5)** and **perfect on barge_in (1.0)**.

So: will the overall go **UP** or **DOWN**? Commit before running.
'''))
C.append(code('''
# YOUR TURN - PREDICT the direction before editing the rubric.
# We made the dimension the call is WORST at (latency, 0.5) count MORE, and a dimension it is
# perfect at (barge_in, 1.0) count nothing. Up or down?
my_direction_guess = ""   # <- type "up" or "down"

if my_direction_guess.strip().lower() not in ("up", "down"):
    print('type "up" or "down" above, then re-run.')
else:
    print("direction locked:", my_direction_guess.strip().lower())
'''))
C.append(code('''
# Deep-copy the parsed rubric so editing the copy never corrupts the original we loaded from
# disk. Mutating shared config in place is a classic way to make later cells lie.
import copy
edited_dims = copy.deepcopy(dims)

# The edit itself - this is exactly what changing two lines in rubric.yaml would do:
edited_dims["latency_gap"]["weight"] = 0.40   # latency now matters twice as much
edited_dims["barge_in"]["weight"] = 0.0       # barge_in zeroed so weights still sum to 1.0

# Always re-verify the invariant after an edit - a rubric whose weights drift off 1.0 produces
# overalls that are no longer comparable. Checking here catches a fat-fingered edit immediately.
new_sum = sum(s["weight"] for s in edited_dims.values())
print("edited weight sum:", round(new_sum, 4), "(must be 1.0)")
'''))
C.append(code('''
# Rerun the SAME scorer with the SAME toy scores - only the rubric changed. This single line
# is the live-edit demo: no scoring code touched, the definition of 'good' moved, rescore.
before = overall_score(dims, toy_scores)
after = overall_score(edited_dims, toy_scores)
print("overall BEFORE edit:", round(before, 4))
print("overall AFTER  edit:", round(after, 4))
print("moved by:", round(after - before, 4))

# Resolve your committed prediction.
if my_direction_guess.strip().lower() in ("up", "down"):
    went = "down" if after < before else "up"
    print("it went", went, "- matched your guess:", went == my_direction_guess.strip().lower())
'''))
C.append(md('''
## EXPLAIN gate
One sentence: the overall went **down** when you up-weighted latency. Say *why*, mentioning
both the score the call had on latency (0.5) and the fact that barge_in's perfect 1.0 stopped
contributing. This is the entire value of a config-driven rubric: opinions about what matters
become a number you can move.
'''))
C.append(md('''
## The other knob: thresholds (not just weights)

Weights decide how much a dimension *counts*. **Thresholds** decide what a measurement *means*
in the first place. `latency_gap` carries `laggy_ms: 800` — a reply slower than 800ms is
flagged "laggy". That cutoff is read straight from `rubric.yaml` by `pipeline/signals.py`.

Changing a threshold does not reweight anything — it changes *which calls trip the flag*. We
will take a few raw reply-gap measurements and re-classify them under two different cutoffs to
feel the difference.
'''))
C.append(md('''
## PREDICT
Four reply gaps from a toy call, in milliseconds: `[250, 600, 900, 1500]`.
Under the real cutoff `laggy_ms = 800`, **how many** count as laggy (gap > 800)?
Then under a stricter `laggy_ms = 500`, how many? Commit both counts.
'''))
C.append(code('''
# Raw reply-gap measurements (ms). We print them RAW first - the classification only makes
# sense once you have seen the unlabeled numbers it operates on.
reply_gaps_ms = [250, 600, 900, 1500]
print("raw reply gaps (ms):", reply_gaps_ms)

# Read the cutoff FROM the rubric, never as a literal 800 - this is the exact discipline
# signals.py follows: the threshold is config, so the same code obeys a different file.
laggy_ms = dims["latency_gap"]["laggy_ms"]
print("laggy cutoff from rubric:", laggy_ms, "ms")
'''))
C.append(code('''
# Classify each gap against the rubric's cutoff. A gap strictly greater than the cutoff is
# 'laggy' - matching signals.py, which flags gap_ms > laggy_ms (equal is still 'ok').
laggy_real = [g for g in reply_gaps_ms if g > laggy_ms]
print(f"with cutoff {laggy_ms}ms -> laggy gaps: {laggy_real}  (count {len(laggy_real)})")

# Now the SAME data under a stricter cutoff - we change ONLY the threshold, nothing else,
# and watch how many calls newly trip the flag. This is the threshold knob in isolation.
strict_cutoff = 500
laggy_strict = [g for g in reply_gaps_ms if g > strict_cutoff]
print(f"with cutoff {strict_cutoff}ms -> laggy gaps: {laggy_strict}  (count {len(laggy_strict)})")
'''))
C.append(md('''
## OBSERVE + EXPLAIN
Did your two counts hold? The data never changed — only the line in the config did. A stricter
threshold makes more replies "laggy" without anyone touching the timing code. That is the same
lever a demo-day stakeholder pulls when they say "no, 500ms is the bar for us."
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
What is the difference between editing a **weight** and editing a **threshold**? (One changes
how much a dimension counts; one changes what a raw measurement is *labeled*.) Give one
sentence each, with an example dimension for each.
'''))
C.append(md('''
## BREAK-IT (guided) — break the weights-sum invariant

We just relied on weights summing to 1.0. What happens if an edit forgets that? Let us bump
`latency_gap` to 0.40 **without** lowering anything else, so the weights now sum to 1.2. The
code will not crash — and that is exactly the danger.
'''))
C.append(md('''
## PREDICT
With weights summing to **1.2** instead of 1.0, our toy call scored well overall.
Will the new overall be able to exceed **1.0**? Crash, or silently-wrong number? Commit.
'''))
C.append(code('''
# BREAK-IT (guided) - we deliberately violate the sum-to-1.0 invariant and DO NOT fix it yet.
broken_dims = copy.deepcopy(dims)
broken_dims["latency_gap"]["weight"] = 0.40   # bumped, but nothing else lowered -> sum drifts

broken_sum = sum(s["weight"] for s in broken_dims.values())
print("broken weight sum:", round(broken_sum, 4), "(no longer 1.0!)")

# The scorer runs happily on a malformed rubric - no exception. The number it returns is the
# bug: it can now exceed 1.0, so it is no longer comparable to a normal scorecard.
broken_overall = overall_score(broken_dims, toy_scores)
print("overall with broken weights:", round(broken_overall, 4))
print("can it exceed a clean max of 1.0?", broken_overall > 1.0)
'''))
C.append(md('''
## Reading the break (silent wrongness, not a crash)

No traceback. No red. The scorer returned a number — and the number is *wrong* in the sense
that it no longer lives on the 0..1 scale every other call's score lives on. A 0.95 from this
broken rubric is not comparable to a 0.95 from the real one.

This is the failure mode that matters in evals: **the config compiled fine and the math ran,
but the meaning is corrupted.** Crashes you notice; a drifted weight-sum you ship. The fix is
a guard that *checks the invariant*, which we add now.
'''))
C.append(code('''
# The fix: validate the rubric before trusting any score from it. A real pipeline runs this at
# load time so a malformed rubric.yaml is rejected loudly instead of silently skewing grades.
def validate_weights(rubric_dims, tol=1e-6):
    total = sum(s["weight"] for s in rubric_dims.values())
    # we RAISE rather than return False so a bad config cannot be ignored downstream -
    # turning silent wrongness back into a loud, friendly crash.
    if abs(total - 1.0) > tol:
        raise ValueError(f"weights sum to {total:.4f}, expected 1.0 - fix rubric.yaml")
    return True

print("real rubric valid?", validate_weights(dims))           # passes - sums to 1.0
try:
    validate_weights(broken_dims)                             # should raise on the broken one
except ValueError as e:
    print("broken rubric correctly rejected:", e)
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
Why is the broken-weights bug *more dangerous* than a crash? And what does `validate_weights`
do to convert that silent wrongness back into a loud failure?
'''))
C.append(md('''
## YOUR break now

Author your own rubric edit. Pick ONE dimension, change its weight to whatever you like, and
predict (in the comment) whether the weights still sum to 1.0 and whether `validate_weights`
will accept or reject your edit. Then run it. The cell is guarded so an unfilled edit runs clean.
'''))
C.append(code('''
# YOUR TURN - self-authored BREAK-IT: edit one weight and predict the validator's verdict.
# my prediction: <write here: does it still sum to 1.0? accept or reject?>

my_rubric = copy.deepcopy(dims)

# Pick a dimension and a new weight by filling BOTH variables. Left as None, the cell just
# reports the original (still-valid) rubric, so a fresh notebook runs clean.
which_dimension = None   # <- e.g. "faithfulness"
new_weight = None        # <- e.g. 0.30

if which_dimension is not None and new_weight is not None:
    my_rubric[which_dimension]["weight"] = new_weight   # apply your edit
    s = sum(d["weight"] for d in my_rubric.values())
    print(f"after your edit, weights sum to {round(s, 4)}")
    try:
        validate_weights(my_rubric)
        print("validator ACCEPTS your rubric")
    except ValueError as e:
        print("validator REJECTS your rubric:", e)
else:
    print("set which_dimension and new_weight above to author your edit (optional).")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this book is built on

**The wrong belief:** "a higher weight on a dimension always raises a call's overall score."

It feels right — weight is importance, and importance sounds like points. But weight is a
*multiplier on that dimension's score*, and the score can be **low**. Up-weighting a dimension
the call is BAD at pulls the overall **down**, not up. You already saw it: up-weighting latency
(score 0.5) lowered the overall. Let us prove the both-directions truth in one cell.
'''))
C.append(code('''
# Same toy call, same dimension up-weighted to 0.40 - but we test it on TWO different calls:
# one that is GOOD at latency and one that is BAD at it. The weight is identical; the direction
# of the effect flips. That flip is the proof the belief 'more weight = more points' is false.
heavy_latency = copy.deepcopy(dims)
heavy_latency["latency_gap"]["weight"] = 0.40
heavy_latency["barge_in"]["weight"] = 0.0   # keep the sum at 1.0 so overalls stay comparable

scores_good_latency = {**toy_scores, "latency_gap": 1.0}   # this call is FAST
scores_bad_latency  = {**toy_scores, "latency_gap": 0.2}   # this call is SLOW

print("GOOD-latency call: base", round(overall_score(dims, scores_good_latency), 3),
      "-> heavy", round(overall_score(heavy_latency, scores_good_latency), 3))
print("BAD-latency  call: base", round(overall_score(dims, scores_bad_latency), 3),
      "-> heavy", round(overall_score(heavy_latency, scores_bad_latency), 3))
print("same weight edit: one overall rose, the other fell -> weight is a multiplier, not a bonus")
'''))
C.append(md('''
## The reveal
A weight does not add points; it decides **how loudly a dimension's own score speaks**. Raise
the weight and a good score speaks louder (overall up), but a bad score also speaks louder
(overall down). "Importance" cuts both ways. This is why you cannot game a rubric by just
cranking the weight on something — you also expose yourself harder when you are bad at it.
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before Act 3 the rubric was a static thing you read. After Act 3 it is a set of **knobs**: you
moved a weight and the overall shifted (live-edit, no code touched); you moved a threshold and
the laggy-count shifted; you broke the sum-to-1.0 invariant and saw silent wrongness, then
guarded it; and you proved that more weight is not more points — it is a louder microphone.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the live edit, or the weight-is-a-multiplier trap)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this lives, who you explain it to, and the bar

## Where this lives in VoiceForge (the real wiring)

This is not a toy. The file you parsed is the actual `rubric.yaml` at the repo root, and the
real code reads it the same way you just did:

- **`pipeline/signals.py`** has a `load_rubric()` and pulls `dims["barge_in"]["threshold_overlap_ms"]`
  and `dims["latency_gap"]["laggy_ms"]` — the deterministic thresholds are read, never hardcoded.
  Its docstring says it out loud: *"all thresholds read from rubric.yaml, never hardcoded at call sites."*
- **`pipeline/judge.py`** reads `rubric["judge"]` for the model and temperature of the LLM judge.
- **`pipeline/score.py`** is the merge step: `overall = sum(weight_i × score_i)` — the exact
  weighted sum you computed by hand — combining deterministic and judged dimensions into one
  scorecard, with weights live-editable so a rerun updates the dashboard.

One file. Three consumers. Edit the file, rerun, everything downstream recomputes.
'''))
C.append(code('''
# Prove the signals.py linkage is real, not a claim: read the same two thresholds signals.py
# reads, straight from the rubric you loaded. If these match what book 04 used, the wiring holds.
print("barge_in threshold_overlap_ms:", dims["barge_in"]["threshold_overlap_ms"], "(signals.py barge-in cutoff)")
print("latency_gap laggy_ms:         ", dims["latency_gap"]["laggy_ms"], "(signals.py laggy cutoff)")
print("judge model:                  ", rubric["judge"]["model"], "(judge.py reads this)")
print("judge temperature:            ", rubric["judge"]["temperature"], "(0 = deterministic judging)")
'''))
C.append(md('''
## The three recurring calls, scored through this rubric

The course cast — **call_A** (clean English success), **call_B** (Hinglish partial), **call_C**
(Telugu-English failure with an agent barge-in) — all get graded by *this* file. call_C's
agent-interrupts-caller moment is exactly what the `barge_in` threshold (100ms) catches, and
its weight (0.20) is how much that failure costs in the overall. The rubric is the bridge from
"the agent talked over the caller" to "the call scored 0.4".
'''))
C.append(code('''
# Toy scorecards for the three cast calls, then grade all three through the SAME rubric. Using
# one rubric for all calls is the point: comparability comes from a shared definition of good.
cast_scores = {
    "call_A": {"barge_in": 1.0, "latency_gap": 1.0, "task_completion": 1.0,
               "language_match": 1.0, "faithfulness": 1.0, "repair_quality": 0.9},  # clean success
    "call_B": {"barge_in": 1.0, "latency_gap": 0.7, "task_completion": 0.5,
               "language_match": 0.8, "faithfulness": 0.8, "repair_quality": 0.6},  # partial
    "call_C": {"barge_in": 0.0, "latency_gap": 0.4, "task_completion": 0.0,
               "language_match": 0.3, "faithfulness": 0.6, "repair_quality": 0.3},  # failure
}
for call_id, scores in cast_scores.items():
    # one overall per call, all via the identical rubric -> the numbers are comparable by design
    print(f"{call_id}: overall {round(overall_score(dims, scores), 3)}")
'''))
C.append(md('''
## PREDICT (course-level)
You just graded the cast under the *real* rubric. If a stakeholder decided
**task_completion is everything** and cranked its weight up (lowering others), which call's
overall would fall the **hardest** — A, B, or C? Write your reasoning in the next cell.
'''))
C.append(code('''
# YOUR TURN - course-level prediction, stored for you to verify by editing the rubric yourself.
# Hint: look at the task_completion scores above (A=1.0, B=0.5, C=0.0) before answering.
my_cast_prediction = ""   # which call falls hardest if task_completion is up-weighted, and WHY

if len(my_cast_prediction.strip()) < 20:
    print("write your prediction above (which call + why), then re-run.")
else:
    print("PREDICTION STORED:", my_cast_prediction)
'''))
C.append(md('''
## Where a config-driven rubric still fails (honesty about the design)

- **Weights are opinions wearing a number costume.** `0.20` for barge_in looks objective, but
  someone *chose* it. The file makes the choice explicit and editable — it does not make it
  correct. Defend the weights, do not hide behind them.
- **Sum-to-1.0 is a convention the file does not enforce by itself.** You saw it break silently.
  A real loader needs the `validate_weights` guard, or a fat-fingered edit ships.
- **A rubric cannot grade a dimension it does not list.** If "interrupting politely vs rudely"
  matters but no dimension captures it, no weight will ever surface it. The rubric bounds what
  "good" can even mean — adding the right dimensions is a harder problem than tuning weights.
'''))
C.append(md('''
## The concept at three levels (same idea, three audiences)

- **To a beginner:** "the rules for grading a call live on one sheet of paper you can edit; change
  the sheet and every grade recomputes the same new way."
- **To an engineer:** "evaluation config is externalised to `rubric.yaml`; `signals.py`,
  `judge.py`, and `score.py` read dimensions/weights/thresholds from it, so `overall =
  Σ wᵢ·scoreᵢ` is re-parameterised by editing data, not code. Weights sum to 1.0 (validated)."
- **To a founder:** "what 'good' means is a single editable file, so on demo day we change the
  definition of quality live — bump latency, rerun — and the dashboard moves, no deploy. Our
  grading criteria are transparent and auditable, not buried in code."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "Your weights look arbitrary — why 0.20 for barge_in?"**
<details><summary>answer</summary>They are deliberate, not arbitrary: deterministic dimensions (the things we can measure exactly) total 0.60, judged dimensions 0.40, and all six sum to 1.0 so the overall stays on a 0..1 scale. The number is a defensible choice living in one file — and I can change it live and show you the effect right now.</details>

**2. "If I disagree that latency matters this much, what do you do?"**
<details><summary>answer</summary>I open rubric.yaml, raise latency_gap's weight, lower another to keep the sum at 1.0, rerun — and every scorecard plus the dashboard recompute with zero code changes. The rubric is config precisely so disagreement is a one-line edit, not an engineering ticket.</details>

**3. "How do you stop a bad edit from silently corrupting every score?"**
<details><summary>answer</summary>A load-time validator: weights must sum to 1.0 within tolerance or it raises. I demoed it — a rubric that sums to 1.2 still computes a number, but it exceeds the 0..1 scale and is no longer comparable, so we reject it loudly instead of shipping silent wrongness.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own the full picture: `rubric.yaml` is the real, single source of grading config;
`signals.py` / `judge.py` / `score.py` read it; the overall is the weighted sum you computed by
hand; editing a weight or threshold reshapes every grade with no code change; and you can defend
the weights, the validator, and the live-edit move to a skeptical room.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. What `rubric.yaml` holds (dimensions · weights · thresholds) and the three files that read it
2. How a call's **overall** score is computed from the rubric (the weighted sum)
3. The difference between editing a **weight** and editing a **threshold**, with an example each
4. The trap: why "more weight" is not "more points" (it is a multiplier, both directions)
5. The live-edit demo move, and the validator that keeps a bad edit from silently corrupting scores

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you would say in a room about config-driven evals

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"What 'good' means lives in one editable file."**

If yours captures that in your own words — that the definition of a good call is data in
`rubric.yaml`, read by the pipeline, editable live — this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "21_rubric_config_driven.ipynb"   # <- this notebook's filename
nb_path = next(p for p in [Path.cwd()/name, Path.cwd()/"notebooks"/name,
               *[a/"notebooks"/name for a in Path.cwd().parents]] if p.exists())
nb = json.loads(nb_path.read_text())
S = lambda c: c["source"] if isinstance(c["source"], str) else "".join(c["source"])
pool = [c for c in nb["cells"] if "SELF-AUDIT" not in S(c) and "banned phrase" not in S(c).lower()]
md = [c for c in pool if c["cell_type"]=="markdown"]; co = [c for c in pool if c["cell_type"]=="code"]
cnt = lambda m, g: sum(1 for c in g if m in S(c))
reason = lambda c: any(len(l.strip("# ").split())>=4 for l in S(c).splitlines() if l.strip().startswith("#"))
t = " ".join(S(c).lower() for c in pool)
checks = {
 "total cells 50-90": (len(nb["cells"]), 50<=len(nb["cells"])<=90),
 "specific checkpoints >=5": (cnt("CHECKPOINT", md), cnt("CHECKPOINT", md)>=5),
 "act knowledge-flow cps >=4": (cnt("knowledge-flow checkpoint", md), cnt("knowledge-flow checkpoint", md)>=4),
 "predict prompts >=8": (cnt("PREDICT", pool), cnt("PREDICT", pool)>=8),
 "break-it >=2": (cnt("BREAK-IT", co)+cnt("EXPECTED FAILURE FOR LEARNING", co), cnt("BREAK-IT", co)+cnt("EXPECTED FAILURE FOR LEARNING", co)>=2),
 "wrong-intuition trap >=1": (cnt("WRONG-INTUITION TRAP", md), cnt("WRONG-INTUITION TRAP", md)>=1),
 "learner cells >=6": (cnt("YOUR TURN", co), cnt("YOUR TURN", co)>=6),
 "reasoning comments all": (sum(map(reason, co)), all(map(reason, co)) if co else False),
 "3-level explanation": (1, all(w in t for w in ("beginner","engineer","founder"))),
 "teach-back": (cnt("TEACH-BACK", md), cnt("TEACH-BACK", md)>=1),
 "clean sentence": (1, "clean sentence" in t),
 "banned phrases =0": (sum(bool(re.search(r"\\b"+w+r"\\b", t)) for w in ["obviously","as you know","simply","intuitively"]), not any(re.search(r"\\b"+w+r"\\b", t) for w in ["obviously","as you know","simply","intuitively"])),
}
print(f"{'metric':<28}{'n':>5}  verdict"); ok=True
for k,(n,p) in checks.items():
    ok &= p; print(f"{k:<28}{n:>5}  {'PASS' if p else 'FAIL'}")
print("AUDIT:", "ALL PASS - now do the teach-back" if ok else "FAIL")
'''))
C.append(md('''
## Next on the ladder

**21 done** (pending your teach-back) → **22 · simulators** — you fixed the ruler; next you
mass-produce the stress scenarios it measures. Every call a simulator generates gets graded by
the `rubric.yaml` you just learned to read, edit, and defend.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "21_rubric_config_driven.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
