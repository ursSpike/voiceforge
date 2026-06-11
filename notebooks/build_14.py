#!/usr/bin/env python3
# Builds 14_cohens_kappa_from_scratch.ipynb per _BUILD_SPEC.md (four acts, marker minimums).
# Concept: chance-corrected agreement, the prevalence trap, a from-scratch bootstrap 95% CI.
# Rerun: .venv/bin/python notebooks/build_14.py
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
# 14 · Cohen's kappa from scratch

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Show **why raw agreement is broken** — a judge that measures nothing can score 90%
2. Compute the **chance floor** `p_e` BY HAND from each rater's base rates
3. Write the **kappa formula** `(p_o − p_e) / (1 − p_e)` and read it as "headroom above luck captured"
4. Walk into and out of the **prevalence trap** — same competence, lower kappa as classes imbalance
5. Build a **bootstrap 95% CI from scratch** so the number carries error bars
6. Place a kappa on the **Landis–Koch** bands and state exactly what you may claim

One atomic idea, stated three ways and never let go: **kappa is agreement after you subtract
the agreement luck would have produced anyway, and the interval decides what you may claim.**
'''))

C.append(md('''
## 2 — Knowledge map (previous → CURRENT → next)

`13 confusion matrix  →  14 Cohen's kappa from scratch  →  15 pilot calibration`

- **From 13:** you can already read a 2×2 confusion matrix (the four cells of human-vs-judge
  agree/disagree). Kappa is a single number *built out of* that 2×2 — so 13 is the raw table,
  14 is the one honest summary of it.
- **This book (14):** turns "they agree a lot" into "they agree *more than luck* — and here is
  the error bar on that claim."
- **Into 15:** pilot calibration is the act of standing up and *reporting* a kappa without fraud
  or shame. You cannot present a number honestly until you can build it and bound it — that is
  why 14 comes first.

No lesson floats in the void. This one sits between the table and the claim.
'''))

C.append(md('''
## 3 — Baby intuition

Two people grade the same 100 calls "task completed: yes / no". They match on 88 of them.
Sounds like a trustworthy pair of graders — until you learn that 95 of the calls succeeded,
and one grader is a sleepy intern who writes **"yes" on every single line without reading**.

The intern measured nothing. Yet they will agree with any sensible grader about 95% of the
time, because *almost everything is a yes anyway*. The agreement came from the **prevalence**
of "yes", not from skill. So raw agreement, on its own, cannot tell a skilled grader from a
sleepy one. We need a number that **subtracts the agreement luck hands you for free** and
reports only what is left.

That leftover, rescaled, is **Cohen's kappa**.
'''))

C.append(md('''
## 4 — The formal version

Two raters label the same N items into the same two classes (call them 0 and 1). Define:

| symbol | meaning | how to get it |
|---|---|---|
| `p_o` | **observed** agreement | fraction of items where the two labels match |
| `p_e` | **expected** (chance) agreement | what they'd match by luck, from each one's base rates |
| `κ` (kappa) | chance-corrected agreement | `(p_o − p_e) / (1 − p_e)` |

The chance floor, for two classes:

> `p_e = P(both say 1 by luck) + P(both say 0 by luck) = a₁·b₁ + a₀·b₀`

where `a₁` is rater A's rate of saying 1, `b₁` is rater B's rate of saying 1, and
`a₀ = 1 − a₁`, `b₀ = 1 − b₁`. Reading of κ:

- **κ = 1** → perfect agreement (captured all the headroom above luck)
- **κ = 0** → exactly luck-level (captured none of it)
- **κ < 0** → *worse* than luck (they actively disagree more than coin flips would)

Everything below this point is us earning each of these symbols by hand before any library
touches them.
'''))

C.append(md('''
## 5 — Why this exists (the one rule that makes the rest make sense)

There is a single fact under this entire book, and it is worth saying before any code:

> **Agreement you would have gotten anyway is not evidence of anything.**

If two coins both come up heads 90% of the time, they "agree" about 82% of the time while
communicating nothing. A metric that rewards that is measuring the *prevalence of heads*, not
the *relationship between the coins*. Kappa's whole job is to set that free agreement to zero
and measure only what is above it.

We will use exactly **one binary question** all the way through, because that is the real
VoiceForge pilot question (`eval/kappa.py`): **"was the task completed on this call?"**
'''))

C.append(md('''
## 6 — The encoding we lock now (so no cell is ambiguous later)

One convention, fixed for the whole notebook, written down so confusion-matrix cells can never
be read two ways:

- **`1` = task completed** (the call succeeded on the required-fields checklist)
- **`0` = task not completed**

Two raters in this book:
- **`human`** — a person labeling blind (our future Spike from the spec / `eval/labels_spike.csv`)
- **`judge`** — the LLM judge's verdict on the same calls

Same items, **same order**, aligned by `call_id`. (Misalignment is the silent killer of kappa;
we will break it on purpose in Act 3.)
'''))

C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never syntax.

# We pin a seed so every run of this notebook produces the SAME numbers - a moving target
# can't be reasoned about, and "predict before run" needs the answer to hold still.
import random
random.seed(14)

# A reasoning aid we'll reuse: print a label and value together so output is self-describing
# rather than a bare number floating under a cell.
print("encoding locked: 1 = task completed, 0 = not completed")
'''))

C.append(md('''
## PREDICT
Below are two label lists for **6 toy calls** (1 = completed, 0 = not). The `human` and the
`judge` lists. Eyeball them and commit to a number: **on how many of the 6 do they match?**
Then commit to the fraction. Write both in the next cell before running anything.
'''))

C.append(code('''
# Tiny RAW data first - 6 calls, small enough to verify every position by eye.
# Course rule: see the ugly input before any transformation touches it.
human = [1, 1, 0, 1, 0, 1]   # what the blind human labeler wrote, call 0..5
judge = [1, 0, 0, 1, 0, 1]   # what the LLM judge returned on the SAME 6 calls

# We print them stacked so each COLUMN is one call - the unit of agreement is the call.
print("call #:", list(range(6)))
print("human :", human)
print("judge :", judge)
'''))

