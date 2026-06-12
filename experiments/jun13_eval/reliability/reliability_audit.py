#!/usr/bin/env python3
"""Deterministic judge-reliability audit over FROZEN labels + judge results.

Agent 1 — Reliability Metrics. ISOLATED experiment.
Reads (read-only): eval/labels_spike.csv, out/judge_results.json, out/calls.json.
Writes only under experiments/jun13_eval/reliability/.

Stdlib only. Deterministic. Bootstrap seeded with 13, 2000 resamples.
`fail` is the RISK/positive class for recall/precision/MCC.

Pairing: human primary_label in {success, fail} AND judge binary label in
{success, fail}. The single human-unsure call is excluded by construction.
"""
import csv
import json
import math
import random
from collections import Counter, OrderedDict
from pathlib import Path

# ---- paths (repo root inferred from this file: experiments/jun13_eval/reliability/) ----
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LABELS_CSV = ROOT / "eval" / "labels_spike.csv"
JUDGE_JSON = ROOT / "out" / "judge_results.json"
CALLS_JSON = ROOT / "out" / "calls.json"

SEED = 13
N_BOOT = 2000
MIN_N = 5  # slices below this are reported but "too small to rank — not a finding"
POS = "fail"   # risk / positive class
NEG = "success"


# ---------------------------------------------------------------- loading
def load():
    labels = list(csv.DictReader(LABELS_CSV.open(encoding="utf-8")))
    jd = json.loads(JUDGE_JSON.read_text(encoding="utf-8"))
    calls = {c["call_id"]: c for c in json.loads(CALLS_JSON.read_text(encoding="utf-8"))}
    judge = {cid: v.get("binary", {}).get("label") for cid, v in jd.get("calls", {}).items()}
    return labels, judge, calls, jd


def tags_of(row):
    split = lambda s: [t for t in (s or "").split("|") if t]
    return split(row["positive_tags"]), split(row["negative_tags"]), split(row["context_tags"])


def archetype(row):
    """Replicated verbatim from pipeline/demo_report.py archetype() (read, not imported)."""
    pos, neg, _ = tags_of(row)
    p = row["primary_label"]
    if p == "unsure":
        return "ambiguous_or_unassessable"
    if p == "success":
        if "handled_confusion_well" in pos and neg:
            return "recovered_success"
        return "brittle_success" if neg else "seamless_success"
    if "workflow_or_tool_failed" in neg:
        return "workflow_failure"
    if "wrong_language_or_tone" in neg:
        return "language_mismatch_failure"
    if "misunderstood_user" in neg or "missing_or_wrong_information" in neg:
        return "intent_or_slot_loss_failure"
    if "repeated_or_stuck" in neg or "poor_clarification_or_recovery" in neg:
        return "repair_loop_failure"
    return "intent_or_slot_loss_failure"


def length_bucket(n_turns):
    if n_turns <= 11:
        return "short (<=11 turns)"
    if n_turns <= 17:
        return "medium (12-17 turns)"
    return "long (>=18 turns)"


# ---------------------------------------------------------------- core metrics
def confusion(pairs):
    """Return TP/FP/FN/TN with fail=positive. pairs = list of (human, judge)."""
    tp = sum(1 for h, g in pairs if h == POS and g == POS)
    fp = sum(1 for h, g in pairs if h == NEG and g == POS)
    fn = sum(1 for h, g in pairs if h == POS and g == NEG)
    tn = sum(1 for h, g in pairs if h == NEG and g == NEG)
    return tp, fp, fn, tn


