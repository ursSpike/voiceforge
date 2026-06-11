#!/usr/bin/env python3
# Builds 28_talking_like_an_engineer.ipynb — VoiceForge University, book 28.
# The ONE atomic concept: the honest lines, drilled, plus competitor positioning — so that under
# a sharp question you reach for a precise true sentence instead of a confident bluff.
# This book is mostly MARKDOWN (it is a language gym), but it keeps the full gym scaffold: PREDICT
# prompts, YOUR TURN learner-owned string-answer cells, BREAK-IT cells that show a bluff then
# dismantle it, checkpoints, the trap, three-level explanation, teach-back, the clean sentence.
# Rerun: .venv/bin/python notebooks/build_28.py
# Gates:  .venv/bin/python notebooks/run_nb.py   notebooks/28_talking_like_an_engineer.ipynb -> EXECUTION OK
#         .venv/bin/python notebooks/audit_nb.py notebooks/28_talking_like_an_engineer.ipynb -> ALL PASS
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
# 28 · Talking like an engineer, not a bluffer

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Recite the **four honest lines** word-for-word and say *why each one is true*:
   - "I do **not** train a model live."
   - "This is **pilot calibration**, not a production agreement claim."
   - "It is **one closed-loop demonstration**, not a fleet result."
   - "I score from the **trace**, not the transcript."
2. Position VoiceForge against five real names in one clean sentence each:
   **Coval / Hamming**, **Roark**, **Langfuse**, **Leaping AI** — without trashing any of them.
3. Answer a **sharp question** with a true sentence in under five seconds, because you drilled it
   here as a string you typed yourself.
4. Catch a **bluff** in your own mouth — the confident-but-unprovable sentence — and trade it for a
   smaller true one.

This book has almost no compute. The "data" is **drills**: short answers you type into string
variables. The skill being trained is *spoken defense*, and the only way to own a sentence is to
produce it, so most cells are markdown and the code cells hold *your* words.
'''))

C.append(md('''
## 2 — Knowledge map (where this book sits)

`27 (provider adapters) → THIS: talking like an engineer → 29 (the demo)`

In **27** you earned a *fact*: provider-neutrality is real because every vendor's payload is
normalized to one `call_log` by an adapter — you can open `pipeline/normalize.py` and point at it.
This book turns every fact you have built across the course into a **sentence you can say under
pressure**. Book **29** is the live demo, where these sentences get spoken to a real room.

Why this book exists, and exists *here*: a hackathon is not lost on the build, it is lost in the
**Q&A**. A judge asks "so you trained an RL model?" and a tired founder, wanting to sound
impressive, says "yeah, basically." That one word is a bluff — it claims something the repo cannot
back — and a sharp judge will pull the thread until it unravels. The cure is not confidence; it is a
**stocked shelf of true sentences** you can reach for faster than you can panic. We stock it now.
'''))

C.append(md('''
## 3 — Baby intuition

Picture two people answering the same hard question on a stage.

**The bluffer** hears "did you train a model?" and reaches for the most impressive-sounding answer:
"Yes, we did RLHF on the agent." It lands for three seconds. Then: "On what hardware? How many
steps? Show me the reward curve." There is no curve. The room watches the answer dissolve.

**The engineer** hears the same question and reaches for the *true* answer, even though it sounds
smaller: "No — I don't train anything live. I built the **eval** that would tell you *whether* a
trained agent got better. Here's the closed loop." It lands for three seconds too — and then it
*keeps* landing, because every follow-up has a cell behind it.

The trick is not being smarter on stage. It is having **decided the true sentence in advance**, so
the pressure has nothing to bend. That pre-deciding is the whole workout of this book.
'''))

C.append(md('''
## 4 — The formal version: the four honest lines

These are the load-bearing claims. Each is phrased as the *smallest true thing*, and each names the
thing it is **NOT**, because a claim's honesty lives in what it refuses to say.

