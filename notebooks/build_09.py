#!/usr/bin/env python3
# Builds 09_language_conditions.ipynb — VoiceForge University book 09.
# ONE atomic concept: language is an EVAL DIMENSION, not a feature checkbox.
# Rerun: .venv/bin/python notebooks/build_09.py
# Style/rhythm/comment-density cloned from build_P00.py (the gold reference).
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
# 09 · Language conditions

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Run the **same task** (book an appointment) through three language conditions — **English**
   (call_A), **Hinglish** (call_B), **Tenglish / Telugu-English** (call_C) — and read the
   outcome and the **turn count** for each.
2. Define **code-switching** (mixing two languages inside one turn) and point at it line by line
   in a real call (`data/hero/turns.json`, language `te-en`).
3. Explain **why an English-trained voice stack degrades** on Hinglish/Tenglish — at the ASR,
   the agent, and the judge — instead of waving at "it's just harder".
4. Defend the load-bearing claim of this book: **language is a slice you must report per
   condition**, the same way you already report p50 *and* p90 — not a yes/no checkbox you tick
   once and forget.

Topic looks small (three short calls). The claim is not small: every later measurement —
the judge (book 10), its calibration, the scorecard — is only trustworthy *per language*. A
single blended number hides which condition is failing.
'''))
C.append(md('''
## 2 — Knowledge map

`08 (cost: $ per successful call) → THIS: language is an eval dimension → 10 (the LLM judge)`

Why this book exists, right here on the ladder. Book 08 taught you to divide by **successes**:
cost is dollars per *good* call, so anything that lowers the success rate quietly raises the
bill. This book names a variable that moves the success rate hard and is usually left
unmeasured: **the language the call happened in**. Book 10 then sends calls to an LLM judge —
and a judge you trust on English can be wrong on Tenglish in ways you will not see unless you
already sliced by language *here*.

No lesson floats in the void: previous = "cost is per success", current = "language changes
the success rate, so it is a slice", next = "now an AI judges the calls — slice that too".
'''))
C.append(md('''
## 3 — Baby intuition

Picture one assistant taking the same booking request in three rooms.

- **Room EN:** the caller speaks clean English. The assistant was built and tested in this
  room. Smooth.
- **Room Hinglish:** the caller mixes Hindi and English in the *same sentence* — "Friday
  chalega I think". The assistant half-follows.
- **Room Tenglish:** the caller mixes Telugu and English — "area ante... Madhapur side
  anukunta". The assistant mishears the address, pushes too hard, and the booking dies.

Same assistant. Same task. Three very different outcomes — and the **only** thing that changed
between the rooms was the **language**. That is the whole book: language is a knob that moves
the result, which makes it a thing you must *measure*, not a feature you *checked off*.
'''))
C.append(md('''
## 4 — The formal version

Two terms we will use precisely all book:

- **language condition** — the language (or language-mix) a call happens in, treated as a
  category you can group calls by: here `English`, `Hinglish`, `Telugu-English`. In the real
  schema this is the `language` field (`en`, `te-en`, …) — see `schemas/call_log.md`.
- **code-switching** — switching between two languages *within one turn* (sometimes mid-clause):
  "morning better... around ten **ayite manchidi**." Not a typo, not noise — a normal feature
  of how bilingual people actually talk.

The claim, stated flat: **a quality number computed over a language-mixed pool of calls is an
average that hides its worst condition.** The fix is the same one this whole course keeps
reaching for — *report per slice*. You report p50 and p90 instead of one mean (book 04); you
report English and Hinglish and Tenglish instead of one blended success rate. Language is an
**eval dimension**.
'''))
C.append(md('''
## 5 — Why this is a checkbox in most stacks (the thing we are fighting)

A feature checkbox sounds like: *"Multilingual? ☑ yes — the model speaks Hindi."* It is a
one-time yes/no about a capability.

An eval dimension sounds like: *"success_rate: EN 0.92 · Hinglish 0.71 · Tenglish 0.48;
p90 latency: EN 700ms · Tenglish 1500ms"* — a number **per condition**, recomputed every run.

The checkbox lets a stack claim "we support Hinglish" while silently failing half of Hinglish
calls, because nobody ever **grouped the calls by language and looked**. This book builds that
group-and-look with your own hands so the checkbox can never hide behind a single average again.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In one sentence: what is the difference between treating language as a **checkbox** versus
   as an **eval dimension**?
2. What does **code-switching** mean — and at what scope does it happen (across calls? across
   turns? *within* a turn)?
