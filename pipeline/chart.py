#!/usr/bin/env python3
"""Business-value chart (Batch 8A). Reads out/analytics.json ONLY — no labels, no judge output, no
recomputation from raw calls — and renders ONE reproducible figure to reports/charts/.

    .venv/bin/python pipeline/chart.py

Deterministic: same analytics.json -> byte-identical PNG (PNG date metadata stripped; fixed order,
fixed colors, no randomness). No dashboard. Honest labels baked in:
- success    = HEURISTIC task completion (goal/workflow keyword match), not gold
- cost       = ESTIMATED prototype dollars
- panel 3    = FAILURE EVENTS (deterministic signal hits), NOT failed calls
- n          = number of calls in that stress profile (sample size on every bar)

Null-safe: an `unmeasured` stress profile with zero successful calls has cost_per_successful_call
null — that bar renders as 0 height with an "n/a" label, and the y-axis ignores the null. Importable
(render()/`_safe_max` are pure); the analytics file is only read in main().
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
# fixed stress-profile order (increasing difficulty, unmeasured last) -> deterministic bar order
PROF_ORDER = ["clean", "pause_heavy", "interruption", "unmeasured"]
GREEN, CORAL, PURPLE = "#1d9e75", "#d85a30", "#7f77dd"


def _safe_max(vals, default=1):
    """max() ignoring None (e.g. cost_per_successful_call null when a profile has no successes)."""
    nums = [v for v in vals if v is not None]
    return max(nums) if nums else default


def annotate(axis, bars, texts, dy):
    for r, t in zip(bars, texts):
        axis.text(r.get_x() + r.get_width() / 2, r.get_height() + dy, t, ha="center", fontsize=9, color="#555")


def render(A, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    prof = sorted(A["by_stress_profile"],
                  key=lambda p: PROF_ORDER.index(p["stress_profile"]) if p["stress_profile"] in PROF_ORDER else 99)
    labels = [p["stress_profile"] for p in prof]
    ns = [p["n"] for p in prof]
    succ = [p["success_rate"] for p in prof]
    cps = [p["cost_per_successful_call"] for p in prof]
    cps_bars = [c if c is not None else 0 for c in cps]   # null cost (no successes) -> 0-height bar, "n/a" label

    clusters = sorted(A["failure_clusters"], key=lambda c: (-c["count"], c["dimension"]))  # deterministic
    cl_labels = [c["dimension"] for c in clusters]
    cl_counts = [c["count"] for c in clusters]

    fig, ax = plt.subplots(1, 3, figsize=(13, 4.3))

    # panel 1 — task success by stress profile (heuristic)
    b1 = ax[0].bar(labels, succ, color=GREEN)
    ax[0].set_ylim(0, 1)
    ax[0].set_ylabel("task success rate (heuristic)")
    ax[0].set_title("Success by stress profile")
    annotate(ax[0], b1, [f"{s:.0%}\nn={n}" for s, n in zip(succ, ns)], 0.02)

    # panel 2 — estimated cost per successful call by stress profile (null-safe)
    b2 = ax[1].bar(labels, cps_bars, color=CORAL)
    ax[1].set_ylim(0, _safe_max(cps) * 1.20)   # headroom so the top label clears the title
    ax[1].set_ylabel("est. $ per successful call (prototype)")
    ax[1].set_title("Cost per success by stress profile")
    annotate(ax[1], b2, [(f"${c:.3f}" if c is not None else "n/a") + f"\nn={n}" for c, n in zip(cps, ns)],
             _safe_max(cps) * 0.02)

    # panel 3 — deterministic failure EVENTS by type (not failed calls)
    b3 = ax[2].bar(cl_labels, cl_counts, color=PURPLE)
    ax[2].set_ylim(0, _safe_max(cl_counts) * 1.16)
    ax[2].set_ylabel("failure EVENTS (not failed calls)")
    ax[2].set_title("Deterministic failure events")
    annotate(ax[2], b3, [str(c) for c in cl_counts], _safe_max(cl_counts) * 0.02)

    fig.suptitle(f"VoiceForge — business-value view · {A['n_calls']} calls · DETERMINISTIC (pre-judge)",
                 fontsize=13, weight="bold")
    fig.text(0.5, 0.01,
             "success = heuristic task completion (goal/workflow keyword match) · cost = estimated prototype $ · "
             "panel 3 = failure EVENTS (signal hits), not failed calls · n = calls in that stress profile",
             ha="center", fontsize=8, color="#777")
    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    # strip the PNG creation date so re-running is byte-stable
    plt.savefig(out_dir / "business_value.png", dpi=130, metadata={"Date": None, "Software": "voiceforge"})
    plt.close(fig)
    return {"labels": labels, "succ": succ, "cps": cps, "clusters": dict(zip(cl_labels, cl_counts))}


def main():
    A = json.loads((ROOT / "out" / "analytics.json").read_text())
    r = render(A, ROOT / "reports" / "charts")
    print("wrote reports/charts/business_value.png")
    print(f"  success by profile: {dict(zip(r['labels'], r['succ']))}")
    print(f"  cost/success:       {dict(zip(r['labels'], r['cps']))}")
    print(f"  failure events:     {r['clusters']}")
    print("  reads out/analytics.json ONLY (no labels/judge/raw recompute)")


if __name__ == "__main__":
    main()
