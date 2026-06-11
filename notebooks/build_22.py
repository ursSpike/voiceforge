#!/usr/bin/env python3
# Builds 22_user_simulators.ipynb — VoiceForge University book 22.
# ONE atomic concept: synthetic caller personas. Simulation buys COVERAGE, never VALIDITY.
# Rerun: .venv/bin/python notebooks/build_22.py
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
# 22 · User simulators

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Write a **caller persona** as data — a small script that says how one *kind* of caller behaves
   (cooperative, hesitant, angry, code-switching) — and run it to **generate a synthetic call
   object** in the exact `schemas/call_log.md` shape the rest of the pipeline already reads.
2. State the load-bearing distinction of this book: **a simulated call is not a real log.** A
   persona is a *hypothesis about a caller*, authored by you; a real log is *evidence* of a caller
   that happened. They are different epistemic objects even when they share a schema.
3. Say precisely **what simulation buys** (coverage: the angry caller, the 2am caller, the
   code-switcher you have no real recording of — on demand, for free, in seconds) and **what it
   cannot buy** (validity: proof the agent works on *real* callers, who surprise you in ways your
   personas never will).
4. Catch the **trap** that ends careers-in-miniature on a demo stage: scoring great on your own
   simulator and calling the agent *validated*. You wrote the test and the answer key; passing it
   proves your personas are satisfiable, not that the world is.

Topic looks playful (toy personas, made-up callers). The discipline is not: knowing exactly which
question your data can and cannot answer is the difference between an honest eval and a flattering one.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits on the ladder)

`21 · rubric.yaml (what "good" means, in one editable file)  →  THIS · user simulators  →  23 · dataset hierarchy`

Why this book exists, right here on the ladder. Book 21 gave you the **rubric**: a single editable
file that defines what "good" means, so every scorecard and the dashboard update when you change it.
But a rubric is a *measuring stick* — it needs **calls to measure**. Where do calls come from when
you have a handful of real ones and need to probe a hundred situations? You **simulate** them. This
book builds that generator: personas in, synthetic call objects out, ready for the book-21 rubric to
score. Then book 23 (dataset hierarchy) places simulation in its proper rank among **all** your data
sources — hero call (theater), public data (validity), **synthetic (coverage)**, provider logs
(production) — and the one-line verdict you will earn here is exactly the job synthetic data holds
there: it buys **coverage**, and another source must buy **validity**.

No lesson floats in the void: previous = "what good means lives in one file", current = "where calls
come from when you need many, and what that source can prove", next = "every data source has a job".
'''))
C.append(md('''
## 3 — Baby intuition

You are building a flight simulator for pilots. In the simulator you can summon an engine fire, a
crosswind, a bird strike, a stuck landing gear — any emergency, any time, repeated until the pilot
handles it cold. That is *priceless*: you would never wait for a real engine fire to train for one.

Now the honest part. A pilot who aces every scenario you *programmed* has proven they can handle the
emergencies **you thought of**. The simulator cannot certify them for the failure mode you never
imagined — the one real sky has and your code does not. The simulator buys **practice across the
situations you can author** (coverage). It does **not** buy **proof they will fly the real plane**
(validity); only real flight hours, or a regulator's real test, buys that.

A user simulator is that flight simulator for a voice agent. Personas are the scenarios you can
summon — the angry caller, the mumbling caller, the Telugu-English caller — on demand, for free. And
the same honest limit holds: passing your simulator proves your agent handles the callers *you
imagined*, never the ones you didn't. Hold that pilot image; the whole book is inside it.
'''))
C.append(md('''
## 4 — The formal version

Three terms we will use precisely all book:

- **persona** — a small specification of how one *kind* of caller behaves: their goal, their
  language, and the *behavioral traits* that make them hard (hesitates, interrupts, gives partial
  info, switches language). It is a script, authored by a human, encoding a *hypothesis* about a
  caller. Ours live as plain Python dicts.
- **user simulator** — the function that *runs* a persona against an agent (or, here, a scripted
  agent) and **emits a call object** in the `schemas/call_log.md` shape: `call_id`, `language`,
  `stress_profile`, `turns[]` with `speaker`/`text`/`start_ms`/`end_ms`. Same schema as a real call —
  that sameness is the convenience *and* the danger.
- **validity vs coverage** — **coverage** = the *range of situations* your data exercises (how many
  kinds of caller, how many failure modes). **validity** = whether your measurement reflects *real
  performance on real callers*. Simulation moves coverage almost without limit and validity not at all.

The claim, stated flat: **a synthetic call shares the schema of a real call but not its standing as
evidence.** You can score it, chart it, tag it — every downstream tool accepts it — and none of that
makes it *true about the world*, because you authored both the caller and (implicitly) the difficulty.
Simulation buys coverage; validity has to come from somewhere else (book 23 names where).
'''))
C.append(md('''
## 5 — Why this is the seductive shortcut (the thing we are fighting)

Real call logs are scarce, slow, and legally fussy. You have one hero call and a handful of public
ones. Getting a hundred angry-caller recordings means real angry callers, consent, storage, PII.

A simulator makes that scarcity vanish: want fifty hesitant Hinglish callers who never confirm the
time? A loop and a persona. Want an angry caller at 2am? One dict. It is *so* cheap and *so* fast that
the temptation is to let it quietly become your whole evaluation — to run the agent against your
simulator, watch the score climb, and report "validated."

That report is false, and the falseness is invisible because nothing errors. The repo says so out
loud: `docs/limitations.md` writes that the constructed hero call "is a demonstration of what
VoiceForge detects, **not evidence drawn from production traffic**", and that "**validity comes from
the public-data calibration**, not from this call." A simulator is the same kind of object, scaled up.
This book builds the generator *and* the reflex to never confuse the practice plane with the real sky.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In one sentence each: what is a **persona**, and what is a **user simulator**?
2. Define **coverage** and **validity** so the difference is sharp. Which one does simulation buy
   cheaply, and which can it *never* buy — no matter how many synthetic calls you generate?
