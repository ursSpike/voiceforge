#!/usr/bin/env python3
# Builds 00_what_is_voiceforge.ipynb per _BUILD_SPEC.md (four acts, marker conventions, recurring cast).
# The ONE atomic concept: VoiceForge is the layer AFTER the call — messy call in, five structured
# artifacts out. Style/rhythm/cell-size matched to the gold reference P00_how_to_learn.ipynb.
# Rerun: .venv/bin/python notebooks/build_00.py
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
# 00 · What is VoiceForge?

## 1 — Learning contract
By the end of this notebook you will be able to:
1. State the ONE thesis in a sentence: **VoiceForge is the layer that runs AFTER a call ends.**
2. Name the **five structured artifacts** a single messy call turns into (outcome, scorecard,
   failure tags, cost, improvement pair) and say what each one is *for*.
3. Explain why a voice-AI **company** needs this layer, and why most demos never build it.
4. Defend the boundary: VoiceForge is **NOT a voice bot** — it never talks to a caller.

This is the first VoiceForge book. The whole 35-book ladder exists to build the five artifacts
properly, one at a time. Today you only learn what they ARE and why they matter — no real
measurement yet. Toy data, by hand, end to end.
'''))

C.append(md('''
## 2 — Knowledge map (where this book sits)

`P04 (debugging) → THIS: What is VoiceForge? → 01 (the call log)`

You just finished the P-track: how to *learn* (P00) and the Python you need — objects, tables,
plots, debugging (P01–P04). That track taught you the **method**. This book is the first one
about the **subject**.

Why this book exists, and exists *here*: every book after this one builds a piece of VoiceForge.
If you do not first hold the whole shape in your head — *call in, five artifacts out* — each
later book feels like a disconnected trick. This book is the map the rest of the course fills in.
Next door, **01** zooms into the very first thing on the left of that picture: the **call log**
itself (what a single recorded call even looks like as data).
'''))

C.append(md('''
## 3 — Baby intuition

Picture a voice agent that takes phone calls — booking an appliance repair, say. The flashy part
is the call: it talks, the caller talks back, words appear on a screen. A demo ends right there,
on the applause.

Then the call ends. And every real question a company has begins *exactly there*:
**Did it actually work? How good was it? What went wrong, and where? What did it cost? How do we
make the next one better?** A recording cannot answer any of those. A wall of transcript text
cannot either. Something has to *read the finished call and produce answers*.

That something is VoiceForge. It is the machine that runs **after the mic turns off**.
'''))

C.append(md('''
## 4 — The formal version

**The thesis, stated plainly:** most voice-AI demos stop when the call ends. The hard, valuable,
boring work is everything *after* — turning one finished call into structured, defensible answers.

VoiceForge is that **after-the-call layer**. Its job is a transformation:

> **messy call in  →  five structured artifacts out**

The five artifacts (you will meet each one for real in a later book):

| # | artifact | one-line job | built for real in |
|---|---|---|---|
| 1 | **outcome** | did the task succeed? (success / partial / failure) | book 06 |
| 2 | **scorecard** | a score per quality dimension, each with a reason + evidence | books 06, 21 |
| 3 | **failure tags** | specific things that went wrong, time-stamped (e.g. barge-in) | books 04, 07 |
| 4 | **cost** | what this call cost to run (an estimate) | book 09 |
| 5 | **improvement pair** | a (worse → better) example to train the next model on | books 05, 17 |

"Structured" is the load-bearing word: not prose *about* the call, but **fields a program can
read, count, sort, and put on a dashboard.**
'''))

C.append(md('''
## 5 — Why this exists (the part founders care about)

A recording is evidence. It is not an **answer**. You cannot sort 10,000 recordings by "how bad
the worst moment was," or chart "cost per successful call this week," or hand your model team a
pile of "do this instead" examples — not from audio, and not from transcript text.

To run a voice-AI *company* (not a demo) you must answer the same five questions about **every
call, at scale, the same way every time.** That demands turning each messy call into the same
five structured artifacts. The artifacts are what you put on dashboards, in investor decks, and
into the training loop. VoiceForge is the layer that produces them.

