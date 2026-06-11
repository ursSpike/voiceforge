#!/usr/bin/env python3
# Builds 23_dataset_hierarchy.ipynb — VoiceForge University book 23.
# The ONE atomic concept: hero / public / synthetic / provider logs — each data source has
# a DIFFERENT job, and disclosure is what makes a mixed-source corpus honest.
# Same four-act skeleton + audit markers as build_P00.py / build_07.py.
# Rerun: .venv/bin/python notebooks/build_23.py
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
# 23 · Dataset hierarchy

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Name the four data sources VoiceForge mixes — **hero**, **public**, **synthetic**,
   **provider logs** — and say the ONE job each does that the others cannot
2. Match a source to a question: *which source proves the system works on real speech?*
   *which one feels like a real call on stage?* *which one fills a gap you have no calls for?*
   *which one shows what production actually does to you?*
3. Read a **strengths / weaknesses** table and pick the right source for a claim
4. Defend the load-bearing lesson: **a mixed-source corpus is only honest if every row carries
   a disclosure label** — where it came from and what that origin can and cannot support

Topic stays small on purpose: four sources, one tiny table, a handful of toy call records.
The *separation of jobs* — and *disclosure as the glue* — is the point.
'''))
C.append(md('''
## 2 — Knowledge map

`22 (simulators) → THIS (dataset hierarchy) → 24 (annotation)`

Where you just were: **book 22** built *simulators* — code that generates fake calls on demand
(a pause-heavy caller, an interrupter). That is one source of data. Useful, but only one.

Why THIS book exists: a real eval set is never one source. You have a flagship demo call, you
have public research corpora, you have simulator output, and (if you are lucky) you have logs
from a real provider. Each arrived for a different reason and can answer a different question.
Pour them into one bucket with no labels and you get a corpus that lies — a synthetic call and a
production call look identical in a table, yet support completely different claims.

Where you go next: **book 24** *annotates* this mixed corpus — humans and judges attach labels.
Annotation only makes sense once you know what each row IS. You cannot label honestly what you
cannot trace. So: sources first (here), labels next (24).
'''))
C.append(md('''
## 3 — Baby intuition

Think about how you would prove a new restaurant is good.

- A **staged photo** of one perfect plate makes people *feel* the food. It is real food — but
  it was plated for the camera. It persuades; it does not prove.
- **Published health-inspection records** prove the kitchen is safe. Dry, external, credible —
  and not yours, so they say nothing about *your* signature dish.
- A **test kitchen** lets you cook a dish you have never served yet, to see if the recipe holds.
  Total control, zero customers.
- The **actual receipts from last night's service** show what really happened when 80 strangers
  ordered at once. Messy, unglamorous, and the only thing that reflects reality.

You would not throw all four in a drawer and call them "evidence." The staged photo is not an
inspection record. A voice-AI eval set has the same four kinds of thing — and the same rule:
keep the labels on, or you will quote the staged photo as if it were the receipts.
'''))
C.append(md('''
## 4 — The formal version

A **data source** is the origin of a call record and the *guarantees that origin carries*.
VoiceForge mixes four, each with one job:

| source | what it is | its ONE job |
|---|---|---|
| **hero** | one scripted, assembled flagship call (real audio, exact assembly timestamps) | **theater** — make a stranger *feel* a real failure in 90 seconds |
| **public** | research corpora collected by others (SpokenWOZ, AMI) | **validity** — external, credible, real human speech you did not author |
| **synthetic** | simulator-generated calls (book 22) | **coverage** — fabricate the rare scenario you have zero real calls for |
| **provider logs** | calls from a production voice platform (Bolna) | **production reality** — what real traffic actually does to your system |

The hierarchy is not "best to worst." It is **job to job**. No single source can do another's
job, which is exactly why you need all four — and why each row must remember which one it is.
'''))
C.append(md('''
## 5 — Why this exists (the honesty problem)

Here is the trap this whole book defends against.

A judge, a chart, a kappa number — none of them ask *where a call came from*. They process every
row the same way. So if your corpus contains a **synthetic** call that a simulator wrote to be
hard, and a **provider-log** call that a real person actually struggled through, your charts will
average them together and your slide will say "the system handles interruptions." But one of those
interruptions was *invented to order* and one was *real*. The claim each supports is different.