3. This book sits between "cost is per success" and "an AI judges calls". Why must language
   come *before* the judge, not after?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: "multilingual support" is a feature a product either has
or does not have. After Act 1 you should hold: **language is a variable that moves the success
rate**, so it is something you *slice and report*, not something you *tick once*. The rest of
the book is you proving that to yourself on the cast — and then on the real hero call.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of "language is an eval dimension, not a checkbox".
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
# Act 2 — Mechanics: the same task, three languages, measured by hand

## The cast, defined inline (same ids/languages/outcomes as every book)

We rebuild the three recurring calls here so this notebook stands alone. The contract is fixed
across the whole course (the consistency reviewer checks it): **call_A** = English / success,
**call_B** = Hinglish / partial, **call_C** = Telugu-English / failure. The point of this book
is that those outcomes line up with the *language* — and we are going to make you see it, not
take my word for it.
'''))
C.append(md('''
## The task is held CONSTANT on purpose

All three calls attempt the **same job**: book an appointment, capture the required fields. If
we changed the task *and* the language at once, we would learn nothing about either (that is
the change-one-thing rule from P00). So the task is fixed; only the **language** varies. Then
any difference in outcome has exactly one suspect.
'''))
C.append(code('''
# call_A — ENGLISH. The condition the stack was built and tested in. We print the RAW object
# first (course rule: see the ugly input before any transformation). Metadata sits OUTSIDE the
# turns because language/outcome are facts about the whole call, not about one turn.
call_A = {
    "call_id": "call_A",
    "language": "English",
    "outcome": "success",                  # all required fields captured, caller cooperative
    "turns": [
        {"speaker": "agent", "text": "Hi! I can book your table. For how many people?",       "start_ms": 0,    "end_ms": 2800},
        {"speaker": "user",  "text": "Four people, tomorrow at 7pm.",                          "start_ms": 3300, "end_ms": 5200},
        {"speaker": "agent", "text": "Booked: table for four, tomorrow 7pm. Anything else?",   "start_ms": 5700, "end_ms": 8400},
        {"speaker": "user",  "text": "No, thank you!",                                         "start_ms": 8900, "end_ms": 9800},
    ],
}
print("id:", call_A["call_id"], "| language:", call_A["language"], "| outcome:", call_A["outcome"])
for t in call_A["turns"]:
    print("  ", t["speaker"], "|", t["text"])
'''))
C.append(code('''
# call_B — HINGLISH (Hindi+English mixed). Same task (an appointment). The two textures the
# spec calls for live in the text: a hesitation ("umm... ek minute") and a repeat request
# ("sorry can you repeat?"). Those textures are WHY it ends partial — watch the turns pile up.
call_B = {
    "call_id": "call_B",
    "language": "Hinglish",
    "outcome": "partial",                  # day captured, but the time is left unconfirmed
    "turns": [
        {"speaker": "agent", "text": "Namaste, main aapka dentist appointment book kar sakta hoon. Kaunsa din?", "start_ms": 0,    "end_ms": 3600},
        {"speaker": "user",  "text": "umm... ek minute... Friday chalega I think.",            "start_ms": 4200,  "end_ms": 7100},
        {"speaker": "agent", "text": "Friday theek hai. Morning ya evening slot?",              "start_ms": 7600,  "end_ms": 9900},
        {"speaker": "user",  "text": "sorry can you repeat? line thodi unclear thi.",           "start_ms": 10400, "end_ms": 12800},
        {"speaker": "agent", "text": "No problem — morning ya evening?",                        "start_ms": 13300, "end_ms": 15100},
        {"speaker": "user",  "text": "haan main baad mein confirm karta hoon.",                "start_ms": 15600, "end_ms": 17900},
    ],
}
print("id:", call_B["call_id"], "| language:", call_B["language"], "| outcome:", call_B["outcome"])
for t in call_B["turns"]:
    print("  ", t["speaker"], "|", t["text"])
'''))
C.append(code('''
# call_C — TELUGU-ENGLISH (Tenglish). Same task again. Here the language mismatch compounds
# into the worst failure mode: the agent mishandles the code-switched address and the booking
# dies. We keep the exact turns the course uses so call_C stays the same character everywhere.
call_C = {
    "call_id": "call_C",
    "language": "Telugu-English",
    "outcome": "failure",                  # address never captured, booking not completed
    "turns": [
        {"speaker": "agent", "text": "Service desk. Which area are you calling from?",         "start_ms": 0,    "end_ms": 3500},
        {"speaker": "user",  "text": "Madhapur... ante, near the metro pillar number...",      "start_ms": 4000, "end_ms": 9000},
        {"speaker": "agent", "text": "I need the full address with pincode.",                   "start_ms": 8200, "end_ms": 11000},  # starts 8200 < user end 9000 = overlap
        {"speaker": "user",  "text": "ayyo... I don't remember exactly ya.",                    "start_ms": 11500, "end_ms": 14000},
    ],
}
print("id:", call_C["call_id"], "| language:", call_C["language"], "| outcome:", call_C["outcome"])
for t in call_C["turns"]:
    print("  ", t["speaker"], "|", t["text"])
