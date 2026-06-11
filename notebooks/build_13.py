#!/usr/bin/env python3
# Builds 13_confusion_matrix.ipynb — VoiceForge University book 13.
# The ONE atomic concept: TP/FP/TN/FN, and WHICH error type kills a failure-detector
# (a missed failure = False Negative = the dangerous cell). accuracy / precision / recall in
# plain words, and the accuracy-is-enough trap. Same four-act skeleton + markers as build_P00.py.
# Rerun:      .venv/bin/python notebooks/build_13.py
# Then gate:  .venv/bin/python notebooks/run_nb.py   notebooks/13_confusion_matrix.ipynb
#             .venv/bin/python notebooks/audit_nb.py notebooks/13_confusion_matrix.ipynb
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
# 13 · Confusion matrix, accuracy, precision, recall

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Build a **2x2 confusion matrix** BY HAND from a list of toy labels — count the four cells
   **TP / FP / TN / FN** yourself before any library does it.
2. Say **accuracy, precision, recall** in plain words (not formulas first) and compute each by hand.
3. Name, for a **failure-DETECTOR**, the ONE cell that is dangerous — a **missed failure (FN)** —
   and explain why it is worse than a false alarm (FP).
4. Walk into the **accuracy-is-enough trap** on purpose, and defend why a 92%-accurate detector
   can still be useless for catching failures.

The topic is four numbers in a little square. The reason it earns a whole book: those four
numbers are the difference between "my detector is 92% accurate" and "my detector misses half
the failures it exists to catch."
'''))
C.append(md('''
## 2 — Knowledge-flow map (where this book sits on the ladder)

`12 · calibration (judge vs human)  →  THIS · confusion matrix, accuracy, precision, recall  →  14 · Cohen's kappa`

Book 12 lined up a **judge's** label against a **human's** label on the same calls — two
labelers, one truth. But "they agreed 90% of the time" hides *how* they disagreed. This book
gives you the instrument that shows the shape of the disagreement: a **2x2 table** that splits
every prediction into four buckets, so "wrong" stops being one lump and becomes *which kind of
wrong*. Book 14 then takes that same agreement and asks a sharper question — "is this agreement
better than two people guessing?" — with **Cohen's kappa**, which is literally built on top of
the same four counts you learn to make here. No 2x2 here → nothing for kappa to correct there.
'''))
C.append(md('''
## 3 — Baby intuition

A smoke alarm has exactly two jobs, and exactly two ways to fail.

- It can **scream when there is no fire** (annoying — you wave a towel at it, maybe pull the
  battery). That is a **false alarm**.
- It can **stay silent when the kitchen is actually burning** (catastrophic). That is a
  **missed fire**.

Both are errors. They are *not* the same size of error. A smoke alarm that never false-alarms
but sleeps through real fires is worse than useless — it is dangerous, because it *looks* like
protection. The whole point of this book is to stop scoring a detector by "how often is it
right?" and start scoring it by **"which way does it go wrong, and does that way kill someone?"**

A VoiceForge **failure-detector** is a smoke alarm for bad calls. A missed failure is a fire
that burned while the alarm stayed quiet.
'''))
C.append(md('''
## 4 — The formal version

A **binary classifier** makes a yes/no call. Ours is a **failure-detector**: for each call it
predicts *"did this call FAIL?"* — `1` = "yes, flag it as a failure", `0` = "no, looks fine".

Two ingredients, never to be confused:
- **truth** (a.k.a. the *label* / *ground truth*): did the call actually fail? (from book 06's
  task-success check, or a human reviewer). `1` = really failed, `0` = really fine.
- **prediction**: what the detector *guessed*. `1` = flagged, `0` = passed.

Cross those two yes/no axes and every call lands in one of **four** cells. The names are written
from the **detector's point of view** — "positive" means "the detector raised its hand":

| cell | truth | prediction | plain name |
|---|---|---|---|
| **TP** true positive  | failed (1) | flagged (1)     | caught a real failure |
| **FP** false positive | fine (0)   | flagged (1)     | **false alarm** — flagged a good call |
| **TN** true negative  | fine (0)   | passed (0)      | correctly let a good call through |
| **FN** false negative | failed (1) | passed (0)      | **MISSED FAILURE** — the dangerous one |

Memorize the second word by the **prediction**: *Positive* = the detector said "fail".
Memorize the first word by *correctness*: *True* = it was right. So **FN** = "the detector said
*Negative* (fine), and it was *False* (wrong)" = a real failure that slipped through silently.
'''))
C.append(md('''
## 5 — Why this book exists (the business reason)

VoiceForge sells **trust**: "we catch the bad calls before your customers do." A detector that
catches bad calls is the product. So the first fair question a founder gets asked is not "how
accurate is it?" — it is **"how many real failures does it MISS?"** Those two questions have
*different answers*, and confusing them is how teams ship a dashboard that looks green while
failures leak straight through.

Concretely: book 06 (`schemas/task_outcome.md`) already gives us a deterministic *truth* for
"did the task complete?" Pair that truth with any *predictor* of failure — a threshold on a
judge score, a heuristic, a model — and you have a classifier whose four cells you must be able
to read. This book builds that reading from nothing, on labels small enough to count on your
fingers, before you trust any `sklearn` one-liner. The next cell is your first run.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just syntax.

