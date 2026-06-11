#!/usr/bin/env python3
# Builds 24_annotation_ground_truth.ipynb — VoiceForge University book 24.
# The ONE atomic concept: ASSEMBLY-AS-TRUTH. The hero call's timestamps are not MEASURED
# (no ASR, no diarization, no human stopwatch) — they are DECLARED in data/hero/timeline.json
# (each turn's fto_ms) and then REALIZED by the assembler, so they are exact BY CONSTRUCTION.
# The recipe IS the ground truth. The ethics: this is only legitimate if you DISCLOSE it
# (metadata.constructed + docs/limitations.md), and validity comes from public-data calibration.
# Same four-act skeleton + audit markers as build_P00.py / build_07.py.
# Rerun: .venv/bin/python notebooks/build_24.py
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
# 24 · Annotation & ground truth

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Explain **assembly-as-truth**: when a call is *built* from a recipe, its turn timestamps are
   **exact by construction** — derived from the recipe, never measured with ASR or a stopwatch
2. Take a list of declared gaps/overlaps (the **assembly timeline**) and compute the resulting
   `start_ms`/`end_ms` **by hand**, then prove a real timeline reproduces the real call exactly
3. Mark a **failure at a timestamp** (the barge-in and the dead air in the hero call) and point at
   the turn-ids that carry the evidence — the same `scorecard` discipline from book 06
4. State the **disclosure rule** that makes this honest: a constructed call is a *demonstration*,
   labelled `constructed` in metadata and on its own slide, with validity sourced elsewhere

Topic stays small on purpose: one real call (`data/hero`), a couple of toy clips, two engineered
failures. The point is the *epistemics* — knowing exactly where a number came from.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits on the ladder)

`23 · dataset hierarchy  →  THIS · annotation & ground truth  →  25 · charts that matter`

Book 23 sorted your data sources into jobs: the **hero call is theatre** (it shows what
VoiceForge detects), public data carries **validity**, synthetic gives **coverage**, provider
logs are **production**. It ended on a promise: *disclosure makes them all legitimate.* This book
cashes that promise for the hero call specifically. If the hero call is theatre, where do its
*numbers* come from, and why are we allowed to show them? The answer is **assembly-as-truth** —
and the ethics that keep it honest. Book 25 then takes the hand-verified numbers you trust here
and turns them into the five demo charts; a chart is only as honest as the annotation under it.
No trustworthy ground truth here → no narratable chart there.
'''))
C.append(md('''
## 3 — Baby intuition

Two ways to know how long a race took.

**Measure it:** stand at the finish line with a stopwatch. Your number has *error* — your thumb
is late, the runner is blurry. You estimate, and you carry uncertainty.

**Build it:** you are the director of a *staged* race for a film. You decide, on paper, "runner
crosses at exactly 12.00 seconds," then you cut the footage to make that true. Now the time is not
an estimate — it is a **fact you authored**. There is nothing to measure; you wrote it down and
then made the world match.

The hero call is the staged race. Nobody ran a diarizer over an audio file to *guess* who spoke
when. An engineer wrote a **timeline** — turn t3 starts 800ms *before* t2 ends — and an assembler
cut the audio clips to make exactly that true. The timestamps are authored, then realized. That is
**assembly-as-truth**: the recipe is the ground truth, and the audio is downstream of it.
'''))
C.append(md('''
## 4 — The formal version

Two ways a turn boundary (`start_ms`, `end_ms`) can come to exist:

| path | how the number is produced | error? | our hero call? |
|---|---|---|---|
| **measured** | ASR / diarization / a human with a stopwatch read it off real audio | yes — estimate | no |
| **assembled** | declared in a timeline as an offset, then audio is cut to match | **none** — authored | **yes** |

The vocabulary this book turns on:
- **assembly timeline** (`data/hero/timeline.json`) — the recipe: per turn, an `fto_ms`
  (floor-transfer offset) saying where this turn starts *relative to the previous turn's end*.
- **FTO** — `fto = this.start_ms − prev.end_ms`. Negative = **overlap** (the next speaker cut in
  early → a **barge-in**). Positive = **gap** (silence → **dead air** if long).
- **assembly-as-truth** — because the assembler *builds* the audio to honour each `fto_ms`, the
  resulting `start_ms`/`end_ms` reproduce the timeline exactly. The recipe is ground truth.
- **disclosure** — the metadata that says, out loud, "this call is `constructed`," so no one
  mistakes a demonstration for evidence.
'''))
C.append(md('''
## 5 — Why this book exists (the honesty hinge of the whole demo)

Every other source in this project carries *measurement error*. SpokenWOZ turn bounds are
synthesized from word-level timestamps; a human label is one person's read. The hero call is the
one artifact where the timestamps are **not** an estimate — and that is exactly why it is the
flagship demo: it shows the FTO math (barge-in at t3, dead air at t7) with **zero ambiguity about
the inputs**, so the audience argues about the *detection*, never about "are those timestamps even
right?"

