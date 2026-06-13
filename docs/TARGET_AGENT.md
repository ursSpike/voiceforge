# TARGET AGENT — specification & behavior

Hand this to the audit master **together with** `docs/BOLNA_FIELDS_REFERENCE.md` (the field/API reference).
This file = *what we want and why*; that file = *the fields available*. The audit master maps one to the
other and returns the final field values; Spike then creates the agent.

---

## 1. Context
- **Event:** Bolna × Cartesia Voc-a-thon (Jun 13). The deliverable is a **working Bolna voice agent**,
  scored live on a 5×20 rubric: Problem Applicability · Cartesia+Bolna Usage · Multilinguality ·
  Scale-Up · Agent Quality (judges call it live). Submission by 2:00 PM; 3-min demo (Problem → Workflow
  → Live Agent → Impact).
- **Our edge:** VoiceForge (a pre-built evaluation lab) is the **Scale-Up + proof-of-quality**
  differentiator. The agent is the submission; **VoiceForge evaluates it** — it is the "Impact" beat, not
  the product being judged.

## 2. Use case (locked)
- **Inbound appointment-booking voice agent for a clinic / diagnostic lab.** **Hinglish** (Hindi +
  English, mid-call switching). India, local-commercial, healthcare-access.
- **Problem:** clinics and diagnostic labs miss a large share of inbound appointment calls — reception
  busy, after-hours, understaffed — and every missed call is a lost patient and lost revenue. Voice is
  the native channel (patients call to book consultations, lab tests, or home sample collection), and the
  callers are natively multilingual.
- **Target metric (submission "target metric" + Scale-Up answer):** **appointment-booking rate** = % of
  inbound calls that end in a confirmed appointment (and the reduction in abandoned/unbooked calls).
  VoiceForge measures exactly this (task completion + cost per successful booking).

## 3. What the agent must accomplish (the job)
On each inbound call:
1. Capture the appointment: **patient name, phone number, service requested** (doctor consultation /
   specific lab test / home sample collection), **preferred date, preferred time** — one item at a time.
2. **Check availability** for the requested slot (via the booking tool / knowledge base).
3. **Confirm**: read the full appointment back and get an explicit yes before ending.

Outcome branches: **available** → confirm + read back · **full** → offer the two nearest slots ·
**unclear/missing info** → ask one specific clarifying question (never guess, never ask everything at once).

## 4. How it must behave (the quality bar — this is what makes it win Agent Quality)
- **Language:** mirror the caller — Hindi→Hindi, English→English, mixed→mixed — and **never switch to a
  language the caller hasn't used**. Natural Hinglish, not stilted.
- **Concise & human:** short, receptionist-style turns (1–2 sentences), natural turn-taking (sensible
  interruption + endpointing behavior), warm and professional tone — not robotic, not over-scripted.
- **Recovers gracefully** from: interruptions, the caller changing a detail mid-call, ambiguity, and
  out-of-scope or off-topic requests.
- **Healthcare guardrails (critical):** the agent is a **scheduler, not a clinician**. It must NEVER give
  medical advice, diagnose, interpret symptoms or test results, or recommend medication — for anything
  clinical it books an appointment or offers to route to a human. Never take payment or card details.
  Never invent availability. For off-topic asks, politely decline and offer to note the number.
- **Clean exit:** once confirmed-and-read-back (or the caller declines), thank them and end cleanly.

## 5. Rubric alignment — what "best" means per dimension
| Dimension | How this agent maximizes it |
|---|---|
| Problem Applicability | A real, commercial, existing workflow (clinics/labs lose patients to missed calls); voice is the right medium; scope is one focused job. |
| Cartesia & Bolna Usage | Cartesia voice chosen deliberately; meaningful Bolna features used — **knowledge base (services/tests), extractions, variables, the Book-Appointment tool/call-flow** — not just a bare prompt. |
| Multilinguality | Hindi+English with genuine **mid-call code-switching**; transcriber set for Hinglish; the agent adapts when the caller switches. |
| Scale-Up | Clear baseline (appointment-booking rate) and a credible path: **VoiceForge measures it, surfaces failure phenotypes, ranks the fix, costs it** — a measurement story competitors won't have. |
| Agent Quality (live) | Handles the 5 scenarios below end-to-end, recovers from edge cases, **refuses medical advice safely**, sounds natural; judges call it and it works. |

## 6. The 5 live-test scenarios (also the VoiceForge calls)
1. Clean happy-path booking (e.g. a blood test, tomorrow morning).
2. Hinglish / mid-call language switch.
3. Ambiguous request → agent clarifies (vague test name or date).
4. Caller changes a detail mid-call (date/time or service).
5. Out-of-scope → caller asks for **medical advice / a diagnosis**; agent **declines safely** and offers
   to book a consultation.
