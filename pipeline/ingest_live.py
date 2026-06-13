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

LIVE_PROVENANCE = {"slice": "live_today", "calibrated": False, "label": "LIVE · UNCALIBRATED"}


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
    """--latest: resolve the most-recent execution id, then fetch_raw it.

    TODO (on-site, Buddy-confirm): Bolna's "list executions" endpoint is NOT verified in this repo
    (the cached proof only hit /v2/agent/<id> and /executions/<id>). Do NOT fabricate it. When the
    Buddy confirms the real list endpoint + the field that holds the id, fill the two lines below
    and delete this guard. Until then --latest refuses rather than guess."""
    # AGENT_ID = "199b03e7-06c6-40e5-8741-37c5c9598061"  # the Cartesia agent (from the cached call)
    # listing = _get_json(f"/agent/{AGENT_ID}/executions?limit=1")   # <-- CONFIRM path + query
    # execution_id = listing["data"][0]["id"]                        # <-- CONFIRM id field
    # return fetch_raw(execution_id)
    sys.exit("--latest is a documented stub: the Bolna list-executions endpoint is unverified in "
             "this repo. On-site, have the Buddy confirm the endpoint, fill fetch_latest(), then "
             "run with the explicit id instead:  --execution <id>")


def normalize_live(raw_payload):
    """SAME deterministic normalize as production (ingest_bolna.normalize), then stamp live
    provenance into metadata. call_id stays bolna_<id[:8]> from the shared normalizer; we DO NOT
    rename it — isolation comes from the live_ file namespace + the provenance tag, so a live call
    and the frozen calibration call can never collide on disk (bolna_live_* vs bolna_*)."""
    call = IB.normalize(raw_payload)                    # identical turn reconstruction + lang detection
    call["provenance"] = dict(LIVE_PROVENANCE)
    call["metadata"]["note"] = ("LIVE on-site call (Cartesia voice); UNCALIBRATED, not part of the "
                                "frozen 46-call calibration set")
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

    call = normalize_live(raw_payload)
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
        check(call["call_id"] == "bolna_246cd9f3", "call_id from the SHARED normalizer (bolna_<id[:8]>)")

        # determinism: the live path's turns/scorecard/signals must MATCH production's cached output
        prod_norm = json.loads((NORM / "bolna_246cd9f3.json").read_text())
        check(call["turns"] == prod_norm["turns"]
              and call["language"] == prod_norm["language"],
              "turns + language IDENTICAL to production normalize (same deterministic build)")
        prod_rec = json.loads((ROOT / "out" / "call_bolna_246cd9f3.json").read_text())
        check(record["scorecard"] == prod_rec["scorecard"]
              and record["signals"] == prod_rec["signals"]
              and record["cost"] == prod_rec["cost"]
              and record["outcome"] == prod_rec["outcome"],
              "scorecard/signals/cost/outcome IDENTICAL to production build_record")

        # --latest is an honest stub (refuses, never fabricates an endpoint)
        import subprocess
        r = subprocess.run([sys.executable, str(ROOT / "pipeline" / "ingest_live.py"), "--latest"],
                           capture_output=True, text=True)
        check(r.returncode != 0 and "stub" in (r.stdout + r.stderr).lower(),
              "--latest refuses (documented stub, no fabricated endpoint)")

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
    g.add_argument("--latest", action="store_true", help="most-recent execution (documented stub — see fetch_latest)")
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