C.append(code('''
# YOUR TURN - predictions go in BEFORE the computing cell, stored so a later cell can
# confront your guess with reality. The gap between guess and truth is the entire lesson.
my_matches_prediction = None     # <- how many of the 6 positions match? (an integer 0..6)
my_po_prediction = None          # <- that count divided by 6 (a fraction, e.g. 0.83)

if my_matches_prediction is None or my_po_prediction is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("locked:", my_matches_prediction, "matches ->", my_po_prediction)
'''))

C.append(md('''
## Observed agreement `p_o`, by hand

No formula yet — just *counting matches*. We walk the two lists position by position and tally
where they are equal. This is the only honest definition of "they agreed": same call, same
label.
'''))

C.append(code('''
# Manual p_o: count matches by walking both lists together, position by position.
# We do it the long way (no shortcut) because p_o IS just "count of equal positions over N",
# and seeing the loop makes that definition concrete before any one-liner hides it.
match_count = 0
for i in range(len(human)):          # i is the call index; both lists are aligned by it
    if human[i] == judge[i]:         # equal label on the same call = one agreement
        match_count += 1
        print(f"call {i}: human={human[i]} judge={judge[i]}  MATCH")
    else:
        print(f"call {i}: human={human[i]} judge={judge[i]}  differ")

n = len(human)                       # N = number of items; p_o is a fraction of it
p_o = match_count / n
print(f"\\nmatches: {match_count}/{n}  ->  p_o = {p_o:.3f}")
'''))

C.append(code('''
# Confront YOUR prediction with the computed truth - the metal-detector reading.
# Guarded so an UNFILLED notebook still runs clean (the prediction may be None).
if my_matches_prediction is not None:
    verdict = "matched" if my_matches_prediction == match_count else "DIFFERED"
    # we report the gap, not a grade - a wrong prediction marks where your model needs work
    print(f"your match-count prediction {verdict} (you said {my_matches_prediction}, truth {match_count})")
'''))

C.append(md('''
## EXPLAIN gate
One sentence, out loud, in this shape: *"p_o took ___ and produced ___ because ___."*
(If it does not mention "the fraction of calls where the two labels are equal," say it again.)
'''))

C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What does `p_o` count, in plain words?
2. The two lists must be in the **same order**. Why would shuffling one of them silently
   produce a wrong `p_o` *without any error*?
3. `p_o = 0.83` here. Is that "good agreement"? (Trick question — hold your answer; the next
   act is about why you cannot answer this yet.)
'''))

C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: "two graders matching 88% of the time is good agreement."
After Act 1 you should hold a doubt: that 88% might be **prevalence, not skill** — and you now
have a precise name for the honest part of it (`p_o`) and a promise that the next act subtracts
the dishonest part (`p_e`). You also locked an encoding (1 = completed) so nothing downstream
is ambiguous.

If that doubt feels real in your own words, continue. If not, re-read the sleepy-intern story.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of why raw agreement might lie. Not mine - yours.
# Producing the sentence is the learning; reading mine would only feel like it.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: it nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: the lazy judge, the chance floor, and the formula

## The lazy constant judge (raw agreement caught red-handed)

Time to prove raw agreement is broken, not just claim it. We build the worst possible judge:
one that **says "completed" on every call** — a constant, measuring nothing — and point it at a
dataset where most calls really did complete. Then we read its raw agreement.
'''))

C.append(md('''
## PREDICT
The dataset: **20 calls, 18 of them genuinely completed** (so prevalence of 1 is 0.90). The
"lazy judge" outputs **1 on every single call** — it never looks at anything.

What raw agreement (`p_o`) will this brain-dead judge score against the truth? Commit to a
number before the next cell.
'''))

C.append(code('''
# Build the skewed truth: 18 completed (1), 2 not (0). We hardcode the COUNTS, not a random
# draw, so the prevalence is exactly 0.90 and the lesson is not muddied by sampling noise.
truth_skew = [1] * 18 + [0] * 2          # 18 successes, 2 failures = 90% prevalence of "1"

# The lazy judge: a constant function. It contains ZERO information about any call.
# We write it as "1 for every item" to make the emptiness visible in the code itself.
lazy_judge = [1 for _ in truth_skew]

# Raw agreement of the lazy judge against truth - reusing the same match-fraction idea.
lazy_matches = sum(1 for i in range(len(truth_skew)) if truth_skew[i] == lazy_judge[i])
lazy_p_o = lazy_matches / len(truth_skew)
print(f"lazy judge raw agreement: {lazy_matches}/{len(truth_skew)} = {lazy_p_o:.2f}")
print("90% agreement from a judge that read nothing. Raw agreement is exposed.")
'''))

C.append(md('''
## OBSERVE
A judge with **zero information** scored **0.90**. If you reported "90% agreement with ground
truth!" on a slide, every evaluator in the room would know you measured the prevalence of
success, not the quality of the judge. This is the disease. Now the cure.
'''))

C.append(md('''
## The chance floor `p_e`, derived in words first

Two raters who never communicate still agree sometimes — purely by base rates. Suppose:
- the human says 1 on a fraction `a₁` of calls,
- the judge says 1 on a fraction `b₁` of calls.

Even with **no communication**, on any given call they *both* say 1 with probability `a₁·b₁`
(each independently rolls a "1"), and they *both* say 0 with probability `a₀·b₀` where
`a₀ = 1 − a₁`. Add those two ways-to-agree-by-luck:

> `p_e = a₁·b₁ + a₀·b₀`

That is the agreement you'd expect from two unrelated raters with those base rates. For the
lazy judge: `b₁ = 1.0` (says 1 always), and if the human says 1 about 0.90 of the time, then
`p_e = 0.90·1.0 + 0.10·0.0 = 0.90` — the chance floor is already 0.90, so there is *no headroom*
to beat. That is why its kappa will collapse.
'''))

