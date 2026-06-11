#!/usr/bin/env python3
# Builds P03_basic_plots_for_evals.ipynb per the BUILD_SPEC four-act contract.
# The ONE atomic concept: reading and making bar / timeline / histogram, and what a chart does NOT license.
# Knowledge flow: P02 tables -> THIS (basic plots) -> P04 debugging.
# Rerun: .venv/bin/python notebooks/build_P03.py
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
# P03 · Basic plots for evals

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Run the **4-question chart ritual** on any chart: what is x · what is y · what is one mark · what claim does it license
2. Make and read the three charts an eval lives on: a **bar** (counts), a **timeline** (turns as bars over time), a **histogram** (one distribution)
3. State out loud what a chart **does NOT license** — the claim that lives off its axes
4. Catch a **misleading chart** built from honest numbers (no lie in the data, a lie in the drawing)

The topic stays small on purpose: a handful of toy numbers and the three cast calls. The
charts are the point — not the data behind them.
'''))
C.append(md('''
## 2 — Knowledge map

`P02 (tables) → THIS (basic plots for evals) → P04 (debugging)`

Why this book exists in the ladder: in P02 you learned to read a table — rows are things,
columns are facts. A table makes you *read* every cell. A **chart compresses many rows into a
shape your eye reads in one glance** — which is a superpower and a trap in the same move.
The glance is fast, and fast is where wrong claims sneak in. P04 then debugs the pipeline that
*produces* these numbers; here you learn to look at the numbers without being fooled by them.
'''))
C.append(md('''
## 3 — Baby intuition

A table is a list of facts you read one by one. A chart is a **picture of those same facts**,
drawn so your eye can compare them without reading each one.

Three pictures cover almost every eval question:
- **bar** — "how many / how much, per category?" (one bar per category, height = the amount)
- **timeline** — "when did things happen, and did they overlap?" (one bar per event, laid along time)
- **histogram** — "what is the *shape* of one pile of numbers?" (bars = how many values land in each range)

The danger is that a picture *feels* like proof. It is not. It is an argument, and arguments
can be honest or slippery. The whole book is learning to tell which.
'''))
C.append(md('''
## 4 — The formal version

A chart **maps data onto visual position and length** so differences become distances your
eye can compare. The three we use, precisely:

| chart | x-axis | y-axis (or length) | one mark = | answers |
|---|---|---|---|---|
| bar | a category | a count or amount | one category's value | "how much per group?" |
| timeline | time (ms) | one row per event | one event's span | "when, how long, did they overlap?" |
| histogram | value *ranges* (bins) | how many values fall in the bin | one bin's count | "what shape is this distribution?" |

The fourth ritual question — **what claim does this chart license?** — is the dangerous one,
because a chart always *implies* more than its axes *support*. Reading a chart well means
naming the claim it does NOT make.
'''))
C.append(md('''
## 5 — Why this exists (for evals specifically)

You will not ship a table of 200 floor-transfer offsets to a room. You will ship **one chart**
and say one sentence about it. If that sentence claims more than the axes hold, you have
overclaimed in public — the single worst thing an evaluator can do.

So the skill is not "make a pretty plot." The skill is: **make the chart, then state the exact
claim it earns and the claim it does not.** Everything below drills that.

The next cells set up our plotting tools and print the raw toy data BEFORE any chart touches it.
'''))
C.append(code('''
# First code cell. Comments in this course say WHY a line exists, never just what it does.

# We force a non-interactive backend so this notebook renders charts the same way headless
# (the run-gate) and in your editor - a chart that only appears in one place is a trap of its own.
import matplotlib
matplotlib.use("Agg")            # Agg = draw to memory, not a popup window; deterministic everywhere
import matplotlib.pyplot as plt  # the standard plotting library; imported here where first needed
print("matplotlib ready, backend:", matplotlib.get_backend())
'''))
C.append(code('''
# Tiny RAW toy data, printed before any chart - a course rule: see the ugly input first,
# because a chart of data you never read is a shape you cannot check.
# Three coffee shops and how many orders each took today (a 'count per category' - the bar case).
shop_orders = {"Asha": 8, "Sam": 3, "Lee": 5}

# We print the dict as-is so the numbers are on the page BEFORE the bar chart compresses them.
for shop, n in shop_orders.items():   # one print per category, so each category is visibly one thing
    print(shop, "took", n, "orders")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What does a chart give you that a table does not — and what new danger comes with it?
