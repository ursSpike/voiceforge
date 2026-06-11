#!/usr/bin/env python3
# Builds 11_evidence_based_scoring.ipynb — VoiceForge University book 11.
# The ONE atomic concept: no naked scores — every score carries a reason AND evidence_turn_ids,
# and the reason must be falsifiable against the transcript. Same four-act skeleton + markers as
# build_P00.py / build_02.py. Rerun: .venv/bin/python notebooks/build_11.py
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
# 11 · Evidence-based scoring

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Say why a **naked score** (`quality: 4`, no reason) is worthless to anyone who has to trust it
2. Build a **scorecard dimension** by hand — `{score, reason, evidence_turn_ids}` — from a real call
3. Run the **falsifiability test**: read the reason, pull the cited turns, and check the claim
   against the transcript yourself (the score is only as good as that check)
4. Read the `scorecard` schema (`schemas/scorecard.md`) and name what each field is for
5. Defend the rule **every score carries a reason and evidence turn ids** — deterministic or judged

Topic stays small on purpose: one call, a handful of dimensions. The *audit trail* is the point.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits on the ladder)

`10 · LLM-as-judge  →  THIS · evidence-based scoring  →  12 · calibration (judge vs human)`

Book 10 made a model hand you a **number** for a fuzzy quality ("how good was the repair?").
But a number alone is un-checkable — you cannot tell a real 0.3 from a hallucinated 0.3.
This book adds the two fields that make a number **auditable**: a *reason* (one falsifiable
sentence) and *evidence_turn_ids* (the exact turns it points at). Book 12 then asks "does the
judge's number agree with a human's?" — and that comparison only means anything once each score
already carries the evidence this book demands. No audit trail here → nothing to calibrate there.
'''))
C.append(md('''
## 3 — Baby intuition

Picture a graded exam handed back with a single red **4/10** at the top and nothing else.
No marks in the margin, no "lost 3 here for X". You cannot argue with it, learn from it, or
catch the grader's mistake. The number is final and useless at the same time.

Now picture the same 4/10 with two notes: *"−6: skipped the whole second proof"* and a circle
around the blank space where the proof should be. Suddenly the score is **checkable** — you can
look at the circled spot and confirm (or dispute) the claim. The grade did not change. What
changed is that it now comes with a **reason** and a **pointer to the evidence**. That pair is
the entire subject of this book.
'''))
C.append(md('''
## 4 — The formal version

In VoiceForge, one call is scored across several **dimensions** (barge-in, latency, repair
quality, …). Each dimension does not just produce a number — it produces a small record:

| field | plain meaning | example |
|---|---|---|
| `score` | the number, normalized 0–1 | `0.0` |
| `reason` | ONE falsifiable sentence — a claim you could check | `"agent began speaking 800ms before the user's turn ended"` |
| `evidence_turn_ids` | the exact turn ids the reason points at | `["t2", "t3"]` |

**Falsifiable** is the load-bearing word: a good reason makes a claim specific enough that you
could read the cited turns and prove it *wrong*. "The agent was rude" is not falsifiable.
"The agent interrupted at t3 while the user was still mid-sentence at t2" is — go read t2 and t3.
'''))
C.append(md('''
## 5 — Why this book exists (a score you can't audit is a liability)

VoiceForge's whole pitch is that its evals are **trustworthy**. The moment you show a founder
or a customer a dashboard of scores, the first fair question is *"says who, and why?"*. If the
answer is "the model said 4", you have a vibe, not a measurement. So the system enforces one
rule at the boundary, written into `schemas/scorecard.md`:

> every dimension — deterministic OR judged — carries a `reason` and `evidence_turn_ids`.

`pipeline/judge.py` is built to return exactly `{score, reason, evidence_turn_ids}` (it raises
if the model omits any of them). `pipeline/signals.py` attaches evidence turn ids to every
timing failure it finds. This book builds that discipline *by hand*, on a toy and on the real
hero call, before you trust any function to do it. The next cell is your first run.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just syntax.