C.append(md('''
## PREDICT
For our **original 6-call** `human`/`judge` lists from Act 1: the human said 1 on 4 of 6 calls
(`a₁ = 4/6 ≈ 0.667`) and the judge said 1 on 3 of 6 (`b₁ = 3/6 = 0.5`).

Compute `p_e = a₁·b₁ + a₀·b₀` in your head or on paper, and commit to it before the cell.
(Hint: `a₀ = 1 − 0.667`, `b₀ = 1 − 0.5`.)
'''))

C.append(code('''
# YOUR TURN - predict the chance floor for the 6-call data before computing it.
my_pe_prediction = None    # <- your p_e for the original human/judge (a fraction near 0.5)

if my_pe_prediction is None:
    print("fill in my_pe_prediction above, then re-run.")
else:
    print("locked p_e guess:", my_pe_prediction)
'''))

C.append(code('''
# Manual p_e on the original 6-call data - every intermediate printed, nothing hidden.
# We compute each rater's base rate as "fraction of 1s" because p_e is built ENTIRELY from
# those two base rates; seeing them named makes the formula stop being magic.
a1 = sum(human) / n          # human's rate of saying 1 (sum of a 0/1 list = count of 1s)
b1 = sum(judge) / n          # judge's rate of saying 1
a0 = 1 - a1                  # human's rate of saying 0 (the only other option, binary)
b0 = 1 - b1                  # judge's rate of saying 0
print(f"a1 (human says 1): {a1:.3f}   a0: {a0:.3f}")
print(f"b1 (judge says 1): {b1:.3f}   b0: {b0:.3f}")

both_1_by_luck = a1 * b1     # both independently land on 1
both_0_by_luck = a0 * b0     # both independently land on 0
p_e = both_1_by_luck + both_0_by_luck
print(f"both-1 by luck: {both_1_by_luck:.3f}  +  both-0 by luck: {both_0_by_luck:.3f}")
print(f"p_e (chance floor) = {p_e:.3f}")
'''))

C.append(code('''
# Confront the p_e prediction (guarded for the unfilled case).
if my_pe_prediction is not None:
    gap = abs(my_pe_prediction - p_e)
    # within 0.02 counts as "you had the mechanic"; bigger gap = revisit a1*b1 + a0*b0
    print(f"your p_e guess vs computed: {my_pe_prediction} vs {p_e:.3f}  (gap {gap:.3f})")
'''))

C.append(md('''
## CHECKPOINT 2 (out loud)
1. In words, what are the **two ways** two raters can agree purely by luck?
2. Why does the lazy judge's chance floor `p_e` come out so high (0.90)?
3. If `p_e` is already 0.90, how much "room to be skilled" is left above it?
'''))

C.append(md('''
## The kappa formula — rescaling against the floor

We now have both pieces. Kappa rescales the observed agreement against the chance floor:

> `κ = (p_o − p_e) / (1 − p_e)`

Read the parts:
- **`p_o − p_e`** (numerator): how far above the luck floor did they actually land?
- **`1 − p_e`** (denominator): how far *could* they have landed above the floor (the headroom)?
- the ratio: **what fraction of the available headroom above luck did they capture?**

So κ = 1 means they used all the headroom (perfect), κ = 0 means they landed exactly on the
floor (luck-level), κ < 0 means they fell *below* the floor (worse than luck).
'''))

C.append(md('''
## PREDICT
You have both numbers for the 6-call data: `p_o = 0.833` (observed) and `p_e = 0.500` (chance
floor). Before you plug them in, commit to the kappa: is it **higher than 0.833, lower, or
exactly 0.833?** And roughly what value? (Remember the formula subtracts the floor, then
rescales by the headroom `1 − p_e`.)
'''))

C.append(code('''
# Manual kappa from the two pieces we already computed by hand - still no function.
# We assemble it from p_o and p_e explicitly so the formula is something you BUILT, not called.
numerator = p_o - p_e            # agreement above the luck floor
headroom = 1 - p_e               # total possible agreement above the floor
kappa_by_hand = numerator / headroom
print(f"p_o = {p_o:.3f}   p_e = {p_e:.3f}")
print(f"kappa = ({p_o:.3f} - {p_e:.3f}) / (1 - {p_e:.3f}) = {kappa_by_hand:.3f}")
'''))

C.append(md('''
## EXPLAIN gate
One sentence: this kappa (~0.4) is *lower* than the raw agreement (0.83). Say why that drop
is the formula **doing its job**, not a bug. (Hint: a chunk of that 0.83 was free.)
'''))

C.append(md('''
## Manual-before-function — only NOW do we write the function

You have computed kappa by hand twice (the pieces, then the ratio). A function is just a box
around those exact steps so we stop retyping them. Meeting the box *after* the by-hand work
means it is a convenience, never a mystery.
'''))

C.append(code('''
# The function is a wrapper around the EXACT arithmetic you just did by hand - nothing new.
# We accept two equal-length 0/1 sequences and return kappa, so every later cell is one call.
def kappa(a, b):
    # p_o: fraction of positions that match - the honest, observed agreement
    po = sum(1 for x, y in zip(a, b) if x == y) / len(a)
    # base rates drive the chance floor, so we compute each rater's rate of 1s
    a1 = sum(a) / len(a)
    b1 = sum(b) / len(b)
    # p_e: both-1-by-luck plus both-0-by-luck, exactly the hand formula
    pe = a1 * b1 + (1 - a1) * (1 - b1)
    # rescale observed agreement against the chance floor
    return (po - pe) / (1 - pe)

# Sanity check: the function MUST reproduce our by-hand number, or the box is wrong.
print(f"function kappa (6-call): {kappa(human, judge):.3f}   by-hand was: {kappa_by_hand:.3f}")
'''))

