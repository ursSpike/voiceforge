#!/usr/bin/env python3
# Builds 30_post_hackathon_path.ipynb per _BUILD_SPEC.md (four acts, marker conventions, recurring cast).
# This is the LAST book on the ladder: 29 (the demo) -> THIS (post-hackathon path) -> none (course end).
# The ONE atomic concept: what turns a weekend artifact into a lane.
# Rerun: .venv/bin/python notebooks/build_30.py
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
# 30 · Post-hackathon path

## 1 — Learning contract
By the end of this notebook you will be able to:
1. State the **one difference** between a weekend artifact and a **lane**: whether the
   **data layer keeps compounding** after Saturday, or stops the moment the demo ends.
2. Name the six roadmap moves that turn VoiceForge from a demo into a lane — and say which
   **one** of them is load-bearing (the improvement-data layer) and why the other five lean on it.
3. Draft **your own next three steps** as a small, ordered, checkable list (the gym output of
   this book is *your* roadmap, not mine).
4. Spot the trap **"a good demo = a product"** in the wild, and replace it with a test you can
   run on any weekend project: *does anything compound, or does it all evaporate?*

This is the final book. Topic-wise it is the lightest in the course — no new math, no new
metric. The work is **decision-shaped**, not arithmetic-shaped: what do you do *Monday*?
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits)

`29 (the demo) → THIS: post-hackathon path → (course end)`

In **29** you stood the artifact up and defended it for three minutes: the hero call, the
timed failures, the scorecard, the improvement queue, the A/B loop. That was the **artifact**.

Why this book exists, and exists *last*: a hackathon rewards the artifact and then goes quiet.
The default after Saturday is **abandonment** — the repo cools, the credits expire, the demo
becomes a screenshot. This book is the antidote. It asks the only question that separates a
project that *became something* from one that *was something once*: **what, if anything,
keeps growing on its own after the applause stops?** There is no "next door" — the ladder
ends here, on purpose, with a decision instead of a lesson.
'''))
C.append(md('''
## 3 — Baby intuition

Two founders both win the same hackathon on Saturday.

- Founder One has a **gorgeous demo**: a slick video, a polished slide, a call that plays
  perfectly. On Monday the video still exists. Nothing else moved. To improve it, they must
  re-record. The artifact is **frozen** — it is exactly as good as it was at 5pm Saturday,
  forever.
- Founder Two has a rougher demo but a **queue**: every call the system judges drops an
  improvement example into a file, flagged for a human to confirm. On Monday there are 12 new
  calls, so the queue has new pairs. On Friday there are 200. The artifact **gets better while
  they sleep**, because the *data* is the thing that grows, not the demo.

Founder One built an **artifact**. Founder Two built a **lane** — a direction the project can
keep moving in without re-doing the work. The difference is not talent or polish. It is whether
there is a **layer that compounds**.
'''))
C.append(md('''
## 4 — The formal version

A **weekend artifact** is a one-time output: a demo, a deck, a recorded call. Its value is
**fixed at creation** — to raise it you must spend the same effort again from scratch.

A **lane** is a direction the project keeps moving in because some layer **compounds**: each new
unit of input makes the next output cheaper or better, with no new from-scratch work.

> **artifact:** value(t) ≈ value(t₀)        (flat after Saturday)
> **lane:** value(t) grows with accumulated data, even at zero new feature work

The layer that compounds in VoiceForge is **the improvement-data layer**: judged calls →
failures with evidence → preference pairs (`chosen` / `rejected`) → a human-reviewed queue →
a DPO export. Every call you ever run feeds it. It is the **only** part of the system whose
value is a function of *time and volume*, not of how clever one Saturday was.

The roadmap (Act 2) is six moves. Five of them are *features*. One is the *compounding layer*.
A lane keeps the load-bearing one alive; an abandoned project lets it freeze.
'''))
C.append(md('''
## 5 — Why this exists (the part founders care about)

"We won the hackathon" is a moment. "We have 600 reviewed preference pairs and the model is on
its third DPO pass, each one measured against the last" is a **trajectory** — something an
investor, a teammate, or future-you can see *moving*. One is a trophy; the other is momentum.

The cost asymmetry is the whole argument. A better demo costs the same every time you want one.
A compounding data layer costs a **fixed bit of plumbing once**, and then every call you were
going to run anyway pays into it for free. The expensive thing (judging, timing, evidence) you
**already built** in books 04–21. The post-hackathon move is not "build more" — it is "stop
throwing away the exhaust."