The fix is not to drop sources. The fix is **disclosure**: every record carries a `source` label
(and the hero call carries an explicit `disclosure` string — you will see the real one). Then a
claim can be scoped: "validated on public data, demoed on the hero call, stress-covered by
synthetic, sampled from production." That sentence is honest. "We tested 200 calls" — without
saying what kind — is not.

This is the same disease you met in P00 (a green cell proves execution, not correctness) wearing
a new coat: **a row in a table proves nothing about its own origin unless the origin is written
down.** Let us build it from toy records up.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. Name the four sources and the ONE job each one does.
2. Why is the hierarchy NOT "best source to worst source"?
3. What single piece of metadata turns a mixed-source corpus from dishonest to honest?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: more data is more data; pour it all in one pile.
After Act 1 you should know: data has **provenance**, provenance assigns a **job**, and four jobs
(theater / validity / coverage / production reality) need four sources. The glue that keeps the
pile honest is a **disclosure label on every row**.

If you can say "hero = theater, public = validity, synthetic = coverage, logs = production
reality" without scrolling up, continue. If not, re-read cell 4's table.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of what a "data source" is to you now. Not mine - yours.
# Producing the sentence is the learning; reading mine would just feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: build the four sources as toy records, then read the real labels

## The plan (toy before real)

We will NOT start with the 246 MB SpokenWOZ file. We start with four hand-typed call records,
one per source, small enough to read in full. Once you can see the `source` field doing its job
on toy data, we open the REAL normalized files on disk and find the very same field. Manual and
tiny first; real and large only after.
'''))
C.append(md('''
## Meet the recurring cast (you have seen them since P00)

Three calls travel through this whole course. We reuse them so nothing is a stranger:
- **call_A** — clean English booking, cooperative caller, task succeeds.
- **call_B** — Hinglish appointment, hesitations and a repeat, task partially done.
- **call_C** — Telugu-English service call, agent interrupts mid-answer, task fails.

In THIS book the question is not *what happened in the call* — it is *where each call came from*.
The same conversation can arrive from any source, and the source changes what it can prove.
'''))
C.append(md('''
## PREDICT
Below we will type four toy call records — one tagged `hero`, one `public`, one `synthetic`,
one `provider_log`. Before you see them: which ONE of the four do you expect to carry an extra
**disclosure** string explaining that it was constructed? (Hint: which job is "theater"?)
Commit out loud.
'''))
C.append(code('''
# YOUR TURN - predict BEFORE running the cell that prints the records.
# Store it so the notebook becomes a record of YOUR thinking, comparable later.
my_disclosure_guess = ""   # <- type one of: "hero" / "public" / "synthetic" / "provider_log"

if len(my_disclosure_guess.strip()) == 0:
    print("fill in my_disclosure_guess above, then re-run this cell.")
else:
    print("guess locked:", my_disclosure_guess)
'''))
C.append(code('''
# Four toy call records, one per source. We keep the SAME shape (call_id, source, language,
# one example turn) so the ONLY thing that varies is provenance - that isolates the lesson.
# This is raw input: we print it untouched before transforming anything (a course rule).
toy_corpus = [
    {"call_id": "call_A", "source": "hero",         "language": "en",
     "note": "scripted flagship; real audio; assembly timestamps",
     "disclosure": "constructed demo scenario; see docs/limitations.md"},
    {"call_id": "swz_x", "source": "public",        "language": "en",
     "note": "SpokenWOZ corpus call, collected by researchers"},
    {"call_id": "sim_7", "source": "synthetic",     "language": "en",
     "note": "simulator-generated pause_heavy caller (book 22)"},
    {"call_id": "bol_3", "source": "provider_log",  "language": "en",
     "note": "real call pulled from Bolna production traffic"},
]
for rec in toy_corpus:                 # one print per row so each ROW is visibly one THING
    print(rec)
'''))
C.append(md('''
## INSPECT — look at the raw rows, do not stare at a summary

Three boring observations dissolve most confusion here:
1. Every row has the same keys *except* one. Which row has an extra key, and what is it?
2. The `note` is for humans; the `source` is for code. Why do we need the machine-readable one?
3. `call_A` appears as `hero` here — but the *same conversation* could be re-collected from a
   provider. The text would be identical; only `source` would change.
