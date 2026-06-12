#!/usr/bin/env python3
"""THE SCHEMA CONSTITUTION (Batch 0). Single source for VoiceForge's data contracts.

Defines every schema as a JSON Schema (draft 2020-12), emits them to schemas/json/*.schema.json
(readable, machine-checkable artifacts), and validates the live pool against them. Field names
match the existing schemas/*.md specs that signals.py / judge.py / normalize.py / the 36 notebooks
already use — the REPO is the constitution, not any hypothetical renaming.

    .venv/bin/python pipeline/schemas.py            # emit json schemas + validate data/normalized/
    from schemas import validate, CALL_LOG          # programmatic use elsewhere

Deterministic-first doctrine is encoded here: scorecard dimensions carry a `type`
(deterministic|judge); timing/interruption/silence/turn-count/task-completion are deterministic,
never judge opinion. Judge dimensions are semantic only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "schemas" / "json"

_num01 = {"type": "number", "minimum": 0, "maximum": 1}

# stress_profile vocabulary. 'unmeasured' = no clock (text-only source); the others imply a clock.
_PROFILES = ["clean", "pause_heavy", "interruption", "ambiguous", "kb_gap", "unmeasured"]
_TIMED_PROFILES = [p for p in _PROFILES if p != "unmeasured"]

# The all-or-none TIMING INVARIANT, encoded in the schema (not just Python). A call is either:
#   (a) fully timed   — every turn.start_ms is an integer AND stress_profile is a measured one, or
#   (b) fully untimed — every turn.start_ms AND end_ms is null AND stress_profile == 'unmeasured'.
# A mixed/partial clock matches NEITHER branch -> oneOf fails -> rejected. This also couples
# timing<->profile both directions (all-null<->unmeasured), so a fake partial clock can never validate.
_TIMING_INVARIANT = {
    "oneOf": [
        {"properties": {"stress_profile": {"enum": _TIMED_PROFILES},
                        "turns": {"items": {"properties": {"start_ms": {"type": "integer"}}}}}},
        {"properties": {"stress_profile": {"const": "unmeasured"},
                        "turns": {"items": {"properties": {"start_ms": {"type": "null"},
                                                           "end_ms": {"type": "null"}}}}}},
    ],
}

# ---------------------------------------------------------------- call_log
CALL_LOG = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "call_log.schema.json",
    "title": "call_log",
    "description": "Normalized record of one call. Every downstream tool reads this shape.",
    "type": "object",
    "required": ["call_id", "source", "language", "stress_profile", "workflow_type", "turns"],
    "properties": {
        "call_id": {"type": "string"},
        "source": {"enum": ["spokenwoz", "ami", "hero", "bolna", "code_mixed_dialog"]},
        "language": {"type": "string"},
        # "unmeasured": timing was never observed (e.g. text-only translated corpora). NOT a stress
        # level — an honest "no clock" marker so timing dimensions are omitted, never faked.
        "stress_profile": {"enum": _PROFILES},
        "workflow_type": {"type": "string"},
        "turns": {
            "type": "array", "minItems": 1,
            "items": {
                "type": "object",
                # end_ms is REQUIRED (present, may be null) — an absent key would slip past the timing
                # invariant and KeyError downstream. "present-but-null" is the contract, never "absent".
                "required": ["turn_id", "speaker", "text", "start_ms", "end_ms"],
                "properties": {
                    "turn_id": {"type": "string"},
                    "speaker": {"enum": ["user", "agent"]},
                    "text": {"type": "string"},
                    # start_ms null = timing unobserved for this turn (text-only source). Present-but-null,
                    # never a fabricated number. signals.py skips untimed turns; score.py omits timing dims.
                    "start_ms": {"type": ["integer", "null"], "minimum": 0},
                    "end_ms": {"type": ["integer", "null"]},
                },
            },
        },
        "audio_path": {"type": ["string", "null"]},
        "metadata": {"type": "object"},
    },
    "allOf": [_TIMING_INVARIANT],   # all-or-none timing + timing<->profile coupling
}

# ---------------------------------------------------------------- task_outcome
TASK_OUTCOME = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "task_outcome.schema.json",
    "title": "task_outcome", "type": "object",
    "required": ["call_id", "task_completed", "required_fields"],
    "properties": {
        "call_id": {"type": "string"},
        "task_completed": {"type": "boolean"},
        "required_fields": {
            "type": "array",
            "items": {"type": "object", "required": ["name", "captured"],
                      "properties": {"name": {"type": "string"}, "captured": {"type": "boolean"},
                                     "value": {"type": ["string", "null"]}}},
        },
        "escalation_needed": {"type": "boolean"},
        "confidence": _num01,
    },
}

# ---------------------------------------------------------------- scorecard
SCORECARD = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "scorecard.schema.json",
    "title": "scorecard",
    "description": "Per-call eval across rubric dimensions. Every dimension carries a reason + evidence. "
                   "type=deterministic for measured signals (timing/task), type=judge for semantic LLM dims.",
    "type": "object", "required": ["call_id", "dimensions", "overall"],
    "properties": {
        "call_id": {"type": "string"},
        "dimensions": {
            "type": "array",
            "items": {"type": "object",
                      "required": ["name", "type", "score", "reason", "evidence_turn_ids"],
                      "properties": {"name": {"type": "string"},
                                     "type": {"enum": ["deterministic", "judge"]},
                                     "score": _num01, "reason": {"type": "string"},
                                     "evidence_turn_ids": {"type": "array", "items": {"type": "string"}}}},
        },
        "overall": _num01,
    },
}

# ---------------------------------------------------------------- cost
COST = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "cost.schema.json",
    "title": "cost", "type": "object",
    "required": ["call_id", "duration_s", "turn_count", "est_cost_total", "est_cost_per_success_note"],
    "properties": {
        "call_id": {"type": "string"}, "duration_s": {"type": ["number", "null"]},
        "turn_count": {"type": "integer"}, "est_llm_calls": {"type": "integer"},
        "est_cost_total": {"type": "number"},
        "est_cost_per_success_note": {"type": "string"},
    },
}

# ---------------------------------------------------------------- improvement_example
IMPROVEMENT = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "improvement_example.schema.json",
    "title": "improvement_example", "type": "object",
    "required": ["call_id", "failure_dimension", "rejected_turn", "chosen_turn", "reason", "needs_human_review"],
    "properties": {
        "call_id": {"type": "string"}, "failure_dimension": {"type": "string"},
        "rejected_turn": {"type": "string"}, "chosen_turn": {"type": "string"},
        "reason": {"type": "string"}, "quality_delta": {"type": "number"},
        "needs_human_review": {"type": "boolean"},
    },
}

# ---------------------------------------------------------------- failure (NEW — for failure clusters)
# call_id is OPTIONAL: when embedded under a call_record.failures[] the parent implies it; the
# standalone Failure-Clusters builder (score.py/crosscut.py) injects call_id so a cluster row can
# point back to its call. signals.py emits context-free failures (no call_id) — assembly adds it.
FAILURE = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "failure.schema.json",
    "title": "failure",
    "description": "One detected failure on a call. Emitted by signals.py (deterministic) or judge "
                   "(semantic). `cluster` groups failures across calls for the Failure Clusters view. "
                   "call_id optional (implied when embedded; injected at assembly for clusters).",
    "type": "object",
    "required": ["dimension", "label", "detail", "evidence_turn_ids"],
    "properties": {
        "call_id": {"type": "string"},
        "dimension": {"type": "string"},
        "at_ms": {"type": ["integer", "null"]},
        "label": {"type": "string"},
        "detail": {"type": "string"},
        "evidence_turn_ids": {"type": "array", "items": {"type": "string"}},
        "severity": {"enum": ["low", "medium", "high"]},
        "cluster": {"type": "string"},
        "origin": {"enum": ["deterministic", "judge"]},
    },
}

# ---------------------------------------------------------------- call_record (merged — the out/calls.json unit)
def _embed(schema):
    """An embedded copy of a schema with call_id dropped from required (the parent implies it).
    Used so call_record validates the SHAPE of its nested outcome/scorecard/cost, not just 'object'."""
    s = json.loads(json.dumps({k: v for k, v in schema.items()
                               if k not in ("$schema", "$id", "title", "description")}))
    s["required"] = [r for r in s.get("required", []) if r != "call_id"]
    s.setdefault("type", "object")
    return s


CALL_RECORD = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "call_record.schema.json",
    "title": "call_record",
    "description": "The dashboard's per-call unit in out/calls.json: the call_log PLUS its outcome, "
                   "scorecard, cost, failures, and signals — each shape-validated. The ONLY shape "
                   "the dashboard consumes. outcome/scorecard/cost/failures are required for a fully "
                   "scored record (Batch 3 output); signals optional.",
    "type": "object",
    "required": ["call_id", "source", "language", "stress_profile", "workflow_type", "turns",
                 "outcome", "scorecard", "cost", "failures"],
    "properties": {
        **CALL_LOG["properties"],
        "outcome": _embed(TASK_OUTCOME),                 # task_outcome shape, call_id implied
        "scorecard": _embed(SCORECARD),                  # scorecard shape (dimensions[], overall)
        "cost": _embed(COST),                            # cost shape
        "failures": {"type": "array", "items": _embed(FAILURE)},
        "signals": {"type": ["object", "null"]},         # raw signals.analyze() summary
    },
    "allOf": [_TIMING_INVARIANT],   # the same all-or-none timing invariant holds on the merged record
}

# ---------------------------------------------------------------- analytics (summary + clusters)
ANALYTICS = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "analytics.schema.json",
    "title": "analytics", "type": "object",
    "required": ["n_calls", "success_rate", "failure_clusters", "timing_coverage"],
    "properties": {
        "n_calls": {"type": "integer"},
        "success_rate": _num01,
        "avg_overall": {"type": ["number", "null"]},
        # coverage split so avg_overall (timed-only) is read in context; counts are non-negative ints
        "timing_coverage": {"type": "object", "required": ["timed", "unmeasured"],
                            "additionalProperties": False,
                            "properties": {"timed": {"type": "integer", "minimum": 0},
                                           "unmeasured": {"type": "integer", "minimum": 0}}},
        "cost_per_successful_call": {"type": ["number", "null"]},
        "by_stress_profile": {"type": "array"},
        "failure_clusters": {
            "type": "array",
            "items": {"type": "object", "required": ["dimension", "count"],
                      "properties": {"dimension": {"type": "string"}, "count": {"type": "integer"},
                                     "example_call_ids": {"type": "array", "items": {"type": "string"}}}},
        },
        "note": {"type": "string"},
    },
}

# ---------------------------------------------------------------- phenotype_label (human annotation)
# FDE-facing transcript taxonomy: small, operational, and reusable across onboarding, booking,
# support, and local-workforce calls. Audio intelligibility/pronunciation tags stay out until an
# audio-enabled review surface exists.
PHENO_POSITIVE = ["easy_to_understand", "understood_user", "handled_confusion_well",
                  "adapted_language_well", "completed_or_clear_next_step", "user_satisfied"]
PHENO_NEGATIVE = ["hard_to_understand", "wrong_language_or_tone", "misunderstood_user",
                  "poor_clarification_or_recovery", "missing_or_wrong_information",
                  "repeated_or_stuck", "workflow_or_tool_failed", "user_frustrated"]
PHENO_CONTEXT = ["mixed_languages", "user_unclear_or_hesitant", "multi_step_request",
                 "transcript_unclear"]

PHENO_TAG_LABELS = {
    "easy_to_understand": "Easy to understand",
    "understood_user": "Understood the user",
    "handled_confusion_well": "Handled confusion well",
    "adapted_language_well": "Adapted language well",
    "completed_or_clear_next_step": "Completed task / clear next step",
    "user_satisfied": "User seemed satisfied",
    "hard_to_understand": "Hard to understand",
    "wrong_language_or_tone": "Wrong language or tone",
    "misunderstood_user": "Misunderstood the user",
    "poor_clarification_or_recovery": "Poor clarification or recovery",
    "missing_or_wrong_information": "Missing or wrong information",
    "repeated_or_stuck": "Repeated or got stuck",
    "workflow_or_tool_failed": "Workflow or tool failed",
    "user_frustrated": "User seemed frustrated",
    "mixed_languages": "Mixed languages",
    "user_unclear_or_hesitant": "User unclear or hesitant",
    "multi_step_request": "Multi-step request",
    "transcript_unclear": "Transcript unclear",
}

PHENOTYPE_LABEL = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "phenotype_label.schema.json",
    "title": "phenotype_label",
    "description": "One blind human annotation. primary_label (binary) is the kappa spine; tags are "
                   "single-rater EXPLORATORY transcript-observable primitives (no kappa on tags this "
                   "sprint). Annotator never sees call_id/source/stress_profile/any score.",
    "type": "object",
    "required": ["call_id", "primary_label", "confidence"],
    "properties": {
        "call_id": {"type": "string"},
        "primary_label": {"enum": ["success", "fail", "unsure"]},
        "confidence": {"enum": ["high", "medium", "low"]},
        "positive_tags": {"type": "array", "items": {"enum": PHENO_POSITIVE}},
        "negative_tags": {"type": "array", "items": {"enum": PHENO_NEGATIVE}},
        "context_tags": {"type": "array", "items": {"enum": PHENO_CONTEXT}},
        "note": {"type": "string"},
        "timestamp": {"type": "string"},
    },
}

ALL = {"call_log": CALL_LOG, "task_outcome": TASK_OUTCOME, "scorecard": SCORECARD, "cost": COST,
       "improvement_example": IMPROVEMENT, "failure": FAILURE, "call_record": CALL_RECORD,
       "analytics": ANALYTICS, "phenotype_label": PHENOTYPE_LABEL}


def validate(obj, schema_name):
    """Validate obj against a named schema. Raises jsonschema.ValidationError on failure."""
    import jsonschema
    jsonschema.validate(obj, ALL[schema_name])


def emit():
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for name, schema in ALL.items():
        (OUTDIR / f"{name}.schema.json").write_text(json.dumps(schema, indent=2) + "\n")
    print(f"emitted {len(ALL)} schemas -> schemas/json/")


def main():
    import jsonschema
    # self-check: every schema is itself a valid JSON Schema
    for name, schema in ALL.items():
        jsonschema.Draft202012Validator.check_schema(schema)
    emit()
    # validate the live pool against call_log (the constitution must hold for existing data)
    ok = bad = 0
    for p in sorted((ROOT / "data" / "normalized").glob("*.json")):
        try:
            validate(json.loads(p.read_text()), "call_log")
            ok += 1
        except jsonschema.ValidationError as e:
            bad += 1
            print(f"  INVALID {p.name}: {e.message} (at {list(e.path)})")
    print(f"pool validated against call_log: {ok} valid, {bad} invalid")

    # call_record contract self-test: a well-formed record passes, a missing-scorecard one fails
    sample = {"call_id": "x", "source": "hero", "language": "en", "stress_profile": "clean",
              "workflow_type": "t", "turns": [{"turn_id": "t1", "speaker": "agent", "text": "hi", "start_ms": 0, "end_ms": 900}],
              "outcome": {"task_completed": True, "required_fields": []},
              "scorecard": {"dimensions": [{"name": "barge_in", "type": "deterministic", "score": 1.0,
                                            "reason": "no overlap", "evidence_turn_ids": []}], "overall": 1.0},
              "cost": {"call_id": "x", "duration_s": 1.0, "turn_count": 1, "est_cost_total": 0.0,
                       "est_cost_per_success_note": "estimated, prototype"},
              "failures": [{"dimension": "latency_gap", "label": "response latency", "detail": "900ms gap",
                            "evidence_turn_ids": ["t1"]}]}
    validate(sample, "call_record")
    try:
        bad_sample = {k: v for k, v in sample.items() if k != "scorecard"}
        validate(bad_sample, "call_record")
        print("  call_record self-test FAILED: missing scorecard wrongly accepted"); bad += 1
    except jsonschema.ValidationError:
        print("call_record contract self-test: well-formed PASS, missing-scorecard correctly REJECTED")

    # nullable-timing contract self-test: a text-only call (no clock) must validate with
    # start_ms/end_ms null, stress_profile 'unmeasured', source 'code_mixed_dialog', timing dims OMITTED.
    unmeasured = {"call_id": "u1", "source": "code_mixed_dialog", "language": "hi-en",
                  "stress_profile": "unmeasured", "workflow_type": "restaurant_reservation",
                  "turns": [{"turn_id": "t1", "speaker": "agent", "text": "namaste", "start_ms": None, "end_ms": None},
                            {"turn_id": "t2", "speaker": "user", "text": "table chahiye", "start_ms": None, "end_ms": None}],
                  "outcome": {"task_completed": True, "required_fields": []},
                  "scorecard": {"dimensions": [{"name": "task_completion", "type": "deterministic", "score": 1.0,
                                                "reason": "captured 1/1 (heuristic)", "evidence_turn_ids": []}], "overall": 1.0},
                  "cost": {"call_id": "u1", "duration_s": None, "turn_count": 2, "est_cost_total": 0.005,
                           "est_cost_per_success_note": "estimated, prototype"},
                  "failures": []}
    validate(unmeasured, "call_record")
    # and a turn with a FABRICATED-looking 0 is still fine, but a non-int non-null start_ms must reject
    try:
        bad_t = json.loads(json.dumps(unmeasured)); bad_t["turns"][0]["start_ms"] = "0"
        validate(bad_t, "call_record")
        print("  nullable-timing self-test FAILED: string start_ms wrongly accepted"); bad += 1
    except jsonschema.ValidationError:
        print("nullable-timing contract self-test: null-timing record PASS, non-int start_ms correctly REJECTED")

    # the JSON SCHEMA (not just Python) must reject a MIXED-timing call_log
    mixed_log = {"call_id": "mx", "source": "bolna", "language": "en", "stress_profile": "clean",
                 "workflow_type": "t",
                 "turns": [{"turn_id": "t1", "speaker": "agent", "text": "a", "start_ms": 0, "end_ms": 1000},
                           {"turn_id": "t2", "speaker": "user", "text": "b", "start_ms": None, "end_ms": None}]}
    try:
        validate(mixed_log, "call_log")
        print("  timing-invariant self-test FAILED: mixed call_log wrongly accepted"); bad += 1
    except jsonschema.ValidationError:
        print("timing-invariant self-test: mixed call_log correctly REJECTED by schema")
    # ...and an all-null call_log with a non-'unmeasured' profile must also be rejected (coupling)
    try:
        bad_couple = json.loads(json.dumps(mixed_log)); bad_couple["turns"][0]["start_ms"] = None; bad_couple["turns"][0]["end_ms"] = None
        validate(bad_couple, "call_log")   # all-null but stress_profile 'clean'
        print("  timing-invariant self-test FAILED: all-null + non-unmeasured profile wrongly accepted"); bad += 1
    except jsonschema.ValidationError:
        print("timing-invariant self-test: all-null + non-'unmeasured' profile correctly REJECTED")

    # ANALYTICS must reject malformed timing_coverage (string / negative counts)
    good_an = {"n_calls": 1, "success_rate": 1.0, "failure_clusters": [], "timing_coverage": {"timed": 1, "unmeasured": 0}}
    validate(good_an, "analytics")
    for label, cov in [("string count", {"timed": "x", "unmeasured": 0}), ("negative count", {"timed": -1, "unmeasured": 0}),
                       ("missing field", {"timed": 1})]:
        try:
            validate({**good_an, "timing_coverage": cov}, "analytics")
            print(f"  analytics self-test FAILED: {label} timing_coverage wrongly accepted"); bad += 1
        except jsonschema.ValidationError:
            pass
    print("analytics self-test: malformed timing_coverage (string / negative / missing) correctly REJECTED")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
