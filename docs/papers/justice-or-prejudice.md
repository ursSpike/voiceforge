# Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge

**Role in VoiceForge's cite-card:** `judge_bias_justification` — justifies the
deterministic-first design and the blind-human-label calibration pilot.

## Citation

- **Title:** Justice or Prejudice? Quantifying Biases in LLM-as-a-Judge
- **Authors:** Jiayi Ye, Yanbo Wang, Yue Huang, Dongping Chen, Qihui Zhang,
  Nuno Moniz, Tian Gao, Werner Geyer, Chao Huang, Pin-Yu Chen, Nitesh V. Chawla,
  Xiangliang Zhang
- **arXiv ID:** arXiv:2410.02736
- **Submitted:** v1 — 3 Oct 2024; v2 — 4 Oct 2024
- **Link:** https://arxiv.org/abs/2410.02736

## Verified finding (quoted from the abstract)

The paper identifies a concrete set of bias types in LLM judges and builds a
framework to measure them:

> "we identify 12 key potential biases and propose a new automated bias
> quantification framework-CALM-which systematically quantifies and analyzes
> each type of bias in LLM-as-a-Judge by using automated and principle-guided
> modification."

And on the persistence of bias even in strong models:

> "the results indicate that while advanced models have achieved commendable
> overall performance, significant biases persist in certain specific tasks."

> "Empirical results suggest that there remains room for improvement in the
> reliability of LLM-as-a-Judge."

The abstract states **12** bias types and frames the framework as **CALM**. It
does **not** publish a single headline bias percentage in the abstract, so no
numeric bias rate is quoted here.

## What VoiceForge can use from this paper

This paper supports two of VoiceForge's design choices — it does **not** validate
VoiceForge's outputs.

- **Deterministic-first.** Because LLM judges carry measurable, persistent biases
  ("significant biases persist in certain specific tasks"), VoiceForge keeps the
  load-bearing signals — barge-in detection, latency math, turn accounting —
  deterministic and computed from timestamps, not delegated to the LLM judge. The
  judge is used only for the softer rubric dimensions where a deterministic rule
  does not exist.
- **Blind human calibration.** Because judge reliability has "room for
  improvement," VoiceForge does not treat the LLM judge's scores as ground truth.
  It runs a blind-human-label calibration pilot (one binary dimension, small n,
  Cohen's kappa with a bootstrap CI) to anchor the judge against human agreement
  rather than assuming it.

## Demo / Q&A use

- One-liner for the cite-card / slide: *"LLM-as-judge has 12 documented bias types
  (arXiv:2410.02736), and significant biases persist even in advanced models —
  which is why VoiceForge computes the deterministic signals itself and calibrates
  the LLM judge against blind human labels instead of trusting it outright."*
- If asked "why not just let the LLM grade everything?": cite this paper's finding
  that biases persist in specific tasks even for strong models; that is the reason
  the deterministic spine exists and the judge is calibrated, not trusted.

## LIMITATION / NON-CLAIM

- This paper **justifies** VoiceForge's deterministic-first + human-calibration
  posture. It does **not** validate VoiceForge, reproduce any VoiceForge result, or
  measure VoiceForge's own judge. We do not claim to reproduce CALM or any of its
  numbers.
- This paper does **not** justify any specific VoiceForge threshold (e.g. the
  100 ms / 800 ms latency cutoffs). Those thresholds are VoiceForge's own design
  choices and are out of scope for this citation.
- The "12 biases" and the persistence-of-bias claims are the paper's findings about
  LLM judges in general; they are evidence for *why* we hedge the judge, not
  evidence about VoiceForge's accuracy.
- Honesty context for the wider cite-card: SpokenWOZ is a **dataset dependency**;
  the three benchmark papers **motivate** the problem but do **not** validate
  VoiceForge; this paper (and the other judge-bias papers) **justify**
  deterministic-first + human calibration. No paper in the set certifies
  VoiceForge's thresholds or reproduces its results.
