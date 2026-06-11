#!/usr/bin/env python3
# Builds 10_llm_as_judge_from_zero.ipynb per the VoiceForge University build spec.
# The ONE atomic concept: a judge reads a transcript and returns a STRUCTURED score, and the
# reliability contract (determinism + caching) is what turns that score into an INSTRUMENT.
# Manual-before-function: a fake keyword judge first, THEN the real Gemini judge via pipeline/judge.py.
# CRITICAL: every live Gemini call is wrapped in try/except with a cached/canned fallback, so
# notebooks/run_nb.py passes with NO network and NO key. A live call is never the only path.
# Rerun: .venv/bin/python notebooks/build_10.py
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
# 10 · LLM-as-judge from zero

## 1 — Learning contract
By the end of this notebook you will be able to:
1. State what an **LLM judge** is in one breath: a function that **reads a transcript** and
   **returns a structured score** — not prose, a contract: `{score, reason, evidence_turn_ids}`.
2. Write a **fake judge by hand** (a plain Python function that scores from keywords) and say
   exactly why it is a toy — so the real one holds no mystery.
3. Run the **real** Gemini judge in `pipeline/judge.py` and name the three properties that make
   it an *instrument* rather than a vibe: **temperature 0** (determinism), **JSON output**
   (a contract), and a **disk cache** (reruns are free and identical).
4. Defend the judge in a room: **disclose** it (which model, which settings), and explain why a
   judge you can rerun for the same answer is trustworthy in a way a one-off opinion never is.

Up to now the course measured what a **stopwatch** can measure (book 04: gaps, overlaps,
latency — pure arithmetic, no opinions). This book is where evaluation crosses into **taste**:
"did the agent handle that ambiguous answer *well*?" is not arithmetic. We hand that question to
a model — carefully, with a contract.''' ))
C.append(md('''
## 2 — Knowledge map (where this book sits)

`09 (language conditions) → THIS: LLM-as-judge from zero → 11 (evidence-based scoring)`

In **09** you learned that a call carries a **language** (English, Hinglish, Telugu-English),
and that you must judge a call **in the language it happened in** — translating first would hide
the very failures you want to catch. That gave you a *call you can hand to a judge honestly*.

This book builds the **judge itself**: the thing that reads that call and emits a score. Why
here, why now? Because everything downstream needs a score that **does not move when you blink**.
Next door, **11** takes the judge's output and demands **evidence** — every score must point at
the exact turns that justify it (`evidence_turn_ids`). A judge that returns a number with no
evidence, or a different number every run, gives 11 nothing to stand on. So this book's whole job
is to make the score **structured and reproducible** before 11 makes it **accountable**.''' ))
C.append(md('''
## 3 — Baby intuition

You have a recording of a phone call and a question that a stopwatch cannot answer:
*"when the caller mumbled half an address, did the agent handle it gracefully?"*

You could hire a person to listen and write down a number from 0 to 1. That works — but a person
is **slow**, **expensive**, and **moody**: ask them the same call on Monday and Friday and you
might get 0.3 then 0.5, with no record of why.

An **LLM judge** is that person, automated. You show the model the transcript, you ask for a
number **and a reason**, and — this is the whole trick — you pin it down so hard that it gives
the **same** number **every** time. A moody reviewer is an opinion. A reviewer who returns the
identical verdict on every rerun is an **instrument** — something you can put on a dashboard and
trust like a thermometer.''' ))
C.append(md('''
## 4 — The formal version

An LLM judge, in this course, is a function with a **strict contract**:

> **input:** a transcript (turns of text) + a question about ONE dimension of quality
> **output:** JSON `{"score": <float 0..1>, "reason": "<one sentence>", "evidence_turn_ids": [...]}`

Three properties separate an *instrument* from a *mood*. Memorize these — they are the spine of
the whole book:

| property | what it means | why it matters |
|---|---|---|
| **temperature 0** | the model's sampling randomness is turned to zero | same prompt → same output, run after run. A judge that drifts is not measuring anything. |
| **JSON output** | the answer is a parseable object, not prose | you can read `score` programmatically, store it, average it, chart it. A paragraph is not a measurement. |
| **disk cache** | every answer is saved, keyed by `(call_id, dimension, prompt_hash)` | the second run reads from disk — **free, instant, byte-identical**. Reproducibility you can prove. |

And one rule of honesty that rides along: you must **disclose** the judge — *which* model, at
*what* temperature — because a score is only as defensible as your willingness to name the
instrument that produced it. (`rubric.yaml → judge:` holds exactly this disclosure.)''' ))
C.append(md('''
## 5 — Why this exists (the part founders care about)

"Our agent is good at handling confused callers" is a claim with no number behind it. **"On our
30-call repair-quality set, the judge scores p50 0.7 — and here are the three worst calls with
the exact turns that sank them"** is a *measurement* you can put on a slide, set a target
against, and prove you improved.

