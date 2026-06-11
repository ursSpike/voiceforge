#!/usr/bin/env python3
# Builds P02_tables_and_pandas.ipynb per _BUILD_SPEC.md (four acts, audit markers, recurring cast).
# Mirrors build_P00.py exactly: md()/code() helpers, one idea per cell, reasoning comments on every
# code cell. The ONE atomic concept: rows are things, columns are facts; a DataFrame from a list of
# call dicts. Rerun: .venv/bin/python notebooks/build_P02.py
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
# P02 · Tables and pandas

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Say the **one true sentence** of a table out loud: a **row is a thing**, a **column is a fact about that thing**
2. Turn a **list of call dictionaries** into a **DataFrame** — and explain what that buys you over the raw list
3. Do four moves on call data both **by hand (a loop) and with pandas**: **count rows**, **select a column**, **filter rows**, **group-and-count**
4. Catch the classic table traps: a filter that copies vs. one that mutates, and a `groupby` count that quietly drops rows

This book uses tiny **toy** call data and the **recurring cast** (call_A, call_B, call_C). The topic is
small on purpose; the move — *a pile of objects becomes a grid you can filter, group, and count* — is
the spine of every measurement book after this one.
'''))
C.append(md('''
## 2 — Knowledge map

`P01 (objects: one call is a dict of facts) → THIS (Tables and pandas) → P03 (plots)`

Why this book exists, in one breath: in **P01** you learned to hold **one** call as a Python object and
walk its fields. But you never analyze one call — you analyze a **hundred**. The instant you have many
calls, the question changes from "what is *in* this object?" to "how many of these are failures? what is
the p90 latency *for Hinglish calls only*?" Those are **table questions**. A `for`-loop can answer them,
but it gets verbose and bug-prone fast. **pandas** is the tool that answers table questions in one line —
*after* you can answer them by hand. **P03** then plots the grouped counts this book produces.
'''))
C.append(md('''
## 3 — Baby intuition

You already know what a table is — you have seen a spreadsheet. The whole lesson hides in one sentence
most people never say out loud:

> **A row is a thing. A column is a fact about that thing.**

For us the *thing* is **one phone call**. So one row = one call. The *facts* are its columns:
which language it was in, how many turns it had, whether it succeeded. Read a table wrong — as a flat
"wall of numbers" — and every later question feels like a maze. Read it as **things-with-facts** and the
moves become obvious: *count the things*, *read one fact across all things*, *keep only the things that
match*, *pile the things up by a shared fact and count each pile*.
'''))
C.append(md('''
## 4 — The formal version

