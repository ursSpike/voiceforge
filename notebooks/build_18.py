#!/usr/bin/env python3
# Builds 18_dpo_baby_language.ipynb — VoiceForge University book 18.
# The ONE atomic concept: DPO teaches a model to prefer chosen over rejected; it lives in a
# JSONL format (TRL conversational + the OpenAI mirror). Format only — NO training, no GPU.
# Human-preference intuition FIRST, the name "DPO" LAST. Same four-act skeleton + markers as
# build_P00.py / build_11.py. Rerun: .venv/bin/python notebooks/build_18.py
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
# 18 · DPO in baby language

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Explain the human-preference idea **without the name** — "show two answers, point at the better one"
2. Place DPO on the **training ladder** (pretrain → SFT → preference) in plain words
3. Say **DPO vs RLHF** in one sentence each, and why DPO is the simpler cousin
4. Write a preference pair in the **TRL conversational JSONL** shape, and mirror it to the
   **OpenAI** preference shape — *format only*, no training, no GPU, nothing downloaded
5. Spot the **"any pair is useful" trap** — why a pair that changes more than one thing teaches the wrong lesson

Topic stays small on purpose: a handful of authored pairs. We **never train anything** here —
this book is about the *data shape* a trainer would later eat, and the discipline that makes it honest.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits on the ladder)

`17 · preference pairs  →  THIS · DPO in baby language  →  19 · RLHF / RLAIF`

Book 17 taught you to mine a **(chosen, rejected) pair** from a real failure: take the turn the
agent botched, write the turn it *should* have said, and let the only difference be the failure
axis. That left an open question — *what does a model actually DO with a pile of those pairs?*
This book answers the "what does it do" at the level of **the data format and the one-line idea**:
a method called DPO reads pairs like yours and nudges the model to prefer the chosen over the
rejected. Book 19 then widens the lens to **RLHF/RLAIF** — the older, heavier family DPO simplified.
So: 17 makes the pairs · 18 names what consumes them and writes the file · 19 places it in the
bigger preference-learning world. We build the *file*, never the *training run*.
'''))
C.append(md('''
## 3 — Baby intuition (the idea, before any name)

Forget machine learning for a second. Picture teaching a kid to write thank-you notes.

You do **not** hand them a rulebook of grammar. You show them **two** notes for the same
occasion — one warm and short, one cold and rambling — and you say *"this one is better."*
Then another two. Then another. You never explain the theory of good notes; you just keep
**pointing at the better of two**, over and over. Slowly the kid's own writing drifts toward
the kind you kept picking.

That is the whole idea. Two candidate answers to the *same* situation, a finger pointing at
the **preferred** one, repeated many times. The learner never needs a score, a rubric, or a
lecture — only a steady signal of *"prefer this over that."* Hold this picture. The fancy name
comes at the very end of the book, and it will feel like a label on something you already own.
'''))
C.append(md('''
## 4 — The training ladder (plain words, no jargon yet)

A chat model is not built in one step. Think of three rungs, each answering a different question:

| rung | plain question it answers | how it learns |
|---|---|---|
| **pretrain** | "what word tends to come next?" | reads a huge pile of text, predicts the next token |
| **SFT** (supervised fine-tune) | "what does a *good answer* look like?" | shown example prompt→answer pairs, copies the style |
| **preference** | "given two answers, which is *better*?" | shown (chosen, rejected) pairs, leans toward chosen |

Pretrain gives raw language. SFT gives the *shape* of a helpful reply. But SFT only ever sees
**one** "right" answer per prompt — it cannot learn the *difference* between a good reply and a
slightly-worse one. The preference rung exists for exactly that: it learns from **contrast**.
DPO is one way to climb that third rung. This book lives entirely on rung three — and only on
its **data format**, not the climb itself.
'''))
C.append(md('''
## 5 — DPO vs RLHF, one sentence each (the name, finally — but kept small)

The idea from cell 3 ("prefer chosen over rejected, many times") has two well-known machines:

- **RLHF** — *reinforcement learning from human feedback*: train a **separate reward model** to
  score answers from the human preferences, then use reinforcement learning to push the chat
  model toward high reward. Powerful, but it is **three moving parts** (preferences → reward
  model → RL loop) and famously fiddly to keep stable.
- **DPO** — *direct preference optimization*: **skip the reward model and the RL loop** — adjust
  the chat model **directly** from the (chosen, rejected) pairs with one ordinary training step.
  Same goal, far fewer moving parts. That is why it is the friendly cousin you meet first.

