#!/usr/bin/env python3
# Builds P01_python_objects_for_call_logs.ipynb — the ONE atomic concept:
# nested Python objects (dict/list/JSON) are the natural shape of a call.
# Rerun: .venv/bin/python notebooks/build_P01.py
# Style/contract: matches notebooks/build_P00.py exactly (md()/code() helpers, four acts,
# the marker strings the audit greps for). NEVER hand-write raw .ipynb JSON.
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
# P01 · Python objects for call logs

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Name the four building blocks — **value** (str/num/bool), **list** (a sequence),
   **dict** (named facts), and **nesting** (objects inside objects) — and say what each is *for*
2. Explain **why a phone call is naturally nested**: one call holds many turns, each turn holds
   its own facts (who spoke, what they said, when)
3. Build the course's three recurring calls — **call_A, call_B, call_C** — BY HAND as nested
   `call_log` objects, from nothing
4. **Index and walk** into any such object: reach one field, loop every turn, pull a column

The topic is small Python on purpose. The payoff is large: every later book — timing, task
success, judges, training pairs — reads exactly this shape.
'''))
C.append(md('''
## 2 — Knowledge map

`P00 (the learning ritual) → THIS (Python objects for call logs) → P02 (tables)`

Why this book exists, and in this exact spot: in P00 you learned the *ritual* (predict → run →
inspect → explain → change → observe → defend). You have no DATA to point the ritual at yet.
This book hands you the data's native shape — the nested object — so that P02 can flatten it
into a **table**, P03 can **plot** it, and P04 can **debug** it. A table is a squashed object;
you cannot understand the squash until you have held the thing un-squashed. That thing is here.
'''))
C.append(md('''
## 3 — Baby intuition

Picture one phone call as a shoebox. Inside the box are sticky notes, in order, one per time
someone spoke — these are the **turns**, and order matters (turn 5 answered turn 4). On each
sticky note are a few labelled facts: *who* spoke, *what* they said, *when* they started, *when*
they stopped.

So a call is a **box of ordered notes, where each note is a little bag of labelled facts**.
Python has exactly two containers for this: a **list** (the ordered notes) and a **dict** (the
bag of labelled facts). Put dicts inside a list inside a dict and you have re-built the call.
That sentence is the whole notebook.
'''))
C.append(md('''
## 4 — The formal version

Four Python building blocks, smallest to largest:

| block | what it is | the call-log job it does |
|---|---|---|
| value | one piece of data: `str` text, `int`/`float` number, `bool` true/false | a single fact: `"agent"`, `18949`, `True` |
| list `[...]` | an **ordered** sequence; position has meaning; can hold duplicates | the **turns**, in the order they were spoken |
| dict `{...}` | **named** slots: `key → value`; look things up by name, not position | the **facts of one turn** (speaker, text, start_ms) |
| nesting | any value may itself be a list or dict | a call = dict whose `turns` key holds a list of dicts |

Two facts you will lean on all course:
- a **list** answers *"what is the 3rd turn?"* — ask by **position** (`turns[2]`)
- a **dict** answers *"who was the speaker?"* — ask by **name** (`turn["speaker"]`)

This shape has a name in the repo: the **call_log** (see `schemas/call_log.md`). Everything
downstream reads it.
'''))
C.append(md('''
## 5 — Why not just one long string?

A natural first instinct: "a call is just its transcript — one big block of text." Hold that
thought; the next cells test it. The question the whole book turns on: **what can you ASK of a
plain string, versus what can you ask of a structured object?** If the structure earns its
keep, it will be by answering questions the string cannot.
'''))
C.append(code('''
# The "call as one big string" instinct, made concrete so we can poke it.
# We write it the way a raw transcript dump actually looks - speaker labels inline, no timing.
transcript = "agent: what area are you in? user: Madhapur side, near the metro station."

# Inspection first (the P00 habit): look at the raw object and its type before judging it.
print(transcript)              # the whole thing
print(type(transcript))        # it is a single str - one undifferentiated blob
print(len(transcript))         # len() of a str counts CHARACTERS, not turns - a hint of trouble
'''))
C.append(md('''
## PREDICT
The string above clearly contains **two turns** (agent, then user). But it is stored as one
`str`. If you wanted *"the text of the user's turn, by itself"*, could you get it cleanly?
Commit out loud: **yes / no**, and why — then run the next cell.
'''))
C.append(code('''
# We TRY to pull the user's turn out of the flat string. There is no "turn 2" to ask for,
# so the only tool is brittle text-slicing - hunt for the literal "user:" and cut there.
marker = "user:"
cut_at = transcript.find(marker)            # find() returns the index where "user:" begins
user_part = transcript[cut_at + len(marker):].strip()  # everything after the marker, trimmed
print("user turn, extracted by string-hacking:", repr(user_part))

