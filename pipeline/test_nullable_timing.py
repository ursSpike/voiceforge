#!/usr/bin/env python3
"""Nullable-timing contract test (Batch 2R). Proves text-only / no-clock calls flow through the
deterministic pipeline HONESTLY — start_ms/end_ms null, stress_profile 'unmeasured', timing
dimensions (barge_in, latency_gap) OMITTED (never scored as a fake perfect 1.0), duration_s null —
while timed calls are completely unaffected.

    .venv/bin/python pipeline/test_nullable_timing.py

Touches no files: builds synthetic calls in memory, runs build_record + signals.analyze, validates
against the call_record schema, asserts the dimension set. Does NOT read or write data/normalized/.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

from schemas import validate                      # noqa: E402
from signals import analyze, load_rubric          # noqa: E402
from score import build_record, build_cost        # noqa: E402

FAILS = []


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def untimed_call():
    return {
        "call_id": "u_test", "source": "code_mixed_dialog", "language": "hi-en",
        "stress_profile": "unmeasured", "workflow_type": "restaurant_reservation",
        "audio_path": None,
        "turns": [
            {"turn_id": "t1", "speaker": "agent", "text": "namaste, restaurant table?", "start_ms": None, "end_ms": None},
            {"turn_id": "t2", "speaker": "user", "text": "haan table chahiye south indian", "start_ms": None, "end_ms": None},
            {"turn_id": "t3", "speaker": "agent", "text": "theek hai, booked", "start_ms": None, "end_ms": None},
        ],
        "metadata": {"timing_observed": False, "source_dataset": "code_mixed_dialog", "license": "Apache-2.0"},
    }


def timed_call():
    c = untimed_call()
    c["call_id"] = "t_test"; c["source"] = "bolna"; c["stress_profile"] = "clean"
    for i, t in enumerate(c["turns"]):
        t["start_ms"] = i * 2000
        t["end_ms"] = i * 2000 + 1500
    c["metadata"] = {"timing_observed": True}
    return c


def main():
    print("nullable-timing contract test")

    # 1) signals.analyze over all-untimed turns: no events, no failures, no crash
    print("\n[1] signals.analyze on untimed turns")
    sig = analyze(untimed_call()["turns"], load_rubric())
    check(sig["events"] == [], "no floor-transfer events")
    check(sig["barge_ins"] == [], "no barge-ins inferred")
    check(sig["failures"] == [], "no timing failures fabricated")
    check(sig["latency"]["median_gap_ms"] is None and sig["latency"]["n_handoffs"] == 0, "latency is None/0 (unmeasured)")

    # 2) build_record on the untimed call: validates, timing dims OMITTED, duration null
    print("\n[2] build_record on untimed (text-only) call")
    rec = build_record(untimed_call())
    validate(rec, "call_record")
    dim_names = {d["name"] for d in rec["scorecard"]["dimensions"]}
    check(dim_names == {"task_completion"}, f"scorecard dims = task_completion only (got {sorted(dim_names)})")
    check("barge_in" not in dim_names and "latency_gap" not in dim_names, "timing dims omitted (not faked as 1.0)")
    tc = next(d for d in rec["scorecard"]["dimensions"] if d["name"] == "task_completion")
    check(rec["scorecard"]["overall"] == tc["score"], "overall re-normalizes to the single present dim")
    check(rec["cost"]["duration_s"] is None, "cost.duration_s is null (no fabricated duration)")
    check(rec["cost"]["est_cost_total"] > 0, "cost still estimated from turn count")
    check(rec["failures"] == [], "no failures on an unmeasured call")

    # 3) timed call is UNAFFECTED: timing dims present, duration computed
    print("\n[3] build_record on a timed call (regression guard)")
    trec = build_record(timed_call())
    validate(trec, "call_record")
    tdims = {d["name"] for d in trec["scorecard"]["dimensions"]}
    check(tdims == {"barge_in", "latency_gap", "task_completion"}, f"timed call keeps all 3 dims (got {sorted(tdims)})")
    check(trec["cost"]["duration_s"] is not None, "timed call has a real duration_s")

    print("\n" + ("NULLABLE-TIMING TEST PASSED ✓" if not FAILS else f"FAILED ({len(FAILS)} checks)"))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