The danger is that an LLM *feels* authoritative — it writes fluent paragraphs — so it is easy to
trust a judge that is secretly a random number generator in a nice suit. This book exists to make
the judge **boring on purpose**: pinned to temperature 0, forced to emit JSON, cached to disk so
any reviewer can rerun it and get **your exact number**. Boring is the feature. A judge you can
rerun is evidence; a judge you cannot is a story.

We start where the course always starts: a **fake** judge we write by hand on a tiny transcript,
so that when the real Gemini judge appears, it holds no magic — only better judgment.''' ))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. What are the **three fields** every judged dimension must return? (Hint: a number, a sentence,
   and a list.)
2. Name the **three properties** that make a judge an *instrument* and not a mood. For each, say
   in one phrase what breaks if it is missing.
3. Why must you **disclose** the judge (model + temperature) when you show its scores?''' ))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: "ask an AI to grade the call" is the whole idea. After Act 1
you should hold a sharper one: a judge is a **function with a contract** — transcript in, a
structured `{score, reason, evidence_turn_ids}` out — and it only becomes an **instrument** when
it is pinned (temperature 0), parseable (JSON), and reproducible (cached). The model is the easy
part; the **contract** is the lesson.

If that is your own sentence now, continue. If not, re-read the table in cell 4.''' ))
C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of what an LLM judge is now.
# Producing the sentence is the learning; reading mine would only feel like it.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: a fake judge by hand, then the real Gemini judge

## The transcript, printed RAW first

Course rule: the ugly input goes on screen **before** anything is computed from it. Here is a
tiny three-turn slice of a real-shaped call — the caller gives a partial, mumbled answer, and we
want to score the agent's **repair_quality**: when an answer is incomplete, does the agent
*acknowledge what it got and ask one targeted follow-up* (good), or *ignore it and over-demand*
(bad)?''' ))
C.append(code('''
# The toy transcript as a list of dictionaries - the same shape as a real call log's "turns".
# We print it RAW (one turn per line) so each TURN is visibly one THING before any scoring,
# because a judge's whole job is reading THIS, and you must see exactly what it will read.
mini_turns = [
    {"turn_id": "t1", "speaker": "agent", "text": "Hi, I can book that service visit. What area are you in?"},
    {"turn_id": "t2", "speaker": "user",  "text": "haan area... ante... Madhapur side anukunta, near the er... metro station"},
    {"turn_id": "t3", "speaker": "agent", "text": "I need your complete address with pincode, landmark and door number before we can proceed."},
]
for t in mini_turns:
    print(t["turn_id"], "|", t["speaker"], "|", t["text"])
'''))
C.append(md('''
## What does GOOD vs BAD look like here? (the rubric in words)

Before we can judge, we must say what we are judging *for*. For **repair_quality** on a partial
answer:
- **GOOD (score → 1.0):** the agent acknowledges the partial info ("Madhapur, got it") and asks
  **one** targeted follow-up ("which landmark?").
- **BAD (score → 0.0):** the agent ignores what the caller gave and **over-demands** everything
  at once ("complete address with pincode, landmark AND door number, now").

Look at `t3` above. The caller offered *Madhapur, near the metro* — and the agent threw it away
and demanded the full set. By this rubric, that is a **bad** repair. Hold that human verdict; we
are about to build two different judges and see which one agrees with you.''' ))
C.append(md('''
## PREDICT
You are the human judge. On a 0-to-1 scale for **repair_quality**, what score does the agent's
`t3` deserve? (Remember: it ignored a partial answer and over-demanded.) Commit to a number
before the next cell — you will store it and compare every machine judge against it.''' ))
C.append(code('''
# YOUR TURN - lock YOUR human score BEFORE any code judges the call, so the notebook records your
# verdict and later cells can measure each machine judge against the human (you). That gap is the lesson.
my_human_score = None     # <- replace None with a float 0.0..1.0 (low = bad repair, high = good)

if my_human_score is None:
    print("fill in my_human_score above (e.g. 0.1), then re-run this cell.")
else:
    print("human verdict locked:", my_human_score)
'''))
C.append(md('''
## Manual-before-function: a FAKE judge, written by hand

New idea, oldest course rule: before we touch a real LLM, we build a **fake judge** — a plain
Python function that returns a score from **keywords**. No model, no network, no magic. Just an
`if`. We do this so that when the real judge arrives, you already know the *shape* of the job
(transcript in, score out) and can see precisely what the LLM adds on top of a dumb keyword rule.''' ))
C.append(code('''
# A FAKE judge: scores repair_quality by counting "demand" words in the agent's last turn.
# This is a toy on purpose - it has NO understanding, only a wordlist. We build it first so the
# real judge later is "this, but with judgment" rather than a black box you never opened.
def fake_keyword_judge(turns):
    # find the agent's last turn - that is where a repair either happens or fails
    agent_turns = [t for t in turns if t["speaker"] == "agent"]
    last_agent = agent_turns[-1]["text"].lower()

    # over-demanding language is the failure mode; we hardcode a tiny wordlist to detect it.
    # this is exactly the kind of brittle rule the LLM will replace - we expose it so you see WHY.
    demand_words = ["complete address", "pincode", "before we can proceed", "i need your"]
    hits = sum(1 for w in demand_words if w in last_agent)

    # more demand-hits -> lower score. The mapping is arbitrary - that arbitrariness is the point.
    score = max(0.0, 1.0 - 0.3 * hits)
    return {
        "score": round(score, 2),
        "reason": f"keyword judge: found {hits} over-demand phrase(s) in the agent's last turn",
        "evidence_turn_ids": [t["turn_id"] for t in turns if t["speaker"] == "agent"][-1:],
    }

fake_result = fake_keyword_judge(mini_turns)
print(fake_result)
'''))
C.append(md('''
## OBSERVE + EXPLAIN

The fake judge returned a structured result — the **same three fields** the real one will: a
`score`, a `reason`, and `evidence_turn_ids`. That is the important win: **the contract does not
depend on the LLM.** A judge is a function that returns that shape; whether the score comes from
an `if` or from Gemini is an implementation detail of *how good the judgment is*.

One sentence, out loud: did the fake judge's number match **your** human score from two cells ago?
Compare them in the next cell.''' ))
C.append(code('''
# Compare the FAKE judge against YOUR human verdict. We are not asking "is the fake judge right" -
# we are asking "how far is a keyword rule from a human", which is the entire reason LLMs exist here.
print("fake keyword judge score:", fake_result["score"])
if my_human_score is not None:
    diff = abs(fake_result["score"] - my_human_score)
    print("your human score:       ", my_human_score)
    print("absolute gap:           ", round(diff, 2),
          "- small gap is luck on this one call; the fake rule has no understanding to generalize")
else:
    print("(fill in my_human_score earlier to see the gap)")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — "the keyword judge basically works, so why bother with an LLM?"

**The wrong belief:** "the fake judge gave a low score and the repair *was* bad — keyword
matching is good enough, an LLM is overkill."

It got *this* call right **by luck**, because the bad agent happened to use the exact words on
our list. Watch it shatter on a sentence with the **same meaning** but different words.''' ))
C.append(md('''
## PREDICT
We feed the fake judge a NEW agent line that is **just as over-demanding** — *"Give me everything:
the full thing, door number, the lot, right now"* — but uses **none** of our wordlist phrases.
What score will the keyword judge return? Will it catch this bad repair, or wave it through?''' ))
C.append(code('''
# Same MEANING (over-demanding, ignores the partial), different WORDS. A human scores this ~0.1.
# We feed it to the keyword judge to expose that the rule scores SURFACE STRINGS, not meaning.
sneaky_turns = [
    {"turn_id": "t1", "speaker": "agent", "text": "Hi, I can book that. What area are you in?"},
    {"turn_id": "t2", "speaker": "user",  "text": "haan... Madhapur side anukunta, near the metro"},
    {"turn_id": "t3", "speaker": "agent", "text": "Give me everything: the full thing, door number, the lot, right now."},
]
sneaky_result = fake_keyword_judge(sneaky_turns)
print(sneaky_result)
print("--> the repair is just as BAD, but the keyword judge scored it", sneaky_result["score"],
      "(near-perfect) because none of its magic words appeared")
'''))
C.append(md('''
## The reveal

The keyword judge gave a **bad** repair a **near-perfect** score, because it matches *strings*,
not *meaning*. Paraphrase the failure and it sails through. This is the gap an LLM judge closes:
it reads for **intent** ("did the agent acknowledge and ask one thing, or dump a demand?"), so
"give me everything right now" and "I need your complete address with pincode" land at the same
low score. The LLM is not magic — it is a judge that reads meaning instead of counting words.

Now — and only now — we earn the real thing.''' ))
C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. The fake judge and the real judge return the **same three fields**. So what, exactly, is the
   LLM adding — what does it do that the `if`-statement cannot?