C.append(code('''
# Now the payoff side-by-side: honest 6-call judge vs the lazy constant judge.
# We need a 'human' for the skewed set too - a decent labeler who slips on a couple calls.
# We build it by flipping the truth on 2 specific calls so it is reproducible, not random.
human_skew = truth_skew.copy()       # start from truth (a good labeler mostly matches it)
human_skew[0] = 0                    # one honest mistake on a completed call
human_skew[19] = 1                   # one honest mistake on a failed call

print(f"honest 6-call judge: raw {p_o:.2f}   kappa {kappa(human, judge):.2f}")
print(f"lazy constant judge: raw {lazy_p_o:.2f}   kappa {kappa(human_skew, lazy_judge):.2f}")
print("\\nThe inversion: the lazy judge has HIGHER raw agreement but kappa near 0.")
print("That inversion - low information scoring high on raw - is the entire reason kappa exists.")
'''))

C.append(md('''
## OBSERVE + EXPLAIN

The lazy judge scored higher on raw agreement (0.90 vs 0.83) and **near zero on kappa**. Raw
agreement ranked the worthless judge *above* the real one. Kappa flipped them back. Say in one
sentence what kappa saw that raw agreement could not.
'''))

C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. Write the kappa formula from memory.
2. What does the **numerator** mean? What does the **denominator** mean?
3. A judge has raw agreement 0.95 and kappa 0.04. In one sentence, what is going on?
'''))

C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: agreement was one number (how often they match). After Act 2 you hold three numbers and
their relationship: **`p_o`** (observed), **`p_e`** (the luck floor from base rates), and **`κ`**
(the fraction of headroom above luck that was captured). You watched kappa expose a judge that
raw agreement praised. You can compute all three by hand and have a function that does nothing
your hands didn't.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (p_e, the formula, or the lazy-judge inversion - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: the prevalence trap, breaks, and a CI from scratch

## The prevalence trap (the subtle one that fools experienced people)

Here is the trap that catches people who *already know* kappa. We will hold a rater's **skill
constant** — same per-call accuracy every time — and only change how **imbalanced** the classes
are. Watch what kappa does. If kappa only measured skill, it would not move. It moves a lot.
'''))

C.append(md('''
## PREDICT
We simulate a human and a judge who each label calls with a **fixed, unchanging accuracy**
(they copy the truth and slip on a fixed fraction of calls). We sweep the **prevalence of "1"**
(completed calls) from a balanced 0.50 up to a lopsided 0.95.

Their per-call skill never changes across the sweep. As prevalence climbs toward 0.95, does
kappa **rise, fall, or stay flat?** Commit out loud, then write it below.
'''))

C.append(code('''
# YOUR TURN - predict the prevalence-sweep direction before seeing the curve.
my_prevalence_direction = ""    # <- type "rise", "fall", or "flat"

if my_prevalence_direction.strip() == "":
    print("type rise / fall / flat above, then re-run.")
else:
    print("locked prediction:", my_prevalence_direction)
'''))

C.append(code('''
# A reproducible "slip with fixed probability" helper - the engine of constant skill.
# Constant skill means: for EVERY call, flip the true label with the same probability p_slip.
# Keeping p_slip fixed across the sweep is what isolates prevalence as the only moving knob.
def label_with_skill(truth_list, p_slip, rng):
    out = []
    for t in truth_list:
        # rng.random() < p_slip fires p_slip-fraction of the time -> a slip; else copy truth
        out.append(1 - t if rng.random() < p_slip else t)
    return out

# A private RNG so this sweep is deterministic and independent of earlier random() calls.
sweep_rng = random.Random(1407)
print("helper ready: same p_slip every call = constant skill, prevalence is the only variable")
'''))

C.append(code('''
# Sweep prevalence with skill held fixed. We make a big sample at each prevalence so the kappa
# estimate is stable (small samples would add noise and blur the trend we're trying to see).
prevalences = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95]
kappas_by_prev = []
N_BIG = 4000                      # large N so each kappa reflects prevalence, not luck-of-draw
for prev in prevalences:
    # build truth at this prevalence: each call is 1 with probability prev
    truth_p = [1 if sweep_rng.random() < prev else 0 for _ in range(N_BIG)]
    # SAME skill for both raters at EVERY prevalence - that is the controlled variable
    h = label_with_skill(truth_p, 0.08, sweep_rng)   # human slips 8% of calls
    j = label_with_skill(truth_p, 0.15, sweep_rng)   # judge slips 15% of calls
    kappas_by_prev.append(kappa(h, j))
    print(f"prevalence {prev:.2f}  ->  kappa {kappa(h, j):.3f}")
'''))

C.append(code('''
# Plot the trap so it is undeniable. Every line says why it exists (chart-as-evidence).
import matplotlib.pyplot as plt   # standard plotting lib, imported where first needed

fig, ax = plt.subplots(figsize=(7, 3))
ax.plot(prevalences, kappas_by_prev, marker="o")   # one dot per prevalence point we swept
ax.set_xlabel("prevalence of 'completed' (class 1)")  # the ONLY thing we changed
ax.set_ylabel("Cohen's kappa")                        # the thing that moved as a result
ax.set_title("same skill at every point - kappa still falls as classes imbalance")
ax.grid(True, alpha=0.3)
plt.show()
'''))

C.append(md('''
## WRONG-INTUITION TRAP

**The wrong belief:** "kappa measures how good my raters are, so if their skill doesn't change,
kappa shouldn't change either."

You just watched it fall — same per-call skill, kappa dropping from comfortable toward zero as
prevalence went 0.50 → 0.95. The reason: as one class dominates, the **chance floor `p_e` rises
toward 1**, so the headroom `1 − p_e` shrinks toward 0. There is almost nothing left to be
"better than luck" *about*, and kappa has little room to live in.

Two hard consequences for VoiceForge:
1. **Always report prevalence next to kappa.** A kappa with no prevalence is uninterpretable.
2. **Stratify the calls** the human blind-labels (`eval/labels_spike.csv`) so the binary class
   is not 95/5 — a balanced-ish label set keeps `p_e` low and kappa meaningful. (This is exactly
   the sampling rule book 15 inherits.)
'''))