3. This book sits between "the rubric (what good means)" and "the dataset hierarchy". Why does a
   simulator only make sense *after* you have a rubric, and what job will it be assigned *next*?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: more data is more data — if a simulated call has the right
schema, it counts like any other call. After Act 1 you should hold a sharper picture: a synthetic
call and a real log can be **byte-identical in shape and worlds apart in standing**. Simulation is a
*coverage engine* — it manufactures the situations you can imagine, on demand — and coverage is not
validity. A persona is a hypothesis you wrote; a real log is evidence that happened.

If "passing my own simulator proves my personas are satisfiable, not that the world is" feels like
your own sentence, continue. If a synthetic call still feels like "just more data", re-read cell 4 —
that missing distinction is the exact thing Act 3 will break in your hands.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of "simulation buys coverage, never validity". Not mine - yours.
# Producing the sentence is the learning; reading mine would only feel like learning.
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
# Act 2 — Mechanics: a persona by hand, then a simulator that emits a real-shaped call

## Start with one persona, as plain data

Before any generator, we write **one** persona the slow visible way — as a dict you can read top to
bottom. A persona has a *goal* (what the caller wants), a *language*, and a list of *behavioral
traits* that make them easy or hard. Raw first: we print the dict before doing anything with it, so
the persona is a THING you can see, not magic hidden in a function.
'''))
C.append(code('''
# Persona #1 - the COOPERATIVE caller, written as a plain dict so every field is visible.
# We separate GOAL (what they want) from TRAITS (how they behave) on purpose: the goal is the task,
# the traits are the difficulty knobs. A cooperative caller's traits are all "easy" - that is the point.
cooperative = {
    "persona_id": "p_cooperative",
    "goal": "book an appointment",            # the task the caller is trying to accomplish
    "language": "English",                    # the language condition (a real eval dimension, book 09)
    "traits": {                               # the behavioral knobs that decide how hard this caller is
        "gives_full_info": True,              # answers completely the first time asked
        "hesitates": False,                   # no "umm... ek minute" stalling
        "interrupts": False,                  # waits for the agent to finish (no barge-in)
        "angry": False,                       # calm, polite
        "code_switches": False,               # stays in one language
    },
    "utterances": [                           # the lines this caller will actually say, in order
        "Hi, I'd like to book a table for four, tomorrow at 7pm.",
        "Yes, that's correct. Thank you!",
    ],
}
# Print the raw persona so it is a readable object before any simulator touches it (course rule).
import json
print(json.dumps(cooperative, indent=2))
'''))
C.append(md('''
## PREDICT
The persona above has `gives_full_info: True` and every hard trait set to `False`. When we run it
through a simulator that interleaves caller lines with a scripted agent, predict: roughly **how many
turns** will the resulting call have, and what will its **outcome** be (success / partial / failure)?
Commit in the next cell before any code runs.
'''))
C.append(code('''
# YOUR TURN - PREDICT here, BEFORE the simulator cell runs. We store the guess as variables so the
# notebook becomes a record of YOUR thinking, and a later cell can confront it against reality.
my_coop_turns = None      # <- a whole number: how many turns total (agent + user)?
my_coop_outcome = None    # <- "success" / "partial" / "failure"

if my_coop_turns is None or my_coop_outcome is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("locked - turns:", my_coop_turns, "| outcome:", my_coop_outcome)
'''))
C.append(md('''
## Build the simulator BY HAND first — one call, every turn assembled in the open

