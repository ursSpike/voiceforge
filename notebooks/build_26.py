#!/usr/bin/env python3
# Builds 26_dashboard_mental_model.ipynb — VoiceForge University book 26.
# The ONE atomic concept: each view exists for a specific PERSON's QUESTION. A dashboard is
# not "screens of data" — it is a set of answers, one per (person, question). The four real
# views — call list / call detail / analytics / improvement queue — map to founder (business
# value) / engineer (inspect the trace) / ML person (the eval/data artifact). We reference the
# real money-shot page web/shot.html (the call-detail view). Same four-act skeleton + markers
# as build_P00.py / build_13.py.
# Rerun:      .venv/bin/python notebooks/build_26.py
# Then gate:  .venv/bin/python notebooks/run_nb.py   notebooks/26_dashboard_mental_model.ipynb
#             .venv/bin/python notebooks/audit_nb.py notebooks/26_dashboard_mental_model.ipynb
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
# 26 · Dashboard mental model

## 1 — Learning contract
By the end of this notebook you will be able to:
1. State the **one rule** that makes a dashboard usable: **every view exists to answer one
   specific PERSON's QUESTION** — not "to show data."
2. Name the **four VoiceForge views** (call list · call detail · analytics · improvement queue)
   and, for each, say *whose question it answers* (founder · engineer · ML person) **in words**.
3. Build, BY HAND, the **same raw call pool** reshaped four different ways — proving a "view" is
   a *filter + shape* chosen by a question, not a new pile of data.
4. Catch the **"more views = better dashboard" trap**, and defend why a view with no owning
   question is worse than no view at all.

