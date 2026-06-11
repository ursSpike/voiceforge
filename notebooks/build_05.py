#!/usr/bin/env python3
# Builds 05_asr_llm_tts_voice_stack.ipynb — VoiceForge University book 05.
# ONE atomic concept: every turn is a three-model relay (ASR -> LLM -> TTS) run under a time budget,
#                     and the per-turn latency is the SUM of where each box spends its milliseconds.
# We do NOT teach model internals — only the relay, the vocabulary, and where the ms accrue.
# Rerun: .venv/bin/python notebooks/build_05.py
# Style/rhythm/comment-density cloned from build_P00.py and build_01.py (the gold references).
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
# 05 · ASR / LLM / TTS — the voice stack

## 1 — Learning contract
By the end of this notebook you will be able to:
1. Name the **three models** a voice agent runs every turn, in order — **ASR** (speech-to-text),
   **LLM** (decide the reply), **TTS** (text-to-speech) — and the one metric each is judged by.
2. Trace **one caller utterance** all the way through the relay using plain Python strings:
   audio → ASR text → LLM reply text → TTS audio → a per-turn log line.
3. State **where the milliseconds accrue** each turn, and compute a turn's total latency as the
   **sum** of the per-box times plus network — never a single mystery number.
4. Define **TTFA** (time to first audio) and say why a streaming stack is judged on *first* audio,
   not *total* audio; and place **Cartesia Sonic's 82ms TTFA** in that picture.

The topic is small on purpose (we fake every model with a one-line string function). The point is
not how a model works inside — it is the **shape of the relay** and the **budget it runs under**.
That shape is what books 04 (timing) and 06 (task success) both stand on.
'''))
C.append(md('''
## 2 — Knowledge map

`04 (timing: gaps & overlaps) → THIS: the three-model relay & the latency budget → 06 (task success)`

Why this book exists, right here on the ladder: book 04 taught you to **measure** the gap on a
user→agent handoff (the silence the caller feels) and call it *laggy* past 800ms. But it never said
**what fills that gap** — what the agent is actually *doing* during those milliseconds. This book
opens the box: the gap is three models running in a relay (ASR, then LLM, then TTS), and the gap's
size is the **sum** of how long each one takes. Book 06 then stops timing the call and starts asking
*did the agent get the job done* (required fields captured) — task success. So the trio is: when did
they talk (04) → **what machine produced each agent turn, and where did its time go (05)** → did that
machine accomplish the task (06).

No lesson floats in the void: previous = "a 1,600ms gap is laggy", current = "that gap is ASR+LLM+TTS
under a budget", next = "judge whether the reply actually completed the task".
'''))
C.append(md('''
## 3 — Baby intuition

Picture a phone call to a booking line, but the "agent" is a small **relay team of three**, and the
baton they pass is the conversation.

1. The caller speaks. The first teammate, **the Listener**, writes down the words they hear. (Audio
   came in; text comes out.)
2. The Listener hands that text to **the Thinker**, who decides what to say back. (Text in; new text
   out.)
3. The Thinker hands the reply to **the Speaker**, who says it out loud in a human-sounding voice.
   (Text in; audio out.)

Listener → Thinker → Speaker. Audio → text → text → audio. That hand-off-the-baton sequence happens
**every single turn** of the call — not once, but again and again, dozens of times. And there is a
stopwatch running: a real human takes the floor back in about a quarter-second, so every millisecond
the relay spends is a millisecond of silence the caller hears. This book is about that team and that
stopwatch.
'''))
C.append(md('''
## 4 — The formal version

A modern voice agent is **three models in a relay**, run in a loop, under time pressure. The real
names (you will hear all of these in the room):

| step | model | plain name | input → output | judged by |
|---|---|---|---|---|
| 1 | **ASR** (also called **STT**) | speech-to-text | caller audio → text | **WER** (word error rate) |
| 2 | **LLM** | the "agent" brain | conversation text → reply text | task quality (book 06; our judge) |
| 3 | **TTS** | text-to-speech | reply text → audio | **TTFA** (time to first audio) / naturalness |

- **ASR** = *Automatic Speech Recognition*; **STT** = *Speech-To-Text*. Same box, two names — this
  book uses **ASR** but they are interchangeable.
- The relay runs **per turn**. So the latency the caller feels on one user→agent handoff is:
  **ASR finalization + LLM first tokens + TTS first audio + network**, added up.
- **TTFA** = *Time To First Audio*: milliseconds from "reply text is ready" until the **first sound**
  of the voice plays. Streaming stacks are judged on *first* audio, not the *whole* clip, because the
  caller stops feeling the silence the instant the voice starts.

We will not open any of these three boxes. How ASR turns sound into letters, how an LLM picks the
next word, how TTS renders a waveform — out of scope, on purpose. We care about **the relay** (what
goes in, what comes out, in what order) and **the budget** (where the milliseconds go).
'''))
C.append(md('''
## 5 — Why this exists (why care about the relay and the budget at all?)

Two reasons VoiceForge needs you to hold this picture:

- **The latency you grade is not atomic.** Book 04's "laggy, 1,620ms gap" is not one thing — it is a
  *sum*. If you cannot name the three addends (ASR, LLM, TTS) plus network, you cannot say *why* a
  call was slow or *which box* to fix. A founder who says "average response is 600ms" is hiding which
  box ate the budget and whether 600ms is a mean over a bimodal mess (you learned in P00 that means
  lie; book 04 made it about silence; here it becomes about *which stage*).