The next cells build one tiny fake call by hand and walk it through all five — so the whole shape
is in your hands before any real data shows up in book 01.
'''))

C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In one sentence: **when** does VoiceForge do its work — during the call, or after it?
2. What is the transformation VoiceForge performs (what goes IN, what comes OUT)?
3. Why is "structured" the load-bearing word — what can you do with a structured field that
   you cannot do with a recording?
'''))

C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (maybe) pictured a voice-AI product AS the talking agent — the call itself.
After Act 1 you should hold a different picture: the call is the **input**, and the product is
the **after-the-call layer** that turns one messy call into five structured artifacts.

If you can say "messy call in, five artifacts out" without scrolling up, continue. If not,
re-read cell 4's table — that table is the spine of this entire course.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of what VoiceForge is. Not mine - yours.
# Producing the sentence is the learning; reading mine would just feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
# (We compare length, not content - future-you is the only grader that matters here.)
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: ONE tiny fake call, walked through all five artifacts

## The plan, and the rule

We will hand-build **one** absurdly small fake call, then produce each of the five artifacts from
it **by hand** — plain Python, no library, every number visible. Course rule: *toy before real,
raw before transformed, manual before function.* You meet the IDEA before any tool wraps it.

This call is fake and tiny on purpose. The point of Act 2 is not the numbers; it is feeling the
shape **call → 5 artifacts** in your own fingers, once, slowly.
'''))

C.append(md('''
## The raw input — a call as a "trace" (timed turns)

A call log is a list of **turns**. One turn = one person speaking once. Two vocabulary words you
will use for the rest of the course:
- **transcript** = the text only (just the words).
- **trace** = the text **plus timing** — each turn carries `start_ms` and `end_ms` (milliseconds
  from the start of the call). Timing is what lets us later catch interruptions and slow replies.

We print the RAW object first, before transforming anything — seeing the ugly input is a course
rule. Read it as: rows are *turns*, columns are *facts about a turn*.
'''))

C.append(code('''
# A toy call as a trace: a list of turn-dictionaries. Tiny on purpose so every value is visible.
# speaker is "user" or "agent" (the two roles in every call in this course);
# start_ms / end_ms are milliseconds from call start - we keep them because TIMING is a signal,
# not decoration (a later artifact reads exactly these numbers to find interruptions).
toy_call = {
    "call_id": "toy_1",                 # a name so artifacts can point back to THIS call
    "language": "English",              # the cast's Call A is English; we mirror that here
    "turns": [
        {"speaker": "agent", "text": "Hi! Can I book your appliance repair?", "start_ms": 0,    "end_ms": 2000},
        {"speaker": "user",  "text": "Yes, my fridge stopped cooling.",        "start_ms": 2300, "end_ms": 4200},
        {"speaker": "agent", "text": "Got it. Tomorrow morning work?",          "start_ms": 4500, "end_ms": 6000},
        {"speaker": "user",  "text": "Yes, ten AM is great. Number is 55501.",  "start_ms": 6300, "end_ms": 9000},
    ],
}
# one print per turn, so each ROW is visibly one THING (one person speaking once)
for t in toy_call["turns"]:
    print(t)
'''))

C.append(md('''
## PREDICT
Look at the four turns above. Count them in your head, and decide: did this call **succeed** at
its task (booking a repair)? What two facts would you point to as evidence? Commit out loud, then
write your guess in the next cell.
'''))

C.append(code('''
# YOUR TURN - predict BEFORE we compute anything. Stored as variables so this notebook becomes
# a record of YOUR thinking, and a later cell can confront your guess with the computed answer.
my_outcome_guess = None    # <- replace None with "success", "partial", or "failure"
my_turn_count_guess = None # <- replace None with an integer (how many turns?)

if my_outcome_guess is None or my_turn_count_guess is None:
    print("fill in BOTH guesses above, then re-run this cell.")
else:
    print("locked:", my_outcome_guess, "| turns:", my_turn_count_guess)
'''))

C.append(md('''
## Artifact 1 of 5 — OUTCOME (did the task succeed?)

