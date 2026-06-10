#!/usr/bin/env python3
# Generates the 7 learning notebooks (00-06). Rerun any time: python notebooks/build_notebooks.py
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
print("repo root:", ROOT)
'''

NBS = {}

# ---------------------------------------------------------------- 00
NBS["00_start_here.ipynb"] = [
    md('''
# 00 — Start here: the method, then the map

You have ~2 hours and 6 notebooks. This one takes 5 minutes and exists so the other 5 stick.

## The loop (use it in every notebook)
1. **Predict** — before running any code cell, say out loud what you expect it to print.
2. **Run** — then run it.
3. **Explain back** — one sentence, out loud, in your own words. If you can't, you don't have it yet; ask Cursor about that exact cell before moving on.
4. **Self-check** — every notebook ends with questions. Answer out loud BEFORE opening the answers.
5. **Teach back** — when done, tell Claude Code "quiz me" in the build session. Getting grilled is the point; it's a hackathon dress rehearsal.

Being wrong in step 1 is the best outcome — surprise is where learning happens. Never skip the prediction.

## The order and the time budget
| nb | topic | min |
|---|---|---|
| 01 | what a voice agent actually is (STT, TTS, VAD, barge-in, latency) | 20 |
| 02 | measuring conversations (FTO, gaps, p50/p90, stress profiles) | 20 |
| 03 | LLM-as-judge (rubrics, JSON contracts, biases, caching) | 20 |
| 04 | trusting the judge (blind labels, Cohen's kappa, bootstrap CI) | 20 |
| 05 | DPO and improvement data (the training ladder, preference pairs) | 25 |
| 06 | the room and the pitch (who builds what, honest claims, final quiz) | 15 |

Everything runs on OUR repo data — the hero call you recorded tonight and the 10 real SpokenWOZ calls. Nothing is synthetic toy data.

## The reusable recipe (your future "learning sprint" prompt)
Save this — it is how you commission this experience again in any new domain:

> I have N hours and spare credits. I know [my real background, specific]. I need to work in [new domain] starting [when]. Build me ordered Jupyter notebooks that (1) use my actual project's data, never toy data, (2) force predict-then-run on every code cell, (3) define every term from zero but bridge to what I know, (4) end each notebook with self-check questions and the final one with a quiz you grade me on harshly, (5) include one "gotcha" per topic that an expert would test me with.

That recipe is the difference between reading about a field and entering it.
'''),
    code(BOOT + '''
import importlib
for m in ["numpy", "matplotlib", "yaml", "google.genai"]:
    importlib.import_module(m)
print("environment ready — open 01 and predict before you run")
'''),
]

# ---------------------------------------------------------------- 01
NBS["01_voice_agents_anatomy.ipynb"] = [
    md('''
# 01 — What a voice agent actually is

## The machine you are evaluating
A modern voice agent is three models in a relay race, run in a loop, under brutal time pressure:

1. **STT / ASR** (speech-to-text, a.k.a. automatic speech recognition) — turns the caller's audio into text, ideally *streaming* (words appear while the person is still talking). Quality metric: **WER**, word error rate.
2. **LLM** — decides what to say next given the conversation so far (this is where the "agent" lives: prompts, tools, business logic).
3. **TTS** (text-to-speech) — turns the reply into audio. Cartesia's whole company is this box. Their headline metric is **TTFA** — time to first audio: how many ms until the voice starts. Sonic 3.5 claims 82ms.

The relay happens **every turn**, so per-turn latency = STT finalization + LLM first tokens + TTS first audio + network. Humans hand off the floor in ~200–300ms, so anything the stack adds is felt immediately. That is why our rubric calls ≤300ms snappy and >800ms laggy — past ~800ms callers start saying "hello? are you there?"

## The hard part is not the models — it is turn-taking
The agent must decide **when the caller is done talking**. That decision is called **endpointing**, and it is built on **VAD** — voice activity detection: a tiny classifier answering "is there speech right now?" frame by frame. Endpointing is basically: VAD says silence + silence has lasted X ms → caller is done → respond.

Get X too small → the agent answers during the caller's thinking pause → **barge-in** (the agent interrupts a human). Get X too big → dead air after every caller turn → laggy. *Every voice agent lives on this knife edge.* Our hero call's two sins are exactly the two ways to fall off it. Not a coincidence — that is the demo's thesis.

Two more terms you will hear in the room:
- **Backchannel** — tiny overlapping listener noises ("mm-hmm", "haan") that do NOT claim the floor. Healthy conversation has them; that is why overlaps ≤100ms do not count as barge-ins in our rubric.
- **Diarization** — figuring out who-spoke-when from raw audio when you do not have separate channels. Error-prone, and a classic way demos die. We engineered around it twice: SpokenWOZ gives speaker tags, and the hero call's timestamps come from how we assembled it.

And one from our own data: **code-switching** — mixing languages mid-sentence ("Madhapur side anukunta, near the metro station"). Real Indian callers do this constantly; most English-trained stacks degrade on it. It is why `language` sits in our schema from day one.
'''),
    code(BOOT + '''
import json, wave, numpy as np
import matplotlib.pyplot as plt
from IPython.display import Audio

w = wave.open(str(ROOT / "data" / "hero" / "hero_001.wav"))
sr, n = w.getframerate(), w.getnframes()
sig = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
call = json.loads((ROOT / "data" / "hero" / "turns.json").read_text())
print(f"{len(sig)/sr:.1f}s of audio · {len(call['turns'])} turns · sr={sr}")
Audio(str(ROOT / "data" / "hero" / "hero_001.wav"))
'''),
    md('''
**PREDICT** before running the next cell: the plot will show one bar per turn (teal = you, purple = agent). Where will bars *overlap vertically in time*, and where will there be a visible horizontal hole? Say the timestamps out loud — you recorded this call.
'''),
    code('''
t = np.arange(len(sig)) / sr
fig, ax = plt.subplots(figsize=(13, 3.5))
ax.plot(t, sig, lw=0.3, color="#999", alpha=0.7)
for tn in call["turns"]:
    c = "#1D9E75" if tn["speaker"] == "user" else "#7F77DD"
    y = (0.75, 1.05) if tn["speaker"] == "user" else (-1.05, -0.75)
    ax.fill_betweenx(y, tn["start_ms"]/1000, tn["end_ms"]/1000, color=c, alpha=0.65)
    ax.text((tn["start_ms"]+tn["end_ms"])/2000, y[0]+0.12, tn["turn_id"], ha="center", fontsize=8)
ax.set(xlabel="seconds", yticks=[], title="hero_001 — caller (top) vs agent (bottom)")
plt.show()
'''),
    md('''
Look at `t2`→`t3`: the purple bar starts while teal is still running — the **barge-in**, exactly 0.8s of double-talk. Look at `t6`→`t7`: a hole — **dead air**, 1.62s. You can *see* the two sins. The failure table is just this picture, written as numbers.
'''),
    md('''
## Build a toy VAD in 6 lines
The booth's hands-free flow tonight was exactly this idea: chop audio into 30ms frames, compute energy (RMS), threshold it. **PREDICT:** during your t2 thinking pause, what will the mask show?
'''),
    code('''
frame = int(0.030 * sr)
trimmed = sig[: len(sig) // frame * frame]
rms = np.sqrt((trimmed.reshape(-1, frame) ** 2).mean(axis=1))
speech = rms > 0.02
tf = (np.arange(len(rms)) * frame + frame/2) / sr
fig, ax = plt.subplots(figsize=(13, 2))
ax.fill_between(tf, 0, speech.astype(int), step="mid", color="#1D9E75", alpha=0.7)
ax.set(xlabel="seconds", yticks=[0, 1], yticklabels=["silence", "speech"], title="energy VAD, 30ms frames")
plt.show()
print(f"speech fraction: {speech.mean():.0%}")
'''),
    md('''
That dip inside t2 is your scripted pause — a VAD with a short endpointing hold would have cut you off there, which is why the booth waited 3.2s on that turn and why real agents barge in on hesitant callers. **An entire product failure class, visible in 6 lines of numpy.**

## Exercise — connect to the pipeline
Use the repo's own `turn_metrics` (the function the failure table is built on) and find both sins programmatically. Fill in the blank, predict the two numbers first.
'''),
    code('''
from signals import turn_metrics
events = turn_metrics(call["turns"])
sins = [e for e in events if e["overlap_ms"] > 100 or e["gap_ms"] > 800]   # YOUR TURN first: why these two conditions?
for e in sins:
    print(f"{e['prev_turn_id']}->{e['next_turn_id']}  fto={e['fto_ms']:+}ms  "
          f"overlap={e['overlap_ms']}  gap={e['gap_ms']}  ({e['prev_spk']}->{e['next_spk']})")
'''),
    md('''
## Self-check (out loud, then open answers)
1. Name the three models in the relay and the metric each is judged by.
2. What is endpointing, and what are the two opposite failure modes of getting it wrong?
3. Why does our rubric ignore overlaps under 100ms?
4. Why did we go out of our way to avoid diarization in this project?
5. A founder says "our agent's average response time is 600ms, we're fine." What two follow-up questions does this notebook arm you to ask?

<details><summary>Answers</summary>

1. STT/ASR (WER), LLM (task quality — what our judge scores), TTS (TTFA / naturalness).
2. Deciding the caller is finished. Too eager → barge-in over thinking pauses; too patient → dead air / laggy responses.
3. Sub-100ms overlaps are mostly backchannels — cooperative listener noises that do not claim the floor. Counting them would flood the table with non-failures.
4. Who-spoke-when from raw audio is error-prone; bad speaker boundaries poison every downstream timing number. We got speaker truth for free instead (channel tags in SpokenWOZ, assembly in the hero call).
5. "What is the p90, not the mean?" and "is that measured per turn from caller-end-of-speech to first audio, or something flattering?" — tails and measurement definitions are where averages hide failure.
</details>
'''),
]

# ---------------------------------------------------------------- 02
NBS["02_measuring_conversations.ipynb"] = [
    md('''
# 02 — Measuring conversations: the deterministic layer

## One number per handoff
For every pair of consecutive turns: **FTO = next.start_ms − prev.end_ms** (floor transfer offset — "the floor" = whose turn it is to speak).
- FTO **negative** → overlap → if >100ms, a **barge-in** (someone took the floor by force).
- FTO **positive** → gap → on user→agent handoffs this is **response latency**; >800ms = laggy.

Everything in the failure table is this subtraction plus two thresholds, and both thresholds live in `rubric.yaml`, not in code. You verified one by hand tonight (t2→t3 = −2,220ms on MUL0035).

## Why median and p90, never mean
Same culture as your perf work: latency distributions are skewed; a few terrible gaps drag a mean while the median stays honest, and the p90 tells you what the *bad tenth* of experiences feel like. Users do not experience averages; they experience tails.

## Stress profiles = workload classes
Each call gets a scenario-difficulty label (`clean`, `pause_heavy`, `interruption` — assigned by deterministic rules; `ambiguous`, `kb_gap` need semantics, so code never assigns them). Slicing results by class — the **cross-cut** — is how "the agent breaks specifically on hesitant callers" becomes visible. One blended score hides exactly that.
'''),
    code(BOOT + '''
import json
import numpy as np
import matplotlib.pyplot as plt
from signals import turn_metrics, analyze, load_rubric

rubric = load_rubric(ROOT / "rubric.yaml")
calls = {p.stem: json.loads(p.read_text()) for p in sorted((ROOT / "data" / "normalized").glob("*.json"))}
print(len(calls), "calls:", ", ".join(calls))
'''),
    md('''
**PREDICT:** which call will have the worst (highest) median user→agent gap? You met `swz_MUL0056` tonight. Then run.
'''),
    code('''
rows = []
for cid, call in calls.items():
    r = analyze(call["turns"], rubric)
    rows.append((cid, call["stress_profile"], len(r["barge_ins"]), r["latency"]["n_laggy"],
                 r["latency"]["median_gap_ms"], r["latency"]["p90_gap_ms"]))
print(f"{'call':<14} {'profile':<13} {'barge':>5} {'laggy':>5} {'med':>7} {'p90':>7}")
for row in sorted(rows, key=lambda x: -(x[4] or 0)):
    print(f"{row[0]:<14} {row[1]:<13} {row[2]:>5} {row[3]:>5} {str(row[4]):>7} {str(row[5]):>7}")
'''),
    md('''
## Mean vs median vs p90 — see it, not believe it
**PREDICT:** for MUL0056's gaps, will the mean be above or below the median, and why?
'''),
    code('''
gaps = [e["gap_ms"] for e in turn_metrics(calls["swz_MUL0056"]["turns"])
        if e["prev_spk"] == "user" and e["next_spk"] == "agent" and e["fto_ms"] >= 0]
gaps_np = np.array(gaps)
print(f"n={len(gaps)}  mean={gaps_np.mean():.0f}  median={np.median(gaps_np):.0f}  p90={np.percentile(gaps_np, 90):.0f}")
plt.figure(figsize=(8, 2.6))
plt.hist(gaps_np, bins=24, color="#7F77DD")
for v, lbl, c in [(gaps_np.mean(), "mean", "#D85A30"), (np.median(gaps_np), "median", "#1D9E75")]:
    plt.axvline(v, color=c, lw=2, label=lbl)
plt.legend(); plt.xlabel("user->agent gap (ms)"); plt.title("MUL0056 response gaps"); plt.show()
'''),
    md('''
## Exercise — you own the threshold now
The rubric says laggy = >800ms. Product teams argue about this number constantly. **PREDICT how many laggy events the whole pool gains if the bar tightens to 500ms**, then run.
'''),
    code('''
def laggy_count(threshold_ms):
    total = 0
    for call in calls.values():
        hand = [e for e in turn_metrics(call["turns"])
                if e["prev_spk"] == "user" and e["next_spk"] == "agent" and e["fto_ms"] >= 0]
        total += sum(1 for e in hand if e["gap_ms"] > threshold_ms)
    return total

for th in (800, 500, 300):
    print(f"laggy events at >{th}ms: {laggy_count(th)}")
'''),
    md('''
That sensitivity — "the failure count is a function of a config line" — is precisely why thresholds live in `rubric.yaml` and get disclosed, never buried. An engineer in the room may push on your 800; your answer: conversation-analysis baselines put natural handoffs ~200–300ms, sub-800 reads as acceptable assistant latency, and the rubric is one line to re-run under their number. Config, not dogma.

## Dirty data — the honesty section
Three real things tonight's corpus taught us, all worth saying out loud to engineers:
1. Some SpokenWOZ "overlaps" run 9+ seconds — ASR segmentation artifacts or crosstalk, not clean barge-ins. We *measure* faithfully but *select* mid-range exemplars (and say so).
2. Speaker truth came from annotation tags, not audio — diarization would have added noise we cannot audit.
3. If a source lacks `end_ms`, overlap is **uncomputable** — the pipeline refuses to fake it (latency-only treatment). Saying "we cannot know that from this data" is a credibility move, not a weakness.

## Self-check
1. Compute the FTO: prev.end = 30,000, next.start = 29,400. Event type?
2. Why is latency only computed on user→agent handoffs?
3. Your agent's mean latency improved 20% after a release but p90 doubled. What happened, in plain words?
4. What makes a stress profile different from a failure?

<details><summary>Answers</summary>

1. −600ms → overlap >100ms → barge-in (whoever spoke second interrupted).
2. We are scoring the agent's responsiveness; a human pausing before answering the bot is not a product defect. (Also: agent→user "gaps" are the human thinking — not ours to judge.)
3. Typical responses got a bit faster but the worst tenth got much worse — e.g. a cache that usually hits but stalls badly on miss. Means hide tail regressions.
4. Profile describes the input (scenario difficulty); failures describe the output (agent performance). Easy-input + failures = the most damning combination — pure product defect.
</details>
'''),
]

# ---------------------------------------------------------------- 03
NBS["03_llm_as_judge.ipynb"] = [
    md('''
# 03 — LLM-as-judge: scoring what arithmetic cannot reach

## Why a judge at all
Subtraction catches *timing* failures. But "did the agent handle the caller's vague answer gracefully?" or "did it claim something the caller never said?" are **semantic** judgments. Pre-LLM, you needed human raters for every call (slow, expensive). The 2023+ move: use a strong LLM as the rater — **LLM-as-judge** — and then *prove* it agrees with humans on a sample (that proof is notebook 04).

## Our judge contract (each line exists for a reason)
- **temperature 0** — sampling randomness off; same input → same verdict (reproducibility).
- **JSON mode** — output is machine-parseable, goes straight into scorecards.
- **Every score ships with a `reason` and `evidence_turn_ids`** — a score you cannot audit is a vibe. Evidence pointers let anyone open the transcript and check the judge.
- **Disk cache keyed by (call_id, dimension, prompt_hash)** — rerunning the pipeline is free, and identical inputs cannot silently produce different histories.
- **Disclosed** — we say it is Gemini Flash, on a slide. Hidden judges are how demos lose rooms.

## The bias list (know these cold — engineers will probe)
LLM judges systematically prefer: **longer answers** (verbosity bias), **the first option shown** (position bias), **their own model family's style** (self-preference), and they **drift lenient** without anchors. Mitigations we use: anchored scales (defined 0/0.5/1 meanings, not "rate 1–10"), required evidence, temperature 0, and human calibration. Notebook 04 is the teeth.
'''),
    code(BOOT + '''
import json
from judge import get_client, judge_dimension, judge_config

client = get_client()
print("judge model:", judge_config()[0])
call = json.loads((ROOT / "data" / "normalized" / "swz_MUL0035.json").read_text())
snippet = "\\n".join(f"{t['turn_id']} {t['speaker']}: {t['text']}" for t in call["turns"][:8])
print(snippet[:600])
'''),
    md('''
Real turns from a real call. Now we judge `repair_quality` — how well the agent handles unclear/partial answers. **PREDICT:** roughly what score does this exchange deserve, and which turn ids should the evidence cite? Commit to numbers before running.
'''),
    code('''
PROMPT = (
  "You are a strict but fair judge of voice-agent calls. Score ONE dimension.\\n\\n"
  "Dimension: repair_quality - when the caller's answer is unclear, partial or mistaken,\\n"
  "does the agent acknowledge what it got and ask one targeted follow-up (1.0),\\n"
  "partially acknowledge but ask clumsily (0.5), or ignore/over-demand/derail (0.0)?\\n\\n"
  "Call turns:\\n" + snippet + "\\n\\n"
  'Return ONLY JSON: {"score": <0, 0.5 or 1>, "reason": "<one falsifiable sentence>", '
  '"evidence_turn_ids": ["..."]}'
)
verdict, cached = judge_dimension(client, "nb03_demo", "repair_quality", PROMPT)
print("from cache:", cached)
print(json.dumps(verdict, indent=2))
'''),
    md('''
Read the `reason`. Is it **falsifiable** — could you check it against the transcript and catch it lying? That property is the entire difference between "AI scored it 0.5" (useless) and an audit trail. Now run the cell again: `from cache: True`, zero cost, identical verdict. That is the cache contract.

## See the cache with your own eyes
'''),
    code('''
cache_dir = ROOT / "data" / ".judge_cache"
for f in sorted(cache_dir.glob("*.json"))[-4:]:
    print(f.name)
print("\\nkey = call_id __ dimension __ sha256(model|prompt)[:16] -> change ONE character of the prompt and it is a different key (cache miss, fresh judgment). Idempotent and honest.")
'''),
    md('''
## Exercise — feel a bad rubric
Run the SAME snippet through a deliberately bad prompt: unanchored 1–10 scale, no evidence required. **PREDICT:** in what ways will the output be worse, not just different?
'''),
    code('''
BAD = ("Rate the agent's handling of unclear answers from 1-10.\\n\\nCall turns:\\n" + snippet +
       '\\n\\nReturn ONLY JSON: {"score": <1-10>, "reason": "<short>", "evidence_turn_ids": []}')
bad_verdict, _ = judge_dimension(client, "nb03_demo", "repair_quality_bad", BAD)
print(json.dumps(bad_verdict, indent=2))
'''),
    md('''
Read what actually came back and judge the *contract*, not the model's mood. The score arrived on a 1–10 scale — but what does a "2" MEAN? Without anchors there is no comparable answer: another call's "3" might describe better or worse behavior. The model may still have volunteered a decent reason or even evidence — modern judges often do — but nothing in the contract FORCED it, so a pipeline cannot rely on it arriving. And a human cannot blind-label "2 vs 3" for agreement stats, so calibration (next notebook) is dead on arrival. Bad rubrics fail *structurally* — comparability, enforceability, calibratability — even when a strong model papers over them on an easy case.

One more thing you just saw: "depart from courage", "head to lift" — that is genuine ASR output mangling place names. Garbled entities are the genre. Judges must reason through transcript noise, and good ones cite it (ours did, in its reason).

## Self-check
1. Why temperature 0 — what claim does it buy us?
2. Recite the cache key and explain why prompt is part of it.
3. Name three judge biases and one mitigation each.
4. Why is "0 / 0.5 / 1 with defined meanings" better than "1–10" for our use?
5. A founder asks: "so the AI grades the AI — why trust it?" Your one-sentence answer?

<details><summary>Answers</summary>

1. Determinism: same call + same rubric → same verdict, so reruns are reproducible and diffs mean something changed in the inputs, not the dice.
2. (call_id, dimension, sha256(model|prompt)) — if the prompt or model changes, old verdicts must not masquerade as current ones.
3. Verbosity → anchored scales & length-blind criteria; position → we judge single transcripts, not A-vs-B orderings; leniency drift / self-preference → human calibration with blind labels (nb 04).
4. Each anchor is a checkable claim; humans can blind-label the same 3 options, enabling agreement stats. Ten unanchored points produce noise no kappa can rescue.
5. "We do not ask you to trust it — we measured where it agrees with blind human labels and we show you the two cases where it was wrong" (that is notebook 04 and Block 7).
</details>
'''),
]

# ---------------------------------------------------------------- 04
NBS["04_human_calibration_kappa.ipynb"] = [
    md('''
# 04 — Trusting the judge: blind labels, kappa, and honest error bars

## The protocol (Block 4 is literally this)
1. A human (you) labels 40–60 calls on ONE binary question ("was the task completed?") **before ever seeing the judge's output on those calls** — *blind*, because seeing the judge first anchors you and the agreement number becomes circular.
2. Run the judge on the same calls. Align by `call_id`.
3. Compute agreement — but not raw agreement. **Kappa.**

## Why raw agreement lies
If 90% of calls succeeded, a broken judge that says "success" every single time scores 90% agreement while measuring nothing. **Cohen's kappa** asks: how much better than *chance* is the agreement, given each rater's base rates?

kappa = (p_observed − p_expected) / (1 − p_expected)

1.0 = perfect, 0 = exactly chance-level, negative = worse than chance. The Landis–Koch reading bands: 0.41–0.60 moderate, **0.61–0.80 substantial**, 0.81+ almost perfect. Our rule: claim "substantial" only if the number AND its confidence interval sit in the band. Otherwise say "moderate, directional" and keep your credibility.
'''),
    code(BOOT + '''
import numpy as np
rng = np.random.default_rng(7)

def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    po = (a == b).mean()
    pe = (a.mean() * b.mean()) + ((1 - a.mean()) * (1 - b.mean()))
    return (po - pe) / (1 - pe)

n = 50
human = rng.integers(0, 2, n)
judge = np.where(rng.random(n) < 0.85, human, 1 - human)   # judge copies human, flips 15%
print(f"raw agreement: {(human == judge).mean():.2f}   kappa: {kappa(human, judge):.2f}")
'''),
    md('''
**PREDICT before the next cell:** keep the SAME 85% copy-rate, but make the labels imbalanced (90% of calls succeed). Raw agreement stays ~0.85 — what happens to kappa, and why?
'''),
    code('''
human_skew = (rng.random(n) < 0.9).astype(int)
judge_skew = np.where(rng.random(n) < 0.85, human_skew, 1 - human_skew)
print(f"raw agreement: {(human_skew == judge_skew).mean():.2f}   kappa: {kappa(human_skew, judge_skew):.2f}")
print("\\nsame raw agreement, weaker kappa - chance agreement is enormous when one class dominates.")
print("This is the prevalence problem. Knowing it = instant credibility with anyone who does evals.")
'''),
    md('''
## Error bars by brute force: the bootstrap
50 items is small. A single kappa could be luck. The bootstrap: resample your 50 (with replacement) 1000 times, recompute kappa each time, take the 2.5th and 97.5th percentiles → a 95% CI without any distribution math. You have done this for benchmark variance; same tool, new metric.
'''),
    code('''
import matplotlib.pyplot as plt
ks = []
for _ in range(1000):
    idx = rng.integers(0, n, n)
    ks.append(kappa(human[idx], judge[idx]))
lo, hi = np.percentile(ks, [2.5, 97.5])
print(f"kappa = {kappa(human, judge):.2f}   95% CI [{lo:.2f}, {hi:.2f}]")
plt.figure(figsize=(7, 2.4)); plt.hist(ks, bins=40, color="#1D9E75")
plt.axvline(lo, color="#D85A30"); plt.axvline(hi, color="#D85A30")
plt.title("bootstrap distribution of kappa"); plt.show()
print("If 0.61 is inside your CI's lower half, you do NOT get to say 'substantial'. The CI decides, not hope.")
'''),
    md('''
## The confusion matrix and the two disagreements
Agreement summarized is good; disagreement *itemized* is better. The 2×2 confusion matrix (human yes/no × judge yes/no) shows the error structure: does the judge miss failures (dangerous — false confidence) or invent them (annoying — alarm fatigue)? And the single most credibility-building demo move: **show two real cases where the judge was wrong and explain why.** It proves you tested the judge instead of worshipping it. The locked sentence: *"I'm not pretending this judge is magic; I tested where it agrees with humans and where it fails."*
'''),
    code('''
def confusion(a, b):
    m = np.zeros((2, 2), int)
    for x, y in zip(a, b):
        m[x, y] += 1
    return m

m = confusion(human, judge)
print("              judge=0  judge=1")
print(f"human=0       {m[0,0]:>5}  {m[0,1]:>5}")
print(f"human=1       {m[1,0]:>5}  {m[1,1]:>5}")
disagree = np.where(human != judge)[0]
print("\\ndisagreement item indices:", disagree[:10], "<- in Block 7 these become the two slide cases")
'''),
    md('''
## Self-check
1. Why must your labels be blind?
2. A judge agrees with you 88% raw on a 92%-positive dataset. Impressed? What do you compute?
3. Kappa 0.66, CI [0.48, 0.81] — what exactly are you allowed to claim?
4. Which confusion-matrix cell is most dangerous for a *failure-detection* product, and why?

<details><summary>Answers</summary>

1. Seeing the judge's answers first anchors your labels toward it; the agreement becomes self-fulfilling and worthless as evidence.
2. Not yet — chance agreement is ~85% at that prevalence. Compute kappa; it may be barely above zero.
3. "Moderate-to-substantial pilot agreement; the interval does not exclude moderate" — i.e., say "moderate, directional," never "substantial," because the CI dips well below 0.61.
4. human=1(failure present... depending on encoding) judged as fine — missed failures: the product's whole promise is catching them, and a leaky detector quietly restores false confidence.
</details>
'''),
]

# ---------------------------------------------------------------- 05
NBS["05_dpo_improvement_data.ipynb"] = [
    md('''
# 05 — DPO and improvement data: from "caught it" to "trained on it"

## The training ladder, from zero
How a chat/voice model comes to behave:
1. **Pretraining** — next-token prediction over the internet. Capability, no manners.
2. **SFT** (supervised fine-tuning) — show it curated example conversations; it imitates. Format + style.
3. **Preference tuning** — show it PAIRS: same prompt, a **chosen** response and a **rejected** one; train it to prefer chosen-like behavior. This is where "do not talk over callers" type behavior actually gets installed.

Step 3's classic recipe was **RLHF**: train a separate *reward model* on the pairs, then run reinforcement learning against it. Powerful, notoriously fiddly. **DPO — Direct Preference Optimization (2023)** — collapsed it: a bit of algebra shows you can skip the reward model and update directly on the pairs. Intuition in one line: **raise the model's log-probability of the chosen response relative to the rejected one, while staying anchored to a frozen reference copy so the model does not drift into nonsense** (a beta knob controls the leash). No RL loop, one dataset format, standard tooling.

That dataset format is the punchline of this whole project: **every failure VoiceForge detects can be emitted as one (prompt, chosen, rejected) line.** Evals usually end at a dashboard. Training data is what the dashboard *cannot* do.

## The format (TRL = HuggingFace's training library that eats this directly)
One JSON object per line ("JSONL"):
- `prompt` — conversation up to the failure moment (system + prior turns)
- `rejected` — what the agent ACTUALLY said (we have it; it is in the transcript)
- `chosen` — the corrected turn

## The single-axis rule (our discipline, your ablation instinct)
Chosen and rejected must differ **only on the detected failure axis** — barged in → shorter acknowledging turn; ignored hesitation → wait + clarify; over-demanded → confirm partial + one follow-up. If chosen is also more polite, better formatted, and longer, the gradient cannot tell WHICH improvement it is learning. Same reason you change one variable per ablation run. Clean pairs = clean credit assignment.
'''),
    code(BOOT + '''
import json
swz = json.loads((ROOT / "data" / "normalized" / "swz_MUL0035.json").read_text())
hero = json.loads((ROOT / "data" / "normalized" / "hero_001.json").read_text())
print("a real corpus failure (the table found it): 0:07 on swz_MUL0035, 2,220ms overlap -")
for t in swz["turns"][:3]:
    print(f"  {t['turn_id']} {t['speaker']:>6}: {t['text'][:70]}")
print("\\nPAUSE and look at the speakers. The USER barged in over the AGENT. Would you train")
print("the agent on this? NO - a user barge-in is a signal about the user's experience")
print("(impatience, eagerness), not an agent sin. We mine AGENT-side failures for pairs.")
print("Selecting which failures are trainable is itself a judgment call the pipeline encodes.")
print("\\nThe hero call has the perfect agent-side specimen:")
for t in hero["turns"][1:3]:
    print(f"  {t['turn_id']} {t['speaker']:>6}: {t['text']}")
print("\\nagent sin x2: barged in (timing) AND over-demanded instead of acknowledging (content).")
'''),
    md('''
Now author the pair from the hero call's agent sin. Read each field and ask: could a gradient learn anything EXCEPT "acknowledge the partial answer, ask one follow-up"? That is the test.
'''),
    code('''
pair = {
    "prompt": [
        {"role": "system", "content": "Voice agent for appointment booking. Replies under 2 sentences. Never speak while the caller is mid-answer; acknowledge partial info before asking ONE follow-up."},
        {"role": "user", "content": hero["turns"][1]["text"]},
    ],
    "chosen":   [{"role": "assistant", "content": "Got it - Madhapur, near the metro station. Morning or evening slot work better?"}],
    "rejected": [{"role": "assistant", "content": hero["turns"][2]["text"]}],
}
print(json.dumps(pair, indent=2)[:800])

line = json.dumps(pair)
openai_line = json.dumps({"input": {"messages": pair["prompt"]},
                          "preferred_output": pair["chosen"],
                          "non_preferred_output": pair["rejected"]})
print("\\nTRL jsonl bytes:", len(line), "| OpenAI-format bytes:", len(openai_line))
'''),
    md('''
Two formats, one authored source — the 3-line mapper you just ran is the entire "OpenAI mirror" in Block 5. Provenance fields (`call_id`, `failure_dimension`, `needs_human_review: true`) ride along in our schema so every pair traces back to the exact ms-stamped failure that spawned it. `needs_human_review` defaults true because auto-generated chosen turns are *proposals* — honest pipelines say so.

## Exercise — your turn, second axis
Author a pair for a **latency** failure (agent took 1.6s of dead air, then answered fine). Careful — the failure is not the words, it is the silence. What does "chosen" even mean here? (Hint: think about what a *text* pair CAN and CANNOT teach. The checker prints a discussion.)
'''),
    code('''
my_pair = {
    "prompt": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}],
    "chosen": [{"role": "assistant", "content": "..."}],
    "rejected": [{"role": "assistant", "content": "..."}],
}
assert set(my_pair) == {"prompt", "chosen", "rejected"}
assert my_pair["chosen"] != my_pair["rejected"], "chosen and rejected must differ"
print("structure ok.\\n")
print("Discussion: pure dead-air cannot be fixed by a text preference pair - silence is runtime behavior")
print("(endpointing/config), not token choice. What CAN be taught: filler acknowledgements like a brief")
print("'one moment' before slow lookups, or shorter turns that reduce processing time. This boundary -")
print("which failures are weight-fixable vs config-fixable - is a SENIOR-ENGINEER distinction. Use it in the room.")
'''),
    md('''
