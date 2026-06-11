#!/usr/bin/env python3
# Builds 15_pilot_calibration_honestly.ipynb per _BUILD_SPEC.md (four acts, marker conventions,
# recurring cast, learner-cell guards, self-audit last). Rerun: .venv/bin/python notebooks/build_15.py
#
# THE one atomic concept: presenting a mediocre agreement number without fraud or shame.
# Knowledge-flow: 14 kappa  ->  THIS (pilot calibration, said honestly)  ->  16 improvement examples.
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
# 15 · Pilot calibration, said honestly

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Read a kappa against the **Landis–Koch bands** and name which band it falls in
2. Apply the **claim rule**: say "substantial agreement" ONLY if the number AND its whole
   confidence interval land in 0.61–0.80 — otherwise say "moderate, directional" and stop
3. Present the **disagreement cases proudly** as the most useful artifact a pilot produces,
   not as a thing to hide
4. Say the **mature sentence** that ships a mediocre number with a small sample, no spin,
   no shame — and defend every word of it

Book 14 taught you to *compute* Cohen's kappa and its bootstrap CI. This book is not about
the math. It is about the harder thing: standing in a room and saying a 0.52 out loud
**without inflating it and without apologizing for it.**
'''))

C.append(md('''
## 2 — Knowledge-flow map

`14 (Cohen's kappa: agreement beyond luck)  →  THIS (pilot calibration, said honestly)  →  16 (improvement examples)`

Why this book exists in the ladder: book 14 hands you a number and an interval. A number is
not a claim. Between "kappa is 0.52, CI [0.28, 0.71]" and the sentence you say to a room
sits a **decision** — what may I honestly assert? Get that decision wrong by rounding up and
you have committed quiet fraud; get it wrong by cringing and you have buried the one finding
(the disagreements) that book 16 turns into improvement data. This book is the bridge from a
measured number to an **honest claim**.
'''))

C.append(md('''
## 3 — Baby intuition

You and a friend each grade the same 30 essays pass/fail. You agree on 24 of them. The
honest question is never "we agreed 80% of the time, good enough?" — luck alone would make
two grist-mill graders agree a lot. The honest question is "did we agree **more than luck**,
and **how sure am I** of that, given it was only 30 essays?"

Now make it uncomfortable. Suppose the beyond-luck answer comes out **mediocre** — better
than coin-flipping, but not impressive. You have two cowardly exits and one mature road:

- **Round it up.** "Basically substantial." (Fraud — you moved a number you did not earn.)
- **Hide it.** Bury the metric, show only the nice demo. (Cowardice — and you lose the
  disagreements, which were the most valuable thing you found.)
- **Say it plainly.** "Moderate and directional on a small sample; here are the exact two
  cases we disagreed on." (Maturity — the only road that survives a sharp question.)

This whole notebook trains the third road.
'''))

C.append(md('''
## 4 — The formal version

**Landis–Koch bands** — the standard reading scale for kappa (κ):

| κ range | label |
|---|---|
| < 0.00 | poor (worse than chance) |
| 0.00 – 0.20 | slight |
| 0.21 – 0.40 | fair |
| 0.41 – 0.60 | **moderate** |
| 0.61 – 0.80 | **substantial** |
| 0.81 – 1.00 | almost perfect |

**The claim rule (locked, house rule from the spec):** you may say the word **"substantial"**
ONLY when the point estimate is in 0.61–0.80 **AND the entire 95% confidence interval also
sits at or above 0.61.** If either the point or any part of the CI falls below 0.61, the
honest claim is **"moderate, directional"** and you say exactly that.

Three words this book leans on:
- **pilot calibration** — a small first round (here ~30 items) checking whether a judge and a
  human agree beyond luck, before trusting the judge at scale
- **point estimate vs interval** — the single κ is the point; the CI is the honesty tax that
  a small sample charges you (it is wide because n is small)
- **directional** — "this points the right way but I will not bet the company on the exact
  number yet" — the honest verb for a mediocre-but-positive result
'''))

C.append(md('''
## 5 — Why this exists (the failure it prevents)

Two real ways a pilot result gets mis-said on a demo stage:

1. **The round-up.** κ=0.58 becomes "we hit substantial agreement." One judge in the room
   asks for the CI, you do not have it or it is [0.34, 0.76], and your credibility is gone for
   every other number you will show that day.
