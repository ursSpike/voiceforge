# Content-Truth Pass — clinic/diagnostic-lab reframe

> Plan/report only. NO source file is modified. Apply only after the integration gate at the bottom of this doc clears.

---

## 0 · Inputs read

- `docs/TARGET_AGENT.md` — use case spec (inbound clinic / diagnostic-lab appointment booking, Hinglish, Cartesia-voiced) + guardrails (no medical advice).
- `docs/demo_docs.md` — 8-scene spoken script, 6:30 budget.
- `PROJECT_BIBLE.md` — honest scope; what "calibrated" does and does NOT mean.
- `docs/BOLNA_FIELDS_REFERENCE.md` — field/API context (referenced in TARGET_AGENT).
- `docs/SPRINT_CONTROL.md` — clinic pivot logged; AGENT-FIRST priority; agent id `ca9d317e-cae5-4953-9d5e-d60a68320b46`, name "Aarogya Clinic & Diagnostics — Aarti".
- `docs/dataset_card.md`, `docs/limitations.md` — already truth-patched once.
- `voiceforge_design/{index.html,app.js,styles.css,design_data.js}` — source of `/` presentation.
- `pipeline/build_surface.py`, `pipeline/build_platform.py` — generators.
- `out/surface/`, `out/platform/` — generated (read-only reference).

---

## 1 · Reframing principle (the one paragraph)

**The agent is the product judged today**; VoiceForge is its **evaluation and observability layer** — the *same thesis*, sharpened by a specific Application. The agent on stage is **Aarogya Clinic & Diagnostics' inbound appointment scheduler ("Aarti")** — Hinglish, Cartesia-voiced (Devansh), Bolna-orchestrated. The framing shift is *not* "we changed what VoiceForge is"; it is "the same calibrated post-call layer, applied to a real clinic appointment-booking agent rather than a generic 'voice agent.'" The honesty discipline is unchanged: deterministic-before-judge · blind labels · κ with prevalence-aware companions · evidence-cited judge · uncalibrated-where-not-measured. **Live clinic calls** ingested today through `pipeline/ingest_live.py` → `pipeline/judge_live.py` appear as `LIVE · UNCALIBRATED` in a separate lane — never mixed into the frozen calibration. The **frozen 46-call calibration slice is NOT clinic-domain** (it is 30 Code-Mixed-Dialog restaurant-booking Hinglish + 14 SpokenWOZ English controls + hero + Bolna), and we say so plainly: it is the **methodology proof** (that the loop calibrates honestly on Hinglish multilingual task-oriented dialogue), while the **live clinic calls are the use-case proof** (that the same machinery measures the agent the judges will call). Two proofs, one loop — and neither has to pretend to be the other.

---

## 2 · Catalog — every copy site (file:line · current · proposed · rationale)

> All numbered numerics, κ captions, balanced-accuracy, prevalence-paradox sentences, evidence-cited-judgments and "uncalibrated / estimated / measured-not-assumed" phrases are PRESERVED. Replacements affect *framing language only*.

### A. Presentation surface — `voiceforge_design/` (also copied into `out/surface/` by `build_surface.py`)