The topic looks like UI. It is not. It is the discipline of **knowing who is looking and what
they need to decide** — the same discipline that decides which number goes on a slide (book 06's
room) and which artifact ships to training (book 17's pairs).
'''))
C.append(md('''
## 2 — Knowledge-flow map (where this book sits on the ladder)

`25 · charts (one chart = one claim)  →  THIS · dashboard mental model  →  27 · adapters`

Book 25 taught you to read and build **one chart** so it licenses exactly one claim. But a
product is not one chart — it is a **surface with several views**, and the danger changes shape:
not "this chart over-claims," but "**this whole screen has no owner** — nobody's question lives
here, so everyone scrolls and nobody decides." This book gives you the organizing rule that turns
a pile of charts and tables into a dashboard: **one view, one person, one question.** Book 27 then
takes each of these views and asks how to *feed* it — the **adapters** that reshape raw pipeline
output (`signals.py`, scorecards, `out/queue.jsonl`) into exactly the shape each view needs. No
clear "who is this view for?" here → nothing for an adapter to target there.
'''))
C.append(md('''
## 3 — Baby intuition

Walk into a hospital. There is a **waiting-room board** (which patients are here, how long
they've waited), a **bedside chart** (one patient, every vital, the full timeline), a **whiteboard
in the admin office** (beds free, average wait, staffing for the week), and a **handoff list at
shift change** (these three cases need the next doctor's attention).

Four surfaces. Same patients underneath all of them. Nobody confuses them, because each one was
built around **a specific person with a specific decision**: the receptionist triaging arrivals,
the nurse at one bedside, the administrator planning capacity, the doctor taking over a shift.

A VoiceForge dashboard is that hospital. The **calls** are the patients. The mistake beginners
make is building "a screen that shows everything about the calls" — a wall nobody can act on —
instead of four surfaces, each answering **one person's one question**.
'''))
C.append(md('''
## 4 — The formal version

A **view** is not "a page of the app." A view is:

> **a chosen SHAPE of the underlying data (a filter + a layout) that exists to answer one
> question for one role.**

The unit is the triple **(role, question, view)**:
- **role** — *who is looking*: founder, engineer, ML person. (Same three audiences as the
  three-level explanation every book ends with — that is not a coincidence; it is the same idea.)
- **question** — *the decision they are trying to make*, phrased as a real sentence ending in "?"
- **view** — the filter + shape of the call data that answers exactly that question.

The four VoiceForge views, named once here and earned across Act 2:

| view | the person | their question |
|---|---|---|
| **call list** | founder | "which calls need attention right now, and how many?" |
| **call detail** | engineer | "what exactly went wrong inside THIS one call?" |
| **analytics** | founder | "is the fleet healthy this week — better or worse than last?" |
| **improvement queue** | ML person | "which fixes are ready to become training data?" |

A view that cannot name its (role, question) is not a view. It is decoration.
'''))
C.append(md('''
## 5 — Why this book exists (the business reason)

On demo day a founder shows a screen and someone in the room asks **"so what do I do with this?"**
If the screen was built question-first, the answer is one sentence ("this is the list of calls
that failed today — you act on the red ones"). If it was built data-first — "here is everything we
measured" — the founder fumbles, because a screen with no owning question has **no action attached
to it**, and a number with no decision attached is the exact thing book 06 told you to keep off the
slide.

Concretely, the real artifacts already exist and each one *is* a view waiting to be named:
`data/normalized/*.json` (11 calls) is the **call list**; the money-shot page **`web/shot.html`**
is the **call detail**; `pipeline/signals.py` `analyze()` aggregated across calls is **analytics**;
`out/queue.jsonl` (the preference pairs from book 17) is the **improvement queue**. This book teaches
you to look at each and say, before anything renders, *whose question does this answer?* The next
cell is your first run.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just syntax.

# We print a sentence so you see WHERE output appears (directly under the cell) and so your first
# action is a run you committed to. PREDICT - what exact text appears below?
print("a view that cannot name its person and question is decoration, not a tool")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. Finish the rule: "every view exists to answer one specific person's ___."
2. Name the four VoiceForge views, and for each, name the person whose question it answers.
3. What is the difference between a *view* and "a page that shows data about the calls"?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) pictured a dashboard as *"a screen that shows the data."* After Act 1
you should hold a sharper frame: a dashboard is a set of **views**, and each view is the answer to
**one person's one question** — a triple **(role, question, view)**. The four VoiceForge views map
to three people (founder · engineer · ML person), and a view that cannot name its (person, question)
is decoration that nobody can act on.

If you can say that in your own words, continue. If not, re-read cell 4 (the (role, question, view)
triple and the four-view table).
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of why "show all the data on one
# screen" is the WRONG goal for a dashboard. Producing the sentence is the learning; reading mine
# would only feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so a skim cannot pass for understanding: the cell nags until you write something.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: one raw call pool, reshaped by four different questions

## The toy data, printed RAW

Course rule: see the ugly input before transforming it. The "underlying data" beneath every view
is the **same pool of calls**. We start with the smallest pool that carries the whole lesson —
**three calls**, the recurring cast. Each call is one dict with a few facts a dashboard reads:
who failed, how badly, and whether a fix was authored. We print the raw pool untouched first.
'''))
C.append(code('''
# The shared call pool - three calls, the recurring cast (ids/languages/outcomes fixed by the
# course spec). Each is ONE dict: identity (id/language), a verdict (outcome + overall score), the
# headline failure, and whether an improvement pair was authored from it. EVERY view below is built
# from THIS one list - that is the point: views are reshapes of a single pool, not new data.
calls = [
    {"call_id": "call_A", "language": "English",        "outcome": "success",
     "overall": 0.91, "top_failure": None,            "fix_authored": False},
    {"call_id": "call_B", "language": "Hinglish",       "outcome": "partial",
     "overall": 0.62, "top_failure": "repair_quality", "fix_authored": True},
    {"call_id": "call_C", "language": "Telugu-English", "outcome": "failure",
     "overall": 0.41, "top_failure": "barge_in",       "fix_authored": True},
]

# Print the raw pool first (course habit: see the input before computing any view from it).
for c in calls:                              # one line per call so each row is visibly one THING
    print(c)
print("pool size:", len(calls), "calls")
'''))
C.append(md('''
## How to read this tiny pool (the 3-move ritual for a small structure)

1. Say the **count**: "three calls."
2. Say what **one row IS**: "one row = one call — its id, its outcome, its score, its headline
   failure, and whether someone wrote a fix for it."
3. Read **one single field** aloud: "call_C's `outcome` is `failure` and its `top_failure` is
   `barge_in`."

Never read data as a wall. Rows are *things*; the fields are *facts about the thing*. Every view
in this book is just a **decision about which facts to keep and how to arrange them**.
'''))
C.append(md('''
## The three people, as a tiny table (who is even looking?)

Before we build a single view, name the audience. A view with no person attached has nothing to be
*right or wrong about*. We list the three roles and the question each one walks up to the dashboard
already holding. Read it as: "this person does not want data — they want **this decision made**."
'''))
C.append(code('''
# The three roles, each with the ONE question they arrive holding. We store them as data (not prose)
# so the next cells can literally pair each view to a person/question and check the match - the whole
# lesson is that pairing, so we make it a structure we can compute on rather than a paragraph.
people = [
    {"role": "founder",
     "question": "which calls need attention, and is the fleet healthy week over week?"},
    {"role": "engineer",
     "question": "what exactly went wrong inside THIS one call (which turn, what signal)?"},
    {"role": "ML person",
     "question": "which detected fixes are ready to become training data?"},
]
for p in people:                             # print each person + their decision so the AUDIENCE is concrete
    print(f"{p['role']:<10} asks: {p['question']}")
'''))
C.append(md('''
## PREDICT
We are about to build the **call list** — the founder's "which calls need attention?" view. Before
any code: from the three-call pool, which calls do you expect to appear on a "needs attention" list,
and which gets left off? (Hint: a clean success is not a thing you act on.) Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - predict which call_ids land on a "needs attention" list BEFORE we build it. We store
# your guess so a later cell can confront it; the gap between guess and result is the lesson.
my_attention_list = None    # <- replace None with a list like ["call_B", "call_C"]

# Guard: unfilled (None) prints a nag and never crashes a fresh run.
if my_attention_list is None:
    print("fill in my_attention_list above (a list of call_ids), then re-run.")
else:
    print("locked - I expect these calls need attention:", my_attention_list)
'''))
C.append(md('''
## View 1 — the CALL LIST, built BY HAND (founder: "which calls need attention?")

Manual-before-function. A view is a **filter + a shape**. The call list's *question* is "which
calls need attention?", so its filter is "drop the clean successes" and its shape is "a short,
scannable row per call with just the triage facts." We build it with a plain loop and print the
decision per call, so the filter is *visible*, not hidden inside a library.
'''))
C.append(code('''
# Build the call-list view by hand: keep only calls a founder would ACT on, and shape each kept
# call down to the few triage facts (id, outcome, score). The filter rule IS the question made
# literal: "needs attention" = outcome is not a clean success. We print why each call is kept/dropped
# so the view's logic is on the page, not buried.
call_list_view = []
for c in calls:
    needs_attention = c["outcome"] != "success"        # the founder acts on partials/failures, not clean wins
    decision = "KEEP (needs attention)" if needs_attention else "drop (clean success)"
    print(f"{c['call_id']}: outcome={c['outcome']:<8} -> {decision}")
    if needs_attention:
        # shape: only the triage facts a scannable list needs - not the whole call dict
        call_list_view.append({"call_id": c["call_id"], "outcome": c["outcome"], "overall": c["overall"]})

print("\\nCALL LIST (founder's triage view):")
for row in call_list_view:                              # one compact row per call needing attention
    print(" ", row)
'''))
C.append(code('''
# Confront your prediction (the metal-detector reading: a gap here is exactly what to study). We
# only compare if you filled the guess in - the guard keeps an unfilled notebook clean.
if my_attention_list is not None:
    actual_ids = [row["call_id"] for row in call_list_view]
    matched = sorted(my_attention_list) == sorted(actual_ids)
    print("your attention list", "MATCHED" if matched else "DIFFERED")
    if not matched:
        print("  you:", sorted(my_attention_list), " actual:", sorted(actual_ids))
        print("  the call you added or missed is the one to re-examine")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, out loud, in this shape:
> "The call list drops ___ and keeps ___, shaped down to ___, because the founder's question is
> '___' — and a clean success is not something you act on."
'''))
C.append(md('''
## View 2 — the CALL DETAIL (engineer: "what went wrong inside THIS call?")

Different person, different question, so a **different shape of the same data**. The engineer does
not want a list — they want **one call, fully unrolled**: every turn in time order, every measured
failure pinned to the turns that caused it. That is exactly the real money-shot page
**`web/shot.html`** (you will meet it for real in Act 4). Here we build a tiny by-hand version for
one call to feel the shape: a turn-by-turn trace plus a failure pinned to its evidence turns.
'''))
C.append(md('''
## PREDICT
The call-detail view for call_C will show its turns in time order and mark the failures. Its top
failure is `barge_in` (the agent talked over the caller). Predict: does the engineer's view need
the **other** calls (call_A, call_B) on screen at all? And does it need *more* facts per turn than
the call list keeps per call, or fewer? Commit to both before the next cell.
'''))
C.append(code('''
# YOUR TURN - predict the SHAPE of the detail view before we build it.
detail_needs_other_calls = None   # <- True or False: does this view show calls other than the one in focus?
detail_facts_vs_list = None       # <- "more" or "fewer": facts per turn here vs facts per call in the list

if detail_needs_other_calls is None or detail_facts_vs_list is None:
    print("fill in BOTH (True/False, and 'more'/'fewer') above, then re-run.")
else:
    print("locked: shows other calls =", detail_needs_other_calls,
          "| facts per item:", detail_facts_vs_list, "than the list")
'''))
C.append(code('''
# Build a tiny call-detail view by hand for ONE call: turns in time order + the failure pinned to
# the turns that caused it. This is the SHAPE of web/shot.html in miniature. We sort by start_ms
# because a trace only makes sense in chronological order - out of order, "who interrupted whom"
# is unreadable. One call only: the engineer's question is about THIS call, so the others are noise.
focus_call = {
    "call_id": "call_C", "language": "Telugu-English",
    "turns": [
        {"turn_id": "t1", "speaker": "agent", "start_ms": 0,     "text": "Which area are you calling from?"},
        {"turn_id": "t2", "speaker": "user",  "start_ms": 10947, "text": "haan area ante... Madhapur side anukunta..."},
        {"turn_id": "t3", "speaker": "agent", "start_ms": 18149, "text": "I need your complete address with pincode now."},
    ],
    # one measured failure, pinned to the exact turns that prove it (scorecard discipline: evidence ids)
    "failures": [{"at_ms": 18149, "label": "agent barge-in", "detail": "800ms overlap",
                  "evidence_turn_ids": ["t2", "t3"]}],
}

ordered = sorted(focus_call["turns"], key=lambda t: t["start_ms"])   # chronological or the trace lies
print("CALL DETAIL —", focus_call["call_id"], f"({focus_call['language']})")
for t in ordered:                                                    # one line per turn, in time order
    print(f"  {t['start_ms']:>6}ms  {t['speaker']:<6} {t['turn_id']}: {t['text']}")
for f in focus_call["failures"]:                                     # failures pinned to evidence turns
    print(f"  >> FAILURE @{f['at_ms']}ms: {f['label']} ({f['detail']}) — turns {f['evidence_turn_ids']}")
'''))
C.append(code('''
# Confront the shape prediction. The detail view shows exactly ONE call (no others) and MORE facts
# per item (per-turn text/speaker/timing + evidence ids) than the list's few-facts-per-call. We
# only check if you committed above - the guard keeps an unfilled notebook clean.
if detail_needs_other_calls is not None and detail_facts_vs_list is not None:
    print("shows other calls -> answer is False (the engineer's question is about THIS call only):",
          "correct" if detail_needs_other_calls is False else "re-examine")
    print("facts per item    -> answer is 'more' (per-turn detail beats per-call summary):",
          "correct" if detail_facts_vs_list == "more" else "re-examine")
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
1. The call list and the call detail are built from the **same** call data. Name the two things
   that differ between them (hint: the filter, and the shape/grain).
2. Why does the call-detail view sort turns by `start_ms` — what breaks if it does not?
3. Whose question does each of the two views answer?
'''))
C.append(md('''
## View 3 — ANALYTICS, by hand (founder: "is the fleet healthy this week?")

A third person-question needs a third shape. The founder's *other* question is not about any single
call — it is about **all of them at once**: "are we better or worse than last week?" That demands an
**aggregate**: collapse the whole pool into a few fleet-level numbers. Manual-before-function: we
compute the aggregates by hand from the pool, and (course rule from book 04) we report **p50/p90,
never a bare mean**, because one terrible call can drag a mean and hide a healthy fleet — or hide a
sick one.
'''))
C.append(md('''
## PREDICT
From the three-call pool (scores 0.91, 0.62, 0.41), predict three fleet numbers the analytics view
would show: the **count of calls needing attention**, the **failure rate** (fraction not "success"),
and roughly the **median (p50) overall score**. Commit to all three in the next cell.
'''))
C.append(code('''
# YOUR TURN - predict the three fleet-level aggregates BEFORE we compute them.
my_attention_count = None   # <- integer: how many calls need attention
my_failure_rate = None      # <- fraction 0..1: share of calls whose outcome is not "success"
my_p50_score = None         # <- the median overall score across the three calls

if None in (my_attention_count, my_failure_rate, my_p50_score):
    print("fill in all three aggregates above, then re-run.")
else:
    print("locked: attention", my_attention_count, "| failure rate", my_failure_rate,
          "| p50 score", my_p50_score)
'''))
C.append(code('''
# Build the analytics view by hand: collapse the WHOLE pool into fleet numbers. Each line is one
# aggregate the founder reads at a glance. We use statistics.median (p50) and a hand p90 helper
# rather than mean(), because a single bad call distorts a mean - p50/p90 survive that (book 04).
import statistics   # python's built-in stats module; imported here, where the aggregate first needs it

scores = [c["overall"] for c in calls]                 # the column we summarize: per-call overall scores
attention_count = sum(1 for c in calls if c["outcome"] != "success")   # how many calls a founder must act on
failure_rate = sum(1 for c in calls if c["outcome"] != "success") / len(calls)  # share not clean-success

def p90(xs):                                           # p90 by hand: the value 90% of calls are at or below
    s = sorted(xs)                                     # percentiles need sorted data - unsorted is meaningless
    idx = max(0, round(0.9 * (len(s) - 1)))            # nearest-rank position for the 90th percentile
    return s[idx]

print("ANALYTICS (founder's fleet view):")
print("  calls total:           ", len(calls))
print("  needing attention:     ", attention_count)
print("  failure rate:          ", round(failure_rate, 2))
print("  overall score p50:     ", statistics.median(scores))   # median, NOT mean - resists one outlier
print("  overall score p90-ish: ", p90(scores))
'''))
C.append(code('''
# Confront the aggregate predictions (gap = study target). Guarded so unfilled stays clean.
if None not in (my_attention_count, my_failure_rate, my_p50_score):
    print("attention count:", "match" if my_attention_count == attention_count else "DIFFERED",
          f"(actual {attention_count})")
    print("failure rate:   ", "match" if abs(my_failure_rate - failure_rate) < 0.01 else "DIFFERED",
          f"(actual {round(failure_rate, 2)})")
    print("p50 score:      ", "match" if abs(my_p50_score - statistics.median(scores)) < 0.01 else "DIFFERED",
          f"(actual {statistics.median(scores)})")
'''))
C.append(md('''
## The grain test — the fastest way to tell two views apart

Notice what changed across the three views: the **grain** (what one row/screen IS).

| view | grain — "one ___ " | the person | the question |
|---|---|---|---|
| call list | one **call** (a short row) | founder | which calls need attention? |
| call detail | one **turn** (within one call) | engineer | what went wrong inside THIS call? |
| analytics | one **fleet number** (the whole pool) | founder | is the fleet healthy? |

When two screens feel confusingly similar, ask **"what is one row here?"** Different grain = different
question = legitimately different views. *Same* grain answering *different* questions is a smell — and
same grain, same question, two screens is duplication you should delete.
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. Define **grain** in one phrase ("what one ___ on the screen represents").
2. Give the grain of each of the three views built so far (call / turn / fleet number).
3. Why does analytics report **p50/p90** instead of the mean — and which book taught you that one
   terrible call can hide behind a mean?
'''))
C.append(md('''
## View 4 — the IMPROVEMENT QUEUE (ML person: "which fixes are ready to train on?")

The fourth person enters: the **ML person**, who does not care about today's triage or the fleet
trend. Their question is **"which detected failures have been turned into training data?"** Their
view filters the pool to calls where a **fix was authored** (a chosen/rejected preference pair, book
17), and shapes each into the thing a training run consumes. This is the real **`out/queue.jsonl`**.
Manual-before-function: we build it by hand from the pool's `fix_authored` flag and `top_failure`.
'''))
C.append(md('''
## PREDICT
The improvement queue keeps only calls where `fix_authored` is `True`. From the three-call pool,
predict exactly which call_ids land in the queue — and whether the clean success (call_A) could
ever appear there. Commit before the next cell.
'''))
C.append(code('''
# YOUR TURN - predict which call_ids appear in the improvement queue.
my_queue_ids = None    # <- a list like ["call_B", "call_C"]

if my_queue_ids is None:
    print("fill in my_queue_ids above (a list of call_ids), then re-run.")
else:
    print("locked - I expect the queue holds:", my_queue_ids)
'''))
C.append(code('''
# Build the improvement-queue view by hand: keep only calls that produced an authored fix, and shape
# each into a training-ready record (which call, which failure axis, and the needs-human-review flag
# from the improvement_example schema). The filter IS the ML person's question made literal:
# "ready to train on" = a fix was authored. A clean success has no failure to fix, so it can never appear.
queue_view = []
for c in calls:
    if c["fix_authored"]:                              # only calls a fix was actually written from
        queue_view.append({
            "call_id": c["call_id"],
            "failure_dimension": c["top_failure"],     # which axis the pair corrects (book 17 discipline)
            "needs_human_review": True,                # true until a human eyeballs the pair (schema default)
        })
    else:
        print(f"{c['call_id']}: no fix authored -> not in queue")

print("\\nIMPROVEMENT QUEUE (ML person's training view):")
for row in queue_view:                                 # one record per authored fix, ready for export
    print(" ", row)
'''))
C.append(code('''
# Confront the queue prediction. Guarded so unfilled stays clean.
if my_queue_ids is not None:
    actual = [row["call_id"] for row in queue_view]
    print("your queue ids", "MATCHED" if sorted(my_queue_ids) == sorted(actual) else "DIFFERED",
          f"(actual {sorted(actual)})")
'''))
C.append(md('''
## The whole dashboard in one frame — same pool, four questions

Everything above came from the **single `calls` pool**. Lay the four views side by side and the
mental model is complete: a dashboard is **one pile of call data, sliced four ways, one slice per
(person, question).**
'''))
C.append(code('''
# Pair each view to its (person, question) and print the four-row map. We build this as data so the
# pairing is explicit and checkable - the ENTIRE book is this table, so we make the table real rather
# than describing it in prose. 'grain' = what one row of that view is (the grain test from Act 2).
dashboard = [
    {"view": "call list",         "person": "founder",   "grain": "one call",
     "question": "which calls need attention right now?"},
    {"view": "call detail",       "person": "engineer",  "grain": "one turn",
     "question": "what went wrong inside THIS call?"},
    {"view": "analytics",         "person": "founder",   "grain": "one fleet number",
     "question": "is the fleet healthy this week?"},
    {"view": "improvement queue", "person": "ML person", "grain": "one training pair",
     "question": "which fixes are ready to train on?"},
]
print(f"{'view':<18}{'person':<11}{'grain':<18}question")
print("-" * 78)
for v in dashboard:
    print(f"{v['view']:<18}{v['person']:<11}{v['grain']:<18}{v['question']}")
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before Act 2: a dashboard was screens, and views were vaguely "different pages." After Act 2 you
built **all four views by hand from one call pool** and can name, for each, its **filter**, its
**shape/grain**, and the **(person, question)** it answers. You have the **grain test** ("what is
one row?") to tell views apart, and you saw that analytics reports **p50/p90, not mean**. The four
views are one pile of data sliced four ways — exactly the four real surfaces book 27 will learn to
*feed*.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (the grain test, or "one pool sliced four ways" - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the dashboard, then the trap that names this book

## Break-it philosophy

A design rule you have never seen *fail* is a rule you do not own. We now build broken dashboards on
purpose — a view with no owning question, a view answering the wrong person — and watch what goes
wrong. Surprise here, at your desk, is education; surprise on the demo stage — a founder staring at a
screen they cannot act on while the room waits — is a disaster.
'''))
C.append(md('''
## PREDICT
First break: the **"kitchen sink" view** — one screen that dumps *every* field of *every* call,
unfiltered and unshaped, "so nothing is hidden." Predict: when the founder asks their actual
question ("which calls need attention?"), will this everything-screen answer it **faster** or
**slower** than the focused 2-row call list? Commit to one.
'''))
C.append(code('''
# BREAK-IT (guided) - the "kitchen sink" view: dump every field of every call onto one screen,
# unfiltered. This does NOT crash; it is supposed to be USELESS while looking thorough - which is
# more dangerous than a crash, because it ships. We render it, then measure how hard the founder's
# question is to answer FROM it.
print("KITCHEN-SINK VIEW (every field, every call, no filter, no shape):")
for c in calls:
    print(" ", c)   # the whole dict, nothing dropped, nothing arranged - "nothing hidden" = nothing usable

# Now try to answer the founder's question off this screen. It is not impossible - it is just work
# the VIEW should have done: the human has to scan all fields of all rows and filter in their head.
needing = [c["call_id"] for c in calls if c["outcome"] != "success"]
print("\\nfounder's question ('which need attention?') answered DESPITE the view:", needing)
print("the screen showed everything and pointed at nothing - the founder did the filtering by eye")
'''))
C.append(md('''
## Reading the lie (no crash, all burden)

No traceback. The kitchen-sink view *rendered fine* and *contained the answer* — and was still a bad
view, because it **pushed the work the view should do back onto the person**. "Show everything so
nothing is hidden" sounds responsible and is actually an abdication: a view's whole job is to
**filter and shape toward one question**, and a screen that refuses to choose forces every viewer to
choose, every time. More fields did not make it more useful — it made it *slower*. (This is the
opposite failure from book 25's over-claiming chart: there a view said *too much*; here a view
*decided too little*.)
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
The kitchen-sink view contained the answer yet was a worse view than the 2-row list. Explain in one
breath *why* "show everything" is a failure, using the words **filter**, **shape**, and **who does
the work**.
'''))
C.append(md('''
## A second break: the right data, the WRONG person's question

The subtler failure: a view that is well-shaped — but aimed at the wrong person. We take the
**analytics** view (fleet aggregates) and hand it to the **engineer** who is mid-incident, debugging
**one specific call**. The data is real and clean. It still fails, because it answers a question this
person is not asking right now.
'''))
C.append(md('''
## PREDICT
The engineer is debugging call_C and needs to know which **turn** the barge-in happened on. You hand
them the analytics view: "failure rate 0.67, p50 score 0.62." Predict: can the engineer locate the
offending turn from that? What single fact do they need that the fleet view structurally cannot
contain? Commit before running.
'''))
C.append(code('''
# BREAK-IT (guided) - hand the analytics (fleet) view to an engineer who needs ONE call's detail.
# Not a crash; a mismatch of (view) to (person, question). We show what the fleet view can offer and
# then the fact the engineer actually needs - which lives at a grain (one turn) the fleet view threw away.
fleet_view = {"failure_rate": 0.67, "p50_score": 0.62, "calls_needing_attention": 2}
print("ANALYTICS view handed to the engineer:", fleet_view)

# The engineer's real need: which TURN in call_C carries the barge-in. The fleet view aggregated the
# whole pool, so per-turn evidence was collapsed away - it CANNOT answer this, at any zoom level.
engineer_need = "which turn_id in call_C is the barge-in, and its overlap ms"
has_it = "turn" in str(fleet_view)          # the fleet view holds no turn-grain facts at all
print("engineer needs:", engineer_need)
print("can the fleet view answer it?", "yes" if has_it else "NO - wrong grain, wrong person, wrong view")
print("the data is correct and useless here: right answer to a question this person is not asking")
'''))
C.append(md('''
## The two failure shapes, stated plainly

You have now seen the two ways a dashboard betrays its user, and neither is a crash:
- **No owning question** (kitchen sink) → the view shows everything and decides nothing; the person
  does the filtering the view should have done.
- **Wrong person's question** (fleet view to the mid-incident engineer) → the view is clean and
  correct, at the **wrong grain**, so it cannot contain the fact this person needs.

Both pass "it renders." Both fail "someone can act on it." That gap — renders vs. answerable — is the
Act-3 trap of this whole course (book P00): green is not understanding, and *rendered* is not
*useful*. The fix for both is the same single discipline: **start from (person, question), then
choose the filter and grain that answer it.**
'''))
C.append(md('''
## YOUR break now

Author your own broken view. Pick ONE of the four views and **mis-aim** it on purpose: hand it to
the wrong person, OR strip its filter so it answers nothing, OR change its grain so it no longer fits
its question. PREDICT in the comment exactly who it now fails and why, then build the mismatch and
print it.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it. Mis-aim ONE view and show the mismatch. Predict the failure first.
# my prediction: <write here: which view, which person it now fails, and WHY (wrong grain? no filter?)>

# Default below is the CORRECT pairing (improvement queue -> ML person) so an UNFILLED notebook runs
# clean. Edit `served_to` to the WRONG person, or change `served_grain`, to inject your mismatch.
view_name = "improvement queue"
correct_person = "ML person"
served_to = "ML person"          # <- change to "founder" or "engineer" to mis-aim the view
served_grain = "one training pair"  # <- or change the grain to break the fit

mismatch = (served_to != correct_person)
print(f"view '{view_name}' (grain: {served_grain}) is being served to: {served_to}")
if mismatch:
    print(f"MISMATCH: this view answers the {correct_person}'s question, not the {served_to}'s -",
          "the data is real but it does not answer what THIS person came to decide")
else:
    print("correctly aimed - now edit `served_to` above to a different role and re-run to see it fail")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this whole book is built on

**The wrong belief:** "**more views = a better, more complete dashboard**" (and its cousin, "the
analytics page is the *important* one — that's the real dashboard").

The next cell pits two dashboards against the same three real questions. Dashboard **MAX** has
**six** views — the four good ones plus two extra "complete-looking" screens (a raw event firehose,
a giant combined mega-table). Dashboard **LEAN** has **exactly the four**, each tied to a person's
question. Run it, then — *before the reveal* — decide which dashboard lets each person answer their
question faster, and whether the two extra views helped at all.
'''))
C.append(md('''
## PREDICT
Three people walk up with three questions (founder: which calls need attention; engineer: which turn
broke in call_C; ML person: which fixes are queued). Dashboard MAX has 6 views, LEAN has 4. Predict:
how many of the three questions does each dashboard answer, and do MAX's two extra views raise that
count or just add scrolling? Commit to both.
'''))
C.append(code('''
# The trap, made measurable. We define each dashboard as the set of (person, question) pairs its
# views actually ANSWER - because a view's worth is "whose question does it answer?", not "does it
# exist?". The two extra MAX views answer NOBODY's stated question (they are "complete-looking"), so
# they add zero answers and only cost attention. We score each dashboard by questions-answered.
asked = [("founder", "needs-attention"), ("engineer", "turn-in-call_C"), ("ML person", "queued-fixes")]

# LEAN: four views, each answering exactly one real question.
lean_answers = {("founder", "needs-attention"), ("engineer", "turn-in-call_C"),
                ("founder", "fleet-health"), ("ML person", "queued-fixes")}
# MAX: the same four PLUS two extra views that answer no one's stated question (firehose, mega-table).
max_answers = lean_answers | {("nobody", "raw-event-firehose"), ("nobody", "combined-mega-table")}

lean_score = sum(1 for q in asked if q in lean_answers)     # how many of the 3 questions LEAN answers
max_score = sum(1 for q in asked if q in max_answers)       # how many MAX answers - the extras don't help
print("questions asked:", len(asked))
print("LEAN: views =", len(lean_answers), "| questions answered =", lean_score)
print("MAX : views =", len(max_answers), "| questions answered =", max_score)
print("extra views in MAX:", len(max_answers) - len(lean_answers),
      "| extra questions they answered:", max_score - lean_score)
'''))
C.append(md('''
## The reveal

Both dashboards answer **all three** questions. MAX has **two more views** and answered **zero more
questions** — the firehose and the mega-table belong to **nobody**: no person walked up holding the
question they answer. They did not add capability; they added **surface to scroll and screens to
maintain**, and they made the founder's eyes work harder to find the one list that matters. "More
views = more complete" is false: **a view earns its place only by owning a (person, question)** — an
unowned view is pure cost.

And the cousin belief — "the analytics page is *the* dashboard" — falls the same way: analytics is
**one** view answering **one** of the founder's two questions. It is not more important than the call
list; it answers a *different* question. Privileging it is just losing the rule again. (This is the
book P00 trap in product form: a screen that *renders* — even impressively — proves nothing about
whether anyone can *act* on it.)
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why does adding views WITHOUT a person/question make a dashboard worse?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
MAX had six views and LEAN had four, and they answered the same questions. State the rule that makes
the two extra views *cost without benefit*. Then: why is "the analytics page is the important one" a
restatement of the same mistake?
'''))
C.append(md('''
## A third break: the view whose data source is empty (the honest crash)

One more failure mode — a *crash* this time, the friendly kind. A view assumes its data exists. If
the improvement queue is built before anyone has authored a single fix, the source is **empty**, and
code that grabs "the first queued pair" to preview has nothing to grab. We show the raw indexing with
no guard, so you respect why real view code must handle the empty state.
'''))
C.append(code('''
# BREAK-IT (guided) - SUPPOSED to error: preview "the first item" of an EMPTY improvement queue.
# Before any fix is authored, the queue is []. Indexing [0] into an empty list raises IndexError -
# Python refusing to invent a row, which is the FRIENDLY failure (a visible crash beats a blank panel
# that silently implies "no failures exist, all is well" - a lie a founder would believe).
empty_queue = []                              # the queue on day zero: nobody has authored a fix yet
first_pair = empty_queue[0]                   # grab the first record to render a preview -> IndexError
print("preview:", first_pair)                 # we never reach here - the index raises first
'''))
C.append(md('''
## Reading the crash, and why the empty state is a real view state

`IndexError` is the code being honest: there is **no first pair**, and a crash says so out loud. The
dangerous alternative is a view that, given no data, renders a serene blank panel — which a founder
reads as *"no failures, everything is healthy,"* the exact opposite of *"the pipeline hasn't run
yet."* Every real view has an **empty state** that must be designed, not defaulted: the call list
when no calls failed, analytics before the first run, the queue before the first fix. A blank that
*means* "all clear" and a blank that *means* "no data yet" must never look the same. (A guard like
`if not queue: show("no fixes queued yet — run the pipeline")` turns the crash into an honest
message.)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: more views felt like a more complete product, and "it renders" felt like done. After Act 3
you know the two silent betrayals (a view with **no owning question** dumps work on the person; a
**well-shaped view at the wrong person/grain** is correct and useless), the **trap** that extra views
without a (person, question) are pure cost — *renders ≠ answerable* — and that every view needs a
designed **empty state** so a blank never lies "all clear" when it means "no data yet."
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the "more views without a question = cost" trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the four REAL views, and how to defend the dashboard

## Where the four views live in the real VoiceForge repo

The toy pool was the lesson; here are the real surfaces, each already a view answering one person:

- **Call list → `data/normalized/*.json`** (11 real calls: the hero + 10 SpokenWOZ). Filter to the
  ones needing attention, shape to a scannable row. *Founder: "which calls need attention?"*
- **Call detail → `web/shot.html`** (the money-shot page). It loads `data/hero/turns.json` and the
  computed `signals.json`, renders the **turns as chat bubbles in time order**, a **failure table**
  with evidence turn ids, and a **clickable transport** — click a red failure tick and the audio
  seeks to that moment. That is the engineer's view, exactly: one call, every turn, every failure
  pinned to the turns that caused it. *Engineer: "what went wrong inside THIS call?"*
- **Analytics → `pipeline/signals.py` `analyze()`** aggregated across the pool: median/p90 latency,
  barge-in counts, laggy counts — fleet numbers, p50/p90 not mean. *Founder: "is the fleet healthy?"*
- **Improvement queue → `out/queue.jsonl`** (the chosen/rejected pairs from book 17, schema in
  `schemas/improvement_example.md`, exported by `pipeline/dpo_export.py`). *ML person: "which fixes
  are ready to train on?"*
'''))
C.append(md('''
## The money-shot page, read as a view (web/shot.html)

Open `web/shot.html` and read it with the frame from this book. Its **person** is the engineer (and
the founder-in-demo standing behind them); its **question** is "what exactly went wrong inside this
one call, and can I hear it?"; its **grain** is one turn. Every element on that page is filter+shape
toward that question: the failure table is `analyze()`'s failures shaped into clickable rows; each
red tick on the transport is one failure pinned to its `at_ms`; clicking a bubble seeks the audio to
that turn. Nothing on the page exists that does not serve the engineer's one question — which is
precisely what makes it a *view* and not a kitchen sink. Book 27 is about the **adapter** that turns
`turns.json` + `signals.json` into the exact shape this page consumes.
'''))
C.append(md('''
## PREDICT (connect to the real artifacts)

A founder, mid-demo, wants to answer **"is the agent getting better since we shipped the fix?"** Of
the four real views — call list, call detail (`web/shot.html`), analytics, improvement queue — which
one answers *that* question? And which view would the **ML person** open instead to check the fix
that caused the improvement? Write both, then read on.
'''))
C.append(code('''
# YOUR TURN - map each question to the real view that answers it.
my_better_view = ""   # <- which view answers the founder's "is it getting better week over week?"
my_mlperson_view = "" # <- which view does the ML person open to inspect the fix itself?

if len(my_better_view.strip()) < 4 or len(my_mlperson_view.strip()) < 4:
    print("name BOTH views above, then re-run.")
else:
    print("you said better-over-time ->", my_better_view, "| fix inspection ->", my_mlperson_view)
    # The reveal: "getting better week over week" is a fleet trend -> the ANALYTICS view (aggregates
    # over time). Inspecting the fix that drove it -> the IMPROVEMENT QUEUE (the chosen/rejected pair).
    print("worked answer: analytics answers 'getting better' (fleet trend over time);")
    print("the improvement queue holds the actual fix (chosen/rejected pair) the ML person inspects.")
'''))
C.append(md('''
## The concept at three levels (say each to its audience)

- **For a beginner:** "A dashboard isn't one screen that shows everything. It's a few screens, and
  each one is built to answer **one person's one question** — like different boards around a hospital
  for the receptionist, the nurse, and the administrator."
- **For an engineer:** "Each view is a **filter + a shape (a grain)** over the same call pool,
  selected by a **(role, question)**. Call list = per-call, founder triage; call detail
  (`web/shot.html`) = per-turn, engineer debug; analytics = per-fleet aggregate (p50/p90); queue =
  per-pair, ML export. The grain test (`what is one row?`) tells two views apart; an unowned view is
  dead weight."
- **For a founder:** "Every screen we show maps to a decision someone in the room is trying to make.
  We don't ship 'all the data on one page' — we ship the **call list** (what needs attention), the
  **call detail** (proof of what went wrong, with audio), the **analytics** (are we improving), and
  the **improvement queue** (what's becoming training data). Four screens, four questions, zero
  decoration."
'''))
C.append(md('''
## Defense questions (×3 — try to answer before opening each)

**1. "Why not just put all the data on one powerful screen — isn't that more transparent?"**
<details><summary>answer</summary>Because a screen that shows everything decides nothing — it pushes the filtering the view should do back onto every viewer, every time. "Transparent" becomes "unactionable." We split into four views because each answers one person's one question (founder triage, engineer debug, founder trend, ML export); transparency is having the right view per decision, not one wall of fields.</details>

**2. "You have a slick analytics page — isn't that the dashboard? Why all the others?"**
<details><summary>answer</summary>Analytics answers exactly one of the founder's two questions ("is the fleet healthy over time?"). It cannot tell you *which* call to act on now (that's the call list), or *what* went wrong inside one call (that's call detail / web/shot.html), or which fix is queued for training (that's the improvement queue). No single view is "the" dashboard; each owns a different (person, question), and dropping any one leaves a real decision unanswered.</details>

**3. "How do you decide whether a proposed new view should exist?"**
<details><summary>answer</summary>It must name a (role, question) that no existing view already owns. If I can't say "this is for [person] to decide [question]" in one sentence, or another view already answers it, the view is decoration and adds only scroll and maintenance. I'd also check its grain (what is one row?) — same grain answering the same question as an existing view is duplication to delete, not a new view to ship.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own: the **four real views** and where they live (`data/normalized/*.json`,
`web/shot.html`, `signals.py` `analyze()`, `out/queue.jsonl`), the **(person, question)** each one
answers, how to read the money-shot page as a view, and how to defend "four focused views, not one
kitchen sink" to a beginner, an engineer, and a founder. Next book takes each view and builds the
**adapter** that reshapes raw pipeline output into exactly the shape that view consumes.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The one rule: every view exists to answer one specific person's ___.
2. Name the four views and the (person, question) each answers — founder, engineer, ML person.
3. The **grain test**: what it is, and the grain of each of the four views.
4. The trap: why "more views = better dashboard" is false — what makes a view earn its place.
5. One real artifact behind each view (`data/normalized/*.json`, `web/shot.html`, `signals.py`
   `analyze()`, `out/queue.jsonl`).

Missed one? Open it back up, find the act, redo it. That is the system working — not a failure.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (the four real views / three-level explanation)
my_clean_sentence = ""      # the sentence you would say in a room about how a dashboard is organized

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Every view exists for a specific person's question."**

If your sentence captures that — a dashboard is not screens of data but a set of answers, one per
(person, question), and a view that cannot name its person and question is decoration — this book did
its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "26_dashboard_mental_model.ipynb"   # <- this notebook's filename
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

**26 done** (pending your teach-back) → **27 · adapters** — you can now name the four views and the
(person, question) each answers. But a view needs to be *fed*: raw pipeline output
(`signals.py` failures, scorecards, `out/queue.jsonl`) is not yet in the shape any of these views
renders. An **adapter** is the thin layer that reshapes one into the other — and now that you know
*what each view is for*, you know exactly *what each adapter must produce*.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "26_dashboard_mental_model.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
