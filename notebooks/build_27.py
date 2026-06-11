#!/usr/bin/env python3
# Builds 27_provider_adapters.ipynb — VoiceForge University, book 27.
# The ONE atomic concept: provider-neutrality is achieved by normalizing every source to one schema.
# Rerun: .venv/bin/python notebooks/build_27.py
# Gates:  .venv/bin/python notebooks/run_nb.py   notebooks/27_provider_adapters.ipynb  -> EXECUTION OK
#         .venv/bin/python notebooks/audit_nb.py notebooks/27_provider_adapters.ipynb  -> ALL PASS
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
# 27 · Provider adapters

## 1 — Learning contract
By the end of this notebook you will be able to:
1. State the **one atomic idea**: provider-neutrality is achieved by **normalizing every source to one schema** — not by a slide that says "neutral".
2. Take a **Bolna-ish execution log** and a **Cartesia-ish synthesis record** — two payloads that share *nothing* — and turn BOTH into the **same `call_log`**.
3. Recite the **adapter contract**: what every adapter must guarantee at the boundary so that nothing downstream (`signals`, `judge`, `score`) ever learns the vendor's name.
4. Avoid the **Bolna timing traps** — why you read turn timing from the `/log` component events, never from the scrubbed top-level transcript.

The real code this book shadows is `pipeline/normalize.py` and `schemas/call_log.md`. We will
build a toy adapter by hand first, then read the real one and see it is the same five moves.
'''))
C.append(md('''
## 2 — Knowledge map

`26 (dashboard mental model) → THIS: Provider adapters → 28 (talking like an engineer)`

Where you just were (26): you learned the dashboard is four views, each answering one
person's question — and every view reads from `out/*.json`, which all trace back to the
**normalized pool**. You never once asked "which vendor produced this call?" — because by the
time data reaches a view, the vendor is gone.

**This book is where the vendor gets erased.** It is the funnel: many shapes go in (SpokenWOZ,
AMI, a constructed hero call, a Bolna log, a Cartesia record), one shape comes out. Book 28
then teaches you to *defend* this on a stage — "provider-neutral is an architecture fact" is a
sentence you can only say honestly once you have written the adapter. So: 26 showed the views;
27 builds the funnel that feeds them; 28 puts the funnel into words for the room.
'''))
C.append(md('''
## 3 — Baby intuition

Three friends mail you a recipe. One sends a voice note. One sends a photo of a handwritten
card. One sends a typed list. The recipes are *different formats* but they can all answer the
same question: "what goes in the pot, in what order?"

If your kitchen needed a different cooking process per format — a voice-note process, a
photo process, a typed-list process — you would drown the moment a fourth friend texts a
link. So you do the sane thing: you **transcribe every incoming recipe into one index card
format first**, and then you only ever cook from index cards. The transcribing step is the
**adapter**. The index card is the **schema**. The kitchen downstream never knows or cares
which friend a card came from.

VoiceForge is that kitchen. The index card is called `call_log`.
'''))
C.append(md('''
## 4 — The formal version

An **adapter** is a function `raw_vendor_payload -> call_log`. It is the *only* code in the
whole system that is allowed to know a vendor's field names, quirks, and traps. Everything
after it reads one shape.

The **schema** (`schemas/call_log.md`) is the index card. Its load-bearing fields:

| field | what it pins down |
|---|---|
| `call_id` | a stable name to key caches and labels |
| `source` | `spokenwoz \\| ami \\| hero \\| bolna` — provenance kept, never *behavior* |
| `language` | `en`, `te-en`, … — a dimension, not a code path |
| `stress_profile` | `clean \\| pause_heavy \\| interruption \\| …` |
| `turns[]` | sorted by `start_ms`; each has `turn_id, speaker(user\\|agent), text, start_ms, end_ms` |
| `end_ms` | `int` OR `null` — `null` means "latency only, never fake an overlap" |

The phrase to hold: **the adapter absorbs the chaos so the core stays assumption-free.**
The core's freedom is *bought* by the adapter's knowledge.
'''))
C.append(md('''
## 5 — Why this exists (the founder reason and the engineer reason)

**Founder reason:** the sponsors in the room (Bolna, Cartesia) each own a slice of the voice
stack. A tool that only works on one of them is a feature of that one; a tool that ingests
*any* of them is a layer above all of them. "Provider-neutral, sponsor-compatible" is the
whole pitch — but only if it is true in code.

**Engineer reason:** if every downstream function (FTO math, the judge, the scorecard) had to
branch on `if source == "bolna": ...`, then adding a vendor would mean editing twenty files,
and each vendor's quirks would leak everywhere. One adapter per vendor + one schema = adding a
vendor touches exactly **one** new function. That is the entire architectural bet.

The next two cells set up the kitchen — the index-card definition we will normalize *into*.
'''))
C.append(code('''
# Our first code cell. Comments here explain WHY a line exists, not what the syntax does.

# We pin the schema's required keys as a plain list so that "valid call_log" stops being a
# vibe and becomes something we can CHECK. Everything in this book is judged against this list.
CALL_LOG_REQUIRED = ["call_id", "source", "language", "stress_profile", "workflow_type", "turns"]

# A turn's required keys, separately - turns are where vendors disagree most, so they get
# their own contract. 'end_ms' is allowed to be None; the others are not.
TURN_REQUIRED = ["turn_id", "speaker", "text", "start_ms", "end_ms"]

print("a normalized call must carry:", CALL_LOG_REQUIRED)
print("each turn must carry:        ", TURN_REQUIRED)
'''))
C.append(code('''
# We print the schema's two hardest rules as text, because they are the rules vendors violate
# and the rules our adapter must enforce. Writing them down now makes the later checks obvious.
print("RULE 1: turns are sorted by start_ms (one clock per call).")
print("RULE 2: speaker is exactly 'user' or 'agent' - the vendor's labels get mapped to these.")
print("RULE 3: end_ms may be None -> that turn gets latency-only treatment, never a faked overlap.")
'''))
C.append(md('''
## CHECKPOINT 1 (say it out loud before continuing)
1. In one sentence: what is an **adapter**, and what is the **one** thing it is uniquely
   allowed to know that nothing else in the system may?
2. What is the **schema** here called, and what does it mean for downstream code that every
   source becomes this shape?