A "user simulator" sounds grand; mechanically it is a loop that **alternates** an agent line and a
persona line, stamping each with a start/end time, until the conversation ends. We do the very first
call **by hand** — no function yet — so you watch a call object get built turn by turn. The agent here
is a fixed script (book 20's "same turns" idea); the *caller* is what the persona drives.
'''))
C.append(code('''
# A tiny SCRIPTED agent: a fixed list of lines it will say, in order. We script the agent (rather than
# call a real LLM) so the ONLY thing varying between simulated calls is the PERSONA - change-one-thing
# from P00. A real simulator would put a live agent here; the call-assembly logic is identical.
agent_script = [
    "Hi! I can book your table. What would you like?",   # agent speaks first (turn 1)
    "Booked: table for four, tomorrow 7pm. Anything else?",
]

# Assemble ONE call by hand. We weave agent[0], user[0], agent[1], user[1], ... and stamp times.
# Timing matters because every downstream signal (FTO, barge-in, latency) reads start_ms/end_ms -
# a call with no clock is unscoreable, so the simulator MUST produce a clock, even a synthetic one.
turns = []
clock_ms = 0                                  # a single running clock for the whole call (one clock per call)
GAP_MS = 500                                  # a flat 500ms gap between turns - a SYNTHETIC, made-up timing
DUR_MS = 2500                                 # a flat 2.5s duration per turn - also synthetic (remember this!)

# zip pairs each agent line with the caller line that answers it; we walk them in order.
for i, (agent_line, user_line) in enumerate(zip(agent_script, cooperative["utterances"]), start=1):
    # agent turn first
    turns.append({"turn_id": f"t{2*i-1}", "speaker": "agent", "text": agent_line,
                  "start_ms": clock_ms, "end_ms": clock_ms + DUR_MS})
    clock_ms += DUR_MS + GAP_MS               # advance the clock past the agent turn + a gap
    # then the caller turn
    turns.append({"turn_id": f"t{2*i}", "speaker": "user", "text": user_line,
                  "start_ms": clock_ms, "end_ms": clock_ms + DUR_MS})
    clock_ms += DUR_MS + GAP_MS

for t in turns:
    print(f'{t["turn_id"]:>3} {t["speaker"]:<6} [{t["start_ms"]:>5}-{t["end_ms"]:>5}]  {t["text"]}')
'''))
C.append(code('''
# Wrap those turns into a full call object in the EXACT schemas/call_log.md shape. This sameness is
# deliberate: the synthetic call must be a drop-in for a real one so book-21's rubric can score it
# unchanged. We set source="synthetic" and metadata.constructed=True so the call CONFESSES its origin -
# an honest synthetic call never pretends to be a real log (that honesty is the whole ethic of book 23).
coop_call = {
    "call_id": "sim_cooperative_001",
    "source": "synthetic",                    # NOT 'hero'/'spokenwoz' - this call announces it is generated
    "language": cooperative["language"],
    "stress_profile": "clean",                # cooperative caller -> the 'clean' stress class (schema enum)
    "workflow_type": "appointment_booking",
    "turns": turns,
    "audio_path": None,                       # there is no recording - it was never spoken aloud
    "metadata": {"constructed": True, "persona_id": cooperative["persona_id"],
                 "timestamps_from": "synthetic_flat_clock"},  # receipts: how the (fake) timing was made
}
print("call_id:", coop_call["call_id"], "| source:", coop_call["source"], "| profile:", coop_call["stress_profile"])
print("turns:", len(coop_call["turns"]), "| language:", coop_call["language"])
print("metadata:", coop_call["metadata"])
'''))
C.append(md('''
## OBSERVE + EXPLAIN

Look at what you built: a call object indistinguishable *in shape* from `data/hero/turns.json` — same
keys, same turn structure, same single clock — except `source` is `"synthetic"` and `metadata` admits
`constructed: True`. That `source` field is the only thing standing between an honest synthetic call
and a forged log. One sentence, out loud: why did we make the synthetic call carry a **flag** that
says it is synthetic, instead of making it look as real as possible?
'''))
C.append(code('''
# Confront YOUR prediction with the assembled call. The comparison is the lesson, not the verdict.
actual_turns = len(coop_call["turns"])
# a cooperative caller who gives full info and confirms -> the agent completes the booking -> success.
actual_outcome = "success"
print("actual turns:", actual_turns, "| actual outcome:", actual_outcome)

if my_coop_turns is not None:
    hit = (my_coop_turns == actual_turns and my_coop_outcome == actual_outcome)
    print("your prediction", "MATCHED" if hit else "DIFFERED",
          "- if it differed, that gap is exactly what to think about")
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
1. A persona separates `goal` from `traits`. Why split them — what does each part control?
2. The synthetic call has `source: "synthetic"` and `metadata.constructed: True`. What would be
   *dishonest* about a generated call that set `source: "hero"` instead?
3. The timestamps came from a flat 500ms/2500ms clock we made up. Name one **signal** from earlier
   books (hint: barge-in, latency) that this synthetic clock will get *wrong on purpose* — because we
   chose the numbers, not a microphone.
'''))
C.append(md('''
## Now — and only now — the simulator as a FUNCTION

You assembled one call by hand and saw every turn and timestamp appear. A simulator is just those
steps written once so they run on *any* persona. Because you met the assembly first, this function is
a convenience, not a mystery — and you can audit every line. It takes a persona and an agent script
and returns the same call-shaped object you built above.
'''))
C.append(code('''
# The simulator, collected into one function. Every line is the by-hand assembly above, generalized.
# We pass the agent script IN (rather than hardcode it) so the same simulator can drive any scenario;
# the persona supplies the caller. Note the synthetic-clock arguments are explicit - we are never
# pretending these timings are measured; they are parameters we chose, and a caller can see them.
def simulate_call(persona, agent_script, call_id, stress_profile,
                  gap_ms=500, dur_ms=2500, workflow_type="appointment_booking"):
    turns = []
    clock = 0                                  # one running clock for the whole call (single clock per call)
    for i, (agent_line, user_line) in enumerate(zip(agent_script, persona["utterances"]), start=1):
        # agent turn, then caller turn - the alternating structure of a two-party call
        turns.append({"turn_id": f"t{2*i-1}", "speaker": "agent", "text": agent_line,
                      "start_ms": clock, "end_ms": clock + dur_ms})
        clock += dur_ms + gap_ms
        turns.append({"turn_id": f"t{2*i}", "speaker": "user", "text": user_line,
                      "start_ms": clock, "end_ms": clock + dur_ms})
        clock += dur_ms + gap_ms
    return {
        "call_id": call_id,
        "source": "synthetic",                 # hardcoded: this function can ONLY make synthetic calls
        "language": persona["language"],
        "stress_profile": stress_profile,
        "workflow_type": workflow_type,
        "turns": turns,
        "audio_path": None,                    # synthetic calls were never spoken -> no audio
        "metadata": {"constructed": True, "persona_id": persona["persona_id"],
                     "timestamps_from": "synthetic_flat_clock"},
    }
print("simulate_call defined")
'''))
C.append(code('''
# Run the function and confirm it reproduces the hand-built cooperative call. If it does not, the
# FUNCTION is wrong (or the by-hand version was) - and that gap would be the lesson, not a nuisance.
auto_coop = simulate_call(cooperative, agent_script, "sim_cooperative_001", "clean")
# Compare the parts that must match the hand build; True everywhere means the wrapper is faithful.
print("same turn count:", len(auto_coop["turns"]) == len(coop_call["turns"]))
print("same source    :", auto_coop["source"] == coop_call["source"])
print("same turns      :", auto_coop["turns"] == coop_call["turns"])
'''))
C.append(md('''
## Three more personas — the coverage the simulator buys

One cooperative caller proves the machine works. The *point* of a simulator is the callers you would
struggle to record: the **hesitant** one, the **angry** one, the **code-switching** one. We write
each as a persona (traits + utterances), exactly like the cooperative one. Watch how the *traits*
change while the *machine* stays the same — that is coverage being manufactured.
'''))
C.append(code('''
# Persona #2 - the HESITANT caller (mirrors call_B, our Hinglish partial). The hard traits are now
# True: hesitates, gives partial info, code-switches. Same dict shape as cooperative - only the knobs
# and lines change. The utterances ENCODE the traits: stalling, a repeat request, no final confirm.
hesitant = {
    "persona_id": "p_hesitant",
    "goal": "book a dentist appointment",
    "language": "Hinglish",                   # Hindi+English mix (the partial-completion condition)
    "traits": {"gives_full_info": False, "hesitates": True, "interrupts": False,
               "angry": False, "code_switches": True},
    "utterances": [
        "umm... ek minute... Friday chalega I think.",     # hesitation + code-switch in one line
        "sorry can you repeat? line thodi unclear thi.",   # a repeat request -> extra turns
        "haan main baad mein confirm karta hoon.",         # never actually confirms -> partial outcome
    ],
}
print(hesitant["persona_id"], "| traits:", hesitant["traits"])
'''))
C.append(code('''
# Persona #3 - the ANGRY caller. The 'angry' trait is True; the utterances carry the frustration
# (caps, "right now", "this is ridiculous"). Anger is a COVERAGE case you rarely have a clean real
# recording of - which is exactly why a simulator is useful here: you can summon it on demand.
angry = {
    "persona_id": "p_angry",
    "goal": "reschedule a booking",
    "language": "English",
    "traits": {"gives_full_info": True, "hesitates": False, "interrupts": True,
               "angry": True, "code_switches": False},
    "utterances": [
        "I have been on hold for TWENTY minutes. Just move my booking to Friday. NOW.",
        "I already TOLD you - Friday. Why is this so hard?",   # interrupts/repeats in frustration
    ],
}
print(angry["persona_id"], "| traits:", angry["traits"])
'''))
C.append(code('''
# Persona #4 - the CODE-SWITCHING caller (mirrors call_C, our Telugu-English failure). Telugu+English
# inside single turns, partial address, the exact texture of the real hero call. This is the persona
# closest to a real artifact we own - which sets up Act 4's honest comparison (sim vs the real log).
code_switcher = {
    "persona_id": "p_code_switcher",
    "goal": "book an appliance service visit",
    "language": "Telugu-English",
    "traits": {"gives_full_info": False, "hesitates": True, "interrupts": False,
               "angry": False, "code_switches": True},
    "utterances": [
        "haan hello... area ante... Madhapur side anukunta... near the metro station.",
        "ayyo okay okay... full address kavala? plot 42, ante... I don't remember exactly ya.",
    ],
}
print(code_switcher["persona_id"], "| traits:", code_switcher["traits"])
'''))
C.append(md('''
## PREDICT
We are about to run all four personas through the *same* simulator and collect four synthetic calls.
Before we do: rank the four by **how many turns** each call will have, fewest to most. (Hint: a
persona with more `utterances` produces more turns — count the lines.) Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - PREDICT the turn-count ranking BEFORE generating. Store the fewest/most as a check.
my_fewest_persona = None    # <- persona_id with the FEWEST turns, e.g. "p_cooperative"
my_most_persona   = None    # <- persona_id with the MOST turns

if my_fewest_persona is None or my_most_persona is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("locked - fewest:", my_fewest_persona, "| most:", my_most_persona)
'''))
C.append(code('''
# Generate one synthetic call PER persona by looping the simulator. This loop IS the coverage engine:
# four kinds of caller, four call objects, in milliseconds, no recordings needed. We give each a long
# enough agent script (extra lines are harmless - zip() stops at the shorter list, the persona).
agent_lines = [
    "Hello! How can I help you today?",
    "Got it. Can you confirm the details?",
    "Thanks - anything else?",
]
personas = [cooperative, hesitant, angry, code_switcher]   # the cast of callers (a list -> we can loop/group)
stress_by_persona = {"p_cooperative": "clean", "p_hesitant": "pause_heavy",
                     "p_angry": "interruption", "p_code_switcher": "interruption"}

sim_calls = []
for p in personas:
    # each persona becomes one synthetic call; stress_profile is chosen to match the persona's traits
    call = simulate_call(p, agent_lines, f"sim_{p['persona_id']}_001", stress_by_persona[p["persona_id"]])
    sim_calls.append(call)

print(f"{'persona_id':<18}{'language':<16}{'profile':<14}{'turns':>6}")
print("-" * 56)
for c in sim_calls:
    print(f'{c["metadata"]["persona_id"]:<18}{c["language"]:<16}{c["stress_profile"]:<14}{len(c["turns"]):>6}')
'''))
C.append(code('''
# Confront YOUR ranking with the generated turn counts.
turn_counts = {c["metadata"]["persona_id"]: len(c["turns"]) for c in sim_calls}
fewest_actual = min(turn_counts, key=turn_counts.get)        # persona id with the smallest call
most_actual   = max(turn_counts, key=turn_counts.get)        # persona id with the largest call
print("actual fewest:", fewest_actual, "| actual most:", most_actual)

if my_fewest_persona is not None:
    hit = (my_fewest_persona == fewest_actual and my_most_persona == most_actual)
    print("your ranking", "MATCHED" if hit else "DIFFERED", "- the gap is the thing to think about")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not memory): you produced four callers — including an angry
