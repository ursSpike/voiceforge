# QA Matrix — Demo Clearance Gate

**Owner:** QA-MATRIX agent (plan), executed by coordinator at integration time.
**Status:** PLAN ONLY — no checks executed yet. This document defines the full gate the coordinator runs before declaring "demo-cleared."
**Hard rule:** if `/platform` fails any required check by the QA deadline, the coordinator falls back to `out/dashboard.html` (open-from-disk, no server) and reports the gap. **Never destabilize `/` to chase platform polish.**

---

## 0. Pre-existing Gates (must already pass before this matrix runs)

| Gate | Command | Pass criterion |
|---|---|---|
| Preflight | `python pipeline/preflight.py` | exit 0 |
| Live isolation | `python pipeline/test_live_isolation.py` | 5/5 pass |
| Live ingest self-test | `python pipeline/ingest_live.py --selftest` | exit 0 |
| Live judge self-test | `python pipeline/judge_live.py --selftest` | exit 0 |

If any of the four fails, **QA matrix does not begin** — fix the gate first.

---

## 1. Resolution Matrix

Viewports under test:

| Tag | Width × Height | Reason |
|---|---|---|
| `R1` | 1280 × 720 | Laptop baseline (matches prior measurement bar: 0 overflow, 0 inner clip) |
| `R2` | 1440 × 900 | MacBook 14" / 16" native |
| `R3` | 1920 × 1080 | Projector-realistic / external monitor |
| `R4` | 1366 × 768 | Low-end projector / conference-room TV |

### 1.1 Scene-by-scene vertical fit (`/` presenter)

For **each of the 8 scenes** of `/`, at **each of R1–R4**:

- `scrollHeight <= clientHeight + 1` (allow 1px AA tolerance) — measured per scene container, **not** the page.
- No clipped CTA / no clipped caption / no clipped chart legend.
- Smooth-scroll settle: after `←/→/Home/End`, wait 600ms then re-measure — must still pass.

**Measurement script (DOM):**
```js
[...document.querySelectorAll('[data-scene]')].map(s => ({
  id: s.dataset.scene,
  overflowV: s.scrollHeight - s.clientHeight,
  overflowH: s.scrollWidth - s.clientWidth
}))
```
Pass = every row has `overflowV <= 1 && overflowH === 0`.

### 1.2 `/platform` aggregate + modes

At each of R1–R4:

- Aggregate landing view (no mode filter).
- Frozen mode view.
- Live mode view (empty + populated).
- **Live Clinic Agent** workspace — empty state.
- **Live Clinic Agent** workspace — populated state (one cached fixture call rendered).

Measure: rail width stable, no horizontal scrollbars, drawer/modal fits viewport.

### 1.3 No horizontal scroll, anywhere

```js
document.documentElement.scrollWidth <= window.innerWidth
```
Must hold at every R1–R4 on every route. **Zero exceptions.**

---

## 2. Offline Dependency Audit

### 2.1 Grep the served bundle

```bash
grep -rE 'src="http|href="http|@import url' \
  <served-html-dir> <served-css-dir> <served-js-dir>
```
**Pass = 0 hits.** Allowed exceptions: `<meta>` tags, comments. Anything pulling a remote asset = fail.

### 2.2 WiFi-off network audit

1. Load `/` and `/platform` once with WiFi on, hard-reload, capture network tab.
2. Disable WiFi.
3. Hard-reload `/` — fully renders, all scenes navigable, no broken images, no 404s in console.
4. Hard-reload `/platform` — fully renders, rail, modes, workspace, drawer all functional.

**Pass = both routes 100% functional offline.**

### 2.3 `out/dashboard.html` open-from-disk fallback

Open `out/dashboard.html` directly via `file://` (no server, no build step).
**Pass = renders fully, no console errors, no missing assets.** This is the guaranteed fallback if `/platform` fails.

---

## 3. Provenance Audit

### 3.1 Live Clinic Agent cards

Every card surfaced from the live clinic agent path must carry visible badge text:
```
LIVE · UNCALIBRATED
```
DOM check:
```js
[...document.querySelectorAll('[data-source="live-clinic"]')]
  .every(c => c.textContent.includes('LIVE') && c.textContent.includes('UNCALIBRATED'))
```

### 3.2 Frozen Pilot cards

