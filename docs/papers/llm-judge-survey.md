# LLM-as-a-Judge Survey — cite-card source

**Role for VoiceForge:** `judge_bias_justification` — documents that LLM-as-a-judge
evaluation has reliability issues (bias, inconsistency) that must be actively
mitigated. This *justifies* VoiceForge's deterministic-first stance plus human
calibration. It does **not** validate VoiceForge.

## Citation

- **Title:** A Survey on LLM-as-a-Judge
- **Authors:** Jiawei Gu, Xuhui Jiang, Zhichao Shi, Hexiang Tan, Xuehao Zhai,
  Chengjin Xu, Wei Li, Yinghan Shen, Shengjie Ma, Honghao Liu, Saizhuo Wang,
  Kun Zhang, Yuanzhuo Wang, Wen Gao, Lionel Ni, Jian Guo
- **arXiv ID:** arXiv:2411.15594
- **Submitted:** v1 — 23 Nov 2024 (latest version v6 — 19 Oct 2025; verified 2026-06-11)
- **Link:** https://arxiv.org/abs/2411.15594

## Verified finding (quoted from the abstract)

> "However, ensuring the reliability of LLM-as-a-Judge systems remains a
> significant challenge that requires careful design and standardization."

And, on the mitigation strategies the survey surveys:

> "We explore strategies to enhance reliability, including improving
> consistency, mitigating biases, and adapting to diverse assessment
> scenarios."

These are exact quotes from the arXiv abstract page (no rounding, no
embellishment). The abstract frames the survey around the question "How can
reliable LLM-as-a-Judge systems be built?" — i.e. reliability is treated as an
open problem, not a solved one. The abstract explicitly names *bias* and
*consistency* as things that must be mitigated/improved.

## What VoiceForge can use from this paper

- A peer-surveyed source establishing that LLM-as-judge evaluation carries
  documented reliability concerns — specifically the need to mitigate **bias**
  and improve **consistency** — rather than being a drop-in trustworthy oracle.
- Justification for VoiceForge putting **deterministic checks first** and
  treating any LLM-based judgment as something requiring **human calibration**,
  consistent with the survey's framing that reliability "requires careful design
  and standardization."
- A citable anchor for the talking point: "the field itself treats judge
  reliability as an open problem that needs design + standardization, so we lead
  with deterministic signals."

## Demo / Q&A use

If asked "why not just use an LLM to grade the outputs?": cite this survey to
note that LLM-as-a-judge reliability is a documented open challenge — the
literature itself calls for mitigating bias and improving consistency. That is
exactly why VoiceForge grades deterministically first and uses human
calibration on top, rather than trusting an LLM judge by default.

## LIMITATION / NON-CLAIM

- This is a **judge-bias justification** paper. It motivates *why* a
  deterministic-first + human-calibration posture is reasonable. It does
  **NOT** validate VoiceForge, evaluate VoiceForge, or measure VoiceForge's
  accuracy.
- The survey does **NOT** endorse any specific numeric threshold. It provides
  **no** support for VoiceForge's exact thresholds (e.g. 100ms / 800ms). Do not
  cite it for those.
- VoiceForge does **NOT** reproduce this paper, its benchmark, or any result in
  it. The survey mentions "a novel benchmark designed for this purpose";
  VoiceForge neither runs nor reproduces that benchmark.
- The quoted finding is qualitative (the survey's framing of reliability as a
  challenge). It is not a quantitative result; do not present it as a measured
  statistic.
- This paper is **not** the SpokenWOZ dataset dependency and is **not** one of
  the three benchmark "problem-motivation" papers — keep those roles distinct.