| # | the honest line | what it refuses to claim | why it is true in THIS repo |
|---|---|---|---|
| 1 | "I do **not** train a model live." | no live RLHF / fine-tune / weights moving | there is no training loop in the repo — `pipeline/` only *measures* |
| 2 | "This is **pilot calibration**." | not a shipped production agreement number | the kappa is from a *small pilot* set; book 15 says so out loud |
| 3 | "It is **one closed-loop demonstration**." | not a fleet / many-agents result | one call → signals → judge → score → an A/B decision, shown once |
| 4 | "I score from the **trace**, not the transcript." | not "I read the text and vibe a grade" | timing comes from `start_ms/end_ms`; evidence is `evidence_turn_ids` |

Two words this book leans on:
- **trace** = the *timed* turns (start_ms/end_ms) — has a clock. **transcript** = text only — no clock.
- **bluff** = a sentence that claims more than the repo can show on demand. The opposite of a bluff
  is not silence; it is a *smaller* sentence that is fully backed.
'''))

C.append(md('''
## 5 — Why this exists (the part that wins or loses the room)

Founders think the demo is judged on what was built. It is judged on **what you can defend**. A
modest system defended precisely beats an ambitious system defended with hand-waving — every time a
technical judge is in the room, which at a serious hackathon is every time.

The honest lines also do something selfish: they **shrink your attack surface**. "I trained an
agent" invites ten questions you cannot answer. "I built the eval that scores any agent, and here is
the trace-level evidence" invites questions you *can* — because you spent 27 notebooks building
exactly those answers. Honesty is not humility here; it is **putting the fight on your home turf.**

The next cells start the drill: predict the bluff, then type the true line yourself.
'''))

C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. Recite the four honest lines from memory. For each, name the thing it **refuses** to claim.
2. Define **trace** vs **transcript** in one breath — which one has a clock?
3. What is a **bluff**, in the precise sense this book uses? (Hint: it is about what the repo can
   show *on demand*, not about confidence.)
'''))

C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) thought: a good demo answer sounds impressive and confident.
After Act 1 you should hold: a good demo answer is the **smallest true sentence**, decided in
advance, with a cell behind it. Confidence is what a bluff wears; backing is what an engineer brings.

If that is your sentence now, continue. If not, re-read the four-line table in cell 4.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 1. Write YOUR one-sentence version of why the smallest-true-sentence
# beats the impressive one. Producing the sentence is the workout; reading mine would only feel like it.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real, but it runs
# clean while empty so a fresh notebook passes the execution gate.
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: drill the four honest lines, one at a time

## How a drill works here
For each honest line we do the same three moves, the manual-before-function rhythm of the course
applied to *speech*:
1. **PREDICT** the bluff — the impressive-sounding wrong answer a tired founder would give.
2. **See it dismantled** — one follow-up question that the bluff cannot survive.
3. **YOUR TURN** — you type the *true* line in your own words into a string variable. That typing is
   the rep. A line you only read is a line you will not have on stage.
'''))

# ---- Honest line 1: I do not train live ----
C.append(md('''
## PREDICT — drill 1: "did you train a model?"
A judge asks: **"So did you train the agent? Is this RL?"**
Before scrolling: what is the *bluffy* answer (the impressive one), and what single follow-up
question makes it collapse? Commit both in your head, then lock the bluff in the next cell.
'''))

C.append(code('''
# YOUR TURN - name the bluff before you see it dismantled. Predicting the bluff is how you learn to
# hear it leaving your own mouth on stage. Leave it None to run clean; fill it to lock your guess.
my_predicted_bluff_1 = None   # <- replace None with a string: the impressive-but-unprovable answer

if my_predicted_bluff_1 is None:
    print("fill in my_predicted_bluff_1 (the bluffy answer), then re-run.")
else:
    print("predicted bluff locked:", my_predicted_bluff_1)
'''))

C.append(code('''
# BREAK-IT (guided) - we show the bluff, then the one follow-up that dismantles it. No crash here;
# the 'break' is rhetorical - we break a SENTENCE, not the kernel, and watch it fail under one probe.
bluff_1 = "Yeah, we did RLHF on the agent so it learned to talk better."
probe_1 = "Great - show me the reward curve and the number of training steps."

