#!/usr/bin/env python3
# Builds 17_preference_pairs.ipynb — VoiceForge University book 17.
# The ONE atomic concept: chosen vs rejected, and the SINGLE-AXIS DIFF RULE — a clean pair
# changes exactly one thing (the detected failure axis) and nothing else, like an ablation.
# Same four-act skeleton + audit markers as build_P00.py / build_07.py.
# Rerun: .venv/bin/python notebooks/build_17.py
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
# 17 · Preference pairs

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Read a **preference pair** — the three-part shape `prompt` / `chosen` / `rejected` — and say
   what each part is for (the situation, the better reply, the worse reply)
2. State and apply the **single-axis diff rule**: a clean pair changes *exactly one thing* — the
   detected failure axis — and holds everything else fixed (it is an ablation, not a rewrite)
3. **Author a pair by hand** from the real hero failure (the 800ms barge-in at 0:18) so the only
   difference between `chosen` and `rejected` is the over-talk / ignored-partial axis
4. Catch a **bad multi-axis pair** the way you would catch a confounded experiment — and explain
   precisely why it teaches confusion instead of one lesson

Topic stays small on purpose: one failed turn, two replies, one axis. The *discipline of changing
one variable* is the whole point — and it is the same change-one-thing rule you met in P00.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits on the ladder)

`16 · improvement examples  →  THIS · preference pairs  →  18 · DPO`

Book 16 taught you to take a detected failure and write down the **better** turn — a single
improved example ("here is what the agent *should* have said"). That is one half of a teaching
signal. But a model cannot learn "better" from a good example alone; *better than what?* The
contrast is missing. This book supplies the other half: we pin the improved turn (`chosen`)
**against** the actual bad turn (`rejected`) on the very same prompt, so the data carries a
*direction*. Book 18 (DPO) is the training method that consumes exactly these pairs — it nudges
the model toward `chosen` and away from `rejected`. No clean pairs here → DPO there learns the
wrong contrast. This book is where the contrast is made honest.
'''))
C.append(md('''
## 3 — Baby intuition

Imagine teaching someone to salt soup. You could hand them a bowl and say "this is good." They
taste it — but good *compared to what*? They learn almost nothing. Now hand them **two** bowls
from the same pot: one you salted right, one you over-salted, identical in every other way.
One sip of each and the lesson lands — *that* is what too much salt tastes like. The teaching is
in the **contrast**, and the contrast only teaches cleanly because the two bowls differ in
**one thing**: the salt.

A preference pair is those two bowls. Same prompt (same pot), a `chosen` reply and a `rejected`
reply that differ on **one axis** — the thing that actually went wrong. If the two bowls also
differed in temperature, herbs, and broth, the taster could not tell which difference to learn
from. So the craft of a pair is ruthless sameness everywhere except the one axis under test.
'''))
C.append(md('''
## 4 — The formal version

A **preference pair** is three parts. Keep them in separate boxes:

| part | what it is | in our hero case |
|---|---|---|
| `prompt` | the situation the agent faced (system instructions + the conversation up to the bad turn) | the booking system prompt + the caller's half-given Madhapur locality |
| `chosen` | the reply we *prefer* — the corrected turn | confirm the partial locality, ask one next thing |
| `rejected` | the reply the agent *actually* gave — the worse one | demand the full address with pincode and door number |

The rule that gives this book its spine — the **single-axis diff rule**:

> Between `chosen` and `rejected`, the **only** meaningful difference is the **detected failure
> axis**. Over-talk → a shorter turn. Ignored hesitation → wait + clarify. Language mismatch →
> reply in-language. Missed field → a clean re-ask. **Nothing else changes.**

This is written verbatim in the real repo at `schemas/improvement_example.md`. It is the exact
discipline of an **ablation**: to learn what one variable does, you change *only* that variable.
'''))
C.append(md('''
## 5 — Why this book exists (a contrast with a direction)

Book 16's improvement example said "do this instead." Useful for a human reading a report. But a
preference-learning method (book 18) does not train on prose advice — it trains on **(prompt,
chosen, rejected)** triples and learns to prefer one completion over another for the same input.
The single number that makes that training trustworthy is **how clean the contrast is**.

If `chosen` is shorter *and* more polite *and* in a different language *and* fixes the address,
the model cannot tell which of those four things you wanted — it might learn "be terse" when you
meant "stop demanding a pincode." A messy pair does not just teach less; it teaches the wrong
lesson with full confidence. So the real pipeline (`pipeline/dpo_export.py`, which writes
`out/queue.jsonl`) is built to emit **one-axis** pairs with provenance, each flagged
`needs_human_review=true` until a person has eyeballed that exactly one thing moved. This book is
the by-hand version of authoring one such pair — and the trained eye for catching a bad one.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What are the **three parts** of a preference pair, and what is each one for?
2. State the **single-axis diff rule** in your own words. What is the one thing allowed to differ
   between `chosen` and `rejected`?
3. Why is a preference *pair* a stronger teaching signal than a single "better" example from
   book 16? (Hint: the word is *contrast* — better *than what*?)
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: training data is a pile of good examples to imitate. After
Act 1 you should hold a sharper picture: the strongest teaching signal is a **contrast with a
direction** — a `chosen`/`rejected` pair on the same `prompt` — and that contrast only teaches
*one* lesson when the two replies differ on exactly *one* axis. Book 16 gave you the better turn;
this book pins it against the worse turn under the single-axis diff rule; book 18 trains on it.

