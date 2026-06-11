#!/usr/bin/env python3
# Builds 01_what_is_a_call_log.ipynb — VoiceForge University book 01.
# ONE atomic concept: a TRACE (timed turns) carries what a TRANSCRIPT (text only) throws away.
# Rerun: .venv/bin/python notebooks/build_01.py
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
# 01 · What is a call log?

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Define a **call log** as an ordered list of **turns**, and name a turn's four parts:
   **speaker**, **text**, **start_ms**, **end_ms** (plus call-level **metadata**).
2. State the one distinction this whole course rests on: a **trace** (timed turns) versus a
   **transcript** (text only) — and say exactly what the transcript throws away.
3. Build the three recurring cast calls (A/B/C) by hand as turn lists, and print them as turns.
4. Take a real call (`data/hero/turns.json`), strip it down to a transcript, and **prove with
   numbers** that an interruption and a long silence disappear when timing is gone.

Topic is small on purpose (a dozen lines of speech). The distinction is not small — every
later book (timing, task success, judging, training pairs) reads the trace this book defines.
'''))
C.append(md('''
## 2 — Knowledge map

`00 (what VoiceForge is) → THIS: what a call log is → 02 (the call_log schema)`

Why this book exists, right here on the ladder: book 00 told you VoiceForge *judges phone
calls*. But to judge a call you first need it as **data** — a thing Python can hold, walk, and
measure. This book defines that thing (the call log / trace). Book 02 then writes its exact
**schema** (field names, types, the `null` rules). You cannot specify a shape you cannot
yet picture, so picture it first — here.

No lesson floats in the void: previous = "VoiceForge exists", current = "a call is a trace of
turns", next = "here is that trace's formal schema".
'''))
C.append(md('''
## 3 — Baby intuition

Imagine two ways to keep a record of the same phone call.

**Way one — the script.** You write down only *who said what*, in order:
> Agent: "Which area are you in?"
> Caller: "Madhapur, near the metro..."

That is a **transcript**. It is the words, nothing else.

**Way two — the recording's clock.** You ALSO write down *when* each person started and
stopped talking — to the millisecond. Now you can see that the caller had not finished the
word "metro" when the agent cut back in. You can see a three-second silence where the agent
froze. The words are identical to Way one; but Way two knows the *timing and overlap*.

That is a **trace**: turns **with a clock attached**. This book is about why VoiceForge keeps
the clock — because most of what makes a call good or bad lives in the timing, not the words.
'''))
C.append(md('''
## 4 — The formal version

A **call log** is one call, stored as data. Its heart is **`turns`**: an ordered list, where
each turn is one uninterrupted stretch of one speaker talking. A single turn has four parts:

| part | type | what it is |
|---|---|---|
| `speaker` | `"user"` or `"agent"` | who is talking this turn |
| `text` | string | the words of this turn (the transcript piece) |
| `start_ms` | int | when this turn STARTED, in milliseconds from call start |
| `end_ms` | int | when this turn ENDED, in milliseconds from call start |

Around the turns sits **metadata** (call-level facts: an id, the language, where the audio
file is). Two words we will use for the rest of the course:

- **trace** = the turns *with* `start_ms`/`end_ms` — timing kept.
- **transcript** = the same turns reduced to *speaker + text only* — timing thrown away.

The trace is a strict superset: you can always make a transcript from a trace by deleting the
timestamps. You can **never** go the other way — deleted time does not come back.
'''))
C.append(md('''
## 5 — Why this exists (why keep the clock at all?)

Keeping millisecond timestamps is extra work and extra storage. VoiceForge does it anyway,
for one reason: **the failures that matter most are timing failures.**

- An agent that **interrupts** the caller mid-sentence (talks while they are still talking)
  is rude and loses information — but the *words* it spoke might read perfectly polite.
- An agent that goes **silent for three seconds** before answering feels broken on a live
  call — but the transcript shows a clean question and a clean answer, no gap visible.

Both of those are invisible in a transcript and obvious in a trace. So the rule of this whole
project, which you will prove to yourself today, is: **we judge the trace, not the transcript.**

This notebook shares one Python process across all cells — variables you create stay alive in
the kernel's memory for later cells. (Book P00 drilled that; we lean on it here.)
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just syntax.

