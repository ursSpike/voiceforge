#!/usr/bin/env python3
"""Deterministic conversation-trace signals — the FTO (floor transfer offset) core. SPEC §7.C.

fto_ms = next.start_ms - prev.end_ms   (negative = overlap, positive = gap)

Rules (all thresholds read from rubric.yaml, never hardcoded at call sites):
- Barge-in: overlap_ms > threshold (default 100; <=100 is backchannel, ignored).
  agent_interrupts_user and user_interrupts_agent are tracked SEPARATELY.
- Latency: gap_ms on user->agent transitions only. <=300 snappy, <=800 ok, >800 laggy.
- Report median + p90, never mean.
- Turns missing end_ms: latency-only treatment — overlap is NEVER inferred or faked.
- One clock per call: all ms relative to call start.

CLI:
  python pipeline/signals.py data/hero/turns.json [--rubric rubric.yaml] [--json out.json]
Accepts a full call_log JSON, {"turns":[...]}, or a bare turns array.
"""
import argparse
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SNAPPY_MS = 300  # display band only; "laggy" threshold comes from rubric


def load_rubric(path=None):
    import yaml
    p = Path(path) if path else ROOT / "rubric.yaml"
    with open(p) as f:
        return yaml.safe_load(f)


def turn_metrics(turns):
    """Pairwise floor-transfer events between consecutive turns (sorted by start_ms)."""
    turns = sorted(turns, key=lambda t: t["start_ms"])
    out = []
    for a, b in zip(turns, turns[1:]):
        if a.get("end_ms") is None:
            # single-timestamp source: cannot know when a ended -> no overlap, no gap. Skip pair.
            continue
        fto = b["start_ms"] - a["end_ms"]
        out.append({
            "prev_turn_id": a.get("turn_id"), "next_turn_id": b.get("turn_id"),
            "prev_spk": a["speaker"], "next_spk": b["speaker"],
            "at_ms": b["start_ms"], "fto_ms": fto,
            "overlap_ms": max(0, -fto), "gap_ms": max(0, fto),
        })
    return out


def p90(xs):
    if not xs:
        return None
    xs = sorted(xs)
    return xs[max(0, math.ceil(0.9 * len(xs)) - 1)]


def analyze(turns, rubric):
    dims = rubric["dimensions"]
    bi_threshold = dims["barge_in"]["threshold_overlap_ms"]
    laggy_ms = dims["latency_gap"]["laggy_ms"]

    events = turn_metrics(turns)

    barge_ins = []
    for e in events:
        if e["overlap_ms"] > bi_threshold:
            barge_ins.append({**e, "kind": f"{e['next_spk']}_interrupts_{e['prev_spk']}"})

    # latency: user finished, how long until agent spoke (clean transitions only)
    handoffs = [e for e in events
                if e["prev_spk"] == "user" and e["next_spk"] == "agent" and e["fto_ms"] >= 0]
    gaps = [e["gap_ms"] for e in handoffs]
    laggy_events = [e for e in handoffs if e["gap_ms"] > laggy_ms]

    failures = []
    for e in barge_ins:
        who = "agent barge-in" if e["kind"] == "agent_interrupts_user" else "user barge-in"
        failures.append({
            "at_ms": e["at_ms"], "dimension": "barge_in", "label": who,
            "detail": f"{e['overlap_ms']}ms overlap",
            "evidence_turn_ids": [e["prev_turn_id"], e["next_turn_id"]],
        })
    for e in laggy_events:
        failures.append({
            "at_ms": e["at_ms"], "dimension": "latency_gap", "label": "response latency",
            "detail": f"{e['gap_ms']:,}ms gap",
            "evidence_turn_ids": [e["prev_turn_id"], e["next_turn_id"]],
        })
    failures.sort(key=lambda f: f["at_ms"])

    return {
        "events": events,
        "barge_ins": barge_ins,
        "latency": {
            "n_handoffs": len(handoffs),
            "median_gap_ms": statistics.median(gaps) if gaps else None,
            "p90_gap_ms": p90(gaps),
            "laggy_threshold_ms": laggy_ms,
            "n_laggy": len(laggy_events),
        },
        "failures": failures,
    }


def mmss(ms):
    return f"{ms // 60000}:{(ms % 60000) // 1000:02d}"


def failure_table(result):
    lines = []
    for f in result["failures"]:
        ev = "→".join(str(t) for t in f["evidence_turn_ids"])
        lines.append(f"{mmss(f['at_ms']):>5}  —  {f['label']}  —  {f['detail']}   ({ev})")
    return "\n".join(lines) if lines else "(no timing failures detected)"


def _load_turns(path):
    data = json.loads(Path(path).read_text())
    if isinstance(data, list):
        return data, None
    return data.get("turns", []), data.get("call_id")


def main():
    ap = argparse.ArgumentParser(description="FTO signals over a call's turns")
    ap.add_argument("call_json", help="call_log JSON, {'turns':[...]}, or bare turns array")
    ap.add_argument("--rubric", default=None)
    ap.add_argument("--json", default=None, help="also write full signals JSON here")
    args = ap.parse_args()

    turns, call_id = _load_turns(args.call_json)
    if not turns:
        sys.exit(f"no turns found in {args.call_json}")
    result = analyze(turns, load_rubric(args.rubric))

    print(f"== {call_id or args.call_json} ==")
    lat = result["latency"]
    print(f"turns: {len(turns)} | handoffs: {lat['n_handoffs']} | "
          f"latency median {lat['median_gap_ms']}ms p90 {lat['p90_gap_ms']}ms | "
          f"barge-ins: {len(result['barge_ins'])} | laggy(> {lat['laggy_threshold_ms']}ms): {lat['n_laggy']}")
    print("\nFAILURE TABLE")
    print(failure_table(result))

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2))
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