- **Each box has its own failure metric, and they don't trade off cleanly.** A faster TTS (low TTFA)
  does not fix a wrong ASR transcription (high WER), and a brilliant LLM reply read by a 2-second-slow
  TTS still feels broken. Three boxes, three metrics, one budget — that is the whole game.

This notebook shares one Python process across all cells — variables you create stay alive in the
kernel's memory for later cells (P00 drilled that; we lean on it here). Everything is plain strings
and integers: we are modelling the **relay**, so a "model" is just a tiny function that takes a
string and returns a string. No audio, no ML, no internals.
'''))
C.append(code('''
# Our first code cell. Comments in this course explain WHY a line exists, never just syntax.

# We represent the caller's AUDIO as a plain string label, NOT a real waveform. The whole book is
# about the RELAY (what each box hands the next), so audio only needs to be "a thing that arrives
# before any text exists" — a label captures that without dragging in signal processing we won't teach.
caller_audio = "<<audio: 'Madhapur side, near the metro'>>"   # the baton at the start of the relay

# Printing the raw input first (course rule: see the ugly input before transforming it).
print("what enters the relay:", caller_audio)
print("type:", type(caller_audio).__name__, "- to us, audio is just an opaque blob until ASR reads it")
'''))
C.append(code('''
# The three boxes, as the three plainest possible functions. Each takes a string and returns a string.
# We define them as STUBS (fake one-liners) on purpose: the lesson is the RELAY's shape — audio->text,
# text->text, text->audio — not what really happens inside any box. Real ASR/LLM/TTS are out of scope.

def asr(audio_blob):
    # ASR's job: audio in, TEXT out. Our stub just strips the "<<audio: ... >>" wrapper to expose the
    # words, standing in for "recognized the speech". (A real ASR could mis-hear; we model that later.)
    return audio_blob.replace("<<audio: '", "").replace("'>>", "")

def llm(conversation_text):
    # LLM's job: conversation text in, REPLY text out. Our stub returns a fixed booking-style reply,
    # because WHAT it decides is book 06's concern — here we only need "text goes in, new text comes out".
    return "I need your full address with pincode to book the visit."

def tts(reply_text):
    # TTS's job: text in, AUDIO out. Our stub re-wraps the text as an audio label — the mirror image of
    # asr() — so you can SEE the relay end where it began: in audio, but now it is the agent speaking.
    return f"<<audio(agent voice): '{reply_text}'>>"

print("three stubs defined: asr (audio->text), llm (text->text), tts (text->audio)")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. Name the **three models** in the relay, in order, and what each one's **input and output** is.
2. **ASR** and **STT** — are those two different boxes, or two names for the same box?
3. In one sentence: the caller's latency on a handoff is the **sum** of which four things?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (probably) pictured "the voice agent" as a single black box that hears and replies.
After Act 1 you should picture it as a **three-stage relay** — ASR (audio→text), LLM (text→text), TTS
(text→audio) — that runs **every turn**, and you should know the per-turn latency is a **sum** of the
three boxes plus network, not one number.

If you can say "audio in, ASR makes text, LLM makes reply text, TTS makes audio out — and it runs
every turn under a stopwatch" without looking, continue. If not, re-run the two code cells and read
each stub's input→output back.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of "what is a voice agent?" Not mine - yours.
# Producing the sentence is the learning; reading mine would just feel like learning.
clean_sentence_act_1 = ""   # <- type your sentence between the quotes

# A gentle gate so you cannot skim past: the cell nags until you write something real.
# (Guarded so a fresh, UNFILLED notebook still runs clean top-to-bottom.)
if len(clean_sentence_act_1.strip()) < 15:
    print("write your Act-1 sentence above (15+ characters), then re-run this cell.")
else:
    print("ACT 1 LOGGED:", clean_sentence_act_1)
'''))

# ============================================================ ACT 2 · MECHANICS
C.append(md('''
# Act 2 — Mechanics: run one utterance through the relay, by hand, then time it

## From three boxes to one turn

In Act 1 we defined the three stubs. Now we **run the baton through them**, one box at a time, and
look at what comes out of each. Manual-before-function: first we pass the value through each stub by
hand (so you SEE the baton change shape three times), and only after that do we wrap the whole relay
in a single function. Watching it step by step is the lesson; the wrapper is just convenience.
'''))
C.append(md('''
## PREDICT
We are about to feed `caller_audio` through `asr`, then the result through `llm`, then *that* through
`tts`. Before you run it: after the **first** box (asr), will the value still look like audio
(`<<audio: ...>>`), or like plain text? And after the **last** box (tts), audio or text? Commit to
both before scrolling.
'''))
C.append(code('''
# YOUR TURN - predictions are written BEFORE the relay runs, stored as variables so the notebook
# becomes a record of YOUR thinking and a later cell can check it.
my_after_asr_is_audio = None   # <- replace None with True or False (is the value audio after asr()?)
my_after_tts_is_audio = None   # <- replace None with True or False (is the value audio after tts()?)

if my_after_asr_is_audio is None or my_after_tts_is_audio is None:
    print("fill in BOTH predictions above (True/False), then re-run this cell.")
else:
    print("predictions locked:", my_after_asr_is_audio, "and", my_after_tts_is_audio)