| # | file:line | current text | proposed replacement | rationale |
|---|---|---|---|---|
| A1 | `voiceforge_design/index.html:6` (`<title>`) | `VoiceForge — the evaluation lab after the call` | `VoiceForge — evaluation layer for the Aarogya clinic appointment agent` | Reframe Application (clinic appointment scheduler) without dropping "evaluation layer." Browser-tab honesty. |
| A2 | `voiceforge_design/app.js:54` (`renderThesis`, wordmark line) | `Voice<b>Forge</b> · The evaluation lab for production voice agents` | `Voice<b>Forge</b> · The evaluation layer for a Hinglish clinic-appointment agent (Cartesia-voiced Bolna)` | Hero kicker — moves "production voice agents" → the specific agent. Keeps "evaluation layer" thesis word. |
| A3 | `voiceforge_design/app.js:56-58` (`<h1 class="hero-thesis">`) | `Success rate tells you whether calls finished. / VoiceForge tells you how.` | **UNCHANGED** — this is the bookend thesis. Apply only at A2 (kicker) and A4 (sub). | The thesis line is verbatim-protected (Slide 1 + Slide 8 bookend). |
| A4 | `voiceforge_design/app.js:61-65` (`hero-sub`) | `It tells you how calls finished, what failures cost, and what to fix first — deterministic signals before semantic judgment, blind human labels before trust, evidence cited on every claim.` | `For this clinic agent — and for any voice agent — it tells you how calls finished, what failures cost, and what to fix first. Deterministic signals before semantic judgment, blind human labels before trust, evidence cited on every claim.` | Anchors Application (clinic agent) while preserving the general thesis ("and for any voice agent"). The honesty triplet is verbatim. |
| A5 | `voiceforge_design/app.js:67` (`hero-stats`, first stat label) | `calls scored` | `calls scored (methodology proof: Hinglish task-oriented dialogue)` | One small clarifier so the 76-call number doesn't read as 76 clinic calls. **Risk-check: must not say "clinic calls."** |
| A6 | `voiceforge_design/app.js:84` (Scene 2 head, `renderTrap`) | head kicker `"The metric trap"`, title `A success-rate dashboard is blind exactly where it costs money.`, lede `The metric most teams ship is completion — a keyword check. Compared with blind human judgment on the same calls, here is how often they agree.` | Kicker + title **UNCHANGED**. Lede: `The metric most voice-agent teams ship is completion — a keyword check. For an appointment agent, that says "the call ended" but not "the slot was filled correctly." Compared with blind human judgment on the same 45 calls, here is how often they agree.` | Sharpens the trap to the appointment use case ("slot was filled correctly") — same number, same finding, sharper consequence. **The 25/45 and 7-of-8 stats and caption stay verbatim.** |
| A7 | `voiceforge_design/app.js:130-132` (Scene 3 head, `renderMeasure`) | title `Deterministic before judge.`, lede `Two rules. Measure what a clock or a rule can answer. Judge only what is genuinely subjective — and calibrate even that.` | **UNCHANGED.** The doctrine sentences are protected. | Doctrine = DO-NOT-TOUCH. |
| A8 | `voiceforge_design/app.js:138` (Rule one body) | `Barge-ins (speech overlap in either direction) and latency gaps come from turn-timestamp arithmetic — counted, not judged. Missing timing is omitted, never fabricated.` | **UNCHANGED** — but consider adding *one* sentence: `For the live Bolna clinic calls, Bolna exposes no interruption telemetry, so barge-in is reported only on the frozen timed slice; latency is reconstructed from /log event times.` | Honest disclosure already required by `SPRINT_CONTROL.md` Bolna-API note. Strengthens, doesn't weaken. **Only add if there is line-space.** |
| A9 | `voiceforge_design/app.js:173-175` (Scene 4 head, `renderHero`) | kicker `Hero call`, title `A "success" that limped.`, lede empty | Title **UNCHANGED**. Add lede: `Disclosed up front — this is NOT the clinic agent. It is a constructed cross-domain call that makes "brittle success" tangible in one listen; validity comes from the calibration in the next scene.` | Hero call is Telugu-English appliance-service — it is NOT the clinic agent. Without an explicit disclosure inside the scene, judges who already know the deliverable is a clinic agent will (rightly) wonder why the demo opens on an appliance call. Sharpening this protects honesty. |
| A10 | `voiceforge_design/app.js:179` (`disclose` chip) | `⚠ Constructed scenario · disclosed up front · voiced with Cartesia` | `⚠ Constructed cross-domain scenario · disclosed up front · voiced with Cartesia · NOT the live clinic agent` | Same reason as A9 — the disclosure already exists; just sharpen it. |
| A11 | `voiceforge_design/app.js:191-192` (hero-line copy) | `The task got done — but the caller had to fight for it. A pass/fail number calls this a win and moves on. VoiceForge calls it brittle, shows the friction, and keeps the receipt.` | **UNCHANGED.** "Brittle success" framing protected. | Brittle-success caption is part of the thesis. |
| A12 | `voiceforge_design/app.js:226-228` (Scene 5 head, `renderJudge`) | kicker `Blind labels & calibration`, title `"I do not trust the judge. I measure how much to trust it."`, lede `Outcomes were labeled blind before any judging — IDs stripped, scores hidden. ${D.val.binary} usable binary labels. Then: does the judge agree? Reported measured, not assumed.` | Kicker + title **UNCHANGED**. Lede: `Outcomes were labeled blind before any judging — IDs stripped, scores hidden, on a frozen Hinglish task-oriented slice (restaurant + travel booking — the methodology proof, not the clinic). ${D.val.binary} usable binary labels. Then: does the judge agree? Reported measured, not assumed.` | Critical: do NOT let viewers think the 45-call calibration is clinic-domain. The truth is the calibration is restaurant+travel booking; the clinic agent is the live/use-case proof. Stated openly, the two-proofs framing strengthens the demo. **Caption + κ + balanced accuracy + truth-correction stay verbatim.** |
| A13 | `voiceforge_design/app.js:249` (`ci-note`) | `82% of calls succeed, so κ is mathematically crushed — the prevalence paradox. Shown low and honest, not hidden.` | **UNCHANGED.** | DO-NOT-TOUCH (prevalence paradox). |
| A14 | `voiceforge_design/app.js:262-265` (truth-row 71% ≈ 69% block) | `71% ≈ 69%` · `hi-en vs English — statistically the same` · `83% vs 50%` · `high vs medium annotator confidence` | **UNCHANGED.** | The truth-correction is verbatim-protected. |
| A15 | `voiceforge_design/app.js:267-268` (chips-key paragraph) | `Where NOT to trust the judge. The real fault line is confidence, not language — it routes a second-rater review queue.` | **UNCHANGED.** | Verbatim. |
| A16 | `voiceforge_design/app.js:299-301` (Scene 6 head, `renderAction`) | kicker `Phenotypes & the queue`, title `Pass/fail is one bit. Failure has shapes — so does success.`, lede `Every call gets transcript-observable phenotype tags; archetypes are derived deterministically, never hand-picked. Each failure becomes a queue entry with evidence and a fix.` | **UNCHANGED.** | Archetype/improvement-queue framing is core thesis. |
| A17 | `voiceforge_design/app.js:316` (panel-note: brittle line) | `Five successes are <b>brittle</b> — done, but the caller fought. A success rate hides that; a phenotype distribution can't.` | **UNCHANGED.** | Brittle success caption protected. |
| A18 | `voiceforge_design/app.js:337` (pheno-foot) | `That's not a score — it's an engineering backlog, sorted by what to fix first.` | **UNCHANGED.** | Verbatim. |
| A19 | `voiceforge_design/app.js:350-352` (Scene 7 head, `renderProof`) | title `Bolna runs the call. Cartesia gives it a voice. VoiceForge tells you what to fix next.`, lede `Three honest links — a real Bolna execution ingested from their API, the live agent configured with Cartesia, and the hero call voiced with that same Cartesia voice.` | Title **UNCHANGED**. Lede: `Three honest links — a real Bolna execution ingested from their API, the live Aarogya clinic agent configured with Cartesia (Devansh · sonic-3), and the hero call voiced with that same Cartesia voice.` | Adds the live-agent identity (Aarogya/Devansh/sonic-3) without making any new performance claim. Already true per `out/bolna_cartesia_proof.json`. |
| A20 | `voiceforge_design/app.js:377` (live-slot paragraph) | `Fresh on-site calls through the live Cartesia-voiced agent — clean, code-switched, a repair loop — pushed through this same pipeline. Timestamps prove they're from today. Shown separately; they never enter the frozen 46-call manifest and never touch κ.` | `Fresh on-site calls through the live Aarogya clinic appointment agent (Cartesia · Devansh · sonic-3, Hinglish) — clean booking, code-switched, ambiguous-request clarification, mid-call detail change, refused medical-advice request — pushed through this same pipeline. Timestamps prove they're from today. Shown separately; LIVE · UNCALIBRATED; never enter the frozen 46-call manifest and never touch κ.` | Names the 5 live scenarios (per TARGET_AGENT.md §6) and reinforces the lane separation. **No new performance claim. "Uncalibrated" wording preserved.** |
| A21 | `voiceforge_design/app.js:392-393` (Scene 8 head, `renderMethod`) | title `Honesty is the feature.`, lede `Clean calls are cheap; calls where the caller fights burn money. That's the budget a success rate can't see.` | **UNCHANGED.** | Verbatim. |
| A22 | `voiceforge_design/app.js:395-402` (limits list) | 8 honest limits. | **UNCHANGED** — but add one clinic-specific honesty limit: `"The live clinic calls collect patient name + phone; the prototype treats them as controlled test calls — production would require consent capture, PII redaction, and a retention policy before judging or storage."` | This is straight from `docs/TARGET_AGENT.md` §7 PII note. **Strengthens** the honesty list rather than weakening it. **Must NOT say "HIPAA-ready" — instead "would require…before".** |
| A23 | `voiceforge_design/app.js:418` (close-line) | `"Success rate tells you whether calls finished. VoiceForge tells you how they finished, what failures cost, and what to fix first."` | **UNCHANGED.** | Verbatim bookend with Slide 1. |
| A24 | `voiceforge_design/app.js:420` (close-thanks) | `Thank you to <b>Bolna</b> and <b>Cartesia</b> for the platform and the voice.` | **UNCHANGED.** | Verbatim. |

