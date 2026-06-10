#!/usr/bin/env python3
# Generates Part A (bedrock stats) + Part B (ML from zero): books A1-A3, B1-B4.
# Rerun any time: .venv/bin/python notebooks/build_part_AB.py
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def md(s):
    return {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n")}


def code(s):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
            "source": s.strip("\n")}


BOOT = '''
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "rubric.yaml").exists())
import sys
sys.path.insert(0, str(ROOT / "pipeline"))
import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(7)
print("ready · repo:", ROOT.name)
'''

NBS = {}

# ================================================================ A1
NBS["A1_distributions_and_tails.ipynb"] = [
    md('''
# A1 — Distributions, tails, and why means lie

**From:** "what is a histogram"  **To:** reading real latency data and explaining why dashboards report p90.

A **distribution** is nothing scary: it is *all the values something takes, and how often it takes them*. Roll a die 1000 times — the list of outcomes is a distribution. Measure 1000 response delays — also a distribution. Statistics is mostly the art of describing these piles of numbers honestly.

Two words used constantly:
- **sample** — the values you actually collected (your 1000 rolls).
- **population** — the (usually unreachable) full truth the sample stands in for (every roll this die could ever make).

Remember the loop: **predict out loud → run → say what you see.**
'''),
    code(BOOT + '''
rolls = rng.integers(1, 7, size=1000)
values, counts = np.unique(rolls, return_counts=True)
for v, c in zip(values, counts):
    print(f"face {v}: {c} times")
'''),
    md('''
**PREDICT first:** should those counts be exactly equal? (They were not.) Each face has probability 1/6 ≈ 167 of 1000 — but randomness wobbles around that. The wobble is *sampling noise*, and it never fully goes away; it only shrinks as the sample grows. Hold that thought for book A2.

## Your first plot, and how to read any plot
The tool below is a **histogram**: it chops the number line into buckets (bins) and draws one bar per bucket; bar height = how many values landed in it. In matplotlib:
- `fig, ax = plt.subplots()` makes a canvas (`fig`) holding one drawing area (`ax`)
- `ax.hist(data, bins=...)` draws the histogram
- always label: `ax.set_xlabel(...)` (what the values are), `ax.set_ylabel(...)` (the count), `ax.set_title(...)`

A plot you cannot read aloud — "x is …, y is …, each bar means …" — is a plot you do not understand yet.

**PREDICT:** the histogram of single rolls is flat-ish. What shape is the histogram of the SUM of two dice? (Think: how many ways to make 2 vs 7.)
'''),
    code('''
two_dice = rng.integers(1, 7, 1000) + rng.integers(1, 7, 1000)
fig, axes = plt.subplots(1, 2, figsize=(10, 3))
axes[0].hist(rolls, bins=np.arange(0.5, 7.5), edgecolor="white")
axes[0].set_xlabel("die face"); axes[0].set_ylabel("count"); axes[0].set_title("one die: flat (uniform)")
axes[1].hist(two_dice, bins=np.arange(1.5, 13.5), edgecolor="white")
axes[1].set_xlabel("sum of two dice"); axes[1].set_ylabel("count"); axes[1].set_title("two dice: a peak at 7")
plt.tight_layout(); plt.show()
'''),
    md('''
Say what you see: one die is flat; the sum has a peak (7 has six ways to happen, 2 has one). Shapes carry meaning — and the next distinction is the one this whole book exists for.

## Symmetric vs skewed, and the three "centers"
- **mean** — the balance point: add everything, divide by n.
- **median** — line everyone up, take the middle person.
- **mode** — the most common value.

On a **symmetric** pile they coincide. On a **skewed** pile — one with a long tail of rare huge values — the mean gets dragged toward the tail while the median stays with the crowd. Latency data is almost always right-skewed: most responses are quick, a few are terrible.

**PREDICT:** in the skewed plot below, which line sits further right — mean or median?
'''),
    code('''
symmetric = rng.normal(500, 80, 5000)
skewed = rng.lognormal(mean=6.0, sigma=0.6, size=5000)
fig, axes = plt.subplots(1, 2, figsize=(11, 3))
for ax, data, name in [(axes[0], symmetric, "symmetric"), (axes[1], skewed, "right-skewed (long tail)")]:
    ax.hist(data, bins=50)
    ax.axvline(data.mean(), color="tab:red", lw=2, label=f"mean {data.mean():.0f}")
    ax.axvline(np.median(data), color="tab:green", lw=2, label=f"median {np.median(data):.0f}")
    ax.set_title(name); ax.set_xlabel("value"); ax.set_ylabel("count"); ax.legend()
plt.tight_layout(); plt.show()
'''),
    md('''
The mean chased the tail; the median did not. Whenever someone quotes you a *mean* for skewed data (latency, income, file sizes), they are — knowingly or not — letting the tail speak for the crowd.

## Percentiles: naming positions in the pile
Sort all values. The **p-th percentile** is the value below which p% of the data sits. p50 *is* the median. **p90** answers: "how bad is the experience for the unluckiest 10%?" Production systems live and die by p90/p99 because users do not experience averages — each user experiences one draw, and the angry ones come from the tail.

Now real data: every user→agent response gap across our 11 normalized calls (the caller finishes, how long until the agent speaks — in milliseconds, from the conversation logs you helped produce).

**PREDICT:** will the mean sit above or below the median here? Where will p90 land relative to both?
'''),
    code('''
import json
from signals import turn_metrics
gaps = []
for p in sorted((ROOT / "data" / "normalized").glob("*.json")):
    call = json.loads(p.read_text())
    for e in turn_metrics(call["turns"]):
        if e["prev_spk"] == "user" and e["next_spk"] == "agent" and e["fto_ms"] >= 0:
            gaps.append(e["gap_ms"])
gaps = np.array(gaps)
mean, med, p90 = gaps.mean(), np.median(gaps), np.percentile(gaps, 90)
print(f"n={len(gaps)} response gaps · mean={mean:.0f}ms · median={med:.0f}ms · p90={p90:.0f}ms")
fig, ax = plt.subplots(figsize=(9, 3))
ax.hist(gaps, bins=40)
for v, lbl, c in [(mean, "mean", "tab:red"), (med, "median", "tab:green"), (p90, "p90", "tab:purple")]:
    ax.axvline(v, color=c, lw=2, label=f"{lbl} {v:.0f}ms")
ax.set_xlabel("user->agent gap (ms)"); ax.set_ylabel("count")
ax.set_title("real response gaps, 11 calls"); ax.legend(); plt.show()
'''),
    md('''
Read it aloud: where is the bulk? where is the tail? which single number would you tell a founder describes "typical" — and what does p90 say that the mean hides? (Our rubric calls a gap laggy above 800ms — find that point on the x-axis and estimate how much of the pile sits beyond it.)

## Exercise — p90 with your bare hands
No `np.percentile`. Sort, find the index, look it up. Then check yourself.
'''),
    code('''
sorted_gaps = np.sort(gaps)
idx = int(np.ceil(0.9 * len(sorted_gaps))) - 1     # the value with 90% of the pile at or below it
by_hand = sorted_gaps[idx]
print(f"by hand: {by_hand}ms · numpy: {np.percentile(gaps, 90):.0f}ms")
print("(small differences are fine - there are several interpolation conventions; the IDEA is identical)")
'''),
    md('''
## Self-check (out loud, then expand)
1. Define distribution, sample, population in one sentence each.
2. Why does the mean exceed the median on right-skewed data?
3. What question does p90 answer that the mean cannot?
4. Our pool's median gap was healthy but p90 was far beyond 800ms. Describe the user experience in plain words.
5. **Gotcha:** a release improves mean latency 20% but p90 doubles. What probably happened, and who noticed?

<details><summary>Answers</summary>

1. Distribution: the values something takes and how often. Sample: the values you collected. Population: the full truth the sample approximates.
2. The long tail of rare large values drags the sum (hence the mean); the middle-ranked value barely moves.
3. "How bad is it for the worst 10% of experiences?" — the tail's size and location.
4. Most replies feel fine; roughly one in ten exchanges has the caller hanging in silence past the point where it feels broken. Callers remember those.
5. Typical requests got faster, but some path (cache miss, retry, lock) got much slower; the unlucky minority noticed — loudly. Means hide tail regressions; that is why we report median + p90.
</details>
'''),
]