For this whole notebook, the only thing you must *do* with either is **write the pairs they eat**.
Neither machine runs here. The deep version of RLHF/RLAIF is book 19's job.
'''))
C.append(md('''
## 6 — Why this book exists (VoiceForge's kicker is a *file*, not a training run)

VoiceForge's demo arc ends on a promise: *"we don't just grade your agent — we hand you the
data to fix it."* That data is a JSONL file of preference pairs (`out/queue.jsonl`), produced by
`pipeline/dpo_export.py` from the failures the pipeline detected. The pitch never claims to have
trained a model on stage (no GPU at a hackathon). It claims something more honest and more
checkable: **here is the corrective dataset, in the exact shape a DPO trainer (HuggingFace TRL)
or OpenAI's fine-tuning API would accept.**

So your job in this book is the job that file does: turn a detected failure into a clean
(chosen, rejected) pair and write it in the right shape — twice (TRL + OpenAI). The discipline
that keeps it honest (only one thing differs between chosen and rejected) is the real lesson.
The next cell is your first run.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just syntax.

# We print a sentence so you can see WHERE output appears (directly under the cell) and so your
# first action is a run you committed to. PREDICT - what exact text shows below?
print("DPO learns from a finger pointing at the better of two answers")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. State the preference idea **without** using the letters D-P-O — the thank-you-note version.
2. Name the three rungs of the training ladder and the plain question each one answers.
3. DPO vs RLHF in one breath: which one **drops the separate reward model and the RL loop**?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: "improving a model" is one mysterious blob of training.
After Act 1 you should hold three things: (a) preference learning is just *"prefer this over
that," repeated*; (b) it sits on the **third rung** above pretrain and SFT, and it is the only
rung that learns from **contrast**; (c) **DPO** is the cousin that reaches that rung *directly*,
without RLHF's separate reward model and RL loop. And this book only ever writes the **file**.

If that feels solid in your own words, continue. If not, re-read cell 4 (the ladder table).
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of the preference idea, WITHOUT the name DPO. Not mine - yours.
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
# Act 2 — Mechanics: a real failure → one clean pair → the two file shapes

## Where the pair comes from (the real hero call, raw first)

Course rule: see the ugly input before transforming it. A preference pair is not invented from
thin air — it is mined from a **detected failure**. We use the recurring hero call (`call_C`, the
Telugu-English booking, `data/hero/turns.json`). The failure we will fix is the early one: the
user gives a *partial* area, and the agent **over-demands** a full address instead of
acknowledging what it got. We load the turns and look at the two that matter, RAW.
'''))
C.append(code('''
# The hero call is the recurring cast member call_C. We load its turns from the real repo file
# so the turn text we turn into a pair is the ACTUAL text, not a paraphrase we made up.
import json
from pathlib import Path

# Resolve the path whether the notebook runs from repo root or from notebooks/ - the file is the
# single source of truth for the turns, so we must read the real one on disk.
here = Path.cwd()
candidates = [here / "data/hero/turns.json", here.parent / "data/hero/turns.json",
              *[p / "data/hero/turns.json" for p in here.parents]]
turns_path = next(p for p in candidates if p.exists())
call = json.loads(turns_path.read_text())

print("call_id:", call["call_id"], "| language:", call["language"], "| turns:", len(call["turns"]))
'''))
C.append(code('''
# We pull the two turns of the failure as a lookup, then print them RAW. t2 is the user's
# partial answer; t3 is the agent's over-demand. The pair we author replaces t3 - so we must
# SEE t2 and t3 exactly before touching them.
by_id = {t["turn_id"]: t for t in call["turns"]}

for tid in ["t2", "t3"]:
    t = by_id[tid]
    # id and speaker first so it is unmistakable who said what - the pair only makes sense in context
    print(f"{tid} ({t['speaker']}): {t['text']}")
'''))
C.append(md('''
## PREDICT
Read t2 (the user's partial area) and t3 (the agent's reply) above. We are about to build a
(chosen, rejected) pair where **rejected = what the agent actually said at t3**. Before the next
cell, commit out loud:
1. What is the ONE thing wrong with t3 — name the failure axis in three words.
2. What would the **chosen** (better) turn do differently — and what must it leave *unchanged*?
'''))
C.append(code('''
# YOUR TURN - commit the failure axis and your one-line fix BEFORE we author the pair.
# Storing them makes the notebook a record of YOUR judgement, to compare against the worked pair.
my_failure_axis = ""   # <- e.g. "over-demand / ignored the partial" (three-ish words)
my_chosen_idea = ""    # <- one line: what the better turn does (acknowledge partial, ask ONE thing)

