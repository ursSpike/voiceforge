# VoiceForge University — Notebook Generation Contract (BINDING)

Read this before generating ANY notebook, every session. Deviation = rejected work.

## Process gate (the anti-drift rule)
1. NOTHING is generated until Spike names the notebook ID(s).
2. Order: cell-level OUTLINE → Spike inspects → build THAT ONE book → Spike inspects → next.
3. One book at a time. No batches. No "while I'm at it." No advanced appendix material early.

## What these are
Not documentation, not lectures, not blog posts. **Training gyms.** The learner is alone with
the notebook; the notebook must behave like a tutor: stop him, make him predict, run tiny
things, explain, change one variable, observe, defend. Goal = ownership (can teach it), not
fluency (can say it).

Learner profile: strong engineering effort, prior research/Python (protein docking, benchmarking),
ran PyTorch without understanding internals. ZERO assumed on: voice AI, evals, LLM judges,
DPO/RLHF, kappa, ASR/TTS, call logs, pandas, matplotlib. Banned phrases: "obviously",
"as you know", "simply", "intuitively" (unless the thing was already taught and demonstrated).

## The loop (every notebook drills it)
PREDICT → run → INSPECT → EXPLAIN (one sentence, out loud) → CHANGE one thing → OBSERVE → DEFEND.

## Cell budget and pacing
- 50–90 SMALL cells. Long because many steps, never because giant essays or code dumps.
- One idea per markdown cell. One clear action per code cell. Output stays visible and small.
- Rhythm: explain → code → output → interpretation prompt → modification → output → reflection.

## Mandatory skeleton (every book, in order — the four acts)
**Act 1 · Orientation:** 1 learning contract ("by the end you can explain…") · 2 knowledge-flow
map (previous → current → next concept + why this book exists in the ladder) · 3 baby intuition
· 4 formal definition · 5 why this exists.
**Act 2 · Mechanics:** 6 toy raw input, printed and inspectable · 7 predict-before-run prompts
ahead of every important cell · 8 reasoning-commented code · 9 output-interpretation gates ·
10 manual calculation on 1–2 examples FIRST · 11 function/library version only AFTER manual.
**Act 3 · Stress:** 12 break-it / change-it (≥2: one guided, one learner-authored) · 13 at least
one wrong-intuition trap (state the wrong belief, prove it wrong with a cell) · 14 one mini
table or graph with the axis-reading ritual.
**Act 4 · Ownership:** 15 VoiceForge connection (where this lives in the real pipeline) ·
16 where it fails / what a smart engineer attacks · 17 beginner + engineer + founder
explanations (all three) · 18 three hackathon defense questions with honest answers ·
19 teach-back gate (close the notebook, 2 minutes, out loud) · 20 the clean sentence.

## Checkpoints
≥5 per notebook, SPECIFIC. Bad: "make sure you understand." Good: "Checkpoint: before
continuing, explain why start_ms and end_ms are needed to detect overlap and why transcript
text cannot."

## Comment standard (savage)
Comments explain reasoning, never syntax.
- Bad: `# sort turns` → Good: `# timing metrics only make sense in chronological order, so we sort by start_ms before computing gaps`
- Bad: `# calculate mean` → Good: `# the mean can hide one terrible delay, so we compare it with p90 later`

## Code rules
Simple Python first. No clever one-liners, no unexplained libraries, no compact tricks.
Print raw inputs before transformed outputs. Show intermediate values. Manual before function,
function before library, ugly before clean. If pandas: say what a row and a column mean.
If plotting: say what x is, what y is, what one mark is, and what claim the chart allows.

## Recurring cast (one coherent world)
The SAME three calls thread through the whole course wherever possible:
- **Call A** — clean English success.
- **Call B** — Hinglish partial success (hesitation, repeats, ambiguity).
- **Call C** — Telugu/Tenglish failure (interruption + language mismatch).
Learned as objects in P01, timed in 04, scored in 06, tagged in 07, judged in 10, paired in 17.

## Prerequisite series (before book 00)
- P00 · How to learn with these notebooks (the ritual itself; trivial topic difficulty)
- P01 · Python objects for call logs (dicts, lists, nesting, JSON-ish)
- P02 · Tables and pandas (rows, columns, filter, group, count)
- P03 · Basic plots for evals (bar, timeline, histogram; axis reading)
- P04 · Debugging confusion (print inputs, intermediates, shrink the example)

## Pass condition (per book)
Cells running is NOT passing. Pass = closed notebook, 2-minute spoken explanation covering:
what it is, why it exists, how it works mechanically, where it fails, how VoiceForge uses it,
and what claim can honestly be made from it.

## Quality checklist (appended to every generated book; any ✗ ⇒ Spike rejects the book)
toy data first ✓ · raw inputs printed ✓ · ≥5 specific checkpoints ✓ · ≥8 predict prompts ✓ ·
manual-before-function ✓ · ≥2 break-its ✓ · ≥1 wrong-intuition trap ✓ · chart/table with
reading ritual ✓ · VoiceForge connection ✓ · 3-level explanation ✓ · 3 defense questions ✓ ·
teach-back gate ✓ · clean sentence ✓ · 50–90 cells ✓ · banned phrases absent ✓

**The standard sentence: these notebooks are not documentation; they are a training gym.**
