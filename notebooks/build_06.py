#!/usr/bin/env python3
# Builds 06_task_success.ipynb — VoiceForge University book 06 (Task success).
# The ONE concept: a required-fields checklist; a call can be polite and still fail the task.
# Rerun: .venv/bin/python notebooks/build_06.py
# Then gate:  .venv/bin/python notebooks/run_nb.py   notebooks/06_task_success.ipynb
#             .venv/bin/python notebooks/audit_nb.py notebooks/06_task_success.ipynb
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
# 06 · Task success

## 1 — Learning contract
By the end of this notebook you will be able to:
1. State the **required-fields checklist** for a booking call (area / time / phone / confirm)
   and explain why it is a *checklist*, not a vibe.
2. Check each field's capture on the recurring cast (**call_A / call_B / call_C**) BY HAND,
   then with a tiny function.
3. Compute two different numbers — **field-capture rate** (how much got captured) and the
   **`task_completed`** bool (did the whole task close) — and say why they are NOT the same.
4. Defend the book's hard truth: **a call can sound great and still not do the job.**

The topic of this book is one boolean. The reason it gets a whole book: that boolean is the
difference between "the agent was pleasant" and "the customer's problem is solved."
'''))
C.append(md('''
## 2 — Knowledge-flow map

`05 the voice stack (ASR -> LLM -> TTS) -> THIS: did the task SUCCEED? -> 07 failure tags`

Book 05 built the *machine* that produces a call: speech in, an LLM brain, speech out.
This book asks the first hard evaluation question about the call that machine produced:
**did it actually accomplish the job?** And book 07 takes the calls that *failed* this check
and gives each failure a **name** (a tag), so we can count which failures happen most.

So the ladder is: **build the agent (05) -> judge if it succeeded (06) -> label why it failed (07).**
You cannot tag a failure (07) until you can detect one (06). That is why this book sits here.
'''))
C.append(md('''
## 3 — Baby intuition

Think of a pizza order over the phone. The call can be *warm* — the agent is polite, the
caller laughs, nobody is rude. And at the end, the kitchen still cannot make the pizza,
because nobody ever said the **address**. Friendly call. No dinner.

"Did the task succeed?" is not "was the call nice?" It is a **checklist** question:
were the specific facts the job needs actually collected? For a service booking those facts
are roughly: *which area, what time, what phone number,* and *did we confirm it back*.
Miss one required fact and the booking cannot be fulfilled — however pleasant the call was.
'''))
C.append(md('''
## 4 — The formal version

We borrow the shape from the project's real schema, **`schemas/task_outcome.md`**. It says,
in plain terms:

- A call has a list of **`required_fields`** — the checklist for THIS kind of call.
- Each field records whether it was **`captured`** (a usable value was obtained) and the
  **`value`** itself.
- **`task_completed`** is a single bool: it is `True` only when *all* required fields are
  captured AND there is no unresolved blocker.

Two terms we will keep separate all book:
- **field-capture rate** — captured fields ÷ required fields (a fraction, like 3/4 = 0.75).
- **`task_completed`** — the all-or-nothing bool. 3 out of 4 is a *good rate* and a *failed task*.

The job a booking call exists to do is binary: the appointment is bookable, or it is not.
'''))
C.append(md('''
## 5 — Why this exists (the business reason, not the academic one)

If you only measured "did the call sound good," you would ship an agent that *charms* people
into hanging up with nothing booked. The required-fields checklist is the deterministic floor
under all the fuzzier judgments later in the course: before we ask an LLM "was the agent
empathetic?" (book 03's judge in the other track), we ask the cheap, checkable question —
**did the four facts get collected?**

Deterministic where possible, says the schema. A checklist you can verify by reading the
transcript beats a vibe you have to argue about. The next acts build that checklist from
nothing, on data small enough to hold in your head.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In one sentence: what is the difference between "the call was nice" and "the task succeeded"?
2. Name the four required fields for a booking call (the checklist).
3. Which schema file in this repo defines `task_completed` and `required_fields`?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you might have measured a call by *tone*. After Act 1 you should hold a sharper
idea: task success is a **checklist of required facts**, scored deterministically, and it is a
different question from "was the call pleasant." This is the detector that book 07 will hang
its failure *tags* on.

