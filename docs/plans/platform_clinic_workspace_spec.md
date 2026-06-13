# Platform — Live Clinic Agent Workspace (Spec)

**Status:** PLAN / SPEC ONLY. No source files are modified by this document. No
artifacts under `out/` are regenerated. No Bolna config or API script is touched.

**Audience:** the design-handoff agent (DOM/CSS targeting), and the future Codex
integration pass that will edit `pipeline/build_platform.py` + `pipeline/serve_surface.py`.

**Goal:** add a clearly separate **Live Clinic Agent** section inside `/platform`,
alongside the existing operator workspace (Frozen Pilot · Live Today). The new
section is the **agent-centric** view: agent identity + KB attachment + live
calls produced by *that one agent*, with Bolna Extractions surfaced as a
first-class block. Frozen Pilot stays untouched. Live Today stays untouched.

**Hard provenance contract (repeated throughout):**
- Every element inside Live Clinic Agent carries the `LIVE · UNCALIBRATED` badge.
- Every element inside Frozen Pilot carries the `FROZEN · CALIBRATED` badge.
- Live and frozen are **never mixed in the same aggregate**, the same chart, or
  the same numeric callout. Cross-jump links are allowed (and exist already in
  `out/platform/app.js`); cross-aggregation is not.
- Cartesia voice provenance is shown as `verified` only when the agent-config
  fetch matches (`synthesizer_verified=true`). Otherwise the badge reads
  `unverified — config not yet fetched`. The fetch lives at
  `out/bolna_cartesia_proof.json` and/or `out/clinic_agent_config.json` (see §3).

---

## 1. Information architecture

### Where the new section sits

The existing `/platform` rail has a **two-state mode switch**
(`#mode-frozen` / `#mode-live`) in `out/platform/index.html` (lines 203–207 of
`pipeline/build_platform.py`). The spec proposes promoting this to a
**three-state** segmented control, in this left-to-right order:

```
┌──────────────────────────────────────────────────────────────┐
│  Frozen Pilot   ·   Live Today   ·   Live Clinic Agent       │
└──────────────────────────────────────────────────────────────┘
```

- `Frozen Pilot` — unchanged. The 76-call calibrated workspace.
- `Live Today` — unchanged. The per-call lens over `out/live_calls.json`.
- `Live Clinic Agent` — **new**. The agent-centric lens: one specific Bolna
  agent (`agent_id` from `out/clinic_agent_created.json`), its KB attachment,
  its synthesizer provenance, and only the live calls produced by that agent.

### Why a third pane (and not just reusing Live Today)

`Live Today` is a **per-call** lens — its model is "what calls came in today,
across whatever agents we ingested." It has no concept of a single agent
identity, voice provenance, or KB attachment. It would be wrong to bolt those
onto Live Today because:

1. **Subject differs.** Live Today's subject is the *call*. Live Clinic Agent's
   subject is the *agent* (the deliverable for the Bolna × Cartesia voc-a-thon).
   The agent card + KB card + extractions are agent-level facts, not call-level.
2. **Scope differs.** Live Today can show calls from any source we ingested
   (e.g. a cached `bolna_246cd9f3` replay, or hypothetical future agents).
   Live Clinic Agent shows only calls whose `agent_id` matches the Aarogya
   Clinic agent — and is silent (with a clean empty state) about everything else.
3. **Honesty.** The voc-a-thon judging story is "this agent, this KB, this
   Cartesia voice, this proof loop." Mixing it with arbitrary live calls would
   dilute the claim. Keeping it separate makes the provenance honest: the
   agent card answers "is this the agent we built?", not "what did we ingest?"
4. **No regression for Live Today.** Operators today open Live Today to triage
   any ingested execution. That muscle memory must stay. Live Clinic Agent is
   the demo lens; Live Today is the operator lens.

Both live panes share the **same underlying data file** (`out/live_calls.json`)
but apply different filters and surface different cards. There is no second
ingest path and no second judge path.

### State model (proposed)

In `out/platform/app.js` the current state object is:

```js
var state = { mode:"frozen", q:"", filters:{...}, selected:null };
```

The spec extends `mode` to one of `"frozen" | "live" | "clinic"`. The
`activeCalls()` helper becomes:

```js
function activeCalls(){
  if (state.mode === "live")   return liveCalls();
  if (state.mode === "clinic") return clinicCalls();   // liveCalls() filtered by agent_id
  return CALLS;                                        // frozen
}
```

