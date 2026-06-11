#!/usr/bin/env python3
# Builds 03_pandas_for_call_data.ipynb per _BUILD_SPEC.md (four acts, marker conventions, cast).
# Rerun: .venv/bin/python notebooks/build_03.py
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
# 03 · Python/pandas for call data

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Load the **11 real calls** from `data/normalized/*.json` into one **DataFrame** where
   **one row = one call** — and say what each column is.
2. Count calls **by a categorical label** — **by hand first** (a plain dict-and-loop tally), then
   get the *same* numbers from pandas' `groupby(...).size()` — and prove they match.
3. **Group and count** the pool two ways that matter downstream: by **`stress_profile`**
   (clean / pause_heavy / interruption) and by **`source`** (hero / spokenwoz).
4. Read the result like a **benchmark table** — rows are runs, columns are facts, a group-by is a
   pivot — and defend why a count is only honest with its denominator attached.

This is the **tool** book. Book 04 needs to reach across many calls at once to compute timing at
scale; you cannot do that one dict at a time. Today you earn the table.
'''))
C.append(md('''
## 2 — Knowledge map (where this book sits)

`02 (JSON schemas / data contracts) → THIS: Python/pandas for call data → 04 (turns, gaps, latency)`

In **02** you learned the **shape** of one call: the `call_log` contract — `call_id`, `source`,
`language`, `stress_profile`, `workflow_type`, and a list of `turns`. That told you what a single
record *is*.

This book asks the next question: **you have eleven of them on disk — now what?** A schema
describes one call; an **eval** lives or dies on what you can say across the *whole pool* at once.
"How many interruption calls do we even have?" is not a question you answer by opening eleven files.
You answer it by loading all eleven into a table and counting a column.

Next door, **04** takes this table-thinking down into one call's *turns* and computes timing in
milliseconds. You need the table muscle first.
'''))
C.append(md('''
## 3 — Baby intuition

You spent years reading **benchmark result tables**: one row per run, columns for config and score,
and you `GROUP BY` hardware to see which box wins. A spreadsheet of runs.

A folder of call logs is the *same object wearing a costume*. Each `.json` file is one run.
Stack them and you have a results table: **one row per call**, columns like `stress_profile` and
`source`, and the question "how many calls per stress profile?" is the exact same `GROUP BY ...
COUNT(*)` you have run a thousand times — only the subject changed from FLOPS to phone calls.

That sentence is the whole book: **a DataFrame lets me treat calls like benchmark rows.** We are
going to earn it, by hand, on the real eleven.
'''))
C.append(md('''
## 4 — The formal version

A **DataFrame** (pandas) is a table with **named columns** and a row index. We will build one where:

| concept | here it means |
|---|---|
| **one row** | one call (one `.json` file from `data/normalized/`) |
| **a column** | one field shared by every call — `call_id`, `source`, `stress_profile`, … |
| **a cell** | one fact about one call — e.g. call `swz_MUL0069`'s `stress_profile` is `clean` |
| **group-by** | bucket the rows by a column's value, then count/aggregate each bucket |

The three verbs this book drills, in order:

1. **load** — read 11 JSON files into a list of dicts, then into a DataFrame (one row each).
2. **group** — `df.groupby("stress_profile")` buckets rows that share a value.
3. **count** — `.size()` reports how many rows landed in each bucket.

One rule stated now, proven in Act 3: a count is half a fact. **"4 interruption calls" out of
**11** is meaningful; "4" alone is a number waiting to mislead.** Always carry the denominator.
'''))
C.append(md('''
## 5 — Why this exists (the part the rest of the course leans on)

Every later book reaches *across* calls, not into one:
- Book 06 asks "what fraction of calls hit task success?" — a count over a column.
- Book 07 tallies failure tags by stress profile — a group-by.
- Book 13's confusion matrix is a group-by of (predicted, actual) pairs.
- Book 23's dataset hierarchy is *entirely* about slicing a table into train/eval splits.