'''))
C.append(code('''
# Put the three calls in one list so we can loop over "the cast" the way the rest of the book does.
# A list (not three loose variables) is what lets us GROUP-BY language in a moment — the core move.
cast = [call_A, call_B, call_C]
print("cast size:", len(cast), "calls")
'''))
C.append(md('''
## PREDICT
Before any counting: rank the three calls by **how many turns** the task took, from FEWEST to
MOST. (Hint: each repeat or hesitation forces an extra back-and-forth.) Then predict the
**outcome** of each. Commit in the next cell — you will check it against the real counts.
'''))
C.append(code('''
# YOUR TURN - PREDICT here, BEFORE the counting cell runs. We store the guess as variables so
# the notebook becomes a record of YOUR thinking and a later cell can confront it.
my_fewest_turns_call = None    # <- "call_A" / "call_B" / "call_C": which took the FEWEST turns?
my_most_turns_call   = None    # <- which took the MOST turns?

if my_fewest_turns_call is None or my_most_turns_call is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("locked - fewest:", my_fewest_turns_call, "| most:", my_most_turns_call)
'''))
C.append(md('''
## Manual-before-function: count turns BY HAND first

Before any tidy table, we compute the number that matters — **turn count per language** — the
slow visible way. Turn count is a cheap proxy for effort: the more back-and-forth a task needs,
the more chances to drop a field or frustrate the caller. We will literally count.
'''))
C.append(code('''
# Manual turn count for ONE call, every step printed - nothing hidden behind a function yet.
# len(turns) is the count, but we print the speakers too so you SEE what is being counted.
one_call = call_B
print("counting turns for:", one_call["call_id"], "(", one_call["language"], ")")
for i, t in enumerate(one_call["turns"], start=1):     # start=1 so the printed index reads like turn numbers
    print("  turn", i, "-", t["speaker"])
print("=> turn count by hand:", len(one_call["turns"]))
'''))
C.append(code('''
# Now the same count for ALL THREE, side by side. This is the first time we GROUP BY language:
# one row per language condition. Read it by ritual: three rows; one row = one language run of
# the same task; one cell aloud = "Hinglish took 6 turns and ended partial".
print(f"{'language':<16}{'call_id':<10}{'turns':>6}  outcome")
print("-" * 44)
for c in cast:
    # we read turn count straight off the trace; outcome is the call-level fact we attached above
    print(f"{c['language']:<16}{c['call_id']:<10}{len(c['turns']):>6}  {c['outcome']}")
'''))
C.append(code('''
# Confront YOUR prediction with the counts. The comparison is the lesson, not the verdict.
turn_counts = {c["call_id"]: len(c["turns"]) for c in cast}   # dict so we can look up by id
fewest_actual = min(turn_counts, key=turn_counts.get)         # id with the smallest turn count
most_actual   = max(turn_counts, key=turn_counts.get)         # id with the largest turn count
print("actual fewest-turns call:", fewest_actual, "| actual most-turns call:", most_actual)

if my_fewest_turns_call is not None:
    hit = (my_fewest_turns_call == fewest_actual and my_most_turns_call == most_actual)
    print("your ranking", "MATCHED" if hit else "DIFFERED",
          "- if it differed, that gap is exactly what to think about")
'''))
C.append(md('''
## OBSERVE + EXPLAIN

Did the ranking hold? Read the counts off the table exactly: English **4** turns, Hinglish **6**,
Tenglish **4**. The English call finished in the fewest turns and **succeeded**; the Hinglish
call took the **MOST** turns (6) and only **partially** completed; the Tenglish call also took
few turns (4) but **FAILED outright** — the booking died fast rather than dragging on. The two
failure modes look different in turn count (Hinglish **drags**, Tenglish **collapses**), but
**BOTH are non-success** once the language moves off clean English — the lesson is the **OUTCOME
shift**, not a tidy turn-count ranking (notice turn count rises *then falls*: 4 → 6 → 4, so it
is not a monotone signal). The task never changed. One sentence, out loud: *why* would a repeat
request ("can you repeat?") show up more in a code-switched call than in a clean-English one?
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
You just grouped the same task by language and saw turns and outcome both move. State the
single claim those three rows support — and the one claim they do **not** yet support. (Hint:
three calls is an illustration, not a measurement; the *shape* is the lesson, the *numbers* are
not yet a result. We will hit that hard in Act 3.)
'''))
C.append(md('''
## Now the success rate — manual, then the grouping function

