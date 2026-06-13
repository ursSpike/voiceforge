# Clinic Demo Script v2 — Hinglish Appointment Agent + VoiceForge

**Status:** PLAN / READ-ALOUD SPEC. Not a deployment artifact.
Do NOT overwrite `docs/demo_docs.md` (that is the prior eval-lab v1).
Do NOT modify Bolna config from this file. Do NOT place live calls from this file.
**Integration gate:** this is the read-aloud spec for Spike. Surface (`/`, `/platform`) is updated
ONLY after Codex confirms the agent id, KB upload, and first `/executions/{id}` schema.

**Slot:** 10 minutes total · ~6:30 spoken (390s) + ~3:30 Q&A (~210s).
**You:** Saivarshith — "Spike". Solo build. The clinic / diagnostic-lab appointment agent is the
submission. VoiceForge is the Impact / Scale-Up edge.

**Rubric you are being scored on, verbatim from `hackathon.md`:**
1. **Problem Applicability** — "Is the problem real, specific, and commercially meaningful?"
2. **Cartesia & Bolna Usage** — "Did you use the platform fully? … Cartesia voice selection and
   meaningful use of Bolna's Agent Builder features — knowledge base, custom analysis, variables,
   and call flow design."
3. **Multilinguality** — "Does the agent handle India's real linguistic diversity? … language
   detection, natural mid-conversation switching … accent handling."
4. **Scale-Up Plan** — "What baseline metric are you beating? How would you measure success at
   scale? What's a realistic 30-day improvement?"
5. **Agent Quality** — "Judges will test it live. … Handle the core flow, manage realistic edge
   cases, recover from unexpected input, and feel natural — not scripted."

---

## HOW TO READ THIS FILE (10 seconds, then forget it)

- **Bold** = lean on these words.
- `[PAUSE]` = one silent breath. Replaces every "uhh" / "um."
- `[SLOW — explain mode]` = drop pace; you're teaching a non-engineer.
- `[PUNCH]` = signature line; say it like you mean it, then `[PAUSE]`.
- `[LOOK UP]` = eyes off the screen, meet the room.
- **WHAT THIS MEANS** boxes are for *you* (you skipped the notebooks). Do not read aloud.
- The clock on each beat is cumulative spoken seconds.

**Mind-blank rescue line (say this, breathe, move on):**
*"The agent is a Hinglish appointment scheduler for a clinic. VoiceForge measures whether each call
actually booked. Together that's a working product and a measured improvement loop."*

---

# BEAT 1 — Self-intro + the problem (clinics lose patients to missed calls)
**Budget: 40s · Clock: 0:40**

> Spoken:

"[LOOK UP] One opening question. [PAUSE]
A clinic's phone rings. **Half the time nobody picks up.** Reception is busy, it's after-hours, the
front desk is on another call. **Every missed call is a lost patient and lost revenue.** [PAUSE]

That's not a niche problem. It's **every clinic and diagnostic lab in India**. And the callers are
**natively multilingual** — they'll switch Hindi to English mid-sentence without thinking. [PAUSE]

I'm **Saivarshith** — call me **Spike**. CSE, **IIT Kharagpur** '25. SDE at **Fujitsu Research**.
Built this **solo**. [PAUSE]

[PUNCH] **I built a Hinglish appointment-booking agent for clinics and diagnostic labs — and the
measurement layer that proves it actually books patients.** [PAUSE]
That's the submission, and that's the edge."

> **WHAT THIS MEANS:** Problem-first cold open, then who you are, then the thesis. The agent is the
> submission (scored on Quality/Cartesia+Bolna/Multilinguality/Problem). VoiceForge is the
> Scale-Up + Impact differentiator — *measurement nobody else in the room has*. Do NOT say
> "savings" — say "lost patients and lost revenue" (that's the qualitative claim; numbers come from
> the measurement layer).

---

# BEAT 2 — The agent: Hinglish, Cartesia, no-medical-advice
**Budget: 45s · Clock: 1:25**

