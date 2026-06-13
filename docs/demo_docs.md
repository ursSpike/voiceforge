# VoiceForge — Demo Docs (the only file Spike reads before & during the slot)

**Slot:** 10-minute window. ~6:30 spoken (390s) + ~3:30 Q&A.
**You:** Saivarshith — "Spike". This is the whole performance. Everything you say is in here, in short phrases.

---

## HOW TO READ THIS FILE (10 seconds, then forget it)

- **Bold words** = the words you lean on. Hit them a touch harder.
- `[PAUSE]` = a **silent beat**. One full breath. **This replaces every "uhh" and "um."** Silence reads as confidence; filler reads as nerves. When in doubt, pause.
- `[SLOW — explain mode]` = drop your pace, you're teaching a non-engineer (an FDE, a product person). Short sentences.
- `[PUNCH]` = the signature line. Say it like you mean it, then `[PAUSE]`.
- `[LOOK UP]` = eyes off the screen, meet the room.
- **WHAT THIS MEANS** boxes are for *you*, not the room — so you understand what you're saying. Don't read them aloud.
- The **clock** on each slide is cumulative spoken seconds. If you're ahead, add a pause. If behind, cut the parenthetical lines.

**One rule if your mind blanks:** say the thesis. *"Success rate tells you whether calls finished. VoiceForge tells you how they finished, what failures cost, and what to fix first."* Then breathe and look at the next slide title.

---

# SLIDE 1 — Thesis + who I am
**Budget: 40s · Clock: 0:40**

> Spoken:

"Hi everyone. [PAUSE] [LOOK UP]
I'm **Saivarshith** — call me **Spike**.
CSE from **IIT Kharagpur**, class of '25.
I'm an SDE at **Fujitsu Research**.
I built this **solo**. [PAUSE]

One line, and then I'll show you everything: [LOOK UP]
[PUNCH] **Success rate tells you whether calls finished.**
**VoiceForge tells you how they finished, what failures cost, and what to fix first.** [PAUSE]

Every voice agent in this room can tell you a call **ended**.
**None** of them can tell you it went **well**.
That gap — [PAUSE] — that's the whole product."

> **WHAT THIS MEANS (for you):** This is the spine. "Success rate" = the one number every team ships: did the call complete? Your claim is that that number is *blind to quality*. You are the layer that runs **after** the call and grades **how** it went. Say the one-liner exactly — it comes back at the close.

---

# SLIDE 2 — The metric trap (25 / 45)
**Budget: 45s · Clock: 1:25**

> Spoken:

"Here's the trap everyone's standing in. [PAUSE]
The metric most teams ship is **completion** — a keyword check. Did the call hit the finish?
[SLOW — explain mode] So I took that heuristic, and I took **blind human judgment** — same calls — and I asked: **how often do they agree?** [PAUSE]

[PUNCH] **Twenty-five out of forty-five.** [PAUSE]
Fifty-six percent.
It **missed 13 real successes** — calls that worked, marked as failures.
And it **passed 7 of 8 real failures** — calls that broke, marked as fine. [PAUSE] [LOOK UP]

[PUNCH] **A success-rate dashboard is blind exactly where it costs you money.**
That's not an opinion. That's 45 calls, measured."

> **WHAT THIS MEANS (for you):** The "metric trap" = the gap between *the call finished* and *the call was good*. The completion heuristic is a dumb keyword match — it sees the words "your table is booked" and says success, even when the booking had the wrong time. **25/45** is the agreement between that heuristic and a human who actually read the call. The scary half is **7 of 8 failures passed** — the heuristic is worst precisely on the calls that hurt. If asked "is the heuristic just bad?" — yes, deliberately: it's the industry-standard naive metric, and the point is that *the naive metric everyone ships is blind*.

---

# SLIDE 3 — Deterministic before judge (the architecture)
**Budget: 45s · Clock: 2:10**

> Spoken:

"So how do you grade a call **without** lying to yourself? Two rules. [PAUSE]