The next cells make this concrete with a tiny model you can run, then hand you the real roadmap,
then make you draft your own. No new library. The hard part is the decision, so we drill the
decision.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In one sentence: what is the **single** difference between an artifact and a lane?
2. Of the six roadmap moves, which **one** is the compounding layer, and what does "compounding"
   mean here (in terms of cost-per-improvement over time)?
3. Why does this book sit **last** on the ladder instead of teaching a new metric?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: winning the hackathon = the work is done, and a better
project means a better demo. After Act 1 you should hold: the demo is an **artifact** whose value
is frozen at creation; a **lane** is whatever **compounds** afterward; and in VoiceForge the one
compounding thing is the **improvement-data layer** — every call feeds it, so it grows on its own.

If that feels like your own sentence, continue. If not, re-read the two-founders story in cell 3.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of "artifact vs lane".
# Producing the sentence is the learning; reading mine would only feel like it.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: model the compounding, then meet the real roadmap

## Artifact vs lane, as two number lines you can watch

Course rule: before any opinion, a tiny toy you can see. We will model "value over the days
after the hackathon" two ways — a flat artifact and a compounding lane — with plain arithmetic,
nothing hidden. The point is to *feel* the gap between flat and compounding, not to be precise.
'''))
C.append(md('''
## PREDICT
Two projects start at value **10** on Saturday (day 0).
- The **artifact** gains **0** per day (it is frozen; improving it means re-doing it).
- The **lane** grows by **8%** of its current value each day (each day's data makes the next
  day's improvement a little cheaper — that is compounding).

After **30 days**, roughly: is the lane **a little** ahead, **double**, or **many times** the
artifact? Commit to one before the next cell.
'''))
C.append(code('''
# YOUR TURN - lock your prediction BEFORE the compute cell, so the notebook records YOUR
# thinking and a later cell can compare it to reality. That comparison is the lesson.
my_day30_ratio_guess = None   # <- replace None with a number: lane_value / artifact_value at day 30

if my_day30_ratio_guess is None:
    print("fill in my_day30_ratio_guess above (e.g. 2 for 'double'), then re-run.")
else:
    print("prediction locked: lane is ~", my_day30_ratio_guess, "x the artifact at day 30")
'''))
C.append(code('''
# Model both by hand, one day at a time, every value visible - no library, no magic.
# We loop day by day instead of using a closed-form formula, because the LESSON is watching
# the lane pull away from the flat artifact step by step.
artifact = 10.0    # frozen: a demo is exactly as good tomorrow as today
lane = 10.0        # compounding: grows by a fraction of itself each day

daily_growth = 0.08    # 8% per day - stands in for "each call makes the next improvement cheaper"
for day in range(1, 31):
    artifact = artifact + 0.0           # the artifact gains nothing without redoing the work
    lane = lane + lane * daily_growth   # the lane grows ON TOP OF what it already accumulated
    if day in (1, 5, 10, 20, 30):       # print a few checkpoints so the curve's shape is visible
        print(f"day {day:>2}:  artifact = {artifact:5.1f}   lane = {lane:6.1f}")
'''))
C.append(code('''
# The metal-detector reading: did YOUR committed guess match the real ratio?
# We compute the ratio explicitly so the "many times, not a little" point lands as a number.
ratio = lane / artifact
print(f"lane / artifact at day 30 = {ratio:.1f}x")

if my_day30_ratio_guess is not None:
    close = abs(my_day30_ratio_guess - ratio) <= 2   # "close enough" since this toy is about shape
    print("your guess", "was in the ballpark" if close else "DIFFERED a lot",
          "- if it differed, the gap is the lesson: compounding outruns intuition")
'''))
C.append(md('''
## OBSERVE + EXPLAIN

The artifact sat at **10** the whole month. The lane crossed **100** — about **10x** — without a
single new "feature," purely from compounding. One sentence, out loud: *why does a flat line and
a compounding line, starting at the same value, end up so far apart in only 30 days?*

(The 8% is invented. The **shape** is the truth: flat stays flat; compounding runs away. A demo
is the flat line. The data layer is the curve.)
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
Explain why "spend Saturday making the demo 20% nicer" and "spend Saturday wiring the data layer
so it compounds" are **not** the same kind of investment — even if both took the same hours.
(If your answer mentions "one pays once, the other pays every day after," you have it.)
'''))
C.append(md('''
## Manual-before-real — the roadmap as raw rows first

Now the actual VoiceForge roadmap: the six moves that turn this weekend's artifact into a lane.
Course rule: print the **raw** list before doing anything with it. Read it as a table — one row
is one move; the columns are *what it adds* and *whether it compounds*.
'''))
C.append(code('''
# The roadmap, as raw rows. We print it RAW (one per line) before any analysis, so each MOVE is
# visibly one THING. "compounds" = does each new call/day make this better on its own, or is it
# a one-time feature that sits at whatever quality you last gave it?
roadmap = [
    {"step": "more call logs",        "adds": "broader coverage (more languages, stress profiles)", "compounds": True},
    {"step": "real provider adapters","adds": "swap mock ASR/LLM/TTS for real vendors",             "compounds": False},
    {"step": "multilingual eval set", "adds": "Hinglish + Telugu held-out calls to score against",  "compounds": True},
    {"step": "human-review UI",       "adds": "a screen to confirm/reject improvement-queue pairs", "compounds": True},
    {"step": "DPO export",            "adds": "reviewed pairs -> a training file (chosen/rejected)", "compounds": True},
    {"step": "public write-up",       "adds": "a post explaining the eval method + findings",        "compounds": False},
]
for r in roadmap:
    print(f"- {r['step']:<22} compounds={str(r['compounds']):<5} | {r['adds']}")
'''))
C.append(md('''
## PREDICT
Look at the six rows above. **Four** are marked `compounds=True` and **two** are `compounds=False`.
Before the next cell: which two do you think are the *non*-compounding ones, and why would
"real provider adapters" and a "public write-up" be one-time features rather than growing layers?
'''))
C.append(code('''
# YOUR TURN - lock your read before the split is computed. Predicting the split first is how you
# test whether you actually internalized "compounds = grows on its own with more data/time".
my_noncompounding_guess = None   # <- a list of two step-names, e.g. ["real provider adapters", "public write-up"]

if my_noncompounding_guess is None:
    print('fill in my_noncompounding_guess above (a list of two step names), then re-run.')
else:
    print("locked your guess for the non-compounding moves:", my_noncompounding_guess)
'''))
C.append(code('''
# Split the roadmap by the compounds flag - manual filter, no library - so the structure is plain.
# We separate them because the WHOLE point of this book is that these two groups are not equal:
# one group is the lane's engine, the other is supporting bodywork.
compounding     = [r["step"] for r in roadmap if r["compounds"]]
noncompounding  = [r["step"] for r in roadmap if not r["compounds"]]
print("compounding (the lane's engine):", compounding)
print("non-compounding (one-time features):", noncompounding)

# Check it against your guess, if you made one - the comparison is the metal detector.
if my_noncompounding_guess is not None:
    match = sorted(my_noncompounding_guess) == sorted(noncompounding)
    print("your non-compounding guess", "matched" if match else "DIFFERED",
          "- if it differed, re-read each 'adds' and ask: does MORE data improve it by itself?")
'''))
C.append(md('''
## OBSERVE
The split is not "important vs unimportant" — adapters and a write-up matter. It is
**compounds vs one-time**. Adapters make the demo *real* but the system is no better on call
1,000 than on call 10 just because adapters exist. The write-up spreads the idea but does not
improve the model. The four `compounds=True` moves all feed the same thing: **the data layer**.
'''))
C.append(md('''
## Manual-before-function — trace ONE call through the compounding layer

The four compounding moves are not four separate engines; they are one **pipe**. Watch a single
call flow through it, by hand, to see why each new call grows the asset:

`raw call → judged (failures + evidence) → preference pair (chosen/rejected) → human-reviewed →
DPO export row`

We will walk one toy call through those five stages, printing each stage, before touching any
real pipeline file.
'''))
C.append(md('''
## PREDICT
We push **one** call (`call_C`, the Telugu failure: agent barged in mid-address) through the five
stages. At the end, how many **new training rows** has this single call added to the DPO export?
And what is the one field that makes the pair *teach* something (the difference between `chosen`
and `rejected`)? Commit before the next cell.
'''))
C.append(code('''
# YOUR TURN - lock your prediction for the trace before running it.
my_rows_added = None   # <- how many DPO training rows does ONE failed call contribute here?

if my_rows_added is None:
    print("fill in my_rows_added above (a number), then re-run.")
else:
    print("locked: you predict one call adds", my_rows_added, "DPO row(s)")
'''))
C.append(code('''
# Walk ONE call through the compounding pipe by hand. Each stage is a plain dict so the
# TRANSFORMATION is visible - we are tracing data, not calling the real pipeline yet (that comes
# in Act 4). This mirrors the cast's call_C (Telugu-English failure, barge-in over the address).
raw_call = {"id": "call_C", "language": "Telugu-English", "outcome": "failure"}

# stage 1: the judge + signals layer tags WHY it failed, with evidence turns (books 04, 10).
judged = {**raw_call, "failure": "barge_in", "evidence_turn_ids": ["t2", "t3"]}

# stage 2: the failure becomes a preference PAIR - the only difference is the failed axis fixed
# (the agent waits instead of cutting in). chosen = the better behavior, rejected = what happened.
pair = {
    "call_id": "call_C", "failure_dimension": "barge_in",
    "rejected": "agent interrupts caller mid-address",
    "chosen":   "agent waits for the address, then confirms it back",
    "needs_human_review": True,   # nothing trains until a human confirms - that is the next stage
}

# stage 3: a human reviews and confirms (or edits) the pair - this is the human-review UI's job.
reviewed = {**pair, "needs_human_review": False, "human_verdict": "confirmed"}

# stage 4: confirmed pairs export to a DPO training row (the format a trainer consumes).
dpo_row = {"prompt": "<the call context>", "chosen": reviewed["chosen"], "rejected": reviewed["rejected"]}

for label, stage in [("raw", raw_call), ("judged", judged), ("pair", pair),
                     ("reviewed", reviewed), ("dpo_row", dpo_row)]:
    print(f"{label:>9}: {stage}")
'''))
C.append(code('''
# Count what ONE call produced, and name the teaching field. We make this explicit because the
# compounding claim IS this number: every call that fails can add a row, so the asset grows per call.
rows_added = 1   # this one failed call yielded exactly one (chosen, rejected) training row
print("DPO rows added by this single call:", rows_added)
print("the field that makes it teach:", "the gap between chosen and rejected on ONE axis (barge_in)")

if my_rows_added is not None:
    print("your prediction", "matched" if my_rows_added == rows_added else "DIFFERED",
          "- the key idea: N failed calls -> ~N reviewed pairs -> a file that grows with every call")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not from memory): why does every additional call make the
