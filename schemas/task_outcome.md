# Schema: task_outcome

Did the call achieve what it existed to achieve? Deterministic where possible: a required-field
checklist per workflow, not a vibe. Feeds the `task_completion` rubric dimension.

## Fields

| field | type | notes |
|---|---|---|
| `call_id` | string | joins to call_log |
| `task_completed` | bool | all required fields captured AND no unresolved blocker |
| `required_fields` | array | the checklist |
| `required_fields[].name` | string | e.g. `service_area`, `time_slot`, `callback_number` |
| `required_fields[].captured` | bool | was a usable value obtained |
| `required_fields[].value` | string\|null | the captured value, verbatim-ish |
| `escalation_needed` | bool | call should route to a human |
| `confidence` | float 0–1 | extraction confidence (judge-assisted extraction is flagged) |

## Example

```json
{
  "call_id": "hero_001",
  "task_completed": false,
  "required_fields": [
    {"name": "service_area", "captured": true, "value": "Madhapur, near metro station"},
    {"name": "time_slot", "captured": false, "value": null}
  ],
  "escalation_needed": false,
  "confidence": 0.9
}
```
