# τ-Voice — cite-card (role: MOTIVATION)

> **Why it's here:** motivates *why* voice-agent evals matter by quantifying the
> voice-vs-text capability gap. It **does NOT validate VoiceForge** — see the
> LIMITATION / NON-CLAIM section.

## Citation
- **Title:** τ-Voice: Benchmarking Full-Duplex Voice Agents on Real-World Domains
- **Authors:** Soham Ray, Keshav Dhandhania, Victor Barres, Karthik Narasimhan
- **arXiv ID:** arXiv:2603.13686 (v1)
- **Submitted:** 14 Mar 2026
- **Primary category:** cs.SD (Sound); secondary cs.AI
- **Link:** https://arxiv.org/abs/2603.13686

## Verified finding (quoted from the abstract)
> "We evaluate task completion (pass@1) and voice interaction quality across 278
> tasks: while GPT-5 (reasoning) achieves 85%, voice agents reach only 31--51%
> under clean conditions and 26--38% under realistic conditions with noise and
> diverse accents--retaining only 30--45% of text capability; qualitative
> analysis confirms 79--90% of failures stem from agent behavior..."

Headline (verbatim numbers, no rounding): on the same grounded tasks, a strong
**text** agent (GPT-5 reasoning) hits **85%** pass@1, while **voice** agents hit
only **31–51%** clean / **26–38%** realistic — i.e. they retain just **30–45%**
of text capability, and **79–90%** of failures are attributed to agent behavior.
The benchmark spans **278 tasks** and extends τ²-bench into a full-duplex voice
setting with a controllable, non-real-time voice user simulator.

## What VoiceForge can use from this paper
- **The "why" for the whole product.** A peer benchmark independently measures a
  large, quantified voice-vs-text gap (retaining only 30–45% of text capability).
  That is the external evidence that evaluating voice agents *separately from
  text agents* is a real, unsolved problem — which is the premise VoiceForge is
  built on.
- **Framing for the demo/pitch:** "voice agents lose more than half their
  text-mode capability, and ~80–90% of the failures are the agent's own
  behavior — yet most teams have no deterministic way to see those failures."
  VoiceForge positions itself as the deterministic-first lens on exactly that
  failure surface (FTO timing, task-outcome, slot-capture).
- **Vocabulary alignment:** confirms the field's framing — full-duplex,
  turn-taking dynamics, grounded multi-turn tasks, voice-vs-text comparison —
  which VoiceForge's call → task-outcome → slot-capture → failure-story pipeline
  speaks to.

## Demo / Q&A use
- **One-liner (slide / verbal):** "An independent 2026 benchmark, τ-Voice
  (arXiv:2603.13686), finds voice agents retain only 30–45% of text-mode
  capability across 278 grounded tasks. Evaluating voice agents is a real,
  unsolved problem — that's the gap VoiceForge tooling targets."
- **If asked "is this just your opinion that voice evals are hard?":** cite the
  85% (text) vs 31–51% / 26–38% (voice) split and the 79–90% agent-behavior
  failure share — these are *their* numbers, not ours.
- **Keep the verbatim numbers** (85%, 31–51%, 26–38%, 30–45%, 79–90%, 278
  tasks). Do not round or paraphrase them in the pitch.

## LIMITATION / NON-CLAIM (read before citing)
- **VoiceForge does not reproduce τ-Voice.** We do not run τ²-bench, the τ-Voice
  user simulator, GPT-5, or any of the 278 tasks. This paper supplies the
  *motivation*, not a result we replicated.
- **This paper does not validate VoiceForge.** None of its numbers measure
  VoiceForge's accuracy, coverage, or correctness. It establishes that the
  *problem* matters; it says nothing about whether *our* solution works.
- **No threshold endorsement.** τ-Voice does not justify VoiceForge's specific
  deterministic thresholds (e.g. 100 ms / 800 ms FTO bands). Those are
  VoiceForge's own design choices and must be defended on their own terms.
- **Different scope.** τ-Voice evaluates *end-to-end agent task completion* on a
  synthetic-simulator benchmark; VoiceForge analyzes *real call transcripts /
  timing* (SpokenWOZ + provider logs) for deterministic failure signals. The
  overlap is the shared problem framing, not the methodology or data.
- **Role recap of the cite-card set (honesty rules):** SpokenWOZ is a *dataset
  dependency*; the three benchmark papers (incl. this one) *motivate* the
  problem but do not validate VoiceForge; the judge-bias papers *justify*
  deterministic-first + human calibration.
