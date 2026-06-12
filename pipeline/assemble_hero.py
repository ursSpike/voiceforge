#!/usr/bin/env python3
"""Hero-call builder. SPEC §7.E: assembly IS ground truth — turns.json is written from the
same timeline that mixes the audio. Zero ASR, zero diarization on the critical path.

  python pipeline/assemble_hero.py tts        # generate agent lines (edge-tts) -> data/hero/raw/
  python pipeline/assemble_hero.py assemble   # preprocess clips -> mix WAV -> turns.json -> failure table

`fto_ms` on each timeline turn = this turn's start relative to the PREVIOUS turn's end.
Negative = engineered overlap (barge-in), positive = gap. After assembly we re-measure with
signals.turn_metrics and ASSERT the engineered sins came out exact — the pipeline checks itself.

Preprocessing (per clip, cached to raw/proc/): mono @ sample_rate, loudnorm I=-18,
lead/tail silence trim (start_periods trick — internal pauses are preserved, which is
what keeps t2's deliberate 2s hesitation intact).

NOTE: the `cartesia` synthesis mode (direct api.cartesia.ai, needs CARTESIA_API_KEY) is an OPTIONAL
HISTORICAL/REPRODUCTION path — it is how the cached hero audio was originally Cartesia-voiced. The
hackathon architecture configures Cartesia inside the Bolna agent's synthesizer; the demo plays the
already-cached hero WAV and needs no Cartesia key.
"""
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERO = ROOT / "data" / "hero"
RAW = HERO / "raw"
PROC = RAW / "proc"

TRIM_DB = "-40dB"


def timeline():
    return json.loads((HERO / "timeline.json").read_text())


def resolve(fname):
    """Exact file, else any extension with the same stem (AirDrop may convert formats)."""
    p = RAW / fname
    if p.exists():
        return p
    hits = [h for h in sorted(RAW.glob(Path(fname).stem + ".*")) if h.is_file()]
    return hits[0] if hits else None


def dur_ms(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return round(float(out.stdout.strip()) * 1000)


def preprocess(src, dst, sr):
    """Normalize + trim lead/tail silence only (areverse trick); internal pauses survive."""
    trim = (f"silenceremove=start_periods=1:start_threshold={TRIM_DB}:start_silence=0.1,"
            f"areverse,"
            f"silenceremove=start_periods=1:start_threshold={TRIM_DB}:start_silence=0.1,"
            f"areverse")
    af = f"aformat=channel_layouts=mono,loudnorm=I=-18:TP=-2,{trim},aresample={sr}"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                    "-i", str(src), "-af", af, "-ar", str(sr), "-ac", "1", str(dst)],
                   check=True)


def tts():
    import edge_tts
    tl = timeline()
    RAW.mkdir(parents=True, exist_ok=True)

    async def run():
        for t in tl["turns"]:
            if t["speaker"] != "agent":
                continue
            out = RAW / t["file"]
            await edge_tts.Communicate(t["text"], tl["agent_voice"]).save(str(out))
            print(f"  {t['turn_id']} -> {out.name}  ({dur_ms(out)}ms)")

    asyncio.run(run())
    print("agent lines done. Record user lines per data/hero/script.md, then: assemble")


def _cartesia_key():
    """Load CARTESIA_API_KEY from .env (no dependency)."""
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    key = os.environ.get("CARTESIA_API_KEY")
    if not key:
        sys.exit("No CARTESIA_API_KEY in .env")
    return key