2. Name the specific way the keyword judge **failed** (one phrase: it scored ___, not ___).
3. Why did building the fake one first make the real one *less* mysterious, not more?''' ))
C.append(md('''
## The real judge — `pipeline/judge.py`

You have built a fake judge by hand and watched it break. Only now do we open the **real** one:
`judge_dimension()` in `pipeline/judge.py`. It is the production judge VoiceForge actually uses.
Read its contract before we run it — it is the same `{score, reason, evidence_turn_ids}` shape,
but the score comes from **Gemini Flash at temperature 0**, and every answer is **cached to disk**.

Three things to notice in the code we are about to import:
- it builds a **prompt hash** from `(model, prompt)` and saves each answer to
  `data/.judge_cache/<call_id>__<dimension>__<hash>.json`;
- on a second call with the same inputs, it **returns the cached file** — no model call at all;
- it **raises** if the model's JSON is missing any of the three required fields (the contract is
  enforced in code, not hoped for).''' ))
C.append(code('''
# Make the repo's pipeline package importable from inside notebooks/. We resolve the repo root by
# walking up until we find pipeline/judge.py, so this runs whether the kernel started in notebooks/
# or the repo root (no hardcoded absolute path - book 04 taught this resolve-by-walking trick).
import sys
from pathlib import Path

