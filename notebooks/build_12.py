#!/usr/bin/env python3
# Builds 12_calibration_why_human_labels.ipynb — VoiceForge University book 12.
# The ONE atomic concept: a judge scoring its OWN pipeline is circular reasoning; a BLIND human
# label (committed BEFORE seeing the judge) is the only thing that breaks the circle. Same four-act
# skeleton + markers as build_P00.py / build_11.py. Rerun: .venv/bin/python notebooks/build_12.py
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
# 12 · Calibration: why human labels

## 1 — Learning contract
By the end of this notebook you will be able to:
1. State the **circularity problem**: a judge that scores its own pipeline is grading its own
   homework — the agreement looks high because both numbers came from the same source
2. Run the **blind protocol**: a human commits a label BEFORE seeing the judge's score, so the
   human label cannot be contaminated by it
3. Lay **10 toy human labels** next to **10 judge labels** and read raw agreement by hand
4. See why a single agreement *percentage* is not yet enough — and what book 13 adds to fix it
5. Defend the rule **calibration needs a label the judge did not produce**

Topic stays small on purpose: ten calls, a yes/no label each. The *independence* is the point.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits on the ladder)

`11 · evidence-based scoring  ->  THIS · calibration: why human labels  ->  13 · confusion matrix`

Book 11 made every score carry a **reason** and **evidence_turn_ids** — auditable, but still the
*judge's own word*. The natural next question a skeptic asks is: *"is the judge any good?"* You
cannot answer that with more judge output — that is the judge vouching for itself. This book
introduces the one thing that can answer it: a **human label produced independently of the
judge**. Book 13 then takes the human labels and judge labels you align here and cross-tabulates
them into a **confusion matrix** (where exactly do they agree and disagree?). No independent
human label here -> nothing to put in that matrix there.
'''))
C.append(md('''
## 3 — Baby intuition

You write your own multiple-choice exam, you take it, and you grade it against your own answer
key. You score 100%. Did you prove you know the material? No — you proved your answers match your
answers. The grade is real arithmetic and completely worthless, because the thing being measured
and the thing measuring it are the **same source**. That loop is called **circular reasoning**.

Now a second person who has never seen your answer key grades your exam blind. Suddenly the score
*means* something: it is a comparison between two **independent** opinions. If you and they agree,
that agreement is evidence. The whole job of calibration is to get that independent second opinion
— and to get it *blind*, so it was not quietly copied from the first.
'''))
C.append(md('''
## 4 — The formal version

**Calibration** = checking a judge's labels against a trusted independent reference, on the same
items, to estimate how much you can trust the judge going forward.

The reference here is **human labels** — a person reads each call and assigns the same label the
judge does (e.g. "did the agent handle the partial answer well: yes/no"). Two hard rules make
those labels usable:

| rule | plain meaning | why it matters |
|---|---|---|
| **independent source** | the human is not the judge, and not the judge's prompt | same-source agreement proves nothing |
| **blind** | the human labels BEFORE seeing the judge's score | seeing the judge's answer first anchors the human to it |

When both hold, lining the two label columns up and counting matches becomes **evidence**. When
either breaks, the agreement number is theater.
'''))
C.append(md('''
## 5 — Why this book exists (a judge that grades itself can't be trusted)

VoiceForge's pitch is that its evals are trustworthy. A founder will ask: *"your AI judge scored
these calls — how do you know the judge is right?"* If the answer is "we asked the judge to
double-check," that is the self-graded exam. The only honest answer is: **"we had humans label a
sample of calls blind, and the judge agreed with them N% of the time."**