The simplest artifact: one label for the whole call — **success / partial / failure**. We decide
it with a **required-fields checklist**: list what a booking MUST capture, then check whether the
call captured each. This is "task success" — you build it for real in book 06; here we do the
by-hand toy version so the idea is yours first.
'''))

C.append(code('''
# Manual outcome via a required-fields checklist. We do NOT eyeball it - we name the fields a
# successful booking must capture, then check each against the transcript text. Naming the rule
# explicitly is the whole point: an outcome you can't justify is an opinion, not an artifact.
required_fields = ["appliance", "time", "callback_number"]  # what a booking MUST capture

# join every turn's text into one searchable blob - crude on purpose (book 06 does this properly)
all_text = " ".join(t["text"].lower() for t in toy_call["turns"])

# check each required field by a simple keyword the caller actually said
captured = {
    "appliance":       "fridge" in all_text,
    "time":            "ten am" in all_text or "10 am" in all_text,
    "callback_number": "55501" in all_text,
}
for field in required_fields:
    print(f"{field:<16} captured? {captured[field]}")

# the outcome RULE: all captured -> success, none -> failure, otherwise -> partial
n_captured = sum(captured.values())
if n_captured == len(required_fields):
    outcome = "success"
elif n_captured == 0:
    outcome = "failure"
else:
    outcome = "partial"
print("ARTIFACT 1 — outcome:", outcome, f"({n_captured}/{len(required_fields)} fields)")
'''))

C.append(code('''
# The confrontation: your committed guess vs the computed outcome. A mismatch is a GIFT - it
# marks exactly where your mental model of "success" and the checklist disagree.
if my_outcome_guess is not None:
    verdict = "matched" if my_outcome_guess == outcome else "DIFFERED"
    print("your outcome guess", verdict, "- if it differed, that gap is the thing to think about")
'''))

C.append(md('''
## EXPLAIN gate
One sentence, out loud, in this shape: "The outcome is `success` **because** ___."
(If your sentence names the *checklist* rather than a vibe, you have the idea.)
'''))

C.append(md('''
## Artifact 2 of 5 — SCORECARD (a score + a reason + evidence)

"Success" is one bit. A **scorecard** is richer: for each **quality dimension**, a score from 0
to 1, **plus a reason, plus which turn(s) prove it** (the `evidence_turn_ids`). A bare score with
no reason and no evidence is not trustworthy — so in this course a scorecard *always* carries all
three. You build real scorecards in books 06 and 21; here is the toy shape.
'''))

C.append(md('''
## PREDICT
We will score two dimensions on a 0–1 scale: **politeness** and **efficiency** (did it book
without wasted turns?). Before the cell runs, commit: will this little call score HIGH or LOW on
each? Say why in your head.
'''))

C.append(code('''
# A toy scorecard: each dimension is NOT just a number - it is (score, reason, evidence).
# We bundle all three together so a score can never travel without its justification. That triple
# (score + reason + evidence_turn_ids) is the exact shape real VoiceForge scorecards use.
def make_entry(score, reason, evidence_turn_indexes):
    # evidence is stored as which turns prove the claim - a score you can't point to is hot air
    return {"score": score, "reason": reason, "evidence_turns": evidence_turn_indexes}

scorecard = {
    "politeness": make_entry(
        1.0, "agent greeted and stayed courteous throughout", [0, 2]),
    "efficiency": make_entry(
        0.9, "booked in 4 turns with no repeats or detours", [0, 1, 2, 3]),
}
for dim, entry in scorecard.items():
    print(f"{dim:<11} score={entry['score']}  reason={entry['reason']!r}  evidence_turns={entry['evidence_turns']}")
'''))

C.append(md('''
## CHECKPOINT 2 (out loud)
Why does this course refuse to let a score travel **alone**? Name the two things that must ride
along with every score, and say what each one protects you from on a demo stage.
'''))

C.append(md('''
## Artifact 3 of 5 — FAILURE TAGS (what went wrong, and when)

A scorecard says *how good*. **Failure tags** say *what specifically broke* — each tagged with a
**timestamp** and the evidence turns. Our toy call is clean, so to *see* a tag we must look at a
call that is not. We will compute the most important failure type by hand: a **barge-in** — when
one speaker starts before the other has finished (the turns overlap in time).
'''))

C.append(md('''
## The metric, by hand first: FTO (floor transfer offset)

Between any two back-to-back turns:

> **FTO = next turn's `start_ms` − previous turn's `end_ms`**