`clinicCalls()` is `liveCalls().filter(c => c.agent_id === D.clinic.agent_id)`.
If `D.clinic.agent_id` is null (config not fetched), `clinicCalls()` returns
`[]` and the empty state shown is the "agent not yet fetched" variant from §5.

---

## 2. Components (DOM-class proposals for the design-handoff agent)

All new classes are prefixed `cl-` (clinic). This keeps them disjoint from the
existing rail/detail classes so a future stylesheet can scope cleanly.

The detail pane uses a single CSS grid called `.cl-workspace` with three
stacked rows: status row (cards), calls table row, selected-call detail row.

### 2.1 Agent status card — `.cl-card.cl-agent`

Surfaces who/what the agent is. Read from `D.clinic.agent` (§3.2). All fields
fall back to a muted `not yet fetched` if missing.

DOM skeleton:

```html
<section class="cl-card cl-agent" data-provenance="live-uncalibrated">
  <header class="cl-card-head">
    <h3 class="cl-card-title">Agent</h3>
    <span class="cl-badge cl-badge-live">LIVE · UNCALIBRATED</span>
  </header>
  <dl class="cl-kv">
    <dt>Name</dt>            <dd class="cl-agent-name">Aarogya Clinic & Diagnostics — Aarti</dd>
    <dt>Agent ID</dt>        <dd class="cl-agent-id" title="ca9d317e-cae5-4953-9d5e-d60a68320b46">ca9d317e…b46</dd>
    <dt>Status</dt>          <dd><span class="cl-pill cl-ok">processed</span></dd>
    <dt>Voice</dt>           <dd>
      <span class="cl-voice-name">Cartesia · Devansh · sonic-3</span>
      <span class="cl-pill cl-prov-verified">verified</span>  <!-- or .cl-prov-unverified -->
    </dd>
    <dt>Transcriber</dt>     <dd>deepgram / nova-3 · <span class="cl-lang-pair">hi · en</span></dd>
    <dt>Deployment</dt>      <dd><span class="cl-pill">test phone configured</span></dd>
  </dl>
</section>
```

Notes:
- `cl-agent-id` shows truncated id, full id in `title` tooltip (per spec).
- `cl-prov-verified` only renders when `D.clinic.agent.synthesizer_verified === true`.
  Otherwise `cl-prov-unverified` reads `unverified — config not yet fetched`.
- Language pair (`hi · en`) comes from the agent's `languages` array.

### 2.2 KB status card — `.cl-card.cl-kb`

```html
<section class="cl-card cl-kb" data-provenance="live-uncalibrated">
  <header class="cl-card-head">
    <h3 class="cl-card-title">Knowledge base</h3>
    <span class="cl-badge cl-badge-live">LIVE · UNCALIBRATED</span>
  </header>
  <ul class="cl-kb-list">
    <li class="cl-kb-item">
      <span class="cl-kb-name">aarogya_knowledge_base.pdf</span>
      <span class="cl-pill cl-ok">processed</span>
      <span class="cl-pill">attached to LLM</span>
      <span class="cl-kb-meta">1 doc · multilingual</span>
    </li>
  </ul>
</section>
```

Fields per KB entry (from `D.clinic.kb`, §3.3):
- `name` (the file name in Bolna)
- `state` (`processed` / `processing` / `failed`) — drives the pill color
- `attached_to_llm` (boolean) — renders the "attached to LLM" pill if true,
  "not attached" if false
- `doc_count`

If `D.clinic.kb` is empty/missing: render `<p class="cl-empty">no knowledge
base attached.</p>`.

### 2.3 Latest live calls table — `.cl-calls-table`

A table (not a card-grid) because it must scan fast during the demo. Replaces
nothing — Live Today's existing card list stays. This is the Live Clinic Agent
view of the same calls, filtered to one agent.