If "a clean pair is an ablation: change one variable, hold the rest fixed" feels like your own
sentence, continue. If `chosen` and `rejected` still feel like "good text vs bad text" with no
rule about *what* may differ, re-read cell 4 — that missing rule is what Act 3 will break.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of the single-axis diff rule. Not mine - yours.
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
# Act 2 — Mechanics: a human pair first, then build one from the hero failure

## Start human: a pair you already have intuitions about

Before any voice-agent data, we make a preference pair about something you can judge with no
training: a reply to "what's a good first programming language?" Two answers to the *same*
question. We will deliberately make them differ on **one axis** — length — so the shape of a pair
is visible before the content gets hard. Raw first; we print the parts before naming anything.
'''))
C.append(md('''
## PREDICT
Below will be two answers to the same question. One is a tight two-sentence reply; the other is
the same advice buried in a long rambling paragraph. Which should be `chosen` and which
`rejected` — and what is the **one axis** on which they differ? Commit before reading the cell.
'''))
C.append(code('''
# A human-judgeable preference pair, built as plain data so the three parts are THINGS we can
# print and inspect. We keep the ADVICE identical in both replies and vary only LENGTH/focus,
# so this first pair already obeys the single-axis diff rule (one axis: verbosity).
human_prompt = "What's a good first programming language?"

# 'chosen' = the reply we prefer: same recommendation, said tightly.
human_chosen = "Python - it reads almost like English and has gentle error messages. Start there."

# 'rejected' = the worse reply: the SAME recommendation, drowned in throat-clearing and tangents.
human_rejected = ("Well, that really depends on so many factors and there are countless opinions "
                  "out there, but if we consider history and the job market and many other things, "
                  "a lot of people might eventually suggest something like Python, possibly.")

# Print the three parts separately so each is visibly one part of the pair (not a wall of text).
print("PROMPT  :", human_prompt)
print("CHOSEN  :", human_chosen)
print("REJECTED:", human_rejected)
'''))
C.append(md('''
## OBSERVE — name the one axis

Both replies recommend Python. The recommendation (the *content*) is held fixed; what differs is
**verbosity** — the `chosen` answer is direct, the `rejected` one buries the same advice in
hedging. One axis moved. If you instead made `chosen` recommend Python *and* `rejected` recommend
JavaScript, you would have changed the content too, and the pair would no longer isolate "be
concise." The next cell measures the axis so the contrast is not a vibe.
'''))
C.append(md('''
## PREDICT
The next cell counts words in each reply (a crude proxy for the verbosity axis). The `chosen`
reply is one tight sentence; the `rejected` one is a long hedge. Predict: roughly how many words
each, and which direction the gap points (which reply is longer)? Commit before running.
'''))
C.append(code('''
# We MEASURE the axis we claim differs, instead of asserting it. Word count is a crude proxy for
# verbosity, but a measured proxy beats an eyeballed one - this is the same 'measure, don't
# eyeball' habit from the timing books. If the axis is 'length', the numbers must move on length.
chosen_words = len(human_chosen.split())     # .split() on whitespace -> a rough token count
rejected_words = len(human_rejected.split())
print("chosen words  :", chosen_words)
print("rejected words:", rejected_words)
# A direction we can teach on: rejected is far longer for the SAME advice -> 'prefer concise'.
print("axis = length; rejected is", rejected_words - chosen_words, "words longer for identical advice")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not memory): in the human pair, what was held *fixed*
between `chosen` and `rejected`, and what single thing was allowed to *differ*?
'''))
C.append(md('''
## Now the real failure — meet the hero call's bad turn

Time to leave toy land. The recurring **hero call** (`data/hero/turns.json`, the te-en appliance
booking, `call_C` in our cast) has a documented failure at the very start: the agent **barges in
800ms early** and then **demands a complete address** while the caller had only managed a partial
locality ("Madhapur side... near the metro station"). That is the failure axis we will build a
pair around. We load the real turns and look at the two that matter — no paraphrase.
'''))
C.append(code('''
# Load the REAL hero call from disk. We resolve the repo root by walking up to the folder that
# holds data/hero, so this runs regardless of the kernel's working directory.
import json
from pathlib import Path
root = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "hero").exists())
hero = json.loads((root / "data" / "hero" / "turns.json").read_text())   # disk text -> dict

# Index turns by id so we can pull the exact two turns the failure lives on (t2 user, t3 agent).
turns_by_id = {t["turn_id"]: t for t in hero["turns"]}
print("call_id     :", hero["call_id"], "| language:", hero["language"], "| profile:", hero["stress_profile"])
print("t2 (user) :", turns_by_id["t2"]["text"])
print("t3 (agent):", turns_by_id["t3"]["text"])
'''))
C.append(md('''
## PREDICT
The user's turn `t2` ends at `18949ms`; the agent's `t3` starts at `18149ms`. Compute
`fto = t3.start_ms - t2.end_ms` in your head. Is it negative (overlap / barge-in) or positive
(gap)? And in one phrase: what is the **failure axis** of `t3` — what did the agent do wrong?
Commit both before running.
'''))
C.append(code('''
# Measure the failure, do not assert it. fto = next.start - prev.end (the FTO core from book 04
# and pipeline/signals.py). A negative FTO means the agent started before the caller finished:
# that overlap IS the barge-in half of the failure; we compute it rather than trust the prose.
t2, t3 = turns_by_id["t2"], turns_by_id["t3"]
fto_ms = t3["start_ms"] - t2["end_ms"]          # negative => agent cut in early
overlap_ms = max(0, -fto_ms)                    # overlap is the positive size of a negative FTO
print("fto_ms:", fto_ms, "| overlap_ms:", overlap_ms)

