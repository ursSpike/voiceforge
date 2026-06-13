# HACKATHON AGENT — READY

## Agent

- **Name:** Aarogya Clinic & Diagnostics — Aarav
- **Bolna agent ID:** `cb7dee37-fe1b-43fb-a669-4f56a46eeb46`
- **Bolna status:** `processed`
- **Use case:** inbound clinic/diagnostic-lab appointment scheduling
- **Primary language:** Hindi
- **Secondary language:** English
- **Mixed mode:** natural Hinglish; continuously mirrors caller

## Verified server-side

- Cartesia **Devansh**, `sonic-3`, for **both Hindi and English**
- Deepgram `nova-3`
- OpenAI `gpt-4.1-mini`, temperature `0.3`, max tokens `300`
- 300-second call ceiling
- 2-word interruption threshold
- `hangup_after_LLMCall: false`
- processed clinic knowledge base attached
- post-call structured extraction runs in VoiceForge's isolated live pipeline

## Structured fields

1. `patient_name`
2. `phone_number`
3. `appointment_type`
4. `doctor_or_department`
5. `test_or_service`
6. `preferred_date`
7. `preferred_time`
8. `collection_address`
9. `booking_confirmed`
10. `appointment_status`
11. `medical_advice_requested`
12. `medical_advice_refused_safely`
13. `language_mode`

## What it does

- Books doctor consultations, lab tests, and home sample collection.
- Collects one field at a time.
- Requires exactly 10 digits for an Indian callback number.
- Requires a full address before closing any home-collection request.
- Handles ambiguous requests and changed details.
- Reads the full appointment back and requires an explicit yes.
- Does not invent availability. Without a configured calendar tool, the request
  is marked `follow_up_required` instead of falsely confirmed.
- Refuses diagnosis, symptom/report interpretation, test or medicine
  recommendations, and emergency advice.
- Never requests payment, card, UPI, OTP, Aadhaar, or insurance details.

## Test now

Run these five calls in the Bolna builder:

1. Clean lab-test booking.
2. Start English, switch to Hindi/Hinglish.
3. Give an ambiguous service, then clarify it.
4. Change the date or time after giving it.
5. Ask for medical advice; verify safe refusal and consultation offer.

After each call, copy the execution ID:

```bash
export BOLNA_AGENT_ID=cb7dee37-fe1b-43fb-a669-4f56a46eeb46
python pipeline/ingest_live.py --execution <execution-id>
python pipeline/judge_live.py
python pipeline/build_platform.py
python pipeline/serve_surface.py --port 7871
```

Open `http://localhost:7871/platform` and select **Live Today**.

## Files

- Reproducible creator: `pipeline/create_clinic_agent.py`
- Full posted config: `out/clinic_agent_config.json`
- Sanitized creation proof: `out/clinic_agent_created.json`

## Still optional

- Bind an inbound number if the event requires phone dialing.
- Add Cal.com availability/booking only if credentials are ready. Until then,
  the prompt honestly records a requested slot for staff verification.

## Knowledge base

- Status: `processed` and attached.
- Vector ID: `3b878d02-a101-43e0-b4e0-96934b3aa0fa`
- Source: `docs/AAROGYA_KNOWLEDGE_BASE.md`
- Cached upload: `out/aarogya_knowledge_base.pdf`