```html
<section class="cl-section cl-calls" data-provenance="live-uncalibrated">
  <header class="cl-section-head">
    <h2>Recent calls</h2>
    <span class="cl-badge cl-badge-live">LIVE · UNCALIBRATED</span>
    <span class="cl-count">3 calls · this agent</span>
  </header>
  <table class="cl-calls-table">
    <thead>
      <tr>
        <th>Call</th><th>Scenario</th><th class="num">Duration</th>
        <th>Outcome</th><th>Judge</th><th>Phenotype</th><th>Provenance</th>
      </tr>
    </thead>
    <tbody>
      <tr class="cl-call-row" data-call-id="bolna_live_246cd9f3">
        <td class="cl-cid mono">bolna_live_246cd9f3</td>
        <td><span class="cl-pill cl-tag-clean">clean</span></td>
        <td class="num">01:24</td>
        <td><span class="cl-pill cl-ok">completed</span></td>
        <td><span class="cl-pill cl-uncal">success · uncal</span></td>
        <td>booking_confirmed_full_readback</td>
        <td><span class="cl-badge cl-badge-live">LIVE · UNCALIBRATED</span></td>
      </tr>
      ...
    </tbody>
  </table>
</section>
```

Scenario tag — required values (mapped from `call.scenario_tag` if Codex adds
one to the live-call shape; otherwise inferred client-side from
`stress_profile` / `language` / `failures`):
- `clean` — happy-path booking
- `hinglish` — mid-call code-switch
- `ambiguous` — caller request needed clarification
- `changed` — caller changed a detail mid-call
- `safety-refusal` — agent refused medical advice safely

DOM class per scenario: `.cl-tag-clean`, `.cl-tag-hinglish`, etc.

Clicking a row sets `state.selected = <call_id>` and renders the call detail
panel (§2.4) below the table.

### 2.4 Selected-call detail panel — `.cl-call-detail`

The detail panel is the agent-centric counterpart to the existing per-call
view (in `app.js` `callView()`). It surfaces:

1. **Transcript** (left column) — same `.transcript` / `.turn.cited` styling
   as today, reused verbatim. Cited turns are highlighted from
   `judge.dims[].evidence_turn_ids` + `judge.binary.evidence_turn_ids`.
2. **Deterministic signals** (right column, top) — same `dimEl()` rendering.
3. **Extracted fields** (right column, middle) — **new block**, the
   Bolna-Extractions view. See §2.4.1.
4. **Judge evidence** (right column, lower) — same as today: binary outcome +
   5 dims, each with reason + cited turn ids.
5. **Phenotype + recommendation** (right column, bottom) — same `.rec` styling.
6. **Recording link** (footer) — if `telephony_data.recording_url` is present,
   render `<a class="cl-recording" href="...">listen to recording ↗</a>`.
   For web-calls this is null → hide the link, show
   `<span class="cl-unmeasured">web-call · no audio recording</span>`.

#### 2.4.1 Extracted fields block — `.cl-extractions`

Surfaces Bolna's `extracted_data` (from `GET /executions/{id}`, see
`docs/BOLNA_API_NOTES.md` §3) for the six **TARGET_AGENT** fields. The agent's
full extraction schema has 13 fields (see `out/clinic_agent_created.json`);
this block shows the 6 user-facing ones first, then collapses the rest into a
"More fields" expander.

```html
<section class="cl-card cl-extractions" data-provenance="live-uncalibrated">
  <header class="cl-card-head">
    <h3 class="cl-card-title">Extracted appointment</h3>
    <span class="cl-badge cl-badge-live">LIVE · UNCALIBRATED</span>
  </header>
  <dl class="cl-extract-fields">
    <div class="cl-extract-row" data-field="patient_name">
      <dt>Patient name</dt>
      <dd class="cl-extract-value">Priya Sharma</dd>
      <dd class="cl-extract-conf" data-label="high">0.94 · high</dd>
    </div>
    <div class="cl-extract-row" data-field="phone_number"> ... </div>
    <div class="cl-extract-row" data-field="appointment_type"> ... </div>     <!-- "service" -->
    <div class="cl-extract-row" data-field="preferred_date"> ... </div>
    <div class="cl-extract-row" data-field="preferred_time"> ... </div>
    <div class="cl-extract-row" data-field="booking_confirmed">
      <dt>Booking confirmed</dt>
      <dd><span class="cl-pill cl-ok">yes</span></dd>
      <dd class="cl-extract-conf" data-label="high">0.97 · high</dd>
    </div>
  </dl>
  <details class="cl-extract-more">
    <summary>More fields (7)</summary>
    <!-- collection_address, doctor_or_department, test_or_service,
         appointment_status, medical_advice_requested,
         medical_advice_refused_safely, language_mode -->
  </details>
</section>
```

Per-field shape (read from `call.extracted_data[field]`):

```json
{ "value": "Priya Sharma", "confidence": 0.94, "confidence_label": "high" }
```

