#!/usr/bin/env python3
# Builds 20_ab_loop.ipynb — VoiceForge University book 20.
# The ONE atomic concept: one-scenario REPLAY (v1 flawed prompt -> detect failure -> v2 prompt ->
# re-run the SAME user turns -> rescore), and the honesty wall between DEMO evidence (a closed loop
# whose SHAPE you can see) and STATISTICAL evidence (n calls, CIs, human review). n=1 is shape,
# not proof. Same four-act skeleton + markers as build_P00.py / build_13.py.
# Rerun:      .venv/bin/python notebooks/build_20.py
# Then gate:  .venv/bin/python notebooks/run_nb.py   notebooks/20_ab_loop.ipynb
#             .venv/bin/python notebooks/audit_nb.py notebooks/20_ab_loop.ipynb
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
# 20 · The A/B loop

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Run **one closed loop** by hand on a single scenario: take a **v1 (flawed) prompt**, score the
   call it produces, **detect** the specific failure, write a **v2 (fixed) prompt**, **re-run the
   SAME user turns**, and **re-score** — watching turns go down, failures go down, score go up.
2. Build the **before/after panel** that every demo lives or dies on, from raw scorecards you
   compute by hand, and read it without overclaiming.
3. Say the **honesty line verbatim** and mean it: this is **demo evidence** (a shape you can see),
   not **statistical evidence** (n calls, intervals, human review).
4. Explain **why n=1 is a shape, not a proof** — and exactly what you would need to turn the shape
   into a claim a customer could bank on.

The topic is one call, replayed twice. The reason it earns a whole book: this is the single most
*persuasive* artifact you will build (a fix you can watch work) and therefore the single easiest
one to **overclaim**. The skill is showing the shape and naming its limits in the same breath.
'''))
C.append(md('''
## 2 — Knowledge-flow map (where this book sits on the ladder)

`19 · RLHF / RLAIF (how preference data trains a policy)  ->  THIS · the A/B loop  ->  21 · the rubric (rubric.yaml: the config the whole eval reads)`

Book 19 showed how a *preference signal* (chosen over rejected) can move a model's behaviour —
the offline machinery of learning from comparisons. But before you spend a single training run,
you owe yourself the cheapest possible question: **did the change I have in mind actually fix the
thing I think is broken — on at least one concrete call I can watch?** That is the A/B loop. It is
the *manual, n=1, eyes-on* version of the same compare-two-behaviours idea: instead of a thousand
preference pairs, **one** scenario, scored both ways. Book 21 then formalizes the *scorer* itself —
`rubric.yaml`, the one config that defines every dimension, weight, and threshold the loop leans
on. This book USES a tiny rubric by hand; book 21 makes it the real, live-editable contract.
No closed loop here -> no honest before/after to put weights behind there.
'''))
C.append(md('''
## 3 — Baby intuition

You changed one line in a recipe — less salt — and you want to know if the soup got better.

The **wrong** way: cook a different soup, on a different day, for different guests, and declare
victory because *this* pot tasted fine. Nothing is comparable; you learned nothing about the salt.

The **A/B** way: same vegetables, same stock, same stove, same spoon — the **only** thing you
change is the salt. Taste the before. Taste the after. Now the difference you taste is *caused by
the one thing you changed*, because everything else was held still.

That is the whole loop. In VoiceForge the "vegetables held still" are the **caller's exact words
and timing**; the "one line changed" is the **agent's system prompt**; the "taste" is the
**scorecard**. And the honest caveat is the one every cook knows: *one good pot is not a recipe
that works every night.* You tasted once. That is a promising sign, not a guarantee.
'''))
C.append(md('''
## 4 — The formal version

An **A/B loop** (here, a *replay*) is a controlled before/after on **one fixed scenario**:

| ingredient | what it is | held fixed or changed? |
|---|---|---|
| **scenario** | the caller's exact turns (text + timing) | **FIXED** — the controlled variable |
| **policy** | the agent's system prompt (v1 then v2) | **CHANGED** — the one knob |
| **pipeline** | the same scorer applied both times | **FIXED** — same ruler both sides |
| **scorecard** | score + reason + evidence per dimension | the *measurement* you compare |

The loop, as five steps you will run by hand:
1. **v1 policy** produces a transcript on the fixed scenario.
2. **Score v1** with the pipeline → a scorecard (per `schemas/scorecard.md`: every dimension
   carries a `score`, a `reason`, and `evidence_turn_ids` — no bare numbers).
3. **Detect** the failure: read the lowest dimension's reason; that is the axis to fix.
4. **v2 policy** changes the prompt to target *that one axis* (and nothing else).
5. **Re-run the SAME scenario** through v2, **re-score** with the SAME pipeline, and lay v1 vs v2
   side by side.

Two words you must never let blur:
- **demo evidence** — "on this one call, the fix did what I claimed; here is the shape."
- **statistical evidence** — "across many calls, with intervals and human review, the fix holds."
This book produces the first and refuses to dress it up as the second.
'''))
C.append(md('''
## 5 — Why this book exists (the business + honesty reason)

The before/after replay is the **money shot** of the whole demo: a stranger watches a bad call,
watches you change one prompt, watches the *same* call go right. Nothing else lands as hard. And
nothing else is as easy to oversell — a watching investor's brain auto-completes "it fixed this
one call" into "it fixes calls," which is a claim you did **not** make and cannot yet support.

So the repo writes the limit down *before* the code. From `docs/limitations.md`:

> **A/B loop is one scenario.** If shown: one closed-loop replay (v1 flawed prompt → detected
> failures → v2 prompt → same user turns re-run → re-scored by the same pipeline). It demonstrates
> the loop's *shape*, not a statistically meaningful improvement. Production would need more logs,
> human review, offline training.

This book teaches you to *build* that replay and to *say its ceiling out loud in the same sentence
you show it*. The next cell is your first run.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just syntax.

# We print a sentence so you can see WHERE output appears (directly under the cell) and so your
# first action is a run you committed to. PREDICT - what exact text will appear below?
print("one call fixed in front of you is a shape, not a proof")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In an A/B replay, what is held **fixed**, and what is the **one** thing you change?
2. What are the five steps of the loop, in order?
3. What is the difference between **demo evidence** and **statistical evidence** — and which one
   does a single replay give you?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: "show the agent getting better" is the goal, and a good
before/after *is* the proof. After Act 1 you should hold a sharper idea: a before/after on **one
fixed scenario** is a **controlled comparison** — its value is that it isolates *the one change* —
but n=1 makes it a **shape you can see**, not a **claim across calls**. The whole craft is showing
that shape while naming its ceiling in the same breath.