DPO export bigger *without any new feature work*, and why is `needs_human_review=True` the gate
that keeps the growing data **trustworthy** rather than just large?
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. Name the five stages a call passes through in the compounding pipe, in order.
2. Which roadmap move builds the **human-review** stage, and why can the export not be trusted
   without it (think back to book 12: why human labels)?
3. In the toy model, the artifact ended at 10 and the lane near 100. Restate that gap in plain
   words about *calls*, not about the made-up 8%.
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: "the roadmap" felt like a flat to-do list of six equal tasks. After Act 2 you can: model
why compounding outruns flat in 30 days, **split** the roadmap into four compounding moves and two
one-time features, and **trace one call** through the five-stage pipe (raw → judged → pair →
reviewed → DPO row) that makes every new call grow the asset. The roadmap is not six chores; it is
one engine plus some bodywork.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (the split / the five-stage pipe / compounding)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: the trap, breaking the lane, and how projects actually die

## WRONG-INTUITION TRAP — "a good demo = a product"

**The wrong belief:** "the demo killed it on Saturday, so we basically have a product — the rest
is just polish."

This is the most expensive belief in this entire course, because it *feels* earned. You won. The
call played. The room clapped. Surely the hard part is behind you?

The next cell scores two hackathon projects on the only axis that predicts whether they survive:
**does anything compound?** Run it, then try to say which project is the "real" one BEFORE the
reveal — and notice that demo quality is not even an input.
'''))
C.append(code('''
# Two projects. We deliberately give the FLASHY one a better demo score and the DURABLE one a
# worse demo score, to prove demo quality does not decide survival - the compounding layer does.
flashy   = {"name": "DemoKing", "demo_polish": 10, "calls_per_week": 0,  "review_queue": False}
durable  = {"name": "Lanely",   "demo_polish": 6,  "calls_per_week": 40, "review_queue": True}