All of it is the move you build today: rows in, group, count. We use pandas not because it is fancy
but because the by-hand loop you will write first does not survive contact with a real dataset —
the moment you want "count by two columns" or "the same thing but only spokenwoz," the loop
explodes and the table shrugs. You will feel that shift happen in Act 2.

The next cells start where the course always starts: a tiny toy, counted by hand, before any real
file or any library touches the data.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In the table we are about to build, what is **one row**? What is **one column**? What is **one
   cell**?
2. Translate "how many calls per `stress_profile`?" into the SQL/benchmark idea you already know.
3. Why is the count **4** less honest than **4 of 11**? (One sentence; the proof is in Act 3.)
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a call log is one JSON file you open and inspect.
After Act 1 you should hold: a *folder* of call logs is a **results table** — one row per call —
and the questions you will ask of it (counts, group-bys) are the same benchmark-table moves you
already own. The schema from 02 describes a row; this book is about the table the rows make.

If that feels like your own sentence, continue. If not, re-read the benchmark analogy in cell 3.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of what a folder of call logs
# IS to you now. Producing the sentence is the learning; reading mine would only feel like it.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: count by hand on a toy, then on the real eleven

## A 3-row toy, printed RAW first

Course rule: the ugly input goes on screen **before** anything is computed from it. Here are three
*toy* calls as plain dictionaries — same shape as the real ones, but only the fields we will count
on, so the idea is not buried in noise. One dict = one call.
'''))
C.append(code('''
# Three toy calls as a list of dicts. We keep ONLY the fields we will group/count on, so the
# counting idea is visible without the full call_log schema crowding the screen.
toy_calls = [
    {"call_id": "toy_A", "source": "hero",      "stress_profile": "clean"},
    {"call_id": "toy_B", "source": "spokenwoz", "stress_profile": "interruption"},
    {"call_id": "toy_C", "source": "spokenwoz", "stress_profile": "clean"},
]
# one print per row, so each ROW is visibly one THING (one call) before we count anything
for c in toy_calls:
    print(c)
'''))
C.append(md('''
## PREDICT
Look at the three toy calls above. Counting by `stress_profile`:
1. How many `clean` calls? How many `interruption`?
2. How many distinct stress profiles appear at all?
Commit to the numbers before the next cell.
'''))
C.append(code('''
# YOUR TURN - lock your prediction BEFORE the counting cell, so the notebook records YOUR thinking
# and a later cell can compare it against reality. That comparison is the lesson.
my_clean_count = None          # <- replace None with how many 'clean' toy calls you see
my_interruption_count = None   # <- replace None with how many 'interruption' toy calls you see

if my_clean_count is None or my_interruption_count is None:
    print("fill in BOTH counts above, then re-run this cell.")
else:
    print("locked:", my_clean_count, "clean,", my_interruption_count, "interruption")
'''))
C.append(md('''
## Manual-before-function — count with a plain dict and a loop

Before pandas does this in one line, we do it the bare way: walk the calls, keep a running tally in
a dictionary. This is the loop pandas runs *for* you — meeting it first means `groupby` will be a
convenience later, not a mystery.
'''))
C.append(code('''
# The by-hand tally. A dict maps each stress_profile -> how many calls had it. We build it the
# long way ON PURPOSE: this is exactly what groupby(...).size() automates, and you cannot trust the
# automation until you have done the thing it automates once.
counts_by_hand = {}                       # empty tally; keys appear as we meet new profiles
for c in toy_calls:
    key = c["stress_profile"]             # the column we are bucketing by
    # .get(key, 0) handles the FIRST time we see a profile: there is no count yet, so start at 0.
    counts_by_hand[key] = counts_by_hand.get(key, 0) + 1
print("by-hand counts:", counts_by_hand)

# The metal-detector reading: did YOUR committed prediction match?
if my_clean_count is not None:
    ok = counts_by_hand.get("clean") == my_clean_count and counts_by_hand.get("interruption") == my_interruption_count
    print("your prediction", "matched" if ok else "DIFFERED",
          "- if it differed, that gap between your model and reality is the thing to chew on")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, out loud: what does each **key** in `counts_by_hand` represent, and what does each
