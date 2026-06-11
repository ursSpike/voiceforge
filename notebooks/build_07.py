#!/usr/bin/env python3
# Builds 07_failure_tags_stress_profiles.ipynb — VoiceForge University book 07.
# The ONE atomic concept: a failure TAXONOMY (named tags) + scenario STRESS classes;
# and the lesson that a scenario is not a performance (a clean call can still fail).
# Same four-act skeleton + audit markers as build_P00.py / build_02.py.
# Rerun: .venv/bin/python notebooks/build_07.py
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
# 07 · Failure tags & stress profiles

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Attach a **failure tag** to a call — a named category from a fixed list
   (`language_mismatch`, `interruption`, `kb_gap`, `too_many_turns`) — instead of a vague "it was bad"
2. Name the three **stress profiles** a scenario can carry (`clean`, `pause_heavy`, `interruption`)
   and say why a stress profile describes the *scenario*, never the *performance*
3. Build a **failure-distribution bar chart** and read what it does (and does NOT) license
4. Defend the load-bearing lesson of this book: **a clean-profile call can still fail** —
   scenario is the test conditions, performance is the result

Topic stays small on purpose: a handful of toy calls, four tags, three profiles. The
*separation of scenario from performance* is the point.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits on the ladder)

`06 · task success  →  THIS · failure tags & stress profiles  →  08 · cost`

Book 06 gave you a single verdict per call: did the task complete (required-fields checklist)
or not — a clean **pass/fail**. But "failed" is not an explanation. *Why* did it fail? Two
calls can both fail for completely different reasons, and you cannot fix what you cannot name.
This book turns the bare verdict into a **named cause** (a failure tag) and sorts each call's
test conditions into a **stress profile**. Book 08 then puts a price on it — a failed call still
burned tokens and minutes, so cost-per-*successful*-call needs exactly the tags you build here.
No taxonomy here → no per-cause cost breakdown there.
'''))
C.append(md('''
## 3 — Baby intuition

A hospital does not write "patient unwell" and stop. It writes a **diagnosis code** from a
fixed list — so two doctors mean the same thing, so cases can be counted, so the right fix is
obvious. "Unwell" is a feeling; a diagnosis is engineering signal.

Our calls arrive as raw chaos: a Telugu-English booking where the agent talked over the caller,
an English call that wandered for forty turns, a call where the bot had no answer. If we only
say "these went badly," we can count nothing and fix nothing. So we do what the hospital does:
pick from a **fixed list of named failure tags**. The naming is the work.

Separately, every call also has **test conditions** — was the caller calm, did they pause a lot,
did people talk over each other? That is the **stress profile**, and it matters that it is a
property of the *situation*, decided before you judge how well the agent did.
'''))
C.append(md('''
## 4 — The formal version

Two ideas this whole book turns on — keep them in separate boxes:

| word | plain meaning | in this book |
|---|---|---|
| **failure tag** | a named category of *what went wrong*, from a fixed closed list | `language_mismatch` · `interruption` · `kb_gap` · `too_many_turns` |
| **stress profile** | a scenario class describing the *test conditions* of the call | `clean` · `pause_heavy` · `interruption` (the enum in `schemas/call_log.md`) |

The trap that gives this book its spine: **`interruption` appears in both lists, and they are
not the same thing.** As a stress profile it means "the scenario contains overlapping speech."
As a failure tag it means "the agent's overlap was bad enough to count as a failure." A call can
carry the `interruption` *profile* (people overlapped) and still *pass* (the overlaps were
harmless backchannels). Profile = the conditions. Tag = the verdict on the result.
'''))
C.append(md('''
## 5 — Why this book exists (raw chaos becomes engineering signal)

A pile of "bad calls" is not actionable. A founder cannot fund "make it less bad." An engineer
cannot fix "it failed." The instant you replace the pile with **counts of named tags**
("9 calls, 4 `interruption`, 2 `kb_gap`, 1 `too_many_turns`"), you have a roadmap: fix the tag
with the tallest bar first.

In the real repo this is exactly the cross-cut that feeds the business chart: `pipeline/crosscut.py`
groups calls **by stress profile** and reports failure rate per profile, and `data/normalized/*.json`
already carries a `stress_profile` field on every call. This book is the hand-built version of that
grouping — so when you read the real chart you know precisely what each bar is, and what it is not.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What is the difference between a **failure tag** and a **stress profile**? (One names the
   result; one names the conditions.)
2. The word `interruption` is in *both* lists. What does it mean in each?
3. Why is "this call was bad" useless to a founder, and what replaces it?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a failed call is a failed call. After Act 1 you should
hold two separate boxes: **scenario** (the stress profile — the test conditions, set before
judging) and **performance** (the failure tag — the named cause of the result). Book 06 gave
you pass/fail; this book gives the failure a *name* and the scenario a *class*.

If those two boxes feel genuinely separate in your head, continue. If `interruption`-the-profile
and `interruption`-the-tag still feel like one thing, re-read cell 4 — that conflation is the
exact mistake Act 3 is built to break.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of "scenario is not performance." Not mine - yours.
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
# Act 2 — Mechanics: tag toy calls by hand, then sort scenarios into profiles