C.append(md('''
## EXPLAIN gate
One sentence, from what you **saw** on the chart (not from memory): as prevalence rises, what
happens to `p_e`, and why does that drag kappa down even though skill held still?
'''))

C.append(md('''
## CHECKPOINT 4 (out loud)
1. Skill was held constant in the sweep. Name the variable that actually moved kappa.
2. Why does a high `p_e` leave little room for a high kappa?
3. Your colleague reports "kappa = 0.3, terrible raters." What ONE number do you ask for before
   you agree? (And how might it rescue the raters' reputation?)
'''))

C.append(md('''
## BREAK-IT #1 (guided) — misalignment, the silent killer

Kappa demands the two lists be **the same items in the same order**, aligned by `call_id`. What
happens if someone sorts one list and not the other? There is no length error, no crash — just a
*wrong number that looks fine*. This is the silent-wrongness failure, and it is far more
dangerous than a crash. Predict first: will the kappa go up, down, or stay about the same?
'''))

C.append(code('''
# BREAK-IT (guided) - misalign the judge list by reversing it, then recompute kappa.
# This does NOT crash: both lists are still length 6, still all 0/1. The damage is semantic -
# call i's human label is now compared against a DIFFERENT call's judge label.
judge_misaligned = list(reversed(judge))    # same labels, wrong order = broken alignment
print("human          :", human)
print("judge (aligned):", judge)
print("judge (REVERSED):", judge_misaligned)

# Same function, same data length - it returns a number with total confidence, and it is wrong.
print(f"\\naligned   kappa: {kappa(human, judge):.3f}   <- the truth")
print(f"misaligned kappa: {kappa(human, judge_misaligned):.3f}   <- a confident lie")
print("No error was raised. That is what makes misalignment dangerous.")
'''))

C.append(md('''
## Reading the break

Two things to carry out of that cell:
- **Why p_o changed but p_e did not.** Reversing the judge list left its *base rate* (count of
  1s) identical, so `p_e` is unchanged — but it scrambled *which* calls line up, so `p_o` and
  therefore kappa moved. The chance floor was blind to the damage.
- **Why this is worse than a crash.** A crash stops you and points at the line. This printed a
  clean number you might put on a slide. The defense: align by `call_id` explicitly and assert
  the ids match before computing — never trust positional order from two different files.
'''))

C.append(md('''
## BREAK-IT #2 — the divide-by-zero edge (a crash that teaches)

There is one input that makes the kappa formula literally undefined: when **both raters use only
one class** (e.g. both say "1" on every call). Then `p_e = 1`, the denominator `1 − p_e` is `0`,
and the formula divides by zero. Predict: what does Python do here — a clean number, a `nan`, or
a crash?
'''))

C.append(code('''
# BREAK-IT - this cell is SUPPOSED to error (or warn) and we do NOT pre-empt it.
# EXPECTED FAILURE FOR LEARNING: both raters say 1 on every call, so p_e = 1 and we divide by 0.
all_ones_human = [1, 1, 1, 1, 1, 1]    # human said 1 on every call - one class only
all_ones_judge = [1, 1, 1, 1, 1, 1]    # judge said 1 on every call - one class only

# p_e = 1*1 + 0*0 = 1, so (p_o - p_e)/(1 - p_e) = 0/0. Watch the formula refuse.
print("kappa when both raters are constant:", kappa(all_ones_human, all_ones_judge))
'''))

C.append(md('''
## Recover from the break (fix the data, then guard the function)

The crash is the *friendly* failure here — it stopped and told us the formula is undefined when
there is no class variation. The fix is twofold: understand it (kappa is meaningless when a
rater never varies — there is nothing for chance to be wrong about), and guard the function so a
real pipeline returns a sentinel instead of exploding.
'''))

C.append(code('''
# Recovery: a guarded kappa that detects the undefined case instead of dividing by zero.
# We return float('nan') (the standard "not a number") so downstream code can DETECT and skip
# it, rather than crashing the whole calibration run on one degenerate input.
def kappa_safe(a, b):
    po = sum(1 for x, y in zip(a, b) if x == y) / len(a)
    a1, b1 = sum(a) / len(a), sum(b) / len(b)
    pe = a1 * b1 + (1 - a1) * (1 - b1)
    if pe >= 1.0:                       # the headroom 1 - pe is zero -> kappa is undefined
        return float("nan")             # a detectable sentinel beats a crash in production
    return (po - pe) / (1 - pe)

# Now the degenerate input returns nan instead of crashing; the honest 6-call case is unchanged.
print("degenerate (both all-1s):", kappa_safe(all_ones_human, all_ones_judge))
print("honest 6-call case      :", round(kappa_safe(human, judge), 3))
'''))

C.append(md('''
## CHECKPOINT 5 (out loud)
1. Which break was scarier — the misalignment or the divide-by-zero — and why?
2. Why is `p_e = 1` (and kappa undefined) the *honest* answer when a rater never varies?
3. What does `kappa_safe` return in that case, and why is a sentinel better than a crash in a
   calibration run over many dimensions?
'''))

C.append(md('''
## The bootstrap: an error bar, from scratch

A single kappa from 40–60 labels could be luck of *which* calls you happened to sample. The
**bootstrap** puts an error bar on it without any distribution math:

1. You have N labeled calls. **Resample N of them WITH replacement** (some calls appear twice,
   some not at all) — a plausible "alternate sample you could have drawn."
2. Recompute kappa on that resample.
3. Do this ~2000 times → a *cloud* of kappa values.
4. The **2.5th and 97.5th percentiles** of that cloud bracket the middle 95% → your **95% CI**.

We will build it by hand: first the resample mechanic on a tiny set so you can *see* it, then
the full loop.
'''))

C.append(md('''
## PREDICT
We will resample our 6 calls with replacement once and print which call indices got drawn.
With replacement, out of 6 draws: do you expect to see **all 6 distinct calls**, or some calls
**repeated and others missing**? Commit before the next cell.
'''))

