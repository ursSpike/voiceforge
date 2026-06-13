# ROOM PLAYBOOK — read in the cab

## Your Center

You are not trying to prove that you know everything about voice AI.

You are showing that you can:

- find a real systems problem;
- build a functioning evaluation loop;
- measure where your own machinery is weak;
- communicate evidence and limitations clearly;
- learn quickly from people who know the domain better.

Before entering: shoulders down, breathe out slowly, walk at a normal pace, and look at people rather
than scanning for status. Curiosity reads as confidence. Rushing reads as fear.

## Your Introduction

### 10 seconds

“Hi, I’m Saivarshith — Spike. I’m an SDE at Fujitsu Research and an IIT Kharagpur CSE graduate. I’m
building VoiceForge, an evaluation and improvement layer for production voice agents.”

### 25 seconds

“Most voice-agent demos stop when the call ends. VoiceForge starts there. It turns call logs into
measured timing signals, blind human outcomes, evidence-cited judge results, failure phenotypes, and
an improvement queue. The simple question is not just ‘did the call finish?’ but ‘how did it finish,
what went wrong, and what should the team fix next?’”

### Non-technical version

“It is quality control after a voice-agent call. A normal dashboard says the call completed.
VoiceForge shows whether the caller had to repeat themselves, whether the agent recovered, and which
problem should be fixed first.”

### Engineer version

“Provider logs normalize into one call schema. Timing and task signals are deterministic. Semantic
judgment is evidence-cited and cached only after validation. A dedicated binary judge is compared
against blind human labels; live sprint calls stay in a separate uncalibrated lane.”

## Your Fujitsu Line

Keep confidential work confidential:

“At Fujitsu Research I work as an SDE. I’m especially interested in reliable agent systems,
evaluation, multilingual interaction, and converting model behavior into evidence an engineering
team can act on. VoiceForge is my way of exploring that end to end.”

If asked for project specifics you cannot share:

“I can explain the engineering themes, but I keep internal project details confidential.”

## What To Say To Different People

### Bolna founder or senior leader

Opening:

“I’m treating Bolna as the call/orchestration layer and building the quality loop that begins after
the execution finishes.”

Questions:

- What failure do customers complain about most after an agent reaches production?
- What do customers currently inspect manually?
- Which outcome or webhook becomes the operational source of truth?
- Do teams optimize completion, conversion, containment, or something more domain-specific?
- Which part of VoiceForge would be most useful inside Bolna rather than as a separate product?

### Bolna engineer or Buddy

Start with the concrete need:

“I have an isolated live-eval lane ready. I need to verify the exact execution and log endpoints before
I depend on it.”

Ask:

- What are the authoritative execution-detail and execution-log endpoints?
- Is there a supported list-latest-executions endpoint and stable execution ID field?
- Does telemetry expose explicit interruption/barge-in events, or only component timestamps?
- Are synthesizer request/response timestamps audio-ready time or playback time?
- Can I retrieve a recording URL, and how long does it remain valid?
- What webhook payload would you recommend for production post-call evaluation?
- Are there rate limits or venue-network constraints I should know?

Repeat their answer back before coding:

“So the supported contract is X, the ID field is Y, and overlap is/isn’t directly observed — correct?”

### Cartesia engineer

- Which voice/model characteristics matter most for conversational agents rather than TTS samples?
- What telemetry would separate synthesis latency from orchestration and playback latency?
- How should teams test code-switching or pronunciation without confusing ASR and TTS failures?
- Which failure should never be blamed on the voice model without audio evidence?

### Founder from another team

- Who is the user and what painful moment made you choose this?
- Who buys it, who uses it, and who blocks deployment?
- What changed in the prototype after you spoke to a real user?
- What is the one claim you can demonstrate today?
- What would you remove if you had half the time?

Share, do not pitch at them:

“That’s interesting. My project attacks a different layer: I’m building the instrumentation that
shows whether voice-agent behavior is actually improving.”

### Engineer from another team

- What part was unexpectedly difficult?
- Which API or model behavior was least predictable?
- What did you cache for demo safety?
- Which metric do you distrust?
- What would you test with one more hour?

Offer one useful observation from VoiceForge, then stop. Good conversations are exchanges, not
mini-presentations.

### Product or FDE person

- What would make this usable by an operations team on Monday?
- Which view should be aggregate and which should be call-level?
- What evidence would a customer need before accepting an automated recommendation?
- Where should a human review step sit?
- What is the shortest path from a detected failure to a changed prompt or workflow?

## Strong Conversation Moves

- Ask one specific question based on what they just said.
- Reflect the answer: “So the real bottleneck is X, not Y?”
- Admit boundaries: “I haven’t measured that yet.”
- Connect without hijacking: “That maps to a failure mode I saw in my calls.”
- Exchange contact only after a real conversation: “I’d like to follow your work — are you on X or
  LinkedIn?”