## Prompt-level vs weight-level fixes (the moat sentence)
A detected failure can be fixed at three depths: **config** (endpointing ms, interruption thresholds), **prompt** (system-prompt rules — cheap, instant, ceiling-limited), or **weights** (DPO on accumulated pairs — durable, portable, compounding). Tomorrow's A/B block demonstrates the prompt-level loop end-to-end; the DPO queue is the weight-level asset you *own and take with you* — which is the answer when someone says "Leaping AI already closes the loop" (theirs is prompt-level, locked to their platform).

## Self-check
1. Recite the ladder: pretraining / SFT / preference tuning — what does each install?
2. DPO vs RLHF in one sentence each.
3. Why must chosen and rejected differ on exactly one axis?
4. Why does `needs_human_review` default to true?
5. Name a failure that should NOT become a DPO pair, and where its fix lives instead.

<details><summary>Answers</summary>

1. Capability (predict text) / format-and-style imitation from curated demos / preferring better over worse behavior from pairs.
2. RLHF: fit a reward model on pairs then RL against it (two stages, unstable, powerful). DPO: algebraic shortcut that optimizes the policy directly on pairs against a frozen reference (one stage, stable, standard tooling).
3. Credit assignment — multi-axis diffs leave the gradient ambiguous about what is being preferred; single-variable changes, like ablations.
4. The chosen turns are machine-proposed corrections; shipping them as ground truth without human eyes would be silent label noise — and dishonest.
5. Pure latency / dead air (or barge-in *timing* itself) — runtime/config territory: endpointing hold, interruption handling, infra speed. Text pairs teach token choices, not clocks.
</details>
'''),
]

# ---------------------------------------------------------------- 06
NBS["06_the_room_and_pitch.ipynb"] = [
    md('''