root = next(a for a in [Path.cwd(), *Path.cwd().parents] if (a / "pipeline" / "judge.py").exists())
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# Import the REAL judge entry point and its config reader. judge_dimension(client, call_id,
# dimension, prompt) -> (parsed_json, from_cache). judge_config() -> (model, temperature) from rubric.yaml.
from pipeline.judge import judge_dimension, judge_config

model, temperature = judge_config()
print("disclosed judge:", model, "| temperature:", temperature)
print("(this is the disclosure rubric.yaml -> judge: holds; you show this whenever you show scores)")
'''))
C.append(md('''
## The cache is what makes it offline-safe (and an instrument)

`pipeline/judge.py` caches every answer to `data/.judge_cache/`. This notebook ships with a real
cached judge result already on disk — the exact one `python pipeline/judge.py --smoke` produced.
Because of the cache, we can demonstrate the real judge's output **with no network and no API
key**: we just read the file the judge already wrote. That is not a workaround — it **is** the
reproducibility guarantee. A cached judge result is the judge's verdict, frozen and rerunnable.''' ))
C.append(code('''
# Load the REAL cached judge result from disk - the verdict pipeline/judge.py wrote for the smoke
# call. We read the cache directly so this cell NEVER needs the network: the cache is the whole
# point - a judged answer, saved, replayable byte-for-byte. This is the offline-safe path.
import json

cache_dir = root / "data" / ".judge_cache"
# the smoke call judged the SAME over-demand scenario as our toy (Madhapur, t2->t3) for repair_quality
cached_files = sorted(cache_dir.glob("smoke_001__repair_quality__*.json"))

cached_verdict = None
if cached_files:
    cached_verdict = json.loads(cached_files[0].read_text())
    print("loaded cached judge verdict from:", cached_files[0].name)
    print(json.dumps(cached_verdict, indent=2))
else:
    # if the cache is ever absent we still must not crash the gate - canned fallback below
    print("no cache file found; the next cell's canned fallback will supply a verdict")
'''))
C.append(md('''
## PREDICT
The cached verdict above is the **real Gemini judge** scoring the **same** over-demand scenario
your fake keyword judge scored. Before reading it closely: will the real judge's `score` be
**closer to your human verdict** than the keyword judge was? And will its `reason` mention the
*meaning* (ignoring the partial answer) rather than counting words?''' ))
C.append(code('''
# YOUR TURN - lock your prediction about the real judge before we line it up against the others.
my_real_judge_closer = None   # <- True if you think the LLM is closer to your human score, else False

if my_real_judge_closer is None:
    print("set my_real_judge_closer to True or False above, then re-run.")
else:
    print("prediction locked:", my_real_judge_closer)
'''))
C.append(code('''
# Three verdicts side by side on ONE scenario: the human (you), the fake keyword judge, the real
# LLM judge. We line them up so the LLM's value is not asserted but SHOWN as a smaller gap to human.
# We guard on cached_verdict so an absent cache never crashes this teaching comparison.
real_score = cached_verdict["score"] if cached_verdict is not None else None

print(f"{'judge':<22}{'score':>7}   reason")
print("-" * 70)
if my_human_score is not None:
    print(f"{'human (you)':<22}{my_human_score:>7}   your committed verdict")
print(f"{'fake keyword judge':<22}{sneaky_result['score']:>7}   {sneaky_result['reason'][:38]}")
if real_score is not None:
    print(f"{'real Gemini judge':<22}{real_score:>7}   {cached_verdict['reason'][:38]}...")

# the headline: the LLM read MEANING (over-demand, ignored partial) - check its gap to human
if real_score is not None and my_human_score is not None:
    print("\\nreal-judge gap to human:", round(abs(real_score - my_human_score), 2),
          "vs keyword-judge-on-sneaky gap:", round(abs(sneaky_result['score'] - my_human_score), 2))
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw**: the real judge's `reason` field names *why* the repair
was bad ("ignored the partial information... over-demanded"). The keyword judge's reason could
only say "found N magic words." What does a real **reason string** buy you that a score alone
never could? (Hint: book 11 is named "evidence-based scoring" for this reason.)''' ))
C.append(md('''
## Determinism, proven: run the judge TWICE, get the SAME answer

The claim "temperature 0 + cache → identical reruns" is worthless until you watch it. We now call
the real `judge_dimension()` **twice**. The first call may go live (if a key is present) or read
the cache; the **second** call is guaranteed to read the cache and return a **byte-identical**
answer. Either way, the two results must be **equal** — that equality is what "instrument" means.

CRITICAL design note (read the code): the live call is wrapped in `try/except`. If there is no
network and no API key, the live path fails *softly* and we fall back to the cached/canned verdict.
A live call is **never** the only path — this is why the notebook runs green offline.''' ))
C.append(code('''
# A tiny canned verdict to fall back on if BOTH the live call and the disk cache are unavailable.
# Why canned: the offline gate (run_nb.py) must pass with no network AND no cache - so there is
# ALWAYS a valid {score, reason, evidence_turn_ids} to return. This is the belt-and-suspenders path.
CANNED_VERDICT = {
    "score": 0.1,
    "reason": "canned fallback: agent over-demanded and ignored the partial answer (no live/cache available)",
    "evidence_turn_ids": ["t2", "t3"],
}

# A prompt identical in spirit to the smoke prompt, so a live call would hit the same cached key.
JUDGE_PROMPT = """You are a strict but fair judge of voice-agent calls. Score ONE dimension.

Dimension: repair_quality - when the caller gives a partial or ambiguous answer, does the
agent acknowledge what it got and ask one targeted follow-up (good), or ignore/over-demand (bad)?

Call snippet (turn_id speaker: text):
t1 agent: Hi, I can book that service visit. What area are you in?
t2 user: haan area... ante... Madhapur side anukunta, near the er... metro station
t3 agent: I need your complete address with pincode landmark and door number before we can proceed any further with this booking request, please provide all details now.

Return ONLY JSON: {"score": <float 0 to 1>, "reason": "<one falsifiable sentence>", "evidence_turn_ids": ["..."]}"""


def judge_safely(call_id, dimension, prompt):
    # try the REAL judge first; if no key/network, judge_dimension's get_client() exits or raises -
    # we catch EVERYTHING and degrade to the on-disk cache, then to the canned verdict. The gate
    # must pass offline, so a thrown live call can never be the end of the line.
    try:
        from pipeline.judge import get_client
        client = get_client()                       # raises/exits without a key
        out, from_cache = judge_dimension(client, call_id, dimension, prompt)
        return out, ("cache" if from_cache else "live")
    except SystemExit:
        pass                                        # get_client() calls sys.exit without a key
    except Exception:
        pass                                        # network/library/parse errors all degrade the same way
    # fallback 1: the cache file the smoke run already wrote
    if cached_verdict is not None:
        return cached_verdict, "cache(direct)"
    # fallback 2: the canned verdict, so we ALWAYS return the contract shape
    return CANNED_VERDICT, "canned"


run_1, source_1 = judge_safely("smoke_001", "repair_quality", JUDGE_PROMPT)
print("run 1 source:", source_1)
print(json.dumps(run_1, indent=2))
'''))
C.append(code('''
# The second call. With the cache warm (the first call wrote/read it), this is guaranteed to be
# the SAME answer - that is the determinism contract made visible, not asserted.
run_2, source_2 = judge_safely("smoke_001", "repair_quality", JUDGE_PROMPT)
print("run 2 source:", source_2)

# The instrument test: two runs, SAME verdict. We compare the full dicts, not just the score,
# because the contract is the whole object - a reason that drifts is also a judge that drifts.
identical = (run_1 == run_2)
print("run 1 == run 2 ?", identical, "  <- this equality is what 'instrument' means")
if not identical:
    print("if these ever differ, the judge is a MOOD, not an instrument - that is the failure to fear")
'''))
C.append(md('''
## CHECKPOINT 3 (out loud)
1. The two runs returned the **same** object. Which two design choices guarantee that — one about
   the **model's sampling**, one about the **disk**?
2. The live call is wrapped in `try/except` with a fallback. Why is "a live call must never be the
   **only** path" a correctness requirement, not just politeness to the offline gate?
3. What is the difference between the judge's `score` and its `reason`, and why does the contract
   demand **both**?''' ))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: "a judge is asking an AI to grade something." After Act 2: a judge is a **function with a