[SLOW — explain mode] **Rule one: never ask an AI something you can measure.**
Barge-ins — when either speaker talks over the other. Latency gaps — dead air.
Those come from **timestamp math**, not opinion. Pure arithmetic.
In this corpus: **183 latency gaps**, **107 barge-in events** — counted, not judged. [PAUSE]
*(Say it right: barge-in = speech overlap in **either** direction, reconstructed from turn
timestamps — not only the caller interrupting. If a judge probes, that precision wins points.)*

**Rule two: the AI judge runs in quarantine, and only **after** humans set the bar — blind.**
Five quality dimensions, temperature zero, every score must cite the turn it came from, and it's **validated before it's ever cached**. [PAUSE] [LOOK UP]

[PUNCH] **Deterministic before judge.**
Measure what's measurable. Judge only what's left. And calibrate even that."

> **WHAT THIS MEANS (for you):** "Deterministic-before-judge" = your core doctrine. Anything a clock or a rule can answer (barge-in, latency, did the slot get filled) is computed — it can't hallucinate. Only the genuinely subjective stuff (was the caller satisfied, did it recover well) goes to the LLM. "Temperature zero" = the judge is as deterministic as an LLM gets. "Evidence-cited / validate-before-cache" = every judgment names the turn it's based on, and a schema check rejects malformed judgments before they're stored. This is the answer to *"how do I know your eval isn't vibes?"* — most of it isn't an eval, it's arithmetic.

---

# SLIDE 4 — The hero call: a "success" that limped
**Budget: 40s · Clock: 2:50**

> Spoken:

"Let me make it concrete. One call. [PAUSE]
This is a **constructed** scenario — I'm telling you that up front, it's voiced with **Cartesia**, and it's here to show **detection**, not to pad a statistic. [PAUSE]

Completion says: **success.** The human says: **success.**
[PUNCH] But look at the shape. [PAUSE]
The caller **barged in**. There were **latency gaps** — measured, on the clock.
[SLOW — explain mode] So this is a **brittle success** — the task got done, but the caller had to **fight** for it. [PAUSE] [LOOK UP]

A pass/fail number calls this a win and moves on.
**VoiceForge calls it brittle, shows you the friction, and keeps the receipt.**"

> **WHAT THIS MEANS (for you):** `hero_001`. Human label success/high, judge says success, **but** it carries deterministic `barge_in` + `latency_gap` hits, so the system tags it **brittle_success**. This is your whole thesis in one call: "finished" and "went well" are different axes. You disclose it's constructed *every time* — that honesty is a feature, and it protects you (validity comes from the public-data calibration on Slide 5, not from this call). If asked "why a fake call?" — *"It demonstrates detection, not prevalence. Prevalence lives in the 46 blind-labeled calls."*

---

# SLIDE 5 — Blind labels + calibration (the centerpiece)
**Budget: 70s · Clock: 4:00**

> Spoken:

"This is the slide I care most about. [PAUSE] [LOOK UP]

[SLOW — explain mode] Before the judge ran, I labeled calls **blind** — IDs stripped, scores hidden, no idea what the machine thought. **46 calls. 45 usable.**
Then I asked the honest question: **does the judge agree with me?**
And I report it **measured, not assumed.** [PAUSE]

Cohen's kappa: **0.206.** [PAUSE]
[SLOW — explain mode] Now — kappa is agreement **beyond chance**. And 0.2 sounds low. Here's why I'm **showing** you a low number instead of hiding it.
My calls are **82% successes**. When one class dominates, kappa gets **mathematically crushed** — that's the prevalence paradox. It's a known artifact. [PAUSE]
So I also report the **imbalance-aware** number: **balanced accuracy 0.63.** And the one that actually matters for risk — **failure recall: the judge catches half the real failures.** [PAUSE]

[PUNCH] And here's the finding nobody expects. [LOOK UP]
You'd think the hard calls are the **Hindi-English** ones. They're **not**.
Hindi-English: **71%** agreement. English: **69%.** Statistically **the same.** [PAUSE]
The real fault line is **confidence** — where I was sure, the judge agreed **83%** of the time. Where I hesitated, **50-50.** [PAUSE]