> Spoken:

"Here's what the agent does. [PAUSE]
[SLOW — explain mode] Inbound call comes in. The agent greets in Hinglish, **mirrors whatever the
caller speaks** — Hindi, English, or mid-sentence switching. It collects one thing at a time:
**patient name, phone, service requested, preferred date, preferred time.** Then it reads the full
appointment back and gets an explicit yes before ending. [PAUSE]

Voice: **Cartesia — Devansh, Sonic-3.** Calm, warm, Indian — picked deliberately for a healthcare
context. The config proves it. [PAUSE]

And the line that separates this from a toy. [LOOK UP]
[PUNCH] **It is a scheduler, not a clinician.** If a caller asks for a diagnosis or medical advice,
it **refuses safely** and offers to book a consultation. Never takes payment. Never invents a slot. [PAUSE]

That's a real commercial workflow with a real guardrail."

> **WHAT THIS MEANS:** This beat sets up Quality and Cartesia in one move. The voice rationale
> (calm/warm/Indian for healthcare) is the *deliberate selection* the rubric scores. The no-medical-
> advice stance is your honesty + safety in one breath — and it's one of the 5 live scenarios. Voice
> proof: `out/bolna_cartesia_proof.json` → agent `199b03e7…`, synthesizer `cartesia`, voice
> `Devansh`, model `sonic-3`. Do not say "HIPAA-ready." Do not say "clinical-grade."

---

# BEAT 3 — Bolna platform usage (criterion-aligned, explicit)
**Budget: 40s · Clock: 2:05**

> Spoken:

"Where does Bolna show up? [PAUSE]
[SLOW — explain mode] Five places, explicit. [PAUSE]
**One — Knowledge Base:** services, tests, doctors, hours, prep instructions, FAQ. The agent
answers info questions from this, then offers to book. [PAUSE]
**Two — Variables:** clinic name, city, hours — so the same agent re-skins to a different clinic
without a prompt rewrite. [PAUSE]
**Three — the Book-Appointment tool / call-flow:** the booking action, not a free-text promise. [PAUSE]
**Four — Extractions:** structured `extracted_data` — patient_name, phone, service, date, time,
booking_confirmed — returned on every execution. [PAUSE]
**Five — Hinglish ASR (transcriber `multi`):** so mid-call code-switching isn't dropped on the floor. [PAUSE]
[PUNCH] **Not a bare prompt. The platform, used.**"

> **WHAT THIS MEANS:** This beat directly answers the Cartesia & Bolna Usage rubric bullets — KB,
> variables, call-flow, custom analysis (Extractions). Extractions are also the bridge to the eval
> layer: VoiceForge fetches `/executions/{id}` and gets `extracted_data` for free — the agent's own
> structured outcome, with Bolna's confidence. Five fingers, five features, one breath each.

---

# BEAT 4 — LIVE AGENT — actual call (the centerpiece)
**Budget: 105s · Clock: 3:50**

> Spoken:

"Now — the live call. [LOOK UP] [PAUSE]
This is the agent on my number, on the venue network, right now. I'll book one appointment. [PAUSE]

[Spike dials. Speakerphone on. Two scenarios to choose live — pick by feel of the room:]

**Path A (Happy path, English-leaning):** *"Hi, I'd like to book a blood test for tomorrow
morning."* → agent collects name → phone → confirms test → offers a slot → reads back → caller says
yes → clean exit.

**Path B (Hinglish switch — preferred if the room looks technical):** Start in English, switch to
Hindi mid-call (*"Actually, kal subah ka time mil jayega?"*), let the agent mirror. Same booking
outcome.

[After the call ends:] [LOOK UP] [PAUSE]
[PUNCH] **That call just produced a structured booking — patient, phone, service, date, time,
confirmed — extracted by Bolna, on the same `/executions/{id}` endpoint VoiceForge reads from.**
Watch."

