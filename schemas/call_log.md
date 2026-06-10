# Schema: call_log

The normalized record of one call. Everything downstream (signals, judge, scorecard, DPO
export) reads this shape. Vendor-neutral and vertical-neutral by design — no field assumes
a domain or a provider.

## Fields

| field | type | notes |
|---|---|---|
| `call_id` | string | unique, stable; used to key caches and labels |
| `source` | enum | `spokenwoz \| ami \| hero \| bolna` |
| `language` | string | BCP-47-ish; `en` this sprint; code-switching noted as e.g. `te-en` |
| `stress_profile` | enum | `clean \| pause_heavy \| interruption \| ambiguous \| kb_gap` |
| `workflow_type` | string | free text, e.g. `appointment_booking`, `info_lookup` |
| `turns` | array | see below; sorted by `start_ms` |
| `turns[].turn_id` | string | e.g. `t1`, `t2` — judge evidence references these |
| `turns[].speaker` | enum | `user \| agent` |
| `turns[].text` | string | transcript of the turn |
| `turns[].start_ms` | int | onset, ms from call start (single clock per call) |
| `turns[].end_ms` | int\|null | offset; `null` allowed → latency-only treatment, never fake overlap |
| `audio_path` | string\|null | relative path to WAV/MP3 if audio exists |
| `metadata` | object | source-specific extras (never read by core pipeline) |

## Example

```json
{
  "call_id": "hero_001",
  "source": "hero",
  "language": "te-en",
  "stress_profile": "interruption",
  "workflow_type": "appointment_booking",
  "turns": [
    {"turn_id": "t1", "speaker": "agent", "text": "Hi, I can book that service visit. What area are you in?", "start_ms": 0, "end_ms": 3400},
    {"turn_id": "t2", "speaker": "user", "text": "haan area... ante... Madhapur side anukunta, near the er... metro station", "start_ms": 4100, "end_ms": 11600}
  ],
  "audio_path": "data/hero/hero_001.wav",
  "metadata": {"constructed": true, "timestamps_from": "assembly_timeline"}
}
```