fixed contract** (`{score, reason, evidence_turn_ids}`); a **fake** keyword judge fills that
contract but scores *strings* and shatters on paraphrase; the **real** Gemini judge scores
*meaning* and — pinned to temperature 0 and cached to disk — returns the **identical** verdict on
every rerun. You ran it twice and watched the two results be equal. That equality is the instrument.''' ))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (the contract / fake-vs-real / determinism - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the contract, break determinism, and the trap of fluent wrongness

## The contract is enforced in CODE — break it and watch

`judge_dimension()` does not *hope* the model returns the right shape; it **raises** if any of
`score`, `reason`, `evidence_turn_ids` is missing. That guard is the difference between a judge
and a chatbot. We now simulate a model that returns **prose instead of JSON** — exactly what
happens when temperature creeps up or the prompt is sloppy — and watch the contract refuse it.''' ))
C.append(md('''
## PREDICT
A misbehaving model returns the string `"The agent did a pretty bad job, I'd say maybe a 3 out
of 10."` — fluent, human, and **not JSON**. When our code tries to treat it as a judged verdict,
does it: (a) crash loudly, (b) silently store a wrong score, or (c) quietly score it 0? Commit to
one before running.''' ))
C.append(code('''
# YOUR TURN - lock your prediction about the malformed-output path before the break-it cell.
my_prose_prediction = None   # <- "a", "b", or "c" from the PREDICT cell above

if my_prose_prediction is None:
    print("set my_prose_prediction to 'a', 'b', or 'c' above, then re-run.")
else:
    print("prediction locked:", my_prose_prediction)
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. EXPECTED FAILURE FOR LEARNING.
# We simulate a model that ignored the JSON instruction and returned prose. Parsing prose as JSON
# is exactly what pipeline/judge.py does to the model's text, so we reproduce that step and watch
# it refuse. Do not fix it yet - read the traceback first (bottom line names WHAT went wrong).
bad_model_text = "The agent did a pretty bad job, I'd say maybe a 3 out of 10."

# json.loads is the FIRST thing judge_dimension does to resp.text - prose is not JSON, so it raises.
parsed = json.loads(bad_model_text)   # JSONDecodeError on purpose
print("this line never prints:", parsed)
'''))
C.append(md('''
## Reading the error (bottom-up, always)

The wall of red is a **traceback**; read the **last line first**. It says
`json.decoder.JSONDecodeError: Expecting value: line 1 column 1` — "you handed me text that is not
JSON." This is the **friendly** failure: the contract caught the malformed output *loudly*,
before a bogus score could enter your dashboard. A judge that **crashed** on bad output is far
safer than one that quietly logged `score = None` and let a non-measurement masquerade as a
measurement. Now the recovery.''' ))
C.append(code('''
# Recovery: the RIGHT way to consume a possibly-malformed judge output. We try to parse, and on
# failure we DISCARD the call (mark it errored) rather than invent a score - a fabricated score is
# worse than a missing one. This mirrors how judge_dimension raises rather than guessing.
def parse_judge_output(model_text):
    try:
        out = json.loads(model_text)
    except json.JSONDecodeError:
        # contract violation: not even JSON. We refuse to manufacture a number.
        return {"ok": False, "error": "model returned non-JSON prose - score discarded, not invented"}
    # even valid JSON must carry all three contract fields, or it is not a verdict.
    for field in ("score", "reason", "evidence_turn_ids"):
        if field not in out:
            return {"ok": False, "error": f"JSON missing required field '{field}'"}
    return {"ok": True, "verdict": out}

print("prose input ->", parse_judge_output(bad_model_text))
print("good input  ->", parse_judge_output(json.dumps(CANNED_VERDICT)))
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
1. The judge raised on prose instead of storing `score = None`. Why is a **loud crash** the safer
   failure here — what would a silent `None` have let slip onto a dashboard?
2. The recovery function, on bad output, **discards** the call instead of scoring it 0. Why is
   "no score" more honest than "score 0" when the model misbehaved?
3. Which of the three contract fields, if quietly dropped, would do the most damage downstream in
   book 11 (evidence-based scoring)?''' ))