> **WHAT THIS MEANS:** This is **the** Agent-Quality moment. You score live here. Pick ONE scenario,
> not three — judges have a rubric, not patience. Happy-path is the safest; Hinglish-switch is the
> highest-ceiling because it doubles as Multilinguality proof in one demo.
>
> **Stop-condition / recovery (rehearse this verbatim):** if the call fails to connect, freezes, or
> the agent loops — wait 8 seconds, then say:
> *"The venue network just bit me. I'll show you a cached call from this morning — same agent, same
> Cartesia voice, same Extractions surface — and we'll watch the live one again at the end if there's
> time."*
> Then open `/platform` Live Today and walk a cached row. **Never fake a call. Never narrate over
> silence.** A clean recovery line is itself an Agent-Quality signal — the *audience's* perception
> of quality.

---

# BEAT 5 — Open /platform, show the extraction
**Budget: 55s · Clock: 4:45**

> Spoken:

"This is `/platform` — VoiceForge's operator view. The call I just ran is the top row, **LIVE ·
UNCALIBRATED.** [PAUSE]

[SLOW — explain mode] Look at the extracted data: **patient_name, phone, service, date, time,
booking_confirmed.** Bolna's own confidence on each field. **That's the agent's structured
outcome — not a transcript guess.** [PAUSE]

Underneath, the deterministic signals VoiceForge added: **latency gaps, barge-in events** — pure
timestamp math, no judge involved. [PAUSE] [LOOK UP]

[PUNCH] **Bolna books the appointment. VoiceForge proves the booking happened — and tells you
whether it happened cleanly.** [PAUSE]
Two surfaces, one truth."

> **WHAT THIS MEANS:** This is where Bolna Extractions stops being a bullet point and becomes the
> product. The fields are the agent's *job* (§3 of TARGET_AGENT). The deterministic overlay is
> VoiceForge's *job*. **Honesty invariant:** the row says `LIVE · UNCALIBRATED` — never say or
> imply this is calibrated. Calibration belongs to the frozen 46-call slice (next beat).

---

# BEAT 6 — Eval layer: judge with citations, calibrated separately
**Budget: 55s · Clock: 5:40**

> Spoken:

"And here's how I keep myself honest. [PAUSE]
[SLOW — explain mode] On top of those deterministic signals, an **LLM judge** scores five
dimensions — language match, faithfulness, repair quality, conciseness, frustration. Temperature
zero. **Every score must cite the turn it came from.** Validated before it ever hits cache. [PAUSE]

Now the boundary — and this is the slide I care most about. [LOOK UP]
The live calls are **`LIVE · UNCALIBRATED`** — a separate lane. They are the **use-case proof**. [PAUSE]
The **methodology proof** is a different artifact: **46 frozen calls, blind-labeled before the judge
ran**, Cohen's κ **0.206**, balanced accuracy **0.628**, failure recall **0.50**. **n=45**. [PAUSE]
[PUNCH] **Measured, not assumed. A team trusting this judge blind would be wrong on 13 of 45
calls — and I can tell them which 13.** [PAUSE]
Today's live calls don't touch that calibration. Ever."

> **WHAT THIS MEANS:** Two lanes, hard wall between them. Live = LIVE·UNCALIBRATED. Frozen 46 =
> the κ machinery. The κ number sounds low; that's the prevalence-paradox honesty move (82%
> successes mechanically crush κ). You report balanced accuracy and failure recall *because* κ is
> compressed. If asked: language is NOT the reliability axis — hi-en 71% ≈ English 69% on this
> sample; *confidence* is (high 83% vs medium 50%). Honesty kill-list reminder: never say
> "calibrated live."

---

# BEAT 7 — Scale-Up: baseline + measurement + 30-day loop
**Budget: 45s · Clock: 6:25**

> Spoken:

"Scale-Up. [PAUSE]
[SLOW — explain mode] **Baseline metric: appointment-booking rate** — the percentage of inbound
calls that end in a confirmed appointment. That's the number a clinic actually cares about, and
it's what I optimize. [PAUSE]

