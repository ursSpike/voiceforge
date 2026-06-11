#!/usr/bin/env python3
# Builds 25_charts_that_matter.ipynb — VoiceForge University book 25 (Charts that matter).
# The ONE atomic concept: the five demo charts. A chart is a CLAIM you read aloud, or it is decoration.
# Rerun: .venv/bin/python notebooks/build_25.py
# Then gate:  .venv/bin/python notebooks/run_nb.py   notebooks/25_charts_that_matter.ipynb   (EXECUTION OK)
#             .venv/bin/python notebooks/audit_nb.py notebooks/25_charts_that_matter.ipynb   (ALL PASS)
# Style/rhythm/comment-density/learner-cell pattern cloned from build_P00.py (the gold reference).
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
# 25 · Charts that matter

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Build the **five demo charts** of a VoiceForge scorecard, over the real normalized pool
   (`data/normalized/*.json`): **success-by-language**, **failure distribution**,
   **cost-per-successful-call**, **turns-by-language**, and **voice-fail vs completion**.
2. Read EVERY chart aloud with the **4-question ritual** (what is x · what is y · what is one
   mark · what claim does it license) — and just as hard, name the claim it does **not** license.
3. Derive each chart's numbers **by hand first** from the call objects, so no bar is a black box:
   a success proxy, a failure tally, a cost proxy, a turn count — all from fields you can point at.
4. Defend the load-bearing claim of this book: **a chart you cannot narrate is decoration** —
   a picture earns its place on a slide only when you can say, in one sentence, what it proves.

Topic looks small (five little plots). The claim is not small: book 26 stacks these five into a
**dashboard**, and a dashboard is only as honest as the narrations behind its tiles. A chart you
cannot read aloud does not get safer when you put four of them in a grid — it gets louder.
'''))
C.append(md('''
## 2 — Knowledge map

`24 (annotation: ground-truth labels) → THIS: five charts you can narrate → 26 (the dashboard)`

Why this book exists, right here on the ladder. Book 24 gave you **labels you trust** — human
ground truth attached to calls. A chart is only as honest as the numbers under it, so trustworthy
labels had to come first: you cannot narrate a bar whose height you do not believe. This book
turns those trusted numbers into **five specific pictures**, each read aloud as a claim. Book 26
then arranges these same five into one **dashboard** — a single screen a buyer reads in ten
seconds — which only works if each tile was already a sentence you can defend.

No lesson floats in the void: previous = "labels you trust", current = "five charts you can
narrate", next = "those five, arranged as one dashboard". Annotation feeds charts; charts feed the
dashboard.
'''))
C.append(md('''
## 3 — Baby intuition

Picture two people showing the same bar chart on a stage.

- **Person 1** points at it and says: "look, the numbers." Then waits. The room waits back.
  The chart is wallpaper — pretty, and saying nothing anyone can repeat.
- **Person 2** points at the *shortest* bar and says: "this is Tenglish; it completes **half** as
  often as English; that gap is the thing we are here to fix." Heads nod. The chart became a claim.

Same pixels. The difference is not the chart — it is whether a **sentence** rode in on it. A chart
that arrives without its sentence is decoration: it decorates the slide and informs no one. The
whole book is the drill that turns Person 1 into Person 2, five times.
'''))
C.append(md('''
## 4 — The formal version

Two terms we will use precisely all book:

- **the 4-question ritual** — the fixed way to read any chart, from P00 and P03: (1) what is on
  the **x**-axis, (2) what is on the **y**-axis, (3) what does **one mark** (one bar/dot/strip)
  stand for, (4) what **claim** does this chart license — and what claim does it NOT. A chart you
  can answer all four for is a chart you can narrate.
- **decoration** — a chart with no narration attached: it renders, it looks like analysis, and it
  licenses no sentence you could defend in a room. Decoration is not "an ugly chart"; a beautiful
  chart with no readable claim is still decoration.

The course-wide test "green cells prove nothing" (P00) has a sibling here: **a rendered chart
proves nothing.** Both run clean and can still say nothing true. The bar for a chart is the same
as the bar for a notebook — can you close it and say what it means.
'''))
C.append(md('''
## 5 — Why this book is "charts that *matter*" and not "how to use matplotlib"

You already know how to draw a bar (P03 taught the mechanics). This book is not about the *drawing*
— it is about the **five specific charts** a VoiceForge scorecard actually shows a buyer, why each
one earns its place, and how to read each as a claim. Plenty of charts could be drawn from a call
pool; these five are the ones that answer the questions a buyer is actually asking:

1. **success-by-language** — does it work for everyone, or only my English callers?
2. **failure distribution** — when it breaks, *how* does it break?
3. **cost-per-successful-call** — what does one *good* outcome cost me?
4. **turns-by-language** — is the conversation getting longer (and pricier) in some languages?
5. **voice-fail vs completion** — do the timing failures actually track the bad outcomes?

We build all five from the same 11 real calls, and read every one aloud.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just what it does.