If you can say that in your own words, continue. If not, re-read cell 4 (fixed vs changed) and 5.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of the difference between
# "this fix worked on one call I can watch" and "this fix works." Producing the sentence is the
# learning; reading mine would only feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so a skim cannot pass for understanding: the cell nags until you write something.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: run one closed loop by hand on one scenario

## The fixed scenario, printed RAW

Course rule: see the ugly input before transforming it. The **controlled variable** is the
caller — the exact same human turns both times. We use a tiny three-exchange booking scenario
(distilled from the real hero call `data/hero/turns.json`: a caller gives a partial locality, the
agent must decide how to handle the missing detail). The caller's turns NEVER change in this book.
We print them raw first.
'''))
C.append(code('''
# The FIXED scenario: only the user's turns, with timing. These are the controlled variable - they
# are identical in the v1 run and the v2 run, so any difference in the scorecard is caused by the
# PROMPT we changed, not by a different caller. We keep just three user turns to stay countable.
# (Distilled from data/hero/turns.json - the Madhapur partial-address booking.)
scenario_user_turns = [
    # (turn label, the caller's exact words, when they START speaking in ms)
    ("u1", "haan hello... area ante Madhapur side, near the metro station.", 600),
    ("u2", "ayyo full address kavala? plot 42 near metro pillar, I don't remember exactly ya.", 9000),
    ("u3", "AC unit... cooling weak airflow vastundi.", 20000),
]

# Print the raw turns first (course habit: see the input before computing anything from it).
for label, text, start_ms in scenario_user_turns:   # one line per turn so each is visibly one THING
    print(f"{label} @ {start_ms:>6}ms | {text}")
print("total user turns (fixed in both runs):", len(scenario_user_turns))
'''))
C.append(md('''
## How to read this tiny scenario (the 3-move ritual for a small structure)

1. Say the **count**: "three user turns."
2. Say what **one row IS**: "one row = one thing the caller said, and when they started."
3. Read **one single cell** aloud: "u1 is the caller giving a *partial* area — Madhapur, near the
   metro — without a full address."

The drama lives in **u1**: the caller hands over a usable-but-incomplete locality. What the agent
*does* with that partial is the entire difference between the v1 and v2 runs.
'''))
C.append(md('''
## The v1 (flawed) policy — one prompt, printed RAW

A **policy** here is just the agent's **system prompt** — the instruction that shapes every reply.
The v1 prompt has a real, common flaw: it is a rigid "collect everything before proceeding" rule
with no instruction to acknowledge partial info or to stay out of the caller's way. We print it
raw — you should be able to *predict the failure from the prompt alone*.
'''))
C.append(code('''
# The v1 POLICY = the agent's system prompt. This is the ONE thing we will change later. The flaw
# is baked into the wording: it orders the agent to demand the complete address up front and says
# nothing about acknowledging a partial answer or not talking over the caller. We store it as a
# plain string so the diff against v2 is literally visible later.
policy_v1 = (
    "You are a booking agent. Collect the customer's COMPLETE address with pincode, landmark, "
    "and door number before proceeding. Do not move on until every field is captured."
)
print("POLICY v1 (flawed):")
print(policy_v1)
'''))
C.append(md('''
## PREDICT
Read `policy_v1` and the caller's `u1` ("Madhapur, near the metro" — a *partial* area). Before we
generate anything, commit to two predictions:
1. How will the v1 agent **respond** to that partial — accept it and move on, or demand the full
   address?
2. Will that response cause a **barge-in** (agent talks over the caller), a **repair** problem
   (mishandled clarification), or a **task** problem (a required field never gets captured)?

Write both in the next cell before we produce the v1 transcript.
'''))
C.append(code('''
# YOUR TURN - lock your two predictions BEFORE the v1 transcript exists, so this notebook records
# YOUR thinking and a later cell can confront it. The gap between guess and reality is the lesson.
my_v1_response_guess = None   # <- a short string: how you think v1 replies to the partial area
my_v1_failure_guess = None    # <- "barge_in" / "repair_quality" / "task_completion" (your pick)

# Guard: unfilled (None) prints a nag and never crashes a fresh run.
if my_v1_response_guess is None or my_v1_failure_guess is None:
    print("fill in BOTH guesses above (a response + a failure axis), then re-run.")
else:
    print("locked: I expect v1 to reply ~", repr(my_v1_response_guess),
          "and fail mainly on:", my_v1_failure_guess)
'''))
C.append(md('''
## Produce the v1 transcript on the fixed scenario

We are not calling a real model in this book (book 10 does that with the live judge). We **author**
the v1 agent turns the way `policy_v1` would drive them — rigid, over-demanding, and (critically)
*starting to speak before the caller has finished u1*. This is the transcript the loop will score.
Manual-before-function: we build the timed turns by hand so every `start_ms`/`end_ms` is visible.
'''))
C.append(code('''
# Build the FULL v1 transcript: the fixed user turns INTERLEAVED with agent turns that policy_v1
# would produce. We hand-author the agent turns (no live model in this book) and - this is the
# point - we make the v1 agent BEGIN at 8600ms while the caller's u2 starts at 9000ms... wait, that
# is the user. We make the v1 agent's reply to u1 START before u1 ends, creating an overlap we can
# measure. Each turn carries start_ms/end_ms so the timing math downstream is real, not vibes.
transcript_v1 = [
    # (turn_id, speaker, text, start_ms, end_ms)
    ("u1", "user",  scenario_user_turns[0][1], 600,   8800),
    # v1 agent talks OVER the tail of u1 (starts 8600 < u1 end 8800) -> a barge-in of 200ms,
    # and it ignores the partial area, demanding the full address instead of acknowledging Madhapur:
    ("a1", "agent", "I need your complete address with pincode, landmark and door number before we proceed.", 8600, 16000),
    ("u2", "user",  scenario_user_turns[1][1], 9000,  18000),   # caller's fixed u2 (partial again)
    ("a2", "agent", "That is still incomplete. Please provide the full address with pincode now.", 18400, 24000),
    ("u3", "user",  scenario_user_turns[2][1], 20000, 27000),   # caller's fixed u3 (the appliance)
    ("a3", "agent", "I cannot book without the complete address. Please call back with all details.", 27300, 33000),
]
for tid, who, text, s, e in transcript_v1:    # one line per turn: see the whole interleaved call
    print(f"{tid:>3} {who:<5} [{s:>6}-{e:>6}ms] {text}")
print("v1 total turns:", len(transcript_v1))
'''))
C.append(md('''
## Score v1 BY HAND — three tiny rubric dimensions

The real pipeline scores six dimensions (`rubric.yaml`); here we score the **three** that this
scenario stresses, each as a 0–1 score with a *reason* and *evidence turn ids* — exactly the
scorecard contract from `schemas/scorecard.md` ("no bare numbers anywhere"). We compute each by
hand so the score stays attached to a fact you can point at.