if len(my_failure_axis.strip()) < 5 or len(my_chosen_idea.strip()) < 15:
    print("set my_failure_axis (5+ chars) and my_chosen_idea (15+ chars), then re-run.")
else:
    print("axis:", my_failure_axis, "| fix:", my_chosen_idea)
'''))
C.append(md('''
## The pair as a plain record, BY HAND

Manual-before-function: before any export helper exists, we write the pair as a plain dict in the
shape `schemas/improvement_example.md` defines. This is the *internal* record (provenance +
both turns + why). The file formats come AFTER — first we get the content right.
'''))
C.append(code('''
# By-hand improvement_example record for ONE failure of the hero call. Every field is here on
# purpose; the comments say WHY each exists, because the fields ARE the lesson of book 17 feeding 18.
pair = {
    "call_id": call["call_id"],          # provenance: which call produced this pair (audit trail)
    "failure_dimension": "repair_quality",  # which rubric dimension fired - the axis we are correcting
    # rejected_turn is the agent's ACTUAL words at t3 - we copy them, we do not paraphrase,
    # because the model must learn from what really went wrong.
    "rejected_turn": by_id["t3"]["text"],
    # chosen_turn differs ONLY on the failure axis: it acknowledges the partial area (Madhapur,
    # near the metro) and asks ONE next thing. Same job, same brevity goal - just the repair fixed.
    "chosen_turn": "Got it - Madhapur, near the metro station. What appliance needs servicing?",
    "reason": "chosen acknowledges the partial area and asks one targeted follow-up; rejected over-demands a full address and ignores what the user already gave",
    "quality_delta": 0.65,               # directional: how much better chosen is (scorecard-implied)
    "needs_human_review": True,          # true until a human eyeballs it - never trust an auto-pair blindly
}
print(json.dumps(pair, indent=2, ensure_ascii=False))
'''))
C.append(md('''
## The single-axis discipline (the heart of a good pair)

Read the two turns side by side. The **only** meaningful difference must be the failure axis.
Same caller, same booking goal, same short style — only the *repair behaviour* flips from
"over-demand" to "acknowledge + one ask". If the chosen turn were also longer, or switched
language, or added a joke, the model could not tell *which* change you wanted it to prefer.

`schemas/improvement_example.md` states it bluntly: **"the ONLY meaningful difference between
chosen and rejected is the detected failure axis."** The next cell shows the contrast explicitly.
'''))
C.append(code('''
# Print rejected vs chosen back to back so the SINGLE difference is visible to the eye.
# We also show their lengths: the chosen is shorter here, but that is a SIDE effect of removing
# the over-demand, not a second axis we are training - the axis is "repair", length just follows.
print("REJECTED:", pair["rejected_turn"])
print("  CHOSEN:", pair["chosen_turn"])
print()
print("rejected length (chars):", len(pair["rejected_turn"]))
print("  chosen length (chars):", len(pair["chosen_turn"]))
print("axis being taught:", pair["failure_dimension"], "- everything else held as constant as possible")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not from memory): name the single axis that differs
between rejected and chosen, and say why a model could not learn cleanly if a *second* thing
(length, language, tone) also changed at the same time.
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
1. What three fields give a pair its **provenance and reason** (so it is not anonymous)?
2. State the single-axis rule in your own words.
3. Why is `needs_human_review` set to `True` by default — what would go wrong if auto-pairs
   were trusted straight into training?
'''))
C.append(md('''
## Now the file shape — TRL conversational JSONL (the format DPO trainers eat)

You have the content right. *Now* the format. A DPO trainer in HuggingFace **TRL** wants each
example as three keys — `prompt`, `chosen`, `rejected` — where each is a **list of chat
messages** (`{"role", "content"}`). The `prompt` is the shared setup (a system instruction + the
user's turn); `chosen` and `rejected` are the two candidate **assistant** replies to it.

We assemble it by hand from our `pair`, naming every piece. This is exactly the line
`pipeline/dpo_export.py` writes to `out/queue.jsonl`. **No trainer runs — we only build the dict.**
'''))
C.append(code('''
# The system instruction is the agent's standing rules - it is part of the PROMPT both replies
# share, so the contrast is purely about the assistant turn, nothing else.
system_msg = ("Voice agent for appointment booking. Replies under 2 sentences. "
              "Never speak while the caller is mid-answer.")

# Build the TRL conversational example. The shape is fixed by TRL: prompt/chosen/rejected, each a
# LIST of {role, content} messages. We map our pair's fields into exactly those slots.
trl_example = {
    # prompt = the shared setup: system rules + the user's real turn (t2). Both candidate replies
    # answer THIS, so the only thing that varies downstream is the assistant content.
    "prompt": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": by_id["t2"]["text"]},
    ],
    # chosen = the preferred assistant reply, as a one-message list (the corrected turn)
    "chosen": [{"role": "assistant", "content": pair["chosen_turn"]}],
    # rejected = the dispreferred assistant reply (what the agent actually said at t3)
    "rejected": [{"role": "assistant", "content": pair["rejected_turn"]}],
}
print(json.dumps(trl_example, indent=2, ensure_ascii=False))
'''))
C.append(md('''
## PREDICT
A **JSONL** file is "one JSON object per line" — not a pretty-printed array. The next cell dumps
`trl_example` as a single line (the way it would actually appear in `out/queue.jsonl`). Predict:
will that line contain newlines *inside* it, and roughly how many top-level keys will you see?
Commit before running.
'''))
C.append(code('''
# JSONL = one compact JSON object per line. We dump WITHOUT indentation so the whole example is a
# single line - that is the literal on-disk format a trainer reads line by line.
one_line = json.dumps(trl_example, ensure_ascii=False)

