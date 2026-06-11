#!/usr/bin/env python3
# Builds 04_turns_gaps_overlap_latency.ipynb per _BUILD_SPEC.md (four acts, marker conventions,
# recurring cast). The ONE atomic concept: FTO per handoff -> gap / overlap / barge-in / latency,
# read as p50/p90 against thresholds. This is the money-shot book: long and careful, and it uses
# the REAL hero call (data/hero/turns.json) and the REAL FTO core (pipeline/signals.py).
# Style/rhythm/cell-size matched to the gold reference P00_how_to_learn.ipynb.
# Rerun: .venv/bin/python notebooks/build_04.py
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
# 04 · Turns, gaps, overlap, latency

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Compute the **FTO** (floor transfer offset) between any two turns by hand:
   `next.start_ms − prev.end_ms`, and read its sign (**negative = overlap, positive = gap**).
2. Classify a handoff: **gap** vs **overlap**, **barge-in** (overlap > 100 ms) vs **backchannel**
   (overlap ≤ 100 ms), and flag **laggy** latency (a user→agent gap > 800 ms).
3. Summarize a whole call with **p50 and p90**, and say in one breath why the **mean** lies here.
4. Turn a **threshold** knob (`laggy_ms`) and watch the count of flagged calls move — and defend
   why that knob is a product decision, not a fact about the call.

This is the **money-shot** book. Everything before it (P01–P04, books 00–03) was scaffolding so
that today you can take one real recorded call and produce **numbers in milliseconds** that a
transcript could never give you. We work on the real hero call: `data/hero/turns.json`.
'''))

C.append(md('''
## 2 — Knowledge map (where this book sits)

`03 (pandas) → THIS: turns, gaps, overlap, latency → 05 (the voice stack)`

In **03** you learned to put rows of call data into a table and compute over columns. That gave
you the *tool*. This book gives you the first *measurement worth defending*: timing.

Why this book exists, and exists *here*: a transcript tells you **what** was said; it is silent on
**when**. Two calls with identical words can be a smooth conversation or a train wreck of
interruptions and dead air — and only the **timestamps** tell them apart. This is the book where
voice evaluation stops being "read the text and judge" and becomes **arithmetic on a clock**.
Next door, **05** opens the voice stack (ASR → LLM → TTS) and you will see *where in the machine*
these milliseconds are actually spent.
'''))

C.append(md('''
## 3 — Baby intuition

Sit in on a phone call you cannot hear — you only get a strip of paper that says, for each
person, **when they started talking and when they stopped**. Two numbers per turn.

From just those numbers you can already feel the conversation's *rhythm*:
- If the agent starts **before** the caller has finished, they **talked over** each other (an
  **overlap**). A long overlap means the agent **cut the caller off** — a barge-in.
- If the caller finishes and then there is **silence** before the agent replies, that is a **gap**.
  A long gap means the caller is sitting there thinking *"hello? is this thing broken?"* — that
  silence is **latency**, and it is felt, not read.

That gap-or-overlap number, measured at the seam between two turns, is the single most important
signal in voice. It has a name: **FTO**, the *floor transfer offset* — how the speaking "floor"
passes from one person to the next.
'''))

C.append(md('''
## 4 — The formal version

For two consecutive turns — a **prev** turn that ends and a **next** turn that begins:

> **fto_ms = next.start_ms − prev.end_ms**

Read the sign like a thermometer crossing zero:

| fto_ms | meaning | name |
|---|---|---|
| **positive** | next speaker waited; there was silence | **gap** |
| **zero** | seamless handoff | (perfect) |
| **negative** | next speaker started before prev finished | **overlap** |

From FTO we derive every timing signal in this course:

| signal | rule | threshold (from `rubric.yaml`) |
|---|---|---|
| **overlap_ms** | `max(0, −fto)` | — |
| **gap_ms** | `max(0, +fto)` | — |
| **barge-in** | overlap_ms **> 100 ms** | `threshold_overlap_ms: 100` |
| **backchannel** | overlap_ms **≤ 100 ms** ("mm-hm", ignored) | same line, other side |
| **latency** | gap_ms on a **user→agent** handoff | — |
| **laggy** | latency gap **> 800 ms** | `laggy_ms: 800` |

Two rules that save you from lying with these numbers, stated now and proven later:
- **One clock per call.** Every `start_ms`/`end_ms` is measured from the call's start. You never
  compare milliseconds across two different calls' clocks.
- **Report p50 and p90, never the mean.** One 1.6-second stall can hide inside a healthy-looking
  average. You will watch exactly that happen, with real numbers, in Act 3.
'''))

C.append(md('''
## 5 — Why this exists (the part founders care about)

"Our agent feels laggy" is a complaint. **"p90 user→agent latency is 1,620 ms; the threshold is
800; one call in four crosses it"** is a *spec* — something you can put on a dashboard, set a
target against, and prove you fixed.