2. **The cringe.** κ=0.58 with two honest disagreements becomes a mumbled "the agreement was
   okay, anyway here's the demo." You just threw away the disagreements — the exact material
   book 16 mines into training pairs — because you were embarrassed by a fine number.

The cost of both is the same: a small, honest, useful result gets converted into either a
liability or a wasted finding. This book gives you the one sentence and the one table that
convert it into an asset instead.
'''))

C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never the syntax.
# We pin numpy's RNG to a fixed seed so every bootstrap CI in this book is identical on every
# machine - calibration claims must be reproducible, or the "honesty" is theater.
import numpy as np
rng = np.random.default_rng(15)   # 15 = this book's id, so the seed is self-documenting

# A one-line sanity print so your first action here is a run you predicted: PREDICT - what
# exact text appears below?
print("pilot calibration bench ready - numpy", np.__version__)
'''))

C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What is the ONE band boundary the whole claim rule hinges on? (a single number)
2. State the claim rule in your own words: when may you say "substantial"?
3. Name the two cowardly exits and the one mature road from Act 1's baby intuition.
'''))

C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a calibration result is a number you report.
After Act 1 you should know: a calibration result is a number **plus an interval plus a
claim decision** — and the claim is gated by a single boundary (0.61) that separates an honest
"substantial" from an honest "moderate, directional." The disagreements are not failure;
they are the deliverable.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of what "calibration said honestly" means to you now.
# Producing the sentence is the learning; reading mine would only feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so an unfilled notebook still runs clean: it nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: a toy pilot, computed and read by hand

## The setup, in plain words

A human reviewer and our LLM judge each label the SAME small batch of calls on one yes/no
dimension: **"was the task completed?"** (the required-fields checklist from book 06). This is
a *pilot* — a first, small calibration round. We will:
1. print the raw paired labels (raw before transformed — a course rule),
2. compute kappa BY HAND (manual before function),
3. get its confidence interval by bootstrap,
4. and only THEN turn the number into an honest claim.

We keep the batch tiny (you can see every row) and deliberately engineer a **mediocre**
result — because a mediocre number is the entire point of this book.
'''))

C.append(md('''
## PREDICT
Below, the human and the judge will label ~30 calls each as 1 (task completed) or 0 (not).
They will agree on most, disagree on a couple. Before you see the numbers:

Commit to a guess for the **raw agreement** (the plain fraction of positions where the two
labels match). A number between 0 and 1. Write it in the next cell.
'''))

C.append(code('''
# YOUR TURN - predictions go in BEFORE the computing cells, stored so the notebook records
# YOUR thinking and a later cell can confront your guess with reality. That gap is the lesson.
my_raw_agreement_guess = None   # <- replace None with a number between 0 and 1

if my_raw_agreement_guess is None:
    print("fill in my_raw_agreement_guess above (e.g. 0.9), then re-run this cell.")
else:
    print("guess locked:", my_raw_agreement_guess)
'''))

C.append(code('''
# The toy pilot, printed RAW before we touch it. Two aligned label arrays: position i is the
# same call_i, labeled by the human and by the judge. We hand-author them (not random) so the
# mediocre result is reproducible and you can literally point at the disagreements later.
# 30 calls. Labels: 1 = task completed, 0 = not completed.
human = np.array([1,1,0,1,1,1,0,1,1,1, 1,0,1,1,1,1,0,1,1,1, 0,1,1,1,1,0,1,1,1,0])
judge = np.array([1,1,0,1,0,1,1,1,1,1, 1,0,1,1,1,0,0,1,1,1, 0,1,1,0,1,1,1,1,1,0])

# We assert equal length because kappa is only defined on PAIRED labels - a length mismatch
# would silently misalign calls and produce a meaningless number (a book-14 lesson).
assert len(human) == len(judge), "label arrays must be paired one-to-one"
n = len(human)
print("n calls:", n)
print("human:", human)
print("judge:", judge)
'''))

C.append(md('''
## Read it as a table first (the reading ritual)

Three moves before any math:
1. **Row count** — "thirty calls."
2. **What one position IS** — "position i is one call, labeled by both the human and the judge."
3. **Read one disagreement aloud** — find a column where the two arrays differ and say it:
   "on call index 4, the human said completed (1) and the judge said not (0)."

The next cell finds and prints exactly those disagreement positions — the rows that matter most.
'''))

