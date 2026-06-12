# VoiceForge Research Verification — Primary Paper Verifier (Agent 5)

Date: 2026-06-13. All six papers verified against their PRIMARY arXiv pages only (no blogs/vendor/secondary sources). Evidence drawn from arXiv abstract/HTML pages.

VoiceForge frozen artifacts referenced throughout: 46-call slice; 45 binary human labels (37 success / 8 fail); binary judge calibrated vs blind human (Cohen's κ=0.206, n=45); 5 semantic judge dims (uncalibrated diagnostics) + binary judge run; deterministic timing on 46 timed calls (barge-in/latency); 3 languages (en, hi-en, te-en) with tiny per-language n; single human rater with confidence levels.

## Summary table

| Paper | One-line use for VoiceForge | Sufficient with current artifacts? |
|---|---|---|
| 1. Balanced Accuracy (Youden's J) | Report balanced accuracy / Youden's J beside κ for the binary judge | YES |
| 2. Trust or Escalate | Selective-escalation routing: trust confident judge calls, escalate the rest | PARTIAL (need judge confidence + budget tier) |
| 3. TD-EVAL | Source-grounded turn-level checks (backend-consistency / policy / cohesion) | NO (need turn-level transcripts + backend state) |
| 4. Full-Duplex-Bench | Timing-threshold taxonomy for barge-in / pause / interruption metrics | PARTIAL (taxonomy framing yes; reference SDM benchmark no) |
| 5. Multilingual LLM-as-a-Judge | Language-normalized slice reporting; flag low-resource fragility | PARTIAL (framing yes; per-language n too tiny for stable κ) |
| 6. SemEval-2023 Task 11 (LeWiDi) | Disagreement-preserving second-rater / soft-label schema | NO (single rater; need 2nd annotator) |

All six papers: VERIFIED.

---

## Paper 1 — Balanced Accuracy: The Right Metric for Evaluating LLM Judges

**(a) Citation / version.** Collot, S., Fraser, C., Zhao, J., Shen, W. F., Willi, T., & Leontiadis, I. "Balanced Accuracy: The Right Metric for Evaluating LLM Judges — Explained through Youden's J statistic." arXiv:2512.08121. v1 submitted 2025-12-08; v2 (current) 2026-01-19. Subjects: cs.LG, cs.AI, cs.CL. Title note: arXiv title carries a subtitle ("— Explained through Youden's J statistic") beyond the short title given.

**(b) VERIFIED finding.** The abstract argues that Accuracy, Precision, and F1 are "sensitive to class imbalance and to arbitrary choices of positive class" and can distort prevalence estimates, whereas "Youden's J statistic is theoretically aligned with choosing the best judge" and Balanced Accuracy is an equivalent linear transformation of it; selecting judges via Balanced Accuracy gives more robust classifier selection.

**(c) Relevance to VoiceForge.** Balanced-accuracy beside kappa. VoiceForge's binary judge is calibrated on a class-imbalanced slice (37 success / 8 fail ≈ 82/18). κ alone is hard to interpret at that prevalence; balanced accuracy / Youden's J = sensitivity + specificity − 1 directly handles the imbalance and the arbitrary positive-class choice (success vs fail).

**(d) NON-CLAIM.** Does NOT prove VoiceForge's judge is good, nor that balanced accuracy on n=45 is statistically stable. It is a metric-selection argument; it says nothing about VoiceForge's specific judge quality, its semantic dims, or small-sample confidence intervals.

**(e) Implementable experiment.** From the existing 45 paired (human binary, judge binary) labels, build the 2x2 confusion matrix and compute sensitivity, specificity, balanced accuracy, and Youden's J. Report these alongside the existing κ=0.206, with bootstrap CIs over the 45 pairs. Show how the prevalence-naive accuracy headline differs from balanced accuracy.

**(f) Data prerequisites.** Paired human-vs-judge binary labels with a fixed positive-class convention. Already present.

**(g) Sufficiency.** YES. The 45 binary labels are exactly the input this method consumes. Only caveat to surface: n=45 means wide CIs (especially specificity, driven by just 8 fails); report intervals, don't over-claim.

---

## Paper 2 — Trust or Escalate: LLM Judges with Provable Guarantees for Human Agreement

**(a) Citation / version.** Jung, J., Brahman, F., & Choi, Y. "Trust or Escalate: LLM Judges with Provable Guarantees for Human Agreement." arXiv:2407.18370. v1 submitted 2024-07-25. Subjects: cs.LG, cs.CL. Title matches.

**(b) VERIFIED finding.** The abstract proposes assessing judge confidence and selectively deciding trustworthiness, giving "provably guaranteed human alignment at user-specified levels." Mechanisms: Simulated Annotators (better confidence estimation) and Cascaded Selective Evaluation (cheap model first, escalate to stronger model when needed). Even with a budget model (Mistral-7B) the method reaches >80% human agreement at ~80% coverage on Chatbot Arena subsets where GPT-4 alone falls short.

**(c) Relevance to VoiceForge.** Selective-escalation routing. VoiceForge could trust the judge only on high-confidence calls and route low-confidence calls to a stronger judge or to human review, trading coverage for guaranteed agreement — directly attacking the low κ=0.206 by abstaining where the judge is unsure.

**(d) NON-CLAIM.** Does NOT prove VoiceForge can hit any agreement guarantee — the guarantee requires a calibration set and a confidence signal VoiceForge does not yet log per call. It also does not address multilingual or voice/timing aspects. The Chatbot-Arena coverage numbers do not transfer to VoiceForge's domain or sample size.

**(e) Implementable experiment.** Re-run (or post-hoc derive) a confidence score per judge verdict (e.g., self-reported confidence or agreement of repeated samples = the "simulated annotators" proxy), then sweep a confidence threshold over the 45 calibration pairs: at each threshold report coverage (fraction auto-judged) vs agreement-with-human on the covered subset. Produce a coverage-vs-agreement curve and pick the threshold meeting a target (e.g., 90% agreement).

**(f) Data prerequisites.** A per-verdict confidence signal (re-sampled judge votes or logged token/confidence) AND the human calibration labels. Calibration labels exist; the confidence signal is NOT in the frozen run.

**(g) Sufficiency.** PARTIAL. The 45 human labels suffice as the calibration target, but the frozen judge run does not include per-call confidence or repeated samples. Missing: a confidence/abstention signal — requires either re-querying the judge (out of scope: no API calls) or having logged it. With current frozen artifacts you can describe the method and define the threshold sweep, but cannot execute the routing curve without the confidence column.

---

## Paper 3 — TD-EVAL: Revisiting Task-Oriented Dialogue Evaluation

**(a) Citation / version.** Acikgoz, E. C., Guo, C., Dey, S., Datta, A., Kim, T., Tur, G., & Hakkani-Tür, D. "TD-EVAL: Revisiting Task-Oriented Dialogue Evaluation by Combining Turn-Level Precision with Dialogue-Level Comparisons." arXiv:2504.19982. v1 submitted 2025-04-28; v2 (current) 2025-07-16. Subjects: cs.CL, cs.AI. Title note: full arXiv title is longer than the short "TD-EVAL" label given.

**(b) VERIFIED finding.** TD-EVAL combines fine-grained turn-level analysis with dialogue-level comparison. Turn level scores three dimensions: conversation cohesion, backend knowledge consistency, and policy compliance; dialogue level uses a "TOD Agent Arena" for pairwise comparison. On MultiWOZ 2.4 and tau-Bench it surfaces errors missed by conventional metrics and aligns better with human judgment.

**(c) Relevance to VoiceForge.** Source-grounded turn checks. The "backend knowledge consistency" and "policy compliance" turn dimensions map onto grounding VoiceForge's per-turn judge dims against the agent's backend/tool state rather than only against the final outcome — converting VoiceForge's uncalibrated semantic dims into source-grounded turn-level checks.

**(d) NON-CLAIM.** Does NOT validate VoiceForge's 5 semantic dims, nor does it provide a turn-level metric for VoiceForge's data. TD-EVAL is grounded in datasets that carry backend DB state and policies (MultiWOZ/tau-Bench); it does not claim anything about call-level voice transcripts lacking that structured state.

**(e) Implementable experiment.** For a handful of VoiceForge calls, segment into turns and have the judge score each turn on cohesion / backend-consistency / policy-compliance, then check whether per-turn failures predict the call-level human fail label — i.e., does turn-level signal localize the 8 failures better than the single binary?

**(f) Data prerequisites.** Turn-segmented transcripts AND a backend/policy ground-truth (tool calls, DB results, allowed-action policy) per turn. VoiceForge has call-level audio/transcripts but no frozen turn-segmentation or structured backend-state ground truth.

**(g) Sufficiency.** NO. The frozen artifacts are call-level (46 calls, call-level binary + dims). Missing: turn segmentation and a backend/policy reference to check "consistency/compliance" against. Would require new annotation/instrumentation, which is out of scope here.

---

## Paper 4 — Full-Duplex-Bench

**(a) Citation / version.** Lin, G.-T., Lian, J., Li, T., Wang, Q., Anumanchipalli, G., Liu, A. H., & Lee, H.-y. "Full-Duplex-Bench: A Benchmark to Evaluate Full-duplex Spoken Dialogue Models on Turn-taking Capabilities." arXiv:2503.04721. v1 submitted 2025-03-06; v3 (current) 2025-08-16. Subjects: cs.CL, eess.AS. Title matches.

**(b) VERIFIED finding.** The abstract introduces Full-Duplex-Bench, which "systematically evaluates key interactive behaviors: pause handling, backchanneling, turn-taking, and interruption management," using automatic metrics for "consistent, reproducible assessment" and a "fair, fast evaluation setup."

**(c) Relevance to VoiceForge.** Timing-threshold taxonomy. It supplies a principled taxonomy (pause handling, backchannel, turn-taking, interruption/barge-in management) into which VoiceForge's deterministic timing signals (barge-in, latency) can be organized and named, so VoiceForge's timing metrics align with an established interactive-behavior framework.

**(d) NON-CLAIM.** Does NOT prove anything about VoiceForge's agents — it benchmarks full-duplex SDMs (models that listen and speak simultaneously). VoiceForge's agents may be half-duplex; the benchmark's specific automatic metrics and reference data are not VoiceForge's, and it does not validate VoiceForge's latency thresholds.

**(e) Implementable experiment.** Re-bucket VoiceForge's 46 timed calls' deterministic timing signals into Full-Duplex-Bench's four categories: derive a barge-in / interruption-management metric (did agent yield on user barge-in, and after what latency?) and a response-latency/turn-taking metric, and report distributions per category. No model calls needed — pure re-aggregation of existing timing logs under the borrowed taxonomy.

**(f) Data prerequisites.** Per-call timing events with speaker boundaries (barge-in timestamps, response latencies). VoiceForge's 46 timed calls provide latency/barge-in signals; full backchannel detection would need overlap-speech labels.

**(g) Sufficiency.** PARTIAL. The 46 timed calls support a barge-in/interruption-management and latency/turn-taking re-aggregation under this taxonomy (YES for those slices). Missing for full coverage: backchannel and fine pause-handling labels, and you cannot run the benchmark's own SDM reference suite. Use the paper for taxonomy/vocabulary, not as a head-to-head benchmark.

---

## Paper 5 — How Reliable is Multilingual LLM-as-a-Judge?

**(a) Citation / version.** Fu, X., & Liu, W. "How Reliable is Multilingual LLM-as-a-Judge?" arXiv:2505.12201. v1 submitted 2025-05-18. Subject: cs.CL. Title matches.

**(b) VERIFIED finding.** Evaluating five models across five tasks and 25 languages, the abstract reports LLM judges "struggle to achieve consistent judgment results across languages, with an average Fleiss' Kappa of approximately 0.3," that "consistency varies significantly across languages, with particularly poor performance in low-resource languages," and that neither multilingual training nor larger scale directly fixes it; they propose an ensemble strategy to improve consistency.

**(c) Relevance to VoiceForge.** Language-normalized slice reporting. Justifies reporting VoiceForge's judge agreement per-language (en vs hi-en vs te-en) rather than pooled, and flagging the low-resource code-mixed slices (hi-en, te-en) as the expected fragility point — VoiceForge's pooled κ=0.206 likely masks worse per-language behavior, exactly the pattern this paper documents.

**(d) NON-CLAIM.** Does NOT prove VoiceForge's judge is unreliable in any specific language — its ~0.3 Fleiss' κ is measured on its own 25-language tasks (consistency across model judges, not agreement with VoiceForge's human rater). It does not license a per-language reliability claim for VoiceForge given VoiceForge's tiny per-language n.

**(e) Implementable experiment.** Slice the 45 calibration pairs by language (en / hi-en / te-en) and report judge-vs-human agreement (balanced accuracy from Paper 1, and raw agreement) per slice with explicit n and CIs, explicitly flagging that code-mixed low-resource slices are the predicted weak points and that small n prevents firm conclusions.

**(f) Data prerequisites.** A language tag per calibration pair AND enough labels per language for a meaningful estimate. Language tags exist; per-language counts are very small.

**(g) Sufficiency.** PARTIAL. Framing and a descriptive per-language breakdown are doable with current artifacts. Missing: adequate per-language n — splitting 45 across 3 languages (with only 8 total fails) yields cells too small for stable κ/balanced accuracy. Report as descriptive/hypothesis-generating only.

---

## Paper 6 — SemEval-2023 Task 11: Learning With Disagreements (LeWiDi)

**(a) Citation / version.** Leonardelli, E., Uma, A., Abercrombie, G., Almanea, D., Basile, V., Fornaciari, T., Plank, B., Rieser, V., & Poesio, M. "SemEval-2023 Task 11: Learning With Disagreements (LeWiDi)." arXiv:2304.14803. v1 submitted 2023-04-28. Subject: cs.CL. Title matches.

**(b) VERIFIED finding.** The abstract states that NLP datasets are "rife with disagreements between the judges," especially for subjective tasks, that "reconciling these different subjective interpretations is inappropriate," and that the community should "preserve them" rather than eliminate them; the task emphasizes soft approaches to evaluation, treating aggregation into a single label as a misrepresentation of subjective data.

**(c) Relevance to VoiceForge.** Disagreement-preserving second-rater schema. Motivates collecting a second human rater (or capturing the existing rater's confidence as a soft label) and evaluating the judge against a disagreement-preserving / soft-label target instead of a single hard label — directly relevant since VoiceForge currently has one rater with confidence levels.

**(d) NON-CLAIM.** Does NOT prove VoiceForge's success/fail task is subjective or that disagreement exists in VoiceForge's labels — with a single rater there is no measured disagreement. It provides a schema/philosophy, not evidence about VoiceForge's specific label distribution, and does not validate VoiceForge's existing κ.

**(e) Implementable experiment.** Convert the single rater's confidence levels into soft labels (e.g., high-confidence success = 1.0, low-confidence = 0.7) and evaluate the judge with a soft/cross-entropy metric in addition to hard agreement; design (spec only) a second-rater annotation round on the same 45 calls to measure true human-human disagreement and set a disagreement-aware ceiling on judge agreement.

**(f) Data prerequisites.** Either per-item soft labels (confidence already captured) for the soft-eval part, OR a second independent annotator for the disagreement-measurement part. Confidence exists; a second rater does not.

**(g) Sufficiency.** NO (for the core disagreement claim). The soft-label re-scoring is doable from existing confidence levels, but the headline contribution — preserving/measuring inter-annotator disagreement — requires a second rater VoiceForge does not have. Missing: a second human annotator on the 45-call slice.

---

## Verification status

VERIFIED (from primary arXiv pages): all six (2512.08121, 2407.18370, 2504.19982, 2503.04721, 2505.12201, 2304.14803). UNVERIFIED: none.