2. Name the three chart types this book covers and the one question each answers.
3. Which of the four ritual questions is the dangerous one, and why?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a chart is how you make data look finished.
After Act 1 you should know: a chart is an **argument drawn from data** — it compresses rows
into a glance, and the glance can carry a claim the axes never earned. P02 made you *read*
rows; this book makes you *not be fooled* by their picture; P04 debugs what produces them.

If that lands in your own words, continue.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of "what is a chart, to me now".
# Producing the sentence is the learning; reading mine would only feel like it.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: this nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: the three charts, raw data first, by hand before the library

## The 4-question chart ritual (the spine of this whole book)

Before you believe ANY chart — yours or a stranger's — you answer four questions out loud:

1. **What is x?** (the horizontal axis — what varies left to right)
2. **What is y?** (the vertical axis — what the height/length measures)
3. **What is one mark?** (one bar, one dot, one strip — what single thing does it stand for)
4. **What claim does this chart license?** (and, just as important, what claim does it NOT)

We will run this ritual on every chart below. Question 4 is where overclaiming dies.
'''))
C.append(md('''
## PREDICT
We are about to draw a **bar chart** of `shop_orders` = `{"Asha": 8, "Sam": 3, "Lee": 5}`.
Commit now (you will write it in the next cell):
- Whose bar is **tallest**?
- Roughly **how many times** taller is the tallest bar than the shortest?
'''))
C.append(code('''
# YOUR TURN - PREDICT: commit BEFORE the chart cell runs, stored so the notebook records YOUR thinking.
my_tallest_shop = None     # <- replace None with a name string, e.g. "Asha"
my_height_ratio = None     # <- replace None with a number: tallest count / shortest count

if my_tallest_shop is None or my_height_ratio is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("predictions locked:", my_tallest_shop, "and ~", my_height_ratio, "x taller")
'''))
C.append(md('''
## Manual before function — what a "bar" actually is

A bar chart is not magic. Before matplotlib draws one, we lay out by hand exactly what it will
draw: a list of **labels** (x) and a matching list of **heights** (y). The chart is just those
two lists turned into rectangles. Seeing the two lists first means you can check the picture.
'''))
C.append(code('''
# By hand: split the dict into the two parallel lists a bar chart is made of.
# We keep them as explicit variables (not a one-liner inside the plot call) so the inputs to
# the chart are visible and checkable - a chart you cannot check is a chart you must trust blindly.
labels = list(shop_orders.keys())     # x-axis: one label per category (the THINGS being compared)
heights = list(shop_orders.values())  # y-axis: the matching amount for each (the MEASURE)

print("x (labels):", labels)
print("y (heights):", heights)
# Sanity: the two lists must be the same length, or a bar would have no height (or vice versa).
print("same length?", len(labels) == len(heights))
'''))
C.append(code('''
# Now - and only now - the library draws the two lists we just built.
fig, ax = plt.subplots(figsize=(5, 3))   # fig = the canvas, ax = the drawing area on it
ax.bar(labels, heights)                  # one bar per label; bar height = that category's count

# Unlabeled axes are how charts lie by omission, so labeling is a duty, not decoration:
ax.set_xlabel("shop")
ax.set_ylabel("orders today (count)")
ax.set_title("orders per shop")
plt.show()   # in headless runs this is swallowed; in your editor the chart appears here
print("drew bar chart of:", dict(zip(labels, heights)))
'''))
C.append(md('''
## Run the ritual on the bar chart (out loud)
1. **x** = shop (a category). 2. **y** = orders today (a count). 3. **one bar** = one shop's order count.
4. **License:** it licenses "Asha took more orders than Lee, who took more than Sam." It does
   **NOT** license anything about revenue, busyness-per-hour, or which shop is *better* — none
   of those are on an axis.
'''))
C.append(code('''
# OBSERVE - did your prediction hold? Compare YOUR committed guess against the drawn reality.
tallest_actual = max(shop_orders, key=shop_orders.get)         # the category with the largest height
ratio_actual = max(shop_orders.values()) / min(shop_orders.values())  # tallest / shortest, as the eye reads it

print("tallest bar (actual):", tallest_actual, "->", shop_orders[tallest_actual], "orders")
print("height ratio (actual): ~", round(ratio_actual, 2), "x")

# The comparison is the lesson: a gap between guess and reality marks where your eye misjudged.
if my_tallest_shop is not None:
    verdict = "matched" if my_tallest_shop == tallest_actual else "DIFFERED"
    print("your 'tallest' guess", verdict)
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
Recite the four chart-reading questions from memory, then answer all four for the bar chart
above. (If you can name the claim it does NOT license, you own question 4.)
'''))
C.append(md('''
## Chart 2 — a histogram (the shape of ONE pile of numbers)

