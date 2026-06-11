#!/usr/bin/env python3
# Builds 02_json_schemas_data_contracts.ipynb — VoiceForge University book 02.
# The ONE atomic concept: a schema is a data contract; we normalize an ugly inconsistent
# dict into the clean call_log shape. Same four-act skeleton + markers as build_P00.py.
# Rerun: .venv/bin/python notebooks/build_02.py
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
# 02 · JSON, schemas, data contracts

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Say what **JSON** is (and what it is *not*) — text on disk vs a live Python object in memory
2. Say what a **schema** is, and why "schema = a data contract" is the whole idea of this book
3. Take an **ugly, inconsistent dict** and normalize it BY HAND into the clean `call_log` shape
4. Read the `call_log` **field table** and name what each field is for
5. Defend the claim **structure is non-negotiable** — why one fixed shape lets every downstream tool work

Topic stays small on purpose: one messy call → one clean record. The *contract* is the point.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits on the ladder)

`01 · call log  →  THIS · JSON, schemas, data contracts  →  03 · pandas for calls`

Book 01 showed you a call **as a thing** — turns, speakers, timestamps. But real calls arrive
**ugly**: every vendor names fields differently, some are missing, some are the wrong type.
This book is the bridge: it turns *whatever showed up* into ONE agreed shape (`call_log`).
Book 03 then loads a folder of those clean records into a table — which only works *because*
they all share the shape this book enforces. No contract here → no table there.
'''))
C.append(md('''
## 3 — Baby intuition

A **shipping container** changed the world not by carrying more, but by being one **agreed
size**. Cranes, ships, trucks, and ports could all be built once, against that one size.
The stuff inside the container still varies wildly — the *outside* is fixed.

A schema is the container's spec sheet. The messy reality (a Telugu-English call, a clean
English booking, a half-finished Hinglish one) is the cargo. As long as each one is packed
into the same `call_log` box — same fields, same types, same names — every tool downstream
can be built once and trusted forever. That packing step has a name: **normalization**.
'''))
C.append(md('''
## 4 — The formal version

Three words this whole book turns on:

| word | plain meaning | in this book |
|---|---|---|
| **JSON** | a text format for nested data (lists, dicts, strings, numbers, `null`) | how a call is stored on disk in `data/normalized/*.json` |
| **schema** | the agreed shape: which fields exist, their types, their names | written in `schemas/call_log.md` |
| **data contract** | a *promise* — "every record will obey the schema, so you can rely on it" | what lets `signals.py`, the judge, the scorecard all assume the shape |

A schema is not a suggestion and not documentation-after-the-fact. It is a **contract**:
the producer promises to emit this shape, and every consumer is allowed to assume it.
Break the contract on one side and the other side breaks — quietly, usually at demo time.
'''))
C.append(md('''
## 5 — Why this book exists (structure is non-negotiable)

VoiceForge ingests calls from several sources (SpokenWOZ, the hero call, others). If every
downstream tool had to handle every vendor's quirks, the code would be an unmaintainable mess
of `if source == ...`. Instead there is exactly **one** rule, enforced at the boundary:

> anything that wants to flow downstream must first become a valid `call_log`.

That one rule is `pipeline/normalize.py`. After it runs, `signals.py` (timing), `judge.py`
(scoring), and the DPO export **never ask where a call came from** — they just read the shape.
This book builds the *idea* of that boundary by hand, on a toy call, before you ever open the
real file. The next cell is your first run — predict, then run.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just syntax.

# We print a sentence so you can see WHERE output appears (directly under the cell) and so
# your first action is a run you committed to. PREDICT - what exact text shows below?
print("a schema is a promise about shape")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In your own words: what is the difference between **JSON** (on disk) and a **dict** (in memory)?
2. Finish the sentence: "A schema is a ______." (one word — the word this book is built on)
3. Why does VoiceForge force every source through ONE shape instead of handling each source's quirks downstream?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: data is data; you read whatever fields are there.
After Act 1 you should hold: data crossing a boundary needs a **contract** — one agreed shape
(`call_log`) that the producer promises and every consumer relies on. The act of forcing
messy input into that shape is **normalization**, and it is why downstream code can be simple.