one and a Telugu-English one — without a single microphone, consent form, or storage bucket. What did
the simulator just buy you, in one word from the contract? (It starts with "c".)
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. The four personas ran through the **same** `simulate_call` function. What varied between the four
   calls, and what stayed fixed? (Connect it to the change-one-thing rule from P00.)
2. You now have four synthetic calls in the real schema. Name two real-book tools (rubric, signals,
   tagger, judge…) that would accept these calls **without knowing they are synthetic** — and say why
   that drop-in compatibility is both the *useful* part and the *dangerous* part.
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: "user simulator" was a vague phrase. After Act 2 you can do four concrete things: write a
**persona** (goal + traits + utterances) as plain data; assemble a **call object by hand** in the
`schemas/call_log.md` shape, with an honest `source: "synthetic"` flag; collapse that assembly into a
**simulator function**; and **loop it over personas** to manufacture coverage — an angry caller and a
code-switching caller on demand, no recordings. You also planted a splinter: the timestamps are a
made-up flat clock, so some signals are synthetic by construction. Act 3 pulls that splinter.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (persona-as-data / assemble-by-hand / coverage-via-loop - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: where simulation lies, and the trap at the heart of the book

## Break-it philosophy

You do not understand a simulator until you have caught it *lying*. A synthetic call passes every
schema check and scores cleanly — that is exactly what makes its lies dangerous. So we now damage it
on purpose and, more importantly, *score it on its own simulator* to watch a meaningless 100% appear.
Surprise here, on your terms, beats surprise on the demo stage when a buyer asks "and on real calls?"
'''))
C.append(md('''
## Lie #1 — the synthetic clock fakes the timing signals

The timestamps came from a flat 500ms-gap / 2500ms-duration clock we *chose*. But earlier books
compute **barge-in** and **latency** straight from those millisecond boundaries (`pipeline/signals.py`,
the FTO core). If we never authored an overlap, the simulator will report **zero barge-ins** — not
because the agent is polite, but because *we never put one in the clock*. The signal is real
arithmetic on fake numbers.
'''))
C.append(md('''
## PREDICT
Our `simulate_call` always advances the clock by a positive gap before the next turn, so no turn ever
starts before the previous ends. If we run the **barge-in** check (overlap > 100ms, from book 04 /
`rubric.yaml`) over the angry caller's synthetic call — a caller whose persona literally has
`interrupts: True` — how many barge-ins will it find? Commit a number before running.
'''))
C.append(code('''
# YOUR TURN - PREDICT the barge-in count for the ANGRY synthetic call (traits say interrupts=True).
my_bargein_count = None    # <- a whole number: how many barge-ins will the signal find?

if my_bargein_count is None:
    print("fill in my_bargein_count above, then re-run this cell.")
else:
    print("locked barge-in prediction:", my_bargein_count)
'''))
C.append(code('''
# BREAK-IT (change-it): run the real book-04 barge-in test over the synthetic call - does the persona trait survive the synthetic clock?
# The real barge-in test from book 04: FTO = next.start_ms - prev.end_ms; overlap = -FTO when negative;
# a barge-in is overlap > 100ms (rubric.yaml threshold_overlap_ms). We run it over the angry sim call.
BARGE_THRESHOLD_MS = 100

def count_barge_ins(call):
    barge = 0
    turns = call["turns"]                      # already in clock order because the simulator built them so
    for prev, nxt in zip(turns, turns[1:]):    # walk consecutive turn pairs
        fto = nxt["start_ms"] - prev["end_ms"] # negative => the next speaker started early (overlap)
        overlap = max(0, -fto)                 # the size of the overlap, 0 if there was a gap
        if overlap > BARGE_THRESHOLD_MS:
            barge += 1
    return barge

angry_call = next(c for c in sim_calls if c["metadata"]["persona_id"] == "p_angry")
found = count_barge_ins(angry_call)
print("angry persona trait 'interrupts':", angry["traits"]["interrupts"])   # the caller is SUPPOSED to interrupt
print("barge-ins the signal found        :", found)                          # ...but the synthetic clock has none
if my_bargein_count is not None:
    print("your prediction", "matched" if my_bargein_count == found else "DIFFERED")
'''))
C.append(md('''
## Reading that result — the simulator told a quiet lie

The persona says `interrupts: True`. The barge-in signal says **0**. Both are "correct" — and that is
the trap. The persona's *text* implies an interrupting caller, but the persona's **timing** was never
authored, so the flat clock laid every turn down with a polite 500ms gap. The deterministic signal
faithfully measured the fake clock and reported zero overlaps. **Nothing errored. The 0 is real
arithmetic on numbers I made up.** A synthetic call can only exercise the dimensions you actually
encoded; the barge-in dimension was *decorative text*, not *timed behavior*, so the signal is hollow.
This is the first crack: simulation is only as valid as the *specific* behaviors you bothered to model.
'''))
C.append(md('''
## Fixing lie #1 — author the overlap if you want the signal to mean anything

The fix is honest, not clever: if you want the barge-in signal to be real, you must *put a real
overlap in the clock*. We rebuild the angry caller's second turn to start **before** the agent's turn
ends — a genuine −X ms FTO — so the persona's `interrupts: True` is now *timed*, not just *typed*.
Then the signal has something true to measure.
'''))
C.append(code('''
# Author a REAL overlap into a copy of the angry call: make the user's turn t2 start 600ms BEFORE the
# agent's turn t1 ends. Now the interruption lives in the CLOCK, not just the text, so the signal is
# measuring authored behavior. We copy (not mutate sim_calls) so earlier cells stay reproducible.
import copy
angry_fixed = copy.deepcopy(angry_call)
t1, t2 = angry_fixed["turns"][0], angry_fixed["turns"][1]
t2["start_ms"] = t1["end_ms"] - 600           # the caller cuts in 600ms early -> a true barge-in
angry_fixed["metadata"]["timestamps_from"] = "synthetic_with_authored_overlap"   # confess the edit
print("t1 end:", t1["end_ms"], "| t2 start (now):", t2["start_ms"], "| FTO:", t2["start_ms"] - t1["end_ms"])
print("barge-ins after authoring the overlap:", count_barge_ins(angry_fixed))   # now the signal is real
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. The barge-in signal returned 0 on a caller whose persona said `interrupts: True`. Whose "fault"
   was the 0 — the signal, the persona text, or the synthetic clock? Be precise.
2. We "fixed" it by editing a start_ms to manufacture an overlap. Did that make the call **more
   valid** (closer to a real caller) or just **more internally consistent** (timing now matches the
   persona's text)? Why is that distinction the whole point of this book?
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this whole book is built on

**The wrong belief:** *"the agent scored 100% on our user simulator, so the agent is validated."*

This feels airtight — a high score on a battery of hard-seeming callers. The next cell scores our
scripted agent against our own personas and prints a glowing **100% task success**. Then it asks the
only question that matters. Run it, and try to explain why a perfect simulator score proves almost
nothing about real performance BEFORE the reveal.
'''))
C.append(code('''
# Score the agent on its OWN simulator. We define "success" by a checklist the SCRIPTED agent always
# satisfies (it always says a confirming line) - which is the trap: we wrote the caller, the agent,
# AND the success test. A 100% here is a closed loop congratulating itself, not evidence about reality.
def task_success(call):
    # toy success rule: did the agent ever produce a confirming/booking line? (real rubric is book 21)
    agent_text = " ".join(t["text"].lower() for t in call["turns"] if t["speaker"] == "agent")
    return any(word in agent_text for word in ("booked", "confirm", "got it", "done"))

# build the calls the agent is "tested" on - the very personas we authored to be passable
tested = [simulate_call(p, ["Got it. Confirmed - your booking is done.", "Anything else?"],
                        f"eval_{p['persona_id']}", stress_by_persona[p["persona_id"]]) for p in personas]
passes = sum(1 for c in tested if task_success(c))
print("personas tested      :", len(tested))
print("agent task success   :", f"{passes}/{len(tested)} = {100*passes//len(tested)}%")
print("question that matters : did real callers behave like these four personas? (we cannot tell from this)")
'''))
C.append(md('''
## The reveal — you wrote the test AND the answer key

The score is **100%**, and it means almost nothing. We authored the personas to be answerable, scripted
an agent that always says a confirming line, and wrote a success test that line satisfies. The loop
*had* to close — it is a machine grading its own homework. A real caller does not read your persona
file: they mumble a word your ASR drops, they ask something off-script, they go silent for nine
seconds, they get angry in a way your `angry: True` flag never captured. **The 100% measures whether
your personas are satisfiable, not whether the agent works.** This is the same shape as P00's deepest
trap — *a result can be valid on one axis (it ran, it scored) and wrong on the axis that matters* —
now landed on evaluation, where confusing coverage for validity is how a demo lies with a straight
face. The repo states the antidote plainly: validity comes from the **public-data calibration**
(`docs/limitations.md`), never from the calls you constructed.
'''))
C.append(md('''
## YOUR break now

Author your *own* simulator lie. Add a brand-new trait to a persona — say `goes_silent: True` — that
your `simulate_call` function **does not actually implement** (the function ignores unknown traits).
Predict in a comment what the generated call will look like, then run it and confirm: the trait is in
the persona, the *behavior is not in the call*. That gap — declared traits the simulator never enacts —
is the most common way a homemade simulator quietly overstates its coverage.
'''))
C.append(code('''
# YOUR TURN - BREAK-IT: self-authored simulator lie. Add a trait the simulator does NOT implement, then prove
# the behavior never appears in the generated call.
# my prediction: <write here what the call will contain, and what 'goes_silent' will (not) do, BEFORE running>

my_persona = {
    "persona_id": "p_my_test",
    "goal": "book an appointment",
    "language": "English",
    "traits": {"gives_full_info": True, "hesitates": False, "interrupts": False,
               "angry": False, "code_switches": False,
               "goes_silent": True},          # <- a trait simulate_call never reads (try adding your own too)
    "utterances": ["I'd like to book for Friday.", "Yes, that's fine."],
}
my_call = simulate_call(my_persona, ["How can I help?", "Confirmed."], "sim_my_test", "clean")
# Inspect: is there any silence/gap in the call that the 'goes_silent' trait should have caused?
gaps = [my_call["turns"][i+1]["start_ms"] - my_call["turns"][i]["end_ms"] for i in range(len(my_call["turns"])-1)]
print("declared trait goes_silent:", my_persona["traits"]["goes_silent"])
print("gaps between turns (ms)   :", gaps, "<- all the flat 500ms; no long silence was enacted")
print("lesson: a trait the simulator does not IMPLEMENT is just a comment - coverage you claim but don't have")
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
1. State the trap in one sentence: why does a 100% on your own user simulator fail to validate the
   agent? Use the words "wrote the test".
2. Two different lies showed up in Act 3: the **synthetic clock** faking a signal, and a **declared
   trait** the simulator never enacts. What do both have in common about the relationship between
   *what a persona claims* and *what the generated call actually contains*?
3. Connect it back: which P00 trap is this the grown-up version of? (Hint: valid on the wrong axis.)
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why is a perfect score on your OWN simulator not validation?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a synthetic call that scores well felt like good news. After Act 3: you have watched a
deterministic signal report **0 barge-ins on an "interrupting" caller** (a real number on a fake
clock), seen a **declared trait produce no behavior**, and scored an agent at **100% on a test you
wrote end to end**. A high simulator score is now something you distrust by reflex — you ask "and on
real calls?" A simulator exercises *exactly the behaviors you encoded*, no more, and grading your own
personas measures their satisfiability, not the world. Coverage is not validity; you have felt the gap.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the 'wrote the test and the answer key' trap is a strong pick)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: sim vs the real log, where this lives, and the bar you must clear

## Put a synthetic call NEXT TO the real one (the honest comparison)

Our `code_switcher` persona was modeled on the real hero call. Time to lay them side by side and look
*honestly*. They share the schema; they do **not** share standing as evidence. The real call's
timestamps came from an audio-assembly timeline (exact, from a real waveform); the synthetic call's
came from a flat clock we typed. Same shape, different truth. We load the real one and compare.
'''))
C.append(md('''
## PREDICT
We will compare our synthetic Telugu-English call against the real `data/hero/turns.json`. Predict
TWO things: (a) will they have the **same number of turns**? (b) which one will have a **real
barge-in** that the signal can detect — the synthetic one (flat clock) or the real one (assembly
timeline, with a documented 800ms overlap at 0:18)? Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - PREDICT the sim-vs-real comparison before loading the real call.
my_same_turn_count = None    # <- True or False: do sim and real have the same number of turns?
my_real_has_bargein = None   # <- "synthetic" or "real": which one has a detectable barge-in?

if my_same_turn_count is None or my_real_has_bargein is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("locked - same turn count:", my_same_turn_count, "| barge-in in:", my_real_has_bargein)
'''))
C.append(code('''
# Load the REAL hero call from disk. We resolve the repo root by walking up to the folder holding
# data/hero, so this runs regardless of the kernel's working directory (headless gate included).
import json
from pathlib import Path
root = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "hero" / "turns.json").exists())
hero = json.loads((root / "data" / "hero" / "turns.json").read_text())   # disk text -> dict

