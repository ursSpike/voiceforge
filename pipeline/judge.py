#!/usr/bin/env python3
"""VoiceForge LLM judge — Gemini Flash via AI Studio key. SPEC §7.B.

Contract: temperature 0, JSON output, every judged dimension returns
{score, reason, evidence_turn_ids}. Every response cached to data/.judge_cache/
keyed by (call_id, dimension, prompt_hash) — reruns are free and idempotent.

Batch 4A — JUDGE MACHINERY, QUARANTINED. The judge scores only the 5 SEMANTIC dims
(language_match, faithfulness, repair_quality, conciseness, user_frustration); timing/overlap/
slots stay DETERMINISTIC (score.py). Every judged dim is marked provenance="uncalibrated" until
blind human labels + kappa exist. Evidence turn ids are validated against the actual call.

QUARANTINE (do NOT lift until Spike labels): never run the 46 real data/normalized calls through
this, never write judge scores into out/calls.json, never expose real-call judge output. Verify
ONLY on the canned synthetic FIXTURE below.

  python pipeline/judge.py --selftest   # OFFLINE: validation logic on mock responses (no network)
  python pipeline/judge.py --fixture    # judge the canned synthetic fixture via Gemini (cached)
  python pipeline/judge.py --smoke      # one canned dim call, twice (proves cache)
"""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / "data" / ".judge_cache"


def _load_env():
    """Tiny .env loader — no dependency."""
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def judge_config():
    import yaml
    cfg = yaml.safe_load((ROOT / "rubric.yaml").read_text()).get("judge", {})
    return cfg.get("model", "gemini-2.5-flash"), cfg.get("temperature", 0)


def get_client():
    _load_env()
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("No GEMINI_API_KEY. Create one (free) at https://aistudio.google.com/apikey,\n"
                 "then: cp .env.example .env  and paste it in.")
    from google import genai
    return genai.Client(api_key=key)


def _is_transient(e):
    s = f"{type(e).__name__} {e}".lower()
    return any(t in s for t in ("429", "rate", "timeout", "deadline", "503", "500",
                                "unavailable", "internal", "connection"))


def _generate_json(client, model, temperature, prompt, attempts=3):
    """Gemini call with retry on TRANSIENT errors only (rate-limit/5xx/network).
    Non-transient (auth, bad request) and malformed JSON surface immediately."""
    from google.genai import types
    last = None
    for i in range(attempts):
        try:
            resp = client.models.generate_content(
                model=model, contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature,
                                                   response_mime_type="application/json"))
            return json.loads(resp.text)   # JSONDecodeError is NOT retried (temp 0 = deterministic)
        except json.JSONDecodeError:
            raise
        except Exception as e:
            last = e
            if _is_transient(e) and i < attempts - 1:
                time.sleep(2 * (i + 1))
                continue
            raise
    raise last


def judge_dimension(client, call_id, dimension, prompt):
    """One judged dimension for one call. Returns (parsed_json, from_cache).
    Strict contract: result must carry score/reason/evidence_turn_ids."""
    model, temperature = judge_config()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    phash = hashlib.sha256(f"{model}|{prompt}".encode()).hexdigest()[:16]
    cpath = CACHE_DIR / f"{call_id}__{dimension}__{phash}.json"
    if cpath.exists():
        return json.loads(cpath.read_text()), True
    out = _generate_json(client, model, temperature, prompt)
    for required in ("score", "reason", "evidence_turn_ids"):
        if required not in out:
            raise ValueError(f"judge returned JSON missing '{required}': {out}")
    cpath.write_text(json.dumps(out, indent=2))
    return out, False


# ---------------------------------------------------------------- 5 SEMANTIC judge dimensions
# Timing/interruption/silence/slots are DETERMINISTIC (score.py) and are NOT judged here.
JUDGE_DIMS = {
    "language_match": "Does the agent respond in / appropriately adapt to the caller's language, "
                      "including code-switching (Hinglish/Tenglish)? 1.0 = fully appropriate, 0 = mismatched.",
    "faithfulness": "Are the agent's statements grounded in what the caller actually said — no "
                    "hallucinated or unsupported claims/values? 1.0 = fully grounded, 0 = hallucinated.",
    "repair_quality": "When the caller is unclear/partial, does the agent acknowledge what it got and "
                      "ask ONE targeted follow-up (1.0), or ignore / over-demand / derail (0)?",
    "conciseness": "Is the agent unnecessarily verbose or unclear? 1.0 = concise and clear, 0 = rambling/padded.",
    "user_frustration": "Does the CALLER show frustration or fall into repair loops? 1.0 = no frustration "
                        "(good), 0 = clear frustration / repeated repair.",
}