If that feels solid in your own words, continue. If not, re-read cell 4 (the three-word table).
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of what a "data contract" means to you now. Not mine - yours.
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
# Act 2 — Mechanics: from an ugly dict to a clean `call_log`, by hand

## What JSON actually is (text vs object)

Two things share a look but are not the same:
- a **JSON string** — characters in a file: `'{"call_id": "call_A"}'`. You cannot index into
  it like a dict; it is just text until something parses it.
- a **Python dict** — a live object in memory you can index: `d["call_id"]`.

`json.loads` turns the **s**tring into an object ("load-s"). `json.dumps` dumps an object back
to a **s**tring. We will watch both, because confusing the two is the #1 beginner JSON bug.
'''))
C.append(md('''
## PREDICT
The next cell holds a JSON **string** (note the surrounding quotes). Before running:
1. What does `type(...)` print for it — `str`, or `dict`?
2. If we try `the_text["call_id"]` on a *string*, do you expect a value or an error?
'''))
C.append(code('''
# A JSON string: this is exactly what sits in a .json file on disk - just text.
# The outer single quotes make it a Python str; the inner content is JSON.
the_text = '{"call_id": "call_A", "lang": "English"}'

# Inspection ritual: print the value, then its TYPE. The type is the lesson here.
print(the_text)            # looks structured, but...
print(type(the_text))      # ...it is a str - characters, not a dict
print(len(the_text))       # len of a str = number of characters, not number of fields
'''))
C.append(code('''
# Now parse it: json.loads = "load string" -> turns text into a real Python object.
# We import where first needed so the dependency is visible at the point of use.
import json

the_object = json.loads(the_text)   # the string becomes a dict living in kernel memory
print(the_object)                    # prints similarly...
print(type(the_object))              # ...but NOW it is a dict - the type changed
print(the_object["call_id"])         # and only now can we index into it by field name
'''))
C.append(md('''
## EXPLAIN gate
One sentence, out loud, in this shape:
> "`json.loads` took ___ and produced ___, so I can now ___ which I could not do before."
'''))
C.append(md('''
## The shape we are aiming at — the `call_log` field table

This is the contract (the real one lives in `schemas/call_log.md`). Every normalized call
obeys it. Read it as a table: each **row is one field**, each row says its **type** and **why
it exists**.

| field | type | why it exists |
|---|---|---|
| `call_id` | string | unique, stable id; keys caches and labels |
| `source` | enum | where it came from: `spokenwoz \\| hero \\| ...` |
| `language` | string | `en`, or code-switch like `te-en` — kept from day one |
| `stress_profile` | enum | scenario class: `clean \\| pause_heavy \\| interruption \\| ...` |
| `workflow_type` | string | task being attempted, e.g. `appointment_booking` |
| `turns` | array | the timed turns (one row below describes each) |
| `turns[].turn_id` | string | `t1`, `t2` — judge evidence points at these |
| `turns[].speaker` | enum | `user \\| agent` |
| `turns[].text` | string | transcript of the turn |
| `turns[].start_ms` | int | onset in ms from call start (one clock per call) |
| `turns[].end_ms` | int \\| null | offset; `null` allowed → latency-only, never fake overlap |

Hold the shape in your head. Act 2 ends by *producing* exactly this from a mess.
'''))
C.append(md('''
## Now the mess — raw input printed FIRST

Course rule: see the **ugly input** before any transformation. Real calls do not arrive as
`call_log`; they arrive as whatever some vendor felt like emitting. Below is a deliberately
nasty dict for **Call A** (our clean-English booking from the recurring cast). Read it slowly:
the fields are *wrong-named*, *wrong-typed*, *out of order*, and *missing*.
'''))
C.append(code('''
# RAW, UGLY input for call_A - printed before we touch it (raw-before-transformed).
# Every quirk here is one a real vendor dump actually does; the comments name each crime.
ugly = {
    "id": "call_A",                       # wrong NAME: schema wants 'call_id', not 'id'
    "lang": "English",                    # wrong NAME + wrong VALUE: schema wants 'language' = 'en'
    "from": "spokenwoz",                  # wrong NAME: schema wants 'source'
    "turns": [                            # right name, but the rows inside are a mess:
        {"who": "AGENT", "said": "Hi, I can book that. What date works?", "t": "0", "end": 3400},
        {"who": "caller", "said": "Tuesday at 3pm please.", "t": 4100},      # missing 'end'!
        {"said": "Booked for Tuesday 3pm. Anything else?", "who": "agent", "t": 9000, "end": 12000},
    ],
    # note what is plainly ABSENT: no stress_profile, no workflow_type, no turn ids, no end_ms on turn 2
}

