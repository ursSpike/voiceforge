#!/usr/bin/env python3
"""Batch E — the GATED real judge run. Produces out/judge_results.json (the contract demo_report.py
and the dashboard consume). Refuses to run until the blind-label gate opens.

    .venv/bin/python pipeline/judge_run.py --selftest    # offline mock-client test (no network, no gate)
    .venv/bin/python pipeline/judge_run.py               # REAL run — only after >=40 blind binary labels
    .venv/bin/python pipeline/judge_run.py --dry-run     # show the gate + plan, call nothing

GATE (enforced, in order):
  1. pipeline/validate_labels.py must pass (exit 0) on the canonical CSV.
  2. >= FLOOR (40) binary labels must exist.
  3. Only calls in the FROZEN manifest are judged — nothing else, ever.

HUMAN<->JUDGE BINARY MAPPING (documented, the rule kappa uses):
  The judge's binary outcome comes from ONE dedicated outcome judgment per call (prompted below) —
  NOT derived post-hoc from the 5 semantic dims. label in {success, fail}; same definition the blind
  annotator used ("did the caller ultimately achieve their essential goal?"). rule recorded per call.

Run manifest records: model, temperature, rubric_hash, labels_csv_sha256, manifest_sha256, n_calls,
cache_hits, failures, started (ISO). Deterministic dims in out/calls.json are NEVER touched —
judge output lives in its own artifact with provenance=uncalibrated until kappa exists.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import judge as J  # noqa: E402  (validated machinery: validate-before-cache, retry policy, dims)

FLOOR = 40
OUT = ROOT / "out" / "judge_results.json"
BINARY_RULE = ("dedicated outcome judgment per call (temperature 0, JSON, evidence-cited); "
               "label in {success,fail}; same question the blind annotator answered. "
               "NOT derived from the 5 semantic dims.")

OUTCOME_PROMPT = (
    "You are a strict but fair judge of voice-agent calls. Decide the OVERALL OUTCOME.\n\n"
    "success = the caller's essential goal was achieved or they received the requested usable "
    "information. fail = the goal remained unresolved, was handled incorrectly, or was falsely "
    "claimed complete. Minor awkwardness does not make a completed task fail; politeness does not "
    "make an unresolved task succeed.\n\n"
    "Call (turn_id speaker: text):\n{call_text}\n\n"
    'Return ONLY JSON: {{"label": "success" or "fail", "reason": "<one falsifiable sentence>", '
    '"evidence_turn_ids": ["<turn ids>"]}}')


def validate_binary(parsed, call):
    """Strict validation of the outcome judgment (mirrors judge.validate_dim discipline)."""
    if not isinstance(parsed, dict):
        raise ValueError("outcome: response is not a JSON object")
    for k in ("label", "reason", "evidence_turn_ids"):
        if k not in parsed:
            raise ValueError(f"outcome: missing '{k}'")
    if parsed["label"] not in ("success", "fail"):
        raise ValueError(f"outcome: label {parsed['label']!r} not in success|fail")
    if not isinstance(parsed["reason"], str) or not parsed["reason"].strip():
        raise ValueError("outcome: reason must be a non-empty string")
    ev_raw = parsed["evidence_turn_ids"]
    if not isinstance(ev_raw, list) or not all(isinstance(e, str) for e in ev_raw):
        raise ValueError("outcome: evidence_turn_ids must be a list of strings")
    valid = {t["turn_id"] for t in call["turns"]}
    ev = [e for i, e in enumerate(ev_raw) if e in valid and e not in ev_raw[:i]]
    if not ev:
        raise ValueError(f"outcome: no valid evidence turn id (cited {ev_raw})")
    return {"label": parsed["label"], "reason": parsed["reason"].strip(),
            "evidence_turn_ids": ev, "rule": BINARY_RULE, "provenance": "uncalibrated"}


def judge_outcome(client, call):
    """Binary outcome judgment, validate-before-cache, same cache discipline as judge_dimension."""
    model, temperature = J.judge_config()
    prompt = OUTCOME_PROMPT.format(call_text=J.format_call(call))
    J.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    phash = hashlib.sha256(f"{model}|{temperature}|{prompt}".encode()).hexdigest()[:16]
    cpath = J.CACHE_DIR / f"{call['call_id']}__outcome_binary__{phash}.json"
    if cpath.exists():
        return json.loads(cpath.read_text()), True
    parsed = J._generate_json(client, model, temperature, prompt)
    entry = validate_binary(parsed, call)            # raises on invalid -> nothing cached
    cpath.write_text(json.dumps(entry, indent=2))
    return entry, False


def gate(skip=False):
    """The blind-label gate. Returns (manifest, labels_csv_sha, manifest_sha)."""
    man_path = ROOT / "eval" / "label_manifest.json"
    csv_path = ROOT / "eval" / "labels_spike.csv"
    manifest = json.loads(man_path.read_text())
    man_sha = hashlib.sha256(man_path.read_bytes()).hexdigest()
    csv_sha = hashlib.sha256(csv_path.read_bytes()).hexdigest() if csv_path.exists() else None
    if skip:
        return manifest, csv_sha, man_sha
    r = subprocess.run([sys.executable, str(ROOT / "pipeline" / "validate_labels.py"), "--quiet"])
    if r.returncode != 0:
        sys.exit("GATE CLOSED: validate_labels.py failed — fix the label CSV first.")
    v = json.loads((ROOT / "out" / "label_validation.json").read_text())
    if v.get("binary", 0) < FLOOR:
        sys.exit(f"GATE CLOSED: {v.get('binary', 0)} binary labels < floor {FLOOR}. "
                 "Finish blind labeling before any real-call judging.")
    return manifest, csv_sha, man_sha


def run(client, manifest, csv_sha, man_sha, calls_dir=None):
    import yaml
    model, temperature = J.judge_config()
    rubric_hash = hashlib.sha256((ROOT / "rubric.yaml").read_bytes()).hexdigest()[:16]
    calls_dir = calls_dir or (ROOT / "data" / "normalized")
    results, cache_hits, failures = {}, 0, []
    for cid in manifest["order"]:                      # MANIFEST CALLS ONLY
        call = json.loads((calls_dir / f"{cid}.json").read_text())
        entry = {"dims": [], "binary": None}
        try:
            for d in J.JUDGE_DIMS:
                e, hit = J.judge_dimension(client, call, d)
                cache_hits += hit
                entry["dims"].append(e)
            b, hit = judge_outcome(client, call)
            cache_hits += hit
            entry["binary"] = b
            results[cid] = entry
            print(f"  {cid}: 5 dims + outcome={b['label']} ✓", flush=True)
        except Exception as e:
            failures.append({"call_id": cid, "error": f"{type(e).__name__}: {e}"})
            print(f"  {cid}: FAILED — {type(e).__name__}: {e}", flush=True)
    payload = {"run": {"model": model, "temperature": temperature, "rubric_hash": rubric_hash,
                       "labels_csv_sha256": csv_sha, "manifest_sha256": man_sha,
                       "n_calls": len(results), "cache_hits": cache_hits,
                       "failures": len(failures), "failed_calls": failures,
                       "binary_rule": BINARY_RULE, "started": datetime.now().isoformat(timespec="seconds")},
               "calls": results}
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    return payload


# ---------------------------------------------------------------- offline selftest (mock client)
def selftest():
    import tempfile
    J._RETRY_BASE = 0
    ok = True

    def check(c, msg):
        nonlocal ok
        print(("  ok   " if c else "  FAIL ") + msg)
        ok = ok and c

    # outcome validation unit cases
    fx = J.FIXTURE
    good = validate_binary({"label": "fail", "reason": "agent over-demanded and never booked",
                            "evidence_turn_ids": ["t3", "t4", "t3"]}, fx)
    check(good["label"] == "fail" and good["evidence_turn_ids"] == ["t3", "t4"]
          and good["provenance"] == "uncalibrated", "outcome validated, deduped, uncalibrated")
    for why, p in {"bad label": {"label": "maybe", "reason": "x", "evidence_turn_ids": ["t1"]},
                   "no evidence": {"label": "fail", "reason": "x", "evidence_turn_ids": ["t99"]},
                   "empty reason": {"label": "fail", "reason": " ", "evidence_turn_ids": ["t1"]}}.items():
        try:
            validate_binary(p, fx)
            check(False, f"should reject {why}")
        except ValueError:
            check(True, f"rejects {why}")

    with tempfile.TemporaryDirectory(prefix="vf_jr_") as td:
        td = Path(td)
        # synthetic 2-call manifest + calls (NOT data/normalized)
        for i in (1, 2):
            c = {**fx, "call_id": f"jrfx{i}"}
            (td / f"jrfx{i}.json").write_text(json.dumps(c))
        manifest = {"order": ["jrfx1", "jrfx2"], "total": 2}
        dim_json = json.dumps({"score": 0.4, "reason": "demanded full address after partial answer",
                               "evidence_turn_ids": ["t2", "t3"]})
        out_json = json.dumps({"label": "fail", "reason": "no booking was completed",
                               "evidence_turn_ids": ["t3", "t4"]})
        # script: per call 5 dims then 1 outcome -> 12 responses
        client = J._MockClient([dim_json] * 5 + [out_json] + [dim_json] * 5 + [out_json])
        global OUT
        OUT = td / "judge_results.json"
        payload = run(client, manifest, "csvsha_fixture", "mansha_fixture", calls_dir=td)
        check(payload["run"]["n_calls"] == 2 and payload["run"]["failures"] == 0, "2 calls judged, 0 failures")
        check(payload["run"]["labels_csv_sha256"] == "csvsha_fixture"
              and payload["run"]["manifest_sha256"] == "mansha_fixture", "run manifest snapshots hashes")
        check(payload["calls"]["jrfx1"]["binary"]["label"] == "fail"
              and len(payload["calls"]["jrfx1"]["dims"]) == 5, "5 dims + binary per call")
        check("NOT derived from the 5 semantic dims" in payload["run"]["binary_rule"], "binary rule documented")
        # rerun -> pure cache
        client2 = J._MockClient(["should-not-be-called"])
        payload2 = run(client2, manifest, "csvsha_fixture", "mansha_fixture", calls_dir=td)
        check(client2.models.calls == 0 and payload2["run"]["cache_hits"] == 12, "rerun = 12/12 cache hits, 0 provider calls")
        # one bad call -> recorded failure, run continues
        (td / "jrfx3.json").write_text(json.dumps({**fx, "call_id": "jrfx3"}))
        bad_client = J._MockClient([json.dumps({"score": 7, "reason": "x", "evidence_turn_ids": ["t1"]})])
        payload3 = run(bad_client, {"order": ["jrfx3"], "total": 1}, "x", "y", calls_dir=td)
        check(payload3["run"]["failures"] == 1 and payload3["run"]["n_calls"] == 0
              and payload3["run"]["failed_calls"][0]["call_id"] == "jrfx3", "invalid response -> recorded failure, nothing cached as result")
        # cleanup mock cache entries
        for f in J.CACHE_DIR.glob("jrfx*"):
            f.unlink()
    print("\n" + ("JUDGE-RUN SELFTEST PASSED ✓ (offline; no real calls; gate untested by design — see --dry-run)"
                  if ok else "SELFTEST FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    if args.dry_run:
        manifest, csv_sha, man_sha = gate(skip=True)
        v = ROOT / "out" / "label_validation.json"
        binary = json.loads(v.read_text()).get("binary", "?") if v.exists() else "?"
        print(f"plan: judge {manifest['total']} manifest calls × (5 dims + 1 outcome) = {manifest['total']*6} judgments")
        print(f"gate: binary labels = {binary} (floor {FLOOR}) -> {'OPEN' if isinstance(binary,int) and binary>=FLOOR else 'CLOSED'}")
        print(f"hashes to snapshot: csv {str(csv_sha)[:16]}… manifest {man_sha[:16]}…")
        return
    manifest, csv_sha, man_sha = gate()
    print(f"GATE OPEN — judging {manifest['total']} manifest calls (5 dims + outcome each)…")
    payload = run(J.get_client(), manifest, csv_sha, man_sha)
    r = payload["run"]
    print(f"\nwrote out/judge_results.json — {r['n_calls']} calls, {r['cache_hits']} cache hits, "
          f"{r['failures']} failures. Provenance: uncalibrated until kappa.")


if __name__ == "__main__":
    main()