# It "worked" - but only because we hand-coded the exact label. Change "user:" to "User :"
# in the data and this silently grabs the wrong span. The structure was never really there;
# we faked it with a substring search. That fragility is the lesson.
print("notice: this broke the moment the format wobbles - the turn boundary was never real")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What is the difference between asking a **list** for something and asking a **dict**?
   (Hint: one word each — *position* vs *name*.)
2. Why is "the call is just one big string" a fragile way to store a conversation?
3. What two Python containers will we use to give a call real structure?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (maybe) pictured a call as text. After Act 1 you should picture it as a
**box of ordered notes, each note a bag of labelled facts** — and you should distrust the flat
string, because the turn boundaries in it are imaginary until you build them. The rest of the
book makes those boundaries real, one block at a time: value → list → dict → nesting.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of why a call wants structure, not a flat string. Yours, not mine.
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
# Act 2 — Mechanics: build the four blocks, smallest to largest

## Block 1 of 4 — values (the atoms)

We start at the bottom: a single **value**. Three kinds carry almost every fact in a call log:
**text** (`str`), **numbers** (`int` for whole, `float` for decimal), and **true/false** (`bool`).
Everything larger is just these atoms arranged. We meet them alone before we nest them, because
a structure you cannot read at the atom level will stay a fog at the object level.
'''))
C.append(md('''
## PREDICT
For each variable in the next cell, predict its **type** before running:
`speaker`, `start_ms`, `confidence`, `task_succeeded`. Whole number? decimal? text? true/false?
Commit to all four.
'''))
C.append(code('''
# One value per line, each a real field you will see in a call log. We print value AND type,
# because in this course "what kind of thing is this?" is a question we ask constantly.
speaker = "agent"            # str  - text; who is talking on this turn
start_ms = 18949             # int  - a whole number of milliseconds from call start
confidence = 0.82            # float- a decimal; e.g. how sure the transcriber was
task_succeeded = True        # bool - a yes/no fact about the whole call

for value in (speaker, start_ms, confidence, task_succeeded):
    # type(...).__name__ prints the short name ('str') instead of "<class 'str'>" - easier to scan
    print(repr(value), "->", type(value).__name__)
'''))
C.append(md('''
## Why the type matters (it is not pedantry)

Types decide what you are *allowed to do*. You can subtract two `int` timestamps to get a gap in
ms — that subtraction is the heart of book 04. You cannot subtract two `str`. Storing a number
as text (`"18949"` instead of `18949`) looks identical on screen and breaks silently later. The
next cell shows the screen-lies-but-type-tells point in miniature.
'''))
C.append(code('''
# Two values that LOOK the same printed, but are different kinds underneath.
number_ms = 18949            # an int we can do math on
text_ms = "18949"            # a str that merely looks like a number

print(number_ms, text_ms)                       # identical on screen - the screen lies
print(type(number_ms).__name__, type(text_ms).__name__)   # the type tells the truth

# math is the tell: int supports subtraction (a real ms gap); str would error or concatenate.
print("int minus 600 =", number_ms - 600)       # 18349 - a meaningful smaller timestamp
print("can we trust the screen? no - we trust type() and what operations succeed")
'''))
C.append(md('''
## Block 2 of 4 — the list (ordered turns)

A **list** is an ordered sequence written in square brackets `[...]`. Two properties make it the
right home for **turns**: (1) **order is preserved** — turn 5 stays after turn 4, which matters
because a conversation IS its order; (2) you fetch items by **position** with an index. We build
a toy list of speakers first — just the *who*, no other facts yet — to isolate list-ness.
'''))
C.append(md('''
## PREDICT
`speakers = ["agent", "user", "agent", "user"]`.
Predict: what does `speakers[0]` give? What does `speakers[2]` give? What is `len(speakers)`?
(Indexing starts at **0** — commit to the exact strings and the count.)
'''))
C.append(code('''
# A toy list: just the speaker of each turn, in spoken order. Order is the whole point here.
speakers = ["agent", "user", "agent", "user"]   # the call opened with the agent, then alternated

print("the whole list:", speakers)
print("len (how many turns):", len(speakers))   # len() of a LIST counts elements - i.e. turns

# Indexing is 0-based: the FIRST element is at position 0, not 1. This trips up everyone once.
print("speakers[0] (first turn):", speakers[0])
print("speakers[2] (third turn):", speakers[2])
print("speakers[-1] (last turn, negative counts from the end):", speakers[-1])
'''))
C.append(md('''
## PREDICT
We now look at a **slice**: `speakers[0:2]`. Slicing takes a *range* of positions.
Predict exactly what comes back, and how many items it has. (Edge to commit on: is position 2
**included** or **excluded**?)
'''))
C.append(code('''
# A slice grabs a RANGE of positions - we will use slices to say "the first two turns" etc.
# The rule that surprises people: the start index is included, the STOP index is excluded.
first_two = speakers[0:2]                 # positions 0 and 1 -> NOT position 2
print("speakers[0:2]:", first_two, "(length", len(first_two), ")")