# Why this dismantles it: the repo has NO training loop. The claim invites a question whose answer
# does not exist in pipeline/. A bluff is exactly a sentence whose follow-up has no cell behind it.
print("BLUFF :", bluff_1)
print("PROBE :", probe_1)
print("RESULT: the bluff dies here - there is no curve, because nothing was trained.")
'''))

C.append(md('''
## The honest line 1 (read, then you write your own)
> **"I don't train a model live. I built the *eval* — the thing that would tell you whether a
> trained agent actually got better. Here is the closed loop: signal → judge → score → A/B."**

It sounds smaller than "we did RLHF." It is also unkillable, because every clause points at a file.
'''))

C.append(code('''
# YOUR TURN - type honest line 1 IN YOUR OWN WORDS. Not a copy of mine - yours, the way you'd actually
# say it. The gate checks length only; the truth is on you. Runs clean while empty.
my_honest_line_no_training = ""   # <- e.g. "I don't train anything; I built the eval that scores agents."

if len(my_honest_line_no_training.strip()) < 20:
    print("write your 'no live training' line above (20+ chars), then re-run.")
else:
    print("LINE 1 LOCKED:", my_honest_line_no_training)
'''))

# ---- Honest line 2: pilot calibration ----
C.append(md('''
## PREDICT — drill 2: "what's your agreement number?"
A judge asks: **"You said the judge agrees with humans — what's the number, and is it production-
grade?"** What is the bluff (the over-claim), and what follow-up kills it? Commit, then lock below.
'''))

C.append(code('''
# YOUR TURN - lock the over-claim bluff for the agreement question before seeing it dismantled.
my_predicted_bluff_2 = None   # <- a string: the version that over-claims the kappa

if my_predicted_bluff_2 is None:
    print("fill in my_predicted_bluff_2, then re-run.")
else:
    print("predicted bluff locked:", my_predicted_bluff_2)
'''))

C.append(code('''
# BREAK-IT (guided) - the agreement over-claim, dismantled by a sample-size probe.
bluff_2 = "Our judge has 0.8 kappa with humans, so it's production-validated."
probe_2 = "On how many labeled calls? Who labeled them? What's the confidence interval?"

# Why it dies: kappa from a tiny PILOT set is fragile - a handful of items moves it a lot (book 14-15).
# Calling a pilot number 'production-validated' claims a stability the sample size cannot support.
print("BLUFF :", bluff_2)
print("PROBE :", probe_2)
print("RESULT: 'production-validated' over-claims a small pilot - the honest word is 'calibration'.")
'''))

C.append(md('''
## The honest line 2 (read, then write your own)
> **"This is *pilot calibration*, not a production agreement claim. On a small labeled set the judge
> agrees with humans on the easy dimensions and *disagrees* on the hard ones — and I can show you
> exactly where it disagrees."**

The strength here is the second half: volunteering where it *fails* is what makes the first half
believable. (This is book 12 and 15 made speakable.)
'''))

C.append(code('''
# YOUR TURN - type honest line 2 in your own words. Include the 'and here's where it disagrees' move,
# because volunteering the failure is what makes the claim credible.
my_honest_line_pilot = ""   # <- your 'pilot calibration, not production' sentence

if len(my_honest_line_pilot.strip()) < 20:
    print("write your 'pilot calibration' line above (20+ chars), then re-run.")
else:
    print("LINE 2 LOCKED:", my_honest_line_pilot)
'''))

# ---- Honest line 3: one closed-loop demo ----
C.append(md('''
## PREDICT — drill 3: "does this work at scale?"
A judge asks: **"Cool — so this runs across all your agents in production?"**
What is the scale bluff, and what follow-up exposes it? Commit, then lock below.
'''))

C.append(code('''
# YOUR TURN - lock the scale bluff before the dismantle.
my_predicted_bluff_3 = None   # <- a string: the 'it runs on everything' over-claim

if my_predicted_bluff_3 is None:
    print("fill in my_predicted_bluff_3, then re-run.")
else:
    print("predicted bluff locked:", my_predicted_bluff_3)
'''))

C.append(code('''
# BREAK-IT (guided) - the scale bluff, dismantled by a 'show me the fleet' probe.
bluff_3 = "Yeah, it's running across our whole fleet of agents in prod right now."
probe_3 = "Show me the dashboard with N agents and the rollout history."