sim_te = next(c for c in sim_calls if c["metadata"]["persona_id"] == "p_code_switcher")
# Compare the two on shape AND on a signal, so the difference is concrete, not a vibe.
print(f'{"":<12}{"source":<12}{"language":<10}{"turns":>6}{"barge-ins":>11}')
print("-" * 51)
print(f'{"SYNTHETIC":<12}{sim_te["source"]:<12}{sim_te["language"]:<10}{len(sim_te["turns"]):>6}{count_barge_ins(sim_te):>11}')
print(f'{"REAL HERO":<12}{hero["source"]:<12}{hero["language"]:<10}{len(hero["turns"]):>6}{count_barge_ins(hero):>11}')
'''))
C.append(code('''
# Confront YOUR prediction with the comparison.
same_turns = (len(sim_te["turns"]) == len(hero["turns"]))
real_barge = count_barge_ins(hero)
sim_barge = count_barge_ins(sim_te)
who_has_barge = "real" if real_barge > sim_barge else ("synthetic" if sim_barge > real_barge else "tie")
print("same turn count:", same_turns, "| barge-in detected in:", who_has_barge,
      f"(real={real_barge}, synthetic={sim_barge})")
if my_same_turn_count is not None:
    print("your turn-count guess:", "matched" if my_same_turn_count == same_turns else "DIFFERED")
    print("your barge-in guess  :", "matched" if my_real_has_bargein == who_has_barge else "DIFFERED")