- **positive** FTO = a **gap** (silence between turns).
- **negative** FTO = an **overlap** — the next speaker started *before* the previous one stopped.
- a big enough overlap (more than ~100 ms) is a **barge-in** — an interruption.

We compute FTO by hand on two turns so the sign convention is burned in before any function does
it for us.
'''))

C.append(md('''
## PREDICT
Two turns: turn P ends at `end_ms = 5000`, turn N starts at `start_ms = 4200`.
Compute `FTO = 4200 − 5000` in your head. Is it positive or negative? Gap or overlap?
'''))

C.append(code('''
# FTO by hand on ONE pair. We print the subtraction itself, not just the answer, because the
# SIGN is the whole lesson: negative means N started before P finished -> they overlapped.
prev_end = 5000     # ms when the previous speaker stopped
next_start = 4200   # ms when the next speaker started

fto_ms = next_start - prev_end   # the one formula the whole timing layer is built on
print("FTO =", next_start, "-", prev_end, "=", fto_ms, "ms")

# turn the sign into the word a human uses
if fto_ms < 0:
    print("negative -> OVERLAP of", -fto_ms, "ms (the next speaker cut in early)")
else:
    print("positive -> GAP of", fto_ms, "ms (silence between turns)")
'''))

C.append(md('''
## Now a call that actually fails — and the function version

Here is a tiny **interruption** call: the agent starts talking while the user is still speaking.
We sweep every back-to-back pair, compute FTO for each, and emit a **failure tag** for any overlap
beyond the 100 ms barge-in threshold. This is the toy version of `pipeline/signals.py` in the
real repo (its `turn_metrics()` / `analyze()` do exactly this on real calls).
'''))

C.append(code('''
# A toy call WITH a barge-in: the agent's turn (t3) starts at 4300, before the user's turn (t2)
# ends at 5000 -> a 700ms overlap. We build the failure tag from the actual numbers + evidence.
bad_call = {
    "call_id": "toy_bad",
    "turns": [
        {"turn_id": "t1", "speaker": "agent", "text": "Which appliance?",        "start_ms": 0,    "end_ms": 1500},
        {"turn_id": "t2", "speaker": "user",  "text": "It's my washing mach-",   "start_ms": 1800, "end_ms": 5000},
        {"turn_id": "t3", "speaker": "agent", "text": "And your address please?", "start_ms": 4300, "end_ms": 6000},
    ],
}

BARGE_IN_MS = 100   # overlaps bigger than this count as an interruption (rubric.yaml owns this for real)

# timing comparisons only make sense in time order, so we sort by start_ms before pairing turns
turns_sorted = sorted(bad_call["turns"], key=lambda t: t["start_ms"])

failure_tags = []
for prev, nxt in zip(turns_sorted, turns_sorted[1:]):   # walk consecutive PAIRS of turns
    fto = nxt["start_ms"] - prev["end_ms"]
    overlap = max(0, -fto)                               # only negatives are overlaps; clamp the rest to 0
    if overlap > BARGE_IN_MS:
        failure_tags.append({
            "tag": "barge_in",
            "at_ms": nxt["start_ms"],                    # WHEN it happened
            "detail": f"{overlap}ms overlap",
            "evidence_turn_ids": [prev["turn_id"], nxt["turn_id"]],  # WHICH turns prove it
        })

print("ARTIFACT 3 — failure tags:")
for tag in failure_tags:
    print(" ", tag)
'''))

C.append(md('''
## EXPLAIN gate
One sentence: a failure tag carries three things a bare word "barge-in" does not. Name them.
(Hint: *what*, *when*, and *proof*.) Why does the *when* and the *proof* matter to anyone who
has to fix the agent?
'''))

C.append(md('''
## Artifact 4 of 5 — COST (what did this call cost to run?)

Every call costs money: the speech-to-text, the language model, the text-to-speech all bill per
use. The **cost** artifact is an **estimate** of that. We will do the crudest possible version —
a flat made-up price per turn — because today's lesson is *that cost is an artifact you attach to
a call*, not how to price it precisely. The real, slightly-less-crude version lives in
`pipeline/costs.py` (book 09).
'''))

C.append(md('''
## PREDICT
Our toy rule: each turn costs a flat **2 rupees** to process. The toy call has 4 turns.
What is the total cost? Commit to the number before the cell runs.
'''))

C.append(code('''
# YOUR TURN - predict the cost before computing it. Tiny arithmetic on purpose: the point is the
# SHAPE (cost = per-turn price x turns), not the math.
my_cost_guess = None   # <- replace None with a number of rupees

