# VoiceForge — 7–8 minute demo script (skeleton; final numbers filled in Batch H)

> Fill `⟨⟩` slots from out/demo_report.html after the real label+judge run. NEVER speak a number
> that isn't in a committed artifact.

## 0:00–0:45 · The problem
"Everyone in this room built a voice agent in the last two days. Every one of those demos ends the
same way — the call ends, everyone smiles, nobody knows if it actually *worked*. Production teams
run thousands of calls a day and their eval is 'listen to a few and vibe.' **Most voice-agent demos
show a cherry-picked call. VoiceForge shows the failure distribution.**"

## 0:45–1:40 · Thesis + ingest
"VoiceForge is the layer AFTER the call: an eval lab for voice agents. It eats call logs —
provider-neutral — and turns them into measurements, calibrated judgments, and an improvement queue.
In this corpus: a **real Bolna call** (Cartesia Devansh voice), 44 SpokenWOZ task calls, 30
Hindi-English code-switched restaurant bookings, and one constructed hero call — **disclosed** as
constructed. 76 calls, every artifact cached and reproducible offline."

## 1:40–2:40 · Deterministic before semantic + blind labeling
"Rule one: never ask an LLM something you can measure. Barge-ins and response latency come from
timestamp math — FTO between turns. [show /shot: 0:15 barge-in, 0:48 gap, click-to-seek.]
Rule two: never let the judge grade before humans set the bar **blind**. [show /label] The booth
strips call IDs, sources, scores — I labeled ⟨N⟩ calls without seeing anything the judge produced.
And where data has no timestamps — the Hindi-English text corpus — timing is **omitted, not faked**:
those calls carry an `unmeasured` profile."

## 2:40–3:50 · Calibration (the centerpiece)
"Now the judge: 5 semantic dimensions, temperature 0, evidence turn IDs required, validated before
caching — those five stay labeled **uncalibrated diagnostics**, because I have no per-dimension human
gold. What I CAN calibrate is the judge's **binary outcome call** — the same success/fail question I
answered blind — and that's this number: Cohen's kappa against my blind labels.
⟨κ = …, CI …–…, raw agreement …, n = …⟩. [show confusion matrix] Here's where we disagreed —
⟨disagreement example⟩ — and that disagreement is *information*: it tells you exactly where not to
trust the judge."

## 3:50–5:30 · Phenotypes (the differentiator)
"Pass/fail is one bit. Calls fail in *shapes*. Every call gets phenotype tags — independent,
transcript-observable primitives — and VoiceForge derives archetypes deterministically:
**seamless success, brittle success, recovered success, language-mismatch failure, slot-loss
failure, repair-loop failure, workflow failure.** [show archetype table + tag bars]
⟨X⟩ of my successes were *brittle* — the task completed but the caller fought for it. A success
rate hides that; a phenotype distribution doesn't. Even my two seed calls: both successes, both
tagged `wrong_language_or_tone` + `mixed_languages` — success with friction, measured."

## 5:30–6:40 · Representative calls + improvement queue
"Representatives are picked **algorithmically** — first call per archetype in manifest order — so I
can't cherry-pick. [show cards] Each failure becomes an improvement-queue entry: evidence turns,
the phenotype, and a concrete fix — ⟨read one: e.g. 'cap repeats at 2, then rephrase with a
concrete example'⟩. That's an engineering backlog, not vibes."

## 6:40–7:30 · Cost, limitations, future
"Cost per *successful* call — estimated, prototype — splits by stress profile: clean calls are
cheap, interruption-heavy calls burn money. [chart] Honest limits: completion is a keyword
heuristic; calibration is a one-rater pilot at n≈40; the judge stays labeled uncalibrated where
kappa doesn't cover it. Next: second rater, audio-native phenotypes, DPO pairs from the queue,
A/B re-run of fixed prompts through this same pipeline."

## 7:30–8:00 · Close
"Bolna runs the calls. Cartesia gives them a voice. **VoiceForge tells you which ones worked, which
ones limped, and what to fix first.** I don't label calls pass/fail — I phenotype them. That's how
a solo ships an eval lab in two days. Questions?"

---

## 60-second compressed pitch
"Voice-agent demos stop when the call ends; VoiceForge starts there. It ingests call logs from any
provider, measures what's measurable — barge-ins, latency, slots — deterministically, then runs an
LLM judge that is *calibrated against my own blind labels* (Cohen's kappa, confusion matrix, n≈40)
instead of trusted blindly. Every call gets a phenotype — seamless, brittle, recovered, slot-loss,
repair-loop, workflow failure — derived deterministically from labeled primitives. The output isn't
a score, it's an improvement queue with evidence turns. Real Bolna call ingested, Cartesia-voiced,
fully offline-reproducible. Pass/fail is one bit; failure has shapes."

## Likely judge Q&A (answers grounded in artifacts)
- **"Why trust an LLM judge?"** → I don't, until it earns it: blind labels first, kappa + CI + the
  confusion matrix say exactly where it's trustworthy; everything else stays marked uncalibrated.
- **"Is the success rate real?"** → It's a documented keyword heuristic — likely an undercount; the
  point is the *relative* ordering across stress profiles, and it's reproducible byte-for-byte.
- **"Constructed hero call?"** → Yes, disclosed on its own slide; validity comes from the public-data
  calibration, not that call. It demonstrates detection, not prevalence.
- **"Hindi data has no timing — did you fake it?"** → No: schema-level all-or-none invariant; those
  calls carry `unmeasured` and timing dimensions are omitted; the schema *rejects* a partial clock.
- **"Why so few labels?"** → n≈40 is a calibration *pilot* with a bootstrap CI; the design scales —
  the booth, validator, and kappa machinery don't care if n is 40 or 4,000.
- **"What's actually novel?"** → The loop: deterministic-first + blind calibration + phenotype
  archetypes derived from labeled primitives → an evidence-backed improvement queue. Not a wrapper.
- **"Couldn't a 4-person team build more?"** → More surface, sure. The thing that matters in eval is
  *trustworthiness per claim* — every number here traces to a committed artifact and an audit trail.
