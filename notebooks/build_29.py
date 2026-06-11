#!/usr/bin/env python3
# Builds 29_the_3_minute_demo.ipynb per _BUILD_SPEC.md (four acts, marker conventions, recurring
# cast). The ONE atomic concept: the demo spine, rehearsed out loud — the locked beat order
# (audible failure -> timestamp -> scorecard -> better response -> DPO pair -> chart ->
# calibration -> close), timed to a budget, anchored to the REAL artifacts (data/hero/turns.json's
# 0:18 barge-in 800ms and 0:53 stall 1620ms; web/shot.html). The learner types their OWN version of
# every beat into guarded string vars, and a break-it shows a beat in the WRONG order / overclaiming.
# Style/rhythm/cell-size matched to the gold reference P00_how_to_learn.ipynb and sibling 04.
# Rerun: .venv/bin/python notebooks/build_29.py
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
# 29 · The 3-minute demo

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Recite the **locked beat order** of the demo from memory:
   **audible failure → timestamp → scorecard → better response → DPO pair → chart → calibration → close**.
2. Say the **two locked lines** verbatim (the opener and the closer) without reaching for notes.
3. Hold a **timing budget** — seconds per beat that sums to ~180 — and know which beat you cut
   first when the clock is against you.
4. Anchor every beat to a **real artifact** (`data/hero/turns.json`: 0:18 barge-in 800 ms, 0:53
   stall 1,620 ms; `web/shot.html`) so nothing you claim is hand-waved.
5. Spot a beat told in the **wrong order** or that **overclaims**, and repair it on the spot.

This is a **rehearsal** book, not a coding book. The deliverable is a demo you can deliver out
loud, the same way every time, in three minutes, under pressure — with each line backed by a
number on disk.
'''))

C.append(md('''
## 2 — Knowledge map (where this book sits)

`28 (engineer-talk) → THIS: the 3-minute demo → 30 (post-hackathon)`

In **28** you learned to *talk like an engineer about this system* — the vocabulary, the honest
caveats, the way you answer a sharp question without flinching. That gave you the **words**. This
book gives you the **performance**: a single rehearsed spine that spends those words in the right
order, on a clock, pointed at real evidence.

Why this book exists, and exists *here*: a hackathon demo is not a conversation — it is a
**three-minute window** where attention is borrowed and a judge decides in the first thirty
seconds whether to keep listening. Improvising that window is how good projects die on stage. A
**rehearsed spine** — the same beats, the same two lines, the same artifacts — turns three nervous
minutes into a thing you have already done twenty times. Next door, **30** is what happens *after*
the room: the follow-ups, the repo, the longer story. But you only earn book 30 if book 29 lands.
'''))

C.append(md('''
## 3 — Baby intuition

A demo is a **song**, not a speech. A speech you can ad-lib; a song has a fixed order of notes,
and if you play them out of order it stops being the song. The 3-minute demo has eight notes:

> **pain → measurement → correction → dataset → scale** — told as eight beats.

You start by making the room **hear** something break (a real call where the agent talks over the
caller). Then you stop being a storyteller and become an instrument: you point at the **exact
millisecond** it broke, show the **scorecard** that caught it, show the **better response**, show
the **training pair** that better response becomes, the **chart** that proves it generalizes, and
the **calibration** number that says a human agrees with your judge. Then you **close** with one
sentence and stop talking.

The whole trick is: **the order is locked, so you never have to think about what comes next** —
you only have to deliver the beat you are on. Thinking happens in rehearsal; the stage is muscle.
'''))

C.append(md('''
## 4 — The formal version: the locked spine

Eight beats, in this exact order. Memorize the order before you memorize the words.

| # | beat | what the room sees/hears | real anchor |
|---|---|---|---|
| 1 | **audible failure** | play the call; the agent cuts the caller off mid-address | `data/hero/turns.json` 0:18 |
| 2 | **timestamp** | point at the exact ms: an 800 ms barge-in at 0:18 | `signals.py` → `turn_metrics()` |
| 3 | **scorecard** | the deterministic flag fired, with `evidence_turn_ids` [t2, t3] | `analyze()` failure table |
| 4 | **better response** | the agent SHOULD have acknowledged + asked one field | the improvement example |
| 5 | **DPO pair** | that better response is a `chosen`; the rude one is `rejected` | preference pair |
| 6 | **chart** | p90 latency / barge-in rate before vs after — it generalizes | `web/shot.html` |
| 7 | **calibration** | a human agreed with our judge (kappa), so the numbers are trusted | pilot calibration |
| 8 | **close** | the one sentence, then stop talking | the clean sentence |

