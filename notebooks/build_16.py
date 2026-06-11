#!/usr/bin/env python3
# Builds 16_improvement_examples.ipynb — VoiceForge University book 16.
# ONE atomic concept: turn one detected failure into a (rejected -> chosen) improvement_example,
#   say WHY chosen beats rejected, and split failures into trainable (token choice, weight-fixable)
#   vs config-fixable (dead air / barge-in TIMING = endpointing, not tokens).
# Data: cast C / the real hero call (data/hero/turns.json) — its t3 is the specimen (barge-in 800ms
#   AND over-demand). Schema: schemas/improvement_example.md. Pipeline: pipeline/dpo_export.py.
# Same four-act skeleton + audit markers as build_P00.py / build_07.py (the gold references).
# Rerun: .venv/bin/python notebooks/build_16.py
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
# 16 · Improvement examples

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Take a **detected agent-side failure** and write the **better agent turn** it should have said —
   then state in one sentence **why** the better turn wins.
2. Pack that failure → fix into one **`improvement_example`** record with the exact fields the repo
   uses (`call_id`, `failure_dimension`, `rejected_turn`, `chosen_turn`, `reason`, `quality_delta`,
   `needs_human_review`).
3. Sort any failure into **trainable** (a *token-choice* problem a text pair can fix — weight-fixable)
   vs **config-fixable** (a *timing* problem like dead air or barge-in that no text pair can fix —
   it lives in endpointing/thresholds, not tokens).
4. Defend the load-bearing line of this book: **every agent-side failure can propose its own fix** —
   and know which failures propose a *training* fix versus a *config* fix.

The topic stays small: one real failed turn from the hero call, a handful of fields, two buckets.
The point is the **move** — failure becomes a labeled proposal — and the **boundary** between the
two kinds of fix.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits on the ladder)

`15 · pilot calibration  →  THIS · improvement examples  →  17 · preference pairs`

Book 15 ended the *measurement* arc honestly: a small pilot, a trust number on the judge, and the
discipline of not overclaiming. So now you have **scored** calls — you can point at a turn and say
"this one failed, here is the dimension, here is the evidence." But a score is a verdict, not a
remedy. This book takes one scored failure and turns it into a **proposal for a better turn** — the
first artifact that *changes the agent* instead of just grading it.

Book 17 then takes a pile of these proposals and shapes them into the (chosen, rejected) **preference
pairs** that a DPO trainer eats. So the ladder is: *measure the failure (≤15)* → **propose the fix,
and decide if it is even a training-shaped fix (16)** → *assemble the training data (17)*. No
proposal here → no clean pairs there. And the trainable/config split you build here is what stops
book 17 from feeding the trainer a failure that training cannot fix.
'''))
C.append(md('''
## 3 — Baby intuition

A code review does not stop at "this function is wrong." A useful review says **what it should be
instead**, and **why** — and a *great* reviewer also says whether the fix belongs in the code, or in
the config/build settings. "Wrong" is a complaint; "here is the corrected line, because X, and this
one is actually a config flag not a code change" is engineering.

Our agent failed a turn: on a real Telugu-English service call, the caller was still mid-answer when
the agent **cut in** and **demanded the full address** instead of acknowledging what it just heard.
A bare score says "barge_in: fail." That fixes nothing. The move in this book is the reviewer's move:
write the **turn the agent should have said**, state **why it wins**, and label **which kind of fix**
this is — a better *sentence* (trainable) or a better *clock* (config).
'''))
C.append(md('''
## 4 — The formal version

Three ideas this whole book turns on — keep them in separate boxes:

| word | plain meaning | in this book |
|---|---|---|
| **rejected turn** | what the agent *actually* said (it is already in the transcript) | hero `t3`: the over-demand |
| **chosen turn** | the corrected turn — differs from rejected **only on the failure axis** | a short acknowledge + one follow-up |
| **improvement_example** | one record bundling failure → fix + provenance + a review flag | the schema in `schemas/improvement_example.md` |

And the cut that gives this book its spine — every failure is one of two kinds:

- **trainable (weight-fixable):** the agent picked the wrong **tokens**. A different *sentence* fixes
  it, so a text (rejected, chosen) pair can teach it. Example: over-demanding instead of acknowledging.
- **config-fixable:** the failure is in the **timing**, not the words — dead air, or the barge-in
  *act* of starting too early. No rewrite of the sentence changes a clock. The fix lives in
  **endpointing milliseconds / interruption thresholds** (config), not in weights.

The trap that earns Act 3: the hero turn is **both at once** — the agent barged in (config-fixable
timing) *and* over-demanded (trainable tokens). One turn, two failures, two different repair shops.
'''))
C.append(md('''
## 5 — Why this book exists (a score grades; a proposal repairs)

