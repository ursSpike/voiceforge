# AGENT BUILD — what to type into platform.bolna.ai (lock before 10:30)

**The agent IS the submission (4 of 5 rubric points + the live test). VoiceForge proves it (Scale-Up).**
Vertical: **inbound restaurant table-booking + enquiry, Hinglish.** Build the agent FIRST; feed its test
calls to VoiceForge SECOND.

## Problem statement (mandatory step 3 — paste into submission)
- **Who/when:** Inbound. Customers call a local restaurant's booking line to reserve a table or ask
  hours/availability — in Hindi, English, or Hinglish.
- **What each call must accomplish:** Capture party size, date, time, name, phone → check availability →
  confirm the booking (read it back).
- **After each outcome:** *Yes* (slot open) → confirm + read back. *No* (full) → offer 2 alternative
  slots. *Unclear* → ask ONE clarifying question, never guess.
- **Metric that improves:** **Booking-completion rate** = % of inbound calls ending in a confirmed
  booking (+ fewer abandoned calls). Baseline: missed/after-hours calls today book ~0%. ← VoiceForge
  measures exactly this (task completion + cost per successful booking).

## The 7 Bolna steps, filled in
**1. New Agent:** name `Aarti — <Restaurant> Bookings` · language **Hinglish** (primary) + Hindi + English ·
direction **inbound**.

**2. System prompt** (paste, then tune):
> **Identity:** You are Aarti, the friendly booking assistant for Spice Garden, a popular multi-cuisine
> family restaurant in Bengaluru. You speak natural Hinglish and ALWAYS mirror the caller's language —
> if they speak Hindi, reply in Hindi; English, English; mixed, mix. Warm, quick, never robotic.
> **Objective:** Book a table. You must capture: party size, date, time, name, and phone number. Confirm
> availability, then read the full booking back and get a yes before ending.
> **Conversation paths:**
> – If the requested slot is available → confirm details, read back, get confirmation.
> – If full → say so warmly and offer the two nearest available slots.
> – If the request is unclear or missing info → ask ONE specific question at a time (don't ask everything
>   at once, don't assume).
> – If they only want info (hours, location, cuisine) → answer from the knowledge base, then offer to book.
> **Guardrails:** Never invent availability — use only the rules given. Never take payment or card details.
> Never promise anything beyond a table booking. If asked something off-topic (delivery, complaints,
> jobs) → politely say you only handle table bookings and offer to note their number. Don't switch to a
> language the caller hasn't used.
> **Exit:** Once the booking is confirmed and read back (or the caller declines), thank them by name and
> end the call cleanly.

**3. Cartesia voice:** pick a **warm, approachable** voice (it's hospitality — first impression matters).
This is a scored criterion; choose deliberately and note which voice you picked.

**4. Multilingual:** primary Hindi+English (Hinglish), enable **mid-call language switching**, set ASR for
Indian English + Hindi. Test a call where you START in English and SWITCH to Hindi mid-sentence — that
switch is worth real points.

**5. Knowledge base** (5–10 short docs): hours (e.g. 12–3:30pm, 7–11pm, closed Mon), capacity/slot rules
(tables of 2/4/8; last seating 10:30pm), cuisines, location + parking, policies (hold 15 min, no outside
food), a short FAQ. Keep it tight.

**6. Test with Buddy — the 5 scenarios (THESE are your VoiceForge calls):**
1. Clean happy path (book a table of 4, Saturday 8pm).
2. Hinglish / mid-call language switch.
3. Confused / ambiguous caller (vague date → agent clarifies).
4. Change a detail mid-call (party 4 → 6, or time change).
5. Out-of-scope / refusal (asks about delivery, or declines to book).
Save the **execution ID** after each — paste it to me, I ingest + judge → /platform Live Today.

**7. Review logs & iterate:** after the 5 calls, VoiceForge shows you exactly where it broke (failure
phenotype + ranked fix). Fix the **prompt** first. That fix-loop IS your Scale-Up story.

## Submission package (link floats 11:45 · HARD deadline 2:00)
- Live agent link (the Bolna agent) · problem statement (above) · target metric (booking-completion rate)
  · **backup recording** (screen-record one clean call + a /platform view — do this by ~1:30).

## 3-min demo arc (if Top 10): Problem → Workflow → Live Agent → Impact
Problem (missed booking calls = lost revenue) → Workflow (the call flow) → **Live Agent** (call it on
stage, Hinglish switch) → **Impact** (open /platform: "I don't just claim it works — I measure every call:
booking-completion, where it fails, the ranked fix, the cost. That's how this scales." ← VoiceForge).

## Discipline
Agent quality first (live-tested, 20 pts + gates Problem Applicability). VoiceForge is the Impact beat,
not the build. Don't touch frozen artifacts; live calls stay the uncalibrated lane.