A bar chart compares **categories**. A histogram is different: it takes **one list of numbers**
and shows their **shape** — how many values land in each range ("bin"). There are no categories;
the x-axis is the *values themselves*, sliced into ranges.

This is the chart that, in evals, shows you whether your latencies are mostly snappy with a few
disasters — the difference a single average would hide. We build it by hand first.
'''))
C.append(md('''
## PREDICT
Here is one pile of toy response-gap times (ms), mostly quick with a couple of slow ones:
`[120, 150, 200, 180, 220, 160, 140, 190, 900, 1500]`.
Commit: when we bucket these into ranges, will MOST values sit on the **left** (small gaps) or
the **right** (large gaps)? And will the chart be **symmetric**, or have a long tail to one side?
'''))
C.append(code('''
# YOUR TURN - PREDICT (histogram): commit and store this before we bin anything.
my_mass_side = None    # <- "left" or "right": where most values sit
my_shape = None        # <- "symmetric" or "long right tail" or "long left tail"

if my_mass_side is None or my_shape is None:
    print("fill in BOTH predictions above, then re-run.")
else:
    print("locked:", my_mass_side, "/", my_shape)
'''))
C.append(code('''
# Raw pile, printed before binning - you cannot trust a histogram of numbers you never saw.
gaps_ms = [120, 150, 200, 180, 220, 160, 140, 190, 900, 1500]
print("raw gaps (ms):", gaps_ms)
print("count:", len(gaps_ms), "| min:", min(gaps_ms), "| max:", max(gaps_ms))
'''))
C.append(code('''
# Manual histogram: a histogram is just COUNTING how many values fall in each range.
# We define ranges (bins) by hand and tally, so the picture later is something you computed,
# not something the library conjured. Edges chosen to separate "snappy-ish" from "disaster".
bin_edges = [0, 300, 600, 900, 1200, 1500, 1800]   # range boundaries in ms

# Tally by hand: for each value, find which range it belongs to and add one to that range's count.
counts = [0] * (len(bin_edges) - 1)                 # one counter per range, all start at zero
for g in gaps_ms:
    for k in range(len(bin_edges) - 1):
        # a value belongs to range k if it is >= the left edge and < the right edge
        if bin_edges[k] <= g < bin_edges[k + 1]:
            counts[k] += 1
            break

# Print the by-hand tally so the histogram's bars have known values BEFORE we draw them.
for k in range(len(counts)):
    print(f"[{bin_edges[k]:>4}-{bin_edges[k+1]:>4}) ms : {counts[k]}  {'#' * counts[k]}")
'''))
C.append(code('''
# Now the library version. plt.hist does the same counting we just did by hand, then draws it.
fig, ax = plt.subplots(figsize=(5, 3))
# We pass the SAME bin edges we tallied by hand, so the drawn chart must match our printed tally.
ax.hist(gaps_ms, bins=bin_edges)
ax.set_xlabel("response gap (ms), bucketed into ranges")  # x is value RANGES, not categories
ax.set_ylabel("how many gaps fell in the range (count)")  # y is a count, like a bar chart
ax.set_title("distribution of response gaps")
plt.show()
print("histogram drawn; bars should match the by-hand tally above")
'''))
C.append(md('''
## Run the ritual on the histogram (out loud)
1. **x** = response-gap *ranges* in ms (NOT categories — buckets of a continuous value).
2. **y** = how many gaps landed in that range (a count).
3. **one bar** = one range, height = how many values fell inside it.
4. **License:** it licenses "most gaps are under 300ms, but a couple are catastrophic (900,
   1500)." It does **NOT** license "the typical gap is ~X" unless you read it off the shape —
   and it definitely does not license a single average, which the two slow gaps would poison.
'''))
C.append(code('''
# OBSERVE - check your prediction against the shape you computed.
# "Most on the left" means most values are in the first range; a "long right tail" means a few
# lonely values sit far to the right. We read that straight off the by-hand counts.
left_mass = counts[0]                     # how many landed in the smallest range
tail_mass = sum(counts[2:])               # how many landed far out to the right (900ms+)
print("in the smallest range:", left_mass, "of", len(gaps_ms))
print("far-right tail values:", tail_mass)

if my_mass_side is not None:
    print("your mass-side guess vs reality (mass is on the):", "left" if left_mass >= tail_mass else "right")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — "the histogram's tallest bar is the average"

**The wrong belief:** "the tallest bar of a histogram sits at the average value."

