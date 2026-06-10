# Architecture

## Flow

```
raw call (audio + provider log / corpus file)
  │
  ▼ pipeline/normalize.py        one adapter per source → schemas/call_log
  │
  ├─▶ pipeline/signals.py        deterministic FTO math: barge-in overlap ms, latency gaps
  │                              (median + p90, never mean) — the timing ground truth
  ├─▶ pipeline/judge.py          Gemini Flash, temp 0, JSON mode; per-dimension
  │                              {score, reason, evidence_turn_ids}; disk-cached
  ▼
pipeline/score.py                merges deterministic + judged dims, weights from rubric.yaml
  │                              → out/calls.json + out/call_<id>.json (scorecards)
  ├─▶ pipeline/dpo_export.py     failures → (chosen, rejected) pairs → out/queue.jsonl (+ OpenAI mirror)
  ├─▶ pipeline/costs.py          turn-based cost estimates
  └─▶ pipeline/crosscut.py       stress-profile × outcome × cost → out/analytics.json
        │
        ▼
      web/                       static dashboard, read-only over out/*.json — no backend, no DB
```

## Principles

1. **rubric.yaml is the only config.** Dimensions, weights, thresholds live there. Editing it and
   rerunning `score.py` changes every scorecard — demonstrably, on demo day.
2. **Deterministic core.** Timing failures (barge-in, latency) are arithmetic on turn timestamps,
   not model opinions. The LLM judge is reserved for dimensions that need judgment
   (language match, faithfulness, repair quality) — and must show its work.
3. **Reasons + evidence everywhere.** A score without a falsifiable reason and turn ids is a bug.
4. **Idempotent and cheap to rerun.** Judge responses cached to `data/.judge_cache/` keyed by
   (call_id, dimension, prompt_hash). Pipeline reruns are free unless inputs changed.
5. **Vendor-neutral by contract.** Anything that can produce `call_log` JSON is a supported
   source: SpokenWOZ, AMI, a constructed call, Bolna execution logs (adapter), or any
   transcript+timestamps pair.

## Two-clock rule

All timestamps within a call share one clock (ms from call start). Cross-source ingestion
must re-zero to that clock during normalization. Sources lacking end timestamps get
latency analysis only — overlap is never inferred.
