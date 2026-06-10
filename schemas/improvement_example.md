# Schema: improvement_example

The kicker artifact: a detected failure converted into a (chosen, rejected) preference pair.
Discipline: **the ONLY meaningful difference between chosen and rejected is the detected
failure axis.** Over-talk → shorter turn; ignored hesitation → wait + clarify; language
mismatch → in-language reply; missed field → clean re-ask. Nothing else changes.

## Fields

| field | type | notes |
|---|---|---|
| `call_id` | string | provenance — which call produced this pair |
| `failure_dimension` | string | rubric dimension that fired (e.g. `barge_in`, `repair_quality`) |
| `rejected_turn` | string | what the agent actually said |
| `chosen_turn` | string | the corrected turn, differing only on the failure axis |
| `reason` | string | why chosen beats rejected, one sentence |
| `quality_delta` | float | scorecard-implied improvement (directional) |
| `needs_human_review` | bool | true until a human has eyeballed the pair |

## Export formats

Authored once as TRL conversational JSONL (`out/queue.jsonl`):

```json
{"prompt": [{"role": "system", "content": "Voice agent for appointment booking. Replies under 2 sentences. Never speak while the caller is mid-answer."}, {"role": "user", "content": "haan area... ante... Madhapur side anukunta, near the er... metro station"}], "chosen": [{"role": "assistant", "content": "Got it — Madhapur, near the metro station. Morning or evening slot work better?"}], "rejected": [{"role": "assistant", "content": "I need your complete address with pincode landmark and door number before we can proceed any further with this booking request, please provide all details now."}]}
```

Mirrored to OpenAI preference format (`out/queue_openai.jsonl`) by the 3-line mapper in
`pipeline/dpo_export.py`: `{"input": {"messages": prompt}, "preferred_output": chosen, "non_preferred_output": rejected}`.