C.append(code('''
# We surface the disagreements explicitly. np.where returns the indices where the condition
# holds; we want positions where the two labels differ - those are the calibration's signal,
# not its noise, so we never let them hide inside an aggregate.
disagreements = np.where(human != judge)[0]
print("disagreement indices:", disagreements)
print("count of disagreements:", len(disagreements))

# Print each disagreement as a row so each is visibly one CALL with two verdicts.
for i in disagreements:
    print(f"  call index {i:>2} | human={human[i]} | judge={judge[i]}")
'''))

C.append(md('''
## PREDICT
You can now count the matches by eye. Out of 30 calls, the two labels differ on the indices
just printed. So the **raw agreement** is (30 − number_of_disagreements) / 30.

Commit to the exact raw agreement now (do the subtraction in your head), then run the next cell.
'''))

C.append(code('''
# Manual raw agreement, BY HAND, every step visible. We compare element-wise; (human == judge)
# is a boolean array, and .mean() of booleans is the fraction that are True - i.e. the match rate.
matches = (human == judge)          # True where the two labels agree, position by position
print("per-call match (True=agree):", matches.astype(int))

raw_agreement = matches.mean()      # mean of a 0/1 array IS the fraction of agreements
print("raw agreement:", round(raw_agreement, 3))

# Confront YOUR stored guess - the metal-detector reading from book P00.
if my_raw_agreement_guess is not None:
    verdict = "matched" if abs(my_raw_agreement_guess - raw_agreement) < 0.02 else "DIFFERED"
    print("your guess", verdict, "- if it differed, that gap is what to think about")
'''))

C.append(md('''
## The trap raw agreement walks into (recap from book 14)

Raw agreement here looks high. But two labelers who both say "completed" most of the time
would agree a LOT **by luck alone** — the task usually succeeds, so both usually say 1. Raw
agreement gives chance a free pass. Cohen's kappa removes that free pass:

> κ = (p_o − p_e) / (1 − p_e)

where **p_o** is observed agreement (the raw number you just got) and **p_e** is the agreement
you'd expect from luck given each labeler's own yes-rate. We compute p_e, then κ, by hand next.
'''))

C.append(md('''
## PREDICT
The human's yes-rate and the judge's yes-rate are both high (most calls succeed). When
chance agreement **p_e** is high, the denominator (1 − p_e) is small, so kappa punishes the
high raw agreement hard.

PREDICT: will kappa land in the **substantial** band (0.61–0.80), or lower into **moderate**
(0.41–0.60)? Commit to a band name before running.
'''))

C.append(code('''
# Manual chance agreement p_e, BY HAND. p_e = P(both say yes by luck) + P(both say no by luck).
# Each term is the product of the two independent yes-rates (or no-rates) - independence is the
# "by luck" assumption that defines chance agreement (book 14's derivation).
human_yes = human.mean()            # the human's marginal yes-rate
judge_yes = judge.mean()            # the judge's marginal yes-rate
print("human yes-rate:", round(human_yes, 3), "| judge yes-rate:", round(judge_yes, 3))

p_both_yes = human_yes * judge_yes              # both say 1 by luck
p_both_no  = (1 - human_yes) * (1 - judge_yes)  # both say 0 by luck
p_e = p_both_yes + p_both_no
print("p_e (chance agreement):", round(p_e, 3))
'''))

C.append(code('''
# Manual kappa, BY HAND, from the two numbers above. We write the formula literally so the
# idea is visible BEFORE we ever wrap it in a function - a wrapper met first hides the idea.
p_o = raw_agreement                 # observed agreement is exactly the raw agreement
kappa_by_hand = (p_o - p_e) / (1 - p_e)
print("p_o:", round(p_o, 3), "| p_e:", round(p_e, 3))
print("kappa by hand:", round(kappa_by_hand, 3))
'''))

C.append(md('''
## OBSERVE + EXPLAIN

Did your band prediction hold? Say the why in one sentence: a high raw agreement collapsed
toward a **moderate** kappa because most calls succeed, so chance agreement p_e was already
high — the labelers had little headroom above luck to claim.

This is the first honest blow of the book: the impressive-looking raw number became an
unremarkable kappa the moment we charged it for luck. Now we wrap it (only after by-hand).
'''))

