#!/usr/bin/env python3
"""Headless notebook executor — the shared execution gate for VoiceForge University.

  python notebooks/run_nb.py notebooks/<id>.ipynb

Runs every code cell top-to-bottom in one shared namespace (like a real kernel), from the
repo root so data paths resolve. Cells deliberately marked as teaching-failures are allowed:
a cell whose source contains "EXPECTED FAILURE FOR LEARNING" (or "SUPPOSED to error") may
raise, and execution continues. Any OTHER exception is an UNEXPECTED FAILURE -> exit 1.

Learner-owned cells must be written to run cleanly when UNFILLED (None placeholders + guards),
so this gate passes on a fresh notebook the learner has not touched yet.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")   # no GUI backend in headless runs

EXPECT = ("EXPECTED FAILURE FOR LEARNING", "SUPPOSED to error")


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: run_nb.py <notebook.ipynb>")
    nb_path = Path(sys.argv[1]).resolve()
    root = next(a for a in [Path.cwd(), *Path.cwd().parents] if (a / "rubric.yaml").exists())
    os.chdir(root)

    import warnings
    warnings.filterwarnings("ignore")
    import matplotlib.pyplot as plt
    plt.show = lambda *a, **k: None        # swallow show() so headless runs don't warn/block

    nb = json.loads(nb_path.read_text())
    ns = {"__name__": "__main__"}
    fails = []
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"]) if isinstance(c["source"], list) else c["source"]
        try:
            exec(compile(src, f"{nb_path.name}:cell{i}", "exec"), ns)
        except Exception as e:
            if any(m in src for m in EXPECT):
                continue                    # this cell is supposed to blow up; teaching moment
            fails.append((i, type(e).__name__, str(e)))
        finally:
            plt.close("all")

    if fails:
        for i, t, m in fails:
            print(f"UNEXPECTED FAILURE cell{i}: {t}: {m}")
        sys.exit(1)
    print(f"EXECUTION OK: every code cell ran clean ({nb_path.name})")


if __name__ == "__main__":
    main()