# Print it raw so the mess is visible before we clean anything.
import json
print(json.dumps(ugly, indent=2))
'''))
C.append(md('''
## PREDICT
Before we normalize, eyeball the ugly dict and commit to answers (write them in the next cell):
1. How many **fields are renamed** on the top level (e.g. `id` → `call_id`)? Count them.
2. How many **turns** are there, and which turn is **missing its `end`**?
3. What top-level fields are **completely absent** that the schema requires?
'''))
C.append(code('''
# YOUR TURN - predictions BEFORE we transform. Stored so the notebook records YOUR thinking.
my_n_renamed_fields = None     # <- top-level fields that need renaming (a number)
my_turn_missing_end = None     # <- which turn index is missing 'end'? (0, 1, or 2)
my_n_absent_fields  = None     # <- required top-level fields entirely missing (a number)

# Guarded so an unfilled notebook still runs clean (course rule for learner cells).
if None in (my_n_renamed_fields, my_turn_missing_end, my_n_absent_fields):
    print("fill in all three predictions above, then re-run this cell.")
else:
    print("locked:", my_n_renamed_fields, my_turn_missing_end, my_n_absent_fields)
'''))
C.append(md('''
## Normalize BY HAND, one field at a time (manual before function)

We will NOT call a magic `normalize()` yet. First we do it by hand so the *idea* is visible.
Each step fixes exactly one class of problem, prints the result, and says why. Three problem
classes, in order: (1) **rename** fields, (2) **fix types/values**, (3) **fill what's missing**.
'''))
C.append(code('''
# STEP 1 - rename top-level fields to the schema's names. Nothing is computed yet;
# we are only re-labelling, because downstream code looks up 'call_id', never 'id'.
step1 = {}
step1["call_id"]  = ugly["id"]        # 'id'   -> 'call_id'
step1["source"]   = ugly["from"]      # 'from' -> 'source'
step1["language"] = ugly["lang"]      # 'lang' -> 'language' (value still 'English' - fixed next)

print("renamed top-level keys:", list(step1.keys()))
print("language value still raw:", step1["language"])   # flagging that VALUE is not yet schema-clean
'''))
C.append(code('''
# STEP 2 - fix VALUES/TYPES to match the contract.
# 'language' must be a BCP-47-ish code, not an English word, so 'English' -> 'en'.
# A tiny lookup table makes the mapping explicit and auditable (no guessing in code).
LANG_MAP = {"English": "en", "Hinglish": "hi-en", "Telugu-English": "te-en"}
step1["language"] = LANG_MAP[step1["language"]]   # now a code the schema accepts

print("language fixed to:", step1["language"])
print("source value:", step1["source"], "(already a valid enum, no change needed)")
'''))
C.append(code('''
# STEP 3 - the turns. Each raw turn has wrong keys ('who'/'said'/'t'), inconsistent casing
# ('AGENT', 'caller'), string timestamps ('0'), missing turn_ids, and one missing 'end'.
# We rebuild each turn into the schema shape, fixing one thing at a time. WHY each line:

SPEAKER_MAP = {"agent": "agent", "caller": "user", "user": "user"}  # normalize speaker vocab

clean_turns = []
for i, raw in enumerate(ugly["turns"]):
    speaker = SPEAKER_MAP[raw["who"].lower()]          # lower() first so 'AGENT' == 'agent'; map 'caller'->'user'
    start_ms = int(raw["t"])                            # timestamps must be int ms, not the string "0"
    end_ms = int(raw["end"]) if "end" in raw else None  # missing end -> null (schema allows it; never fake a number)
    clean_turns.append({
        "turn_id": f"t{i + 1}",                        # generate stable ids the judge can cite (t1, t2, ...)
        "speaker": speaker,
        "text": raw["said"],                           # 'said' -> 'text'
        "start_ms": start_ms,
        "end_ms": end_ms,
    })