# We print a sentence so you can see WHERE output appears (directly under the cell) and so
# your first action is a run you committed to. PREDICT - what exact text shows below?
print("a score with no reason is a number nobody can check")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What two fields must travel with every score for it to be *auditable*?
2. What does **falsifiable** mean for a reason — give a one-line example that is, and one that is not?
3. Why is "the model returned 4" not an acceptable answer when someone asks "says who, and why?"
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: an eval produces a score, and the score is the result.
After Act 1 you should hold: a bare score is a **liability**, not a result. The result is a
small record — `{score, reason, evidence_turn_ids}` — where the reason is *falsifiable* and the
evidence ids let any skeptic re-check the claim against the transcript themselves.

If that feels solid in your own words, continue. If not, re-read cell 4 (the three-field table).
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of why a naked score is a liability. Not mine - yours.
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
# Act 2 — Mechanics: from a naked score to an auditable one, by hand

## The bad output, printed RAW

Course rule: see the ugly input before transforming it. Here is the kind of thing a lazy
eval (or a rushed prompt) hands you for one dimension of one call. Read it as-is first.
'''))
C.append(code('''
# A naked score: a number and nothing else. This is the WHOLE output for the "repair_quality"
# dimension from some careless eval. We print it raw so you feel the problem before we fix it.
naked = {"dimension": "repair_quality", "quality": 4}

# Printing the raw object first is a course habit: transformed outputs make sense only once
# you have seen exactly what went in.
print(naked)
'''))
C.append(md('''
## PREDICT
Look at `{"dimension": "repair_quality", "quality": 4}`. Before running the next cell:
1. Can you tell **which call** this is about? **Which turns**?
2. Can you tell **why** it is a 4 and not a 7?
3. If you suspected the 4 was wrong, what could you do to check it? Commit to an answer out loud.
'''))
C.append(code('''
# We interrogate the naked score the way a skeptic would, and let it fail every question.
# Each .get() asks for a field that would make the score checkable; None means "not here".
print("which call?     ", naked.get("call_id"))         # no provenance
print("which turns?    ", naked.get("evidence_turn_ids"))  # no pointer to evidence
print("why this score? ", naked.get("reason"))          # no justification
print("scale 0-1?      ", naked.get("score"))           # not even a normalized number - just '4' on an unknown scale

# The verdict: every audit question returns None. The number cannot be checked, disputed,
# or learned from. That is the disease this whole book cures.
print("\\naudit verdict: un-checkable - this is a vibe wearing a number's clothes")
'''))
C.append(md('''
## Meet the real call we will score

We will not score a toy here — we will use the real **hero call** the whole course follows
(`call_C`, the Telugu-English service booking, `data/hero/turns.json`). The interesting moment
is early: the user gives a partial area, and the agent over-demands a full address instead of
acknowledging what it got. We load the turns and look at the RAW first.
'''))
C.append(code('''
# The hero call is the recurring cast member call_C. We load its turns from the real repo file
# so the evidence ids we cite are REAL ids you can look up, not invented ones.
import json
from pathlib import Path

# Resolve the path whether the notebook runs from repo root or from notebooks/ - the file is
# the single source of truth for turn ids, so we must read the actual one on disk.
here = Path.cwd()
candidates = [here / "data/hero/turns.json", here.parent / "data/hero/turns.json",
              *[p / "data/hero/turns.json" for p in here.parents]]
turns_path = next(p for p in candidates if p.exists())
call = json.loads(turns_path.read_text())

print("call_id:", call["call_id"], "| language:", call["language"], "| turns:", len(call["turns"]))
'''))
C.append(code('''
# We print the first few turns RAW - id, speaker, and text - because the evidence ids in a
# scorecard are meaningless unless you can see the turns they point at.
for t in call["turns"][:4]:
    # one line per turn, id first, so a cited id like "t3" is something you can eyeball here
    print(t["turn_id"], "|", t["speaker"], "|", t["text"])
'''))
C.append(md('''
## PREDICT
Read t2 (the user's partial answer) and t3 (the agent's reply) above. The dimension is
`repair_quality` — did the agent acknowledge the partial and ask ONE targeted follow-up (good),
or ignore it and over-demand (bad)? Decide a score from **0.0 (terrible) to 1.0 (great)** and,
just as important, the ONE sentence you would write as the reason. Commit before the next cell.
'''))
C.append(code('''
# YOUR TURN - commit your score and reason for repair_quality BEFORE we build the record.
# Storing them makes the notebook a record of YOUR judgement, to compare against the worked one.
my_repair_score = None    # <- replace None with a float 0.0 .. 1.0
my_repair_reason = ""     # <- one falsifiable sentence pointing at what the agent did