# PREDICT - what exact text appears below? We print a sentence so your first action in this book
# is a run you committed to, and so you see WHERE output lands (directly under the cell).
print("a chart is a claim you can read aloud, or it is wallpaper")
'''))
C.append(code('''
# Load every real normalized call once, here, so every chart in this book draws from the SAME pool
# (eleven calls cannot drift between charts if there is one list). We resolve the repo root by
# walking up to the folder that holds data/normalized, so this runs whatever the kernel's cwd is.
import json
from pathlib import Path
root = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "normalized").exists())
files = sorted((root / "data" / "normalized").glob("*.json"))   # sorted => stable, reproducible order
calls = [json.loads(f.read_text()) for f in files]              # disk text -> dicts (json.loads from book 02)
print("loaded", len(calls), "real calls from data/normalized/")
'''))
C.append(code('''
# Look at the RAW pool before charting anything (course rule: see the input before transforming it).
# One print per call so each call reads as one THING; we show only the fields the charts will use.
for c in calls:
    print(f"{c['call_id']:<14} lang={c['language']:<6} turns={len(c['turns']):>2}  profile={c['stress_profile']}")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What is the pass condition for a chart in this book — what makes it "matter" rather than decorate?
2. Name the four questions of the chart-reading ritual.
3. Which book feeds this one (what did it give us that a chart needs), and which book consumes these
   five charts next?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a chart is the output of analysis — you make it and move on.
After Act 1 you should know: a chart is an **input to a sentence**. It earns its place only when you
can narrate it as a claim (the 4-question ritual), and a beautiful chart with no readable claim is
**decoration**. Same bar as the course's "green cells prove nothing": a rendered chart proves nothing.

If that sentence feels true in your own words, continue. If not, re-read cell 4 (the formal version).
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of what makes a chart "matter". Not mine - yours.
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
# Act 2 — Mechanics: derive the numbers by hand, then draw all five charts

## The rule for this whole act

A bar is only honest if you can say where its height came from. So for every chart we **derive the
numbers by hand from the call objects first** — a success proxy, a failure tally, a cost proxy, a
turn count — and only THEN draw the bar. A chart drawn from numbers you did not derive is a chart
you cannot narrate, which is exactly the thing this book is against.
'''))
C.append(md('''
## First we need an honest success proxy (the pool has no "outcome" column)

Look back at the raw pool: each call has `language`, `turns`, `stress_profile` — but **no
success/outcome field**. Real call pools rarely hand you one. So before any "success-by-language"
chart can exist, we must DERIVE success from fields we *do* have. Two honest, greppable signals:

- **timing failures** — barge-ins and laggy gaps, computed by `pipeline/signals.py` (book 04's FTO
  core). A call with timing failures had a rough floor.
- **enough back-and-forth** — a call with very few user turns never really completed a task.

We will call a call **completed** when it has *no* timing failures and *enough* user turns. This is
a proxy, stated out loud — not a ground-truth label. (Book 24's real labels are better; this is the
deterministic floor you can compute with zero annotation.)
'''))
C.append(code('''
# Bring in the real timing core — the SAME analyze() pipeline/signals.py runs on every call.
# We reuse it (not a re-implementation) so our "timing failures" are the project's real numbers.
import sys
sys.path.insert(0, str(root / "pipeline"))   # let python import signals.py from the repo's pipeline/
import yaml                                   # rubric thresholds live in rubric.yaml, never hardcoded here
from signals import analyze                   # analyze(turns, rubric) -> dict incl. a "failures" list

rubric = yaml.safe_load((root / "rubric.yaml").read_text())   # one source of truth for thresholds
# Smoke-check on the hero call so you SEE the function works before we trust it across the pool.
hero = next(c for c in calls if c["call_id"] == "hero_001")
print("hero timing failures:", len(analyze(hero["turns"], rubric)["failures"]))
'''))
C.append(md('''
## PREDICT
We are about to count, for EACH call: how many timing failures it has, and how many **user** turns
it has. The hero call (`hero_001`, Tenglish) has 12 turns total. Predict: more or fewer user turns
than 6? And do you expect it to have zero timing failures, or at least one? Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - PREDICT two things about hero_001 before we compute the per-call table.
my_hero_user_turns = None    # <- a whole number: how many of hero's 12 turns are spoken by the USER
my_hero_has_failures = None  # <- True or False: does hero have at least one timing failure?

if my_hero_user_turns is None or my_hero_has_failures is None:
    print("fill in BOTH predictions above, then re-run this cell.")
else:
    print("locked - hero user turns:", my_hero_user_turns, "| has failures:", my_hero_has_failures)
'''))
C.append(code('''
# Derive the two raw signals per call, by hand, printed so nothing hides. No chart yet - numbers first.
rows = []   # one dict per call: the minimum facts every chart in this book will read
for c in calls:
    n_user_turns = sum(1 for t in c["turns"] if t["speaker"] == "user")   # user turns = real participation
    n_fail = len(analyze(c["turns"], rubric)["failures"])                 # timing failures from the real core
    rows.append({"call_id": c["call_id"], "language": c["language"],
                 "turns": len(c["turns"]), "user_turns": n_user_turns, "timing_failures": n_fail})
for r in rows:
    print(f"{r['call_id']:<14} {r['language']:<6} turns={r['turns']:>2} user={r['user_turns']:>2} fails={r['timing_failures']:>2}")
'''))
C.append(code('''
# Confront your hero prediction against the row we just built (the metal-detector reading).
hero_row = next(r for r in rows if r["call_id"] == "hero_001")
if my_hero_user_turns is not None:
    print("user turns: you said", my_hero_user_turns, "| actual", hero_row["user_turns"],
          "-", "match" if my_hero_user_turns == hero_row["user_turns"] else "differed")
    actual_has = hero_row["timing_failures"] > 0
    print("has failures: you said", my_hero_has_failures, "| actual", actual_has,
          "-", "match" if my_hero_has_failures == actual_has else "differed")
'''))
C.append(md('''
## Manual-before-function: decide "completed" for ONE call by hand