# We hand-build ONE turn as a plain dict before touching any file, because the whole notebook
# is about this object — you should be able to see and name every part before it scales up.
one_turn = {
    "speaker": "agent",       # who talks (only ever "user" or "agent" in this project)
    "text": "Which area are you calling from?",  # the words = the transcript piece of this turn
    "start_ms": 0,            # this turn began 0 ms into the call (the agent opened)
    "end_ms": 3400,           # ...and ended at 3400 ms = 3.4 seconds in
}
# Printing the raw object first (course rule: see the ugly input before transforming it).
print(one_turn)
'''))
C.append(code('''
# PREDICT was in the markdown above — now we read the parts back out, one at a time,
# so "a turn has four parts" stops being a sentence and becomes something you can index.
print("speaker :", one_turn["speaker"])   # pulling each field by key proves the dict holds exactly these four
print("text    :", one_turn["text"])
print("start_ms:", one_turn["start_ms"])
print("end_ms  :", one_turn["end_ms"])

# How LONG did this turn last? end minus start. We compute it (not hardcode 3400) so the line
# stays true for any turn — duration is the first thing timing buys us that text cannot give.
print("duration_ms:", one_turn["end_ms"] - one_turn["start_ms"])
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What are the **four parts** of a single turn? (no scrolling up)
2. Which two of those four parts is a **transcript** allowed to keep, and which two does it
   throw away?
3. In one sentence: what is the difference between a **trace** and a **transcript**?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) pictured a call as *a wall of dialogue text*. After Act 1 you
should picture it as an **ordered list of turns, each stamped with a start and end time** —
and you should know the special name for that timed version (**trace**) versus the
text-only version (**transcript**).

If you can say "a call log is a list of turns; a turn is speaker + text + start_ms + end_ms"
without looking, continue. If not, re-run the two cells above and read each field back.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of "what is a call log?" Not mine - yours.
# Producing the sentence is the learning; reading mine would just feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
# (Guarded so a fresh, UNFILLED notebook still runs clean top-to-bottom.)
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: build turns by hand, then meet the real cast

## From one turn to a whole call

One turn was the atom. A call is just **a list of turns, in time order**. The list ordering
*is* the conversation: turn 0 happened, then turn 1, then turn 2. Because the order carries
meaning, the list must stay sorted by `start_ms` — a shuffled call is a lie about who spoke
when. We will keep things sorted from the very first toy.
'''))
C.append(md('''
## PREDICT
We are about to build a tiny 4-turn toy call: agent asks, user answers, agent asks, user
answers. Before you see it: how many of those 4 turns will have `speaker == "user"`, and
will the `start_ms` values go **up** or **down** as you read down the list?
'''))
C.append(code('''
# YOUR TURN - predictions are written BEFORE the building cell runs, stored as variables so
# the notebook becomes a record of YOUR thinking and a later cell can check it.
my_user_turn_count = None    # <- replace None with a number (how many of the 4 turns are the user?)
my_time_direction  = None    # <- replace None with the string "up" or "down"

if my_user_turn_count is None or my_time_direction is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("predictions locked:", my_user_turn_count, "and", my_time_direction)
'''))
C.append(code('''
# A toy call, built fully by hand. Manual-before-real: you must be able to author a trace
# before you trust one loaded from disk. Times are invented but obey the one rule that matters:
# each turn starts after the previous one (sorted, non-overlapping for now — we add overlap later).
toy_call = [
    {"speaker": "agent", "text": "Hi! What size pizza would you like?", "start_ms": 0,    "end_ms": 2500},
    {"speaker": "user",  "text": "A large, please.",                    "start_ms": 3000, "end_ms": 4200},
    {"speaker": "agent", "text": "Great. Any toppings?",                "start_ms": 4600, "end_ms": 6000},
    {"speaker": "user",  "text": "Just cheese.",                        "start_ms": 6400, "end_ms": 7300},
]
# One print PER turn, so each turn is visibly one thing (never read a call as a wall).
for turn in toy_call:
    print(turn)
'''))
C.append(code('''
# Now check YOUR prediction against reality. This comparison is the lesson, not the count.
user_turns = [t for t in toy_call if t["speaker"] == "user"]   # filter keeps only the user's turns
print("actual user-turn count:", len(user_turns))

starts = [t["start_ms"] for t in toy_call]    # pull the timeline out so we can see its direction
print("start_ms in order:", starts)
print("are they sorted ascending?", starts == sorted(starts))  # True => time goes 'up' the list

if my_user_turn_count is not None:
    verdict = "matched" if (my_user_turn_count == len(user_turns) and my_time_direction == "up") else "DIFFERED"
    print("your prediction", verdict, "- if it differed, that gap is exactly what to think about")