for t in clean_turns:        # print one row per turn so each is visibly one repaired THING
    print(t)
'''))
C.append(md('''
## PREDICT
Turn 2 (the caller's "Tuesday at 3pm please.") had **no `end`** in the raw data.
After our STEP-3 repair, what is that turn's `end_ms` — a guessed number, or `None`?
And which is the *honest* choice for a missing offset? Commit before scrolling.
'''))
C.append(code('''
# Confirm the honest-missing-value choice on turn 2 (index 1).
turn2 = clean_turns[1]
# We assert our intent so a future edit that "helpfully" invents a number trips this guard.
# A null end means 'we genuinely don't know the offset' - downstream treats it latency-only.
assert turn2["end_ms"] is None, "a missing end must stay None, never a fabricated number"
print("turn 2 end_ms:", turn2["end_ms"], "- honest null, not a guess")
'''))
C.append(code('''
# STEP 4 - fill the REQUIRED top-level fields that were entirely absent.
# We cannot invent semantic truth, so we use explicit, honest placeholders the schema permits,
# and we record HOW we set them. (Real normalize.py derives stress_profile from timing; here
# we mark it 'clean' for call_A because nothing in the turns indicates overlap or long pauses.)
step1["stress_profile"] = "clean"                 # call_A is the cooperative, low-stress booking
step1["workflow_type"]  = "appointment_booking"   # the task the call is attempting
step1["turns"]          = clean_turns             # attach the repaired turns
step1["audio_path"]     = None                    # no audio for this toy record (null is valid)
step1["metadata"]       = {"constructed": True}   # provenance: this record was hand-built

print("now present:", sorted(step1.keys()))
'''))
C.append(md('''
## OBSERVE + EXPLAIN

You just did the three moves of every normalization, in order: **rename → fix types/values →
fill missing**. Notice what you did NOT do: you never invented a `start_ms`, never faked the
missing `end_ms`. The contract lets you say "unknown" (`null`); it does not let you lie.

The result `step1` is now a candidate `call_log`. Next we *validate* it against the contract —
because a shape that merely *looks* right and one that *passes the checks* are not the same.
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
Name the **three classes of repair** a normalizer does, in order. For each, give one concrete
example from the ugly dict you just cleaned (e.g. rename: `who` → `speaker`).
'''))
C.append(md('''
## Validate against the contract (the function version, finally)

A contract is only real if something **enforces** it. The real `pipeline/normalize.py` has a
`validate_call()` that asserts the shape before any record is allowed downstream. We write a
tiny version of the same idea here — manual-before-function paid off, so now the function is a
*checker of work you already understand*, not a black box.
'''))
C.append(code('''
# A minimal validator - the same SHAPE of checks as validate_call() in pipeline/normalize.py.
# WHY assertions: they fail LOUDLY at the boundary, so bad data never reaches downstream code
# and turns into a silent wrong number later.
def validate_call(call):
    for field in ("call_id", "source", "language", "stress_profile", "workflow_type", "turns"):
        assert field in call, f"missing required field: {field}"   # contract = all required fields present
    assert call["turns"], "a call must have at least one turn"
    last_start = -1
    for t in call["turns"]:
        assert t["speaker"] in ("user", "agent"), f"bad speaker: {t['speaker']}"  # closed enum
        assert isinstance(t["start_ms"], int), f"start_ms must be int: {t['turn_id']}"  # one ms clock, ints only
        assert t["start_ms"] >= last_start, f"turns must be sorted by start_ms: {t['turn_id']}"  # chronological
        assert t["end_ms"] is None or t["end_ms"] > t["start_ms"], f"end<=start: {t['turn_id']}"  # null ok, inversion not
        last_start = t["start_ms"]
    return call

# Run it on our hand-normalized record. If it returns, the record honors the contract.
validate_call(step1)
print("VALID call_log:", step1["call_id"], "with", len(step1["turns"]), "turns")
'''))
C.append(md('''
## See it as JSON on disk (object → text, the round trip)

The clean record lives in memory as a dict. To *store* it (as `data/normalized/*.json` does),
we dump it back to a JSON string. This is the reverse of the `json.loads` you ran earlier —
the same call, packed and unpacked, is the entire idea of a `.json` file.
'''))
C.append(code('''
# json.dumps = object -> string (the inverse of loads). indent=2 just makes it readable.
# This string is byte-for-byte what would be written to data/normalized/call_A.json.
as_text = json.dumps(step1, indent=2)
print(as_text[:300], "...")            # first 300 chars is enough to see the shape on disk
print("type on disk:", type(as_text))  # a str again - the round trip dict->str->dict closes here
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. Which function turns a JSON string into a dict, and which does the reverse?
2. Why is a loud `assert` in `validate_call` *better* than letting a malformed record through?
3. Our turn 2 has `end_ms = None`. Why is that allowed — and why is faking a number forbidden?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: "JSON" and "dict" were the same blur, and cleaning data felt like vague tidying.
After Act 2 you can: tell text from object (`loads`/`dumps`), read the `call_log` field table,
and **normalize a real mess by hand** in three ordered moves (rename → fix types → fill
missing) — then **validate** it against the contract, the same way `pipeline/normalize.py` does.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (loads/dumps, the 3 repair moves, or validation - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the contract on purpose, and the trap underneath it

## Break-it philosophy

A contract you never test is a contract you do not understand. So we now feed `validate_call`
records that **violate** the shape, on purpose, and watch it refuse. Each break teaches one
edge of the contract. Surprise here, at your desk, is education; surprise at the demo is not.
'''))
C.append(md('''
## PREDICT
We hand `validate_call` a record whose `turns` list is **empty** (`[]`). Before running:
does the validator **crash loudly** (good — it caught a bad record), or **pass it through
silently** (bad — garbage now flows downstream)? Commit to one.
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. Read the failure; do not fix it yet.
# A call with zero turns is meaningless (nothing happened), so the contract must reject it.
empty_call = {
    "call_id": "call_broken",
    "source": "spokenwoz",
    "language": "en",
    "stress_profile": "clean",
    "workflow_type": "appointment_booking",
    "turns": [],                 # <- the violation: a call with no turns
}

# We expect this to raise AssertionError on the "must have at least one turn" check.
validate_call(empty_call)
print("this line should NOT print - the validator should have stopped us")
'''))
C.append(md('''
## Reading the failure (and why a loud failure is the friendly one)

The red wall is a **traceback**. Read the **last line first**: it names what broke
(`AssertionError: a call must have at least one turn`). The validator did its job — it stopped
a meaningless record *at the boundary*, where the cost is one error message.

Picture the alternative: no validator. The empty call flows downstream, the timing tool divides
by zero turns, the judge scores "nothing", and you discover it on stage. **A contract that
fails loudly at the door is cheaper than one that fails silently in production.**
'''))
C.append(md('''
## PREDICT
Now a sneakier break: a turn whose `start_ms` is the **string** `"4100"` instead of the int
`4100`. The data *looks* fine when printed. Does `validate_call` catch it, and on which check?
'''))
C.append(code('''
# BREAK-IT (guided) - SUPPOSED to error again, on a TYPE this time, not a missing field.
# This is the dangerous kind of bad data: it prints identically to good data.
typed_wrong = {
    "call_id": "call_typed",
    "source": "spokenwoz",
    "language": "en",
    "stress_profile": "clean",
    "workflow_type": "appointment_booking",
    "turns": [
        {"turn_id": "t1", "speaker": "user", "text": "hello", "start_ms": "4100", "end_ms": 9000},
    ],                            # start_ms is a str "4100" - looks right, is not
}

# The isinstance(..., int) check exists precisely to catch this. Without it, "4100" would sort
# and compare like text and corrupt every timing metric downstream with no error at all.
validate_call(typed_wrong)
print("this line should NOT print either")
'''))
C.append(md('''
## The fix, and the debug ritual

The repair is one line: coerce the value to the right type (`int("4100")`), exactly the STEP-2
move from Act 2. The debug ritual that found it generalizes:
1. **Print the input** — the raw record, before any transform
2. **Print the intermediate** — the field and its `type(...)`
3. **Shrink the example** — one turn, one field, until the bug has nowhere to hide
'''))
C.append(code('''
# Recovery cell - fix the type and re-validate, proving the contract now holds.
typed_wrong["turns"][0]["start_ms"] = int(typed_wrong["turns"][0]["start_ms"])  # "4100" -> 4100
validate_call(typed_wrong)   # returns cleanly now -> the record honors the contract
print("fixed start_ms type:", type(typed_wrong["turns"][0]["start_ms"]).__name__, "- now valid")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
Recite the three-step debug ritual. Which check caught the `"4100"` string bug — and why is a
wrong **type** that prints fine MORE dangerous than a missing field that crashes immediately?
'''))
C.append(md('''
## YOUR break now

Author your own contract violation. Pick ONE rule from `validate_call` (a missing required
field, a bad speaker like `"robot"`, turns out of `start_ms` order, an `end_ms` <= `start_ms`),
predict exactly which assertion will fire, write the prediction as a comment, then run it.
The cell is marked as an expected failure so the notebook still runs clean.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it. EXPECTED FAILURE FOR LEARNING (this cell may raise).
# my prediction: <write which assertion fires and why, BEFORE running>

my_broken_call = {
    "call_id": "call_mine",
    "source": "spokenwoz",
    "language": "en",
    "stress_profile": "clean",
    "workflow_type": "appointment_booking",
    "turns": [
        {"turn_id": "t1", "speaker": "user", "text": "hi", "start_ms": 0, "end_ms": 1000},
    ],
}

# 1) break ONE rule here (uncomment one, or write your own). Each line violates a different check:
# my_broken_call["turns"][0]["speaker"] = "robot"          # not in (user, agent)
# del my_broken_call["workflow_type"]                       # missing required field
# my_broken_call["turns"][0]["end_ms"] = -5                 # end <= start

# 2) run the contract against your damage and compare reality to your written prediction:
validate_call(my_broken_call)
print("validated (so you did NOT actually break a rule - try uncommenting one above)")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this book is built on

**The wrong belief:** "the JSON parsed without error, so the data is good."

`json.loads` only checks that the text is *well-formed JSON* — brackets matched, commas right.
It says **nothing** about whether the fields are the ones you need, named correctly, typed
correctly, or present at all. A perfectly valid JSON document can be a totally invalid `call_log`.

The next cell parses cleanly — zero errors — and is still useless to every downstream tool.
Run it, then explain *why* it is bad BEFORE reading the reveal.
'''))
C.append(code('''
# This is VALID JSON. json.loads will not complain at all.
sneaky_text = '{"id": "x", "messages": [{"role": "bot", "content": "hi"}]}'

parsed = json.loads(sneaky_text)   # succeeds - the TEXT is well-formed JSON
print("json.loads succeeded:", parsed)        # no error, clean parse
print("but is it a call_log? fields present:", sorted(parsed.keys()))

# Try to use it as a call_log and watch the SHAPE fail, even though the PARSE passed:
try:
    validate_call(parsed)                       # the contract, not the parser, is the real gate
    print("validated (unexpected)")
except (AssertionError, KeyError) as e:
    print("contract REJECTED it ->", type(e).__name__, "-", e)
'''))
C.append(md('''
## The reveal

`json.loads` answered a small question — "is this legal JSON text?" — and said yes. But the
question that matters is "is this a valid `call_log`?", and the answer is no: it has `id` not
`call_id`, `messages` not `turns`, `role: "bot"` not `speaker: "agent"`, no timestamps at all.

**Parsing is not validating.** A green parse proves the *text* is well-formed; it proves
nothing about the *contract*. This is the JSON twin of the course-wide trap "it ran, so it's
right." Out in VoiceForge it bites exactly here: a vendor sends syntactically perfect JSON in
*their* shape, your code parses it happily, and the wrongness only surfaces three tools later.
The cure is a **validator at the boundary** — which is why `pipeline/normalize.py` has one.
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: what does a clean json.loads prove, and what does it NOT prove?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a successful parse felt like success. After Act 3: you break a contract on purpose and
watch it refuse, you know a wrong **type** that prints fine is scarier than a loud missing
field, and you hold the trap — **parsing checks text, validating checks the contract**, and only
the second one keeps garbage out of the pipeline.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the parse-vs-validate trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the real boundary, the cast, and the bar you must clear

## Where this lives in the real pipeline

The toy you just built by hand is, in miniature, the real boundary of VoiceForge:

- `schemas/call_log.md` — the **written contract** (the field table you read is a trimmed copy).
- `pipeline/normalize.py` — the **enforcer**. Its `validate_call()` runs the same shape of
  assertions you wrote; its `spokenwoz_call()` does the rename/fix/fill you did by hand, for
  real SpokenWOZ dumps. After it runs, results land in `data/normalized/*.json`.
- Everything downstream — `pipeline/signals.py` (timing), `pipeline/judge.py` (scoring), the
  DPO export — reads `call_log` and **never asks what vendor a call came from**.

That last sentence is the entire payoff of a data contract: write the messy-handling **once**,
at the boundary, and every tool after it gets to be simple and trusting.
'''))
C.append(md('''
## Touch the real thing — load an actual normalized call

You hand-built a `call_log`. Now load one that `pipeline/normalize.py` already produced from a
real SpokenWOZ dialogue, and confirm it obeys the very same contract your validator checks.
(toy-before-real, completed: the real file is just your toy at scale.)
'''))
C.append(code('''
# Load a real normalized record from disk. We resolve the repo root by walking up to the
# folder that has data/normalized, so this runs no matter the working directory.
from pathlib import Path
root = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "normalized").exists())
real_path = root / "data" / "normalized" / "swz_MUL0035.json"

