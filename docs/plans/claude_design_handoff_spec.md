# Claude-Design Handoff Spec — Round 3 (clinic pivot)

**Status:** plan only. Nothing in this document modifies source, runtime, Bolna,
or design assets. It defines the contract for a single-shot Round-3 handoff to
the Claude-Design agent, after rounds 1 and 2 drifted because the DOM/data
contract was assumed rather than pasted in full.

**Read pairing:**
- `voiceforge_design/{index.html, app.js, styles.css}` — current presenter source (228 CSS classes).
- `out/platform/{index.html, app.js, styles.css}` — current Live Clinic Agent / operator workspace source (82 CSS classes).
- `pipeline/build_surface.py` — generates `out/surface/design_data.js` from real artifacts (76 calls, full transcripts).
- `pipeline/build_platform.py` — generates `out/platform/platform_data.js` from `design_data.js` + `demo_report_data.json` + optional `out/live_calls.json`.
- `voiceforge_design/INTEGRATION_MAP.md`, `voiceforge_design/DESIGN_RATIONALE.md` — prior rationale.

---

## 1. Scope — what we are asking Claude-Design to refine

Three candidate scopes were considered:

| Option | Surface | State |
|---|---|---|
| A | Presenter `/` only (`voiceforge_design/`) | Already passed measured QA at 1280×720 / 1440×900 / 1920×1080 in round 2. 8 scenes, each ≤1 viewport, drawer hardened. |
| B | `/platform` Live Clinic Agent only (`out/platform/`) | New surface from the clinic pivot. Has not had a design pass. Will carry real clinic-agent live calls. |
| C | Both, single prompt | Doubles DOM contract size (297 unique classes), maximizes drift risk, contradicts round-1/2 lesson. |

**Recommendation: Option B — `/platform` Live Clinic Agent FIRST.** Reasons:

1. `/` already passed measured QA at all three projector resolutions. Re-styling it now risks regressing 8-scene one-viewport invariants for negligible upside.
2. `/platform` is the new clinic surface — it is what the operator sees during a live call and what the post-call review is built around. Visual quality there is load-bearing for the pivot story.
3. The data contract `/platform` styles against (`platform_data.js`) wraps the same real artifacts plus the live slice, so a single design pass covers frozen + live evidence views.
4. Smaller DOM contract (82 vs 228 classes) means the single-shot prompt actually fits and the QA gate is auditable.

Presenter `/` is **out of scope** for Round 3. If a follow-on `/` pass is desired, run it as a separate single-shot with its own contract — never bundle.

---

## 2. DOM contract — paste verbatim into the designer prompt

The lesson from rounds 1 and 2: the designer cannot infer markup. The CSS
contract must be the **complete enumerated list** of every class the design
needs to handle. The designer returns CSS keyed to these classes; any class
that exists in the source but is missing from the returned CSS is a Round-3
failure.

Compiled from `out/platform/index.html` + `out/platform/app.js` selectors, and
cross-referenced against `out/platform/styles.css` for completeness.

### 2.1 Platform DOM contract — 82 classes (the styled set)

Layout & shell:
`.detail`, `.rail-head`, `.rail-list`, `.rail-count`, `.empty-rail`, `.brand`,
`.brand-dot`, `.brand-sub`, `.mode-switch`, `.mode-btn`, `.active`,
`.search`, `.filters`, `.filter-group`, `.pill`, `.pills`, `.section`,
`.view-title`, `.caption`, `.sub`, `.subtitle`, `.banner`, `.placeholder`.

Frozen vs Live mode:
`.live`, `.live-pip`, `.live-empty`, `.live-tag`, `.frozen`, `.cmd-box`,
`.cmd-helper`, `.cmd-note`, `.copy`.

Call rail (left directory):
`.call-card`, `.call-head`, `.id`, `.linkid`, `.cid`, `.tid`, `.meta`,
`.name`, `.num`, `.sel`, `.on`, `.dot`.