If you can say that in your own words, continue. If not, re-read cell 4 (capture vs completed).
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of what "task success" means.
# Producing the sentence is the learning; reading mine would only feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so a skim cannot pass for understanding: the cell nags until you write something.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: build the checklist by hand, on the cast

## Meet the recurring cast (the three calls that travel the whole course)

We do not invent new examples each book. Three calls recur, defined to match the course spec
and the real hero call in `data/hero/turns.json`:

- **call_A** — clean English booking. Cooperative caller, every field captured. outcome: success.
- **call_B** — Hinglish partial. Hesitations and a repeat; one field ends up shaky. outcome: partial.
- **call_C** — Telugu-English failure. Agent interrupts (barge-in), the address stays ambiguous,
  so a required field is never usably captured. outcome: failure.

We meet them first as the SMALLEST thing that carries the lesson: a hand-written note of what
each call did or did not capture. Real nested call logs come later; toy before real.
'''))
C.append(md('''
## PREDICT
Before any code: of call_A, call_B, call_C, which one do you expect to have **`task_completed = True`**?
And do you expect the *failure* call to have captured **zero** fields, or *most but not all*?
Commit to both answers out loud now.
'''))
C.append(code('''
# YOUR TURN - lock your predictions BEFORE the data is on screen, so this notebook records
# YOUR thinking and a later cell can confront it. The gap is the lesson.
my_completed_call = None      # <- "call_A" / "call_B" / "call_C": which one fully completes?
my_failure_captured = None    # <- "zero" or "most": how many fields does the failure call capture?

if my_completed_call is None or my_failure_captured is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("locked:", my_completed_call, "completes;  failure call captured", my_failure_captured, "fields")
'''))
C.append(md('''
## The checklist itself (define it once, name the four fields)

The four required fields for a booking call. We write them as plain strings in a list so the
checklist is a *thing we can point at and loop over*, not knowledge trapped in our heads.
'''))
C.append(code('''
# The required-fields checklist for a booking workflow. Naming it once, in one place, means
# every later cell measures against the SAME four fields - the checklist cannot drift mid-notebook.
REQUIRED_FIELDS = ["service_area", "time_slot", "callback_number", "confirmation"]

# Printing it as the raw object first (course rule: see the input before transforming it).
for field in REQUIRED_FIELDS:        # one print per field so each requirement is visibly its own line
    print("required:", field)
print("checklist length:", len(REQUIRED_FIELDS))
'''))
C.append(md('''
## The cast as raw capture notes (toy data, printed raw)

For each call we hand-write what value (if any) was captured for each field. `None` means the
field was never usably captured. These notes are derived from each call's story — call_A got
everything; call_C's address stayed too vague to use and the agent barged in, so the area is
not a usable value.

This is the RAW input. We print it untouched before computing anything from it.
'''))
C.append(code('''
# Toy capture notes: one dict per call, mapping each required field to the value captured (or None).
# A dict (field -> value) is the smallest honest model of "what did the call collect"; None is the
# explicit, greppable marker for "not captured" (an empty string would hide as a maybe-value).
captures = {
    "call_A": {  # clean English success: every field has a real value
        "service_area":    "Banjara Hills",
        "time_slot":       "tomorrow 4pm",
        "callback_number": "98480 11122",
        "confirmation":    "yes, confirmed back to caller",
    },
    "call_B": {  # Hinglish partial: number came out shaky and was never re-confirmed
        "service_area":    "Andheri West",
        "time_slot":       "Saturday morning",
        "callback_number": None,                 # caller hesitated; a usable number never landed
        "confirmation":    "partial - not read back",
    },
    "call_C": {  # Telugu-English failure: agent barged in, address stayed ambiguous
        "service_area":    None,                  # "Madhapur side... near metro" never resolved to a usable area
        "time_slot":       "tomorrow morning ~10am",
        "callback_number": "98492 55031",
        "confirmation":    "agent confirmed, but on an unusable address",
    },
}
for call_id, fields in captures.items():     # one block per call so each call reads as one THING
    print(call_id, "->", fields)
'''))
C.append(md('''
## How to read these notes (the 3-move ritual for a small structure)

1. Say the **count**: "three calls."
2. Say what **one entry IS**: "one entry = one call's capture note, field -> value-or-None."
3. Read **one single cell** aloud: "call_C's `service_area` is `None` — never captured."