# 06 — The room, the competition, and the pitch

## Who is in the room and what they build
- **Bolna** (host, YC F25) — a platform for *running* voice agents: telephony, agent configs, executions, recordings. Their API exposes call logs — which makes them a *data source* for VoiceForge (Block 10 ingests one of their calls if credits land). We are downstream, not competing.
- **Cartesia** (host) — TTS. Flagship **Sonic 3.5: 42 languages, 82ms time-to-first-audio** (their + Artificial-Analysis "#1 naturalness" claim — attribute it as their claim). Their voice could re-voice our hero agent (sponsor-flattering, optional).
- The wider map you should place yourself on:
  - **Test harnesses** (Coval, Hamming, Cekura): simulate calls pre-deploy, tell you *what* failed. One-liner: "test harnesses tell you what failed; VoiceForge mines the same calls for *improvement data* — the DPO pairs they don't produce."
  - **Replay** (Roark): re-runs real calls against new agent versions to *test* you. Ours: "replays to test you; we mine calls to *train* you."
  - **LLM observability** (Langfuse, Braintrust): great plumbing, text-first. Ours: "text-first tools are voice-blind; my preference label IS the voice signal — timing, overlap, repair."
  - **Closed-loop platforms** (Leaping AI): self-improving but platform-locked, prompt-level. Ours: "neutral, and outputs portable weight-level data you own."