print(one_line)
print()
# Show it really is one line and confirm the three required top-level keys are present.
print("newlines inside the line:", one_line.count(chr(10)))   # expect 0 - it is a single line
print("top-level keys:", list(trl_example.keys()))            # expect prompt, chosen, rejected
'''))
C.append(md('''
## EXPLAIN gate
One sentence: what does **one line** of `out/queue.jsonl` represent, and what are its three keys?
(If you said "one preference pair: a shared prompt, plus the chosen and rejected replies," you have it.)
'''))
C.append(md('''
## The OpenAI mirror format — same pair, different field names

The same pair can feed OpenAI's preference fine-tuning API, which uses **different key names** for
the **same three ideas**. `pipeline/dpo_export.py` documents the mapping as a 3-line mapper:

| TRL key | OpenAI key | what it holds |
|---|---|---|
| `prompt` | `input.messages` | the shared setup messages |
| `chosen` | `preferred_output` | the better assistant reply |
| `rejected` | `non_preferred_output` | the worse assistant reply |

Manual-before-function again: we do the rename by hand first, so the helper afterwards is a
convenience, not a mystery. Still **no training** — we are translating one file shape into another.
'''))
C.append(code('''
# Hand-rename TRL -> OpenAI. Nothing about the CONTENT changes - only the field names move.
# We build it explicitly (not in a loop) so each rename is visible and you can check it by eye.
openai_example = {
    "input": {"messages": trl_example["prompt"]},   # prompt -> input.messages (the shared setup)
    "preferred_output": trl_example["chosen"],       # chosen -> preferred_output
    "non_preferred_output": trl_example["rejected"], # rejected -> non_preferred_output
}
print(json.dumps(openai_example, indent=2, ensure_ascii=False))
'''))
C.append(code('''
# Now the helper, EARNED because you did the rename by hand. A 3-line mapper is all it takes -
# this mirrors the mapper described in pipeline/dpo_export.py. We keep it tiny on purpose: the
# whole point of the OpenAI format is that it is the SAME pair wearing different labels.
def to_openai(trl):
    # one dict comprehension would hide the renames; explicit keys keep the mapping auditable
    return {"input": {"messages": trl["prompt"]},
            "preferred_output": trl["chosen"],
            "non_preferred_output": trl["rejected"]}


# Prove the helper reproduces our hand-built version exactly - same content, renamed keys.
assert to_openai(trl_example) == openai_example, "helper must match the hand-built rename"
print("helper matches hand-built OpenAI example:", to_openai(trl_example) == openai_example)
'''))
C.append(md('''
## PREDICT
Both files describe the **same** preference. So if we dig the *chosen assistant text* out of the
TRL example and out of the OpenAI example, will the two strings be **identical** or **different**?
Commit before running — this checks whether you believe the formats differ in *content* or only
in *labels*.
'''))
C.append(code('''
# Pull the chosen assistant text out of BOTH shapes and compare. If the formats are truly just
# different labels on the same pair, these must be the exact same string.
trl_chosen_text = trl_example["chosen"][0]["content"]
openai_chosen_text = openai_example["preferred_output"][0]["content"]

print("TRL chosen   :", trl_chosen_text)
print("OpenAI chosen:", openai_chosen_text)
# Same content, different envelope - the trap of thinking "different format = different data".
print("identical content:", trl_chosen_text == openai_chosen_text)
'''))
C.append(md('''
## Writing the actual file (still no training — just bytes on disk)