Watch it break. The tallest bar above is the 0–300ms range — that is where the *bulk* lives
(the **mode**, the most common range). But the **mean** is dragged toward the two slow gaps.
The next cell computes both and shows they point at different stories. A distribution with a
tail has a mode where the crowd is and a mean pulled toward the stragglers; the histogram shows
you the *crowd*, not the *average*.
'''))
C.append(code('''
# Prove the trap wrong by computing both numbers the histogram does NOT directly show.
import statistics  # built-in stats; imported here where first needed

mean_gap = statistics.mean(gaps_ms)       # the average - pulled toward the two slow gaps
median_gap = statistics.median(gaps_ms)   # the middle value - ignores the extremes
# The tallest bar's range is the MODE region; its center is nowhere near the mean.
print("mean gap:  ", round(mean_gap, 1), "ms  (dragged up by 900 and 1500)")
print("median gap:", median_gap, "ms  (what a typical gap actually is)")
print("tallest bar sits in 0-300ms - which matches the MEDIAN, not the MEAN")
# This is exactly why evals report p50/p90, never the mean: the tail owns the mean.
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. In a histogram, what is on the x-axis — categories, or value ranges? What is on the y-axis?
2. The tallest bar shows you the most common *range*. Which single number does it match here —
   the mean or the median — and why does the other one differ?
'''))
C.append(md('''
## Chart 3 — a timeline (turns as bars laid along time)

The bar chart compared categories; the histogram showed a distribution. The **timeline** is
the chart this whole course is built toward: each **turn** of a call becomes a horizontal bar,
placed at its real start time and as long as it actually lasted. Two speakers, two rows.

This is where **overlap becomes visible**. When the agent's bar starts *before* the user's bar
ends, the bars overlap on the page — and that overlap is a **barge-in**, the exact failure the
hero call (`data/hero/turns.json`) is famous for. We build it on toy turns first, then preview
the real one.
'''))
C.append(md('''
## PREDICT
Here are four toy turns (ms). Speaker alternates user/agent:

| turn | speaker | start_ms | end_ms |
|---|---|---|---|
| 1 | user  | 0    | 1000 |
| 2 | agent | 1200 | 2000 |
| 3 | user  | 2200 | 3500 |
| 4 | agent | 3300 | 4200 |

Commit: which **pair** of consecutive turns **overlaps** on the timeline (one starts before the
previous ends)? And is that overlap the agent cutting off the user, or the user cutting off the agent?
'''))
C.append(code('''
# YOUR TURN - PREDICT (timeline): commit and store this before we draw or compute anything.
my_overlap_pair = None   # <- e.g. "3->4" : which consecutive pair overlaps
my_who_interrupts = None # <- "agent interrupts user" or "user interrupts agent"

if my_overlap_pair is None or my_who_interrupts is None:
    print("fill in BOTH predictions above, then re-run.")
else:
    print("locked:", my_overlap_pair, "/", my_who_interrupts)
'''))
C.append(code('''
# Raw toy turns, printed as a list of dicts before any chart - same rule as always.
# These mirror the real call_log schema (speaker, start_ms, end_ms) so the toy transfers to real data.
toy_turns = [
    {"turn_id": "t1", "speaker": "user",  "start_ms": 0,    "end_ms": 1000},
    {"turn_id": "t2", "speaker": "agent", "start_ms": 1200, "end_ms": 2000},
    {"turn_id": "t3", "speaker": "user",  "start_ms": 2200, "end_ms": 3500},
    {"turn_id": "t4", "speaker": "agent", "start_ms": 3300, "end_ms": 4200},  # starts BEFORE t3 ends
]
for t in toy_turns:   # one print per turn so each turn is visibly one bar-to-be
    print(t)
'''))
C.append(code('''
# Manual before the chart: compute the floor-transfer offset (FTO) for each consecutive pair BY HAND.
# FTO = next.start_ms - prev.end_ms. Negative = overlap (bars cross); positive = gap (silence).
# This is the exact definition from pipeline/signals.py - we compute it here so the timeline's
# overlaps are something we DERIVED, not something we eyeballed off a picture.
for a, b in zip(toy_turns, toy_turns[1:]):
    fto = b["start_ms"] - a["end_ms"]           # the single number that defines overlap vs gap
    kind = "OVERLAP (barge-in)" if fto < 0 else "gap (silence)"
    # who-interrupts-whom is just the speaker of the turn that barged in (the 'next' turn)
    who = f"{b['speaker']} interrupts {a['speaker']}" if fto < 0 else ""
    print(f"{a['turn_id']}->{b['turn_id']}: fto = {fto:>6} ms   {kind}   {who}")