C.append(code('''
# NOW the function - identical math to what you just did by hand. We define it as a reusable
# function because the bootstrap (next) will call it thousands of times on resampled data.
def kappa(a, b):
    # a, b are paired 0/1 label arrays. We recompute p_o and p_e inside so the function is
    # self-contained and safe to call on any resample the bootstrap hands it.
    a, b = np.asarray(a), np.asarray(b)
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return (po - pe) / (1 - pe)

# Proof the function equals the by-hand value - trust is earned by matching, not by assertion.
print("function kappa:", round(kappa(human, judge), 3))
print("by-hand kappa: ", round(kappa_by_hand, 3))
print("match:", abs(kappa(human, judge) - kappa_by_hand) < 1e-9)
'''))

C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. Why did a high raw agreement (~0.83) turn into a much lower kappa here?
2. In one sentence: what does p_e represent, and why does a high p_e shrink kappa?
3. Which Landis–Koch band did the point estimate land in?
'''))

C.append(md('''
## The honesty tax: a point estimate is not a claim

κ ≈ 0.5-something from **30 calls** is one draw from a noisy process. Relabel a slightly
different 30 calls and you would get a slightly different κ. The **confidence interval** is how
wide that wobble is — and with only 30 items, it is WIDE. That width is the tax a small pilot
pays, and hiding it is the most common way calibration numbers lie.

We get the interval the way book 14 did: **bootstrap** — resample the 30 paired calls with
replacement many times, recompute κ each time, and read the middle 95% of those κ values.
'''))

C.append(md('''
## PREDICT
We will bootstrap 5,000 resamples of the 30 calls and take the 2.5th and 97.5th percentiles
of the resulting kappas as a 95% CI.

PREDICT: with only n=30, will the CI be **narrow** (e.g. width < 0.1) or **wide** (e.g. width
> 0.3)? And — the load-bearing question — do you expect its **lower** end to sit above or
below the 0.61 substantial line? Commit to both before running.
'''))

C.append(code('''
# Bootstrap CI, BY HAND so the mechanism is visible. Resampling WITH replacement simulates
# "what if we'd happened to draw a different 30 calls?" - the variation across resamples IS
# the sampling uncertainty a single point estimate cannot show.
B = 5000                                    # number of resamples; more = smoother percentiles
boot_kappas = np.empty(B)                   # pre-allocate so the loop just fills slots
for i in range(B):
    # draw n indices in [0, n) WITH replacement - the same call may appear twice or not at all,
    # which is exactly how the bootstrap mimics re-running the pilot on a fresh sample.
    idx = rng.integers(0, n, size=n)
    boot_kappas[i] = kappa(human[idx], judge[idx])

# The middle 95% of the resample kappas is the 95% bootstrap CI (the percentile method).
ci_low, ci_high = np.percentile(boot_kappas, [2.5, 97.5])
point = kappa(human, judge)
print(f"point estimate kappa: {point:.3f}")
print(f"95% bootstrap CI:     [{ci_low:.3f}, {ci_high:.3f}]")
print(f"CI width:             {ci_high - ci_low:.3f}")
'''))

C.append(md('''
## OBSERVE

Two things to read off, out loud:
1. The CI is **wide** — that is n=30 talking, not a mistake. A small pilot cannot promise a
   tight number; pretending otherwise is the lie.
2. Look at where `ci_low` sits relative to **0.61**. If the lower end is below 0.61, then even
   if the point estimate flirted with "substantial," the data does not support that word.

The next cell draws this so the boundary is impossible to round past.
'''))

C.append(code('''
# A picture of the claim decision. The 0.61 line and the CI relative to it ARE the argument;
# a number in text is easy to round up, a CI crossing a drawn line is not.
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 2.4))
# shade the two bands that matter for the claim rule so the eye sees which side we are on
ax.axvspan(0.41, 0.61, color="gold",      alpha=0.18)   # moderate band
ax.axvspan(0.61, 0.80, color="seagreen",  alpha=0.18)   # substantial band
ax.axvline(0.61, color="black", linestyle="--")         # THE boundary the claim rule hinges on
ax.text(0.61, 1.28, "0.61 substantial line", ha="center", fontsize=9)