A JSONL file with 2 example pairs is just two lines, each a compact JSON object. We author a
second pair (a different failure axis) and write both to a temp file, then read it back to prove
the round-trip. This is the entire job of `pipeline/dpo_export.py` minus the failure-mining —
**zero GPU, zero model, zero network.**
'''))
C.append(code('''
# A SECOND pair on a DIFFERENT axis (barge_in): the agent talks over the caller. rejected = an
# interrupting reply; chosen = the same content but waiting for the caller to finish first.
# Different axis, same single-axis discipline - only the interruption behaviour flips.
pair2_trl = {
    "prompt": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": "haan ek minute, address cheptanu... plot number..."},
    ],
    "chosen": [{"role": "assistant", "content": "Sure, take your time - go ahead with the plot number."}],
    "rejected": [{"role": "assistant", "content": "Okay so for the booking I also need the appliance type and your preferred slot right now."}],
}

# Collect the dataset as a list of TRL examples - this is what gets written line by line.
dataset = [trl_example, pair2_trl]
print("pairs in dataset:", len(dataset))
'''))
C.append(code('''
# Write the dataset as JSONL to a temp path (NOT the real out/queue.jsonl - we never clobber repo
# artifacts from a teaching notebook). One json.dumps per line is the whole format.
import tempfile, os

tmp_dir = tempfile.mkdtemp()                       # a throwaway dir so this cell is side-effect-free
queue_path = os.path.join(tmp_dir, "queue.jsonl")  # mirrors the real out/queue.jsonl name

with open(queue_path, "w", encoding="utf-8") as f:
    for ex in dataset:
        # one compact object + a newline per pair - that newline is what makes it JSON-LINES
        f.write(json.dumps(ex, ensure_ascii=False) + "\\n")

print("wrote", len(dataset), "pairs to", queue_path)
'''))
C.append(code('''
# Read it back line by line and parse each line - proving the file is valid JSONL a trainer
# could stream. We re-derive the count from the FILE, not from memory, so the proof is real.
loaded = []
with open(queue_path, encoding="utf-8") as f:
    for line in f:
        loaded.append(json.loads(line))   # each line parses on its own - the JSONL contract

print("pairs read back from disk:", len(loaded))
print("first pair's keys:", list(loaded[0].keys()))
print("round-trip preserved chosen text:", loaded[0]["chosen"][0]["content"])
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. Name the three TRL keys and their OpenAI equivalents.
2. What does **one line** of a JSONL file contain, and how is JSONL different from a JSON array?
3. We wrote a real file and read it back — yet we trained **nothing**. What *exactly* did this
   book produce, and what is the missing step a trainer would add later?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: "DPO" was a training mystery. After Act 2 you can take a real detected failure, author a
**single-axis** (chosen, rejected) pair, write it in the **TRL conversational** shape, **mirror**
it to the **OpenAI** shape (same content, renamed keys), and serialize a JSONL **file** you read
back from disk — all with **no training, no model, no GPU**. You now own the *data* DPO consumes.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (the pair shape / the two formats / "format not training")

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the format, and the "any pair is useful" trap

## Break-it philosophy

A preference file is only useful if it is **valid** and **disciplined**. So we now feed broken
examples on purpose and watch where the format fails — and, worse, where it *passes the format
check but teaches the wrong thing*. Surprise on your own terms is education; a malformed JSONL
line discovered when a training run dies at 2am is a disaster.
'''))
C.append(md('''
## PREDICT
We build a pair missing the `rejected` key (only `prompt` and `chosen`). When we ask for
`example["rejected"]` to write the line, does Python **crash loudly**, or write a **silently
incomplete** pair? Commit to one before running.
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. Read what happens, do not fix it yet.

# A pair with NO rejected reply. DPO needs BOTH sides - the whole signal is the contrast between
# them. A one-sided "pair" is not a preference at all; it is just an SFT example in disguise.
broken = {
    "prompt": [{"role": "user", "content": "what appliance needs servicing?"}],
    "chosen": [{"role": "assistant", "content": "Got it - which appliance is giving trouble?"}],
    # note: NO "rejected" key at all
}

# Accessing a missing key with [] raises KeyError - the format refuses to pretend a contrast
# exists when only one side was provided. (A trainer would reject this line for the same reason.)
print("rejected side:", broken["rejected"])
'''))
C.append(md('''
## Reading the failure, and the graceful guard