'''))
C.append(code('''
# Now the timeline chart. A timeline is built from horizontal bars: ax.barh draws a bar at a y
# position, starting at 'left' (the turn's start_ms) with a given width (its duration).
fig, ax = plt.subplots(figsize=(7, 2.6))

# We put each speaker on its own row so overlap is visible as two bars sharing the same x-range.
row = {"user": 0, "agent": 1}   # y position per speaker; one row each so bars can cross in x
for t in toy_turns:
    dur = t["end_ms"] - t["start_ms"]            # bar width = how long the turn lasted
    # left = where the bar begins on the time axis; this is what places turns in real time
    ax.barh(row[t["speaker"]], dur, left=t["start_ms"], height=0.6)
    ax.text(t["start_ms"] + 30, row[t["speaker"]], t["turn_id"], va="center", fontsize=8)

ax.set_yticks([0, 1]); ax.set_yticklabels(["user", "agent"])  # name the rows or the chart lies by omission
ax.set_xlabel("time (ms) - one clock for the whole call")     # x is TIME here, not a category
ax.set_title("toy call timeline (overlap = barge-in)")
plt.show()
print("timeline drawn; t3 and t4 bars should visibly overlap in x")
'''))
C.append(md('''
## Run the ritual on the timeline (out loud)
1. **x** = time in ms (one clock for the call). 2. **y** = speaker (user row vs agent row).
3. **one bar** = one turn, its width = how long that turn lasted.
4. **License:** it licenses "the agent's t4 started before the user's t3 finished — that is a
   barge-in." It does **NOT** license anything about *why* (model? VAD? audio glitch?) or
   whether the user minded — cause and reaction are not on this chart. The timeline shows
   **what happened in time**, never **why**.
'''))
C.append(code('''
# OBSERVE - did your overlap prediction hold? We already computed FTOs; surface the overlapping pair.
overlaps = []
for a, b in zip(toy_turns, toy_turns[1:]):
    if b["start_ms"] - a["end_ms"] < 0:                 # negative FTO = the bars cross = a barge-in
        overlaps.append(f"{a['turn_id']}->{b['turn_id']} ({b['speaker']} interrupts {a['speaker']})")
print("overlapping pair(s) on the timeline:", overlaps)
if my_overlap_pair is not None:
    print("your guess was:", my_overlap_pair, my_who_interrupts)
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
On a call timeline: what does it mean, physically, when two bars **overlap in x**? What is the
name of that event, and what does FTO (the number) have to be — positive or negative — for it
to happen?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a chart was a finished picture. After Act 2 you can build all three from raw lists by
hand and read each by ritual: **bar** = amount per category, **histogram** = shape of one pile
(crowd ≠ average), **timeline** = turns in time (overlap = barge-in). Every one of them you
computed before you drew — so every picture is checkable, and you can name the claim each does
NOT license. Next we stress them: a chart built from honest numbers that still lies.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2. One sentence: which of the three charts, and why, is the one
# you would actually put in front of a room to show a barge-in - and what would you SAY about it?
clean_sentence_act_2 = ""   # <- your one-liner

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: charts that lie while every number stays honest

## Break-it philosophy

A chart can be built from 100% correct numbers and still argue something false. The lie does
not live in the data — it lives in the **drawing choices**: where the y-axis starts, how wide
the bins are, what gets left off. We now make these lies on purpose, because a lie you have
built yourself is a lie you will recognize on a stranger's slide.
'''))
C.append(md('''
## PREDICT — the truncated y-axis
Two agents, average response gap (ms): `{"agent_v1": 540, "agent_v2": 500}`. A real, tiny
improvement: 40ms. We will draw the SAME two bars twice — once with the y-axis starting at 0,
once starting at 480. Commit: in the second chart, roughly **how many times taller** will v1's
bar *look* than v2's, even though 540 vs 500 is barely different?
'''))
C.append(code('''
# YOUR TURN - PREDICT the visual exaggeration from the truncated axis BEFORE drawing it.
my_apparent_ratio = None   # <- a number: how many times taller v1 will LOOK in the zoomed chart

if my_apparent_ratio is None:
    print("fill in my_apparent_ratio above, then re-run.")
else:
    print("locked: v1 will look ~", my_apparent_ratio, "x taller than v2 in the zoomed chart")
'''))
C.append(code('''
# The honest numbers - no lie here. 540 vs 500 is a 40ms (about 7%) difference.
agent_gaps = {"agent_v1": 540, "agent_v2": 500}
print("raw, honest numbers:", agent_gaps)
print("true difference:", agent_gaps["agent_v1"] - agent_gaps["agent_v2"], "ms (about 7%)")
'''))
C.append(code('''
# BREAK-IT (guided): draw the SAME data two ways. The only thing we change is where y starts.
# We draw them side by side so the deception is undeniable: identical bars, opposite impressions.
fig, (ax_honest, ax_lying) = plt.subplots(1, 2, figsize=(9, 3))