Two rules that separate a spine from a ramble:
- **One clock for the whole demo.** Every beat has a second-budget; they sum to ~180. You rehearse
  against the clock, not against a feeling of "about three minutes."
- **Every claim points at an artifact.** No beat is a vibe. Beat 2 is a number from `signals.py`;
  beat 6 is a chart in `web/shot.html`; beat 7 is a kappa you computed. If a beat has no artifact,
  it gets cut.
'''))

C.append(md('''
## 5 — The two locked lines

Most of the demo you can paraphrase. **Two lines you say word-for-word, every time**, because they
are load-bearing — the opener that frames the whole thing, and the closer that lands it.

> **OPENER (beat 1, said before you press play):**
> *"This is a real call our voice agent took. Listen to the eight-hundred-millisecond moment it
> goes wrong — then watch us measure it, fix it, and turn the fix into training data."*

> **CLOSER (beat 8, said after the chart, then you stop):**
> *"Pain, measured. Correction, captured. Dataset, growing. That's the loop — and it runs without
> us in three minutes."*

Why lock exactly these two: the opener **buys the next 30 seconds** (it tells the judge a payoff is
coming, so they wait for it), and the closer **states the loop** so the last thing in the room's ear
is your thesis, not an "um." Everything between them you can flex; these two you drill until they
are reflex.

The next cells start where the course always starts: the smallest possible version, by hand, before
the real artifacts come in.
'''))

C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. Recite the **eight beats in order** from memory. (If you can only get six, that is the gap to
   close before anything else in this book.)
2. What are the **two locked lines**, and why those two specifically (what does each *buy* you)?
3. State the rule that decides whether a beat **earns its place** or gets cut. (Hint: it is about
   artifacts, not eloquence.)
'''))

C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a demo is "explain the project well for three minutes."
After Act 1 you should hold: a demo is a **locked spine of eight beats**, two of which are said
**word-for-word**, each pointed at a **real artifact**, delivered against a **clock**. The order is
fixed so the stage becomes muscle memory and your only on-stage job is delivering the beat you are on.