'''))
C.append(code('''
# Inspection is just looking. We print which keys each record carries, because the disclosure
# field's PRESENCE (not its value) is the first thing that separates hero from the rest.
for rec in toy_corpus:
    has_disclosure = "disclosure" in rec        # the hero row carries an explicit honesty string
    print(f"{rec['call_id']:<7} source={rec['source']:<13} has_disclosure={has_disclosure}")
'''))
C.append(md('''
## OBSERVE + EXPLAIN
Did your prediction hold? Only the `hero` row carried a `disclosure` string. Say the why in one
sentence: the hero call is the one that *looks* most like real production but is actually
constructed, so it is the one that most needs a written warning attached.
'''))
C.append(md('''
## Manual-before-function — group the corpus BY source by hand

Before any library `groupby`, we count sources with a plain loop and a dictionary, on data small
enough to verify by eye. Functions are wrappers around ideas; if you meet the wrapper first, the
idea (a histogram over provenance) stays hidden inside it.
'''))
C.append(md('''
## PREDICT
Our toy corpus has four records, one per source. After we count how many calls come from each
source, what will the four counts be? (Trivial on purpose — the habit is the workout.)
'''))
C.append(code('''
# Manual count of calls per source - every step visible, nothing hidden.
counts_by_source = {}                  # we accumulate into a dict: source -> how many calls
for rec in toy_corpus:
    src = rec["source"]
    # .get(src, 0) handles the FIRST time we see a source - there is no running total yet
    counts_by_source[src] = counts_by_source.get(src, 0) + 1

for src, n in counts_by_source.items():
    print(f"{src:<13} {n}")
'''))
C.append(code('''
# Now - and only now - the library wrapper. Counter does exactly what the loop above did.
from collections import Counter        # standard-library multiset; imported where first needed

# We feed it the source of every record; Counter tallies identical values into counts.
library_counts = Counter(rec["source"] for rec in toy_corpus)
print(library_counts)
print("same numbers as the by-hand dict above:", dict(library_counts) == counts_by_source)
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
Why did we count by hand first when `Counter` is one line? (One reason is about the *idea* of a
provenance histogram; one is about *trusting* the library output because you already know the
answer.)
'''))
C.append(md('''
## The strengths / weaknesses table — the heart of this book

Each source is strong at its job and weak everywhere else. We encode that as data so we can
*query* it, not just read it. Watch the pattern: no row is all-strong, no row is all-weak.
'''))
C.append(md('''
## PREDICT
We are about to define, for each source, whether it gives you: **real human speech?**
**production realism?** **scenario control?** **stage impact?** Before you see it — which single
source do you expect to score "yes" on *production realism* but "no" on *scenario control*?
(Which job is "production reality"?) Commit.
'''))
C.append(code('''
# YOUR TURN - predict which source is yes-on-realism, no-on-control.
my_realism_guess = ""   # <- "hero" / "public" / "synthetic" / "provider_log"

if len(my_realism_guess.strip()) == 0:
    print("fill in my_realism_guess above, then re-run.")
else:
    print("guess locked:", my_realism_guess)
'''))
C.append(code('''
# The strengths/weaknesses table as DATA (a list of dicts), so we can query it below.
# Each flag answers one yes/no question about what the source can give you. Encoding it as
# booleans (not prose) is what lets a later cell PICK a source for a claim automatically.
SOURCES = [
    {"source": "hero",         "job": "theater",
     "real_speech": True,  "production_realism": False, "scenario_control": False, "stage_impact": True},
    {"source": "public",       "job": "validity",
     "real_speech": True,  "production_realism": False, "scenario_control": False, "stage_impact": False},
    {"source": "synthetic",    "job": "coverage",
     "real_speech": False, "production_realism": False, "scenario_control": True,  "stage_impact": False},
    {"source": "provider_log", "job": "production reality",
     "real_speech": True,  "production_realism": True,  "scenario_control": False, "stage_impact": False},
]
# Print as an aligned table - rows are sources, columns are facts about sources (table ritual).
cols = ["source", "job", "real_speech", "production_realism", "scenario_control", "stage_impact"]
print(f"{'source':<13}{'job':<19}{'real_sp':<9}{'prod':<7}{'control':<9}{'stage':<7}")
for s in SOURCES:
    print(f"{s['source']:<13}{s['job']:<19}{str(s['real_speech']):<9}{str(s['production_realism']):<7}{str(s['scenario_control']):<9}{str(s['stage_impact']):<7}")
