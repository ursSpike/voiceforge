#!/usr/bin/env python3
"""Failures -> (chosen, rejected) preference pairs. SPEC §7.F. — Block 5 / Batch 5.

For each failed/suboptimal call: one pair where the ONLY meaningful difference is the
detected failure axis (over-talk -> shorter turn; ignored pause -> wait+clarify;
language-mismatch -> in-language reply; missed field -> clean re-ask).

Outputs:
- out/queue.jsonl          TRL conversational: {"prompt":[...], "chosen":[...], "rejected":[...]}
- out/queue_openai.jsonl   the 3-line mapper:
    {"input": {"messages": prompt}, "preferred_output": chosen, "non_preferred_output": rejected}

Target 10-20 pairs. Each carries provenance (call_id, failure_dimension) per
schemas/improvement_example.md, and needs_human_review=true by default.
Built only AFTER the eval core + blind labels exist (do not start before then).
"""
raise SystemExit("TODO Block 5 / Batch 5 (after eval core + blind labels).")