Never read a structure as a wall. Entries are *things*; the inner keys are *facts about the thing*.
'''))
C.append(md('''
## Manual-before-function: check ONE call by hand

Before any helper function, we score capture for a single call the slow, visible way — looking
at each field and asking "is this value usable (not `None`)?" Functions hide the idea; we meet
the idea first.
'''))
C.append(md('''
## PREDICT
For **call_B**, walk the four fields in your head. How many of the four are captured
(value is not `None`)? Write the number in the next cell before running the by-hand check.
'''))
C.append(code('''
# YOUR TURN - predict call_B's captured count BEFORE the by-hand loop prints it.
my_call_B_captured = None     # <- replace None with an integer 0..4

if my_call_B_captured is None:
    print("fill in my_call_B_captured (0..4) above, then re-run.")
else:
    print("locked: I expect", my_call_B_captured, "of 4 fields captured for call_B")
'''))
C.append(code('''
# By hand, fully unrolled: walk call_B field by field and decide captured vs not. Nothing hidden -
# we print each field's verdict so the "is it None?" decision is visible, not buried in a sum().
call_B = captures["call_B"]
captured_count = 0
for field in REQUIRED_FIELDS:                  # iterate the CHECKLIST, not the dict, so a missing
    value = call_B.get(field)                  # field would read as None too (a real failure mode)
    is_captured = value is not None            # the rule for "captured": a usable (non-None) value exists
    print(f"{field:<16} value={value!r:<28} captured={is_captured}")
    if is_captured:
        captured_count += 1                    # tally only the captured ones, one at a time
print("call_B captured", captured_count, "of", len(REQUIRED_FIELDS))

# Confront your prediction (the metal-detector reading: a gap here is exactly what to study).
if my_call_B_captured is not None:
    print("your guess", "MATCHED" if my_call_B_captured == captured_count else "DIFFERED")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, out loud, in this shape:
> "call_B captured ___ of 4 because the ___ field came back `None` (the ___ never landed)."
'''))
C.append(md('''
## Only NOW the function (it does exactly the by-hand thing)

We just did the capture check by hand. The function below is the same loop, given a name so we
can run it on every call without copy-pasting. Meeting the wrapper *after* the idea means the
wrapper is a convenience, not a mystery.
'''))
C.append(code('''
# A tiny function = the by-hand loop with a name. We return BOTH the per-field booleans and the
# count, because a bare number with no per-field detail is exactly the "no evidence" anti-pattern
# the project's scorecard schema forbids (every verdict must point at what it saw).
def capture_report(call_fields):
    # dict comprehension: for each required field, record True/False for "usable value present".
    per_field = {f: (call_fields.get(f) is not None) for f in REQUIRED_FIELDS}
    captured = sum(per_field.values())         # True counts as 1, so summing booleans = how many captured
    return per_field, captured

# Sanity-check the function against the by-hand result we already trust for call_B.
pf_B, cap_B = capture_report(captures["call_B"])
print("per-field:", pf_B)
print("captured count:", cap_B, "(should match the by-hand", captured_count, ")")
'''))
C.append(md('''
## PREDICT
We are about to run `capture_report` on **all three** calls and print captured-of-4 for each.
Predict the three counts now: call_A = ?, call_B = ?, call_C = ?
'''))
C.append(code('''
# YOUR TURN - predict all three captured counts before the table prints.
my_counts = None     # <- replace with a dict like {"call_A": 4, "call_B": 3, "call_C": 3}

if my_counts is None:
    print("fill in my_counts above (a dict of three integers), then re-run.")
else:
    print("locked:", my_counts)
'''))
C.append(code('''
# Run the function across the whole cast and print a small captured-of-4 table.
# We sort by call_id so the row ORDER is stable every run (a table that reshuffles is hard to read
# and hard to diff against your prediction).
print(f"{'call':<8} {'captured/4':>10}   per-field flags")
for call_id in sorted(captures):
    per_field, captured = capture_report(captures[call_id])
    flags = "".join("Y" if v else "-" for v in per_field.values())   # one char per field, in checklist order
    print(f"{call_id:<8} {captured:>7}/4    {flags}   ({', '.join(REQUIRED_FIELDS)})")