# We print a sentence so you can see WHERE output appears (directly under the cell) and so your
# first action is a run you committed to. PREDICT - what exact text will appear below?
print("a detector that misses failures can still look 'accurate'")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. A failure-detector predicts `1` or `0` — in words, what does each mean?
2. What are the four cells of the confusion matrix, by their letters (TP / FP / TN / FN)?
3. Which single cell is the *missed failure*, and why is "Negative" in its name even though a
   real failure happened?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a classifier is "right or wrong", and a good one is right
a lot. After Act 1 you should hold a sharper idea: "wrong" splits into **two different errors**
(false alarm vs missed failure), they are **not equally costly**, and for a *failure-detector*
the missed failure (**FN**) is the one that quietly hurts. The 2x2 table is the instrument that
keeps those two errors from blurring into one "accuracy" number.

If you can say that in your own words, continue. If not, re-read cell 4 (the four-cell table).
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of why "how often is it right"
# is the wrong first question for a failure-detector. Producing the sentence is the learning;
# reading mine would only feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so a skim cannot pass for understanding: the cell nags until you write something.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: build the 2x2 by hand from toy labels

## The toy data, printed RAW

Course rule: see the ugly input before transforming it. We start with the smallest thing that
carries the whole lesson — **ten calls**, each with two facts: did it *truly* fail (`truth`),
and did our detector *flag* it (`pred`). Both are `1`/`0`. We print the raw list untouched first.
'''))
C.append(code('''
# Ten toy calls. Each row is (truth, pred): truth=1 means the call really failed; pred=1 means
# our detector flagged it. We hand-pick the rows so all four cells (TP/FP/TN/FN) appear - a toy
# that only had correct rows could not teach the error cells, which are the point of the book.
# 1 = "failure" is the POSITIVE class because the detector's job is to raise its hand on failures.
labels = [
    # (truth, pred)
    (1, 1),   # really failed, flagged      -> a caught failure
    (1, 1),   # really failed, flagged      -> a caught failure
    (0, 0),   # really fine,   passed       -> correctly let through
    (0, 0),   # really fine,   passed       -> correctly let through
    (0, 0),   # really fine,   passed       -> correctly let through
    (0, 1),   # really fine,   FLAGGED      -> false alarm
    (1, 0),   # really FAILED, passed       -> MISSED failure
    (1, 0),   # really FAILED, passed       -> MISSED failure
    (1, 1),   # really failed, flagged      -> a caught failure
    (0, 0),   # really fine,   passed       -> correctly let through
]

# Print the raw rows first (course habit: see the input before computing anything from it).
for truth, pred in labels:                 # one line per call so each row is visibly one THING
    print("truth =", truth, " pred =", pred)
print("total calls:", len(labels))
'''))
C.append(md('''
## How to read this tiny dataset (the 3-move ritual for a small structure)

1. Say the **count**: "ten calls."
2. Say what **one row IS**: "one row = one call's `(truth, pred)` — what really happened, and
   what the detector guessed."
3. Read **one single cell** aloud: "row 6 is `(0, 1)` — a *fine* call that the detector
   *flagged* — a false alarm."

Never read data as a wall. Rows are *things*; the two numbers are *facts about the thing*.
'''))
C.append(md('''
## PREDICT
Before any counting, eyeball the ten rows above and commit to all four counts:
- **TP** (truth 1, pred 1 — caught failures) = ?
- **FP** (truth 0, pred 1 — false alarms) = ?
- **TN** (truth 0, pred 0 — correct passes) = ?
- **FN** (truth 1, pred 0 — missed failures) = ?

They must add up to 10. Write your four numbers in the next cell before we count.
'''))
C.append(code('''
# YOUR TURN - lock your four counts BEFORE we tally them, so this notebook records YOUR thinking
# and a later cell can confront it. The gap between guess and count is the lesson.
my_TP = None    # <- replace None with your integer
my_FP = None    # <- replace None with your integer
my_TN = None    # <- replace None with your integer
my_FN = None    # <- replace None with your integer

# Guard: unfilled (all None) prints a nag and never crashes a fresh run.
if None in (my_TP, my_FP, my_TN, my_FN):
    print("fill in all four counts above (they should sum to 10), then re-run.")
else:
    print("locked:", "TP", my_TP, "FP", my_FP, "TN", my_TN, "FN", my_FN,
          "| sum =", my_TP + my_FP + my_TN + my_FN)
'''))
C.append(md('''
## Count the four cells BY HAND (fully unrolled, nothing hidden)

Manual-before-function: we walk the ten rows one at a time and decide which of the four cells
each lands in. We print the verdict per row so the classification is *visible*, not buried
inside a library call. The rule for each row is just the pair `(truth, pred)`.
'''))
C.append(code('''
# Walk every row and bucket it into exactly one of the four cells. We start all four at 0 and add
# one per row, printing the decision, so you SEE the matrix being built rather than trusting a sum.
TP = FP = TN = FN = 0
for truth, pred in labels:
    if truth == 1 and pred == 1:           # really failed AND flagged -> caught a real failure
        TP += 1
        cell = "TP (caught failure)"
    elif truth == 0 and pred == 1:         # really fine BUT flagged   -> false alarm
        FP += 1
        cell = "FP (false alarm)"
    elif truth == 0 and pred == 0:         # really fine AND passed     -> correct pass
        TN += 1
        cell = "TN (correct pass)"
    else:                                  # truth == 1 and pred == 0   -> real failure passed!
        FN += 1
        cell = "FN (MISSED failure)"
    print(f"truth={truth} pred={pred} -> {cell}")

