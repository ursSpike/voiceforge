#!/usr/bin/env python3
# Builds 19_rlhf_rlaif_without_mythology.ipynb — VoiceForge University book 19.
# ONE atomic concept: feedback-based alignment in plain words — RLHF (learn from human feedback),
#                     RLAIF (the feedback is AI-generated), the reward-model idea in one breath,
#                     online vs offline — and WHY VoiceForge does not train live: it ships the
#                     dataset layer for safe OFFLINE optimization.
# We do NOT implement RL. We model the SHAPE of feedback-based alignment with tiny toy data, by hand.
# Rerun: .venv/bin/python notebooks/build_19.py
# Style/rhythm/comment-density cloned from build_P00.py and build_05.py (the gold references).
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
# 19 · RLHF / RLAIF without mythology

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Say what **RLHF** is in one breath — *a model learns from human feedback about which answer is
   better* — and what **RLAIF** changes about it (*the feedback is written by an AI judge, not a
   human*). No acronyms left undefined, no magic.
2. Explain the **reward-model idea** in one sentence: feedback is turned into a *score function*,
   and the policy is nudged to produce higher-scoring answers.
3. Tell **online** apart from **offline** optimization — does the model change *while it is talking
   to live callers*, or *later, from a frozen pile of saved feedback*? — and name the safety reason
   the choice matters.
4. State precisely **where VoiceForge sits**: it **does not train live**. It builds the **dataset
   layer** — the saved, reviewed (chosen, rejected) pairs — that *somebody else* optimizes against,
   offline. We make the food; we do not run the kitchen during service.

The topic sounds mythological from the outside ("reinforcement learning from human feedback"). We
strip the myth: every idea here is a tiny pile of preference pairs and a counting rule you can do by
hand. No gradients, no RL library, no GPU. The *shape* is the point.
'''))
C.append(md('''
## 2 — Knowledge map

`18 (DPO: turning failures into chosen/rejected pairs) → THIS: RLHF / RLAIF & why we train OFFLINE → 20 (the A/B loop)`

Why this book exists, right here on the ladder. Book 18 taught you to take a **detected failure** and
mint a **preference pair**: the agent's bad turn becomes `rejected`, a corrected turn becomes `chosen`,
and the only difference between them is the one failure axis. That gave you a *single pair*. This book
zooms out one level: **what is the whole family of methods that consumes piles of those pairs to make a
model better, and how does VoiceForge relate to them?** RLHF and RLAIF are that family. The crucial,
de-mythologising fact you will leave with: VoiceForge **produces the pairs and stops** — it builds the
**dataset layer** for safe **offline** optimization and never touches a live caller's model. Book 20
then closes the loop with the **A/B test**: ship a candidate model that *someone* trained from our
pairs, and measure whether it actually beat the baseline on real calls.

No lesson floats in the void: previous = "one failure → one (chosen, rejected) pair", current = "the
family of feedback-based alignment methods, and our offline dataset-only role in it", next = "A/B the
improved agent against the old one".
'''))
C.append(md('''
## 3 — Baby intuition

Forget "reinforcement learning" for a minute. Picture teaching a new barista who cannot taste coffee.

You cannot hand them a number for "good latte". So instead you do the only thing that works: you put
**two lattes** in front of them and say *"this one is better than that one."* You do it again. And
again. After a few hundred of these *"this beats that"* judgements, the barista has built a private
sense of what *better* means — without you ever defining it. Then they start making lattes that lean
toward the ones you preferred. That is the entire idea of **learning from feedback**: not "here is the
right answer", but **"here is which of two answers I prefer"**, repeated until a taste forms.

Two small twists give you the two acronyms:
- If a **human** does the *"this beats that"* judging → that is **RLHF** (the H is *human*).
- If you are drowning in lattes and instead train a sharp assistant to do the *"this beats that"*
  judging for you, at scale → that is **RLAIF** (the AI is the judge).

And one safety twist that names VoiceForge's whole job: do you let the barista **change their recipe
mid-shift, while serving real customers** (risky — a bad lesson reaches a paying customer instantly),
or do you **collect all the judgements into a notebook and let them practice after closing** (safe —
nothing reaches a customer until it has been reviewed)? VoiceForge writes the notebook. It does not
let anyone change the recipe during service.
'''))
C.append(md('''
## 4 — The formal version

The vocabulary, said plainly and then never mystified again:

