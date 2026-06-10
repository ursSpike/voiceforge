# Build Log

Per-block record: what now exists / what was learned. Written at each block's close,
right after the push (SPEC §2.1).

---

## Block 0 — Skeleton · Jun 10, 20:34–21:15 IST · box 1h, used ~40m
- commit `2751961` → pushed (github.com/ursSpike/voiceforge, private)
- **What now exists:** full §6 tree · 5 schemas · rubric.yaml v0 · signals.py FTO core,
  sanity-tested (synthetic fixture → `0:10 agent barge-in 800ms` + `0:19 latency 1,620ms`,
  exact money-shot format) · judge.py with disk cache + --smoke · limitations.md written first ·
  venv with google-genai + pyyaml.
- **What we learned:** the deterministic core is proven before the hero call depends on it;
  gh was already authed so push-per-block is frictionless. Open item carried into Block 1:
  GEMINI_API_KEY → live smoke run (this buildlog entry rides with the Block 1 commit).