- Exit cleanly: “I’m going to run another call before the sprint ends. Great meeting you.”

## Avoid

- Do not lead with the number of agents, commits, tools, or hours.
- Do not compare yourself to the dementia-care team or diminish another product.
- Do not claim savings, production validation, or multilingual generalization.
- Do not defend every weakness. Name it, state the next measurement, move on.
- Do not use “AI agents built this.” Say what **you designed, verified, measured, and decided**.
- Do not fill silence with technical detail. Pause.

## Confidence Under Pressure

- Slow down the first two sentences.
- Put both feet on the floor before answering.
- If a question is unclear: “Do you mean the evaluation metric or the production workflow?”
- If you do not know: “I haven’t measured that. I would test it by …”
- If challenged on low kappa: “Exactly. I measured that the judge is not ready to be trusted blindly.”
- If the demo breaks: open `out/dashboard.html` and continue the story.
- If you lose your place: repeat the thesis and move to the next section.

Your goal is not to appear finished. Your goal is to appear rigorous, useful, and easy to work with.

## Lower-Level Technical Questions Smart Engineers May Ask

Keep each answer to two or three sentences. Add detail only if they ask again.

### “What exactly is the timing primitive?”

“Floor-transfer offset: `next.start_ms - previous.end_ms`. Positive means silence; negative means
overlap. VoiceForge derives latency and overlap events from that primitive where a shared clock exists.”

### “Are those timestamps actually observed?”

“It depends on the source and the provenance is shown. Bolna timing is reconstructed from timestamped
component events; SpokenWOZ is reconstructed from word timestamps; the hero has an authored assembly
timeline. Text-only calls carry null timing and omit timing dimensions.”

### “Can you really detect barge-in from the Bolna web call?”

“Not reliably from the current web-call trace. I can reconstruct response gaps, but I will only claim
live barge-in if Bolna confirms explicit interruption telemetry or I have aligned audio.”

### “Why 100 ms overlap and 800 ms latency?”

“They are prototype operating thresholds, not values claimed from a paper. A threshold sweep showed
the failure clusters remain reasonably stable under nearby settings; production thresholds would be
validated against domain-specific human labels.”

### “Why median and p90 instead of average latency?”

“A mean hides the tail and is sensitive to one extreme stall. Median describes the normal exchange;
p90 exposes the experience of the slowest common responses.”

### “What happens if half the turns have timestamps?”

“The schema rejects a partial clock. A call must be fully timed or explicitly unmeasured, so the
pipeline cannot accidentally connect two turns across a missing timestamp.”

### “How is the provider-neutral schema useful?”

“Provider-specific payloads are adapters at the boundary. Downstream evaluation reads the same call,
turn, outcome, signal, cost, failure and provenance fields, so Bolna or another provider does not
require rewriting the evaluation engine.”

### “What exactly is deterministic and what is judged?”

“Timing, turn structure, slot evidence and the prototype task-completion heuristic are deterministic.
Language match, faithfulness, repair quality, conciseness and user frustration are semantic judge
dimensions, and they remain explicitly uncalibrated diagnostics.”

### “Why call task completion a heuristic?”

“For most current calls it checks whether required values or keywords appear in the dialogue. It is
reproducible but not gold dialogue state, and its disagreement with blind humans is the metric-trap
finding. A source-grounded outcome probe is researched but not integrated.”

### “How do you stop the judge from hallucinating evidence?”

“Every response must satisfy a strict JSON contract, scores must be numeric and in range, and at least
one evidence turn must exist in that call. Invalid or entirely hallucinated evidence is rejected before
the response reaches cache.”

### “Can stale cache entries silently survive prompt changes?”

“The cache key includes call, dimension, model, temperature and prompt hash. Cache hits are revalidated
against the current call; invalid entries are deleted and fetched again.”

### “Why Gemini 3.1 Flash Lite?”

“It supported the complete evidence-cited JSON run within available throughput. Model identity,
temperature, prompt hash, rubric hash and completion counts are recorded in the run artifact; the
design is model-replaceable.”

### “What does kappa calibrate?”

“Only the dedicated binary success/fail outcome judgment, because that is the question answered by the
blind human labels. It does not calibrate the five semantic dimensions.”

### “Why is kappa low when raw agreement is 71%?”

“The sample is 37 successes to 8 failures, so agreement from the dominant class is cheap and kappa is
compressed. I therefore report the confusion matrix, balanced accuracy 0.628 and failure recall 0.50
alongside κ 0.206 and its confidence interval.”

### “How was the confidence interval produced?”

“A deterministic seeded bootstrap resamples the 45 human/judge pairs with replacement, recomputes
kappa, and uses the percentile interval. It includes zero, so I do not claim statistically established
agreement at this sample size.”

### “Is one human annotator enough?”

“Enough for an honest pilot, not a production benchmark. There is no human-human agreement estimate;
the next step is a second-rater queue prioritized by ambiguous or disagreement-heavy calls.”