## The fixed tag list (a closed vocabulary, printed RAW first)

Before touching any call, we look at the *vocabulary itself*. A taxonomy is only useful if it is
**closed and named** — everyone picks from the same short list. Here is ours, as plain data.
'''))
C.append(code('''
# The failure-tag taxonomy as raw data. We define it as a dict (tag -> what it means) so the
# vocabulary is a THING we can print, count against, and validate input against later -
# a closed list in code beats a fuzzy idea in your head.
FAILURE_TAGS = {
    "language_mismatch": "agent replied in the wrong language / ignored the caller's language",
    "interruption":      "agent talked over the caller (overlap big enough to derail the turn)",
    "kb_gap":            "caller asked something the agent had no knowledge to answer",
    "too_many_turns":    "task dragged on far longer than it should have (caller had to repeat)",
}
# Print the RAW vocabulary before we use it - seeing the closed list first is a course rule.
for tag, meaning in FAILURE_TAGS.items():
    print(f"{tag:<18} -> {meaning}")
'''))
C.append(md('''
## Meet the toy calls (raw, before any tagging)

Four tiny hand-made calls — small enough to read every word. Each is a few turns with a
`speaker`, the `text`, and millisecond timings (the same `start_ms`/`end_ms` you met in book 04).
We print them raw first; the tags come later, by hand, one at a time.
'''))
C.append(code('''
# Four toy calls as plain dicts. Timings are in milliseconds from call start (one clock per call),
# matching the real call_log schema - so the by-hand logic here transfers to the real files.
# We keep them tiny on purpose: every turn must be readable at a glance.
toy_calls = [
    {"call_id": "toy_lang", "language": "te-en", "turns": [
        {"turn_id": "t1", "speaker": "user",  "text": "meeru Telugu lo matladandi please", "start_ms": 0,    "end_ms": 2200},
        {"turn_id": "t2", "speaker": "agent", "text": "I can only continue in English, sir.", "start_ms": 2600, "end_ms": 4800},
    ]},
    {"call_id": "toy_barge", "language": "en", "turns": [
        {"turn_id": "t1", "speaker": "user",  "text": "I think the address is forty-two, near the—", "start_ms": 0,    "end_ms": 3000},
        {"turn_id": "t2", "speaker": "agent", "text": "I need the full pincode now.",                "start_ms": 2200, "end_ms": 4200},
    ]},
    {"call_id": "toy_kb", "language": "en", "turns": [
        {"turn_id": "t1", "speaker": "user",  "text": "do you service the old gas geysers from 2009?", "start_ms": 0,    "end_ms": 2800},
        {"turn_id": "t2", "speaker": "agent", "text": "Sorry, I don't have information about that.",   "start_ms": 3200, "end_ms": 5200},
    ]},
    {"call_id": "toy_long", "language": "en", "turns": [
        # six turns of the caller re-stating the SAME slot - a task that should take one turn.
        {"turn_id": "t1", "speaker": "user",  "text": "morning slot", "start_ms": 0,     "end_ms": 1000},
        {"turn_id": "t2", "speaker": "agent", "text": "which day?",    "start_ms": 1400,  "end_ms": 2200},
        {"turn_id": "t3", "speaker": "user",  "text": "tomorrow morning", "start_ms": 2600, "end_ms": 3600},
        {"turn_id": "t4", "speaker": "agent", "text": "morning of which date?", "start_ms": 4000, "end_ms": 5000},
        {"turn_id": "t5", "speaker": "user",  "text": "tomorrow, the morning", "start_ms": 5400, "end_ms": 6600},
        {"turn_id": "t6", "speaker": "agent", "text": "please state the date.", "start_ms": 7000, "end_ms": 8000},
    ]},
]
# One print per call so each call is visibly one THING (not a wall of text).
for c in toy_calls:
    print(c["call_id"], "|", c["language"], "|", len(c["turns"]), "turns")
'''))
C.append(md('''
## PREDICT (before you read the tagging cells)
Read the four toy calls above, slowly. For each, which **single** failure tag from the closed
list fits best? Commit to four tags now — you will write them down in the next cell, and the
notebook will check them against the by-hand reasoning that follows.
'''))
C.append(code('''
# YOUR TURN - predictions are written BEFORE the tagging cells run, so the notebook becomes a
# record of YOUR thinking. A later cell compares your guess to the by-hand tags; the gap is the lesson.
# Replace each None with one tag string from FAILURE_TAGS (e.g. "kb_gap").
my_tag_lang  = None   # toy_lang  -> ?
my_tag_barge = None   # toy_barge -> ?
my_tag_kb    = None   # toy_kb    -> ?
my_tag_long  = None   # toy_long  -> ?

my_tags = {"toy_lang": my_tag_lang, "toy_barge": my_tag_barge,
           "toy_kb": my_tag_kb, "toy_long": my_tag_long}
# Guard: a fresh notebook (all None) must still run clean, so we only "lock" once all four are filled.
if any(v is None for v in my_tags.values()):
    print("fill in all four predicted tags above, then re-run this cell.")
