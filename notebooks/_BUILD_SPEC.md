# VoiceForge University — Builder Spec (every agent reads this first)

You are building ONE beginner-proof training notebook. Not documentation — a **training gym**.
The learner has research/coding experience (scientific Python, benchmarking) but is NEW to voice
AI, call logs, evals, ASR/TTS, LLM judges, calibration, kappa, DPO/RLHF. Assume zero on the topic.

## Non-negotiable workflow (do this, in order)
1. `Read` the gold reference: `notebooks/P00_how_to_learn.ipynb` — match its rhythm, cell size,
   comment density, learner-cell style. Also `Read` one already-built neighbor if it exists.
2. Write a builder script `notebooks/build_<ID>.py` (Python that emits the .ipynb), using the
   `md()` / `code()` helpers exactly like P00's build script. NEVER hand-write raw .ipynb JSON.
3. Run it: `.venv/bin/python notebooks/build_<ID>.py`
4. Execute gate: `.venv/bin/python notebooks/run_nb.py notebooks/<FILE>.ipynb`  (must print EXECUTION OK)
5. Audit gate: `.venv/bin/python notebooks/audit_nb.py notebooks/<FILE>.ipynb`  (must print ALL PASS)
6. ITERATE on the build script until BOTH gates pass. Do not report success until they do.

## The four acts (skeleton — same as P00)
- **Act 1 Orientation:** learning contract ("by the end you can explain…") · knowledge-flow map
  (`previous → CURRENT → next`, and why this book exists in the ladder) · baby intuition ·
  formal definition · why this exists.
- **Act 2 Mechanics:** tiny toy input printed RAW · PREDICT before important cells · manual
  calculation BY HAND on 1–2 examples · only THEN the function/library version · output
  interpretation gates.
- **Act 3 Stress:** ≥2 break-it/change-it (one guided, one learner-authored) · ≥1 wrong-intuition
  trap (state the wrong belief, prove it wrong in a cell) · where it fails.
- **Act 4 Ownership:** VoiceForge connection (where this lives in the real pipeline — cite real
  files like `pipeline/signals.py`, `rubric.yaml`, `data/hero/turns.json` when true) · beginner +
  engineer + founder explanations (all three) · 3 hackathon defense questions w/ honest answers ·
  TEACH-BACK gate · the clean sentence · the self-audit cell (template below).

## Marker conventions (the audit greps these literal strings — use them exactly)
- specific gates: markdown heading with UPPERCASE `CHECKPOINT` (e.g. `## CHECKPOINT 3`) — need ≥5
- act-end gates: lowercase `knowledge-flow checkpoint` (e.g. `## ACT 2 knowledge-flow checkpoint`) — need 4 (one per act)
- before predict cells: `PREDICT` — need ≥8
- learner-owned code cells: `YOUR TURN` in a comment — need ≥6
- break cells: `BREAK-IT` and for a crashing teaching cell also `EXPECTED FAILURE FOR LEARNING`
- trap: `WRONG-INTUITION TRAP` — need ≥1
- `TEACH-BACK` gate · `clean sentence` heading · `defense question(s)` · the words
  `beginner` / `engineer` / `founder` for the 3-level explanation.
- BANNED words (audit fails if present): obviously · as you know · simply · intuitively.

## Cell budget & style
- 50–90 cells, MANY SMALL ones. One idea per markdown cell, one action per code cell.
- Comments explain WHY a line exists, never syntax. Bad: `# sort turns`. Good:
  `# timing metrics only make sense in chronological order, so we sort by start_ms first`.
  EVERY code cell needs at least one such reasoning comment (the audit checks this).
- Manual before function, raw before transformed, toy before real. No clever one-liners.

## Learner-owned cell pattern (MUST run clean when UNFILLED)
Use `None`/`""` placeholders and a guard so a fresh notebook passes `run_nb.py`:
```
# YOUR TURN - predict the average BEFORE running the compute cell.
my_guess = None          # <- learner replaces None with a number
if my_guess is None:
    print("fill in my_guess above, then re-run this cell.")
else:
    print("locked:", my_guess)
```
Anything a later cell needs must be guarded too (`if x is not None:`), so unfilled cells never
crash downstream. Teaching-crash cells (Act 3) carry `# EXPECTED FAILURE FOR LEARNING` so the
executor allows them, and are immediately followed by a recovery/fix cell.

## The recurring cast (use these EXACT three across the course)
- **Call A — clean English success.** id `call_A`, language English. Booking/appointment, cooperative
  caller, low turns, all required fields captured. outcome: success.
- **Call B — Hinglish partial.** id `call_B`, language Hinglish (Hindi+English mix). Hesitations, a
  repeat request, mild ambiguity; task partially completed. outcome: partial.
- **Call C — Telugu/Tenglish failure.** id `call_C`, language Telugu-English. Agent interrupts the
  caller mid-answer (barge-in), locality/address ambiguity, language mismatch. outcome: failure.
  (This mirrors the real hero call `data/hero/turns.json` — reference it from book 04 onward.)