# the point estimate as a dot, the CI as a horizontal bar through it
ax.errorbar(point, 1.0, xerr=[[point - ci_low], [ci_high - point]],
            fmt="o", color="navy", capsize=5, markersize=9)
ax.text(0.50, 0.55, "moderate", ha="center", fontsize=9)
ax.text(0.705, 0.55, "substantial", ha="center", fontsize=9)
ax.set_xlim(0.0, 1.0)
ax.set_ylim(0.3, 1.6)
ax.set_yticks([])
ax.set_xlabel("Cohen's kappa")
ax.set_title("pilot kappa with 95% CI vs the substantial boundary")
plt.show()
print(f"point {point:.3f}, CI [{ci_low:.3f}, {ci_high:.3f}] - does the WHOLE bar sit right of 0.61?")
'''))

C.append(md('''
## CHECKPOINT 3 (out loud)
Look at the chart. Answer the claim rule directly:
1. Is the **point estimate** in 0.61–0.80?
2. Does the **entire CI** sit at or above 0.61?
3. Therefore — may you say the word "substantial"? If not, what is the exact honest phrase?
'''))

C.append(md('''
## Manual claim decision before the function

Before we wrap the rule in code, decide it by hand on this very result. The rule has exactly
two gates, both must pass for "substantial":
- gate A: `0.61 <= point <= 0.80`
- gate B: `ci_low >= 0.61`  (the whole interval at or above the line)

If both pass → "substantial agreement". Otherwise → "moderate, directional". There is no
third, softer option and no rounding. Say which gate fails here.
'''))

C.append(code('''
# YOUR TURN - decide the claim BY HAND first, then the function will check you.
# Set these two booleans yourself from the printed point/ci_low above (do not call any helper).
gate_A_point_in_band = None   # <- True/False: is 0.61 <= point <= 0.80 ?
gate_B_ci_above_line = None   # <- True/False: is ci_low >= 0.61 ?

if gate_A_point_in_band is None or gate_B_ci_above_line is None:
    print("set both gates to True/False from the numbers above, then re-run.")
else:
    # both gates must hold for the strong word; this AND is the entire rule
    may_say_substantial = gate_A_point_in_band and gate_B_ci_above_line
    print("by-hand verdict:", "substantial" if may_say_substantial else "moderate, directional")
'''))

C.append(code('''
# NOW the function that encodes the claim rule - identical logic, written once so every future
# pilot is judged by the SAME bar (a rule you re-decide each time is a rule you will bend).
def honest_claim(point, ci_low, ci_high):
    # the strong word requires BOTH the point in-band AND the whole CI at/above the 0.61 line;
    # we return the exact phrase so callers cannot paraphrase a stronger claim than earned.
    point_in_band = 0.61 <= point <= 0.80
    ci_clears_line = ci_low >= 0.61
    if point_in_band and ci_clears_line:
        return "substantial"
    return "moderate, directional"

claim = honest_claim(point, ci_low, ci_high)
print("function verdict:", claim)
print("the data licenses exactly this word - no rounding up to the next band")
'''))

C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a calibration is "compute kappa, report it." After Act 2 you should own the full
honest pipeline: raw labels → kappa by hand (high raw collapses once you charge for luck) →
bootstrap CI (wide, because n is small) → a **claim gated by the 0.61 line**, where the whole
CI — not just the point — must clear the line before you may say "substantial."
'''))

