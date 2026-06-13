# Dataset card — public backbone (Batch 2)

> **⚠️ PARTIALLY SUPERSEDED (Jun 13) — read this first.** This card was written before the Phase-B
> Hindi-English ingestion. The current composition is authoritative in `eval/label_manifest.json`
> (`composition`: existing_labeled 2 · code_mixed_dialog_hi 30 · spokenwoz_controls 14) and detailed in
> [`docs/batch2R_source_audit.md`](batch2R_source_audit.md):
> - **Frozen labeled / calibration slice = 46** = **30 Code-Mixed-Dialog Hindi-English** (`cmd_hi_*`,
>   romanized Hinglish, translated DSTC2 restaurant booking, Apache-2.0) + **14 SpokenWOZ** English
>   controls + **1 hero** (te-en, constructed) + **1 Bolna** (hi-en, real).
> - **Full scored corpus = 76** = 44 SpokenWOZ + 30 cmd_hi + 1 Bolna + 1 hero.
> - **Multilingual is SHIPPED, not roadmap** — the 30 Hindi-English calls ARE the calibration backbone
>   (hi-en 71% ≈ English 69% is the headline truth-correction slice). The "it is English" line below is
>   stale. The SpokenWOZ methodology below is still accurate for the SpokenWOZ portion.

## SpokenWOZ (the public eval backbone)
- **Source:** SpokenWOZ, *A Large-Scale Speech-Text Benchmark for Spoken Task-Oriented Dialogue*
  (arXiv:2305.13040). Train+dev text split, `data/spokenwoz/data.json` (246MB, already on disk —
  **no re-download**; only a slice is processed).
- **License:** CC BY-NC 4.0 — fine for hackathon *evaluation*; flagged before any commercial use.
- **Why this dataset:** it is real spoken task-oriented dialogue (booking/info tasks) with
  **word-level timestamps** and speaker tags — which maps directly onto VoiceForge's
  call → task-outcome → slot-capture → failure story, and lets us compute real FTO timing
  (latency/overlap) instead of inventing it.

### Fields used vs ignored
| field | use |
|---|---|
| `log[].words[].BeginTime/EndTime` | **used** — synthesize turn `start_ms`/`end_ms` (first word start → last word end per same-speaker run) → the deterministic FTO signals |
| `log[].tag` (user/system) | **used** — `speaker` (system → agent); channel ids do NOT separate speakers |
| `log[].text` | **used** — turn transcript |
| `goal` (per-domain) | **used** — stored in `metadata.goal`; the required-fields source for `task_outcome` (Batch 3) |
| `dialog_act`, `span_info`, `metadata` (dialogue state) | ignored this sprint (slot-state extraction is roadmap) |
| audio (`.wav` corpus) | **not downloaded** — timing comes from the word timestamps in the text split |

### The slice (reproducible, stratified)
`pipeline/normalize.py spokenwoz --k 44` → 44 calls, deterministic first-fit by sorted id over
the 500-call dev list (filtered to 16–60 turns, ≤300s). Stratified across stress profiles so the
blind-label set carries both pass- and fail-prone calls (prevalence trap, book 14):
- interruption ≈20 · clean (laggy+quiet) ≈19 · pause_heavy 5 (only 5 qualifying — top-up filled the
  rest from interruption, deterministically).
- 44 SpokenWOZ calls are scored into the **76-call corpus**; **14** of them are carried into the frozen
  **46-call labeled slice** as English controls (see the manifest `composition` and the banner above).

### Honest caveats
- SpokenWOZ is protocol-collected → **few genuine barge-ins**; it is **latency-rich**, not
  interruption-rich. The hero call supplies the engineered barge-in; AMI (roadmap) would add real overlap.
- *(This SpokenWOZ portion is English.)* The overall labeled slice is **majority Hindi-English** (30 of
  46 are `cmd_hi_*`); SpokenWOZ supplies the English control arm. Multilingual is **shipped**, not roadmap.
- Turn bounds are *synthesized* from word times — exact given the ASR word timestamps, but a
  reconstruction, not ground-truth diarization.

## Other sources in the pool
- **hero_001** — constructed demo call (disclosed; assembly = ground truth; Cartesia Devansh voice).
- **bolna_246cd9f3** — real Bolna execution (timing from `/log`); the "provider logs" path.
- **AMI** (roadmap) — real ~20% overlap for genuine barge-in rows; not used this sprint.