'''))
C.append(code('''
# The relay BY HAND — three lines, one box each, printing the baton after every hand-off.
# Seeing the value transform audio -> text -> text -> audio is the entire concept made concrete.

step1_text = asr(caller_audio)                 # box 1: audio in -> recognized text out
print("after ASR  (audio->text):", repr(step1_text))

step2_reply = llm(step1_text)                  # box 2: that text in -> reply text out
print("after LLM  (text->text) :", repr(step2_reply))

step3_audio = tts(step2_reply)                 # box 3: reply text in -> agent audio out
print("after TTS  (text->audio):", repr(step3_audio))

# Check YOUR prediction against reality - this comparison is the lesson, not the values.
if my_after_asr_is_audio is not None:
    after_asr_audio = step1_text.startswith("<<audio")     # did box 1 leave it as audio? (no - it made text)
    after_tts_audio = step3_audio.startswith("<<audio")    # did box 3 produce audio? (yes - the mirror of asr)
    ok = (my_after_asr_is_audio == after_asr_audio and my_after_tts_is_audio == after_tts_audio)
    print("your prediction", "matched" if ok else "DIFFERED",
          "- if it differed, that gap is exactly what to think about")
'''))
C.append(md('''
## The EXPLAIN gate

One sentence, out loud, in this shape:

> "The baton entered as ___, and after ASR/LLM/TTS it left as ___, because each box ___."

It feels slow. That is the point — saying it is the difference between *recognizing* three function
calls and *owning* the idea that the relay is a shape: audio in at one end, audio out the other, with
text in the middle.
'''))
C.append(code('''
# YOUR TURN - write the explain-gate sentence for the relay as a string.
my_explanation = ""   # e.g. "The baton entered as audio and left as audio because each box converts one form to the next."

if len(my_explanation.strip()) < 20:
    print("write your one-sentence explanation above (20+ chars), then re-run.")
else:
    print("EXPLAINED:", my_explanation)
'''))
C.append(md('''
## Now wrap the relay in one function

You ran the three boxes by hand. *Now* — and only now — we bundle them into a single `run_turn`
function, so the rest of the notebook can say "run one turn" without rewriting the three lines. The
function does **exactly** what you just did by hand; meeting the wrapper after the manual version
means it is a convenience, not a mystery.
'''))
C.append(code('''
# The whole relay as one function: audio in, agent audio out, with the text it produced along the way.
def run_turn(audio_blob):
    # We thread the baton through the three stubs in order. Returning the intermediates too (the heard
    # text and the reply text), not just the final audio, because later cells want to INSPECT each
    # hand-off — a relay you can only see end-to-end hides exactly where things go wrong.
    heard = asr(audio_blob)        # box 1
    reply = llm(heard)             # box 2
    spoken = tts(reply)            # box 3
    return {"heard": heard, "reply": reply, "spoken": spoken}

turn = run_turn(caller_audio)      # run one full turn end to end
for stage, value in turn.items():  # one print per stage so each hand-off is visibly one thing
    print(f"{stage:>6}: {value}")
'''))
C.append(md('''
## The part that actually matters: where do the milliseconds go?

The relay's *shape* (audio→text→text→audio) is half the lesson. The other half is the **budget**.
Each box takes **time**, and on a live call that time is **silence the caller hears**. So we attach a
millisecond cost to each stage. These are illustrative per-turn numbers (the kind a real stack
reports), not measured from any one vendor:

| stage | what is being timed | example ms |
|---|---|---|
| ASR finalization | from caller stops speaking → final text ready | 150 |
| LLM first tokens | from text in → first words of the reply decided | 400 |
| TTS first audio (**TTFA**) | from reply text → first sound plays | 120 |
| network | round-trips between the boxes/services | 80 |

The caller's felt latency on that handoff is the **sum**: `150 + 400 + 120 + 80`. We will compute it
as a sum, never type the total by hand — the moment you hardcode the total, you lose the ability to
ask *which addend* is the problem.
'''))
C.append(md('''
## PREDICT
1. Add those four numbers in your head: `150 + 400 + 120 + 80` = ? ms.
2. Book 04's rubric said **≤300ms snappy**, **≤800ms ok**, **>800ms laggy**. Which band does your
   total land in?
3. Which **single box** is the biggest slice of the budget?
'''))
C.append(code('''
# YOUR TURN - commit your three predictions BEFORE the compute cell runs.
my_total_ms_prediction = None     # <- replace None with your sum of 150+400+120+80
my_band_prediction = None         # <- replace None with the string "snappy", "ok", or "laggy"
my_biggest_box_prediction = None  # <- replace None with "asr", "llm", "tts", or "network"

if None in (my_total_ms_prediction, my_band_prediction, my_biggest_box_prediction):
    print("fill in ALL THREE predictions above, then re-run this cell.")
else:
    print("predictions locked:", my_total_ms_prediction, my_band_prediction, my_biggest_box_prediction)
'''))
C.append(code('''
# The latency budget for one turn, kept as a dict so each stage stays NAMED. A bare 750 tells you the
# call was laggy; a named breakdown tells you WHICH box to go fix - that difference is the whole point.
budget_ms = {
    "asr_finalization_ms": 150,   # caller stopped -> final transcript ready
    "llm_first_token_ms":  400,   # transcript in -> first reply tokens (usually the biggest slice)
    "tts_ttfa_ms":         120,   # reply text -> first audio sample (this is TTFA)
    "network_ms":           80,   # round-trips between services
}