print("\\nby hand:  TP =", TP, " FP =", FP, " TN =", TN, " FN =", FN)
print("sum of cells:", TP + FP + TN + FN, "(must equal", len(labels), "- every call lands in exactly one cell)")
'''))
C.append(code('''
# Confront your prediction (the metal-detector reading: a gap here is exactly what to study).
# We only compare if you filled the guesses in - the guard keeps an unfilled notebook clean.
if None not in (my_TP, my_FP, my_TN, my_FN):
    matched = (my_TP, my_FP, my_TN, my_FN) == (TP, FP, TN, FN)
    print("your four counts", "MATCHED" if matched else "DIFFERED")
    if not matched:
        print("  you:", (my_TP, my_FP, my_TN, my_FN), " actual:", (TP, FP, TN, FN))
        print("  the cell you missed is the one worth re-counting by hand")
'''))
C.append(md('''
## Lay the four counts into the actual 2x2 square

The four numbers are not a list — they are a **table** with a meaning baked into its layout.
Rows = the **truth**; columns = the **prediction**. Reading the table is a skill (book P00's
chart ritual applies): say what a row is, what a column is, what one cell is.
'''))
C.append(code('''
# Arrange the four counts as the conventional 2x2: rows are TRUTH (did it really fail), columns
# are PREDICTION (did we flag it). We print it as a labeled grid so the layout itself teaches the
# meaning - a bare 2x2 of numbers with no labels is how confusion matrices get misread.
print(f"{'':>16}{'pred=fail(1)':>14}{'pred=fine(0)':>14}")
print(f"{'truth=fail(1)':>16}{TP:>14}{FN:>14}   <- a failed call is either CAUGHT (TP) or MISSED (FN)")
print(f"{'truth=fine(0)':>16}{FP:>14}{TN:>14}   <- a fine call is either false-alarmed (FP) or passed (TN)")
print()
# Two diagnostics that name the dangerous rows directly:
print("real failures total:", TP + FN, "->", TP, "caught,", FN, "MISSED")
print("good calls total:   ", TN + FP, "->", TN, "passed,", FP, "false-alarmed")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, out loud, in this shape:
> "Of the ___ calls that truly failed, the detector caught ___ (TP) and **missed** ___ (FN);
> the missed ones are real failures that slipped through with no alarm."
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
1. In the 2x2 above, which axis is the truth and which is the prediction?
2. Point at the FN cell and say what a number sitting there *means* for a real customer.
3. Why must TP + FP + TN + FN equal the number of calls, always?
'''))
C.append(md('''
## Now define accuracy — in plain words first, then the formula

**Accuracy** in plain words: *"out of all calls, how many did the detector get right?"* Right
means the prediction matched the truth — that is the two cells on the diagonal, **TP** (correctly
caught) and **TN** (correctly passed). Everything off the diagonal (FP, FN) is a mistake.

$$\\text{accuracy} = \\frac{TP + TN}{TP + TN + FP + FN}$$

We compute it by hand from the counts — no library — so the formula stays attached to the cells.
'''))
C.append(md('''
## PREDICT
From the counts (TP, TN on the diagonal; FP, FN off it), what fraction will accuracy be?
Commit to a number between 0 and 1 (or a percent) before the next cell prints it.
'''))
C.append(code('''
# YOUR TURN - predict accuracy as a fraction in [0,1] before it is computed.
my_accuracy_guess = None    # <- replace None with e.g. 0.7

if my_accuracy_guess is None:
    print("fill in my_accuracy_guess (a number 0..1) above, then re-run.")
else:
    print("locked: I expect accuracy ~", my_accuracy_guess)
'''))
C.append(code('''
# Accuracy by hand: the two CORRECT cells (TP+TN) over ALL cells. We divide by the explicit sum
# of all four, never a hardcoded 10, so the line stays true if the dataset changes later.
# Named acc_by_hand (not 'accuracy') because later we define an accuracy() FUNCTION - keeping the
# scratch value and the reusable function as separate names avoids one shadowing the other.
correct = TP + TN                              # the diagonal: predictions that matched the truth
total = TP + TN + FP + FN                       # every call lands in exactly one cell, so this is N
acc_by_hand = correct / total
print("accuracy =", round(acc_by_hand, 3), f"  ({correct} correct out of {total})")

# Confront the prediction.
if my_accuracy_guess is not None:
    print("your guess was", "close" if abs(my_accuracy_guess - acc_by_hand) <= 0.1 else "off",
          "- the gap, if any, is the thing to think about")
'''))
C.append(md('''
## Now precision — "when it raises the alarm, how often is it right?"

**Precision** in plain words: *"of all the calls the detector FLAGGED, what fraction truly
failed?"* It lives entirely in the **prediction = 1 column**: the flags that were right (**TP**)
over all the flags (**TP + FP**). High precision = few false alarms; you can trust a flag.

$$\\text{precision} = \\frac{TP}{TP + FP}$$