Every frozen-pilot card must carry:
```
FROZEN · CALIBRATED
```
DOM check (analogous, `data-source="frozen"`).

### 3.3 No mixed aggregates

No KPI / chart / count on any page may sum frozen + live into a single number presented without segmentation. Specifically:
- "Calls today" cannot combine frozen sample + live calls.
- Judge-score aggregates cannot blend frozen-rubric scores with live-uncalibrated scores.
- Phenotype distributions must be labeled FROZEN or LIVE, not merged.

Audit: visually inspect every aggregate widget and confirm a segmentation marker (badge, sub-row, or stacked split) is present.

### 3.4 Cartesia `synthesizer_verified` badge

The badge may render "verified" **only** when the agent-config fetch succeeded for the relevant agent (`out/clinic_agent_created.json` or live fetch returned 200 with synthesizer block present).

DOM check:
```js
[...document.querySelectorAll('[data-synth-verified]')]
  .every(el => el.dataset.synthVerified === 'true'
    ? el.dataset.synthSource === 'agent-config-fetched'
    : true)
```

If unverified, badge must show neutral or "unverified" state — **never** "verified."

### 3.5 Calibration caption truth-pass

The calibration caption must NOT contain the truth-violation phrase. Confirm the corrected wording is present and the old phrase is absent (see Honesty Audit §4).

---

## 4. Honesty Audit (forbidden-phrase grep)

Forbidden phrases — **must return 0 hits** across every served HTML / CSS / JS / inline data:

| # | Forbidden phrase | Why |
|---|---|---|
| F1 | `measured savings` | We did not measure dollar savings end-to-end |
| F2 | `least reliable exactly there` | Truth-corrected; old caption removed |
| F3 | `live barge-in` | Barge-in is frozen-only / unverified live |
| F4 | `calibrated live` | Live is uncalibrated by definition |
| F5 | `76 provider calls` | Frozen sample is calls, not "provider calls" framing |
| F6 | `every transcript is real` | Includes synthetic frozen transcripts |

**Grep command:**
```bash
for p in "measured savings" "least reliable exactly there" "live barge-in" \
         "calibrated live" "76 provider calls" "every transcript is real"; do
  hits=$(grep -rciE "$p" <served-bundle-dir> | grep -v ':0$' | wc -l)
  echo "$p : $hits files with hits"
done
```
**Pass = all 6 report 0 files with hits.**

---

## 5. Isolation Audit

### 5.1 Test passes

```bash
python pipeline/test_live_isolation.py
```
**Pass = 5/5.**

### 5.2 Frozen artifact byte-identity

Before/after any new integration commit, the SHA-256 of each frozen artifact MUST be unchanged. Reference hashes (truncated to 8 chars for readability — full hash must match):

| Artifact | SHA-256 prefix |
|---|---|
| CSV (frozen sample) | `b3884f9e…` |
| Judge output | `7b76ba48…` |
| Calls JSON | `444956c8…` |
| Analytics JSON | `3edc2acd…` |
| Snapshot | `d592782a…` |
| `demo_report_data` | `7612546f…` |
| Rubric | `c1cc8141…` |
| Manifest | `aec4ba49…` |

**Verification:**
```bash
shasum -a 256 <each-frozen-path> | cut -c1-8
```
**Pass = every prefix matches reference, byte-for-byte.** Any drift = isolation breach, demo blocked until resolved.

---

## 6. Functional Matrix

### 6.1 `/` (presenter, 8 scenes)

| # | Check | How to measure | Pass |
|---|---|---|---|
| P1 | `→` advances scene by 1, settles | dispatch keydown, wait 600ms, read active scene index | index += 1 |
| P2 | `←` retreats scene by 1, settles | same | index -= 1 |
| P3 | `Home` returns to scene 0 | same | index === 0 |
| P4 | `End` jumps to last scene | same | index === N-1 |
| P5 | Drawer opens within viewport | open drawer; `getBoundingClientRect()` of drawer fully inside viewport | top>=0, bottom<=innerHeight |
| P6 | `Esc` closes drawer | dispatch keydown Esc | drawer not in DOM / aria-hidden |
| P7 | Corpus overlay = 76 rows | open corpus; count rows | `rows.length === 76` |
| P8 | No inline corpus in any scene | scan each scene for corpus table | 0 found in scenes; only in overlay |
| P9 | No console errors | listen during nav of all 8 scenes | `console.error` count === 0 |