"Success rate" is just: of the calls in a group, what fraction ended in `success`? We compute
it BY HAND for one group first (so the division is visible), then write the tiny grouping
helper. Manual before function, every time — a function you met before the idea stays a black box.
'''))
C.append(md('''
## PREDICT
Three calls, one per language, outcomes success / partial / failure. If we score **success
rate** as "fraction whose outcome is exactly `success`", what will the rate be for the English
group? For the Hinglish group? For the Tenglish group? Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - PREDICT the three per-language success rates (each group has exactly one call here).
my_en_rate  = None    # <- a number 0..1 for the English group
my_hin_rate = None    # <- a number 0..1 for the Hinglish group
my_ten_rate = None    # <- a number 0..1 for the Telugu-English group

if None in (my_en_rate, my_hin_rate, my_ten_rate):
    print("fill in all three rates above (0..1), then re-run this cell.")
else:
    print("locked rates - EN:", my_en_rate, "Hinglish:", my_hin_rate, "Tenglish:", my_ten_rate)
'''))
C.append(code('''
# Manual success rate for ONE group, fully spelled out. We treat "success" as a 1 and anything
# else (partial, failure) as a 0, because a partial booking is NOT a completed task.
english_group = [c for c in cast if c["language"] == "English"]   # filter the cast to one condition
wins = sum(1 for c in english_group if c["outcome"] == "success") # count the exact-success calls
n    = len(english_group)                                         # how many calls in this group
print("English group size:", n, "| successes:", wins)
print("English success rate by hand:", wins / n)                  # the division, in the open
'''))
C.append(code('''
# The grouping helper - written ONLY now that you have done the division by hand once.
# It returns, per language: how many calls, how many successes, and the rate. We pass the
# success test in as a function so the definition of "success" lives in ONE obvious place.
def success_rate_by_language(calls, is_success):
    groups = {}                                  # language -> running [successes, total]
    for c in calls:
        lang = c["language"]
        groups.setdefault(lang, [0, 0])          # first time we see a language, start its tally
        groups[lang][0] += 1 if is_success(c) else 0
        groups[lang][1] += 1
    # turn the tallies into rows; rate is successes/total, guarded against an empty group
    return {lang: {"successes": s, "total": t, "rate": (s / t if t else None)}
            for lang, (s, t) in groups.items()}

# "success" means the outcome string is exactly 'success' - partial and failure are not wins
by_lang = success_rate_by_language(cast, lambda c: c["outcome"] == "success")
for lang, row in by_lang.items():
    print(f"{lang:<16} {row['successes']}/{row['total']}  rate={row['rate']}")
'''))
C.append(code('''
# Confront YOUR predicted rates with the computed ones, per language.
for lang, mine in [("English", my_en_rate), ("Hinglish", my_hin_rate), ("Telugu-English", my_ten_rate)]:
    actual = by_lang[lang]["rate"]               # look up the computed rate for this condition
    if mine is not None:
        print(f"{lang:<16} you said {mine}, actual {actual}",
              "- match" if mine == actual else "- DIFFERED, think about why")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not memory): if you collapsed these three groups into
ONE overall success rate, what would it be — and which single number would a stakeholder then
*miss*? (You are about to meet exactly this collapse as the trap of the book.)
'''))
C.append(md('''
## Meet code-switching — point at it, do not just define it

We said code-switching is mixing two languages *inside one turn*. Definitions are slippery;
let us make it concrete by scanning call_C's user turns for a short list of Telugu tokens and
marking which turns carry a switch. Manual detection first (a tiny token list) so you see the
mechanism — book 10's judge will do this far better, but you must own the idea first.
'''))
C.append(md('''
## PREDICT
call_C's two user turns are: "Madhapur... ante, near the metro pillar number..." and
"ayyo... I don't remember exactly ya." Each mixes Telugu and English. Which English words sit
right next to which Telugu words? Predict how many of the two user turns our detector will flag
as code-switched. Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - PREDICT how many of call_C's USER turns contain a language switch (0, 1, or 2).
my_codeswitch_count = None    # <- a number: 0, 1, or 2

if my_codeswitch_count is None:
    print("fill in my_codeswitch_count above, then re-run this cell.")