Prereqs P01–P04 BUILD these by hand (that's the lesson). VoiceForge books 00+ define them inline
from this spec (keep ids/languages/outcomes identical — the Consistency reviewer checks this).

## Terminology (use consistently)
call log · trace (timed turns) vs transcript (text only) · turn · speaker (user|agent) ·
start_ms/end_ms · FTO (floor transfer offset = next.start_ms − prev.end_ms; negative=overlap,
positive=gap) · barge-in (overlap >100ms) · backchannel (overlap ≤100ms) · latency (gap on
user→agent) · laggy (>800ms) · p50/p90 (never just mean) · task success (required-fields
checklist) · stress profile (scenario class: clean/pause_heavy/interruption) · failure tag ·
scorecard (score + reason + evidence_turn_ids) · improvement example · preference pair
(chosen/rejected) · DPO · pilot calibration · Cohen's kappa.

## Real repo anchors (use the real thing where the topic allows)
- `data/hero/turns.json` — the real hero call (12 turns, real ms): 0:18 barge-in 800ms · 0:53 gap 1,620ms
- `data/normalized/*.json` — 11 real calls (hero + 10 SpokenWOZ), schema in `schemas/call_log.md`
- `pipeline/signals.py` → `turn_metrics()`, `analyze()` — the deterministic FTO core
- `pipeline/judge.py` → `judge_dimension()` — real Gemini judge, cached (book 10 may call it live)
- `rubric.yaml` — dimensions/weights/thresholds (book 21)
Prefer the small normalized pool + toy data. Only touch `data/spokenwoz/data.json` (246MB) if
truly needed, and load it lazily.

## The self-audit cell (paste as the LAST cell; change only the filename)
```
# SELF-AUDIT - counts this notebook's own structure from the .ipynb on disk.
# A claim of compliance is wet cement; this counts. (Same logic as notebooks/audit_nb.py.)
import json, re
from pathlib import Path
name = "<FILE>.ipynb"   # <- this notebook's filename
nb_path = next(p for p in [Path.cwd()/name, Path.cwd()/"notebooks"/name,
               *[a/"notebooks"/name for a in Path.cwd().parents]] if p.exists())
nb = json.loads(nb_path.read_text())
S = lambda c: c["source"] if isinstance(c["source"], str) else "".join(c["source"])
pool = [c for c in nb["cells"] if "SELF-AUDIT" not in S(c) and "banned phrase" not in S(c).lower()]
md = [c for c in pool if c["cell_type"]=="markdown"]; co = [c for c in pool if c["cell_type"]=="code"]
cnt = lambda m, g: sum(1 for c in g if m in S(c))
reason = lambda c: any(len(l.strip("# ").split())>=4 for l in S(c).splitlines() if l.strip().startswith("#"))
t = " ".join(S(c).lower() for c in pool)
checks = {
 "total cells 50-90": (len(nb["cells"]), 50<=len(nb["cells"])<=90),
 "specific checkpoints >=5": (cnt("CHECKPOINT", md), cnt("CHECKPOINT", md)>=5),
 "act knowledge-flow cps >=4": (cnt("knowledge-flow checkpoint", md), cnt("knowledge-flow checkpoint", md)>=4),
 "predict prompts >=8": (cnt("PREDICT", pool), cnt("PREDICT", pool)>=8),
 "break-it >=2": (cnt("BREAK-IT", co)+cnt("EXPECTED FAILURE FOR LEARNING", co), cnt("BREAK-IT", co)+cnt("EXPECTED FAILURE FOR LEARNING", co)>=2),
 "wrong-intuition trap >=1": (cnt("WRONG-INTUITION TRAP", md), cnt("WRONG-INTUITION TRAP", md)>=1),
 "learner cells >=6": (cnt("YOUR TURN", co), cnt("YOUR TURN", co)>=6),
 "reasoning comments all": (sum(map(reason, co)), all(map(reason, co)) if co else False),
 "3-level explanation": (1, all(w in t for w in ("beginner","engineer","founder"))),
 "teach-back": (cnt("TEACH-BACK", md), cnt("TEACH-BACK", md)>=1),
 "clean sentence": (1, "clean sentence" in t),
 "banned phrases =0": (sum(bool(re.search(r"\\b"+w+r"\\b", t)) for w in ["obviously","as you know","simply","intuitively"]), not any(re.search(r"\\b"+w+r"\\b", t) for w in ["obviously","as you know","simply","intuitively"])),
}
print(f"{'metric':<28}{'n':>5}  verdict"); ok=True
for k,(n,p) in checks.items():
    ok &= p; print(f"{k:<28}{n:>5}  {'PASS' if p else 'FAIL'}")
print("AUDIT:", "ALL PASS - now do the teach-back" if ok else "FAIL")
```

## Done = both gates green
Report back only: filename, total/code/md cell counts, `audit_pass` (bool), `execution_ok` (bool),
and one line on what the learner can explain after it. If a gate won't go green after honest
effort, report `audit_pass:false` with the failing metric — never fake it.