### B. Operator surface — `pipeline/build_platform.py` (generates `out/platform/`)

| # | file:line | current text | proposed replacement | rationale |
|---|---|---|---|---|
| B1 | `pipeline/build_platform.py:195` (`<title>`) | `VoiceForge — Operator Workspace` | `VoiceForge — Operator Workspace · Aarogya Clinic Agent` | Tab honesty. Names what's being operated. |
| B2 | `pipeline/build_platform.py:147` (`data_basis` field on payload) | `"frozen pilot: 76 scored calls, 46 timed, 45-call blind-labeled slice"` | `"frozen calibration pilot (Hinglish task-oriented dialogue): 76 scored calls, 46 timed, 45-call blind-labeled slice — methodology proof, not clinic-domain"` | The operator looking at the workspace needs to see that the frozen pilot is the *method* proof, while Live Today is the clinic-agent slice. Rendered by `app.js:509` inside the frozen banner. |
| B3 | `pipeline/build_platform.py:508` (`aggregateView` frozen banner) | `'<span class="big">Frozen pilot</span><span>'+esc(D.data_basis||"")+'</span>'` | **UNCHANGED** (now picks up B2 automatically). | Same string; just driven by B2. |
| B4 | `pipeline/build_platform.py:508` (`aggregateView` live banner) | `'<span class="big">Live · uncalibrated</span><span>Today’s ingested calls. Diagnostic scores only — no human label or kappa yet.</span>'` | `'<span class="big">Live · uncalibrated · Aarogya clinic agent</span><span>Today’s ingested clinic appointment calls (Hinglish, Cartesia-voiced Bolna). Diagnostic scores only — no human label or kappa yet.</span>'` | Names the agent. Honest "diagnostic only" stays. |
| B5 | `pipeline/build_platform.py:453` (rail live hint) | `'<h3>Live · uncalibrated</h3><p>These calls were ingested today. No human label or kappa applies yet — treat scores as diagnostic only.</p>'` | `'<h3>Live · uncalibrated · clinic agent</h3><p>Aarogya appointment calls ingested today (Hinglish, Cartesia-voiced Bolna). No human label or kappa applies yet — treat scores as diagnostic only.</p>'` | Matches B4. |
| B6 | `pipeline/build_platform.py:478` (live-empty `<h3>` + `<p>`) | `<h3>Live Today · empty</h3><p>${note} Paste a provider execution id below to get the exact ingest + judge command. This panel only DISPLAYS the command — nothing runs from the browser.</p>` | `<h3>Live Today · empty (Aarogya clinic agent)</h3><p>${note} Paste a Bolna execution id below to get the exact ingest + judge command. This panel only DISPLAYS the command — nothing runs from the browser.</p>` | Names the agent + names the provider. |
| B7 | `pipeline/build_platform.py:484` (`cmd-note`) | `Run in the repo root, then switch back to Live Today. Live cards appear as <b>LIVE · UNCALIBRATED</b>; no human label or kappa applies until calibration.` | **UNCHANGED.** | Verbatim — honesty wording. |
| B8 | `pipeline/build_platform.py:513` (live aggregate title + subtitle) | `<h1 class="view-title">Live Today</h1><p class="subtitle">Select a live call from the rail to open its full evidence view.</p>` | `<h1 class="view-title">Live Today — Aarogya clinic agent</h1><p class="subtitle">Select a live appointment call from the rail to open its full evidence view. LIVE · UNCALIBRATED.</p>` | Names the agent + reasserts the uncalibrated lane. |
| B9 | `pipeline/build_platform.py:529` (frozen aggregate title + subtitle) | `<h1 class="view-title">Aggregate</h1><p class="subtitle">Success / friction / failure across the frozen pilot. Click any call id to open its evidence.</p>` | `<h1 class="view-title">Aggregate — frozen calibration pilot</h1><p class="subtitle">Methodology proof on Hinglish task-oriented dialogue (restaurant + travel booking) — not the clinic agent itself. Click any call id to open its evidence.</p>` | Crucial: an operator opening the frozen view must understand the frozen calls are NOT the clinic agent. |
| B10 | `pipeline/build_platform.py:545-553` (Outcome clusters section) | label `Outcome clusters`, derivation caption pulled from `D.archetypes.derivation`. | **UNCHANGED.** | Archetype derivation is verbatim-protected. |
| B11 | `pipeline/build_platform.py:560` (Friction signal clusters heading) | `Friction signal clusters (deterministic)` | **UNCHANGED.** | Deterministic-signal framing protected. |
| B12 | `pipeline/build_platform.py:578` (Cost & quality by stress profile heading) | `Cost &amp; quality by stress profile` | **UNCHANGED.** | Verbatim. |
| B13 | `pipeline/build_platform.py:599` (metric trap section) | `<h2>The metric trap</h2>` + the verbatim caption from data + the `provenance` line. | **UNCHANGED.** | Caption is verbatim-protected. |
| B14 | `pipeline/build_platform.py:606` (Improvement queue heading) | `Improvement queue (${iq.length})` | **UNCHANGED.** | Verbatim. |

