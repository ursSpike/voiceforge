#!/usr/bin/env python3
# Builds P00_how_to_learn.ipynb per the approved outline + amendments (docs/notebook-contract.md).
# Rerun: .venv/bin/python notebooks/build_P00.py
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
# P00 · How to learn with these notebooks

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Run the seven-step loop on any cell: **predict → run → inspect → explain → change → observe → defend**
2. State the **pass condition** for every notebook in this course (hint: it is not "cells ran")
3. Recite the **debug ritual** (3 steps) and the **chart-reading ritual** (4 questions)
4. Use the **state rules** of notebooks so stale variables never lie to you

This book is deliberately trivial in topic (lists, coffee orders). The topic is not the point.
The *method* is the point — you will reuse it in all 35 books after this one.
'''))
C.append(md('''
## 2 — Knowledge map

`(nothing) → THE LEARNING RITUAL → P01 (call-log objects)`

Why this book exists: the difference between studying and cell-running is a ritual.
Without it, you will run every cell in this course, feel productive, and own nothing.
With it, every cell becomes a small experiment you predicted, observed, and can defend.
'''))
C.append(md('''
## 3 — Baby intuition

A video lecture lets you nod along. A notebook is gym equipment: the machine does
**nothing** until you push against it. If you only press run-run-run, you are walking
past the machines while wearing gym clothes.

The push has names. Before a cell: **predict** what it will print. After it runs:
**inspect** the output, **explain** it in one sentence, out loud. Then **change** one thing,
**observe** what moved, and be ready to **defend** the why.
'''))
C.append(md('''
## 4 — The formal version

The loop, as the checklist you will run roughly ten times per notebook:

| step | what you actually do |
|---|---|
| predict | commit to an expected output BEFORE running (write it down) |
| run | execute the cell |
| inspect | look at raw inputs/outputs, not just the last line |
| explain | one sentence, out loud: "this took ___ and produced ___ because ___" |
| change | modify exactly one variable / threshold / value |
| observe | what moved? did it match your new prediction? |
| defend | answer the sharp question (the notebook will supply them) |

Four words this course uses constantly:
- **checkpoint** — a gate that asks you to say something specific before continuing
- **break-it** — a cell where we damage something on purpose to learn the edges
- **teach-back** — closing the notebook and explaining it for 2 minutes, no peeking
- **clean sentence** — the one-liner you could say in a room of engineers
'''))
C.append(md('''
## 5 — The machine you are sitting in (notebook state)

Practical bits, then the one lesson that matters:

- Kernel: pick the `.venv` interpreter (bottom/top-right in Cursor). The kernel is a single
  living Python process; **every cell shares its memory**.
- The number in brackets next to a run cell — `[3]` — is the order it was executed in,
  NOT its position on the page.
- **The lesson: cells are not the program; the kernel's memory is.** If you run cells out of
  order, or run one cell twice, the memory can hold values the page no longer shows.
  This is called **stale state**, and it is the #1 way notebooks lie to beginners.
- Fix when confused: restart the kernel (clean slate) and run top-to-bottom.

The next two cells prove the lie to you on purpose.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just what it does.

# We print a sentence so you can see where output appears (directly under the cell),
# and so your very first action in this course is a run you predicted: PREDICT - what
# exact text will appear below?
print("the machine does nothing until you push")
'''))
C.append(code('''
# We create a variable. The IMPORTANT part: x now lives in the KERNEL'S MEMORY,
# not in this cell. The cell is just the spell that put it there.
x = 10
print("x is now", x)
'''))
C.append(code('''
# PREDICT, then run this cell TWICE in a row (yes, twice - deliberately).
# Before the second run, predict x again.

# We double x. Because x lives in kernel memory, running this twice doubles it twice.
# The page looks identical both times - the MEMORY is what changed. This is stale state
# in action: the screen is not the truth; the kernel is.
x = x * 2
print("x is now", x)
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What does the `[number]` next to a run cell mean?
2. Why did running the doubling cell twice give a different answer the second time,
   even though the cell's text never changed?
3. When a notebook confuses you, what is the clean-slate move?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a notebook is a document you read and run.
After Act 1 you should know: a notebook is a **gym with shared memory** — the loop is the
workout, and the kernel's state (not the page) is the truth.

If that sentence feels obvious-in-your-own-words, continue. If not, re-run cells 7–8 and
watch the memory move.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of what a notebook is to you now. Not mine - yours.
# Producing the sentence is the learning; reading mine would just feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: the loop, drilled on trivial data

