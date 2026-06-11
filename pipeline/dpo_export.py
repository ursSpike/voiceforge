#!/usr/bin/env python3
"""Failures -> (chosen, rejected) preference pairs. SPEC §7.F. — Block 5.

For each failed/suboptimal call: one pair where the ONLY meaningful difference is the
detected failure axis (over-talk -> shorter turn; ignored pause -> wait+clarify;
language-mismatch -> in-language reply; missed field -> clean re-ask).

Outputs:
- out/queue.jsonl          TRL conversational: {"prompt":[...], "chosen":[...], "rejected":[...]}
- out/queue_openai.jsonl   the 3-line mapper:
    {"input": {"messages": prompt}, "preferred_output": chosen, "non_preferred_output": rejected}

Target 10-20 pairs. Each carries provenance (call_id, failure_dimension) per
schemas/improvement_example.md, and needs_human_review=true by default.
"""
raise SystemExit("TODO Block 5 (June 11).")


Hey Prateek, saw your post about the Bolna × Cartesia Voc-a-thon. I registered on Luma and filled the GForm, but haven’t received access yet. I also followed up with Sonam over email but haven’t heard back any.

I’m Saivarshith Valugula, iit kgp cs'25 graduate, currently an SDE-1 at Fujitsu Research India working mainly  ML evaluation & performance. I've already started building my prototype VoiceForge, a conversation data flywheel that turns business call logs into structured outcomes, quality evals, failure clusters, and improvement signals for voice AI systems.

But with the deadline tomorrow, I'm yet to get access to Bolna + Cartesia credits to complete my prototype.

I've used is [valugulakittu3@gmail.com](mailto:valugulakittu3@gmail.com) as my registration email.

Would really appreciate any help with access or being pointed to the right person if there’s still room. Thanks!