If a field is missing from `extracted_data`, render `<dd class="cl-unmeasured">
not extracted</dd>` and omit the confidence row. **Never** invent a value.

Mapping notes (TARGET_AGENT spec uses friendly names; Bolna extraction names
above come from `out/clinic_agent_created.json`):
- `patient_name` → `patient_name`
- `phone` → `phone_number`
- `service` → `appointment_type` (or fall back to `test_or_service`)
- `date` → `preferred_date`
- `time` → `preferred_time`
- `booking_confirmed` → `booking_confirmed`

### 2.5 Improvement queue tie-in — `.cl-improvement`

Pinned to the bottom of the workspace, regardless of selected call. Surfaces
**one** top improvement for the clinic-call set — *not* a lift claim.

```html
<section class="cl-improvement" data-provenance="live-uncalibrated">
  <header class="cl-card-head">
    <h3>One fix, demonstrated</h3>
    <span class="cl-badge cl-badge-live">LIVE · UNCALIBRATED</span>
  </header>
  <p class="cl-fix-summary">
    On the <a class="cl-jump" data-id="bolna_live_…">ambiguous-service scenario</a>,
    the agent skipped a clarifying question and booked the wrong test.
    Patch the FAQ block to enumerate the 3 most-asked tests; re-run scenario 3.
  </p>
  <p class="cl-fix-caveat">
    One demonstrated scenario · the loop, not a lift claim. Calibration requires
    repeat calls + the human-label gate.
  </p>
</section>
```

Source: `D.clinic.improvement` (§3.4). If missing, render an empty state:
`<p class="cl-empty">not enough calls yet to surface a fix.</p>`.

---

## 3. Data contract (read-only consumption)

The workspace MUST NOT change the source-of-truth artifacts. It consumes them.
Two files are referenced; Codex picks one or both at integration time.

### 3.1 Existing — `out/live_calls.json` (extended, additive only)

Already produced by `pipeline/judge_live.py`. Current shape is documented in
that file's header. The spec proposes adding **two optional, additive fields**
per call, both backwards-compatible:

```json
{
  "call_id": "bolna_live_246cd9f3",
  "agent_id": "ca9d317e-cae5-4953-9d5e-d60a68320b46",          // NEW (optional)
  "scenario_tag": "clean",                                       // NEW (optional)
  "extracted_data": {                                            // NEW (optional)
    "patient_name":       { "value": "Priya Sharma", "confidence": 0.94, "confidence_label": "high" },
    "phone_number":       { "value": "+91…",         "confidence": 0.99, "confidence_label": "high" },
    "appointment_type":   { "value": "blood test",   "confidence": 0.88, "confidence_label": "high" },
    "preferred_date":     { "value": "2026-06-14",   "confidence": 0.86, "confidence_label": "high" },
    "preferred_time":     { "value": "10:00",        "confidence": 0.81, "confidence_label": "high" },
    "booking_confirmed":  { "value": "yes",          "confidence": 0.97, "confidence_label": "high" }
  },
  "telephony": {                                                 // NEW (optional)
    "recording_url": null,        // web-calls are null; telephony calls carry a URL
    "duration_sec": 84,
    "hangup_reason": "completed"
  },
  "...all existing fields (source, language, transcript, judge, scorecard, ...)": "..."
}
```

A new top-level **`agent`** block is also added (additive, optional):

```json
{
  "slice": "live_today",
  "calibrated": false,
  "label": "LIVE · UNCALIBRATED",
  "generated_at": "...",
  "agent": {                                                     // NEW (optional)
    "agent_id": "ca9d317e-cae5-4953-9d5e-d60a68320b46",
    "name": "Aarogya Clinic & Diagnostics — Aarti",
    "status": "processed",
    "synthesizer": {
      "provider": "cartesia",
      "voice_name": "Devansh",
      "model": "sonic-3",
      "verified": true                                           // matches D.clinic.agent.synthesizer_verified
    },
    "transcriber": { "provider": "deepgram", "model": "nova-3" },
    "languages": ["hi", "en"],
    "kb": [
      { "name": "aarogya_knowledge_base.pdf",
        "rag_id": "ae5cc5d1-…",
        "state": "processed",
        "attached_to_llm": true,
        "doc_count": 1 }
    ],
    "source_files": ["out/clinic_agent_created.json",
                     "out/clinic_knowledgebase_created.json",
                     "out/bolna_cartesia_proof.json"]
  },
  "judge": { ... },
  "calls": [ ... ]
}
```

