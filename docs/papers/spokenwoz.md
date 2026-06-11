# SpokenWOZ — cite-card (VoiceForge's public backbone)

**Role for VoiceForge:** `dataset_dependency`. SpokenWOZ is the public dataset
VoiceForge's normalized SpokenWOZ calls are sliced from. This is a **direct
dependency**, not a validation of VoiceForge.

---

## Citation

- **Title:** *SpokenWOZ: A Large-Scale Speech-Text Benchmark for Spoken
  Task-Oriented Dialogue Agents*
- **Authors:** Shuzheng Si, Wentao Ma, Haoyu Gao, Yuchuan Wu, Ting-En Lin,
  Yinpei Dai, Hangyu Li, Rui Yan, Fei Huang, Yongbin Li
- **arXiv id:** arXiv:2305.13040
- **Submitted:** 22 May 2023 (v1). Last revised: 24 Jun 2025 (v7).
- **Link:** https://arxiv.org/abs/2305.13040
  (DOI: https://doi.org/10.48550/arXiv.2305.13040)
- **Project / dataset:** https://spokenwoz.github.io/

---

## Verified finding (quoted from the abstract)

> "we introduce SpokenWOZ, a large-scale speech-text dataset for spoken TOD,
> containing 8 domains, 203k turns, 5.7k dialogues and 249 hours of audios from
> human-to-human spoken conversations."

Supporting result, quoted verbatim from the same abstract:

> "the most advanced dialogue state tracker only achieves 25.65% in joint goal
> accuracy and the SOTA end-to-end model only correctly completes the user
> request in 52.1% of dialogues."

These figures are reported by the SpokenWOZ authors. They describe the dataset
and the difficulty of the SpokenWOZ benchmark — they say nothing about
VoiceForge.

---

## What VoiceForge can use from this paper

- **A real spoken task-oriented dialogue corpus** — human-to-human
  booking/info tasks (8 domains), with word-level timestamps and speaker tags.
  VoiceForge slices a small, deterministic subset of these calls as the public
  backbone of its evaluation pool.
- **The motivation framing**, in the authors' own words: there is "a gap
  between academic research and real-world spoken conversation scenarios," and
  prior spoken-TOD work "ignore[s] the unique challenges in spoken
  conversation." This is the gap VoiceForge's call → task-outcome →
  failure-story pipeline operates in.
- **Word timestamps** that let VoiceForge synthesize turn boundaries and
  compute real timing signals (latency/overlap) from data rather than inventing
  them. (See `docs/dataset_card.md` for exactly which fields are used vs
  ignored.)

---

## Demo / Q&A use

- **Cite-card line:** "Our public backbone is SpokenWOZ (arXiv:2305.13040) — a
  large-scale speech-text spoken-TOD benchmark: 8 domains, 203k turns, 5.7k
  dialogues, 249 hours. We slice a small deterministic subset of its calls."
- **If asked 'is this a real dataset or did you make it up?':** real, published,
  CC BY-NC 4.0, with word-level timestamps — that is why we can derive timing
  instead of fabricating it.
- **If asked 'how hard is this problem?':** quote the authors' own numbers —
  the best DST reaches only 25.65% joint goal accuracy and the SOTA end-to-end
  model completes the user request in only 52.1% of dialogues. The headroom is
  large, by the dataset authors' own measurement.

---

## LIMITATION / NON-CLAIM (read before citing)

- **SpokenWOZ is a DATASET DEPENDENCY, not a validation.** VoiceForge uses
  SpokenWOZ calls as input. This paper does **not** evaluate, endorse, or
  validate VoiceForge in any way.
- **VoiceForge does not reproduce this paper.** We do not re-run SpokenWOZ's
  baselines, do not reproduce its 25.65% / 52.1% numbers, and do not claim our
  pipeline matches or improves on any SpokenWOZ result. Those numbers are the
  authors' own, reported here only to characterize the dataset's difficulty.
- **This paper does not justify VoiceForge's thresholds.** Nothing in SpokenWOZ
  endorses VoiceForge's specific timing thresholds (e.g. 100ms / 800ms). Those
  are VoiceForge's own design choices and must be justified separately
  (deterministic-first design + human calibration), not by appeal to this
  paper.
- **Coverage caveats** carried from `docs/dataset_card.md`: SpokenWOZ is
  protocol-collected (latency-rich, **not** interruption-rich) and is English.
  VoiceForge's barge-in / multilingual coverage comes from other pool members,
  not from this dataset.