'''))
C.append(md('''
## Reading the comparison — the schema is shared, the evidence is not

The real hero call carries a **detectable 800ms barge-in** because a real assembly timeline put a real
overlap in the clock; our synthetic Telugu-English call carries **zero**, because our flat clock never
did. Same `language`, same schema, same drop-in compatibility — and one is a *recording of a hard
moment that happened*, the other is *a hypothesis about a caller, with timing we typed*. The synthetic
call is wonderful for **coverage** (we can spin up fifty code-switching variants tonight) and worthless
as **validity** (it cannot prove the agent survives a real Telugu-English caller — only the real call,
or a calibrated public set, speaks to that). That is the entire book, standing in two columns.
'''))
C.append(md('''
## When simulation is USEFUL, and when it LIES (carry this table)

Simulation is not bad — it is *mis-used*. The honest split:

| simulation is USEFUL for… | simulation LIES when used for… |
|---|---|
| **coverage**: probing many caller *kinds* (angry, silent, code-switching) cheaply | **validity**: claiming the agent works on *real* callers |
| **regression smoke tests**: did a prompt change break the cooperative flow? | **success rates you report to a buyer** as if measured on real traffic |
| **stress authoring**: building a *specific* failure to fix (then a real overlap, real silence) | **discovering unknown failures**: it only contains the ones you imagined |
| **pre-real iteration**: cheap practice before you spend on real calls/labels | **calibrating the judge**: kappa needs real human-labeled *real* calls (book 14–15) |