If that feels like your own sentence, continue. If not, re-read the spine table in cell 4.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of what a demo IS now (a locked
# spine vs a speech). Producing the sentence is the learning; reading mine would only feel like it.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: build the spine by hand, then load the real artifacts

## The spine as plain data, printed RAW first

Course rule: the ugly input goes on screen **before** anything is computed from it. The spine is
not prose yet — it is a **list of beats**, each with a name and a second-budget. We print it raw so
the *shape* (eight beats, summing to a budget) is visible before we rehearse a single word.
'''))

C.append(code('''
# The locked spine as a list of (beat_name, seconds) pairs. Order is the WHOLE point, so we keep it
# as an ordered list, never a dict-by-name - a set or unordered map would silently lose the one
# property (sequence) this entire book is about.
spine = [
    ("audible failure", 25),   # play the call, say the opener line
    ("timestamp",       20),   # point at the 800ms barge-in at 0:18
    ("scorecard",       25),   # the deterministic flag + evidence_turn_ids
    ("better response", 25),   # what the agent SHOULD have said
    ("DPO pair",        25),   # chosen vs rejected - the fix becomes training data
    ("chart",           25),   # before/after p90 + barge-in rate
    ("calibration",     20),   # a human agreed (kappa) - trust the number
    ("close",           15),   # the closer line, then stop
]
for i, (beat, secs) in enumerate(spine, start=1):
    print(f"beat {i}: {beat:<16} ~{secs:>3}s")
'''))

C.append(md('''
## PREDICT
Add up the second-budgets you just printed. **Does the spine fit in 180 seconds?** Commit to the
sum (and to over/under) before the next cell computes it.
'''))

C.append(code('''
# YOUR TURN - lock your prediction BEFORE the compute cell, so the notebook records YOUR thinking
# and a later cell can compare it. The arithmetic of a demo IS the demo - 8 beats must literally fit.
my_total_seconds = None    # <- replace None with your summed estimate
my_fits_180 = None         # <- replace None with True or False

if my_total_seconds is None or my_fits_180 is None:
    print("fill in BOTH (the sum, and True/False) above, then re-run this cell.")
else:
    print("locked:", my_total_seconds, "s total, fits 180?", my_fits_180)
'''))

C.append(code('''
# Sum the budgets BY HAND (a plain loop, no library), because the point is to FEEL the clock fill up
# beat by beat - a one-liner sum() would hide which beat pushes you over budget.
total = 0
for beat, secs in spine:
    total += secs
    # printing the running total exposes the moment the budget gets tight - that is where you trim
    print(f"after {beat:<16} running total = {total:>3}s")

budget = 180
print("----")
print("spine total:", total, "s | budget:", budget, "s | slack:", budget - total, "s")

# The metal-detector reading: did YOUR committed prediction match reality?
if my_total_seconds is not None:
    print("your sum", "matched" if my_total_seconds == total else f"DIFFERED (you said {my_total_seconds})")
'''))

C.append(md('''
## OBSERVE + EXPLAIN gate
The eight budgets sum to **180** with **0 slack** — that is deliberate, and it is dangerous. One
sentence, out loud: *if a beat runs 10 seconds long on stage, which beat do you sacrifice, and why
that one?* (Course answer lives in Act 3; commit to yours first.)
'''))

C.append(md('''
## Manual-before-function — rehearse ONE beat into a string

Before we load any real artifact, you rehearse the spine the only way that works: by **writing each
beat's line as a string** and reading it aloud. A beat you have not put into words is a beat you
will improvise on stage. We start with beat 2 (the timestamp), because it is the most concrete.
'''))

C.append(md('''
## PREDICT
Beat 2 is "timestamp." Before you write it: **what number must this beat say out loud**, and what
*time* in the call does it point at? (You met these in book 04 — recall them, do not look yet.)
'''))

C.append(code('''
# YOUR TURN - write beat 2 (the timestamp beat) in YOUR words, as a string you will read aloud.
# A demo line you have not written is a line you will fumble. The guard lets the notebook run clean
# while still nagging you until you actually rehearse this beat.
beat2_timestamp = ""   # e.g. "At eighteen seconds, the agent starts talking 800ms before the caller finishes."

if len(beat2_timestamp.strip()) < 20:
    print("write beat 2 in your own words above (20+ chars), then re-run - and say it ALOUD.")
else:
    print("BEAT 2 REHEARSED:", beat2_timestamp)
'''))

C.append(md('''
## Now the real artifact behind beat 2 — `data/hero/turns.json`

You have rehearsed the *words*. Now we load the **real call** those words point at, so the number
in your mouth is a number on disk — not a thing you hope is roughly right. This is the same hero
call from book 04: 12 turns, Telugu-English, an interruption stress profile.
'''))

C.append(code('''
# Load the REAL hero call. We resolve the path by walking up from the working directory so the
# notebook runs whether the kernel started in notebooks/ or the repo root (no hardcoded abs path).
import json
from pathlib import Path

name = "data/hero/turns.json"
hero_path = next(p for p in [Path.cwd()/name, *[a/name for a in Path.cwd().parents]] if p.exists())
hero = json.loads(hero_path.read_text())

# Print the call's identity FIRST (not the turns) - know which call you are demoing and how big it
# is before quoting any single moment. A demo built on the wrong call is the worst kind of confident.
print("call_id:", hero["call_id"], "| language:", hero["language"], "| stress_profile:", hero["stress_profile"])
print("turns:", len(hero["turns"]))
'''))

C.append(md('''
## PREDICT — the real 0:18 moment (beat 1 + beat 2)
Turn **t2** (the caller, giving their address) **ends at 18949 ms**. Turn **t3** (the agent)
**starts at 18149 ms**. Before the next cell:
1. Did the agent start **before** or **after** the caller finished?
2. What is the **overlap in ms**? Is it a barge-in by the 100 ms line?

This is the audible failure your demo opens on. Commit your number.
'''))

C.append(code('''
# YOUR TURN - lock the real-moment prediction before the function reveals it.
my_overlap_ms = None   # the overlap in ms between t2 (ends 18949) and t3 (starts 18149)

if my_overlap_ms is None:
    print("fill in my_overlap_ms above (a positive ms number), then re-run.")
else:
    print("locked:", my_overlap_ms, "ms overlap predicted")
'''))

C.append(code('''
# The real signals core - the same turn_metrics() the pipeline uses. We import it here, where it is
# first needed, and let it compute the seam your demo is built on (no hand-quoting a number we hope
# is right - the demo's credibility is that this is reproducible from disk).
import sys
root = next(a for a in [Path.cwd(), *Path.cwd().parents] if (a/"pipeline"/"signals.py").exists())
sys.path.insert(0, str(root))   # make the repo's pipeline package importable from inside notebooks/
from pipeline.signals import turn_metrics

events = turn_metrics(hero["turns"])
# Pull the exact t2->t3 seam your beat 1/2 point at, so the demo number is read, not recalled.
t2t3 = next(e for e in events if e["prev_turn_id"] == "t2" and e["next_turn_id"] == "t3")
at = t2t3["at_ms"]
print("t2->t3:  overlap_ms", t2t3["overlap_ms"], "| barge-in?", t2t3["overlap_ms"] > 100,
      "| at", f"{at//60000}:{(at%60000)//1000:02d}")

if my_overlap_ms is not None:
    print("your overlap prediction", "matched" if my_overlap_ms == t2t3["overlap_ms"] else "DIFFERED")
'''))

C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. Beat 1 plays a sound; beat 2 says a **number**. What exactly is that number for the hero call,
   and at what **timestamp** does it happen?
2. Why does beat 2 read the overlap from `turn_metrics()` instead of you just *saying* "about 800
   milliseconds" from memory? (The answer is the whole reason a demo earns trust.)
3. Which beat is the **opener line** attached to, and what does that line promise the room?
'''))