# A loop is how you VISIT every element - the bread-and-butter of walking turns later.
for index, who in enumerate(speakers):    # enumerate gives position AND value together
    # we print the position so the 0-based counting stays visible, not hidden
    print("turn at index", index, "was spoken by", who)
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
1. In `speakers[0]`, why is the answer the **first** element and not the second?
2. `speakers[0:2]` returned two items, not three — state the slicing rule in your own words.
3. Why is a **list** (not a set or a dict) the right container for *turns* specifically?
'''))
C.append(md('''
## Block 3 of 4 — the dict (named facts of ONE turn)

A list answers *"what is at position N?"*. But a turn has several facts — speaker, text,
start, end — and "position 0 of a turn" is meaningless; you want them **by name**. That is a
**dict**: curly braces `{...}` holding `key: value` pairs. You look things up by the key.
We now upgrade ONE turn from a bare speaker string to a full bag of labelled facts.
'''))
C.append(md('''
## PREDICT
The next cell builds one turn as a dict with keys `turn_id, speaker, text, start_ms, end_ms`.
Predict what `turn["speaker"]` returns, and what `turn["start_ms"]` returns. Then the harder one:
what do you think `turn["duration"]` would do, given we never put a `duration` key in?
'''))
C.append(code('''
# ONE turn, now as a dict: each fact gets a NAME (the key) instead of a position.
# These five keys are exactly the call_log turn schema (schemas/call_log.md) - real field names.
turn = {
    "turn_id": "t2",          # a stable label for this turn; judges cite these as evidence later
    "speaker": "user",        # who spoke
    "text": "Madhapur side, near the metro station.",  # what they said
    "start_ms": 10947,        # when the turn began (ms from call start)
    "end_ms": 18949,          # when it ended
}

# Look up BY NAME - this is the dict superpower. Position is irrelevant and unavailable.
print("speaker:", turn["speaker"])
print("start_ms:", turn["start_ms"])
print("the keys this turn carries:", list(turn.keys()))   # what facts do we have on file?
'''))
C.append(md('''
## PREDICT
Two ways to ask a dict for a key that is **missing** (`turn["duration"]` vs
`turn.get("duration")`). One of them crashes, one returns a gentle `None`. Predict **which is
which** before running — this exact choice prevents a whole class of bugs in book 04.
'''))
C.append(code('''
# Missing keys: the difference between a crash and a polite None. Both are useful - on purpose.

# .get() asks softly: "give me duration if you have it, else None." It never raises.
# We use .get() whenever a field is OPTIONAL (end_ms can be null in the real schema!).
maybe_duration = turn.get("duration")    # there is no 'duration' key -> returns None, no crash
print("turn.get('duration') ->", maybe_duration)

# We can derive duration ourselves from facts we DO have - end minus start, an int subtraction.
# This only works because start_ms/end_ms are ints, not strings (Block 1 mattered).
duration = turn["end_ms"] - turn["start_ms"]   # ms the user spoke for
print("derived duration (end_ms - start_ms):", duration, "ms")
'''))
C.append(md('''
## BREAK-IT (guided) — the missing-key crash, on purpose

Square-bracket lookup of a key that does not exist does **not** return `None` — it raises
`KeyError`. We trigger it deliberately so the failure is familiar when it finds you for real.
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. Read the traceback; do not fix it yet.
# EXPECTED FAILURE FOR LEARNING: square brackets on a missing key raise KeyError (unlike .get()).

# We ask for ["duration"] with brackets - the strict form. The key is absent, so Python refuses.
print("trying turn['duration'] with strict brackets...")
print(turn["duration"])   # KeyError: 'duration' - there is no such named slot
'''))
C.append(md('''
## Recover + read the error

That red block is a **traceback** (the P00 ritual: read the **last line first**). It says
`KeyError: 'duration'` — "you asked for a named slot I do not have." The fix is to ask the way
that matches your intent: `["key"]` when the key MUST exist (you *want* the crash if it does
not), `.get("key")` when it is optional. The next cell shows the safe read and continues.
'''))
C.append(code('''
# RECOVERY: ask softly for the optional field, supply a fallback, and carry on.
# The second argument to .get() is the default returned when the key is missing.
safe_duration = turn.get("duration", "unknown")   # no crash; we get the string "unknown"
print("safe read with .get(default):", safe_duration)

# And the value we genuinely have, read the strict way because turn_id MUST be present:
print("strict read of a key that exists:", turn["turn_id"])
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. When do you reach into a structure **by position**, and when **by name**?
2. `turn["duration"]` and `turn.get("duration")` differ how, and when do you want each?
3. Why did Block 1 (types) have to come before this — what breaks if `start_ms` were a string?
'''))
C.append(md('''
## Block 4 of 4 — NESTING (the call appears)