'''))
C.append(md('''
## How to read this table (the 3-move ritual on a strengths/weaknesses grid)

1. Row count: "four rows — one per source."
2. What one row IS: "one row = one source and what it can give you."
3. Read one cell aloud: "synthetic's `production_realism` is False — a fabricated call is not
   production reality, even if it looks like one."

Now the dangerous reading: NO column is all-True. `real_speech` is True for three sources but
False for synthetic. `stage_impact` is True for *only* hero. `production_realism` is True for
*only* provider logs. That spread is the whole point — it is why one source can never replace
another.
'''))
C.append(code('''
# Query the table instead of eyeballing it: which source is the ONLY one with production realism?
# This is the table earning its keep as data - a claim ("only logs are production-real") becomes
# a one-line check anyone can rerun, not a sentence you have to trust.
only_production_real = [s["source"] for s in SOURCES if s["production_realism"]]
only_stage = [s["source"] for s in SOURCES if s["stage_impact"]]
only_control = [s["source"] for s in SOURCES if s["scenario_control"]]
print("production realism:", only_production_real)   # expect just provider_log
print("stage impact:      ", only_stage)             # expect just hero
print("scenario control:  ", only_control)           # expect just synthetic
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just SAW (not memory): why does the fact that each "yes" column has
exactly one owner prove the four sources are *complementary*, not *redundant*?
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
For each of the four jobs — theater, validity, coverage, production reality — name the source
that owns it, and the ONE capability that makes it the owner.
'''))
C.append(md('''
## Now the REAL data — find `source` on disk

Enough toys. The repo has 11 normalized call files in `data/normalized/`. Each is a real record
with a real `source` field. We open them and run our by-hand count from earlier on the actual
corpus. Raw-before-transformed still applies: we print one real record's provenance fields before
summarizing.
'''))
C.append(code('''
# Locate the normalized data folder by walking up from wherever this notebook runs.
# We resolve paths defensively because the kernel's working directory is not guaranteed.
import json
from pathlib import Path

candidates = [Path.cwd() / "data" / "normalized"] + [p / "data" / "normalized" for p in Path.cwd().parents]
norm_dir = next((d for d in candidates if d.exists()), None)
print("normalized dir found:", norm_dir is not None, "->", norm_dir)
'''))
C.append(code('''
# Load every normalized call and print just its provenance fields - the RAW labels on real data.
# We read only the small metadata we need (id, source, language), not the whole turn list, so
# the point (provenance) is not buried under transcript text.
real_calls = []
for f in sorted(norm_dir.glob("*.json")):
    rec = json.loads(f.read_text())
    real_calls.append(rec)
    # .get(...) with a default because a source may legitimately omit a field - we never assume
    print(f"{rec['call_id']:<14} source={rec.get('source','?'):<11} language={rec.get('language','?')}")
'''))
C.append(code('''
# Run our earlier by-hand histogram on the REAL corpus - same idea, real provenance.
real_counts = Counter(rec.get("source", "UNKNOWN") for rec in real_calls)
print("calls per source (real data):", dict(real_counts))
# This is the honest summary of THIS repo right now: a hero call + public SpokenWOZ calls.
# Synthetic and provider_log are jobs the hierarchy DEFINES but this sprint's pool may not fill.
'''))
C.append(md('''
## PREDICT
Look at the real counts you just printed. The repo's pool is mostly `spokenwoz` plus one `hero`.
Given the four jobs, which TWO jobs is this current pool *not yet* filling? (Think: which sources
are missing from the count?) Commit before the next cell answers it.
'''))
C.append(code('''
# YOUR TURN - which two jobs are unfilled in the real pool right now?
# Write the two source names you did NOT see in real_counts.
my_missing_sources = []   # <- e.g. ["synthetic", "provider_log"]  (fill it in)

