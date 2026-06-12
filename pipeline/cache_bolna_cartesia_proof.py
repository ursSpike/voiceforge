#!/usr/bin/env python3
"""Sponsor-proof: cache a SANITIZED snapshot of the live Bolna agent's Cartesia synthesizer config.

    .venv/bin/python pipeline/cache_bolna_cartesia_proof.py            # ONE authorized GET to Bolna -> out/bolna_cartesia_proof.json
    .venv/bin/python pipeline/cache_bolna_cartesia_proof.py --selftest # offline: validator negative tests, no network

Why: Cartesia runs INSIDE the Bolna agent (synthesizer.provider == cartesia). This captures proof of
that — and ONLY that — so the offline demo can show the sponsor chain without a live call. The
artifact holds EXACTLY five fields and nothing else (no key, prompts, webhook URLs, tools, or the
full config). preflight validates it offline.

Refuses to write unless: the fetched agent IS the configured VoiceForge agent, provider == cartesia,
voice is a non-empty string, and fetched_at is timezone-aware. cartesia_model may be null ONLY if
Bolna genuinely omits it (disclosed, never invented).
"""
import argparse
import hashlib  # noqa: F401  (kept for parity; not used directly)
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENT_ID = "199b03e7-06c6-40e5-8741-37c5c9598061"
PROOF_PATH = ROOT / "out" / "bolna_cartesia_proof.json"
PROOF_KEYS = ("agent_id", "fetched_at", "synthesizer_provider", "cartesia_voice", "cartesia_model")


def validate_proof(proof, agent_id=AGENT_ID):
    """Strict structural + semantic validation. Returns (ok: bool, problem: str). Used by BOTH the
    fetch refusal and preflight — a forged blob like {"synthesizer_provider":"cartesia"} must fail."""
    if not isinstance(proof, dict):
        return False, "not a JSON object"
    keys = set(proof)
    if keys != set(PROOF_KEYS):
        extra, missing = keys - set(PROOF_KEYS), set(PROOF_KEYS) - keys
        return False, f"exact-keys violation (extra {sorted(extra)}, missing {sorted(missing)})"
    if proof["agent_id"] != agent_id:
        return False, f"agent_id {proof['agent_id']!r} != configured {agent_id!r}"
    if proof["synthesizer_provider"] != "cartesia":
        return False, f"synthesizer_provider {proof['synthesizer_provider']!r} != 'cartesia'"
    v = proof["cartesia_voice"]
    if not isinstance(v, str) or not v.strip():
        return False, "cartesia_voice must be a non-empty string"
    m = proof["cartesia_model"]
    if not (m is None or (isinstance(m, str) and m.strip())):
        return False, "cartesia_model must be a non-empty string or null"
    ts = proof["fetched_at"]
    try:
        dt = datetime.fromisoformat(ts) if isinstance(ts, str) else None
    except ValueError:
        dt = None
    if dt is None or dt.tzinfo is None:
        return False, f"fetched_at {ts!r} must be a timezone-aware ISO timestamp"
    return True, ""


def build_proof(cfg):
    """Extract the 5 sanitized fields from a raw Bolna agent-config response. agent_id comes FROM
    the response (so validate_proof enforces it == the configured agent — a missing id becomes None
    and FAILS). Used by both the fetch and online preflight, so they validate identically."""
    fetched_id = cfg.get("agent_id") or cfg.get("id")
    syn = (cfg.get("tasks") or [{}])[0].get("tools_config", {}).get("synthesizer", {}) or {}
    pc = syn.get("provider_config", {}) or {}
    model = pc.get("model")
    return {
        "agent_id": fetched_id,
        "fetched_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "synthesizer_provider": syn.get("provider"),
        "cartesia_voice": pc.get("voice"),
        "cartesia_model": model if (model is None or str(model).strip()) else None,
    }


def fetch_and_cache():
    import urllib.request
    # load BOLNA_API_KEY from .env (no dependency)
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, val = line.split("=", 1)
                os.environ.setdefault(k.strip(), val.strip())
    key = os.environ.get("BOLNA_API_KEY")
    if not key:
        sys.exit("No BOLNA_API_KEY in .env — cannot fetch the agent config.")

    req = urllib.request.Request(f"https://api.bolna.ai/v2/agent/{AGENT_ID}",
                                 headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        cfg = json.loads(r.read().decode())

    proof = build_proof(cfg)
    # validate_proof enforces agent_id == configured (a MISSING/None id FAILS), provider==cartesia,
    # non-empty voice, tz-aware timestamp — refuse to write on any miss.
    ok, problem = validate_proof(proof)
    if not ok:
        sys.exit(f"REFUSED to write sponsor proof: {problem}\n(sanitized view: "
                 f"provider={proof['synthesizer_provider']!r} voice={proof['cartesia_voice']!r} model={proof['cartesia_model']!r})")

    PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = PROOF_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(proof, indent=2) + "\n")
    os.replace(tmp, PROOF_PATH)  # atomic
    print(f"wrote {PROOF_PATH.relative_to(ROOT)} (sanitized — 5 fields, no secrets):")
    print(json.dumps(proof, indent=2))
    if proof["cartesia_model"] is None:
        print("note: Bolna did not return a synthesizer model field — recorded as null (not invented).")


def selftest():
    ok_all = True

    def check(c, msg):
        nonlocal ok_all
        print(("  ok   " if c else "  FAIL ") + msg)
        ok_all = ok_all and c

    base = {"agent_id": AGENT_ID, "fetched_at": "2026-06-12T22:00:00+05:30",
            "synthesizer_provider": "cartesia", "cartesia_voice": "Devansh", "cartesia_model": "sonic-3"}
    check(validate_proof(base)[0], "valid proof accepted")
    check(validate_proof({**base, "cartesia_model": None})[0], "null model accepted (disclosed, not invented)")
    # negative tests
    check(not validate_proof({"synthesizer_provider": "cartesia"})[0], "forged provider-only blob rejected")
    check(not validate_proof({**base, "agent_id": "some-other-agent"})[0], "wrong agent_id rejected")
    check(not validate_proof({**base, "cartesia_voice": ""})[0], "empty voice rejected")
    check(not validate_proof({**base, "fetched_at": "2026-06-12T22:00:00"})[0], "naive (no-tz) timestamp rejected")
    check(not validate_proof({**base, "leaked_api_key": "sk_car_xxx"})[0], "extra secret-looking field rejected")
    check(not validate_proof({**base, "synthesizer_provider": "elevenlabs"})[0], "non-cartesia provider rejected")
    check(not validate_proof({k: base[k] for k in base if k != "cartesia_voice"})[0], "missing-key proof rejected")
    print("\n" + ("PROOF VALIDATOR SELFTEST PASSED ✓ (no network)" if ok_all else "SELFTEST FAILED"))
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true", help="offline validator negative tests (no network)")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    fetch_and_cache()


if __name__ == "__main__":
    main()