The rule that organizes the table: **simulation answers "can the agent handle the situations I
imagined?" It can never answer "have I imagined the situations real callers produce?"**
'''))
C.append(md('''
## Where this lives in the real VoiceForge pipeline (cite the files)

This is not a metaphor — it is wired through the repo you can open:

- **`schemas/call_log.md`** — the shape your simulator emits. The example call literally carries
  `"metadata": {"constructed": true, ...}`: the schema has a *built-in place to confess* that a call
  was constructed. An honest synthetic call fills it in; that field is the difference between a
  simulator and a forger.
- **`docs/limitations.md`** — the ethic, in writing: the constructed hero call "is a demonstration of
  what VoiceForge detects, **not evidence drawn from production traffic**", and "**validity comes from
  the public-data calibration**, not from this call." Your simulator is the same object at scale; the
  same sentence governs it.
- **`docs/curriculum-draft.md` (book 23)** — names the dataset hierarchy you are about to learn:
  hero (theater) / public (validity) / **synthetic (coverage)** / provider logs (production). Your
  one-line verdict — *buys coverage, not validity* — is the exact slot synthetic data occupies there.
- **`rubric.yaml` + `pipeline/signals.py`** — what scores the synthetic call. They run identically on
  real and synthetic input, which is *why* the `source` flag and the coverage/validity discipline have
  to live in your head, not in the tooling: the code cannot tell the difference, so you must.
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

Book 23 ranks data sources by job. Predict: when you place **synthetic** data in that hierarchy, which
job will it be assigned — coverage, validity, theater, or production — and which *other* source will be
assigned the job synthetic data *cannot* do? Your stored guess gets confronted in book 23.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for the dataset-hierarchy book (23).
my_course_prediction = ""   # which job synthetic data holds, and which source must supply validity instead - and why

if len(my_course_prediction.strip()) < 20:
    print("write your prediction above (synthetic's job + who supplies validity), then re-run.")