PRICE_PER_TURN = 2     # a made-up flat rate; real pricing is per-token/per-second (book 09)
n_turns = len(toy_call["turns"])
cost = PRICE_PER_TURN * n_turns    # crude estimate: flat price times number of turns

# every cost in this project is labelled an ESTIMATE so no one ever quotes it as a real invoice
cost_artifact = {"est_cost_rupees": cost, "note": "estimated, prototype"}
print("ARTIFACT 4 — cost:", cost_artifact)

if my_cost_guess is not None:
    print("your guess", "matched" if my_cost_guess == cost else "DIFFERED", "the computed cost")
else:
    print("(fill in my_cost_guess above to compare)")
'''))

C.append(md('''
## Artifact 5 of 5 — IMPROVEMENT PAIR (how the next model gets better)

The last artifact is the one that closes the loop. An **improvement pair** (also called a
**preference pair**) is two versions of an agent reply: a **rejected** (worse) one and a
**chosen** (better) one, for the *same* moment. A pile of these pairs is exactly the food a method
called **DPO** eats to make the next model prefer the better behaviour. You build real pairs in
books 05 and 17; here is the toy shape, drawn from our barge-in.
'''))

C.append(code('''
# An improvement pair: SAME situation, two replies - the bad one we saw, and a better one.
# The shape is literally {"rejected": ..., "chosen": ...}. This pair is the bridge from
# "we measured a failure" to "we can train the next agent to not do it" (that method is DPO).
improvement_pair = {
    "situation": "user is still speaking (mid-word) when the agent must respond",
    "rejected": "And your address please?",          # the barge-in: agent cut the user off
    "chosen":   "Sorry, please go on - which machine is it?",  # waits, yields the floor
    "why": "the chosen reply lets the user finish instead of interrupting (no barge-in)",
}
print("ARTIFACT 5 — improvement pair:")
for k, v in improvement_pair.items():
    print(f"  {k:<10}: {v}")
'''))

C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
Name all **five** artifacts in order, and for each give its one-line job. If you can do it from
memory, you are holding the spine of VoiceForge. If you stall, that is the spot to re-read.
'''))

C.append(md('''
## Putting it together: one call → five artifacts (the whole shape, on one screen)

Now the payoff. We collect everything we just built into a single structured object — five fields,
one per artifact — keyed to the call. THIS object is what VoiceForge produces from one call. Read
it slowly: the messy call went in; this tidy, program-readable thing came out.
'''))

C.append(md('''
## PREDICT
Before the next cell prints the assembled object: how many top-level fields will hang off the
`call_id` — and can you name them in order? Commit to the count and the names in your head, then
run and check yourself against the JSON.
'''))

C.append(code('''
# Assemble the five artifacts into ONE record. This is the entire thesis made concrete: a single
# call_id with exactly five structured fields hanging off it - each a thing a dashboard can read.
voiceforge_output = {
    "call_id": toy_call["call_id"],
    "outcome":          outcome,            # artifact 1 (from the checklist)
    "scorecard":        scorecard,          # artifact 2 (score + reason + evidence per dimension)
    "failure_tags":     failure_tags,       # artifact 3 (here, from the bad_call we analysed)
    "cost":             cost_artifact,      # artifact 4 (estimated)
    "improvement_pair": improvement_pair,   # artifact 5 (rejected -> chosen)
}
# pretty-print as JSON so the STRUCTURE is visible - indentation shows the five-way fan-out
import json   # imported here, where we first need to serialise, not at the top
print(json.dumps(voiceforge_output, indent=2))
'''))

C.append(md('''
## EXPLAIN gate
One sentence: point at the object above and say what makes it *structured* rather than *prose* —
and name one thing you could now do with 10,000 of these that you could never do with 10,000
recordings.
'''))

C.append(md('''
## CHECKPOINT 4 (out loud)
The transformation has a left side and a right side. Say the left side (the input) in your own
words, then the right side (the output) in your own words, then the arrow between them (what
VoiceForge actually *does*).
'''))

