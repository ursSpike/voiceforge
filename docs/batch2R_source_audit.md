# Batch 2R · Phase A — Source audit (calibration-slice repair)

**Status:** **Phase B BUILT** — 24 Hindi-English ingested, immutable manifest written, booth wired to it. NO booth restart yet,
labels frozen (`e6d2055…`), existing 46 outputs byte-identical. Awaiting Codex audit of the new pool + manifest before restart.
**Why this batch:** the current label pool is 44 monolingual-English SpokenWOZ calls (turn median ≈36, max 60) —
long to label and mismatched with VoiceForge's multilingual thesis. Goal: a 40-call slice of SHORT, multilingual,
goal-oriented calls.

**Integrity at audit start (unchanged):**
- `eval/labels_spike.csv` SHA-256 `e6d205564e07906f7fc34ab29066d28ce2a47ca8eeba7036c22d47b6975b4eb0` — MATCH (2 labels preserved:
  `bolna_246cd9f3`→success, `hero_001`→success).
- Booth stopped; `data/normalized/` = 46 calls (44 `swz_*` + hero + bolna), untouched.

## Candidate table (verified from primary sources)

**Turn-counting note (corrected per Codex):** VoiceForge counts **each speaker utterance as a turn**. My Phase-A
first pass counted user↔system *exchanges* (median 8) — an undercount of ~2×. Corrected utterance-based distribution
below. Selection filters on the **ingest adapter's exact per-utterance turn count ≤20**.

| source | language | license | dialogues | turn-length (**utterance turns**) | task-oriented | real/translated/synthetic | verdict |
|---|---|---|---|---|---|---|---|
| **Code-Mixed-Dialog** (sumanbanerjee1) @ `9df1d4dc` | **Hindi-English** (romanized Hinglish) | repo LICENSE = Apache-2.0 (text) | dev 500 (train/test larger; DSTC2 splits) | **median 15 · p90 21 · max 35 · ~85–88% ≤20** (≥400 candidates ≤20 in dev — **pre-adapter estimate**; the **final ≤20 count comes from the ingest adapter**) | YES (DSTC2 restaurant reservation: `api_call` + `R_` KB slots) | human-**translated** from English DSTC2 | **INCLUDE** — short, code-mixed, goal-oriented |
| Code-Mixed-Dialog — bengali / gujarati / **tamil** / english splits | Bn/Gu/**Ta**/En-English | Apache-2.0 (text) | same DSTC2 dialogues, translated | same (short) | translated | **EXCLUDE** — Tamil≠Telugu; en + other langs are PARALLEL translations of the same dialogues (would double-count); English control comes from SpokenWOZ instead |
| **Code-Mixed-TOD-Medical-Dataset** (suman101112) | **Telugu-English** (Telugu script + romanized Tenglish) | **CC BY-NC 4.0** | paper 3,005 / repo snapshot ~1,024 transcript files + 2 docs | **not computed** (dropped — see below) | YES — **medical** (patient↔doctor), not restaurant/service | **real** (transcribed audio) | **DROPPED** (Option A) — only verified Telugu-English TOD, but medical domain + non-commercial; not pursued this sprint |
| SpokenWOZ `swz_*` (already in pool) | English | CC BY-NC 4.0 | 44 present | median 36 (long); pick the shortest/most diverse | real (audio-derived) | **INCLUDE (controls)** — select 14 short, diverse |
| _excluded:_ Telugu sentence-pairs, monolingual Telugu, dialog-act-tagging code, social/abusive corpora | — | — | — | — | not dialogue / not task-oriented / no license | **EXCLUDE** (see Telugu hunt report) |

## License discrepancy — what the two artifacts say (not a conclusive legal opinion)
- The **GitHub repo ships an Apache-2.0 LICENSE file** (verbatim Apache 2.0 text; GitHub/SPDX detect Apache-2.0). Caveat: the
  copyright line is the **unfilled stock template** (`[yyyy] [name of copyright owner]`) — the authors dropped in the standard
  license without editing the header. So the repo *presents* Apache-2.0, but I do **not** declare its precise legal scope or call
  it "commercial-safe."
- The **"CC BY 4.0"** seen on the paper is the **arXiv submission license badge** (it licenses the paper PDF/source on
  arxiv.org/abs/1806.05997), NOT the dataset. The paper body only says the data is "made publicly available for research purposes."
- **For this hackathon (non-commercial research eval):** either license — repo Apache-2.0 *or* paper CC BY 4.0 — permits research
  use with attribution, and SpokenWOZ is already CC BY-NC, so the slice is non-commercial regardless. We attribute Banerjee et al.
  (COLING 2018) + repo URL + commit `9df1d4dc`. Any commercial decision is out of scope and would need counsel given the template gap.

