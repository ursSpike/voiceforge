# Paper decision log (Batch 6A) — what we decided each paper is FOR, and why

| paper | arXiv | decision (role) | why this role | hard non-claim |
|---|---|---|---|---|
| SpokenWOZ: A Large-Scale Speech-Text Ben | [2305.13040](https://arxiv.org/abs/2305.13040) | **dataset_dependency** | Direct dataset dependency. VoiceForge slices a small deterministic subset of SpokenWOZ's calls (word-level timestamps + speaker tags) as its public ev | SpokenWOZ is a DATASET DEPENDENCY, not a validation |
| τ-Voice: Benchmarking Full-Duplex Voice  | [2603.13686](https://arxiv.org/abs/2603.13686) | **motivation** | Independent peer benchmark that MOTIVATES why voice-agent evaluation matters by quantifying a large voice-vs-text capability gap. It does NOT validate | This paper does not validate VoiceForge and VoiceForge does not reproduce it (no τ²-bench run, no τ-Voice simulator, no  |
| VoiceAgentBench: Are Voice Assistants re | [2510.07978](https://arxiv.org/abs/2510.07978) | **motivation** | Motivation only. This paper frames the multilingual/Indic agentic-voice evaluation problem (existing speech benchmarks "do not systematically evaluate | VoiceForge does NOT reproduce, re-run, or score against VoiceAgentBench, and makes no claim to its results (the 60 |
| WildSpeech-Bench: Benchmarking End-to-En | [2506.21875](https://arxiv.org/abs/2506.21875) | **motivation** | Motivation only — frames why text-adapted benchmarks miss speech-specific phenomena, motivating the need for real-world speech-LLM evaluation. Does NO | This paper MOTIVATES the problem; it does NOT validate VoiceForge |
| A Survey on LLM-as-a-Judge | [arXiv:2411.15594](https://arxiv.org/abs/2411.15594) | **judge_bias_justification** | JUSTIFIES VoiceForge's deterministic-first stance plus human calibration. The survey treats LLM-as-judge reliability — specifically bias mitigation an | Justifies the deterministic-first + human-calibration posture only; does NOT validate, evaluate, or measure VoiceForge |
| Justice or Prejudice? Quantifying Biases | [2410.02736](https://arxiv.org/abs/2410.02736) | **judge_bias_justification** | JUSTIFIES VoiceForge's deterministic-first design and blind-human-label calibration pilot. Because LLM judges carry 12 documented, persistent bias typ | Paper JUSTIFIES the deterministic-first + human-calibration posture; it does NOT validate VoiceForge, reproduce any Voic |

## Decisions, stated plainly
- **SpokenWOZ → product.** It IS our public backbone (44 normalized calls sliced from it). The only paper VoiceForge depends on.
- **τ-Voice / VoiceAgentBench / WildSpeech-Bench → motivation + Q&A armor.** They establish the problem is real and unsolved (voice-text gap, Indic degradation, missing e2e speech benchmarks). We cite them to justify that voice-agent eval matters — never to claim our numbers match theirs.
- **LLM-judge survey / Justice-or-Prejudice → the deterministic-first justification.** They document that LLM judges are biased/unreliable. That is exactly why VoiceForge keeps timing/overlap/slots DETERMINISTIC and calibrates the judge against blind human labels — the judge is the secondary, audited layer.

## Verification meta
- 6/6 papers fetched + verified from their primary arXiv abstract (no fabrication; findings quoted).
- One verifier agent per paper; each wrote docs/papers/<slug>.md. No PDF/dataset downloads, no model runs.