Precision is the answer to *"is this alarm worth my attention?"* — it ignores the calls we never
flagged, because it only judges the flags we *did* raise.
'''))
C.append(code('''
# Precision by hand: of everything we FLAGGED (the pred=1 column = TP + FP), how many truly failed
# (TP). We guard the denominator: if the detector flagged NOTHING, precision is undefined (0/0),
# and pretending it is 0 or 1 would be a lie - so we say so explicitly.
flagged = TP + FP                               # everything the detector raised its hand on
if flagged == 0:
    prec_by_hand = None
    print("precision = undefined (the detector flagged nothing - there is no flag to be right about)")
else:
    prec_by_hand = TP / flagged
    print("precision =", round(prec_by_hand, 3), f"  (of {flagged} flagged, {TP} truly failed)")
'''))
C.append(md('''
## Now recall — "of the real failures, how many did it CATCH?"

**Recall** in plain words: *"of all the calls that TRULY failed, what fraction did the detector
catch?"* It lives entirely in the **truth = 1 row**: the failures we caught (**TP**) over all the
real failures (**TP + FN**). High recall = few *missed* failures.

$$\\text{recall} = \\frac{TP}{TP + FN}$$

**This is the number a failure-detector lives or dies by.** Recall is `1 - (the miss rate)`. The
FN cell — the missed failure, the dangerous one — sits right in recall's denominator. Watch it.
'''))
C.append(md('''
## PREDICT
Recall = TP / (TP + FN). You know TP and FN from the by-hand count. Predict recall as a fraction.
And one extra: do you expect **recall to be higher or lower than accuracy** here? Commit to both.
'''))
C.append(code('''
# YOUR TURN - predict recall, and whether it is higher or lower than the accuracy you just saw.
my_recall_guess = None        # <- a number 0..1
my_recall_vs_accuracy = None  # <- "higher" or "lower" than accuracy

if my_recall_guess is None or my_recall_vs_accuracy is None:
    print("fill in BOTH (recall guess, and 'higher'/'lower' vs accuracy) above, then re-run.")
else:
    print("locked: recall ~", my_recall_guess, "and", my_recall_vs_accuracy, "than accuracy")
'''))
C.append(code('''
# Recall by hand: of all REAL failures (the truth=1 row = TP + FN), how many did we catch (TP).
# Guard the denominator: if there were no real failures at all, recall is undefined (nothing to
# recall) - again we refuse to invent a number.
real_failures = TP + FN                         # the truth=1 row: every call that actually failed
if real_failures == 0:
    rec_by_hand = None
    print("recall = undefined (no real failures in the data - nothing to catch)")
else:
    rec_by_hand = TP / real_failures
    print("recall =", round(rec_by_hand, 3), f"  (of {real_failures} real failures, {TP} caught,",
          FN, "MISSED)")

# Confront the predictions.
if my_recall_guess is not None and rec_by_hand is not None:
    print("your recall guess was", "close" if abs(my_recall_guess - rec_by_hand) <= 0.1 else "off")
    print("recall is in fact", "higher" if rec_by_hand > acc_by_hand else "lower", "than accuracy here")
'''))
C.append(md('''
## OBSERVE + EXPLAIN
Look at the three numbers together: **accuracy** (overall right), **precision** (flags you can
trust), **recall** (failures you actually catch). They are *different questions about the same
2x2*. Say in one sentence: which of the three would a customer who hates *missed* failures care
about most, and which cell (TP/FP/TN/FN) is dragging that number down?
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
Give the plain-words sentence for each of the three:
- accuracy = "out of all calls, ___"
- precision = "of the calls we flagged, ___"
- recall = "of the calls that truly failed, ___"

Then: which cell is in **recall's** denominator that is *not* in precision's? (That cell is the
missed failure.)
'''))
C.append(md('''
## Only NOW the function — it does exactly the by-hand thing

You counted the four cells and computed all three rates by hand, so a function now is a
*convenience, not a mystery*. We write our own `confusion()` helper (the by-hand counting loop
with a name) and three tiny metric functions, then check them against the numbers we already
trust. First we split the rows into two parallel lists — `y_true` and `y_pred` — because that is
the shape every ML tool expects (`sklearn`'s `confusion_matrix` / `recall_score` take exactly
this, and compute exactly this math; we build it ourselves so nothing is hidden).
'''))
C.append(code('''
# Split the (truth, pred) rows into two parallel lists - this 'y_true, y_pred' shape is the
# lingua franca of every ML metric function, so learning it once pays off across the whole field.
y_true = [truth for truth, pred in labels]      # the ground-truth column
y_pred = [pred for truth, pred in labels]       # the detector's prediction column
print("y_true:", y_true)
print("y_pred:", y_pred)
'''))
C.append(code('''
# Our own confusion() = the by-hand counting loop, given a name so we can reuse it without copy-
# paste. It takes the two parallel lists and returns the four cells. We name the POSITIVE class
# explicitly (pos=1 means 'failure' is the thing we detect) so the function reads like its intent.
def confusion(y_true, y_pred, pos=1):
    TP = sum(1 for t, p in zip(y_true, y_pred) if t == pos and p == pos)   # caught a real positive
    FP = sum(1 for t, p in zip(y_true, y_pred) if t != pos and p == pos)   # false alarm
    TN = sum(1 for t, p in zip(y_true, y_pred) if t != pos and p != pos)   # correct pass
    FN = sum(1 for t, p in zip(y_true, y_pred) if t == pos and p != pos)   # MISSED positive
    return TP, FP, TN, FN