## Meet PREDICT

A *wrong* prediction is the most valuable thing this course can produce. It marks the exact
spot where your mental model and reality disagree — which is the only spot where learning
can happen. A right prediction just confirms what you had. So: predicting is not a quiz,
it is a metal detector for gaps. You must commit BEFORE running; a guess made after seeing
the answer is worthless theater.
'''))
C.append(md('''
## PREDICT
A list of coffee prices: `[40, 60, 90]` (rupees).
The next cells compute the **total** and the **average**.
Commit to both numbers now — you will write them down in the next cell.
'''))
C.append(code('''
# YOUR TURN - predictions are written BEFORE the computing cells run.
# We store them as variables so the notebook becomes a record of YOUR thinking,
# and a later cell can compare your guess against reality. That comparison is the lesson.
my_total_prediction = None     # <- replace None with your number
my_average_prediction = None   # <- replace None with your number

if my_total_prediction is None or my_average_prediction is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("predictions locked:", my_total_prediction, "and", my_average_prediction)
'''))
C.append(code('''
prices = [40, 60, 90]

# sum() walks the list and adds every element - we use it instead of writing 40+60+90
# so the line stays TRUE even when the list changes later (and it will: that is the
# 'change one thing' step coming up).
total = sum(prices)
print("total:", total)
'''))
C.append(code('''
# We divide by len(prices), never by a hardcoded 3, for the same reason as above:
# code that encodes an assumption (3 items) breaks silently the moment the assumption dies.
average = total / len(prices)
print("average:", average)

# The comparison against YOUR committed prediction - this is the metal detector reading.
if my_total_prediction is not None:
    verdict = "matched" if (my_total_prediction == total and my_average_prediction == average) else "DIFFERED"
    print("your prediction", verdict, "- if it differed, that gap is exactly what to think about")
'''))
C.append(md('''
## The EXPLAIN gate

After every important output, one sentence, out loud, in this shape:

> "This cell took ___ and produced ___ because ___."

It feels slow. That is the point — explanation is the difference between recognizing an
output and owning it. The next cell makes you write one down (the only person you can
outsource thinking to here is future-you).
'''))
C.append(code('''
# YOUR TURN - write the explain-gate sentence for the average cell as a string.
my_explanation = ""   # e.g. "This cell took the 3 prices and produced 63.33 because ..."

if len(my_explanation.strip()) < 20:
    print("write your one-sentence explanation above (20+ chars), then re-run.")
else:
    print("EXPLAINED:", my_explanation)
'''))
C.append(md('''
## Meet INSPECT

When an output surprises you, the move is never to stare harder at the output — it is to
look at the **raw input**. Outputs are downstream; confusion almost always lives upstream.
Inspection is unglamorous: print the thing, print its length, print its type. Nothing is magic.
'''))
C.append(code('''
# Inspection is just looking. Three boring prints that dissolve most confusion:
print(prices)          # the raw object itself
print(len(prices))     # how many things it holds
print(type(prices))    # what kind of container it is
'''))
C.append(md('''
## PREDICT
We now `append(10)` — a cheap fourth coffee joins the list.
Does the **average** go UP or DOWN? Commit out loud before running.
'''))
C.append(code('''
# The CHANGE step of the loop, demonstrated: one modification, then re-observe everything.
prices.append(10)

# We recompute rather than reuse the old variables - remember Act 1: 'total' and 'average'
# in kernel memory still hold the OLD world until we overwrite them.
total = sum(prices)
average = total / len(prices)
print("prices:", prices)
print("new total:", total, "| new average:", round(average, 2))
'''))
C.append(md('''
## OBSERVE + EXPLAIN

Did your up/down prediction hold? Say the why in one sentence (a cheap item pulls the
average toward itself).

The principle you just used is the **change-one-thing rule**: real understanding is knowing
*which knob moved the output*. If you change three things at once, the result teaches you
nothing about any of them. This rule returns in every book — and much later it becomes a
deep idea about training data (book 17, the single-axis rule).
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
Explain what a **wrong** prediction gives you that a **right** prediction cannot.
(If your answer mentions "finding where my mental model is wrong," you have it.)
'''))
C.append(md('''
## Manual-before-function