else:
    print("locked code-switch prediction:", my_codeswitch_count)
'''))
C.append(code('''
# A TOY code-switch detector: does a turn contain BOTH an English word AND a Telugu token?
# This is deliberately crude (a hand list, lowercase match) so the MECHANISM is visible.
# Real detection is a model's job; the idea - "two languages in one turn" - is what we own here.
telugu_tokens = {"ante", "ayyo", "ya", "kavala", "ledu", "vastundi", "manchidi", "sare", "anukunta"}

def has_codeswitch(text):
    words = text.lower().replace(",", " ").replace(".", " ").split()  # rough tokenization, on purpose
    has_te = any(w in telugu_tokens for w in words)                   # any Telugu token present?
    has_en = any(w.isascii() and w.isalpha() and w not in telugu_tokens for w in words)  # any plain English word?
    return has_te and has_en                                          # a switch needs BOTH in the same turn

# scan only call_C's USER turns (the caller is the code-switcher here)
user_turns_C = [t for t in call_C["turns"] if t["speaker"] == "user"]
switched = 0
for t in user_turns_C:
    flag = has_codeswitch(t["text"])
    switched += 1 if flag else 0
    print("switch" if flag else "  --  ", "|", t["text"])
print("code-switched user turns:", switched, "of", len(user_turns_C))