# Run it and check against the by-hand counts we already trust - same numbers, two routes.
fTP, fFP, fTN, fFN = confusion(y_true, y_pred, pos=1)
print("function cells: TP", fTP, "FP", fFP, "TN", fTN, "FN", fFN)
print("by-hand  cells: TP", TP,  "FP", FP,  "TN", TN,  "FN", FN)
print("match:", (fTP, fFP, fTN, fFN) == (TP, FP, TN, FN))
'''))
C.append(code('''
# The three metric functions, each the plain-words idea with a name and a guarded denominator.
# We return None (not a fake 0) when a denominator is 0, because "undefined" is the honest answer.
def accuracy(TP, FP, TN, FN):
    total = TP + FP + TN + FN
    return (TP + TN) / total if total else None        # correct diagonal over all calls
def precision(TP, FP, TN, FN):
    return TP / (TP + FP) if (TP + FP) else None        # of the flags raised, how many were real
def recall(TP, FP, TN, FN):
    return TP / (TP + FN) if (TP + FN) else None        # of real failures, how many were caught

# Check each against the by-hand values from earlier in the act (same math, now reusable).
print("accuracy : function", round(accuracy(fTP, fFP, fTN, fFN), 3),  "| by hand", round(acc_by_hand, 3))
print("precision: function", round(precision(fTP, fFP, fTN, fFN), 3), "| by hand", round(prec_by_hand, 3))
print("recall   : function", round(recall(fTP, fFP, fTN, fFN), 3),    "| by hand", round(rec_by_hand, 3))
# Identical numbers, two routes: the function is the by-hand math with a name - the only reason to
# trust it is that you can reconstruct it. (sklearn.metrics gives the very same numbers.)
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before Act 2: a classifier was "right or wrong," scored by accuracy. After Act 2 you can build
the **2x2 by hand** from raw labels, count **TP/FP/TN/FN**, and compute **accuracy / precision /
recall** in plain words *and* with a reusable function you wrote — knowing precision lives in the
*flagged column*, recall lives in the *real-failures row*, and the **FN cell (missed failure)**
sits in recall's denominator. Those four counts are exactly what book 14's kappa will build on.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (the 2x2, or precision-vs-recall - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the matrix, then the trap that names this book

## Break-it philosophy

A metric you have never seen *lie* is a metric you do not understand. We now feed the confusion
matrix degenerate and adversarial inputs on purpose, and watch which metrics stay honest and
which collapse. Surprise here, at your desk, is education; surprise on the demo stage — a 92%
detector that misses every failure — is a disaster.
'''))
C.append(md('''
## PREDICT
First break: a detector that **flags nothing**. It predicts `0` (fine) for every single call —
the laziest possible "everything is fine" stamp. On a dataset where most calls really are fine,
predict: will its **accuracy** be high or low? And what will its **recall** be? Commit to both.
'''))
C.append(code('''
# BREAK-IT (guided) - the "always fine" detector: it predicts 0 for every call, catching nothing.
# This is NOT supposed to crash; it is supposed to be SILENTLY USELESS while scoring high accuracy,
# which is far more dangerous than a crash. We reuse the SAME y_true so the truth is unchanged.
y_pred_lazy = [0 for _ in y_true]               # flag nothing: predict 'fine' no matter what

# Count its four cells by hand again - the lazy detector never flags, so TP and FP are forced to 0.
TP2 = sum(1 for t, p in zip(y_true, y_pred_lazy) if t == 1 and p == 1)   # caught failures: none
FP2 = sum(1 for t, p in zip(y_true, y_pred_lazy) if t == 0 and p == 1)   # false alarms: none
TN2 = sum(1 for t, p in zip(y_true, y_pred_lazy) if t == 0 and p == 0)   # every fine call 'passes'
FN2 = sum(1 for t, p in zip(y_true, y_pred_lazy) if t == 1 and p == 0)   # every real failure MISSED
print("lazy detector cells: TP", TP2, "FP", FP2, "TN", TN2, "FN", FN2)

acc2 = (TP2 + TN2) / (TP2 + TN2 + FP2 + FN2)    # accuracy still counts the many correct TNs
rec2 = TP2 / (TP2 + FN2) if (TP2 + FN2) else None  # recall: caught / real failures
print("lazy accuracy:", round(acc2, 3), "  lazy recall:", rec2)
'''))
C.append(md('''
## Reading the lie (no crash, all wrong where it counts)

No traceback. The "always fine" detector posted a **respectable accuracy** — because most calls
in the data really are fine, and it gets every one of those right (all TN). But its **recall is
`0.0`**: it caught **zero** real failures. It is a smoke alarm with the battery removed that
still reads "92% of the time there's no fire, and I agree!"

This is the dangerous failure: not a crash (Python would tell you) but a **high accuracy sitting
next to a useless recall**. Accuracy was fooled because the *fine* class dominates the data and
accuracy rewards getting the majority right. Recall could not be fooled, because it only looks at
the *real failures* — and the detector caught none of them.
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
The lazy detector flags nothing yet scores high accuracy. Explain in one breath *why* accuracy
is high and *why* recall is 0 — using the words **TN**, **FN**, and **majority class**.
'''))
C.append(md('''
## A second break: a detector that flags EVERYTHING

The opposite degenerate: predict `1` (failure) for every call. Now nothing is ever missed — but
something else breaks instead. This shows the *other* end of the precision/recall seesaw.
'''))
C.append(md('''
## PREDICT
The "always fail" detector flags every call. Predict its **recall** (of real failures, how many
caught?) and its **precision** (of all the flags, how many were real?). Will precision be high or
low on a dataset that is mostly fine calls? Commit before running.
'''))
C.append(code('''
# BREAK-IT (guided) - the "always fail" detector flags every call. It is the mirror of the lazy one.
# Not supposed to crash; supposed to expose the cost of catching everything: a flood of false alarms.
y_pred_panic = [1 for _ in y_true]              # flag everything: predict 'failure' no matter what

TP3 = sum(1 for t, p in zip(y_true, y_pred_panic) if t == 1 and p == 1)  # every real failure caught
FP3 = sum(1 for t, p in zip(y_true, y_pred_panic) if t == 0 and p == 1)  # every fine call false-alarmed
TN3 = sum(1 for t, p in zip(y_true, y_pred_panic) if t == 0 and p == 0)  # none: nothing is ever passed
FN3 = sum(1 for t, p in zip(y_true, y_pred_panic) if t == 1 and p == 0)  # none: nothing is ever missed
print("panic detector cells: TP", TP3, "FP", FP3, "TN", TN3, "FN", FN3)

rec3 = TP3 / (TP3 + FN3) if (TP3 + FN3) else None      # perfect recall: misses nothing
prec3 = TP3 / (TP3 + FP3) if (TP3 + FP3) else None     # precision tanks: drowning in false alarms
print("panic recall:", rec3, "  panic precision:", round(prec3, 3))
print("=> recall 1.0 looks perfect, but precision", round(prec3, 3),
      "means most flags are false alarms - a detector that cries wolf on every call.")
'''))
C.append(md('''
## The seesaw, stated plainly

The two breaks are the two ends of a seesaw every detector sits on:
- **Flag nothing** → recall `0.0` (misses every failure), accuracy looks fine. Useless *quietly*.
- **Flag everything** → recall `1.0` (misses nothing), precision in the floor. Useless *loudly*.

A real detector lives in between, and **you choose where** by moving its threshold. The choice is
not "maximize one number" — it is *"which mistake can I least afford?"* For a failure-detector
whose job is to catch bad calls, a **missed failure (FN) usually costs more than a false alarm
(FP)** — so you bias toward **recall**, and pay for it in precision (more false alarms to sift).
This is the same trade you will tune with a real threshold in the scorecard pipeline.
'''))
C.append(md('''
## YOUR break now

Author your own predictions over the same `y_true`. Hand-write a `y_pred_mine` (ten 0/1 values)
that you design to fail in a *specific* way — say, "catch the easy failures but miss the subtle
ones," or "trade some false alarms for better recall." PREDICT in the comment what your four
cells will be and which metric you sacrificed, then run and check.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it. Design a y_pred_mine over the SAME y_true and predict its cells.
# my prediction: <write here: what four cells you expect, and which metric you deliberately hurt>

# Default below is a clean copy of y_true (a perfect detector) so an UNFILLED notebook runs clean.
# Edit the 0/1 values to inject your own mistakes - e.g. flip a 1 to 0 to create a missed failure.
y_pred_mine = list(y_true)                       # <- edit these ten values to design your detector
# example damage (uncomment and tweak): y_pred_mine[6] = 1   # turn a missed failure into a catch

# Count the four cells of YOUR detector and read its recall - did you create or remove an FN?
mTP = sum(1 for t, p in zip(y_true, y_pred_mine) if t == 1 and p == 1)
mFP = sum(1 for t, p in zip(y_true, y_pred_mine) if t == 0 and p == 1)
mTN = sum(1 for t, p in zip(y_true, y_pred_mine) if t == 0 and p == 0)
mFN = sum(1 for t, p in zip(y_true, y_pred_mine) if t == 1 and p == 0)
mrec = mTP / (mTP + mFN) if (mTP + mFN) else None
print("your cells: TP", mTP, "FP", mFP, "TN", mTN, "FN", mFN, "| recall:", mrec)
print("compare these to your written prediction above - any surprise is the lesson")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this whole book is built on

**The wrong belief:** "my failure-detector is **92% accurate**, so it is a good detector."

The next cell builds a realistic case: **100 calls**, of which only **8 truly failed** (failures
are rare — as they are in production). A detector flags so cautiously that it catches just **1**
of the 8 real failures, and raises **0** false alarms. Run it, then — *before the reveal* — work
out its accuracy and its recall, and decide whether you would ship it.
'''))
C.append(md('''
## PREDICT
100 calls, 8 real failures. The detector catches 1 failure, misses 7, and never false-alarms
(so it correctly passes all 92 fine calls). Predict its **accuracy** and its **recall**. Would
you put it on a slide that says "our detector catches bad calls"? Commit to all three.
'''))
C.append(code('''
# The trap, as a realistic confusion matrix. Failures are RARE (8 of 100) - the exact condition
# under which accuracy lies the loudest. We build the four cells directly from the story so the
# numbers are checkable: 1 caught, 7 missed, 0 false alarms, 92 fine calls all passed.
trap_TP = 1                     # caught 1 of the 8 real failures
trap_FN = 7                     # MISSED the other 7 real failures - the dangerous cell, full
trap_FP = 0                     # raised zero false alarms (looks 'precise' and 'clean')
trap_TN = 92                    # correctly passed all 92 genuinely-fine calls

trap_total = trap_TP + trap_FN + trap_FP + trap_TN
trap_acc = (trap_TP + trap_TN) / trap_total                       # diagonal over all
trap_rec = trap_TP / (trap_TP + trap_FN)                          # caught / real failures
trap_prec = trap_TP / (trap_TP + trap_FP)                         # caught / all flags
print("trap cells: TP", trap_TP, "FP", trap_FP, "TN", trap_TN, "FN", trap_FN, "(of", trap_total, "calls)")
print("accuracy :", round(trap_acc, 3))
print("precision:", round(trap_prec, 3))
print("recall   :", round(trap_rec, 3))
'''))
C.append(md('''
## The reveal

**Accuracy = 0.93.** Precision = 1.0 (every flag it raised was a real failure — it never cried
wolf). Both look fantastic on a slide. And the detector **missed 7 of the 8 failures it exists to
catch** — **recall = 0.125**. It found one bad call in eight and slept through the rest.

Accuracy was fooled because the *fine* class is 92% of the data: a detector can nail the easy
majority (all those TN) and be applauded for "93%" while failing utterly at its one job. Even
*precision* looked perfect here — because it only judges the flags raised, and the one flag
happened to be right. **Recall is the only one of the three that counted the missed failures**,
because the FN cell sits in *its* denominator alone.

**This is the accuracy-is-enough trap:** on rare-event detection, accuracy and even precision can
glow while recall — the number that measures *missed failures* — is on the floor. The cell that
matters for a failure-detector is **FN**, and only recall watches it. (This is exactly why book
14's kappa exists: "92% agreement" between a judge and a human can be almost entirely the easy
agree-it's-fine majority — kappa subtracts that chance baseline out.)
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why can accuracy be 0.93 while the detector is useless?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
The trap detector scored accuracy 0.93 AND precision 1.0 — yet you would not ship it. Name the
one metric that exposed it and the one cell that metric watches. Then: why does accuracy get
*more* misleading as real failures get *rarer*?
'''))
C.append(md('''
## A third break: the divide-by-zero hiding in precision/recall

One more failure mode — a *crash* this time, the honest kind. If a detector flags nothing,
precision is `TP / (TP + FP)` = `0 / 0`. We protected against this earlier with a guard; here we
show what the raw formula does WITHOUT the guard, so you respect why the guard exists.
'''))
C.append(code('''
# BREAK-IT (guided) - SUPPOSED to error: the raw precision formula with no guard, on a detector
# that flagged nothing. 0/0 is undefined - Python raises ZeroDivisionError rather than invent a
# number, which is the FRIENDLY failure (a crash you can see beats a fake 0.0 you would trust).
no_flags_TP = 0
no_flags_FP = 0
precision_unguarded = no_flags_TP / (no_flags_TP + no_flags_FP)   # 0 / 0 -> ZeroDivisionError
print("precision:", precision_unguarded)   # we never reach here - the division raises first
'''))
C.append(md('''
## Reading the crash, and why a guard beats a fake number

`ZeroDivisionError` is the formula being honest: with no flags raised, "what fraction of flags
were right?" has **no answer**, and a crash says so. The dangerous alternative would be silently
returning `0.0` (or `1.0`) — a made-up number that flows into a dashboard and lies. Our guarded
versions earlier printed *"undefined"* on purpose. A crash you can read beats a wrong number you
cannot; a guard that names "undefined" is better still. (Note: `sklearn` defaults such cases to
`0.0` with a warning — convenient, but you must know the real answer is "undefined", not zero.)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a high accuracy felt like a good detector. After Act 3 you know the two degenerate
detectors (flag-nothing → recall 0 but high accuracy; flag-everything → recall 1 but precision
floor), the **seesaw** you tune by choosing *which mistake you can least afford*, and the
**accuracy-is-enough trap**: on rare failures, accuracy (and even precision) can glow while
**recall** — the only metric watching the **FN / missed-failure** cell — is on the floor.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the accuracy-is-enough trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this lives in VoiceForge, and how to defend it

## Where the confusion matrix lives in the real pipeline

This is not a notebook toy — it is how VoiceForge *grades its own graders*:
- **`schemas/task_outcome.md`** gives a deterministic **truth** for "did the task complete?"
  (book 06). That `task_completed = False` is the ground-truth `1` ("this call failed") for a
  failure-detector.
- Any **predictor** of failure — a threshold on a judge dimension in **`rubric.yaml`**
  (e.g. `latency_gap.laggy_ms: 800`, `barge_in.threshold_overlap_ms: 100`), a heuristic in
  **`pipeline/signals.py`** (`analyze()` flags barge-ins and laggy gaps), or the Gemini judge in
  **`pipeline/judge.py`** — produces the **prediction**. Truth vs prediction = a 2x2.
- The real **hero call** (`data/hero/turns.json`, the Telugu-English interruption call = `call_C`)
  is a *true failure* (the area never resolves; agent barges in at t3). If a detector passed it,
  that is an **FN** — a missed failure — the single most expensive cell to land in.
'''))
C.append(md('''
## PREDICT (connect to the real cast)

The recurring cast: **call_A** truly succeeds, **call_B** is a partial, **call_C** truly fails.
Suppose a cheap detector flags a call as "failure" only when it sees an explicit barge-in. It
would catch call_C (which has one) but might pass call_B (whose failure is subtler — a shaky,
unconfirmed number). For *that* detector, which call would be the **FN** (missed failure)? Write
your answer, then read on.
'''))
C.append(code('''
# YOUR TURN - which cast call becomes the missed failure (FN) for a barge-in-only detector?
my_fn_call = ""   # <- "call_A" / "call_B" / "call_C"

if len(my_fn_call.strip()) < 5:
    print("name the call above (call_A / call_B / call_C), then re-run.")
else:
    print("you said the missed failure (FN) would be:", my_fn_call)
    # The reveal: call_B truly failed (partial - number never confirmed) but has no barge-in, so a
    # barge-in-only detector PASSES it -> truth=fail, pred=fine = FN, the dangerous cell.
    print("worked answer: call_B - it truly failed but lacks the one cue this detector looks for,")
    print("so it slips through as a missed failure (FN). call_C's barge-in gets caught (TP).")
'''))
C.append(md('''
## The concept at three levels (say each to its audience)

- **For a beginner:** "Our failure-catcher can be wrong two ways: it can yell about a good call
  (annoying), or it can stay quiet on a bad one (dangerous). We care most about the quiet misses."
- **For an engineer:** "It's a binary classifier; truth × prediction gives a 2x2 of TP/FP/TN/FN.
  Accuracy hides class imbalance, so on rare failures we report **recall** (TP/(TP+FN)) as the
  primary metric and watch the FN cell, trading precision for recall via the decision threshold."
- **For a founder:** "We don't claim '92% accurate' — that number can hide that we miss most bad
  calls. We report what fraction of *real* failures we catch, because a missed failure is what
  reaches a customer, and that's the number our trust pitch actually rests on."
'''))
C.append(md('''
## Defense questions (×3 — try to answer before opening each)

**1. "Your failure-detector is 92% accurate. Isn't that great?"**
<details><summary>answer</summary>Not on its own. If failures are 8% of calls, a detector that flags nothing scores ~92% accuracy while catching zero failures — accuracy rewards the easy majority. The number that matters is recall: of real failures, how many we catch. I'd show you recall and the FN count, not accuracy.</details>

**2. "Why would you ever accept more false alarms (lower precision)?"**
<details><summary>answer</summary>Because for a failure-detector a missed failure (FN) usually costs more than a false alarm (FP): a false alarm wastes a reviewer's minute; a missed failure reaches a customer. So we bias the threshold toward recall and pay in precision — within reason, since too many false alarms get the alarm ignored. It's a cost choice, not a math maximum.</details>

**3. "Precision was 1.0 in your trap example — wasn't that detector at least trustworthy?"**
<details><summary>answer</summary>Precision 1.0 only means every flag it *did* raise was real — it says nothing about the failures it never flagged. That detector missed 7 of 8 failures (recall 0.125). Precision judges the flags raised; recall judges the failures caught. For catching bad calls, recall is the one that counts, and the FN cell only shows up there.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own: where the confusion matrix lives in the real pipeline (truth from
`task_outcome.md`, predictions from `rubric.yaml` thresholds / `signals.py` / `judge.py`), which
cast call is the FN for a naive detector, why a missed failure (FN) is the cell to fear, and how
to defend "report recall, not accuracy" to a beginner, an engineer, and a founder. Next book
takes the *agreement* between two labelers and asks if it beats chance — Cohen's kappa.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. Draw the 2x2 from memory: which axis is truth, which is prediction, and name all four cells.
2. Say accuracy, precision, and recall in plain words (one sentence each).
3. For a failure-detector, which cell is the dangerous one (FN), and why is it called *Negative*.
4. The accuracy-is-enough trap: how a 92%-accurate detector can miss most failures — name the
   metric that exposes it.
5. One real place in VoiceForge a missed failure (FN) would hurt (hint: the hero call passing).

Missed one? Open it back up, find the act, redo it. That is the system working — not a failure.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (where this lives / three-level explanation)
my_clean_sentence = ""      # the sentence you would say in a room about confusion matrices

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Knowing WHICH way it is wrong matters more than how often."**

If your sentence captures that — a detector's value is set by *which* error it makes (a missed
failure vs a false alarm), not by a single "how often is it right" number — this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "13_confusion_matrix.ipynb"   # <- this notebook's filename
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

**13 done** (pending your teach-back) → **14 · Cohen's kappa** — you can now count the four cells
when two labelers (a judge and a human) label the same calls. But "they agreed 90% of the time"
is haunted by the same ghost as accuracy: most of that agreement can be the easy "it's fine"
majority. Kappa subtracts out the agreement you'd get *by chance* and reports what is left —
built directly on the four counts you learned to make here.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "13_confusion_matrix.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