`KeyError: 'rejected'` is the format **doing its job** — a one-sided pair has no contrast to learn
from, so the lookup refuses. But a crash mid-write is blunt; in an exporter you want a *clean
verdict per line*, not a traceback that kills the whole run. The next cell writes a tiny validator
that **reports** which required keys are missing instead of crashing — the difference between code
that dies and code that *flags and continues*.
'''))
C.append(code('''
# A validator that returns a verdict instead of crashing. It checks the three required keys AND
# that chosen/rejected actually differ - a pair where they are identical teaches nothing.
def validate_pair(ex):
    required = ["prompt", "chosen", "rejected"]
    missing = [k for k in required if k not in ex]   # which contract keys are absent
    if missing:
        return False, f"missing keys: {missing}"
    # a pair with identical chosen and rejected has no preference signal - flag it explicitly
    if ex["chosen"] == ex["rejected"]:
        return False, "chosen and rejected are identical - no contrast to learn from"
    return True, "ok"


print("broken pair  ->", validate_pair(broken))        # reports the missing 'rejected'
print("good pair    ->", validate_pair(trl_example))   # passes cleanly
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
A one-sided "pair" (chosen only) is really just an SFT example, not a preference. Why does DPO
**need both sides** to learn anything? And which tool here catches the missing side without
halting the whole export?
'''))
C.append(md('''
## YOUR break now

Author your own broken pair and predict the validator's verdict. Make ONE of these mistakes:
drop a required key, OR set `chosen` equal to `rejected`. Predict exactly what `validate_pair`
returns (the bool AND the message), write it as a comment, then run.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it. Damage ONE thing and predict the verdict.
# my prediction: <write here exactly what validate_pair will return and why>

my_broken_pair = {
    "prompt": [{"role": "user", "content": "morning or evening slot?"}],
    "chosen": [{"role": "assistant", "content": "Morning works - shall I book 10 AM?"}],
    "rejected": [{"role": "assistant", "content": "Morning works - shall I book 10 AM?"}],  # <- damage: change a key or make these differ/identical
}

# Run the validator and compare reality against your written prediction above.
ok, msg = validate_pair(my_broken_pair)
print("passes:", ok, "| message:", msg)
'''))
C.append(md('''
## WRONG-INTUITION TRAP 1 — "any (chosen, rejected) pair is useful training data"

**The wrong belief:** "as long as I label one answer chosen and one rejected, the model learns
something good. More pairs = more improvement, regardless of *how* they differ."

The danger: if chosen and rejected differ on **more than the failure axis**, the model cannot
tell *which* difference you wanted. The next cell builds a pair that is **valid format** and has a
real contrast — but the chosen reply also happens to switch to Hindi, add an emoji, and run
longer. It will **pass `validate_pair`**. Run it, then try to name *every* way the two replies
differ BEFORE the reveal.
'''))
C.append(code('''
# A trap pair: format-valid, real contrast - but the chosen differs on FOUR axes at once, only
# one of which (the repair) we actually meant to teach. validate_pair cannot see this; it only
# checks structure, not discipline.
trap_pair = {
    "prompt": [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": by_id["t2"]["text"]},
    ],
    # chosen: fixes the repair (good) BUT ALSO switches language, adds an emoji, and gets longer
    "chosen": [{"role": "assistant", "content": "Arre haan, Madhapur metro ke paas, samajh gaya! Bahut accha, ab batao konsa appliance theek karna hai aur kaunsa time slot prefer karoge aaj? :)"}],
    # rejected: the original over-demand (English, no emoji, long in a different way)
    "rejected": [{"role": "assistant", "content": by_id["t3"]["text"]}],
}

ok, msg = validate_pair(trap_pair)
print("trap pair passes validate_pair:", ok, "| message:", msg)   # True - structure is fine
print()
print("CHOSEN  :", trap_pair["chosen"][0]["content"])
print("REJECTED:", trap_pair["rejected"][0]["content"])
'''))
C.append(md('''
## The reveal

`validate_pair` returned `True` — the structure is perfect. But count the differences between
chosen and rejected: (1) the **repair** is fixed *(the axis we wanted)*, (2) the **language**
switched English→Hindi, (3) an **emoji** appeared, (4) the **length and tone** changed. That is
**four axes moving at once**. A preference trainer cannot read your mind — it will lean toward
*all four* differences indiscriminately, so you might accidentally teach the agent "prefer Hindi"
or "prefer emojis," not "acknowledge partial answers."

**This is the trap at the heart of preference data:** *more pairs is not better — cleaner pairs
are better.* A format-valid pair can still be **training poison** if it changes more than the one
thing you meant. This is exactly why `schemas/improvement_example.md` is built around the
single-axis rule, and why every auto-mined pair carries `needs_human_review=True`. A human reads
the pair and asks the one question the validator cannot: *"does ONLY the failure axis differ?"*
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why can a format-valid pair still be bad training data?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
Two pairs both pass `validate_pair`. One is clean (only the repair differs); one is the trap
(four axes differ). If the validator cannot tell them apart, what is the validator actually
*for* — and what is the ONLY thing that separates a clean pair from a poisonous one?
'''))
C.append(md('''
## A second break: chosen and rejected accidentally swapped