'''))
C.append(md('''
## The EXPLAIN gate

One sentence, out loud, in this shape:

> "This call has ___ turns; reading down the list walks ___ in time because ___."

It feels slow. That is the point — saying it is the difference between *recognizing* a list
of turns and *owning* the idea that the list's order is the conversation's order.
'''))
C.append(code('''
# YOUR TURN - write the explain-gate sentence for the toy call as a string.
my_explanation = ""   # e.g. "This call has 4 turns; reading down walks forward in time because start_ms rises."

if len(my_explanation.strip()) < 20:
    print("write your one-sentence explanation above (20+ chars), then re-run.")
else:
    print("EXPLAINED:", my_explanation)
'''))
C.append(md('''
## Meet the recurring cast — A, B, C (you will see them in every book)

Three calls travel through this whole course. P00 introduced them as trailer cards (id +
language + outcome). **Now we give them turns.** Keep the ids, languages, and outcomes
identical to how they appear everywhere else — a later Consistency check relies on it:

- **call_A** — clean **English** booking, cooperative caller, task **succeeds**.
- **call_B** — **Hinglish** (Hindi+English) appointment, a hesitation and a repeat request,
  task **partially** done.
- **call_C** — **Telugu-English** service call, the agent **interrupts** the caller mid-answer,
  task **fails**. (This one mirrors the real hero call we load later in this book.)

We build them small, by hand, as traces.
'''))
C.append(code('''
# call_A as a TRACE (turns with a clock). Clean and short: agent asks, user answers, done.
# We attach call-level metadata (id/language/outcome) alongside the turns — those facts belong
# to the whole call, not to any single turn, which is why they sit outside the turns list.
call_A = {
    "call_id": "call_A",
    "language": "English",
    "outcome": "success",                 # required fields all captured, caller cooperative
    "turns": [
        {"speaker": "agent", "text": "Hi! I can book your table. For how many people?", "start_ms": 0,    "end_ms": 2800},
        {"speaker": "user",  "text": "Four people, tomorrow at 7pm.",                    "start_ms": 3300, "end_ms": 5200},
        {"speaker": "agent", "text": "Booked: table for four, tomorrow 7pm. Anything else?", "start_ms": 5700, "end_ms": 8400},
        {"speaker": "user",  "text": "No, thank you!",                                   "start_ms": 8900, "end_ms": 9800},
    ],
}
# Print metadata, then turns — the same top-down order every record in this course uses.
print("id:", call_A["call_id"], "| language:", call_A["language"], "| outcome:", call_A["outcome"])
for t in call_A["turns"]:
    print("  ", t)
'''))
C.append(code('''
# call_B as a TRACE. Hinglish, with the two textures the spec calls for: a hesitation
# ("umm... ek minute") and a repeat request ("can you repeat?"). Task only PARTLY done.
call_B = {
    "call_id": "call_B",
    "language": "Hinglish",
    "outcome": "partial",                  # date captured, but time left unconfirmed -> partial
    "turns": [
        {"speaker": "agent", "text": "Namaste, main aapka dentist appointment book kar sakta hoon. Kaunsa din?", "start_ms": 0,    "end_ms": 3600},
        {"speaker": "user",  "text": "umm... ek minute... Friday chalega I think.",        "start_ms": 4200, "end_ms": 7100},
        {"speaker": "agent", "text": "Friday theek hai. Morning ya evening slot?",          "start_ms": 7600, "end_ms": 9900},
        {"speaker": "user",  "text": "sorry can you repeat? line thodi unclear thi.",       "start_ms": 10400, "end_ms": 12800},
        {"speaker": "agent", "text": "No problem — morning ya evening?",                    "start_ms": 13300, "end_ms": 15100},
        {"speaker": "user",  "text": "haan main baad mein confirm karta hoon.",             "start_ms": 15600, "end_ms": 17900},
    ],
}
print("id:", call_B["call_id"], "| language:", call_B["language"], "| outcome:", call_B["outcome"])
for t in call_B["turns"]:
    print("  ", t)