C.append(code('''
# Show the resample mechanic on the tiny 6-call set - one draw, indices printed.
# "With replacement" means each of the 6 draws is independent, so repeats and gaps are normal.
# Seeing the duplicated/missing indices is the whole intuition of the bootstrap.
boot_rng = random.Random(99)                       # private seed for a reproducible demo draw
resampled_idx = [boot_rng.randrange(n) for _ in range(n)]   # n draws from 0..n-1, with replacement
print("one resample of call indices:", resampled_idx)
# Pull the human/judge labels at those indices - this is the "alternate sample" we score
boot_human = [human[i] for i in resampled_idx]
boot_judge = [judge[i] for i in resampled_idx]
print("resampled human:", boot_human)
print("resampled judge:", boot_judge)
print("note the repeats and missing indices - that variation is what the CI is built from")
'''))

C.append(code('''
# YOUR TURN - predict the kappa of THIS one resample before computing it.
# (It will differ from the original 0.4-ish because the sample changed - by how much?)
my_resample_kappa_guess = None    # <- a fraction; rough is fine, you're feeling the spread

if my_resample_kappa_guess is None:
    print("fill in my_resample_kappa_guess above, then re-run.")
else:
    print("locked guess:", my_resample_kappa_guess, "| actual:", round(kappa(boot_human, boot_judge), 3))
'''))

C.append(md('''
## A bigger, balanced dataset to bootstrap honestly

Six calls is too few for a real CI (the interval would be enormous and the message muddy). We
build a **40-call** set with **balanced classes** (so prevalence is not fighting us) and a judge
of genuine moderate skill — this stands in for the real pilot: 40 blind labels, one binary
dimension.
'''))

C.append(code('''
# A 40-call pilot stand-in: balanced truth, a moderately-good human, a moderately-good judge.
# Balanced (prevalence ~0.5) on purpose so the bootstrap teaches the CI mechanic, not the
# prevalence trap again - one lesson per cell.
pilot_rng = random.Random(2024)
N_PILOT = 40
truth_pilot = [1 if pilot_rng.random() < 0.5 else 0 for _ in range(N_PILOT)]   # ~balanced
human_pilot = label_with_skill(truth_pilot, 0.10, pilot_rng)   # human slips ~10%
judge_pilot = label_with_skill(truth_pilot, 0.20, pilot_rng)   # judge slips ~20%

point_kappa = kappa(human_pilot, judge_pilot)                  # the single "point estimate"
print(f"pilot N = {N_PILOT}   prevalence of 1 = {sum(truth_pilot)/N_PILOT:.2f}")
print(f"point kappa (human vs judge) = {point_kappa:.3f}")
'''))

C.append(md('''
## PREDICT
We are about to bootstrap a 95% CI around this point kappa (a judge that slips ~20% on 40
calls). Before the interval appears: do you expect the CI to be **narrow** (say ±0.05) or
**wide** (spanning a few tenths)? And — foreshadowing the claim rule in Act 4 — do you expect
its lower edge to clear **0.61**? Commit out loud.
'''))

C.append(code('''
# The full bootstrap loop, written out - this is the from-scratch 95% CI.
# We resample indices (not the lists directly) so human and judge stay ALIGNED on each draw:
# call i must keep its own human AND judge label together, or we'd reintroduce the Act-3 break.
B = 2000                                  # number of resamples; more = smoother percentiles
boot_kappas = []
for _ in range(B):
    # one resample: N_PILOT draws with replacement from the call indices 0..N_PILOT-1
    idx = [pilot_rng.randrange(N_PILOT) for _ in range(N_PILOT)]
    bh = [human_pilot[i] for i in idx]    # human labels for the resampled calls
    bj = [judge_pilot[i] for i in idx]    # judge labels for the SAME resampled calls (aligned)
    boot_kappas.append(kappa(bh, bj))

print(f"collected {len(boot_kappas)} bootstrap kappas")
print("first 5:", [round(k, 3) for k in boot_kappas[:5]])
'''))

C.append(md('''
## Percentiles by hand — what a "95% CI" actually is

A 95% CI from the bootstrap is nothing mystical: **sort the cloud of kappas, then read off the
value 2.5% of the way in and the value 97.5% of the way in.** Everything between them is the
middle 95% of plausible kappas. We compute the percentile by sorting and indexing — no library —
so "95% CI" stops being a black box.
'''))

C.append(code('''
# Manual percentile: sort the cloud, then pick the element at the p-th position.
# We define it by hand because a "95% CI" IS just two order statistics - seeing the sort and
# the index demystifies the term that people quote without understanding.
def percentile(values, p):
    s = sorted(values)                    # percentiles only mean anything on sorted data
    # position p% of the way through: (len-1) scaled by p/100, rounded to a real index
    k = int(round((len(s) - 1) * (p / 100.0)))
    return s[k]

ci_low = percentile(boot_kappas, 2.5)     # 2.5th percentile = lower edge of the middle 95%
ci_high = percentile(boot_kappas, 97.5)   # 97.5th percentile = upper edge
print(f"point kappa: {point_kappa:.3f}")
print(f"95% CI from {B} bootstraps: [{ci_low:.3f}, {ci_high:.3f}]")
'''))

C.append(code('''
# Visualize the bootstrap cloud with the CI edges marked - so the interval is a picture, not
# just two numbers. The histogram IS the "alternate samples you could have drawn" distribution.
fig, ax = plt.subplots(figsize=(7, 3))
ax.hist(boot_kappas, bins=30)                          # the cloud of resampled kappas
ax.axvline(point_kappa, linestyle="-", linewidth=2)    # the single point estimate
ax.axvline(ci_low, linestyle="--")                     # lower CI edge (2.5th pct)
ax.axvline(ci_high, linestyle="--")                    # upper CI edge (97.5th pct)
ax.set_xlabel("Cohen's kappa (resampled)")
ax.set_ylabel("count of resamples")
ax.set_title(f"bootstrap 95% CI: [{ci_low:.2f}, {ci_high:.2f}] around {point_kappa:.2f}")
plt.show()
'''))