# ================================================================ A2
NBS["A2_uncertainty_from_scratch.ipynb"] = [
    md('''
# A2 — Uncertainty from scratch

**From:** "I computed a number on 15 data points"  **To:** putting honest error bars on any statistic with the bootstrap, and knowing exactly what a confidence interval does (and does not) claim.

Yesterday's pipeline measured call `swz_MUL0056`: median response gap **1,720ms** — computed from just **15** handoffs. Is 1,720 the truth about this agent, or did we get a weird 15? That doubt has a science to it.

A number computed from a sample (a mean, a median, a kappa…) is an **estimate**. Different samples → different estimates. The spread of would-be estimates is **sampling error** — and we can SEE it by playing god for a moment.
'''),
    code(BOOT + '''
population = rng.lognormal(mean=6.4, sigma=0.7, size=100_000)     # pretend: ALL gaps this agent will ever produce
true_median = np.median(population)
print(f"true population median (god view): {true_median:.0f}ms")

medians_n15 = [np.median(rng.choice(population, 15)) for _ in range(2000)]
fig, ax = plt.subplots(figsize=(9, 3))
ax.hist(medians_n15, bins=50)
ax.axvline(true_median, color="tab:red", lw=2, label="true median")
ax.set_xlabel("median of a 15-gap sample"); ax.set_ylabel("count")
ax.set_title("2000 parallel universes, each measuring 15 gaps"); ax.legend(); plt.show()
print(f"estimates ranged {min(medians_n15):.0f} to {max(medians_n15):.0f}ms - same agent, different luck")
'''),
    md('''
Read it: every bar is a universe where we measured the *same* agent with a *different* 15 handoffs. Some universes concluded 1,300ms; others 2,400ms. Our 1,720 is one draw from this spread.

**PREDICT:** if each universe measured 100 gaps instead of 15, does the spread widen or shrink? By roughly what factor if we go 15 → 60 (4× the data)?
'''),
    code('''
fig, ax = plt.subplots(figsize=(9, 3))
for n, color in [(15, "tab:blue"), (60, "tab:orange"), (240, "tab:green")]:
    meds = [np.median(rng.choice(population, n)) for _ in range(2000)]
    ax.hist(meds, bins=50, alpha=0.55, color=color, label=f"n={n}  (spread sd={np.std(meds):.0f})")
ax.axvline(true_median, color="tab:red", lw=2)
ax.set_xlabel("sample median (ms)"); ax.set_ylabel("count"); ax.legend()
ax.set_title("more data -> narrower spread (roughly 1/sqrt(n))"); plt.show()
'''),
    md('''
Quadrupling the data roughly *halves* the spread — the famous **1/√n** law. This is why our calibration block insists on 40–60 labels, not 10: below that, the error bars swallow the conclusion.

## The confidence interval, stated honestly
A **95% confidence interval** is a *recipe* for turning a sample into a range, built so that **across many repeated experiments, the range traps the true value ~95% of the time.** Subtle but important: any single interval either contains the truth or it does not — the 95% describes the *recipe's* long-run hit rate, not a probability about one interval. The cleanest way to internalize that is to watch the recipe play out:
'''),
    code('''
fig, ax = plt.subplots(figsize=(9, 5))
hits = 0
for i in range(100):
    sample = rng.choice(population, 60)
    boots = [np.median(rng.choice(sample, len(sample))) for _ in range(300)]
    lo, hi = np.percentile(boots, [2.5, 97.5])
    ok = lo <= true_median <= hi
    hits += ok
    ax.plot([lo, hi], [i, i], color="tab:green" if ok else "tab:red", lw=1.5)
ax.axvline(true_median, color="black", lw=2)
ax.set_xlabel("ms"); ax.set_ylabel("experiment #")
ax.set_title(f"100 intervals from 100 samples - {hits} trapped the truth")
plt.show()
'''),
    md('''
Roughly 95 green, a handful of red — *by design*. The red ones are not mistakes; they are the honest 5%.

## But real life gives you ONE sample — enter the bootstrap
No population, no parallel universes. The bootstrap's move: **let the sample impersonate the population.** Resample your own n points *with replacement* (some points repeat, some sit out), recompute the statistic, repeat thousands of times — the spread of those recomputations approximates the sampling error. It feels like cheating; it is provably reasonable; you already saw it work in the plot above (each interval came from bootstrapping one sample).

Now do it for real — `MUL0056`'s actual 15 gaps:
'''),
    code('''
import json
from signals import turn_metrics
call = json.loads((ROOT / "data" / "normalized" / "swz_MUL0056.json").read_text())
gaps = np.array([e["gap_ms"] for e in turn_metrics(call["turns"])
                 if e["prev_spk"] == "user" and e["next_spk"] == "agent" and e["fto_ms"] >= 0])
boots = np.array([np.median(rng.choice(gaps, len(gaps))) for _ in range(4000)])
lo, hi = np.percentile(boots, [2.5, 97.5])
print(f"n={len(gaps)} · point estimate median={np.median(gaps):.0f}ms · 95% CI [{lo:.0f}, {hi:.0f}]ms")
fig, ax = plt.subplots(figsize=(9, 2.6))
ax.hist(boots, bins=40)
ax.axvline(lo, color="tab:red"); ax.axvline(hi, color="tab:red")
ax.set_xlabel("bootstrap median (ms)"); ax.set_ylabel("count")
ax.set_title("bootstrap distribution, real call, n=15"); plt.show()
'''),
    md('''
Read the width of that interval out loud. With n=15, "median 1,720ms" honestly means "somewhere in the high hundreds to mid-two-thousands" — still clearly laggy (the whole interval sits above 800ms!), but a single crisp number would have overclaimed precision. **An estimate without an interval is a vibe.**

This exact machinery returns in Block 7 / book F3: kappa gets a bootstrap CI, and the claim rules read the *interval*, not the point.

## Self-check
1. What is sampling error, in one sentence?
2. The 1/√n law: to halve your error bars, multiply data by …?
3. State precisely what "95%" in a 95% CI refers to.
4. Why does resampling *your own data* tell you anything new?
5. **Gotcha:** a colleague runs 50,000 bootstrap iterations instead of 4,000 "to get a tighter interval." What do you tell them?

<details><summary>Answers</summary>

1. The spread among estimates that different same-size samples from the same truth would produce.
2. ×4.
3. The long-run trap rate of the interval-building recipe across repeated experiments — not a probability statement about any single interval.
4. The sample's internal variability approximates the population's; resampling replays "alternative samples you could have drawn" using the best stand-in you have.
5. Iterations only smooth the *picture* of the spread; the width is driven by n (the real data). Tighter intervals are bought with more data, not more loops.
</details>
'''),
]