Before a helper, score one call the slow, visible way. The rule: **completed = no timing failures
AND at least 4 user turns** (fewer than four user turns means the caller barely engaged — no task
got done). We pick `swz_MUL0271` because its row showed zero timing failures; let us see if it clears
the turn bar too.
'''))
C.append(code('''
# Score ONE call by hand, every condition printed - this is the idea before any wrapper hides it.
one = next(r for r in rows if r["call_id"] == "swz_MUL0271")
cond_no_timing_fail = one["timing_failures"] == 0    # a clean floor: nobody barged in, nothing lagged
cond_enough_turns   = one["user_turns"] >= 4         # the caller actually participated in a task
completed_by_hand = cond_no_timing_fail and cond_enough_turns   # BOTH must hold to count as completed
print(one["call_id"], "| no_timing_fail:", cond_no_timing_fail, "| enough_turns:", cond_enough_turns)
print("completed?", completed_by_hand)
'''))
C.append(md('''
## Only now the function (it does exactly what you just did by hand)

The wrapper encodes the same two conditions, named once so every chart measures completion the
SAME way (the rule cannot drift between charts). Thresholds live as named constants, not magic
numbers buried in a comparison.
'''))
C.append(code('''
# MIN_USER_TURNS is named once so the "enough participation" bar is visible and editable in one place;
# a bare 4 sprinkled through later cells would be an assumption nobody could find or change safely.
MIN_USER_TURNS = 4

def completed(row):
    # completed proxy = clean floor (no timing failures) AND real participation (enough user turns).
    # Returning a plain bool keeps every downstream count a simple sum of True/False.
    return row["timing_failures"] == 0 and row["user_turns"] >= MIN_USER_TURNS

# Attach the derived label to each row so charts read one field instead of re-deriving the rule.
for r in rows:
    r["completed"] = completed(r)
n_done = sum(1 for r in rows if r["completed"])
print("completed calls:", n_done, "of", len(rows))
'''))
C.append(md('''
## CHART 1 of 5 — success-by-language. PREDICT first.

This is the headline chart of any multilingual eval. We group calls by language and plot the
**completion rate** (completed ÷ total) per language. Our pool is mostly English (`en`) with one
Tenglish call (`te-en`, the hero).

PREDICT: the English bar and the Tenglish bar — which is taller, and roughly how do they compare?
(The hero call had timing failures, remember.) Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - PREDICT the two completion rates BEFORE the group-by runs.
my_en_rate = None      # <- a number 0..1: completion rate for English (en) calls
my_teen_rate = None    # <- a number 0..1: completion rate for Tenglish (te-en) calls

if my_en_rate is None or my_teen_rate is None:
    print("fill in BOTH rates above, then re-run this cell.")
else:
    print("locked - en:", my_en_rate, "| te-en:", my_teen_rate)
'''))
C.append(code('''
# Group-by-language BY HAND with a dict of lists, so you see the grouping before any chart.
# (collections.defaultdict avoids the "is this key here yet?" dance; the idea is plain bucketing.)
from collections import defaultdict
by_lang = defaultdict(list)
for r in rows:
    by_lang[r["language"]].append(r)   # bucket each call under its language string

# Completion rate per language = completed in the bucket / size of the bucket. Printed before plotting.
lang_rate = {}
for lang in sorted(by_lang):                       # sorted => stable bar order run-to-run
    bucket = by_lang[lang]
    rate = sum(1 for r in bucket if r["completed"]) / len(bucket)
    lang_rate[lang] = rate
    print(f"{lang:<6} completed {sum(1 for r in bucket if r['completed'])}/{len(bucket)}  rate={rate:.2f}")
'''))
C.append(md('''
## Read CHART 1 with the 4-question ritual (do this BEFORE the bar renders)

1. **What is x?** — the language code (`en`, `te-en`): the category.
2. **What is y?** — completion rate, 0 to 1 (a fraction of calls that completed).
3. **What is one mark?** — one bar = all calls in that language, summarized to a single rate.
4. **What claim does it license?** — "English completes at rate `R_en`; Tenglish at `R_teen`" — a
   per-language outcome. What it does **NOT** license: any claim about *why* (the bar does not say
   barge-in vs latency), and — critically — Tenglish here is **one call**, so the bar is a sample of
   one. We will return to that fragility in Act 3; for now, narrate the bar honestly.
'''))
C.append(code('''
# CHART 1: success-by-language. y starts at 0 so bar HEIGHTS are honestly comparable (P03's rule:
# a non-zero baseline exaggerates differences). Axes are labeled because unlabeled axes lie by omission.
import matplotlib.pyplot as plt
langs = sorted(lang_rate)                       # x labels, stable order
rates = [lang_rate[l] for l in langs]           # bar heights = completion rate per language

fig, ax = plt.subplots(figsize=(5, 3))
ax.bar(langs, rates)                            # one bar per language; height = completion rate
ax.set_ylim(0, 1)                               # rates are fractions; full 0..1 keeps heights honest
ax.set_xlabel("language")                       # x = the category
ax.set_ylabel("completion rate (0-1)")          # y = the measure
ax.set_title("CHART 1 - success by language (real pool)")
plt.show()   # swallowed in headless runs; in your editor the chart appears here
'''))
C.append(code('''
# Confront your CHART 1 prediction. The point is the GAP between the bars, so we print both verdicts.
if my_en_rate is not None:
    print("en:    you said", my_en_rate, "| actual", round(lang_rate.get("en", 0), 2))
    print("te-en: you said", my_teen_rate, "| actual", round(lang_rate.get("te-en", 0), 2))
    print("the chart's CLAIM in one sentence: English completes far more often than Tenglish in this pool.")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, out loud, from what you just **saw** (not from memory): what is the single claim