if len(my_missing_sources) == 0:
    print("fill in my_missing_sources above (two names), then re-run.")
else:
    present = set(real_counts)
    defined = {"hero", "spokenwoz", "synthetic", "provider_log", "public"}
    # We compute the gap so your guess can be checked against the actual missing-from-disk set.
    print("you guessed missing:", my_missing_sources)
    print("sources actually present on disk:", sorted(present))
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a corpus was a bag of calls. After Act 2 you can: build one toy record per source and see
that only the hero carries an explicit disclosure string; count provenance by hand and with
`Counter`; read a strengths/weaknesses grid and prove each "yes" has exactly one owner; and find
the very same `source` field on the real 11-call pool — including which jobs that pool does not
yet fill. The field is small; the discipline of keeping it is the lesson.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (the table / the source field - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: strip the labels, watch the corpus lie

## Break-it philosophy

You do not understand why disclosure matters until you watch a corpus *without* it mislead you.
So we now damage the data on purpose — drop the `source` labels — and prove that the resulting
"clean" table makes a confident, wrong claim. Surprise on your own terms is education; the same
surprise in a hackathon Q&A is a disaster.
'''))
C.append(md('''
## PREDICT
We will merge our four toy records into one list and then **delete the `source` field from every
row**. After that, we ask "how many of these calls are real production traffic?" With the labels
gone: does the code **crash**, or does it return a **confident wrong answer** with no warning at
all? Commit to one.
'''))
C.append(code('''
# BREAK-IT (guided) - we strip provenance, then make a claim the stripped data cannot support.
import copy

# copy.deepcopy so we damage a COPY and keep the labelled originals intact for the fix cell.
stripped = copy.deepcopy(toy_corpus)
for rec in stripped:
    rec.pop("source", None)        # the damage: provenance erased; the text/ids look unchanged
    rec.pop("disclosure", None)    # and the honesty string is gone too

# Without source, a well-meaning analyst counts ALL rows as "calls we tested" and, lacking any
# label, assumes they are representative of production. The number is real; the meaning is false.
total_calls = len(stripped)
print("rows that look like real evaluated calls:", total_calls)
print("example stripped row:", stripped[0])   # nothing flags that this was the CONSTRUCTED hero call
'''))
C.append(md('''
## Read what just happened (this is the silent failure, not a crash)

No error. The cell ran green and printed "4". A slide built on it would say *"evaluated on 4
real calls."* But one of those four was the **constructed hero call** (theater), one was
**synthetic** (fabricated coverage), and only — at most — the provider-log row was real
production traffic. The stripped table cannot tell you that, because **the field that knew was
deleted.** A crash would have been the *friendly* failure; this is the dangerous kind — a
confident wrong number with no red ink. (This is the P00 trap again: green ≠ correct.)
'''))
C.append(md('''
## The fix — recover provenance, re-scope the claim

The repair is not "compute harder." It is "put the label back and let it scope the sentence."
Because we kept the labelled originals, we can recount honestly and say what each subset supports.
'''))
C.append(code('''
# Recover from the labelled originals (NOT the stripped copy) and re-state the claim per source.
# This is the whole remedy: a count is only as honest as the provenance it is grouped by.
honest = Counter(rec["source"] for rec in toy_corpus)   # toy_corpus still has its labels
print("honest breakdown:", dict(honest))

# The scoped, defensible sentence the labels let us say:
real_production = honest.get("provider_log", 0)
print(f"of {len(toy_corpus)} calls: {real_production} is real production traffic; "
      f"{honest.get('hero',0)} is the constructed demo; {honest.get('synthetic',0)} is synthetic; "
      f"{honest.get('public',0)} is public-corpus.")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
Why is "we evaluated 4 calls" (no labels) MORE dangerous than a crash? And what is the exact
remedy — in one move — that turns it back into an honest statement?
'''))
C.append(md('''
## YOUR break now

Author your own damage. Pick ONE source in `toy_corpus` and imagine quoting it for the WRONG job
(e.g. citing the `hero` call as proof of "real production performance", or citing `synthetic` as
"real human speech"). Write, as a comment, which mismatch you are making and exactly what false
claim it would let someone say. Then run the check cell to confront it.
'''))
C.append(code('''
# YOUR TURN - self-authored source/claim mismatch.
# my mismatch: <which source, quoted for which wrong job, and the false sentence it enables>

# Pick a source name to interrogate (leave as "" to just see the gentle nudge):
my_source = ""        # <- e.g. "hero" or "synthetic"
my_claim_job = ""     # <- the job you are WRONGLY attributing, e.g. "production reality"

if my_source == "" or my_claim_job == "":
    print("set my_source and my_claim_job above (and write the comment), then re-run.")
else:
    # Look up what that source actually owns, so reality can contradict the mismatch out loud.
    row = next((s for s in SOURCES if s["source"] == my_source), None)
    if row is None:
        print(f"'{my_source}' is not one of the four sources; check spelling.")
    else:
        print(f"you attributed job '{my_claim_job}' to '{my_source}'.")
        print(f"but '{my_source}' actually owns the job: '{row['job']}'.")
        print("production_realism:", row["production_realism"], "| real_speech:", row["real_speech"])
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this book is built on

**The wrong belief:** "the best dataset is the most realistic one, so I should weight provider
logs highest and treat the others as inferior filler."

It sounds responsible. It is wrong, and the next cell proves it. Realism is ONE axis. If you rank
sources by realism alone, you systematically throw away the jobs the other three do — and those
jobs are not optional. Run it, then try to state the flaw BEFORE the reveal.
'''))
C.append(md('''
## PREDICT
The next cell keeps ONLY the source with `production_realism == True` and then asks whether the
survivors can still do the other three jobs (coverage, stage, validity). Before running: how many
of those three "still has …?" lines do you expect to print **True**? Commit to a number (0–3).
'''))
C.append(code('''
# "Just keep the most realistic data." We rank sources by production_realism and drop the rest,
# then ask whether the survivors can still do the OTHER three jobs. Watch the coverage collapse.
realism_first = [s for s in SOURCES if s["production_realism"]]   # the "keep only realistic" pile
print("kept after ranking by realism:", [s["source"] for s in realism_first])

# Can the survivors still cover the rare scenario? still hit the stage? still give external validity?
can_cover  = any(s["scenario_control"] for s in realism_first)
can_stage  = any(s["stage_impact"]     for s in realism_first)
can_valid  = any(s["source"] == "public" for s in realism_first)
print("still has scenario coverage (synthetic's job)?", can_cover)
print("still has stage theater (hero's job)?         ", can_stage)
print("still has external public validity?           ", can_valid)
'''))
C.append(md('''
## The reveal

Ranking by realism kept only `provider_log` and answered **False** to all three other jobs. You
cannot fabricate the rare interruption you have no real call for (that was synthetic's job). You
cannot make a stranger *feel* the failure in 90 seconds — raw production logs are messy and
un-curated (that was hero's job). You cannot point to external, third-party human speech to prove
you did not cherry-pick your own data (that was public's job).

**Realism is not a ranking; it is one of four jobs.** The right mental model is a *portfolio*,
not a *leaderboard*. Each source is held because of what it uniquely contributes — and disclosure
is what lets the portfolio stay honest about which contribution came from where. This is the same
shape as P00's "average of averages" trap: optimizing one number silently destroys the thing you
actually needed.
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why is "keep only the most realistic source" a mistake?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## A second break — the hero call's REAL disclosure string

This is not a toy. The actual hero call on disk carries a disclosure label written before any
pipeline code. We load it and read it, because *this exact string* is what makes it legitimate to
put a constructed call on the flagship slide. Remove this string and the same call becomes a quiet
lie. We will read it, then (in memory only) imagine it gone.
'''))
C.append(code('''
# BREAK-IT - read the real hero disclosure, then show what its ABSENCE would enable.
# We resolve the hero file from the same normalized pool so this is the genuine record.
hero = next((r for r in real_calls if r.get("source") == "hero"), None)
if hero is None:
    # EXPECTED FAILURE FOR LEARNING - if the hero call is missing, the demo's honesty anchor is gone.
    raise RuntimeError("no hero call found in normalized pool - the disclosure anchor is missing")

meta = hero.get("metadata", {})
print("hero call_id:", hero["call_id"], "| source:", hero["source"], "| language:", hero["language"])
print("constructed flag:", meta.get("constructed"))
print("REAL disclosure string:", meta.get("disclosure"))
'''))
C.append(code('''
# Now the silent-failure version, in memory: strip the disclosure and re-describe the call.
# Nothing crashes; the call just stops admitting what it is. That gap is the entire risk.
hero_no_label = copy.deepcopy(hero)
hero_no_label.get("metadata", {}).pop("disclosure", None)
hero_no_label.get("metadata", {}).pop("constructed", None)
print("without disclosure, this record reads as a normal call:")
print("  id:", hero_no_label["call_id"], "| source:", hero_no_label["source"],
      "| any honesty string?", "disclosure" in hero_no_label.get("metadata", {}))
# Same audio, same turns, same timestamps - but now it is indistinguishable from a real one.
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: realism felt like the thing to maximize, and a labelled vs unlabelled corpus felt
basically the same. After Act 3: stripping `source` produces a confident wrong claim with no
crash (the dangerous failure); the remedy is one move — put the label back and scope the sentence;
ranking sources by realism alone destroys three jobs; and the hero call's real `disclosure` string
is the single line that makes a constructed demo legitimate rather than a lie.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the realism-leaderboard trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this lives in VoiceForge, and how to defend it

## The VoiceForge connection (real files)

This is not an abstract taxonomy — it is wired into the repo:

- **`data/hero/turns.json`** — the real hero call (12 turns, te-en, `source: "hero"`). Its
  `metadata.disclosure` is the genuine string: *"constructed demo scenario; see docs/limitations.md"*.
- **`data/normalized/*.json`** — 11 real records (1 hero + 10 SpokenWOZ), every one carrying a
  `source` field. The schema for that field lives in **`schemas/call_log.md`**.
- **`docs/limitations.md`** — written *before* the first line of pipeline code. It states in
  plain English what each source can and cannot support: the hero call is "a demonstration of
  what VoiceForge detects, not evidence drawn from production traffic"; SpokenWOZ is "protocol-
  collected: few genuine barge-ins"; AMI "supplies real overlap but is meetings-domain"; costs
  and A/B are scoped too. That file IS disclosure at the project level.
- **`docs/later.md`** — names **Bolna** as the planned provider-log source ("real Bolna call
  ingest if credits land"). Provider logs are a defined job the sprint may not fully fill — and
  saying so out loud is the disclosure.
'''))
C.append(code('''
# Prove the connection is real: read the project-level disclosure (docs/limitations.md) headings.
# We do this in code so the claim "the repo discloses its sources" is verified, not asserted.
lim_candidates = [Path.cwd() / "docs" / "limitations.md"] + [p / "docs" / "limitations.md" for p in Path.cwd().parents]
lim = next((f for f in lim_candidates if f.exists()), None)
if lim is None:
    print("limitations.md not found from here - that itself would be a disclosure gap to fix")
else:
    # Print only the section headings (lines starting with ##) - the disclosure topics, at a glance.
    heads = [ln.strip() for ln in lim.read_text().splitlines() if ln.strip().startswith("## ")]
    print("project-level disclosure sections:")
    for h in heads:
        print(" ", h)
'''))
C.append(md('''
## PREDICT
You just printed the section headings of `limitations.md`. Before you scrolled them — predict:
does this file disclose limitations of EACH of the four sources, or only the constructed hero
call? (Think about whether public data and cost estimates got their own honesty sections.) Commit.
'''))
C.append(code('''
# YOUR TURN - your prediction about the breadth of the project's disclosure.
my_disclosure_breadth = ""   # "only hero" / "all sources" / something in between - and why

if len(my_disclosure_breadth.strip()) < 15:
    print("write your prediction above (15+ chars), then re-run.")
else:
    print("PREDICTION STORED:", my_disclosure_breadth)
'''))
C.append(md('''
## Where this fails (honesty about the hierarchy itself)

- **Disclosure rot** — a `source` field that is present but wrong (a synthetic call mislabelled
  `provider_log`) is worse than none: it *looks* trustworthy. Countermeasure: provenance is set at
  ingest by the loader, never edited by hand downstream.
- **Job confusion on stage** — quoting the hero call's numbers as if they were production metrics.
  Countermeasure: the disclosure slide; "demoed on hero, validated on public" as a fixed phrase.
- **Sample-size laundering** — "we evaluated 200 calls" when 190 are synthetic. Countermeasure:
  always report the per-source breakdown, never the merged total alone (you built that count).
- **Missing-job blindness** — forgetting that an unfilled job (no provider logs yet) is a real
  gap, not a non-issue. Countermeasure: `docs/later.md` lists it explicitly as roadmap.
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
Name the four failure modes of the hierarchy itself — disclosure rot, job confusion on stage,
sample-size laundering, missing-job blindness — and give the one-line countermeasure for each.
Then say which one you think is easiest to commit by accident on a deadline, and why.
'''))
C.append(md('''
## The concept at three levels (same concept, three audiences)

- **To a beginner:** "Different data comes from different places, and each place is good for a
  different thing — keep a label on every call saying where it came from, or you will brag with
  the wrong one."
- **To an engineer:** "Provenance is a first-class field (`source`) set at ingest. Hero =
  scripted/assembled (theater), public = external corpora (validity), synthetic = simulator
  (coverage), provider logs = production traffic (reality). Claims are scoped by `groupby(source)`;
  merged totals without the breakdown are a reporting bug."
- **To a founder:** "We do not fake credibility and we do not pretend our demo is our evidence.
  The flagship call sells the problem; public data proves the method; simulators cover the gaps;
  production logs show what is real — and we disclose exactly which is which. That disclosure is
  what makes the whole eval set defensible to a buyer."
'''))
C.append(md('''
## Defense questions (×3 — try to answer before opening each)

**1. "Isn't your hero call just a cherry-picked demo? Why should I trust any of this?"**
<details><summary>answer</summary>The hero call is disclosed as constructed — its job is theater,
to make you feel the failure, not to prove the rate. Validity comes from a different source:
public corpora (SpokenWOZ, AMI) we did not author, plus a pilot calibration against human labels.
The demo and the evidence are deliberately different rows, and every row says which it is.</details>

**2. "If synthetic data is fake, why include it at all — doesn't it pollute your numbers?"**
<details><summary>answer</summary>It is never merged into a realism claim. Synthetic's job is
coverage: it fabricates the rare scenario (a specific interruption pattern) we have zero real
calls for, so the pipeline is exercised on edges before they appear in production. It is reported
under its own `source` label, never folded into "real calls."</details>

**3. "You have almost no provider logs yet. Isn't your eval set basically incomplete?"**
<details><summary>answer</summary>Yes, and we say so — `docs/later.md` lists Bolna provider-log
ingest as roadmap. An unfilled job is a disclosed gap, not a hidden one. The hierarchy defines
four jobs; the honest move is to report which are filled (hero, public) and which are pending
(synthetic at scale, production logs), never to imply the set is complete.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: where the four sources physically live in this repo (`data/hero/turns.json`,
`data/normalized/*.json`, `schemas/call_log.md`, `docs/limitations.md`, `docs/later.md`), how each
job maps to a real file or roadmap item, how to explain the hierarchy to a beginner, engineer, and
founder, and how to answer the three sharpest questions a buyer will ask — every answer anchored in
*disclosure*, not bravado.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. Name the four sources and the ONE job each owns (theater / validity / coverage / production reality).
2. Explain why the hierarchy is a *portfolio*, not a *leaderboard* (the realism trap).
3. Show what happens to a claim when you strip the `source` labels — and the one-move remedy.
4. Quote the hero call's real disclosure string and say why that line makes a constructed demo legitimate.
5. Give the clean sentence in your own words, and name one real repo file that embodies it.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about data sources now

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Each data source has a job; disclosure makes them all legitimate."**

If yours captures that in your own words — theater, validity, coverage, production reality, each
held for its job and each labelled so no one quotes the wrong one — this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "23_dataset_hierarchy.ipynb"   # <- this notebook's filename
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

**23 done** (pending your teach-back) → **24 · annotation** — now that every call carries an
honest `source` label, humans and judges attach the *other* labels (scores, tags, evidence). You
cannot annotate honestly what you cannot trace, so the disclosure discipline you built here is the
precondition for everything 24 does. Sources first; labels next.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "23_dataset_hierarchy.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
