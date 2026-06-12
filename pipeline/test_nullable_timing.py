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

from schemas import validate                              # noqa: E402
from signals import analyze, load_rubric, timing_mode, turn_metrics  # noqa: E402
from score import build_record, build_analytics           # noqa: E402
from normalize import validate_call                        # noqa: E402
import chart                                                # noqa: E402

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


def mixed_call():
    """t1 timed, t2 untimed, t3 timed — the partial clock Codex used to reproduce a false t1->t3 gap."""
    c = untimed_call()
    c["call_id"] = "m_test"; c["source"] = "bolna"; c["stress_profile"] = "clean"
    c["turns"][0]["start_ms"], c["turns"][0]["end_ms"] = 0, 1500
    c["turns"][1]["start_ms"], c["turns"][1]["end_ms"] = None, None
    c["turns"][2]["start_ms"], c["turns"][2]["end_ms"] = 4000, 5500
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

    # 4) mixed timing: rejected at the boundary AND no false floor-transfer is manufactured
    print("\n[4] mixed-timing call (t1 timed, t2 null, t3 timed)")
    mc = mixed_call()
    check(timing_mode(mc["turns"]) == "mixed", "timing_mode classifies it 'mixed'")
    events = turn_metrics(mc["turns"])
    check(events == [], "turn_metrics yields NO events (no fake t1->t3 join across the untimed turn)")
    check(analyze(mc["turns"], load_rubric())["failures"] == [], "no fabricated timing failures")
    try:
        validate_call(mc)
        check(False, "normalize.validate_call should REJECT a mixed-timing call")
    except AssertionError:
        check(True, "normalize.validate_call rejects mixed timing")
    # and the profile coupling: all-null timing requires stress_profile 'unmeasured'
    try:
        bad_prof = untimed_call(); bad_prof["stress_profile"] = "clean"
        validate_call(bad_prof)
        check(False, "all-null timing with non-unmeasured profile should be REJECTED")
    except AssertionError:
        check(True, "all-null timing requires stress_profile 'unmeasured'")
    check(validate_call(untimed_call()) is not None and validate_call(timed_call()) is not None,
          "both all-null and all-timed calls pass the boundary validator")

    # 5) analytics over a timed + untimed mix is coverage-aware (avg_overall over timed only)
    print("\n[5] coverage-aware analytics (timed + untimed records)")
    recs = [build_record(timed_call()), build_record(untimed_call())]
    A = build_analytics(recs)
    validate(A, "analytics")
    check(A["timing_coverage"] == {"timed": 1, "unmeasured": 1}, f"timing_coverage split (got {A.get('timing_coverage')})")
    check(A["avg_overall"] == recs[0]["scorecard"]["overall"], "avg_overall is over the timed call only")

    # 6) chart is null-safe: an unmeasured profile with 0 successes -> cost_per_successful_call null
    print("\n[6] chart null-safety (unmeasured profile, no successes -> null cost)")
    unm_prof = next(b for b in A["by_stress_profile"] if b["stress_profile"] == "unmeasured")
    check(unm_prof["cost_per_successful_call"] is None, "unmeasured profile cost_per_successful_call is null")
    check(chart._safe_max([None, 0.2]) == 0.2 and chart._safe_max([None]) == 1, "_safe_max ignores None")
    try:
        chart.render(A, Path("/tmp/vf_chart_test"))
        check(True, "chart.render() does not crash on a null cost_per_successful_call")
    except Exception as e:
        check(False, f"chart.render crashed: {e}")

    print("\n" + ("NULLABLE-TIMING TEST PASSED ✓" if not FAILS else f"FAILED ({len(FAILS)} checks)"))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
