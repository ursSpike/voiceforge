#!/usr/bin/env python3
"""VoiceForge LLM judge — Gemini Flash via AI Studio key. SPEC §7.B.

Contract: temperature 0, JSON output, every judged dimension returns {score, reason,
evidence_turn_ids}. Responses are cached to data/.judge_cache/ keyed by (call_id, dimension,
model, TEMPERATURE, prompt_hash) — and a response is VALIDATED BEFORE it is cached, so a malformed
or out-of-range response is never persisted (no poisoned cache).

Batch 4A — JUDGE MACHINERY, QUARANTINED. Scores only the 5 SEMANTIC dims (= rubric.yaml's judge
dims, enforced at startup); timing/overlap/slots stay DETERMINISTIC (score.py). Every judged dim
is marked provenance="uncalibrated" PERMANENTLY this sprint — kappa calibrates only the separate
binary outcome judgment (judge_run.py); no per-dimension human gold exists. Evidence turn ids are
validated against the actual call; at least one valid unique id is required.

QUARANTINE (do NOT lift until Spike labels): never run the 46 real data/normalized calls through
this, never write judge scores into out/calls.json, never expose real-call judge output. Verify
ONLY on the canned synthetic FIXTURE.

  python pipeline/judge.py --selftest   # OFFLINE: validation + cache + retry on a mock client (no network)
  python pipeline/judge.py --fixture    # judge the canned synthetic fixture via Gemini (cached)
  python pipeline/judge.py --smoke      # one canned dim, twice (proves the cache)
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
_RETRY_BASE = 2          # seconds; the selftest sets this to 0 so the mock retry test is instant


def _load_env():
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


# ---------------------------------------------------------------- 5 SEMANTIC judge dimensions
# The SET of dims is the source-of-truth rubric.yaml's judge dims (enforced by _check_rubric_dims);
# the criteria text below is the prompt material. Timing/overlap/slots are NOT judged here.
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


def _check_rubric_dims():
    """rubric.yaml is the source of truth: JUDGE_DIMS must be EXACTLY its judge-type dimensions."""
    import yaml
    rub = yaml.safe_load((ROOT / "rubric.yaml").read_text())["dimensions"]
    rubric_judge = {k for k, v in rub.items() if v.get("type") == "judge"}
    if set(JUDGE_DIMS) != rubric_judge:
        raise SystemExit(f"judge dims {sorted(JUDGE_DIMS)} != rubric judge dims {sorted(rubric_judge)} "
                         "— rubric.yaml is the source of truth; reconcile before judging.")


def format_call(call):
    return "\n".join(f"{t['turn_id']} {t['speaker']}: {t['text']}" for t in call["turns"])


def build_prompt(dimension, call):
    return (f"You are a strict but fair judge of voice-agent calls. Score ONE dimension.\n\n"
            f"Dimension: {dimension} — {JUDGE_DIMS[dimension]}\n\n"
            f"Call (turn_id speaker: text):\n{format_call(call)}\n\n"
            f"Return ONLY JSON: {{\"score\": <number 0 to 1>, \"reason\": \"<one falsifiable sentence>\", "
            f"\"evidence_turn_ids\": [\"<turn ids that justify the score>\"]}}")


def validate_dim(parsed, dimension, call):
    """STRICT shape + evidence validation -> a scorecard dim entry (provenance uncalibrated).
    Rejects: non-object, missing keys, boolean/non-number/out-of-range score, non-string/empty
    reason, non-list/non-string evidence, and the case where NO valid unique evidence id survives
    filtering. Dedupes evidence; drops + flags ids not present in the call (hallucinated-turn guard)."""
    if not isinstance(parsed, dict):
        raise ValueError(f"{dimension}: response is not a JSON object")
    for k in ("score", "reason", "evidence_turn_ids"):
        if k not in parsed:
            raise ValueError(f"{dimension}: missing '{k}'")
    score = parsed["score"]
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError(f"{dimension}: score {score!r} must be a non-boolean number")
    if not (0 <= score <= 1):
        raise ValueError(f"{dimension}: score {score} out of range 0..1")
    reason = parsed["reason"]
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError(f"{dimension}: reason must be a non-empty string")
    ev_raw = parsed["evidence_turn_ids"]
    if not isinstance(ev_raw, list) or not all(isinstance(e, str) for e in ev_raw):
        raise ValueError(f"{dimension}: evidence_turn_ids must be a list of strings")
    valid_ids = {t["turn_id"] for t in call["turns"]}
    seen, ev, dropped = set(), [], []
    for e in ev_raw:
        if e in valid_ids:
            if e not in seen:
                seen.add(e)
                ev.append(e)
        else:
            dropped.append(e)
    if not ev:
        raise ValueError(f"{dimension}: no valid evidence turn id after filtering (cited {ev_raw})")
    entry = {"name": dimension, "type": "judge", "score": round(float(score), 3),
             "reason": reason.strip(), "evidence_turn_ids": ev, "provenance": "uncalibrated"}
    if dropped:
        entry["evidence_dropped"] = dropped
    return entry


def _is_transient(e):
    s = f"{type(e).__name__} {e}".lower()
    return any(t in s for t in ("429", "rate", "timeout", "deadline", "503", "500",
                                "unavailable", "internal", "connection"))


def _generate_json(client, model, temperature, prompt, attempts=3):
    """Gemini call, retry on TRANSIENT errors only. Malformed JSON (temp-0 deterministic) and
    non-transient errors (auth/400) surface immediately — no retry."""
    from google.genai import types
    last = None
    for i in range(attempts):
        try:
            resp = client.models.generate_content(
                model=model, contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature,
                                                   response_mime_type="application/json"))
            return json.loads(resp.text)
        except json.JSONDecodeError:
            raise
        except Exception as e:
            last = e
            if _is_transient(e) and i < attempts - 1:
                time.sleep(_RETRY_BASE * (i + 1))
                continue
            raise
    raise last


def judge_dimension(client, call, dimension):
    """One judged dimension for one call. VALIDATES BEFORE CACHING (a bad response is never
    persisted) AND RE-VALIDATES EVERY CACHE HIT against the current call — a corrupted/stale
    entry is deleted and re-fetched live, never trusted. Returns (validated_entry, from_cache).
    Cache key includes model AND temperature."""
    model, temperature = judge_config()
    prompt = build_prompt(dimension, call)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    phash = hashlib.sha256(f"{model}|{temperature}|{prompt}".encode()).hexdigest()[:16]
    cpath = CACHE_DIR / f"{call['call_id']}__{dimension}__{phash}.json"
    if cpath.exists():
        try:
            return validate_dim(json.loads(cpath.read_text()), dimension, call), True
        except (ValueError, json.JSONDecodeError):
            cpath.unlink()                          # corrupted cache entry -> refetch live
    parsed = _generate_json(client, model, temperature, prompt)
    entry = validate_dim(parsed, dimension, call)   # raises on invalid -> NOTHING cached
    cpath.write_text(json.dumps(entry, indent=2))
    return entry, False


def judge_call(client, call):
    """Run all 5 SEMANTIC judge dims over ONE call -> validated, uncalibrated dim entries.
    QUARANTINE: only ever pass the synthetic FIXTURE here this sprint — never the 46 real calls."""
    _check_rubric_dims()
    return [judge_dimension(client, call, d)[0] for d in JUDGE_DIMS]


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


# ---------------------------------------------------------------- offline self-test (mock client)
class _MockClient:
    """Scripted Gemini stand-in: each generate_content returns the next script item (a JSON string)
    or raises it (an Exception). Lets the selftest exercise cache/retry/validation with no network."""
    class _Models:
        def __init__(self, script):
            self.script = list(script)
            self.calls = 0

        def generate_content(self, **kw):
            self.calls += 1
            item = self.script[min(self.calls - 1, len(self.script) - 1)]
            if isinstance(item, Exception):
                raise item
            return type("R", (), {"text": item})()

    def __init__(self, script):
        self.models = self._Models(script)


def selftest():
    global _RETRY_BASE
    _RETRY_BASE = 0   # instant retries
    _check_rubric_dims()
    print("  rubric agreement: JUDGE_DIMS == rubric judge dims ✓")

    # 1) validate_dim unit cases
    ok = validate_dim({"score": 0.2, "reason": "over-demanded a full address after a partial answer",
                       "evidence_turn_ids": ["t2", "t2", "t3"]}, "repair_quality", FIXTURE)
    assert ok["provenance"] == "uncalibrated" and ok["evidence_turn_ids"] == ["t2", "t3"], ok
    print("  good output -> uncalibrated, evidence deduped ✓")
    hallu = validate_dim({"score": 0.5, "reason": "x", "evidence_turn_ids": ["t2", "t99"]}, "faithfulness", FIXTURE)
    assert hallu["evidence_turn_ids"] == ["t2"] and hallu.get("evidence_dropped") == ["t99"], hallu
    print("  hallucinated turn t99 -> dropped + flagged ✓")
    bad = {"bool score": {"score": True, "reason": "x", "evidence_turn_ids": ["t2"]},
           "score>1": {"score": 1.7, "reason": "x", "evidence_turn_ids": ["t2"]},
           "non-str reason": {"score": 0.5, "reason": {"a": 1}, "evidence_turn_ids": ["t2"]},
           "empty reason": {"score": 0.5, "reason": "  ", "evidence_turn_ids": ["t2"]},
           "empty evidence": {"score": 0.5, "reason": "x", "evidence_turn_ids": []},
           "all-invalid evidence": {"score": 0.5, "reason": "x", "evidence_turn_ids": ["t99"]},
           "missing key": {"score": 0.5, "evidence_turn_ids": ["t2"]}}
    for why, p in bad.items():
        try:
            validate_dim(p, "conciseness", FIXTURE)
            raise AssertionError(f"should have rejected: {why}")
        except ValueError:
            pass
    print(f"  rejected all {len(bad)} bad shapes (bool/score>1/non-str+empty reason/empty+all-invalid evidence/missing) ✓")

    # 2) cache + retry behaviour on the mock client (selftest_* ids, cleaned up after)
    for f in CACHE_DIR.glob("selftest_*"):
        f.unlink()
    goodjson = json.dumps({"score": 0.2, "reason": "demanded full address", "evidence_turn_ids": ["t2", "t3"]})
    call_ok = {**FIXTURE, "call_id": "selftest_ok"}
    c = _MockClient([goodjson])
    e1, cached1 = judge_dimension(c, call_ok, "repair_quality")
    e2, cached2 = judge_dimension(c, call_ok, "repair_quality")
    assert not cached1 and cached2 and c.models.calls == 1, (cached1, cached2, c.models.calls)
    print("  valid -> cached; re-run is a CACHE HIT (provider called once) ✓")

    call_poison = {**FIXTURE, "call_id": "selftest_poison"}
    c = _MockClient([json.dumps({"score": 1.7, "reason": "x", "evidence_turn_ids": ["t2"]})])
    try:
        judge_dimension(c, call_poison, "repair_quality")
        raise AssertionError("poison should have raised")
    except ValueError:
        pass
    assert not list(CACHE_DIR.glob("selftest_poison__*")), "poisoned response was cached!"
    print("  invalid response -> raised AND NOT cached (no poisoning) ✓")

    c = _MockClient([RuntimeError("503 service unavailable"), RuntimeError("503 unavailable"), goodjson])
    e, _ = judge_dimension(c, {**FIXTURE, "call_id": "selftest_retry"}, "repair_quality")
    assert c.models.calls == 3, c.models.calls
    print("  transient error -> retried to success (3 attempts) ✓")

    c = _MockClient([ValueError("400 bad request")])
    try:
        judge_dimension(c, {**FIXTURE, "call_id": "selftest_perm"}, "repair_quality")
        raise AssertionError("permanent error should raise")
    except ValueError:
        pass
    assert c.models.calls == 1, c.models.calls
    print("  permanent (400) error -> NOT retried ✓")

    c = _MockClient(["{ not json"])
    try:
        judge_dimension(c, {**FIXTURE, "call_id": "selftest_badjson"}, "repair_quality")
        raise AssertionError("malformed JSON should raise")
    except json.JSONDecodeError:
        pass
    assert c.models.calls == 1, c.models.calls
    print("  malformed JSON -> raised, NOT retried ✓")

    for f in CACHE_DIR.glob("selftest_*"):
        f.unlink()
    _RETRY_BASE = 2
    print("OFFLINE SELFTEST PASSED — validate-before-cache, strict validation, retry policy, rubric "
          "agreement all verified; no network, no real calls touched.")


def fixture_run():
    client = get_client()
    print(f"judging canned FIXTURE {FIXTURE['call_id']} (synthetic; quarantined from real calls)\n")
    dims = judge_call(client, FIXTURE)
    print(json.dumps({"call_id": FIXTURE["call_id"], "dimensions": dims,
                      "_provenance": "uncalibrated (no kappa yet)"}, indent=2))
    assert all(d["provenance"] == "uncalibrated" for d in dims)
    assert all(d["evidence_turn_ids"] and set(d["evidence_turn_ids"]) <= {t["turn_id"] for t in FIXTURE["turns"]} for d in dims)
    print(f"\nFIXTURE judged: {len(dims)}/5 dims, all uncalibrated, all evidence ids valid. "
          "NOT written to out/calls.json (quarantine).")


def smoke():
    client = get_client()
    model, temp = judge_config()
    print(f"judge model: {model} (temperature {temp})")
    for attempt in (1, 2):
        entry, cached = judge_dimension(client, FIXTURE, "repair_quality")
        print(f"\n[{attempt}] {'CACHE HIT' if cached else 'live call'}:\n{json.dumps(entry, indent=2)}")
    print("\nsmoke PASSED — validated {score,reason,evidence}, uncalibrated, cache idempotent")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="one canned dim, run twice (proves cache)")
    ap.add_argument("--selftest", action="store_true", help="OFFLINE: validation+cache+retry on a mock client")
    ap.add_argument("--fixture", action="store_true", help="judge the canned synthetic fixture via Gemini")
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
            sys.exit(1)
    else:
        sys.exit("Batch 4A judge machinery. QUARANTINED — verify with:\n"
                 "  python pipeline/judge.py --selftest   (offline, no network)\n"
                 "  python pipeline/judge.py --fixture    (judge the synthetic fixture via Gemini)\n"
                 "Real-call judging is forbidden until blind human labels exist.")


if __name__ == "__main__":
    main()