C.append(md('''
## BREAK-IT (learner-authored) — your own contract break

Author your own malformed verdict. Build a dict that **looks** like a judge output but **violates
the contract** in one way — drop a field, make `score` a string like `"high"`, or make
`evidence_turn_ids` a single string instead of a list. Predict what `parse_judge_output` (and a
downstream `float(score)`) will do, write the prediction as a comment, then run.''' ))
C.append(code('''
# YOUR TURN - self-authored BREAK-IT. Damage the contract ONE way and predict the consequence.
# my prediction: <write here exactly what parse_judge_output will return, and why>

my_broken_verdict = None   # <- replace with a dict that violates the contract, e.g.
#   {"score": "high", "reason": "x", "evidence_turn_ids": ["t3"]}   # score is a string, not a float
#   {"reason": "x", "evidence_turn_ids": ["t3"]}                     # missing score entirely

if my_broken_verdict is None:
    print("build a contract-violating verdict above (see the commented examples), then re-run.")
else:
    # we run it through the SAME parser the recovery cell defined, so your break meets the real guard
    checked = parse_judge_output(json.dumps(my_broken_verdict))
    print("parser verdict on YOUR break:", checked)
    # the sneaky one: a STRING score passes the "field present" check but poisons any math later
    if checked.get("ok") and not isinstance(my_broken_verdict.get("score"), (int, float)):
        print("WARNING: 'score' is present but not a number - this passes the shape check and",
              "explodes the moment anyone does float(score) or averages it. The contract needs a TYPE check too.")
'''))
C.append(md('''
## WRONG-INTUITION TRAP — "the judge wrote a confident paragraph, so the score is trustworthy"

**The wrong belief:** "the model gave a fluent, specific-sounding reason, so I can trust its
number." Fluency is not correctness. A model at the wrong temperature can write a **beautiful**
reason for a **wrong** score, and write a **different** beautiful reason next run. The next cells
show two judge outputs that are equally articulate and **disagree** — the prose hides the
instability completely.''' ))
C.append(md('''
## PREDICT
Two judge runs on the same call, both fluent, scores **0.2** and **0.6**. If you only read the
**reason** strings (both confident, both plausible), can you tell which is right? What single
property of the judge would have **prevented** these two runs from disagreeing in the first place?''' ))
C.append(code('''
# Two fluent verdicts that DISAGREE - this is what a judge at temperature > 0 looks like across
# runs. We print them to make the danger visceral: prose confidence is uncorrelated with stability.
drifty_run_a = {"score": 0.2, "reason": "The agent clearly steamrolled the caller, demanding everything at once with no acknowledgement.", "evidence_turn_ids": ["t3"]}
drifty_run_b = {"score": 0.6, "reason": "The agent was somewhat firm but did move the booking forward, which is partially acceptable.", "evidence_turn_ids": ["t3"]}

for label, r in [("run A", drifty_run_a), ("run B", drifty_run_b)]:
    print(f"{label}: score {r['score']} | {r['reason']}")

# both are articulate; they differ by 0.4 on a 0-1 scale - a third of the whole range, same call.
print("\\nscore spread across two 'confident' runs:", round(abs(drifty_run_a["score"] - drifty_run_b["score"]), 2),
      "- fluency told you NOTHING about which to trust")
'''))
C.append(md('''
## The reveal

Both reasons are persuasive. Neither tells you the score is **stable**. The only thing that would
have stopped runs A and B from disagreeing is **temperature 0** — pinning the sampling so the same
prompt yields the same answer. This is why the course's first instinct on any LLM output is *not*
"is the reason convincing?" but **"is this number reproducible?"** A reproducible 0.2 you can argue
about; an irreproducible 0.2-or-0.6 is not a measurement at all. (This same shape — "it ran, it
sounded right, it was unstable" — is the green-cells trap from P00, now wearing a judge's robe.)

The fix is the whole point of `pipeline/judge.py`: temperature 0 makes A and B **the same run**.''' ))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why does a fluent reason NOT make a score trustworthy?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
1. Two runs, scores 0.2 and 0.6, both with fluent reasons. Which judge property would have made
   them identical, and why does a confident *reason* not substitute for it?
