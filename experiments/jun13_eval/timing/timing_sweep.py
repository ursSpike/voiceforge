#!/usr/bin/env python3
"""Agent 3 - Timing Threshold Sensitivity (ISOLATED robustness audit).

We DO NOT edit rubric.yaml or any pipeline code. We import pipeline.signals.turn_metrics
(read-only FTO math) and apply our OWN threshold grid on top of the per-pair events.

Grid:  overlap thresholds {0,100,200,300,500} ms  x  lag thresholds {500,800,1000,1500,2000} ms.

A timing "event" at a given (overlap_thr, lag_thr) setting:
  - barge_in     : a consecutive-turn pair with overlap_ms > overlap_thr
  - latency_gap  : a clean user->agent handoff (fto_ms >= 0) with gap_ms > lag_thr
These are exactly the rules in pipeline/signals.analyze(), parameterised by the two thresholds.

CAVEAT (stated in output): this is ROBUSTNESS, NOT CORRECTNESS. The TIMED slice
(bolna/hero/spokenwoz, n=46) carries NO human failure labels. The blind human labels
target the binary success/fail question, and the human-fail calls in this corpus are the
text-only code_mixed_dialog calls -- which are `unmeasured` (all start_ms null) and therefore
yield ZERO timing events. So we CANNOT correlate timing events with binary failure here.
We measure only how sensitive the *event picture* is to the two VoiceForge threshold choices.
"""
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from pipeline.signals import timing_mode, turn_metrics  # read-only import

OUT_DIR = Path(__file__).resolve().parent
CALLS_PATH = ROOT / "out" / "calls.json"

OVERLAP_THRESHOLDS = [0, 100, 200, 300, 500]      # ms; > thr counts as barge-in
LAG_THRESHOLDS = [500, 800, 1000, 1500, 2000]     # ms; > thr counts as laggy
DEFAULT_SETTING = (100, 800)                      # VoiceForge rubric defaults


def load_timed_calls():
    """Return (timed_calls, n_unmeasured, n_mixed). Excludes unmeasured/mixed honestly."""
    data = json.loads(CALLS_PATH.read_text())
    timed, n_unmeasured, n_mixed = [], 0, 0
    for c in data:
        mode = timing_mode(c["turns"])
        if mode == "timed":
            timed.append(c)
        elif mode == "unmeasured":
            n_unmeasured += 1
        else:
            n_mixed += 1
    return timed, n_unmeasured, n_mixed, len(data)


def call_events(call, overlap_thr, lag_thr):
    """Replicate pipeline/signals.analyze() event selection under custom thresholds.

    Returns dict with per-call barge_in / latency_gap event counts and the set of
    pair-keys (prev_turn_id->next_turn_id) for each kind (for change-tracking)."""
    events = turn_metrics(call["turns"])  # [] for non-timed; these are all timed
    barge_pairs, lag_pairs = [], []
    for e in events:
        pair = f"{e['prev_turn_id']}->{e['next_turn_id']}"
        if e["overlap_ms"] > overlap_thr:
            barge_pairs.append(pair)
        # latency: clean user->agent handoff only (matches analyze's `handoffs`)
        if (e["prev_spk"] == "user" and e["next_spk"] == "agent"
                and e["fto_ms"] >= 0 and e["gap_ms"] > lag_thr):
            lag_pairs.append(pair)
    return {
        "n_barge_in": len(barge_pairs),
        "n_latency_gap": len(lag_pairs),
        "n_total": len(barge_pairs) + len(lag_pairs),
        "barge_pairs": barge_pairs,
        "lag_pairs": lag_pairs,
    }