## Telugu-English verdict — RULED: Option A (drop dataset-Telugu)
**No suitable Telugu-English** *restaurant/service/booking* goal-oriented dialogue dataset **was found in this audit** (not a proof
of non-existence — a thorough hunt came up empty).
- The only Telugu-English TOD is **medical-domain** (Code-Mixed-TOD-Medical, CC BY-NC 4.0) — real Tenglish, wrong task family.
- Tamil-English ("Tanglish") in Code-Mixed-Dialog is **NOT** a substitute (different language) — will not silently swap.
- **Already in-pool:** the **hero call is `te-en` Telugu-English** and is one of the 2 fixed labels — so Telugu IS represented
  in the slice even with no Telugu dataset.

### Ruling: **Option A** (Codex). Do NOT introduce medical Telugu data this sprint.
**Chosen slice (40):** 2 existing fixed first (`bolna` hi-en + `hero` te-en) + **24 distinct Hindi-English** (Code-Mixed-Dialog,
each ≤20 utterance turns, no parallel-dialogue duplicates) + **14 short, diverse SpokenWOZ English controls**. Telugu stays honestly
represented by the **`te-en` hero call** already in the slice — no medical-domain or licensing complexity added.
- _(B) rejected:_ 8 Telugu-English medical (CC BY-NC) — real Tenglish but wrong domain + NC license + a 3rd source. Not pursued.

## Disclosure — why the sample changed after 2 labels
The pool change is a **usability + language-coverage correction made BEFORE any judge exposure**, not outcome-based tuning:
Spike hit a 40-turn monolingual-English call at position 3 and stopped; the 44 SpokenWOZ calls are long (turn median ≈36) and
all English, which is hard to label and off-thesis. The judge has **not** run on any real call (quarantine still active), the 2
existing labels are frozen byte-for-byte, and the new calls are selected by length/language only — never by their outcomes.

## Nullable-timing contract — BUILT + TESTED (Codex blocker 3)
`call_log` previously **required integer `start_ms`** per turn, so a text-only source could not be ingested without faking
timestamps. Designed, implemented, and tested a nullable-timing contract — **no synthetic timestamps anywhere**:
- **schema (`pipeline/schemas.py`):** turn `start_ms` → `["integer","null"]`; `stress_profile` enum += `unmeasured`; `source`
  enum += `code_mixed_dialog`; cost `duration_s` → `["number","null"]`. `call_record` inherits these (it reuses `CALL_LOG`
  properties + `_embed(COST)`). Added a self-test: a null-timing record validates; a non-int `start_ms` is rejected.
- **`signals.py`:** `turn_metrics` drops turns with no `start_ms` before sorting → an all-untimed call yields **no** FTO events,
  **no** barge-ins, latency `None`/0, **no** fabricated timing failures.
- **`score.py`:** `barge_in` + `latency_gap` dims are emitted **only when timing is observed**; text-only calls carry **only**
  `task_completion`, and `overall` re-normalizes over the present dims (never a fake perfect-1.0 timing score). `cost.duration_s`
  is `null` when there is no clock (cost itself stays turn-count based).
- **all-or-none invariant (Codex blocker 1 — false-adjacency fix):** a call is **all-timed** or **all-null**, never mixed.
  `signals.timing_mode()` is the single source; `turn_metrics` computes events **only** for a fully-timed call (no more
  filter-then-join, which had manufactured a fake `t1→t3` gap across an untimed `t2`); `score.py` grants timing dims only when
  `timing_mode == "timed"`; `normalize.validate_call` **rejects mixed timing** and couples all-null ⇔ `stress_profile: unmeasured`.
