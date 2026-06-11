# VoiceAgentBench

**Intended role for VoiceForge:** Motivates multilingual / Indic agentic-voice evaluation framing.
**Category:** motivation
**This paper MOTIVATES the problem. It does NOT validate VoiceForge.**

---

## Citation

- **Title:** VoiceAgentBench: Are Voice Assistants ready for agentic tasks?
- **Authors:** Dhruv Jain, Harshit Shukla, Gautam Rajeev, Ashish Kulkarni, Chandra Khatri, Shubham Agarwal
- **arXiv ID:** arXiv:2510.07978
- **Date:** Submitted 9 Oct 2025 ([v1]); last revised 13 Feb 2026 ([v3])
- **Link:** https://arxiv.org/abs/2510.07978

---

## Verified finding (quoted from the abstract)

> "Across agentic tasks, ASR-LLM pipelines outperform end-to-end SpeechLMs, achieving up to 60.6% average parameter-filling accuracy on English, while SpeechLMs exhibit lower performance and sharper degradation on Indic languages. All models struggle in sequential workflows and safety evaluations, highlighting persistent limitations in tool orchestration, multilingual generalization, and safety robustness."

Additional verbatim detail from the abstract: the benchmark comprises "6,000+ synthetic spoken queries spanning single-tool invocations, multi-tool workflows, multi-turn dialogue, and safety evaluations across English and six Indic languages."

---

## What VoiceForge can use from this paper

- **Problem framing:** Existing speech benchmarks "largely focus on isolated capabilities such as transcription or question answering and do not systematically evaluate agentic behavior or adversarial robustness." This grounds why an agentic-voice evaluation lens is worth building toward at all.
- **Multilingual / Indic motivation:** The paper documents "sharper degradation on Indic languages" and "persistent limitations in ... multilingual generalization." VoiceForge can cite this as evidence that multilingual (including Indic) agentic-voice evaluation is an open, real problem — i.e., motivation for the framing, not a benchmark VoiceForge runs against.
- **Evaluation dimensions vocabulary:** The paper's measured dimensions — "tool selection accuracy, structural consistency, and the correctness of tool invocations, including adversarial robustness" — are useful as a vocabulary reference when describing what an agentic-voice evaluation should care about.

---

## Demo / Q&A use

If asked in a demo "why does multilingual / Indic agentic-voice evaluation matter?", cite VoiceAgentBench: a 6,000+ query benchmark across English and six Indic languages showing that even the best pipeline reaches only "up to 60.6% average parameter-filling accuracy on English" and that models show "sharper degradation on Indic languages" with all models struggling on "sequential workflows and safety evaluations." Use this to motivate the problem space — NOT to claim VoiceForge solves or measures any of it.

---

## LIMITATION / NON-CLAIM

- This paper **motivates** the multilingual/Indic agentic-voice problem; it does **NOT validate VoiceForge**. VoiceForge does not reproduce, re-run, or score against VoiceAgentBench.
- VoiceForge makes **no claim** to reproduce any result, number, or benchmark from this paper (e.g., the 60.6% figure describes the paper's evaluated ASR-LLM pipelines, not VoiceForge).
- This paper does **NOT** justify any of VoiceForge's specific thresholds (e.g., 100ms / 800ms latency gates). Those thresholds are VoiceForge's own design choices and are not derived from or endorsed by this paper.
- Honesty context for the cite-card set: SpokenWOZ is a **dataset dependency**; the three benchmark papers (this one included) **motivate** the problem but do not validate VoiceForge; the judge-bias papers **justify** deterministic-first scoring plus human calibration.