### C. `pipeline/build_surface.py` — the privacy_note + generation comments

| # | file:line | current text | proposed replacement | rationale |
|---|---|---|---|---|
| C1 | `pipeline/build_surface.py:147-153` (privacy_note) | `"Every aggregate and transcript here is artifact-backed and non-fixture, with source provenance disclosed: all {N} scored calls are present (public SpokenWOZ + translated Code-Mixed-Dialog + one constructed hero + one real Bolna call), the blind-labeled and judged slice carrying its full transcript, human label, deterministic scorecard, and evidence-cited judge output."` | `"Every aggregate and transcript here is artifact-backed and non-fixture, with source provenance disclosed: all {N} scored calls (public SpokenWOZ + translated Code-Mixed-Dialog Hinglish + one constructed hero + one real Bolna call) are the **methodology proof** — they calibrate VoiceForge's loop on Hinglish task-oriented dialogue, but are NOT clinic-domain. The **live clinic calls** (Aarogya appointment agent, Cartesia-voiced Bolna, ingested today) live in a separate LIVE · UNCALIBRATED lane and never enter this frozen slice. Each frozen call carries its full transcript, blind human label, deterministic scorecard, and evidence-cited judge output."` | Embeds the two-proofs framing directly in the surface contract. No new claims. |
| C2 | `pipeline/build_surface.py:2-10` (module docstring) | `"Build the two-route product surface from the REAL committed artifacts."` etc. | Optional polish: append one paragraph explaining the two-proofs framing for future maintainers. Not user-facing — defer if time is tight. | Internal-only; low priority. |