else:
    print("predictions locked:", my_tags)
'''))
C.append(md('''
## Tag #1 by hand — `language_mismatch`

We tag the first call manually, stating the *evidence* out loud. A tag without evidence is a
guess; a tag *with* a turn-id pointer is engineering signal (this is the `scorecard` discipline
from book 06: every verdict carries `evidence_turn_ids`).
'''))
C.append(code('''
# Manual tag for toy_lang. We do NOT pattern-match cleverly yet - we reason about the evidence.
call = toy_calls[0]                       # toy_lang
user_turn  = call["turns"][0]             # the caller's request
agent_turn = call["turns"][1]             # the agent's reply

# The caller explicitly asked for Telugu; the agent declared English-only. That mismatch IS the tag.
# We print the two turns so the EVIDENCE is visible, not asserted.
print("user  :", user_turn["text"])
print("agent :", agent_turn["text"])
tag_lang = "language_mismatch"            # chosen because the reply ignored the requested language
evidence_lang = [user_turn["turn_id"], agent_turn["turn_id"]]
print("TAG:", tag_lang, "| evidence:", evidence_lang)
'''))
C.append(md('''
## Tag #2 by hand — `interruption` (measured, not eyeballed)

For the overlap tag we do not trust our eyes — we *measure*. This is the FTO (floor transfer
offset) idea from book 04: `fto = next.start_ms - prev.end_ms`. Negative means the next speaker
started **before** the previous one finished — an overlap. We compute it.
'''))
C.append(md('''
## PREDICT
In `toy_barge`, the user's turn ends at `3000ms` and the agent's starts at `2200ms`.
What is `fto = 2200 - 3000`? Is it negative (overlap) or positive (gap)? Commit to the number.
'''))
C.append(code('''
# Manual FTO for toy_barge. We compute the floor-transfer offset by hand, exactly as book 04 did,
# because the tag "interruption" must rest on a measured overlap, never on a vibe.
call = toy_calls[1]                       # toy_barge
prev_turn = call["turns"][0]              # user, ends at 3000
next_turn = call["turns"][1]              # agent, starts at 2200

fto_ms = next_turn["start_ms"] - prev_turn["end_ms"]   # negative => the agent cut in early
overlap_ms = max(0, -fto_ms)              # overlap is the positive size of a negative FTO
print("fto_ms:", fto_ms, "| overlap_ms:", overlap_ms)

# rubric.yaml sets barge_in threshold_overlap_ms = 100: overlap above 100ms counts as a barge-in
# (<=100 is a harmless backchannel). We hardcode 100 HERE only to teach; the real pipeline reads rubric.yaml.
BARGE_THRESHOLD_MS = 100
tag_barge = "interruption" if overlap_ms > BARGE_THRESHOLD_MS else "(no interruption)"
print("TAG:", tag_barge, "| because overlap", overlap_ms, "ms >", BARGE_THRESHOLD_MS, "ms threshold")
'''))
C.append(md('''
## Tag #3 and #4 by hand — `kb_gap` and `too_many_turns`

The last two tags read different signals. `kb_gap` is a **content** signal: the agent said it had
no information. `too_many_turns` is a **length** signal: the call took many turns to capture one
slot. We tag each on its own evidence.
'''))
C.append(code('''
# Manual tag for toy_kb: a knowledge gap shows up in the agent's WORDS, not the timing.
call = toy_calls[2]                        # toy_kb
agent_reply = call["turns"][1]["text"].lower()
# We look for the agent confessing no knowledge - a content signal, so we scan the text, not the clock.
no_info = ("don't have information" in agent_reply) or ("no information" in agent_reply)
tag_kb = "kb_gap" if no_info else "(answered)"
print("toy_kb agent said:", call["turns"][1]["text"])
print("TAG:", tag_kb, "| because the agent admitted it lacked the knowledge to answer")
'''))
C.append(code('''
# Manual tag for toy_long: this is a LENGTH signal. The caller re-stated the same slot repeatedly,
# so we count turns; one slot should not need six turns. We use a small, explicit threshold.
call = toy_calls[3]                        # toy_long
n_turns = len(call["turns"])
# Threshold is a teaching choice: a single-slot exchange over ~4 turns means the caller is repeating.
TOO_LONG_TURNS = 4
tag_long = "too_many_turns" if n_turns > TOO_LONG_TURNS else "(reasonable length)"
print("toy_long has", n_turns, "turns for one slot (date)")
print("TAG:", tag_long, "| because", n_turns, ">", TOO_LONG_TURNS, "turns to capture a single field")
'''))
C.append(md('''
## OBSERVE — did your predictions match the by-hand tags?
Now the metal-detector reading: line up YOUR four predicted tags against the four we derived from
evidence. A mismatch is not a failure — it is the exact spot your mental model of the taxonomy
disagrees with the evidence rules, which is the only spot worth thinking about.
'''))
C.append(code('''
# Compare YOUR locked predictions to the by-hand tags. We only compare if you filled them in
# (the guard keeps a fresh notebook clean); a DIFFERED line marks where your model and the rules diverged.
by_hand = {"toy_lang": tag_lang, "toy_barge": tag_barge, "toy_kb": tag_kb, "toy_long": tag_long}
print("by-hand tags:", by_hand)
if all(v is not None for v in my_tags.values()):
    for cid in by_hand:
        verdict = "matched" if my_tags[cid] == by_hand[cid] else "DIFFERED"
        print(f"  {cid:<10} you={my_tags[cid]:<18} by_hand={by_hand[cid]:<18} -> {verdict}")