if my_repair_score is None or len(my_repair_reason.strip()) < 15:
    print("set my_repair_score (0..1) and write my_repair_reason (15+ chars), then re-run.")
else:
    print("locked:", my_repair_score, "because:", my_repair_reason)
'''))
C.append(md('''
## Build the dimension record BY HAND

Manual-before-function: we assemble the `{score, reason, evidence_turn_ids}` record as a plain
dict, naming every field, before any helper exists. This is the shape `schemas/scorecard.md`
demands for one entry in a scorecard's `dimensions` list.
'''))
C.append(code('''
# By-hand scorecard entry for ONE dimension of the hero call. Every field is here on purpose;
# the comments say WHY each exists, because the fields ARE the lesson of this book.
repair_quality = {
    "name": "repair_quality",     # which rubric dimension this scores (joins to rubric.yaml)
    "type": "judge",              # repair_quality is a JUDGED dim (a model decides); deterministic dims exist too
    "score": 0.25,                # normalized 0..1; low because the agent mishandled the partial answer
    # the reason is FALSIFIABLE: it makes a specific claim you can verify by reading t2 and t3
    "reason": "user gave a partial area at t2; agent ignored it and over-demanded full address with pincode at t3 instead of confirming the partial",
    "evidence_turn_ids": ["t2", "t3"],   # the EXACT turns the reason points at - this is the audit trail
}
print(repair_quality)
'''))
C.append(md('''
## The falsifiability test (the heart of this book)

A reason is only worth something if you can **check it**. The test has three moves:
1. Read the `reason` — what specific claim does it make?
2. Pull the turns named in `evidence_turn_ids` from the transcript.
3. Hold the claim against those turns: does the evidence support it, or refute it?

The next cell does exactly that for the record we just built — it pulls the cited turns so
you can run move 3 with your own eyes.
'''))
C.append(code('''
# We turn the list of turns into a lookup so a cited id ("t3") resolves to its actual text.
# Without this resolve step, evidence_turn_ids are just strings nobody verified.
by_id = {t["turn_id"]: t for t in call["turns"]}

# Pull ONLY the cited turns and print them next to the reason - this is the audit, performed.
print("REASON:", repair_quality["reason"], "\\n")
for tid in repair_quality["evidence_turn_ids"]:
    t = by_id[tid]   # KeyError here would mean we cited a turn that does not exist (Act 3 breaks this on purpose)
    print(f"  {tid} ({t['speaker']}): {t['text']}")

# Now YOU run move 3, out loud: does t2 show a partial answer? does t3 over-demand? If yes,
# the reason is supported and the 0.25 is defensible. That check is what makes the score real.
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not from memory): does the evidence at t2 and t3
support the reason, and therefore is the `0.25` something you could defend to a skeptic? Say why.
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
Recite the three moves of the falsifiability test. Then: what is the difference between a reason
like *"the agent was unhelpful"* and *"the agent over-demanded a full address at t3"* — which one
can a skeptic check, and what makes it checkable?
'''))
C.append(md('''
## Now the function — only after you did it by hand

You built the record by hand, so a helper now is a convenience, not a mystery. We write two
tiny functions: one to *assemble* a dimension record, and one to *audit* that its evidence ids
all exist in the call. The second is the machine version of the falsifiability test's move 2.
'''))
C.append(code('''
# make_dimension just packages the four fields. We use a helper so every dimension across the
# codebase has the SAME shape - uniformity is what lets pipeline/score.py merge them blindly.
def make_dimension(name, dim_type, score, reason, evidence_turn_ids):
    # a record with a missing reason or empty evidence is exactly the naked-score disease,
    # so we refuse to build one - the contract is enforced at construction time.
    assert reason.strip(), "a dimension needs a reason - no naked scores"
    assert evidence_turn_ids, "a dimension needs at least one evidence turn id"
    return {"name": name, "type": dim_type, "score": float(score),
            "reason": reason, "evidence_turn_ids": list(evidence_turn_ids)}


# Rebuild the same repair_quality record through the helper - identical shape, now reusable.
rq = make_dimension("repair_quality", "judge", 0.25,
                    repair_quality["reason"], ["t2", "t3"])