One more failure mode, and it is the scariest because it is **silent**: a pair where the better
turn is in `rejected` and the worse turn is in `chosen` — the labels flipped. The format is
valid. The contrast exists. And the file will teach the model the **exact opposite** of what you
meant. `validate_pair` happily passes it.
'''))
C.append(md('''
## PREDICT
We build a pair where `chosen` holds the over-demand (the *bad* turn) and `rejected` holds the
acknowledging turn (the *good* one) — the labels are swapped. Predict: does `validate_pair`
**catch** this, or **pass** it? Commit first — this tests whether you think a structure check can
catch a *semantic* mistake.
'''))
C.append(code('''
# BREAK-IT (guided) - a SILENTLY wrong pair: the labels are swapped so the file teaches the
# opposite of what we want. There is NO crash - that is the whole danger of this one.
swapped = {
    "prompt": [{"role": "system", "content": system_msg},
               {"role": "user", "content": by_id["t2"]["text"]}],
    "chosen": [{"role": "assistant", "content": by_id["t3"]["text"]}],   # the BAD turn, mislabeled chosen
    "rejected": [{"role": "assistant", "content": pair["chosen_turn"]}], # the GOOD turn, mislabeled rejected
}

# validate_pair only checks STRUCTURE (keys present, sides differ) - both are true here, so it
# passes. A swapped pair is valid format and poisonous content: the failure no machine catches.
ok, msg = validate_pair(swapped)
print("swapped pair passes validate_pair:", ok, "| message:", msg)
print("but chosen is actually the OVER-DEMAND:", swapped["chosen"][0]["content"][:50], "...")
print("-> only a human reading the pair catches this. structure checks are blind to meaning.")
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a (chosen, rejected) pair felt automatically useful. After Act 3 you know a missing key
crashes loudly (and `validate_pair` flags it gracefully), but the **dangerous** failures are
silent: a multi-axis pair (the trap) and a **swapped** pair both pass every structure check while
poisoning the training signal. Structure validation is necessary and **not sufficient** —
single-axis discipline and a human review are what actually keep the data honest.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the "any pair is useful" trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this lives, and the bar you must clear

## Where DPO data lives in VoiceForge

This is not a notebook idea — it is the product's kicker, wired into the real repo:
- **`schemas/improvement_example.md`** defines the pair: `call_id`, `failure_dimension`,
  `rejected_turn`, `chosen_turn`, `reason`, `quality_delta`, `needs_human_review` — and states
  the **single-axis rule** as law.
- **`pipeline/dpo_export.py`** turns detected failures into pairs and writes two files:
  `out/queue.jsonl` (TRL conversational) and `out/queue_openai.jsonl` (the 3-line OpenAI mapper).
  It targets ~10–20 pairs, each with provenance and `needs_human_review=True`.
- The **failure that feeds a pair** comes from the scorecard (book 11): the t3 over-demand scored
  low on `repair_quality` with evidence `[t2, t3]` — that evidence is what identifies the single
  turn to rewrite.
- **No training runs in this repo.** The deliverable is the *dataset*, in the exact shape a TRL
  or OpenAI DPO job would accept. That honesty (data, not a trained model) is the point.
'''))
C.append(md('''
## Where it flows next on the ladder

- **17 · preference pairs** (just behind you) mined the (chosen, rejected) pairs from failures —
  this book named what consumes them (DPO) and wrote them in the two real file shapes.
- **19 · RLHF / RLAIF** (just ahead) zooms out to the heavier family DPO simplified: a separate
  reward model, an RL loop, and the "AI feedback" variant where a model (not a human) does the
  preferring. Everything you wrote here is the *input* those methods also eat — DPO just consumes
  it most directly.
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

You authored two clean pairs and saw two poison pairs (multi-axis, swapped). In book 19, the
preferring is sometimes done by **another AI** instead of a human (RLAIF). Predict: does the
single-axis discipline get **easier or harder** to enforce when an AI labels the pairs at
scale — and what new failure mode might appear that a human reviewer would have caught?
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for book 19 to confront.
my_rlaif_prediction = ""   # easier/harder + the new failure mode an AI labeler might introduce

if len(my_rlaif_prediction.strip()) < 20:
    print("write your prediction above (easier/harder + the new risk), then re-run.")
else:
    print("PREDICTION STORED:", my_rlaif_prediction)
