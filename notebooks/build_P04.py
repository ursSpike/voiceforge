#!/usr/bin/env python3
# Builds P04_debugging_confusion.ipynb — the debug-ritual book of VoiceForge University.
# The ONE atomic concept: when output surprises you, print the input, print the intermediate,
# shrink the example — do not guess. Mirrors build_P00.py exactly (md()/code() helpers).
# Rerun: .venv/bin/python notebooks/build_P04.py
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
# P04 · Debugging confusion

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Run the **debug ritual** on any surprising output: **print the input → print the
   intermediate → shrink the example** — and never *guess*
2. Read a **traceback bottom-up**: last line = *what*, then walk up to *where*
3. Catch **silent wrongness** — a number that is wrong with no error at all — and explain
   why it scares you more than a crash
4. Use the **stale-state** recap from P00 to rule out "the kernel is lying to me" first

The data here is toy on purpose (coffee bills, tips). The topic is not the point.
The *ritual* is the point — it is the move you will make every time a VoiceForge number
surprises you on a demo stage.
'''))
C.append(md('''
## 2 — Knowledge map

`P03 (plots) → THIS · DEBUGGING CONFUSION → book 00 (what VoiceForge is)`

Why this book exists, right here in the ladder: P01–P03 taught you to build call-log
objects, read them as tables, and plot them. Plots are where confusion *first shows up* —
a bar is taller than you expected, a number reads wrong. P03 hands you the surprise.
This book hands you the **response to the surprise**. After P04 you stop staring at wrong
output and start *interrogating* it. Then book 00 opens the real VoiceForge pipeline, where
every wrong number you meet, you will debug with exactly this ritual.
'''))
C.append(md('''
## 3 — Baby intuition