VoiceForge measures it three ways at once. **Bolna Extractions** give the structured booking
outcome. **Deterministic signals** flag the calls that booked but had friction — brittle successes
the dashboard hides. The **improvement queue** ranks the failure phenotypes by call count and
estimated exposure, and writes the fix. [PAUSE]

A 30-day loop: ingest each day's executions, surface the top phenotype, ship a targeted prompt
edit, re-measure. **Top current fix in my frozen slice: `poor_clarification_or_recovery`, 11
calls.** [PAUSE] [LOOK UP]
[PUNCH] **Baseline, measured. Failure, named. Fix, ranked. That's a 30-day improvement loop —
not a slide.**"

> **WHAT THIS MEANS:** This is the Scale-Up beat in rubric language. Baseline = appointment-booking
> rate (TARGET_AGENT §2). Measurement = three lanes (Extractions / deterministic / judge w/
> calibration). 30-day loop = improvement queue (real artifact: `fix_first.phenotype_id =
> poor_clarification_or_recovery`, 11 calls, est. exposure $0.47 in slice, $10.44 per 1,000 modeled).
> Use the word **"estimated exposure,"** never "savings." Production gaps are explicit (next beat /
> Q&A): webhooks, redaction, consent, second rater, real billing.

---

# BEAT 8 — Close
**Budget: 10s · Clock: 6:35**

> Spoken:

"[LOOK UP] [PAUSE]
Thank you to **Bolna** and **Cartesia** — the platform and the voice. [PAUSE]
[PUNCH] **A Hinglish appointment agent that books patients. And the measurement layer that proves
it.** [PAUSE]
I'd love your questions."

> **WHAT THIS MEANS:** Close on the thesis verbatim. It bookends Beat 1. Then shut up.

---

**Spoken total: 40 + 45 + 40 + 105 + 55 + 55 + 45 + 10 = 395s ≈ 6:35 minutes.**
**Remaining for Q&A: ~3:25.**

---

# Q&A BANK — labeled by rubric category

Rule: **2 lines per answer, then stop.** If you don't know: *"I haven't measured that — here's how
I'd find out."*

## CATEGORY 1 — Problem Applicability (5 questions)

**P1. "How real is this problem? Sized?"**
"Clinics and diagnostic labs across India miss a large share of inbound appointment calls —
reception busy, after-hours, understaffed. I am not claiming a measured market size; I am claiming
a workflow every clinic owner recognizes and can name today."

**P2. "Why voice — why not WhatsApp or a booking form?"**
"Because patients **call** to book. It's the native channel — older patients, low-literacy callers,
urgent requests, mid-call clarification ('does this need fasting?'). A form can't ask back. A voice
agent can."

**P3. "Is the scope specific or generic?"**
"Specific: **inbound appointment booking** for a clinic or diagnostic lab. Not triage, not symptom
intake, not payments. One workflow, one job, with an explicit no-medical-advice guardrail."

**P4. "Why India specifically?"**
"Because the callers are natively code-switching Hinglish, the staffing pressure on small clinics
is acute, and voice is overrepresented as a channel. An English-only agent doesn't survive a real
inbound queue here."

**P5. "Who buys this — clinic or platform?"**
"Two-sided: a clinic chain buys it as receptionist overflow; a voice platform like Bolna embeds it
as a vertical template. Either way, the buyer's number is the same — appointment-booking rate."

## CATEGORY 2 — Cartesia & Bolna Usage (5 questions)

**B1. "Why this Cartesia voice?"**
"**Devansh on Sonic-3** — picked by ear for a calm, warm, Indian register. Healthcare calls reward
calm over energetic; the first impression sets whether the caller trusts the agent enough to give
their phone number. Config in `out/bolna_cartesia_proof.json`."

**B2. "Which Bolna features did you actually use, and why?"**
"**Knowledge Base** (services / hours / prep / FAQ), **Variables** (re-skinnable per clinic), the
**Book-Appointment call-flow** (action, not promise), **Extractions** (structured outcome on every
execution), and **transcriber `multi`** for Hinglish ASR. Not a bare prompt."