def tts_cartesia():
    """Re-voice the agent lines with Cartesia Sonic (SPEC §7.E; mandatory hackathon requirement:
    the build must use a Cartesia voice). Writes wav per agent turn and removes any stale edge-tts
    file for that turn so assemble() picks the Cartesia clip."""
    import urllib.request
    tl = timeline()
    RAW.mkdir(parents=True, exist_ok=True)
    key = _cartesia_key()
    vc = tl.get("cartesia") or {}
    if not vc.get("voice_id"):
        sys.exit("timeline.json has no cartesia.voice_id — add one (see pipeline/cartesia_smoke.py voice list).")
    sr = tl.get("sample_rate", 24000)
    hdr = {"X-API-Key": key, "Cartesia-Version": "2024-11-13", "Content-Type": "application/json"}

    for t in tl["turns"]:
        if t["speaker"] != "agent":
            continue
        for old in RAW.glob(Path(t["file"]).stem + ".*"):   # drop the prior edge-tts mp3 for this turn
            old.unlink()
        body = {"model_id": vc.get("model", "sonic-3"), "transcript": t["text"],
                "voice": {"mode": "id", "id": vc["voice_id"]},
                "output_format": {"container": "wav", "encoding": "pcm_s16le", "sample_rate": sr},
                "language": vc.get("language", "en")}
        req = urllib.request.Request("https://api.cartesia.ai/tts/bytes", headers=hdr,
                                     data=json.dumps(body).encode(), method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            audio = r.read()
        out = RAW / (Path(t["file"]).stem + ".wav")
        out.write_bytes(audio)
        print(f"  {t['turn_id']} -> {out.name}  ({dur_ms(out)}ms)  [cartesia {vc.get('model','sonic-3')}/{vc.get('voice')}]")
    print(f"agent lines re-voiced with Cartesia ({vc.get('voice')}). Now: assemble")


def assemble():
    sys.path.insert(0, str(ROOT / "pipeline"))
    from signals import turn_metrics, analyze, load_rubric, failure_table, mmss

    tl = timeline()
    sr = tl.get("sample_rate", 24000)

    missing = [t["file"] for t in tl["turns"] if resolve(t["file"]) is None]
    if missing:
        sys.exit("missing raw clips in data/hero/raw/: " + ", ".join(missing))

    # 1. preprocess every clip (idempotent enough for tonight: always regenerate)
    PROC.mkdir(parents=True, exist_ok=True)
    clips = {}
    for t in tl["turns"]:
        src = resolve(t["file"])
        dst = PROC / (t["turn_id"] + ".wav")
        preprocess(src, dst, sr)
        clips[t["turn_id"]] = (dst, dur_ms(dst))

    # 2. place by engineered FTO
    placed, cursor_end = [], 0
    for t in tl["turns"]:
        path, d = clips[t["turn_id"]]
        start = 0 if t.get("fto_ms") is None else max(0, cursor_end + t["fto_ms"])
        placed.append({**t, "path": path, "start": start, "end": start + d})
        cursor_end = start + d
        print(f"  {t['turn_id']:>3} {t['speaker']:5} {mmss(start):>5}–{mmss(start + d):<5} ({d}ms)")

    # 3. mix
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for p in placed:
        cmd += ["-i", str(p["path"])]
    chains, labels = [], []
    for i, p in enumerate(placed):
        chains.append(f"[{i}:a]adelay={p['start']}|{p['start']}[a{i}]")
        labels.append(f"[a{i}]")
    chains.append("".join(labels) + f"amix=inputs={len(placed)}:normalize=0,alimiter=limit=0.95[mix]")
    wav = HERO / f"{tl['call_id']}.wav"
    cmd += ["-filter_complex", ";".join(chains), "-map", "[mix]", "-ar", str(sr), "-ac", "1", str(wav)]
    subprocess.run(cmd, check=True)

    # 4. turns.json — the call_log, FROM THE SAME PLACEMENT
    call = {
        "call_id": tl["call_id"], "source": tl["source"], "language": tl["language"],
        "stress_profile": tl["stress_profile"], "workflow_type": tl["workflow_type"],
        "turns": [{"turn_id": p["turn_id"], "speaker": p["speaker"], "text": p["text"],
                   "start_ms": p["start"], "end_ms": p["end"]} for p in placed],
        "audio_path": f"data/hero/{wav.name}",
        "metadata": {"constructed": True, "timestamps_from": "assembly_timeline",
                     # record the voice ACTUALLY used: Cartesia when the call was re-voiced, else edge-tts
                     "agent_voice": (f"cartesia/{(tl.get('cartesia') or {}).get('voice')}"
                                     if tl.get("cartesia") else tl["agent_voice"]),
                     "voice_provider": "cartesia" if tl.get("cartesia") else "edge-tts",
                     "disclosure": "constructed demo scenario; see docs/limitations.md"},
    }
    (HERO / "turns.json").write_text(json.dumps(call, indent=2))

    # 5. self-check: measured FTO must equal engineered FTO at every transition
    measured = {(e["prev_turn_id"], e["next_turn_id"]): e["fto_ms"]
                for e in turn_metrics(call["turns"])}
    for a, b in zip(tl["turns"], tl["turns"][1:]):
        want = b["fto_ms"]
        got = measured[(a["turn_id"], b["turn_id"])]
        assert got == want, f"{a['turn_id']}->{b['turn_id']}: engineered {want}ms, measured {got}ms"
    print(f"\nself-check OK: every measured FTO equals its engineered value")
    print(f"wrote {wav.name} ({dur_ms(wav) / 1000:.1f}s) + turns.json\n")

    # 6. the failure table — the money shot's data
    result = analyze(call["turns"], load_rubric())
    print("FAILURE TABLE")
    print(failure_table(result))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "assemble"
    if mode not in ("tts", "cartesia", "assemble"):
        sys.exit("usage: assemble_hero.py [tts|cartesia|assemble]   "
                 "(tts=edge-tts agent lines · cartesia=Sonic re-voice · assemble=mix+turns+table)")
    {"tts": tts, "cartesia": tts_cartesia, "assemble": assemble}[mode]()
