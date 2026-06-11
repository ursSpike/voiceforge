#!/usr/bin/env python3
"""Bolna API-key smoke test + wallet/credits check. SPEC §7.G.

Generate a key at platform.bolna.ai -> Developers -> "Generate a new API Key" (shown ONCE),
add it to .env as BOLNA_API_KEY, then:

    .venv/bin/python pipeline/bolna_smoke.py

This hits GET /me (read-only, no charge) which returns your name, email and wallet
balance. It (1) proves the key works = "use it once", and (2) shows your credit balance so you
can confirm when the organizers top it up. Re-run after they add credits to watch the number rise.

stdlib only (urllib) — no extra dependency.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://api.bolna.ai"   # SPEC §7.G / §10 cite-card: API host api.bolna.ai


def load_env():
    """Tiny .env loader (same pattern as pipeline/judge.py) — no dependency."""
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def get(path, key):
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, json.loads(r.read().decode())


def main():
    load_env()
    key = os.environ.get("BOLNA_API_KEY")
    if not key or key == "paste-key-here":
        sys.exit("No BOLNA_API_KEY in .env.\n"
                 "  1. platform.bolna.ai -> Developers tab -> 'Generate a new API Key'\n"
                 "  2. copy it (it is shown only ONCE)\n"
                 "  3. add to .env:  BOLNA_API_KEY=<your key>\n"
                 "  4. re-run this script")

    print(f"key loaded ({key[:6]}…{key[-4:]}) — calling {BASE}/me …")
    try:
        _, info = get("/me", key)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        hint = " (401 = key wrong/expired — regenerate under Developers)" if e.code == 401 else ""
        sys.exit(f"HTTP {e.code} from /me{hint}\n{body}")
    except urllib.error.URLError as e:
        sys.exit(f"could not reach {BASE}: {e.reason}\n(check internet / that the base URL is right)")

    print("\n✓ KEY WORKS — your Bolna account is live.\n")
    # field names vary; print the likely credit/identity ones if present, then the full payload
    for label in ("name", "email", "wallet", "wallet_balance", "balance", "credits", "amount",
                  "concurrency", "concurrency_limit"):
        if label in info:
            print(f"  {label}: {info[label]}")
    print("\nfull /me response:")
    print(json.dumps(info, indent=2)[:1500])
    print("\nWALLET / CREDITS: look for a balance field above. After the organizers add credits,\n"
          "re-run this script and the number should go up.")


if __name__ == "__main__":
    main()