real_call = json.loads(real_path.read_text())   # disk text -> dict, the loads you now know cold
print("loaded:", real_call["call_id"], "| source:", real_call["source"],
      "| profile:", real_call["stress_profile"], "| turns:", len(real_call["turns"]))
'''))
C.append(md('''
## PREDICT
You are about to run YOUR `validate_call` on this **real** file (not the toy).
Do you expect it to pass or fail? (It was written by the real normalizer to obey the same
contract — so what does that imply?) Commit before running.
'''))
C.append(code('''
# YOUR TURN - run your own validator against the real record and confirm the contract holds.
# This is the proof that "one schema in, every tool works": the SAME check passes on toy and real.
result = validate_call(real_call)   # if this returns, the real file honors the contract
print("real record VALID:", result["call_id"], "- same contract, toy and production")

# Bonus inspection: show one real turn so the field table feels concrete on real data.
print("first turn:", real_call["turns"][0])
'''))
C.append(md('''
## The recurring cast, in their schema form

The three calls that travel through this whole course each become one `call_log` record. Same
shape, wildly different cargo — exactly the shipping-container point from Act 1.
'''))
C.append(code('''
# The cast as schema-level summaries. Each is ONE call_log; only the cargo differs.
# (ids/languages/outcomes match the course-wide cast - the consistency the pipeline relies on.)
cast = [
    {"call_id": "call_A", "language": "en",    "stress_profile": "clean",        "outcome": "success"},
    {"call_id": "call_B", "language": "hi-en", "stress_profile": "pause_heavy",  "outcome": "partial"},
    {"call_id": "call_C", "language": "te-en", "stress_profile": "interruption", "outcome": "failure"},
]
# One print per call so each is visibly one record obeying the same field names.
for c in cast:
    print(f"{c['call_id']} | {c['language']:<6} | {c['stress_profile']:<13} | outcome={c['outcome']}")
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

