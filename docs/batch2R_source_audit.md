# Batch 2R · Phase A — Source audit (calibration-slice repair)

**Status:** AUDIT ONLY — no ingest, no normalization, no schema change, no booth restart. Awaiting Codex ruling.
**Why this batch:** the current label pool is 44 monolingual-English SpokenWOZ calls (turn median ≈36, max 60) —
long to label and mismatched with VoiceForge's multilingual thesis. Goal: a 40-call slice of SHORT, multilingual,
goal-oriented calls.

**Integrity at audit start (unchanged):**
- `eval/labels_spike.csv` SHA-256 `e6d205564e07906f7fc34ab29066d28ce2a47ca8eeba7036c22d47b6975b4eb0` — MATCH (2 labels preserved:
  `bolna_246cd9f3`→success, `hero_001`→success).
- Booth stopped; `data/normalized/` = 46 calls (44 `swz_*` + hero + bolna), untouched.

## Candidate table (verified from primary sources)

| source | language | license | dialogues | turn-length (real turns) | task-oriented | real/translated/synthetic | verdict |
|---|---|---|---|---|---|---|---|
| **Code-Mixed-Dialog** (sumanbanerjee1) @ `9df1d4dc` | **Hindi-English** (romanized Hinglish) | **Apache-2.0** (repo LICENSE) | dev 500 (train/test larger; DSTC2 splits) | **median 8 · p90 11 · max 18 · 99% ≤16 · 100% ≤20** | YES (DSTC2 restaurant reservation: `api_call` + `R_` KB slots) | human-**translated** from English DSTC2 | **INCLUDE** — short, code-mixed, goal-oriented, permissive license |
| Code-Mixed-Dialog — bengali / gujarati / **tamil** / english splits | Bn/Gu/**Ta**/En-English | Apache-2.0 | same DSTC2 dialogues, translated | same (short) | translated | **EXCLUDE for now** — Tamil≠Telugu; en + other langs are PARALLEL translations of the same dialogues (would double-count); English control comes from SpokenWOZ instead |
| **Code-Mixed-TOD-Medical** (suman101112) | **Telugu-English** (Telugu script + romanized Tenglish) | **CC BY-NC 4.0** | paper 3,005 / repo snapshot ~1,023 files | task-oriented (intent/slot) | **real** (transcribed patient↔doctor audio) | **RULING NEEDED** — the ONLY verified Telugu-English TOD, but **medical domain** (not restaurant/service) + non-commercial |
| SpokenWOZ `swz_*` (already in pool) | English | CC BY-NC 4.0 | 44 present | median 36 (long); pick the shortest/most diverse | real (audio-derived) | **INCLUDE (controls)** — select 14 short, diverse |
| _excluded:_ Telugu sentence-pairs, monolingual Telugu, dialog-act-tagging code, social/abusive corpora | — | — | — | — | not dialogue / not task-oriented / no license | **EXCLUDE** (see Telugu hunt report) |

## License discrepancy — resolved
- The **GitHub repo LICENSE is Apache-2.0** (verbatim Apache 2.0 text; SPDX-detected Apache-2.0). The copyright line is the
  unfilled stock template (`[yyyy] [name of copyright owner]`) — authors dropped in the standard license without editing the
  header, but SPDX still classifies it Apache-2.0. **This is the license that governs the dialogue DATA we would ingest.**
- The **"CC BY 4.0"** seen on the paper is the **arXiv submission license badge** (it licenses the paper PDF/source on
  arxiv.org/abs/1806.05997), NOT the dataset. The paper body only says the data is "made publicly available for research purposes."
- **Resolution:** ingest under **Apache-2.0** (repo license). No real conflict — CC BY 4.0 applies to a different artifact (the paper).
  Both are permissive-attribution; we attribute Banerjee et al. (COLING 2018) + repo URL + commit SHA regardless. Apache-2.0 is
  even commercial-safe (unlike SpokenWOZ CC BY-NC).

## Telugu-English verdict — STOP FOR RULING (per plan)
A licensed public **Telugu-English** *restaurant/service/booking* goal-oriented dialogue dataset **does not exist** (verified hunt).
- The only Telugu-English TOD is **medical-domain** (Code-Mixed-TOD-Medical, CC BY-NC 4.0) — real Tenglish, wrong task family.
- Tamil-English ("Tanglish") in Code-Mixed-Dialog is **NOT** a substitute (different language) — will not silently swap.
- **Already in-pool:** the **hero call is `te-en` Telugu-English** and is one of the 2 fixed labels — so Telugu IS represented
  in the slice even with no Telugu dataset.

### Telugu options for the ruling
- **(A) Recommended — drop the dataset-Telugu slice; reallocate to Hindi-English.** Telugu stays represented by the hero call.
  Slice: 2 existing (`bolna` hi-en + `hero` te-en) + **24 Hindi-English** (Code-Mixed-Dialog) + **14 short SpokenWOZ English controls** = 40.
  Cleanest: all short, multilingual via Hinglish + the Telugu hero, licenses Apache-2.0 + CC BY-NC (both eval-safe).
- **(B) Add real Tenglish from the medical set.** 2 existing + 16 Hindi-English + **8 Telugu-English medical (CC BY-NC)** + 14 English = 40.
  Pro: genuine Telugu-English breadth. Con: introduces a 3rd source + a medical domain + a non-commercial license; domain heterogeneity.

## Honest-normalization notes (for the LATER ingest phase, not done now)
- Code-Mixed-Dialog is **text-only, no timestamps** → on ingest: `timing_observed: false`, `stress_profile: unmeasured` (new honest
  value), and timing/overlap dimensions **omitted** (never fabricate ms spacing). Parse only real user↔system exchange lines
  (TAB-separated); skip `api_call`/`R_` KB lines.
- **Outcome derivation:** DSTC2 has `api_call`/KB structure but this repo ships no explicit per-dialogue success label → outcomes
  would be the same documented HEURISTIC as SpokenWOZ (api_call resolved + requested slots provided). Must be labeled HEURISTIC; do
  not invent gold outcomes.
- Provenance per ingested call: original dialogue id, language, repo+commit `9df1d4dc`, license Apache-2.0, selection rule,
  `timing_observed:false`, status=translated.

## Commands run (audit)
- `gh api repos/sumanbanerjee1/Code-Mixed-Dialog …` → license Apache-2.0, branch master, commit `9df1d4dc800548a883f8bc1a9ce4116c77aebc02` (2018-06-20), data dirs = bengali/english/gujarati/hindi/tamil (NO telugu).
- `WebFetch arxiv 1806.05997` → COLING 2018, Banerjee/Moghe/Arora/Khapra; langs Hi/Bn/Gu/Ta-En (no Telugu); DSTC2 restaurant; translated; arXiv badge CC BY 4.0.
- range-fetch + parse of `data/hindi/dialog-dstc2-dev.txt` (500 dialogues) → real-turn distribution median 8 / p90 11 / max 18.
- parallel agent → Telugu-English hunt (verdict PARTIAL: only medical CC BY-NC Telugu TOD exists).

## Next step
**STOP for Codex audit.** On approval: ingest Hindi-English (Apache-2.0) honestly + build `eval/label_manifest.json` (immutable order,
entries 1–2 = bolna/hero) + `label_order()` reads manifest & fails on dup/missing. No ingest until the Telugu ruling (A vs B) lands.