- **barge_in** (deterministic): did the agent overlap the caller? overlap >100ms = a barge-in
  (`rubric.yaml: threshold_overlap_ms: 100`). 1.0 = clean, 0.0 = barged in.
- **repair_quality** (judge-style): when the caller gave a *partial* answer, did the agent
  acknowledge/confirm it (good) or demand everything again (bad)?
- **task_completion** (deterministic): were the required fields captured? (`service_area`,
  `appliance`, `time_slot`). Fraction captured = the score.
'''))
C.append(md('''
## PREDICT
You will score v1's three dimensions. Eyeball `transcript_v1` and commit to all three (0..1):
- **barge_in** (a1 starts 8600, u1 ends 8800 — overlap? how many ms?) = ?
- **repair_quality** (did a1 acknowledge "Madhapur", or demand the full address?) = ?
- **task_completion** (of service_area / appliance / time_slot, how many did v1 capture?) = ?

Write your three numbers in the next cell before we compute them.
'''))
C.append(code('''
# YOUR TURN - lock v1's three dimension scores BEFORE we compute them. The metal-detector reading
# is the gap between these guesses and the by-hand numbers.
my_v1_bargein = None    # <- 0.0 or 1.0 (was there an overlap >100ms?)
my_v1_repair = None     # <- 0..1 (how well did it handle the partial answer?)
my_v1_task = None       # <- 0..1 (fraction of the 3 required fields captured)

if None in (my_v1_bargein, my_v1_repair, my_v1_task):
    print("fill in all three v1 scores above, then re-run.")
else:
    print("locked v1 guesses -> barge_in", my_v1_bargein, "repair", my_v1_repair, "task", my_v1_task)
'''))
C.append(code('''
# Score barge_in BY HAND: find the largest agent-over-user overlap. FTO = next.start - prev.end;
# a NEGATIVE FTO means the next speaker started before the previous finished = overlap. We only
# count agent-talking-over-user (the rude direction) and compare its size to the 100ms threshold.
def max_agent_overlap_ms(transcript):
    worst = 0                                  # ms of the worst agent-over-user overlap seen
    for i in range(1, len(transcript)):
        prev_id, prev_who, _, prev_s, prev_e = transcript[i - 1]
        cur_id, cur_who, _, cur_s, cur_e = transcript[i]
        # overlap exists only when the later turn STARTS before the earlier turn ENDS:
        overlap = prev_e - cur_s               # >0 means cur began that many ms early (overlap)
        if cur_who == "agent" and overlap > 0: # only the agent talking over the user counts here
            worst = max(worst, overlap)
    return worst

v1_overlap = max_agent_overlap_ms(transcript_v1)
# rubric.yaml: overlap >100ms is a barge-in (penalized); <=100ms is a backchannel (ignored).
v1_bargein_score = 0.0 if v1_overlap > 100 else 1.0
v1_bargein_reason = (f"agent began speaking {v1_overlap}ms before the caller finished (overlap > 100ms)"
                     if v1_overlap > 100 else "no agent overlap over 100ms")
print("v1 worst agent overlap:", v1_overlap, "ms -> barge_in score", v1_bargein_score)
print("reason:", v1_bargein_reason)
'''))
C.append(code('''
# Score repair_quality BY HAND. The caller gave a PARTIAL but usable area in u1 ("Madhapur, near
# the metro"). Good repair = acknowledge/confirm the partial and ask only for the ONE missing bit.
# Bad repair = demand the entire address again, ignoring what was offered. We detect "bad" by a
# simple, inspectable rule: did the agent's reply to u1 contain an acknowledgement token AND avoid
# a blanket "complete/full address" demand? (A toy stand-in for the judge - book 10 does it for real.)
a1_text = transcript_v1[1][2].lower()          # the agent's reply to u1
acknowledged = any(w in a1_text for w in ["madhapur", "metro", "got it", "thanks"])  # did it confirm?
over_demanded = any(w in a1_text for w in ["complete address", "full address", "all details"])  # blanket demand?
# score: 1.0 if it acknowledged and did not over-demand; 0.0 if it over-demanded and did not ack.
v1_repair_score = 1.0 if (acknowledged and not over_demanded) else 0.0
v1_repair_reason = ("agent ignored the partial area and demanded the complete address instead of confirming Madhapur"
                    if v1_repair_score == 0.0 else "agent confirmed the partial area and asked only for the missing detail")
print("v1 acknowledged partial?", acknowledged, "| over-demanded?", over_demanded)
print("v1 repair_quality score:", v1_repair_score, "->", v1_repair_reason)
'''))
C.append(code('''
# Score task_completion BY HAND from a required-field checklist (schemas/task_outcome.md). The
# booking needs three fields; we mark each captured/not by scanning the WHOLE transcript text for
# evidence. The score is the fraction captured - a deterministic number, not a vibe.
required_fields = ["service_area", "appliance", "time_slot"]   # the booking's checklist
def captured_fields(transcript):
    all_text = " ".join(t[2].lower() for t in transcript)      # every turn's text, joined
    captured = {}
    captured["service_area"] = "madhapur" in all_text          # did an area survive into the call?
    captured["appliance"]    = "ac" in all_text or "cooling" in all_text   # was the appliance named?
    # a time slot only counts if the agent actually offered/confirmed one (a "morning/evening/AM"):
    captured["time_slot"]    = any(w in all_text for w in ["morning", "evening", "am ", "ten am"])
    return captured

v1_caps = captured_fields(transcript_v1)
v1_task_score = sum(v1_caps.values()) / len(required_fields)   # fraction captured
missing_v1 = [f for f, ok in v1_caps.items() if not ok]
v1_task_reason = f"captured {sorted(f for f,ok in v1_caps.items() if ok)}; never captured {missing_v1}"
print("v1 field capture:", v1_caps)
print("v1 task_completion score:", round(v1_task_score, 2), "->", v1_task_reason)
'''))
C.append(md('''
## Assemble the v1 scorecard (the real artifact shape)

Now we lay the three dimensions into a **scorecard** exactly like `schemas/scorecard.md`: each
dimension is `{name, score, reason, evidence_turn_ids}`, plus a weighted `overall`. The weights
come from `rubric.yaml` (barge_in 0.20, repair_quality 0.10, task_completion 0.20). Because we are
scoring only three of the six dimensions, we normalize by the weights we actually used — so
`overall` is a fair 0–1 within this slice.
'''))
C.append(code('''
# Build the v1 scorecard as a list of dimension dicts + a weighted overall. This is the EXACT shape
# schemas/scorecard.md mandates: every dimension carries a reason and evidence_turn_ids - the rule
# that makes a score auditable instead of a bare number you have to trust.
weights = {"barge_in": 0.20, "repair_quality": 0.10, "task_completion": 0.20}  # from rubric.yaml