Call C is the Telugu-English call where the agent interrupts the caller. Its **transcript text**
might look like a normal booking. Which **schema field** would you most need to catch what
actually went wrong — the `text`, or the `start_ms`/`end_ms` timing? There is no grade today;
book 04 confronts your stored guess with real numbers.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for book 04 to confront.
my_field_for_failure = ""   # which field exposes Call C's interruption, and WHY text alone misses it

if len(my_field_for_failure.strip()) < 20:
    print("write your prediction above (which field + why), then re-run.")
else:
    print("PREDICTION STORED:", my_field_for_failure)
'''))
C.append(md('''
## CHECKPOINT 5 (out loud — the synthesis gate)
1. Your toy validator passed on `swz_MUL0035.json` **unchanged**. What does that prove about
   the relationship between your by-hand `call_log` and the real `pipeline/normalize.py` output?
2. The three cast calls (`call_A`/`call_B`/`call_C`) differ wildly in language and stress, yet
   share one shape. Restate the shipping-container idea using these three.
3. Finish the book's sentence and defend it in one breath: "One schema in, ______."
'''))
C.append(md('''
## Where contracts fail in the real world (honesty applies here too)

- **Silent schema drift** — a vendor renames `start_ms` to `startTime` next month. Your parser
  still succeeds; your validator catches it only if the field is actually required and checked.