else:
    print("PREDICTION STORED:", my_course_prediction)
'''))
C.append(md('''
## Where this method itself fails (honesty applies to simulators too)

- **Persona monoculture** — all your personas come from one author's imagination, so they share blind
  spots. Real callers are drawn from a distribution you do not control; your personas are drawn from
  *you*. Coverage of *your* ideas is not coverage of *reality's*.
- **Decorative traits** — a trait in the dict that the simulator never enacts (the `goes_silent` you
  broke). The persona *claims* coverage the generated call does not *contain*. Audit: does every
  declared trait change the call?
- **Synthetic-timing signals** — barge-in/latency on a made-up clock are arithmetic on fiction. Either
  author real overlaps/silences deliberately, or do not report those signals on synthetic calls.
- **Eval contamination** — letting synthetic calls leak into the set you *calibrate the judge on*, or
  report as "measured performance". Synthetic is for coverage and smoke tests; validity numbers must
  come from real, human-labeled, real calls (the kappa work in books 14–15).
'''))
C.append(md('''
## The concept at three levels (say each in your own words)

- **To a beginner:** "we *invent* different kinds of callers — a calm one, a flustered one, an angry
  one — to practice the agent against, because real recordings of all those are hard to get. But acing
  the callers we made up doesn't prove the agent handles the real ones; we made up the test."
- **To an engineer:** "a user simulator turns persona specs (goal + behavioral traits + utterances)
  into call-log-shaped objects the rubric and signals score unmodified. It maximizes *coverage* of
  scenario space at near-zero cost, but carries no *external validity*: timing-derived signals reflect
  the synthetic clock, declared traits only matter if enacted, and scoring against self-authored
  personas measures their satisfiability. Validity requires real, labeled, real-call data."
- **To a founder:** "simulation lets us probe a hundred awkward call types this week for free — great
  for finding and fixing failure shapes fast. What it can *not* do is be the number we put in front of
  a buyer; 'works on our simulator' and 'works on your callers' are different claims, and we keep them
  separate on purpose. The real-call calibration is what we stand behind."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**Defense question 1: "If your simulated calls use the exact same schema as real ones and score fine, why aren't they just as good as real data?"**
<details><summary>answer</summary>Because schema-sameness is not evidence-sameness. A synthetic call is a hypothesis I authored about a caller; a real log is a recording of one that happened. The tooling can't tell them apart - which is precisely why the discipline lives in my head. They are equivalent for COVERAGE (exercising scenario kinds) and not interchangeable for VALIDITY (proving real-world performance), because I chose the caller, the difficulty, and even the timing. The `source: synthetic` flag and `metadata.constructed` exist to keep that distinction honest.</details>

**Defense question 2: "You ran the agent against your simulator and got 100% task success. Isn't that a strong result?"**
<details><summary>answer</summary>No - it's a closed loop grading its own homework. I wrote the personas, scripted the agent, and wrote the success test; the loop had to close. A 100% there measures whether my personas are satisfiable, not whether the agent works on real callers - who mumble words my ASR drops, go off-script, or fail in ways my `angry: True` flag never modeled. The honest result is "the agent handles the four situations I imagined," and I report it as a coverage/smoke check, never as validated performance. Validity comes from the public-data calibration, per `docs/limitations.md`.</details>

**Defense question 3: "Then why simulate at all - why not just use real calls for everything?"**
<details><summary>answer</summary>Because real calls are scarce, slow, and legally fussy, and they don't arrive on demand in the shape you need. Simulation buys cheap, instant COVERAGE: I can probe the angry caller, the silent caller, the code-switcher tonight, and build a specific failure to fix before spending on real recordings and human labels. It's the practice plane. The mistake isn't simulating - it's confusing the practice plane with the real sky. Use it for coverage, iteration, and regression smoke tests; get validity from real, labeled, real-call data.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own: a synthetic call laid **next to** the real hero call — same schema, different
standing (real overlap vs none); the **useful-vs-lies table** that tells you which questions a
simulator may answer; where simulation lives in the repo (`schemas/call_log.md`'s `constructed` flag,
`docs/limitations.md`'s validity sentence, book 23's hierarchy, the shared `rubric.yaml`/`signals.py`);
and, above all, the bar you must clear to PASS this book — which is *not* "the synthetic calls scored well."
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The atomic claim: **simulation buys coverage, never validity** — define both words.
2. What a **persona** is (goal + traits + utterances) and what a **user simulator** emits (a
   `call_log`-shaped object with an honest `source: "synthetic"` flag).
3. The trap: why **100% on your own simulator** validates nothing — the "wrote the test and the
   answer key" argument.
4. One concrete way a synthetic call **lies** (the barge-in signal reading 0 on an "interrupting"
   caller, because the clock was made up).
5. Where validity actually comes from instead (the public-data calibration, `docs/limitations.md`),
   and what job synthetic data holds in book 23's hierarchy.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about user simulators

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Simulation buys coverage, never validity."**

A user simulator is a coverage engine: personas in, real-shaped synthetic calls out, the angry and the
code-switching caller summoned on demand for free. That is genuinely valuable — and it is *not* proof
the agent works on real callers, because you authored the caller, the difficulty, and the clock.
Passing your own simulator proves your personas are satisfiable; validity has to come from real,
labeled, real-call data. If your sentence captures that split in your own words, this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "22_user_simulators.ipynb"   # <- this notebook's filename
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

**22 done** (pending your teach-back) → **23 · Dataset hierarchy** — the four data sources ranked by
job: hero call (theater, for the demo), public data (validity, for the real number), **synthetic
(coverage, the simulator you just built)**, and provider logs (production). You walk in already
knowing synthetic's slot and its limit — *buys coverage, not validity* — and book 23's whole point is
that disclosure is what makes all four sources legitimate side by side. The simulator is one rung; the
hierarchy is the ladder it sits on.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "22_user_simulators.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