| term | plain meaning | the one-breath version |
|---|---|---|
| **policy** | the model that produces answers (our voice agent's LLM) | "the thing we are trying to improve" |
| **preference pair** | two answers to the same prompt, one marked **chosen**, one **rejected** | "this beats that, for this prompt" |
| **reward model** | a learned *score function* fit to the preference pairs | "a stand-in judge that gives any answer a number" |
| **RLHF** | *Reinforcement Learning from **Human** Feedback*: humans make the preferences; a reward model learns from them; the policy is nudged to score higher | "learn a taste from human this-beats-that, then chase it" |
| **RLAIF** | *RL from **AI** Feedback*: same loop, but an **AI judge** writes the preferences instead of a human | "same, but the judge is a model, so it scales" |
| **online** | the policy is updated **while it serves live traffic** | "change the recipe mid-shift" |
| **offline** | the policy is updated **later, from a frozen saved dataset** | "practice after closing, from the notebook" |

The loop both RLHF and RLAIF share, in four boxes:

1. **Generate** — the policy produces answers (often two per prompt).
2. **Judge** — a **human** (RLHF) or an **AI** (RLAIF) marks which answer is preferred → a preference pair.
3. **Fit a reward** — those pairs train a reward model: a function that scores *any* answer.
4. **Optimize** — nudge the policy toward higher reward (classic RLHF uses PPO; **DPO**, book 18,
   skips the separate reward model and optimizes straight from the pairs — same spirit, fewer moving
   parts).

We will not run step 4. No PPO, no gradients. We model steps 1–3 with toy strings and a counting rule,
because the *concept* you must own is **feedback → score → nudge**, not the optimizer's calculus.
'''))
C.append(md('''
## 5 — Why this exists (why bother de-mythologising RLHF at all?)

Three reasons this book has to exist before you can defend VoiceForge in a room:

- **The acronyms get thrown around as magic.** "We'll just RLHF it" is said the way people say "we'll
  add AI". If you cannot reduce RLHF to *preferences → reward → nudge*, you will either over-claim
  (promise live self-improvement you do not have) or freeze when an investor asks "so do you train the
  model?". The honest, precise answer is a competitive advantage.
- **Online vs offline is a *safety* decision, not a detail.** Training **online** means a bad lesson —
  or a poisoned preference — reaches a live caller before any human sees it. Training **offline** means
  every lesson sits in a reviewable dataset first. VoiceForge chose offline *on purpose*, and you must
  be able to say why (book 16's `needs_human_review=true` flag is that choice made literal).
- **It names our exact lane.** VoiceForge is **not** a training company. It is the **measurement +
  dataset** layer: it finds failures (books 04–11), turns them into reviewed (chosen, rejected) pairs
  (books 16–18), and hands that **clean dataset** to whoever does the actual offline optimization. If
  you blur that line, you are selling something we did not build.

This notebook shares one Python process across all cells — variables you create stay alive in the
kernel's memory for later cells (P00 drilled that). Everything is plain dicts, lists, and integers: we
are modelling **feedback-based alignment**, so a "reward model" will be a tiny scoring function you can
read top to bottom, and a "dataset" will be a short list of pairs you can print in full.
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In one breath: what does a model learn from in **RLHF**? (Not "the right answer" — what *shape* of
   signal?)
2. What single thing does **RLAIF** swap out, compared to RLHF?
3. What is the difference between **online** and **offline** optimization — and which one is safer for
   a system that talks to live callers, and why?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (maybe) thought: "RLHF is some deep reinforcement-learning magic that makes a model
align itself." After Act 1 you should hold a deflationary, precise picture: **feedback is just
*this-beats-that* preferences; RLHF/RLAIF only differ in who judges (human vs AI); and *when* you apply
the lesson — live (online) vs from a saved pile (offline) — is a safety choice.** VoiceForge's whole
role is going to fall out of that last word: **offline**.

If you can say that in your own words, continue. If "reward model" or "offline" still feels like a
spell, re-read section 4's table before moving on.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of what "learning from feedback" means now. Not mine - yours.
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
# Act 2 — Mechanics: feedback → score → nudge, drilled by hand on toy data

## The plan for this act

We build the RLHF loop's first three boxes with data small enough to see:
1. **Raw preference pairs** — printed in full, before anything touches them.
2. **By hand**: turn a pile of *this-beats-that* judgements into a **reward score** for each answer —
   just by counting wins. No library.
3. **Then** wrap that counting in a tiny `reward()` function (the reward model, demystified).
4. Show the **nudge**: pick the higher-reward answer. That is "optimize", in spirit.
5. Swap the human judge for an **AI judge** and watch the *same loop* become RLAIF.

Manual before function, raw before transformed, toy before real — the course rules apply here too.
'''))
C.append(md('''
## Meet the toy: two answers to one caller prompt

Our recurring cast lives in `data/hero/turns.json` (the real Telugu-English failure call, **call_C**):
the agent **interrupted the caller mid-answer** while they were giving an address. That is a real
`barge_in` failure. So the most natural toy prompt is exactly that moment — and two candidate replies,
one that repeats the failure and one that fixes it. This mirrors book 18's pair, kept identical on
purpose.
'''))
C.append(code('''
# The toy prompt: the caller is mid-address on call_C (Madhapur, near the metro). The agent must reply.
# We hold the conversation as plain strings so the "policy" is something you can read, not a black box.
prompt = "user (call_C): haan area... ante... Madhapur side anukunta, near the er... metro station"

# Two candidate agent replies to the SAME prompt. This pairing - same prompt, two answers - is the
# atom of all feedback-based alignment, so we name the parts explicitly.
answer_short = "Got it - Madhapur, near the metro. Morning or evening slot work better?"   # waits, confirms
answer_overtalk = ("I need your complete address with pincode, landmark and door number before we "
                   "can proceed with this booking, please provide all details now.")        # barges, demands

print("PROMPT     :", prompt)
print("answer (1) :", answer_short)
print("answer (2) :", answer_overtalk)
'''))
C.append(md('''
## PREDICT
You have not been told which answer is "preferred" yet. But you have read books 04 and 18.
For a caller who was **mid-answer**, which reply do you expect a human reviewer to mark **chosen** —
the short confirm-and-continue, or the long demand-everything? Commit out loud, then write it down.
'''))
C.append(code('''
# YOUR TURN - predict which answer a human marks 'chosen' BEFORE we reveal the judgements.
# Storing the guess makes the notebook a record of YOUR thinking, and a later cell compares it.
my_chosen_prediction = None   # <- replace None with the string "short" or "overtalk"

if my_chosen_prediction is None:
    print("set my_chosen_prediction to \\"short\\" or \\"overtalk\\" above, then re-run.")
else:
    print("prediction locked:", my_chosen_prediction)
'''))
C.append(md('''
## Raw preference data — printed in full before we touch it

A single *this-beats-that* judgement is one **preference pair**. A pile of them is the **dataset**.
Here is a tiny pile of five judgements from five (toy) human reviewers, each saying which answer they
preferred for the same prompt. We print every row — the dataset is small enough to read whole, which
is the only honest way to start.
'''))
C.append(code('''
# Five human judgements on the SAME two answers. Each row is one reviewer's "this beats that".
# We keep it as a list of dicts (one row = one judgement) so each preference is visibly one THING.
# In RLHF these come from humans; we will swap the source for an AI later (that swap IS RLAIF).
human_pairs = [
    {"reviewer": "h1", "chosen": "short",    "rejected": "overtalk"},   # waited -> preferred
    {"reviewer": "h2", "chosen": "short",    "rejected": "overtalk"},
    {"reviewer": "h3", "chosen": "short",    "rejected": "overtalk"},
    {"reviewer": "h4", "chosen": "overtalk", "rejected": "short"},      # one reviewer disagrees (noise is real)
    {"reviewer": "h5", "chosen": "short",    "rejected": "overtalk"},
]
for row in human_pairs:        # one print per row, so each preference is visibly one judgement
    print(row)
'''))
C.append(md('''
## PREDICT
Four reviewers preferred `short`, one preferred `overtalk`. We are about to turn these votes into a
**reward score** for each answer by counting wins. What will the two scores be — `short` = ?,
`overtalk` = ? Commit to both numbers before running the next cell.
'''))
C.append(code('''
# YOUR TURN - predict the win-counts BEFORE we compute them. Two integers.
my_score_short_prediction = None     # <- replace None with a number
my_score_overtalk_prediction = None  # <- replace None with a number

if my_score_short_prediction is None or my_score_overtalk_prediction is None:
    print("fill in BOTH predicted scores above, then re-run this cell.")
else:
    print("predicted scores locked - short:", my_score_short_prediction,
          "overtalk:", my_score_overtalk_prediction)
'''))
C.append(md('''
## Manual-before-function: a reward score, by counting wins

The whole "reward model" mystique collapses to this on toy data: **a reward score is how often an
answer was preferred.** We count, by hand, with a plain loop — no library, nothing hidden. (A real
reward model *generalises* this counting to unseen answers via a neural net; the **idea** it is
approximating is exactly this tally, which is why we build the tally first.)
'''))
C.append(code('''
# Manual reward: walk every judgement and tally how many times each answer was 'chosen'.
# We start both tallies at 0 so the counting is visible from nothing - no magic initial values.
reward = {"short": 0, "overtalk": 0}

for row in human_pairs:
    # each 'chosen' is one win; a higher tally means humans preferred that answer more often.
    # this counting IS the reward signal in miniature - feedback becoming a number.
    reward[row["chosen"]] = reward[row["chosen"]] + 1

print("reward by counting wins:", reward)

# compare against YOUR committed prediction - the metal-detector reading from P00.
if my_score_short_prediction is not None:
    matched = (my_score_short_prediction == reward["short"]
               and my_score_overtalk_prediction == reward["overtalk"])
    print("your score prediction", "matched" if matched else "DIFFERED",
          "- a gap here is exactly what to think about")
'''))
C.append(md('''
## The EXPLAIN gate
One sentence, out loud, in this shape: *"This cell took ___ and produced ___ because ___."*
(Hint at the shape of the answer: it took the five judgements and produced a per-answer **win count**,
because a reward score is just how often an answer was preferred.) The next cell makes you type it.
'''))
C.append(code('''
# YOUR TURN - write the explain-gate sentence for the reward-counting cell as a string.
my_explanation = ""   # e.g. "This cell took the 5 judgements and produced 4 vs 1 because ..."

if len(my_explanation.strip()) < 20:
    print("write your one-sentence explanation above (20+ chars), then re-run.")
else:
    print("EXPLAINED:", my_explanation)
'''))
C.append(md('''
## Now — and only now — wrap it in a function: the reward model, demystified

A **reward model** is nothing more spooky than: *give it any answer, get back a score.* We earned the
counting by hand, so the wrapper below is a convenience, not a mystery. We fit it from the pairs (the
tally) and then call it like a judge that hands any answer a number.
'''))
C.append(code('''
# The reward MODEL as a tiny function: it closes over the tally we computed and scores any answer.
# Real RLHF fits a neural net here; the JOB is identical - map an answer to a number you can chase.
def reward_model(answer_label):
    # .get(..., 0) so an answer the model has never seen scores 0 instead of crashing - a reward model
    # must return SOME number for any input, the way a real one generalises beyond its training pairs.
    return reward.get(answer_label, 0)

# Use it like a judge: score both candidate answers.
print("reward_model('short')   :", reward_model("short"))
print("reward_model('overtalk'):", reward_model("overtalk"))
# an answer never judged before still gets a (zero) score - no crash, mirroring real generalisation.
print("reward_model('unseen')  :", reward_model("unseen"))
'''))
C.append(md('''
## PREDICT
"Optimize the policy" sounds heavy. In our toy world it just means **pick the higher-reward answer**.
Given the two scores you just printed, which label will the next cell select as the policy's improved
output — `short` or `overtalk`? Commit before running.
'''))
C.append(code('''
# The 'optimize' step, in spirit: a nudged policy prefers the higher-reward answer. Real RLHF/DPO move
# the model's WEIGHTS so it tends to GENERATE that answer; we model the end-effect by SELECTING it,
# because the concept to own is "feedback pulls the policy toward higher reward", not PPO's calculus.
candidates = ["short", "overtalk"]

# max(..., key=reward_model) asks the reward model to score each candidate and keeps the top one.
# this single line is the whole arc of the act: feedback -> reward -> the answer the policy now prefers.
chosen_by_policy = max(candidates, key=reward_model)
print("policy now prefers:", chosen_by_policy, "(reward", reward_model(chosen_by_policy), ")")

# close the loop on YOUR Act-2 prediction from the very first PREDICT in this act.
if my_chosen_prediction is not None:
    print("you predicted humans would choose:", my_chosen_prediction,
          "->", "matched" if my_chosen_prediction == chosen_by_policy else "DIFFERED")
'''))
C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
Walk the three boxes you just built, in order: where did the **preferences** come from, how did they
become a **reward** (one word: you ______ the wins), and what did "optimize" actually do to choose an
answer? If you can name all three, you own the RLHF loop's spine.
'''))
C.append(md('''
## RLAIF in one swap: replace the human judge with an AI judge

Here is the whole difference between RLHF and RLAIF, and it is genuinely this small. Every box of the
loop stays the same — **generate, judge, reward, nudge**. We change **one** thing: the *source* of the
judgements. Instead of five humans voting, an **AI judge** reads the two answers and writes the
preference. Same dataset shape, same reward counting, same nudge. Only the judge changed.

VoiceForge already has such a judge: `pipeline/judge.py`'s `judge_dimension()` (the cached Gemini judge
from book 10). An AI judge that scores a `barge_in` dimension is exactly an RLAIF preference source.
'''))
C.append(code('''
# A toy AI judge: it reads the two answers and prefers the one that does NOT barge in / over-demand.
# We make its RULE explicit (short, waits, confirms beats long, demanding) so it is auditable - a real
# RLAIF judge is an LLM, but the POINT is identical: a non-human process emits the 'this beats that'.
def ai_judge(answer_a_label, answer_b_label, texts):
    # the rule encodes book 04+18's lesson: a reply that confirms-and-continues beats one that demands
    # everything at once. shorter, here, is a proxy for 'did not over-talk the mid-answer caller'.
    len_a = len(texts[answer_a_label])
    len_b = len(texts[answer_b_label])
    # return (chosen, rejected): the shorter, confirming reply wins. this is a STAND-IN for an LLM judge.
    if len_a <= len_b:
        return {"chosen": answer_a_label, "rejected": answer_b_label}
    return {"chosen": answer_b_label, "rejected": answer_a_label}

texts = {"short": answer_short, "overtalk": answer_overtalk}   # the judge needs the actual reply text
ai_pair = ai_judge("short", "overtalk", texts)
print("AI judge says (RLAIF preference):", ai_pair)
print("source of this preference: an AI process, not a human -> that swap is the entire RLHF->RLAIF jump")
'''))
C.append(md('''
## PREDICT
We now build the *same* reward tally as before, but from **AI** judgements (we will stack five copies
of the AI judge's call to mirror the five human rows). Will the AI-fed reward pick the **same** answer
the human-fed reward did? Commit yes/no before running.
'''))
C.append(code('''
# Build a reward from AI feedback - identical counting, different SOURCE. This is RLAIF end to end.
# We reuse the exact tally logic from the manual cell to make the 'only the judge changed' claim literal.
ai_pairs = [ai_judge("short", "overtalk", texts) for _ in range(5)]   # five AI judgements (toy scale)

reward_ai = {"short": 0, "overtalk": 0}
for row in ai_pairs:
    reward_ai[row["chosen"]] = reward_ai[row["chosen"]] + 1   # same win-counting, AI-sourced rows now

chosen_by_ai_policy = max(["short", "overtalk"], key=lambda a: reward_ai[a])
print("AI-sourced reward:", reward_ai)
print("RLHF (human-fed) picked :", chosen_by_policy)
print("RLAIF (AI-fed)   picked :", chosen_by_ai_policy)
print("same pick?", chosen_by_policy == chosen_by_ai_policy,
      "- when the AI judge is good, RLAIF reproduces RLHF's choice at a fraction of the human cost")
'''))
C.append(md('''
## CHECKPOINT 3 (out loud)
RLHF and RLAIF share the same four boxes. Name the **one** box that differs between them, and name the
**price** you pay for that swap (hint: the next act's trap is exactly this price). One sentence.
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: "reward model" and "RLAIF" were intimidating words. After Act 2 you have **built** both on toy
data: a reward is a **win count** (you tallied it by hand before any function), the **reward model** is
a one-line scorer over that tally, **optimize** is "pick the higher-reward answer", and **RLAIF** is
the *same loop with the judge swapped from human to AI*. Nothing here was magic — it was counting.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner (reward = counted preferences / RLAIF = swap the judge - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the loop, meet the trap, find the edges

## Break-it philosophy

You do not understand feedback-based alignment until you have seen it learn the **wrong** thing. The
loop is only as good as the preferences feeding it — so we now feed it bad preferences on purpose and
watch the reward model faithfully learn garbage. Surprise on your own terms is education; surprise
when a mis-trained agent is on a live call is a disaster (which is the whole argument for offline).
'''))
C.append(md('''
## PREDICT
We will hand the reward counter a judgement row whose `chosen` value is **None** (a reviewer's vote
went missing — a real data glitch). When the tally loop hits `reward[None] = reward[None] + 1`: does
Python **crash loudly**, or **silently invent a score for a non-answer**? Commit to one.
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. Read what happens; do not fix it yet.
# A real labelling pipeline WILL hand you a row with a missing 'chosen' someday. We model it and try to
# tally it the same way as every other row - watch where the loop refuses.
# EXPECTED FAILURE FOR LEARNING
broken_pairs = [
    {"reviewer": "h1", "chosen": "short", "rejected": "overtalk"},
    {"reviewer": "hX", "chosen": None,    "rejected": "short"},      # <- the damage: a missing vote
]
reward_broken = {"short": 0, "overtalk": 0}   # note: there is no key for None - that is the crux
for row in broken_pairs:
    # reward_broken[None] has no key AND None is being used as a dict key on a dict that lacks it:
    # the += forces a read of the missing key first -> KeyError. The missing vote cannot be tallied.
    reward_broken[row["chosen"]] = reward_broken[row["chosen"]] + 1
print("tally:", reward_broken)
'''))
C.append(md('''
## Reading the error (bottom-up, always)

The wall of red is a **traceback**; read the **last line first**. It says `KeyError: None` — "you asked
me to look up a key that does not exist." Then the arrow points **up** at the `reward_broken[row["chosen"]]`
line. The meaning, in plain words: **a judgement with no winner cannot become a reward.** A missing
preference is not a small data issue you can paper over — it is a hole in the *signal the whole method
runs on*.

Compare the two failure modes (this distinction runs through the whole course):
- **Loud crash** (what we got): the tally *cannot* count a vote for `None`, so Python stops. Friendly.
- **Silent wrongness** (the scary one): if that row had instead said `chosen: "overtalk"` — a *wrong
  but valid* label — every cell would run green and the reward model would dutifully learn that barging
  in is good. No error. The next BREAK-IT shows exactly that, because it is the failure that actually
  endangers callers.
'''))
C.append(code('''
# Recovery: guard the boundary. A real reward pipeline never lets a missing vote crash or poison it -
# it SKIPS rows it cannot trust and counts how many it dropped (provenance you can defend later).
reward_fixed = {"short": 0, "overtalk": 0}
dropped = 0
for row in broken_pairs:
    if row["chosen"] is None:          # a vote with no winner carries no signal - refuse it explicitly
        dropped = dropped + 1
        continue                        # skip, do not tally - fixing the BOUNDARY, not the formula (cf. P04)
    reward_fixed[row["chosen"]] = reward_fixed[row["chosen"]] + 1
print("recovered tally:", reward_fixed, "| dropped", dropped, "unusable judgement(s)")
print("the loop survived a missing vote by guarding the row; the dataset degraded instead of dying")
'''))
C.append(md('''
## The dangerous failure: garbage preferences, learned perfectly, no error at all

The crash above was the *friendly* failure. Here is the one that should scare you. Feed the **same loop**
a pile of preferences that all say the **barging, over-demanding** answer is better (a mis-aligned
labeller, a prompt-injected AI judge, or a reward hack). Nothing crashes. The reward model learns it
flawlessly. The policy then prefers the answer that **interrupts callers** — and every cell is green.
'''))
C.append(md('''
## PREDICT
We feed five judgements that all mark `overtalk` as chosen. Will any cell turn red? And which answer
will the policy then prefer — the one that waits, or the one that barges in? Commit to both.
'''))
C.append(code('''
# BREAK-IT (poisoned preferences) - no crash, fully green, and the learned lesson is WRONG.
# This is the silent-wrongness failure wearing an alignment costume: the method is only as aligned as
# the preferences feeding it. Garbage-in is learned, not rejected.
poisoned_pairs = [{"chosen": "overtalk", "rejected": "short"} for _ in range(5)]   # all prefer barging

reward_poison = {"short": 0, "overtalk": 0}
for row in poisoned_pairs:
    reward_poison[row["chosen"]] = reward_poison[row["chosen"]] + 1   # counts perfectly... the wrong thing

policy_pick = max(["short", "overtalk"], key=lambda a: reward_poison[a])
print("poisoned reward:", reward_poison)
print("policy now prefers:", policy_pick, "<- the BARGING reply. nothing errored. it just learned wrong.")
'''))
C.append(md('''
## The reveal — and why this is the entire case for OFFLINE

Both BREAK-ITs taught one lesson: **the reward model faithfully learns whatever preferences you feed
it.** Good pairs → good taste. Poisoned pairs → a policy that prefers interrupting callers, with every
cell green. There is no traceback for "learned the wrong values".

Now sit with the consequence. If this loop ran **online** — updating the live agent's model *during
calls* — the poisoned lesson would reach a paying caller **before any human saw it**. If it runs
**offline** — the pairs sit in a reviewed dataset, a human checks them (book 16's
`needs_human_review=true`), and only an explicitly approved model ever ships — the poison is caught at
the *dataset* gate, not on a live call. **That gap is exactly why VoiceForge builds the dataset layer
and refuses to train live.** The next act makes that lane explicit.
'''))
C.append(md('''
## YOUR break now

Author your own damage to the feedback loop. Pick ONE thing to corrupt — flip a single reviewer's
vote, drop the `rejected` field, make all five reviewers disagree with each other, or add a sixth
answer label nobody judged — predict exactly what happens to the reward tally and the policy's pick
(crash? which error? a tie? a silently wrong winner?), write the prediction as a comment, then run.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it on the feedback loop.
# my prediction: <write here exactly what will happen to the tally / the policy pick, and why>

my_pairs = [
    {"reviewer": "h1", "chosen": "short",    "rejected": "overtalk"},
    {"reviewer": "h2", "chosen": "short",    "rejected": "overtalk"},
    {"reviewer": "h3", "chosen": "overtalk", "rejected": "short"},
]

# 1) corrupt one thing here (examples - uncomment/edit ONE):
# my_pairs[0]["chosen"] = "overtalk"          # flip a vote
# my_pairs.append({"reviewer": "h4", "chosen": "brand_new_answer", "rejected": "short"})  # unseen label

# 2) then rebuild the reward and the pick, and compare reality to your written prediction.
my_reward = {}
for row in my_pairs:
    # .get(...,0) so a brand-new label does not KeyError - lets you safely try the 'unseen label' break.
    my_reward[row["chosen"]] = my_reward.get(row["chosen"], 0) + 1
print("your reward tally:", my_reward)
print("your policy pick :", max(my_reward, key=my_reward.get) if my_reward else "(no votes)")
'''))
C.append(md('''
## WRONG-INTUITION TRAP

**The wrong belief:** *"RLAIF means the AI improves itself — VoiceForge could just let the agent learn
from its own calls automatically, live."*

This is the single most common myth about feedback-based alignment, and it is wrong in two ways at
once. **First**, "the AI judges" (RLAIF) is not "the AI trains itself unattended": the AI judge only
*produces preferences* — the same reviewable rows a human would — and in any sane system those rows are
**still reviewed and the optimization still happens offline**. **Second**, letting an agent learn from
its own live calls *online* is precisely the poisoned-loop disaster you just built: one bad call
teaches the next. The next cell shows the seductive "self-improving online" version producing a worse
agent in three steps — green the whole way.
'''))
C.append(code('''
# The seductive myth, made literal: an ONLINE self-improving agent that judges its OWN replies live and
# updates immediately. We show it degrade in three steps, with zero errors - green is not safe.
# Step 0: the agent currently (correctly) prefers to wait. But its self-judge is subtly miscalibrated:
# it rewards LONGER replies (mistaking verbosity for helpfulness) - a realistic reward-hack.
def self_judge_prefers_longer(a, b, texts):
    # a miscalibrated self-judge: 'more words = more helpful'. This is the failure that online enables.
    return a if len(texts[a]) >= len(texts[b]) else b

live_reward = {"short": 0, "overtalk": 0}
for _ in range(3):                                   # three live turns, each updating the model IMMEDIATELY
    winner = self_judge_prefers_longer("short", "overtalk", texts)   # the longer (overtalk) reply 'wins'
    live_reward[winner] += 1                          # ONLINE update: the change is live RIGHT NOW
    # by turn 3 the live agent has taught itself to prefer the barging reply - on real callers, instantly.
print("online self-trained reward:", live_reward)
print("live agent now prefers:", max(live_reward, key=live_reward.get),
      "<- it taught itself to barge in, live, with no human and no error. THIS is what offline prevents.")
'''))
C.append(md('''
## The reveal

The online self-improver ran perfectly and got **worse** — it reward-hacked its own miscalibrated
judge and now prefers interrupting callers, and that change was *already live*. Swap to **offline** and
the same miscalibrated judge's preferences would sit in a dataset, a human would notice "wait, why are
all the long demanding replies marked chosen?", and the bad model would never ship. **Same feedback,
same judge — the only thing that changed is *when* the lesson is applied, and that timing is the entire
safety story.** VoiceForge picks offline so that the gate exists.
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
Two questions, no scrolling. (1) Why does feeding poisoned preferences produce *no error* but a worse
agent — what does that tell you about where "alignment" actually lives? (2) The myth says "RLAIF =
self-improving AI." Give the two-part correction you just saw proven.
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: feedback-based alignment felt like it could only make a model *better*. After Act 3 you have
seen it faithfully learn **garbage** with no error (poisoned pairs), watched an **online** self-judge
reward-hack itself worse *live*, and you can now state the consequence precisely: **the method is only
as aligned as its preferences, and "it ran green" guarantees nothing about the values it learned.**
That is the exact reason the *timing* of the update — online vs offline — is a safety decision, not a
detail.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the poisoned loop / online-is-unsafe is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: VoiceForge's exact lane in the RLHF/RLAIF world

## Where this lives in the real pipeline

You have built the loop's first three boxes by hand. Now place VoiceForge on the map honestly. The
real repo already contains everything *up to but not including* the optimizer:

| RLHF/RLAIF box | who does it | the real VoiceForge artifact |
|---|---|---|
| generate answers | the voice agent (the LLM under test) | the call logs in `data/normalized/*.json` (11 real calls) |
| detect failures | the deterministic + judge pipeline | `pipeline/signals.py`, `pipeline/judge.py`, `rubric.yaml` |
| judge / write preferences | a human **or** the AI judge (RLAIF) | `pipeline/judge.py` → `judge_dimension()` (cached Gemini) |
| **mint (chosen, rejected) pairs** | **VoiceForge** | **`pipeline/dpo_export.py` → `out/queue.jsonl`** (schema: `schemas/improvement_example.md`) |
| review the pairs | a **human** | `needs_human_review=true` on every pair (book 16) |
| **optimize the policy (PPO/DPO)** | **someone else, OFFLINE** | **not in this repo — on purpose** |

Read the bottom two rows together: VoiceForge **stops at the reviewed dataset.** It produces
`out/queue.jsonl` — TRL-format `{"prompt", "chosen", "rejected"}` pairs, every one flagged for human
review — and hands that **dataset layer** to whoever runs the offline optimization. The optimizer is
deliberately not here. That is the lane.
'''))
C.append(code('''
# The real artifact, in miniature: one row of out/queue.jsonl exactly as pipeline/dpo_export.py emits it.
# We print it as JSON so you SEE that VoiceForge's output is a reviewable DATASET row, not a trained model.
# This is the same {prompt, chosen, rejected} shape we tallied all act - now in its on-disk form.
import json   # stdlib; used here to render the pair the way it is written to out/queue.jsonl

queue_row = {
    "prompt":   [{"role": "system", "content": "Voice agent for booking. Never speak while the caller is mid-answer."},
                 {"role": "user", "content": prompt}],
    "chosen":   [{"role": "assistant", "content": answer_short}],
    "rejected": [{"role": "assistant", "content": answer_overtalk}],
    "needs_human_review": True,   # the offline-safety flag: nothing trains until a human signs off (book 16)
}
print(json.dumps(queue_row, indent=2))
print("\\nVoiceForge writes THIS. It does not run step 4 (optimize). The dataset layer is the deliverable.")
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell)

VoiceForge ships reviewed (chosen, rejected) pairs and stops. **Book 20** takes the next step: someone
trains a candidate agent from those pairs (offline), and then VoiceForge measures whether it actually
improved. What measurement do you think proves the candidate is better than the baseline — and why
would the per-call reward numbers from *this* book NOT be enough on their own? (No grading; book 20
hands you the answer.)
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for book 20 (the A/B loop) to confront.
my_course_prediction = ""   # what measurement proves the new agent is better, and why this book's reward alone is not it

if len(my_course_prediction.strip()) < 20:
    print("write your prediction above (the measurement + why reward-alone is insufficient), then re-run.")
else:
    print("PREDICTION STORED:", my_course_prediction)
'''))
C.append(md('''
## Where this idea fails (honesty applies to the method too)

- **Reward hacking** — the policy finds a way to score high on the reward model without being actually
  better (you built the "longer = better" version in Act 3). Countermeasure: a reward model is a proxy,
  never the goal; keep humans in the review loop and A/B on *real* outcomes (book 20).
- **Preference noise & disagreement** — reviewers disagree (you saw `h4` dissent). One pile of votes
  can encode a majority's bias. Countermeasure: measure rater agreement first (Cohen's kappa, books
  14–15) before trusting the preferences as a training signal.
- **Distribution shift** — pairs mined from today's calls may not match tomorrow's callers
  (a new language, a new scenario). Countermeasure: the dataset is *versioned and re-mined*, not frozen
  forever; offline lets you re-check before each new model ships.
- **Treating offline as a limitation** — it is a *choice*. Online would be "more impressive" and far
  more dangerous. Countermeasure: say it as a feature, because it is one.
'''))
C.append(md('''
## The concept at three levels (the same idea, three audiences)

- **To a beginner:** "You teach the agent by showing it pairs — *this reply was better than that one* —
  over and over, until it leans toward the good ones. RLHF means a person picks the better one; RLAIF
  means an AI picks it. VoiceForge writes down all those pairs; it doesn't do the teaching live."
- **To an engineer:** "Feedback-based alignment fits a reward model to preference pairs and optimizes
  the policy toward it (PPO for RLHF, or DPO straight from pairs). RLAIF substitutes an LLM judge for
  human labelers. VoiceForge emits TRL-format `{prompt, chosen, rejected}` to `out/queue.jsonl` with
  `needs_human_review=true` and performs **no** online update — it is the offline dataset layer; the
  optimizer is out of process."
- **To a founder:** "We don't train models on live calls — that's how you ship a bad lesson to a paying
  customer in real time. We build the *clean, reviewed dataset* of what-good-looks-like that any model
  team can safely optimize against offline. We own measurement and data quality; we deliberately don't
  own the training run."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "So does VoiceForge actually train / fine-tune the model with RLHF?"**
<details><summary>answer</summary>No — and that's deliberate. We produce the <em>dataset layer</em>: reviewed (chosen, rejected) preference pairs in <code>out/queue.jsonl</code>, each flagged <code>needs_human_review=true</code>. The actual optimization (PPO/DPO) happens <em>offline, out of process</em>, against our data. We own measurement and data quality, not the training run.</details>

**2. "If you have an AI judge (RLAIF), why not just let the agent improve itself automatically?"**
<details><summary>answer</summary>Because "AI judges" only means the <em>preferences</em> are AI-written — not that training should be unattended or online. Self-improving on live calls is the poisoned/reward-hacked loop: one bad call teaches the next, with no human and no error. We keep the AI judge's pairs in a reviewed dataset and optimize offline, so a bad lesson is caught at the data gate, never on a live caller.</details>

**3. "Online learning sounds more powerful — isn't offline a weakness?"**
<details><summary>answer</summary>It's a safety choice, not a limitation. Online means a poisoned or miscalibrated preference reaches a paying caller before any human sees it. Offline means every lesson sits in a reviewable, versioned dataset and only an explicitly approved model ships. For a system talking to real callers, that gate is the entire point.</details>
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
Point at the box-table you just read and answer three things: (1) which **one** row is the VoiceForge
deliverable, (2) which **one** row is deliberately *not* in this repo, and (3) what flag on every
emitted pair is the offline-safety gate made literal. If you can name all three, you can defend the
lane in a room.
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now hold VoiceForge's exact lane: it sits in the RLHF/RLAIF world as the **measurement +
dataset** layer — it mines failures into reviewed `{prompt, chosen, rejected}` pairs
(`pipeline/dpo_export.py` → `out/queue.jsonl`), flags every one `needs_human_review=true`, and hands
that off for **offline** optimization it does not run. You can place that on the box-table, defend it
in a room, and name where it breaks. Next, book 20 closes the loop by **A/B testing** a model trained
from these pairs against the baseline.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. **RLHF in one breath** — what shape of signal does the model learn from? (not "the right answer")
2. **RLAIF** — the one box that changes, and the price of changing it
3. **The reward-model idea** — feedback becomes a ______, and the policy is nudged to ______
4. **Online vs offline** — which one VoiceForge uses and the safety reason why
5. **VoiceForge's lane** — what artifact it ships (`out/queue.jsonl`, `needs_human_review`) and the one
   step it deliberately does **not** do

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (VoiceForge's lane in the RLHF world)
my_clean_sentence = ""      # the sentence you'd say in a room about RLHF/RLAIF and our offline role

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"VoiceForge builds the dataset layer for safe offline optimization."**

RLHF and RLAIF are just *feedback → reward → nudge*, differing only in whether a human or an AI writes
the preferences. The dangerous knob is *when* you apply the lesson — live (online) or from a reviewed
pile (offline). VoiceForge mines reviewed (chosen, rejected) pairs and hands them off; it never trains
on a live caller. If your sentence captures that in your own words, this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "19_rlhf_rlaif_without_mythology.ipynb"   # <- this notebook's filename
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

**19 done** (pending your teach-back) → **20 · The A/B loop** — take a candidate agent trained
*offline* from the (chosen, rejected) pairs this layer produces, run it against the baseline on real
calls, and measure whether the improvement is real. The dataset you learned to build here is what that
A/B test is built on.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "19_rlhf_rlaif_without_mythology.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