3. Why does adding a new vendor touch exactly **one** new function instead of twenty?
'''))
C.append(md('''
## ACT 1 knowledge-flow checkpoint — what changed in your head?

Before Act 1 you (maybe) heard "provider-neutral" as a marketing adjective. After Act 1 you
should hear it as a **shape claim**: there exists one schema, and every source has a function
that produces it. "Neutral" is the *name* for "we wrote the adapter." If that swap — from
adjective to architecture — feels solid in your own words, continue.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 1.
# Write YOUR one-sentence version of what "provider-neutral" means now. Not mine - yours.
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
# Act 2 — Mechanics: two ugly payloads, normalized by hand into one schema

## The plan for this act
We will:
1. Print a **Bolna-ish execution log** RAW — and see that its top-level transcript is a trap.
2. Print a **Cartesia-ish synthesis record** RAW — a totally different shape.
3. Normalize **each, by hand**, into a `call_log` — watching the five moves repeat.
4. Only THEN look at the real `pipeline/normalize.py` and recognize the same moves.

Raw before transformed. Manual before function. Toy before real.
'''))
C.append(md('''
## Meet the Bolna-ish execution log (the production source)

A real Bolna call exposes three endpoints (SPEC §7.G): a cheap **executions list** (transcript
+ recording URL + cost), an **execution detail**, and — the one that matters for timing — a
**`/log`** stream of component events. We mock a small, faithful version. The faithfulness that
matters: the **top-level `transcript` is one string with no roles and no timing**, and in
"precise transcript" mode it actively *deletes* interrupted (barge-in) content.
'''))
C.append(code('''
# A mock Bolna-ish execution payload. We hand-build it (not download it) so the SHAPE is the
# lesson and nothing depends on credits. The fields mirror SPEC §7.G's real Bolna response.
bolna_execution = {
    "id": "exec_7a1c",
    "agent_id": "agent_book27",
    "status": "completed",
    # TRAP #1: the top-level transcript is a SINGLE STRING. No speaker roles. No timestamps.
    # And in "precise" mode the caller's interrupted words are SCRUBBED out entirely.
    "transcript": "agent: What area are you in? user: Madhapur side, near the metro. "
                  "agent: And which appliance? user: the fridge, cooling nahi ho raha",
    "telephony_data": {
        "recording_url": "https://signed.example/exec_7a1c.wav",  # expires fast in reality
        "post_dial_delay_ms": 2200,   # TRAP #2: PSTN setup time, NOT turn latency
        "ring_duration_ms": 4100,     # also PSTN, also NOT conversation timing
    },
    "total_cost": 0.041,              # TRAP #3: cost is aggregate-only, no per-turn breakdown
}

# Print it raw - seeing the ugly input before touching it is a course rule.
for k, v in bolna_execution.items():
    print(k, "->", v)
'''))
C.append(md('''
## PREDICT
Look at `bolna_execution["transcript"]`. If you tried to compute **barge-in** (who interrupted
whom, and by how many milliseconds) from that string alone — could you? Commit to yes/no and
**why** before the next cell. (Hint: barge-in is an *overlap in time*. What does the string
carry about time?)
'''))
C.append(code('''
# YOUR TURN - PREDICT BEFORE running. Store your guess so the notebook records YOUR thinking.
can_get_bargein_from_transcript = None   # <- replace None with True or False

if can_get_bargein_from_transcript is None:
    print("set the variable above to True or False, then re-run.")
else:
    # The reveal: the transcript has zero timestamps, so no overlap is computable from it.
    # And worse - "precise" mode already deleted the interrupted words, so the evidence is gone.
    print("your guess:", can_get_bargein_from_transcript)
    print("truth: False - the transcript has no ms values, so 'overlap in time' cannot exist in it,")
    print("and precise-mode scrubbing already removed the barge-in words. timing must come from /log.")
'''))
C.append(md('''
## Why the transcript is a trap (read once, remember forever)

This is the single most important fact in this book about Bolna:

> **Timing comes from `GET /executions/{id}/log` ONLY** — you diff `created_at` across
> component events. A `transcriber-response` event marks a **user** turn; an `llm` or
> `synthesizer` event marks an **agent** turn.

The top-level transcript is for human eyeballs. It has no roles you can trust, no timing at
all, and "precise transcript" mode **deletes the very interruptions you are trying to
measure**. `post_dial_delay` and `ring_duration` are telephone-network setup, not
conversation latency — using them as turn timing is a classic wrong number. So our adapter
will **ignore the transcript string** and build turns from the log events instead.
'''))
C.append(code('''
# The Bolna /log stream: component events, each with a created_at timestamp (ms here for clarity;
# real Bolna uses ISO strings you'd diff). We map event TYPE -> speaker, exactly per SPEC §7.G.
# This is the data the transcript string threw away.
bolna_log_events = [
    {"type": "transcriber-response", "created_at_ms": 600,   "text": "Madhapur side, near the metro"},
    {"type": "llm",                  "created_at_ms": 0,     "text": "What area are you in?"},
    {"type": "synthesizer",          "created_at_ms": 150,   "text": "What area are you in?"},
    {"type": "llm",                  "created_at_ms": 5400,  "text": "And which appliance?"},
    {"type": "transcriber-response", "created_at_ms": 8200,  "text": "the fridge, cooling nahi ho raha"},
]

# Print raw, sorted by time, so you can SEE that these events - not the transcript - carry the clock.
for e in sorted(bolna_log_events, key=lambda x: x["created_at_ms"]):
    print(f"{e['created_at_ms']:>6} ms | {e['type']:<22} | {e['text']}")
'''))
C.append(md('''
## The five moves of any adapter (we will repeat these for both vendors)

Every adapter, no matter the vendor, does these five things — and *only* these:

1. **Extract turns** from wherever the vendor hides them (here: log events, not the transcript).
2. **Map speaker** to `user`/`agent` from the vendor's own labels (here: event type).
3. **Put time on one clock** in `start_ms` (and `end_ms`, or `None` if the vendor gives none).
4. **Sort** turns by `start_ms` and assign `turn_id` (`t1`, `t2`, …).
5. **Stamp provenance** (`source`, `language`, `stress_profile`, `workflow_type`) and validate.