# A crude "still alive in 8 weeks?" model: a project survives if its DATA compounds, i.e. new calls
# keep flowing AND there is a queue turning them into reviewed training signal. Polish is ignored
# ON PURPOSE - that is the trap. We project 8 weeks of accumulated reviewed pairs.
def projected_pairs(p, weeks=8):
    # if nothing flows in or there is no queue to catch it, the asset never grows: stays at 0
    if p["calls_per_week"] == 0 or not p["review_queue"]:
        return 0
    # ~30% of calls surface a failure that becomes a reviewable pair (rough, but the SHAPE is real)
    return int(p["calls_per_week"] * weeks * 0.30)

for p in (flashy, durable):
    print(f"{p['name']:<9} demo={p['demo_polish']:>2}/10  ->  reviewed pairs after 8 weeks: {projected_pairs(p)}")
'''))
C.append(md('''
## The reveal

**DemoKing** scored a perfect 10 on polish and accumulated **0** reviewed pairs in eight weeks —
because no calls flow in and there is no queue. It is exactly as good as demo day, forever. It is
an artifact wearing a product's clothes.

**Lanely** had a mediocre demo (6/10) and accumulated **~96** reviewed pairs — a real, growing
training set — because calls flow and a queue catches them. In two months it has *data DemoKing
can never get* without rebuilding from scratch.