# ================================================================ A3
NBS["A3_two_measurers_one_truth.ipynb"] = [
    md('''
# A3 — Two measurers, one truth: agreement beyond luck

**From:** "they agree 88% of the time, nice"  **To:** deriving Cohen's kappa by hand and spotting the two classic traps (chance agreement, prevalence).

Setup, fully general: two measurers label the same items with yes/no. Two assay replicates calling binding/no-binding. Two doctors reading scans. And — where this is headed — **a human and an LLM judge labeling the same calls "task completed?"** The question is never "do they agree a lot?" but **"do they agree more than luck would produce?"**
'''),
    code(BOOT + '''
n = 50
truth = rng.integers(0, 2, n)                       # ground truth, hidden from both
human = np.where(rng.random(n) < 0.92, truth, 1 - truth)   # decent rater: 8% slips
judge = np.where(rng.random(n) < 0.85, truth, 1 - truth)   # decent judge: 15% slips
raw = (human == judge).mean()
print(f"raw agreement: {raw:.2f}  - sounds impressive, no context yet")
'''),
    md('''
## The broken judge that scores 90%
Imagine 90% of calls genuinely succeed, and a "judge" that just says **success every single time** — a constant function, measuring nothing. Watch its raw agreement:
'''),
    code('''
truth_skew = (rng.random(n) < 0.9).astype(int)
human_skew = np.where(rng.random(n) < 0.92, truth_skew, 1 - truth_skew)
lazy_judge = np.ones(n, dtype=int)
print(f"lazy judge raw agreement: {(human_skew == lazy_judge).mean():.2f}")
print("zero information, ~90% agreement. Raw agreement is broken as a metric.")
'''),
    md('''
## Fixing it: subtract the luck
If the human says yes 92% of the time and the judge says yes 100% of the time, then *even with zero communication* they both say yes about 0.92×1.00 = 92% of the time, and both say no 0.08×0.00 = 0%. So **chance alone produces p_e ≈ 0.92 agreement.** General recipe:

p_e = P(both yes by luck) + P(both no by luck) = a₁·b₁ + a₀·b₀

where a₁, b₁ are each rater's yes-rates. **Cohen's kappa** then rescales observed agreement p_o against that floor:

κ = (p_o − p_e) / (1 − p_e)

Read it as: *of the agreement headroom above pure luck, what fraction did they capture?* κ=1 perfect, κ=0 exactly luck-level, κ<0 worse than luck.
'''),
    code('''
def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return (po - pe) / (1 - pe)

print(f"honest judge:  raw {(human == judge).mean():.2f}   kappa {kappa(human, judge):.2f}")
print(f"lazy judge:    raw {(human_skew == lazy_judge).mean():.2f}   kappa {kappa(human_skew, lazy_judge):.2f}")
'''),
    md('''
The honest judge still captures over half the headroom above luck; the lazy judge collapses to **0.00** — exposed despite its higher raw score. That inversion (lower raw, higher kappa) is the entire reason kappa exists.

## The prevalence trap
Subtler: keep the *same* per-item slip rate, but make the classes imbalanced. **PREDICT:** does kappa rise, fall, or stay put as "yes" prevalence goes from 50% to 95%?
'''),
    code('''
prevs = np.linspace(0.5, 0.95, 10)
ks = []
for p in prevs:
    t = (rng.random(4000) < p).astype(int)
    h = np.where(rng.random(4000) < 0.92, t, 1 - t)
    j = np.where(rng.random(4000) < 0.85, t, 1 - t)
    ks.append(kappa(h, j))
fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(prevs, ks, marker="o")
ax.set_xlabel("prevalence of 'yes'"); ax.set_ylabel("kappa")
ax.set_title("same raters, same slip rates - kappa falls as classes imbalance"); plt.show()
'''),
    md('''
Same competence, lower kappa — because the luck floor p_e rises toward 1 when one class dominates, leaving little headroom to be better than. Two consequences for our project: (1) report prevalence alongside kappa, (2) when collecting the 40–60 labels, *stratify* so the binary dimension is not 95/5 — a balanced-ish label set makes kappa meaningful.

## Reading kappa, claiming honestly
The **Landis–Koch** convention: 0.41–0.60 moderate · **0.61–0.80 substantial** · 0.81+ almost perfect. House rule (locked in the spec): claim "substantial agreement" **only if the number AND its bootstrap CI (book A2!) sit inside 0.61–0.80.** Otherwise the phrase is "moderate, directional." The credibility move on top: show the items where the two measurers *disagreed* and discuss them — proof you studied the instrument instead of trusting it.

## Exercise — by hand, every step
Two label lists below (n=40, imbalanced on purpose). Compute p_o, the two yes-rates, p_e, and kappa with plain arithmetic — *then* check against the function.
'''),
    code('''
A = np.array([1,1,1,0,1,1,1,1,0,1,1,1,1,1,0,1,1,1,1,1,1,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,1])
B = np.array([1,1,1,1,1,1,1,1,0,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1])
po = None      # YOUR TURN: fraction of positions where A==B
pe = None      # YOUR TURN: A.mean()*B.mean() + (1-A.mean())*(1-B.mean())
k  = None      # YOUR TURN: (po-pe)/(1-pe)
if k is not None:
    print(f"yours: {k:.3f}   function: {kappa(A, B):.3f}")
else:
    print("fill the three lines, then compare:", f"function says {kappa(A, B):.3f}")
'''),
    md('''
## Self-check
1. Why is raw agreement a broken metric? (One devastating example.)
2. Derive p_e in words for two raters with yes-rates 0.9 and 0.8.
3. κ = 0.55 with CI [0.35, 0.72]: what may you claim?
4. Why will we stratify the calls Spike blind-labels?
5. **Gotcha:** your judge agrees with you at κ=0.78 — a colleague says "so it is right 78% of the time." Correct them.

<details><summary>Answers</summary>

1. A constant judge on imbalanced data scores ~prevalence agreement while measuring nothing (the lazy-judge demo).
2. Both-yes by luck 0.9×0.8=0.72, both-no 0.1×0.2=0.02 → p_e=0.74.
3. "Moderate, directional" — the interval dips well below 0.61, so "substantial" is not earned.
4. To keep the label classes balanced enough that the luck floor stays low and kappa retains headroom (and so every stress profile is represented).
5. Kappa is luck-adjusted *agreement with a human*, not accuracy against truth — and 0.78 is not a percentage of anything; it is the fraction of above-chance headroom captured.
</details>
'''),
]