def metrics(pairs):
    """All point metrics for a set of (human, judge) pairs. None where undefined."""
    n = len(pairs)
    out = {"n": n}
    if n == 0:
        return out
    tp, fp, fn, tn = confusion(pairs)
    out["confusion"] = {"tp_h_fail_j_fail": tp, "fp_h_success_j_fail": fp,
                        "fn_h_fail_j_success": fn, "tn_h_success_j_success": tn}
    agree = tp + tn
    po = agree / n
    out["agree_count"] = agree
    out["raw_agreement"] = po

    # Cohen's kappa
    ph_pos = (tp + fn) / n          # human fail prevalence
    pj_pos = (tp + fp) / n          # judge fail prevalence
    pe = ph_pos * pj_pos + (1 - ph_pos) * (1 - pj_pos)
    out["kappa"] = 0.0 if pe >= 1 else (po - pe) / (1 - pe)

    # recall / precision / specificity (fail = positive)
    out["failure_recall"] = (tp / (tp + fn)) if (tp + fn) else None     # sensitivity
    out["failure_precision"] = (tp / (tp + fp)) if (tp + fp) else None
    out["specificity"] = (tn / (tn + fp)) if (tn + fp) else None
    rec = out["failure_recall"]
    spec = out["specificity"]
    out["balanced_accuracy"] = ((rec + spec) / 2) if (rec is not None and spec is not None) else None
    out["youden_j"] = ((rec + spec) - 1) if (rec is not None and spec is not None) else None

    # F1 (fail positive)
    prec = out["failure_precision"]
    if prec is not None and rec is not None and (prec + rec) > 0:
        out["f1_failure"] = 2 * prec * rec / (prec + rec)
    else:
        out["f1_failure"] = None

    # MCC
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    out["mcc"] = ((tp * tn - fp * fn) / denom) if denom > 0 else None

    return out


def bootstrap_ci(pairs, stat_fn, seed=SEED, n_boot=N_BOOT):
    """Deterministic percentile 95% CI. stat_fn(pairs)->float|None; skips None resamples."""
    n = len(pairs)
    if n == 0:
        return None
    rng = random.Random(seed)
    vals = []
    for _ in range(n_boot):
        s = [pairs[rng.randrange(n)] for _ in range(n)]
        v = stat_fn(s)
        if v is not None and not (isinstance(v, float) and math.isnan(v)):
            vals.append(v)
    if not vals:
        return None
    vals.sort()
    lo = vals[int(0.025 * len(vals))]
    hi = vals[int(0.975 * len(vals))]
    return [lo, hi, len(vals)]


# stat extractors for bootstrap
def _kappa(pairs):
    return metrics(pairs).get("kappa")


def _bal_acc(pairs):
    return metrics(pairs).get("balanced_accuracy")


def _recall(pairs):
    return metrics(pairs).get("failure_recall")


def _precision(pairs):
    return metrics(pairs).get("failure_precision")


def _mcc(pairs):
    return metrics(pairs).get("mcc")


def _agreement(pairs):
    return metrics(pairs).get("raw_agreement")


# ---------------------------------------------------------------- slicing
def build_pairs(labels, judge, calls):
    """Rows that satisfy the pairing rule, enriched with slice keys."""
    rows = []
    for r in labels:
        h = r["primary_label"]
        g = judge.get(r["call_id"])
        if h not in (POS, NEG) or g not in (POS, NEG):
            continue
        c = calls.get(r["call_id"], {})
        rows.append({
            "call_id": r["call_id"],
            "human": h,
            "judge": g,
            "agree": h == g,
            "confidence": r["confidence"],
            "language": c.get("language"),
            "source": c.get("source"),
            "stress_profile": c.get("stress_profile"),
            "n_turns": len(c.get("turns", [])),
            "length_bucket": length_bucket(len(c.get("turns", []))),
            "archetype": archetype(r),
        })
    return rows


def slice_table(rows, key):
    """Per-value agreement + point metrics, with min-n flag. Deterministic ordering."""
    groups = OrderedDict()
    for r in sorted(rows, key=lambda x: (str(x[key]), x["call_id"])):
        groups.setdefault(r[key], []).append(r)
    table = OrderedDict()
    for val, grp in groups.items():
        pairs = [(g["human"], g["judge"]) for g in grp]
        m = metrics(pairs)
        n = m["n"]
        agree = m.get("agree_count", 0)
        entry = {
            "n": n,
            "agree_count": agree,
            "agreement_fraction": f"{agree}/{n}",
            "agreement_rate": round(m.get("raw_agreement", 0.0), 4),
            "n_human_fail": sum(1 for g in grp if g["human"] == POS),
            "n_human_success": sum(1 for g in grp if g["human"] == NEG),
            "kappa": _round(m.get("kappa")),
            "failure_recall": _round(m.get("failure_recall")),
            "failure_precision": _round(m.get("failure_precision")),
            "specificity": _round(m.get("specificity")),
            "balanced_accuracy": _round(m.get("balanced_accuracy")),
            "mcc": _round(m.get("mcc")),
            "too_small_to_rank": n < MIN_N,
        }
        if n < MIN_N:
            entry["note"] = "too small to rank — not a finding"
        table[str(val)] = entry
    return table