if my_codeswitch_count is not None:
    print("your prediction", "matched" if my_codeswitch_count == switched else "DIFFERED")
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. Define code-switching at the right scope (within a turn).
2. Our detector flags a turn when it contains BOTH a Telugu token AND an English word. Name one
   way this toy detector would be **wrong** on a real call (false positive *or* false negative).
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: "the agent handles Hinglish" felt like a yes/no fact. After Act 2 you have, in your own
hands, three numbers that depend on language — **turn count** and **success rate per condition**
— plus a working (if crude) sense of **code-switching** as a within-turn event. You grouped the
same task by language and watched the result move. That grouping *is* treating language as a
dimension.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (group-by-language / success-per-condition / code-switch - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the blended number, and the trap at the heart of the book

## Break-it philosophy

You do not understand a metric until you have seen it lie. So we now build the **one blended
success rate** that a checkbox-shaped stack would report, and we damage the pool underneath it
to watch the single number stay calm while a whole condition collapses. Surprise here, on your
terms, beats surprise on the demo stage.
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this whole book is built on

**The wrong belief:** *"our overall success rate is 0.8, so the agent is fine — multilingual is
handled."*

The next cell computes one blended rate over a realistic pool where English calls dominate the
*count* (most traffic is English) while Tenglish quietly fails. Watch the blended number look
healthy while one condition is on fire. Try to explain the gap BEFORE the reveal.
'''))
C.append(md('''
## PREDICT
A pool of 10 calls: 6 English (all success), 2 Hinglish (1 success, 1 partial), 2 Tenglish
(0 success, 2 failure). Predict TWO numbers: (a) the single blended success rate over all 10,
and (b) the Tenglish-only success rate. Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - PREDICT the blended rate and the Tenglish-only rate for the 10-call pool described above.
my_blended_rate = None     # <- a number 0..1: successes / 10 across the whole pool
my_tenglish_rate = None    # <- a number 0..1: Tenglish successes / Tenglish total

if my_blended_rate is None or my_tenglish_rate is None:
    print("fill in BOTH rates above, then re-run this cell.")
else:
    print("locked - blended:", my_blended_rate, "| Tenglish-only:", my_tenglish_rate)
'''))
C.append(code('''
# A realistic pool: English dominates the COUNT (most traffic), Tenglish is a small slice that
# is failing. This count-imbalance is exactly what lets a blended average hide a dead condition.
pool = (
    [{"language": "English",        "outcome": "success"} for _ in range(6)] +
    [{"language": "Hinglish",       "outcome": "success"}, {"language": "Hinglish", "outcome": "partial"}] +
    [{"language": "Telugu-English", "outcome": "failure"} for _ in range(2)]
)

# THE BLENDED NUMBER a checkbox-stack reports: one success rate over everybody, language ignored.
blended_wins = sum(1 for c in pool if c["outcome"] == "success")
blended_rate = blended_wins / len(pool)
print("pool size:", len(pool), "| blended success rate:", round(blended_rate, 2))

# THE SLICED NUMBERS this book insists on: the same pool, grouped by language.
sliced = success_rate_by_language(pool, lambda c: c["outcome"] == "success")
for lang, row in sliced.items():
    print(f"  {lang:<16} {row['successes']}/{row['total']}  rate={round(row['rate'], 2)}")
'''))
C.append(md('''
## The reveal

The blended rate reads **0.70** — sounds like a B-minus, ship it. But sliced: **English 1.00,
Hinglish 0.50, Telugu-English 0.00.** The Tenglish condition is a *total* failure, and the
blended average buried it under the English calls that dominate the count. **Nothing errored.
The 0.70 is real arithmetic.** It is the wrong arithmetic for the question "does this work for
my Tenglish callers?" — the answer to that is 0.00, and the single number was structurally
incapable of saying so.

This is the soul of the book: a checkbox reports *one* number and calls language "handled"; an
eval dimension reports *per condition* and exposes the 0.00. Same as P00's average-of-averages
and book 04's mean-hides-the-tail — **a single statistic over a mixed pool hides its worst
slice.** Language is one more axis that demands slicing.
'''))
C.append(code('''
# Confront your predictions. The blended number and the slice answer DIFFERENT questions -
# that difference is the entire lesson, so we print both verdicts.
if my_blended_rate is not None:
    print("blended: you said", my_blended_rate, "| actual", round(blended_rate, 2),
          "-", "match" if my_blended_rate == round(blended_rate, 2) else "differed")
    ten = sliced["Telugu-English"]["rate"]
    print("Tenglish-only: you said", my_tenglish_rate, "| actual", ten,
          "-", "match" if my_tenglish_rate == ten else "differed")
'''))
C.append(code('''
# BREAK-IT (guided) - make the trap WORSE on purpose: pour in more English traffic and watch
# the blended number CLIMB even though not one Tenglish call improved. The single metric is
# moved by traffic mix, not by quality - which is exactly why it cannot be trusted as "handled".
flooded = pool + [{"language": "English", "outcome": "success"} for _ in range(40)]  # 40 more easy wins
flooded_rate = sum(1 for c in flooded if c["outcome"] == "success") / len(flooded)
print("after flooding with 40 English successes:")
print("  blended rate climbed to:", round(flooded_rate, 2))
# the slice that matters did not move one bit - prove it:
ten_after = success_rate_by_language(flooded, lambda c: c["outcome"] == "success")["Telugu-English"]["rate"]
print("  Telugu-English rate is STILL:", ten_after, "(zero callers helped)")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
The flood cell raised the blended rate without improving a single Tenglish call. In one
sentence: what real-world change would move the blended number the same way — and why does that
make "overall success rate" a dangerous headline for a multilingual product?
'''))
C.append(md('''
## YOUR break now

Author your own damage to the slice. Change the **outcomes** of the Hinglish calls in `pool`
(make them both `success`, or both `failure`), predict in a comment what happens to the
*blended* rate versus the *Hinglish* slice, then run and compare. The skill: knowing which
number your change should move, and checking.
'''))
C.append(code('''
# YOUR TURN - self-authored BREAK-IT on the slice (you choose the damage this time).
# my prediction: <write here: after my change, blended -> ?, Hinglish slice -> ?, and WHY>

my_pool = (
    [{"language": "English",        "outcome": "success"} for _ in range(6)] +
    [{"language": "Hinglish",       "outcome": "success"}, {"language": "Hinglish", "outcome": "partial"}] +
    [{"language": "Telugu-English", "outcome": "failure"} for _ in range(2)]
)

# 1) change one slice's outcomes here, e.g.:
# my_pool[6]["outcome"] = "failure"
# my_pool[7]["outcome"] = "failure"

# 2) recompute BOTH views and compare against your written prediction:
mb = sum(1 for c in my_pool if c["outcome"] == "success") / len(my_pool)   # blended, one number
ms = success_rate_by_language(my_pool, lambda c: c["outcome"] == "success")  # sliced, per language
print("blended:", round(mb, 2))
for lang, row in ms.items():
    print("  ", lang, "->", round(row["rate"], 2))
'''))
C.append(md('''
## Why an English-trained stack degrades — the mechanism, not a shrug

It is not "Tenglish is just hard". The stack is a **pipeline**, and each stage was tuned on
English, so each stage loses a little — and the losses **stack**:

1. **ASR (speech → text):** trained mostly on English audio. On "near the metro **pillar
   number...**" code-switched with Telugu, it mis-transcribes or drops words. Garbage text in.
2. **The agent (LLM policy):** prompted and few-shot-tuned in English. Facing a half-wrong,
   code-switched address it lacks the repair behavior, so it over-demands ("full address with
   pincode") and barges in — the call_C failure you already saw.
3. **The judge (book 10):** an LLM scoring the call. If it reasons best in English, it can
   misread a *correct* Hinglish answer as wrong, or excuse a real Tenglish failure it did not
   parse. The measurement itself degrades.

Three multiplicative losses. That is why a stack at 0.92 on English can sit at 0.48 on Tenglish
— and why you must measure each condition, because the drop is real and stage-specific.
'''))
C.append(code('''
# A toy of the COMPOUNDING. Give each stage a per-stage "accuracy" that is high on English and
# lower on Tenglish, then MULTIPLY them - because the call only succeeds if every stage holds.
stage_acc = {
    "English":        {"asr": 0.97, "agent": 0.95, "judge": 0.97},
    "Hinglish":       {"asr": 0.85, "agent": 0.88, "judge": 0.90},
    "Telugu-English": {"asr": 0.75, "agent": 0.80, "judge": 0.85},
}
print(f"{'language':<16}{'asr':>6}{'agent':>7}{'judge':>7}   end-to-end (product)")
for lang, s in stage_acc.items():
    # multiply, because a failure at ANY stage sinks the call - independent-ish losses compound
    e2e = s["asr"] * s["agent"] * s["judge"]
    print(f"{lang:<16}{s['asr']:>6}{s['agent']:>7}{s['judge']:>7}   {round(e2e, 2)}")
print("note: each stage looks 'mostly fine' alone; the PRODUCT is where Tenglish falls off a cliff.")
'''))
C.append(md('''
## EXPLAIN gate
One sentence: each Tenglish stage scored 0.75–0.85 (individually "not terrible"), yet the
end-to-end product is far lower. What does that teach you about trusting a *per-stage* "looks
fine" when the stages are chained?
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a single "success rate" felt like an honest headline. After Act 3: you have seen one
blended number stay healthy while a condition reads 0.00, watched it **climb on traffic mix
alone**, and traced the degradation to **compounding per-stage losses** (ASR · agent · judge).
A blended multilingual metric is now something you distrust by reflex — you reach for the slice.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the blended-number trap, or the compounding, is a strong pick)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where language lives in VoiceForge, and the bar you must clear

## The real hero call is a language condition (open it)

call_C is a hand-built stand-in. The real thing ships in the repo: `data/hero/turns.json`, a
12-turn Telugu-English appliance-service booking whose `language` field is literally `"te-en"`.
We load it now and point at the code-switching in real data — the same idea you detected on the
toy, on the call this whole course is built around.
'''))
C.append(md('''
## PREDICT
The real hero call is `te-en` (Telugu+English) and its `stress_profile` is `interruption`.
Predict: across its 12 turns, will you find code-switching in **most** user turns, or only one
or two? And given everything in Act 3, what do you expect its outcome to be? Commit next.
'''))
C.append(code('''
# YOUR TURN - PREDICT, for the real hero call, how many of its USER turns are code-switched.
my_hero_codeswitch_guess = None    # <- a whole number (the hero call has several user turns)

if my_hero_codeswitch_guess is None:
    print("fill in my_hero_codeswitch_guess above, then re-run this cell.")
else:
    print("locked hero code-switch guess:", my_hero_codeswitch_guess)
'''))
C.append(code('''
# Load the REAL hero call. We resolve the path from the repo root so it works headless too.
import json
from pathlib import Path

# walk up until we find the data dir - the notebook may run from notebooks/ or the repo root
root = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "hero" / "turns.json").exists())
hero = json.loads((root / "data" / "hero" / "turns.json").read_text())