Timing is also the part of voice quality that an LLM judge is **worst** at and a stopwatch is
**best** at. Words can be judged by reading; milliseconds cannot be felt from a transcript at all.
So this is where evaluation earns its keep: a **deterministic** signal (same input → same number,
forever), computed by `pipeline/signals.py`, with **zero** model calls and zero opinions. The
judge (books 10+) handles taste; the clock handles time. Today you build the clock.

The next cells start where the course always starts: a tiny toy made of two turns, computed by
hand, before any real file or any library function is allowed in.
'''))

C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. Write the FTO formula from memory. Which sign is a **gap** and which is an **overlap**?
2. What is the one number that separates a **barge-in** from a **backchannel**, and on which
   side does each fall?
3. Why must timing be reported as **p50/p90** and never as a single mean? (One sentence; the
   full proof is in Act 3.)
'''))

C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a call's quality is judged by reading what was said.
After Act 1 you should hold: a call carries a second, **silent** track — its **timing** — and one
subtraction at each seam (`next.start − prev.end`) turns that track into gaps, overlaps,
barge-ins, and latency. The clock is a measuring instrument, not an opinion.

If that feels like your own sentence, continue. If not, re-read the formal table in cell 4.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of what timing adds on top of
# a transcript. Producing the sentence is the learning; reading mine would only feel like it.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: FTO by hand, then with the real signals core

## Two turns, printed RAW first

Course rule: the ugly input goes on screen **before** anything is computed from it. Here are two
turns from a toy call. A turn is one speaker holding the floor once; the four facts that matter for
timing are `speaker`, `start_ms`, `end_ms`, and which turn comes next.
'''))

C.append(code('''
# Two consecutive toy turns as plain dictionaries. We print them RAW (one per line) so each TURN
# is visibly one THING before we do any arithmetic on it - seeing the input first is a course rule.
prev_turn = {"turn_id": "x1", "speaker": "user",  "start_ms": 1000, "end_ms": 3000}
next_turn = {"turn_id": "x2", "speaker": "agent", "start_ms": 3500, "end_ms": 6000}
print(prev_turn)
print(next_turn)
'''))

C.append(md('''
## PREDICT
The user stops at `end_ms = 3000`. The agent starts at `start_ms = 3500`.
1. Is the seam between them a **gap** or an **overlap**?
2. What is the FTO in milliseconds? Commit to a number before the next cell.
'''))

C.append(code('''
# YOUR TURN - lock your prediction BEFORE the compute cell runs, so the notebook records YOUR
# thinking and a later cell can compare it against reality. That comparison is the lesson.
my_fto_prediction = None     # <- replace None with your number (signed: positive=gap, negative=overlap)

if my_fto_prediction is None:
    print("fill in my_fto_prediction above, then re-run this cell.")
else:
    print("prediction locked:", my_fto_prediction)
'''))

C.append(code('''
# FTO by hand. We do the single subtraction the whole book rests on, with every step printed.
gap_or_overlap = next_turn["start_ms"] - prev_turn["end_ms"]   # the definition: next.start - prev.end

# We name the sign out loud, because the SIGN is the meaning - positive and negative are two
# different physical events (silence vs talking-over), not just +/- on one quantity.
label = "gap (silence)" if gap_or_overlap > 0 else ("overlap (talked over)" if gap_or_overlap < 0 else "seamless")
print("fto_ms =", gap_or_overlap, "->", label)

# The metal-detector reading: did YOUR committed prediction match?
if my_fto_prediction is not None:
    print("your prediction", "matched" if my_fto_prediction == gap_or_overlap else "DIFFERED",
          "- if it differed, that gap between your model and reality is exactly the thing to chew on")
'''))

C.append(md('''
## EXPLAIN gate
One sentence, out loud, in this shape:
> "The seam was a ___ because the agent started ___ ms ___ the user finished."

(500 ms of silence here. Felt on a real call, half a second of dead air is a noticeable pause.)
'''))

C.append(md('''
## PREDICT
Now flip the timing. Same two speakers, but the agent's `start_ms` becomes **2600** — it begins
*before* the user's `end_ms` of 3000.
1. Gap or overlap now?
2. What is the new FTO, and what is the **overlap_ms** (the size of the talk-over)?
'''))

C.append(code('''
# We nudge ONE number - the agent's start - earlier, into the user's turn. This is the 'change one
# thing' move: same call, one timestamp moved, and the seam flips from silence to talking-over.
next_turn_barge = {"turn_id": "x2", "speaker": "agent", "start_ms": 2600, "end_ms": 6000}

fto2 = next_turn_barge["start_ms"] - prev_turn["end_ms"]   # 2600 - 3000
# overlap_ms is how FAR negative the fto went; we clamp at 0 so a gap reports 0 overlap, not a
# negative one (gap and overlap are two separate non-negative quantities derived from one signed fto).
overlap_ms = max(0, -fto2)
print("fto_ms =", fto2, "| overlap_ms =", overlap_ms)
'''))

C.append(md('''
## OBSERVE
Same words could have been spoken in both versions. Moving the agent's start by 900 ms turned a
polite half-second pause into a **400 ms talk-over**. Nothing about the *transcript* changed —
only the clock. That is the whole reason this book exists.
'''))

C.append(md('''
## PREDICT — the 100 ms line
A 400 ms overlap: is that a **barge-in** (the agent rudely cut the caller off) or a
**backchannel** (a harmless "mm-hm" over the speaker)? The dividing line is **100 ms**.
Commit before the next cell.
'''))

C.append(code('''
# The barge-in vs backchannel decision is a single threshold comparison. We read the threshold
# from a variable named like the rubric key (threshold_overlap_ms) - at no point do we bury the
# number 100 inside an if-statement, because thresholds are config you will turn later, not facts.
threshold_overlap_ms = 100   # rubric.yaml -> dimensions.barge_in.threshold_overlap_ms