C.append(md('''
## CHECKPOINT 6 (out loud)
1. In one sentence, what is a single bootstrap *resample*?
2. Why do we resample **indices** rather than the two label lists separately?
3. A "95% CI" is literally which two things about the sorted cloud of kappas?
4. The CI here is wide. What is the cheapest way to narrow it? (Hint: it is the same lever the
   spec sets at 40 → 60 labels.)
'''))

C.append(md('''
## BREAK-IT #3 (your turn) — author your own break

You have seen two breaks (misalignment, divide-by-zero). Now author one. Pick ONE damage and
**write your prediction as a comment first**, then run and compare:
- flip MANY of the judge's labels (drive kappa negative — worse than luck), or
- make the human a lazy constant (all 1s) and watch kappa collapse, or
- shrink the pilot to N = 4 and re-bootstrap (watch the CI blow up).

The cell is guarded so it runs clean if you change nothing — but you learn nothing if you don't.
'''))

C.append(code('''
# YOUR TURN - self-authored break. Predict in the comment, then make ONE change and observe.
# my prediction: <write exactly what you expect to happen and WHY before you edit anything>

# Start from a clean copy so you damage a throwaway, not the pilot data the CI above used.
my_human = human_pilot.copy()
my_judge = judge_pilot.copy()

# 1) make ONE change here (uncomment and edit one of these, or write your own):
# my_judge = [1 - x for x in my_judge]          # flip EVERY judge label -> expect kappa < 0
# my_human = [1] * len(my_human)                # lazy constant human -> expect kappa near 0 / nan
# my_human, my_judge = my_human[:4], my_judge[:4]  # tiny N -> re-bootstrap, expect a huge CI

# 2) observe - compare against your written prediction (kappa_safe so all-1s returns nan, no crash):
print("your kappa:", round(kappa_safe(my_human, my_judge), 3) if my_human else "empty")
'''))

C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: kappa was a formula you could compute. After Act 3 you know its **edges**: prevalence
silently drags it down even at fixed skill (so you report prevalence and stratify), misalignment
produces a confident lie with no crash (so you align by `call_id`), one-class inputs make it
undefined (so you guard the function), and a single kappa is not enough — it needs a **bootstrap
CI** you can now build by sorting a cloud of resamples.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the prevalence trap or the bootstrap is a strong pick)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: bands, claims, and where this lives in VoiceForge

## Landis–Koch bands and the house rule

A kappa is a bare number until you place it on a reading scale. The **Landis–Koch** convention:

| kappa range | label |
|---|---|
| < 0.00 | worse than chance |
| 0.00–0.20 | slight |
| 0.21–0.40 | fair |
| 0.41–0.60 | moderate |
| **0.61–0.80** | **substantial** |
| 0.81–1.00 | almost perfect |

**The house rule, locked in the spec (`SPEC.md` §7.F):** you may claim **"substantial
agreement" only if the kappa AND the lower edge of its bootstrap CI both sit inside 0.61–0.80.**
If the CI dips below 0.61, the honest phrase is **"moderate, directional"** — never "substantial."
The interval, not the hope, decides the claim.
'''))

C.append(code('''
# Turn a kappa into its Landis-Koch label - the bands as code, so the reading is not eyeballed.
# We check ranges from the bottom up; the first matching band wins.
def landis_koch(k):
    if k < 0.0:   return "worse than chance"
    if k <= 0.20: return "slight"
    if k <= 0.40: return "fair"
    if k <= 0.60: return "moderate"
    if k <= 0.80: return "substantial"
    return "almost perfect"

# Apply it to our pilot point estimate so the band is attached to a real number we computed.
print(f"pilot kappa {point_kappa:.3f} lands in band: '{landis_koch(point_kappa)}'")
'''))

C.append(code('''
# The claim gate, encoding the house rule exactly: "substantial" needs BOTH the point AND the
# CI lower edge inside 0.61-0.80. This is the difference between honest and fraudulent reporting.
def what_may_i_claim(k, ci_lo):
    band = landis_koch(k)
    # the rule is about the LOWER edge: if the interval reaches down into 'moderate', you cannot
    # honestly say 'substantial' - the data does not exclude the weaker story
    if band == "substantial" and ci_lo >= 0.61:
        return "substantial (point AND CI lower edge both >= 0.61) - claim allowed"
    return f"'{band}, directional' - CI lower edge {ci_lo:.2f} dips below 0.61, so NOT 'substantial'"

print("pilot verdict:", what_may_i_claim(point_kappa, ci_low))
'''))

C.append(md('''
## PREDICT
Suppose a different pilot gives **kappa = 0.72** with **95% CI [0.58, 0.85]**. The point estimate
sits squarely in the "substantial" band (0.61–0.80). Under the house rule, may you stand up and
claim **"substantial agreement"**? Commit yes/no and the reason before the next cell.
'''))

C.append(code('''
# YOUR TURN - apply the house rule to the hypothetical 0.72, CI [0.58, 0.85] case yourself.
my_claim_allowed = None    # <- True or False: may you say "substantial agreement"?

if my_claim_allowed is None:
    print("set my_claim_allowed to True or False above, then re-run.")
else:
    # the function is the ground truth here; we reveal it after you commit
    truth = what_may_i_claim(0.72, 0.58)
    print("you said claim allowed =", my_claim_allowed)
    print("rule says:", truth)
'''))

C.append(md('''
## The reveal — why 0.72 still does not earn "substantial"

The point estimate (0.72) is comfortably "substantial". But the CI is **[0.58, 0.85]**, and
0.58 lands in the **moderate** band. The interval does *not exclude* a merely-moderate truth, so
the honest claim is **"moderate-to-substantial, directional."** Saying "substantial" full stop
would be overclaiming — exactly the kind of green-cells-but-wrong move the whole course warns
against. **The number exists; the interval governs what you may say about it.**
'''))

C.append(md('''
## Where this lives in the real VoiceForge pipeline