New rule of the whole course: before we use any library function for an idea, we compute
the idea BY HAND on data small enough to see. Functions are wrappers around ideas;
if you meet the wrapper first, the idea stays hidden inside it forever.

We will do this now for the **median** — the middle value when everything is sorted.
'''))
C.append(md('''
## PREDICT
1. The median of `[40, 60, 90]` is …?
2. The median of `[40, 60, 90, 1000]` is …? (four values — what does "middle" even mean now?)
'''))
C.append(code('''
# Manual median, every intermediate value printed - nothing hidden.
values = [90, 40, 60]                 # deliberately unsorted, because real data never arrives sorted

step1 = sorted(values)                # medians only make sense on ordered data,
print("sorted:", step1)               # so sorting is not cosmetic - it IS the precondition

middle_index = len(step1) // 2        # integer division finds the middle position (index 1 of 0,1,2)
print("middle index:", middle_index)

median_by_hand = step1[middle_index]
print("median by hand:", median_by_hand)

# Four values: there is no single middle - the convention is the average of the two middle ones.
values4 = [40, 60, 90, 1000]
s4 = sorted(values4)
median4 = (s4[1] + s4[2]) / 2         # positions 1 and 2 are the two middles of 0,1,2,3
print("median of", values4, "is", median4)
'''))
C.append(code('''
# Now - and only now - the library wrapper. It does exactly what you just did by hand.
import statistics   # python's built-in stats module; we import it here, where it is first needed

print("library median (3 values):", statistics.median([90, 40, 60]))
print("library median (4 values):", statistics.median([40, 60, 90, 1000]))
'''))
C.append(md('''
## WRONG-INTUITION TRAP 1

**The wrong belief:** "the average tells me the typical value."

Look at what just happened: `[40, 60, 90, 1000]` has an average of **297.5** — a number that
describes *no coffee that exists*. The 1000 dragged it. The median said **75**, which is what
a typical item actually costs. One rare extreme value owns the mean; the median ignores it.

Hold this trap — it returns with real force in book 04, where one terrible 20-second silence
can make an agent's *average* response time look fine. (Out there this idea is called
"report p50/p90, not mean" — you will derive it yourself there.)
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not from memory): when do mean and median
disagree, and which one follows the extreme value?
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
What are the two reasons this course computes everything manually before using the
library function? (One is about ideas hiding inside wrappers; one is about trust.)
'''))
C.append(md('''
## How to read a small table

Tables are how call data will arrive from book 01 onward. The reading ritual, three moves:
1. Say the **row count** ("three rows")
2. Say what **one row IS** ("one row = one coffee order")
3. Read **one single cell** aloud ("Asha paid 180")

Never read a table as a wall. Always: rows are *things*, columns are *facts about things*.
'''))
C.append(code('''
# Tiny raw data: three coffee orders as a list of dictionaries.
# We print the RAW object before doing anything to it - seeing the ugly input first is a
# course rule (transformed outputs make more sense when you saw what went in).
orders = [
    {"name": "Asha", "items": 2, "paid": 180},
    {"name": "Sam",  "items": 3, "paid": 260},
    {"name": "Lee",  "items": 1, "paid": 90},
]
for order in orders:        # one print per row, so each ROW is visibly one THING
    print(order)
'''))
C.append(md('''
## PREDICT
Which order was the most expensive in total? Point at it. (Easy on purpose — the habit is
the workout, not the difficulty.)
'''))
C.append(code('''
# We find the most expensive order with a plain loop - no library shortcut yet,
# because P02 will earn that shortcut AFTER you can do this by hand.
most_expensive = None
for order in orders:
    # 'most_expensive is None' handles the very first row - there is nothing to compare to yet.
    if most_expensive is None or order["paid"] > most_expensive["paid"]:
        most_expensive = order
print("most expensive order:", most_expensive)
'''))
C.append(md('''
## EXPLAIN gate
One sentence on what the loop did. And a promise kept honest: in P02, pandas will do this
in one line — *after* today's by-hand version, that line will be a convenience, not a mystery.
'''))
C.append(md('''
## How to read ANY chart — the 4-question ritual

Every chart in this course (and every chart you will ever defend on a stage) answers to:
1. **What is x?** 2. **What is y?** 3. **What is one mark** (one bar/dot/line)?
4. **What claim does this chart actually allow?**