names = list(agent_gaps.keys())
vals = list(agent_gaps.values())

# LEFT: y starts at 0. This is the honest baseline - bar LENGTH is proportional to the value,
# which is the entire reason a bar chart is allowed to encode magnitude.
ax_honest.bar(names, vals)
ax_honest.set_ylim(0, 600)                  # baseline at 0 -> lengths are comparable and truthful
ax_honest.set_title("y starts at 0 (honest)")
ax_honest.set_ylabel("avg gap (ms)")

# RIGHT: y starts at 480. Bar length no longer means magnitude; a 7% gap becomes a cliff.
ax_lying.bar(names, vals)
ax_lying.set_ylim(480, 560)                 # truncated baseline -> the lie, with honest numbers
ax_lying.set_title("y starts at 480 (misleading)")
ax_lying.set_ylabel("avg gap (ms)")
plt.show()
print("same two numbers, two stories - the right chart screams a difference the data whispers")
'''))
C.append(code('''
# Measure the deception instead of just feeling it. "Apparent" height is the bar length ABOVE
# the axis baseline; that is what the eye actually compares.
baseline = 480
apparent_v1 = agent_gaps["agent_v1"] - baseline   # visible length of v1's bar above 480
apparent_v2 = agent_gaps["agent_v2"] - baseline   # visible length of v2's bar above 480
print("above the 480 baseline: v1 =", apparent_v1, "px-units, v2 =", apparent_v2, "px-units")
print("apparent ratio:", round(apparent_v1 / apparent_v2, 1), "x  <- the lie")
print("true ratio:    ", round(agent_gaps['agent_v1'] / agent_gaps['agent_v2'], 2), "x  <- the truth")
# The rule this earns: a bar chart's y-axis MUST start at 0, because bars encode magnitude by length.
'''))
C.append(md('''
## The reveal — what just happened
Every number was honest (540, 500). The **only** change was the y-axis baseline (0 → 480). On
the right, v1's bar looks ~3x taller than v2's, "proving" a dramatic regression that does not
exist. Bars encode magnitude with **length**, so the moment the baseline leaves 0, length stops
meaning magnitude and the chart starts lying with true numbers.

Ritual question 4 catches this: *what claim does the right chart license?* It implies "v1 is
massively slower," which the axes (480–560) do not support. Always check where y starts.
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
A colleague shows you a bar chart where one bar towers over another. Before you believe the
gap is real, what is the FIRST thing you check on the chart — and why does that one choice let
honest numbers tell a dishonest story?
'''))
C.append(md('''
## YOUR break now — the over-binned histogram

A second way to lie with honest numbers: **bin width**. Too few bins and a histogram hides the
tail (everything collapses into one fat bar); too many bins and noise looks like structure.
Your turn to build the deception and predict it.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it (histogram binning).
# my prediction: <write here - with ONE giant bin, will the two slow gaps (900,1500) still be
#                 visible as a tail, or will they vanish into a single bar? say which and why.>

# We reuse the honest gaps pile from Act 2 - same data, a worse drawing choice.
gaps_for_breaking = [120, 150, 200, 180, 220, 160, 140, 190, 900, 1500]

# 1) Choose a DELIBERATELY bad number of bins here (try 1 or 2 to hide the tail; try 50 to invent noise):
bad_bins = 1   # <- change this number, predict the effect first, then run and compare

fig, ax = plt.subplots(figsize=(5, 3))
# Fewer bins = coarser ranges; with bins=1 every value falls in ONE bar and the tail disappears.
ax.hist(gaps_for_breaking, bins=bad_bins)
ax.set_xlabel("gap (ms)"); ax.set_ylabel("count"); ax.set_title(f"histogram with bins={bad_bins}")
plt.show()
# Compare against what you KNOW is there: print the truth the bad binning may be hiding.
print("the tail is real:", [g for g in gaps_for_breaking if g >= 900], "<- does the chart show it?")
'''))
C.append(md('''
## A subtle one: the timeline with no scale