C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: "five artifacts" was a list of words from a table. After Act 2 you have *built* each one
by hand from a toy call — an outcome from a checklist, a scorecard as (score+reason+evidence), a
failure tag from FTO, a cost estimate, an improvement pair — and assembled them into the single
structured object VoiceForge emits. The shape **call → 5 artifacts** is now in your fingers.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (the five-artifact fan-out is a strong pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the picture on purpose, and a trap to disarm

## Break-it philosophy

You do not understand a boundary until you push on it. So we now feed VoiceForge things it was
never meant to handle, and watch *how* it refuses or misleads. Surprise on your own terms is
education; surprise on the demo stage is a disaster.
'''))

C.append(md('''
## PREDICT
Our outcome rule joins all turn text and checks for keywords. What happens to the **outcome** of
a perfectly successful call if the transcript is in a language whose words don't match our English
keywords — say the caller said "fridge" as "ఫ్రిజ్"? Does the call's quality change, or does only
our *measurement* break? Commit to one.
'''))

C.append(code('''
# BREAK-IT (guided) - same successful booking, but the appliance word is not the English "fridge".
# The CALL is fine; watch our keyword checklist mislabel it. This is a measurement failure, not a
# call failure - a distinction this whole course turns on.
other_language_call = {
    "turns": [
        {"speaker": "agent", "text": "Which appliance?",                 "start_ms": 0,    "end_ms": 1500},
        {"speaker": "user",  "text": "fridge ku problem - ten AM pin 55501", "start_ms": 1800, "end_ms": 4000},
    ],
}
blob = " ".join(t["text"].lower() for t in other_language_call["turns"])
# our crude rule only knows the literal English token "fridge stopped cooling" context;
# here we deliberately check a token the caller did NOT use, to force a wrong reading
appliance_seen = "refrigerator" in blob   # we look for the wrong synonym on purpose
print("blob:", blob)
print("appliance captured (by our brittle rule)?", appliance_seen)
print("-> the booking SUCCEEDED, but our English-only keyword says it didn't. Measurement broke, not the call.")
'''))

C.append(md('''
## Reading the break

Nothing crashed. No red. The cell printed `False` and moved on — a **silently wrong** answer.
That is more dangerous than a crash: a crash stops you; a silent wrong label flows straight onto
a dashboard and into a deck. The fix is not "panic" — it is to notice that our *measurement* is
brittle (English-only keywords), while the *call itself* was a clean success.

This is why the real cast has **Call B (Hinglish)** and **Call C (Telugu-English)**: multilingual,
messy calls are exactly where naive measurement quietly lies. Hold that — book 04 onward lives here.
'''))

C.append(md('''
## CHECKPOINT 5 (out loud)
State the difference between a **call failing** and our **measurement failing**. Which one did
the cell above show? Why is a silently-wrong label scarier than a loud crash?
'''))

C.append(md('''
## YOUR break now

Author your own. Take the toy outcome checklist and damage ONE thing so the outcome comes out
WRONG while the call is actually fine (or vice-versa). Predict the exact label it will produce and
why, write the prediction as a comment, then run.
'''))

C.append(code('''
# YOUR TURN - self-authored BREAK-IT (you author the damage this time).
# my prediction: <write here EXACTLY what outcome you expect and why, before running>

my_call_text = ["Hi, which appliance?", "My oven broke, 3pm works, number 99100"]  # edit me freely

# rebuild the blob + a checklist that you can sabotage (drop a field, mistype a keyword, etc.)
my_blob = " ".join(s.lower() for s in my_call_text)
my_captured = {
    "appliance":       "oven" in my_blob,     # <- try changing "oven" to a word NOT said
    "time":            "3pm" in my_blob,
    "callback_number": "99100" in my_blob,
}
my_n = sum(my_captured.values())
my_outcome = "success" if my_n == 3 else ("failure" if my_n == 0 else "partial")
print("captured:", my_captured)
print("outcome:", my_outcome, "- does it match your written prediction? if not, that gap is the lesson.")
'''))

C.append(md('''
## WRONG-INTUITION TRAP — the boundary people get wrong on day one

**The wrong belief:** "VoiceForge is the voice bot — it's the thing that talks to the caller."

This is the single most common misread of this project, so we disarm it directly. VoiceForge
**never speaks to a caller. It has no microphone and no voice.** It only ever runs *after* a call
is already recorded. Its input is a finished call log; its output is the five artifacts. The next
cell proves the boundary by showing the only two things VoiceForge ever touches.
'''))

C.append(code('''
# Prove the boundary in code. VoiceForge is a function from a FINISHED call to five artifacts.
# It is handed a recording that already happened; it can only ever READ. It has no way to emit
# speech, no live caller, no microphone - those belong to the voice agent, a SEPARATE system.
def voiceforge(finished_call):
    # input: a call that already ended (note: there is no 'speak' or 'reply' anywhere in here)
    # output: the five structured artifacts - measurement, never conversation
    return {"reads": "a finished call log", "produces": ["outcome", "scorecard",
            "failure_tags", "cost", "improvement_pair"], "ever_speaks_to_caller": False}

result = voiceforge(toy_call)
print(result)
print("VoiceForge consumes a finished call and produces artifacts. The talking belongs to the agent.")
'''))

C.append(md('''
## The reveal

The boundary, stated so it sticks: the **voice agent** is the system that *makes* the call (it has
the mic, the voice, the live caller). **VoiceForge** is the system that *grades* the call after it
is over (it has the five artifacts). Two different machines. Conflating them is the day-one error,
and it quietly corrupts every later conversation about what you are building — so we settle it now.
'''))

C.append(code('''
# YOUR TURN - disarm the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: what does VoiceForge NOT do, and what is it NOT?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP DISARMED:", my_trap_explanation)
'''))

C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: "after-the-call layer" was a phrase. After Act 3 you can defend its edges — you have seen
measurement lie *silently* on a multilingual call (the call was fine; the keyword broke), and you
can place the hard boundary between the **voice agent** (talks, has a mic) and **VoiceForge**
(grades, has artifacts). The most common day-one confusion is now one you can correct in others.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the agent/VoiceForge boundary is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this lives for real, and the bar you must clear

## The VoiceForge pipeline — the five artifacts are REAL files

This was not a metaphor. The toy artifacts you built map onto real code in this repo:

| artifact (today's toy) | where it lives for real | what it does |
|---|---|---|
| failure tags (FTO/barge-in) | `pipeline/signals.py` → `turn_metrics()`, `analyze()` | the deterministic timing core |
| scorecard | `pipeline/score.py` + `rubric.yaml` | merges signals + judged dims into scores |
| cost | `pipeline/costs.py` | per-call cost estimate (`"estimated, prototype"`) |
| improvement pair | `pipeline/dpo_export.py` | exports chosen/rejected pairs for training |
| the calls themselves | `data/normalized/*.json` (11 real calls) | the input side |

And the real hero call — `data/hero/turns.json` — is exactly the shape of our toy trace, just
longer (12 turns, Telugu-English) and *real*: it has a genuine **800 ms agent barge-in at 0:18**
and a **1,620 ms gap at 0:53**. You meet it for real from book 04 onward. Everything you hand-built
today, the repo does at scale.
'''))