# the language field is the eval dimension this whole book is about - print it in the open
print("call_id:", hero["call_id"], "| language:", hero["language"], "| stress_profile:", hero["stress_profile"])
print("turns:", len(hero["turns"]))
'''))
C.append(code('''
# Reuse our toy detector on the REAL user turns. Same mechanism, real data: two languages in one
# turn. We extend the Telugu token list a little to cover the hero call's actual words.
hero_telugu = telugu_tokens | {"haan", "okay", "ante", "ayyo"}   # union: keep prior tokens, add hero ones
hero_user_turns = [t for t in hero["turns"] if t["speaker"] == "user"]   # the caller code-switches

hero_switches = 0
for t in hero_user_turns:
    flag = has_codeswitch(t["text"])     # same crude both-languages-present test from Act 2
    hero_switches += 1 if flag else 0
    print("switch" if flag else "  --  ", "|", t["text"][:64])
print("code-switched user turns in the real hero call:", hero_switches, "of", len(hero_user_turns))

if my_hero_codeswitch_guess is not None:
    print("your guess:", my_hero_codeswitch_guess, "| detected:", hero_switches)
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
1. The real hero call flagged 5 of 6 user turns as code-switched. Does a HIGH code-switch rate
   on its own prove the call went badly? (Careful — what is the difference between a feature of
   how someone *talks* and a *failure*?)
