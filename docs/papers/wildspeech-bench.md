# WildSpeech-Bench

**Role for VoiceForge:** Motivates the real-world speech-LLM evaluation need. Does **NOT** validate VoiceForge.
**Category:** motivation

## Citation

- **Title:** WildSpeech-Bench: Benchmarking End-to-End SpeechLLMs in the Wild
- **Authors:** Linhao Zhang, Jian Zhang, Bokai Lei, Chuhan Wu, Aiwei Liu, Wei Jia, Xiao Zhou
- **arXiv ID:** arXiv:2506.21875
- **Date:** Submitted 27 Jun 2025 (v1); last revised 26 Sep 2025 (v3)
- **Link:** https://arxiv.org/abs/2506.21875

## Verified finding (quoted from the abstract)

> "the lack of specialized and comprehensive benchmarks for end-to-end speech LLM evaluation hinders optimizing the user experience of Audio LLMs in real-world applications. Existing evaluation methods often adapt text-based benchmarks, overlooking speech's unique characteristics and challenges, including prosody, homophones, stuttering, and differing user expectations."

Supporting result (quoted):

> "We conduct comprehensive testing and detailed analysis of various mainstream speech models, revealing significant differences in model performance across different speech scenarios."

Note: the abstract is qualitative — it reports no single headline numeric statistic (e.g. no accuracy/percentage figure) for this finding. The claim above is reproduced verbatim rather than paraphrased or quantified.

## What VoiceForge can use from this paper

- A peer-reviewed-style framing that text-adapted benchmarks miss speech-specific phenomena (prosody, homophones, stuttering, differing user expectations) — this motivates *why* a real-world speech-LLM evaluation harness is worth building at all.
- The paper's "query-aware evaluation" idea (customized checklists/prompts per query) is conceptual support for VoiceForge's deterministic-first + per-scenario evaluation stance — as inspiration only, not as a method VoiceForge reimplements.
- Evidence that mainstream speech models differ significantly across speech scenarios, supporting the general argument that scenario-stratified evaluation matters.

## Demo / Q&A use

When asked "why does evaluating a speech LLM need its own harness instead of reusing text benchmarks?", cite this paper: it documents that existing methods adapt text-based benchmarks and thereby overlook speech-unique challenges (prosody, homophones, stuttering, user expectations). Use it to motivate the problem space — not to claim VoiceForge solves or reproduces it.

## LIMITATION / NON-CLAIM

- This paper **MOTIVATES** the problem of real-world speech-LLM evaluation. It does **NOT** validate VoiceForge, and VoiceForge does **NOT** reproduce this benchmark, its dataset, or its results.
- VoiceForge does not run WildSpeech-Bench, does not use its data, and does not replicate its query-aware evaluation method.
- This paper does **NOT** justify any of VoiceForge's specific thresholds (e.g. 100ms / 800ms latency cutoffs). No threshold in VoiceForge is derived from or endorsed by this work.
- The abstract provides no numeric headline statistic; do not attach a fabricated percentage or score to this citation.
- Distinct from other cite-card papers: SpokenWOZ is a dataset dependency; the benchmark papers (including this one) motivate the problem but do not validate VoiceForge; the judge-bias papers justify the deterministic-first + human-calibration approach.