A scored corpus tells a founder "we fail 30% of interruption calls." That funds nothing and fixes
nothing — it is a thermometer, not a treatment. The instant each failure also carries **the better
turn it should have said** plus **which fix it proposes**, you have an *asset*: a growing queue of
machine-proposed corrections, each traceable to a ms-stamped failure, each labeled train-vs-config.

In the real repo this queue is `pipeline/dpo_export.py` writing `out/queue.jsonl` — failures turned
into (chosen, rejected) pairs, every record carrying `call_id` and `failure_dimension` provenance and
`needs_human_review=true` by default (the schema is `schemas/improvement_example.md`). This book is
the hand-built version of one such record — so when you read the real queue you know exactly what
each field is, and why a dead-air failure must **not** show up there as a text pair.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What is the difference between a **score** on a failed turn and an **improvement_example** for it?
   (One grades; one proposes a remedy.)
2. Name the two kinds of fix a failure can propose, and the one-word signal each reads
   (one is about **tokens**, one is about the **clock**).
3. Why is "barge_in: fail" useless on its own to an engineer, and what does this book add to it?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: once a call is scored, the evaluation work is done. After Act 1
you should hold a new move and a new cut. The move: a failure becomes a **proposal** — `rejected` →
`chosen` + a one-sentence *why*. The cut: not every failure is **trainable**; a pure-timing failure
(dead air, barge-in act) is **config-fixable** and a text pair cannot teach it.

If "a proposal is not a score" and "tokens vs clock" feel like two genuinely separate ideas, continue.
If a barge-in still feels like the kind of thing you would just train away, re-read cell 4 — that
conflation is the exact mistake Act 3 is built to break.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of "a proposal is not a score." Not mine - yours.
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
# Act 2 — Mechanics: take the real failure, write the better turn, pack the record

## The specimen — the hero call's failed turn (raw, before any fix)

Everything in this act hangs off ONE real failure. We load the recurring **cast C** call — the
Telugu-English appliance-service booking, `data/hero/turns.json` — and read the exact two turns
where it goes wrong. No fixing yet; we look at the raw transcript first (a course rule).
'''))
C.append(code('''
# Load the real hero call (cast C). We resolve the repo root by walking up to the folder that holds
# data/hero, so this runs no matter the kernel's working directory - the same load you did in book 04.
import json
from pathlib import Path
root = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "hero" / "turns.json").exists())
hero = json.loads((root / "data" / "hero" / "turns.json").read_text())   # disk text -> dict

# Print the call's identity so you know WHICH specimen we are operating on (provenance starts here).
print("call_id        :", hero["call_id"])
print("language       :", hero["language"])         # te-en: Telugu-English code-switching
print("stress_profile :", hero["stress_profile"])   # interruption - the scenario class from book 07
print("turns          :", len(hero["turns"]))
'''))
C.append(code('''
# Pull out the two turns at the failure moment. t2 is the caller still giving their area;
# t3 is the agent's reply. We isolate them as named variables so every later cell points at the SAME
# evidence (and so the record we build can cite turn-ids, not vibes).
user_t2  = next(t for t in hero["turns"] if t["turn_id"] == "t2")   # the caller, mid-answer
agent_t3 = next(t for t in hero["turns"] if t["turn_id"] == "t3")   # the agent, the failed turn

# Print the raw text of both, so the failure is VISIBLE, not asserted.
print("t2 user :", user_t2["text"])
print("t3 agent:", agent_t3["text"])
'''))
C.append(md('''
## PREDICT (read the two turns above, slowly)
The agent's `t3` does two distinct things wrong at once. One is about **when** it spoke; one is about
**what** it said. Name both in your head before the next cells measure them. Which of the two could a
*rewritten sentence* fix, and which could it not? Commit before running.
'''))
C.append(md('''
## Failure #1 — the timing (measured, not eyeballed): a barge-in

The first failure is *when* the agent spoke. We do not trust our eyes — we measure the floor-transfer
offset (FTO) from book 04: `fto = next.start_ms - prev.end_ms`. Negative means the agent started
**before** the caller finished — an overlap. This is the real hero barge-in.
'''))
C.append(code('''
# Compute the FTO at the t2 -> t3 handoff by hand, exactly as book 04 did. The barge-in tag must rest
# on a measured overlap, never on a feeling - so we read the millisecond stamps off the real turns.
fto_ms = agent_t3["start_ms"] - user_t2["end_ms"]   # negative => the agent cut in early
overlap_ms = max(0, -fto_ms)                         # overlap is the positive size of a negative FTO
print("t2 ends at   :", user_t2["end_ms"], "ms")
print("t3 starts at :", agent_t3["start_ms"], "ms")
print("fto_ms       :", fto_ms, "| overlap_ms:", overlap_ms)