# Why it dies: what EXISTS is one closed loop on the hero call, shown once. Claiming a live fleet
# invites a dashboard that is not there. Smaller-and-true ('one closed-loop demonstration') survives.
print("BLUFF :", bluff_3)
print("PROBE :", probe_3)
print("RESULT: there is no fleet dashboard - the true unit is ONE closed-loop demonstration.")
'''))

C.append(md('''
## The honest line 3 (read, then write your own)
> **"What I'm showing is *one closed-loop demonstration*: one real call goes through signals → judge
> → score → an A/B decision, end to end. The loop is the proof of concept; scaling it is the next
> step, not a claim I'm making today."**

Naming the unit ("one closed-loop demonstration") pre-empts the scale question instead of dodging it.
'''))

C.append(code('''
# YOUR TURN - type honest line 3 in your own words. Name the UNIT ('one closed-loop demonstration')
# so the scale question is answered before it is asked.
my_honest_line_closed_loop = ""   # <- your 'one closed-loop demonstration' sentence

if len(my_honest_line_closed_loop.strip()) < 20:
    print("write your 'closed-loop demonstration' line above (20+ chars), then re-run.")
else:
    print("LINE 3 LOCKED:", my_honest_line_closed_loop)
'''))

# ---- Honest line 4: trace not transcript ----
C.append(md('''
## PREDICT — drill 4: "how is this better than reading the transcript?"
A judge asks: **"An LLM could just read the transcript and grade it. What do you add?"**
What is the bluff, and what follow-up exposes it? Commit, then lock below.
'''))

C.append(code('''
# YOUR TURN - lock the 'we just use a smarter LLM' bluff before the dismantle.
my_predicted_bluff_4 = None   # <- a string: the answer that has no real differentiator

if my_predicted_bluff_4 is None:
    print("fill in my_predicted_bluff_4, then re-run.")
else:
    print("predicted bluff locked:", my_predicted_bluff_4)
'''))

C.append(code('''
# BREAK-IT (guided) - the 'just a smarter prompt' bluff, dismantled by 'what can a transcript NOT show'.
bluff_4 = "We just use a really good prompt so the LLM grades the transcript well."
probe_4 = "A transcript has no clock - how do you catch an 800ms barge-in or a 1620ms stall?"

# Why it dies: text alone cannot measure TIME. The differentiator is the TRACE (start_ms/end_ms) +
# evidence_turn_ids, which is deterministic and replayable - a smarter prompt never gets you there.
print("BLUFF :", bluff_4)
print("PROBE :", probe_4)
print("RESULT: a transcript has no clock; the trace does - that's the differentiator a prompt can't fake.")
'''))

C.append(md('''
## The honest line 4 (read, then write your own)
> **"I score from the *trace*, not the transcript. Text has no clock — it can't see the 800 ms
> barge-in at 0:18 or the 1,620 ms stall at 0:53. My signals are deterministic from `start_ms`/
> `end_ms`, and every flag carries `evidence_turn_ids` you can replay. A smarter prompt can't add a
> clock that the input never had."**

This is the line that turns book 04 (timing) into a one-breath competitive moat.
'''))

C.append(code('''
# YOUR TURN - type honest line 4 in your own words. Make the 'text has no clock' point, because that
# is the part a transcript-grading competitor structurally cannot match.
my_honest_line_trace = ""   # <- your 'trace not transcript' sentence

if len(my_honest_line_trace.strip()) < 20:
    print("write your 'trace not transcript' line above (20+ chars), then re-run.")
else:
    print("LINE 4 LOCKED:", my_honest_line_trace)
'''))

C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. For each of the four bluffs, recite the **one probe** that dismantles it.
2. Which honest line gets its strength from *volunteering a failure*? (Hint: the agreement one.)
3. Why does "a transcript has no clock" beat any "smarter prompt" claim, structurally — not just
   today?
'''))