def _round(x, nd=4):
    return None if x is None else round(x, nd)


# ---------------------------------------------------------------- reproduction targets
def reproduction(rows, overall):
    """Reproduce-or-refute the read-only observations with exact counts."""
    def agr(filt):
        grp = [r for r in rows if filt(r)]
        a = sum(1 for r in grp if r["agree"])
        return a, len(grp)

    checks = OrderedDict()

    a, n = agr(lambda r: True)
    checks["all"] = {"claim": "32/45", "observed": f"{a}/{n}", "match": (a, n) == (32, 45)}

    a, n = agr(lambda r: r["language"] == "hi-en")
    checks["hi_en"] = {"claim": "22/31", "observed": f"{a}/{n}", "match": (a, n) == (22, 31)}

    a, n = agr(lambda r: r["language"] == "en")
    checks["english"] = {"claim": "9/13", "observed": f"{a}/{n}", "match": (a, n) == (9, 13)}

    a, n = agr(lambda r: r["confidence"] == "high")
    checks["high_confidence"] = {"claim": "24/29", "observed": f"{a}/{n}", "match": (a, n) == (24, 29)}

    a, n = agr(lambda r: r["confidence"] == "medium")
    checks["medium_confidence"] = {"claim": "8/16", "observed": f"{a}/{n}", "match": (a, n) == (8, 16)}

    def near(observed, target, tol=0.01):
        return observed is not None and abs(observed - target) <= tol

    checks["balanced_accuracy"] = {
        "claim": "~0.628", "observed": _round(overall["balanced_accuracy"]),
        "match": near(overall["balanced_accuracy"], 0.628)}
    checks["failure_recall"] = {
        "claim": "0.500", "observed": _round(overall["failure_recall"]),
        "match": near(overall["failure_recall"], 0.500)}
    checks["failure_precision"] = {
        "claim": "~0.308", "observed": _round(overall["failure_precision"]),
        "match": near(overall["failure_precision"], 0.308)}
    checks["specificity"] = {
        "claim": "~0.757", "observed": _round(overall["specificity"]),
        "match": near(overall["specificity"], 0.757)}
    checks["mcc"] = {
        "claim": "~0.217", "observed": _round(overall["mcc"]),
        "match": near(overall["mcc"], 0.217)}
    checks["kappa_vs_existing"] = {
        "claim": "0.206 (existing dashboard rounding)",
        "observed": _round(overall["kappa"], 3),
        "match": near(overall["kappa"], 0.206)}
    return checks


