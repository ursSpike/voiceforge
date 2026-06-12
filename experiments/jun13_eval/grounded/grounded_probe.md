# Grounded Outcome Probe — investigation report (jun13_eval, Agent 2)

**Scope.** ISOLATED investigation. Reads the repo read-only; writes only under
`experiments/jun13_eval/grounded/`. Proposes an **additive** `outcome_evidence` contract; does
**not** touch the production `outcome` field. No git, no network, no installs — only on-disk cache.

**The problem being probed.** Production `task_completion` is a keyword HEURISTIC
(`pipeline/score.py:build_outcome`): a required field is "captured" if its goal value (or a slot
keyword) appears *anywhere in the dialogue text*, and the call is "completed" if `>=70%` of fields
are captured. On the 46-call label slice this agrees with human binary labels on only **25/45**
(55.6%) — a metric trap: it scores text overlap, not whether the task was actually accomplished in
the backend.

**The idea.** Both public dataset families ship *ground truth that the agent does not see*:
SpokenWOZ carries a per-turn belief state + dialog acts + booking state; Code-Mixed-Dialog carries
the hidden backend trace (`api_call`, `R_<slot>` KB rows, `api_call no result`). We can read THAT,
not the spoken text, to decide whether constraints reached the backend, whether the surfaced entity
is real and consistent, whether requested info was actually delivered, and whether bookings closed.

---

## 1. Parse coverage (the STOP gate)

Coverage = fraction of *applicable* public manifest calls for which each grounded signal is
computable from the source. Two signals are **conditional** (apply only to a subset) — a
non-applicable call correctly returns `unknown` and is excluded from that signal's denominator (it
is not a parse gap). STOP-flag fires if applicable coverage `< 0.80`.

| Signal | Family | Computable / Applicable | Coverage | Note |
|---|---|---|---|---|
| constraint_supplied | swz | 14/14 | 1.00 | |
| constraint_preserved_frac | swz | 14/14 | 1.00 | final belief-state lookup |
| reqt_supplied_frac | swz | 12/14 | 0.857 | 2 calls have no `reqt` slots → n/a |
| booking_confirmed | swz | 9/9 | 1.00 | conditional (booking-required calls) |
| terminal_resolution | swz | 14/14 | 1.00 | |
| constraints_in_api_call_frac | cmd | 28/30 | 0.933 | 2 calls name no facet value |
| entity_voiced | cmd | 26/30 | 0.867 | 4 calls return no KB entity |
| info_requests_frac | cmd | 27/30 | 0.90 | 3 calls make no info request |
| no_result_recovered | cmd | 14/14 | 1.00 | conditional (KB-miss calls) |
| agent_contradicts_backend | cmd | 30/30 | 1.00 | |

**STOP-conditions hit: NONE.** Every source-grounded rule clears the 0.80 applicable-coverage bar.
No experiment silently drops a call — calls that cannot be grounded are surfaced explicitly as
`unknown` (Section 5).

---

## 2. Agreement vs human labels

Binary human labels only (`success`/`fail`); the one `unsure` (swz_MUL0815) is excluded; grounded
`unknown` is **excluded from the denominator** (the probe abstains rather than guess).

| Contract | Agreement | Rate | Coverage of binary set |
|---|---|---|---|
| **Keyword heuristic** (production, full 45-binary) | **25 / 45** | 55.6% | decides all 45 (incl. 2 non-public it cannot truly ground) |
| **Keyword heuristic** (public 43-binary, like-for-like) | 23 / 43 | 53.5% | |
| **Grounded probe** (public, unknown excluded) | **33 / 41** | **80.5%** | abstains on 4; decides 41 |

The grounded probe lifts agreement from **~56% to ~81%** on the cases it is willing to decide, and
honestly abstains on the 4 it cannot ground — versus the keyword heuristic, which confidently
mislabels several of those same calls.

---

## 3. Where they disagree — and who is right

The disagreements are the payload: most expose the keyword metric trap, and a handful expose
*human* over-generosity on calls that look smooth but failed in the backend.