A **DataFrame** (pandas' table) is a 2-D grid with **labeled rows** (the index) and **named columns**.
The four moves you will drill, named:

| move | plain words | table question it answers |
|---|---|---|
| **count rows** | how many things are there | "how many calls do we have?" |
| **select a column** | pull one fact for every thing | "list every call's language" |
| **filter rows** | keep only things that match a test | "show only the failed calls" |
| **group + count** | pile things by a shared fact, count each pile | "how many calls per language?" |

Vocabulary from the spec we will reuse exactly: **call log**, **turn**, **speaker** (`user`/`agent`),
**outcome** (`success` / `partial` / `failure`), **language**, and the cast ids **call_A / call_B / call_C**.
Everything below is those four moves, first **by hand**, then with pandas — never the reverse.
'''))
C.append(md('''
## 5 — Why not just keep using loops? (the honest case for a library)

You can do all four moves with `for`-loops and `if`-statements — and we will, first, because that is the
only way to *see* what pandas does. So why add a library at all?

- A loop to count failures per language is ~6 lines and easy to get subtly wrong (forgot a key? counted
  the wrong field?). The pandas version is one line you can read like a sentence.
- Real analysis stacks moves: *filter to Hinglish, then group by outcome, then count*. Loops nest and
  blur; pandas chains stay flat.
- Every later book (timing in 04, scoring in 06, judges in 10) hands you results as a table. Speaking
  "table" fluently is not optional here.

The rule of this course still holds, hard: **manual first, library second.** A function you met before
the idea stays a black box forever. So we earn pandas — we do not start with it.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. Finish the sentence: "a row is a ___, a column is a ___."
2. For *our* data, what is the "thing" that one row represents?
3. Name the four table moves this book will drill (count / select / filter / group+count).
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a table is a grid of numbers, and pandas is "the thing you import to
deal with data." After Act 1 you should hold: a table is **things-with-facts** (one row = one call), and
pandas earns its place only because **table questions over many calls** are clumsy as loops. You have not
written any pandas yet — that is correct. We build the by-hand intuition first.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of "what is a table" now. Not mine - yours.
# Producing the sentence is the learning; reading mine would just feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
# It also guarantees a fresh, unfilled notebook still runs clean (the empty string just prints the nag).
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: from a pile of call dicts to a grid you can question

## First, the raw pile (look before you transform)

Course rule: **see the ugly input before any transformation.** Below is our toy data — a small **list of
call dictionaries**. This is exactly the shape P01 left you with: each call is a `dict` of facts. It mirrors
the real schema in `schemas/call_log.md` (real fields: `call_id`, `language`, `outcome`, plus a `turns`
list), trimmed to the few columns this lesson needs so the whole table fits on screen.
'''))
C.append(code('''
# The recurring cast as a LIST OF DICTS - the same call_A / call_B / call_C you met in P00/P01.
# We keep ids, languages, and outcomes IDENTICAL to the spec on purpose: every book shares this cast,
# so a fact you learn about call_C here is still true about call_C in book 10.
calls = [
    {"call_id": "call_A", "language": "English",        "n_turns": 6,  "outcome": "success"},
    {"call_id": "call_B", "language": "Hinglish",       "n_turns": 9,  "outcome": "partial"},
    {"call_id": "call_C", "language": "Telugu-English", "n_turns": 11, "outcome": "failure"},
]

# One print per row, so each ROW is visibly ONE THING (one call). Reading a table starts here:
# resist seeing a "block of data" - see three calls, each carrying four facts.
for call in calls:
    print(call)
'''))
C.append(md('''
## The reading ritual (say these three things about ANY table)

Before computing anything, narrate the table — same ritual you will use on every chart and grid in this
course:
1. **Row count:** "three rows" → three calls.
2. **What one row IS:** "one row = one call" (the *thing*).
3. **One single cell, aloud:** "call_B's language is Hinglish" (one *fact* about one *thing*).

If you cannot say those three, you cannot trust anything you compute from the table. Do it now, out loud.
'''))
C.append(md('''
## PREDICT
The list above has some number of calls in it.
**How many rows** will a table built from this list have — and **how many columns**?
(Count the dicts; count the keys in one dict.) Commit to both numbers before the next cell.
'''))
C.append(code('''
# YOUR TURN - predictions are written BEFORE the counting cell runs.
# We store them as variables so the notebook becomes a record of YOUR thinking, and the next
# cell can confront your guess with reality. That confrontation is the actual lesson.
my_row_prediction = None      # <- replace None with the number of rows you expect
my_col_prediction = None      # <- replace None with the number of columns you expect

if my_row_prediction is None or my_col_prediction is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("predictions locked - rows:", my_row_prediction, "| columns:", my_col_prediction)
'''))
C.append(md('''
## Move 1 of 4 — COUNT THE ROWS, by hand first

The most basic table question: **how many things?** With a list of dicts, "how many rows" is just "how
many items in the list." We compute it the boring way before any library touches it.
'''))
C.append(code('''
# Manual row count. len() on the LIST of calls = number of rows, because one dict = one row.
# We do this by hand FIRST so that when pandas reports the same number, it is a confirmation,
# not a magic trick you have to trust.
n_rows_by_hand = len(calls)
print("rows (by hand):", n_rows_by_hand)

# Columns = the facts each call carries = the keys of one dict. We read them off call_A.
# (Every dict here has the same keys; real data can be ragged - we will hit that trap in Act 3.)
columns_by_hand = list(calls[0].keys())
print("columns (by hand):", columns_by_hand)
print("column count (by hand):", len(columns_by_hand))

# Confront YOUR prediction - the metal-detector reading from the predict cell.
if my_row_prediction is not None:
    verdict = "matched" if (my_row_prediction == n_rows_by_hand and my_col_prediction == len(columns_by_hand)) else "DIFFERED"
    print("your prediction", verdict, "- a gap here is the exact spot to think about")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, out loud, in this shape: "the row count is ___ because ___, and the column count is ___
because ___." (Tie each number to *things* and *facts*, not to "the length of stuff.")
'''))
C.append(md('''
## Now — and only now — build the DataFrame

You can answer "how many rows/columns" by hand. So the DataFrame below is a **convenience over the list
you already understand**, not a mystery. `pd.DataFrame(list_of_dicts)` reads each dict as a row and the
union of keys as columns — exactly the mental model from cell one.
'''))
C.append(code('''
# pandas is the standard table library; we import it HERE, where it is first needed (course habit:
# imports live at the point of first use so you see WHY each one entered the notebook).
import pandas as pd

# pd.DataFrame over a LIST OF DICTS: each dict becomes one row, each key becomes one column.
# This is the single most common way a table is born in real analysis - from a pile of records.
df = pd.DataFrame(calls)

# Printing the DataFrame shows the grid WITH an index (the bold 0,1,2 on the left). That index is
# pandas labeling each row - it is the "which thing" handle we did not have in the bare list.
print(df)
'''))
C.append(md('''
## Read the grid the same way you read the list

Look at what printed. The leftmost column in **bold** (`0  1  2`) is the **index** — pandas' name-tag for
each row. The headers (`call_id language n_turns outcome`) are the **column names**. Nothing new is in
this table that was not in the list — pandas just **labeled the rows** and **aligned the facts into
columns**. Same things, same facts, now in a grid that knows its own shape.
'''))
C.append(md('''
## PREDICT
`df.shape` reports the table's size as `(rows, columns)`.
Given the by-hand counts you just computed, **what exact tuple** will `df.shape` print?
Commit before running.
'''))
C.append(code('''
# .shape is pandas' answer to the row/column question we already answered by hand.
# We compare them on purpose: a library you have verified once is a library you can trust later.
print("df.shape:", df.shape)              # (rows, columns)
print("matches by-hand rows?", df.shape[0] == n_rows_by_hand)
print("matches by-hand cols?", df.shape[1] == len(columns_by_hand))
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
1. When you pass a **list of dicts** to `pd.DataFrame`, what becomes a **row** and what becomes a **column**?
2. What is the **index**, and what did the bare Python list *not* give you that the index does?
3. Why did we compute the row/column counts **by hand before** calling `.shape`?
'''))
C.append(md('''
## Move 2 of 4 — SELECT A COLUMN (pull one fact for every thing)

Second table question: **read one fact across all things.** "What language was each call in?" By hand,
that is a loop collecting one key from every dict. We write that loop first.
'''))
C.append(md('''
## PREDICT
We are about to pull the `language` fact from every call.
**What three values, in what order**, will come out? Say them before running.
'''))
C.append(code('''
# Manual column-select: walk every call, grab ONE key. This IS what selecting a column means -
# "one fact, every thing." Seeing it as a loop first makes the pandas version legible later.
languages_by_hand = []
for call in calls:
    # we collect call["language"] specifically because that is the single fact this question asks for;
    # the other facts are irrelevant to "what language was each call in?"
    languages_by_hand.append(call["language"])
print("languages (by hand):", languages_by_hand)
'''))
C.append(code('''
# The pandas way: df["language"] returns that whole column as a Series (a labeled 1-D column).
# It does EXACTLY the loop above - one fact, every row - but keeps the row labels (the index) attached,
# which is why a Series prints as index->value pairs, not a bare list.
language_col = df["language"]
print(language_col)
print("---")
print("type:", type(language_col).__name__)   # Series, not list - the labels are the difference
'''))
C.append(md('''
## A Series is a column with its row-labels still attached

The bare loop gave you `['English', 'Hinglish', 'Telugu-English']` — values only. `df["language"]` gives
you a **Series**: the same values, but each still tied to its row label (0, 1, 2). That attachment is the
whole point — when you later filter or sort, every value remembers **which call it came from**. A list
forgets; a Series does not.
'''))
C.append(md('''
## EXPLAIN gate
One sentence: what does selecting a column give you that selecting a single cell does not — and what does
a **Series** carry that a plain Python **list** of the same values throws away?
'''))
C.append(md('''
## Move 3 of 4 — FILTER ROWS (keep only the things that pass a test)

Third table question: **keep only matching things.** "Show me the calls that did *not* succeed." By hand:
loop every call, keep the ones where a test is true. We build the test, then the keep-loop.
'''))
C.append(md('''
## PREDICT
We will keep only calls whose `outcome` is **not** `"success"`.
**Which call ids** survive that filter, and **how many rows** remain? Commit before running.
'''))
C.append(code('''
# Manual filter: a plain keep-loop. For each call we evaluate ONE boolean test and keep the row only
# if it passes. "Filtering" is nothing more mysterious than this - a test applied to every thing.
not_success_by_hand = []
for call in calls:
    # the test is outcome != "success": we want every call that fell short (partial OR failure),
    # because "did the call NOT succeed?" is the question a quality reviewer actually asks.
    if call["outcome"] != "success":
        not_success_by_hand.append(call)
for call in not_success_by_hand:
    print(call)
print("rows kept (by hand):", len(not_success_by_hand))
'''))
C.append(md('''
## The pandas filter, in two visible steps (the mask, then the keep)

pandas does not hide the test — it makes it a **column of True/False** called a **boolean mask**. Step 1:
build the mask (one True/False per row). Step 2: index the DataFrame with the mask to keep the True rows.
We print the mask on its own first, because that intermediate is where every filter bug hides.
'''))
C.append(code('''
# STEP 1 - the mask. df["outcome"] != "success" compares EVERY row at once and returns a Series of
# booleans (one True/False per call). Printing the mask alone is the habit that catches filter bugs:
# if the mask is wrong, the filtered table will be wrong, and you want to see WHY here, not downstream.
mask = df["outcome"] != "success"
print(mask)
'''))
C.append(code('''
# STEP 2 - the keep. df[mask] returns only the rows where the mask is True. Same result as the by-hand
# keep-loop, but read as one expression: "from df, keep the rows where outcome is not success."
not_success_df = df[mask]
print(not_success_df)
print("rows kept (pandas):", len(not_success_df))

# Cross-check against the manual answer - two methods agreeing is how you earn trust in the one-liner.
print("matches by-hand row count?", len(not_success_df) == len(not_success_by_hand))
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. A pandas filter happens in two steps — name them (what is the **mask**, what does **`df[mask]`** do?).
2. Why is printing the mask **by itself** a good debugging habit before trusting the filtered table?
3. The mask `df["outcome"] != "success"` kept `partial` AND `failure`. Why both?
'''))
C.append(md('''
## Move 4 of 4 — GROUP + COUNT (pile things by a shared fact, count each pile)

The big one, the move this whole book is building toward. Fourth table question: **how many things in each
pile?** "How many calls per language?" or "how many successes vs. failures?" By hand: walk every call and
tally into a dictionary keyed by the grouping fact. We build that tally first — it *is* what `groupby`
does inside.
'''))
C.append(md('''
## PREDICT
We will group the three calls **by `outcome`** and count each group.
Since each cast call has a different outcome, **what count** will land in each of `success`, `partial`,
`failure`? Commit before running.
'''))
C.append(code('''
# Manual group-and-count: a tally dictionary. The KEY is the fact we group by (outcome); the VALUE is a
# running count. This pattern - "bucket by a shared fact, increment the bucket" - is the literal engine
# inside groupby. Building it by hand means groupby will never be a black box to you.
counts_by_hand = {}
for call in calls:
    key = call["outcome"]                      # the pile this call belongs to (its outcome)
    # .get(key, 0) reads the current tally (0 if this is the first call of its kind), then we add one.
    # This is the safe way to tally without pre-declaring every possible key.
    counts_by_hand[key] = counts_by_hand.get(key, 0) + 1
print("counts by outcome (by hand):", counts_by_hand)
'''))
C.append(code('''
# The pandas way: groupby the column, then count. Read it left to right as a sentence:
# "group the rows by outcome, then for each group, count how many call_ids are in it."
# We count the call_id column specifically because call_id is never missing - it is the row's identity,
# so its count is a faithful "rows per group" (a column with blanks would undercount; that is Act 3).
counts_pandas = df.groupby("outcome")["call_id"].count()
print(counts_pandas)
print("---")
# Same numbers as the by-hand tally - converting to a plain dict makes the comparison obvious.
print("as a dict:", counts_pandas.to_dict())
'''))
C.append(md('''
## Read the grouped result as a tiny table

`groupby("outcome")["call_id"].count()` returns a Series whose **index is now the outcomes** (`failure`,
`partial`, `success`) and whose **values are the pile sizes**. The grouping fact became the row labels.
That is the shape every count-by-category produces — and it is exactly the shape **P03** will hand to a
bar chart: one bar per index label, bar height = the count.
'''))
C.append(md('''
## The whole point, now group by LANGUAGE (the must-cover question)

The spec's headline table question for this book: **group by language, count successes and failures.**
We do it by grouping on **two** facts at once — `language` then `outcome` — so each pile is "calls that
share both a language and an outcome." With our toy cast every pile has exactly one call, which makes the
result easy to read and verify by eye.
'''))
C.append(md('''
## PREDICT
We group by **`language` and then `outcome`**, and count.
Our three calls are English/success, Hinglish/partial, Telugu-English/failure.
**How many groups** will there be, and **what count** sits in each? Commit before running.
'''))
C.append(code('''
# Group by TWO facts: language, then outcome. The result is indexed by the (language, outcome) PAIR -
# this is how you answer "successes and failures broken down per language", the table this book exists
# to teach. count() on call_id gives rows-per-pile, same trustworthy identity-column trick as before.
by_lang_outcome = df.groupby(["language", "outcome"])["call_id"].count()
print(by_lang_outcome)
print("---")
print("number of non-empty groups:", by_lang_outcome.shape[0])
'''))
C.append(md('''
## EXPLAIN gate
One sentence: when you `groupby(["language", "outcome"])`, what does **one row of the result** represent,
and where did the `language`/`outcome` labels on the left come from? (Trace them back to the grouping
keys.)
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: pandas was "the data library you import." After Act 2 you should own the four moves as
**things-with-facts operations**, each done by hand *then* in one pandas line: **count rows** (`len` →
`.shape`), **select a column** (loop-collect → `df["col"]` Series), **filter rows** (keep-loop → mask then
`df[mask]`), **group + count** (tally dict → `groupby(...).count()`). Crucially: every pandas one-liner
matched a by-hand answer you computed first. That match is *why* you can trust the one-liner.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (the four moves / manual-first / groupby - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))
C.append(md('''
## YOUR TURN — select a different column

You selected the `language` column with me. Now select a **different** fact for every call, your choice
(`n_turns`, `outcome`, or `call_id`). Predict the three values first, then read them off.
'''))
C.append(code('''
# YOUR TURN - pick ONE column name and pull it for every call.
# my prediction (the three values I expect, in row order): <write here>
my_column = None             # <- replace None with a column name string, e.g. "n_turns"

# Guard so an UNFILLED notebook still runs clean: we only touch df[...] once you have chosen a column.
# This is the course's learner-cell pattern - None placeholder + guard = no crash downstream.
if my_column is None:
    print("set my_column to a column name above (e.g. 'n_turns'), then re-run.")
else:
    # we print the selected Series so you can match it against your written prediction, row by row
    print(df[my_column])
'''))
C.append(md('''
## YOUR TURN — filter on a number, not a string

You filtered on `outcome` (a text test). Now filter on `n_turns` (a **number** test): keep only the calls
with **more than 7 turns**. Predict which call ids survive, then build the mask and keep.
'''))
C.append(code('''
# YOUR TURN - numeric filter. Build a mask with a > test, then keep.
# my prediction (which call ids have more than 7 turns): <write here>
turn_threshold = None        # <- replace None with the number 7

if turn_threshold is None:
    print("set turn_threshold to 7 above, then re-run.")
else:
    # df["n_turns"] > turn_threshold builds the boolean mask (one True/False per call); a numeric
    # comparison works exactly like the != text comparison did - same two-step filter, different test.
    long_calls_mask = df["n_turns"] > turn_threshold
    print("mask:")
    print(long_calls_mask)
    print("kept rows:")
    print(df[long_calls_mask])      # the rows where the mask is True
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: the ways a table quietly lies

## Break-it philosophy

A table is a confident-looking grid; that confidence is exactly what makes its failures dangerous. We now
damage tables on purpose and watch how they fail — sometimes loudly (a crash), sometimes **silently** (a
number that is wrong but looks fine). Surprise here, at your desk, is education. Surprise on the demo stage
is a disaster.
'''))
C.append(md('''
## PREDICT
We ask for a column that does not exist: `df["lang"]` (we never named it that — the column is `language`).
Does pandas **crash loudly**, or hand back something **empty/blank**? Commit to one before running.
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. Read what happens, do not fix it yet.
# EXPECTED FAILURE FOR LEARNING - the executor allows this raise so the lesson can land.

# We ask for "lang", a column that does not exist (the real name is "language"). The question this
# answers: when you typo a column name, does pandas guess, return blank, or refuse? Watch it refuse.
typo_column = df["lang"]
print(typo_column)
'''))
C.append(md('''
## Reading the error (bottom-up, always)

The wall of red is a **traceback**. The ritual: read the **last line first** — it names *what* went wrong
(`KeyError: 'lang'` — "there is no column called lang"). Then walk **upward** to find *where* (the line
asking for `df["lang"]`).

And notice the **good news in this failure**: pandas **crashed** rather than inventing an empty column.
A `KeyError` costs you ten seconds. The truly dangerous table bugs are the ones that **don't** crash —
they hand you a clean-looking wrong number. The next break-it is one of those.
'''))
C.append(code('''
# The fix is to use the real column name. We print the actual columns so the correct name is unmissable -
# this is the debug ritual's step 1 ("look at the raw thing") applied to a DataFrame's schema.
print("actual columns:", list(df.columns))

# now the correct select, which succeeds because "language" is a real column
print(df["language"])
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. What error does pandas raise for a misspelled column name, and how do you read a traceback?
2. Why is a **loud `KeyError`** friendlier than pandas silently returning a blank column?
3. What is the first thing to print when a column name "isn't working"?
'''))
C.append(md('''
## YOUR break now — author your own table damage

Pick ONE way to break a table operation, predict the failure in a comment, then run it. Ideas: ask for a
column that does not exist, `groupby` a column that does not exist, or filter with a column name typo.
Predict precisely — *which error, or which wrong/blank result?*
'''))
C.append(code('''
# YOUR TURN - self-authored BREAK-IT.
# EXPECTED FAILURE FOR LEARNING - leave this marker so the executor tolerates a raise if you choose one.
# my prediction (exactly what will happen and why): <write here>

# Uncomment ONE line to break it (or write your own damage), then run and compare to your prediction:
# bad = df["outcom"]                      # typo'd column name -> ?
# bad = df.groupby("stress_profile")      # a column we never put in this toy table -> ?
# bad = df[df["n_turns"] > "seven"]       # comparing a number column against a STRING -> ?

# Safe fallback so an UNFILLED notebook still runs clean: with every break line commented out, this
# prints a reminder instead of crashing. Uncomment a line above to actually do the break.
print("uncomment one break line above (or write your own), then re-run to see how it fails.")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — "filtering a DataFrame gives me a fresh, independent table"

**The wrong belief:** "after `subset = df[mask]`, `subset` is its own separate table — editing it is safe,
and editing `df` won't touch it."

Half-right, half a trap. A filtered subset *looks* independent. But pandas often hands back a **view onto
the original's memory**, not a guaranteed copy — so writing into the subset can warn, silently fail, or
(in older patterns) reach back and mutate `df`. The next cells prove the danger, then show the one-word
fix every careful analyst uses: **`.copy()`**.
'''))
C.append(md('''
## PREDICT
We take `subset = df[df["outcome"] != "success"]`, then change a value **inside `subset`**.
Will the matching value in the **original `df`** stay put, or could it change too? Commit before running.
'''))
C.append(code('''
# We rebuild a clean df so this trap is self-contained and re-runnable without depending on edits above
# (Act 1's lesson: kernel memory is sticky; a fresh df here means this cell tells the truth on every run).
df = pd.DataFrame(calls)

# Take a filtered subset WITHOUT copying - the exact pattern that invites the trap.
subset = df[df["outcome"] != "success"]

# Try to "fix up" a label inside the subset. .loc names the row by its index label and the column.
# We wrap it so that whether pandas warns OR mutates, the notebook keeps running and the lesson lands:
# the point is to SEE the ambiguity, not to crash on it.
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")          # silence the SettingWithCopyWarning so output stays readable
    subset.loc[subset.index[0], "outcome"] = "EDITED"

print("subset after edit:")
print(subset)
print("--- original df (did it stay clean?) ---")
print(df)
'''))
C.append(md('''
## The reveal — and the fix

Whether or not `df` visibly changed on your machine, the deeper point stands: **a filtered slice does not
promise to be an independent copy.** Relying on "it's a separate table" is relying on undefined behavior —
the kind of silent wrongness that survives every green run and only bites on the demo. The fix is explicit
and cheap: when you intend to edit a subset, make your intent unambiguous with **`.copy()`**.
'''))
C.append(code('''
# The fix: ask for an explicit, independent copy. Now edits to the subset CANNOT reach the original,
# and pandas stops warning - because you stated your intent instead of leaving it ambiguous.
df = pd.DataFrame(calls)                                   # clean slate again
subset_safe = df[df["outcome"] != "success"].copy()       # .copy() = "I want my own table, detached"

subset_safe.loc[subset_safe.index[0], "outcome"] = "EDITED"   # edit the copy freely

print("edited copy:")
print(subset_safe)
print("--- original df stayed clean: ---")
print(df)                                                  # untouched, guaranteed, because the copy is detached
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
1. Why is "a filter returns an independent table" a dangerous thing to assume?
2. What does `.copy()` change about your intent — and about pandas' behavior?
3. Which is scarier for a demo: a `KeyError` crash, or a slice that silently shares memory? Why?
'''))
C.append(md('''
## WRONG-INTUITION TRAP 2 — "groupby counts every row, so the pile sizes always add up to the total"

**The wrong belief:** "`groupby(col).count()` always tallies all my rows, so the group counts sum to the
number of rows." A `count()` counts **non-missing** values in the chosen column. If you count a column that
has **blanks**, every blank silently vanishes from its pile — the table still prints, no error, and your
totals quietly fall short.
'''))
C.append(md('''
## PREDICT
We add a 4th call whose `outcome` is **missing** (`None`), then run
`groupby("language")["outcome"].count()`. Will the four calls' counts sum to **4**, or to **3**?
Commit before running.
'''))
C.append(code('''
# A realistic mess: a 4th call where the outcome was never recorded (None). Real call logs have holes
# like this constantly - a field the pipeline failed to fill. We KEEP the hole instead of cleaning it,
# because the whole lesson is what counting does in the presence of holes.
calls_with_hole = calls + [
    {"call_id": "call_D", "language": "English", "n_turns": 4, "outcome": None},
]
df_hole = pd.DataFrame(calls_with_hole)
print(df_hole)
print("total rows in table:", len(df_hole))
'''))
C.append(code('''
# Count the OUTCOME column per language. count() ignores None, so call_D (outcome=None) is NOT counted,
# even though it is plainly a row in the table. Watch the English pile read 1, not 2.
bad_total = df_hole.groupby("language")["outcome"].count()
print(bad_total)
print("sum of group counts:", bad_total.sum(), "<- compare to total rows:", len(df_hole))
'''))
C.append(md('''
## The reveal — count *what*, exactly?

`count()` on `outcome` counted **only the rows where `outcome` is present** — so the missing-outcome call
evaporated and the group totals sum to 3, not 4. The table printed cleanly; nothing warned you. This is the
soul of the course's central trap (P00's "green cells prove nothing"): **the cell ran, the number is
wrong.** The fix is to count a column that is never missing — the row's identity, `call_id` — or to count
the rows themselves with `.size()`.
'''))
C.append(code('''
# Two honest fixes that count ROWS, not non-missing values:
# (a) count an identity column that is never blank - call_id is the row's name, always present.
fixed_by_id = df_hole.groupby("language")["call_id"].count()
print("counting call_id (never missing):")
print(fixed_by_id)
print("sum:", fixed_by_id.sum(), "<- now matches total rows", len(df_hole))
print("---")
# (b) .size() counts ROWS per group directly, blanks included - it asks "how many rows", not "how many
# present values", so missingness cannot make rows disappear.
print("groupby(...).size() counts rows including blanks:")
print(df_hole.groupby("language").size())
'''))
C.append(md('''
## Asking AI for help, well (you live in Cursor — this is workflow, not philosophy)

**Lazy ask (produces a lecture):** "explain groupby"

**Strong ask (produces a correction to your model):**
> "Here is my cell: `df_hole.groupby('language')['outcome'].count()`. I predicted the group counts would
> sum to 4 (I have 4 rows). Instead they sum to 3. Here is the raw input: 4 calls, and call_D's `outcome`
> is `None`. **Where is my mental model of `count()` wrong?**"

The template: *what I predicted · what happened instead · the raw input · where is my model wrong*. You
bring the thinking; the AI brings the correction. Reverse those roles and the AI learns while you watch.
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a table that prints is a table you can trust. After Act 3: a misspelled column **crashes loudly**
(`KeyError`, the friendly failure); a filtered slice **may share memory** with its parent unless you say
`.copy()`; and `groupby(...).count()` counts **non-missing values**, so blanks silently shrink your piles
— count `call_id` or `.size()` to count *rows*. Loud crashes cost seconds; silent wrong tables cost demos.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the copy trap or the count-the-blanks trap are strong picks)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where this table lives in the real VoiceForge pipeline

## This is not a toy detour — it is the real data shape

The list-of-dicts you turned into a DataFrame is the **literal shape of VoiceForge's call data**. The
repo carries **11 real normalized calls** at `data/normalized/*.json` (the hero call plus 10 SpokenWOZ
conversations), each a JSON object with exactly the fields you have been handling — `call_id`, `language`,
`stress_profile`, `outcome`, and a `turns` list (schema in `schemas/call_log.md`). Loading that folder is
"a pile of call dicts," and the first thing any analysis does is `pd.DataFrame(those_dicts)`. The next
cell shows the real loader pattern — guarded so it runs whether or not the data is present on your machine.
'''))
C.append(code('''
# The real loader pattern: read every normalized call JSON into a list of dicts, then DataFrame it.
# We GUARD on the folder existing so this notebook runs clean anywhere (a fresh checkout, a grader's box).
import json
from pathlib import Path

# walk up from the working dir to find the repo root (the folder that holds rubric.yaml) - the same
# anchor pipeline/signals.py and run_nb.py use, so paths resolve no matter where the kernel started.
root = next((a for a in [Path.cwd(), *Path.cwd().parents] if (a / "rubric.yaml").exists()), None)
norm_dir = root / "data" / "normalized" if root else None

if norm_dir and norm_dir.exists():
    # one dict per real call - exactly the "pile of objects" this whole book is about
    real_calls = [json.loads(p.read_text()) for p in sorted(norm_dir.glob("*.json"))]
    # keep only the few top-level facts that make a flat table; the nested "turns" list belongs to P03/04
    flat = [{"call_id": c.get("call_id"), "language": c.get("language"),
             "stress_profile": c.get("stress_profile"), "n_turns": len(c.get("turns", []))}
            for c in real_calls]
    real_df = pd.DataFrame(flat)
    print("loaded real calls:", real_df.shape[0], "rows")
    print(real_df)
else:
    # fresh checkout without the data folder - the lesson still stands on the toy cast
    real_df = None
    print("data/normalized not found here - the toy `df` above demonstrates the identical move.")
'''))
C.append(md('''
## The same four moves, now on real calls

If the real data loaded, the move you drilled all book — **group by a fact, count the piles** — answers a
real question: *how many real calls do we have of each stress profile (clean / pause_heavy /
interruption)?* That is the exact distribution **P03** will turn into a bar chart, and the exact slicing
**book 04** filters before computing p50/p90 timing. Same `groupby().size()` you just learned.
'''))
C.append(code('''
# Group the REAL calls by stress_profile and count rows per pile - the book's headline move on live data.
# We use .size() (counts rows, blanks included) because here we genuinely want "how many calls per
# profile", and stress_profile being absent on a call should still count that call as a row somewhere.
if real_df is not None:
    print("real calls per stress profile:")
    print(real_df.groupby("stress_profile").size())
else:
    # guarded fallback: demonstrate the identical call on the toy table so the cell always runs + teaches
    print("toy stand-in - calls per language:")
    print(df.groupby("language").size())
'''))
C.append(md('''
## PREDICT (connect it forward to P03)

The grouped count you just produced is a Series: **index = the category**, **values = the pile sizes**.
P03 feeds exactly this into a bar chart. **What will be on the x-axis, and what will the height of each
bar be?** Write it in the next cell — P03 will confront your answer.
'''))
C.append(code('''
# YOUR TURN - predict the P03 bar chart that this grouped count becomes.
my_xaxis = ""        # what sits on the x-axis (the category labels)?
my_bar_height = ""   # what does the height of each bar represent?

if len(my_xaxis.strip()) < 3 or len(my_bar_height.strip()) < 3:
    print("fill in both my_xaxis and my_bar_height above, then re-run.")
else:
    print("x-axis:", my_xaxis)
    print("bar height:", my_bar_height)
'''))
C.append(md('''
## Where tables fail you in the real pipeline (honesty applies here too)

- **Silent missingness** — a judge or loader leaves `outcome`/`score` blank; `count()` shrinks the pile
  and the dashboard under-reports. Countermeasure: count an identity column or `.size()`; check that group
  counts sum to the row total. (You lived this in Act 3.)
- **Ragged records** — not every real call dict carries every key; `pd.DataFrame` fills the gap with `NaN`,
  and a later `groupby` on that column drops rows. Countermeasure: inspect `df.columns` and missing-counts
  before trusting a grouped number.
- **The mean trap rides along** — a column of latencies summarized with `.mean()` hides the one 20-second
  silence. Countermeasure (from P00, enforced from book 04): report **p50/p90**, never a lone mean.
- **Slice aliasing** — editing a filtered subset without `.copy()` mutates the source. Countermeasure:
  `.copy()` whenever you intend to write.
'''))
C.append(md('''
## The concept at three levels (every book ends with one of these)

- **To a beginner:** "a table is a list of things where every thing carries the same facts; pandas lets
  me count them, pull one fact, keep the ones I want, and pile them up — in one line each."
- **To an engineer:** "a DataFrame is columnar records with a labeled index; the four primitives are
  shape, column-selection (Series), boolean-mask filtering, and split-apply-combine via groupby — and
  `count()` is non-null-aware, which is a footgun on sparse columns."
- **To a founder:** "every quality number we show — success rate, failures per language, p90 latency —
  is a group-and-count over the call table; the person showing it can reproduce each number by hand and
  knows exactly which blanks could make it lie."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "Why use pandas at all — couldn't you just loop?"**
<details><summary>answer</summary>I can, and I showed every move as a loop first. pandas earns its place once moves stack — filter then group then count stays one readable chain instead of nested loops — and because every later result in this project arrives as a table. The loop taught me what the one-liner does; the one-liner keeps real analysis legible.</details>

**2. "Your group counts didn't sum to the number of calls once. Is your data broken?"**
<details><summary>answer</summary>The data had a missing `outcome`, and `count()` tallies non-missing values — so the blank row dropped out of its pile. The data isn't broken; my count was answering "how many present values" when I meant "how many rows." Fix: count the identity column `call_id`, or use `.size()`. I now check that group counts sum to the row total.</details>

**3. "How do you know a filtered table is safe to edit?"**
<details><summary>answer</summary>I don't assume it is. A filtered slice can be a view onto the original's memory, so editing it is undefined behavior that may mutate the source or warn. When I intend to edit a subset I take `.copy()` to detach it explicitly. Stating intent beats relying on whatever pandas happened to return.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: the list-of-dicts → DataFrame move is the **real** entry point for VoiceForge's 11
normalized calls (not a toy contrivance); the **group-and-count** you drilled is the same operation behind
every quality number and every P03 bar; and you can name the real ways a table lies (missingness,
raggedness, the mean trap, slice aliasing) with a countermeasure for each. You are ready to plot these
counts in P03.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The one true sentence of a table (rows are ___, columns are ___) and what one row IS for us.
2. How a **list of dicts** becomes a **DataFrame** — what becomes a row, a column, the index.
3. The four moves, each as **by-hand** and **pandas**: count rows · select a column · filter rows · group+count.
4. The two table traps: a filtered slice may **share memory** (fix: `.copy()`); `count()` skips **blanks**
   (fix: `.size()` or count an identity column).
5. Where this lives in VoiceForge: `data/normalized/*.json` → DataFrame → group-and-count → the P03 bar.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (the real-data connection is a strong candidate)
my_clean_sentence = ""      # the sentence you'd say in a room about what a DataFrame buys you

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"A DataFrame turns a pile of call objects into rows I can filter, group, and count."**

If yours captures that in your own words — things-with-facts, and the four moves over many calls — this
book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "P02_tables_and_pandas.ipynb"   # <- this notebook's filename
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

**P02 done** (pending your teach-back) → **P03 · Plots** — the grouped counts you just produced become
bars and dots, read with the 4-question chart ritual from P00 → then P04 debugging → then VoiceForge book
00. The table you can now filter, group, and count is the thing every chart in this course draws.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "P02_tables_and_pandas.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