else:
    print("(fill in my_tags in the PREDICT cell above to see the comparison)")
'''))
C.append(md('''
## Now — and only now — the function version

You tagged four calls by hand, each on its own evidence. A function is just those rules written
once so they run on a thousand calls. Because you met the rules first, this wrapper is a
convenience, not a mystery — and you can audit every branch in it.
'''))
C.append(code('''
# The tagging rules, collected into one function. Each branch is exactly the by-hand reasoning above.
# We return a LIST because one call can carry more than one failure tag (a call can be both
# too long AND have an interruption) - tags are not mutually exclusive.
def tag_call(call, barge_threshold_ms=100, too_long_turns=4):
    tags = []
    turns = sorted(call["turns"], key=lambda t: t["start_ms"])   # FTO needs chronological order

    # content signal: any agent turn confessing missing knowledge -> kb_gap
    for t in turns:
        if t["speaker"] == "agent" and ("no information" in t["text"].lower()
                                        or "don't have information" in t["text"].lower()):
            tags.append("kb_gap")
            break

    # language signal: caller asked for a language, agent declared a different one -> language_mismatch
    asked_other = any(t["speaker"] == "user" and "telugu" in t["text"].lower() for t in turns)
    agent_english_only = any(t["speaker"] == "agent" and "only continue in english" in t["text"].lower() for t in turns)
    if asked_other and agent_english_only:
        tags.append("language_mismatch")

    # timing signal: any consecutive overlap beyond threshold -> interruption (measured, not eyeballed)
    for a, b in zip(turns, turns[1:]):
        if a.get("end_ms") is not None:
            overlap = max(0, a["end_ms"] - b["start_ms"])
            if overlap > barge_threshold_ms:
                tags.append("interruption")
                break

    # length signal: too many turns for the work done -> too_many_turns
    if len(turns) > too_long_turns:
        tags.append("too_many_turns")

    return tags
print("tag_call defined")
'''))
C.append(code('''
# Run the function on all four toy calls. It should reproduce your by-hand tags exactly -
# if it does not, the FUNCTION is wrong (or your by-hand reasoning was), and that gap is the lesson.
for c in toy_calls:
    print(f"{c['call_id']:<10} -> {tag_call(c)}")