Aggregate / cluster views:
`.agg-grid`, `.grid2`, `.cluster-row`, `.coverage`, `.metric`, `.big`,
`.bar`, `.agent`, `.arch`, `.ph`.

Detail / evidence pane:
`.transcript`, `.turn`, `.bubble`, `.who`, `.user`, `.cites`, `.cited`,
`.dscore`, `.dtype`, `.dh`, `.dr`, `.rh`, `.rt`.

Provenance / state chips (semantically distinct — non-negotiable):
`.prov`, `.deterministic`, `.judge`, `.unsure`, `.uncal`, `.unmeasured`,
`.ok`, `.good`, `.bad`, `.warn`, `.ex`, `.rec`, `.chip`.

### 2.2 Presenter DOM contract — 228 classes (reference only, OUT of Round-3 scope)

Already extracted to `/tmp/style_classes.txt` during prep. Not pasted here
because the recommended Round-3 scope is `/platform` only. If a future round
re-touches `/` the full enumeration is committed under
`voiceforge_design/styles.css` and can be reproduced via:

```
grep -oE '\.[a-zA-Z][a-zA-Z0-9_-]+' voiceforge_design/styles.css | sort -u
```

### 2.3 Coverage audit (mandatory)

After the designer returns CSS, run a coverage audit script that:
1. Enumerates every selector in returned CSS.
2. Diffs against the 82-class contract.
3. Lists missing classes (must be 0) and orphan classes (must be 0 unless
   the designer added an intentional new helper class that the spec
   acknowledges).

Round 1 missed 5 classes. Round 2 missed 35 classes. **Round 3 acceptance
threshold: 0 missing.**

---

## 3. Data contract — what the design must render against

### 3.1 Hard rule

**No fixture numbers. No sample-of-5. The design renders against the FULL
real artifact dataset.** Frozen Pilot mode has 76 calls (full transcripts
on the 46-call judged slice; deterministic dims on all 76). Live Today mode
has 0..N real clinic-agent calls — the empty state must work when N=0 and
must NOT degrade to placeholder data.

### 3.2 `window.__PLATFORM__` schema (assembled by `pipeline/build_platform.py`)

Top-level keys (verbatim from `build_platform.py:assemble()`):

```
generated_from        string  ("pipeline/build_platform.py")
data_basis            string  ("frozen pilot: 76 scored calls, 46 timed, 45-call blind-labeled slice")
analytics             object  see 3.2.1
report                object  see 3.2.2
calibration           object  report.calibration (mirror, designer convenience)
metric_trap           object  see 3.2.3
archetypes            object  { counts: {archetype_name: int}, ... }
product               object  fix_first + matrix (see 3.2.4)
improvement_queue     array   per-call recommendations with citations
fix_first             object  product.fix_first lifted to top
privacy_note          string  the artifact-truth disclosure paragraph
sponsor_proof         object  { agent_id, fetched_at, synthesizer_provider, cartesia_voice, cartesia_model }
calls                 array   see 3.2.5  (this is the rendered set)
live                  object  see 3.2.6
```

#### 3.2.1 `analytics`

```
n_calls                       int   (76)
success_rate                  float (0..1, heuristic)
avg_overall                   float (0..1, over TIMED calls only)
timing_coverage               { timed: int, unmeasured: int }
cost_per_successful_call      float (USD, estimated)
by_stress_profile             array of { stress_profile, n, n_completed, cost, success_rate, cost_per_successful_call }
failure_clusters              array of { dimension, count, example_call_ids[] }
note                          string  (provenance caveat — render verbatim)
```

#### 3.2.2 `report`