### “How did you avoid label leakage?”

“The human booth served stripped raw transcripts without scores, failures, deterministic timing or
judge output. Labels and their manifest were frozen and hash-pinned before the real judge run.”

### “What protects the frozen experiment during today’s calls?”

“Live calls write under `data/normalized/live/` and separate `out/live_*` artifacts. The frozen pipeline
uses a non-recursive top-level glob, and a regression test proves the live and calibration sets are
disjoint.”

### “Could call IDs or caches collide?”

“The live contract requires `bolna_live_<execution-prefix>` inside the JSON as well as in its path.
Call identity, model and prompt hashes participate in cache identity, and this is explicitly tested
before the live route is cleared.”

### “What if the live API fails?”

“The live slice is an enhancement, not a dependency. The frozen 76-call corpus, calibrated pilot and
audited dashboard are cached locally and remain fully demoable offline.”

### “Are the costs real?”

“Mostly estimated prototype exposure from turn counts and public unit assumptions; one Bolna execution
contains observed provider cost. I never call the extrapolation savings.”

### “What does the improvement queue actually generate?”

“A deterministic mapping from observed negative phenotype tags to a recommended change and expected
mechanism, with the supporting calls attached. It requires human review and is not an automatic prompt
deployment system.”

### “Are you already producing DPO training data?”

“No. The shipped artifact is an evidence-backed improvement queue. Preference-pair export and training
are post-hackathon work after better outcomes, more labels and review.”

### “What about audio quality, accent or background noise?”

“Those signals are unavailable for nearly all of the current pool, so I do not infer them from text.
Audio-native evaluation requires recordings and separate human/audio metrics.”

### “How would this scale operationally?”

“Replace manual execution-ID fetches with Bolna webhooks, process calls asynchronously, and keep the
per-call/per-dimension cache. Human review becomes selective: sample routine calls and prioritize
judge disagreement, uncertainty and high-cost failure phenotypes.”

### “What prevents PII from leaking into reports or model calls?”

“The prototype uses public/constructed data plus a controlled Bolna call; production needs a redaction
stage and retention policy before judging. Raw provider payloads and sanitized reporting artifacts
should have separate access controls.”

### “What is the strongest thing here and the weakest?”

“Strongest: the auditable loop from deterministic signals and blind labels to measured judge failure
and actionable examples. Weakest: small single-rater calibration and heuristic outcomes. Both are
visible in the product rather than hidden.”

## Sharper / business questions (a mixed founder + senior-eng room WILL ask these)

### “How is this different from LangSmith / Langfuse / Helicone — isn’t this just LLM observability?”

“Those trace tokens and text. VoiceForge judges the conversation *trace* — timing, overlap, latency,
task outcome, cost — the voice-native failures a text logger structurally can’t see, and it calibrates
its own judge against blind human labels instead of trusting it. Observability tells you what happened;
this tells you how it failed, what it cost, and what to fix first.”

### “Why should Bolna care — where does this sit in your product?”

“Bolna ships the agent; teams still fly blind after the call. This is the post-call evaluation and
improvement layer: ingest an execution, surface failure phenotypes, hand back ranked, evidence-cited
fixes. Natural fit as a Bolna-native eval/observability surface fed by your webhooks.”

### “What does Cartesia get out of this?”

“A latency-and-quality lens on synthesized calls — VoiceForge measures response gaps and overlap on
real traces, so TTS latency wins show up as measured eval improvements, not just a spec number. Honestly:
today Cartesia runs inside the Bolna synthesizer, so I verify that from config rather than assume it.”

### “Why optimize for failure recall over precision?”

“In a quality surface, a missed failure is the expensive error — it ships to a user. So I report failure
recall (0.50 here) prominently and accept lower precision, and I show the full confusion matrix so you
can pick the operating point. It’s a deliberate, visible tradeoff, not an accident of the data.”

### “How does code-switching actually break a normal eval?”

“A keyword/intent rule tuned on English silently mis-scores Hinglish — wrong language, wrong slot
matches. 30 of my 46 labeled calls are Hindi-English exactly to test that. The honest finding: my judge
holds up (hi-en 71% ≈ English 69%) — language wasn’t the reliability axis; annotator confidence was.”

### “The judge only sees text + timing, not audio — doesn’t it miss tone and prosody?”

“Yes, and that’s why prosody-sensitive judgments stay deterministic where possible and the judge is
marked uncalibrated where blind labels don’t cover it. Aligned-audio judging is roadmap. I’d rather
under-claim than grade tone from a transcript.”

### “Is this an A/B harness — can I compare two agent versions?”

“The shape is there: same scenario, change the agent prompt, re-run, re-score through the same machinery
— that’s the Sprint-2 before/after. I frame it as one demonstrated scenario, not a measured lift; a real
A/B needs many calls and human review, which is the natural next build.”