That is what calibration produces, and it is why the loop must be broken with an outside label.
`pipeline/judge.py` produces the judge's `{score, reason, evidence_turn_ids}` (book 11). This book
adds the *other* column — a human label collected independently — and lays the two side by side.
Book 13 turns that alignment into a confusion matrix; later books turn it into a single agreement
number (Cohen's kappa) that survives chance. The next cell is your first run.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just syntax.

# We print one sentence so you can see WHERE output appears (directly under the cell) and so your
# first action is a run you committed to. PREDICT - what exact text shows below?
print("a judge that grades its own work proves nothing but self-agreement")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What is the **circularity problem** in one sentence — why does a judge checking its own scores
   prove nothing?
2. What are the **two rules** a human label must satisfy to break the circle?
3. Why is "we asked the judge to double-check its own answer" not an acceptable reply to
   "how do you know the judge is right?"
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: the judge outputs a score, and a good score means a good
call. After Act 1 you should hold: a score is only the *judge's opinion*, and you cannot validate
an opinion with more of the same opinion. Validation requires an **independent, blind** second
label — a human's — laid next to the judge's. That independence is the entire subject of this
book; the agreement number is downstream of it.

If that feels solid in your own words, continue. If not, re-read cell 3 (the self-graded exam).
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of the circularity problem. Not mine - yours.
# Producing the sentence is the learning; reading mine would only feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: build the circle, then break it with a blind label

## What "the judge scores its own pipeline" looks like

Course rule: see the ugly thing before you fix it. We start by *building the circle on purpose* on
the real hero call, so you feel why it is empty before we break it. We load the call first, RAW.
'''))
C.append(code('''
# The hero call is the recurring cast member call_C (Telugu-English service booking). We load its
# turns from the real repo file so any turn id we cite is REAL and you can look it up.
import json
from pathlib import Path

# Resolve the path whether the notebook runs from repo root or notebooks/ - the file on disk is the
# single source of truth for the turns, so we must read the actual one, not invent turns.
here = Path.cwd()
candidates = [here / "data/hero/turns.json", here.parent / "data/hero/turns.json",
              *[p / "data/hero/turns.json" for p in here.parents]]
turns_path = next(p for p in candidates if p.exists())
call = json.loads(turns_path.read_text())

print("call_id:", call["call_id"], "| language:", call["language"], "| turns:", len(call["turns"]))
'''))
C.append(code('''
# We print the turns that matter for our label RAW - the partial answer and the agent's reply -
# because a label like "handled the partial badly" is meaningless unless you can see those turns.
by_id = {t["turn_id"]: t for t in call["turns"]}   # id -> turn, so "t3" resolves to its text
for tid in ("t2", "t3"):
    t = by_id[tid]
    print(t["turn_id"], "|", t["speaker"], "|", t["text"])
'''))
C.append(md('''
## The label we will calibrate

For the whole book we use ONE simple binary label per call, so the mechanics stay visible:

> **handled_partial** — when the caller gives a partial/ambiguous answer, did the agent handle it
> well? `1` = yes (acknowledged + one targeted follow-up), `0` = no (ignored / over-demanded).

It is the same idea as the `repair_quality` dimension from book 11, collapsed to yes/no so we can
count agreement by hand. On the hero call, the user is partial at t2; the agent's t3 is the moment
this label judges.
'''))
C.append(md('''
## PREDICT
Read t2 and t3 above. Before the next cell:
1. What is **your** `handled_partial` label for the hero call — `1` or `0`?
2. Now imagine the judge labels it too, and then we "check" the judge by asking the judge again.
   What agreement do you expect between the judge and itself — and does that number mean anything?
Commit out loud before running.
'''))
C.append(code('''
# YOUR TURN - commit your own human label for the hero call BEFORE we look at any judge output.
# Committing first is the WHOLE lesson: a label written after seeing the judge is contaminated.
my_hero_label = None   # <- replace None with 1 (handled well) or 0 (handled badly)

if my_hero_label is None:
    print("set my_hero_label to 1 or 0 (your read of t3), then re-run.")
else:
    print("your blind human label locked:", my_hero_label)
'''))
C.append(code('''
# Now the CIRCLE, built on purpose. Pretend the judge labeled the hero call, then we "validate" it
# by comparing the judge's label to... the judge's label. We literally compare a value to itself.
judge_label = 0   # the judge's handled_partial call for the hero call (t3 over-demands -> 0)

# This "agreement" asks whether the judge agrees with the judge. It is 100% by construction.
self_agreement = (judge_label == judge_label)
print("judge label:", judge_label)
print("does the judge agree with itself?", self_agreement, "(100% - and it tells us nothing)")
'''))
C.append(md('''
## OBSERVE — why that 100% is empty

The cell printed `True`. The judge agrees with the judge, perfectly, always. We could run a
thousand calls and get 100% every time. **That number is real arithmetic and zero evidence**,
because the label being checked and the label doing the checking are the *same value*. This is the
self-graded exam, in code. The fix is not a cleverer comparison — it is a *different source* on
one side of the `==`.
'''))
C.append(md('''
## Break the circle: the blind protocol, by hand

The blind protocol has three ordered moves. Order is the whole point:
1. The human reads the call and **commits** a label — with the judge's score **hidden**.
2. Only then is the judge's score **revealed**.
3. The two **independent** labels are compared.

You already did move 1 (`my_hero_label`, committed before you saw `judge_label`). Now we do moves
2 and 3 honestly — the human label and the judge label came from two different sources, so the
comparison is finally meaningful.
'''))
C.append(code('''
# Move 3 of the blind protocol: compare the INDEPENDENT human label to the judge label.
# This == means something the self-comparison did not, because the two sides have different origins.
if my_hero_label is not None:                       # guard: only compare once the learner committed
    agree = (my_hero_label == judge_label)
    print("blind human label:", my_hero_label, "| judge label:", judge_label)
    print("do they agree?", agree)
    # Whether you agreed or not, THIS comparison is evidence and the self-comparison was not -
    # the only thing that changed is that one side now comes from a source the judge did not control.
else:
    print("commit my_hero_label two cells up first, then re-run this cell.")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not from memory): why does comparing your label to the