```
manifest_total                int   (46)
corpus                        { n_scored, timing_coverage, success_rate_heuristic, cost_per_success_est, failure_event_clusters[] }
labels                        { total, binary, unsure, floor, floor_met, distribution: {success, fail, unsure}, ... }
calibration                   {
  kappa: float,
  ci95: [float, float],
  raw_agreement: float,
  balanced_accuracy: 0.628,             # ASSERTED constant — do not let designer alter
  n: int,
  band: string,
  confusion: { tp, fp, tn, fn },
  disagreements: [call_id, ...],
  disagreements_code_switched: [call_id, ...],
  caption: string                       # truth-corrected caption — see invariant 4.7
}
metric_trap                   { n, agree, missed_successes, false_passes, human_failures, caption, provenance }
product                       see 3.2.4
archetypes                    { counts: {...} }
improvement_queue             array (mirrored at top level)
judge_run                     { model, temperature, n_calls, expected_judgments, validated_judgments, failures, cache_hits, hashes, binary_rule }
```

#### 3.2.3 `metric_trap`

```
n               int   (45)
agree           int   (25)
missed_successes int
false_passes    int
human_failures  int
caption         string  (verbatim; do not let designer rephrase)
provenance      string  ("measured" — render with .prov.measured semantics)
```

#### 3.2.4 `product`

```
matrix                          { categories with n, weight, share, unsure_excluded_count }
human_success_rate              float
brittle_share_of_successes      float
cost_per_human_success_est      float
friction_or_failure_spend_share float
caveat                          string
fix_first                       {
  phenotype: string,
  affected_calls: int,
  estimated_spend_usd: float,
  modeled_exposure_per_1k_usd: float,   # render with .prov.estimated semantics + "≈" + italics
  recommendation: string,
  expected_mechanism: string,
  provenance: string,                    # "modeled — not observed savings"
  evidence_call_ids: [call_id, ...]
}
```

#### 3.2.5 `calls[]` — the rendered per-call shape

```
id                  string
source              string  ("spokenwoz" | "code_mixed_dialog" | "hero_constructed" | "bolna_live" | ...)
lang                string
profile             string  (stress_profile: "clean" | "interruption" | "pause_heavy" | "unmeasured")
wf                  string  (workflow_type)
turns               int
outcome             bool    (deterministic task_completed heuristic)
overall             float   (scorecard.overall, 0..1)
in_manifest         bool    (true => in the 46-call blind+judged slice)
archetype           string|null
recommendation      string|null
human               null | { label, confidence, positive[], negative[], context[] }   # null when outside the labeled slice
dims                array   (deterministic scorecard dimensions)
failures            array   (deterministic failure events with turn_ids)
transcript          array of { id, s, x }    # turn_id, speaker, text
judge               { dims: [...cited...], binary: { label, provenance, ... } } | {}
provenance          string  ("source=... · in_manifest|outside_blind_slice · human=... · judge_binary=... · fix_first_evidence")
fix_first_evidence  bool
```

#### 3.2.6 `live`

```
live    bool     # true if at least one live call has been ingested
calls   array    # same shape as calls[] (empty until a real live call lands)
note    string   # optional, present when empty or unreadable
```

**Empty-state requirement:** when `live.live === false`, the Live Today view
renders the empty rail (`.live-empty`), the execution-id command helper
(`.cmd-box`, `.cmd-helper`, `.cmd-note`), and a visible `.banner` explaining
that no live calls have landed yet. It must not show frozen-pilot data while
the user is in Live mode.

### 3.3 The presenter contract (out of Round-3 scope, retained for reference)

`window.__DATA__` keys (from `pipeline/build_surface.py:build_data()`):
`gate_open, floor, val, analytics, report, judge_run, sponsor_proof, rows, fixture(false), design_handoff(false), real_surface(true), privacy_note`.
`rows[]` shape matches `calls[]` above (modulo the workspace-only fields
`archetype`, `recommendation`, `provenance`, `fix_first_evidence`).

---

## 4. Visual constraints to preserve — NON-NEGOTIABLE

The Round-3 prompt must inline all of these. The designer's deliverable is
rejected if any constraint is violated.

### 4.1 Warm light theme
Paper/ember palette per `DESIGN_RATIONALE.md`:
~86% warm paper (`#FAF6EE` and neighbors), ~8% ink (`#221B12`, `#6B6052`),
~4% semantic provenance hues, ~2% ember accent (`#B4541C`). Must be
projector-safe at 1080p, AA+ contrast on every text element.