# ================================================================ B1
NBS["B1_what_learning_is.ipynb"] = [
    md('''
# B1 — What "learning" is

**From:** zero  **To:** training a model with gradient descent you wrote yourself, and knowing what loss, gradient, and learning rate mean forever.

Machine learning in one honest sentence: **adjust numbers until wrongness shrinks.**
- The adjustable numbers are **parameters** (a.k.a. weights).
- The wrongness is the **loss**: one number scoring how bad current predictions are.
- **Training** is the loop that nudges parameters to reduce loss.

Everything else — neural nets, LLMs, the model you ran at Fujitsu — is this sentence with more parameters and fancier bookkeeping. We start with ONE parameter, on real data from our repo.
'''),
    code(BOOT + '''
import json
turns, dur = [], []
for p in sorted((ROOT / "data" / "normalized").glob("*.json")):
    call = json.loads(p.read_text())
    turns.append(len(call["turns"]))
    dur.append(call["turns"][-1]["end_ms"] / 1000)
x, y = np.array(turns, float), np.array(dur, float)
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.scatter(x, y)
ax.set_xlabel("turns in call"); ax.set_ylabel("duration (s)")
ax.set_title("our 11 calls - longer conversations take longer (shocking)"); plt.show()
'''),
    md('''
(How to read a **scatter plot**: each dot is one call; its x is the turn count, its y the duration. A cloud rising to the right = the two grow together.)

## A model with one knob
Propose: `duration ≈ w × turns` — one parameter `w`, "seconds per turn." For any guess of `w` we can score it: **mean squared error**, the average of (prediction − truth)². Squared because: misses in both directions count, big misses hurt disproportionately, and the math stays smooth.

**PREDICT:** plot loss against w from 0 to 12 — what shape must it be, and roughly where is its bottom (eyeball seconds-per-turn from the scatter)?
'''),
    code('''
def loss(w):
    return ((w * x - y) ** 2).mean()

ws = np.linspace(0, 12, 200)
fig, ax = plt.subplots(figsize=(7, 3))
ax.plot(ws, [loss(w) for w in ws])
ax.set_xlabel("w (seconds per turn)"); ax.set_ylabel("mean squared error")
ax.set_title("the loss landscape: a valley"); plt.show()
print(f"loss at w=2: {loss(2):.0f}   at w=5: {loss(5):.0f}   at w=9: {loss(9):.0f}")
'''),
    md('''
A valley. Training = walking downhill in it. With one knob we could brute-force every w — but an LLM has billions of knobs, and you cannot grid-search a billion-dimensional valley. We need the *local slope*: which way is downhill from where I stand?

## The one refresher cell (as agreed: quick, then move)
The **derivative** of loss at w answers: *if I nudge w by a tiny ε, how does loss change?* Positive slope → downhill is to the left. For our loss the calculus gives, via the chain rule (outer: square; inner: w·x − y):

d(loss)/dw = mean( 2 · (w·x − y) · x )

Don't take my word — check it empirically with a finite difference (nudge w by 0.001, see what loss does):
'''),
    code('''
def grad(w):
    return (2 * (w * x - y) * x).mean()

for w in (2.0, 5.0, 9.0):
    eps = 1e-3
    numeric = (loss(w + eps) - loss(w - eps)) / (2 * eps)
    print(f"w={w}: formula {grad(w):10.2f}   nudge-test {numeric:10.2f}")
'''),
    md('''
Formula and nudge-test agree — the calculus is just a fast way to ask "which way is downhill." This *gradient check* trick returns in B4 to keep a whole neural net honest.

## Gradient descent: the loop
Start anywhere. Repeat: compute slope, step *against* it, step size scaled by the **learning rate** (lr).
'''),
    code('''
w, lr, history = 0.5, 0.0005, []
for step in range(60):
    history.append((w, loss(w)))
    w = w - lr * grad(w)
hist = np.array(history)
print(f"learned w = {w:.2f} s/turn   (closed-form best: {(x @ y) / (x @ x):.2f})")
fig, axes = plt.subplots(1, 2, figsize=(11, 3))
axes[0].plot(hist[:, 1]); axes[0].set_xlabel("step"); axes[0].set_ylabel("loss"); axes[0].set_title("loss falls as we walk downhill")
axes[1].scatter(x, y); axes[1].plot(x, w * x, color="tab:red", label=f"y = {w:.2f}·x")
axes[1].set_xlabel("turns"); axes[1].set_ylabel("duration (s)"); axes[1].legend(); axes[1].set_title("the fitted model")
plt.tight_layout(); plt.show()
'''),
    md('''
You just trained a model. That falling curve is the same "training loss" curve you watched at Fujitsu — same loop, different scale.

## The learning rate knife edge
**PREDICT each case before running:** lr tiny (0.00005) — what does the loss curve look like? lr good (0.0005)? lr huge (0.0019)?
'''),
    code('''
fig, ax = plt.subplots(figsize=(8, 3))
for lr, style in [(0.00005, "crawls"), (0.0005, "converges"), (0.0019, "DIVERGES")]:
    w, hs = 0.5, []
    for _ in range(60):
        hs.append(loss(w))
        w = w - lr * grad(w)
    ax.plot(hs, label=f"lr={lr} ({style})")
ax.set_xlabel("step"); ax.set_ylabel("loss"); ax.set_yscale("log"); ax.legend()
ax.set_title("learning rate: too small crawls, too big explodes"); plt.show()
'''),
    md('''
The diverging curve is what "my training blew up" means: each overshoot lands on a steeper slope, which orders an even bigger overshoot. Every practitioner war story about "lowering the lr" is this picture.

Vocabulary now yours: **parameter/weight, loss, gradient, learning rate, step, convergence, divergence, training loop.**

## Self-check
1. The one-sentence definition of learning?
2. What does the gradient tell you, in plain words?
3. Why squared error and not absolute error? (Two reasons given above.)
4. Loss reached exactly zero on the training data. Is that automatically good? (Hold your answer — B2 settles it.)
5. **Gotcha:** doubling the learning rate halves training time, a colleague claims. When is that true and when does it detonate?

<details><summary>Answers</summary>

1. Adjust numbers until wrongness shrinks.
2. For each parameter: which direction (and how steeply) the loss changes if you nudge it — i.e., which way is downhill.
3. Penalizes both directions, punishes large misses superlinearly, and is smooth so slopes exist everywhere.
4. Not necessarily — it may have memorized the training points while learning nothing general (overfitting; next book).
5. True while steps stay well inside the valley's curvature; past the critical size, overshoot compounds and loss diverges — the third curve.
</details>
'''),
]

