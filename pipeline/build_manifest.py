#!/usr/bin/env python3
"""Build eval/label_manifest.json — the IMMUTABLE blind-label order (Batch 2R Phase B).

Deterministic + idempotent: same data/normalized/ -> byte-identical manifest. The booth (serve.py
label_order) reads this file and fails on any duplicate or missing call. Composition (Option A, 46 —
6 SHORT Hinglish reserves added over English controls so a few honest `unsure`s still clear the
>=40-binary calibration floor):
  1-2   frozen prefix  : the two already-labeled calls (bolna_246cd9f3, hero_001), in label order
  3-32  code_mixed_dialog : 30 Hindi-English cmd_hi_* (sorted; each <=20 utterance turns)
  33-46 spokenwoz controls: the 14 SHORTEST swz_* by (turn_count, call_id)

    .venv/bin/python pipeline/build_manifest.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NORM = ROOT / "data" / "normalized"
MANIFEST = ROOT / "eval" / "label_manifest.json"

FROZEN_PREFIX = ["bolna_246cd9f3", "hero_001"]   # the two already-labeled calls — never reordered
N_CMD = 30          # 24 originals + 6 short Hinglish reserves (unsure-slack for the >=40 binary floor)
N_CONTROLS = 14


def turn_count(call_id):
    return len(json.loads((NORM / f"{call_id}.json").read_text())["turns"])


def main():
    have = {p.stem for p in NORM.glob("*.json")}
    for cid in FROZEN_PREFIX:
        assert cid in have, f"frozen-prefix call missing from pool: {cid}"

    cmd = sorted(p.stem for p in NORM.glob("cmd_hi_*.json"))
    assert len(cmd) >= N_CMD, f"need {N_CMD} cmd calls, have {len(cmd)}"
    cmd = cmd[:N_CMD]

    swz = sorted(p.stem for p in NORM.glob("swz_*.json"))
    controls = sorted(swz, key=lambda c: (turn_count(c), c))[:N_CONTROLS]   # shortest, deterministic tie-break

    order = FROZEN_PREFIX + cmd + controls
    assert len(order) == len(set(order)), "duplicate call_id in manifest order"
    assert all(c in have for c in order), "manifest references a call missing from data/normalized/"
    assert len(order) == len(FROZEN_PREFIX) + N_CMD + N_CONTROLS

    manifest = {
        "version": 1,
        "total": len(order),
        "frozen_prefix": FROZEN_PREFIX,
        "order": order,
        "composition": {"existing_labeled": len(FROZEN_PREFIX),
                        "code_mixed_dialog_hi": N_CMD, "spokenwoz_controls": N_CONTROLS},
        "selection_rules": {
            "frozen_prefix": "the two already-labeled calls (bolna hi-en, hero te-en), in label order — immutable",
            "code_mixed_dialog_hi": "first 24 cmd_hi_* (sorted); each 4<=utterance_turns<=20, deduped; repo @9df1d4dc",
            "spokenwoz_controls": "14 SHORTEST swz_* by (turn_count, call_id)",
        },
        "source_revisions": {
            "code_mixed_dialog": "9df1d4dc800548a883f8bc1a9ce4116c77aebc02 (Apache-2.0)",
            "spokenwoz": "dev split (CC BY-NC 4.0)",
            "hero": "constructed (assembly_timeline)", "bolna": "execution 246cd9f3",
        },
        "note": "IMMUTABLE blind-label order. Booth serves in this order, 'Call N of 40'. Do not add/remove "
                "data/normalized/ during a labeling session. Tags are exploratory; the binary spine is the kappa anchor.",
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")

    control_turns = {c: turn_count(c) for c in controls}
    print(f"wrote {MANIFEST.relative_to(ROOT)} — {len(order)} calls")
    print(f"  frozen prefix : {FROZEN_PREFIX}")
    print(f"  cmd ({N_CMD})      : {cmd[0]} … {cmd[-1]}")
    print(f"  controls (14) : shortest swz, turns {min(control_turns.values())}–{max(control_turns.values())}")
    print(f"                  {controls}")


if __name__ == "__main__":
    main()
