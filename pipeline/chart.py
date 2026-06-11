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
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
A = json.loads((ROOT / "out" / "analytics.json").read_text())
OUT = ROOT / "reports" / "charts"
OUT.mkdir(parents=True, exist_ok=True)

# fixed stress-profile order (increasing difficulty) -> deterministic bar order
PROF_ORDER = ["clean", "pause_heavy", "interruption"]
prof = sorted(A["by_stress_profile"],
              key=lambda p: PROF_ORDER.index(p["stress_profile"]) if p["stress_profile"] in PROF_ORDER else 99)
labels = [p["stress_profile"] for p in prof]
ns = [p["n"] for p in prof]
succ = [p["success_rate"] for p in prof]
cps = [p["cost_per_successful_call"] for p in prof]

clusters = sorted(A["failure_clusters"], key=lambda c: (-c["count"], c["dimension"]))  # deterministic
cl_labels = [c["dimension"] for c in clusters]
cl_counts = [c["count"] for c in clusters]

fig, ax = plt.subplots(1, 3, figsize=(13, 4.3))
GREEN, CORAL, PURPLE = "#1d9e75", "#d85a30", "#7f77dd"


def annotate(axis, bars, texts, dy):
    for r, t in zip(bars, texts):
        axis.text(r.get_x() + r.get_width() / 2, r.get_height() + dy, t, ha="center", fontsize=9, color="#555")


# panel 1 — task success by stress profile (heuristic)
b1 = ax[0].bar(labels, succ, color=GREEN)
ax[0].set_ylim(0, 1)
ax[0].set_ylabel("task success rate (heuristic)")
ax[0].set_title("Success by stress profile")
annotate(ax[0], b1, [f"{s:.0%}\nn={n}" for s, n in zip(succ, ns)], 0.02)

# panel 2 — estimated cost per successful call by stress profile
b2 = ax[1].bar(labels, cps, color=CORAL)
ax[1].set_ylim(0, max(cps) * 1.20)   # headroom so the top label clears the title
ax[1].set_ylabel("est. $ per successful call (prototype)")
ax[1].set_title("Cost per success by stress profile")
annotate(ax[1], b2, [f"${c:.3f}\nn={n}" for c, n in zip(cps, ns)], max(cps) * 0.02)

# panel 3 — deterministic failure EVENTS by type (not failed calls)
b3 = ax[2].bar(cl_labels, cl_counts, color=PURPLE)
ax[2].set_ylim(0, max(cl_counts) * 1.16)
ax[2].set_ylabel("failure EVENTS (not failed calls)")
ax[2].set_title("Deterministic failure events")
annotate(ax[2], b3, [str(c) for c in cl_counts], max(cl_counts) * 0.02)

fig.suptitle(f"VoiceForge — business-value view · {A['n_calls']} calls · DETERMINISTIC (pre-judge)",
             fontsize=13, weight="bold")
fig.text(0.5, 0.01,
         "success = heuristic task completion (goal/workflow keyword match) · cost = estimated prototype $ · "
         "panel 3 = failure EVENTS (signal hits), not failed calls · n = calls in that stress profile",
         ha="center", fontsize=8, color="#777")
plt.tight_layout(rect=[0, 0.04, 1, 0.95])
# strip the PNG creation date so re-running is byte-stable
plt.savefig(OUT / "business_value.png", dpi=130, metadata={"Date": None, "Software": "voiceforge"})
plt.close(fig)

print("wrote reports/charts/business_value.png")
print(f"  success by profile: {dict(zip(labels, succ))}")
print(f"  cost/success:       {dict(zip(labels, cps))}")
print(f"  failure events:     {dict(zip(cl_labels, cl_counts))}")
print("  reads out/analytics.json ONLY (no labels/judge/raw recompute)")