C.append(md('''
## The recurring cast (you will travel with these three all course)

Three calls thread through every book. You met our toy `toy_1` (English, clean) as a stand-in for
**Call A**. The full cast:
'''))

C.append(code('''
# The three calls that recur for the whole course (ids/languages/outcomes are FIXED by the spec).
# Today is a handshake - book 01 turns these into real structured objects you walk field by field.
cast = [
    {"id": "call_A", "language": "English",        "story": "clean booking, cooperative caller",         "outcome": "success"},
    {"id": "call_B", "language": "Hinglish",       "story": "appointment with hesitations and a repeat",  "outcome": "partial"},
    {"id": "call_C", "language": "Telugu-English", "story": "service call; agent interrupts mid-answer",   "outcome": "failure"},
]
# print aligned so the THREE OUTCOMES (success/partial/failure) line up and contrast cleanly
for c in cast:
    print(f"{c['id']} | {c['language']:<15} | {c['story']:<45} | {c['outcome']}")
'''))

C.append(md('''
## PREDICT (course-level — write it in the next cell, no answer exists yet)

Of the five artifacts, which do you think is **hardest to produce honestly** — and why? (Think
about which one needs a *judgment*, not just arithmetic.) No grading today; your stored guess will
be waiting when the judge books — 10 through 15 — hand you the answer.
'''))