The trap, dismantled: **demo polish was not even in the survival formula.** "A good demo" measures
how Saturday went. "Does anything compound" measures whether Monday-through-forever goes anywhere.
They are different axes, and only the second one predicts a product. (This is the same shape as
book 04's mean trap — a number that looks great and predicts nothing about the thing you care about.)
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why does "a good demo" fail to predict whether a project survives?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## Break-it philosophy

You do not understand the lane until you know what **kills** it. So we now damage the compounding
layer on purpose and watch the asset stop growing. A lane is fragile in a specific way: it needs
**both** new calls flowing in **and** a trustworthy review step. Cut either, and "compounding"
quietly becomes "flat" — with no error message to warn you.
'''))
C.append(md('''
## PREDICT
We take a healthy lane (40 calls/week, queue on) and break **one** thing: we set
`calls_per_week = 0` (the team stops running new calls after the hackathon — the single most
common way these projects die). Does the 8-week reviewed-pair count go to **zero**, drop a
**little**, or stay the **same** because the old pairs are still there? Commit before running.
'''))
C.append(code('''
# BREAK-IT (guided) - we damage the INFLOW, the way a real team does by going quiet after Saturday.
# We copy the durable project so the original stays intact, then zero out its call inflow.
import copy
abandoned = copy.deepcopy(durable)
abandoned["calls_per_week"] = 0          # the damage: no new calls after the hackathon

# Re-run the SAME survival model. With zero inflow, the queue has nothing to catch, so the
# compounding asset flatlines - the lane silently becomes an artifact, no crash, no warning.
print("healthy lane reviewed-pairs (8 wks):  ", projected_pairs(durable))
print("abandoned lane reviewed-pairs (8 wks):", projected_pairs(abandoned))
print("the asset did not shrink - it stopped GROWING, which is how a lane dies quietly")
'''))
C.append(md('''
## Reading the result — abandonment is silent

Nothing errored. No red. The reviewed-pair count just went from ~96 to **0** new pairs, and the
project *feels* the same on Monday — the repo is still there, the demo still plays. That silence is
the danger. A lane does not die with a crash; it dies when the inflow stops and **nobody notices
for weeks** because the artifact still looks fine. The fix is not technical: it is keeping the
cheap inflow alive (run the calls you were going to run anyway through the pipe).
'''))
C.append(md('''
## PREDICT — the second break
Now the *other* failure mode. Calls keep flowing (40/week) but we turn the review step into a
**rubber stamp**: every pair is auto-confirmed with `needs_human_review` never actually checked by
a human. The export still grows fast. Predict: is a fast-growing **un**-reviewed export *more*
valuable than a slow reviewed one, the same, or a **liability**? (Think book 12: why human labels.)
'''))
C.append(code('''
# YOUR TURN - self-authored BREAK-IT. Damage the REVIEW quality instead of the inflow, and decide
# what an un-reviewed-but-large export is worth. Fill the placeholders, then run.
# my prediction: <write here what a fast-growing un-reviewed export is worth, and why>

auto_confirmed_pairs = None   # <- set a number: how many pairs/week if you skip human review (e.g. 12)
human_reviewed_pairs = None   # <- set a smaller number a human can actually check (e.g. 4)

# Guard so the cell runs clean UNFILLED: only compare once you have committed both numbers.
if auto_confirmed_pairs is None or human_reviewed_pairs is None:
    print("fill in BOTH numbers above (auto-confirmed vs truly human-reviewed per week), then re-run.")
else:
    # The trust point (book 12): an unreviewed pair can encode the judge's OWN mistakes as
    # "training truth", so volume without review can teach the model the wrong lesson faster.
    print("auto-confirmed/week:", auto_confirmed_pairs, " (fast, but each may carry a judge error)")
    print("human-reviewed/week:", human_reviewed_pairs, " (slow, but each is trustworthy signal)")
    print("bigger is NOT better here: un-reviewed volume can be a liability, not an asset")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. Name the **two** distinct ways the compounding lane dies (one is about inflow, one is about
   review quality). Which one is silent and why is silence dangerous?
2. Why is a *fast-growing un-reviewed* export potentially **worse** than a slow reviewed one?
   (Tie it to book 12: why human labels.)
3. The demo-polish score was never in the survival model. Say why that is the whole point of the
   "a good demo = a product" trap.
'''))
C.append(md('''
## A crashing teaching cell — what "abandon it after Saturday" looks like in code

The most honest way to feel abandonment: write code that *assumes the project kept going* and run
it against a project that **stopped**. The next cell tries to compute the model's improvement from
DPO pass #2 — but an abandoned project never ran pass #1, so the data it needs does not exist. It
will crash. Read the error; it is the shape of every dead hackathon project.
'''))
C.append(code('''
# BREAK-IT - this cell is SUPPOSED to error. # EXPECTED FAILURE FOR LEARNING
# We model an ABANDONED project: it has an empty history of DPO passes because nobody continued
# after Saturday. Asking for "the improvement since the last pass" has no last pass to point at.
dpo_pass_history = []   # abandoned: zero training passes ever ran

# Trying to read the most recent pass crashes - there is no "last" of an empty history. This IS
# what abandonment costs: the code that would measure progress has no progress to measure.
last_pass_score = dpo_pass_history[-1]["model_score"]   # IndexError on an empty list
print("improvement since last pass:", last_pass_score)
'''))
C.append(md('''
## Reading the error — and the recovery

`IndexError: list index out of range`. The history is empty because the project **stopped**. The
error is not a bug in the code; it is the code correctly reporting that *there is nothing to
measure when nothing happened*. The recovery is not a try/except — it is **not abandoning the
project**: keep even one pass flowing so the history is never empty. The next cell shows the
not-abandoned version, where one pass exists and the measurement works.
'''))
C.append(code('''
# Recovery cell: the SAME computation on a project that did NOT abandon - one DPO pass exists, so
# the history is non-empty and the measurement the crashing cell wanted is now well-defined.
dpo_pass_history = [{"pass": 1, "model_score": 0.71}]   # kept going: at least one pass ran

# Guard against the empty-history crash explicitly, because "did we keep going?" must be CHECKED,
# never assumed - that check is the whole post-hackathon discipline in one line.
if dpo_pass_history:
    last_pass_score = dpo_pass_history[-1]["model_score"]
    print("latest DPO pass score:", last_pass_score, "- there is a number because the project stayed alive")
else:
    print("no passes yet - the project stopped; nothing to measure (this is the failure to avoid)")
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
1. The crashing cell raised `IndexError` not because of a code bug — explain what real-world fact
   the empty list was reporting.
2. The "recovery" was not a try/except. What was it, and why is that the right fix for *this*
   problem rather than catching the exception?
3. Connect it to the lane: what is the single cheapest habit that keeps the DPO-pass history from
   ever being empty?
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: "a good demo = a product" felt self-evidently true, and a roadmap felt like a list you either
finish or don't. After Act 3: demo polish does **not** predict survival (only compounding does),
a lane dies in **two** silent ways (inflow stops, or review becomes a rubber stamp), and the code
that measures progress **crashes on an abandoned project** because there is literally nothing to
measure. Abandonment is not dramatic; it is a quiet flatline you prevent with cheap, steady inflow.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the trap, or "a lane dies silently", your pick)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the real repo, your own roadmap, and defending the plan