def format_call(call):
    return "\n".join(f"{t['turn_id']} {t['speaker']}: {t['text']}" for t in call["turns"])


def build_prompt(dimension, call):
    return (f"You are a strict but fair judge of voice-agent calls. Score ONE dimension.\n\n"
            f"Dimension: {dimension} — {JUDGE_DIMS[dimension]}\n\n"
            f"Call (turn_id speaker: text):\n{format_call(call)}\n\n"
            f"Return ONLY JSON: {{\"score\": <float 0 to 1>, \"reason\": \"<one falsifiable sentence>\", "
            f"\"evidence_turn_ids\": [\"<turn ids that justify the score>\"]}}")


def validate_dim(parsed, dimension, call):
    """Strict-shape + evidence-turn validation. Returns a scorecard dim entry marked uncalibrated.
    Evidence ids not present in the call are DROPPED and flagged (hallucinated-turn guard)."""
    for k in ("score", "reason", "evidence_turn_ids"):
        if k not in parsed:
            raise ValueError(f"{dimension}: missing '{k}'")
    score = parsed["score"]
    if not isinstance(score, (int, float)) or not (0 <= score <= 1):
        raise ValueError(f"{dimension}: score {score!r} not a float in 0..1")
    if not isinstance(parsed["evidence_turn_ids"], list):
        raise ValueError(f"{dimension}: evidence_turn_ids not a list")
    valid_ids = {t["turn_id"] for t in call["turns"]}
    ev = [e for e in parsed["evidence_turn_ids"] if e in valid_ids]
    dropped = [e for e in parsed["evidence_turn_ids"] if e not in valid_ids]
    entry = {"name": dimension, "type": "judge", "score": round(float(score), 3),
             "reason": str(parsed["reason"]), "evidence_turn_ids": ev,
             "provenance": "uncalibrated"}   # no kappa yet -> never present as calibrated
    if dropped:
        entry["evidence_dropped"] = dropped   # judge cited turn ids that don't exist in the call
    return entry


def judge_call(client, call):
    """Run all 5 SEMANTIC judge dims over ONE call. Returns validated, uncalibrated dim entries.
    QUARANTINE: only ever pass the synthetic FIXTURE here this sprint — never the 46 real calls."""
    dims = []
    for d in JUDGE_DIMS:
        parsed, _ = judge_dimension(client, call["call_id"], d, build_prompt(d, call))
        dims.append(validate_dim(parsed, d, call))
    return dims


# canned synthetic FIXTURE — NOT from data/normalized; the only call this machinery touches now
FIXTURE = {
    "call_id": "fixture_4a", "source": "hero", "language": "te-en",
    "stress_profile": "interruption", "workflow_type": "appointment_booking",
    "turns": [
        {"turn_id": "t1", "speaker": "agent", "text": "Hi, I can help book your visit. Which area?", "start_ms": 0, "end_ms": 2000},
        {"turn_id": "t2", "speaker": "user", "text": "haan area ante... Madhapur side, near the metro station ", "start_ms": 2500, "end_ms": 7000},
        {"turn_id": "t3", "speaker": "agent", "text": "I need your COMPLETE address with pincode, landmark and door number before we can proceed at all.", "start_ms": 6500, "end_ms": 11000},
        {"turn_id": "t4", "speaker": "user", "text": "arre I just told you na, Madhapur metro... why again", "start_ms": 11500, "end_ms": 14000},
    ],
}