**value** represent? (Key = a stress profile that appeared; value = how many calls had it.)
'''))
C.append(md('''
## Now the library version — pandas, on the SAME toy

Only now do we let pandas in. `pd.DataFrame(list_of_dicts)` turns our three dicts into a table; the
dict keys become **columns**, each dict becomes a **row**. We print it and confirm the shape.
'''))
C.append(code('''
# pandas turns a list-of-dicts directly into a table: each dict -> one row, shared keys -> columns.
# We import it here, where it is first needed, so the import sits next to its first use.
import pandas as pd

toy_df = pd.DataFrame(toy_calls)   # 3 dicts in -> a 3-row table out, columns = the dict keys
print(toy_df)
print()
# .shape is (rows, columns). We read it FIRST, every time, before trusting any count: knowing it is
# 3 rows x 3 columns is the table-reading ritual ('say the row count') made into code.
print("shape (rows, columns):", toy_df.shape)
'''))
C.append(md('''
## PREDICT
`toy_df.groupby("stress_profile").size()` is about to run. It buckets the rows by stress profile and
counts each bucket. Before it runs: what two labels will appear, and what number next to each?
(You already did this by hand — predict the pandas output matches it.)
'''))
C.append(code('''
# groupby buckets rows that share a stress_profile; .size() counts the rows in each bucket. This is
# the SAME tally as counts_by_hand - we run it next to the hand version specifically to prove that.
toy_grouped = toy_df.groupby("stress_profile").size()
print(toy_grouped)
print()
# Proof they agree: convert the pandas result to a plain dict and compare to the by-hand tally.
# If a 'convenience' function disagrees with the thing it replaced, you trust the hand version.
print("pandas == by-hand?", toy_grouped.to_dict() == counts_by_hand)
'''))
C.append(md('''
## OBSERVE + EXPLAIN
The by-hand dict and the pandas `groupby().size()` produced the **same** tally. One sentence: what
did pandas save you here? (Not the *idea* — you already had that — but the **bookkeeping**: the
empty-dict-then-`.get(key, 0)+1` ritual, done for you, and it will not get harder when the data does.)
'''))
C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. `pd.DataFrame(toy_calls)` made a table — where did the **column names** come from?
2. In `groupby("stress_profile").size()`, which part **buckets** the rows and which part **counts**
   them?
3. Why did we write the dict-loop tally FIRST when pandas does it in one line?
'''))
C.append(md('''
## Now the REAL eleven — load `data/normalized/*.json`

Toy done. We load the real pool: eleven `.json` files in `data/normalized/`, the same calls the
whole pipeline reads. Raw-before-transformed: we list the files first, then load one and look at it
before stacking all eleven into a table.
'''))
C.append(code('''
# Find the data folder by walking up from wherever the kernel started, so the notebook runs whether
# it launched in notebooks/ or the repo root (no hardcoded absolute path that breaks on another machine).
import json
from pathlib import Path

name = "data/normalized"
data_dir = next(p for p in [Path.cwd()/name, *[a/name for a in Path.cwd().parents]] if p.exists())

# sorted() so the file order is stable and reproducible run-to-run - an unstable order would make
# row positions (and any 'first call') silently change between runs, which is a debugging nightmare.
files = sorted(data_dir.glob("*.json"))
print("found", len(files), "call files in", data_dir.name + "/")
for f in files:
    print(" ", f.name)
'''))
C.append(md('''
## How to read one real call (the table-reading ritual on a single row)

Before stacking eleven, we look at **one** raw record. Three moves: name the **fields**, say what
**one record IS** ("one call"), then read **one single field aloud** ("its stress_profile is …").
We trim the `turns` list because today we count *calls*, not turns — book 04 goes inside `turns`.
'''))
C.append(code('''
# Load ONE real call and look at its top-level fields. We deliberately do NOT print the turns list:
# today one row = one CALL, so the per-turn detail is noise we will only need in book 04.
one_call = json.loads(files[0].read_text())
for key, value in one_call.items():
    # turns is a long list; we print only its LENGTH so the call-level fields stay readable on screen
    shown = f"<{len(value)} turns>" if key == "turns" else value
    print(f"{key:<16}: {shown}")
'''))
C.append(md('''
## PREDICT
We are about to load all eleven calls and keep only the **call-level** fields (`call_id`, `source`,
`language`, `stress_profile`, `workflow_type`) — dropping `turns` for now. How many **rows** will
the resulting DataFrame have? How many of those **columns**?
'''))
C.append(code('''
# YOUR TURN - lock both predictions before the load cell builds the real table.
my_row_count = None      # how many rows? (one per call file)
my_col_count = None      # how many call-level columns we keep (count the fields listed above)

if my_row_count is None or my_col_count is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("locked:", my_row_count, "rows,", my_col_count, "columns")
'''))
C.append(code('''
# Build the real list-of-dicts: one dict per call, keeping ONLY the call-level fields we count on.
# We drop 'turns', 'audio_path', 'metadata' on purpose - one row = one CALL, and carrying the turns
# list into every row would bloat the table with data this book never groups on.
keep = ["call_id", "source", "language", "stress_profile", "workflow_type"]
records = []
for f in files:
    call = json.loads(f.read_text())
    # a dict comprehension picks out just the keep-fields - explicit, so the table's columns are a
    # deliberate choice, not 'whatever happened to be in the file'.
    records.append({k: call[k] for k in keep})

# print the first two records RAW before tabling them - seeing the list-of-dicts confirms the shape
# we are handing to pandas (and matches the toy pattern from earlier in this act).
for r in records[:2]:
    print(r)
'''))
C.append(code('''
# Now the real DataFrame: 11 call-dicts -> 11 rows, one per call. Same move as the toy, real data.
import pandas as pd   # re-imported here so this cell stands alone if run after a kernel restart

calls = pd.DataFrame(records)
# read the shape FIRST (the ritual), then confirm against your prediction - never trust a table you
# have not sized.
print("shape (rows, columns):", calls.shape)

if my_row_count is not None:
    print("rows match your prediction?", my_row_count == calls.shape[0])
    print("cols match your prediction?", my_col_count == calls.shape[1])
'''))
C.append(md('''
## Look at the whole table

Eleven rows, five columns. We print the entire table — small enough to read every cell. This is the
real pool the rest of VoiceForge runs on: the hero call plus ten SpokenWOZ calls.
'''))
C.append(code('''
# Print the full table. With only 11 rows we can SEE every call - reading the whole thing once,
# row by row, is how you catch a wrong source or a typo'd stress_profile before it skews a count.
print(calls.to_string())   # to_string() prints all rows (pandas otherwise truncates wide/long tables)
'''))
C.append(md('''
## PREDICT — the real group-by
`calls.groupby("stress_profile").size()` on the real eleven. From the table you just read, predict
the count next to each of `clean`, `pause_heavy`, `interruption`. They must add up to 11.
'''))
C.append(code('''
# YOUR TURN - lock your three real-pool predictions before the group-by reveals them.
my_clean = None          # how many 'clean' calls in the real eleven?
my_pause_heavy = None    # how many 'pause_heavy'?
my_interruption = None   # how many 'interruption'?

if any(v is None for v in (my_clean, my_pause_heavy, my_interruption)):
    print("fill in all three counts above, then re-run.")
else:
    total = my_clean + my_pause_heavy + my_interruption
    print("locked:", my_clean, my_pause_heavy, my_interruption, "| they sum to", total, "(should be 11)")
'''))
C.append(code('''
# The real group-by-and-count: bucket the 11 calls by stress_profile, count each bucket. This is the
# benchmark-table GROUP BY stress_profile, COUNT(*) - the exact move, now on real call data.
by_stress = calls.groupby("stress_profile").size()
print(by_stress)
print()
# A count without its total is half a fact (the Act-3 rule, stated early): we print the sum so the
# denominator travels WITH the counts - 4 means nothing until you know it is 4 of 11.
print("total calls:", by_stress.sum())

if my_clean is not None:
    got = by_stress.to_dict()
    print("clean match?", got.get("clean") == my_clean,
          "| pause_heavy match?", got.get("pause_heavy") == my_pause_heavy,
          "| interruption match?", got.get("interruption") == my_interruption)
'''))
C.append(md('''
## PREDICT — group by `source` now
Same table, different column: `calls.groupby("source").size()`. The pool is the hero call plus ten
SpokenWOZ calls. Predict the count next to `hero` and next to `spokenwoz`.
'''))
C.append(code('''
# Group by a DIFFERENT column - same verb (groupby.size), new question. Switching the grouping key
# is the whole power of the table: one structure answers 'by stress' and 'by source' with one word changed.
by_source = calls.groupby("source").size()
print(by_source)
print()
# again, carry the denominator so each count is a fraction-of-the-whole, not a naked number
print("total calls:", by_source.sum())
'''))
C.append(md('''
## OBSERVE + EXPLAIN
You grouped the **same** eleven rows two ways — by `stress_profile` and by `source` — changing one
word. One sentence: why is "switch the group key" the move that makes a table worth more than the
folder of files it came from? (Hint: the folder forces you to re-walk every file for each new question.)
'''))
C.append(md('''
## CHECKPOINT 3 (out loud)
1. The real `groupby("stress_profile").size()` returned three numbers that summed to 11 — why
   *must* they sum to 11, and what would a sum of 10 or 12 tell you about your load step?
2. You answered "by stress" and "by source" from one table. What did the *folder of JSON files*
   make you do for each new question that the table does not?
3. Did pandas' real group-by compute anything your toy by-hand dict-loop did not? (The honest
   answer is the point.)
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: counting calls by a label meant opening files and tallying in your head. After Act 2 you can: load
eleven real call logs into a DataFrame (one row per call), count a column **by hand** with a
dict-loop, get the *same* count from `groupby(...).size()`, and re-aim the question at a new column
by changing one word. The folder became a benchmark table you can interrogate.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (load -> group -> count, or 'switch the key')

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the load, the trap of a naked count, and your own group-by

## Break-it philosophy
You do not understand a table until you know how it lies and how it breaks. So we now damage the
load on purpose and watch what pandas does — because a real `data/` folder *will* hand you a call
that is missing a field, and "the count looked fine" is not a defense.
'''))
C.append(md('''
## PREDICT
We add a **twelfth** record that is missing the `stress_profile` field entirely (a real export
defect — the field was never written). When we build the DataFrame and `groupby
("stress_profile").size()`:
does pandas **crash**, **drop** that row from the counts, or **invent** a bucket for it? Commit to one.
'''))
C.append(code('''
# BREAK-IT (guided): a real export defect - one call dict missing 'stress_profile'. We feed it to
# the SAME pipeline and watch what the count does, because this is what a dirty data/ folder hands you.
dirty_records = records + [{"call_id": "swz_BROKEN", "source": "spokenwoz", "language": "en",
                            "workflow_type": "mystery"}]   # note: NO stress_profile key at all

dirty_df = pd.DataFrame(dirty_records)
# print the new row's stress_profile cell: pandas fills missing keys with NaN (not a crash) - seeing
# the NaN is the lesson, because NaN is exactly what the group-by is about to quietly skip.
print("dirty table rows:", dirty_df.shape[0])
print("broken row's stress_profile cell:", repr(dirty_df.iloc[-1]["stress_profile"]))
'''))
C.append(code('''
# Run the group-by on the dirty table. By default groupby DROPS rows whose key is NaN - so the
# broken call vanishes from the counts WITHOUT any error. We surface that by checking the total.
dirty_counts = dirty_df.groupby("stress_profile").size()
print(dirty_counts)
print("group-by total:", dirty_counts.sum(), "| but rows in table:", dirty_df.shape[0])
# the gap (11 counted, 12 rows) is the silent drop: no crash, no warning, just a missing call.
'''))
C.append(md('''
## Reading the result — the silent drop is the danger

No crash. No red. The group-by counted **11**, but the table had **12 rows** — the broken call was
silently dropped because its `stress_profile` was `NaN`, and `groupby` skips `NaN` keys by default.

This is the trap that ruins real evals: **the code ran, the numbers looked clean, and one call
disappeared.** If you report "11 calls" off this table you are *under-counting your own dataset* and
you would never know. The fix is not to trust the group-by total — it is to **check it against the
row count** every time. We do that next, and recover.
'''))
C.append(code('''
# Recovery: NEVER trust a group-by total over the table's own row count. We assert they match, and
# when they do not, we find the offenders explicitly instead of shipping an under-count.
counted = dirty_counts.sum()
rows = dirty_df.shape[0]
if counted != rows:
    # .isna() finds the rows pandas would silently drop - we name them rather than lose them.
    missing = dirty_df[dirty_df["stress_profile"].isna()]
    print(f"MISMATCH: group-by counted {counted} but table has {rows} rows.")
    print("dropped (missing stress_profile):", list(missing["call_id"]))
else:
    print("counts and rows agree - no silent drop")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. When a row's group key is `NaN`, what does `groupby().size()` do by default — and why is that
   *more* dangerous than a crash?
2. What single check turns that silent drop into a loud one?
3. The real eleven-call table summed to 11 earlier. Now you know *why* you checked that sum — say it.
'''))
C.append(md('''
## WRONG-INTUITION TRAP — "the most common kind in the pool is the most common kind in the world"

**The wrong belief:** "interruption ties for the most common kind of call (4 of 11), so our dataset
is *mostly* interruption calls / our agent mostly faces interruptions."

(Read the real counts back: `interruption` is **4**, `clean` is also **4**, `pause_heavy` is **3** —
interruption is one of the two *largest* buckets, tied with clean, not a lone winner. The slip we
are hunting is bigger than the tie, though.)

A raw count answers "how many rows landed here," and people reflexively read it as "how common this
is *in the world*." Those are different claims. Watch the count stay the same while the meaning
moves — because **how the pool was assembled** decides what the count is even allowed to say.
'''))
C.append(md('''
## PREDICT
`interruption` is 4 of 11 in our pool. **True or false:** that licenses the claim "about 36% of real
production calls are interruptions." Commit before the reveal.
'''))
C.append(code('''
# YOUR TURN - lock your verdict before the reveal.
# A count over a HAND-PICKED pool describes the POOL, not the world the pool was sampled from.
licenses_production_claim = None   # <- set to True or False

if licenses_production_claim is None:
    print("set licenses_production_claim to True or False above, then re-run.")
else:
    print("locked:", licenses_production_claim)
'''))
C.append(code('''
# The reveal, in data. This pool was CURATED for teaching: a hero call plus SpokenWOZ calls chosen
# to cover each stress profile - the proportions were DESIGNED, not sampled from production traffic.
profile_share = (calls.groupby("stress_profile").size() / len(calls) * 100).round(1)
print("share of THIS pool by stress_profile (%):")
print(profile_share)
print()
# The count (4 interruption) is a true fact ABOUT THIS POOL. It is NOT an estimate of production
# traffic, because the pool was not a random sample of production. Same number, two very different claims.
print("'4 of 11' describes the curated pool. It does NOT estimate production call mix -")
print("for that you would need a RANDOM sample of real traffic, which this is not.")
if licenses_production_claim is False:
    print("you locked False - correct: a curated count cannot speak for the unsampled world.")
'''))
C.append(md('''
## The reveal (in words)

The count `4` never changed. What changed is the **claim it licenses**. "4 of 11 calls in this pool
are interruptions" is true and defensible. "~36% of production calls are interruptions" is a
fabrication, because this pool was **hand-assembled to cover the stress profiles**, not randomly
sampled from live traffic. A count describes *the rows you have*; it can only speak for *the world*
if the rows were sampled from that world. This is the same family as P00's average-of-averages and
04's mean-hides-the-stall: **the number is real, the inference is the lie.** Every count you ship
gets its denominator *and* its provenance attached.
'''))
C.append(md('''
## BREAK-IT (learner-authored) — your own group-by

Author your own slice. Pick **one** column to group by (`source`, `language`, or `workflow_type`),
predict the buckets and their counts as a comment, then run. Guarded so it runs clean unfilled.
'''))
C.append(code('''
# YOUR TURN - self-authored BREAK-IT / group-by.
# my prediction: <write here which buckets you expect and roughly how many in each, and why>

group_column = None   # <- set to a column name string, e.g. "language" or "workflow_type"

# the guard: unfilled (None) this cell just prints a nudge, so a fresh notebook runs clean. Filled,
# it groups the REAL table by your chosen column and counts - the same verb on a key you picked.
if group_column is None:
    print("set group_column to a column name above (e.g. 'source'), then re-run.")
elif group_column not in calls.columns:
    # a friendly error beats a cryptic KeyError - we tell you the valid options instead of crashing.
    print(group_column, "is not a column. choose from:", list(calls.columns))
else:
    my_grouping = calls.groupby(group_column).size()
    print(my_grouping)
    print("total:", my_grouping.sum(), "(must be 11 - if not, a key was NaN and got dropped)")
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
1. A group-by total of 11 on our pool is a passed self-check. What does a total of **10** prove
   happened, and where?
2. "4 of 11 are interruptions" — write the one sentence that is true and the one sentence that is a
   lie, and name what separates them.
3. You grouped by a column you chose. Name a column where the buckets would be nearly all-distinct
   (close to one row each) — and why that group-by would be near-useless for counting.
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a clean-looking count felt like a fact, and "it ran" felt like success. After Act 3: a
`groupby` **silently drops** rows with a missing key (so you check the total against the row count,
every time), and a raw count describes **the rows you have** — it speaks for the world only if those
rows were *sampled* from it. The number is the easy part; the claim it licenses is the discipline.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the silent NaN drop, or 'count describes the pool, not the world')

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this table lives, the chart, and defending the counts

## Where this lives in VoiceForge (these are real files)

Nothing today was a metaphor. The pool you loaded is the real one the pipeline runs on:

| what you built today | where it lives for real | what it is |
|---|---|---|
| the 11-row table | `data/normalized/*.json` (hero + 10 SpokenWOZ) | one JSON file per call |
| the row contract | `schemas/call_log.md` | the fields every row must have |
| group-by counts | every later book that reaches across calls | 06 task-success rate, 07 failure tags, 13 confusion matrix, 23 splits |
| the per-call `turns` we dropped | `pipeline/signals.py` → `turn_metrics()` | book 04 goes *inside* one row's turns |

The split is worth naming: **this book counts whole calls (rows); book 04 counts events inside one
call (turns).** Same table-thinking, one level down. We confirm the real pool one more time, then
chart it.
'''))
C.append(code('''
# Re-confirm the real pool with the production-shaped question every later book asks: how many calls
# per stress_profile, with the denominator attached. This is the artifact books 06/07/23 build on.
summary = calls.groupby("stress_profile").size().rename("n_calls").reset_index()
summary["share_%"] = (summary["n_calls"] / len(calls) * 100).round(1)   # denominator travels with the count
print(summary.to_string(index=False))
print("total:", summary["n_calls"].sum(), "calls")
'''))
C.append(md('''
## PREDICT — the chart
We will draw one bar per `stress_profile`, height = number of calls. Before it renders: which bar is
tallest, and what is the tallest height? (You counted this in Act 2 — the chart just draws it.)
'''))
C.append(code('''
# One bar per stress_profile, height = call count. We chart the GROUP-BY result (not raw rows) because
# the bar chart's whole job is to make the buckets comparable at a glance. Every line says why it exists.
import matplotlib.pyplot as plt

labels = list(by_stress.index)    # x: the stress profiles (the BUCKETS / things)
heights = list(by_stress.values)  # y: how many calls in each (the MEASURE)

fig, ax = plt.subplots(figsize=(5, 3))   # fig = canvas, ax = the drawing area on it
ax.bar(labels, heights)                  # one bar per profile; height = number of calls
ax.set_xlabel("stress_profile")          # unlabeled axes are how charts mislead by omission,
ax.set_ylabel("number of calls")         # so labeling is a duty, not decoration
ax.set_title("call pool by stress profile (n=11)")   # n=11 in the title keeps the denominator visible
plt.show()
'''))
C.append(md('''
## Read the chart — the 4-question ritual
1. **x?** the three stress profiles. 2. **y?** number of calls. 3. **one bar?** one bucket of calls
sharing a stress profile. 4. **what does it license?** Exactly one claim: *in this pool of 11*,
interruption and clean are the larger buckets. It does **not** license "our agent mostly faces
interruptions" — that is the Act-3 trap, and this curated pool cannot speak for production traffic.
'''))
C.append(md('''
## The three-level explanation (same concept, three rooms)

- **To a beginner:** "We put every call on one line of a table — one row per call — and then we
  count the rows in each group, like sorting cards into piles and counting each pile."
- **To an engineer:** "Load `data/normalized/*.json` into a pandas DataFrame, one row per call,
  call-level fields as columns. `groupby('stress_profile').size()` is `GROUP BY ... COUNT(*)`;
  re-aim by swapping the key. Missing keys become `NaN` and are silently dropped by `groupby`, so
  assert the group total equals the row count. Counts ship with denominator and provenance."
- **To a founder:** "Our call data is a results table, not a pile of files. In one line we can say
  'this many calls of each kind,' which is the denominator every quality number on the dashboard
  divides by — and we can defend exactly what each count does and does not claim."
'''))
C.append(md('''
## Defense questions (×3 — try first, then open)

**1. "Why pandas? Couldn't you just loop over the JSON files and tally?"**
<details><summary>answer</summary>I did — by hand, first, and it matched. The loop holds for one
count. The moment the question becomes "by two columns," "the same but only spokenwoz," or "joined
to scores," the loop multiplies and the table answers with one changed word. pandas is the same idea
with the bookkeeping removed, and it does not get harder when the dataset grows.</details>

**2. "Your deck says '4 of 11 interruption calls.' Is that your production call mix?"**
<details><summary>answer</summary>No. That is a fact about this *curated* pool, assembled to cover
each stress profile, not a random sample of production traffic. The count is real; it describes the
rows I have. Estimating production mix would need a random sample of live calls, which this is not —
so I report it as a pool composition, with n=11 attached, never as a traffic estimate.</details>

**3. "How do you know your count didn't silently drop a call?"**
<details><summary>answer</summary>Because I assert the group-by total equals the table's row count.
`groupby` drops `NaN` keys without warning, so a missing `stress_profile` would quietly shrink the
count. The assert turns that silent drop into a loud failure that names the offending `call_id`
before any number reaches a slide.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own the whole loop: a folder of `data/normalized/*.json` → a DataFrame (one row per
call) → `groupby(key).size()` for counts you can re-aim by swapping the key → a self-check that the
total matches the row count → a chart that licenses exactly one claim, with its denominator on it.
You can place every piece in a real file and defend every count — including what it does *not* say.
Book 04 takes this same table-thinking one level down, inside a single call's turns.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. In this table, what is one row, one column, one cell?
2. The by-hand dict-loop tally, and the one line of pandas that replaces it (`groupby(key).size()`).
3. Why you check the group-by total against the row count — and what `NaN` keys do silently.
4. The trap: why "4 of 11 interruption" is true but "~36% of production calls" is a lie.
5. The benchmark analogy: a folder of call logs is a results table; group-by is `GROUP BY COUNT(*)`.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (the real pool / denominator+provenance / defending counts)
my_clean_sentence = ""      # the sentence you would say in a room about call data as a table

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"A DataFrame lets me treat calls like benchmark rows."**

Eleven JSON files became one table; "how many calls per stress profile?" became the same
`GROUP BY ... COUNT(*)` you have run your whole career — only the subject changed, from FLOPS to
phone calls. If your sentence captures that in your own words, this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "03_pandas_for_call_data.ipynb"   # <- this notebook's filename
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

**03 done** (pending your teach-back) → **04 · Turns, gaps, overlap, latency** — now that you can
load calls into a table and count across them, 04 goes *inside* one row's `turns` and computes
timing in milliseconds: the first measurement worth defending.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "03_pandas_for_call_data.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