If Codex elects this option, `pipeline/build_platform.py` reads
`payload["live"]["agent"]` directly into `payload["clinic"]` and the JS
binds `D.clinic = (window.__PLATFORM__.clinic) || null`.

### 3.2 Alternative — `out/clinic_agent_state.json` (a sidecar)

If keeping `live_calls.json` strictly produced-by-the-judge is preferable, the
agent block lives in a sidecar:

```
out/clinic_agent_state.json
```

```json
{
  "generated_at": "2026-06-13T…",
  "source": "merge of out/clinic_agent_created.json + clinic_knowledgebase_created.json + bolna_cartesia_proof.json",
  "agent": { ... same shape as 3.1 .agent ... },
  "improvement": {
    "scenario_tag": "ambiguous",
    "evidence_call_id": "bolna_live_…",
    "summary": "On the ambiguous-service scenario …",
    "caveat": "one demonstrated scenario · the loop, not a lift claim"
  }
}
```

`pipeline/build_platform.py` reads it (gracefully empty if absent) and exposes
it as `D.clinic` on the page. `out/live_calls.json` stays exactly as
`judge_live.py` writes it; the per-call `extracted_data` would then ride on
that file (3.1) but the agent metadata lives in this sidecar.

**Either file is fine.** Recommendation: **option 3.2 (sidecar)** because
`judge_live.py` is hermetic by design and the agent metadata is not an
artifact of judging — it is an artifact of agent creation. Keeping the
production boundaries clean trumps the second file. Codex makes the final call.

### 3.3 KB block — exact field map

Source: `out/clinic_knowledgebase_created.json`. Field map:

| KB UI field      | Source path                            |
|------------------|----------------------------------------|
| `name`           | `.file_name`                           |
| `rag_id`         | `.rag_id`                              |
| `state`          | `.status` (`processed`/`processing`)   |
| `attached_to_llm`| **derived** from a future fetch of `GET /v2/agent/{id}` showing the rag id in the agent's knowledgebase array. Until that fetch lands, default to `true` if `status==="processed"` AND surface a footnote `attached_to_llm inferred from create-time status` |
| `doc_count`      | constant `1` for the current PDF; future: doc count from the rag |

### 3.4 Improvement block

Hand-curated for now (one entry, scenario-tagged). Codex can later generate it
from a clinic-only run of the same logic that produces
`out/demo_report_data.json::improvement_queue`, but **must not** mix it with
the frozen queue.

### 3.5 What MUST NOT change

- `out/judge_results.json` — frozen, audited. **Read only, never touched.**
- `out/analytics.json`, `out/demo_report_data.json`, `out/calls.json` —
  frozen pilot aggregates. **Read only, never touched.**
- `out/surface/design_data.js` — the presentation bundle. **Read only.**
- `rubric.yaml`, `eval/label_*` — calibration ground truth. **Read only.**
- The `LIVE_PROVENANCE` constant and the `judge_live.py` write path — keep as is.

---

## 4. Provenance rules (explicit, repeated)

These rules are **load-bearing** for the voc-a-thon honesty story. They are
restated here so the design-handoff agent has them in one place.

1. **Every Live Clinic Agent card, table row, and field carries
   `LIVE · UNCALIBRATED`.** No exceptions. The badge is the `.cl-badge-live`
   class.
2. **Every Frozen Pilot card, table row, and field carries
   `FROZEN · CALIBRATED`.** No exceptions. The existing `.banner.frozen` is
   the precedent.
3. **Live and frozen aggregates never combine.** No average of live + frozen
   scores. No "X of 80 calls succeeded" where X mixes the 76 frozen + 4 live.
   The two are rendered in disjoint sections with the mode switch.
4. **Cartesia provenance:**
   - `verified` (green pill `.cl-prov-verified`) renders ONLY when the
     agent-config fetch returns `synthesizer.provider === "cartesia"` AND
     the spec's expected voice matches. The boolean `synthesizer_verified`
     in the data contract (§3.1) is the gate.
   - Otherwise: `unverified — config not yet fetched` (warning pill
     `.cl-prov-unverified`). No green pill until the fetch lands.
5. **Cross-pane jumps are allowed.** Clicking a cited call id inside Frozen
   Pilot already jumps to that frozen call. The same affordance for clinic
   calls jumps within `mode==="clinic"`. The mode switch is the source of
   truth; jumps respect it.