'''))
C.append(md('''
## OBSERVE + EXPLAIN
call_C captured 3 of 4 — *more* fields than you might expect for a "failure." The missing one
is `service_area` (the `-` in the flags). Say in one sentence: which single field is missing
for call_C, and why a missing **area** sinks a booking even when time, number, and a confirmation
all exist.
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
Why does `capture_report` iterate over `REQUIRED_FIELDS` rather than over the call's own keys?
(Hint: what happens, and what *should* happen, if a call's note is outright *missing* a field?)
'''))
C.append(md('''
## From counts to the bool: define `task_completed`

A count is not the verdict. The schema's `task_completed` is `True` only when **every** required
field is captured. We build that bool now — and this is where capture-rate and task-success split
apart for good.
'''))
C.append(md('''
## PREDICT
`task_completed` is "all four captured." For which of the three calls is it `True`?
And what is call_C's *field-capture rate* (a fraction) versus its *`task_completed`* (a bool)?
'''))
C.append(code('''
# YOUR TURN - predict the bool for each call before computing it.
my_completed = None     # <- e.g. {"call_A": True, "call_B": False, "call_C": False}

if my_completed is None:
    print("fill in my_completed above (dict of three bools), then re-run.")
else:
    print("locked:", my_completed)
'''))
C.append(code('''
# task_completed: the all-or-nothing bool. We compute it as "captured == required length", i.e.
# nothing missing. We deliberately keep it SEPARATE from the rate so the two numbers can disagree
# in plain sight - that disagreement is the whole point of this book.
def task_completed(call_fields):
    _, captured = capture_report(call_fields)
    return captured == len(REQUIRED_FIELDS)    # True only when ALL four are captured; 3/4 is False

for call_id in sorted(captures):
    _, captured = capture_report(captures[call_id])
    rate = captured / len(REQUIRED_FIELDS)     # field-capture RATE: a fraction in [0,1]
    done = task_completed(captures[call_id])   # task_completed: the BOOL
    print(f"{call_id}:  capture_rate={rate:.2f}   task_completed={done}")
'''))
C.append(md('''
## The split, stated plainly

Look at **call_C**: capture rate **0.75**, task_completed **False**. Seventy-five percent
"done" and the appointment still cannot be booked, because the *area* is missing. A rate is a
**progress bar**; `task_completed` is a **door** — it is shut unless every required field is in.
This is the same shape as the course-wide trap "green cells ≠ correct": a high number can sit
right next to a failed outcome. Hold this; the wrong-intuition trap in Act 3 weaponizes it.
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
State the difference between **field-capture rate** and **`task_completed`** in one sentence
each, and give the call_C numbers for both (the fraction and the bool).
'''))
C.append(md('''
## Reference the real schema (so this is not a toy invention)

Everything above mirrors **`schemas/task_outcome.md`** in this repo. That schema also carries two
fields we have not modeled yet but will name now, because they matter for honesty:
- **`escalation_needed`** — should this call route to a human? (a blocker, even if fields captured)
- **`confidence`** — how sure is the extraction? (judge-assisted extraction gets flagged)

We will keep using `captured` / `task_completed`, but a real outcome record names these too.
'''))
C.append(code('''
# Emit one call's outcome in the shape of schemas/task_outcome.md - so the toy connects visibly
# to the real contract. We build the required_fields array from our capture note, mirroring the
# schema's {name, captured, value} sub-objects exactly (this is what downstream code reads).
def to_task_outcome(call_id, call_fields):
    fields = call_fields                       # alias for readability below
    return {
        "call_id": call_id,
        "task_completed": task_completed(fields),
        "required_fields": [
            {"name": f, "captured": fields.get(f) is not None, "value": fields.get(f)}
            for f in REQUIRED_FIELDS            # checklist order, so two records are comparable
        ],
        "escalation_needed": False,            # toy default; a real extractor would set this
        "confidence": 0.9,                     # toy default; judge-assisted extraction would flag lower
    }

import json   # stdlib; imported here, where we first pretty-print a record
print(json.dumps(to_task_outcome("call_C", captures["call_C"]), indent=2))
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before Act 2: "did it work?" was a single fuzzy feeling. After Act 2 you can: name a
**required-fields checklist**, check capture per field **by hand then by function** on the cast,
and compute **two distinct numbers** — capture *rate* and the *`task_completed`* bool — knowing
exactly why 3-of-4 is a good rate and a failed task. That bool is what book 07 will tag.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (rate-vs-bool, or checklist-not-vibe - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the checklist, then the trap

## Break-it philosophy

A checklist you have never seen *fail* is a checklist you do not understand. We now feed it
broken and adversarial inputs on purpose. Surprise here, at your desk, is education; surprise
on the demo stage is a disaster.
'''))
C.append(md('''
## PREDICT
We give a call an **empty string** `""` for `callback_number` (the agent logged a blank, not
`None`). Our rule is "captured = value is not `None`." Does `""` count as **captured** or **not**?
Will `task_completed` come out wrongly `True`? Commit before running.
'''))
C.append(code('''
# BREAK-IT (guided) - an empty string is the classic "looks captured, is worthless" value.
# This is NOT supposed to crash; it is supposed to be SILENTLY WRONG, which is more dangerous.
blank_number_call = {
    "service_area":    "Kothrud",
    "time_slot":       "Friday 6pm",
    "callback_number": "",                 # <- the damage: blank string, not None and not a real number
    "confirmation":    "yes",
}
per_field, captured = capture_report(blank_number_call)
print("per-field:", per_field)
print("captured:", captured, "  task_completed:", task_completed(blank_number_call))
print("...but the callback_number is an empty string - is this task REALLY completable?")
'''))
C.append(md('''
## Reading the silent failure (no red, all wrong)

No traceback. `captured` came back **4** and `task_completed` came back **True** — because
`"" is not None` is `True`. The agent technically "captured" a callback number that is **blank**.
The checklist passed; the task is **not** completable (you cannot call back an empty string).

This is the dangerous failure: not a crash (Python would tell you) but a **silently wrong**
`True`. A "captured" check that only tests `is not None` trusts the data too much. The fix is to
tighten the rule to "a *usable* value," which we do next.
'''))
C.append(md('''
## The debug + fix ritual (tighten the rule, re-test on the break)

1. **Name the bad rule:** "captured = not None" let `""` through.
2. **Write the better rule:** "captured = a non-empty, stripped string."
3. **Re-test on the exact input that broke it** (the blank-number call), then on the cast,
   to be sure the fix did not *over*-correct and reject real values.
'''))
C.append(code('''
# The fix: "captured" means a usable value, not merely a non-None one. We strip whitespace and
# require something left - so "", " ", and None all read as NOT captured, while real values pass.
def is_usable(value):
    # None has no .strip(); guard it first. Then a blank/whitespace string strips down to "".
    return value is not None and str(value).strip() != ""

def capture_report_v2(call_fields):
    per_field = {f: is_usable(call_fields.get(f)) for f in REQUIRED_FIELDS}
    return per_field, sum(per_field.values())

# Re-test on the EXACT input that broke v1 - the blank-number call should now fail completion.
pf, cap = capture_report_v2(blank_number_call)
print("blank-number call now:", pf, "captured:", cap)
print("task now completable?", cap == len(REQUIRED_FIELDS), "(should be False)")
'''))
C.append(code('''
# Guard against over-correction: the fix must NOT start rejecting the real captured values.
# We re-run v2 across the cast; call_A should still be fully captured (4/4).
for call_id in sorted(captures):
    _, cap = capture_report_v2(captures[call_id])
    print(f"{call_id}: captured {cap}/4 under the tightened rule")
print("call_A still 4/4 => the fix tightened the edge without breaking real values")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
Why is a wrongly-`True` `task_completed` *more* dangerous than a crash? And what one change to
the "captured" rule turned the silent `True` into an honest `False`?
'''))
C.append(md('''
## YOUR break now

Author your own damage. Pick ONE field in `my_break_call` below and set it to a value you think
will fool the checklist (ideas: the string `"none"`, the number `0`, whitespace `"   "`, or a
made-up placeholder). PREDICT in the comment whether v1 and v2 each call it captured, then run.
'''))
C.append(code('''
# YOUR TURN - self-authored BREAK-IT.
# my prediction: <which field I damage, and what v1 vs v2 will say about it, and why>

my_break_call = {
    "service_area":    "Indiranagar",
    "time_slot":       "Sunday noon",
    "callback_number": "90000 12345",
    "confirmation":    "yes",
}

# 1) damage ONE field here (uncomment and edit), e.g. a sneaky placeholder:
# my_break_call["service_area"] = "   "

# 2) compare the loose rule (v1) against the tightened rule (v2) on your damage:
_, cap_v1 = capture_report(my_break_call)        # v1: "not None" - the loose, foolable rule
_, cap_v2 = capture_report_v2(my_break_call)     # v2: "usable" - the tightened rule
print("v1 captured:", cap_v1, "/4   v2 captured:", cap_v2, "/4")
print("if these two disagree, your value fooled the loose rule but not the tight one")
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
Give one value (other than `""`) that a "captured = not None" rule would wrongly accept as a
real field, and say what the tightened `is_usable` rule would do with it. Then: which matters
more for trusting `task_completed` — the *quantity* of fields captured, or their *usability*?
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the heart of this book

**The wrong belief:** "the call sounded great — warm, polite, smooth — so the task succeeded."

The next cell scores a call on two axes: a **politeness signal** (did the agent greet, thank,
stay courteous?) and the **required-fields checklist**. We rig a call that is *maximally polite*
and **misses a required field**. Run it, then explain — before the reveal — why a high politeness
score next to `task_completed = False` is not a contradiction at all.
'''))
C.append(md('''
## PREDICT
The next cell scores `polished_but_failed` on two axes: a **politeness** count and the
**required-fields** checklist. Predict both before running: roughly how high is the politeness
count (0? mid? high?), and what is `task_completed` — `True` or `False`? Commit to both.
'''))
C.append(code('''
# A very polite call that still fails the task. politeness_markers counts courtesy cues; the
# checklist counts captured facts. They measure DIFFERENT things, so they can point opposite ways.
polished_but_failed = {
    "transcript": "Hello! So lovely to hear from you. Thank you so much! Have a wonderful day!",
    "captures": {                              # ...but it never pinned down the area
        "service_area":    None,               # the agent charmed and chatted; no usable area landed
        "time_slot":       "Monday 11am",
        "callback_number": "98765 43210",
        "confirmation":    "yes, absolutely!",
    },
}

# A crude politeness score: count courtesy words. High = sounds great. (Real judges are fancier,
# but the POINT survives: pleasantness and task-completion are separate measurements.)
courtesy_words = ["hello", "please", "thank", "lovely", "wonderful", "absolutely"]
text = polished_but_failed["transcript"].lower()
politeness = sum(text.count(w) for w in courtesy_words)   # count every courtesy cue in the words

_, captured = capture_report_v2(polished_but_failed["captures"])
done = captured == len(REQUIRED_FIELDS)
print("politeness score:", politeness, "(high = sounds great)")
print("captured:", captured, "/4   task_completed:", done)
print("A warm, courteous call -> and the task did NOT complete.")
'''))
C.append(md('''
## The reveal

`politeness` is high. `task_completed` is `False`. **Both are true at once**, and neither
disproves the other — because they measure different things. Politeness scores *manner*; the
checklist scores *outcome*. An agent can be a delight and leave the customer un-helped (no area,
no booking). If you graded only on tone, this call passes; graded on the job, it fails.

This is exactly the course-wide trap ("it ran / it sounded fine ≠ it was correct") in its
book-06 costume. It is also *why book 07 exists*: this failed call needs a **tag** — here it
would be something like `missing_required_field: service_area` — so we can count how often
charm-without-completion happens across many calls.
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why can politeness be high while task_completed is False?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a "captured" check felt safe and a smooth call felt like success. After Act 3: you know
the loose rule (`not None`) lets blanks through as a **silent wrong `True`**, that tightening it
to "usable value" fixes it, and that **politeness and task-completion are orthogonal** — a great-
sounding call can flat-out fail the job. Failed calls are what book 07 will name.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the politeness-vs-completion trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this lives, and how to defend it

## Where this sits in the real VoiceForge pipeline

The toy `task_completed` you built is the seed of a real rubric dimension. In the project:
- **`schemas/task_outcome.md`** defines the exact record shape you mirrored (`required_fields[]`
  with `name` / `captured` / `value`, plus `task_completed`, `escalation_needed`, `confidence`).
- That outcome feeds the **`task_completion`** dimension of the scorecard
  (**`schemas/scorecard.md`**) — and the scorecard's iron rule is *every dimension carries a
  reason and `evidence_turn_ids`*. That is why our function returns per-field detail, never a
  bare number: the reason has to point at *which* field was missing.
- The real hero call lives in **`data/hero/turns.json`** — call_C is its stand-in. There the
  caller says "Madhapur side... near metro" and the agent barges in demanding a full address;
  the area never resolves to a usable value. Same failure you scored here, real timestamps.
'''))
C.append(md('''
## PREDICT (connect to the real call)

Open the story of `data/hero/turns.json` in your mind (call_C): the caller DID give a time
("around ten"), a number (the digits at the end), and the agent DID confirm. Which single
required field is the one that keeps `task_completed` at `False`? Write your answer, then read on.
'''))
C.append(code('''
# YOUR TURN - which field sinks the real hero call? Stored so you commit before the answer.
my_hero_missing_field = ""   # <- one of the four field names

if len(my_hero_missing_field.strip()) < 4:
    print("name the missing field above, then re-run.")
else:
    print("you said the hero call fails on:", my_hero_missing_field)
    # The reveal, kept honest: the area ("Madhapur side, near metro") never became a usable,
    # complete service_area (no pincode/door), so service_area stays uncaptured.
    print("schema's answer: service_area - an ambiguous locality is not a usable value")
'''))
C.append(md('''
## The concept at three levels (say each to its audience)

- **For a beginner:** "We tick a checklist — area, time, phone, confirm. If even one box is
  empty, the booking can't happen, no matter how nice the call was."
- **For an engineer:** "`task_completed` is a deterministic AND over required-field capture,
  where 'captured' means a *usable* value (non-empty, validated), emitted with per-field
  evidence so the scorecard's `task_completion` dimension can cite which field failed."
- **For a founder:** "We measure whether calls actually get the customer's job done — not just
  whether they sound good. That's the number that maps to bookings, refunds avoided, and trust;
  an agent that charms but doesn't complete is a leak we can now see and count."
'''))
C.append(md('''
## Defense questions (×3 — try to answer before opening each)

**1. "Your call_C captured 3 of 4 fields. Isn't 75% basically a success?"**
<details><summary>answer</summary>No — task_completed is a door, not a progress bar. A booking with no usable area cannot be fulfilled; the customer is not 75% helped, they are un-helped. Capture rate is a diagnostic of *how close*; the bool is the *outcome*.</details>

**2. "Why not just have an LLM read the transcript and say success or fail?"**
<details><summary>answer</summary>Because the required-fields checklist is deterministic and verifiable from the transcript — cheaper, reproducible, and auditable. We reserve the LLM judge for genuinely fuzzy dimensions (empathy, repair quality). Determinism where possible; judgment only where necessary.</details>

**3. "How do you stop a blank or junk value from counting as captured?"**
<details><summary>answer</summary>The 'usable value' rule (is_usable): non-None AND non-empty after stripping. Act 3 showed an empty-string callback number passing the loose rule as a silent True; the tightened rule rejects it. Real systems extend this with format validation (e.g., a phone number must have enough digits).</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own: where `task_completed` lives in the real pipeline (`schemas/task_outcome.md`
-> `task_completion` dimension in `schemas/scorecard.md`), why it carries per-field evidence,
which field sinks the real hero call, and how to explain task-success to a beginner, an engineer,
and a founder. Next book takes every call that failed *this* check and gives the failure a name.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The four required fields for a booking call (the checklist).
2. The difference between **field-capture rate** and **`task_completed`** (one sentence each).
3. Why call_C captured 3 of 4 yet `task_completed` is `False` — name the missing field.
4. The silent-failure break: how `""` fooled the loose rule, and the one-line fix.
5. The trap: why a maximally polite call can still have `task_completed = False`.

Missed one? Open it back up, find the act, redo it. That is the system working — not a failure.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (where this lives / three-level explanation)
my_clean_sentence = ""      # the sentence you would say in a room about task success

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"A call can sound great and still not do the job."**

If your sentence captures that — pleasant manner and completed task are different measurements,
and only the checklist tells you if the job got done — this book did its work.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "06_task_success.ipynb"   # <- this notebook's filename
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

**06 done** (pending your teach-back) → **07 · Failure tags** — take every call where
`task_completed` came back `False` and give the failure a *name* (`missing_required_field`,
`barge_in`, `language_mismatch`, …), so we stop saying "it failed" and start counting *how*.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "06_task_success.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