# rubric.yaml sets barge_in threshold_overlap_ms = 100: above 100ms it is a barge-in, not a
# harmless backchannel. We name the axis from BOTH signals: the overlap AND the over-demand.
BARGE_THRESHOLD_MS = 100
is_barge_in = overlap_ms > BARGE_THRESHOLD_MS
print("is_barge_in:", is_barge_in, "(overlap", overlap_ms, "ms >", BARGE_THRESHOLD_MS, "ms)")
print("failure axis = over-talk: agent barged in AND demanded a full address over a partial answer")
'''))
C.append(md('''
## The prompt half of the pair (the situation, frozen)

A pair's `prompt` is the situation the agent was in — the **system instructions** plus the
**conversation up to the bad turn**. It must be the *same* situation both replies answer, so we
freeze it once and reuse it for `chosen` and `rejected`. We use the real conversational shape from
`schemas/improvement_example.md`: a list of role/content messages (`system`, then `user`).
'''))
C.append(code('''
# Build the prompt half exactly as the real export does: a list of {role, content} messages.
# The system message states the agent's standing instructions; the user message is the caller's
# actual t2 turn. This is FROZEN - both chosen and rejected must answer THIS same situation.
system_msg = ("Voice agent for appliance-service booking. Replies under 2 sentences. "
              "Never speak while the caller is mid-answer.")
prompt = [
    {"role": "system", "content": system_msg},      # the standing rules (note: 'under 2 sentences')
    {"role": "user", "content": turns_by_id["t2"]["text"]},   # the caller's real partial-locality turn
]
# Print the frozen situation so we can see it is the SAME pot both bowls come from.
for m in prompt:
    print(f"[{m['role']}] {m['content']}")
'''))
C.append(md('''
## The rejected half (what the agent really said)

The `rejected` reply is not invented — it is the agent's **actual** turn `t3`, verbatim. Using the
real bad turn (not a strawman we wrote to lose) keeps the pair honest: we are correcting what
truly happened, the way `pipeline/dpo_export.py` pulls `rejected_turn` straight from the trace.
'''))
C.append(code('''
# The rejected completion is the REAL t3 turn, unedited - a list with one assistant message,
# matching the export shape. We take it from the trace, not from imagination, so the pair
# corrects a real failure rather than a convenient one.
rejected = [{"role": "assistant", "content": turns_by_id["t3"]["text"]}]
print("REJECTED:", rejected[0]["content"])
# Sanity: confirm it is literally the agent's t3, so nobody can accuse us of building a strawman.
print("is verbatim t3:", rejected[0]["content"] == turns_by_id["t3"]["text"])
'''))
C.append(md('''
## YOUR TURN — author the chosen half (the heart of the book)

Now you write the **corrected** turn by hand. The single-axis diff rule is your only constraint,
and it is strict: fix **the over-talk / ignored-partial axis and nothing else**. That means —
confirm the partial locality the caller *did* give (Madhapur, near the metro), then ask **one**
short next thing. Do **not** also switch language, do **not** add cheerful padding, do **not**
fix unrelated things. Same situation, one axis moved.
'''))
C.append(code('''
# YOUR TURN - write the chosen (corrected) assistant turn as a single string.
# CONSTRAINT (single-axis diff rule): change ONLY the over-talk axis - acknowledge the partial
# locality the caller gave, then ask ONE next thing. Keep it under 2 sentences (the system rule).
# Do NOT change language, tone-padding, or anything unrelated; that would add a second axis.
my_chosen_turn = ""   # e.g. "Got it - Madhapur, near the metro. What appliance needs servicing?"

# Guard: a fresh notebook (empty string) must still run clean, so we only build the pair once
# you have written a turn. We also nudge if the turn drifts off the one axis we are allowed to move.
if len(my_chosen_turn.strip()) < 15:
    print("write my_chosen_turn above (confirm the partial locality + ask one thing), then re-run.")
else:
    # cheap one-axis check: a good correction should be SHORTER than the over-demanding rejected
    # turn (over-talk -> less talk) and should not introduce a brand-new demand for a pincode.
    shorter = len(my_chosen_turn.split()) < len(turns_by_id["t3"]["text"].split())
    still_demands_pincode = "pincode" in my_chosen_turn.lower()
    print("CHOSEN (yours):", my_chosen_turn)
    print("shorter than rejected:", shorter, "| still demands pincode:", still_demands_pincode)
    if not shorter or still_demands_pincode:
        print("note: a clean fix of the over-talk axis is shorter and drops the pincode demand.")
'''))
C.append(md('''
## A reference chosen turn (read only after writing yours)

Here is one correct `chosen` turn, taken from `schemas/improvement_example.md` itself. Yours does
not need to match it word-for-word — it needs to move the **same one axis**: acknowledge the
partial locality, ask one next thing, drop the full-address demand. We will use this reference
from here on so the notebook runs the same whether or not you filled yours in.
'''))
C.append(code('''
# The reference corrected turn from the schema doc. We fall back to it when yours is unfilled,
# so every downstream cell runs clean on a fresh notebook (the learner-cell guard pattern).
reference_chosen = "Got it - Madhapur, near the metro station. Morning or evening slot work better?"
# Use the learner's turn if they wrote one; otherwise the reference. This keeps the pair real
# AND keeps the notebook executable top-to-bottom before anyone fills the YOUR TURN cell.
chosen_text = my_chosen_turn.strip() if len(my_chosen_turn.strip()) >= 15 else reference_chosen
chosen = [{"role": "assistant", "content": chosen_text}]
print("CHOSEN (in use):", chosen[0]["content"])
'''))
C.append(md('''
## Assemble the whole pair — manual, every part visible

