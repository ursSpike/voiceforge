#!/usr/bin/env python3
"""Build the two-route product surface from the REAL committed artifacts.

Copies the repaired cinematic design bundle (voiceforge_design/{index.html,app.js,styles.css})
into out/surface/ and GENERATES out/surface/design_data.js from the real artifacts so the
presentation renders ALL 76 calls (full ROWS), the real calibration block (incl. balanced
accuracy 0.628 in the truth-corrected caption), real disagreements, the 25/45 metric trap,
real archetypes and the real improvement queue.

Unlike voiceforge_design/design_data.js (a sanitized ~5-row FIXTURE), this is the real surface:
every labeled/judged call's transcript is included. The output is self-contained — design_data.js
is plain `window.__DATA__ = {...}` with zero network references — so it loads with Wi-Fi off.

Reads (all read-only; none are written):
  out/calls.json                  76 normalized + deterministically-scored calls
  out/judge_results.json          46 semantic-judge results (5 dims + binary), keyed by call_id
  out/analytics.json              corpus analytics (n_calls, timing_coverage, failure_clusters, ...)
  out/demo_report_data.json       the real report block (calibration, metric_trap, product, ...)
  out/bolna_cartesia_proof.json   sponsor proof (agent_id, cartesia voice/model, fetched_at)
  eval/labels_spike.csv           the blind human labels (primary_label, confidence, *_tags)

Writes:
  out/surface/index.html          (copied, byte-identical)
  out/surface/app.js              (copied, byte-identical)
  out/surface/styles.css          (copied, byte-identical)
  out/surface/design_data.js      (GENERATED real-data contract)

Run:  python3 pipeline/build_surface.py
"""
import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "voiceforge_design"
OUT = ROOT / "out"
SURFACE = OUT / "surface"

# ---------- load real artifacts ----------


def _load_json(path):
    return json.loads(Path(path).read_text())


def read_labels():
    """call_id -> blind human label dict from the frozen CSV (csv module handles quoted notes)."""
    out = {}
    csv_path = ROOT / "eval" / "labels_spike.csv"
    with csv_path.open(newline="") as f:
        for row in csv.DictReader(f):
            out[row["call_id"]] = row
    return out


def _split_tags(s):
    return [t for t in (s or "").split("|") if t]


def human_from_label(row):
    """Map a labels_spike.csv row -> the row.human shape app.js reads
    (label, confidence, positive[], negative[], context[])."""
    if not row:
        return None
    return {
        "label": row.get("primary_label", ""),
        "confidence": row.get("confidence", ""),
        "positive": _split_tags(row.get("positive_tags")),
        "negative": _split_tags(row.get("negative_tags")),
        "context": _split_tags(row.get("context_tags")),
    }


def row_from_call(call, judge_calls, labels):
    """Map one out/calls.json call -> the ROWS[] shape app.js reads.

    app.js reads, per row: id, source, lang, profile, wf, turns (count), outcome (bool),
    overall (number), dims (deterministic scorecard dims), failures, transcript[{id,s,x}],
    judge ({dims, binary} or absent), human ({label,confidence,positive,negative,context} or absent).
    """
    cid = call["call_id"]
    transcript = [
        {"id": t["turn_id"], "s": t["speaker"], "x": t.get("text", "")}
        for t in call.get("turns", [])
    ]
    scorecard = call.get("scorecard") or {}
    outcome = call.get("outcome") or {}
    return {
        "id": cid,
        "source": call.get("source"),
        "lang": call.get("language"),
        "profile": call.get("stress_profile"),
        "wf": call.get("workflow_type"),
        "turns": len(call.get("turns", [])),
        "outcome": bool(outcome.get("task_completed")),
        "overall": scorecard.get("overall"),
        "dims": scorecard.get("dimensions", []),
        "failures": call.get("failures", []),
        "transcript": transcript,
        # judge_results.calls[cid] is already {dims:[...], binary:{...}} — exactly the row.judge shape
        "judge": judge_calls.get(cid),
        "in_manifest": cid in judge_calls,
        "human": human_from_label(labels.get(cid)),
    }


def build_data():
    calls = _load_json(OUT / "calls.json")
    judge = _load_json(OUT / "judge_results.json")
    analytics = _load_json(OUT / "analytics.json")
    report = _load_json(OUT / "demo_report_data.json")
    proof = _load_json(OUT / "bolna_cartesia_proof.json")
    labels = read_labels()

    judge_run = report["judge_run"]
    judge_calls = judge["calls"]

    rows = [row_from_call(c, judge_calls, labels) for c in calls]

    labels_block = report["labels"]
    val = {"binary": labels_block["binary"], "unsure": labels_block["unsure"]}

    sponsor_proof = {
        "agent_id": proof["agent_id"],
        "fetched_at": proof["fetched_at"],
        "synthesizer_provider": proof.get("synthesizer_provider", "cartesia"),
        "cartesia_voice": proof["cartesia_voice"],
        "cartesia_model": proof["cartesia_model"],
    }

    # app.js reads report.* (calibration, metric_trap, product, archetypes, improvement_queue,
    # manifest_total, corpus) — demo_report_data.json IS that block, real and complete.
    data = {
        "gate_open": True,
        "floor": labels_block["floor"],
        "val": val,
        "analytics": analytics,
        "report": report,
        "judge_run": judge_run,
        "sponsor_proof": sponsor_proof,
        "rows": rows,
        "fixture": False,
        "design_handoff": False,
        "real_surface": True,
        "privacy_note": (
            "Every aggregate and every transcript on this surface is real: all "
            f"{analytics['n_calls']} scored calls are present, with the blind-labeled and "
            "judged slice carrying its full transcript, human label, deterministic scorecard, "
            "and evidence-cited judge output."
        ),
    }
    return data


def write_design_data(data, path):
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    js = (
        "/* GENERATED by pipeline/build_surface.py from the real committed artifacts.\n"
        "   Do not hand-edit. Self-contained: zero network references. */\n"
        "window.__DATA__ = " + payload + ";\n"
    )
    Path(path).write_text(js, encoding="utf-8")


def main():
    SURFACE.mkdir(parents=True, exist_ok=True)

    # 1) copy the design bundle byte-for-byte (presentation shell + interaction + styles)
    for name in ("index.html", "app.js", "styles.css"):
        src = DESIGN / name
        if not src.exists():
            sys.exit(f"missing design bundle file: {src}")
        shutil.copyfile(src, SURFACE / name)

    # 2) generate the real-data contract
    data = build_data()
    write_design_data(data, SURFACE / "design_data.js")

    n_calls = len(data["rows"])
    n_judged = sum(1 for r in data["rows"] if r.get("judge"))
    n_labeled = sum(1 for r in data["rows"] if r.get("human"))
    cap = data["report"]["calibration"]["caption"]
    assert "least reliable" not in cap.lower(), "calibration caption contains banned 'least reliable' language"
    assert data["report"]["calibration"].get("balanced_accuracy") == 0.628, "balanced accuracy missing/changed"

    print("built out/surface/")
    print(f"  index.html, app.js, styles.css copied from {DESIGN}")
    print(f"  design_data.js generated: {n_calls} calls (ROWS), "
          f"{n_judged} judged, {n_labeled} blind-labeled")
    print(f"  calibration.balanced_accuracy = {data['report']['calibration']['balanced_accuracy']}")
    print(f"  metric_trap = {data['report']['metric_trap']['agree']}/{data['report']['metric_trap']['n']}")
    print("  caption clean of 'least reliable': OK")


if __name__ == "__main__":
    main()
