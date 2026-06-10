#!/usr/bin/env python3
"""Normalize raw sources into schemas/call_log.md shape. SPEC §7.D. — Block 3.

Adapters (one function per source, all emit identical call_log JSON to data/normalized/):
- spokenwoz: train+dev from spokenwoz.github.io. Word-level timestamps, separated channels.
  Turn bounds synthesized from word times: first word start -> last word end per same-speaker run.
  Protocol data: few real barge-ins -> latency-rich. CC BY-NC (eval use).
- ami: HF `edinburghcstr/ami` (CC BY 4.0). Real overlap (~20%). Use 2-3 calls, narrowly.
- hero: data/hero/turns.json is ALREADY ground truth from the assembly timeline — pass-through + validate.
- bolna (bonus, §7.G): timing from GET /executions/{id}/log created_at diffs ONLY.
  Never the top-level transcript (single string, no roles, barge-ins scrubbed).

Re-zero every call to its own ms clock. Set stress_profile per call. One clock per call.
"""
raise SystemExit("TODO Block 3 (June 11): spokenwoz + ami adapters. Hero turns.json is written in Block 1.")