- **boundary (Codex blocker 2):** `normalize.validate_call` now accepts complete-timing AND all-null calls (so the adapter can use
  the repo's existing validator) and enforces the invariant above.
- **human-readable docs (Codex blocker 3):** `schemas/call_log.md` (source/profile/nullable `start_ms` + all-or-none note) and
  `schemas/cost.md` (`duration_s` int|null) updated.
- **coverage-aware analytics + chart (Codex blocker 4):** `out/analytics.json` adds `timing_coverage {timed, unmeasured}` and
  computes `avg_overall` over **timed calls only** (timed = 3 dims vs unmeasured = task_completion only — never blended). `chart.py`
  is null-safe (an unmeasured profile with 0 successes → `cost_per_successful_call: null` → 0-height bar + "n/a" label, axis ignores
  null) and refactored to be importable/testable.
- **tests:** `pipeline/test_nullable_timing.py` (committed) — untimed→`{task_completion}` only/null duration/no failures; timed→all
  3 dims + duration; **mixed→classified mixed, no events, rejected at the boundary**; profile coupling enforced; coverage-aware
  analytics; chart null-cost render. All pass. **Existing 46 `out/calls.json` BYTE-IDENTICAL** (hash `9e68bab5…`), chart PNG
  byte-identical, `out/analytics.json` changes only by the additive `timing_coverage` field — the real pool is provably untouched.

## Honest-normalization notes (for the LATER ingest phase, not done now)
- Code-Mixed-Dialog is **text-only, no timestamps** → on ingest: `timing_observed: false` (metadata), `stress_profile: unmeasured`,
  `start_ms/end_ms: null` per turn; timing/overlap dimensions **omitted by the contract above** (never fabricate ms spacing). Parse
  only real user↔system exchange lines (TAB-separated); skip `api_call`/`R_` KB lines.
- **Outcome derivation:** DSTC2 has `api_call`/KB structure but this repo ships no explicit per-dialogue success label → outcomes
  would be the same documented HEURISTIC as SpokenWOZ (api_call resolved + requested slots provided). Must be labeled HEURISTIC; do
  not invent gold outcomes.
- Provenance per ingested call: original dialogue id, language, repo+commit `9df1d4dc`, license Apache-2.0, selection rule,
  `timing_observed:false`, status=translated.

## Commands run (audit)
- `gh api repos/sumanbanerjee1/Code-Mixed-Dialog …` → license Apache-2.0, branch master, commit `9df1d4dc800548a883f8bc1a9ce4116c77aebc02` (2018-06-20), data dirs = bengali/english/gujarati/hindi/tamil (NO telugu).
- `WebFetch arxiv 1806.05997` → COLING 2018, Banerjee/Moghe/Arora/Khapra; langs Hi/Bn/Gu/Ta-En (no Telugu); DSTC2 restaurant; translated; arXiv badge CC BY 4.0.
- range-fetch + parse of `data/hindi/dialog-dstc2-dev.txt` (500 dialogues) → **utterance-turn** distribution median 15 / p90 21 /
  max 35 (matches Codex; my first pass counted exchanges = median 8, ~2× undercount); 423+ dialogues ≤20 turns.
- parallel agent → Telugu-English hunt (no suitable restaurant/service Telugu TOD found; only medical CC BY-NC).
- nullable-timing contract: edited `schemas.py`/`signals.py`/`score.py` + new `pipeline/test_nullable_timing.py`; ran
  `schemas.py` (9 schemas, pool 46/46 valid, self-tests pass) + the contract test (PASS) + `score.py` (out/ byte-identical, hash `9e68bab5…`).

## Phase B — BUILT (awaiting audit; booth NOT restarted)
- **Source cached** at the pinned commit: `data/code_mixed_dialog/dialog-dstc2-dev.txt` (+ `SOURCE.json` provenance). Apache-2.0
  permits redistribution; committed for reproducible + offline ingest.
- **`pipeline/ingest_cmd.py`** → **24** `cmd_hi_*` call_logs in `data/normalized/`. Parses bAbI: keeps only real user/agent
  natural-language utterances (skips `<SILENCE>`, `api_call` actions, and `R_` KB rows), merges consecutive same-speaker turns,
  filters **4 ≤ utterance-turns ≤ 20** (selected span **7–17**, median 11), dedups by transcript, deterministic file-order.
  Every turn `start_ms`/`end_ms` **null**, `stress_profile: unmeasured`, `source: code_mixed_dialog`, `language: hi-en`,
  `workflow_type: restaurant_reservation`; full provenance (repo, commit `9df1d4dc`, split, dialog index, license, translated).
  **Each call is `validate_call()`'d before writing** (Codex warning).
- **Heuristic outcome:** added `restaurant_reservation` to `score.py` `WORKFLOW_FIELDS` (cuisine/area/price/contact facets) — a
  coarse, documented heuristic over the negotiated search; affects ONLY the new calls (20/24 task_completed). Existing 46 unchanged.
- **`pipeline/build_manifest.py`** → **`eval/label_manifest.json`** (immutable, idempotent): 40 calls = 2 frozen
  (`bolna_246cd9f3`, `hero_001`) + 24 `cmd_hi_*` + 14 shortest `swz_*` controls (turns 20–32). Asserts no dup / all present.
- **Booth wired:** `serve.py label_order()` now reads the manifest and **fails loudly on duplicate or missing call**; serves in
  manifest order; resumes at the first unlabeled = **ref 2 = `cmd_hi_0000`** (short, Hinglish); UI shows "Call N of 40". Blind-strip
  intact (no call_id/source/stress_profile/score leaves the server).

**Verification:** pool 70/70 valid against the timing invariant; existing 46 per-call outputs **byte-identical**; `out/analytics.json`
`timing_coverage {timed:46, unmeasured:24}`; nullable-timing suite PASS; manifest idempotent; dup/missing rejected; CSV SHA `e6d2055…`
frozen; 44 `swz_*` intact (none deleted). No judge calls. (Source fetch = one cached GitHub-raw text pull at the pinned SHA — not audio,
not a provider/judge API.)

**⚠️ For the audit — slack flag:** the slice is exactly 40 and the calibration floor is **≥40 binary** (unsure excluded), so any
`unsure` drops below 40. Two options: (a) accept tight (label all 40, minimal unsure); (b) bump controls to 20 → **46** total for a
6-label buffer (one-line change: `N_CONTROLS=20`). Recommend (b); deferring to your ruling rather than silently changing the composition.

## Next step
**STOP for Codex audit** of the new pool + manifest. On clear (and the slack ruling): restart the booth for blind labeling. No
booth restart until then.