C.append(md('''
## The real artifact behind beat 6 — `web/shot.html`

Beat 6 is the chart, and it is not a slide you mock up the night before — it is a **real rendered
page** in the repo: `web/shot.html`. It shows the call, the failure table with timestamps, and the
before/after of the fix. Your beat-6 line points the room at that page. We confirm the artifact
exists (a demo beat whose artifact is missing is a beat that will fail live).
'''))

C.append(code('''
# Confirm the chart artifact your beat 6 points at actually exists on disk. We check existence and
# size rather than rendering it - the lesson is 'every beat has a real artifact behind it', and an
# empty or missing file is a beat that dies on stage. Better to catch it here than at the podium.
shot_path = next((p for p in [Path.cwd()/"web"/"shot.html", *[a/"web"/"shot.html" for a in Path.cwd().parents]]
                  if p.exists()), None)
if shot_path is None:
    print("web/shot.html NOT FOUND - beat 6 has no artifact; fix before demo day.")
else:
    print("beat-6 artifact OK:", shot_path.name, f"({shot_path.stat().st_size:,} bytes)")
'''))

C.append(md('''
## PREDICT
We will now lay the spine next to its artifacts in one table — beat → seconds → which file backs it.
Before the cell: **how many of the eight beats do you think have a concrete artifact on disk** (vs
a beat that is pure narration)? Commit a number.
'''))

C.append(code('''
# Map every beat to the artifact that backs it, so 'no beat is a vibe' is something you can SEE.
# We keep narration-only beats explicitly labelled (not silently absent) - an unbacked beat is not a
# bug here, but it IS a beat you must deliver from conviction, so naming it is the honest move.
artifact_of = {
    "audible failure": "data/hero/turns.json (the call) + the audio",
    "timestamp":       "signals.py turn_metrics() -> 800ms overlap",
    "scorecard":       "analyze() failure table (evidence_turn_ids)",
    "better response": "the improvement example (the rewrite)",
    "DPO pair":        "preference pair: chosen vs rejected",
    "chart":           "web/shot.html (before/after)",
    "calibration":     "pilot kappa (a human agreed)",
    "close":           "(narration: the closer line)",
}
backed = 0
for beat, _secs in spine:
    art = artifact_of[beat]
    is_backed = not art.startswith("(narration")
    backed += is_backed
    print(f"{beat:<16} <- {art}")
print("----")
print("beats with a concrete artifact:", backed, "of", len(spine))
'''))

C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: the demo was an order in your head and some words you hoped to remember. After Act 2: the
spine is **data** (eight beats summing to a 180 s budget), beat 2's number is **read from
`turn_metrics()`** (an 800 ms barge-in at 0:18), beat 6's chart is a **real file** (`web/shot.html`),
and **seven of eight beats point at an artifact on disk**. The demo is now backed, not bluffed.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (the spine-as-data / artifact-backed beats)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the order, break the claims, and rehearse under pressure

## Break-it philosophy

