#!/usr/bin/env python3
"""Tiny synthetic-call tests for the threshold sweep logic.

Run: .venv/bin/python experiments/jun13_eval/timing/test_timing_sweep.py
Pure stdlib asserts (no API calls, no installs). Validates that the custom-threshold
event selection in timing_sweep.call_events matches the documented rules and that the
helper math (jaccard, rank, kendall_tau_like) behaves.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import timing_sweep as ts


def synthetic_call():
    """A 5-turn fully-timed call with one engineered overlap and one engineered gap.

    Timeline (ms):
      t1 agent  0   .. 1000
      t2 user   1200 .. 1800   -> handoff agent->user: gap 200 (not a user->agent latency)
      t3 agent  1650 .. 2000   -> overlap 150ms onto t2 (agent interrupts user) ; prev=user
      t4 user   2200 .. 2600   -> agent->user gap 200
      t5 agent  3600 .. 4000   -> user->agent handoff, gap 1000ms (laggy at default 800)
    """
    return {
        "call_id": "synthetic_0001",
        "source": "synthetic",
        "stress_profile": "interruption",
        "workflow_type": "test",
        "language": "en",
        "turns": [
            {"turn_id": "t1", "speaker": "agent", "start_ms": 0, "end_ms": 1000, "text": "hi"},
            {"turn_id": "t2", "speaker": "user", "start_ms": 1200, "end_ms": 1800, "text": "hello"},
            {"turn_id": "t3", "speaker": "agent", "start_ms": 1650, "end_ms": 2000, "text": "wait"},
            {"turn_id": "t4", "speaker": "user", "start_ms": 2200, "end_ms": 2600, "text": "ok"},
            {"turn_id": "t5", "speaker": "agent", "start_ms": 3600, "end_ms": 4000, "text": "done"},
        ],
    }


def test_default_thresholds():
    c = synthetic_call()
    # default overlap>100, lag>800
    ce = ts.call_events(c, overlap_thr=100, lag_thr=800)
    # the t2->t3 pair has overlap 150 > 100  => 1 barge-in
    assert ce["n_barge_in"] == 1, ce
    assert "t2->t3" in ce["barge_pairs"], ce
    # the t4->t5 pair is user->agent gap 1000 > 800 => 1 laggy
    assert ce["n_latency_gap"] == 1, ce
    assert "t4->t5" in ce["lag_pairs"], ce
    assert ce["n_total"] == 2


def test_overlap_threshold_raises_drops_bargein():
    c = synthetic_call()
    # overlap 150: counted at thr 0/100 but NOT at 200/300/500
    assert ts.call_events(c, 0, 800)["n_barge_in"] == 1
    assert ts.call_events(c, 100, 800)["n_barge_in"] == 1
    assert ts.call_events(c, 200, 800)["n_barge_in"] == 0
    assert ts.call_events(c, 300, 800)["n_barge_in"] == 0


def test_lag_threshold_raises_drops_latency():
    c = synthetic_call()
    # gap 1000: laggy at lag 500/800 but NOT at 1000(strict >)/1500/2000
    assert ts.call_events(c, 100, 500)["n_latency_gap"] == 1
    assert ts.call_events(c, 100, 800)["n_latency_gap"] == 1
    assert ts.call_events(c, 100, 1000)["n_latency_gap"] == 0  # strict >, 1000 not > 1000
    assert ts.call_events(c, 100, 1500)["n_latency_gap"] == 0


def test_latency_only_clean_user_to_agent():
    """The agent->user gap (t2 ends 1800, t4 user... ) must never count as latency_gap;
    only user->agent handoffs with fto>=0 are latency candidates."""
    c = synthetic_call()
    ce = ts.call_events(c, overlap_thr=100, lag_thr=500)
    # only t4->t5 (user->agent) qualifies, not any agent->user pair
    assert ce["lag_pairs"] == ["t4->t5"], ce


def test_unmeasured_yields_no_events():
    c = synthetic_call()
    for t in c["turns"]:
        t["start_ms"] = None
        t["end_ms"] = None
    ce = ts.call_events(c, 0, 500)
    assert ce["n_total"] == 0, ce  # turn_metrics returns [] for unmeasured


def test_jaccard():
    assert ts.jaccard(set(), set()) == 1.0
    assert ts.jaccard({"a"}, set()) == 0.0
    assert ts.jaccard({"a", "b"}, {"b", "c"}) == 1 / 3


def test_rank_and_tau():
    setting = {"per_call": {
        "a": {"n_total": 5}, "b": {"n_total": 3}, "c": {"n_total": 0}, "d": {"n_total": 3},
    }}
    ranked = ts.rank_calls(setting)
    ids = [cid for cid, _ in ranked]
    assert ids == ["a", "b", "d"], ids  # c dropped (0); ties broken by id
    # identical ranking => tau 1.0; reversed => -1.0
    assert abs(ts.kendall_tau_like(["a", "b", "d"], ["a", "b", "d"]) - 1.0) < 1e-9
    assert abs(ts.kendall_tau_like(["a", "b", "d"], ["d", "b", "a"]) + 1.0) < 1e-9


def test_consistency_with_pipeline_analyze():
    """At the rubric defaults, our event counts must equal pipeline.signals.analyze()
    on the synthetic call (single source of truth for the FTO rules)."""
    from pipeline.signals import analyze
    c = synthetic_call()
    rubric = {"dimensions": {"barge_in": {"threshold_overlap_ms": 100},
                             "latency_gap": {"laggy_ms": 800}}}
    a = analyze(c["turns"], rubric)
    ce = ts.call_events(c, 100, 800)
    assert len(a["barge_ins"]) == ce["n_barge_in"], (a["barge_ins"], ce)
    assert a["latency"]["n_laggy"] == ce["n_latency_gap"], (a["latency"], ce)


def run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
        passed += 1
    print(f"\n{passed}/{len(tests)} tests passed")


if __name__ == "__main__":
    run()
