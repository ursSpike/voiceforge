#!/usr/bin/env python3
"""Live on-site Bolna calls -> isolated 'live_today' slice. The LIVE-BRIDGE (Jun 13).

Fresh on-site calls (Cartesia-voiced agent) ingest through the SAME deterministic pipeline as
production — ingest_bolna.reconstruct_turns/normalize + score.build_record — but land in a
SEPARATE namespace so the frozen 46-call calibration experiment is never touched:

    data/provider_logs/bolna_live_<id>.json   raw payload  {"execution":…, "log":{"data":[…]}}
    data/normalized/live/bolna_live_<id>.json  normalized call_log (call_id = bolna_live_<id[:8]>) — SUBDIR keeps it out of the frozen pipeline's top-level glob
    out/live_calls.json                         merged view (built by judge_live.py, not here)

Provenance is stamped on every normalized live call: {"slice":"live_today","calibrated":false,
"label":"LIVE · UNCALIBRATED"}. These calls carry NO human gold labels and are NOT part of the
kappa-calibrated set — the /platform LIVE-TODAY section must render them as uncalibrated.

    .venv/bin/python pipeline/ingest_live.py --execution <id>   # fetch-or-load + normalize one call
    .venv/bin/python pipeline/ingest_live.py --latest           # most-recent execution (TODO: on-site)
    .venv/bin/python pipeline/ingest_live.py --selftest          # OFFLINE: replay cached 246cd9f3 (no network)

GUARDRAIL: never reads or writes the frozen calibration artifacts (eval/*, out/judge_results.json,
out/calls.json, out/analytics.json, out/demo_report_data.json, rubric.yaml is read-only via score).
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
RAW = ROOT / "data" / "provider_logs"
NORM = ROOT / "data" / "normalized"
# ISOLATION (audit blocker #1): live calls land in a SUBDIR so the production consumers that do a
# top-level NORM.glob("*.json") — score.py, build_manifest.py, schemas.py, preflight.py — can never
# pick them up. The glob is non-recursive, so data/normalized/live/ is invisible to the frozen pipeline.
LIVE_NORM = NORM / "live"

# production deterministic pieces, reused verbatim (no fork of the normalize / signals logic)
import ingest_bolna as IB  # noqa: E402  (reconstruct_turns + normalize, the SAME as the cached path)

BASE = "https://api.bolna.ai"   # SPEC §7.G / §10 cite-card: API host api.bolna.ai (matches bolna_smoke.py)

# synthesizer_verified defaults False (audit P0C edge 2): never infer Cartesia from liveness alone —
# flip to True only after validating the fetched agent config via cache_bolna_cartesia_proof.py.
LIVE_PROVENANCE = {"slice": "live_today", "calibrated": False, "label": "LIVE · UNCALIBRATED",
                   "synthesizer_verified": False}


def _load_env():
    """Read BOLNA_API_KEY from .env (no dependency), mirroring bolna_smoke.py / cache_bolna_*."""
    import os
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    return os.environ.get("BOLNA_API_KEY")


def _get_json(path):
    """Authenticated GET (urllib, no dependency) — used ONLY on-site under --execution/--latest.
    NEVER called by --selftest or any offline path."""
    import urllib.request
    key = _load_env()
    if not key:
        sys.exit("No BOLNA_API_KEY in .env — needed to fetch a live execution. "
                 "(Offline replay: use --selftest, which makes no network call.)")
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=30) as r:   # noqa: S310 (host pinned to api.bolna.ai)
        return json.loads(r.read().decode())


def fetch_raw(execution_id):
    """Build the raw payload {"execution":…, "log":{"data":[…]}} from the two Bolna endpoints,
    matching the shape ingest_bolna expects from the cached file. ON-SITE ONLY.

    Endpoint shapes are taken from the cached payload (execution = the execution object; log =
    {"data":[component events], "status":…}). If the on-site account's paths differ, the Buddy
    confirms them and only these two f-strings change — the normalize/build path is unaffected."""
    execution = _get_json(f"/executions/{execution_id}")          # the execution object
    log = _get_json(f"/executions/{execution_id}/log")            # {"data":[…], "status":…}
    return {"execution": execution, "log": log}


def fetch_latest():
    """--latest: resolve the most-recent execution id for the agent, then fetch_raw it.

    Endpoint verified against the Bolna docs (docs/BOLNA_API_NOTES.md):
      GET /v2/agent/{agent_id}/executions?page_size=1&page_number=1  ->  data[0]["id"]
    The agent id comes from $BOLNA_AGENT_ID — set it to TODAY's agent (not the old cached one).
    CAVEAT: the ordering of data[] is undocumented; confirm with the Buddy that data[0] is the newest.
    If unsure, just use  --execution <id>  with the id Bolna shows you (always unambiguous)."""
    import os
    agent_id = os.environ.get("BOLNA_AGENT_ID")
    if not agent_id:
        sys.exit("--latest needs $BOLNA_AGENT_ID set to today's agent id. "
                 "Either `export BOLNA_AGENT_ID=<id>` or use the explicit `--execution <id>`.")
    listing = _get_json(f"/v2/agent/{agent_id}/executions?page_size=1&page_number=1")
    rows = listing.get("data") or []
    if not rows:
        sys.exit(f"no executions found for agent {agent_id} (make a call first, or use --execution <id>).")
    return fetch_raw(rows[0]["id"])  # data[0] assumed newest — verify ordering with the Buddy


def normalize_live(raw_payload, execution_id):
    """SAME deterministic normalize as production (ingest_bolna.normalize), then stamp live provenance
    and a NAMESPACED internal call_id (audit P0C edge 1). The call_id is rewritten to
    bolna_live_<id[:8]> — NOT left as bolna_<id[:8]> — so identity AND the judge-cache key (keyed on
    call_id) can never collide with the frozen bolna_* calibration call; isolation no longer relies on
    the filename/subdir alone. Synthesizer provider is NOT assumed Cartesia just because the call is
    live (audit P0C edge 2): it is marked unverified until validated from the fetched agent config
    (pipeline/cache_bolna_cartesia_proof.py)."""
    cid, _short = live_call_id(execution_id)
    call = IB.normalize(raw_payload)                    # identical turn reconstruction + lang detection
    call["call_id"] = cid                               # namespaced identity (was bolna_<id[:8]>)
    call["provenance"] = dict(LIVE_PROVENANCE)          # carries synthesizer_verified=False by default
    call["metadata"]["note"] = ("LIVE on-site call; UNCALIBRATED, not part of the frozen 46-call "
                                "calibration set. Synthesizer provider UNVERIFIED — validate via "
                                "pipeline/cache_bolna_cartesia_proof.py before claiming Cartesia.")
    return call


def live_call_id(execution_id):
    """Namespaced ids so live artifacts never overwrite frozen ones."""
    short = execution_id[:8]
    return f"bolna_live_{short}", short


def ingest_one(raw_payload, execution_id, norm_dir=LIVE_NORM, raw_dir=RAW, write_raw=True):
    """Raw -> cached raw file -> normalized+validated call_log with live provenance -> deterministic
    record. Returns (call_log, call_record). norm_dir/raw_dir are injectable so the selftest writes
    to a TEMP dir, never the real data/ tree."""
    from schemas import validate
    from score import build_record

    _, short = live_call_id(execution_id)
    if write_raw:
        raw_dir.mkdir(parents=True, exist_ok=True)
        (raw_dir / f"bolna_live_{short}.json").write_text(json.dumps(raw_payload, indent=2))

    call = normalize_live(raw_payload, execution_id)
    validate(call, "call_log")                          # constitution must hold BEFORE writing

    norm_dir.mkdir(parents=True, exist_ok=True)
    (norm_dir / f"bolna_live_{short}.json").write_text(json.dumps(call, indent=2))

    record = build_record(call)                         # production deterministic signals/scorecard/cost
    validate(record, "call_record")
    return call, record


# ---------------------------------------------------------------- offline selftest (no network)
def selftest():
    """Replay the EXISTING cached raw payload (data/provider_logs/bolna_246cd9f3.json) THROUGH the
    live path into a TEMP dir. Proves: fetch-free, frozen files untouched, identical deterministic
    output to production, live provenance stamped. No network, no real data/ or out/ writes."""
    import hashlib
    import shutil
    import tempfile

    ok = True

    def check(c, msg):
        nonlocal ok
        print(("  ok   " if c else "  FAIL ") + msg)
        ok = ok and c

    cached = RAW / "bolna_246cd9f3.json"
    check(cached.exists(), f"cached raw payload present ({cached.name})")
    if not cached.exists():
        print("\nSELFTEST FAILED — missing cached payload")
        return 1
    raw = json.loads(cached.read_text())

    # frozen guard: snapshot hashes before, re-check after (these files must never be touched)
    frozen = ["eval/label_manifest.json", "eval/labels_spike.csv", "eval/label_snapshot.json",
              "out/judge_results.json", "out/calls.json", "out/analytics.json",
              "out/demo_report_data.json", "rubric.yaml"]
    before = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in frozen if (ROOT / f).exists()}

    with tempfile.TemporaryDirectory(prefix="vf_live_") as td:
        td = Path(td)
        tnorm, traw = td / "normalized", td / "provider_logs"
        # replay the cached payload through the FULL live ingest into the temp dir
        call, record = ingest_one(raw, IB.EXEC_ID, norm_dir=tnorm, raw_dir=traw)

        _, short = live_call_id(IB.EXEC_ID)
        check((traw / f"bolna_live_{short}.json").exists()
              and (tnorm / f"bolna_live_{short}.json").exists(),
              "live raw + normalized written to TEMP dir (not real data/)")
        check(call["provenance"] == LIVE_PROVENANCE
              and call["provenance"]["calibrated"] is False
              and call["provenance"]["label"] == "LIVE · UNCALIBRATED",
              "live provenance stamped {slice:live_today, calibrated:false, LIVE · UNCALIBRATED}")
        check(call["call_id"] == "bolna_live_246cd9f3", "call_id namespaced bolna_live_<id[:8]> (no collision with frozen bolna_*)")

        # determinism: the live path's turns/scorecard/signals must MATCH production's cached output
        prod_norm = json.loads((NORM / "bolna_246cd9f3.json").read_text())
        check(call["turns"] == prod_norm["turns"]
              and call["language"] == prod_norm["language"],
              "turns + language IDENTICAL to production normalize (same deterministic build)")
        prod_rec = json.loads((ROOT / "out" / "call_bolna_246cd9f3.json").read_text())
        def _no_cid(d):  # scorecard/cost/outcome embed call_id; namespacing it is intentional — compare the MATH
            return {k: v for k, v in d.items() if k != "call_id"} if isinstance(d, dict) else d
        check(_no_cid(record["scorecard"]) == _no_cid(prod_rec["scorecard"])
              and record["signals"] == prod_rec["signals"]
              and _no_cid(record["cost"]) == _no_cid(prod_rec["cost"])
              and _no_cid(record["outcome"]) == _no_cid(prod_rec["outcome"]),
              "scorecard/signals/cost/outcome IDENTICAL to production build_record (modulo namespaced call_id)")

        # --latest needs $BOLNA_AGENT_ID; with it unset, it refuses cleanly (no network, no fabrication)
        import subprocess
        env = {k: v for k, v in os.environ.items() if k != "BOLNA_AGENT_ID"}
        r = subprocess.run([sys.executable, str(ROOT / "pipeline" / "ingest_live.py"), "--latest"],
                           capture_output=True, text=True, env=env)
        out = (r.stdout + r.stderr).lower()
        check(r.returncode != 0 and "bolna_agent_id" in out and "execution" in out,
              "--latest without $BOLNA_AGENT_ID refuses cleanly (points to --execution; no network)")

    after = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in before}
    check(before == after, f"all {len(before)} frozen files byte-identical after selftest")

    print("\n" + ("INGEST-LIVE SELFTEST PASSED ✓ (offline; frozen files untouched; production-identical)"
                  if ok else "INGEST-LIVE SELFTEST FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(
        description="Ingest fresh on-site Bolna calls into the isolated live_today slice. "
                    "Network modes (--execution/--latest) require BOLNA_API_KEY; --selftest is offline.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--execution", metavar="ID", help="fetch + ingest this Bolna execution id")
    g.add_argument("--latest", action="store_true", help="most-recent execution for $BOLNA_AGENT_ID (verify ordering with Buddy)")
    g.add_argument("--selftest", action="store_true", help="OFFLINE replay of the cached payload (no network)")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    raw = fetch_latest() if args.latest else fetch_raw(args.execution)
    exec_id = raw["execution"]["id"] if args.latest else args.execution
    call, record = ingest_one(raw, exec_id)
    cid = call["call_id"]
    print(f"ingested LIVE {cid} (bolna_live_{exec_id[:8]})  "
          f"{len(call['turns'])} turns, {call['language']}, "
          f"cost {call['metadata']['total_cost_cents']}c  [{call['provenance']['label']}]")
    lat = record["signals"]["latency"]
    print(f"latency: median {lat['median_gap_ms']}ms p90 {lat['p90_gap_ms']}ms | barge-ins {record['signals']['n_barge_ins']}")
    print("normalized -> data/normalized/live/bolna_live_<id>.json  (raw -> data/provider_logs/)")
    print("next: python pipeline/judge_live.py   -> out/live_judge_results.json + out/live_calls.json")


if __name__ == "__main__":
    main()