## Where the lane lives in VoiceForge (these are real files)

The compounding layer is not a metaphor — it is already half-built in this repo. The
post-hackathon path is mostly *finishing* and *feeding* what books 04–21 stood up:

| roadmap move | where it lives for real | status today |
|---|---|---|
| more call logs | `data/normalized/*.json` (11 real calls now: hero + 10 SpokenWOZ) | the pool to grow |
| real provider adapters | `pipeline/normalize.py`, `pipeline/judge.py` (real Gemini judge) | judge real, ASR/TTS mocked |
| multilingual eval set | the cast: `call_A` English, `call_B` Hinglish, `call_C` Telugu-English | seeded, needs volume |
| human-review UI | `out/queue.jsonl` pairs carry `needs_human_review=true` | flag exists, no screen yet |
| DPO export | `pipeline/dpo_export.py` → `out/queue.jsonl` / `out/queue_openai.jsonl` | scaffolded (a TODO stub) |
| public write-up | `README.md`, `SPEC.md`, `reports/` | the method is documented |

The honest read: the **expensive** parts (timing in `pipeline/signals.py`, judging in
`pipeline/judge.py`, the rubric in `rubric.yaml`) are **done**. The post-hackathon work is the
cheap connective tissue — a review screen and steady inflow — that turns those one-off parts into
a layer that compounds. We confirm the real export target exists in the next cell.
'''))
C.append(md('''
## PREDICT — the size of the pool you start from
The lane's inflow today is the `data/normalized/` pool (the hero call plus a handful of real
SpokenWOZ calls). Before the next cell lists them: how many real call logs do you think are in
that pool **right now** — a few, a few dozen, or hundreds? Commit a number; it sets the honest
baseline you are growing from.
'''))
C.append(code('''
# Confirm the real compounding-layer anchors EXIST on disk - the lane is real files, not a wish.
# We resolve the repo root by walking up to wherever rubric.yaml lives, so this runs from anywhere.
from pathlib import Path
root = next(a for a in [Path.cwd(), *Path.cwd().parents] if (a / "rubric.yaml").exists())