### D. Spoken script — `docs/demo_docs.md` (Spike-facing, NOT user-facing surface, but updated for consistency)

| # | file:line | current text | proposed replacement | rationale |
|---|---|---|---|---|
| D1 | `docs/demo_docs.md:22-41` (SLIDE 1) | Opens with "Every voice agent in this room can tell you a call ended. None of them can tell you it went well." | **UNCHANGED.** Optionally add one inline beat after the introduction: `"The agent I built for today is a Hinglish appointment scheduler for a clinic and diagnostic lab. VoiceForge is the layer that tells you whether it actually worked."` | Preserves the cold-open thesis. The clinic-agent insertion lives between "who I am" and the punch line — Spike's existing steer (problem-first cold open) already supports this. |
| D2 | `docs/demo_docs.md:50-60` (SLIDE 2, "the trap") | Verbatim 25/45 and 7-of-8. | **UNCHANGED.** Optionally one beat after "Did the call hit the finish?": `"For an appointment agent, that means \"did it say 'booked'\" — not \"did the right slot, on the right date, for the right patient, actually get captured.\""` | Sharpens the metric trap to clinic appointment booking. Same 25/45 finding. |
| D3 | `docs/demo_docs.md:167-186` (SLIDE 7, Bolna × Cartesia + LIVE TODAY) | Includes the `⟨LIVE TODAY — fill in on-site if live calls happened⟩` block. | Replace the `⟨N⟩ fresh calls` placeholder with: `⟨N⟩ fresh Aarogya appointment calls through the live Cartesia-voiced Bolna agent — clean booking, code-switched, an ambiguous-request clarification, a mid-call detail change, and a refused medical-advice request — pushed through this same pipeline.` | Names the live agent + the 5 TARGET_AGENT scenarios. Honesty caveat ("uncalibrated, never touches κ") UNCHANGED. |
| D4 | `docs/demo_docs.md:190-208` (SLIDE 8, close + limits) | Lists current honest limits. | Add one limit after "Calibration is a one-rater pilot at n=45": `"The 45-call calibration is restaurant+travel booking Hinglish, not clinic-domain — it's the methodology proof; the live clinic calls today are the use-case proof."` | Two-proofs framing in the close. Strengthens honesty. |
| D5 | `docs/demo_docs.md:212-251` (Q&A KILL-LIST) | 12 Q&A bullets. | Add two clinic-specific Qs: **(a)** "Is this clinical-grade / HIPAA-ready?" → "*No, and it doesn't need to be to make the eval argument. The agent is a scheduler — it never gives medical advice, never takes payment. The prototype treats live calls as controlled test calls; production would need consent capture, PII redaction, and retention policy before judging or storage. That's already a slide.*" **(b)** "Why a clinic agent if your calibration is restaurant-booking?" → "*Two proofs, one loop. The 45 blind-labeled calls show the loop calibrates honestly on Hinglish task-oriented dialogue. The live clinic calls today show the same loop applied to the agent the judges will actually call. I never pretend the calibration is clinic-domain.*" | Pre-empts the two most likely judge probes. |