**B3. "Why a KB and not just stuff it all in the prompt?"**
"Two reasons. The KB is **retrieved per turn**, so updating clinic hours doesn't require a prompt
deploy. And it keeps the system prompt focused on **behavior** — language mirroring, no medical
advice, one-question-at-a-time — instead of facts."

**B4. "How do Extractions plug into the eval loop?"**
"Bolna returns `extracted_data` on `GET /executions/{id}` — patient_name, phone, service, date,
time, booking_confirmed, plus a confidence per field. VoiceForge reads that endpoint, so the
agent's own structured outcome **is** the booking-rate signal — no transcript regex required."

**B5. "Why not build your own platform layer?"**
"Because Bolna already solved the call layer. The post-call eval and improvement loop is the gap.
Building on Bolna means a clinic deploys the agent on Day 1, not Day 90 — and VoiceForge ships as
the quality surface, not a competing stack."

## CATEGORY 3 — Multilinguality (5 questions)

**M1. "How does the agent actually handle Hinglish?"**
"Transcriber is set to `multi` (Deepgram code-switch), and the prompt explicitly mirrors the
caller's language — Hindi→Hindi, English→English, mixed→mixed, **never switching to a language the
caller hasn't used.** That last rule is the one most agents get wrong."

**M2. "Does it follow mid-call language switches?"**
"Yes — that's exactly the second of my five test scenarios, and one option in the live demo. The
mirroring rule is in the system prompt and the transcriber doesn't lock to a single language at
session start."

**M3. "How do you score multilinguality beyond 'it spoke Hindi'?"**
"Two ways. **Deterministic:** language mismatch is a tag in the failure phenotype set
(`wrong_language_or_tone` — currently 4 of my 45 labeled calls). **Judge dimension:** language
match is one of the five scored dimensions, evidence-cited at turn level."

**M4. "How did Hinglish perform in your calibration?"**
"Honest finding — language was NOT the reliability axis. hi-en agreement was **71%**, English was
**69%** — statistically indistinguishable on this sample (n=45). The axis that actually predicts
agreement is annotator confidence (83% high vs 50% medium). I report it because it surprised me."

**M5. "What about accents — Telugu speaker switching into Hinglish, for example?"**
"Honest answer: I have not measured per-accent agreement on this build — n=45 doesn't support a
per-accent slice. Production needs labeled Tamil/Telugu/Kannada-into-Hinglish samples and a second
rater on each. That's a concrete next step, not a hand-wave."

## CATEGORY 4 — Scale-Up Plan (5 questions)

**S1. "What baseline metric are you beating?"**
"**Appointment-booking rate** — percent of inbound calls that end in a confirmed appointment,
measured from Bolna's `booking_confirmed` extraction. It's the number a clinic owner already
tracks manually; the agent is judged against the baseline of 'we miss this call.'"

**S2. "How do you measure success at scale?"**
"Three lanes feeding one number: Bolna Extractions give the structured outcome,
deterministic-timing flags brittle bookings, and the calibrated judge scores semantic quality on a
sample. Aggregate booking-rate, brittle-success share, and friction-or-failure spend share — daily."

**S3. "What's a realistic 30-day improvement?"**
"Pick the top phenotype in the improvement queue, ship a targeted prompt edit, re-measure on the
next week's executions. My frozen slice's top fix is `poor_clarification_or_recovery`, 11 calls,
estimated exposure $0.47 in slice, $10.44 per 1,000 calls modeled. That's the loop, monthly."

**S4. "What does this need to be production-ready?"**
"Four concrete gaps and I'll name them: **Bolna webhooks** (replace polling),
**PII redaction + consent capture** before any judging or storage,
**a second rater** to lift κ off a single-rater pilot,
**real per-call billing telemetry** to replace estimated exposure with measured spend."

