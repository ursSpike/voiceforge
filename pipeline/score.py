#!/usr/bin/env python3
"""Merge deterministic signals + judged dimensions into scorecards. SPEC §7.A scorecard. — Block 3.

- Reads rubric.yaml for the dimension list, types, and weights (ONLY source of config).
- Deterministic dims (barge_in, latency_gap, task_completion): map measurements -> 0..1 score
  with a reason string built from the actual numbers and evidence turn ids.
- Judge dims: from judge.py (cached).
- overall = sum(weight_i * score_i). Weights live-editable -> rerun -> dashboard updates.
- Emits out/call_<id>.json per call + out/calls.json index.
"""
raise SystemExit("TODO Block 3 (June 11).")