def make_scorecard(call_id, bargein, bargein_reason, repair, repair_reason, task, task_reason):
    dims = [
        {"name": "barge_in",        "type": "deterministic", "score": bargein,
         "reason": bargein_reason,  "evidence_turn_ids": ["u1", "a1"]},
        {"name": "repair_quality",  "type": "judge",         "score": repair,
         "reason": repair_reason,   "evidence_turn_ids": ["u1", "a1"]},
        {"name": "task_completion", "type": "deterministic", "score": task,
         "reason": task_reason,     "evidence_turn_ids": ["u2", "u3", "a3"]},
    ]
    # weighted overall, normalized by the weights actually used (we score 3 of 6 dims here):
    total_w = sum(weights[d["name"]] for d in dims)
    overall = sum(d["score"] * weights[d["name"]] for d in dims) / total_w
    return {"call_id": call_id, "dimensions": dims, "overall": round(overall, 3)}

scorecard_v1 = make_scorecard("replay_v1", v1_bargein_score, v1_bargein_reason,
                              v1_repair_score, v1_repair_reason, v1_task_score, v1_task_reason)
for d in scorecard_v1["dimensions"]:           # print each dimension so the reasons are visible
    print(f"{d['name']:<16} {d['score']:>4}  ({d['reason']})")
print("v1 OVERALL:", scorecard_v1["overall"], "| v1 turns:", len(transcript_v1))
'''))
C.append(code('''
# Confront your v1 predictions (the metal-detector reading). Guarded so an unfilled notebook is clean.
if None not in (my_v1_bargein, my_v1_repair, my_v1_task):
    actual = (v1_bargein_score, v1_repair_score, round(v1_task_score, 2))
    guessed = (my_v1_bargein, my_v1_repair, round(my_v1_task, 2))
    print("your v1 guesses:", guessed, "| actual:", actual, "->",
          "MATCHED" if guessed == actual else "DIFFERED (the gap is the thing to study)")
'''))
C.append(md('''
## DETECT the failure (step 3 of the loop)

This is the hinge of the whole loop, and it is *not* "the score is low." A scorecard with reasons
turns a number into a **diagnosis**: read the dimension with the lowest score and look at its
*reason* — that sentence names the single axis to fix. Do **not** change everything; change the
thing the evidence points at.
'''))
C.append(code('''
# Find the failure to fix: the lowest-scoring dimension AND its reason. The reason is what makes
# this actionable - "repair_quality 0.0 because the agent demanded the full address instead of
# confirming Madhapur" tells you exactly what the v2 prompt must change (and what it must NOT touch).
worst_dim = min(scorecard_v1["dimensions"], key=lambda d: d["score"])   # lowest score = the failure
print("DETECTED failure axis:", worst_dim["name"], "(score", worst_dim["score"], ")")
print("evidence:", worst_dim["reason"], "| turns:", worst_dim["evidence_turn_ids"])
print("=> the v2 prompt must fix THIS axis and change nothing else (single-axis discipline).")
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
1. What is the **controlled variable** in this replay, and why must it stay byte-for-byte identical
   across v1 and v2?
2. The scorecard rule from `schemas/scorecard.md` is "no bare numbers" — what two things must ride
   alongside every score, and why does that turn a number into a *diagnosis*?
3. Which dimension did we **detect** as the failure, and what one axis will v2 change?
'''))
C.append(md('''
## The v2 (fixed) policy — change ONE axis

Now write **v2**. The detected failure was **repair_quality** (and the barge-in alongside it): the
agent steamrolled a partial answer. So v2 adds exactly two instructions targeting that — *confirm
the partial, ask only for the missing piece, and never speak while the caller is mid-answer.* It
changes **nothing else** (still a booking agent, still wants the fields). That single-axis
discipline is the same rule that makes a preference pair valid in book 19 / `improvement_example.md`.
'''))
C.append(md('''
## PREDICT
With v2's "confirm the partial, stay concise, don't talk over the caller" instructions on the
**same** scenario, commit to three predictions:
1. v2's **barge_in** score (will the agent still talk over u1?)
2. v2's **repair_quality** score (will it acknowledge Madhapur now?)
3. Will the **number of turns** go up, down, or stay the same? (Hint: does confirming a partial
   end the address loop faster than demanding everything?)

Write all three in the next cell before v2 exists.
'''))
C.append(code('''
# YOUR TURN - predict v2's outcome on the SAME scenario before it is built.
my_v2_bargein = None    # <- 0.0 or 1.0
my_v2_repair = None     # <- 0..1
my_v2_turns_direction = None   # <- "up" / "down" / "same" vs v1's turn count

if None in (my_v2_bargein, my_v2_repair, my_v2_turns_direction):
    print("fill in all three v2 predictions above, then re-run.")
else:
    print("locked v2 guesses -> barge_in", my_v2_bargein, "repair", my_v2_repair,
          "| turns go", my_v2_turns_direction)
'''))
C.append(code('''
# The v2 POLICY: same role, ONE axis changed. We add acknowledge-the-partial + stay-out-of-the-way,
# and touch nothing else - so any scorecard difference is attributable to THIS change. We will diff
# it against v1 in the next cell to make "we changed one thing" literally visible.
policy_v2 = (
    "You are a booking agent. If the customer gives a partial detail, CONFIRM it and ask only for "
    "the single missing piece. Reply in under two sentences. Never speak while the caller is mid-answer."
)
print("POLICY v2 (fixed):")
print(policy_v2)
'''))
C.append(code('''
# Show the change is SINGLE-AXIS by diffing the two prompts word-set wise. This is the soup rule
# made literal: if many unrelated things changed, the before/after would not isolate a cause. We
# print what v2 ADDS and what it DROPS so a reviewer can see the knob we turned (and only that knob).
set_v1, set_v2 = set(policy_v1.lower().split()), set(policy_v2.lower().split())
print("v2 ADDS  :", sorted(set_v2 - set_v1)[:12], "...")   # the new behaviour (confirm/concise/never-interrupt)
print("v2 DROPS :", sorted(set_v1 - set_v2)[:12], "...")   # the rigid 'complete/before proceeding' demand
print("=> the change is confined to how the agent handles a PARTIAL answer + interruption.")
'''))
C.append(md('''
## Re-run the SAME scenario through v2 (steps 4–5)