### 6.2 `/platform` (operator)

| # | Check | How to measure | Pass |
|---|---|---|---|
| O1 | Rail search filters | type query; row count drops monotonically | filtered count < total |
| O2 | Mode switch Frozen → Live | click toggle | view shows only `data-source="live"` |
| O3 | Mode switch Live → Live-Clinic | click toggle | view shows only `data-source="live-clinic"` |
| O4 | Mode switch back to Frozen | click toggle | view shows only `data-source="frozen"` |
| O5 | Empty-live banner at top when live=0 | clear live; check first child of live panel | banner present |
| O6 | Individual call view — transcript | open a frozen call | transcript block rendered |
| O7 | Individual call view — cited turns | same | citation markers visible |
| O8 | Individual call view — signals | same | signals panel rendered |
| O9 | Individual call view — judge evidence | same | judge evidence rendered |
| O10 | Individual call view — phenotype | same | phenotype label visible |
| O11 | Individual call view — recommendation | same | recommendation text present |
| O12 | Individual call view — extracted_data (when present) | open a call with extracted_data | extracted fields rendered |
| O13 | No console errors during full sweep | listen during 30s click-through | `console.error` count === 0 |

---

## 7. Live Data Dry-Run (gates final clearance)

This section runs **only** when first real live execution arrives. It is the final gate.

| # | Check | Pass |
|---|---|---|
| L1 | One cached-fixture live call renders in Live Clinic Agent workspace | call card visible |
| L2 | `extracted_data` populates patient fields (name/age/symptom/etc. per schema) | fields populated, no `null`/`undefined` displayed |
| L3 | Every live element carries `LIVE · UNCALIBRATED` | §3.1 DOM check passes |
| L4 | Live call appears in Live Today (or per-spec destination) | exactly one new row |
| L5 | No double-counting in aggregates | aggregate count delta = +1 in Live, +0 in Frozen, +0 in combined-blended |
| L6 | Judge runs against live call without crashing | `judge_live.py` exit 0 on the new call |
| L7 | Isolation re-check after live ingest | §5.2 hashes still byte-identical |

**Pass = all 7 green.** Any red = clearance withheld.

---

## 8. Pass/Fail Matrix (single table)