Watch for these five as we hand-build the Bolna adapter next.
'''))
C.append(md('''
## PREDICT
We are about to turn those 5 log events into turns. Two of the three `llm`/`synthesizer`
events describe the **same** agent utterance ("What area are you in?"). When we build turns,
how many **agent** turns and how many **user** turns should end up in the call? Commit to two
numbers.
'''))
C.append(code('''
# YOUR TURN - PREDICT the turn counts BEFORE the build cell runs.
my_agent_turns = None    # <- your number
my_user_turns = None     # <- your number

if my_agent_turns is None or my_user_turns is None:
    print("fill in both counts above, then re-run.")
else:
    print("locked: you expect", my_agent_turns, "agent turns and", my_user_turns, "user turns.")
'''))
C.append(code('''
# MOVE 1+2+3 by hand for Bolna: extract turns, map speaker by event type, place on the clock.
# We treat llm/synthesizer as the SAME agent utterance, so we collapse them to avoid a phantom
# duplicate turn - the synthesizer just speaks what the llm decided.
def bolna_event_to_speaker(ev_type):
    # transcriber-response == the USER was transcribed; llm/synthesizer == the AGENT spoke.
    # This mapping is the ONLY place Bolna's vendor vocabulary is allowed to live.
    return "user" if ev_type == "transcriber-response" else "agent"

raw_turns = []
seen_agent_text = set()
for e in sorted(bolna_log_events, key=lambda x: x["created_at_ms"]):
    spk = bolna_event_to_speaker(e["type"])
    # collapse the llm+synthesizer pair: if we already made an agent turn for this exact text,
    # skip the twin so one utterance == one turn (a real normalize concern, not cosmetic).
    if spk == "agent" and e["text"] in seen_agent_text:
        continue
    if spk == "agent":
        seen_agent_text.add(e["text"])
    raw_turns.append({"speaker": spk, "text": e["text"], "start_ms": e["created_at_ms"]})

for t in raw_turns:
    print(t)
'''))
C.append(code('''
# MOVE 4 by hand: sort by start_ms and assign turn_ids. Timing only makes sense in
# chronological order, so the sort is a PRECONDITION, not a tidy-up.
raw_turns.sort(key=lambda t: t["start_ms"])
for i, t in enumerate(raw_turns):
    t["turn_id"] = f"t{i + 1}"
    # Bolna's log gave onset only (no end_ms) -> we honor RULE 3 and set end_ms = None,
    # which downstream reads as "latency-only, never fake an overlap for this turn".
    t["end_ms"] = None

# Re-print to confirm the count matches (or breaks) your prediction.
print("built", len(raw_turns), "turns:")
for t in raw_turns:
    print(f"  {t['turn_id']} | {t['speaker']:<5} | start={t['start_ms']:>5} | end={t['end_ms']} | {t['text']}")
'''))
C.append(md('''
## OBSERVE + EXPLAIN
Did your agent/user counts hold? The "What area are you in?" utterance appeared as BOTH an
`llm` event and a `synthesizer` event, but became **one** agent turn — because one decision
spoken once is one turn. Say in a sentence: why would *not* collapsing it have produced a
wrong barge-in number later? (Hint: a phantom duplicate turn invents a gap or overlap that
never happened.)
'''))
C.append(code('''
# MOVE 5 by hand: stamp provenance and assemble the full call_log. Note end_ms is None on every
# turn here - that is honest, because Bolna's /log in this mock gave onsets, not offsets.
bolna_call_log = {
    "call_id": "bolna_exec_7a1c",       # stable id keyed off the execution id
    "source": "bolna",                  # provenance kept - but it changes NO downstream behavior
    "language": "te-en",                # code-switching noted as a dimension, not a code path
    "stress_profile": "interruption",   # a label; deterministic rules can confirm it later
    "workflow_type": "appliance_service_booking",
    "turns": raw_turns,
    "audio_path": None,                 # we have a recording_url, not a local file, so None
    "metadata": {
        "vendor": "bolna",
        "timing_source": "log events (created_at diffs), NOT the scrubbed transcript",
        "recording_url": bolna_execution["telephony_data"]["recording_url"],
    },
}
import json
print(json.dumps(bolna_call_log, indent=2))
'''))
C.append(md('''
## CHECKPOINT 2 (out loud, without scrolling up)
1. Name the **five moves** every adapter performs.
2. For Bolna specifically: which move was the trap, and where did the real timing come from?
3. Why did `end_ms` end up `None` on every Bolna turn here — and what does `None` license
   downstream (and forbid)?
'''))
C.append(md('''
## Meet the Cartesia-ish synthesis record (a totally different shape)

Cartesia makes **Sonic** — a TTS engine (42 languages, ~82ms time-to-first-audio per the
sponsor card). A Cartesia record is *not* a phone call; it is a list of **synthesis events**:
the agent's spoken lines, each with the audio it produced and how long that audio ran. There is
**no user side at all** in a pure TTS log — Cartesia speaks; it does not listen.

This is the opposite trap from Bolna: Bolna gave us a transcript but hid the timing; Cartesia
gives us precise per-utterance timing but covers **only the agent**. Our adapter has to be
honest about that gap, not paper over it.
'''))
C.append(code('''
# A mock Cartesia-ish synthesis record: agent utterances only, each with start + audio duration.
# Different keys, different nesting, different everything from Bolna - that is the whole point.
cartesia_record = {
    "request_id": "cart_55f",
    "model": "sonic-3.5",
    "language": "en",
    "synthesis": [
        {"utterance_index": 0, "begin_ms": 0,    "audio_ms": 1850, "say": "Hello, how can I help you book today?"},
        {"utterance_index": 1, "begin_ms": 6200, "audio_ms": 1400, "say": "Great - what date works for you?"},
        {"utterance_index": 2, "begin_ms": 9800, "audio_ms": 1100, "say": "Booked. Anything else?"},
    ],
}

# Print raw so the new shape is visible before we touch it.
print("request:", cartesia_record["request_id"], "| model:", cartesia_record["model"])
for u in cartesia_record["synthesis"]:
    print(f"  idx {u['utterance_index']} | begin={u['begin_ms']:>5} | audio={u['audio_ms']:>4} | {u['say']}")