# Total felt latency = SUM of the parts. We sum the dict's values rather than typing 750, so editing
# any stage above keeps this line TRUE (the change-one-thing rule from P00, applied to a budget).
total_latency_ms = sum(budget_ms.values())
print("per-stage budget:", budget_ms)
print("total felt latency:", total_latency_ms, "ms")

# Name the biggest slice programmatically (max by value) - so "which box to fix" is computed, not eyeballed.
biggest_box = max(budget_ms, key=budget_ms.get)
print("biggest single slice:", biggest_box, "=", budget_ms[biggest_box], "ms")
'''))
C.append(code('''
# Classify the total into the rubric's bands. Thresholds match book 04 / rubric.yaml: 300 and 800.
# We compute the band rather than asserting "laggy" so the label follows the number, not our memory.
def latency_band(ms):
    # the two cutoffs are the SAME numbers the FTO latency dimension uses (rubric.yaml: laggy_ms 800,
    # snappy display band 300) - we reuse them so this book and book 04 can never disagree.
    if ms <= 300:
        return "snappy"
    if ms <= 800:
        return "ok"
    return "laggy"

band = latency_band(total_latency_ms)
print(f"{total_latency_ms} ms -> band: {band}")

# Confront YOUR predictions now.
if my_total_ms_prediction is not None:
    print("total:   you said", my_total_ms_prediction, "/ actual", total_latency_ms,
          "->", "match" if my_total_ms_prediction == total_latency_ms else "DIFFERED")
    print("band:    you said", repr(my_band_prediction), "/ actual", repr(band),
          "->", "match" if my_band_prediction == band else "DIFFERED")
    print("biggest: you said", repr(my_biggest_box_prediction), "/ actual", repr(biggest_box),
          "->", "match" if my_biggest_box_prediction == biggest_box else "DIFFERED")
'''))
C.append(md('''
## EXPLAIN gate
One sentence, from what you just **saw** (not memory): the total felt latency was a **sum** of four
named stages — which one stage was the largest slice, and why does keeping the breakdown *named*
(instead of just reporting 750) matter when a call is judged laggy?
'''))
C.append(md('''
## CHECKPOINT 2 (out loud)
1. The per-turn latency is a **sum** of four things — name all four.
2. For our example turn, which band did 750ms fall into (snappy / ok / laggy), and which **single
   box** was the biggest slice?
3. Why do we `sum(budget_ms.values())` instead of writing `total = 750`? (One reason is about edits
   staying true; one is about being able to ask *which box* is the problem.)
'''))
C.append(md('''
## PREDICT
A turn is laggy at 750ms and you can only speed up **one** box by 100ms. The budget was ASR 150,
**LLM 400**, TTS 120, network 80. If you shave 100ms off the **TTS** box versus 100ms off the **LLM**
box — does the caller's total felt latency change by a **different** amount, or the **same** amount?
Commit before scrolling (it is a trap-shaped question — think about what "sum" means).
'''))
C.append(code('''
# YOUR TURN - predict which 100ms cut helps the caller more, BEFORE the compute cell.
my_bigger_help = None   # <- replace None with "tts", "llm", or "same"

if my_bigger_help is None:
    print("fill in my_bigger_help (\\"tts\\"/\\"llm\\"/\\"same\\") above, then re-run.")
else:
    print("prediction locked:", my_bigger_help)
'''))
C.append(code('''
# Shave 100ms off TTS vs off LLM and compare the TOTAL each time. The point: because total latency is
# a SUM, a 100ms cut anywhere moves the total by exactly 100ms - WHICH box you cut doesn't change the
# caller's felt saving. (What it DOES change is whether that box had 100ms to give - LLM did, a fast
# TTS might not.) This kills the intuition that "optimize the famous box" automatically helps most.
cut_tts = dict(budget_ms);  cut_tts["tts_ttfa_ms"] -= 100        # speed up the TTS box by 100ms
cut_llm = dict(budget_ms);  cut_llm["llm_first_token_ms"] -= 100  # speed up the LLM box by 100ms

total_cut_tts = sum(cut_tts.values())
total_cut_llm = sum(cut_llm.values())
print("cut 100ms from TTS -> total:", total_cut_tts, "ms")
print("cut 100ms from LLM -> total:", total_cut_llm, "ms")
print("same saving?", total_cut_tts == total_cut_llm,
      "- a 100ms cut moves a SUM by 100ms no matter which addend; the box choice is about feasibility, not arithmetic")

if my_bigger_help is not None:
    print("you predicted:", repr(my_bigger_help),
          "-> the felt saving is the SAME (100ms) either way; only 'can that box spare 100ms' differs")
'''))
C.append(md('''
## Meet TTFA properly (and Cartesia's 82ms)

The TTS stage's metric, **TTFA** (time to first audio), deserves its own moment because it is subtle.

A reply like *"Your booking is confirmed for tomorrow at ten AM in Madhapur"* takes a few **seconds**
to say out loud in full. But the caller does not wait for the *whole* sentence to feel the agent
respond — they feel it the instant the **first sound** plays. So TTS is judged on **time to FIRST
audio**, not time to finish. A streaming TTS starts emitting sound while it is still rendering the
rest of the sentence.

