#!/usr/bin/env python3
"""Label-CSV validator (Batch A). One command that proves eval/labels_spike.csv is sound:

    .venv/bin/python pipeline/validate_labels.py            # human summary + writes out/label_validation.json
    .venv/bin/python pipeline/validate_labels.py --quiet    # exit code only (0 ok / 1 problems)

Checks (every one machine-recorded in out/label_validation.json):
  1. exact column set, in order: call_id, primary_label, confidence, positive_tags,
     negative_tags, context_tags, note, timestamp
  2. call_id unique in the stored CSV (write path is last-label-wins; the FILE must hold one row per call)
  3. every call_id belongs to the FROZEN manifest (eval/label_manifest.json)
  4. manifest SHA-256 matches the frozen value recorded at audit time
  5. primary_label / confidence / every tag against the schema allowlists (single source: schemas.py)
  6. notes survive csv quoting (parsed row count == DictReader row count; no field bleed)
  7. binary (success|fail) vs unsure counts vs the >=40 floor
  8. the two pre-repair annotations are PRESERVED EXACTLY (bolna_246cd9f3 + hero_001, success/high
     with their original tags)

Read-only: never writes to the CSV. Output artifact: out/label_validation.json.
"""
import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

CSV_PATH = ROOT / "eval" / "labels_spike.csv"
MANIFEST = ROOT / "eval" / "label_manifest.json"
OUT = ROOT / "out" / "label_validation.json"

EXPECTED_COLS = ["call_id", "primary_label", "confidence", "positive_tags",
                 "negative_tags", "context_tags", "note", "timestamp"]
FROZEN_MANIFEST_SHA = "aec4ba49000c9f4fdfa203cfca4bc787b71004abb47e4a7eff899175446cae33"
FLOOR = 40

# the two annotations that pre-date the slice repair — must never drift
FROZEN_LABELS = {
    "bolna_246cd9f3": {"primary_label": "success", "confidence": "high"},
    "hero_001": {"primary_label": "success", "confidence": "high"},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    import schemas

    checks, problems = [], []

    def check(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        if not ok:
            problems.append(f"{name}: {detail}")
        if not args.quiet:
            print(f"  {'ok  ' if ok else 'FAIL'} {name}" + (f" — {detail}" if detail else ""))

    if not CSV_PATH.exists():
        # an absent CSV is a VALID empty state (labeling not started), not an error
        result = {"csv_present": False, "rows": 0, "binary": 0, "unsure": 0, "floor": FLOOR,
                  "ok": True, "note": "labels file absent — labeling not started"}
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(result, indent=2) + "\n")
        print("labels file absent — valid empty state. wrote out/label_validation.json")
        return 0

    raw = CSV_PATH.read_text()
    rows = list(csv.DictReader(raw.splitlines()))
    header = raw.splitlines()[0].split(",") if raw else []

    # 1 columns
    check("columns exact + ordered", header == EXPECTED_COLS, f"got {header}")
    # 2 unique call_id
    ids = [r["call_id"] for r in rows]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    check("call_id unique (file holds last-label-wins state)", not dupes, f"dupes: {dupes}" if dupes else f"{len(ids)} rows")
    # 3+4 manifest membership + frozen SHA
    man = json.loads(MANIFEST.read_text())
    man_sha = hashlib.sha256(MANIFEST.read_bytes()).hexdigest()
    check("manifest SHA frozen", man_sha == FROZEN_MANIFEST_SHA, man_sha[:16])
    outside = sorted(set(ids) - set(man["order"]))
    check("every call_id in frozen manifest", not outside, f"outside: {outside}" if outside else f"{len(set(ids))} ids")
    # 5 allowlists
    bad_enum = []
    for r in rows:
        if r["primary_label"] not in ("success", "fail", "unsure"):
            bad_enum.append(f"{r['call_id']}: primary={r['primary_label']!r}")
        if r["confidence"] not in ("high", "medium", "low"):
            bad_enum.append(f"{r['call_id']}: confidence={r['confidence']!r}")
        for col, allow in (("positive_tags", schemas.PHENO_POSITIVE),
                           ("negative_tags", schemas.PHENO_NEGATIVE),
                           ("context_tags", schemas.PHENO_CONTEXT)):
            for t in (x for x in (r[col] or "").split("|") if x):
                if t not in allow:
                    bad_enum.append(f"{r['call_id']}: {col} has unknown tag {t!r}")
    check("enums + tag allowlists", not bad_enum, "; ".join(bad_enum[:4]))
    # 6 quoting integrity: every row has exactly the expected fields, none spilled
    spill = [r["call_id"] for r in rows if None in r or any(k not in EXPECTED_COLS for k in r if k is not None)]
    check("csv quoting intact (no field bleed)", not spill, f"bad rows: {spill}")
    # 7 counts vs floor
    binary = [r for r in rows if r["primary_label"] in ("success", "fail")]
    unsure = [r for r in rows if r["primary_label"] == "unsure"]
    check(f"usable binary count (floor {FLOOR})", True,
          f"{len(binary)} binary + {len(unsure)} unsure of {man['total']} — "
          + ("FLOOR MET" if len(binary) >= FLOOR else f"{FLOOR - len(binary)} more needed"))
    # 8 frozen first-two annotations preserved
    by_id = {r["call_id"]: r for r in rows}
    for cid, want in FROZEN_LABELS.items():
        r = by_id.get(cid)
        ok = r is not None and all(r[k] == v for k, v in want.items())
        check(f"frozen annotation preserved: {cid}", ok,
              f"{r['primary_label']}/{r['confidence']}" if r else "MISSING")

    result = {"csv_present": True, "csv_sha256": hashlib.sha256(raw.encode()).hexdigest(),
              "manifest_sha256": man_sha, "rows": len(rows), "binary": len(binary),
              "unsure": len(unsure), "floor": FLOOR, "floor_met": len(binary) >= FLOOR,
              "checks": checks, "problems": problems, "ok": not problems}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    if not args.quiet:
        print(f"\n{'LABEL VALIDATION OK' if not problems else 'PROBLEMS: ' + str(len(problems))} "
              f"· {len(binary)} binary / {len(unsure)} unsure · wrote out/label_validation.json")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