This is not an exercise — it is **Block 7** of the build, and the file is already stubbed:

- **`eval/kappa.py`** — the pilot calibration script. Its header literally says
  `cohen_kappa_score(human, judge)` over id-aligned labels, then *"bootstrap CI: resample item
  indices 1000x → 2.5/97.5 percentiles"* — the exact mechanic you just built by hand.
- **`eval/labels_spike.csv`** — rater 1's blind labels (the `human` here); optionally
  `eval/labels_friend.csv` for a second rater (the human-human ceiling).
- **`rubric.yaml`** — the binary dimension under test. The judge dimensions there
  (`language_match`, `faithfulness`, `repair_quality`) each return `{score, reason,
  evidence_turn_ids}`; calibration tests one of them against blind human labels.
- The recurring cast — **`call_A`** (English success), **`call_B`** (Hinglish partial),
  **`call_C`** (Telugu-English failure) — are the kind of calls that get labeled. `call_B`'s
  "partial" is exactly where a human and judge most often disagree, which is why the two
  disagreement cases go on a slide.
'''))

C.append(code('''
# Tie it to the cast: a tiny aligned label set over the three recurring calls, scored honestly.
# We map their outcomes to the binary "task completed?" dimension: success/partial -> the human's
# call; the judge may see it differently - and THAT disagreement is the credibility material.
cast_calls = ["call_A", "call_B", "call_C", "call_A2", "call_B2", "call_C2"]
human_cast = [1, 1, 0, 1, 0, 0]    # human: A completed, B counted as completed, C failed, ...
judge_cast = [1, 0, 0, 1, 0, 1]    # judge: disagrees on call_B (partial) and call_C2 - the cases

# Surface the disagreements explicitly - in the demo these become the "here's where the judge
# was wrong" slide, the single most credibility-building move in the calibration story.
print(f"cast kappa: {kappa(human_cast, judge_cast):.3f}")
for i in range(len(cast_calls)):
    if human_cast[i] != judge_cast[i]:
        print(f"  DISAGREEMENT on {cast_calls[i]}: human={human_cast[i]} judge={judge_cast[i]} <- slide case")
'''))

C.append(md('''
## The concept at three levels (the same idea, three rooms)

- **To a beginner:** "If almost every call succeeds, even a judge that always guesses 'success'
  looks right most of the time. Kappa subtracts that free credit and asks: how much better than
  guessing are you, really? — and the error bar says how sure we are of *that*."
- **To an engineer:** "Cohen's kappa is `(p_o − p_e)/(1 − p_e)` over a 2×2; `p_e` is the
  base-rate chance floor, so kappa degrades as prevalence skews even at fixed pairwise accuracy.
  We bound it with a nonparametric bootstrap over item indices (2.5/97.5 percentiles) and gate
  the 'substantial' claim on the CI's lower edge, not the point estimate."
- **To a founder:** "We don't claim our judge is magic. We measured how often it agrees with a
  human *beyond luck*, put honest error bars on that, and we'll show you two calls where it was
  wrong. That's a calibrated instrument, not a vibe — and it's why the number is defensible."
'''))

C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "Your judge agrees with the human at kappa 0.78 — so it's right 78% of the time, yes?"**
<details><summary>answer</summary>No. Kappa is luck-adjusted *agreement with a human*, not accuracy against ground truth, and 0.78 is not a percentage of anything — it is the fraction of above-chance headroom the two raters captured. A different human could shift it.</details>

**2. "Why did you bootstrap instead of just reporting the kappa?"**
<details><summary>answer</summary>Forty labels is a small sample; a single kappa could be the luck of which calls we drew. The bootstrap resamples those calls with replacement ~2000 times and reads the 2.5/97.5 percentiles, giving a 95% CI with no distribution assumptions. The interval — not the point — decides whether we may say "substantial."</details>

**3. "Your kappa is only 0.5 — isn't your judge just bad?"**
<details><summary>answer</summary>Maybe, but first ask the prevalence. At 90/10 the chance floor is high and kappa is suppressed even for a competent judge; that's the prevalence trap. We stratify the label set toward balance so kappa stays meaningful, and we report prevalence alongside it. We also show the disagreement cases so "0.5" is a diagnosis, not just a grade.</details>
'''))

C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own the full arc: a kappa is computed (`p_o`, `p_e`, the formula), bounded (a
from-scratch bootstrap CI), banded (Landis–Koch), and **claimed honestly** (the CI lower edge,
not the point, licenses "substantial"). You know the real files it lives in (`eval/kappa.py`,
`eval/labels_spike.csv`, `rubric.yaml`) and that book 15 picks this up to present the number
without fraud or shame.
'''))

C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all six:
1. Why raw agreement is broken (the lazy constant judge — one sentence)
2. The chance floor `p_e` — the two ways to agree by luck, and the formula `a₁·b₁ + a₀·b₀`
3. The kappa formula, and what numerator and denominator mean
4. The prevalence trap — same skill, lower kappa, *because* `p_e` rises
5. The bootstrap CI — resample with replacement, recompute, take the 2.5/97.5 percentiles
6. The house rule — when you may say "substantial," and when you must say "moderate, directional"

Could not hit all six? Open it back up, find the gap, redo that act. That is the system working.
'''))

C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (bands / claim rule / where it lives - your pick)
my_clean_sentence = ""      # the sentence you'd say in a room about what kappa is and does

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))

C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Kappa asks: better than luck — and the interval decides what I may claim."**

If yours captures that in your own words — chance-corrected agreement, bounded by a CI, claimed
honestly — this book did its job.
'''))

C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "14_cohens_kappa_from_scratch.ipynb"   # <- this notebook's filename
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

**14 done** (pending your teach-back) → **15 · Pilot calibration, said honestly** — you have the
instrument (kappa + CI + bands); 15 is standing up and *presenting* a mediocre-but-honest number
without fraud or shame: small sample, honest framing, disagreements shown proudly.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "14_cohens_kappa_from_scratch.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