Re-run means: the **caller's turns are the exact same objects** (`scenario_user_turns`), and we
author the v2 agent turns the way `policy_v2` would drive them — acknowledge Madhapur, ask only
for the one missing field, stay concise, and **wait** for the caller to finish (no overlap). Then
we score it with the **same** functions. Same caller, same ruler, one changed prompt.
'''))
C.append(code('''
# Build the v2 transcript on the SAME fixed user turns. The agent now (a) waits - its first reply
# starts at 8900 > u1 end 8800, so NO overlap; (b) confirms "Madhapur" and asks only for the missing
# piece; (c) is concise enough to CLOSE the booking in one final turn after the caller volunteers the
# appliance, so it needs only TWO agent turns instead of v1's three. The user turns are reused
# verbatim from scenario_user_turns - that reuse is what makes this a controlled re-run, not a new call.
transcript_v2 = [
    ("u1", "user",  scenario_user_turns[0][1], 600,   8800),
    # v2 agent WAITS (starts 8900 > 8800 = no barge-in) and confirms the partial, asking one thing:
    ("a1", "agent", "Got it - Madhapur, near the metro. What's the door or plot number?", 8900, 13000),
    ("u2", "user",  scenario_user_turns[1][1], 9000,  18000),   # caller gives the plot number
    ("u3", "user",  scenario_user_turns[2][1], 20000, 27000),   # caller volunteers the appliance, unprompted
    # v2 CLOSES in a single concise final turn: confirms plot + appliance AND offers a time slot. By
    # not re-asking redundantly, it resolves the booking in fewer agent turns than v1 did:
    ("a2", "agent", "Thanks - plot 42, AC cooling issue. I can book tomorrow morning around ten AM. Confirm?", 27300, 32000),
]
for tid, who, text, s, e in transcript_v2:
    print(f"{tid:>3} {who:<5} [{s:>6}-{e:>6}ms] {text}")
print("v2 total turns:", len(transcript_v2), "(v1 had", len(transcript_v1), "- the concise agent closed faster)")
'''))
C.append(code('''
# Re-score v2 with the SAME functions used on v1 - reusing the ruler is non-negotiable: if you
# scored v2 with a kinder rubric, the before/after would be measuring two different things. We call
# the identical max_agent_overlap_ms / captured_fields helpers and the same scorecard builder.
v2_overlap = max_agent_overlap_ms(transcript_v2)
v2_bargein_score = 0.0 if v2_overlap > 100 else 1.0
v2_bargein_reason = (f"agent overlapped the caller by {v2_overlap}ms"
                     if v2_overlap > 100 else "agent waited for the caller to finish (no overlap)")

a1v2 = transcript_v2[1][2].lower()
ack2 = any(w in a1v2 for w in ["madhapur", "metro", "got it", "thanks"])
over2 = any(w in a1v2 for w in ["complete address", "full address", "all details"])
v2_repair_score = 1.0 if (ack2 and not over2) else 0.0
v2_repair_reason = ("agent confirmed the partial area (Madhapur) and asked only for the missing detail"
                    if v2_repair_score == 1.0 else "agent still mishandled the partial answer")

v2_caps = captured_fields(transcript_v2)
v2_task_score = sum(v2_caps.values()) / len(required_fields)
v2_task_reason = f"captured {sorted(f for f,ok in v2_caps.items() if ok)}"

scorecard_v2 = make_scorecard("replay_v2", v2_bargein_score, v2_bargein_reason,
                              v2_repair_score, v2_repair_reason, v2_task_score, v2_task_reason)
for d in scorecard_v2["dimensions"]:
    print(f"{d['name']:<16} {d['score']:>4}  ({d['reason']})")
print("v2 OVERALL:", scorecard_v2["overall"], "| v2 turns:", len(transcript_v2))
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. Name the **two** things we deliberately reused (not rebuilt) for the v2 run, and why reusing
   each is what makes this a *controlled* comparison rather than a second unrelated call.
2. v2's barge_in went to 1.0 — point at the exact timing fact that flipped it (which two ms numbers).
3. If you had also rewritten the rubric for v2, what claim would the before/after lose the right
   to make?
'''))
C.append(md('''
## Build the before/after panel — the money shot, from raw scorecards

Now the panel every demo rests on: v1 vs v2, side by side, on the three things a viewer cares about
— **turns**, **failures** (dimensions scoring 0), and **overall score**. We compute each column
from the two scorecards by hand first (no chart yet — numbers before pictures), so you can defend
every cell of the panel.
'''))
C.append(md('''
## PREDICT
Before the panel prints, commit to the three deltas (v1 → v2):
- **turns**: v1 had 6. v2 has …? (count `transcript_v2`.)
- **failures** (dimensions at score 0): v1 had …? v2 has …?
- **overall score**: up or down, and roughly by how much?
'''))
C.append(code('''
# YOUR TURN - predict the three panel deltas before the panel is built.
my_turns_v2 = None       # <- integer: number of turns in v2
my_failures_v2 = None    # <- integer: how many v2 dimensions score 0
my_score_direction = None  # <- "up" / "down"

if None in (my_turns_v2, my_failures_v2, my_score_direction):
    print("fill in all three predictions above, then re-run.")
else:
    print("locked panel guesses -> v2 turns", my_turns_v2, "| v2 failures", my_failures_v2,
          "| score goes", my_score_direction)
'''))
C.append(code('''
# Compute the panel's three measures for each version BY HAND from the scorecards. "failures" =
# the count of dimensions that scored exactly 0 (a hard fail on that axis) - a blunt but honest
# tally of how many things went wrong, which is what a viewer reads first.
def panel_row(transcript, scorecard):
    turns = len(transcript)                                   # how long the call ran
    failures = sum(1 for d in scorecard["dimensions"] if d["score"] == 0.0)  # hard-failed axes
    score = scorecard["overall"]                              # the weighted 0..1 overall
    return turns, failures, score

v1_turns, v1_fails, v1_score = panel_row(transcript_v1, scorecard_v1)
v2_turns, v2_fails, v2_score = panel_row(transcript_v2, scorecard_v2)

# Print the before/after panel as a labeled table (numbers before any chart - course rule):
print(f"{'measure':<18}{'v1 (before)':>14}{'v2 (after)':>14}{'delta':>10}")
print("-" * 56)
print(f"{'turns':<18}{v1_turns:>14}{v2_turns:>14}{v2_turns - v1_turns:>+10}")
print(f"{'failures (score 0)':<18}{v1_fails:>14}{v2_fails:>14}{v2_fails - v1_fails:>+10}")
print(f"{'overall score':<18}{v1_score:>14}{v2_score:>14}{round(v2_score - v1_score, 3):>+10}")
'''))
C.append(code('''
# Confront your panel predictions. Guarded for an unfilled notebook.
if None not in (my_turns_v2, my_failures_v2, my_score_direction):
    dir_actual = "up" if v2_score > v1_score else "down"
    print("turns:    you", my_turns_v2, "| actual", v2_turns, "->", "OK" if my_turns_v2 == v2_turns else "off")
    print("failures: you", my_failures_v2, "| actual", v2_fails, "->", "OK" if my_failures_v2 == v2_fails else "off")
    print("score:    you said", my_score_direction, "| actual", dir_actual, "->",
          "OK" if my_score_direction == dir_actual else "off")