6. **No barge-in claim on live calls.** Honor the constraint in
   `docs/BOLNA_API_NOTES.md` §4: the Bolna API has no interruption telemetry.
   Live Clinic Agent must not render a barge-in number, badge, or chart.
7. **The judge layer is uncalibrated, even for the clinic agent.** Judge
   evidence shows the binary outcome + 5 dims with cited turn ids, all with the
   `uncal` pill. Kappa is **not** rendered anywhere in the clinic pane.

---

## 5. Empty-state behavior

### 5.1 Zero live clinic calls yet

Pinned to the top of the workspace (above the agent card):

```html
<section class="cl-empty-state" data-provenance="live-uncalibrated">
  <h3 class="cl-empty-title">Live Clinic Agent · empty</h3>
  <p class="cl-empty-copy">
    No live calls for this agent yet. Paste a Bolna execution id below to get
    the exact ingest + judge command. Nothing runs from the browser.
  </p>
  <label class="cl-cmd-label" for="cl-exec-id">Execution id</label>
  <input id="cl-exec-id" class="cl-cmd-input" type="text" placeholder="exec_…">
  <pre class="cl-cmd-box"><button class="cl-cmd-copy">COPY</button><code id="cl-cmd-text">python pipeline/ingest_live.py --execution &lt;execution-id&gt; &amp;&amp; python pipeline/judge_live.py</code></pre>
  <p class="cl-cmd-note">Run in the repo root, then refresh. Live cards appear as <b>LIVE · UNCALIBRATED</b>; no human label or kappa applies until calibration.</p>
</section>
```

This is intentionally the **same command shape** Live Today already uses (see
`liveEmptyEl()` in `app.js` line ~474) so operators don't have to learn a
second ingest path. The only behavioral difference is the surrounding copy.

### 5.2 Agent config not yet fetched

If `D.clinic.agent` is missing (sidecar not built, or agent block absent from
`live_calls.json`):

```html
<section class="cl-card cl-agent cl-agent-unfetched">
  <header class="cl-card-head">
    <h3>Agent</h3>
    <span class="cl-badge cl-badge-live">LIVE · UNCALIBRATED</span>
  </header>
  <p class="cl-unmeasured">
    Agent config not yet fetched. The Cartesia voice cannot be marked
    <em>verified</em> until <code>GET /v2/agent/{id}</code> is cached locally.
  </p>
  <p class="cl-unmeasured">
    Build the sidecar with the integration commands in
    <code>docs/plans/platform_clinic_workspace_spec.md §7</code>.
  </p>
</section>
```

KB card has the analogous empty state when `D.clinic.agent.kb` is `[]`.

### 5.3 Live calls present but none from this agent

Show the table empty state:
`<tr class="cl-empty-row"><td colspan="7">Live calls ingested today, but none from this agent (<code class="cl-agent-id-short">ca9d…b46</code>). Open Live Today for the full ingested set.</td></tr>`

This is the explicit handoff to Live Today — it reinforces *why* the two
panes exist.

---

## 6. Out of scope for this spec

The following are explicitly **NOT** in scope. The integration pass must
refuse them unless a future spec opens them.

1. **No browser-driven ingest.** No button that runs a shell command. The
   command helper DISPLAYS the command for the operator to copy/paste, same
   as Live Today. The string "nothing runs from the browser" is part of the
   empty-state copy.
2. **No mutation of frozen artifacts.** The list in §3.5 is the
   never-touch set.
3. **No mixing of live and frozen aggregates.** Restated from §4 — no chart,
   number, or sentence may average across the two.
4. **No live kappa.** Live has no human gold labels; no kappa is computed,
   shown, or implied.
5. **No "we boosted booking rate by X%" framing.** The improvement-queue
   tie-in (§2.5) is "one demonstrated scenario, the loop" — not a lift claim.
6. **No new judge prompt.** The clinic pane reuses `judge_live.py` output
   verbatim. If a clinic-specific rubric is wanted later, it goes in a
   separate spec and must be calibrated.
7. **No write path inside the JS bundle.** The workspace is read-only. The
   `extracted_data` is consumed; corrections to it (if any are ever wanted)
   are out of scope.

---

## 7. Integration gate (sequence for the future Codex pass)