C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: the four honest lines were items on a list you'd read. After Act 2 you have *typed each one
in your own words*, predicted the bluff it replaces, and seen the single probe that kills each bluff.
You now own four reps, not four facts — and a rep is what survives stage adrenaline.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 2. One sentence on which honest line you're least solid on yet.
# Naming the weak one is how you know which to drill again before the demo.
clean_sentence_act_2 = ""   # your Act-2 one-liner (which line needs another rep, and why)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS (competitors + traps)
C.append(md('''
# Act 3 — Stress: competitor one-liners, the trash-talk trap, and sharp-question practice

## Why competitor positioning is a *defense* skill, not marketing
A judge who knows the space will ask: **"How is this different from Coval?"** If you have never heard
the name, you look like you built in a vacuum. If you trash them, you look insecure. The win is a
**neutral, accurate one-liner** that names what *they* do well and where *you* sit relative to it.
You are not competing on the slide; you are proving you understand the landscape.
'''))

C.append(md('''
## The five names, one honest line each (the landscape, said fairly)

These are real products in or near voice-agent evaluation. Lines are positioning, not put-downs —
each names their strength first.

| name | what they do (fairly) | your one-line position |
|---|---|---|
| **Coval / Hamming** | simulation + eval platforms for voice/AI agents — run many simulated calls, score them | "They're the mature platform play; I'm a *focused, transparent* eval you can read end-to-end — trace-level signals, no black box." |
| **Roark** | call analytics / monitoring for voice agents — observability over real calls | "Roark watches production; I *calibrate the judge against humans first*, so the scores you watch are ones you've checked." |
| **Langfuse** | open-source LLM observability / tracing / evals — general-purpose | "Langfuse traces any LLM app; mine is *voice-specific* — FTO, barge-in, latency — the timing signals a general tracer doesn't model." |
| **Leaping AI** | AI voice agents + self-improving / eval loops | "They build the agent *and* the loop; I'm agent-agnostic — my eval scores *anyone's* agent because every vendor normalizes to one schema (book 27)." |

The shape of every line: **their real strength → my specific, narrower, provable edge.** Never
"they're bad"; always "here's the axis where I'm sharp."
'''))

C.append(md('''
## PREDICT — the positioning shape
Before the next cell: across all four competitor lines, what is the *repeated structure*? (If you
can name the template, you can generate a fair line for a competitor you've never heard of, live.)
'''))

C.append(code('''
# We store the four competitor lines as data so the SHAPE is inspectable - positioning is a template,
# not four memorized sentences. Reading the template off the data is the lesson.
competitor_lines = [
    {"name": "Coval/Hamming", "their_strength": "mature simulation+eval platform",
     "my_edge": "focused, transparent, trace-level eval you can read end-to-end"},
    {"name": "Roark",         "their_strength": "production call analytics/monitoring",
     "my_edge": "judge calibrated against humans before you trust the scores"},
    {"name": "Langfuse",      "their_strength": "general-purpose LLM observability",
     "my_edge": "voice-specific timing signals (FTO, barge-in, latency)"},
    {"name": "Leaping AI",    "their_strength": "builds the agent and the loop",
     "my_edge": "agent-agnostic - scores anyone's agent via one normalized schema"},
]
# Print as 'strength -> edge' so the repeated template is visible on every row.
for c in competitor_lines:
    print(f"{c['name']:<15} | THEIRS: {c['their_strength']:<38} | MINE: {c['my_edge']}")
'''))

C.append(md('''
## OBSERVE + EXPLAIN
Every row is **their strength → my narrower-but-provable edge**. Say the template in one sentence.
That template is the reusable skill: hand it a new competitor name and a fair guess at their
strength, and you can produce a clean, non-defensive line on the spot.
'''))

C.append(code('''
# YOUR TURN - write YOUR one-liner for ONE competitor, in your own voice, using the template.
# Pick whichever name you'd most likely be asked about. Names their strength, then your edge.
my_competitor_line = ""   # <- e.g. "Langfuse traces any LLM; mine models voice timing they don't."

if len(my_competitor_line.strip()) < 25:
    print("write one competitor positioning line above (25+ chars), then re-run.")
else:
    print("COMPETITOR LINE LOCKED:", my_competitor_line)
'''))

C.append(md('''
## WRONG-INTUITION TRAP — "the way to win a comparison is to show why the competitor is bad"

**The wrong belief:** "If a judge brings up Coval, I should explain why Coval is worse than us."

The next cell shows that exact move and then dismantles it. Run it, and try to feel *why* trashing a
competitor loses the room before you read the reveal.
'''))

