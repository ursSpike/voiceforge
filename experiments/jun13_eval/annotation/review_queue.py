#!/usr/bin/env python3
"""
Agent 4 / Task A — deterministic SECOND-RATER REVIEW QUEUE builder.

Reads (READ-ONLY, never written):
  - eval/labels_spike.csv      human labels: primary_label, confidence, tags, note
  - out/judge_results.json     LLM-judge per-call binary outcome (calls[id].binary.label)
  - out/calls.json             heuristic pipeline outcome (outcome.task_completed)

Ranks the 46 labeled calls for a second-rater pass by reason signals, emits a
deterministic queue (stable tie-break by call_id) with per-call REASON CODES,
and writes review_queue.json + review_queue.md.

HONESTY NOTE: this is annotation OPERATIONS. We are NOT claiming the model
"knows" when it is uncertain. The priority score is a heuristic over signals
that *correlate* with annotation difficulty (human-reported confidence,
judge/heuristic disagreement, conflicting/heavy tag load). True human
confidence on a re-read is known ONLY AFTER a second rater annotates.

Disagreement is SIGNAL, not error (SemEval-2023 Learning With Disagreements,
arXiv:2304.14803). The queue surfaces disagreement for review; it never
silently reconciles or overwrites a rater's label.

Run:  .venv/bin/python experiments/jun13_eval/annotation/review_queue.py
Deterministic: no RNG, no clock, stable sort. Re-running yields identical output
(except the generator's own provenance hashes are derived from inputs).
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths (repo-root relative; resolved from this file's location)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[3]
LABELS_CSV = REPO_ROOT / "eval" / "labels_spike.csv"
JUDGE_JSON = REPO_ROOT / "out" / "judge_results.json"
CALLS_JSON = REPO_ROOT / "out" / "calls.json"
OUT_DIR = Path(__file__).resolve().parent
OUT_JSON = OUT_DIR / "review_queue.json"
OUT_MD = OUT_DIR / "review_queue.md"

# ---------------------------------------------------------------------------
# Phenotype tag vocabulary (derived from labels_spike.csv; pinned here so the
# "negative phenotype" definition is explicit and auditable).
# ---------------------------------------------------------------------------
NEGATIVE_TAGS = {
    "hard_to_understand",
    "missing_or_wrong_information",
    "misunderstood_user",
    "poor_clarification_or_recovery",
    "repeated_or_stuck",
    "user_frustrated",
    "workflow_or_tool_failed",
    "wrong_language_or_tone",
}
POSITIVE_TAGS = {
    "adapted_language_well",
    "completed_or_clear_next_step",
    "easy_to_understand",
    "handled_confusion_well",
    "understood_user",
    "user_satisfied",
}

# Reason codes and their priority weights. Higher weight = stronger pull toward
# the top of the second-rater queue. Weights are ordinal design choices, not
# calibrated probabilities. Tie-break is ALWAYS by call_id (stable, lexical).
REASON_WEIGHTS = {
    "R1_LOW_CONFIDENCE": 5,        # human confidence == low
    "R1_MEDIUM_CONFIDENCE": 3,     # human confidence == medium
    "R2_JUDGE_DISAGREE": 4,        # LLM-judge binary != human binary
    "R3_HEURISTIC_DISAGREE": 2,    # heuristic task_completed != human binary
    "R4_HEAVY_NEGATIVE_TAGS": 2,   # >= 2 negative phenotype tags
    "R5_CONFLICTING_TAGS": 3,      # has >=1 positive AND >=1 negative tag
    "R6_UNSURE_LABEL": 4,          # human primary_label not decisive (unsure)
}

REASON_DESCRIPTIONS = {
    "R1_LOW_CONFIDENCE": "Human annotator marked confidence = low.",
    "R1_MEDIUM_CONFIDENCE": "Human annotator marked confidence = medium.",
    "R2_JUDGE_DISAGREE": "LLM-judge binary outcome disagrees with human binary outcome.",
    "R3_HEURISTIC_DISAGREE": "Heuristic task_completed disagrees with human binary outcome.",
    "R4_HEAVY_NEGATIVE_TAGS": "Two or more negative phenotype tags present.",
    "R5_CONFLICTING_TAGS": "Both positive AND negative tags present (internally tense judgment).",
    "R6_UNSURE_LABEL": "Human primary_label is non-decisive (e.g. 'unsure'); inherently needs a second read.",
}


def _split_tags(cell: str) -> list[str]:
    return [t for t in (cell or "").split("|") if t]


def _human_binary(primary_label: str) -> str | None:
    """Map human primary_label to a decisive binary, or None if non-decisive.

    'success' -> success ; 'fail' -> fail ; anything else (e.g. 'unsure') -> None.
    A None human binary means disagreement against it is undefined — we do NOT
    fabricate a disagreement; instead R6_UNSURE_LABEL carries the review signal.
    """
    if primary_label == "success":
        return "success"
    if primary_label == "fail":
        return "fail"
    return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_inputs():
    # Human labels (preserve row order for provenance only; queue order is computed).
    rows = list(csv.DictReader(LABELS_CSV.open()))

    judge_doc = json.load(JUDGE_JSON.open())
    judge_calls = judge_doc.get("calls", {})

    calls_list = json.load(CALLS_JSON.open())
    heuristic = {}
    for c in calls_list:
        tc = (c.get("outcome") or {}).get("task_completed")
        # heuristic binary: task_completed True -> success, False -> fail, None -> unknown
        if tc is True:
            heuristic[c["call_id"]] = "success"
        elif tc is False:
            heuristic[c["call_id"]] = "fail"
        else:
            heuristic[c["call_id"]] = None
    return rows, judge_calls, heuristic, judge_doc


def build_entry(row, judge_calls, heuristic):
    call_id = row["call_id"]
    primary_label = row["primary_label"]
    confidence = row["confidence"]
    pos = _split_tags(row.get("positive_tags", ""))
    neg = _split_tags(row.get("negative_tags", ""))
    ctx = _split_tags(row.get("context_tags", ""))
    note = (row.get("note") or "").strip()

    human_bin = _human_binary(primary_label)

    judge_bin = None
    jc = judge_calls.get(call_id)
    if jc and isinstance(jc.get("binary"), dict):
        judge_bin = jc["binary"].get("label")

    heur_bin = heuristic.get(call_id)

    reasons: list[str] = []

    # (1) human confidence medium/low
    if confidence == "low":
        reasons.append("R1_LOW_CONFIDENCE")
    elif confidence == "medium":
        reasons.append("R1_MEDIUM_CONFIDENCE")

    # (6) non-decisive human label
    if human_bin is None:
        reasons.append("R6_UNSURE_LABEL")

    # (2) judge <-> human disagreement (only when both decisive)
    judge_disagree = (
        human_bin is not None and judge_bin in ("success", "fail") and judge_bin != human_bin
    )
    if judge_disagree:
        reasons.append("R2_JUDGE_DISAGREE")

    # (3) heuristic <-> human disagreement (only when both decisive)
    heur_disagree = (
        human_bin is not None and heur_bin in ("success", "fail") and heur_bin != human_bin
    )
    if heur_disagree:
        reasons.append("R3_HEURISTIC_DISAGREE")

    # (4) >= 2 negative phenotype tags
    neg_pheno = [t for t in neg if t in NEGATIVE_TAGS]
    if len(neg_pheno) >= 2:
        reasons.append("R4_HEAVY_NEGATIVE_TAGS")

    # (5) conflicting positive AND negative tags
    pos_pheno = [t for t in pos if t in POSITIVE_TAGS]
    if pos_pheno and neg_pheno:
        reasons.append("R5_CONFLICTING_TAGS")

    score = sum(REASON_WEIGHTS[r] for r in reasons)

    return {
        "call_id": call_id,
        "priority_score": score,
        "reason_codes": reasons,
        "n_reasons": len(reasons),
        "human": {
            "primary_label": primary_label,
            "human_binary": human_bin,
            "confidence": confidence,
            "positive_tags": pos,
            "negative_tags": neg,
            "context_tags": ctx,
            "n_negative_phenotype": len(neg_pheno),
            "note": note,
        },
        "judge_binary": judge_bin,
        "heuristic_binary": heur_bin,
        "disagreement": {
            "judge_vs_human": bool(judge_disagree),
            "heuristic_vs_human": bool(heur_disagree),
        },
    }


def build_queue():
    rows, judge_calls, heuristic, judge_doc = load_inputs()
    entries = [build_entry(r, judge_calls, heuristic) for r in rows]

    # Deterministic ordering: priority_score DESC, then call_id ASC (stable).
    entries.sort(key=lambda e: (-e["priority_score"], e["call_id"]))
    for i, e in enumerate(entries, 1):
        e["rank"] = i

    # ---- summaries ----
    by_conf: dict[str, int] = {}
    by_label: dict[str, int] = {}
    reason_dist: dict[str, int] = {r: 0 for r in REASON_WEIGHTS}
    judge_dis = 0
    heur_dis = 0
    both_dis = 0
    tag_load_buckets = {"0": 0, "1": 0, "2": 0, "3+": 0}
    conflicting = 0
    flagged = 0  # >=1 reason

    for e in entries:
        by_conf[e["human"]["confidence"]] = by_conf.get(e["human"]["confidence"], 0) + 1
        by_label[e["human"]["primary_label"]] = by_label.get(e["human"]["primary_label"], 0) + 1
        for r in e["reason_codes"]:
            reason_dist[r] += 1
        jd = e["disagreement"]["judge_vs_human"]
        hd = e["disagreement"]["heuristic_vs_human"]
        judge_dis += int(jd)
        heur_dis += int(hd)
        both_dis += int(jd and hd)
        n = e["human"]["n_negative_phenotype"]
        key = "3+" if n >= 3 else str(n)
        tag_load_buckets[key] += 1
        if "R5_CONFLICTING_TAGS" in e["reason_codes"]:
            conflicting += 1
        if e["reason_codes"]:
            flagged += 1

    summary = {
        "n_calls": len(entries),
        "n_flagged_for_review": flagged,
        "n_clean_no_signal": len(entries) - flagged,
        "by_confidence": by_conf,
        "by_primary_label": by_label,
        "reason_code_distribution": reason_dist,
        "disagreement": {
            "judge_vs_human": judge_dis,
            "heuristic_vs_human": heur_dis,
            "both_judge_and_heuristic": both_dis,
        },
        "negative_phenotype_tag_load": tag_load_buckets,
        "conflicting_pos_and_neg_tags": conflicting,
    }

    provenance = {
        "generator": "experiments/jun13_eval/annotation/review_queue.py",
        "deterministic": True,
        "tie_break": "priority_score DESC, then call_id ASC (stable)",
        "reason_weights": REASON_WEIGHTS,
        "negative_phenotype_tags": sorted(NEGATIVE_TAGS),
        "positive_phenotype_tags": sorted(POSITIVE_TAGS),
        "inputs": {
            "labels_spike_csv_sha256": _sha256(LABELS_CSV),
            "judge_results_json_sha256": _sha256(JUDGE_JSON),
            "calls_json_sha256": _sha256(CALLS_JSON),
        },
        "judge_run_meta": {
            k: judge_doc.get("run", {}).get(k)
            for k in ("model", "temperature", "rubric_hash", "judge_prompt_hash", "binary_rule")
        },
        "honesty": (
            "Annotation operations only. Priority score is a heuristic over "
            "difficulty-correlated signals; it is NOT model self-knowledge of "
            "uncertainty. True human confidence is observed only AFTER rater-2 "
            "annotates. Disagreement is preserved as signal (arXiv:2304.14803), "
            "never silently reconciled."
        ),
        "reason_descriptions": REASON_DESCRIPTIONS,
    }

    return {"provenance": provenance, "summary": summary, "queue": entries}


def write_md(doc, path: Path):
    s = doc["summary"]
    rd = s["reason_code_distribution"]
    lines = []
    lines.append("# Second-Rater Review Queue\n")
    lines.append(
        "Deterministic ranking of the 46 labeled calls for a second annotation "
        "pass. Generated by `review_queue.py`. Re-running on the same inputs "
        "yields byte-identical ordering (sort: priority_score DESC, call_id ASC).\n"
    )
    lines.append(
        "> **Honesty.** This is annotation *operations*, not a claim that the "
        "model knows when it is uncertain. The priority score is a heuristic over "
        "signals that correlate with annotation difficulty. Real human confidence "
        "is known only AFTER a second rater annotates.\n"
    )
    lines.append(
        "> **Disagreement is signal** (SemEval-2023 Learning With Disagreements, "
        "arXiv:2304.14803). This queue *surfaces* judge/heuristic/human "
        "disagreement for a second read; it never silently reconciles or "
        "overwrites a label.\n"
    )

    lines.append("## Summary\n")
    lines.append(f"- Calls: **{s['n_calls']}**")
    lines.append(f"- Flagged for review (>=1 reason): **{s['n_flagged_for_review']}**")
    lines.append(f"- Clean / no signal: **{s['n_clean_no_signal']}**\n")

    lines.append("### By human confidence\n")
    for k in ("low", "medium", "high"):
        if k in s["by_confidence"]:
            lines.append(f"- {k}: {s['by_confidence'][k]}")
    lines.append("")

    lines.append("### By human primary_label\n")
    for k, v in sorted(s["by_primary_label"].items()):
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("### Disagreement type\n")
    d = s["disagreement"]
    lines.append(f"- judge vs human: {d['judge_vs_human']}")
    lines.append(f"- heuristic vs human: {d['heuristic_vs_human']}")
    lines.append(f"- both judge AND heuristic vs human: {d['both_judge_and_heuristic']}\n")

    lines.append("### Negative-phenotype tag load\n")
    for k in ("0", "1", "2", "3+"):
        lines.append(f"- {k} negative tags: {s['negative_phenotype_tag_load'][k]}")
    lines.append(f"- conflicting positive AND negative tags: {s['conflicting_pos_and_neg_tags']}\n")

    lines.append("### Reason-code distribution\n")
    lines.append("| code | count | weight | description |")
    lines.append("|---|---|---|---|")
    for code in REASON_WEIGHTS:
        lines.append(
            f"| {code} | {rd[code]} | {REASON_WEIGHTS[code]} | {REASON_DESCRIPTIONS[code]} |"
        )
    lines.append("")

    lines.append("## Ranked queue\n")
    lines.append("| rank | call_id | score | human (conf) | judge | heur | reasons |")
    lines.append("|---|---|---|---|---|---|---|")
    for e in doc["queue"]:
        h = e["human"]
        reasons = ", ".join(e["reason_codes"]) if e["reason_codes"] else "—"
        human_cell = f"{h['primary_label']} ({h['confidence']})"
        lines.append(
            f"| {e['rank']} | {e['call_id']} | {e['priority_score']} | "
            f"{human_cell} | {e['judge_binary']} | {e['heuristic_binary']} | {reasons} |"
        )
    lines.append("")

    path.write_text("\n".join(lines))


def main():
    doc = build_queue()
    OUT_JSON.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
    write_md(doc, OUT_MD)
    s = doc["summary"]
    print(f"Wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(
        f"queue={s['n_calls']} flagged={s['n_flagged_for_review']} "
        f"clean={s['n_clean_no_signal']}"
    )
    print("reason_dist:", s["reason_code_distribution"])
    print("disagreement:", s["disagreement"])


if __name__ == "__main__":
    main()