CHART 1 licenses, and what is one claim a viewer might wrongly read into it that the chart never made?
'''))
C.append(md('''
## CHART 2 of 5 — failure distribution. PREDICT first.

When the agent breaks, *how* does it break? Each timing failure from `pipeline/signals.py` carries a
**dimension** — `barge_in` (the agent or user interrupted) or `latency_gap` (a laggy response). We
tally failures across the whole pool by dimension and plot the counts. This is the "what kind of
broken" chart.

PREDICT: across all 11 calls, do you expect MORE barge-in failures or MORE latency-gap failures?
Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - PREDICT which failure kind dominates the pool, before the tally runs.
my_dominant_failure = None    # <- type "barge_in" or "latency_gap"

if my_dominant_failure is None:
    print('fill in my_dominant_failure above ("barge_in" or "latency_gap"), then re-run.')
else:
    print("locked - you predict the dominant failure is:", my_dominant_failure)
'''))
C.append(code('''
# Tally failures across the WHOLE pool by their dimension. Counter is exactly "group a category and
# count it"; each failure dict from analyze() already carries its dimension, so we just read that field.
from collections import Counter
fail_counts = Counter()
for c in calls:
    for f in analyze(c["turns"], rubric)["failures"]:
        fail_counts[f["dimension"]] += 1     # one increment per failure event, keyed by its kind
for dim in sorted(fail_counts):              # sorted => stable order
    print(f"{dim:<14} {fail_counts[dim]}")
print("total failure events:", sum(fail_counts.values()))
'''))
C.append(md('''
## Read CHART 2 with the 4-question ritual (BEFORE it renders)

1. **What is x?** — the failure dimension (`barge_in`, `latency_gap`): the kind of break.
2. **What is y?** — count of failure *events* across the whole pool (not calls — events).
3. **What is one mark?** — one bar = how many times that kind of failure happened, pool-wide.
4. **What claim does it license?** — "when this agent fails on timing, it fails *this way* most
   often." What it does **NOT** license: a rate (this is raw counts, not per-call), and nothing about
   *which* calls or languages — a long English call can dominate the tally just by being long.
'''))
C.append(code('''
# CHART 2: failure distribution. Horizontal bars (barh) read nicely when labels are words, not numbers.
dims = sorted(fail_counts)                   # categories on the y-axis
counts = [fail_counts[d] for d in dims]      # bar lengths = event counts

fig, ax = plt.subplots(figsize=(5, 2.6))
ax.barh(dims, counts)                        # one bar per failure kind; length = how many events
ax.set_xlabel("failure events (count, pool-wide)")   # x is a count here
ax.set_ylabel("failure dimension")                   # y is the category (the kind of break)
ax.set_title("CHART 2 - failure distribution")
plt.show()
'''))
C.append(code('''
# Confront your CHART 2 prediction against the tally.
if my_dominant_failure is not None:
    actual_dom = max(fail_counts, key=fail_counts.get)   # the dimension with the most events
    print("you predicted:", my_dominant_failure, "| actual dominant:", actual_dom,
          "-", "match" if my_dominant_failure == actual_dom else "differed")
'''))
C.append(md('''
## CHART 3 of 5 — cost-per-successful-call. PREDICT first.

A buyer does not ask "what does a call cost"; they ask **"what does a call that WORKED cost me?"**
(book 08's idea: cost is dollars per *good* outcome). The pool has no dollar column either, so we
derive a **cost proxy**: each turn costs some tokens, tokens cost dollars, and we divide the pool's
total cost by the number of **completed** calls — not by all calls.

Why divide by completed and not by all? Because money spent on a call that failed bought you
nothing; spreading the bill only over the wins is the honest unit cost. PREDICT: will dividing by
completed make the per-good-call cost HIGHER or LOWER than dividing by all calls? Commit next.
'''))
C.append(code('''
# YOUR TURN - PREDICT the direction before the cost math runs.
my_cost_direction = None    # <- type "higher" or "lower": cost-per-completed vs cost-per-all-calls

if my_cost_direction is None:
    print('fill in my_cost_direction above ("higher" or "lower"), then re-run.')
else:
    print("locked - dividing by completed makes per-good-call cost:", my_cost_direction)
'''))
C.append(code('''
# Cost proxy, derived in tiny visible steps - no black-box pricing. Constants named so the
# assumptions (how many tokens a turn costs, the price of a token) are pointable and editable.
TOKENS_PER_TURN = 80              # rough: one spoken turn ~ this many model tokens (a stated assumption)
USD_PER_1K_TOKENS = 0.002        # rough model price; the absolute value is illustrative, the SHAPE is the point

total_turns = sum(r["turns"] for r in rows)                  # every turn in the pool costs tokens
total_tokens = total_turns * TOKENS_PER_TURN                 # turns -> tokens
total_cost = total_tokens / 1000 * USD_PER_1K_TOKENS         # tokens -> dollars
print("pool: total turns", total_turns, "| total tokens", total_tokens, "| total cost $", round(total_cost, 4))
'''))
C.append(code('''
# The two unit costs, side by side - this contrast IS chart 3. We divide the SAME total cost two ways.
n_completed = sum(1 for r in rows if r["completed"])
cost_per_all = total_cost / len(rows)              # naive: spread the bill over every call
cost_per_good = total_cost / n_completed           # honest: spread the bill over only the WINS
print("cost per call (all):       $", round(cost_per_all, 4))
print("cost per COMPLETED call:   $", round(cost_per_good, 4), f"  (over {n_completed} wins)")
'''))
C.append(md('''
## Read CHART 3 with the 4-question ritual (BEFORE it renders)

1. **What is x?** — two costing methods: "per call (all)" vs "per completed call".
2. **What is y?** — dollars per call (a cost proxy, stated assumptions).
3. **What is one mark?** — one bar = the pool's total cost divided one of the two ways.
4. **What claim does it license?** — "a *successful* outcome costs more than a naive per-call number
   suggests, because failures still cost money." What it does **NOT** license: a real invoice (these
   are illustrative token prices), and nothing about *which* calls were expensive.