def setting_summary(timed, overlap_thr, lag_thr):
    """Aggregate one grid cell across all timed calls."""
    per_call = {}
    total_barge = total_lag = 0
    affected_barge = affected_lag = affected_any = 0
    # event signature: set of "call_id|kind|pair" strings, for Jaccard between settings
    event_sig = set()
    for c in timed:
        cid = c["call_id"]
        ce = call_events(c, overlap_thr, lag_thr)
        per_call[cid] = ce
        total_barge += ce["n_barge_in"]
        total_lag += ce["n_latency_gap"]
        affected_barge += 1 if ce["n_barge_in"] else 0
        affected_lag += 1 if ce["n_latency_gap"] else 0
        affected_any += 1 if ce["n_total"] else 0
        for p in ce["barge_pairs"]:
            event_sig.add(f"{cid}|barge_in|{p}")
        for p in ce["lag_pairs"]:
            event_sig.add(f"{cid}|latency_gap|{p}")
    return {
        "overlap_thr_ms": overlap_thr,
        "lag_thr_ms": lag_thr,
        "is_default": (overlap_thr, lag_thr) == DEFAULT_SETTING,
        "n_barge_in_events": total_barge,
        "n_latency_gap_events": total_lag,
        "n_total_events": total_barge + total_lag,
        "n_calls_with_barge_in": affected_barge,
        "n_calls_with_latency_gap": affected_lag,
        "n_calls_affected_any": affected_any,
        "per_call": per_call,
        "_event_sig": event_sig,
    }


def rank_calls(setting, top_n=10):
    """Failure-cluster ranking: order calls by total timing-event load (desc).
    Returns ordered list of call_ids (ties broken by call_id for determinism)."""
    items = [(cid, ce["n_total"]) for cid, ce in setting["per_call"].items() if ce["n_total"] > 0]
    items.sort(key=lambda x: (-x[1], x[0]))
    return items


