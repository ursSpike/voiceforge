# Product brainstorm — demo day (Jun 13), written night of Jun 12

> Status at writing: labels frozen (46 rows · 45 binary: **37 success / 8 fail** · 1 unsure, CSV SHA `b3884f9…`),
> full judge run IN FLIGHT (gemini-3.1-flash-lite, 36/276 validated at 21:45). Every number in this doc is
> derived from **committed/frozen artifacts** (`eval/labels_spike.csv`, `out/calls.json`, `out/analytics.json`)
> using the same code paths as `pipeline/demo_report.py`. **Rule: after the judge run finishes and
> `demo_report.py` regenerates, the regenerated artifact wins — never speak a number from this doc if it
> disagrees with `out/demo_report.html`.** Nothing here is invented; slots marked ⟨⟩ stay slots until filled.

---

## TOP 5 — DO TONIGHT (ranked; respect the 22:30 freeze and the 00:30 sleep gate)

| # | item | effort | why first |
|---|------|--------|-----------|
| 1 | **Batch H capture: fallback recording of /shot + the 7 screenshots** (checklist already in README_DEMO.md). Non-negotiable; the demo's insurance policy. | S (30–40 min) | Every other idea dies if audio dies and there's no catch. Already in the plan — just don't let it slip past 23:00. |
| 2 | **The "metric trap" beat** — the keyword heuristic agreed with your blind labels on only **25/45 calls (56%)**: it missed 13 real successes AND waved through 7 of your 8 real failures. Derivation below (§2.4). If freeze allows, add it as one card in `demo_report.py`; if not, it's one rehearsed sentence + the two-line derivation kept open in a terminal. | S (15 min verbal / 45 min as card) | This is the single best honest stat in the repo: it's the *reason calibrated eval exists*, computed from your own frozen artifacts, and it preempts the "is your success rate real?" question by answering it before it's asked. |
| 3 | **Rehearse the low-kappa branch out loud** (§7.1) + memorize one citation: Feinstein & Cicchetti (1990), "high agreement but low kappa." With 37/8 imbalance, kappa can come out low tonight even if the judge is good. Decide NOW what you'll say in both branches. | S (20 min) | The kappa number lands while you sleep. The difference between "my number is low" (loss) and "kappa is conservative under prevalence imbalance — here's the confusion matrix, and this is the known paradox" (win) is pure rehearsal. |
| 4 | **Lock the one-liner + the closing question** (§1.3, §4.4) and patch them into the script's open/close. | S (15 min) | Open and close are the only two moments every judge remembers. The middle is already strong. |
| 5 | **Rehearse the "show me a raw artifact" power move**: terminal with `pipeline/preflight.py` green + `out/call_swz_MUL0035.json` one keystroke away; decide the private-repo answer (zip on desktop, or flip public after SPEC scrub). | S (15 min) | This room WILL ask. Auditability is your brand — turn their hardest probe into your best moment by being visibly ready for it. |

**Optional #6 (only if all five are done before ~23:30):** one fresh, deliberately-messy, Cartesia-voiced Bolna
call ingested as call #77, kept **outside** the frozen 46-slice (manifest/CSV untouched). M effort, closes the
sponsor chain completely (§3.1). Skip without guilt — the honest chain story works without it, and post-freeze
churn is the bigger risk.

---

## 1 · PRODUCT FRAMING — how eval infrastructure beats a dementia-care story

### 1.1 The strategic read on the room

You cannot out-emotion a dementia-care agent, and you shouldn't try. The move is **aikido: make their product
your TAM.** Every team demoing tomorrow — including the dementia team — will end their demo with a call that
*sounded* fine. None of them can answer: did it work? how often? what does a failure cost? what do I fix first?
The dementia agent *especially* cannot afford brittle successes (a confused repair-loop with a dementia patient
is a safety incident, not a UX bug). You are not competing with the 22 other teams; you are the layer all 23
need. Say a version of this out loud — generously, not smugly: *"the more these agents matter, the less
acceptable 'it sounded fine' becomes."*