# ================================================================ B2
NBS["B2_classification_end_to_end.ipynb"] = [
    md('''
# B2 — Classification end-to-end

**From:** "predicting numbers" (B1)  **To:** predicting *categories* with probabilities, the loss LLMs actually train on, and the overfitting trap plus its fix.

Our project asks categorical questions constantly: task completed — yes or no? Call acceptable — yes or no? A regression line outputs any number; we need **"yes with probability 0.83."** Three new ideas chain together: **logit → sigmoid → cross-entropy.**

The toy world below mimics our calls: two features per call (median response gap, number of overlaps), and a truth label "failed call?" — synthetic, but shaped like the real thing.
'''),
    code(BOOT + '''
n = 120
good = np.column_stack([rng.normal(550, 150, n // 2), rng.normal(1.6, 1.0, n // 2)])
bad  = np.column_stack([rng.normal(820, 210, n // 2), rng.normal(2.8, 1.4, n // 2)])
X = np.vstack([good, bad])
y = np.array([0] * (n // 2) + [1] * (n // 2))
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.scatter(X[y == 0, 0], X[y == 0, 1], label="ok call", alpha=0.7)
ax.scatter(X[y == 1, 0], X[y == 1, 1], label="failed call", alpha=0.7, marker="x")
ax.set_xlabel("median gap (ms)"); ax.set_ylabel("overlap count"); ax.legend()
ax.set_title("synthetic calls in feature space"); plt.show()
'''),
    md('''
## Logits and the squash
A linear model scores each point: **z = w₁·gap + w₂·overlaps + b**. That raw score is called a **logit** — any real number, more positive = more "failed-ish." To bet money we need a probability in (0,1). The **sigmoid** squashes: σ(z) = 1/(1+e^(−z)). (Its n-class sibling, **softmax**, does the same for many categories — that is the last layer of every LLM, turning logits over ~100k tokens into next-token probabilities.)

**PREDICT:** what does scaling all logits by 5 (z → 5z) do to the sigmoid curve — and to the model's *confidence*?
'''),
    code('''
z = np.linspace(-6, 6, 200)
sig = lambda z: 1 / (1 + np.exp(-z))
fig, ax = plt.subplots(figsize=(7, 3))
ax.plot(z, sig(z), label="sigmoid(z)")
ax.plot(z, sig(5 * z), label="sigmoid(5z) - sharper")
ax.set_xlabel("logit z"); ax.set_ylabel("probability"); ax.legend()
ax.set_title("the squash; scaling logits = confidence knob"); plt.show()
'''),
    md('''
Scaling logits sharpens confidence without changing *which* side wins. File that away: **temperature in LLMs is exactly this knob in reverse** (divide logits by T; T→0 sharpens toward certainty). Book C1 picks it up.

## Cross-entropy: the loss of "surprise"
For a true label, the loss is **−log(probability the model gave the truth)**. Confidently right → tiny loss. Unsure → moderate. **Confidently wrong → enormous.** This asymmetry is the point: it brutalizes overconfident error.
'''),
    code('''
for p_truth, story in [(0.95, "confidently RIGHT"), (0.5, "shrugging"), (0.05, "confidently WRONG")]:
    print(f"model gave truth p={p_truth:4.2f} ({story:18s}) -> loss {-np.log(p_truth):5.2f}")
'''),
    md('''
LLMs train on exactly this loss, token by token: "the truth was token X — how surprised were you?" Trillions of small surprises, descended by gradient. You now know the loss function of the entire modern era.

## Train it (B1's loop, three parameters now)
'''),
    code('''
Xs = (X - X.mean(0)) / X.std(0)            # standardize features so one lr fits both
w, b, lr = np.zeros(2), 0.0, 0.5
for step in range(400):
    p = sig(Xs @ w + b)
    grad_w = Xs.T @ (p - y) / len(y)       # gradients of cross-entropy (take on faith today)
    grad_b = (p - y).mean()
    w -= lr * grad_w; b -= lr * grad_b
acc = ((sig(Xs @ w + b) > 0.5) == y).mean()
print(f"train accuracy: {acc:.0%}   weights: gap {w[0]:+.2f}, overlaps {w[1]:+.2f}")

gx, gy = np.meshgrid(np.linspace(-2.5, 2.5, 200), np.linspace(-2.5, 2.5, 200))
pp = sig(np.column_stack([gx.ravel(), gy.ravel()]) @ w + b).reshape(gx.shape)
fig, ax = plt.subplots(figsize=(7, 3.4))
ax.contourf(gx, gy, pp, levels=20, cmap="RdBu_r", alpha=0.65)
ax.scatter(Xs[y == 0, 0], Xs[y == 0, 1], label="ok")
ax.scatter(Xs[y == 1, 0], Xs[y == 1, 1], marker="x", label="failed")
ax.set_xlabel("gap (standardized)"); ax.set_ylabel("overlaps (standardized)"); ax.legend()
ax.set_title("decision field: shading = model's P(failed)"); plt.show()
'''),
    md('''
(How to read a **contour/decision plot**: the background shading is the model's probability at every possible point — deep blue "surely ok," deep red "surely failed," the pale band between them is the **decision boundary**, where the model genuinely does not know.)

Both weights came out positive — bigger gaps and more overlaps push toward "failed." The model *discovered* the rubric's direction from data.

## Overfitting: the trap, seen with eyes
A model can ace training data by **memorizing** it. The honest test is data it never saw. Watch a memorizer (1-nearest-neighbor: copy the label of the closest training point) vs our humble line, on fresh validation calls:
'''),
    code('''
def fresh(n):
    g = np.column_stack([rng.normal(550, 150, n // 2), rng.normal(1.6, 1.0, n // 2)])
    b = np.column_stack([rng.normal(820, 210, n // 2), rng.normal(2.8, 1.4, n // 2)])
    Xv = (np.vstack([g, b]) - X.mean(0)) / X.std(0)
    return Xv, np.array([0] * (n // 2) + [1] * (n // 2))

def knn1(Xq):
    d = ((Xq[:, None, :] - Xs[None, :, :]) ** 2).sum(-1)
    return y[d.argmin(1)]

Xv, yv = fresh(200)
rows = [("memorizer (1-NN)", (knn1(Xs) == y).mean(), (knn1(Xv) == yv).mean()),
        ("logistic line",    ((sig(Xs@w+b) > .5) == y).mean(), ((sig(Xv@w+b) > .5) == yv).mean())]
print(f"{'model':<18} {'train acc':>9} {'VAL acc':>9}")
for name, tr, va in rows:
    print(f"{name:<18} {tr:>9.0%} {va:>9.0%}")
'''),
    md('''
The memorizer is perfect on what it saw and *worse* on what it did not — that spread is the **generalization gap**, ML's lie detector. The humble line, which could not memorize, holds steady. Moral: **always score on held-out data**, and distrust any perfect training number.

Bridge to our project: this is *the same epistemology* as judging the judge with **blind** human labels (F3) — performance claimed on data the system could fit is not evidence.

## Self-check
1. Logit, sigmoid, probability — chain them in one sentence.
2. Why is cross-entropy brutal specifically to confident error, and why is that desirable?
3. What is the generalization gap and what does a large one scream?
4. Connect temperature to today's "scale the logits" demo.
5. **Gotcha:** your protein model reports 99.4% training accuracy. Your first question?

<details><summary>Answers</summary>

1. The model emits a raw score (logit); sigmoid squashes it into (0,1); that squashed value is the claimed probability.
2. Loss −log p explodes as p(truth)→0; a model that bets hard and wrong must be punished harder than one that shrugs, or it learns to bluff.
3. Train-vs-heldout performance spread; a big gap screams memorization, not learning.
4. Temperature divides logits before softmax: T→0 sharpens toward argmax certainty (our judge's setting), T high flattens toward dice.
5. "And on data it has never seen?" — no validation number, no conversation.
</details>
'''),
]