Now the payoff. A list can hold dicts. A dict can hold a list. Put **a list of turn-dicts
inside a call-dict** and the conversation re-assembles itself: top-level facts about the call
(id, language, outcome) sit beside a `turns` key whose value is the ordered list of turn bags.
This is the **call_log**. We build the smallest possible one first — two turns — so the nesting
is visible at a glance.
'''))
C.append(md('''
## PREDICT
The next cell builds a 2-turn call dict. Predict: what **type** is `mini_call["turns"]`?
What type is `mini_call["turns"][0]`? And what does `mini_call["turns"][0]["speaker"]` give?
(Read that last one left-to-right: call → its turns list → first turn → that turn's speaker.)
'''))
C.append(code('''
# The smallest real call_log: top-level facts + a 'turns' key holding a LIST of turn DICTS.
# This is the nest: dict -> (value at key 'turns') -> list -> (each element) -> dict.
mini_call = {
    "call_id": "toy_001",        # top-level fact about the whole call
    "language": "en",            # another whole-call fact
    "turns": [                   # the value here is a LIST - the ordered turns
        {"turn_id": "t1", "speaker": "agent", "text": "What area are you in?", "start_ms": 0,     "end_ms": 3400},
        {"turn_id": "t2", "speaker": "user",  "text": "Madhapur side.",         "start_ms": 4100, "end_ms": 6200},
    ],
}

# Peel the nest one layer at a time so each TYPE is explicit (this is the core skill of the book).
print("type of mini_call:           ", type(mini_call).__name__)            # dict (the call)
print("type of mini_call['turns']:  ", type(mini_call["turns"]).__name__)   # list (the turns)
print("type of turns[0]:            ", type(mini_call["turns"][0]).__name__) # dict (one turn)
'''))
C.append(md('''
## Walking the nest (the move you will do a thousand times)

Reaching a deep value is just chaining the two operations you already know: `["name"]` to enter
a dict, `[position]` to enter a list. Read the chain **left to right**, saying each layer aloud.
The cell does the famous deep reach: the first turn's speaker.
'''))
C.append(code('''
# The deep reach, narrated. Each bracket moves you one layer DOWN into the nest.
call = mini_call                                 # start at the top (the whole call dict)
turns_list = call["turns"]                       # step 1: enter dict by name -> the list of turns
first_turn = turns_list[0]                       # step 2: enter list by position -> the first turn dict
first_speaker = first_turn["speaker"]            # step 3: enter dict by name -> the speaker value
print("walked step by step ->", first_speaker)

# The same thing in one chained expression - identical result, just without the named stops.
# We show the long form FIRST (above) so this one-liner is a convenience, not a mystery.
print("same in one chain     ->", mini_call["turns"][0]["speaker"])
'''))
C.append(md('''
## PREDICT
We loop every turn and print *who spoke* and *how long they spoke* (`end_ms - start_ms`).
Predict the two durations for `mini_call` before running. (t1: 0→3400, t2: 4100→6200.)
'''))
C.append(code('''
# Looping the turns is how you process a WHOLE call. 'for turn in call["turns"]' visits each dict.
for turn in mini_call["turns"]:
    # inside the loop, 'turn' is one dict - read its named facts and derive what we need.
    # duration only makes sense as end minus start, and only because both are ints (Block 1 again).
    spoke_for = turn["end_ms"] - turn["start_ms"]
    print(turn["turn_id"], "|", turn["speaker"], "| spoke for", spoke_for, "ms")
'''))
C.append(md('''
## Pulling a "column" out of the nest

Sometimes you want just one field across **all** turns — every speaker, or every start time.
That is a **list comprehension**: "the value at key K, for each turn in the list." It is the
bridge to P02, where this exact move becomes a table column. We build two columns by hand.
'''))
C.append(code('''
# A comprehension reads as a sentence: "speaker, for each turn in the call's turns."
# We do it by hand here; in P02 a DataFrame will hand you these columns for free - earned later.
all_speakers = [turn["speaker"] for turn in mini_call["turns"]]   # the 'speaker' column
all_starts   = [turn["start_ms"] for turn in mini_call["turns"]]  # the 'start_ms' column

print("speaker column:", all_speakers)
print("start_ms column:", all_starts)
print("note: each is a flat LIST now - we squeezed one field out of the nested object")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. In `mini_call["turns"][0]["speaker"]`, name what each of the three brackets does, in order.
2. Why is the value at `"turns"` a **list** and not a **dict**?
3. What did the comprehension produce, and why is that the shape a table wants?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: "structure" was a vague word. After Act 2 you can build it from atoms: a **value** is one
fact, a **list** orders the turns, a **dict** names a turn's facts, and **nesting** (list-of-dicts
inside a dict) re-creates the whole call. You can also **walk** it — `["name"]` to enter a dict,
`[pos]` to enter a list — and **pull a column** with a comprehension. That is the entire toolkit
the rest of the course stands on.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner: what nesting IS, or what walking a nest means - your pick

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))
C.append(md('''
## YOUR TURN — build a turn from scratch

You have seen turns built. Now build one. Fill the five fields for a brand-new turn (any
plausible content), then the guard checks you supplied all five with the right types.
'''))
C.append(code('''
# YOUR TURN - author one turn dict yourself. Replace each None with a real value.
# This is the manual-before-anything rep: you cannot trust a structure you have never built.
my_turn = {
    "turn_id": None,     # <- a string like "t1"
    "speaker": None,     # <- "agent" or "user"
    "text": None,        # <- a string of what was said
    "start_ms": None,    # <- an int (ms)
    "end_ms": None,      # <- an int (ms), larger than start_ms
}

# The guard runs clean when UNFILLED, and only validates once you have filled every slot.
# We check types too, because a turn with "start_ms": "0" (a string) is a bug factory.
if any(v is None for v in my_turn.values()):
    print("fill in all five fields above (replace every None), then re-run.")
elif not (isinstance(my_turn["start_ms"], int) and isinstance(my_turn["end_ms"], int)):
    print("start_ms and end_ms must be ints (numbers), not strings - fix and re-run.")
else:
    print("turn built! it lasted", my_turn["end_ms"] - my_turn["start_ms"], "ms")
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the nest, and the trap that costs demos

## Build the real cast — call_A, call_B, call_C (BY HAND)

Time to build the three calls that travel through the whole course, as full nested `call_log`
objects, from nothing. This is the lesson, not a detour: you only trust a shape you have
assembled with your own hands. We keep ids/languages/outcomes **exactly** as the course spec
defines them (the consistency reviewer checks this), and we keep each tiny — 2–3 turns — so the
structure stays readable.
'''))
C.append(code('''
# Call A - clean English success: a cooperative booking, all fields captured.
# Built by hand so the nest is yours: dict (call) with a 'turns' list of turn dicts.
call_A = {
    "call_id": "call_A",
    "language": "en",                       # English, per the course cast spec
    "stress_profile": "clean",              # the scenario class (book 04 uses this term)
    "outcome": "success",                   # task completed - the whole-call verdict
    "turns": [
        {"turn_id": "t1", "speaker": "agent", "text": "Hi! I can book your appointment. What day works?", "start_ms": 0,    "end_ms": 2600},
        {"turn_id": "t2", "speaker": "user",  "text": "Tuesday at 3pm, please.",                          "start_ms": 3000, "end_ms": 4800},
        {"turn_id": "t3", "speaker": "agent", "text": "Booked: Tuesday 3pm. Anything else?",              "start_ms": 5100, "end_ms": 7200},
    ],
}
# one print to confirm the object exists and see its top-level shape
print("built", call_A["call_id"], "with", len(call_A["turns"]), "turns, outcome:", call_A["outcome"])
'''))
C.append(code('''
# Call B - Hinglish partial: hesitations and a repeat request; task only partly done.
# Same schema, different content - structure is reusable, which is the point of a schema.
call_B = {
    "call_id": "call_B",
    "language": "hi-en",                    # Hinglish (Hindi+English), per the cast spec
    "stress_profile": "pause_heavy",        # hesitations -> a pause-heavy profile
    "outcome": "partial",                   # only part of the task got done
    "turns": [
        {"turn_id": "t1", "speaker": "agent", "text": "Hello, I can help with your order. Kya chahiye?", "start_ms": 0,    "end_ms": 2500},
        {"turn_id": "t2", "speaker": "user",  "text": "haan woh... ek minute... can you repeat please?",  "start_ms": 3200, "end_ms": 6400},
        {"turn_id": "t3", "speaker": "agent", "text": "Sure - I can add one item. Aur kuch?",             "start_ms": 6900, "end_ms": 9100},
    ],
}
print("built", call_B["call_id"], "with", len(call_B["turns"]), "turns, outcome:", call_B["outcome"])
'''))
C.append(code('''
# Call C - Telugu/Tenglish failure: the agent INTERRUPTS the caller mid-answer (barge-in),
# plus address ambiguity. This mirrors the real hero call in data/hero/turns.json (book 04+).
# The interruption is encoded honestly in the timing: t3 STARTS before t2 ENDS (overlap).
call_C = {
    "call_id": "call_C",
    "language": "te-en",                    # Telugu-English, per the cast spec
    "stress_profile": "interruption",       # the agent talks over the caller
    "outcome": "failure",                   # task not completed
    "turns": [
        {"turn_id": "t1", "speaker": "agent", "text": "Which area should I send the technician to?",        "start_ms": 0,     "end_ms": 3000},
        {"turn_id": "t2", "speaker": "user",  "text": "Madhapur side, near the metro... ante...",            "start_ms": 3500, "end_ms": 9000},
        {"turn_id": "t3", "speaker": "agent", "text": "I need a full address with pincode.",                 "start_ms": 8200, "end_ms": 11000},
    ],
}
# Notice t3.start_ms (8200) < t2.end_ms (9000): the agent began before the user finished.
# That negative gap (8200 - 9000 = -800 ms) IS the barge-in. We just stored it as plain ints.
print("built", call_C["call_id"], "- t3 starts at", call_C["turns"][2]["start_ms"],
      "but t2 ends at", call_C["turns"][1]["end_ms"], "-> overlap encoded in the structure")
'''))
C.append(md('''
## Hold all three in one place

Three calls = a **list of three call dicts**. Now the nesting is two levels of list-of-dicts:
a list of calls, each call a dict, each holding a list of turn dicts. The next cell parks them
together and walks the outer level.
'''))
C.append(code('''
# A list of calls - the natural home for "the whole dataset" (book 01 loads real ones this way).
cast = [call_A, call_B, call_C]            # outer list; each element is a full call_log dict

# Walk the OUTER level: one row per call, reading top-level facts + a derived turn count.
for c in cast:
    # len(c["turns"]) reaches into each call and counts its turns - nesting in action
    print(f"{c['call_id']} | {c['language']:<6} | {c['stress_profile']:<13} | "
          f"{len(c['turns'])} turns | {c['outcome']}")
'''))
C.append(md('''
## PREDICT
We want every **user** turn's text across **all three** calls. That means a loop inside a loop:
for each call, for each turn, keep it if `speaker == "user"`. Predict **how many** user turns
there are in total across A, B, C before running. (Count them by eye from the build cells.)
'''))
C.append(code('''
# Nested walk: outer loop over calls, inner loop over that call's turns. This double-loop is
# the single most common shape in the whole pipeline (analyze() in pipeline/signals.py does it).
user_lines = []
for c in cast:                              # each c is one call dict
    for turn in c["turns"]:                # each turn is one dict inside that call
        if turn["speaker"] == "user":      # keep only the caller's turns
            # record (which call, what they said) so the provenance is not lost
            user_lines.append((c["call_id"], turn["text"]))

print("total user turns across A/B/C:", len(user_lines))
for call_id, text in user_lines:
    print(" ", call_id, "->", text)
'''))
C.append(md('''
## PREDICT
We change exactly one thing: set `call_A["turns"]` to an **empty list** `[]` (a call where the
audio existed but no turns were transcribed — a real edge). Then we run a loop that computes
each call's first speaker with `c["turns"][0]["speaker"]`. Does the loop **crash**, give a
**wrong answer**, or **skip** call_A? Commit to one before running.
'''))
C.append(code('''
# BREAK-IT (guided) - this is SUPPOSED to error. An empty turns list has no [0] to index.
# EXPECTED FAILURE FOR LEARNING: indexing [0] into an empty list raises IndexError.

# Damage one field: a call with zero transcribed turns (audio dropout, ASR returned nothing).
call_A_empty = dict(call_A)            # a shallow copy so we do not corrupt the real call_A
call_A_empty["turns"] = []             # the edge case: present-but-empty list

probe = [call_A_empty, call_B, call_C]
for c in probe:
    # we blindly grab the first turn's speaker - fine for B and C, fatal for the empty one
    print(c["call_id"], "first speaker:", c["turns"][0]["speaker"])   # IndexError on call_A_empty
'''))
C.append(md('''
## Recover — guard the edge, do not pray

`IndexError: list index out of range` means you indexed past the end — here, position 0 of a
**zero-length** list. The professional fix is not "hope it never happens"; it is to **check
before you reach**: skip or handle empties explicitly. The next cell does the same walk safely.
'''))
C.append(code('''
# RECOVERY: check the list is non-empty BEFORE indexing into it. Defensive, and honest about edges.
for c in probe:
    if c["turns"]:                     # an empty list is "falsy" - this is False for [] only
        # safe now: we only reach [0] when there is at least one turn
        print(c["call_id"], "first speaker:", c["turns"][0]["speaker"])
    else:
        # the explicit alternative: name the edge instead of crashing on it
        print(c["call_id"], "has no turns - nothing to read (edge handled, not ignored)")
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
1. What exactly does `IndexError: list index out of range` tell you about your data?
2. Why is `if c["turns"]:` a safe guard — what is special about an empty list's truthiness?
3. Name one real-world reason a call could arrive with an empty `turns` list.
'''))
C.append(md('''
## YOUR TURN — author your own break

Pick ONE field in `call_B` and damage it so a later operation misbehaves. Predict in a comment
exactly what will happen (crash? which error? wrong number?), then run and compare. Examples to
consider: make `start_ms` a string, delete the `"speaker"` key, set `turns` to a dict.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it.
# my prediction: <write here exactly what will happen and why, BEFORE you damage anything>

import copy
my_call = copy.deepcopy(call_B)        # deep copy so your experiment cannot harm the real call_B

# 1) damage ONE field here (uncomment and edit one line, or write your own):
# my_call["turns"][0]["start_ms"] = "zero"      # a string where an int belongs
# del my_call["turns"][0]["speaker"]            # remove a key a loop will ask for
# my_call["turns"] = {"oops": 1}                # wrong container type entirely

# 2) then run a computation and compare reality against your written prediction:
for turn in my_call["turns"]:
    # this line assumes each turn is a dict with the right keys/types - your damage tests that
    print(turn.get("turn_id", "?"), "by", turn.get("speaker", "?"))
'''))
C.append(md('''
## WRONG-INTUITION TRAP — "the copy is a snapshot"

**The wrong belief:** "I copied the call into a new variable, so editing the copy leaves the
original alone." With nested objects this is **false** in a way that silently corrupts data.
A plain assignment (`b = a`) makes a second *name* for the **same** object, and even a shallow
`dict(a)` copies the top level but shares the inner lists/dicts. Run the next cell, then predict
what `original` looks like — BEFORE reading the reveal.
'''))
C.append(code('''
# Two "copies" that are not copies. We mutate a NESTED field through each and check the original.
original = {"call_id": "x", "turns": [{"speaker": "agent"}]}

alias = original                     # NOT a copy - just a second name for the same object
shallow = dict(original)             # copies the TOP level, but 'turns' is the SAME list inside

# mutate a deep field via each handle:
alias["turns"][0]["speaker"] = "USER-via-alias"      # reaches the one shared inner dict
shallow["turns"][0]["speaker"] = "USER-via-shallow"  # reaches that SAME shared inner dict

# both edits landed on the ORIGINAL, because the inner list/dict was never duplicated:
print("original after editing the 'copies':", original)
# every line printed, no error - and the data is corrupted. green cells, silent wrongness.
'''))
C.append(md('''
## The reveal — and the fix

Both writes mutated `original`, because `alias` *is* `original`, and `shallow`'s `turns` list is
the **same list** the original points at. No error fired — the corruption was silent, the cells
green. This is the P00 trap (green ≠ correct) wearing a new costume: **nested data**. The fix is
a **deep copy** (`copy.deepcopy`), which duplicates every layer. You already used it in your
break cell — that was not decoration; it was the antidote to exactly this trap.
'''))
C.append(code('''
# The fix, proven: copy.deepcopy duplicates EVERY nested layer, so the original is truly safe.
import copy
safe = {"call_id": "x", "turns": [{"speaker": "agent"}]}
clone = copy.deepcopy(safe)                 # a real, independent copy all the way down

clone["turns"][0]["speaker"] = "changed-on-clone-only"   # mutate deep into the clone
print("the clone:   ", clone)               # shows the change
print("the original:", safe)                # UNTOUCHED - this is what "copy" should mean
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a copy felt like a snapshot and indexing felt safe. After Act 3 you built the real cast
by hand, walked it with a double loop, met `IndexError` on the empty-turns edge and guarded it,
and saw the **shared-reference trap** corrupt an original through a fake copy — green cells, no
error, wrong data. Your defenses now: check before you index, `deepcopy` before you mutate.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the copy trap, or the empty-turns guard - your pick)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this lives in VoiceForge

## This object IS the pipeline's currency

The nested `call_log` you just built by hand is not a teaching toy — it is the **real schema**
the whole project runs on. The contract lives in `schemas/call_log.md`: a call dict with
`call_id`, `language`, `stress_profile`, and a `turns` list, each turn a dict with `turn_id`,
`speaker`, `text`, `start_ms`, `end_ms`. Eleven real calls sit in `data/normalized/*.json` in
exactly this shape, and `pipeline/signals.py` walks them with the same double loop you wrote.
'''))
C.append(md('''
## PREDICT
The next cell loads a **real** VoiceForge call from disk — `data/normalized/hero_001.json` — the
true hero call. Predict: when we parse that JSON file, what Python **type** will the top object
be? What type will `data["turns"]` be? (JSON's `{...}` and `[...]` map onto which Python types?)
'''))
C.append(code('''
# JSON is just text on disk shaped like Python dicts/lists - json.load turns it back into objects.
# We use the repo's real hero call so the shape you built by hand is shown to be the shape that ships.
import json
from pathlib import Path

# resolve the path whether the notebook runs from repo root or the notebooks/ folder
candidates = [Path.cwd() / "data" / "normalized" / "hero_001.json",
              *[p / "data" / "normalized" / "hero_001.json" for p in Path.cwd().parents]]
hero_path = next(p for p in candidates if p.exists())

data = json.loads(hero_path.read_text())   # parse the JSON text into Python objects
print("top-level type:", type(data).__name__)            # dict - same as your call_A
print("data['turns'] type:", type(data["turns"]).__name__)  # list - same as your turns list
print("number of real turns:", len(data["turns"]))       # the hero call has 12 turns
'''))
C.append(md('''
## JSON ↔ Python — the same nest, two costumes

JSON (JavaScript Object Notation) is the **on-disk / on-the-wire** spelling of exactly the
objects you built. The mapping is one-to-one: JSON object `{}` → Python `dict`, JSON array `[]`
→ Python `list`, JSON string/number/`true`/`null` → `str`/`int`-or-`float`/`bool`/`None`. So
"loading data" is just JSON text becoming the nested dict/list you already know how to walk.
'''))
C.append(code('''
# Walk the REAL hero call with the exact skills from Act 2 - no new ideas, just real data.
# We find the barge-in the way book 04 will: compare each turn's start to the previous turn's end.
turns = data["turns"]                         # the list of real turn dicts

for i in range(1, len(turns)):                # start at 1 so we can look back at i-1
    prev_end = turns[i - 1]["end_ms"]         # when the previous turn ended
    this_start = turns[i]["start_ms"]         # when this turn began
    gap = this_start - prev_end               # FTO: negative = overlap (barge-in), positive = gap
    if gap < 0:                               # an overlap is the agent talking over the caller
        print(f"barge-in at {turns[i]['turn_id']}: overlap of {abs(gap)} ms "
              f"({turns[i-1]['speaker']} -> {turns[i]['speaker']})")
'''))
C.append(md('''
## CHECKPOINT 6 (out loud)
1. JSON `{}` becomes which Python type? JSON `[]` becomes which? JSON `null`?
2. The real hero call and your hand-built `call_C` share the same **structure** — name two keys
   that appear in both at the turn level.
3. The barge-in scan found an overlap. Which two fields, subtracted, revealed it?
'''))
C.append(md('''
## The method at three levels

Three honest framings of the one idea — *a call is a nested object* — for three audiences:

- **To a beginner:** "a call is a box of in-order notes, and each note is a little form with
  labelled blanks; in Python the box is a list and the form is a dict."
- **To an engineer:** "the call_log is a dict with a `turns` array of homogeneous turn objects;
  reads are key-access for facts and index-access for sequence; persistence is JSON, which is an
  isomorphic serialization of these dict/list/scalar types."
- **To a founder:** "every call becomes one structured record with a consistent shape, so the
  same code measures timing, scores success, and exports training data across any language or
  vertical — the data model is the moat."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "Why nest it? Why not flat columns — one row per turn with a call_id?"**
<details><summary>answer</summary>You will flatten to exactly that in P02 for analysis. But the SOURCE of truth is nested because a call is naturally one unit that owns its turns; nesting keeps a call's turns together, preserves order, and lets a turn carry its own optional fields without exploding every other row. Flatten for tables; store nested.</details>

**2. "What stops a turn from being missing a field like `end_ms`?"**
<details><summary>answer</summary>Nothing at the Python level — that is why the schema (schemas/call_log.md) declares `end_ms` as `int|null`, and why I read optional fields with `.get()` not `[]`. The structure permits gaps; the discipline is to handle them, which is what book 04's null-safe timing does.</details>

**3. "JSON or Python dict — which is the real thing?"**
<details><summary>answer</summary>Same thing, two costumes. JSON is the on-disk text; the Python dict/list is the in-memory object. `json.loads` goes text→object, `json.dumps` goes object→text. The nesting and the field names are identical; only the spelling differs.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: the hand-built nest IS the shipping schema (`schemas/call_log.md`); real
calls in `data/normalized/*.json` load via `json.loads` into the same dict/list objects; walking
them is the Act-2 skill unchanged; and the same double loop powers `pipeline/signals.py`. You did
not learn a toy — you learned the pipeline's currency, and P02 will now flatten it into a table.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The four building blocks (value, list, dict, nesting) and the *job* each does in a call
2. Why a call is **naturally nested** — one call, many turns, each turn many facts
3. The two ways to reach into a structure (**by position** vs **by name**) and when to use each
4. The shared-reference trap and its fix (what `copy.deepcopy` does that `dict(x)` does not)
5. How JSON on disk relates to the Python object — and where this shape lives in the real repo

Could not hit all five? Re-open, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (the repo connection is a strong candidate)
my_clean_sentence = ""      # the sentence you'd say in a room about what a call log IS

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"A call log is a structured object: lists hold sequences, dictionaries hold facts, and
> nesting lets one call contain many turns."**

If yours captures that in your own words, this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "P01_python_objects_for_call_logs.ipynb"   # <- this notebook's filename
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

**P01 done** (pending your teach-back) → **P02 · Tables** — you will take this nested call_log
and **flatten** it into a row-and-column table (one row per turn), earning the pandas one-liners
whose by-hand versions you wrote today (the comprehension that pulled a column). Then P03 plots,
P04 debugging, then VoiceForge book 00.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "P01_python_objects_for_call_logs.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
