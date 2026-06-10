# Schema: scorecard

One call's eval result across every rubric dimension. The contract that makes this trustworthy:
**every dimension — deterministic or judged — carries a reason and evidence turn ids.**
No bare numbers anywhere.

## Fields

| field | type | notes |
|---|---|---|
| `call_id` | string | joins to call_log |
| `dimensions` | array | one entry per rubric.yaml dimension |
| `dimensions[].name` | string | e.g. `barge_in`, `language_match` |
| `dimensions[].type` | enum | `deterministic \| judge` |
| `dimensions[].score` | float 0–1 | normalized; deterministic dims map measurements onto this |
| `dimensions[].reason` | string | one falsifiable sentence ("agent overlapped user by 800ms at 0:14") |
| `dimensions[].evidence_turn_ids` | array | turn ids the reason points at |
| `overall` | float 0–1 | weighted by rubric.yaml weights — recomputable live |

## Example

```json
{
  "call_id": "hero_001",
  "dimensions": [
    {"name": "barge_in", "type": "deterministic", "score": 0.0,
     "reason": "agent began speaking 800ms before user turn t2 ended (overlap at 0:14)",
     "evidence_turn_ids": ["t2", "t3"]},
    {"name": "repair_quality", "type": "judge", "score": 0.25,
     "reason": "user gave an ambiguous locality; agent demanded full address instead of confirming the partial",
     "evidence_turn_ids": ["t2", "t3"]}
  ],
  "overall": 0.41
}
```