# A short overlap is a backchannel ("mm-hm" while the other talks); a long one is a real barge-in
# (you cut the person off). The > (strict) means exactly 100 is still a backchannel.
kind = "BARGE-IN (cut them off)" if overlap_ms > threshold_overlap_ms else "backchannel (harmless)"
print(f"overlap {overlap_ms}ms vs threshold {threshold_overlap_ms}ms  ->  {kind}")
'''))

C.append(md('''
## PREDICT — the 100 ms boundary itself
Two more overlaps to classify against the same 100 ms line: **80 ms** and **100 ms** exactly.
Which of these is a barge-in? (Watch the word "**strictly** greater than.")
'''))

C.append(code('''
# We probe the BOUNDARY on purpose - boundaries are where off-by-one bugs and arguments live.
# Same rule (strict >), three values straddling the line, so the threshold's behaviour is exposed.
for ov in [80, 100, 240]:
    verdict = "BARGE-IN" if ov > threshold_overlap_ms else "backchannel"
    print(f"  overlap {ov:>4}ms  ->  {verdict}")
# Note 100 is a backchannel (not >100) and 240 is the first barge-in here. The exact 0.1s line is a
# product choice; the code just applies whatever line the rubric sets.
'''))

C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. FTO from memory, with the sign rule.
2. Why are **gap_ms** and **overlap_ms** stored as two separate non-negative numbers instead of
   one signed value?
3. Why is the 100 ms barge-in line read from `rubric.yaml` instead of typed into the `if`?
'''))

C.append(md('''
## Manual-before-function — now LATENCY, the user→agent gap

Latency is just a **gap with a direction rule**: it only counts on a **user→agent** handoff (the
user finished a thought; how long until the agent responded?). A gap on the *other* direction
(agent→user) is the human thinking — not the system's fault, so latency ignores it.

We build it by hand on three toy handoffs before any function touches it.
'''))

C.append(md('''
## PREDICT
Three handoffs, each a (prev_speaker → next_speaker) with a gap:
- `user → agent`, gap **400 ms**
- `agent → user`, gap **2000 ms**  (the human took two seconds to answer)
- `user → agent`, gap **900 ms**

Using the rule "latency = gap on user→agent only," which gaps count as latency? And with a
**laggy** line of **800 ms**, how many laggy events are there?
'''))

C.append(code('''
# YOUR TURN - lock your two predictions before the compute cell.
my_latency_count = None   # how many of the three gaps are 'latency' (user->agent only)?
my_laggy_count   = None   # of those latency gaps, how many exceed the 800ms laggy line?

if my_latency_count is None or my_laggy_count is None:
    print("fill in BOTH counts above, then re-run this cell.")
else:
    print("locked:", my_latency_count, "latency events,", my_laggy_count, "laggy")
'''))

C.append(code('''
# Three toy handoffs. We keep prev/next speaker on each so the DIRECTION RULE is visible - latency
# is defined only on user->agent, so we must carry who-handed-to-whom, not just the gap size.
handoffs = [
    {"prev_spk": "user",  "next_spk": "agent", "gap_ms": 400},
    {"prev_spk": "agent", "next_spk": "user",  "gap_ms": 2000},   # human thinking - NOT latency
    {"prev_spk": "user",  "next_spk": "agent", "gap_ms": 900},
]
laggy_ms = 800   # rubric.yaml -> dimensions.latency_gap.laggy_ms

# Keep only the user->agent gaps: those are the system's response time. We filter FIRST, then judge,
# because mixing in the agent->user gap (the 2000) would slander the system for a human's pause.
latency_gaps = [h["gap_ms"] for h in handoffs if h["prev_spk"] == "user" and h["next_spk"] == "agent"]
laggy = [g for g in latency_gaps if g > laggy_ms]
print("latency gaps (user->agent only):", latency_gaps)
print("laggy (> 800ms):", laggy, "| count:", len(laggy))

if my_latency_count is not None:
    print("your latency count", "matched" if my_latency_count == len(latency_gaps) else "DIFFERED")
    print("your laggy count  ", "matched" if my_laggy_count == len(laggy) else "DIFFERED")
'''))

C.append(md('''
## OBSERVE + EXPLAIN
The 2000 ms gap was the **biggest** number in the list — and latency ignored it completely,
because it was the *human* pausing (agent→user), not the *system* stalling. One sentence: why does
direction matter more than size when measuring latency?
'''))