judge's mean something, while comparing the judge's label to itself meant nothing — even though
both are just `==`?
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
Recite the three ordered moves of the blind protocol. Then: in move 1, *why* must the judge's
score be hidden from the human — what specifically goes wrong if the human sees it first?
'''))
C.append(md('''
## Scale up: 10 toy calls, two label columns

One call cannot show an agreement *rate*. So we move to a small toy panel of 10 calls. Each call
has a `human` label (collected blind) and a `judge` label. These are toy numbers chosen to make
the counting visible — book 13 onward uses them too. We print the panel RAW first.
'''))
C.append(code('''
# Toy calibration panel: 10 calls, each with a blind human label and a judge label for handled_partial.
# Toy-before-real: hand-made 0/1s make the agreement arithmetic countable by eye before any function.
labels = [
    {"call": "c01", "human": 1, "judge": 1},   # both say handled well
    {"call": "c02", "human": 0, "judge": 0},   # both say handled badly
    {"call": "c03", "human": 1, "judge": 1},
    {"call": "c04", "human": 0, "judge": 1},   # DISAGREE: human 0, judge 1
    {"call": "c05", "human": 1, "judge": 1},
    {"call": "c06", "human": 0, "judge": 0},
    {"call": "c07", "human": 1, "judge": 0},   # DISAGREE: human 1, judge 0
    {"call": "c08", "human": 1, "judge": 1},
    {"call": "c09", "human": 0, "judge": 0},
    {"call": "c10", "human": 1, "judge": 1},
]
# Print one row per call so each ROW is visibly one call with its two independent labels.
for r in labels:
    print(r["call"], "| human:", r["human"], "| judge:", r["judge"])
'''))
C.append(md('''
## PREDICT
Look at the 10 rows above. Before counting in code:
1. On how many of the 10 calls do `human` and `judge` **match**?
2. What **percentage agreement** is that?
Commit both numbers in the next cell.
'''))
C.append(code('''
# YOUR TURN - predictions go BEFORE the counting cell so the notebook records YOUR thinking,
# and the next cell can compare your guess to reality. That comparison is the lesson.
my_match_count = None        # <- how many of the 10 rows match (a whole number 0..10)
my_agreement_percent = None  # <- that as a percent (a number 0..100)

if my_match_count is None or my_agreement_percent is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("predictions locked:", my_match_count, "matches,", my_agreement_percent, "% agreement")
'''))
C.append(md('''
## Count agreement BY HAND

Manual-before-function: before any library, we count matches with a plain loop, printing each
comparison, so nothing hides. "Agreement" here is just: on how many calls did the two independent
labels land on the same value?
'''))
C.append(code('''
# Manual agreement count - one visible comparison per call, nothing hidden inside a helper.
matches = 0
for r in labels:
    same = (r["human"] == r["judge"])   # the two INDEPENDENT labels for this call
    # printing the verdict per row makes the agreement count auditable line by line
    print(r["call"], "human", r["human"], "vs judge", r["judge"], "->", "match" if same else "DISAGREE")
    if same:
        matches += 1