### E. Docs that are NOT user-facing but should be reframe-consistent

| # | file:line | current text | proposed replacement | rationale |
|---|---|---|---|---|
| E1 | `README.md:1-24` | "VoiceForge is the improvement-data layer for voice agents." | Add one sentence after line 8: `"This sprint, VoiceForge is applied to a Hinglish inbound appointment scheduler for a clinic and diagnostic lab (Aarogya · Cartesia-voiced Bolna). The frozen 46-call calibration is the methodology proof (restaurant + travel booking Hinglish task-oriented dialogue); the live clinic calls are the use-case proof — separate lane, LIVE · UNCALIBRATED."` | Repo-level honesty for anyone landing on the README. |
| E2 | `docs/ROOM_PLAYBOOK.md:20-30` (Your Introduction) | "I'm building VoiceForge, an evaluation and improvement layer for production voice agents." + "Most voice-agent demos stop when the call ends. VoiceForge starts there." | Optional: append a one-line clinic-agent-specific intro variant: `"Today's deliverable is an Aarogya clinic appointment agent (Hinglish, Cartesia · Devansh, Bolna-orchestrated); VoiceForge is the evaluation layer measuring it."` | Spike-facing room scripts. Low risk. |
| E3 | `docs/dataset_card.md` | Already truth-patched (line 1-13 banner). | **UNCHANGED** — but verify the banner explicitly says "calibration is restaurant-booking + travel Hinglish, not clinic-domain." (It already implies it via `cmd_hi_*` = "translated DSTC2 restaurant booking" — sufficient.) | No edit needed. |
| E4 | `docs/limitations.md` | Already truth-patched. | **UNCHANGED** — add one limitation paragraph after "Multilingual: shipped, Hindi-English majority": `"## Use-case proof is live and uncalibrated. The frozen calibration is restaurant + travel booking Hinglish (the methodology proof), not the clinic appointment agent demoed today. The clinic agent's calls live in a separate LIVE · UNCALIBRATED lane through pipeline/ingest_live.py + pipeline/judge_live.py; they never enter the frozen 46-call manifest, never touch κ, and we never claim they do. Calibration to clinic-domain is roadmap."` | This belongs in limitations.md regardless of whether anything else changes. |

---

## 3 · DO-NOT-TOUCH list (stays verbatim, no exceptions)

These strings are the load-bearing honesty of the whole demo. **Any reframe pass must keep them byte-identical.**

