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
        "source": {"enum": ["spokenwoz", "ami", "hero", "bolna"]},
        "language": {"type": "string"},
        "stress_profile": {"enum": ["clean", "pause_heavy", "interruption", "ambiguous", "kb_gap"]},
        "workflow_type": {"type": "string"},
        "turns": {
            "type": "array", "minItems": 1,
            "items": {
                "type": "object",
                "required": ["turn_id", "speaker", "text", "start_ms"],
                "properties": {
                    "turn_id": {"type": "string"},
                    "speaker": {"enum": ["user", "agent"]},
                    "text": {"type": "string"},
                    "start_ms": {"type": "integer", "minimum": 0},
                    "end_ms": {"type": ["integer", "null"]},
                },
            },
        },
        "audio_path": {"type": ["string", "null"]},
        "metadata": {"type": "object"},
    },
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
        "call_id": {"type": "string"}, "duration_s": {"type": "number"},
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
FAILURE = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "failure.schema.json",
    "title": "failure",
    "description": "One detected failure on a call. Emitted by signals.py (deterministic) or judge "
                   "(semantic). `cluster` groups failures across calls for the Failure Clusters view.",
    "type": "object",
    "required": ["call_id", "dimension", "label", "detail", "evidence_turn_ids"],
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
CALL_RECORD = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "call_record.schema.json",
    "title": "call_record",
    "description": "The dashboard's per-call unit in out/calls.json: the call_log plus its outcome, "
                   "scorecard, cost, and failures. The ONLY shape the dashboard consumes.",
    "type": "object",
    "required": ["call_id", "source", "language", "stress_profile", "workflow_type", "turns"],
    "properties": {
        **CALL_LOG["properties"],
        "outcome": {"type": ["object", "null"]},        # task_outcome (call_id implied)
        "scorecard": {"type": ["object", "null"]},      # scorecard (call_id implied)
        "cost": {"type": ["object", "null"]},           # cost (call_id implied)
        "failures": {"type": "array", "items": {"type": "object"}},
        "signals": {"type": ["object", "null"]},        # raw signals.analyze() summary
    },
}

# ---------------------------------------------------------------- analytics (summary + clusters)
ANALYTICS = {
    "$schema": "https://json-schema.org/draft/2020-12/schema", "$id": "analytics.schema.json",
    "title": "analytics", "type": "object",
    "required": ["n_calls", "success_rate", "failure_clusters"],
    "properties": {
        "n_calls": {"type": "integer"},
        "success_rate": _num01,
        "avg_overall": {"type": ["number", "null"]},
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

ALL = {"call_log": CALL_LOG, "task_outcome": TASK_OUTCOME, "scorecard": SCORECARD, "cost": COST,
       "improvement_example": IMPROVEMENT, "failure": FAILURE, "call_record": CALL_RECORD,
       "analytics": ANALYTICS}


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
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