total = len(labels)
agreement = matches / total            # fraction in 0..1; we multiply by 100 only for display
print("\\nmatches:", matches, "of", total)
print("raw agreement:", round(agreement * 100, 1), "%")
'''))
C.append(code('''
# The comparison against YOUR committed prediction - this is the metal detector reading.
# A gap between your count and the real count is exactly the spot worth a second look.
if my_match_count is not None:
    verdict = "matched" if (my_match_count == matches and my_agreement_percent == round(agreement*100, 1)) else "DIFFERED"
    print("your prediction", verdict)
    print("you said", my_match_count, "matches /", my_agreement_percent, "% ; truth is", matches, "/", round(agreement*100, 1), "%")
'''))
C.append(md('''
## PREDICT
We are about to wrap the by-hand count in a function, `agreement_rate(labels)`. Before running it:
what percentage should it return if it is correct? (You already counted this by hand one cell ago
— commit to the exact number, because a function that disagrees with your hand count is a bug, not
a revelation.)
'''))
C.append(md('''
## Now the function — only after you did it by hand

You counted by hand, so a helper now is a convenience, not a mystery. `agreement_rate` does
exactly what your loop did: count matching pairs, divide by total. We will reuse it for the rest
of the book.
'''))
C.append(code('''
# agreement_rate packages the by-hand count. We use a helper so every later comparison uses the
# SAME definition of agreement - consistency is what lets us trust one number against another.
def agreement_rate(rows, a="human", b="judge"):
    # raw agreement = fraction of rows where the two named label columns are equal.
    # an empty panel has no defined rate, so we refuse it rather than divide by zero.
    assert rows, "need at least one labeled call to compute agreement"
    same = sum(1 for r in rows if r[a] == r[b])
    return same / len(rows)


# Same answer as the by-hand count - that sameness is how you trust the helper.
print("agreement_rate(labels) =", round(agreement_rate(labels) * 100, 1), "%")
'''))
C.append(md('''
## EXPLAIN gate
One sentence: the function returned the same percentage as your hand count. Why is matching your
manual result the thing that earns the function your trust — rather than the function's output
being trustworthy on its own?
'''))
C.append(md('''
## Which calls did they disagree on?

An agreement *rate* hides *where* the disagreement is. The two disagreements (c04, c07) are the
interesting calls — they are exactly what a human would re-examine, and exactly what book 13's
confusion matrix will separate by *direction* (human-yes/judge-no vs human-no/judge-yes).
'''))
C.append(code('''
# Pull only the rows where the independent labels disagree - these are the calls worth a human's
# second look, because that is where judge and human see the same call differently.
disagreements = [r for r in labels if r["human"] != r["judge"]]
for r in disagreements:
    # showing the DIRECTION (who said what) matters - book 13 splits these two kinds apart
    print(r["call"], "-> human said", r["human"], ", judge said", r["judge"])
print("\\ndisagreements:", len(disagreements), "of", len(labels))
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. What does **raw agreement** count, in one sentence?
2. Why does the agreement *rate* alone hide something important — what do you lose by collapsing
   10 rows into one percentage?