Rows = checks. Columns = R1 / R2 / R3 / R4 (where resolution applies) or N/A (where it doesn't). Pass criterion + measurement method per row.

| ID | Check | R1 1280×720 | R2 1440×900 | R3 1920×1080 | R4 1366×768 | Pass criterion | Method |
|---|---|---|---|---|---|---|---|
| V1.1 | `/` scenes vertical fit (per scene) | ☐ | ☐ | ☐ | ☐ | `scrollHeight - clientHeight <= 1` | DOM script §1.1 |
| V1.2 | `/` no horizontal overflow (per scene) | ☐ | ☐ | ☐ | ☐ | `scrollWidth - clientWidth === 0` | DOM script §1.1 |
| V1.3 | `/platform` aggregate fit | ☐ | ☐ | ☐ | ☐ | no scrollbar, no clipped controls | visual + §1.3 |
| V1.4 | `/platform` Frozen mode fit | ☐ | ☐ | ☐ | ☐ | same | same |
| V1.5 | `/platform` Live mode fit | ☐ | ☐ | ☐ | ☐ | same | same |
| V1.6 | `/platform` Live-Clinic empty fit | ☐ | ☐ | ☐ | ☐ | same | same |
| V1.7 | `/platform` Live-Clinic populated fit | ☐ | ☐ | ☐ | ☐ | same | same |
| V1.8 | Page-level no horizontal scroll | ☐ | ☐ | ☐ | ☐ | `documentElement.scrollWidth <= innerWidth` | §1.3 |
| O2.1 | Grep external `src=http` / `href=http` / `@import url` = 0 | N/A | N/A | N/A | N/A | 0 hits | §2.1 grep |
| O2.2 | WiFi-off `/` loads fully | N/A | N/A | N/A | N/A | renders + navigable | §2.2 |
| O2.3 | WiFi-off `/platform` loads fully | N/A | N/A | N/A | N/A | renders + functional | §2.2 |
| O2.4 | `out/dashboard.html` opens from disk | N/A | N/A | N/A | N/A | renders, no errors | §2.3 |
| P3.1 | Live cards carry `LIVE · UNCALIBRATED` | N/A | N/A | N/A | N/A | every card | §3.1 DOM |
| P3.2 | Frozen cards carry `FROZEN · CALIBRATED` | N/A | N/A | N/A | N/A | every card | §3.2 DOM |
| P3.3 | No mixed aggregates | N/A | N/A | N/A | N/A | every aggregate segmented | §3.3 visual |
| P3.4 | Cartesia `synthesizer_verified` truthful | N/A | N/A | N/A | N/A | verified only when fetched | §3.4 DOM |
| P3.5 | Calibration caption truth-corrected | N/A | N/A | N/A | N/A | old phrase absent | §3.5 + §4 |
| H4.1 | Forbidden phrase F1 (`measured savings`) | N/A | N/A | N/A | N/A | 0 hits | §4 grep |
| H4.2 | Forbidden phrase F2 (`least reliable exactly there`) | N/A | N/A | N/A | N/A | 0 hits | §4 grep |
| H4.3 | Forbidden phrase F3 (`live barge-in`) | N/A | N/A | N/A | N/A | 0 hits | §4 grep |
| H4.4 | Forbidden phrase F4 (`calibrated live`) | N/A | N/A | N/A | N/A | 0 hits | §4 grep |
| H4.5 | Forbidden phrase F5 (`76 provider calls`) | N/A | N/A | N/A | N/A | 0 hits | §4 grep |
| H4.6 | Forbidden phrase F6 (`every transcript is real`) | N/A | N/A | N/A | N/A | 0 hits | §4 grep |
| I5.1 | `test_live_isolation.py` 5/5 | N/A | N/A | N/A | N/A | exit 0, 5 passes | §5.1 |
| I5.2 | Frozen CSV SHA = `b3884f9e…` | N/A | N/A | N/A | N/A | match | §5.2 shasum |
| I5.3 | Judge SHA = `7b76ba48…` | N/A | N/A | N/A | N/A | match | §5.2 shasum |
| I5.4 | Calls SHA = `444956c8…` | N/A | N/A | N/A | N/A | match | §5.2 shasum |
| I5.5 | Analytics SHA = `3edc2acd…` | N/A | N/A | N/A | N/A | match | §5.2 shasum |
| I5.6 | Snapshot SHA = `d592782a…` | N/A | N/A | N/A | N/A | match | §5.2 shasum |
| I5.7 | `demo_report_data` SHA = `7612546f…` | N/A | N/A | N/A | N/A | match | §5.2 shasum |
| I5.8 | Rubric SHA = `c1cc8141…` | N/A | N/A | N/A | N/A | match | §5.2 shasum |
| I5.9 | Manifest SHA = `aec4ba49…` | N/A | N/A | N/A | N/A | match | §5.2 shasum |
| F6.P1 | `→` advances scene | N/A | N/A | N/A | N/A | index += 1 | §6.1 |
| F6.P2 | `←` retreats scene | N/A | N/A | N/A | N/A | index -= 1 | §6.1 |
| F6.P3 | `Home` returns to scene 0 | N/A | N/A | N/A | N/A | index === 0 | §6.1 |
| F6.P4 | `End` jumps to last scene | N/A | N/A | N/A | N/A | index === N-1 | §6.1 |
| F6.P5 | Drawer opens in viewport | ☐ | ☐ | ☐ | ☐ | rect inside viewport | §6.1 |
| F6.P6 | `Esc` closes drawer | N/A | N/A | N/A | N/A | drawer gone | §6.1 |
| F6.P7 | Corpus overlay = 76 rows | N/A | N/A | N/A | N/A | count === 76 | §6.1 |
| F6.P8 | No inline corpus in scenes | N/A | N/A | N/A | N/A | 0 inline | §6.1 |
| F6.P9 | No console errors on `/` | N/A | N/A | N/A | N/A | 0 errors | §6.1 |
| F6.O1 | Rail search filters | N/A | N/A | N/A | N/A | filtered < total | §6.2 |
| F6.O2 | Mode switch Frozen → Live | N/A | N/A | N/A | N/A | view filters correctly | §6.2 |
| F6.O3 | Mode switch Live → Live-Clinic | N/A | N/A | N/A | N/A | view filters correctly | §6.2 |
| F6.O4 | Mode switch back to Frozen | N/A | N/A | N/A | N/A | view filters correctly | §6.2 |
| F6.O5 | Empty-live banner at top | N/A | N/A | N/A | N/A | banner present | §6.2 |
| F6.O6 | Call view — transcript | N/A | N/A | N/A | N/A | rendered | §6.2 |
| F6.O7 | Call view — cited turns | N/A | N/A | N/A | N/A | citation markers | §6.2 |
| F6.O8 | Call view — signals | N/A | N/A | N/A | N/A | signals rendered | §6.2 |
| F6.O9 | Call view — judge evidence | N/A | N/A | N/A | N/A | evidence rendered | §6.2 |
| F6.O10 | Call view — phenotype | N/A | N/A | N/A | N/A | label visible | §6.2 |
| F6.O11 | Call view — recommendation | N/A | N/A | N/A | N/A | text present | §6.2 |
| F6.O12 | Call view — extracted_data | N/A | N/A | N/A | N/A | fields rendered | §6.2 |
| F6.O13 | No console errors on `/platform` | N/A | N/A | N/A | N/A | 0 errors | §6.2 |
| L7.1 | Live fixture call renders | N/A | N/A | N/A | N/A | card visible | §7 |
| L7.2 | `extracted_data` populates fields | N/A | N/A | N/A | N/A | fields populated | §7 |
| L7.3 | LIVE · UNCALIBRATED badges everywhere | N/A | N/A | N/A | N/A | every live el | §7 + §3.1 |
| L7.4 | Live call appears in Live Today | N/A | N/A | N/A | N/A | +1 row | §7 |
| L7.5 | No double-counting in aggregates | N/A | N/A | N/A | N/A | deltas correct | §7 |
| L7.6 | Judge runs on live call | N/A | N/A | N/A | N/A | exit 0 | §7 |
| L7.7 | Isolation hashes still match after live ingest | N/A | N/A | N/A | N/A | byte-identical | §5.2 |

**Total checks: 60.**

Resolution-dependent checks (8 rows × 4 resolutions = 32 cells) live in V1.1–V1.8 + F6.P5. Non-resolution-dependent checks fire once.

---

## 9. Hard Stop / Fallback Policy

1. If **any V1.x** fails at any resolution on `/platform`: try one polish pass. If still failing at QA deadline → coordinator switches the live demo target to `out/dashboard.html` (open-from-disk) and reports `/platform` gap in the demo notes.
2. If **any V1.x** fails on `/`: **do not ship.** `/` is the presenter spine. Halt, fix, re-run §1.1. Do not paper over with `/platform` work.
3. If **any I5.x** (isolation hash) fails: **demo blocked** until the offending live-path code is reverted or sandboxed. Frozen artifacts are inviolable.
4. If **any H4.x** (forbidden phrase) fails: replace the wording before demo. Honesty audit is non-negotiable.
5. If **any P3.x** (provenance) fails: relabel before demo. Mixed provenance > zero demo.

**Never destabilize `/` to chase `/platform` polish.** `/` ships, `/platform` is a bonus surface.

---

## 10. Execution Order (when coordinator runs this)

1. Run pre-existing gates (§0). Stop if any fail.
2. Run isolation hashes (§5). Stop if any drift.
3. Run forbidden-phrase grep (§4). Fix any hit before continuing.
4. Run offline-dependency grep + WiFi-off test (§2).
5. Spin up `/` on R1; walk V1.1, V1.2, F6.P1–P9. Repeat R2, R3, R4.
6. Spin up `/platform` on R1; walk V1.3–V1.7, F6.O1–O13. Repeat R2, R3, R4.
7. Run provenance audit (§3) at any resolution (DOM checks are resolution-independent).
8. If first live call available: run §7. Re-run §5.2 immediately after.
9. Fill in §8 matrix. All ☐ → ✓ or ✗ with note.
10. Sign-off only when every required cell is ✓ (or fallback per §9 invoked).

---

**End of plan. No checks have been executed by this document — it defines the gate the coordinator runs when integration time arrives.**