### 4.2 Presenter `/` — 8 scenes, one viewport each
Each `.scene` (`sc-thesis, sc-trap, sc-measure, sc-hero, sc-judge, sc-action,
sc-proof, sc-method`) must fit ENTIRELY within one viewport at all three
measured resolutions: **1280×720, 1440×900, 1920×1080**. Never let a scene
exceed the viewport. (`/` is out of Round-3 scope but the invariant remains
in case the designer touches shared tokens.)

### 4.3 Drawer hardening (presenter callsheet + corpus, and any platform sheet)
- ≤ 60vw width.
- Default parked off-canvas: `.callsheet:not(.cs-open) { transform: translateX(102%); }`.
- `cs-open` is toggled by JS; CSS must never assume default-open.
- Scrim (`.callsheet-scrim`) hidden by default; visible only when drawer is open.

### 4.4 Keyboard
`←` / `→` / `Home` / `End` / `Esc` all working. Designer must not introduce
focus traps that break Esc.

### 4.5 Offline fallback
- `out/dashboard.html` stays **UNTOUCHED**. It is the always-working demo.
- Zero external `http(s)://` references in any generated HTML/CSS/JS.
- No web fonts. System stack only (Iowan/Palatino/Georgia serif display;
  system grotesque; monospace for IDs/hashes).
- No remote images. No CDN.

### 4.6 Provenance labels — semantically distinct, visible
`.prov.measured`, `.prov.human`, `.prov.calibrated`, `.prov.uncal`,
`.prov.estimated`, `.prov.notobs` must all be visually distinguishable AND
survive grayscale (estimated must be italicized in addition to its hue).
The designer cannot collapse two provenance classes into one style.

### 4.7 Honesty wording — source of truth, do not let the designer rephrase
The following strings come from data and must render verbatim. The designer
may style, but not edit:
- `"estimated exposure"`
- `"heuristic completion"`
- `"LIVE · UNCALIBRATED"`
- `"FROZEN · CALIBRATED"`
- the truth-corrected calibration caption from `report.calibration.caption`
  (a bannned-substring assertion already enforces that "least reliable"
  cannot appear — see `pipeline/build_surface.py:186-187`).
- `report.calibration.balanced_accuracy === 0.628` (asserted constant).

The prompt to the designer must list these as DO-NOT-EDIT strings and
explicitly forbid rephrasing.

---

## 5. Single-shot prompt template — Round 3

One prompt, all contracts inlined. Returns ONLY CSS (≤ ~500 lines).

```text
You are designing the VoiceForge Operator Workspace — the /platform surface.
This is a single-shot pass. Return ONLY CSS. Do not return HTML, JS, or prose.
Do not assume markup beyond what is enumerated below. Maximum length: ~500
lines. No external resources. No web fonts. No remote images.

SCOPE
The single surface you are styling is /platform (Live Clinic Agent operator
workspace). Do not touch presenter / styles. You may share CSS variables with
presenter / via a :root token block, but the cascade must be self-sufficient
within out/platform/styles.css.

DOM CONTRACT — exactly these 82 classes (style every one; add no new ones):
[paste the §2.1 list verbatim]

DATA CONTRACT — your CSS must render correctly against the real data shape:
[paste the §3.2 schema verbatim, including the empty-state rules from §3.2.6]
The data is window.__PLATFORM__, generated by pipeline/build_platform.py from
real artifacts. There are 76 frozen calls and 0..N live calls. The live empty
state at N=0 must look intentional and complete, not broken.

VISUAL CONSTRAINTS — non-negotiable:
[paste §4.1 through §4.7 verbatim]

PROVENANCE PALETTE (semantic, AA+, projector-safe at 1080p):
- .prov.measured  — steel
- .prov.human     — green
- .prov.calibrated — violet
- .prov.uncal     — ochre, dashed border
- .prov.estimated — ember, italicized
- .prov.notobs    — gray
All six must remain distinguishable in grayscale.

DO-NOT-EDIT STRINGS:
[paste §4.7 verbatim]

OUTPUT
Return one fenced block of CSS, suitable to save as out/platform/styles.css.
No commentary. No rationale. No example HTML. CSS only.
```