C.append(code('''
# BREAK-IT (guided) - the trash-talk answer, then the probe that turns it against the speaker.
# Again a rhetorical break: we show a confident sentence and watch ONE follow-up make it backfire.
trash_talk = "Coval is bloated and slow and honestly their eval isn't even rigorous."
probe = "Have you used Coval? Which of their features did you benchmark to say that?"

# Why it backfires: the speaker almost certainly hasn't benchmarked Coval, so the put-down is itself
# an unprovable claim - a BLUFF aimed at someone else. It signals insecurity and invites an audit
# the speaker can't pass. The judge now trusts the speaker LESS, not more.
print("TRASH :", trash_talk)
print("PROBE :", probe)
print("RESULT: the put-down is itself a bluff - now the JUDGE doubts you, and Coval looks unbothered.")
'''))

C.append(md('''
## The reveal — fair positioning is the stronger move
Trashing a competitor is a bluff pointed sideways: it claims you've evaluated them when you haven't,
and it tells the room you feel threatened. **Naming their real strength and then your specific edge**
does the opposite — it signals you understand the space *and* you're secure enough to be generous.
A judge trusts the person who can praise a rival and still draw a clean line to their own edge. The
honest-line discipline from Act 2 applies to competitors too: say the *smallest true thing*, and let
the narrower-but-provable edge do the work.
'''))

C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why does trashing a competitor weaken YOUR position?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))

C.append(md('''
## CHECKPOINT 3 (out loud)
1. State the competitor-positioning template (strength → edge) and apply it live to a name not in
   the table (pick any voice-AI company you know).
2. Why is trashing a competitor a *bluff*, in the precise sense from Act 1?
3. Coval/Hamming, Roark, Langfuse, Leaping AI: name each one's real strength in four words or fewer.
'''))

C.append(md('''
## Sharp-question practice — the part that actually gets you on stage
Three sharp questions follow, the kind a technical judge fires when they smell hand-waving. For each:
**PREDICT** your gut answer, then type your *true, drilled* answer into a string. The model answers
are below each — but type yours first, because the rep is the point. An answer you read is one you
won't have when the adrenaline hits.
'''))

C.append(md('''
## PREDICT — sharp question A
**"Isn't your LLM judge just as biased as the agent it's grading? Garbage in, garbage out."**
What's your gut answer? Then type your true one below.
'''))

C.append(code('''
# YOUR TURN - your true answer to sharp question A (judge bias). Runs clean while empty.
# my honest answer should mention: I CALIBRATED the judge against human labels and report kappa,
# AND I show where it disagrees - bias isn't denied, it's measured (books 12-15).
my_answer_judge_bias = ""   # <- type your answer

if len(my_answer_judge_bias.strip()) < 20:
    print("write your judge-bias answer above (20+ chars), then re-run.")
else:
    print("ANSWER A LOCKED:", my_answer_judge_bias)
'''))

C.append(md('''
## Model answer A (read only after writing yours)
> "It could be — which is exactly why I don't *trust* it blind. I calibrate it against human labels
> and report Cohen's kappa, and I show you the dimensions where it *disagrees* with humans. Bias
> isn't something I deny; it's something I *measured*. That's the difference between a judge and a
> vibe."
'''))

C.append(md('''
## PREDICT — sharp question B
**"You only showed one call. How do I know this isn't cherry-picked?"**
Gut answer first, then type your true one.
'''))

C.append(code('''
# YOUR TURN - your true answer to sharp question B (cherry-picking / n=1).
# honest answer should: ADMIT it's one demonstration (honest line 3), point at the deterministic
# signals (same input -> same number, no cherry-picking the math), and name the next step (more calls).
my_answer_cherry_pick = ""   # <- type your answer

if len(my_answer_cherry_pick.strip()) < 20:
    print("write your cherry-pick answer above (20+ chars), then re-run.")
else:
    print("ANSWER B LOCKED:", my_answer_cherry_pick)
'''))