C.append(md('''
## Now the real signals core — `pipeline/signals.py`

You have now computed FTO, overlap, barge-in, and latency by hand. Only now do we open the
**real** function the VoiceForge pipeline uses: `turn_metrics()` in `pipeline/signals.py`. It does
exactly your by-hand subtraction for **every** consecutive pair in a call — no more, no less.

First we load the **real hero call** from disk.
'''))

C.append(code('''
# Load the REAL hero call. We resolve the path by walking up from the working directory so the
# notebook runs whether the kernel started in notebooks/ or the repo root (no hardcoded abs path).
import json
from pathlib import Path

name = "data/hero/turns.json"
hero_path = next(p for p in [Path.cwd()/name, *[a/name for a in Path.cwd().parents]] if p.exists())
hero = json.loads(hero_path.read_text())

# We print the call's identity and shape FIRST (not the turns) - know what call you are holding and
# how big it is before reading any single turn. This is the table-reading ritual on a call.
print("call_id:", hero["call_id"], "| language:", hero["language"], "| stress_profile:", hero["stress_profile"])
print("number of turns:", len(hero["turns"]))
'''))

C.append(md('''
## How to read one turn

A call is a list of turns. The reading ritual, three moves: say the **turn count** ("12 turns"),
say what **one turn IS** ("one speaker holding the floor once"), then read **one single turn**
aloud (its speaker and its start/end in ms).
'''))

C.append(code('''
# Print the first two REAL turns raw. t1 is the agent's long greeting; t2 is the caller answering
# in Telugu-English. We look at the actual ms here because the next cells subtract exactly these.
for t in hero["turns"][:2]:
    # text trimmed only so the timing fields (the point) are not lost off the side of the screen
    print(t["turn_id"], "|", t["speaker"], "| start", t["start_ms"], "| end", t["end_ms"], "|", t["text"][:40], "...")
'''))

C.append(md('''
## PREDICT — the real 0:18 seam (the famous one)
Look at the two turns you just printed plus the next one. Turn **t2** (user) **ends at 18949**.
Turn **t3** (agent) **starts at 18149**.
1. Gap or overlap?
2. What is the FTO, and the overlap_ms? Is it a barge-in by the 100 ms rule?

This is the real **0:18 barge-in** from the spec. Commit your numbers before running.
'''))

C.append(code('''
# YOUR TURN - lock the real-seam prediction before the function reveals it.
my_t2t3_overlap = None   # overlap in ms between t2 (ends 18949) and t3 (starts 18149)

if my_t2t3_overlap is None:
    print("fill in my_t2t3_overlap above (a positive ms number), then re-run.")
else:
    print("locked:", my_t2t3_overlap, "ms overlap predicted")
'''))

C.append(code('''
# The real function, first time. turn_metrics() walks consecutive pairs and computes the same
# fto/overlap/gap you did by hand - we import it here, where it is first needed, from the pipeline.
import sys
root = next(a for a in [Path.cwd(), *Path.cwd().parents] if (a/"pipeline"/"signals.py").exists())
sys.path.insert(0, str(root))   # make the repo's pipeline package importable from inside notebooks/
from pipeline.signals import turn_metrics

# events is one row per SEAM (11 seams for 12 turns). We are about to find the t2->t3 row.
events = turn_metrics(hero["turns"])
print("number of seams (events):", len(events), "  (= turns - 1)")

# Pull the specific t2->t3 seam so we can check it against your prediction and the by-hand value.
t2t3 = next(e for e in events if e["prev_turn_id"] == "t2" and e["next_turn_id"] == "t3")
print("t2->t3:", "fto_ms", t2t3["fto_ms"], "| overlap_ms", t2t3["overlap_ms"], "| gap_ms", t2t3["gap_ms"])
print("barge-in?", t2t3["overlap_ms"] > 100, f"(overlap {t2t3['overlap_ms']}ms vs 100ms line)")

if my_t2t3_overlap is not None:
    print("your overlap prediction", "matched" if my_t2t3_overlap == t2t3["overlap_ms"] else "DIFFERED")
'''))

C.append(md('''
## CHECKPOINT 3 (out loud)
1. `turn_metrics()` on a 12-turn call returns how many rows, and why that number?
2. The t2→t3 seam: the agent started **before** the user finished. Look at t2's text — the caller
   was still giving their address. What did the agent's 800 ms barge-in *cost* the call?
3. Did the real function compute anything your by-hand subtraction did not? (The honest answer is
   the point.)
'''))

C.append(md('''
## See every seam at once

Eleven seams, one table. We print all of them so the **shape** of the call is visible: where the
overlaps are (just one — the famous t2→t3), and where the long gaps hide.
'''))

C.append(code('''
# Print every seam as an aligned row. We show direction (prev->next speaker) next to fto, because
# fto alone is ambiguous until you know WHO handed to WHOM (it decides whether a gap is 'latency').
print(f"{'seam':<9}{'dir':<16}{'fto_ms':>8}{'gap':>7}{'overlap':>9}")
for e in events:
    direction = f"{e['prev_spk']}->{e['next_spk']}"
    print(f"{e['prev_turn_id']+'->'+e['next_turn_id']:<9}{direction:<16}{e['fto_ms']:>8}{e['gap_ms']:>7}{e['overlap_ms']:>9}")
'''))