# ---------------------------------------------------------------- main
def run():
    labels, judge, calls, jd = load()
    rows = build_pairs(labels, judge, calls)
    pairs = [(r["human"], r["judge"]) for r in rows]
    overall = metrics(pairs)

    cis = {
        "kappa": bootstrap_ci(pairs, _kappa),
        "raw_agreement": bootstrap_ci(pairs, _agreement),
        "balanced_accuracy": bootstrap_ci(pairs, _bal_acc),
        "failure_recall": bootstrap_ci(pairs, _recall),
        "failure_precision": bootstrap_ci(pairs, _precision),
        "mcc": bootstrap_ci(pairs, _mcc),
    }

    slices = {
        "language": slice_table(rows, "language"),
        "source": slice_table(rows, "source"),
        "stress_profile": slice_table(rows, "stress_profile"),
        "length_bucket": slice_table(rows, "length_bucket"),
        "human_confidence": slice_table(rows, "confidence"),
        "archetype": slice_table(rows, "archetype"),
    }

    repro = reproduction(rows, overall)

    # the flagged unsupported claim — counts vs rates
    hi = slices["language"].get("hi-en", {})
    en = slices["language"].get("en", {})
    disagreements = [r["call_id"] for r in rows if not r["agree"]]
    cs_disagree = [r["call_id"] for r in rows if not r["agree"] and r["language"] == "hi-en"]
    en_disagree = [r["call_id"] for r in rows if not r["agree"] and r["language"] == "en"]

    flag = {
        "claim_in_dashboard": "9 of 13 disagreements are code-switched, so the judge is least reliable there",
        "verdict": "UNSUPPORTED",
        "n_disagreements_total": len(disagreements),
        "n_disagreements_hi_en": len(cs_disagree),
        "n_disagreements_en": len(en_disagree),
        "hi_en_agreement": f"{hi.get('agreement_fraction')} = {round(100 * hi.get('agreement_rate', 0), 1)}%",
        "en_agreement": f"{en.get('agreement_fraction')} = {round(100 * en.get('agreement_rate', 0), 1)}%",
        "why": ("hi-en and en agreement RATES are ~equal (71.0% vs 69.2%); the raw disagreement "
                "COUNT is a base-rate artifact because hi-en dominates the paired set (31 of 45). "
                "A higher count of disagreements where most calls live is not evidence of lower reliability there."),
        "better_supported_slice": {
            "dimension": "human_confidence",
            "high": f"{slices['human_confidence'].get('high', {}).get('agreement_fraction')} "
                    f"= {round(100 * slices['human_confidence'].get('high', {}).get('agreement_rate', 0), 1)}%",
            "medium": f"{slices['human_confidence'].get('medium', {}).get('agreement_fraction')} "
                      f"= {round(100 * slices['human_confidence'].get('medium', {}).get('agreement_rate', 0), 1)}%",
            "caveat": ("confidence is only known AFTER annotation, so it cannot route calls at inference "
                       "time. It supports a human REVIEW QUEUE (re-check low-confidence-prone calls), "
                       "NOT an auto-router."),
        },
    }

    result = {
        "meta": {
            "seed": SEED, "n_boot": N_BOOT, "min_n_rule": MIN_N,
            "positive_class": POS,
            "n_paired": overall["n"],
            "excluded_human_unsure": [r["call_id"] for r in labels if r["primary_label"] == "unsure"],
            "labels_csv": str(LABELS_CSV.relative_to(ROOT)),
            "judge_json": str(JUDGE_JSON.relative_to(ROOT)),
            "existing_kappa_in_run": jd.get("run", {}).get("rubric_hash") and None,  # placeholder; existing kappa is rendered, not stored in run
            "note_metrics_answer_different_questions": (
                "kappa (chance-corrected agreement), balanced_accuracy (mean of recall+specificity, "
                "prevalence-robust class performance), and the confusion matrix (raw counts) answer "
                "DIFFERENT questions. They are reported side by side; the uncomfortable kappa is NOT "
                "swapped for a flattering metric."),
        },
        "overall": {
            "n": overall["n"],
            "confusion_matrix_human_x_judge": overall["confusion"],
            "raw_agreement": _round(overall["raw_agreement"]),
            "agree_count": overall["agree_count"],
            "kappa": _round(overall["kappa"]),
            "balanced_accuracy": _round(overall["balanced_accuracy"]),
            "youden_j": _round(overall["youden_j"]),
            "failure_recall": _round(overall["failure_recall"]),
            "failure_precision": _round(overall["failure_precision"]),
            "specificity": _round(overall["specificity"]),
            "f1_failure": _round(overall["f1_failure"]),
            "mcc": _round(overall["mcc"]),
        },
        "bootstrap_ci_95": {k: ([_round(v[0]), _round(v[1]), v[2]] if v else None) for k, v in cis.items()},
        "slices": slices,
        "reproduction_targets": repro,
        "unsupported_claim_flag": flag,
    }
    return result


def main():
    result = run()
    out = HERE / "reliability_audit.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    o = result["overall"]
    print(f"n={o['n']}  agreement={o['agree_count']}/{o['n']} ({o['raw_agreement']})  "
          f"kappa={o['kappa']}  bal_acc={o['balanced_accuracy']}  recall={o['failure_recall']}  "
          f"prec={o['failure_precision']}  spec={o['specificity']}  mcc={o['mcc']}")
    for name, c in result["reproduction_targets"].items():
        print(f"  {'OK ' if c['match'] else 'XX '} {name}: claim {c['claim']} -> observed {c['observed']}")
    return result


if __name__ == "__main__":
    main()
