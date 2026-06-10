#!/usr/bin/env python3
"""Programmatic notebook structure audit — the shared QUALITY gate (docs/notebook-contract.md).

  python notebooks/audit_nb.py notebooks/<id>.ipynb

Counts the notebook's own structure from the .ipynb on disk and prints PASS/FAIL per metric.
Exit 0 = all pass; exit 1 = at least one FAIL. A claim of compliance is wet cement; this counts.

Marker convention every builder MUST follow so the greps land (also in _BUILD_SPEC.md):
- specific gate headings contain uppercase "CHECKPOINT" (e.g. "## CHECKPOINT 3")
- act-end gates contain lowercase "knowledge-flow checkpoint"
- "PREDICT" before predict-cells · "YOUR TURN" in learner-owned code cells
- "BREAK-IT" or "EXPECTED FAILURE FOR LEARNING" on break cells
- "WRONG-INTUITION TRAP" · "TEACH-BACK" · "clean sentence" · "defense question"
- the three-level explanation names "beginner", "engineer", "founder"
"""
import json
import re
import sys
from pathlib import Path

BANNED = ["obviously", "as you know", "simply", "intuitively"]


def src(c):
    return c["source"] if isinstance(c["source"], str) else "".join(c["source"])


def has_reasoning(c):
    # a code cell teaches if at least one comment line carries a real sentence (>= 4 words),
    # not just "# import x". Trivial cells with no reasoning comment fail the contract.
    return any(len(line.strip("# ").split()) >= 4
               for line in src(c).splitlines() if line.strip().startswith("#"))


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: audit_nb.py <notebook.ipynb>")
    nb = json.loads(Path(sys.argv[1]).read_text())
    all_cells = nb["cells"]
    # the audit cell names every marker it greps for, so it must never count itself
    pool = [c for c in all_cells if "SELF-AUDIT" not in src(c) and "banned phrase" not in src(c).lower()]
    md = [c for c in pool if c["cell_type"] == "markdown"]
    co = [c for c in pool if c["cell_type"] == "code"]

    def cnt(marker, group, lower=False):
        return sum(1 for c in group if (marker.lower() in src(c).lower() if lower else marker in src(c)))

    text_all = " ".join(src(c).lower() for c in pool)
    banned_hits = [w for w in BANNED if re.search(r"\b" + re.escape(w) + r"\b", text_all)]

    # specific gates use uppercase "CHECKPOINT"; act gates use lowercase "knowledge-flow
    # checkpoint" and so never match the uppercase grep -> no subtraction needed
    specific_cp = cnt("CHECKPOINT", md)
    breakit = cnt("BREAK-IT", co) + cnt("EXPECTED FAILURE FOR LEARNING", co) + cnt("self-authored break", co)
    three_level = all(w in text_all for w in ("beginner", "engineer", "founder"))

    checks = {
        "total cells (50-90)":              (len(all_cells), 50 <= len(all_cells) <= 90),
        "code cells":                       (len(co), True),
        "markdown cells":                   (len(md), True),
        "specific checkpoints (>=5)":       (specific_cp, specific_cp >= 5),
        "act knowledge-flow cps (>=4)":     (cnt("knowledge-flow checkpoint", md), cnt("knowledge-flow checkpoint", md) >= 4),
        "predict prompts (>=8)":            (cnt("PREDICT", pool), cnt("PREDICT", pool) >= 8),
        "break-it cells (>=2)":             (breakit, breakit >= 2),
        "wrong-intuition traps (>=1)":      (cnt("WRONG-INTUITION TRAP", md), cnt("WRONG-INTUITION TRAP", md) >= 1),
        "learner-owned cells (>=6)":        (cnt("YOUR TURN", co), cnt("YOUR TURN", co) >= 6),
        "code cells w/ reasoning comments": (sum(map(has_reasoning, co)), all(map(has_reasoning, co)) if co else False),
        "3-level explanation":              (int(three_level), three_level),
        "defense questions":                (cnt("defense question", pool, lower=True), cnt("defense question", pool, lower=True) >= 1),
        "teach-back gate":                  (cnt("TEACH-BACK", md), cnt("TEACH-BACK", md) >= 1),
        "clean sentence":                   (cnt("clean sentence", pool, lower=True), cnt("clean sentence", pool, lower=True) >= 1),
        "banned phrases (=0)":              (len(banned_hits), len(banned_hits) == 0),
    }

    print(f"{'metric':<36} {'count':>6}  verdict")
    print("-" * 56)
    ok = True
    for k, (n, passed) in checks.items():
        ok &= passed
        print(f"{k:<36} {n:>6}  {'PASS' if passed else 'FAIL'}")
    print("-" * 56)
    if banned_hits:
        print("banned:", banned_hits)
    print("AUDIT:", "ALL PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