def selftest():
    """OFFLINE: prove the validation logic on MOCK judge responses — no network, no real calls.
    Confirms: good output validates + is marked uncalibrated; hallucinated evidence is dropped;
    a missing key and an out-of-range score are rejected."""
    good = {"score": 0.2, "reason": "agent over-demanded a full address after a partial answer", "evidence_turn_ids": ["t2", "t3"]}
    e = validate_dim(good, "repair_quality", FIXTURE)
    assert e["provenance"] == "uncalibrated" and e["evidence_turn_ids"] == ["t2", "t3"], e
    print("  good output -> validated, provenance=uncalibrated ✓")

    hallu = {"score": 0.5, "reason": "x", "evidence_turn_ids": ["t2", "t99"]}   # t99 not in call
    e = validate_dim(hallu, "faithfulness", FIXTURE)
    assert e["evidence_turn_ids"] == ["t2"] and e.get("evidence_dropped") == ["t99"], e
    print("  hallucinated turn id t99 -> dropped + flagged ✓")

    for bad, why in [({"reason": "x", "evidence_turn_ids": []}, "missing score"),
                     ({"score": 1.5, "reason": "x", "evidence_turn_ids": []}, "score out of range")]:
        try:
            validate_dim(bad, "conciseness", FIXTURE)
            raise AssertionError(f"should have rejected: {why}")
        except ValueError:
            print(f"  rejected ({why}) ✓")
    print("OFFLINE SELFTEST PASSED — strict validation + evidence guard + uncalibrated marking work; "
          "no network, no real calls touched.")


def fixture_run():
    """Judge the canned FIXTURE via Gemini (cached). Proves the end-to-end machinery on a SYNTHETIC
    call — never the 46 real calls; nothing written to out/calls.json."""
    client = get_client()
    print(f"judging canned FIXTURE {FIXTURE['call_id']} (synthetic; quarantined from real calls)\n")
    dims = judge_call(client, FIXTURE)
    print(json.dumps({"call_id": FIXTURE["call_id"], "dimensions": dims,
                      "_provenance": "uncalibrated (no kappa yet)"}, indent=2))
    assert all(d["provenance"] == "uncalibrated" for d in dims)
    assert all(set(d["evidence_turn_ids"]) <= {t["turn_id"] for t in FIXTURE["turns"]} for d in dims)
    print(f"\nFIXTURE judged: {len(dims)}/5 dims, all uncalibrated, all evidence ids valid. "
          "NOT written to out/calls.json (quarantine).")


SMOKE_PROMPT = """You are a strict but fair judge of voice-agent calls. Score ONE dimension.

Dimension: repair_quality — when the caller gives a partial or ambiguous answer, does the
agent acknowledge what it got and ask one targeted follow-up (good), or ignore/over-demand (bad)?

Call snippet (turn_id speaker: text):
t1 agent: Hi, I can book that service visit. What area are you in?
t2 user: haan area... ante... Madhapur side anukunta, near the er... metro station
t3 agent: I need your complete address with pincode landmark and door number before we can proceed any further with this booking request, please provide all details now.

Return ONLY JSON: {"score": <float 0 to 1>, "reason": "<one falsifiable sentence>", "evidence_turn_ids": ["..."]}"""


def smoke():
    client = get_client()
    model, temp = judge_config()
    print(f"judge model: {model} (temperature {temp})")
    for attempt in (1, 2):
        out, cached = judge_dimension(client, "smoke_001", "repair_quality", SMOKE_PROMPT)
        tag = "CACHE HIT" if cached else "live call"
        print(f"\n[{attempt}] {tag}:\n{json.dumps(out, indent=2)}")
    print("\nsmoke test PASSED — judge returns {score, reason, evidence_turn_ids}, cache is idempotent")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="one canned judge call, run twice (proves cache)")
    ap.add_argument("--selftest", action="store_true", help="OFFLINE: validation logic on mock responses (no network)")
    ap.add_argument("--fixture", action="store_true", help="judge the canned synthetic fixture via Gemini (cached)")
    args = ap.parse_args()
    if args.selftest:
        print("Batch 4A judge machinery — offline self-test:")
        selftest()
        return
    if args.fixture:
        fixture_run()
        return
    if args.smoke:
        try:
            smoke()
        except Exception as e:
            print(f"smoke FAILED: {type(e).__name__}: {e}", file=sys.stderr)
            try:
                client = get_client()
                flash = [m.name for m in client.models.list() if "flash" in m.name.lower()]
                print("\nmodels with 'flash' available to this key (update rubric.yaml judge.model):",
                      *flash[:15], sep="\n  ", file=sys.stderr)
            except Exception:
                pass
            sys.exit(1)
    else:
        sys.exit("Batch 4A judge machinery. QUARANTINED — verify with:\n"
                 "  python pipeline/judge.py --selftest   (offline, no network)\n"
                 "  python pipeline/judge.py --fixture    (judge the synthetic fixture via Gemini)\n"
                 "Real-call judging is forbidden until blind human labels exist.")


if __name__ == "__main__":
    main()