print(rq)
'''))
C.append(code('''
# check_evidence is the audit, automated: it confirms every cited turn id actually exists.
# An evidence id that points at no real turn is a broken audit trail - worse than no trail,
# because it LOOKS rigorous while pointing at nothing.
def check_evidence(dimension, call):
    valid_ids = {t["turn_id"] for t in call["turns"]}          # the only ids that are real
    missing = [tid for tid in dimension["evidence_turn_ids"] if tid not in valid_ids]
    return (not missing), missing   # (passes?, which ids are bogus)


ok, missing = check_evidence(rq, call)
print("evidence check passes:", ok, "| missing ids:", missing)
'''))
C.append(md('''
## The scorecard schema (one call, every dimension)

A single dimension record is one row. A **scorecard** is the whole eval for one call: a list of
those records plus a weighted `overall`. This is `schemas/scorecard.md`:

| field | meaning |
|---|---|
| `call_id` | which call this scores |
| `dimensions[]` | one `{name, type, score, reason, evidence_turn_ids}` per rubric dimension |
| `overall` | weighted average of the dimension scores (weights from `rubric.yaml`) |

The non-negotiable rule the schema states in one line: **no bare numbers anywhere** — every
dimension, deterministic or judged, carries its reason and evidence. We assemble one next.
'''))
C.append(md('''
## PREDICT
We will add a second, **deterministic** dimension: `barge_in`. The hero call has an agent
barge-in early on (the agent starts at t3 before the user's t2 has ended). Predict: will the
`reason` for a deterministic dimension be vaguer or *more* precise than the judged one — and
why? (Hint: deterministic dims are computed from exact timestamps.) Commit before running.
'''))
C.append(code('''
# A deterministic dimension's reason is built from ACTUAL numbers, so it is the most falsifiable
# kind: anyone can recompute the overlap from start_ms/end_ms. We read the two turns to get them.
t2, t3 = by_id["t2"], by_id["t3"]
overlap_ms = t2["end_ms"] - t3["start_ms"]   # t3 starts before t2 ends -> positive overlap = barge-in

# Build the barge_in dimension. score 0.0 = full penalty; the reason quotes the measured overlap
# so the claim is checkable against the timestamps, not a matter of opinion.
barge_in = make_dimension(
    "barge_in", "deterministic", 0.0,
    f"agent began speaking at t3 {overlap_ms}ms before the user's turn t2 had ended (barge-in)",
    ["t2", "t3"])
print("measured overlap:", overlap_ms, "ms")
print(barge_in)
'''))
C.append(code('''
# A scorecard is just the per-call assembly: the two dimensions plus a weighted overall.
# We read weights from rubric.yaml so 'overall' is RECOMPUTABLE, never a magic constant.
import yaml

rubric_path = next(p for p in [Path.cwd()/"rubric.yaml", *[a/"rubric.yaml" for a in Path.cwd().parents]] if p.exists())
rubric = yaml.safe_load(rubric_path.read_text())
weights = {name: d["weight"] for name, d in rubric["dimensions"].items()}

dims = [barge_in, rq]   # both carry score + reason + evidence_turn_ids - no naked numbers
# weighted average over just these two dims (a full scorecard would include all six)
overall = sum(weights[d["name"]] * d["score"] for d in dims) / sum(weights[d["name"]] for d in dims)

scorecard = {"call_id": call["call_id"], "dimensions": dims, "overall": round(overall, 3)}
print(json.dumps(scorecard, indent=2, ensure_ascii=False))
'''))
C.append(md('''
## EXPLAIN gate
One sentence: point at any single number in that scorecard and say *exactly* how a skeptic would
check it — which field tells them why, and which field tells them where to look.
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. What three things does a `scorecard` hold for one call?
2. Why is a **deterministic** dimension's reason the most falsifiable kind?
3. Where does the `overall` number come from, and why is it computed from `rubric.yaml`
   instead of being typed in by hand?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a score was a number you produce. After Act 2 you can build the auditable version by
hand — `{name, type, score, reason, evidence_turn_ids}` — *run the falsifiability test* by
pulling the cited turns, automate the evidence check, and assemble a full scorecard whose
`overall` is recomputable from `rubric.yaml`. Every number now has a why and a where.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (the record shape / the falsifiability test - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the audit trail, and the trap of the confident reason

## Break-it philosophy

The audit trail's whole value is that it *catches* a bad score. So we now feed it broken
scores on purpose and watch where it does — and does not — protect us. Surprise on your own
terms is education; a fabricated evidence id discovered on the demo stage is a disaster.
'''))
C.append(md('''
## PREDICT
We build a dimension whose `evidence_turn_ids` include `"t99"` — a turn that does not exist in
this 12-turn call. When we resolve the evidence (the `by_id[tid]` lookup), does Python **crash
loudly**, or hand back a **silently wrong** record? Commit to one before running.
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. Read what happens, do not fix it yet.

# A score that cites a turn id which does not exist. It LOOKS rigorous - it has a reason and
# evidence ids - but the trail points at nothing. We try to audit it by resolving the ids.
bogus = make_dimension("faithfulness", "judge", 0.9,
                       "agent stated the booking was confirmed, matching what the user asked",
                       ["t7", "t99"])   # <- t99 is not a real turn in this call

# Resolving each cited id is move 2 of the falsifiability test. A bogus id has no entry,
# so the dict lookup raises KeyError - the audit refuses to pretend the evidence exists.
for tid in bogus["evidence_turn_ids"]:
    print(tid, "->", by_id[tid]["text"])
'''))
C.append(md('''
## Reading the failure, and the better guard

The `KeyError: 't99'` is the audit **doing its job** — a raw dict lookup crashes rather than
invent a turn. But a crash mid-loop is a blunt instrument; in a pipeline you want a *clean
verdict*, not a traceback. That is exactly what `check_evidence` (from Act 2) gives you: it
reports which ids are bogus without blowing up. The next cell uses it to catch the same bug
gracefully — and that is the difference between code that crashes and code that *reports*.
'''))
C.append(code('''
# The graceful version of the same catch: check_evidence returns a verdict instead of crashing.
# In a real pipeline you want to FLAG the bad dimension and move on, not halt the whole run.
ok, missing = check_evidence(bogus, call)
print("bogus dimension passes evidence check:", ok)
print("bogus / non-existent evidence ids:", missing)

# The fix is to point at a real turn. Here t11 is where the agent confirms the booking.
fixed = make_dimension("faithfulness", "judge", 0.9,
                       "agent confirmed the booking for tomorrow 10am at t11, matching the user's stated slot at t8",
                       ["t8", "t11"])
ok2, missing2 = check_evidence(fixed, call)
print("fixed dimension passes evidence check:", ok2, "| missing:", missing2)
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
A fabricated evidence id is *more* dangerous than a missing one. Why? (Hint: which one looks
rigorous while being hollow?) And which tool here catches it without halting the pipeline?
'''))
C.append(md('''
## YOUR break now

Author your own broken audit trail. Build a dimension with `make_dimension`, but cite at least
one turn id that is NOT in this call. Predict exactly what `check_evidence` will report
(`ok` value? which ids in `missing`?), write the prediction as a comment, then run.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it. Cite a bad evidence id and predict the verdict.
# my prediction: <write here exactly what check_evidence will return and why>

my_broken = make_dimension(
    "language_match", "judge", 0.5,
    "agent replied in English while the user code-switched to Telugu",
    ["t6", "t_does_not_exist"],   # <- damage: change/add a bogus id here
)

# Run the audit and compare reality against your written prediction above.
ok, missing = check_evidence(my_broken, call)
print("passes:", ok, "| missing ids:", missing)
'''))
C.append(md('''
## WRONG-INTUITION TRAP 1 — a confident reason is NOT a correct score

**The wrong belief:** "if a score comes with a fluent, specific reason that cites real turn ids,
the score must be right."

A reason can be **well-formed and still false**. `check_evidence` only proves the cited turns
*exist* — it cannot prove the reason's *claim about them* is true. The next cell builds a
dimension whose reason is confident, cites two REAL turns, and passes the evidence check — yet
the transcript at those very turns refutes it. Run it, then read the cited turns yourself before
the reveal.
'''))
C.append(code('''
# This dimension is a trap: high score, fluent reason, REAL evidence ids - and check_evidence
# is perfectly happy. We are testing whether "passes the check" means "is true". It does not.
trap = make_dimension(
    "repair_quality", "judge", 0.9,
    "agent acknowledged the user's partial area at t2 and asked one gentle follow-up at t3",
    ["t2", "t3"])

ok, missing = check_evidence(trap, call)
print("trap passes evidence check:", ok, "| missing:", missing)   # True, [] - the ids are real

# Now perform move 3 of the falsifiability test: read what t3 ACTUALLY says and judge the claim.
print("\\nwhat t3 actually says:")
print(" ", by_id["t3"]["text"])
'''))
C.append(md('''
## The reveal

`check_evidence` returned `True` — every cited id is real. But read t3: the agent **demanded**
a complete address with pincode, landmark, and door number. The reason claimed a *"gentle
follow-up"*. The claim is false, and the `0.9` is a lie wearing two real turn ids as a costume.

**This is the trap at the heart of evidence-based scoring:** existence of evidence is necessary
but not sufficient. The audit trail lets a human run move 3 — *hold the claim against the cited
turns* — and that human judgement is the real check. A machine can verify the ids point
*somewhere*; only reading them verifies they point at the truth. (Book 12 exists precisely
because of this: it pits the judge's reasoned score against a human's on the same evidence.)
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: what does check_evidence prove, and what can it NOT prove?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
Two scores both "pass" `check_evidence`. One has a true reason, one has a false reason (the
trap). If the check cannot tell them apart, what is the check actually *for* — and what is the
ONLY thing that separates the true score from the false one?
'''))
C.append(md('''
## A second break: the empty reason

One more failure mode, and it is the original disease in disguise: a score that ships with an
*empty* reason. `make_dimension` refuses to build one — the contract is enforced at construction.
'''))
C.append(md('''
## PREDICT
We call `make_dimension("latency_gap", "deterministic", 0.5, "", ["t1", "t2"])` — note the
**empty string** for the reason. Recall `make_dimension` had an `assert reason.strip()`. Predict:
does this build a record with a blank reason, or does it **crash** before returning? Commit first.
'''))
C.append(code('''
# BREAK-IT (guided) - SUPPOSED to error: a naked score sneaking back in with an empty reason.
# make_dimension's assert is the boundary that keeps the no-naked-scores rule from being skipped.
sneaky = make_dimension("latency_gap", "deterministic", 0.5, "", ["t1", "t2"])
print(sneaky)   # we never reach here - the assert fires first
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a score with a reason and real evidence ids felt trustworthy. After Act 3: you know a
broken evidence id is caught (loudly by a lookup, gracefully by `check_evidence`), an empty
reason is refused at construction, and — the deep one — a *passing* evidence check still does
not make the reason true. The audit trail enables the human check; it does not replace it.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the confident-reason trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this lives, and the bar you must clear

## Where evidence-based scoring lives in VoiceForge

This is not a notebook idea — it is enforced in the real pipeline:
- **`schemas/scorecard.md`** states the contract: every dimension carries `reason` and
  `evidence_turn_ids`; "no bare numbers anywhere".
- **`pipeline/judge.py`** → `judge_dimension()` requires the model to return
  `{score, reason, evidence_turn_ids}` and *raises* if any field is missing — the same guard
  your `make_dimension` had.
- **`pipeline/signals.py`** attaches `evidence_turn_ids` to every timing failure (barge-in,
  laggy gap) it detects, so deterministic dimensions are auditable too.
- **`pipeline/score.py`** merges deterministic + judged dimensions into the scorecard and
  computes `overall` from `rubric.yaml` weights — recomputable, never hand-typed.
'''))
C.append(md('''
## Where it flows next on the ladder

The evidence trail you built is the input to two later books:
- **12 · calibration** asks "does the judge's score agree with a human's?" — and a human can
  only re-judge a call *because* the scorecard pointed them at the exact turns. No evidence ids
  → no shared ground to compare on.
- **17 · DPO pairs** turns a *detected failure* (e.g. the t3 over-demand, score 0.0, evidence
  `[t2, t3]`) into a `(chosen, rejected)` training pair — the evidence is what identifies the
  single turn to rewrite. (`schemas/improvement_example.md`.)
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

You have now scored the hero call's repair_quality (0.25) and barge_in (0.0) with full evidence.
In book 12, a human will independently score the *same* dimension on the *same* call. Predict:
will the human likely agree with these scores, disagree a little, or disagree a lot — and what
about the evidence trail would make their disagreement *productive* rather than just a clash?
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for book 12 to confront.
my_calibration_prediction = ""   # agree/disagree + why the evidence trail makes disagreement useful

if len(my_calibration_prediction.strip()) < 20:
    print("write your prediction above (agree/disagree + why), then re-run.")
else:
    print("PREDICTION STORED:", my_calibration_prediction)
'''))
C.append(md('''
## Where this idea itself fails (honesty applies to the method too)

- **Evidence theater** — citing turn ids that exist but do not actually support the claim
  (you built one in the trap). Countermeasure: a human runs move 3, reading the cited turns.
- **Reason inflation** — a fluent sentence that *sounds* falsifiable but makes no checkable
  claim ("the agent showed poor judgement"). Countermeasure: demand a claim tied to specific
  turn content, like the deterministic dims force.
- **Over-trusting the check** — treating a green `check_evidence` as "score is correct".
  Countermeasure: remember it only proves the ids are real, never that the reason is true.
- **Stale evidence** — ids that pointed at the right turns before a transcript was re-normalized
  and turn ids shifted. Countermeasure: re-run the evidence check whenever the call log changes.
'''))
C.append(md('''
## The same idea at three levels

- **To a beginner:** "don't just say the score — say why, and point at the exact spot in the
  call, so anyone can check you."
- **To an engineer:** "every dimension is `{score, reason, evidence_turn_ids}`; the reason is a
  falsifiable claim and the ids index the transcript, so any score is independently re-auditable
  — that's the contract `judge.py` enforces and `score.py` assembles."
- **To a founder:** "our scores aren't opinions — each one shows its work and links to the
  moment in the call that justifies it, so a customer can verify any number we put on a slide."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "Your judge returns a score AND a reason — what stops it from just making up a
plausible-sounding reason?"**
<details><summary>answer</summary>Nothing stops the model from writing a fluent reason — which is exactly why the reason must cite evidence_turn_ids and be falsifiable. A human (book 12) re-reads the cited turns and checks the claim; the evidence trail makes that re-check cheap. We never claim the model is honest; we make it auditable.</details>

**2. "Deterministic dimensions are just math — why bother attaching a reason and evidence to
those?"**
<details><summary>answer</summary>So every number on the dashboard is checkable the same way, with no special cases. A barge-in score of 0.0 carries "800ms overlap at t2→t3" so a skeptic can recompute it from the timestamps. Uniform shape is what lets score.py merge judged and deterministic dims and lets anyone audit any number identically.</details>

**3. "A score has a reason and the evidence ids all exist — is the score correct?"**
<details><summary>answer</summary>Not necessarily. Existing evidence is necessary, not sufficient — the reason's claim about those turns can still be false (the trap we built: a "gentle follow-up" reason citing a turn that actually over-demanded). The audit trail enables a human to verify the claim; it does not replace that verification.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: where the no-naked-scores rule is enforced in the real code
(`schemas/scorecard.md`, `judge.py`, `signals.py`, `score.py`), how the evidence trail feeds
calibration (12) and DPO pairs (17), the method's own failure modes, and how to defend the
contract at three levels — including the hard truth that a passing evidence check is not proof
the reason is true.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. Why a naked score (`quality: 4`) is a liability — name the two missing fields
2. The shape of one dimension record, and what `type` distinguishes
3. The three moves of the falsifiability test
4. What `check_evidence` proves — and the one thing it can NOT prove (the trap)
5. One real place in the pipeline this rule is enforced, and one book downstream that needs it

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (where it lives / where it flows)
my_clean_sentence = ""      # the sentence you'd say in a room about evidence-based scoring

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"A score you cannot audit is a vibe."**

If yours captures that in your own words — a number with no reason and no evidence is a feeling
dressed as a measurement — this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "11_evidence_based_scoring.ipynb"   # this notebook's filename
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

**11 done** (pending your teach-back) → **12 · calibration** — now that every score carries a
reason and evidence, you hand the *same* calls to a human, collect their scores on the same
evidence, and measure agreement (Cohen's kappa). The trail you built here is what makes that
comparison fair: judge and human are looking at the same cited turns.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "11_evidence_based_scoring.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