This is exactly the metric **Cartesia** (a sponsor of this hackathon) leads on: their **Sonic** model
advertises **82ms end-to-end TTFA across 42 languages**. 82ms is the gap between "reply text is ready"
and "the voice has started" — small enough that, of our four budget stages, TTS would be a *minor*
slice. (We cite 82ms and 42 languages exactly as their published figures; we do not cite their
unverified "Turbo ~40ms" number.) Let's make TTFA concrete with strings and a tiny clock.
'''))
C.append(md('''
## PREDICT
We will "speak" a reply one character at a time, 8ms per character. TTFA is the time until the
**first** character is out. Total-audio time is until the **last**. For a 60-character reply: roughly
what is TTFA (first char), and roughly what is total time (all 60)? Which number does the caller feel?
'''))
C.append(code('''
# A toy "streaming TTS": we don't render real audio, we model the CLOCK. Each character is one chunk
# of speech taking a fixed number of ms - enough to show the gap between FIRST audio and FULL audio.
reply_text = "Your booking is confirmed for tomorrow at ten AM in Madhapur."
ms_per_char = 8                       # invented per-chunk cost, so the two timings are visibly different

ttfa_ms = ms_per_char                 # TIME TO FIRST AUDIO = time until the very first chunk plays
full_audio_ms = ms_per_char * len(reply_text)   # time until the LAST chunk plays (the whole clip)

print("reply length:", len(reply_text), "chars")
print("TTFA (first audio):", ttfa_ms, "ms  <- what the caller FEELS as 'it responded'")
print("full audio (whole clip):", full_audio_ms, "ms  <- when the sentence finishes")
print("ratio:", round(full_audio_ms / ttfa_ms, 1), "x  - the caller stops feeling silence at the FIRST number, not the second")
'''))
C.append(code('''
# Why streaming matters, shown as a contrast. A NON-streaming TTS must finish the whole clip before
# ANY sound plays - so its 'first audio' equals its 'full audio'. Same words, very different feel.
streaming_first_audio = ttfa_ms                 # streaming: first sound after one chunk
nonstreaming_first_audio = full_audio_ms        # non-streaming: first sound only after the LAST chunk

print("streaming TTS     - caller hears voice after:", streaming_first_audio, "ms")
print("non-streaming TTS - caller hears voice after:", nonstreaming_first_audio, "ms")
print("the streaming stack feels", round(nonstreaming_first_audio / streaming_first_audio, 1),
      "x faster to the caller, with identical words - THAT is why TTFA is the metric, not total audio")
'''))
C.append(md('''
## CHECKPOINT 3 (out loud, without scrolling up)
1. What does **TTFA** stand for, and which moment does it measure (first audio or full clip)?
2. Why is TTFA the metric a streaming TTS is judged on, rather than how long the whole reply takes to
   say?