'''))
C.append(md('''
## PREDICT
We are about to build **call_C**, where the agent interrupts the caller. An interruption
means the agent **starts talking before the caller has finished**. In the timestamps, what
must be true for the agent's turn to overlap the caller's? (Hint: compare the agent's
`start_ms` to the caller's `end_ms`.) Commit to the relationship before you scroll.
'''))
C.append(code('''
# call_C as a TRACE — and here we plant the thing transcripts cannot show: an OVERLAP.
# Telugu-English; agent cuts in on the caller's address mid-answer (task FAILS: address never
# captured). Watch turn t2->t3: the agent's start_ms (8200) is BEFORE the user's end_ms (9000).
call_C = {
    "call_id": "call_C",
    "language": "Telugu-English",
    "outcome": "failure",                  # agent barges in, address lost, booking not completed
    "turns": [
        {"speaker": "agent", "text": "Service desk. Which area are you calling from?",      "start_ms": 0,    "end_ms": 3500},
        {"speaker": "user",  "text": "Madhapur... ante, near the metro pillar number...",   "start_ms": 4000, "end_ms": 9000},
        {"speaker": "agent", "text": "I need the full address with pincode.",               "start_ms": 8200, "end_ms": 11000},  # starts at 8200 < user's 9000 = OVERLAP
        {"speaker": "user",  "text": "ayyo... I don't remember exactly ya.",                "start_ms": 11500, "end_ms": 14000},
    ],
}
print("id:", call_C["call_id"], "| language:", call_C["language"], "| outcome:", call_C["outcome"])
for t in call_C["turns"]:
    print("  ", t)
'''))
C.append(md('''
## The cast, side by side (read this little table by ritual)

Reading ritual, three moves: say the **row count** ("three rows"), say what **one row IS**
("one row = one whole call"), read **one single cell** aloud ("call_B is Hinglish, partial").
A row here is a *call*; the columns are *facts about that call*.
'''))
C.append(code('''
# We put the three cast calls in one list so the rest of the course can loop over "the cast".
cast = [call_A, call_B, call_C]

# A compact roster: one line per call. We count turns with len(...) rather than writing 4/6/4
# by hand, because a hand-typed count rots the moment anyone edits a call above.
for c in cast:
    print(f"{c['call_id']} | {c['language']:<15} | {c['outcome']:<8} | {len(c['turns'])} turns")
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
1. Which cast call has an **overlap** baked into its timestamps, and which two turns overlap?
2. For that overlap: which exact numbers did you compare to *know* it is an overlap (name the
   two fields and the two values)?
3. Could you detect that overlap from the `text` of those turns alone? Why or why not?
'''))
C.append(md('''
## Manual-before-function: measure the gap/overlap BY HAND

The single number that turns "turns" into "timing" is the space **between** two consecutive
turns: take the **later** turn's `start_ms`, subtract the **earlier** turn's `end_ms`.

- A **positive** result = a **gap** (silence): the second speaker waited that long to start.
- A **negative** result = an **overlap**: the second speaker started *before* the first
  finished — they talked over each other.

(Out in the codebase this exact subtraction has a name — **FTO**, floor-transfer offset — and
lives in `pipeline/signals.py`. Book 04 makes you derive it in full. Today we just do the
subtraction by hand so the idea is yours before any function owns it.)
'''))
C.append(md('''
## PREDICT
1. For **call_A**, turn 1 ends at `5200`, turn 2 starts at `5700`. Gap or overlap, and how many ms?
2. For **call_C**, turn 2 (user) ends at `9000`, turn 3 (agent) starts at `8200`. Gap or overlap, how many ms?
'''))
C.append(code('''
# By hand, on the two specific pairs from the PREDICT — every intermediate value printed.
# A: agent turn 2 follows user turn 1.
a_earlier_end   = call_A["turns"][1]["end_ms"]     # user's "Four people..." ended here
a_later_start   = call_A["turns"][2]["start_ms"]   # agent's "Booked..." started here
a_offset = a_later_start - a_earlier_end            # later.start - earlier.end : the whole idea, one subtraction
print("call_A pair: later.start", a_later_start, "- earlier.end", a_earlier_end, "=", a_offset,
      "->", "GAP (silence)" if a_offset > 0 else "OVERLAP")

# C: the barge-in pair. Same subtraction, but the agent jumped in early.
c_earlier_end   = call_C["turns"][1]["end_ms"]     # user mid-address, ended at 9000
c_later_start   = call_C["turns"][2]["start_ms"]   # agent cut in at 8200
c_offset = c_later_start - c_earlier_end
print("call_C pair: later.start", c_later_start, "- earlier.end", c_earlier_end, "=", c_offset,
      "->", "GAP (silence)" if c_offset > 0 else "OVERLAP (barge-in)")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not memory): what sign (positive/negative) means