'''))
C.append(md('''
## PREDICT
Cartesia gives us `begin_ms` AND `audio_ms` (how long the speech lasted). That means we CAN
compute a real `end_ms` for each agent turn (unlike Bolna). Predict the `end_ms` of utterance
0: it begins at `0` and its audio runs `1850`ms. Write the number. Then predict: will the
Cartesia call_log have any `user` turns? yes/no.
'''))
C.append(code('''
# YOUR TURN - PREDICT end_ms of utterance 0 and whether any user turns exist.
my_end_ms_utt0 = None      # <- a number
my_has_user_turns = None   # <- True or False

if my_end_ms_utt0 is None or my_has_user_turns is None:
    print("fill in both predictions above, then re-run.")
else:
    print("locked: end_ms[0] =", my_end_ms_utt0, "| has user turns:", my_has_user_turns)
'''))
C.append(code('''
# Normalize Cartesia BY HAND - the same five moves, but the vendor specifics differ.
# MOVE 1: turns are the synthesis utterances. MOVE 2: every one is the AGENT (TTS only speaks).
# MOVE 3: start_ms = begin_ms, and here we CAN set a real end_ms = begin_ms + audio_ms.
cartesia_turns = []
for u in cartesia_record["synthesis"]:
    cartesia_turns.append({
        "speaker": "agent",                              # a TTS log has no user side, ever
        "text": u["say"],
        "start_ms": u["begin_ms"],
        "end_ms": u["begin_ms"] + u["audio_ms"],         # real offset: audio duration is known
    })

# MOVE 4: sort + turn_ids (already in order, but we never TRUST input order - we enforce it).
cartesia_turns.sort(key=lambda t: t["start_ms"])
for i, t in enumerate(cartesia_turns):
    t["turn_id"] = f"t{i + 1}"

for t in cartesia_turns:
    print(f"  {t['turn_id']} | {t['speaker']:<5} | start={t['start_ms']:>5} | end={t['end_ms']:>5} | {t['text']}")
'''))
C.append(code('''
# MOVE 5 for Cartesia: stamp provenance and assemble. We keep source="bolna"? NO - this is a
# Cartesia synthesis source. The schema's source enum is spokenwoz|ami|hero|bolna today; we
# record the true origin in metadata and pick the closest enum honestly (it is agent audio,
# so we tag it 'bolna'-family only if it were a call - here we are explicit it is synthesis).
cartesia_call_log = {
    "call_id": "cartesia_cart_55f",
    "source": "bolna",                 # enum is limited this sprint; the TRUE origin is in metadata
    "language": cartesia_record["language"],
    "stress_profile": "clean",         # agent-only audio, no interruptions possible
    "workflow_type": "appointment_booking",
    "turns": cartesia_turns,
    "audio_path": None,
    "metadata": {
        "vendor": "cartesia",          # the honest provenance lives here, never lost
        "true_source": "cartesia_tts_synthesis",
        "model": cartesia_record["model"],
        "note": "TTS-only record: agent turns have real end_ms; there is no user side to time",
    },
}
print(json.dumps(cartesia_call_log, indent=2))
'''))
C.append(md('''
## The punchline: two payloads, one shape

Stop and look. `bolna_execution` and `cartesia_record` shared **zero** field names. One hid
its timing in a log stream; the other handed timing over freely but only for the agent. Yet
both came out the far end as a `call_log` with the *same* keys, the *same* `turns[]` shape,
the *same* `speaker` vocabulary. That sameness is not luck — it is the five moves, applied
twice. **The downstream pipeline cannot tell them apart, and that is the victory.**
'''))
C.append(code('''
# Prove the shape-sameness mechanically: both call_logs expose the identical top-level key set.
# If this set ever differed, a downstream tool would have to branch on vendor - the thing we
# built the adapter to prevent. So we ASSERT they match.
bolna_keys = set(bolna_call_log.keys())
cartesia_keys = set(cartesia_call_log.keys())

print("bolna call_log keys   :", sorted(bolna_keys))
print("cartesia call_log keys:", sorted(cartesia_keys))
print("identical top-level shape:", bolna_keys == cartesia_keys)

# And every turn, from either vendor, carries the same turn-level keys:
all_turn_keys = {frozenset(t.keys()) for t in bolna_call_log["turns"] + cartesia_call_log["turns"]}
print("number of distinct turn shapes across BOTH vendors:", len(all_turn_keys), "(1 == neutral)")
'''))
C.append(md('''
## CHECKPOINT 3 (out loud)
A downstream function `turn_metrics(call["turns"])` computes barge-in and latency. Explain why
it can run on `bolna_call_log` and `cartesia_call_log` **without a single line that mentions
Bolna or Cartesia**. What did the adapter have to guarantee for that to be safe?
'''))
C.append(md('''
## Now the real thing: `pipeline/normalize.py`

You have done the five moves by hand, twice. Here is the *actual* repo function for SpokenWOZ
(lightly trimmed). Read it and tag each of the five moves in the margin of your mind. The
vendor specifics differ (SpokenWOZ hides speaker in a `tag` field, and timing in word-level
ASR timestamps) — but it is the same five moves you just performed.
'''))
C.append(code('''
# This is a faithful, runnable miniature of pipeline/normalize.py's spokenwoz_call() (SPEC §7.D).
# We include it so you can RUN the real shape on toy SpokenWOZ-like input, not just read it.
PLAUSIBLE_OVERLAP_MAX_MS = 4000   # overlaps bigger than this are data noise, not real barge-in
LONG_PAUSE_MS = 1500              # an intra-turn word gap this big counts as a long pause

def _merge_same_speaker(raw_turns):
    # MOVE (extra): adjacent same-speaker turns merge, because a "floor transfer" only exists
    # BETWEEN speakers - two agent fragments in a row are one turn, not two.
    merged = []
    for t in raw_turns:
        if merged and merged[-1]["speaker"] == t["speaker"]:
            m = merged[-1]
            m["text"] = (m["text"] + " " + t["text"]).strip()
            m["end_ms"] = max(m["end_ms"], t["end_ms"])
        else:
            merged.append(dict(t))
    for i, t in enumerate(merged):
        t["turn_id"] = f"t{i + 1}"   # MOVE 4: turn_ids assigned after the final ordering
    return merged

