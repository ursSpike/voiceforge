# Paper decision log (Batch 6A) — what each paper is FOR, and why

6/6 verified from primary arXiv abstracts (no fabrication; findings quoted).
One verifier agent per paper; each wrote `docs/papers/<slug>.md`. No PDF/dataset downloads, no model runs.

## SpokenWOZ: A Large-Scale Speech-Text Benchmark for Spoken Task-Oriented Dialogue Agents
- **arXiv:** [2305.13040](https://arxiv.org/abs/2305.13040) — verified: True
- **Decision (role):** `dataset_dependency`
- **Why this role:** Direct dataset dependency. VoiceForge slices a small deterministic subset of SpokenWOZ's calls (word-level timestamps + speaker tags) as its public evaluation backbone. The paper is the SOURCE of the data; it does not evaluate, endorse, or validate VoiceForge.
- **Hard non-claim:** SpokenWOZ is a DATASET DEPENDENCY, not a validation. VoiceForge does NOT reproduce this paper — it does not re-run SpokenWOZ baselines and does not claim to match or beat the 25.65% / 52.1% numbers (those are the authors' own). This paper does NOT justify VoiceForge's specific timing thresholds (e.g. 100ms/800ms); those are VoiceForge's own design choices, justified separately by deterministic-first design plus human calibration, not by appeal to this paper. Coverage caveats: SpokenWOZ is protocol-collected (latency-rich, not interruption-rich) and English-only; barge-in / multilingual coverage comes from other pool members.

## τ-Voice: Benchmarking Full-Duplex Voice Agents on Real-World Domains
- **arXiv:** [2603.13686](https://arxiv.org/abs/2603.13686) — verified: True
- **Decision (role):** `motivation`
- **Why this role:** Independent benchmark preprint that MOTIVATES why voice-agent evaluation matters by quantifying a large voice-vs-text capability gap. It does NOT validate VoiceForge: VoiceForge does not run τ²-bench, the τ-Voice simulator, GPT-5, or any of the 278 tasks, and shares only the problem framing, not the methodology or data.
- **Hard non-claim:** This paper does not validate VoiceForge and VoiceForge does not reproduce it (no τ²-bench run, no τ-Voice simulator, no GPT-5, none of the 278 tasks). None of its numbers measure VoiceForge's accuracy or correctness — it establishes that the problem matters, not that our solution works. It does NOT justify VoiceForge's specific deterministic thresholds (e.g. 100ms/800ms FTO bands); those are VoiceForge's own design choices. Scope differs: τ-Voice evaluates end-to-end agent task completion on a synthetic-simulator benchmark, whereas VoiceForge analyzes real call transcripts/timing for deterministic failure signals.

## VoiceAgentBench: Are Voice Assistants ready for agentic tasks?
- **arXiv:** [2510.07978](https://arxiv.org/abs/2510.07978) — verified: True
- **Decision (role):** `motivation`
- **Why this role:** Motivation only. This paper frames the multilingual/Indic agentic-voice evaluation problem (existing speech benchmarks "do not systematically evaluate agentic behavior or adversarial robustness"). It does NOT validate VoiceForge; VoiceForge does not reproduce or score against this benchmark.
- **Hard non-claim:** VoiceForge does NOT reproduce, re-run, or score against VoiceAgentBench, and makes no claim to its results (the 60.6% figure is the paper's own evaluated pipelines). This paper does NOT justify VoiceForge's specific thresholds (e.g., 100ms/800ms latency gates) — those are VoiceForge's own design choices. Honesty context: SpokenWOZ is a dataset dependency; the benchmark papers (this one) motivate but do not validate; judge-bias papers justify deterministic-first + human calibration.

## WildSpeech-Bench: Benchmarking End-to-End SpeechLLMs in the Wild
- **arXiv:** [2506.21875](https://arxiv.org/abs/2506.21875) — verified: True
- **Decision (role):** `motivation`
- **Why this role:** Motivation only — frames why text-adapted benchmarks miss speech-specific phenomena, motivating the need for real-world speech-LLM evaluation. Does NOT validate VoiceForge.
- **Hard non-claim:** This paper MOTIVATES the problem; it does NOT validate VoiceForge. VoiceForge does not reproduce this benchmark, its dataset, or its results, and does not run WildSpeech-Bench or replicate its query-aware evaluation. It does NOT justify any of VoiceForge's specific thresholds (e.g. 100ms/800ms latency cutoffs). The abstract gives no numeric headline statistic, so no percentage/score should be attached to this citation.

## A Survey on LLM-as-a-Judge
- **arXiv:** [arXiv:2411.15594](https://arxiv.org/abs/2411.15594) — verified: True
- **Decision (role):** `judge_bias_justification`
- **Why this role:** JUSTIFIES VoiceForge's deterministic-first stance plus human calibration. The survey treats LLM-as-judge reliability — specifically bias mitigation and consistency — as an open challenge requiring careful design and standardization, which supports leading with deterministic signals rather than trusting an LLM judge by default.
- **Hard non-claim:** Justifies the deterministic-first + human-calibration posture only; does NOT validate, evaluate, or measure VoiceForge. Provides NO support for VoiceForge's exact thresholds (e.g. 100ms/800ms). VoiceForge does NOT reproduce this paper or its benchmark. The finding is qualitative framing, not a measured statistic. Not the SpokenWOZ dataset dependency and not one of the three benchmark problem-motivation papers.

## Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge
- **arXiv:** [2410.02736](https://arxiv.org/abs/2410.02736) — verified: True
- **Decision (role):** `judge_bias_justification`
- **Why this role:** JUSTIFIES VoiceForge's deterministic-first design and blind-human-label calibration pilot. Because LLM judges carry 12 documented, persistent bias types, VoiceForge keeps load-bearing signals (barge-in, latency, turn accounting) deterministic and calibrates the LLM judge against blind human labels rather than trusting it. Does NOT validate VoiceForge or reproduce any result.
- **Hard non-claim:** Paper JUSTIFIES the deterministic-first + human-calibration posture; it does NOT validate VoiceForge, reproduce any VoiceForge result, or measure VoiceForge's own judge. It does NOT justify any specific VoiceForge threshold (e.g. 100ms/800ms) — those are VoiceForge's own design choices. We do not claim to reproduce CALM or its numbers.

## Decisions, stated plainly
- **SpokenWOZ → product.** Our public backbone (44 normalized calls sliced from it). The ONLY paper VoiceForge depends on.
- **τ-Voice / VoiceAgentBench / WildSpeech-Bench → motivation + Q&A armor.** They establish the problem is real and unsolved (voice-text gap, Indic degradation, the lack of specialized end-to-end speech-LLM benchmarks). Cited to justify that voice-agent eval matters — never to claim our numbers match theirs.
- **LLM-judge survey / Justice-or-Prejudice → deterministic-first justification.** They document LLM judges are biased/unreliable — exactly why VoiceForge keeps timing/overlap/slots DETERMINISTIC and calibrates the judge against blind human labels.
