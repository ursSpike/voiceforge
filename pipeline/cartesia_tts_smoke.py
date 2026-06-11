#!/usr/bin/env python3
"""Cartesia TTS smoke — proves the SYNTHESIS path (the binding submission requirement:
"You must use a Cartesia voice model in your build").

cartesia_smoke.py only proves the key authenticates (GET /voices, no charge). This one
actually calls POST /tts/bytes with a Sonic model and writes a .wav, so we know the
credit-spending generation path works end to end. Doubles as the §7.E comparison sample
(Cartesia agent voice vs the current edge-tts en-IN Neerja) for the hero re-voice call.

    .venv/bin/python pipeline/cartesia_tts_smoke.py [voice_id] ["line to speak"]

Defaults: first English voice, a generic agent line. Output -> samples/cartesia_smoke.wav.
stdlib only (urllib).
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
VERSION = "2024-11-13"
MODEL = "sonic-2"                       # current Sonic flagship
DEFAULT_VOICE = "db6b0ed5-d5d3-463d-ae85-518a07d3c2b4"   # Skylar - Friendly Guide (en)
DEFAULT_LINE = ("Hi, this is your assistant calling about your appointment. "
                "I can help you reschedule — what day works best for you?")
OUT = ROOT / "samples" / "cartesia_smoke.wav"


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def post_bytes(path, key, payload, attempts=3):
    headers = {
        "X-API-Key": key,
        "Cartesia-Version": VERSION,
        "Content-Type": "application/json",
    }
    body = json.dumps(payload).encode()
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(BASE + path, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.status, r.read()
        except urllib.error.HTTPError:
            raise                                  # 401/402/403/422 are real, not transient
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

    voice = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_VOICE
    line = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_LINE
    payload = {
        "model_id": MODEL,
        "transcript": line,
        "voice": {"mode": "id", "id": voice},
        "output_format": {"container": "wav", "encoding": "pcm_s16le", "sample_rate": 44100},
    }

    print(f"key loaded ({key[:7]}…{key[-4:]}) — synthesizing with {MODEL}, voice {voice[:8]}… …")
    try:
        _, audio = post_bytes("/tts/bytes", key, payload)
    except urllib.error.HTTPError as e:
        body = e.read().decode()[:500]
        hints = {401: " (key wrong)", 403: " (key wrong / not permitted)",
                 402: " (out of Cartesia credits — ping the organizers)",
                 422: " (bad voice id or model — check the value)"}
        sys.exit(f"HTTP {e.code} from /tts/bytes{hints.get(e.code, '')}\n{body}")
    except (TimeoutError, urllib.error.URLError, OSError) as e:
        sys.exit(f"network timeout/error reaching {BASE} after retries: {getattr(e, 'reason', e)}\n"
                 "Transient — check wifi and re-run.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(audio)
    kb = len(audio) / 1024
    print(f"\n✓ SYNTHESIS WORKS — Cartesia voice model verified end to end.")
    print(f"  wrote {OUT.relative_to(ROOT)} ({kb:.1f} KB wav)")
    print(f'  line: "{line}"')
    print("\n  Listen, then compare against the current edge-tts en-IN hero agent (§7.E).")


if __name__ == "__main__":
    main()