[PUNCH] **A team trusting this judge blind would be wrong on 13 of 45 calls — and never know it.**
I know exactly which 13. That disagreement isn't noise. **It's the map of where not to trust the machine.**"

> **WHAT THIS MEANS (for you):** This is the most senior thing you say all day, so internalize it.
> - **Blind labels:** you graded the calls *before* seeing the judge, so you can't have unconsciously copied it. That's what makes the agreement meaningful.
> - **κ (Cohen's kappa) = 0.206:** agreement *corrected for luck*. A **low honest κ beats a high fake one** because a fake-high κ comes from either copying the judge or from a dataset so imbalanced you'd get high raw agreement by always guessing "success." You did neither. You're showing the real number and explaining it.
> - **Prevalence paradox:** 82% of your calls succeed. With that imbalance, κ is mechanically suppressed even when the judge is decent — so you *also* give balanced accuracy 0.63 and failure recall 0.50, which don't carry that penalty.
> - **The truth correction (memorize this — it's counterintuitive and it's yours):** language is **NOT** the reliability axis. Hindi-English (71%) and English (69%) are indistinguishable. The axis that *does* predict agreement is **your own annotator confidence** (83% vs 50%). And confidence is only known *after* labeling — so it justifies a **second-rater review queue**, not an automatic router.
> - **13/45 disagreements** = the calls where you and the judge split. That's the value, not a flaw: it tells a real team exactly where the judge is untrustworthy.

---

# SLIDE 6 — Failure phenotypes + the improvement queue
**Budget: 55s · Clock: 4:55**

> Spoken:

"Pass/fail is **one bit**. But calls don't fail one way — they fail in **shapes**. [PAUSE]

[SLOW — explain mode] Every call gets **phenotype** tags — transcript-observable, like 'repeated itself' or 'tool failed.' And from those, the system **derives an archetype**, deterministically — never hand-picked:
**seamless** success, **brittle** success, **recovered** success, **slot-loss** failure, **workflow** failure. [PAUSE]

Out of my successes, **five were brittle** — done, but the caller fought.
A success rate **hides** that. A phenotype distribution **can't**. [PAUSE] [LOOK UP]

And then the payoff. [PUNCH]
Every failure becomes a **queue entry** with evidence turns and a fix.
The system's **fix-first** pick: **poor clarification and recovery** — **11 calls**.
The fix: **'replace generic re-asks with a targeted question that names the unclear slot.'** [PAUSE]

[PUNCH] That's not a score. **That's an engineering backlog, sorted by what to fix first.**"

> **WHAT THIS MEANS (for you):** A **phenotype** = a named *shape* of behavior in a call, observable straight from the transcript (e.g. `repeated_or_stuck`, `workflow_or_tool_failed`). **Archetypes** are derived from those by fixed rules (precedence: workflow > language > slot-loss > repair-loop), so you can't cherry-pick — the code does it. **Brittle success** = passed but with friction; you have 5 of them (about 13.5% of successes). The **improvement queue** turns each failure into a concrete prompt fix with the evidence turns attached. **Fix-first** = the queue's top recommendation, ranked by how many calls and how much estimated spend it touches: `poor_clarification_or_recovery`, 11 calls. If asked how the fix is generated: it's **template-derived from the observed tags** — honest, not magic; a human reviews before shipping.

---

# SLIDE 7 — Bolna × Cartesia proof + LIVE TODAY
**Budget: 45s · Clock: 5:40**

> Spoken:

"Where do Bolna and Cartesia live in this? Three honest links. [PAUSE]
**One:** a **real Bolna execution**, pulled straight from the Bolna API into this pipeline.
**Two:** the live agent is configured with **Cartesia — voice Devansh, Sonic-3** — and the config proves it.
**Three:** the hero call is voiced with that same Cartesia voice. [PAUSE]

[SLOW — explain mode] So: **Bolna runs the calls. Cartesia gives them a voice. VoiceForge is the layer both are missing** — post-call quality, calibrated. [PAUSE] [LOOK UP]

⟨LIVE TODAY — fill in on-site if live calls happened:⟩
*"And today, on the venue network, I ran ⟨N⟩ fresh calls through the live Cartesia-voiced agent — clean, code-switched, a repair loop — pushed through this same pipeline. Timestamps prove it's from today. These are **uncalibrated** — they don't touch the frozen calibration — they're a live slice, shown separately."*
⟨If no live calls: skip this paragraph entirely — say nothing about it.⟩"

> **WHAT THIS MEANS (for you):** The sponsor proof is real and cached: agent `199b03e7…`, synthesizer **cartesia**, voice **Devansh**, model **sonic-3** (in `out/bolna_cartesia_proof.json`). The real Bolna execution predates the Cartesia voice swap — if pressed, say that plainly: *"the ingested call predates my Cartesia config; the live agent runs Cartesia today, and the config shows it."* The **LIVE TODAY** slot is your optics-and-substance move: on-site calls prove you worked today. **Critical guardrail:** live calls are **uncalibrated** and **corpus-only** — they never enter the frozen 46-call manifest and never touch κ. Say "uncalibrated," never imply they're validated.

---

# SLIDE 8 — Value, honest limits, close
**Budget: 50s · Clock: 6:30**

> Spoken:

"What's it worth, and what's it not? [PAUSE]

[SLOW — explain mode] The value: failures aren't free. Clean calls are cheap; the calls where the caller **fights** burn money. About **42% of estimated spend** sits in calls with **friction or failure**. That's the budget a success rate can't see. [PAUSE]

Now the limits — I'll say them **before** you ask. [LOOK UP]
Completion is a **heuristic**, not gold. Costs are **estimated exposure**, not measured savings. Calibration is a **one-rater pilot** at n=45. The live calls are **uncalibrated**. [PAUSE]
[PUNCH] **Every one of those is labeled in the product. Honesty is the feature.** [PAUSE]

So — to close. [LOOK UP] [PAUSE]
Thank you to **Bolna** and **Cartesia** for the platform and the voice.
[PUNCH] **Success rate tells you whether calls finished. VoiceForge tells you how they finished, what failures cost, and what to fix first.** [PAUSE]
I'd love your questions."

> **WHAT THIS MEANS (for you):** Close on the thesis, *verbatim*, same as Slide 1 — it bookends the talk. The value number is **friction-or-failure spend share = 0.42** (42%). Frame cost language carefully: it's **"estimated exposure,"** never **"savings"** — you didn't save anyone money, you *quantified where money is exposed*. **Estimated** = from public per-unit prices, not invoices. **Heuristic** = keyword rule, not ground truth. **Uncalibrated** = no human gold backs it yet. Volunteering limits first is a power move in a room of ML engineers — it signals you know exactly where your own edges are.

---

# Q&A KILL-LIST
**You have ~3:30. Answer in 2 lines, then stop talking. A short confident answer beats a long one.**
**If you don't know: "I haven't measured that — here's how I'd find out."** That answer wins respect.

**1. "How do you ensure the eval layer itself doesn't hallucinate?"** *(the one they'll ask)*
"Four ways. Most of it isn't an LLM at all — barge-ins, latency, slots are **deterministic math**. The judge runs **temperature zero**, must **cite the turn** for every score, and is **validated before caching**. And I never trust it blind — I calibrate it against **blind human labels** and **publish where it disagrees**. It's marked **uncalibrated** anywhere kappa doesn't cover it."

**2. "How does this scale to thousands of calls?"**
"The pipeline is **batch, async-ready, and cache-keyed per call and per dimension** — re-runs are nearly free. The **calibration protocol is the part that scales**: the booth, the validator, the kappa machinery don't care if n is 45 or 4,000 — you just keep labeling a sample. Live-stream ingestion is the roadmap, via **Bolna webhooks** instead of polling."

**3. "Why should I trust an LLM judge at all?"**
"You shouldn't — until it earns it. That's why blind labels come **first**, and kappa plus the confusion matrix say **exactly where** it's trustworthy. Everything else stays labeled uncalibrated."

**4. "κ is 0.2 — isn't that basically no agreement?"**
"Corrected for my **82% success prevalence**, that's a known compression — the prevalence paradox. Imbalance-aware, it's **balanced accuracy 0.63**, and **failure recall 0.50** is the number that matters for risk. A fake-high kappa would worry me more than an honest low one."

**5. "Is the success rate real?"**
"It's a documented **keyword heuristic** — likely an undercount. The point isn't the absolute number, it's that it **disagrees with humans on 25 of 45 calls** and is blind on 7 of 8 failures."

**6. "The hero call is constructed — doesn't that undercut you?"**
"It's disclosed every time, and it demonstrates **detection, not prevalence**. Prevalence comes from the **46 blind-labeled calls** (public + real, hero excluded from the prevalence claim). The hero just makes 'brittle success' tangible in one listen."

**7. "Hindi data has no timestamps — did you fabricate the timing?"**
"No — the schema enforces **all-or-none** timing. Those text-only calls carry an **`unmeasured`** profile and their timing dimensions are **omitted**, never faked. The schema *rejects* a partial clock."

**8. "Why so few labels — n=45?"**
"It's a calibration **pilot** with a bootstrap CI, not a final benchmark. The design scales unchanged; n is the one thing you grow. I'd rather show 45 honest labels than 4,000 I didn't actually read."

**9. "What's actually novel here? Isn't this an LLM wrapper?"**
"The **loop**: deterministic-first, **blind** calibration, phenotype archetypes derived from labeled primitives, into an **evidence-backed improvement queue**. Every number traces to a committed artifact. That's an eval lab, not a wrapper."

**10. "A 4-person team could build more surface — why you, solo?"**
"More surface, sure. But in **eval**, what matters is **trustworthiness per claim** — and every number here traces to a committed artifact and an audit trail. I built the thing that's hard to fake, not the thing that's easy to show."

**11. "Where exactly are Bolna and Cartesia?"**
"Three links: a **real Bolna execution** ingested from their API; the **live agent configured with Cartesia Devansh, Sonic-3** — config on request; and the **hero call voiced with that same Cartesia voice**. Bolna is the call layer I ingest from; Cartesia is the voice I evaluate."

**12. "What would you do with another week?"**
"Second rater to lift kappa off a one-person pilot, audio-native phenotypes, and **DPO preference pairs from the improvement queue** — so the eval lab starts feeding the **fix**, not just naming it."

---

# IF EVERYTHING BREAKS (offline fallback order)
1. `out/dashboard.html` — open from Finder, fully self-contained, no network.
2. `out/demo_report.html` — same numbers, static.
3. Screenshots in `reports/screenshots/`.
Talk over any of them. **The numbers are the demo, not the live server.**

# THE NUMBERS YOU MUST NOT MISQUOTE (cheat strip)
- Corpus **76** calls · **46** timed · **30** unmeasured.
- Metric trap: heuristic agrees **25/45** (56%) · missed **13** successes · passed **7 of 8** failures.
- Labels: **46** labeled · **45** binary · **37** success / **8** fail / **1** unsure.
- Calibration: κ **0.206** (CI −0.108 to 0.499) · raw agreement **0.711** · balanced accuracy **0.63** · failure recall **0.50** · n=**45**.
- Truth correction: hi-en **71%** ≈ English **69%** · confidence high **83%** vs medium **50%** · disagree on **13/45**.
- Archetypes: seamless **25** · brittle **5** · recovered **7** · slot-loss **3** · workflow **5**.
- Fix-first: `poor_clarification_or_recovery` · **11** calls.
- Failure events: latency_gap **×183** · barge_in **×107**.
- Value: friction-or-failure spend share **42%** · cost/successful call **$0.12** (estimated exposure).
- Sponsor proof: agent `199b03e7…` · **cartesia** · **Devansh** · **sonic-3**.
- Judge: gemini-3.1-flash-lite · temp 0 · **276** judgments · **0** failures.