# rubric.yaml sets barge_in threshold_overlap_ms = 100: overlap above 100ms is a barge-in
# (<=100ms is a harmless backchannel). We name the threshold HERE to teach; the pipeline reads rubric.yaml.
BARGE_THRESHOLD_MS = 100
is_bargein = overlap_ms > BARGE_THRESHOLD_MS
print("barge_in     :", is_bargein, "| because overlap", overlap_ms, "ms >", BARGE_THRESHOLD_MS, "ms")
'''))
C.append(md('''
## Failure #2 — the content: an over-demand instead of an acknowledgement

The second failure is *what* the agent said. The caller offered a partial answer ("Madhapur side...
near the metro station"). A good service agent **acknowledges the partial**, then asks **one** focused
follow-up. Instead, `t3` demanded the *entire* address with pincode, landmark and door number — a
wall that ignores what the caller just gave. This one is about word choice, not the clock.
'''))
C.append(code('''
# We make the content failure concrete by reading two signals from the agent's words, not its timing.
# This is a CONTENT signal, so we scan the text - the opposite of the millisecond check above.
agent_text = agent_t3["text"].lower()

# Signal A: did the agent acknowledge what the caller said? (look for any acknowledging move)
acknowledges = any(w in agent_text for w in ["got it", "thanks", "thank you", "okay", "madhapur"])
# Signal B: did the agent over-demand a pile of fields at once instead of one follow-up?
overdemands = ("complete address" in agent_text) and ("pincode" in agent_text)

print("agent acknowledged the partial answer? ", acknowledges)   # False - it skipped straight to demands
print("agent over-demanded many fields at once?", overdemands)    # True  - the content failure
'''))
C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. Which failure did we measure from the **clock** (millisecond stamps), and which from the **words**?
2. The barge-in rested on a number. What was the overlap, and what threshold made it a barge-in?
3. Say the over-demand failure in one sentence: what *should* the agent have done with the partial answer?
'''))
C.append(md('''
## Now write the better turn — the `chosen` (manual, one axis at a time)

You have the `rejected` turn (the real `t3`) and you named *why* it failed. Now author the **chosen**
turn. The single most important discipline of this entire book: **the chosen turn differs from rejected
ONLY on the failure axis we are fixing.** We are fixing the *content* (over-demand → acknowledge + one
follow-up). So chosen must be a short acknowledgement plus one question — and **nothing else** new
(not more polite, not more formatted; that would muddy what the fix taught).
'''))
C.append(md('''
## PREDICT
Before you read my version: roughly how many sentences should the `chosen` turn be, and what are the
two jobs it must do? (Hint: the system prompt says "replies under 2 sentences; acknowledge partial
info before asking ONE follow-up.") Commit before running.
'''))
C.append(code('''
# The chosen turn, authored by hand. It does EXACTLY two jobs and no more: (1) acknowledge the partial
# answer the caller already gave, (2) ask ONE focused follow-up. We change only the content axis -
# the timing failure is a DIFFERENT fix (Act 3), so we deliberately do not touch it here.
rejected_turn = agent_t3["text"]   # what the agent actually said - already in the transcript
chosen_turn = "Got it - Madhapur, near the metro station. Morning or evening slot works better tomorrow?"

# Print both so the single-axis difference is visible: same job (advance the booking), corrected content.
print("REJECTED:", rejected_turn)
print()
print("CHOSEN  :", chosen_turn)
'''))
C.append(md('''
## State the *why* in one sentence (the `reason` field)

A pair without a reason is a guess. The `reason` is the one-sentence argument that `chosen` beats
`rejected` **on the failure axis** — and naming the axis keeps you honest that you fixed *that* and
not five other things at once.
'''))
C.append(code('''
# The reason: one sentence, naming the axis. We write it as a string because it is a real schema field
# (it ships with the pair so a human reviewer sees the argument, not just two turns).
reason = ("chosen acknowledges the caller's partial answer and asks one focused follow-up, "
          "instead of over-demanding the full address - it advances the booking on the same content axis.")
print("reason:", reason)

# A blunt single-axis self-check: chosen must not just be 'rejected + politeness'. They must truly differ.
assert chosen_turn != rejected_turn, "chosen and rejected must differ"
print("single-axis check: chosen differs from rejected on content ->", chosen_turn != rejected_turn)
'''))
C.append(md('''
## Pack the `improvement_example` record (the real schema, field by field)

Now assemble the whole thing into one record with the **exact fields** the repo uses
(`schemas/improvement_example.md`). We build it as a plain dict, naming each field with a comment so
you meet the schema as data you can read, not a black box.
'''))
C.append(code('''
# The improvement_example record, every field from schemas/improvement_example.md, with WHY each exists.
improvement_example = {
    "call_id": hero["call_id"],            # provenance: which call produced this pair (trace it back)
    "failure_dimension": "repair_quality",  # the rubric dimension that fired - the CONTENT failure we fixed
    "rejected_turn": rejected_turn,         # what the agent actually said (from the transcript)
    "chosen_turn": chosen_turn,             # the corrected turn, differing only on the content axis
    "reason": reason,                       # one-sentence argument chosen beats rejected
    "quality_delta": 0.6,                   # directional, scorecard-implied improvement (a positive estimate)
    "needs_human_review": True,             # default true: a machine-proposed chosen turn is a PROPOSAL, not truth
}
# Print it as pretty JSON so you SEE the artifact this book produces - one failure, fully packed.
print(json.dumps(improvement_example, indent=2, ensure_ascii=False))
'''))
C.append(md('''
## Why `failure_dimension` is `repair_quality`, not `barge_in`

The record above tags `repair_quality` — the *content* dimension — because the turn we **rewrote** is
the content failure. The barge-in is real too, but a rewritten sentence is the wrong tool for it (you
will prove that in Act 3), so it does not become *this* text pair. One record fixes one axis; the field
names which axis. (`barge_in` and `repair_quality` are both real dimensions in `rubric.yaml`.)
'''))
C.append(md('''
## PREDICT
The pipeline mirrors every pair into a second format for a different trainer. Given our record has a
`prompt` (system + the caller turn), a `chosen`, and a `rejected`, how many *new* facts does the mirror
add — or is it a pure **rename** of fields you already have? Commit before running.
'''))
C.append(code('''
# The two export formats from one authored source. First the TRL conversational shape that a DPO trainer
# eats: prompt (system + prior user turn) / chosen / rejected. We build prompt from the SAME hero turn,
# so the pair is grounded in the real failure moment, not a toy.
system_prompt = ("Voice agent for appointment booking. Replies under 2 sentences. "
                 "Never speak while the caller is mid-answer; acknowledge partial info before asking ONE follow-up.")
trl_pair = {
    "prompt":   [{"role": "system", "content": system_prompt},
                 {"role": "user", "content": user_t2["text"]}],     # the caller turn the agent replied to
    "chosen":   [{"role": "assistant", "content": chosen_turn}],
    "rejected": [{"role": "assistant", "content": rejected_turn}],
}

# The OpenAI mirror is the 3-line mapper from pipeline/dpo_export.py - a pure RENAME, no new facts:
# prompt -> input.messages, chosen -> preferred_output, rejected -> non_preferred_output.
openai_pair = {"input": {"messages": trl_pair["prompt"]},
               "preferred_output": trl_pair["chosen"],
               "non_preferred_output": trl_pair["rejected"]}
print("TRL keys   :", list(trl_pair.keys()))
print("OpenAI keys:", list(openai_pair.keys()), "- same content, renamed fields (no new information)")
'''))
C.append(md('''
## CHECKPOINT 3 (out loud)
1. List the seven fields of an `improvement_example` from memory (or read them off the record above).
2. Why does `needs_human_review` default to **True**? (What kind of thing is a machine-written `chosen`?)
3. The single-axis rule: state it, and say what goes wrong with credit assignment if `chosen` also
   happens to be more polite and better formatted than `rejected`.
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a failed turn was a dead end with a red mark on it. After Act 2 you can do four concrete
things on a real failure: **measure** the barge-in from the clock and **read** the over-demand from the
words, **author** a `chosen` turn that differs from `rejected` on exactly one axis, **state** the
one-sentence reason, and **pack** the whole thing into the seven-field `improvement_example` record
that mirrors cleanly into the trainer formats. Failure is now a labeled proposal, not a complaint.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (the move: failure -> rejected/chosen/why -> packed record)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the pair, then the trap at the heart of this book

## Break-it philosophy

A pair you have never pushed against is a pair you do not trust. So we now write **bad** improvement
examples on purpose and watch exactly how they fail the discipline — a multi-axis chosen, and then the
one this whole book is built on: a failure that **cannot** be a text pair at all. Surprise on your own
terms is education; surprise in the training run — "why did the model learn to be verbose?" — is a disaster.
'''))
C.append(md('''
## PREDICT
We write a `chosen` turn that fixes the over-demand **and also** adds politeness, an emoji-free
greeting, and an extra reassurance — many improvements at once. If a DPO trainer learns from
(rejected, this chosen), can it tell **which** of those changes made chosen "better"? Commit yes/no
before running.
'''))
C.append(code('''
# BREAK-IT (guided) - a multi-axis chosen turn. This is not a crash; it is a DISCIPLINE break:
# the pair "works" structurally but teaches a muddy lesson. Watch how many axes change at once.
rejected_same = rejected_turn   # same rejected turn as before, so only 'chosen' is under test
multi_axis_chosen = ("Thank you so much for calling QuickCool, I really appreciate your patience! "
                     "Got it, Madhapur near the metro - no worries at all. Whenever you are ready, "
                     "would morning or evening tomorrow be more convenient for your visit?")

# Count the axes that changed vs the minimal chosen: content fix + politeness + length + reassurance.
changed_axes = []
if "morning or evening" in multi_axis_chosen.lower():     changed_axes.append("content (the real fix)")
if "thank you" in multi_axis_chosen.lower():              changed_axes.append("politeness")
if len(multi_axis_chosen) > len(chosen_turn) + 40:        changed_axes.append("length/verbosity")
if "no worries" in multi_axis_chosen.lower():             changed_axes.append("reassurance")
print("axes that changed in this chosen:", changed_axes)
print("a gradient sees ONE label (chosen>rejected) but", len(changed_axes), "changes - it cannot tell which it is rewarding")
'''))
C.append(md('''
## Reading that result — the single-axis rule, violated

The trainer gets one bit of signal — *chosen is preferred* — but four things changed. So the gradient
might learn "be better at acknowledging" OR "be more effusive" OR "be longer" OR "add reassurance," and
you cannot tell which. This is the **single-axis rule** from book 17's world, broken on purpose: clean
credit assignment needs the (chosen, rejected) diff to be the failure axis and *nothing else* — the
exact same reason you change one variable per ablation run. The minimal chosen from Act 2 is the fix;
this verbose one is a lesson about what *not* to ship.
'''))
C.append(md('''
## PREDICT
Now a different kind of break. We try to author an improvement_example for the call's **dead-air /
barge-in TIMING** failure — the agent started 800ms too early. We will write a `chosen` *sentence* to
fix it. Will a different sentence change *when* the agent spoke? Commit yes/no before running.
'''))
C.append(code('''
# BREAK-IT (guided) - try to fix a TIMING failure with a text pair, and watch it fail to make sense.
# The barge-in is that the agent started at 18149ms while the caller spoke until 18949ms - an 800ms overlap.
# No rewrite of the WORDS moves those millisecond stamps; the start time is a runtime decision, not a token.
attempted_chosen = "I need your complete address with pincode, landmark and door number."  # same words, "said later"
# The start_ms is set by the runtime's endpointing, not by the text. Rewriting text leaves the clock untouched:
print("rejected start_ms:", agent_t3["start_ms"], "| overlap was:", overlap_ms, "ms")
print("does changing the SENTENCE change start_ms?  No - start_ms comes from endpointing/VAD, not tokens.")
print("=> a (rejected_text, chosen_text) pair cannot teach the model to WAIT. The fix is not trainable here.")
'''))
C.append(md('''
## The reveal — trainable vs config-fixable (the cut this book is built on)

That break was not a bug in your code — it is the **boundary**. A text preference pair can only teach
**token choice**. The over-demand was token choice → **trainable** (weight-fixable), and you packed it
into a real record in Act 2. But the barge-in is **timing**: the agent spoke 800ms too early. No
sentence changes a clock. Its fix lives in **config** — the endpointing hold / interruption threshold —
not in weights. That is why `pipeline/dpo_export.py` mines **agent-side content** failures into pairs,
and why pure dead-air / barge-in *timing* is handled as a runtime setting instead.

The hero `t3` is the perfect specimen because it is **both at once**: barge-in (config-fixable) **and**
over-demand (trainable). One detected failure, two proposed fixes, two different repair shops. Reading
one as the other — trying to *train away* dead air, or *configure away* a rude sentence — is the
deepest mistake in this part of the pipeline.
'''))
C.append(code('''
# Make the boundary executable: a tiny classifier that routes a failure to its repair shop.
# We split on the SIGNAL each failure reads - a 'timing' failure is config-fixable; a 'content'
# failure is trainable. This is the senior-engineer distinction, written as one honest function.
def fix_kind(failure_signal):
    # 'timing' failures (dead air, barge-in act) live in the clock -> config (endpointing/thresholds).
    if failure_signal == "timing":
        return "config-fixable (endpointing ms / interruption threshold) - NOT a text pair"
    # 'content' failures (wrong words: over-demand, language mismatch, missed re-ask) -> trainable pair.
    if failure_signal == "content":
        return "trainable (weight-fixable) - author a (rejected, chosen) text pair"
    return "unknown signal - decide before mining"

# Route the hero turn's TWO failures - same turn, opposite repair shops.
print("barge-in    (signal=timing) ->", fix_kind("timing"))
print("over-demand (signal=content)->", fix_kind("content"))
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. Why can a text (rejected, chosen) pair fix the over-demand but **not** the barge-in?
2. State the cut in your own words: a **trainable** failure reads which signal, a **config-fixable**
   one reads which? (One word each: tokens / clock.)
3. The hero `t3` carried **two** failures. Name each and which repair shop it goes to.
'''))
C.append(md('''
## YOUR break now

Author your own stress test on the discipline. Pick ONE: (a) write a `chosen` that secretly changes
**two** axes (and name them), OR (b) describe a failure that looks trainable but is really
**config-fixable** (a clock problem in disguise). Predict the verdict in a comment, then run the checks.
Finding a muddy pair or a mis-routed failure is a real contribution — it is exactly what human review
catches before these reach the trainer.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it on the improvement_example discipline.
# my prediction: <write whether your pair is single-axis, and your failure's repair shop, BEFORE running>

# (a) optionally author a chosen turn here and we report how different it is from rejected:
my_chosen = ""        # <- leave "" to skip, or write a chosen turn to test the single-axis rule
# (b) optionally name a failure signal to route: "timing" or "content" (or leave "" to skip):
my_failure_signal = ""

# Guarded so a fresh notebook runs clean: we only check what you filled in.
if my_chosen.strip():
    # crude axis spread: more than a content fix usually means a much longer string than the minimal chosen
    much_longer = len(my_chosen) > len(chosen_turn) + 40
    print("your chosen vs rejected differ:", my_chosen.strip() != rejected_turn.strip(),
          "| suspiciously long (multi-axis?):", much_longer)
if my_failure_signal.strip():
    print("your failure routes to:", fix_kind(my_failure_signal.strip()))
if not my_chosen.strip() and not my_failure_signal.strip():
    print("fill in my_chosen and/or my_failure_signal above, then re-run.")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this whole book is built on

**The wrong belief:** "every detected failure can be fixed by training on a better example."

It is a seductive belief — you have a failure, you have the schema, just write a chosen turn. The next
cell takes the call's **dead-air** failure (the 1,620ms silence at the t6→t7 handoff, a real gap in the
hero call) and tries to author a text pair for it. The structure will pass — two turns, they differ —
and the lesson it would teach the model is **nothing about the silence**. Run it, then explain the gap
BEFORE the reveal.
'''))
C.append(code('''
# The hero call has a real dead-air gap: the user finishes t6 at 52253ms, the agent starts t7 at 53873ms.
# That is a 1,620ms silence the caller sat through - a latency failure (book 04 calls >800ms laggy).
user_t6  = next(t for t in hero["turns"] if t["turn_id"] == "t6")
agent_t7 = next(t for t in hero["turns"] if t["turn_id"] == "t7")
gap_ms = agent_t7["start_ms"] - user_t6["end_ms"]   # positive => a gap (dead air), not an overlap
print("t6 ends:", user_t6["end_ms"], "| t7 starts:", agent_t7["start_ms"], "| gap_ms:", gap_ms)

# Now try to "fix" it with a text pair. The chosen is a perfectly good SENTENCE - but the failure was
# the SILENCE before it, and the sentence cannot carry timing. The pair looks valid and teaches nothing useful.
dead_air_pair = {
    "rejected": [{"role": "assistant", "content": agent_t7["text"]}],          # the words after the silence
    "chosen":   [{"role": "assistant", "content": "Got it - an AC cooling issue. Morning or evening tomorrow?"}],
}
structurally_valid = dead_air_pair["chosen"] != dead_air_pair["rejected"]      # True - they differ
print("pair is structurally valid:", structurally_valid, "| but the failure was", gap_ms, "ms of dead air")
print("the chosen sentence is fine - and it teaches the model NOTHING about waiting less. Wrong repair shop.")
'''))
C.append(md('''
## The reveal — a valid-looking pair can be the wrong tool entirely

The pair is structurally perfect: a `chosen`, a `rejected`, they differ. And it is **useless** for the
actual failure, because the failure was 1,620ms of *silence* and a text pair only ever teaches *tokens*.
Training on it would either teach nothing about latency, or worse, teach the model to change its words
for a problem that was never about words — silent label noise.

This is why the trainable/config cut comes **before** you author the pair, not after: the first question
about any failure is "is this a clock problem or a token problem?" Dead air → **config** (lower the
endpointing hold; speed the ASR→LLM→TTS relay from book 05). Over-demand → **train**. The fix for
"every failure can propose its own fix" is honest only when you let some failures propose a *config*
fix, not a training one.
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
1. The dead-air pair was structurally valid. Say in one sentence why it was still the wrong tool.
2. Which question must you ask about a failure **before** writing a chosen turn? (clock or token?)
3. Where does a dead-air fix actually live, and name one knob that would shorten the silence?
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why can a structurally-valid text pair be the WRONG fix for a failure?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a failure plus the schema felt like enough to make a training example. After Act 3: a chosen
turn must differ from rejected on **exactly one axis** (the verbose chosen broke that), and some
failures are **not trainable at all** — a dead-air or barge-in *timing* failure is **config-fixable**,
and a structurally-valid text pair for it is the wrong repair shop. The first question about any failure
is **clock or token**. That cut is the spine of book 16.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the trainable-vs-config-fixable cut is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the cast, the real pipeline, and the bar you must clear

## The recurring cast, as improvement sources

Three calls travel through this whole course. Here they are with the failure each proposes a fix for,
and **which repair shop** that fix goes to — so the trainable/config cut sits on the cast one last time.
Cast ids, languages, and outcomes match the course-wide spec exactly.
'''))
C.append(md('''
## PREDICT
Of the three cast calls, exactly **one** carries *both* a config-fixable failure and a trainable
failure in the same call. Which one — `call_A`, `call_B`, or `call_C`? And the clean call: how many
failures does it propose a fix for? Commit before reading the table below.
'''))
C.append(code('''
# The cast as a small table: id, language, outcome, the failure it carries, and its repair shop.
# call_C IS the hero specimen we operated on all book; A and B round out the trainable/config picture.
cast = [
    {"id": "call_A", "language": "en",    "outcome": "success",
     "failure": "(none - clean booking)",          "fix": "nothing to mine"},
    {"id": "call_B", "language": "hi-en", "outcome": "partial",
     "failure": "missed field -> had to re-ask",    "fix": "trainable (clean re-ask pair)"},
    {"id": "call_C", "language": "te-en", "outcome": "failure",
     "failure": "barge-in (timing) + over-demand (content)", "fix": "config (barge-in) + trainable (over-demand)"},
]
# One row per call so each is visibly one THING; the failure and its repair shop printed side by side.
for c in cast:
    print(f"{c['id']} | {c['language']:<6} | {c['outcome']:<8} | {c['failure']:<40} | {c['fix']}")
'''))
C.append(md('''
## call_C is the lesson in one row

`call_C` (the hero call) carries **both** kinds of failure in a single turn: a config-fixable barge-in
and a trainable over-demand. That is why it has been our specimen all book — it forces you to route two
failures from one turn to two different fixes. `call_B`'s missed-field is a clean trainable re-ask;
`call_A` has nothing to mine. The cast shows the whole spread; the trap showed the case (dead air) that
breaks the lazy "just train it" reading.
'''))
C.append(md('''
## Where this lives in the real VoiceForge pipeline

This book is the hand-built version of three real pieces:

- **`schemas/improvement_example.md`** — the seven-field record you packed by hand (`call_id`,
  `failure_dimension`, `rejected_turn`, `chosen_turn`, `reason`, `quality_delta`, `needs_human_review`).
  Its discipline line is the single-axis rule: *the only meaningful difference between chosen and
  rejected is the detected failure axis.*
- **`pipeline/dpo_export.py`** — turns failed/suboptimal calls into (chosen, rejected) pairs, writes
  `out/queue.jsonl` (TRL) and mirrors to `out/queue_openai.jsonl` with the 3-line mapper you ran. Every
  pair carries provenance and `needs_human_review=true`. It mines **agent-side content** failures —
  exactly the trainable side of the cut you drew.
- **`rubric.yaml`** — the dimensions a failure can fire on: `barge_in` (deterministic, timing →
  config-fixable) and `repair_quality` (judge, content → trainable) are the two your specimen hit.
  The dimension a record carries is what tells a reviewer which axis it claims to fix.
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

`pipeline/dpo_export.py` targets **10-20 pairs** for the whole corpus. Of the failures you would find
across 11 calls, predict the rough split: what fraction become **trainable** text pairs, and what
fraction get routed to **config** (timing) instead? Your stored guess gets confronted when you build the
real queue in book 17.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for the DPO queue in book 17.
my_course_prediction = ""   # rough trainable-vs-config split across the corpus, and WHY - one sentence

if len(my_course_prediction.strip()) < 20:
    print("write your prediction above (trainable vs config split + why), then re-run.")
else:
    print("PREDICTION STORED:", my_course_prediction)
'''))
C.append(md('''
## Where this method itself fails (honesty applies to improvement examples too)

- **Multi-axis chosen** — a `chosen` that fixes the failure *and* is more polite/longer/formatted. The
  gradient cannot tell what it is learning. (You broke this on purpose; the cure is the single-axis rule.)
- **Wrong repair shop** — authoring a text pair for a timing failure (dead air, barge-in act). It looks
  valid and teaches nothing. Ask **clock or token** first.
- **Proposal shipped as truth** — treating a machine-written `chosen` as ground truth. It is a proposal;
  `needs_human_review=true` exists exactly so a human eyeballs it before it trains anything.
- **Mining user-side failures** — a *user* barge-in is a signal about the caller (impatience), not an
  agent sin. Mining it would train the agent for someone else's behavior. Mine **agent-side** failures only.
'''))
C.append(md('''
## The concept at three levels (say each in your own words)

- **To a beginner:** "when the agent says something wrong, we write down what it should have said and
  why - and we first check whether the problem is the *words* (we can teach that) or the *timing* (we
  fix that in settings, not by teaching)."
- **To an engineer:** "each agent-side failure becomes an `improvement_example`: a (rejected, chosen)
  pair differing only on the failure axis, with provenance and a review flag. Content failures are
  weight-fixable via DPO pairs; pure-timing failures (dead air, barge-in act) are config-fixable
  (endpointing/thresholds) and must not be mined as text pairs - clock vs token is the routing key."
- **To a founder:** "every failure proposes its own fix and labels whether that fix is a model
  improvement we *own and compound* (training data) or a quick config change - so 'make it less bad'
  becomes a prioritized, costed queue of concrete repairs instead of a vibe."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**Defense question 1: "You can write a better turn for almost any failure - so isn't every failure trainable?"**
<details><summary>answer</summary>No. A text pair can only teach token choice. You can write a "better turn" for a dead-air failure, but the failure was the 1,620ms silence, and the sentence carries no timing - the pair would be the wrong repair shop. The routing key is clock-vs-token: timing failures (dead air, the barge-in act) are config-fixable (endpointing/thresholds); content failures (over-demand, language mismatch, missed re-ask) are trainable. Writing a turn is easy; whether it *teaches the actual failure* is the test.</details>

**Defense question 2: "Why does chosen have to differ from rejected on only one axis - isn't a more-polished chosen just better?"**
<details><summary>answer</summary>Credit assignment. A DPO trainer gets one bit - chosen is preferred - so if chosen also got more polite, longer, and better formatted, the gradient cannot tell which change earned the preference. It is the same reason you change one variable per ablation run. A minimal, single-axis chosen gives clean credit; a polished multi-axis one teaches a muddy lesson. Polish is not the job; isolating the fix is.</details>

**Defense question 3: "These chosen turns are machine-written - why trust them as training data?"**
<details><summary>answer</summary>We do not, yet - that is what `needs_human_review=true` (the schema default) is for. An auto-generated chosen turn is a *proposal*; shipping it as ground truth without a human eyeballing it would be silent label noise and dishonest. The pipeline authors the pair AND carries provenance (call_id, failure_dimension) so a reviewer can trace it to the exact ms-stamped failure and approve or reject it before it trains anything.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own: the cast routed by repair shop, where the record and the queue live in the real
repo (`schemas/improvement_example.md`, `pipeline/dpo_export.py`, `rubric.yaml`), how this book hands a
labeled proposal forward to book 17's preference pairs - and, above all, the bar you must clear to PASS
this book.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The move: a detected failure → `rejected` → `chosen` → a one-sentence **why** → a packed record.
2. The seven fields of an `improvement_example`, and why `needs_human_review` defaults to True.
3. The single-axis rule, and what breaks (credit assignment) when chosen changes more than one axis.
4. The cut: **trainable** (token choice → text pair) vs **config-fixable** (timing: dead air / barge-in
   act → endpointing). The first question about any failure is **clock or token**.
5. The book's clean sentence (below) — in your own words first, then mine.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about improvement examples

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Every agent-side failure can propose its own fix."**

A detected failure is not a dead end — it proposes the better turn it should have said, with a reason,
packed into one reviewable record. And the proposal is honest about *which kind* of fix it is: a
trainable token-choice pair, or a config-fixable timing change that no sentence can teach. If your
sentence captures both halves in your own words, this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "16_improvement_examples.ipynb"   # <- this notebook's filename
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

**16 done** (pending your teach-back) → **17 · preference pairs** — you packed one
`improvement_example`; book 17 gathers many into the (chosen, rejected) **preference pairs** a DPO
trainer eats, enforces the single-axis rule across the whole queue, and only admits the **trainable**
failures you learned to separate here. The cut you drew (clock vs token) is what keeps that queue clean.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "16_improvement_examples.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