# We check the call pool (the inflow you grow) and the DPO export script (the compounding sink).
# Listing them proves the lane is already plumbed - the post-hackathon job is to FEED it, not invent it.
normalized = sorted((root / "data" / "normalized").glob("*.json"))
print("real call logs in the pool right now:", len(normalized))
print("  e.g.:", [p.name for p in normalized[:3]])
print("DPO export script present:", (root / "pipeline" / "dpo_export.py").exists(),
      "(-> out/queue.jsonl: the file that grows with every reviewed pair)")
'''))
C.append(md('''
## PREDICT — your own next three steps
This is the gym output of the whole book. There is no answer key. Given that the expensive parts
are done and the lane needs *feeding* and a *review screen*, what are **your** next three steps,
in order, that you could actually start Monday? Think small and checkable (a step you can mark
"done", not "world domination"). Commit them in the next cell.
'''))
C.append(code('''
# YOUR TURN - draft YOUR next three steps. This is the point of the notebook: not my roadmap, yours.
# Keep each step small and checkable. Guarded so the cell runs clean while still empty.
my_next_steps = [
    None,   # step 1: <replace None with a short string, e.g. "add 20 more normalized call logs">
    None,   # step 2: <replace None with your second step>
    None,   # step 3: <replace None with your third step>
]

# A step "counts" only if it is a real string; we filter Nones so an unfilled cell runs clean.
filled = [s for s in my_next_steps if isinstance(s, str) and s.strip()]
if len(filled) < 3:
    print(f"you have drafted {len(filled)}/3 steps - replace the Nones above with real steps, then re-run.")
else:
    for i, s in enumerate(filled, 1):
        print(f"step {i}: {s}")
    print("locked: three concrete, ordered next steps you could start Monday")
'''))
C.append(md('''
## YOUR TURN — pressure-test your own roadmap
A roadmap is only as good as the question you ask of it. For each of your three steps, ask the one
test from this whole book: **does this step feed the compounding layer, or is it a one-time
feature?** Both kinds are allowed — but you should *know which is which*, so you do not mistake
polish for progress. Mark each step in the next cell.
'''))
C.append(code('''
# YOUR TURN - tag each of your steps as compounding or one-time. Guarded for the unfilled case.
# We do this because the book's core skill is telling "feeds the lane" apart from "nice feature".
my_step_tags = [
    None,   # tag for step 1: replace None with True (compounds) or False (one-time)
    None,   # tag for step 2
    None,   # tag for step 3
]

tagged = [t for t in my_step_tags if t is not None]
if len(tagged) < 3:
    print(f"you have tagged {len(tagged)}/3 steps - set each to True (compounds) or False (one-time), then re-run.")
else:
    n_compounding = sum(1 for t in my_step_tags if t is True)
    print("compounding steps:", n_compounding, "of 3")
    # The honest gut-check: if NONE of your next three feed the lane, you are polishing an artifact.
    if n_compounding == 0:
        print("warning: zero compounding steps - that is a polish plan, not a lane plan. revisit.")
    else:
        print("good: at least one step feeds the layer that grows on its own")
'''))
C.append(md('''
## PREDICT — the abandonment guard
One more, and it is the realest one. The #1 reason this project dies is not technical — it is that
**you stop after Saturday**. What is the single, cheap, recurring habit (something you could do in
under five minutes a week) that keeps the inflow alive so the lane never silently flatlines?
Commit it in the next cell as your personal anti-abandonment rule.
'''))
C.append(code('''
# YOUR TURN - your personal anti-abandonment rule. Guarded so it runs clean unfilled.
# Stored as a string because the act of NAMING the habit is what makes it stick (book P00's logic).
my_weekly_habit = ""   # e.g. "every Monday, run the 10 newest calls through the pipe and review 3 pairs"