1. **The thesis bookend** — `"Success rate tells you whether calls finished. VoiceForge tells you how they finished, what failures cost, and what to fix first."` (Slide 1, Slide 8, `app.js:418`).
2. **The κ caption** in `report.calibration.caption` (`design_data.js:198`) — every word, especially "prevalence paradox," "balanced accuracy 0.63 (Youden's J +0.26)," "failure recall 0.50 is the more actionable number for risk surfaces," "the reliability axis is NOT language — hi-en 22/31≈71% and English 9/13≈69% are statistically indistinguishable," and "the defensible split is annotator confidence (high ≈83% vs medium ≈50%)."
3. **The metric-trap caption** (`design_data.js:207`, `app.js:112`): `"The completion heuristic — the metric most voice-agent teams ship — agrees with blind human judgment on only 25/45 calls (56%). It missed 13 real successes and passed 7 of 8 real failures. A success-rate dashboard is blind exactly where it costs money."` Numbers and phrasing locked.
4. **The truth-correction phrases**: `"71% ≈ 69%"`, `"hi-en vs English — statistically the same"`, `"83% vs 50% high vs medium annotator confidence"` (`app.js:262-265`).
5. **The prevalence-paradox sentence** at `app.js:249`: `"82% of calls succeed, so κ is mathematically crushed — the prevalence paradox. Shown low and honest, not hidden."`
6. **The "deterministic before judge" doctrine** sentences at `app.js:131-132` and 157-158.
7. **The brittle-success caption** at `app.js:316` and 191-192.
8. **The archetype derivation language** ("derived deterministically, never hand-picked").
9. **The improvement-queue framing** ("That's not a score — it's an engineering backlog, sorted by what to fix first." — `app.js:337`).
10. **Honesty wording vocabulary** — `estimated`, `heuristic`, `uncalibrated`, `measured-not-assumed`, `LIVE · UNCALIBRATED`, `pilot calibration`, `prototype`, `template-derived · requires review`, `est. spend touched by friction or failure`. All instances unchanged.
11. **dataset_card.md composition numbers**: `46 = 30 Code-Mixed-Dialog Hindi-English + 14 SpokenWOZ + 1 hero + 1 Bolna`, full corpus `76 = 44 SpokenWOZ + 30 cmd_hi + 1 Bolna + 1 hero`. Do not adjust.
12. **All κ, balanced-accuracy, Youden's J, MCC, raw-agreement, failure recall numbers** (κ 0.206, raw 0.711, balanced 0.628, J +0.257, recall 0.500, precision 0.308, specificity 0.757, F1 0.381, MCC 0.217, CI [-0.108, 0.499], n=45, friction-or-failure spend share 0.421, brittle share 0.135, cost/human-success est $0.0511, fix-first 11 calls, 183 latency + 107 barge-in, 276 judgments / 0 failures / 178 cache hits, 25/45 trap).
13. **The Bolna × Cartesia proof artifact** values (agent `199b03e7…`, synthesizer `cartesia`, voice `Devansh`, model `sonic-3`) — these come from `out/bolna_cartesia_proof.json`, a separate frozen artifact. The **live clinic agent id** (`ca9d317e-cae5-…`) is a SEPARATE id and must not replace the frozen proof's agent id. (Mentioning both is fine; conflating them is not.)
14. **The `binary_rule` language** in `judge_run` payload (`"dedicated outcome judgment per call (temperature 0, JSON, evidence-cited) … kappa calibrates THIS judgment only — the semantic dims remain uncalibrated diagnostics"`).
15. **All "single-rater," "exploratory," "uncalibrated diagnostics," "needs human review" provenance labels** on archetypes/tags/improvement-queue.

---

## 4 · Risk register — clinic-reframe traps to avoid

> Sites where a clinic reframe could accidentally claim clinical capability we don't have. Each row lists a "must not say" example, the site it could leak through, and the safe alternative.