3. On the toy panel, which two calls disagreed, and in which **direction** each?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a judge score was the answer. After Act 2 you can: build the empty self-comparison and say
why its 100% is hollow, run the **blind protocol** (commit human label, then reveal judge, then
compare), count raw agreement by hand and confirm a helper against it, and isolate the
disagreements by direction. You now have two independent label columns and a number relating them.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (the blind protocol / raw agreement - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the independence, and the trap of a high agreement number

## Break-it philosophy

Calibration's whole value rests on one fragile thing: the two label columns being **independent**.
So we now attack that independence on purpose and watch the agreement number lie. Surprise on your
own terms is education; a contaminated calibration discovered on the demo stage is a disaster.
'''))
C.append(md('''
## PREDICT
We make a "human" column that is just a **copy** of the judge column (a not-blind labeler who
peeked at the judge and agreed every time). Before running: what agreement rate will
`agreement_rate` report on that copied column — and is that number evidence the judge is good?
Commit to one answer.
'''))
C.append(code('''
# BREAK-IT (guided) - we sabotage independence: the "human" label is COPIED from the judge label.
# This is what a non-blind labeler produces - they saw the judge's answer and went along with it.
contaminated = [{"call": r["call"], "human": r["judge"], "judge": r["judge"]} for r in labels]

# agreement_rate does not error - it happily reports a beautiful, meaningless number.
rate = agreement_rate(contaminated)
print("contaminated agreement rate:", round(rate * 100, 1), "%")
# 100%. No crash. And it is the self-graded exam wearing a human's name tag.
'''))
C.append(md('''
## Reading the failure — the dangerous kind

This break did **not** crash. `agreement_rate` returned `100.0%` — a number a slide would love.
That is precisely what makes contamination dangerous: it fails *silently*, producing a *better*
number than honest calibration would. A loud crash protects you; a silently inflated agreement
rate walks straight onto the demo stage. The defense is not in the code — it is in the
**protocol**: the human must label blind, before seeing the judge, or the number it produces is a
lie no function can detect.
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
Contaminated calibration is *more* dangerous than calibration that crashes. Why? (Hint: which one
hands you a beautiful number?) And where does the defense live — in `agreement_rate`, or in the
protocol around it?
'''))
C.append(md('''
## YOUR break now

Author your own attack on independence. Take the toy `labels` and create a `my_contaminated`
panel where the human column is derived from the judge column by SOME rule you choose (copy it,
copy-then-flip one row, copy with a typo). Predict the agreement rate your rule produces, write
the prediction as a comment, then run.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it on independence.
# my prediction: <write here the agreement rate your rule produces and why>

# Start from a copy of the judge column (already not-blind), then optionally tweak one row.
my_contaminated = [{"call": r["call"], "human": r["judge"], "judge": r["judge"]} for r in labels]
# OPTIONAL damage: uncomment and edit to flip one human label and see the rate move.
# my_contaminated[0]["human"] = 1 - my_contaminated[0]["human"]

# Run the SAME metric and compare reality against your written prediction above.
print("your contaminated agreement rate:", round(agreement_rate(my_contaminated) * 100, 1), "%")
'''))
C.append(md('''
## WRONG-INTUITION TRAP 1 — high agreement does NOT mean the judge is good

**The wrong belief:** "the human and the judge agreed 90% of the time, so the judge is 90% good."

Two different things can inflate raw agreement *without* the judge being good. First, the
contamination you just saw (not-blind labels). Second — and subtler — **chance**: when one label
is overwhelmingly common, two labelers can agree most of the time by *guessing in line with the
common label*, never actually looking at the call. The next cell builds a panel where the judge is
a brain-dead "always say 0" stamp, the human is mostly-0 too, and they still agree a lot. Run it,
then explain the agreement BEFORE the reveal.
'''))
C.append(md('''
## PREDICT
The next cell builds a 10-call panel where the judge always outputs `0` (it read nothing) and the
human is `0` on 8 of the 10 calls. Before running: what agreement rate will `agreement_rate`
report for this do-nothing judge — and does that number tempt you to call the judge "good"?
Commit to the percentage.
'''))
C.append(code('''
# A panel where the judge does NO work: it stamps 0 on every call (a constant). The human happens
# to be 0 on most calls because "handled badly" is the common case in this skewed toy sample.
skewed = [
    {"call": "s01", "human": 0, "judge": 0},
    {"call": "s02", "human": 0, "judge": 0},
    {"call": "s03", "human": 0, "judge": 0},
    {"call": "s04", "human": 0, "judge": 0},
    {"call": "s05", "human": 0, "judge": 0},
    {"call": "s06", "human": 0, "judge": 0},
    {"call": "s07", "human": 0, "judge": 0},
    {"call": "s08", "human": 1, "judge": 0},   # the judge's constant 0 is WRONG here
    {"call": "s09", "human": 0, "judge": 0},
    {"call": "s10", "human": 1, "judge": 0},   # and wrong here
]
# The judge never looked at a single call - it returns 0 always. Yet agreement is high.
print("agreement with a do-nothing always-0 judge:", round(agreement_rate(skewed) * 100, 1), "%")
print("judge labels are all zero:", [r["judge"] for r in skewed])
'''))
C.append(md('''
## The reveal

The do-nothing judge — which **never read a call** — agreed with the human **80%** of the time.
Raw agreement rewarded it for nothing, because the label `0` is so common that matching it is easy
by default. So a high agreement rate can come from (a) a genuinely good judge, (b) a contaminated
not-blind label, or (c) pure base-rate luck on a skewed panel. **Raw agreement cannot tell these
apart.**

This is exactly the gap **book 13 (confusion matrix)** and the kappa that follows it close: the
confusion matrix shows *where* agreement happens (is the judge ever right about the rare `1`
calls?), and **Cohen's kappa** subtracts the agreement you would expect from chance, so a
do-nothing stamp scores near zero. Raw agreement is the start of calibration, never the end.
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: name two ways a high agreement rate can be misleading

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## A second break: the empty panel

One more failure mode, the boring-but-real one: trying to compute an agreement rate over **zero**
labeled calls. There is no rate to compute — you cannot divide matches by a total of zero — and
`agreement_rate` refuses it at the door rather than returning a fake number.
'''))
C.append(code('''
# BREAK-IT (guided) - SUPPOSED to error: asking for agreement on an empty calibration panel.
# The assert is the boundary that stops a meaningless 0/0 from masquerading as a real rate.
empty_panel = []
print(agreement_rate(empty_panel))   # we never reach the print - the assert fires first
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a high agreement number felt like proof the judge is good. After Act 3: you know
contamination (not-blind labels) inflates agreement *silently* with no crash, an empty panel is
refused at construction, and — the deep one — even honest blind agreement can be inflated by
**chance** on a skewed panel. Raw agreement is necessary, never sufficient; that gap is what
book 13 and kappa exist to fix.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the chance-agreement trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this lives, and the bar you must clear

## Where calibration lives in VoiceForge

This is not a notebook idea — it is how the project earns the right to show judge scores at all:
- **`pipeline/judge.py`** → `judge_dimension()` produces the judge column: one
  `{score, reason, evidence_turn_ids}` per dimension per call (book 11's contract).
- **Human labels** are collected on a **sample** of calls, blind — a labeler reads the call and
  its evidence turns (e.g. t2/t3 on the hero call) and assigns the same label WITHOUT seeing the
  judge's score. The evidence trail from book 11 is what lets the human re-judge the *same* moment.
- **The pilot calibration** lays the two columns side by side on that sample, exactly like the toy
  panel here, and reports agreement — the honest answer to "is the judge any good?".
- The dimensions and thresholds the judge scores against live in **`rubric.yaml`**; calibration is
  what justifies trusting those judged dimensions on the calls nobody hand-labeled.
'''))
C.append(md('''
## Where it flows next on the ladder

The two aligned label columns you built are the direct input to:
- **13 · confusion matrix** — cross-tabulates human vs judge into the four cells
  (agree-yes, agree-no, human-yes/judge-no, human-no/judge-yes), so you see *where* and *which
  direction* the disagreements run, not just how many.
- then **Cohen's kappa** — collapses that matrix into one agreement number that **subtracts
  chance**, so the do-nothing always-0 judge from Act 3 scores near zero instead of 80%.

Neither is possible without this book's move: getting an independent, blind human label to sit
next to the judge's.
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

You saw the do-nothing always-0 judge score 80% raw agreement. In book 13, **Cohen's kappa** will
re-score that same panel after subtracting chance agreement. Predict: roughly what will kappa say
about the do-nothing judge — near 0, near 0.8, or near 1 — and why does subtracting "agreement you
would get by guessing the common label" punish a constant stamp?
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for book 13 to confront.
my_kappa_prediction = ""   # near 0 / 0.8 / 1 for the do-nothing judge, and WHY chance-subtraction punishes it

if len(my_kappa_prediction.strip()) < 20:
    print("write your prediction above (a value + why), then re-run.")
else:
    print("PREDICTION STORED:", my_kappa_prediction)
'''))
C.append(md('''
## Where this idea itself fails (honesty applies to the method too)

- **Contaminated labels** — a "human" label that peeked at the judge first (you built one).
  Countermeasure: enforce blind labeling — judge score hidden until the human commits.
- **Chance inflation** — high raw agreement from a skewed panel where guessing the common label
  wins (the do-nothing judge). Countermeasure: report kappa, never raw agreement alone (book 13+).
- **Tiny sample** — calibrating on 3 calls and trumpeting "100% agreement". Countermeasure: state
  the sample size next to the rate; a rate without an N is a half-truth.
- **Labeler-of-one** — a single human's labels treated as ground truth when that human is also
  biased. Countermeasure: multiple independent labelers, and measure *their* agreement too.
'''))
C.append(md('''
## The same idea at three levels

- **To a beginner:** "you can't check your own answers against your own answer key — you need
  someone else to grade you blind, then see if you two agree."
- **To an engineer:** "calibration measures judge-vs-human agreement on a sample where the human
  labels are collected blind and independent of the judge; raw agreement is the first cut, but it
  is confounded by base rate, so we report Cohen's kappa to subtract chance."
- **To a founder:** "we don't just trust our AI judge — we have humans grade a sample of calls
  without seeing the AI's answer, and we publish how often they agree, so 'the judge is good' is a
  measured claim, not a promise."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "Your AI judge scored these calls — how do you know it's right?"**
<details><summary>answer</summary>We don't take the judge's word for it. We had humans label a sample of calls blind — without seeing the judge's score — and measured how often the judge agreed with them. That agreement (reported as Cohen's kappa, which removes chance) is the evidence. A judge validating itself would be circular; the human label breaks that circle.</details>

**2. "Why blind? Why not let the human see the judge's score and just confirm or correct it?"**
<details><summary>answer</summary>Because seeing the judge first anchors the human to it — they drift toward agreeing, and the agreement number inflates without any real independent check. We demonstrated this: copying the judge's column into the human column gives 100% agreement and proves nothing. Blind labeling is the only way the two columns stay independent.</details>

**3. "The human and judge agreed 90% of the time — isn't the judge clearly good?"**
<details><summary>answer</summary>Not from that number alone. A do-nothing judge that always stamps the common label can hit high raw agreement by base-rate luck — we showed an always-0 judge scoring 80% having read nothing. That's why we report the confusion matrix (where the agreement is) and Cohen's kappa (agreement above chance), not raw agreement.</details>
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, the whole-book recap)
1. Why can a judge never validate itself — what is the one ingredient a real check must add?
2. In the blind protocol, which move would, if skipped, silently inflate agreement — and how?
3. Name the two confounds that let raw agreement overstate a judge, and the two later tools
   (one in book 13, one right after) that each confound is fixed by.
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: where calibration sits in the real pipeline (`judge.py` produces one column,
blind human labels the other, `rubric.yaml` defines what is scored), how the aligned columns feed
the confusion matrix (13) and Cohen's kappa, the method's own failure modes (contamination, chance
inflation, tiny N), and how to defend "the judge is good" as a *measured* claim at three levels —
including the hard truth that raw agreement is confounded by chance.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The circularity problem — why a judge checking its own scores proves nothing
2. The three ordered moves of the blind protocol, and why move 1 must hide the judge's score
3. What raw agreement counts — and the two ways it can be misleading (contamination, chance)
4. Why the do-nothing always-0 judge scored 80%, and what kappa does about it
5. One real place this lives in the pipeline, and the book downstream that needs the aligned columns

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (where it lives / where it flows)
my_clean_sentence = ""      # the sentence you'd say in a room about why calibration needs humans

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Human labels break the circle the judge cannot break itself."**

If yours captures that in your own words — a judge cannot validate a judge; only an independent,
blind human label can — this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "12_calibration_why_human_labels.ipynb"   # this notebook's filename
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

**12 done** (pending your teach-back) → **13 · confusion matrix** — you now have two independent,
blind-aligned label columns (human and judge). Book 13 cross-tabulates them into the four cells of
a confusion matrix, so you can see exactly *where* and in which *direction* judge and human
disagree — the structure raw agreement collapsed away, and the thing Cohen's kappa then scores
against chance.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "12_calibration_why_human_labels.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