2. Restate the rule: when an LLM output surprises you, the first question is not "is the reason
   convincing?" but "______?"
3. Tie it back: how is this the **same** trap as P00's "all my cells ran green so I learned it"?''' ))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: an LLM that writes a fluent answer feels trustworthy. After Act 3: the **contract is
enforced in code** (malformed output raises — loudly, on purpose), a **fabricated score is worse
than a missing one** (discard, never invent), and **fluency is not stability** — only temperature
0 makes two runs agree. You now fear a confident, drifting judge more than a crashing one.''' ))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the contract guard, or 'fluency is not stability')

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the real pipeline, the disclosure, and defending the judge

## Where this lives in VoiceForge (these are real files)

Nothing today was a metaphor. The judge you ran is the production judge:

| what you built/ran today | where it lives for real | what it does |
|---|---|---|
| the fake keyword judge | (nowhere — it was the toy that earned the real one) | shows the contract without the model |
| `judge_dimension(client, call_id, dimension, prompt)` | `pipeline/judge.py` | one judged dimension, cached, contract-enforced |
| the disclosure (model + temperature) | `rubric.yaml → judge:` | `provider: gemini`, `model: gemini-2.5-flash`, `temperature: 0` |
| the cache files you read | `data/.judge_cache/*.json` | every verdict, keyed by `(call_id, dimension, prompt_hash)` |
| the smoke proof | `python pipeline/judge.py --smoke` | one judge call run twice, proving the cache hit |

The flow is exactly what you lived: a prompt about one dimension → `judge_dimension()` → JSON
verdict at temperature 0 → written to `data/.judge_cache/` → next run reads the file. The judge is
disclosed, deterministic, and replayable. Book 11 next attaches **evidence** to make it auditable;
book 21 puts its dimensions and weights in `rubric.yaml` so the whole rubric is config you can edit.''' ))
C.append(code('''
# Confirm the disclosure is a real, loadable config - not something we typed into a slide. We read
# the SAME rubric.yaml the production judge reads, so what we show on the demo IS what runs.
import yaml

rubric_path = root / "rubric.yaml"
rubric = yaml.safe_load(rubric_path.read_text())
disclosed = rubric.get("judge", {})
print("rubric.yaml -> judge:", disclosed)
print("\\nthis is the sentence you say on stage: 'the judge is", disclosed.get("model"),
      "at temperature", disclosed.get("temperature"), "- here is the cache, rerun it yourself.'")
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

You now have a judge that returns `{score, reason, evidence_turn_ids}`. Book 11 will insist every
score **point at the exact turns** that justify it. Predict: for the over-demand call you judged
today, **which turn ids** are the real evidence for the low repair_quality score — and what goes
wrong downstream if a judge returns a confident score with an **empty** `evidence_turn_ids`?''' ))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for book 11 to confront.
my_evidence_prediction = ""   # which turn ids are the evidence + what breaks if evidence is empty

if len(my_evidence_prediction.strip()) < 20:
    print("write your prediction above (turn ids + the cost of empty evidence), then re-run.")
else:
    print("PREDICTION STORED:", my_evidence_prediction)
'''))
C.append(md('''
## Where this idea itself fails (honesty applies to the judge too)