The prompt is deliberately one-shot. Rounds 1 and 2 drifted because the
contract was paraphrased across multiple back-and-forth turns and the
designer lost track of which classes still needed styling.

---

## 6. QA gate the designer-output must pass before integration

Delegate to the QA matrix doc — to be created or referenced at
`docs/plans/qa_matrix_platform.md` (TBD). At minimum the gate enforces:

1. **DOM-coverage audit** (mandatory). Diff returned CSS selectors against
   the 82-class contract in §2.1. Missing classes: 0. Round 1 missed 5,
   Round 2 missed 35 — this is the gate that catches that regression.
2. **Resolution check.** Open `/platform` in headless Chromium at
   1280×720, 1440×900, 1920×1080. No horizontal scrollbar. No clipped
   content in the rail, detail pane, or live-empty banner.
3. **Drawer parking check.** Any drawer in the page (if introduced) must
   render off-canvas at first paint. Reload and screenshot before any JS
   click — drawer must not be visible.
4. **Offline check.** Disable network. Reload. Page must render
   pixel-identical. Zero failed requests in DevTools network panel.
5. **Provenance distinctness.** Convert screenshot to grayscale. All six
   `.prov.*` chips must remain visually distinguishable.
6. **Honesty string scan.** `grep -F` for each §4.7 string in the rendered
   DOM and assert presence. No rephrasing.
7. **Empty live mode.** With `out/live_calls.json` absent, switch to Live
   Today. Banner + cmd-box visible. No frozen data bleeding through.
8. **Populated live mode.** With a real live call in `out/live_calls.json`,
   switch to Live Today. Real call renders with `LIVE · UNCALIBRATED` chip.

The QA gate runs BEFORE the CSS is committed to `pipeline/build_platform.py`'s
inline `STYLES_CSS` string.

---

## 7. Integration gate — NOT before Codex confirms

None of this is fetched, integrated, or committed until Codex confirms three
things, because the `platform_data.js` the designer's CSS will be measured
against MUST contain real clinic-agent data, not a placeholder:

1. **Final agent id confirmed.** The Bolna agent_id used for the live
   clinic-agent call is locked. `out/bolna_cartesia_proof.json` reflects it.
2. **KB attached.** The clinic knowledge base (`docs/AAROGYA_KNOWLEDGE_BASE.md`
   or its successor) is attached to the live agent and the attachment is
   evidenced in the agent config (`out/clinic_agent_config.json`).
3. **First execution schema verified.** A first real live call has been
   ingested through `pipeline/ingest_live.py`, lands in
   `out/live_calls.json` in the shape `build_platform.py` expects
   (see §3.2.5 — same fields as `calls[]`), and the Live Today view in the
   workspace renders it without empty-state fallback.

Until those three land, the design pass is premature: the designer would be
styling against the empty state only, and Round 3 would not test the loaded
Live case.

---

## Final pre-flight check (before sending the prompt)

- [ ] §2.1 class list re-extracted from current `out/platform/{index.html,app.js,styles.css}` (in case more components were added).
- [ ] §3.2 schema re-checked against `pipeline/build_platform.py:assemble()` (in case fields were added).
- [ ] §4.7 honesty strings re-checked against `pipeline/build_surface.py` assertions and live data.
- [ ] Integration gate (§7) confirmed green by Codex.
- [ ] QA gate (§6) script ready to run on returned CSS.
- [ ] `out/dashboard.html` untouched (verify SHA).
- [ ] No fixture data anywhere in `out/platform/platform_data.js` (`grep -c '"fixture":true'` returns 0).