def jaccard(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def kendall_tau_like(rank_a, rank_b):
    """Fraction of concordant pairs over the union of ranked calls (simple rank-agreement).
    Calls absent from a ranking get a sentinel rank = len+1 (tie at bottom)."""
    ids = sorted(set(rank_a) | set(rank_b))
    pos_a = {cid: i for i, cid in enumerate(rank_a)}
    pos_b = {cid: i for i, cid in enumerate(rank_b)}
    big = len(ids) + 1

    def pos(d, cid):
        return d.get(cid, big)

    conc = disc = 0
    for x, y in combinations(ids, 2):
        ax, ay = pos(pos_a, x), pos(pos_a, y)
        bx, by = pos(pos_b, x), pos(pos_b, y)
        sa = (ax > ay) - (ax < ay)
        sb = (bx > by) - (bx < by)
        if sa == 0 and sb == 0:
            continue
        if sa == sb:
            conc += 1
        else:
            disc += 1
    tot = conc + disc
    return (conc - disc) / tot if tot else 1.0


def main():
    timed, n_unmeasured, n_mixed, n_total = load_timed_calls()

    # source / stress coverage of the timed slice
    coverage = {"source": {}, "stress_profile": {}, "workflow_type": {}, "language": {}}
    for c in timed:
        for field in coverage:
            v = c.get(field)
            coverage[field][v] = coverage[field].get(v, 0) + 1

    # sweep
    settings = []
    for ov in OVERLAP_THRESHOLDS:
        for lg in LAG_THRESHOLDS:
            settings.append(setting_summary(timed, ov, lg))

    # rankings per setting (full + top10)
    rankings = {}
    for s in settings:
        key = f"ov{s['overlap_thr_ms']}_lg{s['lag_thr_ms']}"
        rankings[key] = rank_calls(s)

    # default setting as the anchor for stability comparisons
    default_key = f"ov{DEFAULT_SETTING[0]}_lg{DEFAULT_SETTING[1]}"
    default_rank_ids = [cid for cid, _ in rankings[default_key]]
    default_sig = next(s["_event_sig"] for s in settings
                       if (s["overlap_thr_ms"], s["lag_thr_ms"]) == DEFAULT_SETTING)

    # pairwise Jaccard of event signatures between every setting and the default
    vs_default = []
    for s in settings:
        key = f"ov{s['overlap_thr_ms']}_lg{s['lag_thr_ms']}"
        j = jaccard(s["_event_sig"], default_sig)
        rank_ids = [cid for cid, _ in rankings[key]]
        tau = kendall_tau_like(default_rank_ids, rank_ids)
        # top-5 set overlap vs default
        d5, s5 = set(default_rank_ids[:5]), set(rank_ids[:5])
        top5_overlap = len(d5 & s5)
        vs_default.append({
            "setting": key,
            "overlap_thr_ms": s["overlap_thr_ms"],
            "lag_thr_ms": s["lag_thr_ms"],
            "jaccard_events_vs_default": round(j, 4),
            "rank_tau_vs_default": round(tau, 4),
            "top5_overlap_vs_default": top5_overlap,
            "n_total_events": s["n_total_events"],
        })

    # full pairwise Jaccard matrix (events) across all 25 settings
    keys = [f"ov{s['overlap_thr_ms']}_lg{s['lag_thr_ms']}" for s in settings]
    sigs = {f"ov{s['overlap_thr_ms']}_lg{s['lag_thr_ms']}": s["_event_sig"] for s in settings}
    jaccard_matrix = {}
    for ka in keys:
        jaccard_matrix[ka] = {kb: round(jaccard(sigs[ka], sigs[kb]), 4) for kb in keys}

    # per-call classification CHANGES across the grid:
    # for each call, record the distinct (n_barge_in, n_latency_gap) states it takes, and
    # whether its "affected/not-affected" flag flips anywhere in the grid.
    call_change = {}
    for c in timed:
        cid = c["call_id"]
        states = set()
        affected_flags = set()
        barge_counts = set()
        lag_counts = set()
        for s in settings:
            ce = s["per_call"][cid]
            states.add((ce["n_barge_in"], ce["n_latency_gap"]))
            affected_flags.add(ce["n_total"] > 0)
            barge_counts.add(ce["n_barge_in"])
            lag_counts.add(ce["n_latency_gap"])
        call_change[cid] = {
            "source": c.get("source"),
            "stress_profile": c.get("stress_profile"),
            "n_distinct_states": len(states),
            "barge_in_range": [min(barge_counts), max(barge_counts)],
            "latency_gap_range": [min(lag_counts), max(lag_counts)],
            "affected_flips": len(affected_flags) > 1,  # crosses the 0-event boundary somewhere
            "states": sorted(list(states)),
        }

    changing_call_ids = sorted(cid for cid, v in call_change.items() if v["n_distinct_states"] > 1)
    flipping_call_ids = sorted(cid for cid, v in call_change.items() if v["affected_flips"])

    # ---- per-axis isolation: hold one threshold at default, vary the other ----
    def axis_counts(vary_overlap):
        rows = []
        for s in settings:
            if vary_overlap and s["lag_thr_ms"] == DEFAULT_SETTING[1]:
                rows.append((s["overlap_thr_ms"], s["n_barge_in_events"], s["n_latency_gap_events"]))
            if (not vary_overlap) and s["overlap_thr_ms"] == DEFAULT_SETTING[0]:
                rows.append((s["lag_thr_ms"], s["n_barge_in_events"], s["n_latency_gap_events"]))
        return rows

    # most / least stable setting vs default (by jaccard, excluding default itself)
    non_default = [r for r in vs_default if r["setting"] != default_key]
    most_stable = max(non_default, key=lambda r: (r["jaccard_events_vs_default"], r["rank_tau_vs_default"]))
    least_stable = min(non_default, key=lambda r: (r["jaccard_events_vs_default"], r["rank_tau_vs_default"]))

    # event-count spread across the whole grid
    barge_counts_all = [s["n_barge_in_events"] for s in settings]
    lag_counts_all = [s["n_latency_gap_events"] for s in settings]

    result = {
        "experiment": "Agent 3 - Timing Threshold Sensitivity (robustness audit)",
        "caveat": (
            "ROBUSTNESS, NOT CORRECTNESS. The TIMED slice (n=46) has NO human failure labels; "
            "the human-fail calls are the text-only code_mixed_dialog calls, which are 'unmeasured' "
            "(no timing) and produce ZERO timing events. Timing events therefore CANNOT be correlated "
            "with binary failure in this slice. We measure only sensitivity of the event picture to "
            "the two VoiceForge threshold choices (barge-in overlap, laggy latency)."
        ),
        "slice": {
            "n_calls_total": n_total,
            "n_timed": len(timed),
            "n_unmeasured_excluded": n_unmeasured,
            "n_mixed_excluded": n_mixed,
        },
        "grid": {"overlap_thresholds_ms": OVERLAP_THRESHOLDS, "lag_thresholds_ms": LAG_THRESHOLDS,
                 "default_setting": {"overlap_thr_ms": DEFAULT_SETTING[0], "lag_thr_ms": DEFAULT_SETTING[1]}},
        "coverage_timed_slice": coverage,
        "per_setting": [
            {k: v for k, v in s.items() if not k.startswith("_") and k != "per_call"}
            for s in settings
        ],
        "stability_vs_default": vs_default,
        "most_stable_vs_default": most_stable,
        "least_stable_vs_default": least_stable,
        "event_count_spread": {
            "barge_in_min": min(barge_counts_all), "barge_in_max": max(barge_counts_all),
            "latency_gap_min": min(lag_counts_all), "latency_gap_max": max(lag_counts_all),
        },
        "axis_overlap_at_default_lag": [
            {"overlap_thr_ms": ov, "n_barge_in": b, "n_latency_gap": l}
            for ov, b, l in axis_counts(vary_overlap=True)
        ],
        "axis_lag_at_default_overlap": [
            {"lag_thr_ms": lg, "n_barge_in": b, "n_latency_gap": l}
            for lg, b, l in axis_counts(vary_overlap=False)
        ],
        "jaccard_matrix_events": jaccard_matrix,
        "ranking_default_top10": rankings[default_key][:10],
        "calls_changing_classification": {
            "n_changing_any": len(changing_call_ids),
            "ids_changing_any": changing_call_ids,
            "n_flipping_affected_boundary": len(flipping_call_ids),
            "ids_flipping_affected_boundary": flipping_call_ids,
            "detail": call_change,
        },
    }

    out_json = OUT_DIR / "timing_sweep.json"
    out_json.write_text(json.dumps(result, indent=2))
    print(f"wrote {out_json}")

    write_md(result, OUT_DIR / "timing_sweep.md")
    print(f"wrote {OUT_DIR / 'timing_sweep.md'}")

    # console digest
    print(f"\ntimed={len(timed)}  unmeasured(excluded)={n_unmeasured}  mixed(excluded)={n_mixed}")
    print(f"barge_in events range {result['event_count_spread']['barge_in_min']}.."
          f"{result['event_count_spread']['barge_in_max']}; "
          f"latency_gap range {result['event_count_spread']['latency_gap_min']}.."
          f"{result['event_count_spread']['latency_gap_max']}")
    print(f"most stable vs default: {most_stable['setting']} (J={most_stable['jaccard_events_vs_default']}, "
          f"tau={most_stable['rank_tau_vs_default']})")
    print(f"least stable vs default: {least_stable['setting']} (J={least_stable['jaccard_events_vs_default']}, "
          f"tau={least_stable['rank_tau_vs_default']})")
    print(f"calls changing classification across grid: {len(changing_call_ids)}")
    return result


def write_md(r, path):
    L = []
    L.append("# Timing Threshold Sensitivity - Robustness Audit (Agent 3)\n")
    L.append("> **" + r["caveat"] + "**\n")
    s = r["slice"]
    L.append(f"## Slice\n")
    L.append(f"- Total calls in `out/calls.json`: **{s['n_calls_total']}**")
    L.append(f"- **Timed** (analysed): **{s['n_timed']}**")
    L.append(f"- **Unmeasured** (excluded, no timing): **{s['n_unmeasured_excluded']}**")
    L.append(f"- **Mixed** (excluded, partial clock): **{s['n_mixed_excluded']}**\n")

    cov = r["coverage_timed_slice"]
    L.append("## Coverage of the timed slice")
    L.append(f"- source: {cov['source']}")
    L.append(f"- stress_profile: {cov['stress_profile']}")
    L.append(f"- workflow_type: {cov['workflow_type']}")
    L.append(f"- language: {cov['language']}\n")

    g = r["grid"]
    L.append("## Grid")
    L.append(f"- overlap thresholds (ms): {g['overlap_thresholds_ms']}")
    L.append(f"- lag thresholds (ms): {g['lag_thresholds_ms']}")
    L.append(f"- VoiceForge default: overlap>{g['default_setting']['overlap_thr_ms']}ms, "
             f"lag>{g['default_setting']['lag_thr_ms']}ms (25 cells total)\n")

    L.append("## Per-setting event & affected-call counts")
    L.append("| overlap>ms | lag>ms | barge_in ev | latency_gap ev | total ev | calls w/ barge | calls w/ lag | calls affected | default |")
    L.append("|---:|---:|---:|---:|---:|---:|---:|---:|:---:|")
    for ps in r["per_setting"]:
        L.append(f"| {ps['overlap_thr_ms']} | {ps['lag_thr_ms']} | {ps['n_barge_in_events']} | "
                 f"{ps['n_latency_gap_events']} | {ps['n_total_events']} | {ps['n_calls_with_barge_in']} | "
                 f"{ps['n_calls_with_latency_gap']} | {ps['n_calls_affected_any']} | "
                 f"{'YES' if ps['is_default'] else ''} |")
    L.append("")

    sp = r["event_count_spread"]
    L.append("## How much the picture moves")
    L.append(f"- barge_in event count across grid: **{sp['barge_in_min']} .. {sp['barge_in_max']}**")
    L.append(f"- latency_gap event count across grid: **{sp['latency_gap_min']} .. {sp['latency_gap_max']}**\n")

    L.append("### Isolating the overlap axis (lag held at default 800ms)")
    L.append("| overlap>ms | barge_in ev | latency_gap ev |")
    L.append("|---:|---:|---:|")
    for row in r["axis_overlap_at_default_lag"]:
        L.append(f"| {row['overlap_thr_ms']} | {row['n_barge_in']} | {row['n_latency_gap']} |")
    L.append("")
    L.append("### Isolating the lag axis (overlap held at default 100ms)")
    L.append("| lag>ms | barge_in ev | latency_gap ev |")
    L.append("|---:|---:|---:|")
    for row in r["axis_lag_at_default_overlap"]:
        L.append(f"| {row['lag_thr_ms']} | {row['n_barge_in']} | {row['n_latency_gap']} |")
    L.append("")

    L.append("## Failure-cluster RANK stability (vs default setting)")
    L.append("Calls ranked by total timing-event load. `tau` = rank-agreement vs default "
             "(1.0 = identical order); `J` = Jaccard of the exact per-call event set vs default; "
             "`top5∩` = how many of the default top-5 calls remain in this setting's top-5.")
    L.append("| setting | total ev | J events vs default | rank tau vs default | top5∩ |")
    L.append("|:--|---:|---:|---:|---:|")
    for row in r["stability_vs_default"]:
        L.append(f"| {row['setting']} | {row['n_total_events']} | {row['jaccard_events_vs_default']} | "
                 f"{row['rank_tau_vs_default']} | {row['top5_overlap_vs_default']} |")
    L.append("")
    ms, ls = r["most_stable_vs_default"], r["least_stable_vs_default"]
    L.append(f"- **Most stable vs default:** `{ms['setting']}` (J={ms['jaccard_events_vs_default']}, "
             f"tau={ms['rank_tau_vs_default']})")
    L.append(f"- **Least stable vs default:** `{ls['setting']}` (J={ls['jaccard_events_vs_default']}, "
             f"tau={ls['rank_tau_vs_default']})\n")

    L.append("## Default-setting top-10 failure cluster")
    L.append("| rank | call_id | total timing events |")
    L.append("|---:|:--|---:|")
    for i, (cid, n) in enumerate(r["ranking_default_top10"], 1):
        L.append(f"| {i} | {cid} | {n} |")
    L.append("")

    cc = r["calls_changing_classification"]
    L.append("## Calls whose classification CHANGES across the grid")
    L.append(f"- **{cc['n_changing_any']}** calls change their (barge_in, latency_gap) event counts "
             f"somewhere in the grid.")
    L.append(f"- **{cc['n_flipping_affected_boundary']}** calls cross the affected / not-affected "
             f"(0-event) boundary.\n")
    L.append("IDs changing any event count:")
    L.append("`" + ", ".join(cc["ids_changing_any"]) + "`\n")
    L.append("IDs crossing the 0-event boundary:")
    L.append("`" + (", ".join(cc["ids_flipping_affected_boundary"]) or "(none)") + "`\n")
    L.append("### Per-call detail (source / stress / ranges)")
    L.append("| call_id | source | stress | barge_in range | latency_gap range | crosses 0-boundary |")
    L.append("|:--|:--|:--|:--|:--|:--:|")
    for cid in sorted(cc["detail"]):
        v = cc["detail"][cid]
        L.append(f"| {cid} | {v['source']} | {v['stress_profile']} | {v['barge_in_range']} | "
                 f"{v['latency_gap_range']} | {'YES' if v['affected_flips'] else ''} |")
    L.append("")

    path.write_text("\n".join(L))


if __name__ == "__main__":
    main()