**Gate.** None of the steps below run until Codex confirms ALL of the
following from the agent buddy:
1. Final agent id (already known: `ca9d317e-cae5-4953-9d5e-d60a68320b46`,
   per `out/clinic_agent_created.json` — confirm it has not been re-created).
2. KB attachment status — that the rag id `ae5cc5d1-…` is attached to the
   agent's LLM in the live Bolna config.
3. First execution schema — at least one `GET /executions/{id}` payload from
   the clinic agent, so the `extracted_data` field shape can be verified
   against the spec in §3.1.

Once the gate clears, the integration pass executes these edits **in order**:

### Step 1 — generator: build the clinic state sidecar

NEW file: `pipeline/build_clinic_state.py`. Reads
`out/clinic_agent_created.json`, `out/clinic_knowledgebase_created.json`, and
`out/bolna_cartesia_proof.json`. Writes `out/clinic_agent_state.json` per §3.2.
Does not touch any other file. Pure read + write of one sidecar.

Run: `python pipeline/build_clinic_state.py`

### Step 2 — judger: emit `extracted_data` + `telephony` on live calls

EDIT `pipeline/judge_live.py`'s merged-record assembly (the `record` block
inside `run()`). Additive only:
- Copy `execution.extracted_data` into `record["extracted_data"]` (verbatim,
  no transformation). If absent, omit the field.
- Copy `execution.telephony_data` into `record["telephony"]` if present.
- Copy `execution.agent_id` into `record["agent_id"]` if present.
- Tag `record["scenario_tag"]` from a small classifier (clean / hinglish /
  ambiguous / changed / safety-refusal). Hand-rule for now; fine to start as
  null.

Run: `python pipeline/judge_live.py`

Verify: `out/live_calls.json` calls now carry `agent_id`, `extracted_data`,
`telephony`, and `scenario_tag`. Frozen artifacts unchanged.

### Step 3 — platform generator: read both files, expose `D.clinic`

EDIT `pipeline/build_platform.py`:
- Add `CLINIC = OUT / "clinic_agent_state.json"` and `_load_clinic()`.
- In `assemble()`, add `payload["clinic"] = _load_clinic()`. Graceful empty
  state if absent (`{}`).
- No other change. Frozen path untouched.

Run: `python pipeline/build_platform.py`

Verify: `out/platform/platform_data.js` contains `window.__PLATFORM__.clinic`.

### Step 4 — workspace JS: mode switch + clinic view

EDIT `out/platform/app.js` (the inline `APP_JS` string in
`build_platform.py`). Additions only:
- Add the third mode button to `index.html`'s `.mode-switch`.
- Extend `state.mode` to accept `"clinic"`.
- Add `clinicCalls()` (liveCalls filtered by agent_id).
- Add `clinicView()` (renders agent card, KB card, calls table, selected-call
  detail with extractions). Reuses `dimEl()`, `citesEl()`, the transcript
  rendering, and `.rec` styling.
- Add the empty-state from §5.1 / §5.2 / §5.3.
- Wire the third button into `init()`.

Re-run: `python pipeline/build_platform.py` (regenerates `out/platform/app.js`).

### Step 5 — server: no changes required

`pipeline/serve_surface.py` already serves `out/platform/*` as static files
and proxies `/platform/live`. The new sidecar is consumed at build time, not
at request time, so no new route is needed. **No edit.**

### Step 6 — smoke check

1. Open `http://localhost:8080/platform`.
2. Confirm three-state segmented control.
3. Click `Live Clinic Agent`. With zero clinic calls: see the §5.1 empty
   state with the copy-button command helper. With agent config absent: see
   §5.2.
4. Run the displayed ingest+judge command on a real execution id.
5. Reload `/platform`, switch to `Live Clinic Agent`, confirm: agent card
   green-verified IF the cartesia proof is cached, KB card processed,
   calls table populated, selected-call detail shows transcript +
   deterministic + extractions + judge + recommendation.
6. Switch back to Frozen Pilot — all numbers unchanged (audited dashboard
   integrity preserved).

### What this spec does **not** unlock

- It does not unlock a clinic-specific judge prompt.
- It does not unlock a clinic-specific rubric.
- It does not unlock a live kappa.
- It does not unlock browser-driven ingest.

Those each need their own spec.

---

## Appendix A — File map (read-only references for the design agent)

- `pipeline/build_platform.py` — current generator. Lines 199–221 hold the
  `INDEX_HTML` mode switch. Lines 357–760 hold the JS to extend.
