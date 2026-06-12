#!/usr/bin/env python3
"""Tests for reliability_audit using SMALL synthetic fixtures.

Run: .venv/bin/python test_reliability_audit.py
Stdlib only; no test framework dependency. Covers metric correctness on
hand-checkable confusion matrices, a prevalence-imbalanced case, an empty
slice, a tiny (n<MIN_N) slice, perfect agreement, and bootstrap determinism.
"""
import math

import reliability_audit as ra


def approx(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol


def case(name, ok):
    print(f"  {'OK ' if ok else 'XX '} {name}")
    assert ok, name


def test_known_confusion():
    # fail=positive. Build a hand-computed 2x2:
    # TP (h_fail,j_fail)=3, FN (h_fail,j_success)=2, FP (h_success,j_fail)=1, TN=4 ; n=10
    pairs = (
        [("fail", "fail")] * 3
        + [("fail", "success")] * 2
        + [("success", "fail")] * 1
        + [("success", "success")] * 4
    )
    m = ra.metrics(pairs)
    case("n == 10", m["n"] == 10)
    case("confusion tp", m["confusion"]["tp_h_fail_j_fail"] == 3)
    case("confusion fn", m["confusion"]["fn_h_fail_j_success"] == 2)
    case("confusion fp", m["confusion"]["fp_h_success_j_fail"] == 1)
    case("confusion tn", m["confusion"]["tn_h_success_j_success"] == 4)
    case("raw agreement = 7/10", approx(m["raw_agreement"], 0.7))
    case("recall = 3/5", approx(m["failure_recall"], 0.6))
    case("precision = 3/4", approx(m["failure_precision"], 0.75))
    case("specificity = 4/5", approx(m["specificity"], 0.8))
    case("balanced acc = (0.6+0.8)/2", approx(m["balanced_accuracy"], 0.7))
    case("youden J = 0.6+0.8-1", approx(m["youden_j"], 0.4))
    # F1 = 2*0.75*0.6/(0.75+0.6) = 0.9/1.35
    case("f1 = 2/3", approx(m["f1_failure"], 0.9 / 1.35))
    # MCC = (TP*TN - FP*FN)/sqrt(...) = (12-2)/sqrt(4*5*5*6)=10/sqrt(600)
    case("mcc = 10/sqrt(600)", approx(m["mcc"], 10 / math.sqrt(600)))
    # kappa: po=0.7; ph_pos=5/10=.5, pj_pos=4/10=.4; pe=.5*.4+.5*.6=.5; k=(.7-.5)/.5=.4
    case("kappa = 0.4", approx(m["kappa"], 0.4))


def test_perfect_agreement():
    pairs = [("fail", "fail")] * 4 + [("success", "success")] * 6
    m = ra.metrics(pairs)
    case("perfect raw agreement", approx(m["raw_agreement"], 1.0))
    case("perfect kappa", approx(m["kappa"], 1.0))
    case("perfect mcc", approx(m["mcc"], 1.0))
    case("perfect recall", approx(m["failure_recall"], 1.0))
    case("perfect specificity", approx(m["specificity"], 1.0))


def test_prevalence_imbalanced():
    # Heavy success prevalence; judge calls everything success.
    # 18 success (all agree) + 2 fail (both missed). High raw agreement, but
    # recall=0 and kappa=0 — the prevalence paradox in action.
    pairs = [("success", "success")] * 18 + [("fail", "success")] * 2
    m = ra.metrics(pairs)
    case("imbalanced n=20", m["n"] == 20)
    case("imbalanced high raw agreement 18/20", approx(m["raw_agreement"], 0.9))
    case("imbalanced recall = 0", approx(m["failure_recall"], 0.0))
    case("imbalanced specificity = 1", approx(m["specificity"], 1.0))
    case("imbalanced balanced acc = 0.5", approx(m["balanced_accuracy"], 0.5))
    # judge never says fail -> precision undefined (tp+fp=0)
    case("imbalanced precision undefined (None)", m["failure_precision"] is None)
    # pe: ph_pos=2/20=.1, pj_pos=0 -> pe=.1*0+.9*1=.9; k=(.9-.9)/(1-.9)=0
    case("imbalanced kappa = 0 (no chance-corrected signal)", approx(m["kappa"], 0.0))
    # MCC denom has (tp+fp)=0 -> 0 -> None
    case("imbalanced mcc undefined (None)", m["mcc"] is None)


def test_empty_slice():
    m = ra.metrics([])
    case("empty slice n=0", m["n"] == 0)
    case("empty slice has no confusion key", "confusion" not in m)
    case("empty bootstrap returns None", ra.bootstrap_ci([], ra._kappa) is None)


def test_tiny_slice_min_n_rule():
    # slice_table should flag n < MIN_N (5) as too_small_to_rank.
    rows = [
        {"human": "fail", "judge": "fail", "call_id": "a", "lang": "x"},
        {"human": "success", "judge": "success", "call_id": "b", "lang": "x"},
        {"human": "fail", "judge": "success", "call_id": "c", "lang": "y"},
    ]
    tbl = ra.slice_table(rows, "lang")
    case("tiny slice x flagged too small", tbl["x"]["too_small_to_rank"] is True)
    case("tiny slice x note present", tbl["x"]["note"].startswith("too small"))
    case("tiny slice y (n=1) flagged", tbl["y"]["too_small_to_rank"] is True)
    case("tiny slice x agreement 2/2", tbl["x"]["agreement_fraction"] == "2/2")

    # a slice at/above MIN_N is NOT flagged
    big = [{"human": "success", "judge": "success", "call_id": f"c{i}", "lang": "z"} for i in range(5)]
    tblb = ra.slice_table(big, "lang")
    case("n=5 slice not flagged (>= MIN_N)", tblb["z"]["too_small_to_rank"] is False)


def test_bootstrap_determinism():
    pairs = [("fail", "fail")] * 3 + [("fail", "success")] * 2 \
        + [("success", "fail")] + [("success", "success")] * 4
    a = ra.bootstrap_ci(pairs, ra._kappa)
    b = ra.bootstrap_ci(pairs, ra._kappa)
    case("bootstrap is deterministic (same seed -> same CI)", a == b)
    case("bootstrap lo <= hi", a[0] <= a[1])


def test_archetype_replication():
    # Spot-check the replicated archetype precedence (fail: workflow > language).
    row = {"primary_label": "fail",
           "positive_tags": "",
           "negative_tags": "workflow_or_tool_failed|wrong_language_or_tone",
           "context_tags": ""}
    case("archetype workflow beats language", ra.archetype(row) == "workflow_failure")
    row2 = {"primary_label": "success",
            "positive_tags": "handled_confusion_well",
            "negative_tags": "wrong_language_or_tone",
            "context_tags": ""}
    case("archetype recovered_success", ra.archetype(row2) == "recovered_success")
    row3 = {"primary_label": "success", "positive_tags": "", "negative_tags": "", "context_tags": ""}
    case("archetype seamless_success", ra.archetype(row3) == "seamless_success")
    row4 = {"primary_label": "unsure", "positive_tags": "", "negative_tags": "", "context_tags": ""}
    case("archetype unsure -> ambiguous", ra.archetype(row4) == "ambiguous_or_unassessable")


def test_real_run_targets():
    """Integration: the real audit must reproduce all read-only targets."""
    result = ra.run()
    case("real n == 45", result["overall"]["n"] == 45)
    for name, c in result["reproduction_targets"].items():
        case(f"reproduction target {name} matches", c["match"] is True)
    case("unsupported claim flagged", result["unsupported_claim_flag"]["verdict"] == "UNSUPPORTED")
    case("flag: 9 of 13 hi-en disagreements (count is true)",
         result["unsupported_claim_flag"]["n_disagreements_hi_en"] == 9
         and result["unsupported_claim_flag"]["n_disagreements_total"] == 13)


if __name__ == "__main__":
    tests = [
        test_known_confusion,
        test_perfect_agreement,
        test_prevalence_imbalanced,
        test_empty_slice,
        test_tiny_slice_min_n_rule,
        test_bootstrap_determinism,
        test_archetype_replication,
        test_real_run_targets,
    ]
    for t in tests:
        print(t.__name__)
        t()
    print("\nALL TESTS PASSED")