"they talked over each other", and which two fields did you subtract to get it?
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
Why did we compute the gap/overlap **by hand** before naming any function for it? (One reason
is about the idea being yours instead of hidden inside a wrapper; one is about being able to
*check* a function later because you already know the right answer.)
'''))
C.append(md('''
## Now the real thing: load `data/hero/turns.json`

Toy calls were training wheels. VoiceForge ships a real **hero call** — a constructed but
realistic Telugu-English appliance-service booking, 12 turns, with the timestamps taken from
a real assembled audio timeline. It is the same *shape* you just built by hand (turns with
speaker/text/start_ms/end_ms), only longer and messier. We load it raw and look first.
'''))
C.append(code('''
# Load the real call from disk. We read the file with json so we get the SAME kind of dicts we
# built by hand — proving a real call log is not a new mystery object, just a bigger version of
# the toy. run_nb.py runs from the repo root, so this relative path resolves.
import json                                  # stdlib JSON reader; imported here, where first needed
from pathlib import Path

hero_path = Path("data/hero/turns.json")     # the real hero call shipped with VoiceForge
hero = json.loads(hero_path.read_text())     # parse the file's text into a Python dict

# Look at the call-level metadata first (the wrapper around the turns).
print("call_id        :", hero["call_id"])
print("language       :", hero["language"])         # 'te-en' = Telugu + English code-switching
print("stress_profile :", hero["stress_profile"])   # 'interruption' — a hint at what we'll find
print("number of turns:", len(hero["turns"]))
'''))
C.append(code('''
# Print the real turns the same way we printed the toy: one line each, speaker + a slice of text.
# We truncate text to 60 chars so the TIMING columns stay readable — today timing is the point,
# the words are not. (Seeing the raw shape matters more than reading every word.)
for t in hero["turns"]:
    snippet = t["text"][:60] + ("..." if len(t["text"]) > 60 else "")
    print(f'{t["turn_id"]:>3} | {t["speaker"]:<5} | {t["start_ms"]:>6}-{t["end_ms"]:<6} | {snippet}')
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a call was an abstract idea. After Act 2 you can **build** a trace by hand (cast
A/B/C), **measure** the gap/overlap between two turns with one subtraction, and **load** the
real hero call and see it is the very same shape — just longer. You also planted one overlap
yourself (call_C) and found a real one is coming (hero's `stress_profile` literally says
`interruption`). Next act: prove what a transcript loses.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (building traces / the gap subtraction / the real load - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: make a transcript, and watch the timing die

## The whole point, made concrete

We keep claiming a **transcript loses timing and overlap**. Claims are wet cement. So now we
*build* the transcript from the trace — by deleting the timestamps — and then try to ask it a
timing question. When it cannot answer, you will have **proven** the loss with your own hands,
not taken it on faith.
'''))
C.append(md('''
## PREDICT
We will write a function that turns a trace into a transcript by keeping only `speaker` and
`text`. After that, we will try to compute the hero call's barge-in offset **from the
transcript**. Will the transcript version be able to produce the `-800 ms` number? Commit to
**yes** or **no**, and why, before running.
'''))
C.append(code('''
# YOUR TURN - your prediction about the transcript, stored for the reveal cell to confront.
my_transcript_can_time = None   # <- replace None with the string "yes" or "no"

if my_transcript_can_time is None:
    print("fill in my_transcript_can_time (\\"yes\\"/\\"no\\") above, then re-run.")
else:
    print("prediction locked:", my_transcript_can_time)
'''))
C.append(code('''
# Manual-before-function once more: do the stripping BY HAND on the first two hero turns,
# so "make a transcript" is a concrete deletion you watched, not an abstraction.
first_two = hero["turns"][:2]                 # just two turns, small enough to see fully
print("TRACE (timed) — what we start with:")
for t in first_two:
    print("  ", t)

print("\\nTRANSCRIPT (text only) — same turns, timestamps DELETED by hand:")
for t in first_two:
    # we copy ONLY speaker + text into a new dict; start_ms/end_ms are not carried over at all.
    # this deletion IS the trace->transcript reduction, shown on two turns before we generalize.
    print("  ", {"speaker": t["speaker"], "text": t["text"]})
'''))
C.append(code('''
# Now the function — it does exactly what you just did by hand, for every turn.
def to_transcript(call_turns):
    # Build a new list keeping only the two text-y fields. We return a NEW list (not mutate the
    # input) so the original trace stays intact in memory — destroying your only copy of the
    # timing would be the very loss we are studying, done by accident.
    return [{"speaker": t["speaker"], "text": t["text"]} for t in call_turns]

hero_transcript = to_transcript(hero["turns"])   # the hero call, reduced to words + who-said-them
print("transcript turns:", len(hero_transcript), "(same count — we lost columns, not turns)")
for row in hero_transcript[:4]:
    print("  ", row)
'''))
C.append(md('''
## The reveal — ask the transcript a timing question

The trace knows the barge-in: hero turn **t2** (the caller) ends at `18949`, and turn **t3**
(the agent) starts at `18149` — the agent began **800 ms before** the caller finished. That
`-800` is a real interruption, and it is exactly why this call's `stress_profile` is
`interruption`.

Now watch the same question hit the transcript, where `start_ms`/`end_ms` no longer exist.
'''))
C.append(code('''
# BREAK-IT (guided) — this cell is SUPPOSED to error. Read what happens; do not fix it yet.
# We try to compute the barge-in offset FROM THE TRANSCRIPT. The transcript rows have no
# 'end_ms' / 'start_ms' keys — we deleted them — so Python cannot even find the numbers to
# subtract. The crash is the proof: the information is physically gone.
# EXPECTED FAILURE FOR LEARNING
user_turn  = hero_transcript[1]    # t2, the caller, in the TRANSCRIPT (text-only)
agent_turn = hero_transcript[2]    # t3, the agent, in the TRANSCRIPT (text-only)
offset = agent_turn["start_ms"] - user_turn["end_ms"]   # KeyError: 'start_ms' — the field was deleted
print("barge-in offset from transcript:", offset)
'''))
C.append(md('''
## Reading the error (bottom-up, always)

The wall of red is a **traceback**; read the **last line first**. It says
`KeyError: 'start_ms'` — "you asked the transcript row for a field called `start_ms`, and it
has none." That is not a typo to fix. It is the literal shape of the loss: a transcript row is
`{speaker, text}` and nothing else, so a timing question has nowhere to land.

Compare the two failure modes (this distinction runs through the whole course):
- **Loud crash** (what we got): the transcript *cannot fake* a timing answer, so Python stops
  and tells you. Friendly.
- **Silent wrongness** (the scary one): if instead we had *assumed* "no timestamp means no
  overlap" and quietly reported "0 ms, looks fine", the barge-in would vanish with **no error
  at all**. The next cells show that silent version — the dangerous one.
'''))
C.append(code('''
# Recovery: the SAME question, asked of the TRACE (which still has the timestamps). This is the
# right answer the broken cell could never reach — and it matches the -800 the markdown claimed.
u = hero["turns"][1]    # t2 caller, from the full TRACE
a = hero["turns"][2]    # t3 agent,  from the full TRACE
barge_in_offset = a["start_ms"] - u["end_ms"]   # later.start - earlier.end, the Act-2 subtraction
print("barge-in offset from the TRACE:", barge_in_offset, "ms",
      "-> OVERLAP, agent cut in early" if barge_in_offset < 0 else "")

if my_transcript_can_time is not None:
    print("your prediction was:", my_transcript_can_time,
          "-> the transcript could NOT produce this number; only the trace could.")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. What exact error did asking the transcript for `start_ms` raise, and what does that error
   *mean* about the data?
2. The same barge-in question answered fine against the **trace**. State the rule this proves
   about which record VoiceForge must keep.
3. Why is the loud `KeyError` *friendlier* than a function that quietly returns "0 ms, no
   overlap" for a transcript?
'''))
C.append(md('''
## WRONG-INTUITION TRAP

**The wrong belief:** *"The transcript has all the turns and all the words — so it has the
whole conversation. Timestamps are just metadata I can drop."*

Two turns can have **identical text** and be a completely different call. The next cell builds
two versions of the *same two lines*: in one the agent waits politely; in the other the agent
**barges in 800 ms early**. The transcript of both is **byte-for-byte identical**. If you
believed the transcript was the whole conversation, you would call these two calls the same.
They are not — one is fine, one is rude and loses the caller's words.
'''))
C.append(code('''
# Same words, two different calls — the difference lives ONLY in the timestamps.
polite = [
    {"speaker": "user",  "text": "near the metro pillar number...", "start_ms": 4000, "end_ms": 9000},
    {"speaker": "agent", "text": "I need the full address.",        "start_ms": 9400, "end_ms": 11000},  # starts 400ms AFTER user ends -> polite gap
]
rude = [
    {"speaker": "user",  "text": "near the metro pillar number...", "start_ms": 4000, "end_ms": 9000},
    {"speaker": "agent", "text": "I need the full address.",        "start_ms": 8200, "end_ms": 11000},  # starts 800ms BEFORE user ends -> barge-in
]

# Their TRANSCRIPTS (text-only) — compare them directly. We use == on the stripped versions;
# if the transcripts are equal, no text-only analysis could EVER tell these calls apart.
print("transcripts identical? ->", to_transcript(polite) == to_transcript(rude))

# Their TIMING — the one thing that differs. Same subtraction as always, on each version.
print("polite offset:", polite[1]["start_ms"] - polite[0]["end_ms"], "ms (gap, fine)")
print("rude   offset:", rude[1]["start_ms"]   - rude[0]["end_ms"],   "ms (overlap, barge-in)")
'''))
C.append(md('''
## The reveal

`transcripts identical? -> True`, yet one call is a clean exchange and the other is the agent
talking over the caller. **The entire difference between a good call and a bad one lived in
two integers the transcript threw away.** This is the trap defused: the transcript is *not*
the whole conversation; it is the conversation with its timing amputated. Keep the trap — it
returns with real force in book 04 (timing metrics) and book 07 (failure tags), where "the
agent interrupts" is a failure you can only *see* in the trace.
'''))
C.append(md('''
## YOUR break now

Author your own version of the trap. Below is one user turn and one agent turn with timestamps
you control. **Predict** (as a comment) whether your chosen agent `start_ms` makes a gap or an
overlap and by how many ms — then set the number and run to check yourself.
'''))
C.append(code('''
# YOUR TURN - self-authored BREAK-IT: bend the timing and predict the offset's sign.
# my prediction: <write here: will it be a gap or an overlap, and how many ms? and why?>

my_user  = {"speaker": "user",  "text": "yes that's the one", "start_ms": 1000, "end_ms": 5000}
my_agent = {"speaker": "agent", "text": "Confirmed.",          "start_ms": 5000, "end_ms": 6000}  # <- change this start_ms

# Same subtraction you have used all notebook; now YOU pick the input and own the prediction.
my_offset = my_agent["start_ms"] - my_user["end_ms"]
print("your offset:", my_offset, "ms ->",
      "GAP (silence)" if my_offset > 0 else ("OVERLAP (barge-in)" if my_offset < 0 else "ZERO (back-to-back)"))
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
1. You made two calls with **identical transcripts** read as different calls. What single kind
   of information made them different, and how many numbers per turn carries it?
2. State the **one rule** of this whole project that this proves (it is the book's clean
   sentence — try to say it before you reach the bottom of the notebook).
3. Name one real VoiceForge artifact on disk that stores calls in the timed (trace) shape, not
   the text-only (transcript) shape.
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: it was plausible that "transcript ≈ the call". After Act 3 you have **proven**
otherwise three ways: a transcript physically lacks the timing fields (the `KeyError`), the
same timing question answers fine against the trace, and two calls with **identical
transcripts** can differ entirely in the timing the transcript dropped. "It has all the
words" is not "it has the whole conversation".
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the identical-transcripts trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where the call log lives, and how to defend it

## Where this sits in real VoiceForge

The trace you built by hand today is the **real input format of the entire pipeline** — not a
teaching simplification:

- `data/hero/turns.json` — the very file you loaded: one real call log, 12 turns with real ms.
- `data/normalized/*.json` — 11 real calls (the hero + 10 from a corpus called SpokenWOZ),
  every one in this same `turns` shape.
- `schemas/call_log.md` — the formal field-by-field spec of this object. **That is literally
  book 02, the next book.** Today you met the thing; next you pin down its exact schema
  (types, the `end_ms = null` rule, the `speaker` enum).
- `pipeline/signals.py` — reads these traces and computes the timing (the gap/overlap
  subtraction you did by hand, generalized over a whole call). Book 04.

Everything VoiceForge measures, judges, and trains on **starts from a call log in this shape.**
'''))
C.append(md('''
## The concept at three levels (say the right one to the right person)

- **To a beginner:** "A call log is the call written down as a list of turns, and each turn is
  stamped with when it started and stopped — so we can see *when* people talked, not only
  *what* they said."
- **To an engineer:** "A call log is an ordered list of `{speaker, text, start_ms, end_ms}`
  turns plus call-level metadata. The **trace** keeps `start_ms`/`end_ms`; the **transcript**
  is its projection onto `{speaker, text}`. Timing signals (FTO, overlap, latency) are
  computable from the trace and **undefined** on the transcript — so the trace is the source
  of truth and the transcript is a lossy view of it."
- **To a founder:** "We store calls with millisecond timing, not just text, because the
  failures that lose customers — the bot interrupting people, the three-second dead-air —
  are invisible in a transcript and obvious in the timing. We grade the recording's behavior,
  not a tidy script of it."
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell, no grading today)