'''))
C.append(md('''
## Where this idea itself fails (honesty applies to the method too)

- **Multi-axis pairs** — chosen differs from rejected on more than the failure axis (the trap you
  built). Countermeasure: the single-axis rule + a human eyeballing each pair (`needs_human_review`).
- **Swapped labels** — the better turn lands in `rejected`. Countermeasure: a human reads the pair;
  no structure check sees meaning.
- **Format-confidence** — assuming a file that *parses* is a file that *teaches correctly*.
  Countermeasure: remember `validate_pair` checks structure, never discipline or direction.
- **"Train it on stage" overclaim** — promising a fine-tuned model from a hackathon dataset.
  Countermeasure: claim only what is true — *here is the corrective dataset in trainer-ready
  shape*; the training itself is future work that needs a GPU and a held-out eval.
'''))
C.append(md('''
## The same idea at three levels

- **To a beginner:** "show the model two answers and point at the better one, again and again —
  that pointing, saved as a file of pairs, is what DPO learns from. We make the file, not the
  trained model."
- **To an engineer:** "a DPO example is `{prompt, chosen, rejected}` (TRL conversational),
  mirrored to `{input.messages, preferred_output, non_preferred_output}` for OpenAI. We export
  single-axis pairs from detected failures to `out/queue.jsonl`; DPO skips RLHF's reward model and
  RL loop and optimizes the policy directly from the pairs. No training in-repo — the artifact is
  the dataset."
- **To a founder:** "we don't just score your agent — we hand you a ready-to-train improvement
  dataset built from its real mistakes, in the format the standard tooling expects. The
  improvement is concrete and auditable, and we're honest that training it is the next step, not
  a stage trick."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "You say DPO but you never trained anything — isn't that a cop-out?"**
<details><summary>answer</summary>No — the deliverable is deliberately the dataset, not a trained model. Training DPO needs a GPU and a held-out eval we can't fake on stage. What we CAN produce honestly is the corrective dataset in the exact TRL/OpenAI shape a DPO job accepts, mined from real detected failures. The format and the single-axis discipline are the hard part; the training step is standard tooling on top.</details>

**2. "Why DPO and not RLHF?"**
<details><summary>answer</summary>RLHF is three moving parts — collect preferences, train a separate reward model, then run an RL loop against it — and it's notoriously fiddly to stabilize. DPO reaches the same goal (prefer chosen over rejected) by adjusting the model directly from the pairs, dropping the reward model and the RL loop. Same input data, far fewer ways to break. RLHF/RLAIF is book 19.</details>

**3. "A pair is just chosen-vs-rejected — why fuss over what differs between them?"**
<details><summary>answer</summary>Because the model leans toward EVERY difference, not just the one you meant. If chosen also switches language or adds an emoji, you might teach "prefer Hindi" instead of "acknowledge partial answers." That's why the schema enforces single-axis pairs and every auto-mined pair is needs_human_review=True — a structure check (valid JSON, both sides present) is blind to whether only the failure axis differs.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: where the pair format lives in the real repo
(`schemas/improvement_example.md`, `pipeline/dpo_export.py`, `out/queue.jsonl`), how it flows from
the scorecard's detected failures (11/17) toward RLHF/RLAIF (19), the method's own failure modes
(multi-axis, swapped, format-confidence, the train-on-stage overclaim), and how to defend at three
levels — including the honest line that we ship the *dataset*, not a trained model.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The preference idea in plain words — *without* the name DPO (the thank-you-note version)
2. The three rungs of the training ladder, and which rung learns from contrast
3. DPO vs RLHF in one sentence each — what DPO drops
4. The TRL pair shape `{prompt, chosen, rejected}` and its OpenAI mirror — and why it's *format, not training*
5. The "any pair is useful" trap — why a format-valid pair can still be poison, and what catches it

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (where it lives / where it flows)
my_clean_sentence = ""      # the sentence you'd say in a room about DPO data

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"DPO teaches a model to prefer chosen over rejected — VoiceForge mines those pairs from real failures."**

If yours captures that in your own words — preference data is a finger pointing at the better of
two answers, saved as a file, and ours comes from the agent's actual mistakes — this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "18_dpo_baby_language.ipynb"   # this notebook's filename
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

**18 done** (pending your teach-back) → **19 · RLHF / RLAIF** — you have the preference *data* and
the *direct* method that eats it. Book 19 opens up the heavier family DPO simplified: a separate
reward model, an RL loop, and the RLAIF twist where an AI does the preferring. The pairs you wrote
here are the fuel; 19 shows the other engines that burn it.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "18_dpo_baby_language.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