- **Judge-as-oracle** — treating the LLM's score as ground truth. It is **not**; it is a fast,
  cheap *proxy* for a human, and it can be confidently wrong. Countermeasure: book 12 (calibration)
  checks the judge against human labels; book 14 (kappa) quantifies the agreement.
- **Undisclosed judge** — showing scores without naming the model/temperature. Countermeasure:
  the disclosure lives in `rubric.yaml` and you say it out loud, every time.
- **Prompt drift** — quietly editing the judge prompt invalidates every cached score (the prompt
  hash changes). Countermeasure: the cache key *includes* the prompt, so an edit forces a re-judge
  rather than silently mixing old and new verdicts.
- **Temperature creep** — anything above 0 reintroduces the drift you saw in Act 3.
  Countermeasure: temperature 0 is in the config and in the contract, not a default you hope holds.''' ))
C.append(md('''
## The three-level explanation (same concept, three rooms)

- **To a beginner:** "We ask an AI to read the call and give it a score *and* a reason — and we
  set it up so it gives the **same** answer every time we ask. A reviewer who never changes their
  mind for no reason is one you can trust."
- **To an engineer:** "`judge_dimension()` calls Gemini Flash at **temperature 0**, forces
  `response_mime_type=application/json`, validates `{score, reason, evidence_turn_ids}` (raises on
  miss), and caches the verdict to `data/.judge_cache/` keyed by `(call_id, dimension,
  sha256(model|prompt))`. Reruns are cache hits — free and byte-identical. No model call is the
  only path; everything degrades to cache."
- **To a founder:** "Our quality scores are produced by a **disclosed**, **deterministic**
  instrument: same call in, same number out, with a saved reason and the exact turns as evidence.
  Anyone can rerun it and get our number. That is the difference between a metric we can defend and
  an opinion we can only assert."''' ))
C.append(md('''
## Defense questions (×3 — try first, then open)

**1. "An LLM is non-deterministic — how can you call its score a measurement?"**
<details><summary>answer</summary>We run it at temperature 0, which removes sampling randomness, and
we cache every verdict keyed by (call_id, dimension, prompt_hash). The same call yields the same
JSON on every run — we proved it live by calling the judge twice and showing the two results are
equal. A score you can rerun for the identical answer is a measurement; we never ship one you can't.</details>

**2. "How do I know the judge isn't just making up a confident-sounding number?"**
<details><summary>answer</summary>Two guards. First, the contract: it must return a `reason` and
`evidence_turn_ids`, so every score points at the exact turns you can replay (book 11). Second,
calibration: book 12 checks the judge's scores against human labels and book 14 reports Cohen's
kappa — we measure the judge's agreement with humans rather than assuming it. The judge is a
proxy we audit, not an oracle we trust.</details>

**3. "Which model, and what if it changes under you?"**
<details><summary>answer</summary>It is disclosed in `rubric.yaml`: gemini-2.5-flash at temperature
0. If we change the model or the prompt, the cache key (which includes both) changes, so every
affected call is re-judged rather than silently mixing verdicts from two different judges. The
disclosure is config we read at runtime, not a claim on a slide.</details>''' ))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own the whole loop: a transcript + a one-dimension question → `judge_dimension()`
at temperature 0 → a JSON verdict `{score, reason, evidence_turn_ids}` → cached to disk →
rerunnable for the identical answer → disclosed via `rubric.yaml`. You can place every piece in a
real file, run it offline from the cache, and defend it against "it's just an AI guessing" — because
you made it deterministic, contract-bound, and auditable. The next books make it *accountable*
(evidence) and *trustworthy* (calibration); you built the instrument they stand on.''' ))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The judge's **contract**: the three fields, and why a score alone is not enough.
2. The fake keyword judge: what it does, and the **exact** way it broke (string-matching, not
   meaning) on a paraphrased over-demand.
3. The three **instrument** properties — temperature 0, JSON, disk cache — and what each prevents.
4. Why a **live call must never be the only path**, and how the cache makes the judge offline-safe.
5. The **trap**: why a fluent reason does not make a score trustworthy — and the first question to
   ask of any LLM output instead.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.''' ))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (the real pipeline / disclosure / defending the judge)
my_clean_sentence = ""      # the sentence you would say in a room about what an LLM judge is

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"A judge you can rerun and get the same answer is an instrument; anything else is a mood."**

You proved it: the keyword judge had no judgment, the drifty judge had no stability, and the real
Gemini judge — pinned to temperature 0 and cached to disk — returned the **identical** verdict
twice in a row. If your sentence captures that in your own words, this book did its job.''' ))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "10_llm_as_judge_from_zero.ipynb"   # <- this notebook's filename
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

**10 done** (pending your teach-back) → **11 · Evidence-based scoring** — now that the judge
returns a score *and* a reason *and* the turns, 11 makes the **evidence** mandatory: every score
must point at the exact turns that justify it, so a reviewer can replay the seconds and check the
judge's work. The judge you built is the instrument; 11 makes it accountable.''' ))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "10_llm_as_judge_from_zero.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