C.append(md('''
## Model answer B (read only after writing yours)
> "It's one closed-loop *demonstration*, and I'm calling it that on purpose — I'm not claiming a
> fleet result. But the timing signals are *deterministic*: same trace in, same milliseconds out,
> nothing to cherry-pick in the math. The honest next step is running the loop across the normalized
> pool of calls (book 27) — and that's a data question, not a method question."
'''))

C.append(md('''
## PREDICT — sharp question C (the closer)
**"Three sentences: what did you actually build?"**
This is the defense question that decides whether they remember you. Gut answer, then type your true
three-sentence version.
'''))

C.append(code('''
# YOUR TURN - your true three-sentence 'what did you build' answer. This is THE one to over-rehearse.
# A strong version threads: trace-level signals -> calibrated judge -> closed A/B loop, all honest.
my_three_sentences = ""   # <- type your 3-sentence answer

if len(my_three_sentences.strip()) < 40:
    print("write your 3-sentence summary above (40+ chars), then re-run.")
else:
    print("CLOSER LOCKED:", my_three_sentences)
'''))

C.append(md('''
## Model answer C (read only after writing yours)
> "I built a voice-agent eval that scores from the *trace*, not the transcript — deterministic
> timing signals like barge-in and latency, each tied to the exact second of evidence. I calibrated
> the LLM judge against human labels so the scores are checked, and I'm honest about where it still
> disagrees. Then I closed the loop: signal → judge → score → an A/B decision, shown end-to-end on
> one real call."
'''))

C.append(md('''
## CHECKPOINT 4 (out loud, no scrolling)
1. Answer sharp question A (judge bias) in one breath, hitting the word **calibrated**.
2. Answer sharp question B (cherry-picking) hitting both **deterministic** and **one demonstration**.
3. Deliver your three-sentence "what did you build" — and check: did any sentence claim something the
   repo can't show on demand? If yes, that sentence is a bluff; shrink it.
'''))

C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: competitors were names to fear and tough questions were ambushes. After Act 3: you have a
*template* for fair positioning (strength → edge), you know trashing a rival is a sideways bluff that
costs you the room, and you've typed your own true answers to the three sharpest questions. The Q&A
is now home turf, not an ambush.
'''))

C.append(code('''
# YOUR TURN - learning log, Act 3. One sentence: which sharp question still scares you, and what cell
# in the course is the answer behind it? Naming the file is how a scary question becomes a backed one.
clean_sentence_act_3 = ""   # your Act-3 one-liner

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where these lines live, three rooms, and the teach-back

## Where these sentences are backed (real files, so every line has a cell)
None of the honest lines are slogans — each points at something on disk you can open mid-answer:

| honest line | the file/fact behind it |
|---|---|
| "I don't train live" | there is **no** training loop in `pipeline/` — it only measures |
| "trace, not transcript" | `pipeline/signals.py` → `turn_metrics()` reads `start_ms`/`end_ms` |
| "evidence, not vibes" | `analyze()` emits `evidence_turn_ids`; flags point at exact turns |
| "pilot calibration" | the kappa is a small-set pilot number (book 15), reported as such |
| "agent-agnostic / neutral" | `pipeline/normalize.py` + one `call_log` schema (book 27) |
| "thresholds are product choices" | `rubric.yaml` — the knobs are one editable file (book 21) |

This is the difference between a pitch and a defense: a pitch *asserts*; a defense *points*. When you
say "trace, not transcript," your hand should already be moving toward `signals.py`.
'''))

C.append(md('''
## The same idea, three rooms (beginner · engineer · founder)

- **To a beginner:** "I practice saying the *true* small thing instead of the impressive big thing,
  because the true thing can't be knocked over."
- **To an engineer:** "Every claim I make in Q&A is backed by a file I can open — deterministic
  signals from the trace, a judge calibrated against human labels with kappa reported honestly, one
  normalized schema for provider-neutrality. I name the unit ('one closed-loop demonstration') so the
  scale question is answered before it's asked, and I volunteer where the judge disagrees."
- **To a founder:** "I win the Q&A by shrinking my attack surface: I claim only what I can show on
  demand, I position fairly against Coval, Roark, Langfuse, and Leaping AI instead of trashing them,
  and I let the narrower-but-provable edge do the selling. Honesty here isn't modesty — it's strategy."