'''))
C.append(code('''
# CHART 3: cost-per-successful-call vs naive per-call. Two bars, y in dollars, baseline at 0.
methods = ["per call (all)", "per completed"]    # x: the two costing methods
costs = [cost_per_all, cost_per_good]            # bar heights = dollars per call, each method

fig, ax = plt.subplots(figsize=(5, 3))
ax.bar(methods, costs)                           # one bar per method; height = $/call
ax.set_ylim(0, max(costs) * 1.3)                 # headroom above the taller bar; baseline stays at 0
ax.set_ylabel("cost per call ($, proxy)")        # y = dollars (a proxy)
ax.set_title("CHART 3 - cost per successful call")
plt.show()
'''))
C.append(code('''
# Confront your CHART 3 prediction: dividing by the smaller "completed" count makes the bar taller.
if my_cost_direction is not None:
    actual_dir = "higher" if cost_per_good > cost_per_all else "lower"
    print("you said", my_cost_direction, "| actual", actual_dir,
          "-", "match" if my_cost_direction == actual_dir else "differed")
    print("claim: a call that WORKED costs more than the naive per-call average, because failures still bill.")
'''))
C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. CHART 1 and CHART 3 both summarize the whole pool. What claim does each license, in one sentence?
2. CHART 3 divides total cost by *completed* calls, not all calls. Whose vote does that give to a
   call that failed — and why is that the honest unit for a buyer?
'''))
C.append(md('''
## CHART 4 of 5 — turns-by-language. PREDICT first.

Conversation **length** is a cost-and-friction signal: more turns means more tokens, more latency
exposure, more chances to break. We plot the **average turn count per language**. This is close
cousin to CHART 1 but measures *effort*, not *outcome*.

PREDICT: does the Tenglish call have MORE or FEWER turns than the average English call? (Recall the
hero call is 12 turns; the English calls ran from 26 up to 46.) Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - PREDICT before the per-language average runs.
my_teen_turns_vs_en = None    # <- type "more" or "fewer": Tenglish turns vs average English turns

if my_teen_turns_vs_en is None:
    print('fill in my_teen_turns_vs_en above ("more" or "fewer"), then re-run.')
else:
    print("locked - Tenglish has", my_teen_turns_vs_en, "turns than average English")
'''))
C.append(code('''
# Average turns per language, reusing the by_lang buckets we already built (one grouping, many charts).
# Average = sum of turns in the bucket / bucket size; printed before plotting so the bar is no mystery.
lang_avg_turns = {}
for lang in sorted(by_lang):
    bucket = by_lang[lang]
    avg = sum(r["turns"] for r in bucket) / len(bucket)
    lang_avg_turns[lang] = avg
    print(f"{lang:<6} avg turns = {avg:.1f}  (n={len(bucket)})")
'''))
C.append(md('''
## Read CHART 4 with the 4-question ritual (BEFORE it renders)

1. **What is x?** — language code (`en`, `te-en`).
2. **What is y?** — average number of turns per call in that language.
3. **What is one mark?** — one bar = the mean turn count over that language's calls.
4. **What claim does it license?** — "calls in language L run about N turns long on average." What it
   does **NOT** license: anything about cost in dollars (turns ≠ dollars without a price), and — the
   trap waiting in Act 3 — with `te-en` being a single call, its "average" is just that one call's
   length. A mean over n=1 is the riskiest bar on this page.
'''))
C.append(code('''
# CHART 4: turns-by-language. Bars, y = average turns, baseline 0 so the comparison is honest.
langs4 = sorted(lang_avg_turns)
avgs = [lang_avg_turns[l] for l in langs4]   # bar heights = average turns per language

fig, ax = plt.subplots(figsize=(5, 3))
ax.bar(langs4, avgs)                         # one bar per language; height = mean turn count
ax.set_ylim(0, max(avgs) * 1.2)              # headroom; baseline at 0 keeps heights comparable
ax.set_xlabel("language")
ax.set_ylabel("average turns per call")
ax.set_title("CHART 4 - turns by language")
plt.show()
'''))
C.append(code('''
# Confront your CHART 4 prediction.
if my_teen_turns_vs_en is not None:
    en_avg = lang_avg_turns.get("en", 0)
    teen_avg = lang_avg_turns.get("te-en", 0)
    actual = "more" if teen_avg > en_avg else "fewer"
    print(f"te-en avg {teen_avg:.1f} vs en avg {en_avg:.1f} -> Tenglish has {actual} turns")
    print("you said", my_teen_turns_vs_en, "-", "match" if my_teen_turns_vs_en == actual else "differed")
'''))
C.append(md('''
## CHART 5 of 5 — voice-fail vs completion. PREDICT first.

The previous four charts each show ONE measure. This one shows a **relationship**: does the timing
failure signal actually track the bad outcomes? We plot one **dot per call**: x = its timing-failure
count, y = whether it completed (1) or not (0). If the proxy is any good, the completed dots (y=1)
should cluster at low failure counts, and the not-completed dots (y=0) should stretch to the right.

PREDICT: will the y=1 (completed) dots sit mostly at the LEFT (few failures) or be scattered
everywhere? Commit in the next cell.
'''))
C.append(code('''
# YOUR TURN - PREDICT the shape of the scatter before it renders.
my_completed_dots_position = None    # <- type "left" (low-failure) or "scattered"

if my_completed_dots_position is None:
    print('fill in my_completed_dots_position above ("left" or "scattered"), then re-run.')
else:
    print("locked - completed dots will sit:", my_completed_dots_position)
'''))
C.append(code('''
# Build the (x, y) pairs by hand: x = timing failures, y = 1 if completed else 0. Printed first.
xs = [r["timing_failures"] for r in rows]               # x-axis value per call: its failure count
ys = [1 if r["completed"] else 0 for r in rows]         # y-axis value per call: completed yes/no as 1/0
for r in rows:
    print(f"{r['call_id']:<14} fails={r['timing_failures']:>2}  completed={int(r['completed'])}")
'''))
C.append(md('''
## Read CHART 5 with the 4-question ritual (BEFORE it renders)

1. **What is x?** — a call's timing-failure count (a number, not a category).
2. **What is y?** — completed (1) or not (0): a binary outcome.
3. **What is one mark?** — one **dot = one call** (this is the only per-call chart of the five).
4. **What claim does it license?** — "calls with zero timing failures tend to complete; calls with
   many do not" — i.e. the proxy and the outcome *agree*. What it does **NOT** license: causation
   (failures might be a symptom, not the cause), and a clean line (with 11 dots it is a hint, not a law).
'''))
C.append(code('''
# CHART 5: voice-fail vs completion, a scatter (one dot per call). We jitter nothing and label both
# axes; the y-axis ticks are forced to 0 and 1 because y is a yes/no, not a continuous scale.
fig, ax = plt.subplots(figsize=(5, 3))
ax.scatter(xs, ys)                                  # one dot per call: (timing failures, completed?)
ax.set_yticks([0, 1]); ax.set_yticklabels(["not completed", "completed"])  # name the rows or it lies
ax.set_xlabel("timing failures (count) for the call")   # x = how rough the floor was
ax.set_title("CHART 5 - voice-fail vs completion (one dot = one call)")
plt.show()
'''))
C.append(code('''
# Confront your CHART 5 prediction: where did the completed (y=1) dots land on the x-axis?
if my_completed_dots_position is not None:
    completed_fail_counts = [r["timing_failures"] for r in rows if r["completed"]]
    # if every completed call has 0 failures, the dots are hard LEFT - the proxy and outcome agree
    all_left = completed_fail_counts and max(completed_fail_counts) == 0
    actual = "left" if all_left else "scattered"
    print("completed calls' failure counts:", completed_fail_counts)
    print("you said", my_completed_dots_position, "| actual", actual,
          "-", "match" if my_completed_dots_position == actual else "differed")
'''))
C.append(md('''
## CHECKPOINT 3 (out loud)
You have now built all five charts. Four of them (1-4) summarize the pool into **bars**; one (5)
keeps **one dot per call**. In one sentence each: why does CHART 5 *have* to keep calls separate to
make its point, while CHART 1 *has* to blend them to make its point?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: a chart is something you draw at the end. After Act 2 you should own the workflow: **derive
the numbers by hand from the call objects first** (success proxy, failure tally, cost proxy, turn
count), THEN draw, THEN **read the bar aloud with the 4-question ritual** — including the claim it
does NOT license. Five charts, five claims, every height traceable to a field you can point at.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (derive-then-draw / the 4-question ritual / the five charts - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the charts, and the trap at the heart of the book

## Break-it philosophy

A chart you cannot narrate is decoration — but a chart you narrate *wrongly* is worse: it is a
confident lie. So we now damage these charts on purpose and watch them keep rendering while their
claim quietly rots. Surprise here, on your terms, beats a buyer catching it on the demo stage.
'''))
C.append(md('''
## PREDICT
We change CHART 1's y-axis to start at **0.8** instead of 0 (a single line of code). The completion
rates do not change at all. Does the *chart* change — and does the *claim a viewer reads off it*
change? Commit to one: "the bars look the same" or "a small gap looks huge". Then run.
'''))
C.append(code('''
# BREAK-IT (guided) - this cell draws CHART 1 again with a LYING baseline. Nothing errors; the data
# is identical. Only set_ylim changed. Watch a modest gap balloon into a cliff - the chart's CLAIM moved
# without a single number moving. (P03's misleading-axis lesson, now on a chart you built.)
fig, ax = plt.subplots(figsize=(5, 3))
ax.bar(langs, rates)                  # SAME data as CHART 1 - the heights are unchanged
ax.set_ylim(0.8, 1.0)                 # <- the damage: baseline at 0.8 amputates the bottom of every bar
ax.set_xlabel("language")
ax.set_ylabel("completion rate (0-1)")
ax.set_title("CHART 1 with a LYING baseline (ylim starts at 0.8)")
plt.show()
print("same rates as CHART 1:", {l: round(r, 2) for l, r in lang_rate.items()})
print("the bars now imply a far bigger gap than the numbers support - the chart lies, the data did not.")
'''))
C.append(md('''
## Reading the damage

Both CHART 1 and this version are "correct" plots of the same rates. But the second one **licenses a
different claim** — "Tenglish is *catastrophically* worse" — that the data does not support; the real
gap is whatever the honest 0-baseline showed. The chart did not error. It rendered beautifully. And it
would mislead every viewer who did not check the y-axis. **A chart that renders is not a chart that is
honest** — exactly the sibling of the course's "green cells prove nothing".
'''))
C.append(md('''
## The chart-debug ritual (three steps, in order)

When a chart looks surprising or too good:
1. **Read the axes** — what are the limits, and does the baseline start at 0?
2. **Read one mark back to the data** — pick one bar, find the exact number it should be.
3. **Count the marks** — how many calls is each bar standing on? (A bar over n=1 is a rumor.)

That is the whole ritual. The next cell runs step 3 on CHART 1, which is where its real fragility hides.
'''))
C.append(code('''
# Step 3 of the chart-debug ritual on CHART 1: how many calls is each bar actually standing on?
# A rate of 0.00 or 1.00 feels strong until you see it rests on ONE call - then it is a rumor, not a rate.
for lang in sorted(by_lang):
    n = len(by_lang[lang])
    print(f"{lang:<6} bar rests on {n} call(s)" + ("  <- a 'rate' over one call is a single anecdote" if n == 1 else ""))
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
Recite the three-step chart-debug ritual. Which step exposes the lying-baseline break, and which
step exposes the "Tenglish bar is one call" fragility — and why is a fragile bar *more* dangerous than
an ugly one?
'''))
C.append(md('''
## YOUR break now

Author your own damage to a chart you built. Pick ONE: (a) re-plot CHART 4 (turns-by-language) with a
non-zero baseline and predict how the gap distorts, OR (b) drop the single Tenglish call from the pool
and predict what happens to CHART 1's Tenglish bar. Write your prediction as a comment, then run.
'''))
C.append(code('''
# YOUR TURN - self-authored BREAK-IT on a chart you built (you choose the damage).
# my prediction: <write here exactly what will happen to the chart's CLAIM and why>

# Option (a) scaffold - a lying baseline on CHART 4 (uncomment and set the floor):
# fig, ax = plt.subplots(figsize=(5, 3))
# ax.bar(langs4, avgs)
# ax.set_ylim(?, max(avgs) * 1.2)      # <- pick a non-zero floor and predict the distortion
# ax.set_ylabel("average turns per call"); ax.set_title("CHART 4 with a chosen baseline")
# plt.show()

# Option (b) scaffold - drop te-en and recompute CHART 1's buckets (uncomment to use):
# pool_no_teen = [r for r in rows if r["language"] != "te-en"]
# remaining = sorted({r["language"] for r in pool_no_teen})
# print("languages remaining after dropping te-en:", remaining)

print("pick option (a) or (b) above, write your prediction, run, and compare to what you expected.")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this whole book is built on

**The wrong belief:** *"the chart rendered and looks professional, so it is telling the truth."*

The next cell builds a SIXTH chart — average **timing failures per language** — and it renders
cleanly, looks authoritative, and would slot right into a dashboard. It also says that **Tenglish is
the cleanest language in the pool** (fewest failures). Run it, look at the bars, and try to explain
why that headline is a lie BEFORE the reveal.
'''))
C.append(code('''
# A sixth chart that looks great and lies. Average timing failures per language - lower looks "better".
lang_avg_fails = {}
for lang in sorted(by_lang):
    bucket = by_lang[lang]
    lang_avg_fails[lang] = sum(r["timing_failures"] for r in bucket) / len(bucket)

fig, ax = plt.subplots(figsize=(5, 3))
ax.bar(sorted(lang_avg_fails), [lang_avg_fails[l] for l in sorted(lang_avg_fails)])  # height = avg failures
ax.set_ylim(0, max(lang_avg_fails.values()) * 1.2)
ax.set_xlabel("language"); ax.set_ylabel("avg timing failures per call")
ax.set_title("avg failures by language - Tenglish looks CLEANEST")
plt.show()
for lang in sorted(lang_avg_fails):
    print(f"{lang:<6} avg failures = {lang_avg_fails[lang]:.1f}  (n={len(by_lang[lang])})")
'''))
C.append(md('''
## The reveal

Tenglish shows the **lowest** average failures — but that average is over **one call** (the hero),
and the English average is dragged up by a few very long calls (`swz_MUL0056` alone has 34 turns and
many laggy gaps). The bar is real arithmetic. It is the **wrong** arithmetic for the headline "Tenglish
is cleanest", because (1) it is a mean over n=1, and (2) raw failure counts scale with call **length**,
not call **quality** — a longer call has more turn-pairs and thus more chances to register a failure.

This is the soul of the book, and the sibling of P00's average-of-averages and book 09's blended
success rate: **a chart can render cleanly and still license a false claim.** The defense is never
"does it render" — it is the 4-question ritual plus the chart-debug ritual: read the axes, read one
mark back to the data, and *count the marks*. A chart you cannot narrate is decoration; a chart you
narrate without counting its marks is a confident lie.
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why is "Tenglish is cleanest" a lie even though the bar is real?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above, then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: a chart that renders is a chart that informs. After Act 3: a chart can render cleanly and lie
two ways — a **non-zero baseline** inflates a gap, and a **mean over too few marks** (n=1!) launders an
anecdote into a "rate". The chart-debug ritual is three boring reads: check the axes, read one mark back
to the data, count the marks. "It rendered" earns exactly nothing — same bar as "it ran".
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the trap / lying baseline / count-the-marks - your pick)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where these five charts live, and the bar you must clear

## Where this lives in the real VoiceForge pipeline

These five are not a teaching toy — they are the **scorecard's demo charts**, and every number under
them is computed by code you have already touched:

- **success-by-language** and **turns-by-language** group the real pool the same way `pipeline/`
  crosscut reporting does, by reading `language` and `turns` straight off each `data/normalized/*.json`.
- **failure distribution** and **voice-fail vs completion** read the `failures` list from
  `pipeline/signals.py` (`analyze()`), the exact deterministic FTO core from book 04 — thresholds from
  `rubric.yaml`, never hardcoded.
- **cost-per-successful-call** is book 08's idea: divide spend by *good* outcomes, not all calls.

Book 26 arranges these five tiles into one dashboard. The narration you practiced here IS the dashboard's
caption track — without it, the dashboard is five decorations in a grid.
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
1. Recite the four chart-reading questions (x? y? one mark? what claim is licensed?).
2. For the success-by-language bar, what is the ONE claim it licenses — and the one it does NOT
   (think about why the Tenglish bar is a sample of one)?
3. Which of the five charts is the cost-per-successful-call chart, and why does dividing by the
   number of *successful* calls (not all calls) make a failure show up as money?
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

Of the five charts, which **one** do you think is the most likely to be *misread* by a buyer on a
stage — and what is the single sentence you would say out loud to stop the misreading before it starts?
There is no grading; this is the narration muscle the whole book trained.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for book 26 (the dashboard) to use.
my_course_prediction = ""   # which chart is most misread + the one sentence you would say to prevent it

if len(my_course_prediction.strip()) < 20:
    print("write your prediction above (which chart + your guarding sentence), then re-run.")
else:
    print("PREDICTION STORED:", my_course_prediction)
'''))
C.append(md('''
## Where this method itself fails (honesty applies to charts too)

- **Decoration drift** — adding a chart because the slide "looked empty", with no claim attached.
  Countermeasure: every chart ships with its one-sentence narration or it does not ship.
- **Baseline laundering** — a non-zero y-axis that turns a small gap into a cliff. Countermeasure:
  bars start at 0 unless you can defend otherwise out loud.
- **Mean-over-nothing** — a "rate" or "average" computed over one or two marks. Countermeasure: the
  third chart-debug step — *count the marks* — and label small-n bars as anecdotes.
- **Counts mistaken for rates** — a tall failure bar that is just a long call. Countermeasure: say
  whether the y-axis is a count or a rate, every time.
'''))
C.append(md('''
## The concept at three levels (the same five charts, three audiences)

- **To a beginner:** "every chart should come with a sentence — if you can't say what the picture
  proves, it's just decoration."
- **To an engineer:** "five scorecard views — success-by-language, failure distribution,
  cost-per-success, turns-by-language, voice-fail vs completion — each derived from `data/normalized`
  + `pipeline/signals.py`, each read with a 4-question ritual that includes the claim it does NOT
  license; small-n bars flagged, baselines pinned at 0."
- **To a founder:** "we don't show pretty graphs; we show five claims a buyer can repeat back —
  *it works in English but not yet Tenglish, here's how it breaks, here's the cost of a good call* —
  and every claim is defensible down to the call it came from."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "Isn't 'cost per completed call' just inflating the number to look scary?"**
<details><summary>answer</summary>No - it is the only honest unit for a buyer. Money spent on a failed call bought nothing, so spreading the bill only over successes is the true cost of a good outcome. Dividing by all calls hides the cost of failure inside a cheaper-looking average.</details>

**2. "Your Tenglish bars rest on one call. Why show them at all?"**
<details><summary>answer</summary>Because the honest move is to SHOW it and SAY it: this is a sample of one, directional not conclusive. I label small-n bars as anecdotes and run the count-the-marks step. Hiding the slice would be the dishonest choice; over-claiming on it would be the other. Naming the n is how you do neither.</details>

**3. "How is this different from just making matplotlib charts?"**
<details><summary>answer</summary>The drawing is the easy 10%. The book is the other 90%: choosing the FIVE charts that answer a buyer's real questions, deriving every height from a field you can point at, and attaching a one-sentence claim (plus the claim it does NOT license) to each. A chart without that sentence is decoration, however well matplotlib drew it.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: where these five charts live in the real pipeline (`data/normalized` +
`pipeline/signals.py` + `rubric.yaml`), how each maps to a buyer's question, the three failure modes
of charts (decoration drift, baseline laundering, mean-over-nothing), the three-level explanation, and
above all what it takes to PASS this book — narrating all five charts, out loud, from memory.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. Name the five demo charts and the buyer question each answers.
2. The 4-question chart-reading ritual (and why question 4 — what it does NOT license — is the sharp one).
3. The three-step chart-debug ritual (axes · one mark back to data · count the marks).
4. The trap: a chart can render cleanly and still license a false claim — give the "Tenglish looks
   cleanest" example and why it lies.
5. The clean sentence of this book.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about what makes a chart worth showing

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"A chart you cannot narrate is decoration."**

Five charts, five claims, every height traceable to a call you can point at — and each one read
aloud, including what it does *not* say. If your sentence captures that in your own words, this book
did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "25_charts_that_matter.ipynb"   # <- this notebook's filename
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

**25 done** (pending your teach-back) → **26 · The dashboard mental model** — these exact five charts
stop being five separate plots and become one screen a buyer reads in ten seconds. Everything you
narrated here becomes the dashboard's caption track: a tile a viewer cannot read aloud is a decoration
you put in a grid.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "25_charts_that_matter.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