# ================================================================ B3
NBS["B3_words_as_vectors.ipynb"] = [
    md('''
# B3 — Words as vectors

**From:** "computers cannot read"  **To:** building word vectors from our own call transcripts and watching meaning emerge as geometry.

Models eat numbers. Words are symbols. The bridge between them is *the* founding move of modern NLP, and you can build it from scratch in this notebook with counting alone.

## Attempt 1: one-hot vectors (and why they fail)
Give each word its own slot: "hotel" = [1,0,0,…], "guesthouse" = [0,1,0,…]. Honest encoding, but every pair of words is equally distant — the geometry contains **no meaning**. We measure that with **cosine similarity**: 1.0 = same direction (similar), 0.0 = perpendicular (unrelated).
'''),
    code(BOOT + '''
words = ["hotel", "guesthouse", "thursday", "friday", "cheap", "expensive"]
onehot = np.eye(len(words))
def cosine(u, v):
    return u @ v / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-9)
print("cosine similarities under one-hot:")
print(f"  hotel ~ guesthouse: {cosine(onehot[0], onehot[1]):.2f}")
print(f"  hotel ~ thursday:   {cosine(onehot[0], onehot[2]):.2f}")
print("identical words aside, EVERYTHING is 0 - 'hotel' is no closer to 'guesthouse' than to 'thursday'")
'''),
    md('''
## Attempt 2: "you shall know a word by the company it keeps" (Firth, 1957)
Words that appear in similar **contexts** have similar meanings — *thursday* and *friday* both follow "leave on", precede "at 9:30". So: slide a window over lots of text, count which words co-occur near which, and let each word's **row of counts** be its vector. Similar contexts → similar rows → high cosine. Meaning from raw counting.

Our corpus: 100 real SpokenWOZ call transcripts (loading the 246MB file takes a few seconds).
'''),
    code('''
import json, re
from collections import Counter
data = json.load(open(ROOT / "data" / "spokenwoz" / "data.json"))
dev_ids = open(ROOT / "data" / "spokenwoz" / "valListFile.json").read().split()[:100]
docs = []
for did in dev_ids:
    if did in data:
        text = " ".join(t["text"] for t in data[did]["log"])
        docs.append(re.findall(r"[a-z']+", text.lower()))
freq = Counter(w for d in docs for w in d)
ranked = [w for w, c in freq.most_common(230)]
vocab = [w for w in ranked[30:] if len(w) > 2][:150]   # drop the 30 most frequent: glue words ('the', 'and') co-occur with EVERYTHING and drown meaning
v2i = {w: i for i, w in enumerate(vocab)}
print(f"{len(docs)} calls · {sum(map(len, docs))} words · vocab of {len(vocab)} -> sample:", vocab[:12])
'''),
    code('''
WINDOW = 4
C = np.zeros((len(vocab), len(vocab)))
for doc in docs:
    idx = [v2i.get(w, -1) for w in doc]
    for i, wi in enumerate(idx):
        if wi < 0: continue
        for j in range(max(0, i - WINDOW), min(len(idx), i + WINDOW + 1)):
            if j != i and idx[j] >= 0:
                C[wi, idx[j]] += 1
V = np.log1p(C)                                   # tame the heavy-hitters
print("co-occurrence matrix built:", V.shape)
'''),
    md('''
**PREDICT before running:** the three nearest neighbors of "tuesday"? of "hotel"? of "expensive"? Commit out loud.
'''),
    code('''
def neighbors(word, k=5):
    u = V[v2i[word]]
    sims = V @ u / (np.linalg.norm(V, axis=1) * np.linalg.norm(u) + 1e-9)
    order = np.argsort(-sims)
    return [(vocab[i], round(float(sims[i]), 2)) for i in order if vocab[i] != word][:k]

for q in ["tuesday", "hotel", "expensive"]:
    if q in v2i:
        print(f"{q:>10} -> {neighbors(q)}")
'''),
    md('''
Nobody told the matrix that weekdays form a family or that price words travel together — *counting context* discovered it. This is meaning-as-geometry, the bedrock idea under every embedding layer in every LLM.

## See the whole map at once
150 dimensions do not fit on a screen. **PCA** (principal component analysis) finds the 2 directions along which the vectors vary most and projects onto them — a shadow that preserves as much structure as a flat picture can. Six lines of numpy:
'''),
    code('''
Vc = V - V.mean(0)
U, S, Vt = np.linalg.svd(Vc, full_matrices=False)
P = Vc @ Vt[:2].T
fig, ax = plt.subplots(figsize=(11, 7))
show = vocab[:70]
for w in show:
    x_, y_ = P[v2i[w]]
    ax.annotate(w, (x_, y_), fontsize=9)
ax.scatter(P[[v2i[w] for w in show], 0], P[[v2i[w] for w in show], 1], s=8, alpha=0.4)
ax.set_title("word map from OUR calls (PCA of co-occurrence vectors)")
ax.set_xlabel("principal direction 1"); ax.set_ylabel("principal direction 2"); plt.show()
'''),
    md('''
(How to read: position has no absolute meaning — only *proximity* does. Hunt for: the day-of-week cluster, food/restaurant territory, booking verbs. Words sharing a neighborhood share contexts in real Indian service calls transcribed by a real, garbling ASR.)

## From counted to learned
Real systems do not count — they **learn** the vectors: word2vec (2013) trained small networks to predict context words, and the vectors became famous (king − man + woman ≈ queen). LLMs take the final step: the **token embedding layer** (every token → a learned vector) is literally layer one of the machine you will meet in Part C, learned jointly with everything else by the B1/B2 loop.

## Exercise
Pick three words from `vocab` yourself (print it). For each, predict neighbors, then query. At least one result will be junk — ASR garble or a stopword-ish term. Explain *why* its contexts are uninformative.
'''),
    code('''
print(vocab)
for q in ["train", "people", "phone"]:        # replace with your three
    if q in v2i:
        print(f"{q:>9} -> {neighbors(q)}")
'''),
    md('''
## Self-check
1. Why are one-hot vectors meaning-blind, in geometric terms?
2. State the distributional hypothesis in one sentence and name the operation that exploits it here.
3. What does cosine similarity measure, and why normalize by the norms?
4. What did PCA buy us, and what did it cost?
5. **Gotcha:** two true synonyms never co-occur *with each other*. Does that break this method?

<details><summary>Answers</summary>

1. All pairs are orthogonal — equal distance everywhere, so the geometry encodes identity only, zero similarity structure.
2. Words in similar contexts mean similar things; we exploit it by counting context windows so rows of the matrix become comparable.
3. The angle between vectors (direction match), ignoring magnitude — frequent words would otherwise dominate raw dot products.
4. A viewable 2D shadow preserving maximal variance; the cost is everything in the discarded 148 directions (some structure is invisible).
5. No — synonyms are similar because they co-occur with the same *third* words (each other's contexts overlap), not because they co-occur together. That is second-order similarity, exactly what the row-vectors capture.
</details>
'''),
]