A demo only reveals its weak beats when something hits them — a wrong order, an overclaim, a beat
that runs long. So we damage the spine ON PURPOSE and watch it fail, here, where it is safe.
Surprise in rehearsal is education; surprise on the demo stage is a project that does not advance.
'''))

C.append(md('''
## PREDICT
We will play beat 3 (**scorecard**) **before** beat 1 (**audible failure**) — show the number
before the room has heard the thing it measures. Before the cell: **why does this kill the demo**
even though every individual beat is still "correct"? Commit your reason.
'''))

C.append(code('''
# BREAK-IT (guided) - reorder the spine so the scorecard comes BEFORE the audible failure.
# This cell does not crash; it produces a demo that runs in the WRONG ORDER. The damage is to
# MEANING, not to Python - the most dangerous kind, because nothing turns red to warn you.
wrong_order = [
    ("scorecard",       25),   # <- showing the NUMBER first...
    ("audible failure", 25),   # <- ...before the room has heard what the number is about
    ("timestamp",       20),
    ("better response", 25),
    ("DPO pair",        25),
    ("chart",           25),
    ("calibration",     20),
    ("close",           15),
]
for i, (beat, _s) in enumerate(wrong_order, start=1):
    print(f"beat {i}: {beat}")
print("----")
# Why this is broken: a scorecard is an ANSWER. Leading with the answer to a question the room has
# not heard yet means the number lands on deaf ears - they have no pain to attach it to.
print("PROBLEM: the room sees a failure score for a failure they have not heard yet -> the number means nothing.")
'''))

C.append(md('''
## The fix — pain always comes first

The repair is the locked rule from beat 1: **make them feel the pain before you show the
measurement.** The audible failure is the hook; the scorecard is the proof. Proof before hook is a
solution in search of a problem. We restore the order and confirm beat 1 leads.
'''))

C.append(code('''
# Recovery: restore the locked order and assert beat 1 is the audible failure. We re-derive from the
# original `spine` rather than hand-fixing `wrong_order`, because the source of truth is the locked
# spine - you fix a broken demo by returning to the spine, not by patching the broken run.
fixed_order = list(spine)
assert fixed_order[0][0] == "audible failure", "beat 1 must be the audible failure - pain comes first"
print("restored. beat 1 is:", fixed_order[0][0], "- the room feels the pain before any number.")
'''))

C.append(md('''
## CHECKPOINT 3 (out loud)
1. Why must **audible failure** precede **scorecard** — what does each beat do to the room, and what
   breaks if you swap them?
2. The wrong-order cell **did not error**. So what is the difference between a demo that *runs* and a
   demo that *lands*? (You met this exact trap on green-but-wrong code in P00.)
'''))

C.append(md('''
## WRONG-INTUITION TRAP — "more impressive numbers make a stronger close"

**The wrong belief:** "for the chart and the close, reach for the biggest, roundest claim — say the
agent is *90% better* and *fully fixed* — a bold number wins the room."

The next cell writes that bold version and the honest version side by side, then checks each claim
against what the artifacts actually support. Watch which one survives contact with a judge who asks
"how do you know?"
'''))

C.append(code('''
# Two versions of the beat-6 / beat-8 claim. We tag each line with whether an ARTIFACT backs it,
# because a demo claim is only as strong as the file behind it - an overclaim is a claim with no
# artifact, and on stage that gap is exactly where a sharp judge sticks the knife.
bold_claim    = "Our agent is 90% better and fully fixed - barge-ins are gone."
honest_claim  = "After the fix, this call's barge-in is removed and p90 latency drops below the 800ms line - on our pilot set."

# What the artifacts actually license: one real call's barge-in + a before/after chart on a small
# pilot. NOT 'fully fixed' (no number for that), NOT '90% better' (no baseline that says 90).
claims = [
    (bold_claim,   "overclaim: no artifact says '90%' or 'fully fixed' - it invents numbers"),
    (honest_claim, "backed: web/shot.html before/after + the pilot set scope is stated"),
]
for line, verdict in claims:
    print("CLAIM :", line)
    print("CHECK :", verdict)
    print()
'''))

C.append(md('''
## The reveal

The bold claim feels stronger and is **weaker** — because the first question after it is *"90%
relative to what baseline? what does 'fully fixed' mean — you tested every call?"* and you have no
artifact for either. The honest claim is **smaller and unbreakable**: every word in it points at
`web/shot.html` and names its scope ("this call," "our pilot set"). On a demo stage, a claim you can
**defend** beats a claim that sounds **big**. The judge is not buying the number; they are buying
whether you can stand behind it. Overclaiming is borrowing credibility you have to pay back the
instant someone asks "how do you know?" — and they always ask.
'''))

C.append(code('''
# YOUR TURN - rewrite the over-claim into a claim YOUR artifacts can defend. Name the scope.
# Storing it makes future-you rehearse the honest version, not the tempting one.
my_honest_close_claim = ""   # one line: a result you can back with a file + its scope ('this call', 'pilot set')

