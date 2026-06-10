# RESUME — frozen 2026-06-10 ~23:10 IST (learning sprint until ~01:00)

## Where the build stands (all pushed, nothing dangling)
- **Blocks 0, 1, 2, 3a DONE** on night one (~5h ahead of SPEC §5 schedule).
- Hero call take 2: `data/hero/hero_001.wav` + `turns.json` (assembly = ground truth).
  Real failure table: **0:18 agent barge-in 800ms · 0:53 latency 1,620ms** (demo copy uses these).
- Money-shot page `/shot` + recording booth `/` on the local server
  (`.venv/bin/python web/recorder/serve.py` → localhost:7861). Click-to-seek verified (needs the
  server's Range/206 support — don't swap in a server without it).
- Normalized pool: `data/normalized/` = hero + 10 SpokenWOZ
  (3 interruption / 3 pause_heavy / 2 clean_laggy / 2 clean_quiet), stratified, reproducible.
- Signals verified across pool. Judge smoke-tested (contract + cache).

## Resume ritual (in order)
1. **Quiz first (~10 min):** Spike says "quiz me" → oral exam from notebook self-checks +
   the 3 unanswered checkpoint questions (FTO sign at 29,400 vs 30,000; why latency is
   user→agent only; why SpokenWOZ `goal` lives in metadata). Grade honestly, fill gaps.
2. **Block 3b (next build work, ~2h):**
   - `pipeline/judge.py`: per-dimension prompts (language_match, faithfulness, repair_quality)
     over `data/normalized/*.json` — temp 0, JSON, {score, reason, evidence_turn_ids}, cached.
   - `task_outcome` from SpokenWOZ `metadata.goal` (required-fields checklist) → task_completion dim.
   - `pipeline/score.py`: merge deterministic + judged dims, weights from rubric.yaml →
     `out/call_<id>.json` + `out/calls.json`.
   - Push: "pipeline: 9-12 SpokenWOZ calls normalized -> signals + judged scorecards (reasons+evidence)".
3. **Then Block 4** (Spike's 40–60 blind labels — build the blind label sheet BEFORE showing him
   any judge output), then Block 5 (DPO export). Day 3 per SPEC §5 unchanged.

## Standing constraints
- Sleep gate ~00:30 IST. Sleep is outside the 35h budget. A/B = 3h hard clock. Dashboard = 90-min
  Streamlit trigger. Repo private until SPEC.md sanitized (docs/later.md).
- Learning mode artifacts: `notebooks/00–06` + this file. Working agreement: what/how/why per piece,
  Cursor checkpoints, no unexplained jargon.