3. Cartesia Sonic advertises **82ms** TTFA. In our four-stage budget (ASR 150, LLM 400, TTS 120,
   net 80), would an 82ms TTS be a big slice or a small one?
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before: the relay was three boxes in the abstract. After Act 2 you can **run** one utterance through
all three with plain strings (audio→text→text→audio), **bundle** them into `run_turn`, **compute** the
per-turn latency as a *named sum* and classify it against book 04's bands, and **define TTFA** —
seeing with a toy clock why *first* audio is what the caller feels (and where Sonic's 82ms sits). Next
act: break the relay and meet the trap that hides in averaged latency.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (the relay / the named latency sum / TTFA - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the relay, and the trap inside averaged latency

## Break-it philosophy

You do not understand the relay until you know its edges. The relay has a brutal one: it is a
**chain**, so if any one box stalls or mishears, the *whole turn* is wrong or late — the other two
boxes were perfect and it did not matter. We now damage one box at a time and watch the turn fail, so
that on demo day the failure is one you have already seen.
'''))
C.append(md('''
## PREDICT
The relay is `asr → llm → tts`. We are about to feed the LLM stub a value that is **None** instead of
text (imagine ASR returned nothing — a dropped recognition). When `llm(None)` tries to treat `None`
as conversation text: does Python **crash loudly**, or **quietly produce a wrong-but-plausible
reply**? Commit to one.
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. Read what happens; do not fix it yet.
# We model "ASR dropped the utterance" by handing the LLM None instead of a string. Our llm() stub
# ignores its input, so to make the BREAK realistic we first try to USE the text the way a real agent
# would - by appending it to a running conversation string. None + string is the crash.
# EXPECTED FAILURE FOR LEARNING
asr_output = None                                  # ASR heard nothing this turn (a real, common failure)
conversation_so_far = "agent: which area?\\nuser: "  # the agent keeps a running transcript of the call
conversation_so_far = conversation_so_far + asr_output   # TypeError: can only concatenate str to str
reply = llm(conversation_so_far)
print("reply:", reply)
'''))
C.append(md('''
## Reading the error (bottom-up, always)

The wall of red is a **traceback**; read the **last line first**. It says something like
`TypeError: can only concatenate str (not "NoneType") to str` — "you tried to glue text and a
*nothing* together." That is not a typo to fix in passing. It is the relay's chain-failure made
literal: **box 1 (ASR) produced nothing, so box 2 (LLM) had nothing to work with.** One stalled box
broke the whole turn.

Compare the two failure modes (this distinction runs through the whole course):
- **Loud crash** (what we got): the LLM *cannot* pretend `None` is a sentence, so Python stops. Friendly.
- **Silent wrongness** (the scary one): if ASR had instead *mis-heard* "Madhapur" as "Mada poor" and
  passed that on, every downstream box would run perfectly on the **wrong words** — no error at all,
  just a confidently wrong turn. The next cell shows that silent version.
'''))
C.append(code('''
# Recovery: guard the box boundary. A real relay never lets a dead box poison the next one - it checks.
# We give ASR a fallback ("(unintelligible)") so the LLM always receives a STRING, and the turn degrades
# gracefully instead of crashing. Fixing the BOUNDARY, not the formula, is the lesson (cf. P04).
asr_output = None
safe_asr_text = asr_output if asr_output is not None else "(unintelligible)"  # never hand None onward
conversation_so_far = "agent: which area?\\nuser: " + safe_asr_text
reply = llm(conversation_so_far)
print("recovered turn -> reply:", reply)
print("the turn survived a dropped ASR by guarding the hand-off; the relay degraded instead of dying")
'''))
C.append(md('''
## The silent failure: ASR mishears, the relay runs perfectly on wrong words

The crash above was the *friendly* failure. Here is the dangerous one. ASR does not crash when it
mishears — it returns confident text that happens to be wrong. The LLM and TTS then do their jobs
**flawlessly** on those wrong words. No error anywhere. The turn looks healthy and is silently broken.
'''))
C.append(md('''
## PREDICT
ASR mishears the caller's **address** — it hears `"near the matter"` instead of `"near the metro"`.
The LLM and TTS run with zero errors on that text. Will any cell turn red? And will the agent's spoken
reply *look* fine to someone reading the log? Commit to both before running.
'''))
C.append(code('''
# A mishearing ASR: same shape (audio->text), but the text is WRONG. Nothing here errors - that is the
# entire danger. We define a second stub so we can compare a clean turn against a misheard one side by side.
def asr_mishears(audio_blob):
    # stand-in for a real recognition error: one word swapped. A real ASR's WER (word error rate) is
    # exactly the count of swaps like this - the metric exists because this failure is invisible otherwise.
    return asr(audio_blob).replace("metro", "matter")   # 'metro' -> 'matter': one wrong word, silently

clean_text   = asr(caller_audio)            # what was actually said
misheard_text = asr_mishears(caller_audio)  # what a faulty ASR passed downstream
print("clean ASR   :", repr(clean_text))
print("misheard ASR:", repr(misheard_text))

# Run the REST of the relay (llm, tts) on the misheard text - watch it succeed flawlessly on bad input.
downstream_reply = llm(misheard_text)       # LLM works perfectly... on the wrong words
downstream_audio = tts(downstream_reply)    # TTS works perfectly... on the wrong words
print("agent reply (no error):", downstream_reply)
print("nothing crashed; the WRONG turn looks exactly as healthy as a right one")
'''))
C.append(md('''
## The reveal

Both turns ran green. One heard "metro", one heard "matter". **The relay has no idea it misheard** —
ASR's error became LLM's and TTS's truth, and every box reported success. This is the same lesson P00
planted (green cells prove execution, never correctness) wearing a voice-stack costume: a turn can be
**fully successful at every stage and still be wrong**, because *correctness lives upstream of where
the error shows*. This is *why* ASR is judged by **WER** (word error rate) — a metric that exists
precisely to catch the silent mishears that never throw.
'''))
C.append(md('''
## WRONG-INTUITION TRAP

**The wrong belief:** *"Our agent's **average** response time is 600ms, which is in the 'ok' band — so
latency is fine."*

This is the P00 mean-vs-median trap, now wearing the voice stack's clothes. An *average* latency hides
**which turns** were slow and **which box** caused them. A stack can average a comfortable 600ms while
**one in five turns blows past 800ms into laggy** — and on a live call, those few laggy turns are
exactly when the caller says "hello? are you there?". The average smooths them into invisibility. The
next cell builds five real turns and shows the mean lying.
'''))
C.append(code('''
# Five turns' total latencies (ms). Four are snappy/ok; ONE turn the LLM stalled (a slow tool call).
# This is the bimodal mess an average flattens - the same shape as P00's average-of-averages trap.
turn_latencies_ms = [240, 300, 280, 1500, 320]   # turn 4 = 1500ms: the LLM hung; caller heard dead air

mean_latency = sum(turn_latencies_ms) / len(turn_latencies_ms)   # the flattering single number

# median: sort, take the middle. We compute it by hand (P00 rule) so it is not a mystery from a library.
ordered = sorted(turn_latencies_ms)
median_latency = ordered[len(ordered) // 2]      # middle of 5 sorted values = index 2

# How many turns were actually LAGGY (>800ms)? The count the mean hides.
laggy_turns = [ms for ms in turn_latencies_ms if ms > 800]

print("per-turn latencies:", turn_latencies_ms)
print("mean   latency:", round(mean_latency, 1), "ms  -> band:", latency_band(mean_latency))
print("median latency:", median_latency, "ms  -> band:", latency_band(median_latency))
print("turns actually LAGGY (>800ms):", len(laggy_turns), "of", len(turn_latencies_ms),
      "->", laggy_turns, "ms")
'''))
C.append(md('''
## The reveal

The **mean** is 528ms — comfortably "ok", and a lie. The **median** is 300ms — and one full turn
(1,500ms) screamed past laggy into dead-air territory. A founder reporting "600ms average, we're fine"
is doing exactly what P00 warned against and what book 04 formalized: **report p50/p90, never the
mean**, because the tail is where the caller actually suffers. And note *which box* stalled — the LLM —
which you could only say because the budget stayed **named** (Act 2). Trap defused: an average latency
in a good band can hide both *which turns* were laggy and *which box* did it.
'''))
C.append(md('''
## YOUR break now

Author your own damage to the relay. Pick ONE box and break it your way: feed `asr` an audio blob it
cannot parse, make `llm` receive an integer instead of text, or hand `tts` a non-string. **Predict**
(as a comment) exactly what will happen — crash with which error, or a silent wrong value — then run.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it on the relay.
# my prediction: <write here: which box do you break, crash or silent wrongness, and why?>

# Pick ONE line to make real (delete the leading # ), or write your own break below.
# Each is a different way a real relay fails - predict the outcome BEFORE you uncomment.
# broken = asr(12345)                       # asr expects a string blob; an int has no .replace -> ?
# broken = llm(["not", "a", "string"])      # llm appends nothing here, but what does it RETURN? silent?
# broken = tts(None)                        # tts does an f-string on None - crash, or a weird label?

# Guard so the UNFILLED cell still runs clean: only act if you defined `broken` above.
if "broken" in dir():
    print("your break produced:", repr(broken))
else:
    print("uncomment one line above (or write your own), predict first, then re-run.")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud, without scrolling up)
1. The relay is a **chain**. Explain why one stalled or mishearing box ruins the whole turn even when
   the other two boxes are perfect.
2. Which failure is **friendlier** — ASR returning `None` (crash) or ASR mishearing "metro" as
   "matter" (no crash)? Why?
3. The five-turn example had a 528ms **mean** in the "ok" band. What did that average **hide**, and
   which two numbers (p50/p90 style) would have exposed it?
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before: the relay was a tidy three-step pipeline. After Act 3 you have **broken** it three ways: a
dropped ASR crashes the next box (chain failure), a mishearing ASR sails through every box silently
wrong (which is *why* WER exists), and an averaged latency in a good band hides both the laggy turns
and which box caused them (report p50/p90, not mean). "Every box reported success" is not "the turn
was right or fast".
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the silent-mishear or the averaged-latency trap are strong candidates)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: where the relay lives in VoiceForge, and how to defend it

## Where this sits in real VoiceForge

The relay is the **machine that produced every agent turn** in the calls you already work with:

- `data/hero/turns.json` — the real hero call you met in book 01. Every `agent` turn in it was
  produced by an ASR→LLM→TTS relay; the `agent_voice` in its metadata (`en-IN-NeerjaNeural`) is the
  TTS box's voice. The two famous "sins" are relay-timing failures: `t3` = **−800ms** (agent's TTS
  started before the caller finished — a barge-in) and `t7` = **+1,620ms** (dead air — the relay took
  too long that turn).