But a built call is a loaded gun. If you show authored numbers and *imply* they are production
evidence, you have lied — politely, but lied. So the same file that makes the call exact
(`data/hero/timeline.json`, `metadata.constructed`) is paired with a disclosure rule written down
in `docs/limitations.md` **before any pipeline code existed**. This book is where you learn to
hold both at once: the numbers are exact *and* the call proves nothing about real traffic. Both,
always, together.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What is the difference between a **measured** timestamp and an **assembled** one? Which carries
   error, and which does the hero call use?
2. In one sentence: what does *assembly-as-truth* mean — where does the hero call's ground truth
   actually live?
3. A constructed call has exact numbers. Why is that *not* enough on its own — what must travel
   with it for the demo to be honest?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: timestamps in a call log were *read off the audio* somehow,
so "ground truth" meant "what the recording actually contains." After Act 1 you should hold a
sharper picture: for the hero call the recording is **downstream of a recipe**. The
`data/hero/timeline.json` declares the offsets; the assembler makes the audio obey; the timestamps
are therefore **authored, not estimated**. Ground truth is the recipe, and honesty is the
disclosure that travels beside it.

If "the recipe is the truth, the audio is the product" feels solid, continue. If you still picture
a stopwatch reading the hero call, re-read cell 3 — that stopwatch is the wrong mental model here.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of "assembly-as-truth." Not mine - yours.
# Producing the sentence is the learning; reading mine would just feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
# (Guarded with a length check so a fresh, unfilled notebook still runs clean top-to-bottom.)
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: place clips by hand, derive timestamps, then trust the real timeline

## The recipe, printed RAW (before any audio, before any computation)

A course rule: look at the ugly input first. The "input" to a constructed call is not audio — it
is a **list of offsets**. We build a tiny three-turn toy recipe as plain data and read it. Each
turn says how long its clip is (`dur_ms`) and where it starts relative to the previous turn's end
(`fto_ms`). Nothing is computed yet; this is just the director's notes.
'''))
C.append(code('''
# A toy assembly recipe: three clips, as plain dicts. dur_ms = how long the spoken clip is;
# fto_ms = floor-transfer offset = where this clip STARTS relative to the PREVIOUS clip's END.
# We model the recipe BEFORE any timestamps exist, because in assembly the offsets come FIRST
# and the start_ms/end_ms are DERIVED from them - that ordering is the whole lesson.
toy_recipe = [
    {"turn_id": "x1", "speaker": "agent", "dur_ms": 1000, "fto_ms": None},  # first clip: no previous turn, so no offset
    {"turn_id": "x2", "speaker": "user",  "dur_ms": 1500, "fto_ms": 500},   # starts 500ms AFTER agent finishes -> a gap
    {"turn_id": "x3", "speaker": "agent", "dur_ms": 1200, "fto_ms": -300},  # starts 300ms BEFORE user finishes -> an overlap (barge-in)
]
# Print the raw recipe so the OFFSETS are visible before we turn them into a timeline.
for r in toy_recipe:
    print(f"{r['turn_id']} | {r['speaker']:<5} | dur={r['dur_ms']:>5}ms | fto={str(r['fto_ms']):>5}")
'''))
C.append(md('''
## PREDICT (before you compute a single timestamp)
The first clip `x1` is 1000ms long and starts at time 0. So `x1`: start=0, end=1000.
`x2` has `fto_ms = 500`, meaning it starts 500ms *after* x1 ends.
1. What is `x2.start_ms`? What is `x2.end_ms` (it is 1500ms long)?
2. `x3` has `fto_ms = -300` — it starts 300ms *before* x2 ends. What is `x3.start_ms`?
Commit to all three numbers now; you will write them in the next cell.
'''))
C.append(code('''
# YOUR TURN - predictions are written BEFORE the by-hand cell runs, so the notebook becomes a
# record of YOUR thinking. A later cell compares your guess against the derived timestamps.
my_x2_start = None   # <- replace None with your number
my_x2_end   = None   # <- replace None with your number
my_x3_start = None   # <- replace None with your number

my_preds = {"x2_start": my_x2_start, "x2_end": my_x2_end, "x3_start": my_x3_start}
# Guard: a fresh notebook (all None) must still run clean, so we only "lock" once all are filled.
if any(v is None for v in my_preds.values()):
    print("fill in all three predictions above, then re-run this cell.")
else:
    print("predictions locked:", my_preds)
'''))
C.append(md('''
## Derive the timestamps BY HAND (the offsets become a clock)

This is the heart of assembly-as-truth, done with arithmetic you can see. We walk the recipe in
order, carrying a running clock. The very first clip anchors at 0. For every later clip:

`start_ms = previous.end_ms + fto_ms`   (positive fto pushes it later = gap; negative pulls it earlier = overlap)
`end_ms   = start_ms + dur_ms`