Question 4 is the dangerous one. Charts *imply* more than they *license* — reading a chart
means knowing what it does NOT say. You will practice exactly that in a moment.
'''))
C.append(md('''
## PREDICT
A bar chart of the three order totals: whose bar is tallest, and roughly how many times
taller than the shortest?
'''))
C.append(code('''
# Our first chart. Every line says why it exists.
import matplotlib.pyplot as plt   # the standard plotting library; imported where first used

names = [o["name"] for o in orders]    # x-axis: one label per order (the THINGS)
paids = [o["paid"] for o in orders]    # y-axis: the fact we are comparing (the MEASURE)

fig, ax = plt.subplots(figsize=(5, 3)) # fig = the canvas, ax = the drawing area on it
ax.bar(names, paids)                   # one bar per order; bar height = rupees paid
ax.set_xlabel("order (person)")        # unlabeled axes are how charts lie by omission,
ax.set_ylabel("total paid (rupees)")   # so labeling is a duty, not decoration
ax.set_title("coffee order totals")
plt.show()
'''))
C.append(code('''
# YOUR TURN - question 4 of the ritual: what claim does THIS chart license?
claim_a = "Sam spends the most PER ITEM"
claim_b = "Sam's order TOTAL is the largest"

chart_allows = ""   # <- type "a" or "b"

# Why this drill exists: the bars show TOTALS. Per-item spending needs paid/items,
# which this chart never plotted. A chart can only license claims about what is on its axes.
if chart_allows == "b":
    print("correct. totals are on the y-axis, so only the TOTAL claim is licensed.")
    print("check the per-item truth:", [(o["name"], round(o["paid"] / o["items"], 1)) for o in orders])
    print("Sam is actually the CHEAPEST per item - the chart never knew that.")
elif chart_allows == "a":
    print("look again: where would per-item spending appear on this chart? it never does.")
    print("the y-axis is totals - claims beyond the axes are not licensed. try 'b'.")
else:
    print("type 'a' or 'b' above and re-run.")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
Recite the four chart-reading questions from memory, and answer all four for the chart above.
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: running code = progress. After Act 2 you should own four habits: predictions are
**committed before running** (and wrong ones are the prize), explanations are **produced not
consumed**, every computation is **manual before library**, and tables/charts are read by
**ritual** — including what a chart does *not* license.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (the loop / manual-first / chart ritual - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break it, debug it, and the trap at the heart of this course

## Break-it philosophy

You do not understand a system until you know its edges, and edges only show themselves
when something hits them. So we now damage things ON PURPOSE and watch how they fail.
Surprise on your own terms is education; surprise on the demo stage is a disaster.
'''))
C.append(md('''
## PREDICT
We change Lee's `paid` from the number `90` to the **string** `"yes"` (a typo a real data
source absolutely will make someday). When the totals loop runs over this: does Python
**crash loudly**, or **produce a silently wrong number**? Commit to one.
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. Read what happens, do not fix it yet.

broken_orders = [
    {"name": "Asha", "items": 2, "paid": 180},
    {"name": "Sam",  "items": 3, "paid": 260},
    {"name": "Lee",  "items": 1, "paid": "yes"},   # <- the damage: a string where a number lives
]

# Summing numbers with a string forces Python to add 440 + "yes" - watch it refuse.
total_paid = sum(o["paid"] for o in broken_orders)
print("total paid:", total_paid)
'''))
C.append(md('''
## Reading the error (bottom-up, always)

The wall of red is called a **traceback**. The ritual: read the **last line first** — it names
*what* went wrong (`TypeError: unsupported operand type(s) for +: 'int' and 'str'` — "you
made me add a number and text"). Then walk **upward** to find *where* (the arrow points at
the summing line).

