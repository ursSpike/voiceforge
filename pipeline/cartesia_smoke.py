#!/usr/bin/env python3
"""Cartesia API-key smoke test + voice list.

OPTIONAL HISTORICAL / REPRODUCTION UTILITY — NOT required by the current hackathon architecture,
where Cartesia is configured INSIDE the Bolna agent's synthesizer (provider=cartesia) and no separate
Cartesia key is needed to run or demo VoiceForge. Only verifies a direct CARTESIA_API_KEY for
re-synthesizing the cached hero audio.

Add your key to .env as CARTESIA_API_KEY (format sk_car_...), then:

    .venv/bin/python pipeline/cartesia_smoke.py

Hits GET /voices (read-only, no credit charge) to prove the key works and list available voices,
so we can pick an Indian-English agent voice to re-voice the hero call's agent lines.

stdlib only (urllib) — no extra dependency.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://api.cartesia.ai"
VERSION = "2024-11-13"   # Cartesia-Version header (verified working); newer dates also accepted


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def get(path, key, attempts=3):
    headers = {"X-API-Key": key, "Cartesia-Version": VERSION}
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(BASE + path, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read().decode())
        except urllib.error.HTTPError:
            raise                                  # 401/403 etc. are real, not transient
        except (TimeoutError, urllib.error.URLError, OSError) as e:
            last = e
            if i < attempts - 1:
                print(f"  …attempt {i + 1} timed out, retrying in 2s")
                time.sleep(2)
    raise last


def main():
    load_env()
    key = os.environ.get("CARTESIA_API_KEY")
    if not key or key == "paste-key-here":
        sys.exit("No CARTESIA_API_KEY in .env (format sk_car_...). Add it and re-run.")

    print(f"key loaded ({key[:7]}…{key[-4:]}) — calling {BASE}/voices …")
    try:
        _, data = get("/voices", key)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:400]
        hint = " (401/403 = key wrong — check it in the Cartesia dashboard)" if e.code in (401, 403) else ""
        sys.exit(f"HTTP {e.code} from /voices{hint}\n{body}")
    except (TimeoutError, urllib.error.URLError, OSError) as e:
        sys.exit(f"network timeout/error reaching {BASE} after retries: {getattr(e, 'reason', e)}\n"
                 "Transient — check wifi and re-run.")

    voices = data if isinstance(data, list) else data.get("data", data)
    print(f"\n✓ KEY WORKS — {len(voices)} voices available.\n")
    # surface English voices first (best fit for the hero agent), then the rest
    def lang(v):
        return v.get("language") or (v.get("languages") or [""])[0]
    eng = [v for v in voices if str(lang(v)).startswith("en")]
    show = (eng or voices)[:15]
    print(f"{'name':<26}{'lang':<8}id")
    for v in show:
        print(f"  {str(v.get('name'))[:24]:<24}{str(lang(v)):<8}{v.get('id')}")
    if eng:
        print(f"\n({len(eng)} English voices — pick one to re-voice the hero agent with Sonic.)")


if __name__ == "__main__":
    main()