'''))

C.append(md('''
## PREDICT — your own weakest line
Across everything you typed today, which of YOUR locked sentences would crack first under a
relentless judge? Predict it, then store it in the next cell — that's the one to drill before book 29.
'''))

C.append(code('''
# YOUR TURN - name your single weakest line and the one probe you fear against it. Storing your
# weakest point is how you walk into the demo having already found it, instead of the judge finding it.
my_weakest_line = ""      # which of your answers is most likely to crack
my_feared_probe = ""      # the follow-up question you'd least want to hear

if len(my_weakest_line.strip()) < 10 or len(my_feared_probe.strip()) < 10:
    print("write BOTH your weakest line and the feared probe above, then re-run.")
else:
    print("WEAKEST:", my_weakest_line)
    print("FEARED PROBE:", my_feared_probe)
'''))

C.append(md('''
## Defense questions (×3 — try first, then open)

**1. "Aren't you just being modest? Why not claim the impressive version and hope they don't probe?"**
<details><summary>answer</summary>Because a serious judge always probes, and the impressive version
has no cell behind it — the bluff dies on the first follow-up and takes my credibility with it. The
smaller true sentence survives every follow-up because each clause points at a file. Honesty isn't
modesty; it's putting the fight on my home turf.</details>

**2. "If you praise your competitors, won't the judges just go use the competitor?"**
<details><summary>answer</summary>No — naming their strength fairly proves I understand the landscape,
and then the narrower-but-provable edge (voice-specific trace signals, a human-calibrated judge) is
what they remember. Trashing them is a sideways bluff that makes me look insecure and makes them look
unbothered. Generosity plus a sharp edge beats insecurity every time.</details>

**3. "What's the one sentence that survives any follow-up question a judge can ask?"**
<details><summary>answer</summary>"I score voice agents from the trace, not the transcript — timing
signals tied to the exact second of evidence — and I calibrated the judge against humans so I can
show you where it agrees and where it fails." Every clause has a file behind it, so every follow-up
has an answer.</details>
'''))

C.append(md('''
## CHECKPOINT 5 (out loud — the bluff self-audit)
Go back through the locked answers you typed today. For each one, ask the only question that matters:
1. **Can I show a file on demand that backs this clause?** If not, it is a bluff — shrink it now.
2. Did any answer say "we trained / it's in prod / it's production-validated"? Those are the three
   classic over-claims — replace each with its honest line from Act 2.
3. Could you say your three-sentence closer right now, cold, with your hand already moving toward
   `pipeline/signals.py`? If the hand doesn't move, the sentence isn't backed yet.
'''))

C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now own the whole defense posture: four honest lines each backed by a real file, a fair
template for positioning against Coval/Hamming, Roark, Langfuse, and Leaping AI, drilled answers to
the three sharpest questions, and your own named weakest point. The Q&A is no longer where the demo
dies — it's where you've already done the reps. Book 29 just turns the lights on.
'''))

C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The four honest lines, and the thing each one *refuses* to claim.
2. The competitor template (strength → edge), applied to Coval, Roark, Langfuse, and Leaping AI.
3. Why trashing a competitor is a bluff that loses the room.
4. Your three-sentence "what did you build" — with zero clauses the repo can't show.
5. Your own weakest line, and the file that backs the answer behind it.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))

C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (defense posture / lines backed by files)
my_clean_sentence = ""      # the sentence you'd actually say in a room about how you talk on stage

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))

C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"I tested where the judge agrees with humans — and where it fails."**

That single sentence is the whole posture of this book: it claims something real (calibration), it
volunteers the failure (where it disagrees), and every word has a file behind it. No bluff survives
contact with a judge; this sentence thrives on it. If yours captures that in your own words, this
book did its job.
'''))

C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "28_talking_like_an_engineer.ipynb"   # <- this notebook's filename
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

**28 done** (pending your teach-back) → **29 · The demo** — you now hold a stocked shelf of true
sentences and fair competitor lines. Book 29 turns the lights on: the live closed-loop walkthrough,
where every one of these drilled answers gets spoken to a real room, on the clock.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "28_talking_like_an_engineer.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