'''))
C.append(md('''
## PREDICT
The next cell draws the panel as a grouped bar chart (overall score, v1 vs v2). Apply P00's
chart ritual *in advance*: what is x, what is y, what is one bar, and — the dangerous question —
**what claim will this chart license, and what claim will it NOT?** Commit before it renders.
'''))
C.append(code('''
# Draw the money-shot chart: v1 vs v2 overall score, two bars. Every line says why it exists.
import matplotlib.pyplot as plt   # the standard plotting library; imported where first used

labels = ["v1 (before)", "v2 (after)"]     # x: the two policy versions (the THING that changed)
scores = [v1_score, v2_score]              # y: the overall scorecard value (the MEASURE)

fig, ax = plt.subplots(figsize=(5, 3))     # small canvas; this is a glance, not a dashboard
bars = ax.bar(labels, scores, color=["#c0504d", "#4f81bd"])  # red=before, blue=after (a viewer reads color)
ax.set_ylim(0, 1)                          # scores are 0..1; fixing the axis stops a tiny gain looking huge
ax.set_ylabel("overall score (0-1)")       # unlabeled axes are how charts lie by omission
ax.set_title("one scenario, v1 vs v2 (n=1)")  # the title CARRIES the caveat: n=1, on purpose
for b, s in zip(bars, scores):             # print the value on each bar so the number is undeniable
    ax.text(b.get_x() + b.get_width() / 2, s + 0.02, f"{s:.2f}", ha="center")
plt.show()
'''))
C.append(md('''
## OBSERVE + EXPLAIN (and the chart's ceiling)

Say it in one sentence: the bar went from v1 to v2 **because the one prompt change removed the
barge-in and fixed the partial-answer handling, which also let the task complete in fewer turns.**

Now the dangerous question 4 from the ritual, answered out loud: this chart licenses *"on this one
scenario, v2 scored higher than v1."* It does **NOT** license *"v2 is better"* — there is one call
behind each bar. A two-bar chart with n=1 behind it is a **shape**, and the title says so.
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before Act 2: "show a before/after" was a vague goal. After Act 2 you can **run the whole loop by
hand** — fix the scenario, score v1 into a scorecard with reasons/evidence, **detect** the failure
from the lowest dimension's reason, change **one axis** into v2, **re-run the same turns**, re-score
with the **same ruler**, and assemble the before/after panel (turns down, failures down, score up).
And you can read the panel honestly: it shows a shape on one call. That scorecard shape is exactly
what book 21's `rubric.yaml` exists to define and weight.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (the five-step loop, or "same ruler/same caller" - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the loop's honesty, then the trap at its heart

## Break-it philosophy

The A/B loop is a *measurement*, and a measurement you have never seen lie is one you do not
understand. We now sabotage the loop in the exact ways a hurried demo-builder would — change two
things at once, score the two runs with different rulers, "improve" by retrying noise — and watch
the before/after turn into a number that *looks* like progress and *means* nothing. Surprise here,
at your desk, is education; surprise on the demo stage is a lie you told by accident.
'''))
C.append(md('''
## PREDICT
First break: v2 changes the prompt **and** secretly drops one hard user turn (we make u2 cooperative
instead of the messy partial). The score will go up. Predict: is that rise caused by your prompt
fix, by the easier scenario, or **can you no longer tell**? Commit to one.
'''))
C.append(code('''
# BREAK-IT (guided) - the "moved two knobs" sabotage. This is NOT supposed to crash; it is supposed
# to produce a HIGHER score that means nothing, because we changed the prompt AND the scenario at
# once. We replace the messy partial u2 with a clean, fully-cooperative turn - now any gain is
# un-attributable. (The whole soup lesson, violated on purpose so you feel why it matters.)
scenario_user_turns_EASY = list(scenario_user_turns)
scenario_user_turns_EASY[1] = ("u2", "Sure - plot 42, pincode 500081, near metro pillar 3, door 2B.", 9000)  # now complete!

# Build a v2-on-EASY transcript: same v2 agent behaviour, but the caller handed over everything.
transcript_v2_easy = [
    ("u1", "user",  scenario_user_turns_EASY[0][1], 600,   8800),
    ("a1", "agent", "Got it - Madhapur, near the metro. What's the door or plot number?", 8900, 13000),
    ("u2", "user",  scenario_user_turns_EASY[1][1], 9000,  16000),   # the SWAPPED easy turn
    ("a2", "agent", "Thanks. And which appliance needs servicing?", 16400, 19000),
    ("u3", "user",  scenario_user_turns_EASY[2][1], 20000, 27000),
    ("a3", "agent", "An AC cooling issue - I can book tomorrow morning at ten AM. Confirm?", 27300, 31000),
]
easy_caps = captured_fields(transcript_v2_easy)
easy_task = sum(easy_caps.values()) / len(required_fields)
print("v2-on-EASY task_completion:", round(easy_task, 2), "(captured", easy_caps, ")")
print("score rose - but we changed TWO things (prompt AND scenario). Which one caused it? Unknowable.")
'''))
C.append(md('''
## Reading the lie (a real gain and a fake one are now indistinguishable)

No crash. The score went up. And it is **worthless**, because two variables moved: the prompt got
better *and* the caller got easier. When the scenario is not held fixed, the before/after stops
being a controlled comparison and becomes two unrelated calls with a flattering arrow drawn between
them. A skeptic asks one question — *"is the v2 call the same call?"* — and the whole demo evaporates.

The fix is the discipline from Act 2: the **controlled variable (the user turns) must be byte-for-byte
identical**. Change the policy. Never the scenario. If you want to test an easier scenario, that is
a *different* A/B, run and reported separately.
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
The "moved two knobs" run scored higher than the honest v2. Explain, using the word **controlled
variable**, why that higher number is *less* trustworthy than the lower honest one — and what one
question a skeptic asks to expose it.
'''))
C.append(md('''
## A second break: different rulers for the two runs