print("defined _merge_same_speaker - the SpokenWOZ-specific move the toy adapters did not need")
'''))
C.append(code('''
# A tiny SpokenWOZ-like dialogue: speaker hides in `tag`, timing hides in word-level times.
# We run the real-shaped normalize over it so the five moves are visible on production-style data.
swz_like = {"log": [
    {"tag": "user",   "text": "yeah .",                      "words": [{"BeginTime": 5520, "EndTime": 6400}]},
    {"tag": "system", "text": "hi, how can I help .",        "words": [{"BeginTime": 6880, "EndTime": 9470}]},
    {"tag": "system", "text": "what city .",                 "words": [{"BeginTime": 9500, "EndTime": 10800}]},
    {"tag": "user",   "text": "cambridge please .",          "words": [{"BeginTime": 11200, "EndTime": 13410}]},
]}

raw = []
for t in swz_like["log"]:
    words = t.get("words") or []
    if not words:            # MOVE 1: a turn with no word timing is unusable for FTO -> skip it
        continue
    raw.append({
        # MOVE 2: SpokenWOZ's vendor label is `tag`; we map system->agent, else user.
        "speaker": "agent" if t["tag"] == "system" else "user",
        "text": t["text"].strip(),
        "start_ms": words[0]["BeginTime"],   # MOVE 3: onset = first word's BeginTime
        "end_ms": words[-1]["EndTime"],      #          offset = last word's EndTime
    })
raw.sort(key=lambda t: t["start_ms"])        # MOVE 4: enforce chronological order
swz_turns = _merge_same_speaker(raw)         # the two adjacent system turns become ONE agent turn

for t in swz_turns:
    print(f"  {t['turn_id']} | {t['speaker']:<5} | {t['start_ms']:>5}-{t['end_ms']:<5} | {t['text']}")
'''))
C.append(md('''
## EXPLAIN gate
The two `system` turns ("hi, how can I help ." and "what city .") merged into ONE agent turn.
Say in a sentence why merging same-speaker turns is *required* before computing barge-in — and
not just a nicety. (Connect it to the definition: FTO = `next.start_ms − prev.end_ms` between
*different* speakers.)
'''))
C.append(md('''
## ACT 2 knowledge-flow checkpoint — what changed in your head?

Before Act 2: "normalize" was a black box you trusted. After Act 2: it is **five concrete
moves** you have performed by hand on two fake vendors and one real-shaped one — extract, map
speaker, one clock, sort+id, stamp+validate. You also met the two opposite traps: Bolna hides
timing (read `/log`, not the transcript); Cartesia hides the user (agent-only, be honest about
the missing side). Same schema came out every time. That repeatability **is** provider-neutrality.
'''))
C.append(code('''
# YOUR TURN - learning log, Act 2.
clean_sentence_act_2 = ""   # your one-liner for Act 2 (the five moves / the two traps - your pick)

if len(clean_sentence_act_2.strip()) < 15:
    print("write your Act-2 sentence above, then re-run.")
else:
    print("ACT 2 LOGGED:", clean_sentence_act_2)
'''))

# ============================================================ ACT 3 · STRESS
C.append(md('''
# Act 3 — Stress: break the adapter, meet the timing trap, debug it

## Break-it philosophy
An adapter that only works on clean input is not an adapter — it is a demo. Real vendor
payloads arrive malformed: an unsorted log, a missing speaker, a string where a number should
be. We now damage things ON PURPOSE so you have met these failures *before* a sponsor's live
data hands them to you on stage.
'''))
C.append(md('''
## PREDICT
The whole system trusts that turns are **sorted by start_ms**. Suppose a vendor's log arrives
out of order and our adapter **forgets to sort** (skips MOVE 4). When `turn_metrics` computes
`fto = next.start_ms − prev.end_ms` on the unsorted turns: does it **crash**, or does it
**return a silently wrong number** (a negative "overlap" that is really just disorder)? Commit
to one.
'''))
C.append(code('''
# BREAK-IT (guided) - an unsorted call, run through the FTO core WITHOUT the sort move.
# This cell does NOT raise; it produces a believable, WRONG number. That is the danger.
def turn_metrics(turns):
    # The real signal math (SPEC §7.C). It assumes chronological order - it does NOT sort for you.
    out = []
    for a, b in zip(turns, turns[1:]):
        fto = b["start_ms"] - a["end_ms"]   # negative => overlap (barge-in), positive => gap
        out.append({"at_ms": b["start_ms"], "fto_ms": fto,
                    "overlap_ms": max(0, -fto), "gap_ms": max(0, fto)})
    return out

unsorted_turns = [
    {"turn_id": "t1", "speaker": "agent", "start_ms": 9000, "end_ms": 11000},  # OUT OF ORDER
    {"turn_id": "t2", "speaker": "user",  "start_ms": 1000, "end_ms": 3000},
]
# We deliberately skip the sort, simulating an adapter bug, and read the bogus "overlap".
bad = turn_metrics(unsorted_turns)
print("WITHOUT sorting, FTO core reports:")
for m in bad:
    print(f"  at {m['at_ms']}ms | fto={m['fto_ms']} | overlap={m['overlap_ms']} | gap={m['gap_ms']}")
print("note: a huge 'overlap' of", bad[0]["overlap_ms"], "ms - pure fiction from disorder, no crash.")
'''))
C.append(md('''
## Reading the failure (this is the silent kind)
No red traceback appeared. The cell ran "green". And it reported an **10000ms overlap** — a
barge-in so violent it would dominate any scorecard — that **never happened**. It is an
artifact of the two turns being in the wrong order. This is the failure mode the whole course
fears: not a crash, but a *plausible wrong number*. The fix is not in `turn_metrics`; it is in
the **adapter**, which must guarantee MOVE 4 (sort) so the core can stay sort-free and simple.
'''))
C.append(code('''
# The debug ritual, step 1: print the raw input. The bug is visible the instant you look.
print("raw turn order as received:")
for t in unsorted_turns:
    print(f"  {t['turn_id']} start={t['start_ms']}")

# The fix lives in the adapter's MOVE 4 - sort by start_ms - not in the math downstream.
fixed_turns = sorted(unsorted_turns, key=lambda t: t["start_ms"])
good = turn_metrics(fixed_turns)
print("AFTER the adapter sorts, FTO core reports:")
for m in good:
    print(f"  at {m['at_ms']}ms | fto={m['fto_ms']} | overlap={m['overlap_ms']} | gap={m['gap_ms']}")
