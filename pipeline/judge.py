#!/usr/bin/env python3
"""VoiceForge LLM judge — Gemini Flash via AI Studio key. SPEC §7.B.

Contract: temperature 0, JSON output, every judged dimension returns
{score, reason, evidence_turn_ids}. Every response cached to data/.judge_cache/
keyed by (call_id, dimension, prompt_hash) — reruns are free and idempotent.

Block 0: client + cache + `--smoke` (one tiny judge call, run twice to prove the cache).
Block 3: per-dimension prompts over normalized calls (judge_dimension below is the entry point).
"""
import argparse
import hashlib
import json
import os
import sys
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


def judge_dimension(client, call_id, dimension, prompt):
    """One judged dimension for one call. Returns (parsed_json, from_cache)."""
    model, temperature = judge_config()
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    phash = hashlib.sha256(f"{model}|{prompt}".encode()).hexdigest()[:16]
    cpath = CACHE_DIR / f"{call_id}__{dimension}__{phash}.json"
    if cpath.exists():
        return json.loads(cpath.read_text()), True

    from google.genai import types
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
        ),
    )
    out = json.loads(resp.text)
    for required in ("score", "reason", "evidence_turn_ids"):
        if required not in out:
            raise ValueError(f"judge returned JSON missing '{required}': {out}")
    cpath.write_text(json.dumps(out, indent=2))
    return out, False


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
    args = ap.parse_args()
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
        sys.exit("Full pipeline judging lands in Block 3. For now: python pipeline/judge.py --smoke")


if __name__ == "__main__":
    main()