The honest-numbers lie has a timeline version too. The next cell draws our toy timeline but
**hides the x-axis ticks** — the bars are in the right *relative* places, but with no time
scale you cannot tell if a "gap" is 200ms (fine) or 2000ms (a disaster). A timeline without a
readable time axis licenses *ordering* claims but not *duration* claims.
'''))
C.append(code('''
# BREAK-IT (guided): same toy turns, but we strip the x-axis scale. Relative positions survive;
# absolute durations become unreadable - so any claim about "how long" is no longer licensed.
fig, ax = plt.subplots(figsize=(7, 2.4))
row = {"user": 0, "agent": 1}
for t in toy_turns:
    dur = t["end_ms"] - t["start_ms"]
    ax.barh(row[t["speaker"]], dur, left=t["start_ms"], height=0.6)
ax.set_yticks([0, 1]); ax.set_yticklabels(["user", "agent"])
ax.set_xticks([])                       # <- the damage: no time ticks at all
ax.set_xlabel("time -> (no scale shown)")
ax.set_title("timeline with the time scale hidden")
plt.show()
# The fix is one line - restore the scale so duration claims become legible again:
print("without ticks you can see ORDER but not DURATION; the FTOs we computed (e.g. -200ms) are now invisible")
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a chart felt trustworthy if its numbers were correct. After Act 3 you know the lie
often lives in the **drawing**, not the data: a truncated y-axis turns 7% into a cliff, one fat
bin hides a tail, a missing time scale kills duration claims. Ritual question 4 — *what does it
license?* — is your defense. Next, where these exact charts live in VoiceForge.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3. One sentence: name the chart-lie that scares you most and the
# one check that catches it (the truncated y-axis is a strong candidate).
clean_sentence_act_3 = ""   # <- your one-liner

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: these charts on the real call

## The cast, and where these charts plug in

Three calls travel through this whole course (you met them in P00):
- **call_A** — clean English booking, cooperative caller, outcome **success**
- **call_B** — Hinglish appointment with hesitations and a repeat, outcome **partial**
- **call_C** — Telugu-English service call where the **agent interrupts mid-answer**, outcome **failure**

call_C is the real hero call on disk: `data/hero/turns.json`, language `te-en`, stress profile
`interruption`. The timeline you built on toy turns is exactly the chart that exposes its
barge-in. Let's draw the real one.
'''))
C.append(code('''
# Load the REAL hero call from disk - the same file pipeline/signals.py runs on.
# We resolve the path from repo root so it works headless and in your editor alike.
import json
from pathlib import Path
root = next(a for a in [Path.cwd(), *Path.cwd().parents] if (a / "rubric.yaml").exists())
hero = json.loads((root / "data" / "hero" / "turns.json").read_text())

# Print the raw header before charting - know the call you are about to draw.
print("call_id:", hero["call_id"], "| language:", hero["language"], "| profile:", hero["stress_profile"])
print("turns:", len(hero["turns"]))
'''))
C.append(md('''
## PREDICT — the real call's worst FTOs
The spec says the hero call has a **barge-in around 0:18** (~800ms overlap) and a **long gap
around 0:53** (~1,600ms). Commit: on the timeline, the barge-in will show as two bars that
**overlap**; the long gap will show as a **blank stretch** between bars. Which one is the agent
cutting off the user — the overlap, or the gap?
'''))
C.append(code('''
# YOUR TURN - PREDICT (real call): commit and store this before we compute its FTOs.
my_bargein_is = None   # <- "the overlap" or "the gap"

if my_bargein_is is None:
    print("fill in my_bargein_is above, then re-run.")
else:
    print("locked: the agent cutting off the user shows as ->", my_bargein_is)
'''))
C.append(code('''
# Compute the real call's FTOs BY HAND (same formula as pipeline/signals.py: next.start - prev.end).
# We surface only the big events so the two famous failures stand out from normal turn-taking.
turns = sorted(hero["turns"], key=lambda t: t["start_ms"])   # timing only makes sense in time order
for a, b in zip(turns, turns[1:]):
    fto = b["start_ms"] - a["end_ms"]
    if abs(fto) >= 700:                                       # only the dramatic events, not normal gaps
        sec = b["start_ms"] / 1000                            # seconds for human-readable timing
        kind = "BARGE-IN (overlap)" if fto < 0 else "long gap"
        print(f"~{int(sec//60)}:{int(sec%60):02d}  {a['turn_id']}->{b['turn_id']}  fto={fto:>6}ms  {kind}  ({b['speaker']} after {a['speaker']})")
'''))
C.append(code('''
# Draw the REAL hero timeline. Same barh recipe as the toy one - the toy transferred directly.
fig, ax = plt.subplots(figsize=(9, 2.6))
row = {"user": 0, "agent": 1}
for t in turns:
    dur = t["end_ms"] - t["start_ms"]                  # real turn duration in ms
    color = "tab:orange" if t["speaker"] == "agent" else "tab:blue"  # color by speaker so rows read fast
    ax.barh(row[t["speaker"]], dur, left=t["start_ms"], height=0.6, color=color)