C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (the claim rule / the CI tax - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the claim, and the disagreements you were tempted to hide

## Break-it philosophy

You do not own a rule until you have tried to cheat it and watched it refuse. So we now apply
pressure to the claim rule on purpose: round numbers up, drop the CI, lean on the point
estimate. Each break shows a real way calibration gets mis-said — and the rule's job is to
not let you.
'''))

C.append(md('''
## PREDICT
Here is the most common dishonest move: report only the **point estimate** and round it to the
nearest "nice" band. Suppose a pilot gives point = 0.63 with CI [0.34, 0.79].

PREDICT: if you ONLY look at the point (0.63, which is inside 0.61–0.80) and ignore the CI,
which claim would you wrongly make? And what does the FULL rule say once the CI is included?
Commit to both before running.
'''))

C.append(code('''
# BREAK-IT (guided) - the point-only shortcut that overclaims. This cell is the WRONG method
# shown deliberately, so you can feel exactly how rounding-to-band manufactures a false claim.
sketchy_point = 0.63
sketchy_ci    = (0.34, 0.79)

# The dishonest shortcut: judge the claim from the point estimate ALONE.
point_only_claim = "substantial" if 0.61 <= sketchy_point <= 0.80 else "moderate, directional"
print("point-only (DISHONEST) claim:", point_only_claim)

# The full rule, which also demands the whole CI clear 0.61:
full_claim = honest_claim(sketchy_point, sketchy_ci[0], sketchy_ci[1])
print("full-rule (HONEST) claim:   ", full_claim)
print("the CI low is", sketchy_ci[0], "-> far below 0.61, so the honest claim is weaker")
'''))

C.append(md('''
## Reading the break

The point-only shortcut said "substantial." The full rule said "moderate, directional" —
because the CI's lower end (0.34) is nowhere near the 0.61 line. **Same number, two different
claims, and only one is defensible when a sharp listener asks for the interval.** The point
estimate is the most tempting place to commit quiet fraud precisely because it is the part
that looks decisive. The CI is the part that keeps you honest.
'''))

C.append(md('''
## CHECKPOINT 4 (out loud)
A colleague's slide says "substantial agreement, κ=0.63." You ask for the CI; it is
[0.34, 0.79]. State, in one breath: what is wrong with the slide, what the honest claim is,
and which single gate of the rule the slide skipped.
'''))

C.append(md('''
## YOUR break now

Author your own attempt to cheat the rule. Pick a (point, ci_low, ci_high) where the **point**
is inside the substantial band but the **CI lower end** is below 0.61 — i.e. a result that is
tempting to overclaim. Predict the rule's verdict in a comment, then run it through
`honest_claim` and confirm the rule refuses to say "substantial."
'''))

C.append(code('''
# YOUR TURN - self-authored break-it of the claim rule.
# my prediction: <write the verdict you expect honest_claim to return, and WHY>

my_point   = None   # <- a point inside 0.61-0.80, e.g. 0.66
my_ci_low  = None   # <- a CI low BELOW 0.61, e.g. 0.45
my_ci_high = None   # <- a CI high, e.g. 0.82

# Guard so an unfilled notebook still runs clean; only judge once all three are set.
if my_point is None or my_ci_low is None or my_ci_high is None:
    print("fill in my_point, my_ci_low, my_ci_high above, then re-run.")
else:
    verdict = honest_claim(my_point, my_ci_low, my_ci_high)
    print(f"point {my_point}, CI [{my_ci_low}, {my_ci_high}] -> rule says: {verdict}")
    print("if your point was in-band but CI low < 0.61, the rule should REFUSE 'substantial'")
'''))

C.append(md('''
## WRONG-INTUITION TRAP

**The wrong belief:** "a mediocre kappa and a couple of disagreements mean the pilot failed —
hide them and just show the demo."

This is exactly backwards, and the next cell proves it. The disagreements are not the pilot's
shame; they are its **single most valuable output**. Each disagreement is a concrete call
where the human and the judge saw the task differently — which is precisely the raw material
book 16 turns into improvement examples and book 17 turns into preference pairs. A pilot that
agreed 100% would teach you *nothing* about where the judge is weak. Run the cell, then read
the reveal.
'''))

C.append(code('''
# The disagreements as a PROUD artifact, not a buried one. We attach a tiny human-written note
# to each disagreed call so the table is actionable - "where did the two minds diverge, and
# what does that point at?" This table is the deliverable book 16 consumes.
notes = {
    4:  "judge missed an implicit confirmation; human counted task complete",
    6:  "human too strict: caller gave the slot, judge was right",
    15: "agent barge-in cut the answer; genuinely ambiguous which way to score",
    23: "address half-captured; reasonable people disagree on 'completed'",
    25: "language switch mid-turn; judge read it as non-completion, human disagreed",
}
print(f"{'call':>4} | {'human':>5} | {'judge':>5} | note")
print("-" * 72)
for i in disagreements:
    # default note keeps the loop robust if a disagreement has no hand-written annotation yet
    note = notes.get(int(i), "(needs review - annotate before the next round)")
    print(f"{i:>4} | {human[i]:>5} | {judge[i]:>5} | {note}")
print("-" * 72)
print(f"{len(disagreements)} disagreements = {len(disagreements)} concrete leads for book 16")
'''))

C.append(md('''
## The reveal

A pilot's value is not "did the two labelers agree?" — it is **"where, exactly, did they
disagree, and what does each disagreement teach?"** A high kappa with no disagreements gives
you a comfortable slide and zero leads. A moderate kappa with five annotated disagreements
gives you five concrete improvements. The disagreements are the asset; the kappa is just the
honesty gauge on top of them. Showing them **proudly** is the mature move — it signals you
went looking for where you are weak, which is the opposite of hiding a bad number.
'''))

C.append(md('''
## PREDICT
One more pressure test. We add **two more disagreements** to the pilot (the judge slips on two
more calls). Cohen's kappa will drop.

PREDICT: roughly how far does kappa fall, and — the claim question — does adding disagreements
ever move you UP a band? (Think about the direction before running.)
'''))

C.append(code('''
# BREAK-IT - perturb the data to feel kappa move. We flip two of the judge's labels (calls 8
# and 18, currently agreements) to manufacture two new disagreements, then recompute. Changing
# exactly two cells isolates the effect - the change-one-thing rule from P00, scaled to two.
judge_worse = judge.copy()           # copy so the original pilot stays intact for comparison
judge_worse[8]  = 1 - judge_worse[8]  # flip a 1<->0 at call 8: a new disagreement
judge_worse[18] = 1 - judge_worse[18] # and at call 18: another new disagreement

new_point = kappa(human, judge_worse)
print(f"kappa before: {kappa(human, judge):.3f}")
print(f"kappa after +2 disagreements: {new_point:.3f}")
print("more disagreements push kappa DOWN, never up - it can only lower the claim, never inflate it")
'''))

C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a mediocre kappa and some disagreements felt like a failed pilot to hide. After Act 3:
the point estimate is where overclaiming hides (round-up = quiet fraud, the CI catches it),
and the disagreements are the **deliverable**, not the shame — they are the leads book 16
mines. More disagreements only ever lower the claim; the rule cannot be cheated upward.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the disagreements-are-the-asset trap is a strong pick)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this lives, and the sentence you say in the room

## The VoiceForge connection

This is not an abstract stats lesson — it is the script for a real moment in the VoiceForge
pilot. The pieces map to real repo parts:

- the human/judge labels are the **task-success** dimension from the required-fields checklist
  (`pipeline/signals.py` computes the signals; book 06 built the checklist)
- the judge is the cached Gemini judge in `pipeline/judge.py` (`judge_dimension()`), which
  book 10 calls live
- the dimension and its threshold live in `rubric.yaml` (book 21)
- the disagreement table you built feeds **book 16 (improvement examples)** and onward to
  **book 17 (preference pairs / DPO)**

The mature sentence below is the literal thing you say when a judge in the hackathon room asks
"how good is your eval?"
'''))