## Research you may cite (exact, verified phrasing — never improvise numbers)
- **tau-Voice** (Sierra + Princeton): voice agents retain roughly **30–45% of their text-mode capability** — the single best stat for "voice-native failure is real."
- **VoiceAgentBench** (Krutrim): English + **six Indic languages**, 6,000+ spoken queries — your multilingual-roadmap citation. Preprint.
- **WildASR**: it is the benchmark's name, not the paper title (paper: "Back to Basics: Revisiting ASR in the Age of Voice Agents").
- Rule from the spec: click the link before citing anything beyond these lines.

## The honest-claims card (recite under pressure)
1. Hero call: **constructed and disclosed** — "timestamps from assembly; validity comes from the public-data calibration."
2. Judge: **pilot-calibrated** — kappa + CI + two disagreement cases shown proudly; "substantial" only if number AND CI land 0.61–0.80.
3. Costs: **estimated** — turn counts × public per-unit prices, labeled.
4. A/B: **one scenario replay, not statistical evidence** — the point is the closed-loop *shape*.
5. The two locked lines: "VoiceForge judges the **conversation trace**, not just the transcript." / "Most voice-agent demos stop when the call ends. **VoiceForge starts there.**"

## Conversation playbook
- Opener for Monday's panel crowd (ask, don't pitch): "Deploying voice across languages and regions — what's been the harder bottleneck: latency, turn-taking, accent robustness, task-completion evals, or structured feedback from real calls?"
- "Isn't the demo staged?" → "Yes, disclosed — constructed so you can *hear* the failure; the measurements and calibration run on real public calls I didn't construct."
- "Why not build the agent itself?" → you asked this yourself tonight; the answer you accepted is the one you give: the room already builds agents; nobody owns the layer after the call ends; live agents enter as data sources (Bolna ingest), not as something we rebuild.
'''),
    md('''
## FINAL QUIZ — 12 questions, out loud, no notes
Then go to Claude Code and say **"quiz me"** — it grades these harshly and adds follow-ups. No answers in this notebook; that is deliberate.

1. Walk the relay: caller speaks → agent replies. Name every component and where the milliseconds go.
2. Define FTO. prev.end 30,000 / next.start 29,400 → number, sign, event?
3. Why median + p90, never mean? Give the cache-stall example from your own field.
4. Backchannel vs barge-in — and why the 100ms line?
5. Endpointing: the knife edge. Name both failure modes and the hero call's two sins.
6. Why does the deterministic layer exist at all — why not judge everything with the LLM?
7. The judge contract: four properties, and what each buys.
8. Three judge biases + mitigations.
9. Why blind labels? Why kappa over raw agreement? When may you say "substantial"?
10. The training ladder. Then DPO vs RLHF, one sentence each.
11. The single-axis rule and which failure type should NOT become a pair.
12. Place VoiceForge on the map against Coval/Hamming, Roark, Langfuse, Leaping — one line each — and close with the two locked lines.

When you can hit 10+ of these cold, you are not bluffing anybody — you built the thing AND you can defend its epistemology. That is rarer in those rooms than you think.
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