The judges are Bolna/Cartesia founding+senior engineers and product folks. They run a **platform**. Platforms
don't think in single agents; they think in fleets, SLAs, churn from quality incidents, and what feature makes
their customers stickier. An eval lab is a *platform feature*; a consumer agent is a *platform customer*. You're
pitching to the people who own the shelf, not a rival product on it.

### 1.2 The 30-second product read (memorize as four sentences)

- **Who uses it:** forward-deployed engineers, voice-ops teams, and eval engineers at companies running voice
  agents in production — the people who today do QA by listening to a sampled handful of calls.
- **What pain dies:** "listen-and-vibe" QA, and uncalibrated dashboard metrics nobody trusts. (Your own
  heuristic was wrong about 20 of 45 calls — §2.4. That's the pain, demonstrated on yourself.)
- **What action follows:** an evidence-backed improvement queue — each entry is a phenotype, the turns that
  prove it, and a concrete fix. An engineering backlog, not a score.
- **What business metric moves:** cost per *human-confirmed* successful call, and share of spend burned on
  failed-or-brittle calls (41% in this corpus, estimated — §2.2). Fix the queue, watch those two numbers.

### 1.3 One-liners — five candidates, ranked

1. **"Voice-agent demos stop when the call ends. VoiceForge starts there."** — WINNER, see below.
2. "Success rate tells you whether calls finished. VoiceForge tells you *how* they finished, what the failures
   cost, and what to fix first." — the given line; best as the SECOND sentence (the product unpack of #1).
3. "Pass/fail is one bit. Failure has shapes — VoiceForge measures them." — best mid-demo, introducing
   phenotypes; too abstract to open with.
4. "Every voice agent ships with a demo. VoiceForge ships with a confusion matrix." — engineer-bait, great in
   Q&A or on the calibration slide; product judges won't feel it.
5. "Bolna runs the call. Cartesia gives it a voice. VoiceForge tells you whether it worked — and what to fix
   first." — the CLOSER, not the opener (sponsor alignment lands harder at the end).

**Why #1 wins as the opener:** it indicts every other demo in the building — including the emotionally
compelling one — in nine words, without naming anyone, while defining the category ("the layer after the
call"). It's the only candidate that simultaneously differentiates against 22 agent demos AND tells the platform
judges where this sits in *their* stack. Use #1 → #2 as a one-two punch in the first 15 seconds, #4 on the
calibration slide, #5 as the final spoken line.
**Risk:** mild arrogance if delivered cold — soften with "everyone in this room built an agent this week,
mine is the one that grades them" delivered with a smile. EFFORT: S. HONESTY RISK: none (no claims).

### 1.4 Why a solo eval project reads as a COMPANY here (say these, ranked)

1. **The freeze chain** — labels frozen by SHA, manifest frozen by SHA, judge gated on byte-equality with git
   HEAD, validate-before-cache. That's not hackathon hygiene, that's eval-vendor DNA. Engineers will recognize
   it instantly. (WHY it lands: Bolna/Cartesia engineers live downstream of customers who ask "why did the
   agent do that?" — they know exactly how rare this discipline is.) EFFORT: S (one slide / one sentence).
   RISK: none.
2. **Provider-neutral schema with an all-or-none timing invariant** — "where data has no clock, timing is
   omitted, not faked; the schema *rejects* a partial clock." One sentence, enormous trust. RISK: none.
3. **Deterministic-first doctrine** — "never ask an LLM something you can measure." This room builds
   latency-sensitive infrastructure; they FEEL this rule. RISK: none.

---

## 2 · NUMBERS THAT IMPRESS WITHOUT LYING (exact card copy)

All derived from frozen `eval/labels_spike.csv` + committed `out/calls.json` / `out/analytics.json` using the
report's own archetype/tag code paths. Re-verify each against the regenerated `out/demo_report.html` tonight.
The most quotable stat SHAPE for this room: **small-integer ratios with a confessed caveat** ("1 in 3", "7 of
8", "25 of 45") — they survive being repeated to a colleague tomorrow, which is the actual test.

### 2.1 The headline trio (cards, in this order)

> **1 in 3 successes was a fight.**
> 12 of 37 human-confirmed successes carried observable friction (5 brittle + 7 recovered).
> *Single human rater, n=45 binary labels, blind protocol.*

> **41% of spend bought failure or friction.**
> $0.79 of $1.95 estimated spend on the labeled slice went to calls that failed or limped.
> *Costs estimated from public per-unit prices — prototype, not billing data.*

> **$0.053 per human-confirmed success.**
> Total labeled-slice spend ÷ 37 blind-labeled successes.
> *Estimated, prototype. Contrast: $0.119 per heuristic success on the full 76-call corpus — the gap between
> those two numbers is itself the product.*

WHY these three: product judges get cost and waste; engineers get the caveats; nobody can attack a number that
arrives pre-caveated. RISK: a judge divides $1.95 by 46 and asks why the corpus is so cheap — answer ready:
"turn-count × public unit prices on short calls; the ratios are the claim, the absolute dollars are not."

### 2.2 The Success × Friction matrix (the product-judge wow)

|  | clean | friction (≥1 negative tag) |
|---|---|---|
| **human: success** | 25 | **12** |
| **human: fail** | 1 | 7 |

(+1 unsure, friction.) Spoken line: *"Success rate collapses this 2×2 into one number and throws away the
interesting half. The top-right cell — successes with friction — is invisible to every dashboard these agents
ship with today, and it's a third of my successes."* Also note the bottom row, which is quietly profound:
**7 of 8 failures left at least one observable phenotype fingerprint.** Failures aren't mysterious; they're
under-instrumented. CAVEAT to attach: *"single-rater exploratory tags; the binary spine is what's calibrated."*
EFFORT: S (the dashboard already shows archetypes; this 2×2 is one rehearsed beat or one slide). RISK: none if
the single-rater caveat is spoken, not just printed.

### 2.3 Phenotype prevalence vs cost exposure (engineer wow)

From the labeled slice — counts are calls carrying the tag; cost exposure is estimated spend on those calls:

| negative phenotype | calls | est. spend exposed |
|---|---|---|
| poor_clarification_or_recovery | 11 | $0.47 |
| workflow_or_tool_failed | 10 | $0.34 |
| missing_or_wrong_information | 10 | $0.37 |
| repeated_or_stuck | 8 | $0.31 |
| misunderstood_user | 6 | $0.21 |
| wrong_language_or_tone | 4 | $0.22 |

Spoken line: *"Prevalence tells you what to fix; cost exposure tells you what it's worth. Bad clarification is
both the most common failure primitive and the most expensive — that's why it's at the top of the improvement
queue, with the evidence turns attached."* MANDATORY PHRASING: "estimated, prototype" on cost; "single-rater
exploratory" on tags; and if you say "fixing X would save Y," say **"modeled opportunity, not observed
savings."** RISK: do NOT sum the column (calls carry multiple tags — overlapping spend; say "exposure
overlaps" if asked).

### 2.4 THE single most quotable stat: the metric trap

> **The automated success metric was wrong about 20 of 45 calls.**
> VoiceForge's own keyword heuristic vs the blind human labels: raw agreement **25/45 (56%)** — it missed 13
> real successes *and* passed 7 of the 8 real failures. Wrong in both directions.
> *The heuristic is documented as a heuristic everywhere it appears. This gap is why the judge gets calibrated
> against blind human labels instead of trusted — and why "success rate" alone should scare you.*

Derivation (two lines, keep in a terminal — this is your receipts move):
```
labels  = eval/labels_spike.csv (frozen b3884f9…)          # human, blind
heur    = out/calls.json outcome.task_completed (committed) # keyword heuristic
# confusion on the 45 binary: h_succ/j_succ 24 · h_succ/j_fail 13 · h_fail/j_succ 7 · h_fail/j_fail 1
```
WHY this is the one: it's self-critical (credibility), it's the entire thesis in one number (uncalibrated
metrics lie), and it sets up kappa as the hero. An ML engineer hears it and immediately understands why the
calibration layer exists. EFFORT: S verbal / M to add as a report card (only if pre-freeze). RISK: a judge
says "so your dashboard's 0.566 success rate is garbage?" — the answer is YES, gladly: *"on the labeled slice
the heuristic reads 0.67 where humans say 0.82 — it's labeled 'heuristic' on every surface precisely because of
this. VoiceForge's claim is the calibrated layer, not the heuristic."* You CANNOT lose this exchange unless
you get defensive.

### 2.5 Calibration card (filled tonight — slots only)

> **Judge ↔ human agreement: κ = ⟨…⟩ (95% CI ⟨…⟩–⟨…⟩), raw agreement ⟨…⟩, n = ⟨…⟩.**
> Calibrates ONLY the judge's dedicated binary outcome judgment — the same question the blind annotator
> answered. The 5 semantic dimensions remain uncalibrated diagnostics.
> *Single rater, pilot n, class prevalence 37/8 — kappa is conservative under imbalance (see §6).*

### 2.6 Numbers to NOT headline

- **Cross-corpus cost contrast** ($0.037/success on text-Hindi vs $0.246 on interruption-stressed timed calls)
  — confounded by call length and corpus source; an engineer will spot it in seconds. Use within-timed-corpus
  contrasts only, and only with "small n per profile."
- **183 latency events / 107 barge-in events** — fine as instrumentation flexing ("signal hits, NOT failed
  calls" — the dashboard already says this), but never let them sound like a failure rate.
- Absolute dollars. $5.11 total corpus spend is a toy number; ratios only.

---

## 3 · SPONSOR ALIGNMENT — honest and strong

### 3.1 The Cartesia chain — present it proactively, in this exact order

The facts: the ingested real Bolna execution (246cd9f3) ran **before** the voice swap (ElevenLabs-era); the
LIVE Bolna agent is configured with **Cartesia Devansh / sonic-3** (set via API, verified); the hero call —
the audio the room actually hears — **is Cartesia-voiced** (re-synthesized through api.cartesia.ai). The
honest-and-strong framing is **provider-neutrality as the feature**:

> "VoiceForge is provider-neutral by design — it ate a real Bolna execution from before I swapped voices, the
> same way it would eat your customers' historical calls. The agent as it stands today speaks with Cartesia's
> Devansh on sonic-3, and every second of audio you'll hear in this demo is Cartesia."

WHY this works: you volunteer the seam before anyone finds it (auditability brand), and you convert a
chronology wrinkle into the actual product property platforms care about (ingest anything, including legacy
logs). EFFORT: S — one sentence in the ingest beat. RISK: ZERO if volunteered; REAL if discovered. Never say
"the Bolna call is Cartesia-voiced." If the optional fresh call (#6, top section) happens, the sentence
upgrades to "…and here's this morning's execution, Cartesia-voiced end-to-end, through the same pipeline."

### 3.2 What VoiceForge means FOR Bolna (pitch these, ranked)

1. **Post-call quality API** (S to pitch): every Bolna execution already emits logs VoiceForge can eat —
   webhook → scorecard + phenotype + queue entry per call. Bolna's customers get "why did call X fail" as a
   platform feature; Bolna gets the stickiest possible retention surface. *"You already have the logs. This is
   the margin on top of them."*
2. **Eval-as-a-feature / agent acceptance testing** (M): before an FDE ships a Bolna agent to a client, run it
   against a stress corpus, hand the client a calibrated scorecard. Sales enablement, not just ops.
3. **Fleet benchmarking** (roadmap framing): same pipeline, N agents, one Success×Friction matrix per agent —
   "which prompt/voice/model config limps least under interruption." Platforms monetize comparisons.

### 3.3 What VoiceForge means FOR Cartesia — honest version

Voice *synthesis* quality (pronunciation, naturalness, prosody) is **currently out of scope and labeled so** —
the judge sees text + timing, and the phenotype allowlist deliberately bans inferring audio properties from
transcripts. Pitch it as the roadmap with a concrete hook: *"The phenotype layer is designed for audio-native
dimensions it doesn't have yet — pronunciation fidelity on Indic names, prosody under interruption, voice
naturalness as a judged dimension calibrated the same way: blind human labels first. Cartesia ships the voices;
VoiceForge wants to be where 'did the voice actually land with the caller' gets measured."* The hero call's
code-switched Telugu-English with a Cartesia Indian-English voice is your one concrete exhibit: language-match
scored 0.2 by the judge — the pipeline already *notices* voice-language mismatch at the semantic level.
EFFORT: S. RISK: don't promise timelines; "designed for, not built" phrasing.

---

## 4 · DEMO CHOREOGRAPHY — 7–8 minutes, mixed panel

### 4.1 What's live vs canned (decide now, no improvising)

- **LIVE:** `/shot` money-shot page (audio + click-to-seek) · `out/demo_report.html` (static, zero network)
  · the raw-artifact open if asked (terminal ready). The dashboard (`out/dashboard.html`) is also static —
  safe to drive live.
- **SCREENSHOT/CANNED:** the labeling booth (a screenshot mid-annotation proves blindness without a live
  server) · preflight green terminal (screenshot as backup, live if smooth) · the chart PNG.
- **NEVER live:** anything needing network, the judge, or Bolna/Cartesia APIs. The demo's superpower is that
  it cannot rate-limit.

### 4.2 Beat map (wow beats in CAPS)

| time | beat | surface |
|---|---|---|
| 0:00–0:30 | One-liner #1 → #2. "Everyone here built an agent this week; mine grades them." | face, no screen |
| 0:30–1:30 | **WOW 1 — THE EAR.** /shot: play 0:15 barge-in ("hear the caller cut in — the agent keeps talking 800ms"), click-to-seek to 0:48 ("1,620ms of dead air — feel it"). Then the kicker: *"no LLM touched these numbers — they're timestamp math."* | /shot live |
| 1:30–2:30 | Pipeline strip: ingest (real Bolna execution + the provider-neutral line from §3.1) → deterministic → blind labels → gated judge → phenotypes → queue. Speak the freeze chain in one sentence. | dashboard Overview |
| 2:30–4:00 | **WOW 2 — THE TRAP, THEN THE NUMBER.** Metric-trap stat (§2.4) as the why → blind booth screenshot ("I labeled 46 calls with IDs, sources, and scores stripped — code-enforced") → confusion matrix + κ ⟨slots⟩ + CI. "I don't trust the judge. I measured how much to trust it." (One-liner #4 here.) | report/dashboard |
| 4:00–5:30 | **WOW 3 — FAILURE HAS SHAPES.** Success×Friction 2×2 → "1 in 3 successes was a fight" → archetype table (25/5/7 + 5/3/1) → one representative call card (algorithmic pick — say so). | dashboard |
| 5:30–6:30 | Improvement queue: read ONE entry aloud, evidence turns and all. Then cost: "41% of spend, estimated, bought failure or friction." | dashboard Queue |
| 6:30–7:10 | Volunteered limitations (30s — heuristic, pilot-n, single rater, constructed hero, text-only Hindi timing omitted-not-faked) → roadmap (§8, 30s). | one slide |
| 7:10–7:45 | Close: one-liner #5 (sponsor line) → **the closing question (§4.4)**. | face |

WHY this ordering: ears-first beats charts-first with ANY audience; the trap→kappa sequence makes calibration
*felt* before it's shown; phenotypes land harder after kappa establishes you measure your own trustworthiness.
The dementia team will make the room feel; the 0:48 dead-air click makes the room feel too — *viscerally* —
and then you show the receipts.

### 4.3 3-minute compression

0:00–0:20 one-liner pair → 0:20–1:00 /shot barge-in + gap → 1:00–1:50 metric trap + κ ⟨slot⟩ + confusion
matrix → 1:50–2:30 Success×Friction 2×2 + one queue entry read aloud → 2:30–3:00 limitations in one breath +
sponsor close + closing question. (Cut: pipeline strip, archetype table, representative card, chart.)

### 4.4 End on this question

> "Every demo you'll see ends with a call that sounded fine. Mine ends with a question you can take to any of
> them: **how many of your successes were brittle — and can you show me the receipts?** I'll go first: a third
> of mine, and the receipts are in the repo. Pick any call ID and I'll open the raw artifact."

WHY: it weaponizes the room's own demos as your use case, restates the headline stat, and converts Q&A into an
audit you've already rehearsed winning. RISK: cocky if rushed — deliver the "I'll go first" with self-deprecation.

### 4.5 Fallback discipline (already in README_DEMO — just rehearse the catch lines)

Audio dies → fallback recording, line: *"this is why VoiceForge caches everything — including its own demo."*
Server dies → static report from Finder. Laptop dies → screenshots on phone/USB. Every catch line should make
the failure look like the product's philosophy working.

---

## 5 · Q&A KILL-LIST — the 10 hardest questions, with answers that exist in artifacts

1. **"Why should I trust an LLM judge at all?"** (Bolna ML)
   → "You shouldn't — that's the design. The judge earns trust one dimension at a time: blind human labels
   first, then κ ⟨slot⟩ with a bootstrap CI and the full confusion matrix on its binary outcome call. The five
   semantic dimensions have no per-dimension human gold, so they're labeled *uncalibrated diagnostics* on every
   surface. The disagreement list is in the report — disagreement is information about where not to trust it."

2. **"n=45, single rater. Seriously?"**
   → "Seriously, and labeled so: it's a calibration *pilot* with a single human anchor. The point of the build
   is that the *machinery* doesn't care about n — frozen manifest, blind booth, snapshot-gated judge, kappa
   with CI run identically at n=45 or n=4,500. A second rater is the first roadmap item, and inter-HUMAN kappa
   becomes the ceiling against which the judge gets graded."

3. **"37 successes vs 8 failures — your kappa is hostage to class imbalance."** (the sharpest one)
   → "Yes — known and disclosed. With 82% prevalence, chance agreement is high and kappa gets compressed; this
   is the Feinstein–Cicchetti 'high agreement, low kappa' paradox. That's exactly why the report shows raw
   agreement AND the confusion matrix AND the CI, never kappa alone — and why prevalence-robust statistics
   (PABAK, Gwet's AC1) are named in the roadmap rather than quietly computed tonight to get a prettier number."
   *(Honesty note: name them, do NOT compute-and-quote them on stage — that's the move the question is testing.)*

4. **"Your success rate is a keyword heuristic. Isn't that garbage?"**
   → Gift question. "Mostly, yes — and I can quantify the garbage: it agreed with my blind labels on 25 of 45
   calls. It's labeled 'heuristic' on every surface, and that 56% is the strongest argument in the repo for why
   the calibrated layer exists. The product claim is the calibration discipline, not the heuristic."

5. **"The hero call is fake."**
   → "Constructed and disclosed on its own slide — it demonstrates *detection* (a barge-in and a 1.6-second
   gap you can hear and click), not prevalence. Every claim about rates comes from the public-data corpus and
   the blind labels, never from that call. Its timestamps are exact because they come from the assembly
   timeline — which is also disclosed."

6. **"SpokenWOZ is protocol-collected — your 107 barge-ins are artifacts of synthesized turn bounds."**
   → "Partly, yes: turn bounds are synthesized from word-level timestamps and the corpus has few genuine
   barge-ins — that's in limitations.md, written before the pipeline. They're counted as signal *events*, never
   as failed calls, and the genuinely-overlapped exemplar is the (disclosed) hero call. Real overlap corpora —
   AMI, and live Bolna traffic — are the roadmap fix."

7. **"Why not Langfuse / Braintrust / HoneyHive / Arize?"** (product, and the one to prepare hardest)
   → "Those are excellent *text-trace* observability tools, and VoiceForge happily coexists — but voice breaks
   their assumptions in five places. (1) **Physics**: barge-in, floor-transfer offset, dead air — timing math
   on audio timestamps; there is no span in a trace for 'the agent kept talking 800ms after the caller cut
   in.' (2) **Telephony reality**: provider log formats, expiring recording URLs, scrubbed transcripts — I
   ingest Bolna's `/log` timing because the transcript alone lies. (3) **Code-switching**: a third of this
   corpus is Hindi-English; language-match is a first-class dimension, not an afterthought. (4) **Calibration
   discipline**: their LLM-judge scores ship uncalibrated; here the judge is quarantined until blind human
   labels exist, then graded with kappa and a confusion matrix. (5) **Voice failure taxonomy**: brittle
   success, repair loop, language mismatch — phenotypes a generic 'helpfulness 4/5' will never surface. The
   provider-native dashboards have the logs but not the human-calibration loop; the eval platforms have the
   loop-shape but not the voice physics. The gap is the company."

8. **"Who pays, and how big is this?"**
   → "Three buyers, in order of reachability: voice-agent *platforms* (this is an attach-rate feature — a
   post-call quality API priced per analyzed call, riding the same unit economics Bolna already bills);
   *enterprises* running voice fleets in production, whose current QA is sampled listening by ops staff; and
   *FDEs/agencies* who need acceptance evidence to close deployments. I won't invent a TAM number on stage —
   the honest version is: every production voice deployment does QA today by listening to a sample, and that
   doesn't scale past the first thousand calls a day." *(Never quote a dollar TAM you can't source.)*

9. **"What's defensible? Anyone can call Gemini with a rubric."**
   → "The rubric call is the commodity; the moat candidates are (a) the calibration corpus — blind-labeled,
   frozen, growing with every deployment, and the disagreement set is exactly the data that improves the
   judge; (b) the phenotype taxonomy validated against human labels rather than invented; (c) the audit chain
   itself — in enterprise procurement, 'every number traces to a frozen artifact' is a feature competitors
   must rebuild culturally, not just technically. And distribution: built inside a platform's log stream, it's
   an API call away from every call the platform carries."

10. **"A 4-person team would have built more. What did solo cost you?"**
    → "Surface area — a second rater, audio-native dims, the A/B replay are all roadmap. What it bought is
    discipline-per-claim: one person CAN keep every number honest at this size, and the gates (frozen labels,
    quarantined judge, validate-before-cache) are what let this scale to a team without the honesty diluting.
    The thing eval customers buy is trustworthiness per claim, and that's what I optimized."

---

## 6 · RESEARCH CREDIBILITY — small touches for the ML judges

Ranked by signal-per-second:

1. **The ONE citation to drop verbally: Feinstein & Cicchetti (1990) — "high agreement but low kappa."**
   Say it inside the imbalance answer (Q3) or, if kappa comes out low, in the main demo. WHY this one: it's
   exactly your 37/8 situation, it's a clinical-epi classic that signals you read outside ML, and it converts
   your weakest number into evidence of statistical maturity. Runner-up: Levinson & Torreira (2015) on
   turn-taking and **Floor Transfer Offset** — but you already use "FTO" naturally in the signals beat, which
   is the better way to deploy it (terminology used casually > citation performed). Landis–Koch is already in
   limitations.md as the interpretation gate — mention only that you *refuse* to claim "substantial agreement"
   unless number AND CI clear 0.61. EFFORT: S. RISK: do not cite anything you can't say one sentence about.
2. **The prevalence-trap pre-emption** (§5 Q3) with PABAK/Gwet's AC1 *named as known alternatives, explicitly
   not computed tonight* — the restraint IS the credibility.
3. **Blind-protocol specifics**: "blindness was code-enforced — the labeling API strips call IDs, sources, and
   every score server-side; I verified zero leakage." One sentence, huge.
4. **Deterministic-first doctrine** as a stated rule, with the rubric split (3 deterministic / 5 judged) shown.
5. **Temperature-0, evidence-turn-IDs-required, validate-before-cache** — say "the judge must cite turns, and
   malformed judgments never enter the cache" — ML engineers know exactly what failure mode that kills.

---

## 7 · RISK REGISTER — top 10, each with the counter-move

1. **Kappa comes out LOW tonight.** Likeliest serious risk (37/8 compresses kappa). COUNTER: present it as a
   *finding*, with the script: "κ ⟨x⟩ — lower than raw agreement ⟨y⟩ suggests, and that gap is the
   prevalence paradox (Feinstein–Cicchetti): at 82% success prevalence, chance agreement is already high.
   The confusion matrix shows *where* the judge diverges — and an eval product that reports an honest low
   kappa is worth more than one that reports a flattering fake. This is the system working." NEVER recompute
   with a friendlier statistic tonight. Decide the branch BEFORE reading the number.
2. **Judge run incomplete/partial at freeze** (running 36/276 at 21:45; ~35min ETA, but 429s happen).
   COUNTER: the runner checkpoints atomically and the report renders PENDING honestly; demo line: "the run is
   resumable and partial-honest — here's the run manifest with expected vs validated counts." Do not
   hand-finish; do not demo a number from a partial run without saying "partial."
3. **Audio doesn't play** (the classic). COUNTER: fallback recording made TONIGHT (top-5 #1), screenshots
   layer 3, and the rehearsed catch line (§4.5). Test /shot on the demo machine in the morning (it needs the
   Range/206 server for click-to-seek — known Chrome gotcha, already solved in serve.py; do not swap servers).
4. **Live dashboard dies / file won't open.** COUNTER: dashboard and report are self-contained static HTML —
   open from Finder; keep both ALREADY OPEN in tabs before walking up. Zero network needed by design — say so.
5. **An engineer asks to see a raw artifact.** Not a risk — a TRAP YOU SET (top-5 #5). COUNTER: terminal
   pre-staged: `preflight.py` green + `cat out/call_<id>.json | head`. If they pick a call you can't open fast,
   the report's call IDs are all real — let THEM pick, that's the point.
6. **"The repo's private — how do I verify?"** COUNTER: decide tonight: scrub SPEC §1 + flip public in the
   morning, OR carry a sanitized zip. Worst answer is improvising ("uh, it's private because…"). The honest
   line: "private because it contains personal planning notes; here's the full export / it flips public today."
7. **Someone challenges the constructed hero call mid-audio** (worst moment: during WOW 1). COUNTER: the
   disclosure happens BEFORE the audio plays — one clause: "this is my constructed stress-test call —
   disclosed as constructed — listen to what the pipeline catches." Disclosed-first turns the gotcha into
   already-answered.
8. **Cross-corpus number challenge** ("your Hindi calls are cheap because they're SHORT, not because they're
   good"). COUNTER: concede instantly — it's true and §2.6 says never headline that contrast. "Correct —
   text-only calls are shorter and cost-modeled differently; that's why the report computes avg-overall on
   timed calls only and labels coverage." Conceding fast on a planted weakness buys credibility for the
   numbers you defend.
9. **Demo overruns / gets cut to 3 minutes on the spot.** COUNTER: the §4.3 compression rehearsed ONCE out
   loud tonight; know which beats die first (pipeline strip, archetype table, chart).
10. **A number on screen disagrees with your mouth.** Self-inflicted, fatal to an auditability brand.
    COUNTER: after the final regen tonight, read the demo script against `out/demo_report.html` and fill every
    ⟨slot⟩ from the screen, not from memory or from THIS DOC. The artifact wins, always.

---

## 8 · POST-HACKATHON ARC — the 30-second roadmap (say it as one breath, in this order)

> "Five steps from pilot to product: **a second human rater** — inter-human kappa becomes the ceiling the
> judge is graded against. **Audio-native phenotypes** — prosody, pronunciation on Indic names, real overlap
> from audio, scored with Cartesia in the loop and calibrated the same blind-first way. **DPO pairs straight
> from the improvement queue** — every evidence-backed failure is half of a preference pair, so the eval lab
> becomes training data. **A/B replay** — fix the prompt, re-run the same callers through the same pipeline,
> and let the Success×Friction matrix say whether it worked. And **fleet benchmarking** — every agent on a
> platform like Bolna, one scorecard, per call, as an API."

WHY this order: each step is a credible next sprint (not a fantasy), each reuses machinery the judges just
saw working, and it ends on the Bolna-shaped business. The DPO beat matters: it reframes the eval lab from
"measurement cost center" to "training-data refinery" — the framing ML engineers invest in. RISK: none if
delivered as roadmap; do not imply any of it exists.

---

*Every number in this doc traces to: `eval/labels_spike.csv` (SHA b3884f9…), `eval/label_manifest.json` (SHA
aec4ba49…), `out/calls.json`, `out/analytics.json`, `out/judge_results.json` (run manifest). Recompute nothing
by hand on stage; read everything from the regenerated report.*
