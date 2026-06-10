# Hero Call — script + recording sheet (SPEC §7.E)

~95s constructed call. **Disclosure:** demo scenario, assembled; timestamps come from the
assembly timeline (see docs/limitations.md). Canonical turn texts live in `timeline.json`.

Scenario: QuickCool appliance-care service desk. English TTS agent (en-IN Neerja) ×
Tenglish caller (Spike). The agent commits **exactly two sins**, both engineered at assembly:
- **t2→t3: barge-in** — agent starts 800ms before the caller finishes his hesitant answer
- **t6→t7: dead air** — 1,620ms of silence before the agent responds

The t3 over-demand ("complete address with pincode...") doubles as the DPO **rejected** turn.

## Full dialogue

| turn | speaker | line |
|---|---|---|
| t1 | agent | Hi, this is the service desk for QuickCool appliance care. I can help you book a technician visit. May I know which area you're calling from? |
| t2 | **you** | haan hello... area ante... *(silent pause ~2s)* Madhapur side anukunta... near the, er... metro station. |
| t3 | agent | *(BARGES IN over your last words)* I need your complete address with pincode, landmark and door number before we can proceed any further with this booking request. |
| t4 | **you** | ayyo okay okay... full address kavala? it's plot 42, ante... near metro pillar number... I don't remember exactly ya. |
| t5 | agent | Thank you. And what appliance needs servicing today? |
| t6 | **you** | AC unit... cooling sariga ledu, very weak airflow vastundi. |
| t7 | agent | *(after 1.6s dead air)* Got it — an AC cooling issue. Would you prefer a morning or an evening visit tomorrow? |
| t8 | **you** | morning better... around ten ayite manchidi. |
| t9 | agent | Perfect, tomorrow morning around ten AM. Could I get a callback number? |
| t10 | **you** | nine eight four nine two... double five... zero three one. |
| t11 | agent | Thank you. Your booking is confirmed for tomorrow at ten AM in Madhapur. The technician will call you before arriving. |
| t12 | **you** | sare, thanks ya. |

(Note t11: agent "confirms" without ever resolving the address — that's the task_outcome
gap: `full_address.captured = false`.)

## Recording sheet — 6 voice memos, ~10 minutes

Quiet room · phone ~20cm from mouth · **one Voice Memo per line** · natural pace, you're a
slightly distracted customer, not an actor. Record **in this order**, AirDrop all six to the
Mac, done — they get renamed and trimmed automatically (leading/trailing silence is removed,
so don't worry about gaps around your words).

1. **(t2 — THE important one.)** "haan hello... area ante..." → **full silent stop, count
   one-thousand-one, one-thousand-two** → "Madhapur side anukunta... near the, er... metro
   station." Hesitant throughout — you're thinking while talking. Don't rush the pause; the
   pause is the point.
2. **(t4)** "ayyo okay okay... full address kavala? it's plot 42, ante... near metro pillar
   number... I don't remember exactly ya." — slightly thrown off.
3. **(t6)** "AC unit... cooling sariga ledu, very weak airflow vastundi." — matter-of-fact.
4. **(t8)** "morning better... around ten ayite manchidi."
5. **(t10)** "nine eight four nine two... double five... zero three one." — steady digits.
6. **(t12)** "sare, thanks ya." — wrapping up.

Multiple takes fine — keep the best, delete the rest, AirDrop exactly six files.

## Assembly (automated)

```bash
.venv/bin/python pipeline/assemble_hero.py tts        # agent lines via edge-tts (done by copilot)
.venv/bin/python pipeline/assemble_hero.py assemble   # mix WAV + turns.json + failure table
```

Re-voicing the agent with Cartesia Sonic 3.5 later (if credits land) = regenerate the six
agent files, re-run `assemble`. Nothing else changes.