| risk | could leak via | MUST NOT SAY | SAFE alternative |
|---|---|---|---|
| **R1 · Medical advice claim** | A21/A22 limits list, A20 live-slot copy, D5 Q&A. | "VoiceForge handles medical advice," "evaluates clinical decisions," "judges medical correctness," "scores symptom triage." | "VoiceForge evaluates the scheduler's behavior — including its refusal to give medical advice when asked (scenario 5)." Always: *behavior of the refusal*, never *correctness of the medical answer*. |
| **R2 · Diagnosis claim** | Anywhere we mention the agent's job. | "diagnoses patients," "interprets test results," "recommends medication," "triages symptoms." | "books appointments for doctor consultations, lab tests, or home sample collection." |
| **R3 · HIPAA/compliance claim** | A22 limits, README, limitations.md. | "HIPAA-ready," "HIPAA-compliant," "GDPR-ready," "PHI-safe," "encrypted at rest." | "Prototype treats live calls as controlled test calls. **Production would require** consent capture, PII redaction, and retention policy before judging or storage." (TARGET_AGENT §7 wording.) |
| **R4 · "Clinical-grade" claim** | Title, hero kicker, README. | "clinical-grade evaluation," "medical-grade calibration," "hospital-grade reliability." | "Evaluation layer for the Aarogya clinic appointment agent." No "-grade" adjectives. |
| **R5 · Calibration false-attribution** | A12 Scene 5 lede, B9 frozen aggregate subtitle. | "Calibrated on 45 clinic appointment calls," "κ measured on clinic-domain data," "appointment-booking κ = 0.206." | "Calibrated on Hinglish task-oriented dialogue (restaurant + travel booking — methodology proof, not clinic-domain). Clinic-domain calibration is roadmap." |
| **R6 · Live-calls-as-validated** | A20 live-slot, B4/B5/B8 live banner. | "Live clinic calls validate the eval layer," "Live calls confirm κ for healthcare." | "LIVE · UNCALIBRATED. Diagnostic only. Never enters the frozen manifest, never touches κ." |
| **R7 · Barge-in claim on live calls** | A8 optional addition, anywhere Bolna live calls are mentioned. | "We detect agent barge-in on the Aarogya calls," "Live overlap measurement." | "Bolna exposes no interruption telemetry; live barge-in is not claimed. Latency is reconstructed from /log event times." (Per SPRINT_CONTROL Bolna API note.) |
| **R8 · PII in transcript display** | Whenever a live call transcript is rendered in `/platform`. | (Don't display patient name + phone in screenshots/recordings.) | Today this is a controlled test call only. If shown live, redact patient name/phone in the transcript view before screenshot. **Action item for live-ingest path — not a copy fix.** Flag here for review. |
| **R9 · Cartesia/Bolna conflation** | A19 lede, frozen vs live agent ids. | "Same agent today and in the frozen proof," "live agent powers the calibration." | "Frozen proof = `199b03e7…` (cached config snapshot). Live clinic agent = `ca9d317e-cae5-…` (today). Both use Cartesia · Devansh · sonic-3; that's the link." |
| **R10 · Prevalence/generalization** | A4 hero-sub, D-row spoken script. | "Works on any voice agent," "Generalizes to all healthcare verticals," "Applies across languages." | "Applied to this clinic appointment agent — the methodology generalizes (deterministic-first, blind-calibrated, evidence-cited), but every new domain needs its own blind labels before κ applies." |

---

## 5 · Integration gate (one line + apply sequence)

**Gate (one line):** NONE of the changes catalogued in §2 are applied to source files until Codex confirms (a) the final live agent id is `ca9d317e-cae5-4953-9d5e-d60a68320b46` (or its successor), (b) the agent's knowledge base is attached and verified, and (c) the first real Bolna execution schema (`GET /executions/{id}` + `/log`) is verified end-to-end against a real test call.

**Apply sequence (after gate clears):**

1. Edit `voiceforge_design/index.html` (A1) and `voiceforge_design/app.js` (A2, A4, A5, A6 lede, A9 lede + A10 disclose chip, A12 lede, A19 lede, A20 live-slot, A22 added limit).
2. Edit `pipeline/build_surface.py` (C1 privacy_note).
3. Run `python3 pipeline/build_surface.py` → regenerates `out/surface/index.html`, `app.js`, `styles.css`, `design_data.js`. **The build_surface assertions in the script (lines 186-187) still hold** because none of the protected captions or `balanced_accuracy=0.628` change.
4. Edit `pipeline/build_platform.py` (B1, B2, B4, B5, B6, B8, B9) — these are all inside the inline INDEX_HTML/STYLES_CSS/APP_JS string blocks; the inputs (`data_basis` field) are also inside `assemble()`.
5. Run `python3 pipeline/build_platform.py` → regenerates `out/platform/{index.html, styles.css, app.js, platform_data.js}`. **Requires `out/surface/design_data.js` to exist first** (line 763 check), so the order in step 3 → step 5 is mandatory.
6. Edit `docs/demo_docs.md` (D1–D5) — Spike-facing only, no generator dependency.
7. Edit `README.md` (E1) and `docs/limitations.md` (E4) — repo-doc only, no generator dependency.
8. Smoke-check the cleared QA list from `docs/TODAY.md`: open `http://localhost:7871/` (8 scenes load, κ caption byte-identical, 25/45 caption byte-identical), open `http://localhost:7871/platform` (frozen banner reads "methodology proof," Live Today banner names the Aarogya agent + LIVE · UNCALIBRATED).
9. Run `python3 pipeline/test_live_isolation.py` to confirm frozen hashes are unchanged.

**Generator order is strict:** `build_surface.py` → `build_platform.py`. Never the reverse. Do NOT regenerate `out/dashboard.html` (fallback) or any frozen artifact (`out/judge_results.json`, `out/calls.json`, `out/analytics.json`, `out/demo_report_data.json`, `out/bolna_cartesia_proof.json`).

---

## Total copy sites catalogued

- **Surface (A):** 24 rows, of which **11 are CHANGES** (A1, A2, A4, A5, A6 lede, A9 lede, A10, A12 lede, A19 lede, A20, A22 added limit) and 13 are explicit DO-NOT-TOUCH confirmations.
- **Platform (B):** 14 rows, of which **8 are CHANGES** (B1, B2, B4, B5, B6, B8, B9 — and B3 is a passive pickup of B2) and 6 are DO-NOT-TOUCH confirmations.
- **build_surface.py (C):** 1 CHANGE (C1 privacy_note) + 1 optional comment polish (C2, skip if time-bound).
- **demo_docs (D):** 5 CHANGES (D1, D2, D3, D4, D5 — Spike-facing, no generator).
- **Other docs (E):** 2 CHANGES (E1 README, E4 limitations.md) + 1 optional (E2 ROOM_PLAYBOOK) + 1 verified-no-change (E3 dataset_card).

**Total change sites: 27 mandatory + 2 optional = 29 sites.**
