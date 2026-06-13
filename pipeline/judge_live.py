#!/usr/bin/env python3
"""Live-call judge path — ISOLATED from the gated calibration run. The LIVE-BRIDGE (Jun 13).

judge_run.py judges ONLY the frozen 46-call manifest (gate on manifest["total"]==46) and writes
out/judge_results.json — the audited, kappa-calibrated artifact. This module does NEITHER. It:
  - judges ONLY the live_today slice (data/normalized/bolna_live_*.json), nothing from the manifest;
  - has NO frozen-snapshot gate (live calls have no human gold labels — they are uncalibrated);
  - reuses pipeline/judge.py machinery verbatim (5 semantic dims, validate-before-cache, retry) and
    judge_run.judge_outcome for the binary outcome (SAME cache discipline);
  - writes out/live_judge_results.json  — NEVER out/judge_results.json;
  - writes out/live_calls.json  — the merged view the /platform LIVE-TODAY section reads.

EPISTEMIC CONTRACT (unchanged): the 5 semantic dims are uncalibrated diagnostics; the binary
outcome judgment is the same question the annotator answered, BUT live calls carry no human label,
so NO kappa is computed for them. Every live record is tagged calibrated:false · LIVE · UNCALIBRATED.

    .venv/bin/python pipeline/judge_live.py            # judge all live_today calls (cache-resumable)
    .venv/bin/python pipeline/judge_live.py --selftest  # OFFLINE mock-client end-to-end (no network)

# ---- out/live_calls.json SHAPE (the LIVE-TODAY contract) ---------------------------------------
# {
#   "slice": "live_today",
#   "calibrated": false,
#   "label": "LIVE · UNCALIBRATED",
#   "generated_at": "<tz-aware ISO>",
#   "judge": {"model": ..., "temperature": ..., "rubric_hash": ..., "judge_prompt_hash": ...,
#             "status": "complete"|"partial", "n_calls": N, "failures": [...],
#             "note": "uncalibrated — live calls have no human gold labels; no kappa"},
#   "calls": [
#     { <every deterministic call_record field: call_id, source, language, stress_profile,
#        workflow_type, turns, outcome, scorecard (deterministic dims), cost, failures, signals>,
#       "provenance": {"slice":"live_today","calibrated":false,"label":"LIVE · UNCALIBRATED"},
#       "judge": {                       # the LLM layer, kept SEPARATE from the deterministic scorecard
#          "dims": [ {name,type:"judge",score,reason,evidence_turn_ids,provenance:"uncalibrated"} x5 ],
#          "binary": {label:"success"|"fail", reason, evidence_turn_ids, rule, provenance} | null,
#          "error": "<type: msg>"        # present ONLY if this call failed to judge
#       }
#     }, ...
#   ]
# }
# Deterministic dims live under calls[].scorecard (production shape); LLM dims live under calls[].judge.
# The two are never merged into one list, so the deterministic scorecard is never polluted by LLM output.
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import judge as J            # noqa: E402  (5 semantic dims, validate-before-cache, retry policy)
import judge_run as JR       # noqa: E402  (judge_outcome — binary outcome, same cache discipline)
from ingest_live import LIVE_PROVENANCE  # noqa: E402  (the single source of the provenance tag)

NORM = ROOT / "data" / "normalized"
OUT_LIVE_JUDGE = ROOT / "out" / "live_judge_results.json"
OUT_LIVE_CALLS = ROOT / "out" / "live_calls.json"
LIVE_GLOB = "bolna_live_*.json"

UNCALIBRATED_NOTE = ("uncalibrated — live calls have no human gold labels; no kappa is computed for "
                     "this slice. Semantic dims are evidence-cited diagnostics only.")


def _now():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _atomic_write(path, payload):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n")
    os.replace(tmp, path)


def live_call_ids(norm_dir=NORM):
    """The live_today slice ONLY — data/normalized/bolna_live_*.json. NEVER the manifest's 46 calls
    (those are bolna_* / cmd_* / hero_* / swz_* — no bolna_live_ prefix), so this can never reach
    into the calibration set."""
    return sorted(p.stem for p in norm_dir.glob(LIVE_GLOB))


def judge_live_call(client, call):
    """5 semantic dims (judge.judge_dimension) + binary outcome (judge_run.judge_outcome) for ONE
    live call. Reuses the EXACT validated machinery + cache as the gated path — same cache dir, same
    validate-before-cache. Returns {"dims":[...], "binary":{...}} or raises (caller records it)."""
    J._check_rubric_dims()                                   # rubric drift -> SystemExit (shared guard)
    dims = [J.judge_dimension(client, call, d)[0] for d in J.JUDGE_DIMS]
    binary, _ = JR.judge_outcome(client, call)
    return {"dims": dims, "binary": binary}


def run(client, call_ids, norm_dir=NORM, out_judge=OUT_LIVE_JUDGE, out_calls=OUT_LIVE_CALLS):
    """Judge the live slice -> live_judge_results.json + the merged live_calls.json. Per-call honesty:
    a call that fails to judge is recorded with its error and status goes 'partial'; the deterministic
    record is still emitted (the LIVE-TODAY surface degrades gracefully, never blanks)."""
    from score import build_record
    from schemas import validate

    model, temperature = J.judge_config()
    rubric_hash = hashlib.sha256((ROOT / "rubric.yaml").read_bytes()).hexdigest()[:16]
    _ref = "||".join(J.build_prompt(d, J.FIXTURE) for d in J.JUDGE_DIMS) + JR.OUTCOME_PROMPT
    prompt_hash = hashlib.sha256(_ref.encode()).hexdigest()[:16]

    judge_results, merged, failures = {}, [], []
    for cid in call_ids:                                     # LIVE SLICE ONLY (live_call_ids is pre-filtered)
        call = json.loads((norm_dir / f"{cid}.json").read_text())
        record = build_record(call)                          # production deterministic record
        validate(record, "call_record")
        record["provenance"] = dict(LIVE_PROVENANCE)
        try:
            jl = judge_live_call(client, call)
            judge_results[cid] = jl
            record["judge"] = jl
            print(f"  {cid}: 5 dims + outcome={jl['binary']['label']} ✓  [LIVE · UNCALIBRATED]", flush=True)
        except Exception as e:                               # noqa: BLE001 (honest per-call failure)
            err = f"{type(e).__name__}: {e}"
            failures.append({"call_id": cid, "error": err})
            judge_results[cid] = {"dims": [], "binary": None, "error": err}
            record["judge"] = {"dims": [], "binary": None, "error": err}
            print(f"  {cid}: FAILED — {err}", flush=True)
        merged.append(record)

    status = "complete" if (call_ids and not failures) else ("partial" if call_ids else "empty")
    judge_payload = {
        "run": {"mode": "live", "status": status, "model": model, "temperature": temperature,
                "rubric_hash": rubric_hash, "judge_prompt_hash": prompt_hash,
                "n_calls": len(call_ids), "failures": len(failures), "failed_calls": failures,
                "calibrated": False, "binary_rule": JR.BINARY_RULE, "note": UNCALIBRATED_NOTE,
                "generated_at": _now()},
        "calls": judge_results,
    }
    _atomic_write(out_judge, judge_payload)

    merged_payload = {
        **LIVE_PROVENANCE,
        "generated_at": _now(),
        "judge": {"model": model, "temperature": temperature, "rubric_hash": rubric_hash,
                  "judge_prompt_hash": prompt_hash, "status": status, "n_calls": len(call_ids),
                  "failures": failures, "note": UNCALIBRATED_NOTE},
        "calls": merged,
    }
    _atomic_write(out_calls, merged_payload)
    return judge_payload, merged_payload


# ---------------------------------------------------------------- offline selftest (mock client)
def selftest():
    """End-to-end OFFLINE: ingest the cached 246cd9f3 payload through ingest_live into a TEMP
    normalized dir, judge it with a MOCK client through this live path into TEMP out files, and
    prove (a) it works, (b) the live judge cache stays hermetic, (c) NO frozen file is touched,
    (d) the merged shape is exactly the documented contract. No network."""
    import shutil
    import tempfile
    import ingest_bolna as IB
    import ingest_live as IL

    J._RETRY_BASE = 0
    ok = True
    _real_cache = J.CACHE_DIR

    def check(c, msg):
        nonlocal ok
        print(("  ok   " if c else "  FAIL ") + msg)
        ok = ok and c

    # live slice filter never reaches into the manifest's 46 calls
    real_ids = live_call_ids(NORM)
    check(all(cid.startswith("bolna_live_") for cid in real_ids),
          f"live slice filter yields only bolna_live_* ids (found {len(real_ids)} on disk)")

    frozen = ["eval/label_manifest.json", "eval/labels_spike.csv", "eval/label_snapshot.json",
              "out/judge_results.json", "out/calls.json", "out/analytics.json",
              "out/demo_report_data.json", "rubric.yaml"]
    before = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in frozen if (ROOT / f).exists()}

    raw = json.loads((ROOT / "data" / "provider_logs" / "bolna_246cd9f3.json").read_text())

    with tempfile.TemporaryDirectory(prefix="vf_jl_") as td:
        td = Path(td)
        J.CACHE_DIR = td / ".judge_cache"; J.CACHE_DIR.mkdir(parents=True, exist_ok=True)  # hermetic cache
        tnorm = td / "normalized"
        # 1) replay the cached payload through the live ingest -> a real bolna_live_* normalized call
        IL.ingest_one(raw, IB.EXEC_ID, norm_dir=tnorm, raw_dir=td / "raw")
        ids = live_call_ids(tnorm)
        check(ids == ["bolna_live_246cd9f3"], "ingest produced one live call (bolna_live_246cd9f3)")

        # 2) judge it via a MOCK client (5 dim responses + 1 outcome response), into TEMP out files
        dim_json = json.dumps({"score": 0.9, "reason": "agent adapted to the code-switched input",
                               "evidence_turn_ids": ["t6", "t7"]})
        out_json = json.dumps({"label": "success", "reason": "appointment confirmed with date and place",
                               "evidence_turn_ids": ["t9", "t11"]})
        client = J._MockClient([dim_json] * 5 + [out_json])
        jp, mp = run(client, ids, norm_dir=tnorm, out_judge=td / "lj.json", out_calls=td / "lc.json")

        check(jp["run"]["status"] == "complete" and jp["run"]["n_calls"] == 1
              and jp["run"]["calibrated"] is False, "live judge run -> complete, calibrated:false")
        check((td / "lj.json").exists() and not (td / "lj.tmp").exists(), "atomic write (no .tmp left)")
        check(not (td / "judge_results.json").exists(), "did NOT write judge_results.json")

        # 3) merged live_calls.json shape == the documented LIVE-TODAY contract
        check(mp["slice"] == "live_today" and mp["calibrated"] is False
              and mp["label"] == "LIVE · UNCALIBRATED", "merged view tagged live_today / UNCALIBRATED")
        c0 = mp["calls"][0]
        check(all(k in c0 for k in ("call_id", "outcome", "scorecard", "cost", "failures",
                                    "signals", "provenance", "judge")),
              "merged call carries deterministic record + provenance + judge")
        check(c0["provenance"] == LIVE_PROVENANCE, "per-call provenance == {live_today, false, UNCALIBRATED}")
        det_names = {d["name"] for d in c0["scorecard"]["dimensions"]}
        check("latency_gap" in det_names and "task_completion" in det_names
              and all(d["type"] == "deterministic" for d in c0["scorecard"]["dimensions"]),
              "deterministic scorecard untouched (no judge dims leaked into it)")
        jdims = c0["judge"]["dims"]
        check(len(jdims) == 5 and all(d["type"] == "judge" and d["provenance"] == "uncalibrated" for d in jdims)
              and c0["judge"]["binary"]["label"] == "success"
              and "pending calibration" in c0["judge"]["binary"]["provenance"],
              "judge layer: 5 uncalibrated dims + binary outcome, kept separate")

        # 4) cache resume: a second run makes ZERO provider calls
        client2 = J._MockClient(["never"])
        run(client2, ids, norm_dir=tnorm, out_judge=td / "lj2.json", out_calls=td / "lc2.json")
        check(client2.models.calls == 0, "second run is pure cache resume (0 provider calls)")

        # 5) per-call failure honesty: a bad dim response -> status partial, error recorded, record still
        # emitted. Cache keys use the SHARED call_id (bolna_<id[:8]>, set by the production normalizer),
        # so clear by that prefix before forcing a live fetch of the (bad) first dim.
        cache_call_id = mp["calls"][0]["call_id"]            # bolna_246cd9f3 (shared normalizer id)
        bad = J._MockClient([json.dumps({"score": 7, "reason": "x", "evidence_turn_ids": ["t1"]})])
        for f in J.CACHE_DIR.glob(f"{cache_call_id}__*"):
            f.unlink()
        jp3, mp3 = run(bad, ids, norm_dir=tnorm, out_judge=td / "lj3.json", out_calls=td / "lc3.json")
        check(jp3["run"]["status"] == "partial" and jp3["run"]["failures"] == 1
              and "error" in mp3["calls"][0]["judge"] and mp3["calls"][0]["scorecard"]["overall"] is not None,
              "judge failure -> partial + error recorded, deterministic record still emitted")
        check(all("score" in json.loads(p.read_text()) for p in J.CACHE_DIR.glob(f"{cache_call_id}__*")),
              "invalid judge response never poisoned the cache")

    J.CACHE_DIR = _real_cache
    after = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in before}
    check(before == after, f"all {len(before)} frozen files byte-identical after selftest")

    print("\n" + ("JUDGE-LIVE SELFTEST PASSED ✓ (offline; isolated from calibration; frozen files untouched)"
                  if ok else "JUDGE-LIVE SELFTEST FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(
        description="Judge the live_today slice ONLY (uncalibrated). Reuses judge.py machinery; "
                    "writes out/live_judge_results.json + out/live_calls.json. NEVER touches the "
                    "frozen out/judge_results.json or the 46-call manifest.")
    ap.add_argument("--selftest", action="store_true", help="OFFLINE end-to-end mock-client test (no network)")
    args = ap.parse_args()

    if args.selftest:
        sys.exit(selftest())

    ids = live_call_ids()
    if not ids:
        sys.exit("No live calls found (data/normalized/bolna_live_*.json). "
                 "Run: python pipeline/ingest_live.py --execution <id> first.")
    print(f"judging {len(ids)} live call(s) [LIVE · UNCALIBRATED]: {ids}")
    jp, _ = run(J.get_client(), ids)
    r = jp["run"]
    print(f"\nstatus {r['status'].upper()} — {r['n_calls']} live call(s), {r['failures']} failures")
    print("wrote out/live_judge_results.json + out/live_calls.json (NOT out/judge_results.json)")
    print("NOTE: live slice is UNCALIBRATED — no human gold labels, no kappa. Semantic dims are diagnostics.")


if __name__ == "__main__":
    main()