**Grounded corrects the keyword heuristic (keyword wrong, grounded matches human):** the keyword
rule fires `fail` on long, successful SpokenWOZ calls merely because a goal value never appears
verbatim in the noisy ASR transcript — e.g. `swz_MUL2483/2658/0211/1685/1560/1004/0271` (human
success, keyword fail, grounded success via preserved belief state + supplied reqt + confirmed
booking). It also fires `success` on shallow CMD calls — see §4 worked examples.

**Grounded contradicts BOTH keyword and human — and the source backs grounded:**
- `cmd_hi_0025` (human success, keyword success, **grounded fail**): KB row says
  `nandos R_location centre`, but the agent says it is in the *south* (the user's requested area).
  A factual contradiction against the backend that both the keyword rule and the human missed.
- `cmd_hi_0007` (human success, keyword fail, **grounded fail**): after `api_call no result`, the
  agent voices a restaurant "ask" that has **no KB row at all** — a hallucinated recommendation.
- `swz_MUL0280 / swz_MUL1552` (human success, **grounded fail**): the goal requires a booking, but
  the trace shows only `booking-request` (the agent asking for details) — the reservation never
  actually closes. Smooth conversation, unfinished task.
- `swz_MUL0035` (human success, **grounded fail**): the agent never emits an `*-inform` act for the
  one `reqt` slot (attraction `postcode`) the user asked for — requested info never delivered.

These four are exactly the "looks fine, isn't done" cases a grounded contract is built to catch.

**Grounded over-credits a few (grounded success, human fail):** `cmd_hi_0001/0004/0015` — the
backend recovered an on-constraint entity and voiced the requested info, so the *task* grounding
succeeds, but the human penalized friction (the user had to re-ask / a first search missed). This
is the legitimate boundary between **task grounding** (what this probe measures) and **experience
quality** (what the judge dims `repair_quality`/`user_frustration` are for). The grounded contract
should be read as the task spine, not the whole verdict.

Full 46-row table: `_disagreement_table.md` (machine-source: `grounded_probe.json`).

---

## 4. Ten manually-inspectable worked examples

Each = call_id · raw evidence · grounded verdict · human label. Verify against the raw sources
(`data/spokenwoz/data.json` and `data/code_mixed_dialog/dialog-dstc2-dev.txt`).

1. **cmd_hi_0007** — human=success, keyword=fail, **grounded=FAIL**.
   Trace: `api_call R_cuisine R_location R_price` → `api_call no result`; **zero `R_` KB rows**; the
   agent then voices entity "ask" / "ask_address". *Grounded:* hallucinated entity after a KB miss,
   no real recovery → fail. **High-value catch.**

2. **cmd_hi_0025** — human=success, keyword=success, **grounded=FAIL**.
   KB: `nandos R_location centre`. Agent: "nandos … nagar ke **south** bhaag mein". User asked for
   south. *Grounded:* agent claim contradicts the KB location → fail. **Catches a hallucination
   both others missed.**

3. **cmd_hi_0001** — human=fail, keyword=success, **grounded=SUCCESS**.
   First `api_call lebanese west` → no result; user pivots to thai; `api_call thai west` returns
   `sala_thong` (west, expensive); agent voices it + phone + address. *Grounded:* recovered, on
   constraint, info supplied → task succeeded (human penalized the retry friction).

4. **cmd_hi_0000** — human=fail, keyword=success, **grounded=UNKNOWN**.
   Trace has **no `api_call` and no KB rows** — the agent answered entirely from memory. Nothing in
   the backend to ground. *Grounded:* abstains (vs keyword's false `success`). Honest `unknown`.

5. **cmd_hi_0014** — human=success, keyword=success, **grounded=SUCCESS**.
   KB returns 4 entities; agent voices `peking_restaurant` (south, chinese) consistently. *Grounded:*
   correct only because the probe scopes the contradiction check to the **voiced** entity, not the
   first KB row (see §6 — this was a bug fixed mid-investigation).

6. **cmd_hi_0003** — human=success, keyword=success, **grounded=SUCCESS**.
   `api_call cantonese expensive` → no result → pivot `north_american` → entity found, phone +
   postcode voiced. Clean multi-step recovery.

7. **swz_MUL2483** — human=success, keyword=fail, **grounded=SUCCESS**.
   goal.book = hotel+restaurant. Trace: `restaurant-ack [bookpeople 8, booktime 12:45, bookday
   tuesday]` + "that [booking] has been secured". *Grounded:* booking confirmed via `*-ack` payload
   (keyword failed on ASR-garbled text).

8. **swz_MUL0280** — human=success, keyword=fail, **grounded=FAIL**.
   goal.book = restaurant. Trace shows only `booking-request [bookday ?]` — agent asks, never
   confirms; no `booked` payload anywhere. *Grounded:* required booking never closed → fail.

9. **swz_MUL0035** — human=success, keyword=fail, **grounded=FAIL**.
   goal.reqt = attraction `postcode`. No `attraction-inform[post]` act in any system turn; constraints
   ARE preserved (cp_frac 1.0) and booking IS confirmed, but the one requested fact was never
   delivered. *Grounded:* requested info never supplied → fail.

10. **swz_MUL0069** — human=success, keyword=success, **grounded=SUCCESS**.
    Constraints preserved in final belief (cp_frac 1.0), reqt informed, hotel booking confirmed,
    clean `general-bye` close. All three contracts agree — the unambiguous-success control.

---

## 5. Cases that MUST stay `unknown` (never guessed)

4 of the 46 calls; the probe abstains rather than fabricate a verdict:

| call_id | why unknown |
|---|---|
| `bolna_246cd9f3` | **non-public** (frozen Bolna execution) — no source ground-truth dataset to read. |
| `hero_001` | **non-public** (constructed hero timeline) — no source ground truth. |
| `cmd_hi_0000` | Backend trace has **no `api_call` and no KB rows** — agent answered from memory; nothing groundable. |
| `cmd_hi_0024` | Partial grounding only — an entity/miss exists but signals are insufficient to assert success or fail. |

These are a feature: an inspectable outcome contract should say "I cannot tell from the source"
instead of guessing. The keyword heuristic, by contrast, emits a confident `success` for all four.

---

## 6. Honesty notes / limitations

- **A real bug was found and fixed mid-investigation.** The first contradiction check compared the
  agent's spoken facets against the *first* KB row, but DSTC2 `api_call`s return many candidates and
  the agent picks one. That produced 6 false-positive `fail`s (cmd_hi_0012/0014/0016 etc.). Fix:
  identify the **voiced** entity (delex token in a system turn) and check consistency against *that*
  entity's KB row. Agreement went 22/37 → 30/41. Then broadening booking-confirmation to accept an
  `*-ack` carrying `book*` slots (swz_MUL2483) took it to **33/41**.
- **Conditional signals are not parse gaps.** `booking_confirmed` (9/9) and `no_result_recovered`
  (14/14) have perfect coverage *where applicable*; their low unconditional coverage just reflects
  that most calls neither book nor hit a KB miss. Reported as applicable coverage to avoid a false
  STOP-flag.
- **Task grounding ≠ experience quality.** The probe measures whether the *task* closed against the
  backend, not whether the caller was happy. The grounded-success / human-fail cases
  (cmd_hi_0001/0004/0015) are the seam — keep this contract additive and pair it with the judge's
  `repair_quality`/`user_frustration`.
- This is a prototype on a 44-call public slice, not a production replacement.

## Files

- `grounded_probe.py` — runnable prototype (`.venv/bin/python …/grounded_probe.py`).
- `grounded_probe.json` — machine output: per-call evidence, signals, verdicts, coverage, agreement.
- `outcome_evidence.contract.json` — the proposed additive JSON contract + roll-up rules.
- `_disagreement_table.md` — full 46-row keyword vs grounded vs human table.
- `_swz_raw/` — small per-dialogue extracts pulled from the 246MB raw file (cache only).
