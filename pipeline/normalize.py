#!/usr/bin/env python3
"""Normalize raw sources into the call_log schema (schemas/call_log.md). SPEC §7.D.

The adapter contract: anything that can become call_log JSON in data/normalized/ is
supported by every downstream tool (signals, judge, score, dpo, analytics). Speaker truth,
one ms-clock per call, turns sorted by start. Downstream code never knows the vendor.

SpokenWOZ notes (learned from inspection, 2026-06-10):
- speaker comes from turn `tag` (user|system) — ChannelId does NOT separate speakers
- turn bounds = first word BeginTime -> last word EndTime (word-level ASR timestamps)
- adjacent same-speaker turns get merged (floor transfer only exists between speakers)
- stress_profile assigned by DETERMINISTIC rule from timing features, never by judgment:
    interruption: >=2 plausible overlaps (100ms < overlap <= 4000ms)
    pause_heavy:  >=4 intra-turn word gaps > 1500ms
    clean:        none of the above anywhere in the call
  (ambiguous / kb_gap are semantic profiles — only assigned manually/by judge, never here)
- selection is reproducible: filtered, sorted by id, sliced. Same inputs -> same sample.

CLI:
  python pipeline/normalize.py spokenwoz [--k 10]   # scan-driven stratified sample
  python pipeline/normalize.py hero                  # validate hero turns.json into the pool
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SWZ = ROOT / "data" / "spokenwoz"
OUT = ROOT / "data" / "normalized"

PLAUSIBLE_OVERLAP_MAX_MS = 4000
LONG_PAUSE_MS = 1500


def validate_call(call):
    """Boundary validation — downstream stays assumption-free. Enforces the all-or-none timing
    invariant: every turn is timed (int start_ms) OR every turn is untimed (null) — never mixed,
    which would let signals manufacture false floor-transfer offsets across the gaps."""
    for k in ("call_id", "source", "language", "stress_profile", "workflow_type", "turns"):
        assert k in call, f"missing field: {k}"
    turns = call["turns"]
    assert turns, "no turns"
    flags = [t.get("start_ms") is not None for t in turns]
    if all(flags):
        mode = "timed"
    elif not any(flags):
        mode = "unmeasured"
    else:
        raise AssertionError(f"mixed timing: {sum(flags)}/{len(turns)} turns have start_ms — a call "
                             "must be all-timed or all-null (partial clocks are rejected, never bridged)")
    # timing <-> profile coupling: unmeasured timing iff stress_profile 'unmeasured'
    if mode == "unmeasured":
        assert call["stress_profile"] == "unmeasured", "all-null timing requires stress_profile 'unmeasured'"
    else:
        assert call["stress_profile"] != "unmeasured", "stress_profile 'unmeasured' requires all-null timing"
    last_start = -1
    for t in turns:
        assert t["speaker"] in ("user", "agent"), f"bad speaker: {t}"
        if mode == "timed":
            assert isinstance(t["start_ms"], int) and t["start_ms"] >= last_start, f"unsorted: {t['turn_id']}"
            assert t["end_ms"] is None or t["end_ms"] > t["start_ms"], f"end<=start: {t['turn_id']}"
            last_start = t["start_ms"]
        else:   # unmeasured: both ends null, never a fabricated number
            assert t["start_ms"] is None and t.get("end_ms") is None, \
                f"unmeasured call must have null start_ms AND end_ms: {t['turn_id']}"
    return call


def _merge_same_speaker(raw_turns):
    merged = []
    for t in raw_turns:
        if merged and merged[-1]["speaker"] == t["speaker"]:
            m = merged[-1]
            m["text"] = (m["text"] + " " + t["text"]).strip()
            m["end_ms"] = max(m["end_ms"], t["end_ms"])
        else:
            merged.append(t)
    for i, t in enumerate(merged):
        t["turn_id"] = f"t{i + 1}"
    return merged


def spokenwoz_call(did, dlg):
    raw = []
    skipped = 0
    for t in dlg["log"]:
        words = t.get("words") or []
        if not words:
            skipped += 1
            continue
        raw.append({
            "turn_id": "tmp",
            "speaker": "user" if t["tag"] == "user" else "agent",
            "text": t["text"].strip(),
            "start_ms": words[0]["BeginTime"],
            "end_ms": words[-1]["EndTime"],
        })
    raw.sort(key=lambda t: t["start_ms"])
    turns = _merge_same_speaker(raw)

    # timing features for the deterministic stress_profile rule
    overlaps, intra_long = [], 0
    for a, b in zip(turns, turns[1:]):
        ov = a["end_ms"] - b["start_ms"]
        if 100 < ov <= PLAUSIBLE_OVERLAP_MAX_MS:
            overlaps.append(ov)
    for t in dlg["log"]:
        w = t.get("words") or []
        intra_long += sum(1 for x, y in zip(w, w[1:]) if y["BeginTime"] - x["EndTime"] > LONG_PAUSE_MS)

    if len(overlaps) >= 2:
        profile = "interruption"
    elif intra_long >= 3:
        profile = "pause_heavy"
    else:
        profile = "clean"  # mild calls fold into clean; only strong signals earn a stress label

    goal = dlg.get("goal", {})
    domains = [k for k, v in goal.items() if isinstance(v, dict) and v]

    return validate_call({
        "call_id": f"swz_{did}",
        "source": "spokenwoz",
        "language": "en",
        "stress_profile": profile,
        "workflow_type": "+".join(domains) or "task_call",
        "turns": turns,
        "audio_path": None,
        "metadata": {
            "license": "CC BY-NC 4.0 (eval use)",
            "speaker_source": "tag field (channel ids do not separate speakers)",
            "skipped_unwordtimed_turns": skipped,
            "n_plausible_overlaps": len(overlaps),
            "n_long_intra_pauses": intra_long,
            "goal": {k: goal[k] for k in domains},
        },
    })


def cmd_spokenwoz(k):
    """Stratified, reproducible selection. Buckets come from the SAME spokenwoz_call()
    that writes the files — selection feature == labeling feature, one definition.
    'clean_laggy' = clean scenario where the agent still responded slowly: stress_profile
    stays clean (slowness is a FAILURE, not a scenario stress) but the pick is recorded."""
    data = json.load(open(SWZ / "data.json"))
    scan = {s["id"]: s for s in json.load(open(SWZ / "dev_scan.json"))}

    candidates = sorted(did for did, s in scan.items()
                        if did in data and 16 <= s["turns"] <= 60 and s["dur_s"] <= 300)
    calls = {did: spokenwoz_call(did, data[did]) for did in candidates}

    # scale the stratified quota to k (>=40 needed for blind-label calibration); proportions keep a
    # failure-rich-vs-clean mix so the binary label set is not single-class (the prevalence trap).
    _frac = {"interruption": 0.30, "pause_heavy": 0.27, "clean_laggy": 0.23, "clean_quiet": 0.20}
    quota = {b: max(1, round(k * f)) for b, f in _frac.items()}
    buckets = {b: [] for b in quota}

    def bucket_of(did):
        p = calls[did]["stress_profile"]
        if p in ("interruption", "pause_heavy"):
            return p
        if scan[did]["max_gap"] >= 1500:
            return "clean_laggy"
        if scan[did]["max_gap"] < 800 and scan[did]["n_long_pause"] == 0:
            return "clean_quiet"
        return None

    for did in candidates:                      # sorted -> deterministic first-fit
        b = bucket_of(did)
        if b and len(buckets[b]) < quota[b]:
            buckets[b].append(did)
        if sum(len(v) for v in buckets.values()) == k:
            break

    # if a bucket ran dry, top up to k from any matching bucket (deterministic, still mixed)
    total = sum(len(v) for v in buckets.values())
    if total < k:
        for did in candidates:
            if total >= k:
                break
            b = bucket_of(did)
            if b and did not in buckets[b]:
                buckets[b].append(did)
                total += 1

    OUT.mkdir(parents=True, exist_ok=True)
    print(f"selected {sum(len(v) for v in buckets.values())} calls (stratified, reproducible):")
    for name, chosen in buckets.items():
        print(f"  {name:<13} {chosen}")
    for name, chosen in buckets.items():
        for did in chosen:
            call = calls[did]
            call["metadata"]["selection_bucket"] = name
            path = OUT / f"{call['call_id']}.json"
            path.write_text(json.dumps(call, indent=2))
            print(f"  wrote {path.name}: {len(call['turns'])} turns · profile={call['stress_profile']}"
                  f" · {call['workflow_type']}")


def cmd_hero():
    call = validate_call(json.loads((ROOT / "data" / "hero" / "turns.json").read_text()))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{call['call_id']}.json").write_text(json.dumps(call, indent=2))
    print(f"wrote {call['call_id']}.json ({len(call['turns'])} turns) — hero joins the pool")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", choices=["spokenwoz", "hero"])
    ap.add_argument("--k", type=int, default=10)
    args = ap.parse_args()
    if args.source == "spokenwoz":
        cmd_spokenwoz(args.k)
    else:
        cmd_hero()


if __name__ == "__main__":
    main()
