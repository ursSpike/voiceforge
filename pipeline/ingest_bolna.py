#!/usr/bin/env python3
"""Bolna execution -> VoiceForge call_log (SPEC §7.G). Batch 1.

Builds from the CACHED raw payload (data/provider_logs/bolna_<id>.json), not live API, so the
demo never needs a network call. Reconstructs turns + timing from the /log component events'
created_at diffs — NEVER from the top-level transcript (role-less, and Bolna's 'precise' mode
scrubs interrupted content). Single timestamps -> latency only, NEVER faked overlap (signals.py rule).

    .venv/bin/python pipeline/ingest_bolna.py [--fetch <exec_id>]

Mapping (verified against the real log):
  transcriber.response -> a USER turn finished (data = transcribed user speech, time = end)
  synthesizer.request  -> an AGENT turn began speaking (data = spoken text, time = start)
  synthesizer.response -> agent audio ready (time = agent turn end)
  latency gap (user->agent) = agent.start_ms - user.end_ms  ==  the real response delay
"""
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
RAW = ROOT / "data" / "provider_logs"
NORM = ROOT / "data" / "normalized"
OUT = ROOT / "out"
EXEC_ID = "246cd9f3-8479-407d-b65b-bac1b6d4e4a7"


def _parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def reconstruct_turns(log):
    """Ordered turns with ms timing from the component-event stream."""
    events = log["data"] if isinstance(log, dict) else log   # /log returns {"data":[...], "status":...}
    events = sorted(events, key=lambda e: _parse(e["created_at"]))
    t0 = _parse(events[0]["created_at"])
    ms = lambda e: int((_parse(e["created_at"]) - t0).total_seconds() * 1000)

    raw = []
    pending_agent = None  # synth request awaiting its response (to set end_ms)
    for e in events:
        comp, typ, data = e.get("component"), e.get("type"), (e.get("data") or "").strip()
        if comp == "transcriber" and typ == "response" and data:
            raw.append({"speaker": "user", "text": data, "start_ms": ms(e), "end_ms": ms(e)})
        elif comp == "synthesizer" and typ == "request" and data:
            pending_agent = {"speaker": "agent", "text": data, "start_ms": ms(e), "end_ms": None}
            raw.append(pending_agent)
        elif comp == "synthesizer" and typ == "response" and pending_agent is not None:
            pending_agent["end_ms"] = ms(e)          # agent audio ready = turn end
            pending_agent = None

    # merge consecutive same-speaker fragments (one utterance can span several synth requests)
    merged = []
    for t in raw:
        if merged and merged[-1]["speaker"] == t["speaker"]:
            m = merged[-1]
            m["text"] = (m["text"] + " " + t["text"]).strip()
            m["end_ms"] = t["end_ms"] if t["end_ms"] is not None else m["end_ms"]
        else:
            merged.append(dict(t))

    # give user turns a sensible start (they began after the previous turn ended) so the
    # user->agent latency gap is honest; clamp so start <= end.
    prev_end = 0
    for t in merged:
        if t["speaker"] == "user":
            t["start_ms"] = min(prev_end, t["end_ms"])
        prev_end = t["end_ms"] if t["end_ms"] is not None else t["start_ms"]
    for i, t in enumerate(merged, 1):
        t["turn_id"] = f"t{i}"
    return merged


def normalize(raw_payload):
    ex, log = raw_payload["execution"], raw_payload["log"]
    turns = reconstruct_turns(log)
    # code-switching detected in the real transcript (Devanagari present) -> hi-en
    text_blob = " ".join(t["text"] for t in turns)
    lang = "hi-en" if any("ऀ" <= c <= "ॿ" for c in text_blob) else "en"
    return {
        "call_id": f"bolna_{ex['id'][:8]}",
        "source": "bolna",
        "language": lang,
        "stress_profile": "clean",   # cooperative web-call test; refine from signals if interruption appears
        "workflow_type": "appointment_booking",
        "turns": [{"turn_id": t["turn_id"], "speaker": t["speaker"], "text": t["text"],
                   "start_ms": t["start_ms"], "end_ms": t["end_ms"]} for t in turns],
        "audio_path": None,   # web-call: no telephony recording url (telephony_data None)
        "metadata": {
            "provider": ex.get("provider"), "execution_id": ex["id"], "agent_id": ex["agent_id"],
            "total_cost_cents": float(ex.get("total_cost") or 0),
            "timing_source": "log component created_at diffs (SPEC §7.G); overlap NOT computed (web-call)",
            "note": "real Bolna execution; this call predates the Cartesia voice swap (synth=elevenlabs)",
        },
    }


def main():
    if "--fetch" in sys.argv:
        sys.exit("fetch path lives in the inspection script; this builds from the cached "
                 "data/provider_logs/bolna_246cd9f3.json (build-from-files / demo-safe).")
    rawf = RAW / "bolna_246cd9f3.json"
    if not rawf.exists():
        sys.exit(f"missing {rawf} — run the ingest inspection first to cache the raw payload.")
    payload = json.loads(rawf.read_text())

    call = normalize(payload)

    # validate against the constitution BEFORE writing
    from schemas import validate
    validate(call, "call_log")

    NORM.mkdir(parents=True, exist_ok=True)
    (NORM / f"{call['call_id']}.json").write_text(json.dumps(call, indent=2))

    # deterministic signals on the real call
    from signals import analyze, load_rubric, failure_table, mmss
    res = analyze(call["turns"], load_rubric())
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"call_id": call["call_id"], "source": "bolna", "language": call["language"],
              "n_turns": len(call["turns"]), "provider_cost_cents": call["metadata"]["total_cost_cents"],
              "latency": res["latency"], "barge_ins": res["barge_ins"], "failures": res["failures"]}
    (OUT / "provider_ingest_report.json").write_text(json.dumps(report, indent=2))

    print(f"ingested {call['call_id']}  ({len(call['turns'])} turns, {call['language']}, "
          f"cost {call['metadata']['total_cost_cents']}c) -> data/normalized/ + out/provider_ingest_report.json")
    lat = res["latency"]
    print(f"latency: median {lat['median_gap_ms']}ms p90 {lat['p90_gap_ms']}ms | laggy(>800): {lat['n_laggy']}")
    print("\nFAILURE TABLE (real Bolna call):")
    print(failure_table(res))


if __name__ == "__main__":
    main()