C.append(md('''
## The mature sentence (memorize the shape)

> **"On a 30-call pilot, our judge agrees with a human reviewer on task-success at kappa
> ≈ 0.56, 95% CI roughly [0.15, 0.86] — moderate and directional, not yet substantial. The
> sample is small, so the interval is wide. The handful of disagreements are the useful part:
> here they are, and each is a concrete lead for the next round."**

Every clause does a job: the **n** (sets expectations), the **kappa** (the number, unrounded),
the **CI** (the honesty tax), the **band word** ("moderate, directional" — claim rule applied),
the **why-wide** (small sample, not incompetence), and the **disagreements offered proudly**.
'''))

C.append(code('''
# We assemble the mature sentence FROM the computed numbers, so the words can never drift from
# the data. Building the claim programmatically is the anti-fraud control: the sentence is a
# function of (point, ci, claim), not a thing a tired presenter retypes and rounds at 2am.
band_word = honest_claim(point, ci_low, ci_high)   # reuse the locked rule, never re-decide it

mature_sentence = (
    f"On a {n}-call pilot, our judge agrees with a human reviewer on task-success at "
    f"kappa = {point:.2f}, 95% CI [{ci_low:.2f}, {ci_high:.2f}] - {band_word}. "
    f"Small sample, so the interval is wide. The {len(disagreements)} disagreements are the "
    f"useful part and each is a lead for the next round."
)
print(mature_sentence)
'''))