Of the three cast calls, **call_C** fails because of a barge-in you can only see in timing.
Which **timing field** (`start_ms` or `end_ms`) of which speaker's turn is the one that, if
you nudged it later, would turn that barge-in into a polite gap and possibly *save* the call?
Store your guess — book 04 will let you actually run that experiment.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for book 04 to confront.
my_course_prediction = ""   # which field + whose turn, and WHY moving it removes the overlap

if len(my_course_prediction.strip()) < 20:
    print("write your prediction above (which field + why), then re-run.")
else:
    print("PREDICTION STORED:", my_course_prediction)
'''))
C.append(md('''
## Where the call-log idea itself bites you (honest failure modes)

- **`end_ms` can be `null`.** Real corpora sometimes give onset but not offset. With no
  `end_ms` you cannot compute an *overlap* for that turn — only a one-sided latency. The
  schema (book 02) keeps `null` legal precisely so nobody *invents* a fake end time and
  manufactures a fake overlap. Honesty over completeness.
- **One shared clock per call.** Every `start_ms`/`end_ms` in a call must come from the *same*
  timeline, or subtracting them is meaningless. The hero call notes `timestamps_from:
  assembly_timeline` for exactly this reason.
- **Turns are an interpretation.** "One uninterrupted stretch of one speaker" is a judgement
  call at the edges (where does a turn end if someone trails off?). The trace is faithful, but
  it is not the raw audio — it is already one layer of decisions above it.