- **Over-trusting nulls** — `end_ms: null` is honest, but if half a dataset is null, your timing
  metrics quietly thin out. The contract permits null; it cannot make missing data exist.
- **Enum creep** — someone adds `speaker: "system"`. The closed enum rejects it (good) — but only
  if you remembered to make it closed. An open string field would have let it slip.
- **Validating too late** — checking shape *after* three transforms means the traceback points at
  the wrong place. The fix is to validate **at the boundary**, before anything trusts the record.
'''))
C.append(md('''
## The concept at three levels (every book ends with this)

- **To a beginner:** "messy data comes in, we force it into one tidy form everyone agreed on —
  like making every parcel fit the same box before it goes on the truck."
- **To an engineer:** "a `call_log` schema with required fields, closed enums, and typed
  timestamps, enforced by a boundary validator (`pipeline/normalize.py`); downstream code is
  source-agnostic because the contract holds invariants it can assume."
- **To a founder:** "we normalize every call into one contract on day one, so adding a new call
  vendor is a one-file adapter, not a rewrite — the product scales across sources cheaply."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "Why not just let each downstream tool read whatever fields a vendor sends?"**
<details><summary>answer</summary>Because then every tool must know every vendor, and N tools × M vendors quirks multiply. One boundary normalizer collapses that to N + M: write each adapter once, every tool stays source-agnostic.</details>