No audio is read. The timestamps are *manufactured* from the offsets. That is the point.
'''))
C.append(code('''
# Derive start_ms/end_ms from the recipe by hand - a running clock, every step printed.
# We do this with an explicit loop (no library) because the DERIVATION is the idea being taught;
# a one-liner would hide exactly the arithmetic that makes the timestamps "true by construction".
built = []
clock_prev_end = None                       # there is no "previous end" before the first clip
for r in toy_recipe:
    if r["fto_ms"] is None:                  # first clip anchors the whole timeline at time 0
        start = 0
    else:
        # the next turn's onset is the previous turn's end shifted by the floor-transfer offset
        start = clock_prev_end + r["fto_ms"]
    end = start + r["dur_ms"]                # a clip occupies [start, start+duration)
    built.append({"turn_id": r["turn_id"], "speaker": r["speaker"], "start_ms": start, "end_ms": end})
    print(f"{r['turn_id']}: start={start:>5}  end={end:>5}   (fto={r['fto_ms']}, dur={r['dur_ms']})")
    clock_prev_end = end                      # carry this clip's end forward as the next clip's anchor
'''))
C.append(code('''
# The metal-detector reading: line up YOUR locked predictions against the derived timestamps.
# A DIFFERED line marks exactly where your mental model of "offset -> timestamp" diverged.
got = {"x2_start": built[1]["start_ms"], "x2_end": built[1]["end_ms"], "x3_start": built[2]["start_ms"]}
print("derived:", got)
if all(v is not None for v in my_preds.values()):
    for k in got:
        verdict = "matched" if my_preds[k] == got[k] else "DIFFERED"
        print(f"  {k:<10} you={my_preds[k]:>5}  derived={got[k]:>5}  -> {verdict}")
else:
    print("(fill in the PREDICT cell above to see the comparison)")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not memory): where did `x3.start_ms` come from — did any
microphone, ASR, or stopwatch touch it? (Hint: trace it back to a single number in `toy_recipe`.)
'''))
C.append(md('''
## Read the overlap straight back out (FTO is reversible here)

We declared the offsets to *build* the timeline. Now run the FTO formula *forward* on the built
timestamps and watch it return the very offsets we started with. That round-trip — declare → build
→ recompute → same number — is what "exact by construction" means in one observation.
'''))
C.append(code('''
# Recompute FTO from the BUILT timestamps: fto = this.start - prev.end. It must return the recipe's
# fto_ms exactly, because we BUILT the timestamps to honour those offsets. A mismatch would mean the
# build step has a bug - so this check is also how the real assembler is validated.
for prev, cur, r in zip(built, built[1:], toy_recipe[1:]):
    recomputed_fto = cur["start_ms"] - prev["end_ms"]
    match = "OK" if recomputed_fto == r["fto_ms"] else "MISMATCH"
    kind = "overlap/barge-in" if recomputed_fto < 0 else ("gap" if recomputed_fto > 0 else "flush")
    print(f"{cur['turn_id']}: recomputed fto={recomputed_fto:>5}  declared={r['fto_ms']:>5}  [{match}]  {kind}")