C.append(md('''
## PREDICT — find the long gap
Scan the table you just printed. One user→agent seam has a **much** larger gap than the others —
the real **0:53 stall** from the spec. Which seam (`tX->tY`), and roughly how many ms?
'''))

C.append(code('''
# We pull out the user->agent handoffs (the latency-eligible ones) and rank them, so the worst
# stall surfaces by itself rather than being eyeballed. Direction filter first, same as by hand.
user_to_agent = [e for e in events if e["prev_spk"] == "user" and e["next_spk"] == "agent"]
worst = max(user_to_agent, key=lambda e: e["gap_ms"])   # the single longest the caller waited
print("user->agent handoffs:", [(e["prev_turn_id"]+"->"+e["next_turn_id"], e["gap_ms"]) for e in user_to_agent])
print("worst stall:", worst["prev_turn_id"]+"->"+worst["next_turn_id"], "=", f"{worst['gap_ms']:,}ms",
      "at", f"{worst['at_ms']//60000}:{(worst['at_ms']%60000)//1000:02d}")
'''))

C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: timing was a vibe ("feels laggy"). After Act 2 you can: compute FTO by hand, split it into
gap/overlap, apply the 100 ms barge-in line and the user→agent latency rule, and confirm the **real**
`turn_metrics()` does exactly your arithmetic on all 11 seams of the hero call — finding the real
800 ms barge-in at 0:18 and the 1,620 ms stall at 0:53, the same two events the spec names.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (FTO / direction rule / the real seam table)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: the mean trap, the threshold knob, and the missing clock

## Summarizing a call: p50 and p90 (and the trap living inside "average")

You have 4 user→agent latency gaps on the hero call. To report the call's latency in **one
number**, the tempting move is the **mean**. The next cells show why that one number can hand a
stakeholder a comfortable lie — and what to report instead.
'''))

C.append(md('''
## WRONG-INTUITION TRAP — "the average response time tells me how the agent feels"

**The wrong belief:** "mean latency is low, so the agent feels responsive."

The hero call's four user→agent gaps are **400, 1620, 350, 400** ms. One of them — the 1,620 ms
stall at 0:53 — is the moment a real caller wondered if the line had dropped. Watch whether the
**mean** lets you see it, or buries it.
'''))

C.append(md('''
## PREDICT
For gaps `[400, 1620, 350, 400]`:
1. The **mean** is …? (add them, divide by 4)
2. The **median (p50)** is …? (sort, take the middle)
3. The **p90** is …?
Then ask: against an 800 ms threshold, does the **mean** look fine? Does p90?
'''))

C.append(code('''
# YOUR TURN - lock all three before the reveal. This is the trap; predicting first is how you feel
# it spring rather than just reading the result.
my_mean   = None    # 400+1620+350+400 over 4
my_median = None    # the p50
my_p90    = None    # the 90th-percentile value

if any(v is None for v in (my_mean, my_median, my_p90)):
    print("fill in all three (mean, median, p90) above, then re-run.")
else:
    print("locked  mean:", my_mean, " median:", my_median, " p90:", my_p90)
'''))

C.append(code('''
# Compute all three by hand-visible steps. statistics is the stdlib; we still SHOW the sort so the
# percentile is not a black box - p50/p90 are just positions in the sorted list, nothing magic.
import statistics
import math

gaps = [400, 1620, 350, 400]
ordered = sorted(gaps)                       # percentiles only mean anything on ordered data
print("sorted gaps:", ordered)

mean_gap = sum(gaps) / len(gaps)             # the trap: one big value drags this up (or here, masks itself)
median_gap = statistics.median(gaps)         # p50 = the middle; half are below it, half above
# p90 the same way pipeline/signals.py does it: ceil(0.9*n)-1 index into the sorted list.
p90_gap = ordered[max(0, math.ceil(0.9 * len(ordered)) - 1)]

print(f"mean:   {mean_gap:.1f} ms   <- under 800, looks 'fine'")
print(f"median: {median_gap:.1f} ms   <- the typical handoff is snappy")
print(f"p90:    {p90_gap} ms   <- the bad tail the caller actually felt")
'''))

C.append(md('''
## The reveal

The **mean is 692.5 ms** — under the 800 ms line, so a mean-only dashboard reports "**latency OK**"
and the 1,620 ms stall **vanishes**. But the **p90 is 1,620 ms** — it refuses to hide the worst
moment, because p90 asks *"how bad is a near-worst call?"* not *"what cancels out on average?"*.