A wrong number on the screen is not an accusation — it is a *clue with a location*. The
beginner reaction is to stare at the wrong number and guess what went wrong ("maybe the
formula is off? maybe rounding?"). Guessing is the slowest possible debugging: it edits the
*story* in your head instead of *looking* at the data.

The ritual replaces guessing with looking. Three boring looks, in order: look at what went
**in** (the input), look at the value **halfway through** (the intermediate), and if it is
still hiding, **cut the data down** until the bug has nowhere left to hide. Boring beats
clever, every time, because boring is repeatable under stress.
'''))
C.append(md('''
## 4 — The formal version

The **debug ritual**, as a checklist you will run dozens of times across this course:

| step | what you actually do | what it rules out |
|---|---|---|
| 1. print the input | print the RAW object, before any transform | "the data wasn't what I assumed" |
| 2. print the intermediate | print the value halfway through the computation | "the bug is downstream of where I think" |
| 3. shrink the example | cut the data to the smallest case that still misbehaves | "too much data is hiding the cause" |

One rule wraps all three: **do not guess.** Every step replaces a guess with a printed
fact. A guess updates your story; a print updates your *model*. Only one of those is true.

Three words this book leans on:
- **traceback** — the wall of red Python prints when a cell crashes; read it bottom-up
- **silent wrongness** — a wrong answer with NO error: the cell runs green and lies
- **shrink** — reducing the input to the smallest case that still reproduces the bug
'''))
C.append(md('''
## 5 — First, rule out the kernel (the P00 stale-state recap)

Before you debug your *code*, rule out the *machine*. From P00: a notebook's truth is the
**kernel's memory**, not the page. If you ran cells out of order, or ran one twice, a
variable can hold a value the page no longer shows — **stale state**. A "bug" that is really
stale state will waste an hour of real debugging.

So step zero of every confusing moment: ask "could this be stale?" The next two cells make
a stale value bite, then show the one move that clears it.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just syntax.

# We set a running bill total. The IMPORTANT part (from P00): bill_total now lives in the
# KERNEL'S memory, not in this cell — the cell is just the spell that put it there.
bill_total = 100
print("bill_total is now", bill_total)
'''))
C.append(code('''
# PREDICT, then run this cell TWICE in a row (deliberately). Predict bill_total before the 2nd run.

# We add a 20-rupee item. Because bill_total lives in kernel memory, running this twice adds
# the item TWICE — the page text never changes, but the MEMORY does. That mismatch between
# "what the page says" and "what the kernel holds" is stale state, the #1 fake bug.
bill_total = bill_total + 20
print("bill_total is now", bill_total)
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. After running the add-item cell twice, what is `bill_total`, and why is it not 120?
2. When a number looks wrong, what is the *step-zero* question — before you suspect your code?
3. What single move gives you a clean slate to rule out stale state for good?
   (Hint from P00: it starts with "restart".)
'''))
C.append(code('''
# YOUR TURN - the clean-slate move, written as the literal menu action you would take.
# Producing the sentence is the learning; reading mine would just feel like learning.
restart_move = ""   # <- e.g. "Restart kernel, then Run All from the top"

# A gentle gate so you cannot skim past: the cell nags until you write something real.
if len(restart_move.strip()) < 12:
    print("write the clean-slate move above (12+ chars), then re-run this cell.")
else:
    print("STALE-STATE RULED OUT BY:", restart_move)
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a wrong number means my code is wrong. After Act 1 you
should hold two ideas: (1) a wrong number is a *located clue*, not an accusation, and (2) the
machine itself can lie via **stale state**, so ruling that out is step zero. P03 handed you
surprising plots; this book is teaching you to *respond* to surprise instead of guessing.

If that feels yours-in-your-own-words, continue. If not, re-run cells 6–7 and watch the
stale value bite.
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: a wrong-number bug, taken apart by ritual

## The setup: a tip calculator that lies

We will compute a 10% tip on a coffee bill. The bill has a few items. The tip will come out
**wrong** — not crash, just *wrong*. That is the whole point: this is the dangerous kind of
bug, the kind that prints a clean number and lets you ship it.

We meet the bug RAW first (course rule: raw before transformed, manual before function),
then take it apart one ritual step at a time.
'''))
C.append(md('''
## PREDICT
Here are four coffee prices in rupees: `[40, 60, 90, 110]`.
1. What is their **total**?
2. A **10% tip** on that total is …?
Commit to both numbers now — you will write them down in the next cell.
'''))
C.append(code('''
# YOUR TURN - predictions are written BEFORE the computing cell runs, so the notebook becomes
# a record of YOUR thinking and a later cell can compare your guess against reality.
my_total_guess = None   # <- replace None with your number
my_tip_guess = None     # <- replace None with your number (10% of the total)

if my_total_guess is None or my_tip_guess is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("predictions locked: total", my_total_guess, "| tip", my_tip_guess)
'''))
C.append(code('''
# The buggy calculator, met RAW. Read the output — do NOT fix anything yet.
prices = [40, 60, 90, 110]

# We intend: total of the prices, then 10% of that total. One of these two lines is wrong
# in a way that prints a believable number instead of crashing — that is what makes it nasty.
total = sum(prices)
tip = total / 10 / 100        # <- the bug hides in here; the output will look plausible
print("total:", total)
print("tip (should be 10% of total):", tip)
'''))
C.append(md('''
## OBSERVE — does the output match your prediction?

You predicted a tip of **41** (10% of 300). The cell printed **0.3**. It did not crash. It
printed a clean, confident, *wrong* number. If you were moving fast, "0.3" might slip past —
it is a number, it is positive, it looks like it could be a tip on something.

This is the moment the ritual exists for. We do NOT guess which line is wrong. We *look*.
'''))
C.append(md('''
## Ritual step 1 — print the input

The first look is always the raw input, because the cheapest explanation for a wrong output
is that the input was never what you assumed. Print the object, its length, its types.
'''))
C.append(code('''
# Step 1: print the input. Three boring prints that rule out "the data wasn't what I thought".
print("prices:", prices)                    # the raw object itself
print("count:", len(prices))                # how many items (we expect 4)
print("types:", [type(p).__name__ for p in prices])   # all int? a stray str would explain a lot
'''))
C.append(md('''
## What step 1 told us

The input is clean: four integers, `[40, 60, 90, 110]`, exactly as expected. So the bug is
**not** in the data — which means it is in the **computation**. We just spent one cheap print
to eliminate an entire category of cause. That is the ritual working: each step *rules
something out* with a fact instead of a guess.
'''))
C.append(md('''
## PREDICT
We are about to print the **intermediate** value `total` on its own, then compute the tip a
second way, step by step. Before we do: is `total` itself correct (should be 300), or is the
bug already upstream in `total`? Commit out loud.
'''))
C.append(code('''
# Ritual step 2: print the intermediate. We isolate 'total' and the tip math into named steps,
# so we can SEE which step first goes wrong instead of guessing about the one-liner above.
total = sum(prices)
print("intermediate -> total:", total)      # is this 300? (checks the first half of the math)

# now rebuild the tip slowly, naming each stage so a wrong stage cannot hide inside a one-liner
ten_percent_as_fraction = 10 / 100          # 10% means 0.10 — this is the number we MEANT
print("intermediate -> 10% as a fraction:", ten_percent_as_fraction)

tip_correct = total * ten_percent_as_fraction   # tip = total * 0.10
print("intermediate -> tip done correctly:", tip_correct)
'''))
C.append(md('''
## What step 2 told us

`total` was **300** — correct. So the bug is downstream of `total`, in the tip line. And
when we rebuilt the tip *slowly* — `total * (10/100)` — we got **30.0**, the right answer.

Now compare to the buggy line: `total / 10 / 100`. Dividing by 10 and then by 100 is dividing
by 1000, giving `300/1000 = 0.3`. The bug was a **wrong operation**: division where it should
have been multiplication by a fraction. The intermediate print pinned it to one line. No
guessing happened — we *watched* the value go wrong.
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
The buggy line was `tip = total / 10 / 100`. In one sentence: what was the actual mistake,
and which ritual step (input vs intermediate) is the one that *located* it? Why could step 1
never have caught this bug?
'''))
C.append(md('''
## Ritual step 3 — shrink the example

Sometimes the input is big and the intermediate is tangled and you still cannot see it. The
third move: **shrink**. Cut the data to the *smallest* case where the bug still shows. A bug
on one number is far easier to read than a bug on four. Shrinking does not fix anything — it
*removes hiding places*.

We will shrink the tip bug to a single price where the right answer is a number you know cold.
'''))
C.append(md('''
## PREDICT
Shrink the prices to just `[100]`. A correct 10% tip on 100 is a number you know in your
sleep. What is it? And what will the BUGGY formula `total / 10 / 100` print instead?
'''))
C.append(code('''
# Step 3: shrink to the smallest case with a known answer. On [100], a correct 10% tip is 10 —
# so any formula that does NOT print 10 is visibly, undeniably wrong. Small data, nowhere to hide.
tiny_prices = [100]
tiny_total = sum(tiny_prices)

buggy_tip = tiny_total / 10 / 100     # the original bug, now on data where the right answer is obvious
right_tip = tiny_total * (10 / 100)   # the corrected version, for side-by-side contrast

print("on [100]: correct 10% tip is 10")
print("buggy formula prints:", buggy_tip, "  <- not 10, so it is wrong, no debate")
print("fixed formula prints:", right_tip, "  <- 10, correct")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not memory): why is a bug on `[100]` easier to
catch than the same bug on `[40, 60, 90, 110]`? (If your answer mentions "I already know the
right answer for 100," you have it — shrinking buys you a *known-correct target*.)
'''))
C.append(md('''
## Manual-before-function: the fix, then the safe wrapper

We found the bug by hand. Now we write the fix as a tiny named function — but only AFTER
doing it by hand, so the function is a convenience, not a mystery. And we make the function
*defend itself*: it checks its own input, because a function that trusts bad input just moves
the silent-wrongness bug somewhere harder to find.
'''))
C.append(code('''
# The corrected tip, wrapped — written only AFTER we computed it by hand above.
def tip_for(prices, rate=0.10):
    # we re-print the input INSIDE the function the first time we trust it, because step 1 of
    # the ritual ("print the input") applies to functions too — a function is just a cell you reuse
    if not prices:
        # an empty bill has no defined tip; returning 0 silently would be exactly the kind of
        # plausible-but-wrong number this whole book is about, so we refuse instead
        raise ValueError("no prices given — cannot tip on an empty bill")
    total = sum(prices)
    return total * rate     # multiply by the fraction — the operation we proved correct by hand

print("tip on [40,60,90,110]:", tip_for([40, 60, 90, 110]))   # expect 30.0
print("tip on [100]:", tip_for([100]))                         # expect 10.0
'''))
C.append(code('''
# YOUR TURN - confirm the fix against YOUR original prediction from the top of Act 2.
# my expected tip on [40,60,90,110] was: <fill this comment in with your number>
result = tip_for([40, 60, 90, 110])

# Why this drill: closing the loop on your own prediction is the EXPLAIN step — it turns
# "the cell ran" into "I predicted 30 and got 30, and I know why the old 0.3 was wrong."
print("fixed tip:", result, "| matches the correct answer 30.0 ->", result == 30.0)
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
Recite the three steps of the debug ritual in order. For the tip bug: which step *eliminated
the input as the cause*, and which step *pinned the bug to one line*? What is the single rule
that wraps all three steps?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a wrong number sends you guessing at formulas. After Act 2 you own the ritual as
muscle memory: **print the input** (rules out bad data), **print the intermediate** (pins the
bug to a line), **shrink the example** (removes hiding places) — and the rule over all three,
**do not guess**. You also saw the dangerous kind of bug: one that prints a believable number
and never crashes. That kind is Act 3's whole subject.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2. Write YOUR one-sentence version of the ritual. Not mine - yours.
ritual_in_my_words = ""   # one sentence covering input / intermediate / shrink

if len(ritual_in_my_words.strip()) < 20:
    print("write your one-sentence ritual above (20+ chars), then re-run.")
else:
    print("ACT 2 LOGGED:", ritual_in_my_words)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: tracebacks, break-its, and the silent-wrongness trap

## Two kinds of failure (and which one should scare you)

A bug fails in one of two ways:
- **Loud:** the cell **crashes** and prints a traceback. Python stops and tells you where.
- **Silent:** the cell **runs green** and prints a wrong number. Nothing tells you anything.

Beginners fear the loud one (red is scary). But the loud failure is the *friendly* one — it
hands you a location for free. The silent one is the demo-killer. This act trains you to read
the loud failure fast, then spends its second half on the silent one.
'''))
C.append(md('''
## Reading a traceback — the bottom-up ritual

When a cell crashes, Python prints a **traceback**: a wall of red. The reading order is
*counter-intuitive*, so it is a ritual you memorize:
1. **Read the LAST line first.** It names *what* went wrong (the error type + message).
2. **Then walk UPWARD** to find *where* — the arrow / line number points at the guilty line.

The middle is the call chain (how Python got there); you usually only need the bottom (what)
and the line nearest your code (where). Let's make one crash on purpose and read it this way.
'''))
C.append(md('''
## PREDICT
The next cell adds up a list of prices, but one entry is the **string** `"90"` (text), not the
number `90` — a typo a real data source absolutely will make someday. When `sum()` hits it:
does Python **crash loudly** with a traceback, or **produce a silently wrong number**? Commit
to one before running.
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. Read the traceback, do not fix it yet.
# EXPECTED FAILURE FOR LEARNING
prices_with_typo = [40, 60, "90", 110]   # <- the damage: a string "90" where a number belongs

# sum() starts at 0 (an int) and tries 0 + 40 + 60 + "90" — adding an int and a str is undefined,
# so Python REFUSES rather than guessing. Watch it crash, and read the LAST line of red first.
total = sum(prices_with_typo)
print("total:", total)
'''))
C.append(md('''
## Read it bottom-up (do this now)

The last line of that traceback says something like:
`TypeError: unsupported operand type(s) for +: 'int' and 'str'`
— that is the **what**: "you asked me to add a number and text." Now walk up: the arrow points
at the `sum(prices_with_typo)` line — the **where**.

Notice what the traceback did NOT make you do: guess. It *told* you the what and the where.
This is why a crash is the friendly failure — it is the ritual's step 1 and 2 done for you,
for free. The fix is to repair the input (turn `"90"` back into `90`), not the formula.
'''))
C.append(code('''
# The recovery cell: fix the DATA, not the formula. (Crash cells in this course are always
# followed immediately by a fix, so a fresh run ends in a clean state.)
prices_fixed = [40, 60, int("90"), 110]   # int("90") converts the text "90" back to the number 90
print("repaired input:", prices_fixed)
print("total now:", sum(prices_fixed))    # 300 — the crash is gone because the INPUT is clean
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
Recite the bottom-up traceback ritual (which line first, which direction next). For the crash
above: what was the *what*, what was the *where*, and why is "fix the data" the right move
instead of "fix the formula"?
'''))
C.append(md('''
## YOUR break now

Author your own crash. Pick ONE change to `prices` that will make a computation throw a
traceback — for example put a string where a number goes, or divide by something that becomes
zero. Predict the *exact* error type first (TypeError? ZeroDivisionError?), write it as a
comment, then break it and read the last line of red to check yourself.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it. (This cell is allowed to crash for learning.)
# EXPECTED FAILURE FOR LEARNING
# my prediction: <write the EXACT error type you expect and why, BEFORE running>

my_prices = [40, 60, 90, 110]

# 1) damage one thing here so a later line will crash. Examples (uncomment & edit ONE):
# my_prices[2] = "ninety"          # a non-numeric string -> ?
# divisor = 0                      # then divide by it below -> ?

# 2) run a computation over it and compare reality to your written prediction:
print("total:", sum(my_prices))                 # crashes if you put a string in my_prices
# print("avg per item:", sum(my_prices) / divisor)   # uncomment if you set divisor = 0
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this book is built on

**The wrong belief:** "the cell ran with no error, so the number is right."

The next cell computes an *average response time* for a voice agent, the way a beginner
would. It runs perfectly. No red. Clean output. And the number it prints is a **lie** — it
says the agent is fine when one response was catastrophic. Run it, then try to explain why
the printed average is misleading BEFORE reading the reveal.
'''))
C.append(code('''
# Response gaps (ms) between a caller finishing and the agent replying, across one call.
# Most are snappy; ONE is a disastrous 20-second silence (the kind that loses a real caller).
response_gaps_ms = [180, 220, 200, 260, 240, 20000]   # five fine replies + one 20,000ms freeze

# The beginner's "how's the agent doing?" number: the mean. It runs green and looks official.
mean_gap = sum(response_gaps_ms) / len(response_gaps_ms)
print("mean response gap (ms):", round(mean_gap, 1))
print("does that look like a healthy agent? (it ran with no error...)")
'''))
C.append(md('''
## The reveal

The mean is about **3,517 ms** — which describes *no real response in the call*. Five replies
were ~220 ms and one was 20,000 ms; the single freeze dragged the average up by thousands.
A reader who trusts the mean concludes "average ~3.5s, a bit slow but okay" and **misses a
20-second catastrophe entirely**.

The cell ran green. It printed a number. The number lies. **Green proves execution, never
correctness.** This is the trap at the heart of the whole curriculum: a judge can return
perfectly-formatted JSON and be wrong; a chart can render and imply more than it licenses;
a metric can compute and hide the one event that matters. The cure is the same everywhere —
print the input (look at the *raw* gaps, see the 20000), and never trust a number you have
not interrogated.
'''))
C.append(md('''
## PREDICT
We will now look at the **raw gaps** (step 1 of the ritual) and compute the **median** instead
of the mean. The median is the middle value when sorted. With one giant outlier in the data,
will the median be near the snappy replies (~220) or near the 20,000 freeze? Commit out loud.
'''))
C.append(code('''
# Apply the ritual to the trap: step 1, print the INPUT (the raw gaps) so the outlier is visible
# instead of hidden inside an average. The 20000 is sitting right there once you actually look.
print("raw gaps (ms):", sorted(response_gaps_ms))   # sorting makes the lone 20000 jump out at the end

# the median (middle value) ignores how FAR the outlier is — it just steps to the center,
# so one freeze cannot drag it the way it dragged the mean. This is the P00 mean-vs-median trap,
# now with teeth: out there it is the rule "report p50/p90, never the mean."
import statistics                                    # python's built-in stats; imported where first needed
print("median gap (ms):", statistics.median(response_gaps_ms))
print("worst gap (max, ms):", max(response_gaps_ms))   # and ALWAYS look at the worst case directly
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
trap_in_my_words = ""   # one sentence: why did the green cell lie, and what one LOOK exposes it?

if len(trap_in_my_words.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP EXPLAINED:", trap_in_my_words)
'''))
C.append(md('''
## Asking AI for help, well (you live in Cursor — workflow, not philosophy)

**Lazy ask (produces a lecture):** "why is my tip wrong?"

**Strong ask (produces a correction to your model):**
> "Here is the cell: `tip = total / 10 / 100`. I predicted tip = 30 for total = 300, but it
> printed 0.3. I already printed the input — prices are four clean ints summing to 300, so the
> data is fine. The bug is in the tip line. **What operation did I actually write vs. what I
> meant?**"

The template: *what I predicted · what happened · the ritual steps I already ran · the precise
question*. You bring the looking; the AI brings the correction. Hand it a vague "fix this" and
it guesses for you — which is the exact habit this book is trying to kill.
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: red was scary and green felt like success. After Act 3: a **traceback** is read
bottom-up and is the *friendly* failure (it hands you what + where), a self-authored break
maps an edge, and **silent wrongness** — the green cell that lies — scares you more than any
crash. The ritual beats both: loud bugs by reading the trace, silent bugs by printing the
raw input until the lie has nowhere to hide.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the silent-wrongness trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this ritual lives in VoiceForge

## The real pipeline runs the same ritual

This is not a toy skill. VoiceForge's deterministic timing core, `pipeline/signals.py`,
computes things like **FTO** (floor transfer offset = `next.start_ms − prev.end_ms`) for
every pair of turns in a call. When one of those numbers looks wrong, the engineer debugging
it runs *this exact ritual*: print the input (the raw turns), print the intermediate (the
per-pair FTO), shrink the example (one suspicious pair of turns).

The real hero call — `data/hero/turns.json`, 12 turns of a Telugu-English appliance booking —
has two timing failures baked in. We will debug one by hand, with the ritual, on real ms.
'''))
C.append(md('''
## PREDICT
In the real hero call, the agent **interrupts the caller** (a barge-in) early on. Here are the
two turns involved, with real millisecond timestamps:

- turn t2 (user) ends at `end_ms = 18949`
- turn t3 (agent) starts at `start_ms = 18149`

FTO = `next.start_ms − prev.end_ms`. Compute it in your head: is it **negative** (the agent
started before the user finished = overlap = barge-in) or **positive** (a gap)? By how many ms?
'''))
C.append(code('''
# Ritual step 1 on REAL data: print the input — the two real turns, exactly as they live in
# data/hero/turns.json. Seeing the raw ms first is the course rule (raw before transformed).
prev_turn = {"turn_id": "t2", "speaker": "user",  "end_ms": 18949}    # caller's turn, when it ENDS
next_turn = {"turn_id": "t3", "speaker": "agent", "start_ms": 18149}  # agent's turn, when it STARTS
print("prev (user) end_ms:", prev_turn["end_ms"])
print("next (agent) start_ms:", next_turn["start_ms"])
'''))
C.append(code('''
# Ritual step 2: print the intermediate — the FTO itself, computed the way signals.py does it.
# fto = next.start_ms - prev.end_ms  (negative = overlap/barge-in, positive = gap)
fto_ms = next_turn["start_ms"] - prev_turn["end_ms"]
print("intermediate -> fto_ms:", fto_ms)

# a negative fto means the agent's turn STARTED before the user's turn ENDED — they overlapped.
# the overlap magnitude is how far negative we went; that is the barge-in size signals.py reports.
overlap_ms = max(0, -fto_ms)   # max(0, ...) because a positive fto is a gap, not an overlap
print("intermediate -> overlap_ms:", overlap_ms, "(this is the barge-in: agent cut the caller off)")
'''))
C.append(md('''
## What the ritual just showed on real data

`fto_ms = 18149 − 18949 = −800`. Negative, so the agent's turn *started 800 ms before the
caller finished* — a real **barge-in** (overlap > 100 ms). This is exactly the
`agent_interrupts_user` failure `pipeline/signals.py` flags, and it is the headline failure
of the hero call. You just reproduced a production signal with two prints and a subtraction —
input, intermediate — no guessing.

The hero call has a second one: a **1,620 ms gap** later (t6 ends 52253, t7 starts 53873 →
`53873 − 52253 = +1620`, a positive FTO = laggy response). Same ritual, opposite sign.
'''))
C.append(md('''
## PREDICT
The second hero-call failure is a **gap**: t6 (user) ends at `52253`, t7 (agent) starts at
`53873`. Using `fto = next.start_ms − prev.end_ms`, predict the sign and size. Will it be
**positive** (a gap, the agent was slow to reply) or **negative** (an overlap)? Roughly how
many ms — and is that over the 800 ms "laggy" line? Commit before the next cell confirms it.
'''))
C.append(code('''
# Confirm your prediction on the SECOND real failure: the laggy-response gap (t6 -> t7).
# Same formula as signals.py; a POSITIVE fto here means the agent left the caller waiting.
t6_end, t7_start = 52253, 53873           # real ms straight from data/hero/turns.json
gap_fto = t7_start - t6_end               # positive = gap (silence), negative would be overlap
print("fto_ms (t6->t7):", gap_fto)        # expect +1620
print("is it laggy? (> 800 ms):", gap_fto > 800)   # the rubric's laggy line; 1620 clears it easily
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, on real data)
You just reproduced two production signals by hand. Recite the FTO formula. For the barge-in
(t2→t3) the FTO was −800 and for the gap (t6→t7) it was +1620 — say what the *sign* means in
each case (who started early vs. who was slow), and which ritual steps you used to get there
without guessing.
'''))
C.append(md('''
## The silent-wrongness trap, but in production

Remember Act 3's trap — the mean hiding a 20-second freeze? That is not a toy worry here.
The hero caller is mid-sentence giving their address when the agent barges in. If you reported
only the agent's *average* response time across the call, it would look fine — the barge-in is
a single event, and the mean would smooth it away. The failure that would lose this real
caller is **invisible to the summary number** and **visible the instant you print the raw
turns**. That is why VoiceForge reports p50/p90 and an explicit failure table, never a lone
mean — and why the ritual's "print the input" is a production habit, not a beginner crutch.
'''))
C.append(md('''
## The same concept at three levels

- **To a beginner:** "when a number looks wrong, don't guess — print what went in, print the
  middle value, and shrink it down until the mistake is obvious."
- **To an engineer:** "bisect the computation with prints: verify the input invariants, dump
  the intermediate at the suspected fault line, and minimize the repro. Distrust green cells —
  silent wrongness (e.g. mean-masked outliers) fails no test but ships the bug."
- **To a founder:** "our numbers are debuggable and defensible — when a metric surprises us we
  can trace it to the exact turn in the exact call, so nothing on the demo stage is a number
  we can't stand behind."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "An eval number looks wrong on stage. What do you actually do?"**
<details><summary>answer</summary>The debug ritual: print the input (the raw turns/scores), print the intermediate (the per-turn FTO or per-dimension score), shrink to the one call or one turn that misbehaves. I locate the bug to a line; I don't guess and I don't hand-wave.</details>

**2. "Why don't you just trust a cell that ran without errors?"**
<details><summary>answer</summary>Because green proves execution, not correctness. A mean can run clean and hide a 20-second freeze; a judge can return valid JSON and be wrong. Running was never the bar — interrogating the raw input is.</details>

**3. "What's the very first thing you rule out when a notebook number is wrong?"**
<details><summary>answer</summary>Stale state. The kernel's memory, not the page, is the truth — so I restart and run top-to-bottom to rule out an out-of-order or double-run value before I suspect my code.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: the ritual you drilled on toy tips is the *same* move engineers run on
`pipeline/signals.py` over real call timing; that the hero call's barge-in is just
`fto = next.start − prev.end` going negative; that silent wrongness is a production threat,
not a toy one; and that you can explain all of this at beginner, engineer, and founder levels.
P03 handed you surprising plots; this book taught you to interrogate them. Next, book 00
opens the real VoiceForge, where you will do this for real.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The three steps of the debug ritual, in order, and the one rule that wraps them
2. How to read a traceback (which line first, which direction next)
3. Why a crash is *friendlier* than a clean wrong number
4. What **silent wrongness** is, and the one LOOK that exposes it
5. The hero-call barge-in as an FTO: `fto = next.start_ms − prev.end_ms`, and why −800 means
   the agent interrupted

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (the ritual in production)
my_clean_sentence = ""      # the sentence you'd say in a room about how you debug now

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"When output surprises me, I print the input, print the intermediate, and shrink the
> example — I do not guess."**

If yours captures that in your own words, this book did its job.
'''))
C.append(md('''
## Next on the ladder

**P04 done** (pending your teach-back) → you have finished the P-series (P00 method → P01
objects → P02 tables → P03 plots → P04 debugging). Next is **book 00 · Start here** — the
real VoiceForge pipeline opens, and every wrong number you meet there, you debug with the
ritual you just built: print the input, print the intermediate, shrink the example.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "P04_debugging_confusion.ipynb"   # <- this notebook's filename
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
out = HERE / "P04_debugging_confusion.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