**2. "A vendor's JSON parsed fine with no errors — isn't that enough to trust it?"**
<details><summary>answer</summary>No. Parsing only proves the text is well-formed JSON. It says nothing about whether the fields, names, types, and required values match the call_log contract. Validation is a separate, stricter gate — that is the Act-3 trap.</details>

**3. "Why allow `end_ms: null` at all — isn't a missing value just bad data?"**
<details><summary>answer</summary>A null end is the honest representation of an unknown offset; downstream treats those turns as latency-only and never fabricates overlap. Forbidding null would push people to invent numbers, which is worse — silent wrongness instead of an explicit unknown.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now hold: where the contract lives in the real repo (`schemas/call_log.md` +
`pipeline/normalize.py`), that your toy validator passes on a **real** normalized file unchanged,
who the three cast calls are as `call_log` records, and the three-level pitch for why one shape
makes the whole system simple — and what makes contracts fail in practice.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. JSON vs dict — which function goes each way (`loads` / `dumps`)
2. "A schema is a ______" — and what a **data contract** promises
3. The three repair moves of normalization, in order (rename → fix types → fill missing)
4. The trap: what a clean `json.loads` proves and what it does NOT
5. One real place in VoiceForge this lives, and why downstream code is source-agnostic

Could not hit all five? Reopen, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (the real boundary / source-agnostic downstream)
my_clean_sentence = ""      # the sentence you'd say in a room about schemas as contracts

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"One schema in, every tool downstream works."**

If yours captures that in your own words — messy reality forced into one agreed shape so the
rest of the system can be simple and trusting — this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "02_json_schemas_data_contracts.ipynb"   # this notebook's filename
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

**02 done** (pending your teach-back) → **03 · pandas for calls** — now that every call obeys
one shape, you load a *folder* of them into a single table and ask questions across all of them
at once. That table only works because of the contract you enforced here.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "02_json_schemas_data_contracts.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