C.append(md('''
## PREDICT
The sentence above was built from the numbers. Suppose next week's pilot improves to
point = 0.72 with CI [0.63, 0.81].

PREDICT: what single word in the sentence changes, and does the honest claim become
"substantial"? (Check the rule: point in band AND whole CI ≥ 0.61.) Commit before running.
'''))

C.append(code('''
# We re-run the SAME assembly on a hypothetical better pilot - proving the sentence updates
# itself honestly when the data improves, with no human deciding to "promote" the claim.
better_point, better_lo, better_hi = 0.72, 0.63, 0.81
better_band = honest_claim(better_point, better_lo, better_hi)   # the rule decides, not us
print("better pilot claim word:", better_band)
print("now the whole CI (low 0.63) clears 0.61, so 'substantial' is finally earned and honest")
'''))

C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
Recite the mature sentence's six jobs (n · kappa · CI · band word · why-wide · disagreements).
Then: which two of those six are the parts a dishonest version would drop, and why exactly
those two?
'''))

C.append(md('''
## The concept at three levels (say each in one breath)

- **To a beginner:** "We checked if our robot grader agrees with a person. It mostly does, but
  on a small test, so we say 'pretty good, leaning right' instead of pretending it's perfect —
  and we show the few cases they disagreed on, because those are the interesting ones."
- **To an engineer:** "Pilot inter-rater κ ≈ 0.5 on n=30, bootstrap 95% CI straddles the
  0.61 Landis–Koch boundary, so the claim is 'moderate, directional' — point-and-CI gated, no
  band rounding. Disagreement set is logged as labeled error cases for the improvement loop."
- **To a founder:** "Our eval is honestly calibrated, not optimistically reported: a small
  first study shows the automated judge tracks human judgment in the right direction, we state
  the uncertainty plainly, and the disagreements are already a backlog of concrete fixes — so
  no number on stage is one a sharp investor could puncture."
'''))

C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "Your kappa is only ~0.5. Isn't your eval just bad?"**
<details><summary>answer</summary>It is moderate and directional on a 30-call pilot — better than chance, pointing the right way, with a wide CI because n is small. We are not claiming substantial; we are claiming honestly. The disagreements are logged as the next round's fixes, which a "good number with no leads" would not give us.</details>

**2. "Why won't you just say 'substantial agreement'? The number rounds there."**
<details><summary>answer</summary>The claim rule: 'substantial' requires the point in 0.61–0.80 AND the entire 95% CI at or above 0.61. Our CI's lower end is below 0.61, so the data does not license the word. Saying it anyway would be quiet fraud the first sharp listener could expose by asking for the interval.</details>

**3. "Why are you showing me the cases where you disagreed? Isn't that admitting failure?"**
<details><summary>answer</summary>The opposite — the disagreements are the deliverable. Each is a concrete call where human and judge diverged, which is exactly the material the improvement loop (book 16) and preference pairs (book 17) are built from. A pilot with zero disagreements would be comfortable and useless.</details>
'''))

C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own the full ownership layer: where this calibration lives in the real pipeline
(`signals.py`, `judge.py`, `rubric.yaml`), the **mature sentence** built from the numbers so it
cannot drift, the three-level explanation, the three defense answers — and above all, the
reflex to present a mediocre number as an honest, useful asset rather than hide or inflate it.
This feeds directly into book 16, where the disagreements become improvement examples.
'''))

C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The Landis–Koch bands around the one boundary that matters (0.61) — name the two bands it
   separates
2. The claim rule, exactly: when may you say "substantial," and what do you say otherwise
3. Why the CI (not the point) is the part that keeps you honest, and why it is wide here
4. Why the disagreements are the deliverable, not the shame — and which later book consumes them
5. The mature sentence's six jobs, said as one fluent sentence

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))

C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you would say in a room about presenting a mediocre number

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))

C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Small sample, honest framing, disagreements shown proudly."**

If yours captures that in your own words — a mediocre number presented without fraud and
without shame — this book did its job. Next on the ladder: **book 16 · improvement examples**,
where those disagreements you logged stop being a calibration footnote and become the training
material that makes the judge better.
'''))

C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "15_pilot_calibration_honestly.ipynb"   # <- this notebook's filename
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

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "15_pilot_calibration_honestly.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
