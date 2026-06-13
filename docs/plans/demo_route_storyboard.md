# Demo Route Storyboard — VoiceForge clinic agent on stage

**Owner:** DEMO-ROUTE agent · **Status:** PLAN ONLY — no code, no `out/` artifacts, no Bolna writes.
**Two tracks:** §1 the **3-min stage demo** (the hackathon's actual on-stage window) · §2 the
**10-min slot** (reuses `docs/demo_docs.md`'s 8-slide spine).
**Spec scope:** this file specifies how the existing `/` (presenter, 8 scenes) and `/platform`
(operator workspace, drawer + filters) routes should be **driven** during the demo. Any surface
*update* implied here is **gated** — see §7. Until that gate clears, this is a script that runs on
the surfaces we already have.

The use case is the locked one from `docs/TARGET_AGENT.md`: **inbound clinic / diagnostic-lab
appointment agent, Hinglish, Cartesia voice (Devansh, sonic-3).** The journey on stage is:
**Agent setup → live call → extracted fields → deterministic + semantic eval → improvement
recommendation.** Rubric arc per `hackathon.md`: **Problem → Workflow → Live Agent → Impact.**

---

## 0. The numbers that may be cited (and only these)

Every number that crosses Spike's lips on stage must trace to one of these artifacts. Anything
else is theatre and is forbidden.

| Number | Value | Source |
|---|---|---|
| Corpus size | 76 calls (46 timed · 30 unmeasured) | `out/analytics.json` |
| Metric-trap agreement | 25 / 45 (56%) | `out/demo_report_data.json :: metric_trap` |
| Missed real successes | 13 | demo_report_data |
| Failures passed by heuristic | 7 of 8 | demo_report_data |
| Cohen's κ | 0.206 (CI −0.108 → 0.499) | demo_report_data |
| Balanced accuracy | 0.628 ≈ 0.63 | demo_report_data |
| Failure recall | 0.50 | demo_report_data |
| Archetypes | seamless 25 · brittle 5 · recovered 7 · slot-loss 3 · workflow 5 | demo_report_data |
| Fix-first | `poor_clarification_or_recovery` · 11 calls | demo_report_data :: `fix_first` |
| Friction-or-failure spend share | 42% | demo_report_data |
| Cost per successful call | $0.12 (estimated exposure) | analytics.json |
| Latency-gap events | 183 | analytics.json |
| Barge-in events | 107 | analytics.json |
| Sponsor proof | agent `199b03e7…` · cartesia · Devansh · sonic-3 | `out/bolna_cartesia_proof.json` |
| Backup live trace | `bolna_246cd9f3` | `out/call_bolna_246cd9f3.json` |

**The 46-call calibration is methodology proof; live clinic calls are use-case proof. Never mix.**

---

## 1. THE 3-MINUTE STAGE STORYBOARD (180s budget)

Four beats matching the rubric. Times are cumulative spoken seconds. Spike runs the deck hands-on
keys; the live phone is on speaker into the room mic.

### Beat A · Problem · 25s · cum 0:25
- **Screen:** `/` · scene **1 `sc-thesis`** (already where the deck opens).
- **Rubric:** Problem Applicability.
- **Said (short phrases):**
  - "Clinics and diagnostic labs miss inbound calls. Reception busy, after-hours, understaffed."
  - "Every missed call is a lost patient and lost revenue."
  - "Voice is the native channel. Callers are natively multilingual."
  - "We're building the inbound appointment agent — in Hinglish."
- **Key action at end:** press **`→`** to advance to scene 2.

### Beat B · Workflow card · 25s · cum 0:50
- **Screen:** `/` · scene **2 `sc-trap`** (already on screen) used as the workflow card. Spike reads
  it as: *here is the workflow the agent runs and the metric we beat.*
- **Rubric:** Cartesia & Bolna Usage (the workflow lives inside the Bolna builder + KB + extractions
  + Cartesia voice) **and** Scale-Up (the metric story).
- **Said:**
  - "The workflow is one job: capture patient, phone, service, date, time — one at a time — check
    availability, read back, get yes."
  - "Built in **Bolna's** builder: KB for services and tests, extractions for the appointment
    fields, **Cartesia Devansh sonic-3** for the voice."
  - "Target metric: **appointment-booking rate**. Today everyone ships **completion** — a keyword
    check — and that gap is where money leaks."
- **Key action at end:** **dial the agent's Bolna Buddy number on the speaker phone**, then press
  **`Home`** to flip the deck to a neutral scene (or stay on scene 2 — the deck recedes).

### Beat C · Live Agent · 60s · cum 1:50
- **Screen:** the room watches the **phone**, not the deck. The deck stays where it is. Don't fight
  for screen attention during the call.
- **Rubric:** Agent Quality + Multilinguality + Cartesia & Bolna Usage (live, judged in-room).
- **Pre-staged call:** Scenario 1 (clean booking) from `docs/TARGET_AGENT.md §6` — Hinglish, a blood
  test, tomorrow morning. Contingency tree in §4 below if the room demands a harder scenario or the
  call fails.
- **Said before the dial-tone:**
  - "I'm going to call our clinic agent live. Hinglish. **Real Cartesia voice. Real Bolna runtime.**"
- **During the call:** Spike says nothing unless the call stalls. Let the agent talk.
- **Said at hang-up:**
  - "That's the conversation. Now the eval lab."
- **Key action at end:** **`Cmd+T → /platform`** (or click the tab Spike pre-opened on
  `localhost:8000/platform`).

### Beat D · Impact · 60s · cum 2:50
- **Screen:** `/platform`, Live Today mode.
- **Rubric:** Scale-Up + Agent Quality (the post-call receipt).
- **Sub-beats (the exact click path):**
  1. **0:00–0:10** — Top of `/platform`: click **Live Today** in the header tab. The live-pip
     should be lit. Say: "This is the call we just made — already ingested."
  2. **0:10–0:25** — Click the freshest row in the **left rail** (top of Live Today list). The
     drawer opens with the live call. Point at the **Extracted Fields** group inside *Deterministic
     signals* (patient name, phone, service, date, time, booking_confirmed — from
     `extracted_data` on `GET /executions/{id}`; see §7 if this group is not yet broken out as its
     own labeled card). Say: *"Bolna's extractions populated. This is the structured appointment
     outcome with confidence."*
  3. **0:25–0:40** — Slide eye down to **Deterministic signals**: outcome, latency gaps, barge-in
     events. Say: *"Counted, not judged — timestamp math."*
  4. **0:40–0:55** — Slide down to **Judge evidence · uncalibrated diagnostics**: cite the dimension
     scores with their **evidence turns**. Say: *"Temperature zero, every score cites the turn it
     came from. Marked uncalibrated because the live lane is separate from the 46-call
     calibration."*
  5. **0:55–1:00** — Slide down to **Recommendation**. Read it verbatim. Say: *"This is the
     improvement — ranked first because it touches 11 calls in our frozen corpus."*

### Beat E · Impact one-liner · 10s · cum 3:00
- **Screen:** stay on `/platform` drawer.
- **Said:**
  - "**Booking-completion measured per call. Failure phenotyped. Fix ranked. $0.12 cost per
    successful booking** — estimated exposure, from real per-unit prices."
- (Pick the exact line from §5 alternatives.)

### 3-min budget check (sum)
**25 + 25 + 60 + 60 + 10 = 180s ✅**

---

## 2. THE 10-MIN SLOT STORYBOARD (6:30 spoken + ~3:30 Q&A)

Reuse the 8-slide spine from `docs/demo_docs.md` exactly. The deltas below are the only changes.
**Honors the existing 6:30 spoken budget.** The live-call interlude is the centerpiece and sits
between Slide 6 and Slide 7. Spike does not lengthen any slide; the live call replaces ~30s of
Slide 7's existing "LIVE TODAY" paragraph and uses ~60s borrowed from breathing room (Spike must
have rehearsed under 6:00 by the morning of).

| Slide | demo_docs role | Route | Clinic-agent delta |
|---|---|---|---|
| 1 — Thesis | `/` sc-thesis | `/` | No change. Same opener. |
| 2 — Metric trap | `/` sc-trap | `/` | No change. The 25/45 lives on. |
| 3 — Deterministic before judge | `/` sc-measure | `/` | No change. Cite 183 / 107 from analytics. |
| 4 — Hero call | `/` sc-hero | `/` | Disclose constructed *every time*. Unchanged. |
| 5 — Blind labels & calibration | `/` sc-judge | `/` | Methodology proof — call it that. *"This is the methodology — next I'll show it on a clinic call live."* |
| 6 — Phenotypes + queue | `/` sc-action | `/` | Frame `fix_first` (`poor_clarification_or_recovery`, 11 calls) as the kind of fix the live call about to happen will generate. |
| **6½ — LIVE CLINIC CALL** | new interlude | switch to **phone + `/platform`** | **~90s.** Dial → talk → hang up → switch tab. This is the use-case proof. |
| 7 — Bolna × Cartesia + Live Today | `/` sc-proof → `/platform` Live Today | `/` then `/platform` | Drop the "if no live calls happened" branch — we just made them. Open `/platform` Live Today drawer for the call we just placed. Walk the same 5-sub-beat sequence as 3-min Beat D, but slower. |
| 8 — Value, limits, close | `/` sc-method | `/` | Same close, verbatim thesis. Add one clinic-specific line in limits: *"PII redaction is a production must — these were controlled test calls."* |

### 10-min screen choreography (per-slide cumulative clock)

| t (mm:ss) | Route | Section | What Spike does |
|---|---|---|---|
| 0:00 | `/` | `sc-thesis` | Open. Page loads at scene 1. |
| 0:40 | `/` | `sc-trap` | Press **`→`**. |
| 1:25 | `/` | `sc-measure` | Press **`→`**. |
| 2:10 | `/` | `sc-hero` | Press **`→`**. |
| 2:50 | `/` | `sc-judge` | Press **`→`**. |
| 4:00 | `/` | `sc-action` | Press **`→`**. |
| 4:55 | phone | — | Walk to phone, dial Bolna number on speaker. |
| ~6:25 | `/platform` | Live Today | **`Cmd+T → /platform`**, click **Live Today** tab, click the freshest live row. Walk Extracted → Deterministic → Judge → Recommendation. |
| ~6:55 | `/` | `sc-proof` | Press **`Home`** then **`→ → → → → → ←`** (or just **`End`** then **`←`**) to land on scene 7 from a hard-known position. *(Easier path: keep `/platform` open during sponsor proof — point to the live drawer as the proof itself, then **`Cmd+T → /`** for sc-method.)* |
| ~7:40 | `/` | `sc-method` | Press **`End`**. Close. |
| 8:30 | — | Q&A | Hand off. |

(The clock-shifts assume Spike rehearsed Slide 7's spoken under-budget; if not, drop the optional
multi-agent paragraph as the demo_docs note already allows.)

---

## 3. THE SCREEN CHOREOGRAPHY (explicit ordered click list)

### `/` route — keyboard nav (from `out/surface/app.js`)
- **`→` / `↓` / `PageDown` / `Space`**: next scene.
- **`←` / `↑` / `PageUp`**: previous scene.
- **`Home`**: jump to scene 1 (`sc-thesis`).
- **`End`**: jump to scene 8 (`sc-method`).
- **`Esc`**: closes the call evidence sheet if it was opened.

### `/platform` route — mouse + filters
- **Header tabs**: **Frozen Pilot ↔ Live Today**. Click **Live Today** before Beat D.
- **Left rail**: list of calls. **Click a row → drawer opens to the right**, scrolled to top.
- **Filters**: source / outcome / profile chips above the rail. **Do NOT touch filters mid-demo.**
  They reset the selected row.
- **Drawer order (top → bottom):** title → metrics tiles → **Transcript** → **Deterministic
  signals** (this is where Extracted Fields lives — see §7) → **Judge evidence · uncalibrated
  diagnostics** → **Recommendation**.

### The exact click script for Beat D
1. `Cmd+T` → type `localhost:8000/platform` → Enter. *(Spike: pre-open this tab before stage.)*
2. Header → click **Live Today**.
3. Left rail → click the **top row** (most recent live ingest).
4. Drawer auto-scrolls to top. **Scroll the drawer**, not the page, with the trackpad.
5. Stop at Deterministic signals · Extracted fields. Speak.
6. Scroll. Stop at Deterministic signals · latency / barge-in. Speak.
7. Scroll. Stop at Judge evidence. Speak.
8. Scroll. Stop at Recommendation. Read verbatim.

---

## 4. LIVE-CALL CONTINGENCY TREE

The 5 live-test scenarios from `docs/TARGET_AGENT.md §6`. Spike picks the **default** below; if a
judge demands a specific scenario, Spike runs that one and the storyboard branches as shown.

### Default: Scenario 1 · Clean happy-path booking
- **Trigger:** Spike dials. Asks for a blood test tomorrow morning, in English to start.
- **Show on `/platform` drawer:**
  - **Extracted Fields** all populated (patient_name, phone, service=`blood_test`, date, time,
    booking_confirmed=`true`).
  - **Judge evidence** → success outcome on the relevant dimensions.
- **Said:** *"All five fields. Confirmed. Judge agrees. Recommendation queue: empty for this
  call."*

### Branch: Scenario 2 · Hinglish / mid-call language switch
- **Trigger:** Spike opens in Hindi, switches to English mid-call.
- **Show:** Extracted Fields populate the same way. Point at **transcript turns** in the drawer
  where the language flips — *"the agent mirrored — Hindi-to-Hindi, English-to-English, never
  forced a switch."*
- **Rubric beat:** Multilinguality. Cite the methodology finding from Slide 5: *"In our calibration,
  Hindi-English (71%) ≈ English (69%). Language isn't the fault line; confidence is."*

### Branch: Scenario 5 · Caller asks for medical advice
- **Trigger:** Spike asks "I have chest pain, what should I take?"
- **Expected agent behavior:** safe refusal + offer to book a consultation.
- **Show on `/platform`:**
  - **Judge evidence**: the refusal dimension should fire. Phenotype tag: the closest archetype in
    the current schema is **`safety_recovery`** (or whatever the live judge emits — Spike reads
    what's there, doesn't invent the tag).
  - **Recommendation** card: the *template-derived* fix for the refusal pattern (e.g. *"after
    declining medical advice, always offer to book a consultation in the same turn"*).
- **Said:** *"Healthcare guardrail held. The judge flagged it, named the phenotype, and the
  recommendation says exactly what to add."*

### Disaster branch: live call fails on stage
- **Trigger:** call drops, agent silent, Bolna unreachable, venue Wi-Fi flakes.
- **Recovery line (honest, not theatre):** *"I've already shown this with real calls today. Here
  is one such trace."*
- **Action:** `Cmd+T → /platform` → header **Frozen Pilot** (or stay on Live Today if any
  pre-ingested live row exists) → left rail → find row **`bolna_246cd9f3`** → click. Walk the same
  Extracted → Deterministic → Judge → Recommendation sequence on the cached call.
- **What NOT to say:** never call the cached call "today's call." It's the recovery trace. Honesty
  invariant from §6 below.

---

## 5. IMPACT BEAT — 3–5 alternative phrasings

All cite only artifact-backed numbers. Pick one per run; do **not** combine. ≤12 spoken seconds.

1. **"Booking-completion measured per call. Failure phenotyped. Fix ranked.
   **$0.12 per successful booking** — estimated exposure, from public per-unit prices."**
2. **"Today every team ships completion. We ship the **shape** of failure —
   25 / 45 agreement says completion is blind on **7 of 8** real failures.
   We fix what completion can't see."**
3. **"**42% of estimated call spend** sits in calls with friction or failure.
   That's the budget a success rate can't see. We name it, queue it, and rank the fix."**
4. **"Five archetypes, one fix-first: **poor clarification, 11 calls.**
   That's not a score — that's an engineering backlog, sorted by what to fix first."**
5. **"Bolna runs the calls. Cartesia gives them a voice. **VoiceForge measures whether the
   booking actually happened — and at what cost.**"**

---

## 6. HONESTY CHECKLIST FOR THE SCRIPT

**Words Spike must never say on stage:**
- "Calibrated" applied to the live calls. The live lane is **`LIVE · UNCALIBRATED`**. The frozen
  46-call calibration never touches a live call.
- "Barge-in" applied to a live call as a *detection* (Bolna exposes no interruption telemetry).
  Barge-in counts are a frozen-corpus deterministic-signal claim only.
- "Saved" applied to any cost number. Always **"estimated exposure"**, never "savings."
- "Validated" applied to any judge dimension that isn't covered by the frozen κ. Say
  **"uncalibrated diagnostics"** — that's what the platform UI already labels them.
- "Our customer" / "in production" — these are controlled test calls. Production needs **consent
  capture + redaction** (PII = patient name + phone). Say that out loud if the room asks.
- "Hindi calls have timestamps" for the 30 unmeasured ones. They carry the `unmeasured` profile;
  timing dimensions are **omitted**, never faked.

**Words Spike must say at least once:**
- *Cartesia Devansh, sonic-3* (the sponsor proof).
- *Bolna extractions / `GET /executions/{id}`* (the integration proof).
- *Uncalibrated* — applied explicitly to the live drawer once.
- *Methodology* (frozen corpus) vs *use case* (live calls) — the lanes are separate, on purpose.

**The two lanes, said once on stage:**
> "The 46-call calibration is **methodology** — it proves the eval lab works. Today's clinic calls
> are the **use case** — they prove the agent works. The lanes never mix."

---

## 7. INTEGRATION GATE

This storyboard is the **spec** for an eventual surface update. Until Codex confirms the three
items below, **do not modify surface code**. The storyboard runs on the current `/` and
`/platform` with the small caveats marked **(IG)** throughout.

**Codex must confirm, before any surface edit ships:**
1. **Final agent id** — the production clinic agent that the stage demo will dial. The proof file
   (`out/bolna_cartesia_proof.json`) currently points at `199b03e7…` — confirm or replace.
2. **Knowledge base** — the 1-page services/tests/hours/FAQ PDF (see `docs/TARGET_AGENT.md §8.7`)
   is uploaded and bound to the agent.
3. **First execution schema** — a sample `GET /executions/{id}` response from the live clinic agent,
   showing the actual `extracted_data` keys and the analysis payload. This is what
   `pipeline/ingest_live.py` will normalise into the drawer's **Extracted Fields** group.

**Surface deltas that this storyboard implies (queued, NOT applied):**
- **(IG)** Break out **Extracted Fields** as its own labeled card inside the drawer, ahead of
  Deterministic signals. Currently `pipeline/build_platform.py` renders a *Deterministic signals*
  section but does not call the extracted booking fields out as a top-level card. The storyboard
  has Spike point at it by name — the surface should match.
- **(IG)** The Live Today live-pip should light when at least one ingested live row exists for
  today's date, so Spike has a visual confirmation before he clicks the tab on stage.
- **(IG)** Reorder the drawer to: title → tiles → **Extracted Fields** → **Deterministic signals**
  → **Transcript** → **Judge evidence** → **Recommendation**. Current order puts Transcript before
  Deterministic; the demo flow wants the structured outcome first.

**Do not apply any of the above** until items 1–3 above are confirmed. This file is the storyboard;
the surface update is a separate ticket.

---

## 8. PRE-STAGE CHECKLIST (last 5 minutes before Spike walks up)

- [ ] `localhost:8000/` open in tab 1, on **scene 1** (`Home`-pressed).
- [ ] `localhost:8000/platform` open in tab 2, on **Live Today** tab. Live-pip lit.
- [ ] Phone on speaker, dialer pre-loaded with the Bolna Buddy number.
- [ ] One **pre-stage warm-up call** done (so the live row exists for the disaster branch as
      *another* fallback even if today's stage call fails).
- [ ] `out/dashboard.html` open in tab 3 as the offline-network fallback.
- [ ] Backup recording uploaded per `hackathon.md` 11:45 AM requirement.

---

## CHANGE LOG
- v1 — initial storyboard. PLAN ONLY. No source modified. Awaits Codex Integration Gate (§7).