'''))
C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. The derivation rule was `start = prev.end + fto`. Why does a **negative** `fto` produce an
   **overlap** (the next clip starting before the previous one ends)?
2. We computed FTO forward and got the recipe's offsets back exactly. What does that round-trip
   prove about the timestamps that a stopwatch reading could never prove?
3. Which came first in assembly — the offsets, or the timestamps? Why does the order matter?
'''))
C.append(md('''
## Now — and only now — the function version

You placed three clips and derived their timestamps by hand. A function is just that loop written
once so it runs on twelve turns instead of three. Because you met the arithmetic first, this
wrapper is a convenience, not a mystery — and you can audit every line against the by-hand version.
'''))
C.append(code('''
# The by-hand loop, collected into one function. Each line is exactly the arithmetic above.
# This mirrors what pipeline/assemble_hero.py does when it lays clips on the master timeline.
def build_timeline(recipe):
    out = []
    prev_end = None
    for r in recipe:
        # first turn anchors at 0; every later turn is prev_end shifted by its floor-transfer offset
        start = 0 if r["fto_ms"] is None else prev_end + r["fto_ms"]
        end = start + r["dur_ms"]
        out.append({"turn_id": r["turn_id"], "speaker": r["speaker"], "start_ms": start, "end_ms": end})
        prev_end = end
    return out
print("build_timeline defined")
'''))
C.append(code('''
# Run the function on the toy recipe; it must reproduce the by-hand `built` list exactly.
# If it does not, the FUNCTION is wrong (or the by-hand reasoning was), and that gap is the lesson.
fn_built = build_timeline(toy_recipe)
same = fn_built == built
print("function output matches by-hand list:", same)
for row in fn_built:
    print(row)
'''))
C.append(md('''
## Touch the real thing — the hero call's actual recipe on disk

The toy was the lesson; the real recipe already lives at `data/hero/timeline.json`. It carries the
same shape — per turn an `fto_ms` — for the 12-turn hero call. We load it straight off disk and
read the two offsets that the script engineered as the call's *two sins*: a barge-in and dead air.
'''))
C.append(code('''
# Load the REAL hero assembly recipe. We resolve the repo root by walking up to the folder that
# contains data/hero, so this runs no matter the kernel's working directory.
import json
from pathlib import Path
root = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "hero").exists())
timeline = json.loads((root / "data" / "hero" / "timeline.json").read_text())   # disk text -> dict

# Print the declared fto_ms per turn - this is the recipe, the authored offsets, before any audio.
print("call:", timeline["call_id"], "| stress_profile:", timeline["stress_profile"])
for t in timeline["turns"]:
    print(f"  {t['turn_id']:>3} | {t['speaker']:<5} | declared fto_ms = {t['fto_ms']}")
'''))
C.append(md('''
## PREDICT
Look at the printed `fto_ms` list above. **Two** offsets stand out from the rest (most are
small positive gaps of 350–600ms). One is **negative** (an overlap), one is a **large positive**
(long silence). Name the two turn-ids, and say which is the barge-in and which is the dead air.
Commit before running the next cell.
'''))
C.append(code('''
# Find the engineered failures FROM THE RECIPE, not by eye. We scan declared offsets and flag any
# overlap (negative fto) or long gap (fto over a teaching threshold). These thresholds echo book 04:
# barge-in = overlap beyond 100ms; "laggy/dead air" = a gap beyond 800ms.
BARGE_MS = 100        # overlap larger than this is a barge-in (not a harmless backchannel)
DEADAIR_MS = 800      # a gap larger than this is conspicuous dead air (the agent was slow)
for t in timeline["turns"]:
    fto = t["fto_ms"]
    if fto is None:
        continue
    if fto < -BARGE_MS:
        print(f"  {t['turn_id']}: fto={fto}  -> BARGE-IN (agent cut in {-fto}ms early)")
    elif fto > DEADAIR_MS:
        print(f"  {t['turn_id']}: fto={fto}  -> DEAD AIR (agent waited {fto}ms before replying)")
'''))
C.append(md('''
## Build the real timestamps from the real recipe — and meet the call on disk

Now the payoff. We run `build_timeline` on the real recipe to MANUFACTURE the hero call's
`start_ms`/`end_ms`, then load the already-assembled `data/hero/turns.json` (the call log the rest
of the pipeline actually reads) and check: do our recipe-derived timestamps match the ones on disk?
If assembly-as-truth holds, they must match to the millisecond.
'''))
C.append(code('''
# Manufacture the hero timestamps from the recipe (durations come from each clip's declared length).
# The timeline stores fto_ms but not dur_ms, so we recover each clip's duration from the assembled
# call's own end-start (the assembled file IS the realized recipe) - then rebuild and cross-check.
turns_on_disk = json.loads((root / "data" / "hero" / "turns.json").read_text())["turns"]
durations = {t["turn_id"]: t["end_ms"] - t["start_ms"] for t in turns_on_disk}   # realized clip lengths

recipe_real = [{"turn_id": t["turn_id"], "speaker": t["speaker"],
                "dur_ms": durations[t["turn_id"]], "fto_ms": t["fto_ms"]} for t in timeline["turns"]]
rebuilt = build_timeline(recipe_real)        # recipe -> timestamps, using our own by-hand function
print("rebuilt first 3 turns:")
for row in rebuilt[:3]:
    print(" ", row)
'''))
C.append(code('''
# The cross-check that PROVES assembly-as-truth: our recipe-derived timestamps vs the call on disk.
# We compare every turn's start_ms and end_ms. All-equal means the assembled file is exactly what
# the recipe declares - the timestamps are ground truth because the recipe authored them.
all_match = True
for built_row, disk_row in zip(rebuilt, turns_on_disk):
    ok = (built_row["start_ms"] == disk_row["start_ms"]) and (built_row["end_ms"] == disk_row["end_ms"])
    all_match &= ok
    if not ok:
        print(f"  MISMATCH at {built_row['turn_id']}: built {built_row['start_ms']}/{built_row['end_ms']}"
              f" vs disk {disk_row['start_ms']}/{disk_row['end_ms']}")
print("recipe-derived timestamps match data/hero/turns.json exactly:", all_match)
'''))
C.append(md('''
## EXPLAIN gate
One sentence: you just showed the timestamps in `turns.json` equal the ones you rebuilt from
`timeline.json`. Why is that **not** a coincidence — and why does it mean nobody needed ASR or a
diarizer to "find" who spoke when in the hero call?
'''))
C.append(md('''
## CHECKPOINT 3 (out loud)
1. The recipe-derived timestamps matched the on-disk call exactly. State, in one sentence, the
   claim this licenses about the hero call's ground truth.
2. Which two turns carry the engineered failures, and what is the `fto_ms` of each?
3. If you wanted to *change* where the barge-in lands, which file would you edit — the recipe
   (`timeline.json`) or the assembled call (`turns.json`)? Why?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a call log's timestamps were a given, source unknown. After Act 2 you can do four concrete
things: read an **assembly recipe** (offsets, not audio), **derive** `start_ms`/`end_ms` from it by
hand, run **FTO forward** to recover the declared offsets (the round-trip that means "exact by
construction"), and **prove** on the real `data/hero` files that the assembled call reproduces its
recipe to the millisecond. Ground truth is now a recipe you can rebuild, not a recording you must trust.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (assembly-as-truth / the round-trip / recipe-is-ground-truth - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: mark a failure, break the recipe, then the trap at the heart of this book

## Marking a failure AT a timestamp (annotation with evidence)

"The agent barged in" is a feeling. **Annotation** turns it into a record: a named failure, the
turn-ids it spans, and the measured offset that proves it. This is the `scorecard` discipline from
book 06 — `score + reason + evidence_turn_ids` — applied to a timing failure. We annotate the hero
call's barge-in by hand, carrying the evidence, not asserting it.
'''))
C.append(md('''
## PREDICT
The barge-in is at t3 (`fto_ms = -800`): the agent's t3 starts 800ms before the caller's t2 ends.
We are about to write an annotation record for it. Before you see it: what **three** pieces should
that record carry so a stranger could verify it without trusting us? (Hint: a name, a pointer, a number.)
'''))
C.append(code('''
# Annotate the barge-in BY HAND as a structured record. The record is verifiable: anyone can take
# evidence_turn_ids, look up those turns in turns.json, recompute the offset, and confirm the tag.
# That verifiability is the difference between annotation (engineering signal) and opinion.
def fto_between(turns, prev_id, next_id):
    # recompute the floor-transfer offset for a specific pair, so the annotation's number is derived
    # from the data on disk, never typed in by hand (a typed number is an unverifiable claim).
    by_id = {t["turn_id"]: t for t in turns}
    return by_id[next_id]["start_ms"] - by_id[prev_id]["end_ms"]

barge_fto = fto_between(turns_on_disk, "t2", "t3")     # derive the number from the assembled call
barge_annotation = {
    "failure_tag": "interruption",                      # named category, not a vibe (book 07's taxonomy)
    "evidence_turn_ids": ["t2", "t3"],                  # the pointer: where to look to verify
    "fto_ms": barge_fto,                                # the number, recomputed from disk
    "note": "agent t3 starts before caller t2 finishes -> barge-in",
}
print("BARGE-IN annotation:", barge_annotation)
print("verify: fto(t2->t3) recomputed from disk =", barge_fto, "ms (negative => overlap)")
'''))
C.append(md('''
## YOUR TURN — annotate the *other* sin (the dead air at t7)

You just saw the barge-in annotation built and verified. The second engineered failure is **dead
air**: t7 starts 1,620ms after t6 ends. Build the matching annotation record for it. The guard lets
a fresh notebook run; fill in the three fields to lock it. (Re-use `fto_between` — derive the number,
do not type 1620 by hand; a derived number is verifiable, a typed one is a claim.)
'''))
C.append(code('''
# YOUR TURN - annotate the dead-air failure, mirroring the barge-in record above.
my_deadair_tag        = None    # <- the failure_tag string (what KIND of failure is a long silence?)
my_deadair_evidence   = None    # <- the two turn-ids that span the gap, as a list e.g. ["t?", "t?"]
my_deadair_note       = None    # <- one short string describing the failure

# We DERIVE the offset from disk rather than asking you to type it - the number must be verifiable.
# This line is safe even unfilled, so it runs on a fresh notebook; the lock below needs your fields.
my_deadair_fto = fto_between(turns_on_disk, "t6", "t7") if my_deadair_evidence else None

if my_deadair_tag is None or my_deadair_evidence is None or my_deadair_note is None:
    print("fill in the three dead-air fields above (tag, evidence turn-ids, note), then re-run.")
else:
    my_deadair_annotation = {"failure_tag": my_deadair_tag, "evidence_turn_ids": my_deadair_evidence,
                             "fto_ms": fto_between(turns_on_disk, my_deadair_evidence[0], my_deadair_evidence[1]),
                             "note": my_deadair_note}
    print("YOUR DEAD-AIR annotation:", my_deadair_annotation)
'''))
C.append(md('''
## Break-it philosophy

A recipe you have never pushed against is a recipe you do not trust. The whole claim of this book
is "the assembled call honours the recipe exactly." So we now *change the recipe* and watch the
ground truth move with it — and then feed it something malformed to see where it bends or breaks.
Surprise on your own terms is education; surprise on the demo stage is a disaster.
'''))
C.append(md('''
## PREDICT
We change the toy recipe's `x2` offset from `fto_ms = 500` (a gap) to `fto_ms = -400` (an overlap).
Everything downstream of x2 must shift. Does `x3.start_ms` move **earlier**, **later**, or **stay
the same**? Commit before running. (Trace it: x2 starts earlier → x2 ends earlier → x3 anchors on
x2's end.)
'''))
C.append(code('''
# BREAK-IT (guided) - change ONE offset in the recipe and rebuild. This is the "change one thing"
# loop from P00: edit the recipe, re-derive, observe what moved. The ground truth is not fixed -
# it is whatever the recipe says, which is the point: editing timeline.json edits the truth.
broken_recipe = [dict(r) for r in toy_recipe]     # copy so we do not mutate the original toy recipe
broken_recipe[1]["fto_ms"] = -400                  # was +500 (gap) -> now -400 (overlap/barge-in)
rebuilt_broken = build_timeline(broken_recipe)
print("after changing x2 fto 500 -> -400:")
for before, after in zip(built, rebuilt_broken):
    moved = after["start_ms"] - before["start_ms"]
    print(f"  {after['turn_id']}: start {before['start_ms']:>5} -> {after['start_ms']:>5}  (moved {moved:+}ms)")
'''))
C.append(md('''
## Reading that result — the truth tracks the recipe

Changing one offset shifted x2 and everything after it. The ground truth is **not** a fixed fact
about some recording — it is a *function of the recipe*. That is the power (edit `timeline.json`,
re-assemble, and the whole call's truth updates consistently) **and** the responsibility (the truth
is only as honest as the recipe you disclose). Measured data cannot be edited like this; authored
data can — which is exactly why disclosure is non-negotiable.
'''))
C.append(md('''
## PREDICT
Now a nastier break. We hand `build_timeline` a recipe whose **first** turn has `fto_ms = 500`
instead of `None` (someone forgot to mark the anchor turn). The code does
`0 if fto_ms is None else prev_end + fto_ms`, and `prev_end` is `None` for the first turn. Does it
**crash loudly**, or **produce a silently wrong timeline**? Commit to one before running.
'''))
C.append(code('''
# BREAK-IT (guided) - a malformed recipe: the first turn has a real fto instead of None.
# EXPECTED FAILURE FOR LEARNING - this cell is SUPPOSED to error. Read the traceback, do not fix yet.
malformed_recipe = [dict(r) for r in toy_recipe]
malformed_recipe[0]["fto_ms"] = 500    # <- the damage: anchor turn now has an offset but no previous end
# build_timeline will hit prev_end + 500 with prev_end = None on the very first turn. Watch it refuse.
print(build_timeline(malformed_recipe))
'''))
C.append(md('''
## Reading the error (bottom-up) and the fix

The last line of the traceback names *what* broke:
`TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'` — "you asked me to add 500 to
`None`," because `prev_end` is `None` on the first turn. Walk **upward** to find *where* (the
`prev_end + r["fto_ms"]` line). A loud crash was the friendly outcome: it pointed at the exact line.
The fix is a guard at the boundary — a well-formed recipe's anchor turn must have `fto_ms is None`,
so we validate that *before* building, turning a confusing math error into a clear contract error.
'''))
C.append(code('''
# The fix: validate the recipe's contract BEFORE building, so a malformed anchor fails with a clear
# message instead of an opaque math crash. Validation at the boundary is cheaper than debugging
# wrong timestamps later - the same lesson as guarding null text in book 07.
def build_timeline_safe(recipe):
    if recipe and recipe[0]["fto_ms"] is not None:
        # a clear, early contract error beats a confusing 'NoneType + int' three lines deep
        raise ValueError("anchor turn (first) must have fto_ms=None; got "
                         f"{recipe[0]['fto_ms']} - fix the recipe, not the builder")
    return build_timeline(recipe)

# Show the guard catching the bad recipe cleanly (we catch the error so this cell runs to completion).
try:
    build_timeline_safe(malformed_recipe)
except ValueError as e:
    print("caught at the boundary:", e)
print("well-formed recipe still builds fine:", build_timeline_safe(toy_recipe)[:1])
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. Changing `x2`'s offset moved every turn after it. Why does that prove the ground truth is a
   *function of the recipe*, not a fixed property of a recording?
2. The malformed anchor crashed with `NoneType + int`. Why is a loud crash here *friendlier* than
   a timeline that silently anchored at the wrong time?
3. The fix went into a **validation** step, not into the math. Why guard the *contract* at the
   boundary instead of patching `build_timeline`'s arithmetic?
'''))
C.append(md('''
## YOUR break now

Author your own change to the recipe. Pick ONE: edit an `fto_ms` to invent a *new* barge-in or a
*new* dead-air somewhere it was not, OR set a duration to something that makes two clips collide
oddly. Predict — in a comment — the exact `start_ms` of the turn after your change, then rebuild and
compare. (Use the safe builder so a malformed anchor fails loudly rather than silently.)
'''))
C.append(code('''
# YOUR TURN - self-authored break-it on the recipe.
# my prediction: <write the exact start_ms you expect for the turn AFTER your change, and why>

my_recipe = [dict(r) for r in toy_recipe]   # start from a clean copy of the toy recipe
# 1) change ONE field to probe an edge (a new overlap, a new gap, an odd duration):
# my_recipe[1]["fto_ms"] = ?      # e.g. make x2 a barge-in
# my_recipe[2]["dur_ms"] = ?      # e.g. stretch x3

# 2) rebuild with the SAFE builder and hold the result against your written prediction:
my_built = build_timeline_safe(my_recipe)
for row in my_built:
    print(row)
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this whole book is built on

**The wrong belief:** "the hero call's timestamps are *exact*, so the hero call is *strong
evidence* that VoiceForge works on real calls."

Exactness and evidential weight are **different axes**. The timestamps are exact *because* the call
was authored — and that very authoring is what makes it **weak** as evidence about real traffic. A
constructed call cannot surprise you; it only contains what its director put in. The next cell lays
the two facts side by side: precision is perfect, external validity is near zero, and they do not
contradict — they are *causally linked*. Run it, then try to state the link before the reveal.
'''))
C.append(code('''
# The trap, made concrete: two properties of the hero call that feel opposed but are not.
# We read the disclosure metadata straight off the assembled call - the call itself ADMITS it is built.
hero_meta = json.loads((root / "data" / "hero" / "turns.json").read_text())["metadata"]

precision_ms = 0                                  # authored timestamps carry zero measurement error
is_constructed = hero_meta.get("constructed")     # ...and the SAME authoring is why it is not evidence
external_validity = "near zero (single constructed scenario)"

print("timestamp precision (measurement error) :", precision_ms, "ms  -> perfect")
print("metadata.constructed                    :", is_constructed, " -> it is built, by its own admission")
print("external validity for real traffic      :", external_validity)
print("timestamps_from                         :", hero_meta.get("timestamps_from"))
# Both true at once. Precision came FROM construction; construction is WHY validity is low. Linked, not opposed.
'''))
C.append(md('''
## The reveal — exactness and evidence are different axes

The hero call's timestamps have **zero** error, and the call is **near-worthless** as proof that
the system works on production traffic — and the first fact *causes* the second. You get exactness
by authoring every input; authoring every input means the call can only echo its own script. So:
the hero call is the perfect *demonstration* (it shows the FTO detection cleanly) and a terrible
*study* (it proves nothing about calls you did not write).

This is exactly why `docs/limitations.md` says, in the first paragraph written before any pipeline
code: *"Validity comes from the public-data calibration, not from this call."* The honest demo uses
the hero call to **show the mechanism** and points to the public-data kappa (books 14–15) for
**evidence it generalizes**. Reading exactness as evidence is the single most seductive mistake in
this whole area — and the disclosure rule exists precisely to block it.
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
1. State the two axes: which one is **timestamp precision**, which is **external validity**, and
   why are they *different* questions about the same call?
2. The trap said precision and low-validity are *causally linked*, not merely coexisting. Say the
   causal sentence: authoring gives you ___, and authoring is *why* you have low ___.
3. Where does the honest demo get its evidence-of-generalization from, if not the hero call?
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why does the hero call being EXACT make it WEAK as evidence?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a failure was a vibe, and an "exact" call felt like strong proof. After Act 3: you can
**annotate** a failure as a verifiable record (tag + evidence turn-ids + a recomputed offset), you
saw the ground truth **track the recipe** when you edited it, a malformed recipe **crashes loudly**
(friendlier than silent wrongness) so you guard the contract at the boundary, and — the spine of
the book — **exactness and evidential weight are different axes**, with construction buying the
first at the cost of the second.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the exact-but-not-evidence trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the cast, the disclosure rule, and the bar you must clear

## The recurring cast — which timestamps are authored vs measured

Three calls travel through this whole course. The point of this book lands when you see *where each
one's timestamps come from*. The hero call (`call_C`'s real embodiment) is assembled — authored,
exact. The SpokenWOZ calls behind `call_A`/`call_B`-style scenarios are **measured** — synthesized
from word-level timestamps, so they carry error. Same schema, different epistemics.
'''))
C.append(code('''
# The cast with the SOURCE of their timestamps spelled out. ids/languages/outcomes match the
# course-wide spec exactly; the added column is THIS book's contribution: where the numbers came from.
cast = [
    {"id": "call_A", "language": "en",    "outcome": "success", "timestamps": "measured (SpokenWOZ word-aligned)"},
    {"id": "call_B", "language": "hi-en", "outcome": "partial", "timestamps": "measured (SpokenWOZ word-aligned)"},
    {"id": "call_C", "language": "te-en", "outcome": "failure", "timestamps": "ASSEMBLED (hero recipe -> exact)"},
]
# One row per call so each is visibly one THING; the timestamps column is the epistemic fact this book adds.
for c in cast:
    print(f"{c['id']} | {c['language']:<6} | {c['outcome']:<8} | timestamps: {c['timestamps']}")
'''))
C.append(md('''
## call_C is the lesson in one row

`call_C` (the hero call) is the only one whose timestamps are **assembled** — and it is the demo
star precisely because of that exactness. The other two are **measured**, so they carry the error
real data always carries. Disclosure is what lets all three sit in the same project honestly: the
assembled one is labelled `constructed`, the measured ones are labelled with their public source.
Book 23's promise — *disclosure makes them all legitimate* — is this row.
'''))
C.append(md('''
## Where this lives in the real VoiceForge pipeline

This book is the hand-built version of three real things you can open right now:

- **`data/hero/timeline.json`** — the real recipe: per-turn `fto_ms`, with a `_fto_ms_doc` field
  that literally names *"THE TWO SINS: t3 = -800 (barge-in), t7 = +1620 (dead air)."* You rebuilt
  the call from this file.
- **`data/hero/turns.json`** — the assembled call log, whose `metadata` carries `constructed: true`,
  `timestamps_from: "assembly_timeline"`, and `disclosure: "...see docs/limitations.md"`. You read
  that disclosure straight off disk in the trap cell.
- **`docs/limitations.md`** — the disclosure rule in prose, written *before* any pipeline code:
  *"The hero call is constructed... Validity comes from the public-data calibration, not from this
  call. Disclosed on its own slide."* The exactness you proved and this paragraph are a matched pair.

(`pipeline/assemble_hero.py` is the real assembler; `pipeline/signals.py`'s FTO core is the same
offset math you ran by hand.)
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)
In book 25 you will narrate five demo charts. One of them shows the hero call's per-turn FTO with
the barge-in and dead air marked. Predict: when you present that chart, what **one sentence of
disclosure** must you say *out loud* before the numbers, so the chart is honest? Your stored guess
gets confronted when you build that chart.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for the charts in book 25.
my_course_prediction = ""   # the single disclosure sentence you must say before showing hero-call numbers

if len(my_course_prediction.strip()) < 20:
    print("write your prediction above (the disclosure sentence), then re-run.")
else:
    print("PREDICTION STORED:", my_course_prediction)
'''))
C.append(md('''
## Where this method itself fails (honesty applies to annotation too)

- **Undisclosed construction** — showing authored numbers as if they were measured. This is the
  cardinal sin; the entire `constructed`/`disclosure` metadata exists to prevent it.
- **Exactness laundering** — letting "the timestamps are exact" *imply* "the result is validated."
  Exactness is about precision, not generalization. (The Act-3 trap, named.)
- **Unverifiable annotation** — a failure tag with no `evidence_turn_ids` and no recomputed number
  is an opinion. Every annotation must point at the turns and derive its offset from disk.
- **Recipe drift** — editing `turns.json` by hand instead of `timeline.json`, so the call no longer
  matches its recipe. The recipe is the source of truth; the call log is generated from it.
'''))
C.append(md('''
## The concept at three levels (say each in your own words)

- **To a beginner:** "we *built* the demo call on purpose, so we know its exact timing the way a
  film director knows exactly when an actor hits a mark — and we always say out loud that it's staged."
- **To an engineer:** "the hero call's turn boundaries are derived from a declared assembly timeline
  (`fto_ms` per turn), not from ASR or diarization, so they're exact by construction and round-trip
  through the FTO formula; the call carries `constructed`/`disclosure` metadata, and external
  validity is sourced from the public-data kappa, not this artifact."
- **To a founder:** "our flagship call shows the mechanism with zero ambiguity *because* we built
  it, and we disclose that it's constructed on its own slide — so the room trusts the demo and the
  *evidence it generalizes* comes from the public-data calibration, exactly where it should."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**Defense question 1: "If you built the hero call yourself, isn't the whole demo rigged?"**
<details><summary>answer</summary>It's *constructed*, and we say so on its own slide and in the call's metadata (`constructed: true`, `disclosure: see docs/limitations.md`). It's a demonstration of what the pipeline detects, not evidence about production traffic. The construction is disclosed, not hidden - that's the difference between a rigged demo and an honest one. Evidence that the detection generalizes comes from the public-data calibration (the kappa in books 14-15), not from this call.</details>

**Defense question 2: "How can timestamps have *zero* error? Real audio is never that clean."**
<details><summary>answer</summary>Because they aren't measured off audio - they're *authored*. The assembly timeline declares each turn's offset (`fto_ms`), and the assembler cuts the clips to honour it, so the resulting `start_ms`/`end_ms` reproduce the recipe exactly. I proved it: rebuilding the call from `timeline.json` matches `turns.json` to the millisecond, and the FTO formula round-trips back to the declared offsets. The error is zero because there's nothing being estimated.</details>

**Defense question 3: "Why bother with a constructed call at all if it proves nothing about real calls?"**
<details><summary>answer</summary>Because a demonstration and a study are different jobs. The hero call shows the FTO mechanism (barge-in at t3, dead air at t7) with no argument possible about whether the inputs are right - so the audience evaluates the *detection*, not the data. It's the cleanest possible teaching artifact. Generalization is a separate claim, and we back it separately with public data. Using the right artifact for each job, and disclosing which is which, is the honesty.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own: the cast labelled by *timestamp source* (assembled vs measured), where the
recipe / assembled call / disclosure rule live in the real repo (`data/hero/timeline.json`,
`data/hero/turns.json`, `docs/limitations.md`), how this book hands trustworthy ground truth forward
to book 25's charts — and, above all, the bar you must clear to PASS this book.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. **Assembly-as-truth** — where the hero call's ground truth lives, and why its timestamps carry
   zero measurement error (recipe → build → exact)
2. The **derivation rule** `start = prev.end + fto`, and why negative fto = overlap = barge-in
3. How you **annotate a failure** verifiably: tag + evidence turn-ids + a recomputed offset (the
   barge-in at t3, the dead air at t7)
4. The **trap**: exactness and external validity are different axes, and construction buys the
   first at the cost of the second — so where does evidence-of-generalization come from?
5. The book's **clean sentence** (below) — in your own words first

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about annotation and disclosure

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Annotation is not cheating if you say exactly how the numbers were made."**

The hero call's timestamps are exact because they were assembled from a disclosed recipe — and the
disclosure (`constructed` in metadata, the rule in `docs/limitations.md`) is what turns "we built
it" from a confession into a method. If your sentence captures that — exactness *plus* disclosure —
this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "24_annotation_ground_truth.ipynb"   # <- this notebook's filename
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

**24 done** (pending your teach-back) → **25 · charts that matter** — the five demo charts, each
read aloud. You now hold *trustworthy* ground truth (exact, and honestly disclosed); book 25 turns
it into pictures. A chart you can't narrate is decoration — and a chart built on numbers you can't
explain is worse. The hand-verified timestamps and the disclosure sentence you wrote here are what
make those charts defensible in the room.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "24_annotation_ground_truth.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
