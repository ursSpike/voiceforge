#!/usr/bin/env python3
"""Contamination regression test (audit blocker #1).

Guarantees a live on-site call can NEVER enter the frozen pipeline. The frozen producers
(score.py, build_manifest.py, schemas.py, preflight.py) all discover calls with a NON-recursive
top-level `data/normalized/*.json` glob; the live bridge writes to `data/normalized/live/`. This test
drops a fake live call into the live dir and asserts every frozen discovery glob excludes it.

Run: python pipeline/test_live_isolation.py   (exit 0 = isolated)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NORM = ROOT / "data" / "normalized"
LIVE = NORM / "live"

ok = True
def check(c, msg):
    global ok
    print(("  ok   " if c else "  FAIL ") + msg)
    ok = ok and c

# the exact globs the frozen producers use (must stay in sync if those files change)
FROZEN_GLOBS = {
    "score.py":          'NORM.glob("*.json")',
    "build_manifest.py": 'NORM.glob("*.json")',
    "schemas.py":        'normalized.glob("*.json")',
    "preflight.py":      'data/normalized.glob("*.json")',
}

LIVE.mkdir(parents=True, exist_ok=True)
canary = LIVE / "bolna_live_canary.json"
created = not canary.exists()
try:
    if created:
        canary.write_text(json.dumps({"call_id": "bolna_live_canary", "_test": True}))

    # 1) the live canary IS visible to the live discovery
    live_stems = {p.stem for p in LIVE.glob("bolna_live_*.json")}
    check("bolna_live_canary" in live_stems, "live discovery sees the live call (data/normalized/live/)")

    # 2) the live canary is INVISIBLE to the frozen top-level discovery
    top = {p.stem for p in NORM.glob("*.json")}
    check("bolna_live_canary" not in top, "frozen top-level NORM.glob('*.json') EXCLUDES the live call")
    check(not any(s.startswith("bolna_live_") for s in top),
          "no bolna_live_* anywhere in top-level data/normalized/")

    # 3) the two sets are disjoint (belt-and-braces)
    check(live_stems.isdisjoint(top), "live slice and frozen slice are disjoint sets")

    # 4) the actual production source still uses a non-recursive glob (guards against a future rglob)
    src = (ROOT / "pipeline" / "score.py").read_text()
    check('NORM.glob("*.json")' in src and 'NORM.rglob' not in src,
          "score.py still uses non-recursive NORM.glob('*.json') (a future rglob would break isolation)")
finally:
    if created and canary.exists():
        canary.unlink()
    # remove the live dir only if we created it and it's now empty
    if LIVE.exists() and not any(LIVE.iterdir()):
        LIVE.rmdir()

print("\n" + ("LIVE-ISOLATION TEST PASSED ✓ (live calls cannot contaminate the frozen pipeline)"
              if ok else "LIVE-ISOLATION TEST FAILED — contamination possible"))
sys.exit(0 if ok else 1)