if len(my_honest_close_claim.strip()) < 20:
    print("write your defensible close-claim above (20+ chars, name the scope), then re-run.")
else:
    print("HONEST CLAIM LOGGED:", my_honest_close_claim)
'''))

C.append(md('''
## BREAK-IT (learner-authored) — find your own weak beat

Author your own break. Pick **one** beat and damage it the way pressure will: either **move it out
of order** (e.g. put `DPO pair` before `better response`, so the fix has no source), or **inflate
its claim** (state a number no artifact backs). Predict in a comment exactly *why* it breaks the
demo, then run and read it back.
'''))

C.append(code('''
# YOUR TURN - self-authored BREAK-IT of the spine.
# my prediction: <write here which beat you broke, how, and WHY it kills the demo>

my_spine = list(spine)   # start from the locked order so your damage is a deliberate, single change

# 1) damage ONE thing here (uncomment and edit ONE of these):
# my_spine[4], my_spine[3] = my_spine[3], my_spine[4]     # e.g. DPO pair before better response (fix with no source)
# my_broken_claim = "we beat every competitor by 10x"      # e.g. a number no artifact backs

# 2) print your damaged spine and say aloud why it fails:
for i, (beat, _s) in enumerate(my_spine, start=1):
    print(f"beat {i}: {beat}")
print("(now say, out loud, the sentence a judge would use to expose your break)")
'''))

C.append(md('''
## Rehearse under pressure — the cut order

A live demo runs long; the audio takes 30 seconds, a judge interrupts, the laptop lags. You will be
**over budget**, and you must cut without panic. The rule: **never cut beats 1, 2, or 8** (the
failure, the number, the close — the spine's backbone). Cut from the *middle*, in a fixed order you
decided in rehearsal, so the cut is a reflex, not a decision made while sweating.
'''))

C.append(md('''
## PREDICT
If you are 30 seconds over, which beat do you drop **first**, and which **last** would you ever
touch? Commit your two answers before the cell shows the rehearsed cut order.
'''))

C.append(code('''
# YOUR TURN - lock your cut decisions before seeing the rehearsed order.
my_cut_first = ""   # the beat name you sacrifice first when over budget
my_cut_last  = ""   # the beat you would protect to the very end

if len(my_cut_first.strip()) < 3 or len(my_cut_last.strip()) < 3:
    print("name BOTH beats (cut-first, protect-last) above, then re-run.")
else:
    print("locked: cut", my_cut_first, "first; protect", my_cut_last, "longest")
'''))

C.append(code('''
# The rehearsed cut order: a fixed priority so a live overrun is a reflex, not a panic. We protect
# the backbone (1 audible failure, 2 timestamp, 8 close) and shed from the middle, calibration first
# - it is the most 'extra' beat (trust-building) and the least 'story' beat (no narrative momentum lost).
cut_priority = ["calibration", "chart", "DPO pair", "better response", "scorecard"]   # drop in THIS order
protect      = ["audible failure", "timestamp", "close"]                              # never cut these

print("cut in this order when over budget:")
for i, beat in enumerate(cut_priority, start=1):
    print(f"  {i}. {beat}")
print("PROTECT (never cut):", ", ".join(protect))

if my_cut_first.strip():
    print("note: rehearsed cut-first is 'calibration' - compare against your '" + my_cut_first.strip() + "'")
'''))

C.append(md('''
## CHECKPOINT 4 (out loud)
1. You are 30 seconds over. Name the **first beat you cut** and **why that one** (what makes it the
   most droppable?).
2. Name the **three beats you never cut**, and what each one is load-bearing *for* (hook / proof /
   thesis).
3. Why is deciding the cut order **in rehearsal** strictly better than deciding it on stage?
'''))

C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a demo felt like "say good things in roughly the right order." After Act 3: **order is
load-bearing** (proof-before-pain is a green-but-dead demo), **overclaiming is borrowing
credibility you repay under the first question**, and **cuts are pre-decided** (protect failure /
number / close; shed calibration first). Pressure no longer makes decisions for you — rehearsal
already did.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the overclaim trap, or 'order is load-bearing', your pick)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the full run-through, three rooms, and defending the demo

## Where this lives in VoiceForge (these are real artifacts)

Nothing in the demo is a metaphor. Every beat points at a thing that exists in this repo:

| beat | real artifact | the number/thing it shows |
|---|---|---|
| 1 audible failure | `data/hero/turns.json` + `data/hero/hero_001.wav` | the call where the agent barges in |
| 2 timestamp | `pipeline/signals.py` → `turn_metrics()` | 800 ms overlap at 0:18 |
| 3 scorecard | `pipeline/signals.py` → `analyze()` | failure table with `evidence_turn_ids` |
| 6 chart | `web/shot.html` | before/after p90 latency + barge-in rate |
| 7 calibration | the pilot kappa (books 14–15) | a human agreed with the judge |

The demo is the whole course, compressed: the timing core (04), the scorecard (06–11), the
improvement example and DPO pair (16–18), the chart (25–26), and calibration (12–15) — eight beats,
each cashing in one earlier book. That is why this is book 29: you can only rehearse the spine once
every beat behind it is real.
'''))