print("the fictional overlap is gone; the real gap of", good[0]["gap_ms"], "ms is what actually happened.")
'''))
C.append(md('''
## CHECKPOINT 4 (out loud)
Why is it *correct* that `turn_metrics` does **not** sort its own input — why push that
responsibility onto the adapter? (Think about: where should an assumption be enforced, once,
so that everything downstream may rely on it for free?)
'''))
C.append(md('''
## A second break — the validation boundary

`pipeline/normalize.py` ends every adapter with `validate_call()`: it asserts the speaker is
`user`/`agent`, that turns are sorted, that `end_ms > start_ms` or is `None`. That assert is a
**fence at the boundary**. Below we feed it a call with a bad speaker label (a vendor sent
`"bot"` instead of `"agent"`) and watch the fence stop it — loudly, on purpose.
'''))
C.append(code('''
# A faithful miniature of validate_call() from pipeline/normalize.py - the boundary fence.
def validate_call(call):
    # Every required key must be present - downstream stays assumption-free because of this line.
    for k in ["call_id", "source", "language", "stress_profile", "workflow_type", "turns"]:
        assert k in call, f"missing field: {k}"
    last_start = -1
    for t in call["turns"]:
        # speaker MUST be in the two-value vocabulary; a vendor's 'bot'/'system' must be mapped
        # BEFORE here. If it reaches the fence unmapped, that is a bug we want to hear about now.
        assert t["speaker"] in ("user", "agent"), f"bad speaker: {t['speaker']}"
        assert t["start_ms"] >= last_start, f"unsorted at {t['turn_id']}"
        assert t["end_ms"] is None or t["end_ms"] > t["start_ms"], f"end<=start at {t['turn_id']}"
        last_start = t["start_ms"]
    return call

print("validate_call defined - the fence every adapter's output must clear")
'''))
C.append(code('''
# BREAK-IT (guided) - this cell is SUPPOSED to error. EXPECTED FAILURE FOR LEARNING.
# A vendor sent speaker="bot"; our adapter forgot to map it to "agent". The fence catches it.
bad_call = {
    "call_id": "x", "source": "bolna", "language": "en",
    "stress_profile": "clean", "workflow_type": "test",
    "turns": [{"turn_id": "t1", "speaker": "bot", "text": "hi", "start_ms": 0, "end_ms": 1000}],
}
# We call the fence on purpose - read the AssertionError, then we fix it in the next cell.
validate_call(bad_call)
print("this line never prints - the assert above stops execution")
'''))
C.append(md('''
## Reading the error (bottom-up)
The last line of the traceback says `AssertionError: bad speaker: bot`. That is the fence doing
its job: it refused to let an unmapped vendor label leak downstream, where some chart would
later silently drop "bot" turns or miscount speakers. A loud assert here costs you one minute;
a silent mis-mapped speaker costs you a wrong scorecard on demo day. **The fence converts a
silent future bug into a loud present one.**
'''))
C.append(code('''
# The fix: do the speaker mapping in the adapter (MOVE 2), where vendor vocabulary belongs,
# BEFORE the fence. Then the same call clears validation cleanly.
SPEAKER_MAP = {"bot": "agent", "system": "agent", "assistant": "agent",
               "caller": "user", "human": "user"}   # vendor labels -> our two-value vocabulary

def map_speaker(vendor_label):
    # .get with a default of the original lets already-correct labels pass through untouched,
    # while known vendor synonyms get normalized. Unknown labels still reach the fence and fail
    # loudly - which is what we want for a label nobody taught the adapter yet.
    return SPEAKER_MAP.get(vendor_label, vendor_label)

bad_call["turns"][0]["speaker"] = map_speaker(bad_call["turns"][0]["speaker"])
ok_call = validate_call(bad_call)   # now clears the fence
print("after mapping 'bot' -> 'agent', validate_call passed:", ok_call["turns"][0]["speaker"])
'''))
C.append(md('''
## CHECKPOINT 5 (out loud)
Recite the debug ritual you just used (print the input → find the unmapped label → fix it in
the adapter, not downstream). Then answer: a loud `AssertionError` at the boundary is
*friendlier* than what alternative — and why?
'''))
C.append(md('''
## YOUR break now
Author your own damage. Pick ONE thing an adapter could get wrong on a vendor payload — a
missing `end_ms`, a `start_ms` that is a string `"600"` instead of an int, a duplicate
`turn_id`, an empty `turns` list — predict exactly what `validate_call` (or `turn_metrics`)
will do with it, write the prediction as a comment, then break it and run.
'''))
C.append(code('''
# YOUR TURN - self-authored break-it.
# my prediction: <write here exactly what will happen and why, BEFORE you run it>

my_call = {
    "call_id": "mine", "source": "bolna", "language": "en",
    "stress_profile": "clean", "workflow_type": "test",
    "turns": [
        {"turn_id": "t1", "speaker": "agent", "text": "hi",   "start_ms": 0,   "end_ms": 1000},
        {"turn_id": "t2", "speaker": "user",  "text": "yeah", "start_ms": 1500, "end_ms": 2000},
    ],
}

# 1) damage ONE field here (uncomment & edit one, or write your own):
# my_call["turns"][1]["start_ms"] = "1500"        # a string where an int is required
# my_call["turns"][1]["end_ms"] = 1400            # end_ms <= start_ms
# my_call["turns"] = []                           # no turns at all

# 2) run it through the fence and the math, and compare reality to your written prediction.
#    We wrap in try/except so an unfilled or fixed cell still runs clean for the executor.
try:
    validate_call(my_call)
    print("validate_call: PASSED (no damage active, or your damage slipped past the fence)")
except AssertionError as e:
    print("validate_call: caught it ->", e)
'''))
C.append(md('''
## WRONG-INTUITION TRAP — the one this book is built to kill

**The wrong belief:** *"My pipeline reads from `data/normalized/`, so it is already
provider-neutral. Neutrality is a property of the folder."*