This is the same trap from P00 (the coffee priced at ₹1000 that wrecked the mean), now with real
consequences: **mean smears one disaster across many good handoffs until it disappears.** p50 tells
you the typical experience; p90 tells you the experience you must apologize for. Report both;
report the mean alone and you will ship a stall you swore was not there. This is why
`pipeline/signals.py` returns `median_gap_ms` and `p90_gap_ms` — and **no mean at all.**
'''))

C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why does the mean hide the 1620ms stall but p90 does not?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))

C.append(md('''
## CHECKPOINT 4 (out loud)
The mean said 692 (fine), p90 said 1,620 (alarming) — from the **same four numbers**. Explain to a
skeptical PM, in one sentence each, what question p50 answers and what question p90 answers. Why
does shipping the **mean alone** here amount to hiding a real failure?
'''))

C.append(md('''
## The threshold is a knob — turn it, watch the flags move

`laggy_ms = 800` is **not** a fact about the call; it is a **product decision** sitting in
`rubric.yaml`. The same recorded call gets *more or fewer* failures the instant you turn that knob.
We prove it by re-flagging the **real** hero gaps at several thresholds.
'''))

C.append(md('''
## PREDICT
The real user→agent gaps are `[400, 1620, 350, 400]`. How many are flagged **laggy** when
`laggy_ms` is:
- **800** (today's rubric)?
- **300** (a strict "snappy or bust" product)?
Commit both counts before running.
'''))

C.append(code('''
# YOUR TURN - lock both counts before the sweep.
flagged_at_800 = None   # how many of [400,1620,350,400] exceed 800?
flagged_at_300 = None   # how many exceed 300?

if flagged_at_800 is None or flagged_at_300 is None:
    print("fill in BOTH counts above, then re-run.")
else:
    print("locked:", flagged_at_800, "at 800ms,", flagged_at_300, "at 300ms")
'''))

C.append(code('''
# Re-flag the SAME gaps at a sweep of thresholds. The call is frozen; only the knob moves. This is
# the whole point: a 'failure count' is meaningless until you state the threshold it was counted at.
real_gaps = [400, 1620, 350, 400]   # the four user->agent gaps from the hero call
for thr in [800, 500, 300, 200]:
    flagged = [g for g in real_gaps if g > thr]
    print(f"laggy_ms = {thr:>4}  ->  {len(flagged)} flagged  {flagged}")

if flagged_at_800 is not None:
    print("check 800:", "matched" if flagged_at_800 == sum(g > 800 for g in real_gaps) else "DIFFERED")
    print("check 300:", "matched" if flagged_at_300 == sum(g > 300 for g in real_gaps) else "DIFFERED")
'''))

C.append(md('''
## OBSERVE
At **800 ms**, **one** call is flagged. Drop the knob to **300 ms** and **all four** are flagged —
the *identical* recording, four times worse on the dashboard, with **zero** change to the call.
This is why every failure count in this course is reported **with its threshold attached**, and why
the rubric is a single editable file you can defend line by line on demo day.
'''))

C.append(md('''
## BREAK-IT (guided) — the missing `end_ms`

Real call data is dirty. A common defect: a turn arrives with a `start_ms` but **no `end_ms`**
(the source only logged when each speaker *started*). FTO needs `prev.end_ms` — so what does the
real function do when it is missing? Predict first: does it **crash**, **invent** an end time, or
**skip** that seam?
'''))

C.append(md('''
## PREDICT
We delete `end_ms` from the hero's turn **t6** (the one right before the big 0:53 gap), then run
`turn_metrics()` again. Will the number of seams **go down**, stay the same, or will it **error**?
And what happens to the t6→t7 stall we found earlier?
'''))

C.append(code('''
# BREAK-IT (guided): damage the data the way a real ASR export might, then watch the contract hold.
import copy

broken = copy.deepcopy(hero["turns"])     # deepcopy so we damage a COPY, not the real loaded call
t6 = next(t for t in broken if t["turn_id"] == "t6")
del t6["end_ms"]                          # the damage: t6 now has a start but no end

# turn_metrics' rule (signals.py): if a turn's end_ms is None/missing, its outgoing seam is SKIPPED -
# overlap is NEVER inferred or faked from a missing timestamp. We expect FEWER seams, not a crash.
broken_events = turn_metrics(broken)
print("seams with all end_ms present:", len(events))
print("seams after deleting t6.end_ms:", len(broken_events))
print("t6->t7 still present?", any(e["prev_turn_id"] == "t6" for e in broken_events))
'''))

C.append(md('''
## Reading the result — silence is a design choice

The seam count **dropped** (the t6→t7 pair vanished) and nothing crashed. The function chose to
**skip** rather than **guess**: with no `end_ms`, it cannot know if t7 overlapped t6 or followed a
silence, so it reports **neither**. Inventing an `end_ms` would have manufactured a barge-in or a
gap that **never happened** — a fabricated failure is worse than a missing one. "When you cannot
measure it, do not pretend you did" is the rule baked into `signals.py`.
'''))

C.append(md('''
## BREAK-IT (learner-authored) — your own damage

Author your own break. Pick **one** turn and **one** field to corrupt — for example, make a
`start_ms` **earlier than the previous turn's start** (clocks out of order), or set an `end_ms`
**before** its own `start_ms` (a negative-duration turn). Predict what FTO/overlap will do, write
the prediction as a comment, then run.
'''))

C.append(code('''
# YOUR TURN - self-authored BREAK-IT.
# my prediction: <write here exactly what you expect to happen to fto/overlap/gap, and why>
import copy

my_turns = copy.deepcopy(hero["turns"])   # again, damage a copy so the real call stays intact

# 1) damage ONE field of ONE turn here (uncomment and edit):
# my_turns[3]["start_ms"] = 0          # e.g. force t4 to start at the very beginning of the call
# my_turns[5]["end_ms"] = 40000        # e.g. make t6 end BEFORE it starts (negative duration)

# 2) recompute and read the seams around your edit against your written prediction:
my_events = turn_metrics(my_turns)
print("seams:", len(my_events))
for e in my_events[2:6]:   # a window around the middle, where edits above tend to land
    print(" ", e["prev_turn_id"]+"->"+e["next_turn_id"], "fto", e["fto_ms"], "overlap", e["overlap_ms"], "gap", e["gap_ms"])
'''))

C.append(md('''
## CHECKPOINT 5 (out loud)
1. When a turn is missing `end_ms`, what does `turn_metrics()` do, and **why is that safer** than
   filling in a guess?
2. You moved one threshold and the failure count went 1 → 4 on a frozen call. So is "4 laggy calls"
   a fact about the **call** or about the **rubric**? How do you report it honestly?
3. Name one way a *negative-duration* turn (end before start) could silently poison the numbers.
'''))

C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a single average felt like a fair summary, and a "failure count" felt like a fact. After
Act 3: the **mean hides tail disasters** (report p50 **and** p90), every count is meaningless
**without its threshold**, and the timing core **refuses to invent** numbers it cannot measure
(missing `end_ms` → skip, never fake). Honesty is now a property of the *math*, not a footnote.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the mean trap, or 'thresholds are knobs', your pick)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the real pipeline, the chart, and defending the numbers

## Where this lives in VoiceForge (these are real files)

Nothing today was a metaphor. The arithmetic you ran is the production timing core:

| what you built today | where it lives for real | what it does |
|---|---|---|
| FTO per seam (gap/overlap) | `pipeline/signals.py` → `turn_metrics()` | one row per consecutive pair |
| barge-in + latency + p50/p90 | `pipeline/signals.py` → `analyze()` | applies thresholds, summarizes |
| the thresholds (100 ms, 800 ms) | `rubric.yaml` → `dimensions.barge_in`, `dimensions.latency_gap` | the editable knobs |
| the call itself | `data/hero/turns.json` (12 real turns, te-en) | the input |

`analyze()` is just everything you did, assembled: run `turn_metrics()`, flag overlaps over 100 ms
as barge-ins, take user→agent gaps, report median + p90, and emit a **failure table** with
`evidence_turn_ids`. We call the real thing now and confirm it matches your hand-work.
'''))