ax.set_yticks([0, 1]); ax.set_yticklabels(["user", "agent"])
ax.set_xlabel("time (ms) - one clock for the whole call")
ax.set_title("hero_001 real timeline (call_C) - look near 18s and 53s")
plt.show()
# Near 18s the agent bar starts before the user bar ends (the 800ms barge-in); near 53s there is a blank stretch (the 1.6s gap).
print("real timeline drawn from data/hero/turns.json")
'''))
C.append(md('''
## Where each chart lives in the real pipeline (honest map)

- **bar** → counts per failure tag / per call outcome (success vs partial vs failure across the
  cast and the 11 normalized calls in `data/normalized/`). "How many calls failed on barge-in?"
- **histogram** → the distribution of FTO gaps that `pipeline/signals.py` produces via
  `turn_metrics()` and `analyze()`; the histogram is why the rubric reports **p50/p90, not mean**
  (`rubric.yaml`, `latency_gap.laggy_ms = 800`). The tail you saw is real latency disasters.
- **timeline** → the per-call view of `turns` (the schema in `schemas/call_log.md`); overlap on
  it = the `barge_in` dimension (`threshold_overlap_ms = 100`). This is the chart that turns a
  number ("−800ms FTO") into something a room *sees*.
'''))
C.append(md('''
## The same concept at three levels (say each in one breath)

- **To a beginner:** "a chart is a picture of numbers; before you trust it, name what the
  sideways and up-down directions mean, and what one bar stands for."
- **To an engineer:** "bar = categorical magnitude (baseline 0 or it lies), histogram = the
  distribution behind a summary stat (so we show p50/p90 not a tail-poisoned mean), timeline =
  turns over a single clock where negative FTO renders as overlap = barge-in."
- **To a founder:** "every chart we put on a slide is an argument we can defend axis by axis —
  we state what it proves and what it does not, so we never get caught overclaiming in the room."
'''))
C.append(md('''
## Defense questions (×3, answers below — try first)

**1. "Your latency bar chart looks great — why should I believe the agent is fast?"**
<details><summary>answer</summary>A single bar is a mean or median; it hides shape. I show the histogram behind it: most gaps are snappy but there is a tail of slow ones, which is why we report p50 AND p90, never just the mean. The bar alone does not license "the agent is fast."</details>

**2. "This timeline shows an overlap — how do you know it is a real barge-in and not a drawing glitch?"**
<details><summary>answer</summary>The overlap is not eyeballed off the picture; it is the FTO computed in pipeline/signals.py (next.start_ms − prev.end_ms = −800ms at ~0:18), which exceeds the barge_in threshold of 100ms in rubric.yaml. The chart only visualizes a number the deterministic code already found.</details>

**3. "Could I draw your data to make the new agent look better than it is?"**
<details><summary>answer</summary>Yes — truncate the y-axis off 0 and a 7% gap becomes a cliff; widen the bins and a latency tail vanishes; hide the time scale and duration claims disappear. That is exactly why I keep y at 0, fix bin edges deliberately, and label every axis: so the chart licenses only what the data supports.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You can now place all three charts in the real VoiceForge pipeline: bar for failure/outcome
counts, histogram for the FTO distribution behind p50/p90, timeline for per-call barge-in. You
drew the real hero call and saw its 800ms barge-in and 1.6s gap as a shape. You can defend each
chart axis by axis. Next book, P04, debugs the code that produces these numbers when a chart
looks wrong.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The **4-question chart ritual** (all four, in order)
2. The three charts and the one question each answers (bar / histogram / timeline)
3. What **overlap on a timeline** means and the sign FTO must have for it
4. One way to make an **honest-numbers chart lie**, and the check that catches it
5. Where ONE of these charts lives in the real pipeline (cite the file)

Could not hit all five? Reopen, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (where the charts live in the real pipeline)
my_clean_sentence = ""      # the sentence you would say in a room about reading/making eval charts

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"A chart is an argument; I must be able to say what its axes are and what claim it does and
> does not license."**

If yours captures that in your own words, this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "P03_basic_plots_for_evals.ipynb"   # <- this notebook's filename
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

**P03 done** (pending your teach-back) → **P04 · Debugging** — when one of these charts looks
wrong, P04 is the ritual for finding out *why*: print the input, print the intermediate, shrink
the example, until the bug in the pipeline that produced the number has nowhere to hide.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "P03_basic_plots_for_evals.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