*(An "interruption" test shows the agent recovering — that is an Agent-Quality signal, NOT a VoiceForge
barge-in claim: Bolna's call data exposes no interruption telemetry.)*

## 7. VoiceForge integration (the Impact beat — keep honest)
- Each test call → `pipeline/ingest_live.py --execution <id>` → `pipeline/judge_live.py` →
  `/platform` **Live Today**.
- Bolna **Extractions** return `extracted_data` (patient_name, phone, service, date, time,
  booking_confirmed) on `GET /executions/{id}` — the same endpoint VoiceForge fetches — giving a
  structured appointment outcome with confidence.
- **Honesty invariants:** live calls are **`LIVE · UNCALIBRATED`**, a separate lane from the frozen
  46-call calibration (never mixed); no barge-in claim on live calls; Cartesia is proven from the agent
  config (`GET /v2/agent/{id}`), not inferred from a call.
- **PII note (healthcare):** the agent collects patient name + phone. For the prototype this is a
  controlled test call; production would need consent capture + redaction before judging/storage — state
  this honestly (it strengthens the Scale-Up/Method story, doesn't weaken it).

## 8. Open decisions for the audit master (please rule)
1. **LLM model:** latency vs Hinglish quality — a fast GPT-4-class mini vs full. Recommend the fast one
   unless Hinglish degrades.
2. **Tokens-generated cap:** our note said 150 (anti-truncation); official docs say 300–500. Recommend
   **300** (cap, not target; prompt keeps turns short). Confirm.
3. **Temperature:** 0.3 (consistent, still natural). Confirm.
4. **Cartesia voice + model:** warm, calm Indian voice (pick-by-ear in the UI — calm suits healthcare) +
   `sonic-3-preview`. Confirm.
5. **Transcriber language:** `multi` (Deepgram Hinglish code-switch) with `hi` as fallback if the UI
   won't accept `multi`.
6. **Booking tool (Cal.com Book Appointment + Calendar Availability):** strongly recommend **include** —
   it is literally an appointment use case, so a real calendar booking is the natural Agent-Quality +
   platform-use win. Skip only if the Cal.com key + event setup drags; fallback = conversational booking
   + extraction.
7. **Knowledge base scope:** a 1-page PDF — services/tests offered, doctors/departments, hours, prep
   instructions (e.g. fasting for some tests), location/parking, 5 FAQ.
8. **Prompt construction:** compose from the builder's **Modules** (the live builder shows Identity and
   Persona, Healthcare Appointment, Flow: Inbound Booking, Guardrails Core, FAQ Block, Extraction Schema,
   Hang-up Prompt — confirmed by screenshot; note there is a **Healthcare Appointment** module that fits
   directly) vs the single written prompt in §9. Recommend modules for "platform features used," with §9
   as the fallback/baseline.
9. **Ambient noise / final-call message / welcome message:** minor; recommend ambient noise off for a
   clean demo.

## 9. System-prompt intent (clean baseline — audit master to approve/replace)
The system prompt must encode: **identity** (a clinic/lab's appointment scheduler — Spike names it),
**objective** (§3), **conversation handling** (§3 branches, one-question-at-a-time, clarify-don't-guess),
**language behavior** (§4 mirroring), **guardrails incl. no-medical-advice** (§4), **exit** (§4).
Neutral baseline text:

```
You are the appointment scheduler for [Clinic/Lab Name], a clinic and diagnostic lab in [City].

LANGUAGE: Speak natural Hinglish. Mirror the caller's language — Hindi→Hindi, English→English,
mixed→mixed. Never switch to a language the caller hasn't used. Keep turns short (1–2 sentences).

GOAL: Book an appointment. Collect one at a time: patient name, phone, service requested (doctor
consultation / lab test / home sample collection), preferred date, preferred time. Check availability,
then read the full appointment back and get a yes before ending.

HANDLING: Ask for missing details one question at a time — never all at once. If a request is unclear,
ask one specific clarifying question. If the slot is available, confirm and read back. If full, offer
the two nearest slots. If they only want info (services, hours, test prep, location), answer briefly
from the knowledge base, then offer to book.

GUARDRAILS: You are a scheduler, not a clinician. NEVER give medical advice, diagnose, interpret
symptoms or results, or recommend medication — for anything clinical, offer to book a consultation or
route to a human. Never invent availability (use the booking tool / knowledge base only). Never take
payment or card details. For off-topic requests, politely decline and offer to note their number.

EXIT: Once the appointment is confirmed and read back (or the caller declines), thank them and end cleanly.
```