C.append(md('''
## PREDICT — the full timed run-through
We will print the whole spine with running timestamps (when each beat *starts*, mm:ss). Before the
cell: **at what time does beat 6 (the chart) begin**, roughly? (Sum the budgets of beats 1–5.)
'''))

C.append(code('''
# Print the full run-through with a START clock per beat, so you can rehearse against a stopwatch.
# We accumulate a running offset (not just per-beat seconds) because what you actually rehearse is
# 'am I at the chart by 2:25?' - the absolute time is the thing a clock on the wall shows you.
def mmss(s):
    return f"{s//60}:{s%60:02d}"   # seconds -> m:ss, the way you read a stopwatch on stage

offset = 0
for i, (beat, secs) in enumerate(spine, start=1):
    print(f"{mmss(offset):>5}  beat {i}: {beat:<16} ({secs}s)")
    offset += secs           # the NEXT beat starts after this one's budget
print("----")
print("total run time:", mmss(offset), "(target <= 3:00)")
'''))

C.append(md('''
## The two locked lines — say them once, from memory

Beat 1's opener and beat 8's closer. The next cell does not check your *exact* wording (the lines
are yours to internalize) — it just gives you the place to recite them and confirms you have
committed to *something*. Say each one out loud, then write your version.
'''))

C.append(code('''
# YOUR TURN - the two locked lines, in your own committed wording. Guarded so the notebook runs
# clean unfilled, but it nags until you have rehearsed BOTH - these are the lines you cannot improvise.
my_opener = ""   # beat 1, said before you press play (buys the next 30 seconds)
my_closer = ""   # beat 8, said after the chart, then you STOP talking

if len(my_opener.strip()) < 20 or len(my_closer.strip()) < 20:
    print("write BOTH locked lines above (20+ chars each), then re-run - and say each ALOUD.")
else:
    print("OPENER:", my_opener)
    print("CLOSER:", my_closer)
'''))

C.append(md('''
## PREDICT — the closer must contain the clean sentence
The closer line and the book's **clean sentence** are close cousins. Before you see it: the clean
sentence is the five-word arc of the whole loop. **What are the five nouns**, in order? (You have
them from cell 3.) Commit before reading the close.
'''))

C.append(code('''
# YOUR TURN - write the five-noun arc of the loop from memory (the skeleton of the closer).
# This is the spine of your close; if you can produce it cold, the closer writes itself.
my_five_word_arc = ""   # e.g. "pain, measurement, correction, dataset, scale"

if len(my_five_word_arc.strip()) < 15:
    print("write the five-noun arc above, then re-run.")
else:
    print("ARC:", my_five_word_arc)
'''))

C.append(md('''
## The demo at three levels (same spine, three rooms)

- **To a beginner (a friend who is not technical):** "It is a three-minute song with eight notes.
  You play a recording of our robot being rude, you point at the exact second it happened, you show
  the report card that caught it, you show the better answer and how that answer becomes practice
  data, you show a chart that it is improving, you say a human checked our grading, and you stop.
  Same eight notes every time."
- **To an engineer:** "A locked eight-beat spine summing to a 180 s budget: audible failure →
  timestamp (`turn_metrics()`, 800 ms overlap at 0:18) → scorecard (`analyze()` failure table with
  `evidence_turn_ids`) → improvement example → DPO chosen/rejected pair → before/after chart
  (`web/shot.html`) → pilot kappa → close. Every claim is read from an artifact on disk; cuts are
  pre-prioritized (protect beats 1/2/8). Deterministic where it can be, calibrated where it cannot."
- **To a founder:** "Three minutes that prove a *loop*, not a feature: we find a real failure,
  measure it to the millisecond, fix it, turn the fix into training data, and show a human trusts
  our scoring — and it runs without a person in the loop. The pitch is the flywheel, demonstrated
  live, with every number backed by a file we can open on the spot."
'''))