'''))
C.append(md('''
## Defense questions (×3 — try to answer before opening each)

**1. "You loaded one call. Isn't 'trace vs transcript' just a fancy word for 'I kept the
timestamps'?"**
<details><summary>answer</summary>Yes — and that is the whole point. The two records differ by exactly two integer fields per turn, but those fields are where interruptions, dead-air, and latency live. I proved it: two calls with byte-identical transcripts differed only in timing, and one was a barge-in. The fancy word just names which record is the source of truth.</details>

**2. "Why not store the transcript and recompute timing later if you need it?"**
<details><summary>answer</summary>You can't recompute what you deleted. Timing is a property of the audio timeline; the transcript is a projection that drops it. From `{speaker, text}` there is no function that recovers `start_ms`/`end_ms` — I hit the `KeyError` on purpose to show the information is physically gone, not merely hidden.</details>

**3. "Your hero call is `constructed: true`. Doesn't that make the timing fake?"**
<details><summary>answer</summary>The scenario is constructed and disclosed (`docs/limitations.md`), but the timestamps come from a real assembled audio timeline (`timestamps_from: assembly_timeline`), so the -800 ms barge-in and the 1620 ms gap are real offsets on a real clock — not numbers I typed. The 10 SpokenWOZ calls in `data/normalized/` are real corpus calls in the identical shape.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: the trace you built by hand is VoiceForge's real input (`turns.json`,
`data/normalized/*`), the next book (02) pins its exact schema, the timing you measured by
hand is what `pipeline/signals.py` computes at scale, and you can pitch "trace vs transcript"
to a beginner, an engineer, and a founder — plus defend why the timing is real and
unrecoverable once dropped.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. Define a **call log** and name the **four parts of a turn**.
2. State the difference between a **trace** and a **transcript**, and which one is a lossy
   view of the other.
3. Give the one **subtraction** that detects a gap vs an overlap, naming the two fields.
4. Explain **why a transcript cannot answer a timing question** (what the `KeyError` proved).
5. Recall the trap: **two calls, identical transcripts, different timing** — and one real
   VoiceForge place this matters.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about what a call log is

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"We judge the conversation trace, not just the transcript."**

A call log is an ordered list of timed turns. The timing is not decoration — it is where the
interruptions and silences live, and those are what make a call good or bad. If your sentence
captures that in your own words, this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "01_what_is_a_call_log.ipynb"   # <- this notebook's filename
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

**01 done** (pending your teach-back) → **02 · The call_log schema** — you have the *picture*
of a call log; next you pin its exact contract: every field's type, why `end_ms` may be
`null`, the `speaker` enum, and the `source`/`stress_profile` values. Then 03 → 04 (timing:
the gap/overlap subtraction you did by hand, computed over whole calls) → onward.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "01_what_is_a_call_log.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