if len(my_weekly_habit.strip()) < 15:
    print("write your weekly anti-abandonment habit above (15+ chars), then re-run.")
else:
    print("ANTI-ABANDONMENT RULE LOGGED:", my_weekly_habit)
    print("this one habit is what keeps the DPO-pass history from ever being empty")
'''))
C.append(md('''
## The three-level explanation (same concept, three rooms)

- **To a beginner:** "A demo is a thing you made once — it does not get better on its own. A lane
  is a setup where every call you run makes the system a little better, even while you sleep. After
  the hackathon, keep the calls flowing into the queue and you have a lane, not just a demo."
- **To an engineer:** "The compounding layer is `signals.py` + `judge.py` → failures with evidence
  → `dpo_export.py` preference pairs (`chosen`/`rejected`, `needs_human_review=true`) →
  `out/queue.jsonl`. Value is O(calls processed), not O(features shipped). The post-hackathon work
  is the cheap connective tissue: a review UI over the queue and a weekly inflow job — not new
  metrics. The expensive deterministic core is already built and frozen."
- **To a founder:** "We are not shipping a better demo; we are shipping a flywheel. Every call our
  customers make becomes reviewed training data, so the product improves with usage at near-zero
  marginal cost. The moat is the accumulating, human-verified preference set — not the Saturday
  demo, which any competitor can copy in a weekend."
'''))
C.append(md('''
## Defense questions (×3 — try first, then open)

**1. "You won the hackathon — isn't the work basically done?"**
<details><summary>answer</summary>The demo is done; the demo is an artifact whose value is frozen at
creation. What is not done is the compounding layer: a review UI over `out/queue.jsonl` and steady
call inflow. Without those, every future improvement costs a fresh from-scratch effort. With them,
each call we were already going to run pays into a growing, human-verified preference set. The
trophy is done; the trajectory is the work.</details>

**2. "Why pour effort into a data/review layer instead of just making the product nicer?"**
<details><summary>answer</summary>Cost asymmetry. A nicer product costs the same effort every time we
want it nicer — it does not compound. The data layer costs a fixed bit of plumbing once
(`dpo_export.py` is already scaffolded), then every call improves the asset for free. We proved the
shape: a flat artifact stayed at 10 while a compounding lane crossed 100 in 30 days. Polish is a
flat line; the data layer is the curve.</details>

**3. "Your improvement queue could grow huge fast if you auto-confirm — why gate it on human review?"**
<details><summary>answer</summary>Because un-reviewed volume can be a liability, not an asset (book 12,
why human labels). An auto-confirmed pair can encode the judge's own mistake as "training truth",
teaching the model the wrong lesson faster. That is why every pair ships `needs_human_review=true`
by default. A slow trustworthy export beats a fast poisoned one — bigger is not better when the
data is wrong.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own the whole picture: the compounding layer is **real files** already half-built
(`signals.py`, `judge.py`, `dpo_export.py`, `out/queue.jsonl`), the post-hackathon work is the
**cheap connective tissue** that feeds them, and you have drafted **your own** next three steps,
tagged each as compounding-or-not, and named the weekly habit that prevents the silent flatline.
You can defend, to a beginner, an engineer, and a founder, why the lane — not the demo — is the
thing worth keeping alive.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The one difference between an **artifact** and a **lane** (compounding or not).
2. The six roadmap moves, and **which four** feed the compounding data layer.
3. The five-stage pipe a call flows through (raw → judged → pair → reviewed → DPO row).
4. The trap "a good demo = a product" — and the survival test that replaces it.
5. The **two** silent ways a lane dies, and your one cheap weekly habit that prevents both.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book (and course).
clean_sentence_act_4 = ""   # one-liner for Act 4 (the real files / your roadmap / defending the plan)
my_clean_sentence = ""      # the sentence you would say in a room about turning a demo into a lane

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"A weekend artifact becomes a lane when the data layer keeps compounding."**

The toy proved the shape (flat 10 vs a curve past 100), the roadmap split into four compounding
moves and two one-time features, and the two break-its showed how the lane dies silently if the
inflow stops or the review becomes a rubber stamp. If your sentence captures that in your own
words, this book — and this course — did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "30_post_hackathon_path.ipynb"   # <- this notebook's filename
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
## End of the ladder

**30 done** (pending your teach-back) — and with it, the course. You started at P00 (how to learn),
walked through call logs, timing, judges, calibration, kappa, DPO, the A/B loop, the rubric, the
demo — and you finish here, with the one move that outlasts the weekend: keep the data layer
compounding. There is no book 31. The next thing you build is the lane itself.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "30_post_hackathon_path.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