C.append(md('''
## Defense questions (×3 — try first, then open)

**1. "Three minutes is short — why not show me more of what it can do?"**
<details><summary>answer</summary>Because a demo proves one thing well, not ten things vaguely. The
one thing is the loop: pain -> measurement -> correction -> dataset -> scale. Every beat earns its
seconds by advancing that loop; anything that does not advance it is cut. Breadth is for the repo
(book 30), not the three minutes.</details>

**2. "Your chart shows improvement — on how many calls? Isn't one call cherry-picked?"**
<details><summary>answer</summary>It is one hero call for the *audible* beats (you cannot play ten
calls in three minutes) and the *pilot set* for the chart and calibration. We say that scope out
loud - "this call" for the failure, "our pilot set" for the trend - so the claim is small and
defensible. We never say "fully fixed"; we say what `web/shot.html` and the kappa actually
support.</details>

**3. "You rehearse it word-for-word — isn't a scripted demo just hiding that it's brittle?"**
<details><summary>answer</summary>Only two lines are word-for-word (the opener and closer); they are
locked because they are load-bearing - one buys attention, one states the thesis. The rest is
flexible, and the cut order is pre-decided so a live overrun is a reflex, not a fumble. Rehearsal is
not hiding brittleness; it is removing the part of the stage where brittleness shows up - improvised
transitions under pressure.</details>
'''))

C.append(md('''
## CHECKPOINT 5 (out loud, the whole spine cold)
1. Recite the **eight beats in order** and, for each, name the **artifact** behind it (or say
   "narration" for the close). Any beat you cannot back is a beat to re-examine.
2. The closer line and the **clean sentence** share a five-noun arc — say it, and map each noun to
   the beats that prove it (which beats are "measurement"? which are "scale"?).
3. A judge asks "how do you know it improved?" mid-demo. Which **beat** answers that, and what is the
   **scope** word you must say so the claim does not overreach?
'''))

C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own the whole performance: the eight-beat spine on a stopwatch (chart by ~2:25,
close by 3:00), the two locked lines you can recite cold, every beat traced to a real file
(`turns.json`, `signals.py`, `web/shot.html`, the pilot kappa), three audience-level retellings, and
three defenses that hold under a sharp question. The demo is no longer a hope; it is a rehearsed
instrument you can place on the table and play the same way every time.
'''))

C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Three minutes, out loud, no peeking — actually *deliver the demo*. Hit all five:
1. The **eight beats in order**, no gaps, no swaps.
2. Both **locked lines** (opener + closer), word-for-word enough to land.
3. The **real number** beat 2 says (800 ms barge-in at 0:18) and the **artifact** it comes from.
4. Your **cut order** if you run 30 s long, and the three beats you never cut.
5. The **clean sentence** as your close.

Could not deliver it cleanly in one pass? That IS the bug - open it back up, find the beat you
stumbled on, and re-rehearse that one. A demo you cannot do closed-book is a demo you have not
rehearsed, whatever the green cells say.
'''))

C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (the full run-through / artifact-backed beats / defenses)
my_clean_sentence = ""      # the sentence you would say in a room about how you demo this project

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))

C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Pain → measurement → correction → dataset → scale."**

That five-noun arc IS the demo: the audible failure is the **pain**, the 800 ms timestamp and the
scorecard are the **measurement**, the better response is the **correction**, the DPO pair is the
**dataset**, and the chart plus calibration are the **scale**. Eight beats, one arc, three minutes.
If your sentence captures that loop in your own words, this book did its job.
'''))

C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "29_the_3_minute_demo.ipynb"   # <- this notebook's filename
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

**29 done** (pending your teach-back — actually deliver the three minutes) → **30 · Post-hackathon**
— what happens after the room: the follow-up questions, the repo someone clones, the longer story
the three minutes earned you the right to tell.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "29_the_3_minute_demo.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