**S5. "Doesn't a 1-person prototype melt under real volume?"**
"The pipeline is batch, async-ready, cache-keyed per call and per dimension — re-runs are nearly
free. The calibration protocol is what actually has to scale, and the booth, validator, and κ
machinery don't care if n is 45 or 4,000. Webhooks replace polling for live ingestion."

## CATEGORY 5 — Agent Quality (5 questions)

**Q1. "How does it handle the five live scenarios?"**
"**Happy path** — collects, confirms, reads back, exits clean. **Hinglish switch** — mirrors.
**Ambiguous request** — asks one specific clarifying question naming the unclear slot.
**Caller changes detail** — updates the field, re-confirms. **Medical-advice request** — refuses
safely, offers a consultation booking. All five are in the prompt and the live test."

**Q2. "What about interruptions and recovery?"**
"Bolna's endpointing + the prompt's short-turn rule handle natural turn-taking; the agent recovers
when a caller talks over it. **Important honesty:** that's an **Agent-Quality** signal observed in
the demo — VoiceForge does not claim live barge-in detection, because Bolna's web-call trace
doesn't expose interruption telemetry."

**Q3. "Show me the no-medical-advice refusal."**
"Built into guardrails — '*you are a scheduler, not a clinician. Never diagnose, interpret
symptoms, or recommend medication. Offer to book a consultation or route to a human.*' One of the
five live scenarios — happy to trigger it on a second call if there's time."

**Q4. "What fails today — honestly?"**
"Three things. **Per-call billing** is estimated exposure, not measured spend. **Live calls** are
`LIVE · UNCALIBRATED` — I do not blend them into κ. **Single-rater calibration** at n=45 — the CI
includes zero. All three are labeled in the product, not hidden."

**Q5. "If I called this agent at 2 AM tomorrow, what would I get?"**
"A booking, in Hinglish, with structured `extracted_data` on the execution endpoint. What you
**wouldn't** get: medical advice, an invented slot, a card-payment ask. What I **wouldn't**
silently claim afterwards: that the call was calibrated — it would land in the LIVE·UNCALIBRATED
lane in `/platform`, separate from the frozen calibration."

---

# HONESTY KILL-LIST (Spike must NEVER say these)

These are tripwires. Saying any of them once is a credibility hole.

- "savings" → **say "estimated exposure"**
- "calibrated live" → live = **LIVE · UNCALIBRATED**, frozen 46 = calibrated
- "live barge-in" → **Agent-Quality signal only**; no VoiceForge claim on live
- "HIPAA-ready" → **never**; production needs consent + redaction (state it)
- "clinical-grade" → **never**; the agent is a scheduler, not a clinician
- "diagnosed" → the agent **refuses to diagnose**
- "76 provider calls" → corpus is **76 calls total, 46 timed**, not all from one provider
- "every transcript is real" → **the hero call is constructed** and disclosed; SpokenWOZ is public
- "least reliable exactly there" → on language: **hi-en (71%) ≈ English (69%)** — language is NOT
  the reliability axis; **confidence is** (83% vs 50%)

If a kill-list word slips: **stop, correct in-line, move on.** Do not apologize at length.

---

# 3-MINUTE STAGE VERSION (compressed sibling — same beats, 180s)

Use this if pulled into the 3-minute Top-10 slot at 4:40 PM (per `hackathon.md` schedule).

**Beat A — Problem (25s · 0:25)**
"Clinics lose patients to missed inbound calls. Voice is the native channel; Indian callers
code-switch Hinglish without thinking. I built a Hinglish appointment agent — and the measurement
layer that proves it books patients. I'm Spike."

**Beat B — Workflow (25s · 0:50)**
"Inbound call → mirrors the caller's language → collects name, phone, service, date, time → reads
back → confirms. Cartesia Devansh on Sonic-3 — calm, warm, Indian. Bolna KB, Variables,
Book-Appointment flow, Extractions, multi-language transcriber. **Scheduler, not clinician** —
refuses medical advice safely."