- `pipeline/serve_surface.py` — server. No edit needed.
- `out/platform/index.html`, `app.js`, `platform_data.js`, `styles.css` —
  current built workspace. DO NOT EDIT IN PLACE; they are generated.
- `out/live_calls.json` — live slice (consumer of `judge_live.py` output).
- `out/clinic_agent_created.json` — source-of-truth for agent identity
  (agent_id, name, voice, transcriber, languages).
- `out/clinic_knowledgebase_created.json` — source-of-truth for KB.
- `out/bolna_cartesia_proof.json` — source-of-truth for synthesizer
  verification.
- `docs/TARGET_AGENT.md` — use case + extraction field list.
- `docs/BOLNA_API_NOTES.md` — extraction shape, telephony shape, no-barge-in
  constraint.
- `pipeline/judge_live.py` — produces `out/live_calls.json`. Only Step 2 of
  §7 edits this; no other pass touches it.

## Appendix B — Class-name table for the design-handoff agent

| Class                          | Role                                                |
|--------------------------------|-----------------------------------------------------|
| `.cl-workspace`                | Outer grid wrapping the clinic pane                 |
| `.cl-card`                     | Generic card (agent / KB / extractions)             |
| `.cl-card.cl-agent`            | Agent identity card                                 |
| `.cl-card.cl-kb`               | KB attachment card                                  |
| `.cl-card.cl-extractions`      | Extracted-fields block                              |
| `.cl-card-head` / `.cl-card-title` | Card header / title                             |
| `.cl-kv` / `dt` / `dd`         | Definition list inside agent card                   |
| `.cl-agent-name`               | Agent display name                                  |
| `.cl-agent-id`                 | Truncated agent id; full id in `title` attr         |
| `.cl-voice-name`               | "Cartesia · Devansh · sonic-3"                      |
| `.cl-lang-pair`                | "hi · en"                                           |
| `.cl-kb-list` / `.cl-kb-item`  | KB list + entry                                     |
| `.cl-kb-name` / `.cl-kb-meta`  | KB filename / metadata                              |
| `.cl-section` / `.cl-section-head` | Wrapping section + header                       |
| `.cl-calls` / `.cl-calls-table`| Calls table                                         |
| `.cl-call-row[data-call-id]`   | Table row, clickable                                |
| `.cl-cid.mono`                 | Monospaced call id cell                             |
| `.cl-tag-clean` / `-hinglish` / `-ambiguous` / `-changed` / `-safety-refusal` | Scenario pills |
| `.cl-call-detail`              | Selected-call panel                                 |
| `.cl-extractions`              | Extracted fields card                               |
| `.cl-extract-fields`           | Extraction list                                     |
| `.cl-extract-row[data-field]`  | One extraction row                                  |
| `.cl-extract-value`            | Extracted value                                     |
| `.cl-extract-conf[data-label]` | Confidence + label (`high`/`medium`/`low`)          |
| `.cl-extract-more`             | Collapsible 7-extra-fields expander                 |
| `.cl-recording`                | Recording-url link (telephony only)                 |
| `.cl-improvement`              | Bottom improvement-queue tie-in                     |
| `.cl-fix-summary` / `.cl-fix-caveat` | Fix text + caveat                             |
| `.cl-empty-state`              | Top empty state when zero clinic calls              |
| `.cl-empty-title` / `.cl-empty-copy` | Empty state copy                              |
| `.cl-cmd-label` / `.cl-cmd-input` / `.cl-cmd-box` / `.cl-cmd-copy` / `.cl-cmd-note` | Command helper |
| `.cl-empty-row`                | Empty row inside calls table                        |
| `.cl-unmeasured`               | Muted "not extracted / not fetched" copy            |
| `.cl-pill`                     | Generic pill                                        |
| `.cl-pill.cl-ok`               | Green ok pill                                       |
| `.cl-pill.cl-uncal`            | Amber uncalibrated pill                             |
| `.cl-pill.cl-prov-verified`    | Green verified pill (synthesizer)                   |
| `.cl-pill.cl-prov-unverified`  | Amber unverified pill                               |
| `.cl-badge.cl-badge-live`      | The `LIVE · UNCALIBRATED` badge                     |
| `.cl-jump[data-id]`            | Cross-section jump anchor (mirrors `.linkid`)       |

All classes are `cl-`-prefixed so they cannot collide with the existing
operator workspace classes.
