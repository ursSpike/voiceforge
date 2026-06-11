#!/usr/bin/env python3
"""Deterministic eval core (Batch 3). Merge signals + task_outcome + cost into validated
call_records → out/calls.json, plus out/analytics.json (summary + failure clusters).

DETERMINISTIC ONLY — judge dimensions (language_match, faithfulness, repair_quality, conciseness,
user_frustration) are added in Batch 4. The scorecard here carries the 3 measured dims
(barge_in, latency_gap, task_completion); `overall` is a weighted mean over PRESENT dims
(re-normalized), so it stays a clean 0..1 now and recomputes correctly when judge dims land.

    .venv/bin/python pipeline/score.py     # build out/calls.json + out/analytics.json (validated)

Every score carries a reason + evidence turn ids. task_outcome is a transparent HEURISTIC from the
SpokenWOZ goal (or a workflow keyword set for hero/bolna): a field is "captured" if its goal value
(or the slot keyword) appears in the dialogue text — NOT gold dialogue-state. Documented, not hidden.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
NORM = ROOT / "data" / "normalized"
OUT = ROOT / "out"
PER_TURN_USD = 0.005   # public anchor: Bolna's observed ~5.96c / 13 turns ≈ $0.005/turn (LLM+TTS+STT)


# ---------------------------------------------------------------- task_outcome (heuristic, deterministic)
WORKFLOW_FIELDS = {   # for calls with no SpokenWOZ goal (hero/bolna): slot -> keyword alternatives
    "appliance_service_booking": {"service_area": ["madhapur", "metro", "area"],
                                  "appliance": ["ac", "unit", "cooling", "airflow"],
                                  "time_slot": ["morning", "evening", "ten", "am", "pm"]},
    "appointment_booking": {"location": ["street", "bangalore", "बैंगलोर", "road", "near", "metro"],
                           "date_time": ["june", "pm", "am", "five", "ten", "thirteenth",
                                         "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]},
}


def _required_from_goal(goal):
    fields = []
    for dom, g in goal.items():
        if not isinstance(g, dict):
            continue
        for slot, val in (g.get("info") or {}).items():
            fields.append((f"{dom}.{slot}", str(val), "value"))
        for slot, val in (g.get("book") or {}).items():
            fields.append((f"{dom}.book_{slot}", str(val), "value"))
        for slot in (g.get("reqt") or []):
            fields.append((f"{dom}.{slot}", None, "reqt"))
    return fields


def build_outcome(call):
    text = " ".join(t["text"].lower() for t in call["turns"])
    agent_text = " ".join(t["text"].lower() for t in call["turns"] if t["speaker"] == "agent")
    goal = call["metadata"].get("goal")
    rf = []
    if goal:
        for name, val, kind in _required_from_goal(goal):
            if kind == "value":
                cap = val.lower() in text
                rf.append({"name": name, "captured": cap, "value": val if cap else None})
            else:   # reqt: the agent should have PROVIDED this info -> slot keyword in an agent turn
                kw = name.split(".")[-1].lower()
                rf.append({"name": name, "captured": kw in agent_text, "value": None})
    else:   # hero/bolna: workflow keyword sets
        for slot, kws in WORKFLOW_FIELDS.get(call["workflow_type"], {}).items():
            cap = any(kw in text for kw in kws)
            rf.append({"name": slot, "captured": cap, "value": None})
    n = len(rf) or 1
    ncap = sum(r["captured"] for r in rf)
    frac = ncap / n
    return {"call_id": call["call_id"], "task_completed": frac >= 0.7,
            "required_fields": rf, "escalation_needed": False, "confidence": round(frac, 2)}, frac, ncap, n


# ---------------------------------------------------------------- deterministic scorecard
def deterministic_scorecard(call, sig, frac_captured, ncap, n_fields):
    dims = []
    # barge_in: only AGENT-interrupts-user counts against the agent
    agent_bi = [b for b in sig["barge_ins"] if b.get("kind") == "agent_interrupts_user"]
    bi_score = max(0.0, 1.0 - 0.34 * len(agent_bi))
    bi_reason = ("no agent barge-ins" if not agent_bi else
                 f"agent interrupted the caller {len(agent_bi)}x (overlap "
                 f"{', '.join(str(b['overlap_ms'])+'ms' for b in agent_bi[:3])})")
    bi_ev = [tid for b in agent_bi for tid in (b["prev_turn_id"], b["next_turn_id"]) if tid]
    dims.append({"name": "barge_in", "type": "deterministic", "score": round(bi_score, 3),
                 "reason": bi_reason, "evidence_turn_ids": bi_ev[:6]})

    # latency_gap: fraction of snappy user->agent responses
    lat = sig["latency"]
    nh, nl = lat["n_handoffs"], lat["n_laggy"]
    lat_score = 1.0 if nh == 0 else round(1.0 - nl / nh, 3)
    lat_reason = (f"median {lat['median_gap_ms']}ms / p90 {lat['p90_gap_ms']}ms; "
                  f"{nl}/{nh} responses laggy (>{lat['laggy_threshold_ms']}ms)" if nh else "no user→agent handoffs")
    lat_ev = [f["evidence_turn_ids"][1] for f in sig["failures"] if f["dimension"] == "latency_gap"]
    dims.append({"name": "latency_gap", "type": "deterministic", "score": lat_score,
                 "reason": lat_reason, "evidence_turn_ids": [e for e in lat_ev if e][:6]})

    # task_completion: fraction of required fields captured
    dims.append({"name": "task_completion", "type": "deterministic", "score": round(frac_captured, 3),
                 "reason": f"captured {ncap}/{n_fields} required fields (heuristic from goal/workflow)",
                 "evidence_turn_ids": []})

    # overall = weighted mean over PRESENT dims, re-normalized (rubric weights)
    from signals import load_rubric
    weights = {k: v["weight"] for k, v in load_rubric()["dimensions"].items()}
    wsum = sum(weights[d["name"]] for d in dims)
    overall = round(sum(weights[d["name"]] * d["score"] for d in dims) / wsum, 3) if wsum else 0.0
    return {"call_id": call["call_id"], "dimensions": dims, "overall": overall}


# ---------------------------------------------------------------- cost
def build_cost(call, sig):
    dur = (call["turns"][-1]["end_ms"] or call["turns"][-1]["start_ms"]) / 1000
    n_turns = len(call["turns"])
    n_agent = sum(1 for t in call["turns"] if t["speaker"] == "agent")
    real = call["metadata"].get("total_cost_cents")
    est = (real / 100.0) if real is not None else round(n_agent * PER_TURN_USD, 4)
    return {"call_id": call["call_id"], "duration_s": round(dur, 1), "turn_count": n_turns,
            "est_llm_calls": n_agent, "est_cost_total": est,
            "est_cost_per_success_note": "estimated, prototype" + (" (real provider cost)" if real is not None else "")}


# ---------------------------------------------------------------- failures (signals + call_id)
def build_failures(call, sig):
    return [{**f, "call_id": call["call_id"], "origin": "deterministic"} for f in sig["failures"]]


# ---------------------------------------------------------------- assemble + validate one call_record
def build_record(call):
    from signals import analyze, load_rubric
    sig = analyze(call["turns"], load_rubric())
    outcome, frac, ncap, n = build_outcome(call)
    rec = {k: call[k] for k in ("call_id", "source", "language", "stress_profile", "workflow_type",
                                "turns", "audio_path", "metadata") if k in call}
    rec["outcome"] = outcome
    rec["scorecard"] = deterministic_scorecard(call, sig, frac, ncap, n)
    rec["cost"] = build_cost(call, sig)
    rec["failures"] = build_failures(call, sig)
    rec["signals"] = {"latency": sig["latency"], "n_barge_ins": len(sig["barge_ins"])}
    return rec


# ---------------------------------------------------------------- analytics + failure clusters
def build_analytics(records):
    n = len(records)
    completed = [r for r in records if r["outcome"]["task_completed"]]
    total_cost = sum(r["cost"]["est_cost_total"] for r in records)
    clusters = {}
    for r in records:
        for f in r["failures"]:
            c = clusters.setdefault(f["dimension"], {"dimension": f["dimension"], "count": 0, "example_call_ids": []})
            c["count"] += 1
            if r["call_id"] not in c["example_call_ids"] and len(c["example_call_ids"]) < 5:
                c["example_call_ids"].append(r["call_id"])
    by_prof = {}
    for r in records:
        p = r["stress_profile"]
        b = by_prof.setdefault(p, {"stress_profile": p, "n": 0, "n_completed": 0, "cost": 0.0})
        b["n"] += 1
        b["n_completed"] += r["outcome"]["task_completed"]
        b["cost"] += r["cost"]["est_cost_total"]
    for b in by_prof.values():
        b["success_rate"] = round(b["n_completed"] / b["n"], 3)
        b["cost_per_successful_call"] = round(b["cost"] / b["n_completed"], 4) if b["n_completed"] else None
    return {
        "n_calls": n,
        "success_rate": round(len(completed) / n, 3) if n else 0.0,
        "avg_overall": round(sum(r["scorecard"]["overall"] for r in records) / n, 3) if n else None,
        "cost_per_successful_call": round(total_cost / len(completed), 4) if completed else None,
        "by_stress_profile": sorted(by_prof.values(), key=lambda b: -b["n"]),
        "failure_clusters": sorted(clusters.values(), key=lambda c: -c["count"]),
        "note": "deterministic eval only (judge dims add in Batch 4); costs estimated, prototype",
    }


def main():
    from schemas import validate
    OUT.mkdir(parents=True, exist_ok=True)
    records, bad = [], 0
    for p in sorted(NORM.glob("*.json")):
        call = json.loads(p.read_text())
        rec = build_record(call)
        try:
            validate(rec, "call_record")
        except Exception as e:
            bad += 1
            print(f"  INVALID call_record {call['call_id']}: {e}")
            continue
        records.append(rec)
        (OUT / f"call_{call['call_id']}.json").write_text(json.dumps(rec, indent=2))
    (OUT / "calls.json").write_text(json.dumps(records, indent=2))
    analytics = build_analytics(records)
    validate(analytics, "analytics")
    (OUT / "analytics.json").write_text(json.dumps(analytics, indent=2))

    print(f"scored {len(records)} call_records -> out/calls.json (+ per-call), {bad} invalid")
    print(f"success_rate {analytics['success_rate']} | avg_overall {analytics['avg_overall']} | "
          f"cost/successful ${analytics['cost_per_successful_call']}")
    print("failure clusters:", [(c["dimension"], c["count"]) for c in analytics["failure_clusters"]])
    print("by stress profile:", [(b["stress_profile"], b["n"], b["success_rate"]) for b in analytics["by_stress_profile"]])
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