The other classic sabotage: keep the scenario fixed, but score v1 with a harsh rubric and v2 with
a lenient one. Same trick, different knob — the *measurement* changed between before and after, so
the comparison is meaningless even though the call did not change.
'''))
C.append(md('''
## PREDICT
We re-score the **honest** v2 transcript but with a *kinder* barge-in threshold (allow up to 500ms
overlap before it counts). v1 keeps the strict 100ms threshold. Predict: will v2's barge_in look
better, and is that improvement real or an artifact of the changed ruler?
'''))
C.append(code('''
# BREAK-IT (guided) - score the SAME two calls with DIFFERENT rulers. Not supposed to crash;
# supposed to manufacture a fake improvement. We re-score v1's overlap at the strict 100ms cut but
# v2's at a lenient 500ms cut - so even an identical overlap would be judged differently. Comparing
# across two rulers is comparing nothing.
v1_strict = 0.0 if v1_overlap > 100 else 1.0     # v1 judged strictly (overlap > 100ms = fail)
v2_lenient = 0.0 if v2_overlap > 500 else 1.0    # v2 judged leniently (overlap > 500ms = fail) <- rigged
print(f"v1 overlap {v1_overlap}ms judged at >100ms -> {v1_strict}")
print(f"v2 overlap {v2_overlap}ms judged at >500ms -> {v2_lenient}  <- different ruler!")
print("if these look different, you cannot tell whether v2 improved or the ruler softened.")
print("the SAME ruler must score both sides - that is why Act 2 reused max_agent_overlap_ms verbatim.")
'''))
C.append(md('''
## YOUR break now

Author your own sabotage of the loop's honesty. Pick ONE thing that should be held fixed (the user
turns, the rubric weights, the scoring functions, the set of dimensions scored) and *change it
between v1 and v2*. PREDICT in the comment how it fakes a gain or hides a regression, then run and
read. The default below is a harmless no-op so an unfilled notebook runs clean.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it of the loop's honesty.
# my prediction: <write here: which 'held-fixed' thing you changed, and how it fakes/hides a result>

# Default: an HONEST re-score (changes nothing) so an unfilled notebook passes. Edit to inject a
# sabotage - e.g. give v2 a different 'weights' dict, or drop a dimension from v2's scorecard, or
# bump a user turn's wording. Whatever you change between the two sides is the lie you are studying.
my_weights_v1 = dict(weights)                 # v1's rubric weights
my_weights_v2 = dict(weights)                 # <- change a value here to score v2 on a different rubric
# example sabotage (uncomment): my_weights_v2["barge_in"] = 0.0   # make v2 ignore barge-ins entirely

# Re-derive each overall under its own (possibly tampered) weights and compare:
def overall_under(scorecard, w):
    tot = sum(w[d["name"]] for d in scorecard["dimensions"]) or 1
    return round(sum(d["score"] * w[d["name"]] for d in scorecard["dimensions"]) / tot, 3)

ov1 = overall_under(scorecard_v1, my_weights_v1)
ov2 = overall_under(scorecard_v2, my_weights_v2)
print("v1 overall under its weights:", ov1, "| v2 overall under its weights:", ov2)
print("if the two weight dicts differ, this 'improvement' is partly the changed ruler, not the agent.")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this whole book is built on

**The wrong belief:** "the replay shows v2 beats v1, so **v2 is the better policy**."

The next cell exposes the gap. We keep our honest, controlled loop — same caller, same ruler, one
prompt change — and it cleanly shows v2 winning **on this scenario**. Then we run v2 against a
*second, different* caller (an impatient one who interrupts the agent) and discover v2 can lose
there. One closed loop told us the **shape** of a fix; it never told us the fix **generalizes**.
Run it, then — before the reveal — decide what the single replay did and did not earn the right to say.
'''))
C.append(md('''
## PREDICT
v2 beat v1 on our scenario. Now a *different* caller barges in on the agent mid-sentence (something
our fixed scenario never tested). Predict v2's **barge_in** score on this new caller. Does v2's win
on scenario #1 guarantee a win on scenario #2? Commit to a yes/no and a score.
'''))
C.append(code('''
# The trap, made concrete. We take the SAME honest v2 prompt and drop it into a DIFFERENT scenario:
# an impatient caller who starts u2 while the agent's a1 is still talking. v2 was tuned to not let
# the AGENT interrupt - it says nothing about a caller who interrupts, and our barge_in metric only
# flags AGENT-over-user, so a caller-over-agent overlap here is a failure mode the replay never saw.
transcript_v2_other = [
    ("u1", "user",  "Madhapur, near the metro - and I'm in a real hurry.", 600, 8800),
    ("a1", "agent", "Got it - Madhapur, near the metro. What's the door or plot...", 8900, 14000),
    # different caller barges over the AGENT (u2 starts 12000 < a1 end 14000): a new failure mode
    ("u2", "user",  "just book it for tomorrow morning, ten AM, plot 42!", 12000, 16000),
    ("a2", "agent", "Tomorrow at ten AM, plot 42 - but I also still need...", 16200, 20000),
    ("u3", "user",  "that's fine, AC cooling issue, bye.", 19000, 22000),  # interrupts again
]
# Our barge_in metric scores AGENT-over-user only, so it still reads 1.0 here - it literally cannot
# SEE the caller-over-agent chaos. The honest v2 'win' did not transfer; the scenario hid the issue.
other_overlap = max_agent_overlap_ms(transcript_v2_other)
print("v2 on a DIFFERENT caller - agent-over-user overlap:", other_overlap, "ms -> barge_in",
      0.0 if other_overlap > 100 else 1.0)
print("but the caller barged over the AGENT twice (12000<14000, 19000<20000) - a failure our")
print("one-scenario replay never tested and our metric never measured. one loop != generalization.")
'''))
C.append(md('''
## The reveal

The replay was *honest* — controlled variable fixed, one knob turned, same ruler — and it truly
showed **v2 > v1 on that scenario**. Every bit of that is real. What it could not show, and what the
viewer's brain silently added, is **"v2 > v1 in general."** A second caller surfaced a failure mode
the single scenario never contained (a caller who interrupts the agent), and even our *metric* was
blind to it. **One closed loop measures a shape on one scenario; it does not measure generalization.**

This is the heart of the book: a perfectly honest, perfectly controlled n=1 result is still **demo
evidence, not statistical evidence**. To earn *"v2 is better"* you need what `docs/limitations.md`
names: **more logs, human review, offline training** — many scenarios, intervals around the gains,
and humans confirming the scorecards. The replay's job is to be the *promising shape* that earns
those next steps, not to impersonate them.
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why does v2 winning on ONE controlled scenario not mean "v2 is better"?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
The replay was fully honest and still did not prove "v2 is better." State the exact boundary: what
DID the single controlled loop earn the right to claim, what did it NOT, and name the three things
`docs/limitations.md` says production would need to cross that line.
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a rising before/after bar felt like proof a change works. After Act 3 you know the three
ways a replay lies — **two knobs moved** (scenario not held fixed), **two rulers** (rubric changed
between sides), and the subtler one, **an honest n=1 mistaken for generalization**. The first two
you prevent with discipline (fix the caller, reuse the ruler); the third you prevent with *honesty*
— calling a controlled single loop **demo evidence (a shape)**, never **statistical evidence (a
proof across calls)**.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the n=1 trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where the A/B loop lives in VoiceForge, and how to defend it

## Where the replay lives in the real pipeline