# ================================================================ B4
NBS["B4_neural_net_in_numpy.ipynb"] = [
    md('''
# B4 — A neural net in 100 lines of numpy

**From:** B2's straight-line classifier  **To:** a trained neural network you built, verified, and can no longer be mystified by — plus the bridge to the PyTorch you ran at Fujitsu.

B2's model draws a *line*. Some truths are not line-shaped. Today's data: two interleaved arcs (the classic "moons") — no line can separate them. The fix: stack **linear → nonlinearity → linear**, and the machine can bend.

New words, defined: a **layer** is a matrix multiply (+ bias); **hidden units** are the intermediate values between layers; an **activation** is the nonlinear squish between layers — ours is **ReLU**: max(0, x), brutally simple. Without the nonlinearity, stacked layers collapse algebraically into one line again (multiply two matrices, get a matrix) — the nonlinearity is *load-bearing*.
'''),
    code(BOOT + '''
n = 240
t1 = rng.uniform(0, np.pi, n // 2); t2 = rng.uniform(0, np.pi, n // 2)
arc1 = np.column_stack([np.cos(t1), np.sin(t1)]) + rng.normal(0, 0.12, (n // 2, 2))
arc2 = np.column_stack([1 - np.cos(t2), 0.4 - np.sin(t2)]) + rng.normal(0, 0.12, (n // 2, 2))
X = np.vstack([arc1, arc2]); y = np.array([0] * (n // 2) + [1] * (n // 2))
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.scatter(X[y == 0, 0], X[y == 0, 1], alpha=0.7, label="class 0")
ax.scatter(X[y == 1, 0], X[y == 1, 1], alpha=0.7, marker="x", label="class 1")
ax.set_title("two moons - no straight line separates these"); ax.legend(); plt.show()
'''),
    md('''
## The forward pass = shapes flowing through matrices
Architecture: input (n,2) → layer 1 weights (2,16) → ReLU → layer 2 weights (16,1) → sigmoid → probability. Follow the shapes; that is 80% of understanding any network.
'''),
    code('''
sig = lambda z: 1 / (1 + np.exp(-z))
H = 16
W1 = rng.normal(0, 0.8, (2, H)); b1 = np.zeros(H)
W2 = rng.normal(0, 0.8, (H, 1)); b2 = np.zeros(1)

def forward(X):
    z1 = X @ W1 + b1          # (n,2)@(2,16) -> (n,16)
    a1 = np.maximum(0, z1)    # ReLU: negatives become 0
    z2 = a1 @ W2 + b2         # (n,16)@(16,1) -> (n,1)
    return z1, a1, z2, sig(z2).ravel()

_, _, _, p = forward(X)
print("untrained predictions hover near chance:", p[:6].round(2))
'''),
    md('''
## Backward: the chain rule, industrialized
B1's chain rule, applied layer by layer from the loss backwards — each layer asks "how should MY weights nudge, given how my output should nudge?" The algebra is mechanical (calculus homework, skippable today per our agreement); the **code + a numerical check** is the trust we need:
'''),
    code('''
def backward(X, y, z1, a1, p):
    n = len(y)
    dz2 = (p - y).reshape(-1, 1) / n            # cross-entropy + sigmoid: famously clean gradient
    dW2 = a1.T @ dz2; db2 = dz2.sum(0)
    dz1 = (dz2 @ W2.T) * (z1 > 0)               # ReLU gate: gradient flows only where it was active
    dW1 = X.T @ dz1; db1 = dz1.sum(0)
    return dW1, db1, dW2, db2

def loss_fn(p, y):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p)).mean()

z1, a1, z2, p = forward(X)
dW1, db1, dW2, db2 = backward(X, y, z1, a1, p)
i, j, eps = 0, 3, 1e-5
W1[i, j] += eps; _, _, _, p_hi = forward(X); L_hi = loss_fn(p_hi, y)
W1[i, j] -= 2 * eps; _, _, _, p_lo = forward(X); L_lo = loss_fn(p_lo, y)
W1[i, j] += eps
print(f"gradient via backward: {dW1[i, j]:.6f}   via nudge-test: {(L_hi - L_lo) / (2 * eps):.6f}")
print("they match -> the backward code is telling the truth")
'''),
    md('''
That check is the same finite-difference honesty from B1, now policing a real network. Professionals do exactly this when implementing layers by hand.

## Train, and watch the boundary bend
'''),
    code('''
lr = 0.6
losses = []
for step in range(1500):
    z1, a1, z2, p = forward(X)
    losses.append(loss_fn(p, y))
    dW1, db1, dW2, db2 = backward(X, y, z1, a1, p)
    W1 -= lr * dW1; b1 -= lr * db1; W2 -= lr * dW2; b2 -= lr * db2
print(f"final train accuracy: {((p > .5) == y).mean():.0%}")

gx, gy = np.meshgrid(np.linspace(-1.6, 2.6, 250), np.linspace(-1.3, 1.7, 250))
_, _, _, pp = forward(np.column_stack([gx.ravel(), gy.ravel()]))
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(losses); axes[0].set_xlabel("step"); axes[0].set_ylabel("loss"); axes[0].set_title("training")
axes[1].contourf(gx, gy, pp.reshape(gx.shape), levels=20, cmap="RdBu_r", alpha=0.7)
axes[1].scatter(X[y == 0, 0], X[y == 0, 1], s=12)
axes[1].scatter(X[y == 1, 0], X[y == 1, 1], s=12, marker="x")
axes[1].set_title("the boundary BENDS - hello nonlinearity"); plt.tight_layout(); plt.show()
'''),
    md('''
A curved decision field from nothing but matrices, max(0,·), and B1's loop. **PREDICT, then run:** with 2 hidden units instead of 16 — what does the boundary look like? With 64 — better or just *busier*?
'''),
    code('''
def train_width(H, steps=1500, lr=0.6):
    W1 = rng.normal(0, 0.8, (2, H)); b1 = np.zeros(H)
    W2 = rng.normal(0, 0.8, (H, 1)); b2 = np.zeros(1)
    for _ in range(steps):
        z1 = X @ W1 + b1; a1 = np.maximum(0, z1); p = sig((a1 @ W2 + b2)).ravel()
        dz2 = (p - y).reshape(-1, 1) / len(y)
        dW2 = a1.T @ dz2; db2 = dz2.sum(0)
        dz1 = (dz2 @ W2.T) * (z1 > 0)
        W1 -= lr * (X.T @ dz1); b1 -= lr * dz1.sum(0); W2 -= lr * dW2; b2 -= lr * db2
    def f(Q):
        return sig((np.maximum(0, Q @ W1 + b1) @ W2 + b2)).ravel()
    return f

fig, axes = plt.subplots(1, 3, figsize=(14, 3.6))
for ax, H in zip(axes, [2, 16, 64]):
    f = train_width(H)
    ax.contourf(gx, gy, f(np.column_stack([gx.ravel(), gy.ravel()])).reshape(gx.shape),
                levels=20, cmap="RdBu_r", alpha=0.7)
    ax.scatter(X[y == 0, 0], X[y == 0, 1], s=8); ax.scatter(X[y == 1, 0], X[y == 1, 1], s=8, marker="x")
    ax.set_title(f"{H} hidden units")
plt.tight_layout(); plt.show()
'''),
    md('''
Two units underfit (not enough bend); sixteen is graceful; sixty-four traces noise wiggles — B2's overfitting lesson, now in curve form. Capacity is a dial, not a virtue.

## The bridge to what you already ran
At Fujitsu you wrote something like: `loss.backward(); optimizer.step()`. Decoded against today:
- `model(x)` — our `forward` (matrices + activations)
- `loss.backward()` — our `backward` cell, except **autograd** derives it mechanically for any architecture (that is PyTorch's entire magic trick)
- `optimizer.step()` — our `W -= lr * dW` lines (fancier optimizers like Adam add per-weight adaptive learning rates)
- GPU — these same matrix multiplies, thousands at once

And an LLM? *This machine*, with ~10⁹–10¹² parameters, a smarter wiring diagram (attention — Part C), trained by this exact loop on next-token cross-entropy (B2). You have now personally built every conceptual component except attention. The mystery budget is almost spent.

## Self-check
1. Why is the nonlinearity non-negotiable? (The algebraic reason.)
2. What does ReLU do during backward, not just forward?
3. What does the numerical gradient check prove, and what does it not prove?
4. Width 64 hit 100% train accuracy — your reaction, verbatim from B2?
5. **Gotcha:** "PyTorch trains models." What does PyTorch actually automate, in one sentence?

<details><summary>Answers</summary>

1. Stacked linear maps compose into a single linear map (matrix product) — without a nonlinearity, depth buys nothing and the boundary stays a line.
2. It gates gradients: where the unit was inactive (z≤0), zero gradient flows back — only active paths learn.
3. That backward computes the true derivative of THIS loss for THIS code; not that the model is good, the data sensible, or training will converge.
4. "And on data it has never seen?" — train-perfect means little; check the generalization gap.
5. It automates the backward pass (autograd) and bookkeeping around the same loop you wrote today — the learning is still loss + gradient + step.
</details>
'''),
]

for name, cells in NBS.items():
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                      "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    (HERE / name).write_text(json.dumps(nb, indent=1))
    print("wrote", name, f"({len(cells)} cells)")