It is not. Neutrality is a property of the **boundary discipline**. The next cell shows a call
that *lives in the normalized folder shape* and *passes a shallow check* — yet a vendor quirk
leaked through the adapter into a field the core trusts. The folder did not save us. Run it,
and try to spot the leak BEFORE the reveal.
'''))
C.append(code('''
# This call looks normalized: right keys, right speaker values, sorted. A shallow check passes.
# But the adapter leaked a Bolna trap: it used post_dial_delay (PSTN ring/setup time, NOT
# conversation timing) as the first turn's start_ms. The shape is perfect; the NUMBER is poison.
leaky_call = {
    "call_id": "bolna_leak", "source": "bolna", "language": "en",
    "stress_profile": "clean", "workflow_type": "booking",
    "turns": [
        # start_ms=2200 is the post_dial_delay_ms - telephone setup time, not when speech began.
        {"turn_id": "t1", "speaker": "agent", "text": "Hello?", "start_ms": 2200, "end_ms": 4000},
        {"turn_id": "t2", "speaker": "user",  "text": "hi yeah", "start_ms": 4300, "end_ms": 5200},
    ],
}

# The shallow check: keys present, speakers valid, sorted. It PASSES - and proves nothing.
shallow_ok = (set(["call_id","source","language","stress_profile","workflow_type","turns"]).issubset(leaky_call)
              and all(t["speaker"] in ("user","agent") for t in leaky_call["turns"]))
print("shallow 'is it normalized?' check passes:", shallow_ok)

# But the user->agent latency we will report is measured from a fake clock origin:
gap = leaky_call["turns"][1]["start_ms"] - leaky_call["turns"][0]["end_ms"]
print("reported first gap:", gap, "ms - but the whole call's t=0 is the PSTN setup, not speech onset.")
'''))
C.append(md('''
## The reveal
The call had every right key and passed a shallow "is it normalized?" check. But the adapter
let a **Bolna trap** through: it seeded the clock with `post_dial_delay` (telephone ring/setup
time), so every timestamp in the call is offset by ~2.2 seconds of *nothing happening on the
call*. Latency and barge-in computed off that origin are quietly wrong. **Provider-neutrality
is not "the data sits in the normalized folder." It is "the adapter caught every vendor trap
before the boundary."** The folder is the destination; the discipline is the adapter. That gap
between *looks normalized* and *is correctly normalized* is exactly what book 28 means when it
insists you say "architecture fact, not slide claim."
'''))
C.append(code('''
# YOUR TURN - explain the trap in your own words, stored for future-you.
my_trap_explanation = ""   # one sentence: why does "it's in data/normalized/" NOT prove neutrality?

if len(my_trap_explanation.strip()) < 20:
    print("write your explanation above (20+ chars), then re-run.")
else:
    print("TRAP EXPLAINED:", my_trap_explanation)
'''))
C.append(md('''
## ACT 3 knowledge-flow checkpoint — what changed in your head?

Before Act 3: an adapter felt like plumbing that either works or crashes. After Act 3 you know
its two scariest failures are **silent**: an unsorted log invents a barge-in, and a leaked
vendor trap (post_dial_delay as t=0) poisons every timestamp while the shape stays perfect. You
also know where the fix lives — in the adapter and its boundary `validate_call`, never patched
downstream — and you can no longer be fooled by "it's in the normalized folder."
'''))
C.append(code('''
# YOUR TURN - learning log, Act 3.
clean_sentence_act_3 = ""   # your one-liner (the silent-wrong-number trap is a strong candidate)

if len(clean_sentence_act_3.strip()) < 15:
    print("write your Act-3 sentence above, then re-run.")
else:
    print("ACT 3 LOGGED:", clean_sentence_act_3)
'''))

# ============================================================ ACT 4 · OWNERSHIP
C.append(md('''
# Act 4 — Ownership: the contract, the real pipeline, and defending it

## The adapter contract (write this on the wall)

An adapter from any vendor `V` to `call_log` MUST guarantee, at the boundary:

1. **Speaker truth** — every `speaker` is `user` or `agent`; vendor labels are mapped, never
   passed through raw.
2. **One clock per call** — all `start_ms`/`end_ms` share a single origin = first real speech
   onset (NOT PSTN setup, NOT wall-clock).
3. **Sorted turns** — ascending `start_ms`, with `turn_id`s assigned after the final order.
4. **Honest `end_ms`** — a real offset when the vendor gives one; `None` when it does not
   (latency-only treatment, never a faked overlap).
5. **Provenance kept, behavior unchanged** — `source` + `metadata` record where it came from;
   nothing downstream branches on that.

If all five hold, every downstream tool (`pipeline/signals.py`, `pipeline/judge.py`,
`pipeline/score.py`) runs vendor-blind. That blindness is the product.
'''))
C.append(md('''
## Where this lives in the real repo

- `pipeline/normalize.py` — the real adapters. `spokenwoz_call()` (speaker from `tag`, timing
  from word-level ASR times, same-speaker merge, deterministic `stress_profile`) and
  `cmd_hero()` (validates `data/hero/turns.json` into the pool). `validate_call()` is the fence.
- `schemas/call_log.md` — the index card every adapter targets.
- `data/normalized/*.json` — the 11 real outputs (hero + 10 SpokenWOZ) that all downstream
  code reads. The Bolna path (SPEC §7.G) is the bonus: same five moves, `/log` for timing.
- The honest line in code, verbatim from `normalize.py`: *"Downstream code never knows the
  vendor."*

You did not learn a toy. You re-derived the exact discipline that file encodes.
'''))
C.append(code('''
# Let's confirm the claim against the REAL repo output: load the actual normalized pool and show
# that every file - hero + SpokenWOZ, different original vendors - has the identical schema shape.
import json
from pathlib import Path

# Find the repo root by walking up to the folder that holds data/normalized (works from anywhere).
root = next(a for a in [Path.cwd(), *Path.cwd().parents] if (a / "data" / "normalized").exists())
norm_dir = root / "data" / "normalized"
files = sorted(norm_dir.glob("*.json"))
print("real normalized calls on disk:", len(files))
print("sources represented:", end=" ")
sources = sorted({json.loads(f.read_text())["source"] for f in files})
print(sources)
'''))
C.append(code('''
# Now prove provider-neutrality is an ARCHITECTURE FACT, not a claim: every real file exposes
# the exact same key set, so no downstream code could branch on vendor even if it wanted to.
shapes = set()
for f in files:
    call = json.loads(f.read_text())
    # we record the top-level key set of each real call; if neutrality holds, there is ONE shape.
    shapes.add(frozenset(call.keys()))

