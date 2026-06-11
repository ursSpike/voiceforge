#!/usr/bin/env python3
"""Per-call cost estimates. SPEC §7.A cost schema. — Block 8.

cost = turns x per-turn LLM/TTS/STT public-price estimate. Every output carries
est_cost_per_success_note = "estimated, prototype". Aggregate cost-per-successful-call
is computed in crosscut.py (cohort cost / completed calls).
"""
raise SystemExit("ABSORBED into pipeline/score.py:build_cost() (canonical). This file retained for "
                 "SPEC §7 naming only. Cost chart IMAGES come in Batch 8.")