C.append(code('''
# Call the real analyze() - the full deterministic summary the pipeline produces for one call.
# It needs the rubric (for the thresholds); we load the SAME rubric.yaml the production code reads.
from pipeline.signals import analyze, load_rubric

result = analyze(hero["turns"], load_rubric())   # same function, same config the dashboard uses
lat = result["latency"]
print("handoffs:", lat["n_handoffs"], "| median:", lat["median_gap_ms"], "ms | p90:", lat["p90_gap_ms"], "ms")
print("barge-ins:", len(result["barge_ins"]), "| laggy (> {}ms):".format(lat["laggy_threshold_ms"]), lat["n_laggy"])
'''))

C.append(md('''
## The failure table — the artifact, with evidence

A score with no evidence is an opinion. Every failure `analyze()` emits carries
`evidence_turn_ids` — the exact turns you can pull the audio for. This is the "money shot": two
timed, defensible failures, each pointing at the seconds you can replay.
'''))

C.append(code('''
# Print the real failure table with timestamps and evidence turn ids. mmss converts ms->m:ss so a
# stakeholder can scrub straight to the moment - evidence_turn_ids is what makes a flag defensible.
def mmss(ms):
    return f"{ms // 60000}:{(ms % 60000) // 1000:02d}"   # ms -> minutes:seconds for human reading

for f in result["failures"]:
    ev = "->".join(str(t) for t in f["evidence_turn_ids"])
    print(f"{mmss(f['at_ms']):>5}  -  {f['label']:<16}  -  {f['detail']:<14}  ({ev})")
'''))

C.append(md('''
## PREDICT — the chart
We will draw the 4 user→agent latency gaps as bars, with the 800 ms `laggy` line drawn across.
Before the chart: how many bars **poke above** the red line, and which seam is the tall one?
'''))