**Beat C — Live agent (60s · 1:50)**
[Dial. One scenario — happy-path booking OR Hinglish switch. Same recovery line as Beat 4 if it
fails. After the call:] "Structured booking just landed on `/executions/{id}`."

**Beat D — Impact on /platform (60s · 2:50)**
"Here it is in `/platform` — `LIVE · UNCALIBRATED`. Extracted fields with Bolna's confidence.
Deterministic latency/barge-in overlay. Baseline metric: appointment-booking rate. 30-day loop:
top phenotype `poor_clarification_or_recovery`, 11 calls in my frozen slice, targeted fix written.
The frozen 46-call calibration — κ 0.206, balanced acc 0.628 — is methodology proof, separate
lane."

**Beat E — Close (10s · 3:00)**
"Thanks Bolna and Cartesia. An agent that books, and the layer that proves it. Questions."

---

# INTEGRATION GATE (read this before touching anything)

This file is the **spec for Spike's read-aloud**, not a deployment.

- Do NOT replace `docs/demo_docs.md` (that is the prior eval-lab v1 — kept for fallback).
- Do NOT update the `/` or `/platform` surface from this file. Surface updates wait on Codex's
  confirmation of:
  1. **agent id** (final clinic agent, not the prior eval-lab agent),
  2. **KB upload acknowledged** by Bolna and reachable in agent config,
  3. **first `/executions/{id}` schema** observed live — specifically that `extracted_data`
     contains the six fields claimed in Beat 5 (patient_name, phone, service, date, time,
     booking_confirmed) with confidence values.
- Do NOT place live calls from this file. Live calls follow `SPRINT1_RUNBOOK.md`.
- If any of the three gate conditions fail, Spike falls back to the v1 `docs/demo_docs.md` script
  unchanged and the `/platform` Live Today row reads from cached executions only.

---

# OFFLINE FALLBACK (if everything breaks)

1. `out/dashboard.html` — self-contained, no network.
2. `out/demo_report.html` — same numbers, static.
3. Cached `/platform` view with frozen-slice rows only — explicitly note the live lane is empty
   today.

**The numbers are the demo, not the live server.**

---

# THE NUMBERS YOU MUST NOT MISQUOTE (cheat strip)

Artifact-backed only. Source in parentheses.

- Corpus: **76** calls · **46** timed · **30** unmeasured (`out/analytics.json`).
- Heuristic agreement: **25/45** = 56% · **missed 13** real successes · **passed 7 of 8**
  failures (`demo_report_data.json:metric_trap`).
- Labels: **46** labeled · **45** binary · **37** success / **8** fail / **1** unsure.
- Calibration: **κ 0.206** · CI **[-0.108, 0.499]** · raw agreement **0.711** · balanced
  accuracy **0.628** · failure recall **0.50** · n=**45** (`demo_report_data.json:calibration`).
- Language slice: hi-en **71%** (22/31) ≈ English **69%** (9/13) — indistinguishable.
- Confidence slice: high **83%** (24/29) vs medium **50%** (8/16) — the real axis.
- Archetypes: seamless **25** · brittle **5** · recovered **7** · slot-loss **3** · workflow **5**.
- Fix-first: `poor_clarification_or_recovery` · **11** calls · est. exposure **$0.47** in slice ·
  **$10.44 per 1,000 calls modeled** (`demo_report_data.json:product.fix_first`).
- Failure events: latency_gap **×183** · barge_in **×107** (`analytics.json:failure_clusters`).
- Friction-or-failure spend share: **42%** (`product.friction_or_failure_spend_share = 0.421`).
- Cost per successful call: **$0.12** — *estimated exposure*, not savings
  (`analytics.json:cost_per_successful_call = 0.1188`).
- Sponsor proof: agent **`199b03e7…`** · synthesizer **cartesia** · voice **Devansh** · model
  **sonic-3** (`out/bolna_cartesia_proof.json`).
- Judge: gemini-3.1-flash-lite · temperature 0 · evidence-cited · validated-before-cache.

**Every number above traces to a committed artifact. If a judge asks 'source?', point at the file.**