One more thing, and it matters: a crash is the **friendly** failure. Python stopped and told
you. If Lee's paid had been the string `"90"` in a different operation, you might have gotten
a wrong number with **no error at all** — silent wrongness. Crashes cost minutes; silent
wrongness costs demos. (Act 3's second half is entirely about that.)
'''))
C.append(md('''
## The debug ritual (three steps, in order)

When output confuses you:
1. **Print the input** — the raw object, before any transformation
2. **Print the intermediate** — the value halfway through the computation
3. **Shrink the example** — cut the data down until the bug has nowhere to hide

That's the whole ritual. P04 trains it hard; here is the mini version on our break:
'''))
C.append(code('''
# Step 1 of the ritual: print the input. The bug is visible before any clever debugging.
for o in broken_orders:
    # printing the VALUE and its TYPE side by side - type mismatches hide in plain sight
    print(o["name"], "| paid =", repr(o["paid"]), "| type =", type(o["paid"]).__name__)

# The print exposed it: Lee's paid is a str. Fix the data, not the formula:
broken_orders[2]["paid"] = 90
total_paid = sum(o["paid"] for o in broken_orders)
print("fixed total:", total_paid)
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
Recite the three-step debug ritual. Which step caught our bug — and why is a loud crash
*friendlier* than a silent wrong number?
'''))
C.append(md('''
## YOUR break now

Author your own damage. Pick ONE field in the orders data (a name, an items count, a paid
value), predict exactly what will happen to the totals loop (crash? which error? silent
wrongness? which number?), write the prediction as a comment, then break it and run.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it.
# my prediction: <write here exactly what will happen and why>

my_orders = [
    {"name": "Asha", "items": 2, "paid": 180},
    {"name": "Sam",  "items": 3, "paid": 260},
    {"name": "Lee",  "items": 1, "paid": 90},
]

# 1) damage one field here:
# my_orders[?][?] = ?

# 2) then run the computation and compare reality against your written prediction:
print("total:", sum(o["paid"] for o in my_orders))
print("most items:", max(my_orders, key=lambda o: o["items"])["name"])
'''))
C.append(md('''
## WRONG-INTUITION TRAP 2 — the one this whole course is built on

**The wrong belief:** "all my cells ran green, so I learned it / so the result is right."

The next cell runs perfectly. No errors. Clean output. And one of its two numbers is a lie
waiting to happen. Run it, then try to explain the difference between the numbers BEFORE
reading the reveal.
'''))
C.append(code('''
# Two coffee shops report their average order value.
shop_A_orders = [100, 110, 90, 105, 95, 100, 110, 90]   # 8 orders, steady prices
shop_B_orders = [400, 420]                               # 2 orders, premium prices

avg_A = sum(shop_A_orders) / len(shop_A_orders)
avg_B = sum(shop_B_orders) / len(shop_B_orders)

# "Company-wide average" - computed two different ways:
average_of_averages = (avg_A + avg_B) / 2
overall_average = sum(shop_A_orders + shop_B_orders) / len(shop_A_orders + shop_B_orders)

print("shop A average:", avg_A, "  shop B average:", avg_B)
print("average of the two averages:", average_of_averages)
print("true overall average:       ", round(overall_average, 1))
# Both lines printed. No error anywhere. The numbers disagree by a lot. Which one is 'the' average?
'''))
C.append(md('''
## The reveal

`average_of_averages` treats a 2-order shop as equal to an 8-order shop — it silently gives
each *shop* one vote instead of each *order* one vote. The true overall average weighs every
order equally. **Both cells ran. Both printed. One is the wrong tool for almost every
question you'd ask.** Green cells prove execution, never understanding — and never correctness.

This trap is the soul of the curriculum, because it scales straight into VoiceForge:
a judge can return perfectly-formatted JSON **and be wrong** (book 12 exists because of this) ·
a chart can render beautifully **and imply more than it licenses** (you caught one in Act 2) ·
an agreement number can exist **and be overclaimed** (book 14–15). The pass condition of every
book — closed-notebook teach-back — exists precisely because running was never the bar.
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why do the two 'averages' differ, and which vote does each give?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## Asking AI for help, well (you will live in Cursor — this is workflow, not philosophy)

**Lazy ask (produces a lecture):** "explain this cell"

**Strong ask (produces a correction to your model):**
> "Here is the cell: `<paste>`. I predicted the average of averages would equal 255-ish
> because both are averages of the same data. Instead I got 255 vs 173.1. Here is the raw
> input: 8 orders around 100, 2 orders around 410. **Where is my mental model wrong?**"

The template: *what I predicted · what happened instead · the raw input · where is my model
wrong*. You bring the thinking; the AI brings the correction. Reverse those roles and the
AI learns while you watch.
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: errors were scary and green cells felt like success. After Act 3: breaks are how you
map edges, tracebacks read bottom-up, the debug ritual is three boring prints, silent
wrongness scares you MORE than crashes — and "it ran" earns exactly nothing.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the course, the cast, and the bar you must clear

## How every coming book uses this ritual

Each of the 35 books ahead (P01–P04, then 00–30) is built from the same four acts you just
lived: **orientation** (what/why), **mechanics** (toy data → manual → function), **stress**
(break-its + a wrong-intuition trap), **ownership** (VoiceForge connection, failure modes,
three-level explanations, defense questions, teach-back). Same checkpoints. Same learning
logs. Same predict-before-run. The ritual you ran on coffee orders will run on call logs,
judges, kappa, and DPO pairs — only the subject gets harder; the method never changes.
'''))
C.append(md('''
## Your QA power (and duty)

Every generated book ends with a **quality self-audit** that counts its own structure:
checkpoints, break-its, traps, learner-owned cells, comment coverage. If a book's audit
fails the contract minimums — or it *passes the counts* but you catch it assuming knowledge
it never taught — **you reject the book and it gets rebuilt.** You are not a student of this
course; you are its quality gate. (This notebook's own audit is two cells from the end.)
'''))
C.append(md('''
## The full ladder (you are here)

`P00 ✦ → P01 objects → P02 tables → P03 plots → P04 debugging`
`→ 00–09 survival (what VoiceForge is, call logs, schemas, timing, task success, cost…)`
`→ 10–19 measurement (judges, evidence, calibration, kappa, honesty)`
`→ 20–30 system & defense (A/B, rubrics, adapters, the demo, the room)`

Every book opens by placing itself on this map: previous concept → current → next.
No lesson floats in the void.
'''))
C.append(md('''
## Meet the recurring cast (trailer only — no analysis today)

Three calls travel through this entire course with you. You will meet them as Python objects
in P01, time their turns in 04, score their tasks in 06, tag their failures in 07, judge them
in 10, and mine training pairs from them in 17. Today you only shake hands.
'''))
C.append(code('''
# The cast, as trailer cards. P01 turns these into real structured objects - today we just look.
cast = [
    {"id": "call_A", "language": "English",         "story": "clean booking, cooperative caller",          "outcome": "success"},
    {"id": "call_B", "language": "Hinglish",        "story": "appointment with hesitations and a repeat",  "outcome": "partial"},
    {"id": "call_C", "language": "Telugu-English",  "story": "service call; agent interrupts mid-answer",  "outcome": "failure"},
]
for c in cast:
    print(f"{c['id']} | {c['language']:<15} | {c['story']:<45} | {c['outcome']}")
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell, no answer exists yet)

Which of the three calls do you think will be **hardest to evaluate from transcript text
alone**, and why? There is no grading today — book 04 will hand you the answer with numbers,
and your stored guess will be waiting there to be compared.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for book 04 to confront.
my_course_prediction = ""   # which call, and WHY text alone might miss what went wrong

if len(my_course_prediction.strip()) < 20:
    print("write your prediction above (which call + why), then re-run.")
else:
    print("PREDICTION STORED:", my_course_prediction)
'''))
C.append(md('''
## Where this method itself fails (honesty applies to the method too)

- **Prediction theater** — vaguely "predicting" after a peek. Countermeasure: predictions go
  in cells as variables/comments BEFORE running. (You did this five times today.)
- **Mumbled explain-gates** — thinking "yeah I get it" instead of producing a sentence.
  Countermeasure: say it ALOUD or type it; production is the test.
- **Checkpoint scrolling** — answering checkpoints by scrolling up. Countermeasure: answer
  first, scroll to verify after.
- **Teach-back skipping** — the strongest gate is the easiest to skip. Countermeasure: it is
  the pass condition; skipping it = the book is not passed, whatever the green cells say.
'''))
C.append(md('''
## The method at three levels (every book ends with one of these for its own concept)

- **To a beginner:** "guess first, then check — being wrong is how you find what to learn."
- **To an engineer:** "active recall plus hypothesis-per-cell plus deliberate perturbation;
  pass condition is closed-book reconstruction, not execution."
- **To a founder:** "training that produces explainable knowledge instead of run logs —
  the person can defend every number they show you."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "How do you know you understood something and didn't just run it?"**
<details><summary>answer</summary>Because the pass bar is reconstruction: closed notebook, two minutes, what/why/how/where-it-fails. Running can't fake that.</details>

**2. "Why predict before running — isn't that slower?"**
<details><summary>answer</summary>Slower per cell, faster per concept: a wrong prediction pinpoints the exact gap in my model, which is the only thing worth spending time on.</details>

**3. "What's your move when an output surprises you?"**
<details><summary>answer</summary>The debug ritual: print the raw input, print the intermediate value, shrink the example until the surprise has nowhere to hide. Then update the model, not the story.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: how every future book is shaped, that you hold rejection power over
them, where you sit on the ladder, who the three recurring calls are — and above all, what
it takes to PASS a book.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The seven-step loop (name the steps)
2. The pass condition for any book in this course
3. The three-step debug ritual
4. The four chart-reading questions
5. The trap: why green cells prove nothing — and one VoiceForge place it will matter

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about how you learn now

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"I don't pass a notebook when its cells run — I pass when I can close it and explain
> what, why, how, and where it breaks."**

If yours captures that in your own words, this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - this cell counts the notebook's own structure from the .ipynb file on disk.
# Why programmatic: a checklist I merely CLAIM to satisfy is wet cement. Counts or it didn't happen.
import json
from pathlib import Path

name = "P00_how_to_learn.ipynb"
candidates = [Path.cwd() / name, Path.cwd() / "notebooks" / name] + \
             [p / "notebooks" / name for p in Path.cwd().parents]
nb_path = next(p for p in candidates if p.exists())
nb = json.loads(nb_path.read_text())

src = lambda c: c["source"] if isinstance(c["source"], str) else "".join(c["source"])
all_cells = nb["cells"]
# the audit must not count itself: its source contains every marker string it greps for
pool = [c for c in all_cells if "SELF-AUDIT" not in src(c)]
md_cells   = [c for c in pool if c["cell_type"] == "markdown"]
code_cells = [c for c in pool if c["cell_type"] == "code"]

def count(marker, group):
    return sum(1 for c in group if marker in src(c))

# a code cell 'has reasoning comments' if some comment line carries an actual sentence (4+ words)
def has_reasoning(c):
    return any(len(line.strip("# ").split()) >= 4
               for line in src(c).splitlines() if line.strip().startswith("#"))

banned = ["obviously", "as you know", "simply", "intuitively"]
banned_hits = [w for w in banned for c in pool if w in src(c).lower()]

audit = {
    "total cells (incl this audit)":   (len(all_cells),             "50-90",  50 <= len(all_cells) <= 90),
    "code cells":                      (len(code_cells),            "-",      True),
    "markdown cells":                  (len(md_cells),              "-",      True),
    # uppercase CHECKPOINT marks the 5 specific gates; the act-level ones say 'knowledge-flow checkpoint' in lowercase, so case alone separates them
    "specific checkpoints":            (count("CHECKPOINT", md_cells), ">=5", count("CHECKPOINT", md_cells) >= 5),
    "act knowledge-flow checkpoints":  (count("knowledge-flow checkpoint", md_cells), "=4", count("knowledge-flow checkpoint", md_cells) == 4),
    "predict prompts":                 (count("PREDICT", pool),     ">=8",    count("PREDICT", pool) >= 8),
    "break-it cells":                  (count("BREAK-IT", code_cells) + count("self-authored break", code_cells), ">=2", (count("BREAK-IT", code_cells) + count("self-authored break", code_cells)) >= 2),
    "wrong-intuition traps":           (count("WRONG-INTUITION TRAP", md_cells), ">=1", count("WRONG-INTUITION TRAP", md_cells) >= 1),
    "learner-owned cells (YOUR TURN)": (count("YOUR TURN", code_cells), ">=6", count("YOUR TURN", code_cells) >= 6),
    "code cells w/ reasoning comments":(sum(map(has_reasoning, code_cells)), f"={len(code_cells)}", all(map(has_reasoning, code_cells))),
    "banned phrases found":            (len(banned_hits),           "=0",     len(banned_hits) == 0),
}

print(f"{'metric':<36} {'count':>6}  {'target':>8}  verdict")
print("-" * 64)
all_pass = True
for k, (n, target, ok) in audit.items():
    all_pass &= ok
    print(f"{k:<36} {n:>6}  {target:>8}  {'PASS' if ok else 'FAIL'}")
print("-" * 64)
print("AUDIT:", "ALL PASS - book accepted pending YOUR teach-back" if all_pass else "FAIL - reject this book")
'''))
C.append(md('''
## Next on the ladder

**P00 done** (pending your teach-back) → **P01 · Python objects for call logs** — the three
cast calls become real nested structures, and you learn to walk any object you'll ever meet
in this project → P02 tables → P03 plots → P04 debugging → then VoiceForge book 00.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "P00_how_to_learn.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