You now have all three parts: the frozen `prompt`, the real `rejected`, and your `chosen`. We
assemble them into the single record the real pipeline writes, **by hand**, so you see the whole
object before any function does it for you. This is the TRL conversational shape from
`schemas/improvement_example.md`: `{"prompt": [...], "chosen": [...], "rejected": [...]}`.
'''))
C.append(code('''
# Assemble the pair as one dict, the same keys pipeline/dpo_export.py writes to out/queue.jsonl.
# We build it literally (no helper yet) so the three-part structure is fully exposed to the eye.
pair = {
    "prompt": prompt,        # the frozen situation (system + user)
    "chosen": chosen,        # the corrected assistant turn (one axis moved)
    "rejected": rejected,    # the real bad assistant turn (verbatim t3)
}
# json.dumps with indent makes the nested structure readable - this is the artifact, pretty-printed.
import json
print(json.dumps(pair, indent=2, ensure_ascii=False))
'''))
C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. Which part of `pair` is the **frozen situation**, which is the **corrected** turn, and which
   is the **real bad** turn?
2. Why did we take `rejected` *verbatim* from the trace instead of writing a worse turn ourselves?
3. Name the single axis your `chosen` turn was allowed to move. What were you forbidden to change?
'''))
C.append(md('''
## Add provenance — a pair without a paper trail is unverifiable

The real schema (`schemas/improvement_example.md`) does not stop at the three text parts. Each
pair carries **provenance and a review flag**: `call_id` (which call produced it),
`failure_dimension` (which rubric dimension fired), a one-sentence `reason`, and
`needs_human_review=true` until a person has checked that exactly one axis moved. We attach those
now, because an unsourced pair is a claim with no receipt.
'''))
C.append(code('''
# Attach the metadata fields from schemas/improvement_example.md. needs_human_review defaults to
# True because the WHOLE safety of preference data is a human confirming the single-axis rule held -
# the export never trusts itself. failure_dimension names which rubric.yaml dimension fired.
pair_record = {
    **pair,
    "call_id": hero["call_id"],            # provenance: which call this came from (hero_001)
    "failure_dimension": "barge_in",       # the rubric dimension that fired (over-talk / overlap)
    "reason": "agent barged in 800ms early and demanded a full address over a partial locality; "
              "chosen confirms the partial and asks one thing",
    "needs_human_review": True,            # stays True until a human eyeballs the one-axis claim
}
# Print just the metadata so the receipt is visible without re-dumping the whole conversation.
for k in ("call_id", "failure_dimension", "reason", "needs_human_review"):
    print(f"{k:<18}: {pair_record[k]}")
'''))
C.append(md('''
## Now — and only now — the function version

You assembled one pair by hand and saw every part. A function is just those steps written once so
they run on a thousand failures. Because you met the parts first, this wrapper is a convenience,
not a mystery — and you can audit every line of it. It takes a prompt, a chosen string, a rejected
string, plus provenance, and returns the same record you built above.
'''))
C.append(code('''
# The pair-builder, collected into one function. Each line is exactly the by-hand assembly above.
# We default needs_human_review=True for the same reason the real exporter does: the pair is a
# claim about a single axis, and only a human can sign off that nothing else moved.
def make_pair(prompt_msgs, chosen_text, rejected_text, call_id, failure_dimension, reason):
    return {
        "prompt": prompt_msgs,                                   # frozen situation, reused as-is
        "chosen": [{"role": "assistant", "content": chosen_text}],     # wrap the corrected turn
        "rejected": [{"role": "assistant", "content": rejected_text}], # wrap the real bad turn
        "call_id": call_id,                                      # provenance travels with the pair
        "failure_dimension": failure_dimension,
        "reason": reason,
        "needs_human_review": True,                             # never auto-trusted
    }
print("make_pair defined")
'''))
C.append(code('''
# Run the function and confirm it reproduces the hand-built record. If it does not, the FUNCTION
# is wrong (or the by-hand version was) - and that gap would be the lesson, exactly as in book 07.
auto_pair = make_pair(prompt, chosen_text, turns_by_id["t3"]["text"],
                      hero["call_id"], "barge_in", pair_record["reason"])
# Compare the parts that must match the hand build; True everywhere means the wrapper is faithful.
print("prompt matches  :", auto_pair["prompt"] == pair_record["prompt"])
print("chosen matches  :", auto_pair["chosen"] == pair_record["chosen"])
print("rejected matches:", auto_pair["rejected"] == pair_record["rejected"])
'''))
C.append(md('''
## Export shape — the same pair, two formats

The real pipeline writes each pair to `out/queue.jsonl` in **TRL conversational** form (the dict
you built), and mirrors it to `out/queue_openai.jsonl` via the 3-line mapper in
`pipeline/dpo_export.py`. The mapper just **renames keys** — it does not change the content. Seeing
both shapes side by side shows that a preference pair is a *structure*, independent of vendor.
'''))
C.append(md('''
## PREDICT
The mapper turns `chosen` into `preferred_output` (just a key rename). Predict: after mapping,
will the `chosen` *text* be byte-for-byte identical under the new key, or could a rename quietly
alter the content? The next cell checks equality — commit to your answer first.
'''))
C.append(code('''
# The 3-line OpenAI mapper from schemas/improvement_example.md: it RENAMES keys, nothing more.
# prompt -> input.messages, chosen -> preferred_output, rejected -> non_preferred_output.
# We show it to prove the pair's MEANING is format-independent; the contrast survives renaming.
openai_pair = {
    "input": {"messages": auto_pair["prompt"]},
    "preferred_output": auto_pair["chosen"],
    "non_preferred_output": auto_pair["rejected"],
}
# The same chosen text must appear under the new key - same content, different envelope.
print("TRL key 'chosen'        ->", auto_pair["chosen"][0]["content"][:40], "...")
print("OpenAI 'preferred_output'->", openai_pair["preferred_output"][0]["content"][:40], "...")
print("same content, renamed key:",
      auto_pair["chosen"] == openai_pair["preferred_output"])
'''))
C.append(md('''
## CHECKPOINT 3 (out loud)
1. The OpenAI mapper is "3 lines." What does it actually *do* to a pair — and what does it
   deliberately **not** do?
2. What does `needs_human_review=True` protect against, given that the export ran with no errors?
3. If `out/queue.jsonl` and `out/queue_openai.jsonl` disagreed on the `chosen` text, which step
   would you suspect — the pair-build or the mapper? Why?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a "preference pair" was a vague phrase. After Act 2 you can do five concrete things: read
the **three parts** of a pair, **freeze a prompt** so both replies answer the same situation, take
`rejected` **verbatim** from a real trace, **author a chosen turn that moves one axis**, and attach
**provenance** so the pair is a receipt and not a rumor. You built one real pair from the hero
failure, by hand, then watched a function reproduce it and a mapper re-envelope it.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (three-part shape / freeze the prompt / one-axis chosen - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: build a BAD multi-axis pair, then the trap at the heart of this book

## Break-it philosophy

You do not understand the single-axis rule until you have *broken* it and felt the damage. So we
now author a deliberately **bad** pair — one whose `chosen` and `rejected` differ on several axes
at once — and diagnose it the way you would diagnose a confounded experiment. Surprise on your own
terms is education; shipping a confounded pair into DPO and wondering why the model got terse and
rude is a disaster you find out about three books from now.
'''))
C.append(md('''
## PREDICT
We are about to write a `chosen` turn for the SAME hero prompt that fixes the address demand
**and also** switches to Telugu **and also** adds a chirpy apology. Against the same `rejected`
t3, **how many axes** will differ between chosen and rejected? And if DPO trained on it, name one
*wrong* lesson it might absorb. Commit both before running.
'''))
C.append(code('''
# BREAK-IT (guided) - a deliberately MULTI-AXIS chosen turn. This is not a crash; it is a subtler
# break: the pair looks fine and exports fine, but it moves THREE axes at once, so any method that
# learns from it cannot tell which difference we wanted. We build it to feel the confound.
bad_chosen_text = ("Ayyo sorry sorry! Meeru cheppindi correct - Madhapur, metro daggara. "
                   "Chala thanks andi, morning or evening manchidi cheppandi please!")
# Axes moved vs the real rejected t3: (1) over-talk fixed, (2) language en->te-en switched,
# (3) tone: gushing apology + padding added. Three changes, one prompt. The contrast is muddy.
bad_pair = make_pair(prompt, bad_chosen_text, turns_by_id["t3"]["text"],
                     hero["call_id"], "barge_in", "fixes address demand (but also changes language and tone)")
print("BAD chosen :", bad_pair["chosen"][0]["content"])
print("rejected   :", bad_pair["rejected"][0]["content"])
'''))
C.append(md('''
## Diagnose it like a confounded experiment

The bad pair *exports* with no error — that is exactly why it is dangerous. To catch it, we do
what we would do for any ablation we suspect is confounded: **list the axes that changed** and
check that only one is the intended failure axis. We measure three concrete signals: length
(over-talk axis), language (a script/word check), and tone-padding (apology words). More than one
moving → the pair is confounded.
'''))
C.append(code('''
# A small confound-detector: for each axis we care about, did it move between rejected and chosen?
# This is the ablation discipline made mechanical - we are not judging 'better', only counting
# how many things differ. A clean pair scores 1 axis moved (the intended one); this one will score 3.
rej_text = bad_pair["rejected"][0]["content"]
cho_text = bad_pair["chosen"][0]["content"]

def axes_moved(rejected_text, chosen_text):
    moved = []
    # axis 1 - over-talk / length: a real fix makes the turn shorter, so length is the intended axis.
    if abs(len(chosen_text.split()) - len(rejected_text.split())) >= 5:
        moved.append("length(over-talk)")
    # axis 2 - language: Telugu-romanization markers absent from the English rejected turn.
    te_markers = ("meeru", "ayyo", "andi", "daggara", "cheppandi", "manchidi")
    if any(w in chosen_text.lower() for w in te_markers):
        moved.append("language")
    # axis 3 - tone padding: gushing apology / thanks that the task did not require.
    pad_markers = ("sorry sorry", "chala thanks", "thanks andi", "please!")
    if any(w in chosen_text.lower() for w in pad_markers):
        moved.append("tone-padding")
    return moved

bad_axes = axes_moved(rej_text, cho_text)
print("axes that moved:", bad_axes, "->", len(bad_axes), "axes")
print("confounded:", len(bad_axes) > 1, "(a clean pair moves exactly 1 axis)")
'''))
C.append(md('''
## Reading that result — why a confounded pair teaches the wrong thing

Three axes moved: length, language, tone. To a preference-learning method, this pair says "prefer
the Telugu, gushing, shorter reply over the English, curt, long one" — as **one** undifferentiated
preference. It cannot know you only cared about the over-talk. So it might learn "always switch to
Telugu" or "always apologize profusely," lessons you never intended, from a pair that looked
perfectly valid and exported without a hiccup. The damage is invisible at authoring time and
expensive at training time. **A pair that moves N axes is N tangled lessons wearing one label.**
'''))
C.append(md('''
## Repair it — back to one axis

The fix is the same as fixing a confounded experiment: hold everything constant except the one
variable under test. We rebuild the `chosen` turn so it fixes **only** the over-talk axis — English
(matching the rejected turn's language), no extra apology, just confirm the partial and ask one
thing. Then we re-run the detector and confirm exactly one axis moves.
'''))
C.append(code('''
# The repaired chosen turn: ONE axis only. Same language as rejected (English), no tone padding,
# just the over-talk fix. We reuse reference_chosen from Act 2 - it was one-axis-clean by design.
clean_pair = make_pair(prompt, reference_chosen, turns_by_id["t3"]["text"],
                       hero["call_id"], "barge_in", "confirms partial locality, asks one thing")
clean_axes = axes_moved(clean_pair["rejected"][0]["content"], clean_pair["chosen"][0]["content"])
print("repaired chosen:", clean_pair["chosen"][0]["content"])
print("axes that moved:", clean_axes, "->", len(clean_axes), "axis")
print("confounded:", len(clean_axes) > 1, "(now exactly one axis - the over-talk fix)")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. The bad pair exported with **no error**. So what exactly made it bad — and why is that more
   dangerous than a pair that crashes?
2. Name the three axes that moved in the bad pair. Which **one** was the intended failure axis?
3. The repair held two things constant that the bad version changed. Which two, and why does
   holding them constant make the lesson clean?
'''))
C.append(md('''
## PREDICT
One more break, a crashing one. A pair-builder must defend against a `chosen` that was never
filled in — a `None` where text should be. `axes_moved` calls `.split()` on the chosen text. If we
hand it `chosen_text = None`, does it **crash loudly** or return a **silently wrong** axis count?
Commit to one before running.
'''))
C.append(code('''
# BREAK-IT (guided) - a null chosen turn, the failure a half-authored pair really produces.
# EXPECTED FAILURE FOR LEARNING - this cell is SUPPOSED to error; read the traceback, do not fix yet.
missing_chosen = None     # <- the damage: nobody wrote the corrected turn
# axes_moved does chosen_text.split(); calling .split() on None makes Python refuse. Watch it.
print("axes for a null chosen:", axes_moved(turns_by_id["t3"]["text"], missing_chosen))
'''))
C.append(md('''
## Reading the error (bottom-up) and the fix

The last line of the traceback names *what* broke:
`AttributeError: 'NoneType' object has no attribute 'split'` — "you asked the chosen text to split
itself, but it was `None`." Walk **upward** to find *where* (the `.split()` inside `axes_moved`).
The fix is a guard at the boundary: a pair with no `chosen` is not "zero axes moved," it is
**not a pair yet** — so we reject it explicitly instead of letting it slip through as valid. A loud
crash was the friendly outcome; the dangerous version would be a confounded pair that *looks* fine.
'''))
C.append(code('''
# The fix: validate the pair BEFORE measuring axes, so a missing chosen is caught as "not a pair"
# rather than crashing mid-measurement or, worse, counting as a clean zero-axis pair.
def validate_pair(chosen_text, rejected_text):
    # an unfilled chosen (None or blank) means the pair is incomplete - reject it, do not measure it.
    if not chosen_text or not chosen_text.strip():
        return "INCOMPLETE: chosen turn is empty - not a pair yet, nothing to teach against"
    if not rejected_text or not rejected_text.strip():
        return "INCOMPLETE: rejected turn is empty - no failure to correct"
    return f"OK: {len(axes_moved(rejected_text, chosen_text))} axis/axes moved"
# Now the null chosen degrades to a clear message instead of a stack trace - graceful, not silent.
print("null chosen   :", validate_pair(None, turns_by_id["t3"]["text"]))
print("real pair      :", validate_pair(reference_chosen, turns_by_id["t3"]["text"]))
'''))
C.append(md('''
## YOUR break now

Author your *own* multi-axis violation. Start from a clean fix of the over-talk axis, then
deliberately smuggle in **one extra** axis (switch language, OR add padding, OR fix an unrelated
field). Predict in a comment how many axes the detector will report, then run it and check. The
skill being built is *catching your own confound* — the exact eye the human review flag depends on.
'''))
C.append(code('''
# YOUR TURN - self-authored multi-axis break. Build a chosen turn that moves MORE than one axis.
# my prediction: <write how many axes you expect axes_moved() to report, and which ones, BEFORE running>

# 1) write a chosen turn that fixes over-talk but ALSO sneaks in a second axis (language OR padding):
my_bad_chosen = "Got it, Madhapur near the metro."   # <- edit me to smuggle in a 2nd axis
# 2) score it against the real rejected t3 and compare the count to your written prediction:
my_axes = axes_moved(turns_by_id["t3"]["text"], my_bad_chosen)
print("your chosen:", my_bad_chosen)
print("axes moved :", my_axes, "->", len(my_axes), "axes")
print("confounded :", len(my_axes) > 1, "(did this match your prediction?)")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this whole book is built on

**The wrong belief:** "as long as `chosen` is genuinely better than `rejected`, the pair is good."

This feels airtight. `chosen` *is* better — so what could be wrong? The next cell builds a pair
where `chosen` is unarguably the better reply *in every way*: it fixes the address demand, it is
warmer, it is shorter, it confirms more. A human would pick it every time. And it is a **bad pair**
for training. Run it, then try to explain why "clearly better" is not the bar BEFORE the reveal.
'''))
C.append(code('''
# A pair whose chosen is BETTER ON EVERY AXIS - and is therefore a bad TRAINING pair.
# Each improvement is real; that is the trap. Multiple good changes at once = multiple entangled
# lessons. We score the axes to show 'better' and 'clean' are different measurements.
better_everything = ("So sorry for cutting in! Madhapur near the metro, perfect. "
                     "You're doing great - shall we say morning or evening for the visit?")
trap_axes = axes_moved(turns_by_id["t3"]["text"], better_everything)
print("chosen (better on every axis):", better_everything)
print("axes moved:", trap_axes, "->", len(trap_axes), "axes")
# The verdict the trap hinges on: humans grade on 'better', training needs 'one axis'. Different bars.
print("a human would prefer it:", True)
print("it is a clean training pair:", len(trap_axes) == 1)
'''))
C.append(md('''
## The reveal — "better" is not the bar; "one axis" is

The `chosen` turn was better in every way a human cares about — and that is precisely what makes it
a **bad** pair. "Better on N axes" hands the training method N preferences fused into one signal;
it cannot recover which one you meant. The bar for a *teaching* pair is not "is chosen better?" (a
human-grading question) but "**do chosen and rejected differ on exactly one axis?**" (an ablation
question). A pair can be clearly-better-to-a-human and useless-or-harmful-to-train-on at the same
time. This is the same shape as P00's deepest trap — *a thing can be valid on one axis (it ran / it
is nicer) and wrong on the axis that matters* — now landed on training data, where it costs the
most. `needs_human_review=true` exists in the schema for exactly this: a person must confirm one
axis, because "it looks better" will pass every automated check.
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
1. State the two different bars: the **human-grading** bar and the **training-pair** bar. Which
   one does a "better on every axis" reply pass, and which does it fail?
2. Why can a pair be *clearly better to a human* and *bad to train on* at the same moment?
3. Connect it back: which P00 trap is this the grown-up version of? (Hint: green cells / valid on
   the wrong axis.)
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why is 'chosen is clearly better' NOT enough for a good pair?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a good pair meant "chosen beats rejected." After Act 3: a multi-axis pair **exports
cleanly and still poisons training** (the dangerous kind of bug - no crash); you can **count the
axes that moved** like checking an experiment for confounds; and the real bar is **exactly one
axis**, not "better." "Clearly better to a human" is a *different measurement* from "clean to train
on," and conflating them is the deepest mistake in preference data. That separation is the spine of
book 17.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the 'better is not the bar, one-axis is' trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the cast, the real pipeline, and the bar you must clear

## One pair per cast member — the failure axis decides the fix

Three calls travel through this whole course. Each failed (or strained) on a *different* axis, so
each yields a pair whose single allowed difference is **its own** axis. Seeing them in one table
makes the discipline concrete: the failure axis is not a style choice — it is *dictated by what
went wrong*, and it is the only thing the pair may move.
'''))
C.append(code('''
# The cast as pairs, one row each. The 'axis' column is the ONLY thing chosen may change vs
# rejected - and it is fixed by the detected failure, matching the course-wide spec (ids/outcomes).
cast_pairs = [
    {"id": "call_A", "language": "en",    "outcome": "success",
     "axis": "(none - clean call, no pair needed)",
     "rejected": "(no failure to correct)",
     "chosen":   "(no failure to correct)"},
    {"id": "call_B", "language": "hi-en", "outcome": "partial",
     "axis": "ignored-hesitation -> wait + clarify",
     "rejected": "Please repeat your phone number fully right now.",
     "chosen":   "No rush - whenever you're ready, the number again slowly?"},
    {"id": "call_C", "language": "te-en", "outcome": "failure",
     "axis": "over-talk -> confirm partial, ask one thing",
     "rejected": "I need your complete address with pincode, landmark and door number.",
     "chosen":   "Got it - Madhapur, near the metro. Morning or evening slot work better?"},
]
# One print per cast member so each pair is visibly one THING; the axis is named explicitly.
for c in cast_pairs:
    print(f"{c['id']} | {c['language']:<6} | {c['outcome']:<8} | axis: {c['axis']}")
'''))
C.append(md('''
## call_A is the lesson in one row

`call_A` is a clean success — and it produces **no pair at all**. That is correct, not a gap:
preference pairs come from *detected failures*. No failure → no axis to move → nothing to teach
against. A pipeline that manufactured a pair for a perfect call would be inventing a problem, the
same way book 07's tagger must stay quiet on good calls. Pairs are mined from what went wrong.
'''))
C.append(md('''
## Where this lives in the real VoiceForge pipeline

This book is the hand-built version of three real pieces:

- **`schemas/improvement_example.md`** — the contract you followed: the `prompt`/`chosen`/`rejected`
  shape, the fields (`call_id`, `failure_dimension`, `reason`, `needs_human_review`), and the
  single-axis rule stated in its own words ("the ONLY meaningful difference is the failure axis").
- **`pipeline/dpo_export.py`** — turns detected failures into pairs, writes `out/queue.jsonl` (TRL
  conversational) and mirrors to `out/queue_openai.jsonl` via the 3-line key-rename mapper you ran.
  Target 10–20 pairs, each with provenance and `needs_human_review=true`.
- **`rubric.yaml` + `pipeline/signals.py`** — name and *measure* the failure axis. The `barge_in`
  dimension (threshold 100ms) and the FTO core gave you the 800ms overlap that justified call_C's
  axis. You did not guess the axis; you measured it.
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

Book 18 (DPO) will train on `out/queue.jsonl`. Predict: if half the pairs in that file were
*confounded* (chosen better on 3 axes each), what would you expect to go wrong with the trained
agent — and would the **training run itself** show any error to warn you? Your stored guess gets
confronted when you train in book 18.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for the DPO training in book 18.
my_course_prediction = ""   # what breaks if pairs are confounded, AND whether training shows an error - and why

if len(my_course_prediction.strip()) < 20:
    print("write your prediction above (what breaks + does training warn you), then re-run.")
else:
    print("PREDICTION STORED:", my_course_prediction)
'''))
C.append(md('''
## Where this method itself fails (honesty applies to pairs too)

- **Strawman rejected** — writing a deliberately awful `rejected` the agent never actually said, to
  make `chosen` look good. The pair then teaches against a failure that does not occur. Take
  `rejected` from the real trace.
- **Multi-axis chosen** — the confound from Act 3. The single biggest failure mode; the whole
  `needs_human_review` flag exists to catch it.
- **Style leakage** — "fixing" a pair but also nudging tone/length/persona, so the model drifts on
  things you never meant to train. One axis, measured.
- **Reward hacking the proxy** — if the only axis is "shorter," the model can learn to be curt and
  unhelpful while scoring great. The axis must be the *failure*, not a cheap proxy for it.
'''))
C.append(md('''
## The concept at three levels (say each in your own words)

- **To a beginner:** "we show the model two replies to the same question - the good one and the bad
  one - and we make sure they differ in only ONE way, so it learns exactly that one thing."
- **To an engineer:** "a preference pair is `(prompt, chosen, rejected)`; the chosen-minus-rejected
  delta must isolate a single failure axis (an ablation), with provenance and a human-review gate -
  multi-axis deltas confound the DPO gradient and teach unintended preferences."
- **To a founder:** "we turn each caught mistake into one crisp before/after the model can learn
  from - disciplined enough that 'fix the interruptions' doesn't accidentally also make the agent
  terse or switch languages. Clean data in, predictable behavior out."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**Defense question 1: "If `chosen` is clearly the better reply, why isn't that a good pair?"**
<details><summary>answer</summary>Because "better" is a human-grading bar, and a training pair needs the ablation bar: chosen and rejected must differ on exactly ONE axis. A reply that is better on three axes hands the method three entangled preferences and it cannot recover which one you meant - it may learn to switch language or pad tone when you only wanted to stop the over-talk. Better-to-a-human and clean-to-train-on are different measurements.</details>

**Defense question 2: "You used the hero call's real t3 as rejected. Why not write a worse turn to make the contrast sharper?"**
<details><summary>answer</summary>Because a strawman rejected teaches against a failure that never happens. The value of the pair is correcting REAL behavior, so rejected comes verbatim from the trace (t3) and the failure axis is the one we measured - an 800ms barge-in plus a full-address demand over a partial answer. Sharpening the contrast by inventing a worse turn would make the pair dishonest and the lesson hollow.</details>

**Defense question 3: "Every pair is flagged `needs_human_review=true`. Isn't that just bureaucracy if the export already ran cleanly?"**
<details><summary>answer</summary>No - it guards the exact failure no automated check catches: a confounded pair exports with zero errors. The single-axis rule is a judgment about MEANING (did only the failure axis move?), and a human is the only thing that reliably catches a chosen turn that is better-but-multi-axis. The flag is the seam where 'it ran' and 'it teaches one lesson' are kept separate.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own: one pair per cast member with its axis dictated by the failure (and call_A
correctly yielding none), where pairs live in the real repo (`schemas/improvement_example.md`,
`pipeline/dpo_export.py`, `rubric.yaml`, `pipeline/signals.py`), how clean pairs hand book 18 a
trustworthy training signal — and, above all, the bar you must clear to PASS this book.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The **three parts** of a preference pair, and what each is for
2. The **single-axis diff rule** — the one thing allowed to differ between chosen and rejected
3. The hero pair you built: what was the failure axis, and where did `rejected` come from?
4. The trap: why a "better on every axis" pair is a **bad** training pair — the two different bars
5. The book's clean sentence (below) — in your own words first

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about preference pairs

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"A clean pair teaches one lesson; a messy pair teaches confusion."**

A preference pair is a contrast with a direction, and the contrast only teaches *one* thing when
`chosen` and `rejected` differ on exactly *one* axis — the detected failure. Move two axes and you
have taught two tangled lessons under one label. If your sentence captures that single-axis
discipline in your own words, this book did its job.
'''))
C.append(md('''
## Next on the ladder

**17 done** (pending your teach-back) -> **18 · DPO** — the training method that *consumes* the
pairs you just learned to author. It nudges the model toward every `chosen` and away from every
`rejected`. Now you know why book 18 lives or dies on the single-axis discipline: feed it clean
pairs and it learns the one lesson you meant; feed it confounded ones and it learns three you
didn't. The pairs you author here are the fuel for the engine there.

(The self-audit below is the LAST cell — run it, read the verdict, then do the teach-back.)
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "17_preference_pairs.ipynb"   # <- this notebook's filename
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

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "17_preference_pairs.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
