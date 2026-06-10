# Schema: cost

Estimated economics of one call. Honest by construction: every figure derived from turn counts ×
public per-unit price estimates, and the schema carries its own disclaimer field so no rendering
of it can drop the caveat.

## Fields

| field | type | notes |
|---|---|---|
| `call_id` | string | joins to call_log |
| `duration_s` | float | last end_ms / 1000 |
| `turn_count` | int | total turns |
| `est_llm_calls` | int | ≈ agent turns |
| `est_cost_total` | float USD | turns × per-turn LLM/TTS/STT estimate |
| `est_cost_per_success_note` | string | fixed: `"estimated, prototype"` — rendered wherever cost is shown |

Cost per **successful** call is computed at the aggregate level (analytics): total estimated cost
of a cohort / number of completed-task calls in it. Failed calls make the denominator smaller —
that is the business-value chart.

## Example

```json
{
  "call_id": "hero_001",
  "duration_s": 102.4,
  "turn_count": 14,
  "est_llm_calls": 7,
  "est_cost_total": 0.038,
  "est_cost_per_success_note": "estimated, prototype"
}
```