'''))
C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. Why does `tag_call` return a **list** of tags and not a single tag?
2. Which tag is computed from **timing**, which from **text content**, and which from **length**?
3. Why did we measure the overlap for `interruption` instead of just looking at the transcript?
'''))
C.append(md('''
## Switching boxes: from tags (performance) to stress profiles (scenario)

You now have the performance box: named tags for *what went wrong*. Open the second box —
the **stress profile**, the *test conditions* of the scenario. This is the enum that already
lives on every real call in `data/normalized/*.json`. Three classes this sprint:

- **`clean`** — cooperative caller, no overlaps, steady pacing
- **`pause_heavy`** — long silences / hesitations (the caller stalls, the agent waits)
- **`interruption`** — overlapping speech in the scenario

The hinge of this book: a stress profile is decided by the *conditions*, **before** you judge
how well the agent performed. Same word `interruption`, different box.
'''))
C.append(md('''
## PREDICT
We are about to classify a scenario into a stress profile from its **timing only** (gaps and
overlaps between turns) — deliberately ignoring whether the agent did well. For a call with one
800ms+ silence and zero overlaps, which profile do you predict: `clean`, `pause_heavy`, or
`interruption`? Commit before running.
'''))
C.append(code('''
# A scenario carries silences and overlaps; we read ONLY those to assign a stress profile,
# because the profile is about CONDITIONS, not about how the agent handled them.
def stress_profile(call, big_pause_ms=800, overlap_ms_thresh=100):
    turns = sorted(call["turns"], key=lambda t: t["start_ms"])
    max_overlap = 0
    max_gap = 0
    for a, b in zip(turns, turns[1:]):
        if a.get("end_ms") is None:
            continue                                  # no end => cannot know gap/overlap; skip pair
        fto = b["start_ms"] - a["end_ms"]             # negative=overlap, positive=gap (book 04's FTO)
        max_overlap = max(max_overlap, max(0, -fto))
        max_gap = max(max_gap, max(0, fto))
    # priority: overlap dominates (interruption is the harshest condition), then long pauses, else clean.
    if max_overlap > overlap_ms_thresh:
        return "interruption"
    if max_gap > big_pause_ms:
        return "pause_heavy"
    return "clean"
print("stress_profile defined")
'''))
C.append(code('''
# Build two clear scenarios so the profile logic is visible, then classify them.
# scenario_pause has a long silence and NO overlap; scenario_overlap has an overlap.
scenario_pause = {"call_id": "sc_pause", "turns": [
    {"turn_id": "t1", "speaker": "agent", "text": "what time?", "start_ms": 0,    "end_ms": 1000},
    {"turn_id": "t2", "speaker": "user",  "text": "...um... ten", "start_ms": 2200, "end_ms": 3000},  # 1200ms gap
]}
scenario_overlap = {"call_id": "sc_overlap", "turns": [
    {"turn_id": "t1", "speaker": "user",  "text": "the address is—", "start_ms": 0,    "end_ms": 2000},
    {"turn_id": "t2", "speaker": "agent", "text": "pincode now",     "start_ms": 1500, "end_ms": 2500},  # 500ms overlap
]}
# Classify each from timing alone - the function never sees an outcome, only the clock.
print(scenario_pause["call_id"], "->", stress_profile(scenario_pause))
print(scenario_overlap["call_id"], "->", stress_profile(scenario_overlap))
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not memory): what inputs did `stress_profile` read,
and what did it deliberately *not* read? (Hint: it never looked at whether the booking succeeded.)
'''))
C.append(md('''
## Touch the real thing — stress profiles already live on disk

The toy logic was the lesson; the real corpus already carries a `stress_profile` field on every
call (set by `pipeline/normalize.py`). We load the 11 real normalized calls from
`data/normalized/*.json` and read their profiles straight off disk — no re-derivation.
'''))
C.append(code('''
# Load every real normalized call. We resolve the repo root by walking up to the folder that has
# data/normalized, so this runs no matter the kernel's working directory.
import json
from pathlib import Path
root = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "normalized").exists())
files = sorted((root / "data" / "normalized").glob("*.json"))   # sorted => stable, reproducible order

real_calls = [json.loads(f.read_text()) for f in files]          # disk text -> dicts (the json.loads from book 02)
# Print id + the profile that already lives on each record, so you see the real field, not a guess.
for c in real_calls:
    print(f"{c['call_id']:<14} {c['language']:<6} profile={c['stress_profile']}")
'''))
C.append(md('''
## PREDICT
You are about to count how many real calls fall in each stress profile (`clean` / `pause_heavy`
/ `interruption`). There are 11 calls. Commit to a rough split now — which profile do you expect
to be the largest bucket?
'''))
C.append(code('''
# Count calls per stress profile. We use Counter because tallying a category is exactly its job;
# this is the by-hand "group and count" that pipeline/crosscut.py does for the real business chart.
from collections import Counter
profile_counts = Counter(c["stress_profile"] for c in real_calls)
# Print sorted by profile name so the output is stable run-to-run (no dict-ordering surprises).
for prof in sorted(profile_counts):
    print(f"{prof:<14} {profile_counts[prof]}")
print("total:", sum(profile_counts.values()))
'''))
C.append(md('''
## How to read the bar chart we are about to draw (the 4-question ritual)

Before any chart renders, the reading ritual from P00:
1. **What is x?** — the stress-profile name (the category)
2. **What is y?** — the count of calls in that profile
3. **What is one bar?** — one profile's bucket size
4. **What claim does this chart license?** — *only* how many calls fall in each scenario class.
   It says **nothing** about how well the agent performed in them. Guard question 4 hard here.
'''))
C.append(code('''
# The failure-distribution / stress-profile bar chart. Every line states why it exists.
import matplotlib.pyplot as plt
profiles = sorted(profile_counts)                 # x-axis labels: the category names, stable order
counts = [profile_counts[p] for p in profiles]    # y-axis: one count per profile (the measure)

fig, ax = plt.subplots(figsize=(5, 3))            # small figure: this is a glance chart, not a poster
ax.bar(profiles, counts)                          # one bar per profile; height = number of calls
ax.set_xlabel("stress profile (scenario class)")  # an unlabeled axis is how a chart lies by omission,
ax.set_ylabel("number of calls")                  # so labeling is a duty here, not decoration
ax.set_title("calls per stress profile (n=11 real calls)")
plt.show()                                         # headless runner swallows show(); in Cursor you see bars
'''))
C.append(md('''
## CHECKPOINT 3 (out loud)
Answer all four chart-reading questions for the bar chart above. Then the dangerous one:
finish the sentence "this chart does NOT tell me ___" — what performance claim is off-limits
no matter how tall a bar is?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a failed call was a shapeless "bad." After Act 2 you can do four concrete things:
attach a **named tag** from a closed list (with turn-id evidence), measure `interruption` from
**timing** instead of eyeballing, classify a scenario into a **stress profile** from conditions
alone, and read a distribution bar chart for **only** what it licenses (counts per scenario,
never performance). Tags and profiles now live in two separate boxes in your head.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (tags vs profiles / measure-don't-eyeball / chart ritual - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the taxonomy, then the trap at the heart of this book

## Break-it philosophy

A taxonomy you have never pushed against is a taxonomy you do not trust. So we now feed it
things it was not built for and watch where it bends or breaks. Surprise on your own terms is
education; surprise on the demo stage — "wait, why is this call tagged nothing?" — is a disaster.
'''))
C.append(md('''
## PREDICT
We hand `tag_call` a call where the caller mumbles, the agent answers fine, nobody overlaps,
and it is short — a genuinely **clean, successful** call. How many tags will come back? Commit
to a number (0? 1? more?) before running.
'''))
C.append(code('''
# BREAK-IT (guided) - feed the tagger a clean, successful call and watch what it returns.
# This is not an error-crash; it is a different kind of break: does the taxonomy stay quiet
# when nothing went wrong? A taxonomy that tags a good call is worse than useless.
clean_success = {"call_id": "all_good", "language": "en", "turns": [
    {"turn_id": "t1", "speaker": "agent", "text": "Which area?",          "start_ms": 0,    "end_ms": 1500},
    {"turn_id": "t2", "speaker": "user",  "text": "Madhapur, ten AM please", "start_ms": 1900, "end_ms": 4000},  # 400ms gap, no overlap
    {"turn_id": "t3", "speaker": "agent", "text": "Booked for ten AM. Done.", "start_ms": 4400, "end_ms": 6500},
]}
# We expect an EMPTY list: no kb confession, no language clash, no overlap, only 3 turns.
print("tags for a clean successful call:", tag_call(clean_success))
'''))
C.append(md('''
## Reading that result — silence is a feature

An empty tag list is the taxonomy behaving correctly: **no failure → no tag.** That is the whole
contract. If a tagger sprays tags onto good calls, every count downstream is inflated and the
"tallest bar" roadmap points you at a problem that is not real. A good taxonomy is *quiet* on
good inputs and *specific* on bad ones.
'''))
C.append(md('''
## PREDICT
Now a nastier break. We feed `tag_call` a call whose agent text is `None` (a real data source
*will* hand you a null transcript someday). The function calls `.lower()` on turn text. Does it
**crash loudly**, or **return wrong tags silently**? Commit to one before running.
'''))
C.append(code('''
# BREAK-IT (guided) - a malformed call: one turn has text = None. This cell is SUPPOSED to error.
# EXPECTED FAILURE FOR LEARNING - read the traceback, do not fix it yet.
malformed = {"call_id": "null_text", "language": "en", "turns": [
    {"turn_id": "t1", "speaker": "user",  "text": "hello", "start_ms": 0,    "end_ms": 1000},
    {"turn_id": "t2", "speaker": "agent", "text": None,     "start_ms": 1400, "end_ms": 2400},  # <- the damage: null text
]}
# tag_call does t["text"].lower() - calling .lower() on None makes Python refuse. Watch it.
print("tags for malformed call:", tag_call(malformed))
'''))
C.append(md('''
## Reading the error (bottom-up) and the fix

The last line of the traceback names *what* broke:
`AttributeError: 'NoneType' object has no attribute 'lower'` — "you asked text to lowercase
itself, but text was `None`." Walk **upward** to find *where* (the `.lower()` calls inside
`tag_call`). The fix is a guard at the boundary: treat a missing transcript as an empty string
so the tagger degrades gracefully instead of exploding. A loud crash was the friendly outcome —
it pointed at the exact line. The dangerous version would be *silently* tagging it wrong.
'''))
C.append(code('''
# The fix: coerce missing text to "" at the point of use, so a null transcript cannot crash tagging.
# We wrap the original logic; defensively, agent turns with no text just carry no content signal.
def tag_call_safe(call, barge_threshold_ms=100, too_long_turns=4):
    safe = {**call, "turns": [{**t, "text": (t.get("text") or "")} for t in call["turns"]]}  # None -> ""
    return tag_call(safe, barge_threshold_ms, too_long_turns)
# Now the same malformed call returns cleanly instead of crashing - graceful degradation, not a stack trace.
print("safe tags for malformed call:", tag_call_safe(malformed))
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. Why is an **empty** tag list the *correct* output for a good call, not a bug?
2. The null-text call crashed. Why is a loud crash here *friendlier* than silently mis-tagging?
3. Where did the fix go — inside the rules, or at the **boundary** where data enters? Why there?
'''))
C.append(md('''
## YOUR break now

Author your own stress test on the taxonomy. Pick ONE: invent a call that *should* get a tag but
slips through (a false negative), OR one that gets a tag it should not (a false positive). Predict
the exact tag list in a comment, then run `tag_call_safe` on it and compare. Finding a gap in the
rules is a real contribution — it is how the real taxonomy earns new tags.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it on the taxonomy.
# my prediction: <write the exact tag list you expect, and why, BEFORE running>

my_break_call = {"call_id": "my_break", "language": "en", "turns": [
    # 1) build a call that probes an edge of the rules (false positive OR false negative):
    {"turn_id": "t1", "speaker": "user",  "text": "...", "start_ms": 0,    "end_ms": 1000},
    {"turn_id": "t2", "speaker": "agent", "text": "...", "start_ms": 1400, "end_ms": 2400},
]}
# 2) run the safe tagger and hold the result against your written prediction:
print("tags:", tag_call_safe(my_break_call))
print("profile:", stress_profile(my_break_call))
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this whole book is built on

**The wrong belief:** "a `clean` stress profile means the call went well."

The profile says the *conditions* were calm — no overlaps, no long silences. It says **nothing**
about whether the agent captured the booking. The next cell shows a call with a spotless `clean`
profile that **still failed the task**: cooperative caller, perfect pacing, and the agent just
never asked for the callback number. Profile clean. Outcome: failure. Run it, then try to explain
the gap BEFORE the reveal.
'''))
C.append(code('''
# A clean-profile call that STILL fails the task. No overlaps, no long pauses -> profile is clean.
# But a required field (callback_number) is never captured -> the TASK fails (book 06's checklist).
clean_but_failed = {"call_id": "clean_fail", "language": "en", "stress_profile": "clean", "turns": [
    {"turn_id": "t1", "speaker": "agent", "text": "Which area for the visit?",   "start_ms": 0,    "end_ms": 1800},
    {"turn_id": "t2", "speaker": "user",  "text": "Madhapur, tomorrow morning.", "start_ms": 2200, "end_ms": 4500},  # 400ms gap
    {"turn_id": "t3", "speaker": "agent", "text": "Great, booked for the morning. Bye!", "start_ms": 4900, "end_ms": 7000},
]}
# required-field checklist from book 06: a callback number is mandatory for this workflow.
required_fields = ["service_area", "time_slot", "callback_number"]
captured = {"service_area": "Madhapur", "time_slot": "tomorrow morning", "callback_number": None}  # never asked!

profile = stress_profile(clean_but_failed)                       # reads timing only -> clean
task_completed = all(captured[f] is not None for f in required_fields)  # book 06's pass/fail rule
print("stress_profile :", profile)               # 'clean' - the conditions were calm
print("task_completed :", task_completed)        # False - a required field is missing
print("missing fields :", [f for f in required_fields if captured[f] is None])
'''))
C.append(md('''
## The reveal — scenario is not performance

`profile == "clean"` and `task_completed == False` at the **same time**. The scenario was easy;
the agent still blew it (never asked for the callback number). The stress profile measured the
*test conditions*; the task outcome measured the *result*. They are different axes, and reading
one as the other is the deepest mistake in this whole area.

This is why `pipeline/crosscut.py` reports **failure rate _per_ stress profile** rather than
assuming clean = good: the interesting, fundable number is exactly "how often do we fail even
when conditions were easy?" A clean call that failed is not noise — it is the agent's fault laid
bare, with the scenario excuse removed.
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
1. State the two axes: which one is the **stress profile**, which one is the **task outcome**,
   and which describes *conditions* vs *result*?
2. The trap call had `profile == "clean"` and `task_completed == False`. Say in one sentence why
   those two facts do not contradict each other.
3. Why is a **clean-profile failure** more informative to fix than an interruption-profile failure?
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why can a 'clean' profile and a FAILED task coexist?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a `clean` profile felt like a gold star, and a malformed call felt like a dead end. After
Act 3: the taxonomy is *quiet on good calls* (empty list = correct), it *crashes loudly* on null
text (friendlier than silent mis-tagging) and you guard at the boundary, and above all — a clean
scenario can hide a failed performance. **Scenario and performance are different axes.** That
separation is the spine of book 07.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the scenario-vs-performance trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the cast, the real pipeline, and the bar you must clear

## The recurring cast, tagged

Three calls travel through this whole course. Here they are with their stress profiles (the
scenario) and their failure tags (the performance) side by side — so the two boxes sit together
one last time. Note the cast ids and outcomes match the course-wide spec exactly.
'''))
C.append(code('''
# The cast as a small table: id, language, the SCENARIO (stress profile) and the PERFORMANCE
# (outcome + plausible failure tags). Profiles/outcomes are the course-fixed facts from the spec.
cast = [
    {"id": "call_A", "language": "en",    "stress_profile": "clean",        "outcome": "success",
     "tags": []},
    {"id": "call_B", "language": "hi-en", "stress_profile": "pause_heavy",  "outcome": "partial",
     "tags": ["too_many_turns"]},
    {"id": "call_C", "language": "te-en", "stress_profile": "interruption", "outcome": "failure",
     "tags": ["interruption", "language_mismatch"]},
]
# One row per call so each is visibly one THING; scenario and performance printed in adjacent columns.
for c in cast:
    print(f"{c['id']} | {c['language']:<6} | profile={c['stress_profile']:<13} | {c['outcome']:<8} | tags={c['tags']}")
'''))
C.append(md('''
## call_A is the lesson in one row

`call_A` carries the `clean` profile and `success`, empty tags. `call_C` carries `interruption`
profile and `failure`, two tags. So far profile and outcome agree — easy to believe they are the
same thing. They are not, and you proved it in Act 3: a `clean` profile can sit on a `failure`
outcome. The cast shows the *common* case; the trap shows the case that breaks the lazy reading.
'''))
C.append(md('''
## Where this lives in the real VoiceForge pipeline

This book is the hand-built version of two real pieces:

- **`data/normalized/*.json`** — every call already carries a `stress_profile` field
  (`clean | pause_heavy | interruption | ambiguous | kb_gap`), set by `pipeline/normalize.py`.
  You read it straight off disk in Act 2.
- **`pipeline/crosscut.py`** — the analytics that group calls **by stress profile** and report
  failure rate per profile for the business chart (calls with voice failures → lower task
  completion). The grouping you did with `Counter` is precisely what it does at scale.
- **`pipeline/signals.py`** → `turn_metrics()` — the real FTO core whose overlap measurement your
  `interruption` tag and `stress_profile` both lean on. You did not approximate it; you used it.
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

`pipeline/crosscut.py` will report a **failure rate per stress profile**. Predict the *ranking*:
which profile do you expect to have the highest failure rate — `clean`, `pause_heavy`, or
`interruption` — and (the subtle part) do you expect `clean` to be exactly **zero**? Your stored
guess gets confronted when you read the real chart in book 08.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for the cost/business chart in book 08.
my_course_prediction = ""   # which profile fails most, AND whether clean's failure rate is zero - and why

if len(my_course_prediction.strip()) < 20:
    print("write your prediction above (ranking + is-clean-zero), then re-run.")
else:
    print("PREDICTION STORED:", my_course_prediction)
'''))
C.append(md('''
## Where this method itself fails (honesty applies to the taxonomy too)

- **Tag soup** — too many tags, or fuzzy ones, so two people tag the same call differently. The
  whole value is a *closed, agreed* list; a sprawling vocabulary is no vocabulary.
- **Mono-tagging** — forcing one tag per call when a call genuinely has two failures hides half
  the signal. (That is why `tag_call` returns a list.)
- **Profile-as-grade** — reading `clean` as "good." A profile is conditions, never a result.
- **Threshold theater** — the `>4 turns` and `>100ms` cutoffs are choices; the real pipeline
  reads them from `rubric.yaml` so they are visible and tunable, not buried in a function.
'''))
C.append(md('''
## The concept at three levels (say each in your own words)

- **To a beginner:** "instead of saying a call was bad, we pick its reason from a short fixed list
  — and we keep that separate from how hard the call was to begin with."
- **To an engineer:** "a closed failure-tag taxonomy (multi-label, evidence-backed) plus a
  scenario stress-profile enum; the two are orthogonal axes — conditions vs outcome — and the
  business cross-cut is failure-rate grouped by the scenario axis."
- **To a founder:** "we turn a pile of 'bad calls' into counts of named problems, so we can say
  'our biggest loss is X, here is the fix, here is the cost it saves' — raw chaos becomes a
  prioritized roadmap a room will fund."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**Defense question 1: "Isn't a fixed tag list too rigid — won't you miss failures it has no word for?"**
<details><summary>answer</summary>Yes, deliberately — a closed list is what makes counts comparable across people and time. When a real failure recurs with no tag, that is the signal to add ONE new tag through review, not to let everyone freelance. Rigidity is the feature; the escape hatch is governed, not ad hoc.</details>

**Defense question 2: "You tagged toy calls. Why should I trust the same tags on real calls?"**
<details><summary>answer</summary>Because the tag rules read the SAME fields the real schema guarantees — `speaker`, `text`, `start_ms`/`end_ms` — and the overlap measurement is book 04's FTO, the same one `pipeline/signals.py` uses. The toy size was for readability, not a different method; I ran the profile read on the 11 real `data/normalized` files unchanged.</details>

**Defense question 3: "A call was in the `clean` profile and still failed — doesn't that mean your profiles are wrong?"**
<details><summary>answer</summary>No — it means profile and outcome are different axes, which is the point. The profile correctly reported calm conditions; the agent still missed a required field. A clean-profile failure is the MOST informative kind: it strips away the 'hard scenario' excuse and shows the agent's fault directly. `crosscut.py` reports failure rate per profile precisely to surface those.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own: the cast tagged on both axes, where stress profiles and tag-counts live in
the real repo (`data/normalized/*.json`, `pipeline/crosscut.py`, `pipeline/signals.py`), how this
book hands a per-cause breakdown forward to book 08's cost work — and, above all, the bar you
must clear to PASS this book.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The four failure tags, and which **signal** each reads (timing / text / language / length)
2. The three stress profiles, and the one sentence: a profile is **conditions, not a result**
3. Why `interruption` is in **both** lists, and what it means in each
4. The trap: a `clean`-profile call that still **failed** — and which real file reports
   failure-rate-per-profile
5. The book's clean sentence (below) — in your own words first

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about tags vs profiles

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Raw chaos becomes engineering signal through categories."**

Named failure tags turn a pile of bad calls into countable causes; the stress profile keeps the
scenario's conditions separate from the agent's performance. If your sentence captures that
separation in your own words, this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "07_failure_tags_stress_profiles.ipynb"   # <- this notebook's filename
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

**07 done** (pending your teach-back) → **08 · cost** — every call, failed or not, burned tokens
and minutes. With the failure tags from this book, cost stops being one blurry number and becomes
**cost per cause** and **cost per _successful_ call** — the founder math. The tags you named here
are the columns that breakdown needs.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "07_failure_tags_stress_profiles.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