2. Name the three pipeline stages where an English-trained stack loses accuracy on this call,
   in order, and say why their losses **compound** rather than add.
'''))
C.append(md('''
## Where this lives in the real pipeline (cite the files)

This is not a metaphor — language is wired through the VoiceForge code you can open:

- **`schemas/call_log.md`** — the `language` field (BCP-47-ish: `en`, `te-en`). Code-switching
  is "noted as e.g. `te-en`". The dimension exists in the data contract on day one.
- **`rubric.yaml`** — there is a dimension `language_match` (`type: judge, weight: 0.15`),
  commented "the multilingual slot". The rubric reserves real weight for language fit.
- **`data/hero/turns.json`** — the `te-en` hero call you just opened: the course's anchor case
  is itself a code-switched, non-English condition.
- **book 10 (`pipeline/judge.py`, `judge_dimension()`)** — the LLM judge that will score
  `language_match`. The very next book inherits the slice you built here.

So "language is an eval dimension" is the literal shape of the repo: a field in the schema, a
weighted dimension in the rubric, and a `te-en` flagship call.
'''))
C.append(md('''
## The concept at three levels (say each in one breath)

- **To a beginner:** "we ran the *same* booking in English, Hinglish, and Telugu-English and
  scored each language on its own — because the assistant that aces English can flop on the
  others, and one combined score would hide that."
- **To an engineer:** "language is a grouping key, not a capability flag. We report
  success-rate and latency *per language condition* (never one blended pool), because a
  count-dominant English slice masks a failing Tenglish slice, and the degradation compounds
  across ASR → agent → judge."
- **To a founder:** "a checkbox says 'we do Hinglish'. Our scorecard says 'Hinglish success is
  0.71, Tenglish is 0.48, here is the gap and the cost of closing it' — that is what a buyer
  with non-English callers will actually ask, and we answer it per condition."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "You only have one call per language in the cast — isn't this whole book anecdote?"**
<details><summary>answer</summary>The cast is the illustration, not the measurement. The CLAIM is structural: a single statistic over a language-mixed pool hides its worst slice — I proved that on a 10-call pool where blended read 0.70 while Tenglish was 0.00, and showed it climbs on traffic mix alone. The fix (report per condition) holds at any N; the real run uses the normalized pool and the te-en hero call.</details>

**2. "Why not just translate everything to English first, then evaluate once?"**
<details><summary>answer</summary>Because translation is itself one of the failing stages, and it discards the very thing being judged. Code-switching, the address mangling, the over-demanding repair — those live in the original language mix. Translating to English would hide the ASR/agent failures that caused call_C and inject new ones; you would be grading a different call than the one your caller had.</details>

**3. "Is 'language_match' enough — doesn't the rubric already cover this?"**
<details><summary>answer</summary>language_match (weight 0.15) scores whether the agent answered in the right language on ONE call. That is necessary but not the dimension this book is about: I'm arguing you must SLICE every other metric — success, latency, barge-in — BY language too. One judged sub-score per call is not the same as reporting the whole scorecard per condition.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now hold: the real `te-en` hero call is itself a language condition; `language` is a
schema field and `language_match` a weighted rubric dimension; the degradation has a mechanism
(compounding stages), not a shrug; and "report per language" is the same discipline as "report
p50 and p90". You are ready for book 10, where an AI judge scores these calls — and you already
know to read its scores *per condition*.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The atomic claim: language is an eval dimension, not a checkbox — and what each phrase means.
2. The trap: a blended success rate over a language-mixed pool, and why it can climb without any
   condition improving.
3. **Code-switching** defined at the right scope, with one real example from the hero call.
4. The degradation mechanism: the three stages (ASR · agent · judge) and why losses compound.
5. Where language lives in the repo: the `language` schema field, the `language_match` rubric
   dimension, and the `te-en` hero call.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about language and evals

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Multilinguality is an eval dimension, not a checkbox."**

If yours captures that in your own words — language is a *slice you report per condition*, not a
*capability you tick once* — this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "09_language_conditions.ipynb"   # <- this notebook's filename
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

**09 done** (pending your teach-back) → **10 · LLM as judge** — an AI model reads each call and
scores its dimensions (including `language_match`). You carry one rule in with you: read every
judge score **per language condition**, because a judge you trust on English is not yet a judge
you trust on Tenglish.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "09_language_conditions.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