C.append(code('''
# YOUR TURN - course-level prediction, stored for the judge books to confront later.
my_hardest_artifact = ""   # which artifact + WHY it is hard to produce honestly

if len(my_hardest_artifact.strip()) < 20:
    print("write your prediction above (which artifact + why), then re-run.")
else:
    print("PREDICTION STORED:", my_hardest_artifact)
'''))

C.append(md('''
## Where this idea itself fails (honesty applies to the thesis too)

- **Artifacts are only as honest as their rules.** Today's English-only outcome keyword lied on a
  multilingual call. A scorecard built on a bad rubric is confident and wrong (books 12, 21).
- **A cost is an *estimate*, not an invoice** — it carries `"estimated, prototype"` for a reason;
  quoting it as truth is a way to mislead with a real-looking number (book 09).
- **"Structured" is not "correct."** A perfectly-formatted JSON artifact can be perfectly wrong —
  the format proves nothing about the content (this is P00's whole trap, and books 12–15 hammer it).
'''))

C.append(md('''
## The thesis at three levels (say the one that fits your listener)

- **To a beginner:** "The call is the easy, flashy part. VoiceForge is the boring machine that
  reads the finished call and tells you if it worked, how good it was, what broke, what it cost,
  and how to make the next one better."
- **To an engineer:** "A deterministic-plus-judged pipeline that maps a call log to five typed
  artifacts — outcome, scorecard (score+reason+evidence), time-stamped failure tags, a cost
  estimate, and chosen/rejected preference pairs — each a field a dashboard or trainer can read."
- **To a founder:** "The layer that turns raw calls into the numbers you put on a dashboard, the
  evidence you defend in the room, and the training data that makes version N+1 better than N. The
  demo is the call; the company is everything after it."
'''))

C.append(md('''
## Defense questions (×3 — answers below each, try first)

**1. "Isn't VoiceForge just the voice bot?"**
<details><summary>answer</summary>No. The voice bot makes the call (mic, voice, live caller). VoiceForge runs after the call ends and produces five structured artifacts. It never speaks to a caller. Different machine.</details>

**2. "Why not just keep the recordings and transcripts — why build all this?"**
<details><summary>answer</summary>Because you cannot sort, chart, total, or train on prose. To run at scale you need the same five structured artifacts for every call, computed the same way — that is what makes dashboards, decks, and a training loop possible.</details>

**3. "Your demo already books a repair on stage. What does this layer add?"**
<details><summary>answer</summary>The demo proves one call can work once. The layer proves it works across thousands, says how good, flags what broke and where, estimates cost, and produces the data to improve it. One call is a magic trick; the layer is a product.</details>
'''))

C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You now know that the five artifacts are **real files** (`signals.py`, `score.py`, `costs.py`,
`dpo_export.py`) over **real calls** (`data/normalized/*.json`, the hero `data/hero/turns.json`),
you have shaken hands with the recurring cast, and you can pitch the thesis to a beginner, an
engineer, and a founder. Above all you can defend the boundary: agent talks, VoiceForge grades.
'''))

C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The thesis in one sentence (when does VoiceForge run, and what does it transform?).
2. The five artifacts, in order, each with its one-line job.
3. The boundary: how is VoiceForge different from the voice agent?
4. The break: how can *measurement* fail while the *call* was fine? (your multilingual example)
5. Why a voice-AI **company** (not a demo) cannot skip this layer.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))

C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about what VoiceForge IS

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))

C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"VoiceForge is the layer after the call ends."**

Messy call in, five structured artifacts out. If your sentence captures that in your own words,
this book did its job.
'''))

C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "00_what_is_voiceforge.ipynb"   # <- this notebook's filename
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

**00 done** (pending your teach-back) → **01 · The call log** — we open up the left side of
today's picture: what a single recorded call actually *is* as data (turns, speakers, timing), the
object every one of the five artifacts is computed from. From here, the course builds the five,
one at a time.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "00_what_is_voiceforge.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
