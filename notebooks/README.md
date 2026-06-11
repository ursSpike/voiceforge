# VoiceForge University

36 interactive training notebooks that take you from absolute zero to being able to
*explain* (not just run) every concept VoiceForge is built on — to a beginner, an engineer,
and a founder.

These are **training gyms, not documentation.** Each book makes you work, not read.

## The ritual (do this on every cell — it is the whole method)
**predict → run → inspect → explain → change → observe → defend**
- Before a cell: say (or type) what you expect.
- After it: explain the output in one sentence, out loud.
- Hit the `YOUR TURN` cells — type your real answer into the variable; they nag until you do.
- Honor the `CHECKPOINT` and `TEACH-BACK` gates: a book is *passed* only when you can close it
  and explain what it is, why it exists, how it works, where it fails, and how VoiceForge uses it.
  Green cells are not passing.

## How to run
Open a notebook in Cursor/Jupyter, pick the `.venv` kernel, run top to bottom.
Some cells are **designed to crash** (marked `EXPECTED FAILURE FOR LEARNING`) — that is a lesson,
keep going. The last cell of every book is a self-audit that counts its own structure.

You can re-check any book yourself:
```
.venv/bin/python notebooks/run_nb.py   notebooks/<file>.ipynb   # every cell executes
.venv/bin/python notebooks/audit_nb.py notebooks/<file>.ipynb   # structure is gym-shaped
```

## Run order
**Start with `P00`** — it teaches the learning method itself on trivial data. Then the
prerequisites, then the three tiers. Full ordered list with status: `reports/notebook_manifest.md`.

1. **Prerequisites** — P00 method · P01 objects · P02 tables · P03 plots · P04 debugging
2. **Tier 1 (00–09) survival** — what VoiceForge is, call logs, schemas, pandas, timing, the
   voice stack, task success, failure tags, cost, language
3. **Tier 2 (10–19) measurement** — LLM-as-judge, evidence, calibration, confusion matrix,
   kappa, honest framing, improvement examples, preference pairs, DPO, RLHF/RLAIF
4. **Tier 3 (20–30) system & defense** — A/B loop, rubric, simulators, datasets, annotation,
   charts, dashboard, adapters, engineer-talk, the demo, the roadmap

Recurring cast across the course: **Call A** (clean English success), **Call B** (Hinglish
partial), **Call C** (Telugu-English failure) — mirrored by the real hero call in `data/hero/`.

## Note on the canonical set
The 36 books above (`P00`–`P04`, `00`–`30`) are the canonical course. A few earlier
exploratory notebooks (`00_start_here`, `01_voice_agents_anatomy`, `02_measuring_conversations`,
`03_llm_as_judge`, `04_human_calibration_kappa`, `05_dpo_improvement_data`, `06_the_room_and_pitch`,
`A1`–`A3`, `B1`–`B4`) remain in this folder as an optional deep-dive appendix — they are NOT part
of the numbered course; follow the run order above.