C.append(code('''
# One bar per user->agent handoff, with the threshold drawn as a line. We chart only the latency-
# eligible gaps (not all 11 seams) because mixing in agent->user 'thinking' gaps would mis-frame
# the chart as system latency when it is not. Every line says why it exists.
import matplotlib.pyplot as plt

labels = [e["prev_turn_id"]+"->"+e["next_turn_id"] for e in user_to_agent]   # x: the handoffs (THINGS)
gaps_ms = [e["gap_ms"] for e in user_to_agent]                                # y: the wait in ms (MEASURE)

fig, ax = plt.subplots(figsize=(5, 3))   # fig = canvas, ax = the drawing area on it
ax.bar(labels, gaps_ms)                  # one bar per handoff; height = ms the caller waited
ax.axhline(800, linestyle="--")          # the laggy threshold as a horizontal line - the bar/line
ax.text(0, 820, "laggy = 800ms")         # crossing is the entire claim this chart makes
ax.set_xlabel("user->agent handoff")     # unlabeled axes are how charts lie by omission,
ax.set_ylabel("latency gap (ms)")        # so labeling is a duty, not decoration
ax.set_title("hero call: response latency per handoff")
plt.show()
'''))

C.append(md('''
## Read the chart — the 4-question ritual
1. **x?** the four user→agent handoffs. 2. **y?** latency in ms. 3. **one bar?** one moment the
caller waited for the agent. 4. **what does it license?** Exactly one claim: *one* handoff (t6→t7)
crosses the 800 ms line. It does **not** license "the agent is slow" — three of four are snappy.
The chart shows a **tail problem**, not a baseline problem. (That is p50-vs-p90, drawn.)
'''))

C.append(md('''
## The three-level explanation (same concept, three rooms)

- **To a beginner:** "We measure the silence and the talking-over between turns. Long silence =
  the caller waiting; talking-over = the agent cutting them off. We count the bad ones."
- **To an engineer:** "Per consecutive pair, `fto = next.start_ms − prev.end_ms`. overlap = −fto
  clamped at 0; barge-in if overlap > 100 ms. Latency = gap on user→agent handoffs; laggy if
  > 800 ms. Summarize with median and p90, never mean. Missing `end_ms` → skip the seam, never
  infer. Deterministic, no model calls — `pipeline/signals.py`."
- **To a founder:** "We turn 'it feels laggy' into a number we can put a target on: p90 latency,
  barge-in rate, each tied to the exact second of evidence. Deterministic, free to compute, and the
  thresholds are one editable file we can defend live."
'''))

C.append(md('''
## Defense questions (×3 — try first, then open)

**1. "Why median and p90 — why not just the average response time?"**
<details><summary>answer</summary>The average smears one disaster across many good handoffs until it
disappears: the hero call's mean is 692 ms (under our 800 ms line) while its p90 is 1,620 ms. p50
reports the typical experience; p90 reports the near-worst one we must fix. The mean alone would let
us ship a stall we swore was not there.</details>

**2. "Your barge-in flag fired once — how do I know it is real and not a clock artifact?"**
<details><summary>answer</summary>It is an 800 ms overlap (well past the 100 ms backchannel line) and
it carries `evidence_turn_ids` [t2, t3] — you can replay 0:18 and hear the agent cut the caller off
mid-address. The signal is deterministic from the timestamps; the evidence is auditable audio.</details>

**3. "If I change `laggy_ms` to 300, four calls fail instead of one — isn't your metric arbitrary?"**
<details><summary>answer</summary>The threshold is a product decision, not a measurement. The
*measurement* (the gaps: 400/1620/350/400) is fixed and reproducible; the *threshold* lives in
`rubric.yaml` and we report every count with its threshold attached. Choosing 800 vs 300 is a
business call about how snappy we promise to be — and it is one editable line we can defend.</details>
'''))

C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own the whole loop: a raw call → `turn_metrics()` (your by-hand FTO, at scale) →
`analyze()` (thresholds + p50/p90 + a failure table with evidence) → a chart that licenses exactly
one claim. You can place every piece in a real file, and defend every number — including the ones a
turned knob would change. The clock is no longer a vibe; it is an instrument you can hand to a PM.
'''))

C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The FTO formula, with the sign rule (gap vs overlap).
2. Barge-in vs backchannel (the 100 ms line) and latency vs laggy (user→agent, 800 ms).
3. Why p50 **and** p90, and the exact way the **mean** hid the hero call's 1,620 ms stall.
4. What `turn_metrics()` does with a missing `end_ms`, and why skipping beats guessing.
5. Why "4 laggy calls" is a statement about the **rubric**, not only the call.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))

C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (the real pipeline / evidence / defending numbers)
my_clean_sentence = ""      # the sentence you would say in a room about timing in voice

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))

C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Voice failures are measurable in milliseconds, not just judgeable from text."**

The hero call proved it: one subtraction per seam exposed an 800 ms barge-in at 0:18 and a 1,620 ms
stall at 0:53 — two failures no amount of reading the transcript would have handed you a number for.
If your sentence captures that in your own words, this book did its job.
'''))

C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "04_turns_gaps_overlap_latency.ipynb"   # <- this notebook's filename
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

**04 done** (pending your teach-back) → **05 · The voice stack (ASR → LLM → TTS)** — now that you
can *measure* latency, 05 shows you *where* in the machine those milliseconds are spent, so you know
which box to fix when p90 is too high.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "04_turns_gaps_overlap_latency.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