- `pipeline/signals.py` — `turn_metrics()` / `analyze()` measure the **gap** on each user→agent
  handoff. That gap **is** the relay's total per-turn latency (book 04's number). This book named what
  fills it: ASR + LLM + TTS + network.
- `rubric.yaml` — the bands you reused (`latency_gap.laggy_ms: 800`, snappy ≤300) and the metric slot
  names. The three-box framing is why the rubric has *separate* dimensions: timing (the relay's
  latency) vs faithfulness/task (the LLM's reply) — different boxes, different metrics.
- **Cartesia Sonic** (sponsor) is specifically the **TTS** box, leading on **TTFA (82ms, 42
  languages)** — the metric you made concrete with a toy streaming clock.

Everything VoiceForge times and judges starts from turns this relay produced.
'''))
C.append(md('''
## The concept at three levels (say the right one to the right person)

- **To a beginner:** "A voice agent is three programs in a row — one writes down what you said, one
  decides what to say back, one says it out loud — and they run that little relay every single time
  you speak, racing a stopwatch so you don't hear silence."
- **To an engineer:** "Every turn is an ASR→LLM→TTS relay. Per-turn latency = ASR finalization + LLM
  first-token + TTS TTFA + network, summed; it is a chain, so the slowest or wrongest box dominates.
  Each stage has its own metric (WER, task quality, TTFA) and they don't trade off — and you report
  p50/p90 of the per-turn total, never the mean, because the tail is the felt failure."
- **To a founder:** "The 'agent' is really three vendors in series: speech-recognition, the language
  model, and the voice. The customer-felt delay is the sum of all three plus network, so 'our latency
  is fine on average' hides which turns went dead-air and which box to fix. We instrument the relay so
  we can point at the exact stage — that is cheaper than swapping the whole stack on a hunch."
'''))
C.append(md('''
## PREDICT (course-level — write it in the next cell, no grading today)

The hero call's `t7` was **+1,620ms** of dead air — laggy. You now know that gap is
ASR + LLM + TTS + network for that turn. Which **single box** would you bet ate most of those 1,620ms
on a turn where the agent had to *think* about what to ask next — and what cheap experiment would
confirm it? Store your guess.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for later books to confront.
my_course_prediction = ""   # which box ate the 1,620ms, and the experiment that would confirm it

if len(my_course_prediction.strip()) < 20:
    print("write your prediction above (which box + the experiment), then re-run.")
else:
    print("PREDICTION STORED:", my_course_prediction)
'''))
C.append(md('''
## Where the relay idea itself bites you (honest failure modes)

- **The boxes overlap in reality.** We summed ASR + LLM + TTS as if they run strictly one-after-another.
  Production stacks **stream** — the LLM can start before ASR fully finalizes; TTS can start before the
  LLM finishes. So the true latency is often *less* than the naive sum, and modelling it as a clean sum
  is a teaching simplification. The **shape** (three boxes, each with a metric) holds; the exact
  arithmetic is an upper bound.
- **Our stubs can't mishear in the ways that matter.** A real ASR's errors cluster on names, numbers,
  and code-switched speech (the hero call's "Madhapur", the phone digits). A one-word `replace()` only
  *gestures* at WER; do not mistake the gesture for the measurement.
- **TTFA is not the whole TTS story.** First audio can be fast (82ms) and the voice can still sound
  robotic, mispronounce a name, or stumble on Tenglish. Naturalness is a separate axis from TTFA; a low
  TTFA is necessary, not sufficient.
- **"Which box to fix" needs per-stage timing you may not have.** Splitting a 1,620ms gap into
  ASR/LLM/TTS/network requires the stack to *emit* per-stage timestamps. If it only reports the total,
  you are back to a single mystery number — instrument first, blame second.
'''))
C.append(md('''
## CHECKPOINT 5 (out loud, without scrolling up)
1. The hero call's `t7` was a **+1,620ms** laggy gap. Name the **four addends** that gap decomposes
   into, and which one you'd instrument first to find the culprit.
2. A teammate says "Sonic gives us 82ms TTFA, so our latency problem is solved." Using the budget
   shape, give the one-sentence reason that does **not** follow.
3. Name the real VoiceForge file that **measures** this per-turn latency, and the real file whose
   **thresholds** (300 / 800ms) you used to call a turn snappy / ok / laggy.
'''))
C.append(md('''
## Defense questions (×3 — try to answer before opening each)

**1. "You faked all three models with one-line string functions. How is that not a toy that teaches
nothing?"**
<details><summary>answer</summary>The book's claim is about the relay's SHAPE and BUDGET, not model internals — and those are exactly what survive faking. Audio→text→text→audio is real; the per-turn latency being a SUM of named stages is real; the chain-failure (one bad box ruins the turn) is real; TTFA being first-audio is real. Stubs let me show all of that without 246MB of audio or a GPU. The moment I needed internals (how ASR decodes, how an LLM samples) I'd be out of this book's scope on purpose.</details>

**2. "Cartesia says 82ms TTFA. Your example budget put TTS at 120ms and LLM at 400ms. Aren't your
numbers just made up?"**
<details><summary>answer</summary>Yes — the 150/400/120/80 split is illustrative, labelled as such, not measured from any vendor. The ONE external number I cite precisely is Cartesia's published 82ms TTFA over 42 languages (their figure; I deliberately don't cite their unverified ~40ms Turbo). The teaching point survives either way: TTS/TTFA is typically a SMALL slice and the LLM's first-token time is usually the big one — which is why "make the voice faster" rarely fixes a laggy agent.</details>

**3. "Why does this book exist between timing (04) and task success (06)? Isn't it just vocabulary?"**
<details><summary>answer</summary>Book 04 measures the gap; book 06 grades the outcome; neither says what PRODUCES the agent turn or where its time goes. Without this book, "laggy" is one opaque number and "the agent replied" is one opaque event. With it, the gap decomposes into ASR+LLM+TTS+network (so you can fix the right box) and the reply is understood as the LLM box's output (so book 06's task-success judging has a subject). It's vocabulary, yes — but it's the vocabulary that makes 04 and 06 actionable instead of magic.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now know: the relay is the real machine behind every agent turn in `data/hero/turns.json`,
the gap `pipeline/signals.py` measures is the relay's total per-turn latency, the rubric's separate
dimensions exist because the three boxes have separate metrics, Cartesia Sonic is specifically the TTS
box (82ms TTFA), and you can pitch the relay-and-budget idea to a beginner, an engineer, and a founder
— plus defend why string stubs are enough and why "fix the voice" rarely fixes "the agent is slow".
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. Name the **three models** in order, each one's **input→output**, and the **metric** each is judged by.
2. Give the **per-turn latency** as a sum of its **four** named parts.
3. Define **TTFA** and say why a streaming TTS is judged on *first* audio, not the full clip — and
   where Cartesia Sonic's **82ms** sits in a typical budget.
4. Explain the **chain failure**: why one stalled or mishearing box ruins the whole turn, and why a
   mishear (no crash) is more dangerous than a drop (crash) — i.e. why **WER** exists.
5. Recall the trap: an **averaged** latency in a good band hides the **laggy tail** and **which box**
   caused it — so report **p50/p90**, not the mean.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4
my_clean_sentence = ""      # the sentence you'd say in a room about the voice stack

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Every turn is a three-model relay under a time budget."**

ASR hears, the LLM decides, TTS speaks — every turn, and the latency the caller feels is the sum of
where each box spends its milliseconds. If your sentence captures that in your own words, this book
did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "05_asr_llm_tts_voice_stack.ipynb"   # <- this notebook's filename
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

**05 done** (pending your teach-back) → **06 · Task success** — you now know the **LLM box** produces
the agent's reply; next you stop timing the relay and start asking *did that reply get the job done* —
the required-fields checklist (did the agent capture area, address, appliance, time, callback number?)
that turns a call's outcome into `success` / `partial` / `failure`. Then onward to judging and cost.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "05_asr_llm_tts_voice_stack.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