print("distinct top-level call_log shapes across the WHOLE real pool:", len(shapes))
print("provider-neutral by construction:", len(shapes) == 1)
# This is the cell you point at on stage instead of saying the word "neutral".
'''))
C.append(md('''
## PREDICT (course-level)
You just saw the real pool has **one** shape. Suppose the hackathon ends and a Bolna engineer
hands you 500 live execution logs. To ingest them, how many of the five downstream tools
(`signals`, `judge`, `score`, `dpo_export`, the dashboard) must you **modify**? Write your
number and why in the next cell.
'''))
C.append(code('''
# YOUR TURN - your course-level prediction, stored for your own defense prep.
my_downstream_edits = None   # <- how many downstream tools need changing to add Bolna ingest?
my_reason = ""               # <- one line: why that number

if my_downstream_edits is None or len(my_reason.strip()) < 10:
    print("fill in the number AND a one-line reason above, then re-run.")
else:
    print("locked:", my_downstream_edits, "downstream edits because:", my_reason)
    # The intended answer is 0: you write ONE new adapter (bolna_call) feeding the same schema;
    # signals/judge/score/dashboard already read call_log and never learn the vendor.
    print("(intended answer: 0 - you add ONE adapter; the schema absorbs the rest.)")
'''))
C.append(md('''
## The concept at three levels (say each in one breath)

- **To a beginner:** "Different companies send call data in different shapes. We translate
  every shape into one standard form first, so the rest of our tools only ever see that one
  form."
- **To an engineer:** "One adapter per provider, `raw -> call_log`; the adapter is the sole
  owner of vendor vocabulary and quirks (Bolna timing from `/log`, not the scrubbed
  transcript; map `tag`/`bot` to `user`/`agent`; one ms-clock; sort; honest null `end_ms`). A
  boundary `validate_call` fences it. Downstream is vendor-blind, so adding a provider is one
  new function, zero edits elsewhere."
- **To a founder:** "We are a layer above the providers, not a feature of one. Any vendor's
  logs flow into the same evals — provider-neutral and sponsor-compatible, and it is true in
  the code, not just the deck."
'''))
C.append(md('''
## Defense questions (×3, answers below each — try first)

**1. "You say provider-neutral — prove it's not just a slide."**
<details><summary>answer</summary>I point at the normalized pool: every file, regardless of original vendor, has one identical key set, and every downstream tool reads only that schema with zero vendor branches. Neutrality is the adapter discipline plus the one-shape pool — a fact you can grep, not a claim.</details>

**2. "Bolna gives you a full transcript — why not just score that?"**
<details><summary>answer</summary>Because the top-level transcript has no roles and no timing, and 'precise' mode deletes the interrupted words — so barge-in and latency are uncomputable or wrong from it. We read timing from the `/log` component events (transcriber-response→user, llm/synthesizer→agent) and ignore the transcript string for timing.</details>

**3. "What breaks if an adapter is sloppy, and how would you even notice?"**
<details><summary>answer</summary>Silent wrong numbers: an unsorted log fabricates a barge-in; using post_dial_delay as t=0 offsets every timestamp. The shape still looks normalized, so a shallow check passes. We notice via the boundary `validate_call` (loud asserts on speaker/order/end_ms) and by never seeding the clock from PSTN setup — the fence turns a silent future bug into a loud present one.</details>
'''))
C.append(md('''
## ACT 4 knowledge-flow checkpoint — what changed in your head?

You should now hold: the five-point **adapter contract**, where it lives in the real repo
(`pipeline/normalize.py`, `schemas/call_log.md`, `data/normalized/*.json`), the proof that the
real pool has exactly one shape, the three-level explanation, and three defense answers. You
can now say "provider-neutral" and back it with a cell, not a slide — which is precisely what
book 28 (talking like an engineer) will drill you to do under sharp questions.
'''))
C.append(md('''
## TEACH-BACK GATE — the pass bar for this book

**Close this notebook.** Two minutes, out loud, no peeking. Hit all five:
1. The one atomic idea (provider-neutrality = normalizing every source to one schema).
2. The **five moves** every adapter performs (extract turns · map speaker · one clock · sort+id · stamp+validate).
3. The **two opposite traps** you met: Bolna (timing in `/log`, never the scrubbed transcript) and Cartesia (agent-only, be honest about the missing user side).
4. The **silent failures** an adapter can cause (unsorted log → fake barge-in; post_dial_delay as t=0 → poisoned clock) and where the fix lives (the adapter + `validate_call`, never downstream).
5. The **adapter contract**'s five guarantees — and why they buy the whole downstream its vendor-blindness.

Could not hit all five? Open it back up, find the gap, redo that act. That is the system working.
'''))
C.append(code('''
# YOUR TURN - final learning log: Act 4 sentence + YOUR clean sentence for the whole book.
clean_sentence_act_4 = ""   # one-liner for Act 4 (the contract / where it lives)
my_clean_sentence = ""      # the sentence you'd say in a room about provider adapters

if len(clean_sentence_act_4.strip()) < 15 or len(my_clean_sentence.strip()) < 15:
    print("write both sentences above, then re-run.")
else:
    print("ACT 4 LOGGED:", clean_sentence_act_4)
    print("YOUR CLEAN SENTENCE:", my_clean_sentence)
'''))
C.append(md('''
## The book's clean sentence (read only after writing yours)

> **"Provider-neutral is an architecture fact, not a slide claim."**

If yours captures that — that neutrality is *earned* by writing one adapter per vendor that
funnels every shape into a single schema, proven by a pool with exactly one shape and tools
that never name a vendor — this book did its job.
'''))
C.append(code('''
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "27_provider_adapters.ipynb"   # this notebook's filename
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

**27 done** (pending your teach-back) → **28 · Talking like an engineer, not a bluffer** — you
now hold the *fact* of provider-neutrality (one adapter per vendor, one schema, a one-shape
pool). Book 28 turns that fact into *spoken defense*: the honest lines, drilled, and sharp-
question practice — so when a founding engineer asks "prove it's neutral," you reach for the
cell, not the adjective. The funnel you built here is the thing you will defend there.
'''))

nb = {"cells": C,
      "metadata": {"kernelspec": {"display_name": "Python 3 (.venv)", "language": "python",
                                  "name": "python3"},
                   "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 5}
out = HERE / "27_provider_adapters.ipynb"
out.write_text(json.dumps(nb, indent=1))
md_n = sum(1 for c in C if c["cell_type"] == "markdown")
print(f"wrote {out.name}: {len(C)} cells ({md_n} md, {len(C) - md_n} code)")