This is the demo's closing move, assembled from parts you have already met:
- The **fixed scenario** is a real call's turns — `data/hero/turns.json` (the Telugu-English
  Madhapur booking = `call_C`). Its user turns are the controlled variable; only the agent's
  **system prompt** changes between v1 and v2.
- The **scorer** is the real pipeline: `pipeline/signals.py` (`turn_metrics()`, `analyze()`) for the
  deterministic dimensions (barge_in, latency_gap, task_completion) and `pipeline/judge.py`
  (`judge_dimension()`) for the judged ones — both reading dimensions/weights/thresholds from
  **`rubric.yaml`** (book 21). The **same** scorer runs on both v1 and v2.
- The output is two **scorecards** (`schemas/scorecard.md`) and the before/after panel. The detected
  failure becomes an **improvement_example** (`schemas/improvement_example.md`) — a (chosen, rejected)
  pair differing only on the failure axis — which is the bridge back to RLHF/RLAIF (book 19) and DPO.
- The honesty caveat is pre-written in **`docs/limitations.md`** ("A/B loop is one scenario") and
  shown on its **own slide**, in the same beat as the panel.
'''))
C.append(md('''
## PREDICT (connect to the real cast + honesty line)

The recurring cast: **call_A** succeeds, **call_B** is a partial, **call_C** fails (the hero call).
The demo replays a fix on **call_C**. Suppose the panel shows call_C going from score 0.41 to 0.78
after a one-line prompt change. A judge in the room asks: *"so your agent is 90% better now?"*
Predict the **one sentence** you should say back — the honest line that shows the shape and names
its ceiling at once. Write it, then compare to the book's verbatim line below.
'''))
C.append(code('''
# YOUR TURN - draft the one honest sentence you'd say when the panel impresses someone. It must do
# BOTH jobs: claim the shape you really showed, and refuse the over-claim you did not earn.
my_honest_line = ""   # <- your one sentence (shape shown + ceiling named, together)

if len(my_honest_line.strip()) < 25:
    print("write your honest one-liner above (25+ chars), then re-run.")
else:
    print("YOUR HONEST LINE:", my_honest_line)
    # The book's verbatim version (docs/curriculum-draft.md) - say it the same way every time:
    print("BOOK'S LINE     : One closed-loop demonstration, not statistical proof - the shape is the point.")
'''))
C.append(md('''
## The honesty line, verbatim (memorize it)

> **"One closed-loop demonstration, not statistical proof — the shape is the point."**

Say it in the same breath as you show the panel. It is not a hedge that weakens the demo — it is the
sentence that makes a sharp room *trust* the demo, because you named the ceiling before they could.
A founder who shows a shape and calls it a proof loses the room the instant someone asks "n?". A
founder who shows a shape and *calls it a shape* keeps the room — and earns the follow-up meeting.
'''))
C.append(md('''
## The concept at three levels (say each to its audience)

- **For a beginner:** "We recorded one bad call, changed one instruction to the agent, and played
  the *same* call again — it went better. It is one example we can watch work, not a promise it
  works every time."
- **For an engineer:** "A controlled A/B on one fixed scenario: user turns held constant, system
  prompt is the single varied factor, the same scoring pipeline runs both sides. It isolates the
  effect of the prompt change at n=1 — demo-grade evidence, not a powered comparison; generalization
  needs many scenarios, CIs, and human-verified labels."
- **For a founder:** "It is the most convincing thing we show and the easiest to oversell, so we do
  both: we show the fix working live, and we say in the same sentence that it is one scenario — a
  shape, not a statistical claim. That honesty is the moat; anyone can demo a cherry-pick."
'''))
C.append(md('''
## Defense questions (×3 — try to answer before opening each)

**1. "Your before/after looks great — is the agent actually better now?"**
<details><summary>answer</summary>On this one scenario, yes, and you can watch why: same caller, same scorer, one prompt change, barge-in gone and the task completed in fewer turns. But it is n=1 — demo evidence, not statistical evidence. "Better in general" needs many calls, confidence intervals, and human review. I'd show this as a shape that earns the bigger run, not as the bigger run.</details>

**2. "How do I know you didn't just pick an easier call for v2?"**
<details><summary>answer</summary>Because the caller's turns are the controlled variable — byte-for-byte identical objects in both runs (we reuse the same scenario list, not a fresh call). Only the system prompt changes, and the same scoring functions run on both transcripts. If the scenario or the rubric had changed too, the comparison would be meaningless, and I'd be the first to throw it out.</details>

**3. "Why show n=1 at all if it proves nothing?"**
<details><summary>answer</summary>Because a shape is worth showing when you label it as a shape. The replay proves the loop *closes* — detect a failure, change one axis, re-run, see it fixed — which is the mechanism the whole product rests on. It is the cheapest possible check before spending a training run, and it makes the abstract concrete. I never let it stand in for the statistical claim; I say "the shape is the point" out loud.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own: where the replay lives in the real pipeline (fixed scenario from
`data/hero/turns.json`, scored by `signals.py` + `judge.py` + `rubric.yaml`, output as two
scorecards + an `improvement_example`), the **verbatim honesty line**, how to explain the loop to a
beginner / engineer / founder, and how to defend "it's a shape, not a proof" under pressure. Next
book formalizes the **ruler** itself — `rubric.yaml`, the one config every score in this loop read
from.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The five steps of the A/B loop (v1 → score → detect → v2 → re-run+rescore), and the ONE thing
   held fixed throughout.
2. What a scorecard must carry beyond a number (reason + evidence) and why that makes "detect the
   failure" possible.
3. The two discipline breaks (two knobs moved; two rulers) and the one honesty break (n=1 read as
   generalization) — and the guard against each.
4. The honesty line, **verbatim**, and why saying it *strengthens* a demo.
5. One real place in VoiceForge this runs (hint: replay `call_C` from `data/hero/turns.json`,
   scored by the same pipeline, shown on its own slide next to the limitations slide).

Missed one? Open it back up, find the act, redo it. That is the system working — not a failure.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (where this lives / the honesty line)
my_clean_sentence = ""      # the sentence you would say in a room about the A/B loop

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"One closed-loop demonstration, not statistical proof — the shape is the point."**

If your sentence captures that — a single controlled replay shows you the *shape* of a fix working
(detect → change one thing → re-run → see it move), and its honesty is in calling that a shape and
not a statistical proof — this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "20_ab_loop.ipynb"   # <- this notebook's filename
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

**20 done** (pending your teach-back) → **21 · the rubric (`rubric.yaml`)** — you just leaned on a
3-dimension rubric by hand (barge_in, repair_quality, task_completion, with weights). Book 21 makes
that the **real, single source of truth**: the one YAML file the whole pipeline reads for every
dimension, weight, and threshold — live-editable on demo day so editing one line re-scores every
call and redraws every panel, including the before/after you just built.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "20_ab_loop.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
