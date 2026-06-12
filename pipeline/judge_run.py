#!/usr/bin/env python3
"""Batch E — the GATED real judge run. Produces out/judge_results.json (the contract demo_report.py
and the dashboard consume). Hardened against the FROZEN label snapshot (Phase E1).

    .venv/bin/python pipeline/judge_run.py --selftest          # offline mock-client tests (no network)
    .venv/bin/python pipeline/judge_run.py --dry-run           # show the gate + plan, call nothing
    .venv/bin/python pipeline/judge_run.py --canary            # REAL: first 2 manifest calls -> out/judge_canary.json
    .venv/bin/python pipeline/judge_run.py [--delay 1.0]       # REAL: all 46 manifest calls -> out/judge_results.json

GATE (every real run, in order — any miss refuses):
  1. judge._check_rubric_dims() — rubric drift closes the gate.
  2. pipeline/validate_labels.py exits 0 on the canonical CSV.
  3. eval/label_snapshot.json exists with annotation_status=complete.
  4. CSV raw-byte SHA == snapshot SHA (mutation after the freeze closes the gate).
  5. Manifest SHA == snapshot SHA.
  6. Exactly snapshot.rows unique annotations and snapshot.binary binary labels.
  7. Only calls in the FROZEN manifest are judged — nothing else, ever.

EPISTEMIC CONTRACT: Cohen's kappa calibrates ONLY the dedicated binary outcome judgment against the
human success/fail labels. The 5 semantic dimensions have NO per-dimension human gold labels — they
remain evidence-cited, UNCALIBRATED diagnostics regardless of kappa.

Run manifest records model, temperature, rubric_hash, frozen hashes, expected/completed request
counts, cache hits, failures, started_at/finished_at, elapsed, and status complete|partial.
Outputs are written ATOMICALLY (tmp + rename). Resumable: every validated judgment is cached
(validate-before-cache), so an interrupted run re-fires only the missing calls.
Deterministic dims in out/calls.json are NEVER touched.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))

import judge as J  # noqa: E402  (validated machinery: validate-before-cache, retry policy, dims)

CSV_PATH = ROOT / "eval" / "labels_spike.csv"
MAN_PATH = ROOT / "eval" / "label_manifest.json"
SNAP_PATH = ROOT / "eval" / "label_snapshot.json"
OUT_REAL = ROOT / "out" / "judge_results.json"
OUT_CANARY = ROOT / "out" / "judge_canary.json"

BINARY_RULE = ("dedicated outcome judgment per call (temperature 0, JSON, evidence-cited); "
               "label in {success,fail}; same question the blind annotator answered. "
               "NOT derived from the 5 semantic dims; kappa calibrates THIS judgment only — "
               "the semantic dims remain uncalibrated diagnostics.")

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
            "evidence_turn_ids": ev, "rule": BINARY_RULE, "provenance": "pending calibration (binary)"}


def judge_outcome(client, call):
    """Binary outcome judgment, validate-before-cache, same cache discipline as judge_dimension."""
    model, temperature = J.judge_config()
    prompt = OUTCOME_PROMPT.format(call_text=J.format_call(call))
    J.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    phash = hashlib.sha256(f"{model}|{temperature}|{prompt}".encode()).hexdigest()[:16]
    cpath = J.CACHE_DIR / f"{call['call_id']}__outcome_binary__{phash}.json"
    if cpath.exists():
        # re-validate every cache hit against the CURRENT call; corrupted -> delete + refetch
        try:
            return validate_binary(json.loads(cpath.read_text()), call), True
        except (ValueError, json.JSONDecodeError):
            cpath.unlink()
    parsed = J._generate_json(client, model, temperature, prompt)
    entry = validate_binary(parsed, call)            # raises on invalid -> nothing cached
    cpath.write_text(json.dumps(entry, indent=2))
    return entry, False


def gate(csv_path=CSV_PATH, man_path=MAN_PATH, snap_path=SNAP_PATH, run_validator=True):
    """The frozen-snapshot gate. Returns (manifest, csv_sha, man_sha, snapshot) or sys.exits."""
    import csv as csvmod
    J._check_rubric_dims()                                              # rubric drift -> SystemExit
    if run_validator:
        r = subprocess.run([sys.executable, str(ROOT / "pipeline" / "validate_labels.py"), "--quiet"])
        if r.returncode != 0:
            sys.exit("GATE CLOSED: validate_labels.py failed — labels do not validate.")
    if not snap_path.exists():
        sys.exit("GATE CLOSED: eval/label_snapshot.json missing — freeze the labels first (Phase E0).")
    snap = json.loads(snap_path.read_text())
    if snap.get("annotation_status") != "complete":
        sys.exit("GATE CLOSED: snapshot annotation_status != complete.")
    csv_sha = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    if csv_sha != snap["labels_csv_sha256"]:
        sys.exit(f"GATE CLOSED: labels CSV mutated after the freeze "
                 f"({csv_sha[:12]}… != frozen {snap['labels_csv_sha256'][:12]}…).")
    man_sha = hashlib.sha256(man_path.read_bytes()).hexdigest()
    if man_sha != snap["manifest_sha256"]:
        sys.exit(f"GATE CLOSED: manifest mutated after the freeze ({man_sha[:12]}…).")
    rows = list(csvmod.DictReader(csv_path.read_bytes().decode().splitlines()))
    ids = [r["call_id"] for r in rows]
    binary = [r for r in rows if r["primary_label"] in ("success", "fail")]
    if len(ids) != len(set(ids)) or len(ids) != snap["rows"]:
        sys.exit(f"GATE CLOSED: expected {snap['rows']} unique annotations, found {len(set(ids))}.")
    if len(binary) != snap["binary"]:
        sys.exit(f"GATE CLOSED: expected {snap['binary']} binary labels, found {len(binary)}.")
    return json.loads(man_path.read_text()), csv_sha, man_sha, snap


def atomic_write(path, payload):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n")
    os.replace(tmp, path)


def _now():
    """Timezone-aware local timestamp (ISO, with UTC offset)."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def run(client, order, csv_sha, man_sha, out_path, calls_dir=None, delay=0.0, mode="full"):
    """Judge `order` (manifest calls only). ATOMICALLY CHECKPOINTS after EVERY call (success or
    failure) with status='running', so an interrupted run leaves an honest partial artifact on
    disk; final write marks complete|partial. `validated_judgments` counts judgments that passed
    validation (cache hits included) — NOT raw provider requests (retries are not counted)."""
    model, temperature = J.judge_config()
    rubric_hash = hashlib.sha256((ROOT / "rubric.yaml").read_bytes()).hexdigest()[:16]
    calls_dir = calls_dir or (ROOT / "data" / "normalized")
    started_at = _now()
    t0 = time.monotonic()
    expected = len(order) * 6
    results, cache_hits, validated, failures = {}, 0, 0, []

    def payload(status):
        return {"run": {"mode": mode, "status": status, "model": model, "temperature": temperature,
                        "rubric_hash": rubric_hash, "labels_csv_sha256": csv_sha, "manifest_sha256": man_sha,
                        "n_calls": len(results), "expected_judgments": expected,
                        "validated_judgments": validated, "cache_hits": cache_hits,
                        "failures": len(failures), "failed_calls": failures,
                        "binary_rule": BINARY_RULE, "started_at": started_at,
                        "checkpointed_at": _now(),
                        "finished_at": _now() if status in ("complete", "partial") else None,
                        "elapsed_s": round(time.monotonic() - t0, 1)},
                "calls": results}

    for cid in order:                                  # MANIFEST CALLS ONLY (order is pre-vetted)
        call = json.loads((calls_dir / f"{cid}.json").read_text())
        entry = {"dims": [], "binary": None}
        try:
            for d in J.JUDGE_DIMS:
                e, hit = J.judge_dimension(client, call, d)
                cache_hits += hit
                validated += 1
                entry["dims"].append(e)
                if not hit and delay:
                    time.sleep(delay)
            b, hit = judge_outcome(client, call)
            cache_hits += hit
            validated += 1
            entry["binary"] = b
            results[cid] = entry
            print(f"  {cid}: 5 dims + outcome={b['label']} ✓", flush=True)
            if not hit and delay:
                time.sleep(delay)
        except Exception as e:
            failures.append({"call_id": cid, "error": f"{type(e).__name__}: {e}"})
            print(f"  {cid}: FAILED — {type(e).__name__}: {e}", flush=True)
        atomic_write(out_path, payload("running"))     # checkpoint after EVERY call
    final = payload("complete" if (len(results) == len(order) and not failures) else "partial")
    atomic_write(out_path, final)
    return final


# ---------------------------------------------------------------- offline selftest (mock client)
def selftest():
    import shutil
    import tempfile
    J._RETRY_BASE = 0
    ok = True

    def check(c, msg):
        nonlocal ok
        print(("  ok   " if c else "  FAIL ") + msg)
        ok = ok and c

    fx = J.FIXTURE
    good = validate_binary({"label": "fail", "reason": "agent over-demanded and never booked",
                            "evidence_turn_ids": ["t3", "t4", "t3"]}, fx)
    check(good["label"] == "fail" and good["evidence_turn_ids"] == ["t3", "t4"]
          and "pending calibration" in good["provenance"], "outcome validated, deduped, pending-calibration provenance")
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
        # --- gate tests against COPIES (canonical files never touched) ---
        csv_c, man_c, snap_c = td / "l.csv", td / "m.json", td / "s.json"
        shutil.copy(CSV_PATH, csv_c); shutil.copy(MAN_PATH, man_c); shutil.copy(SNAP_PATH, snap_c)
        manifest, csv_sha, man_sha, snap = gate(csv_c, man_c, snap_c, run_validator=False)
        check(manifest["total"] == 46 and csv_sha == snap["labels_csv_sha256"], "gate OPEN on frozen copies")
        check(manifest["total"] * 6 == 276, "dry-run math: 46 × 6 = 276 judgments")
        # mutated CSV -> closed
        csv_c.write_bytes(CSV_PATH.read_bytes().replace(b"success", b"fail", 1))
        try:
            gate(csv_c, man_c, snap_c, run_validator=False)
            check(False, "mutated CSV should close the gate")
        except SystemExit as e:
            check("mutated after the freeze" in str(e), "mutated CSV closes the gate")
        shutil.copy(CSV_PATH, csv_c)
        # mutated manifest -> closed
        man_c.write_text(man_c.read_text().replace("46", "47", 1))
        try:
            gate(csv_c, man_c, snap_c, run_validator=False)
            check(False, "mutated manifest should close the gate")
        except SystemExit as e:
            check("manifest mutated" in str(e), "mutated manifest closes the gate")
        shutil.copy(MAN_PATH, man_c)
        # incomplete snapshot -> closed
        s = json.loads(snap_c.read_text()); s["annotation_status"] = "in_progress"
        snap_c.write_text(json.dumps(s))
        try:
            gate(csv_c, man_c, snap_c, run_validator=False)
            check(False, "incomplete snapshot should close the gate")
        except SystemExit as e:
            check("annotation_status" in str(e), "incomplete snapshot closes the gate")
        shutil.copy(SNAP_PATH, snap_c)
        # rubric drift -> closed (patch JUDGE_DIMS)
        saved = dict(J.JUDGE_DIMS)
        try:
            J.JUDGE_DIMS.pop("conciseness")
            try:
                gate(csv_c, man_c, snap_c, run_validator=False)
                check(False, "rubric drift should close the gate")
            except SystemExit as e:
                check("rubric" in str(e).lower(), "rubric drift closes the gate")
        finally:
            J.JUDGE_DIMS.clear(); J.JUDGE_DIMS.update(saved)

        # --- run() behaviour on mock client, synthetic calls ---
        for i in (1, 2):
            (td / f"jrfx{i}.json").write_text(json.dumps({**fx, "call_id": f"jrfx{i}"}))
        dim_json = json.dumps({"score": 0.4, "reason": "demanded full address after partial answer",
                               "evidence_turn_ids": ["t2", "t3"]})
        out_json = json.dumps({"label": "fail", "reason": "no booking was completed",
                               "evidence_turn_ids": ["t3", "t4"]})
        client = J._MockClient([dim_json] * 5 + [out_json] + [dim_json] * 5 + [out_json])
        p = run(client, ["jrfx1", "jrfx2"], "csvX", "manX", td / "res.json", calls_dir=td, mode="selftest")
        check(p["run"]["status"] == "complete" and p["run"]["n_calls"] == 2, "clean run -> status complete")
        check(p["run"]["expected_judgments"] == 12 and p["run"]["validated_judgments"] == 12,
              "judgment accounting 12/12 (validated, not provider requests)")
        check(p["run"]["started_at"] <= p["run"]["finished_at"] and "elapsed_s" in p["run"]
              and ("+" in p["run"]["started_at"] or "Z" in p["run"]["started_at"]),
              "timezone-aware timestamps + elapsed recorded")
        check((td / "res.json").exists() and not (td / "res.tmp").exists(), "atomic write (no tmp left)")
        # rerun -> pure cache resume
        client2 = J._MockClient(["never"])
        p2 = run(client2, ["jrfx1", "jrfx2"], "csvX", "manX", td / "res2.json", calls_dir=td, mode="selftest")
        check(client2.models.calls == 0 and p2["run"]["cache_hits"] == 12, "resume from cache: 12/12 hits, 0 provider calls")
        # CORRUPTED CACHE: tamper a semantic entry + a binary entry -> rejected, deleted, refetched
        sem = next(J.CACHE_DIR.glob("jrfx1__language_match__*"))
        good_sem = sem.read_text()
        sem.write_text(json.dumps({"score": 9.9, "reason": "tampered", "evidence_turn_ids": ["t1"]}))
        binc = next(J.CACHE_DIR.glob("jrfx1__outcome_binary__*"))
        binc.write_text("{ not json")
        client3 = J._MockClient([good_sem, json.dumps({"label": "fail", "reason": "no booking completed",
                                                       "evidence_turn_ids": ["t3"]})])
        p2b = run(client3, ["jrfx1"], "c", "m", td / "res2b.json", calls_dir=td, mode="selftest")
        check(client3.models.calls == 2 and p2b["run"]["status"] == "complete"
              and p2b["run"]["cache_hits"] == 4, "corrupted cache entries rejected+deleted+refetched (4 clean hits, 2 live)")
        check(json.loads(next(J.CACHE_DIR.glob("jrfx1__language_match__*")).read_text())["score"] <= 1,
              "tampered entry replaced by a valid one on disk")
        # canary separation: canary output must not touch the real path
        p3 = run(J._MockClient([dim_json] * 5 + [out_json]), ["jrfx1"], "c", "m", td / "canary.json",
                 calls_dir=td, mode="canary")
        check(p3["run"]["mode"] == "canary" and not (td / "judge_results.json").exists(),
              "canary writes its own file, real output untouched")
        # partial honesty: one bad call
        (td / "jrfx3.json").write_text(json.dumps({**fx, "call_id": "jrfx3"}))
        bad = J._MockClient([json.dumps({"score": 7, "reason": "x", "evidence_turn_ids": ["t1"]})])
        p4 = run(bad, ["jrfx3"], "c", "m", td / "res3.json", calls_dir=td, mode="selftest")
        check(p4["run"]["status"] == "partial" and p4["run"]["failures"] == 1
              and p4["run"]["failed_calls"][0]["call_id"] == "jrfx3", "failed call -> status partial, recorded honestly")
        check(not list(J.CACHE_DIR.glob("jrfx3__*")), "invalid response never cached")
        # INTERRUPTED RUN: provider dies mid-call-2 -> checkpoint on disk holds call 1 with status 'running'.
        # _Killer is a BaseException so run()'s per-call `except Exception` does NOT absorb it —
        # it behaves like a real KeyboardInterrupt/kill, escaping the loop mid-call.
        class _Killer(BaseException):
            pass

        class _DieAfter:
            def __init__(self, script, die_at):
                self.models = J._MockClient(script).models
                self.models_die_at = die_at
                orig = self.models.generate_content

                def wrapper(**kw):
                    if self.models.calls + 1 >= die_at:
                        raise _Killer("simulated interruption")
                    return orig(**kw)
                self.models.generate_content = wrapper
        for f in J.CACHE_DIR.glob("jrfx*"):
            f.unlink()
        # call 1 = 5 dims + outcome (requests 1-6, completes); dies on request 8 (mid call 2)
        dying = _DieAfter([dim_json] * 5 + [out_json] + [dim_json] * 6, die_at=8)
        try:
            run(dying, ["jrfx1", "jrfx2"], "c", "m", td / "intr.json", calls_dir=td, mode="selftest")
        except _Killer:
            pass
        # the per-call checkpoint after call 1 (and after the failed call 2 it never reached) is on disk
        ck = json.loads((td / "intr.json").read_text())
        check(ck["run"]["status"] == "running" and ck["run"]["n_calls"] == 1
              and "jrfx1" in ck["calls"] and ck["run"]["finished_at"] is None,
              "interrupted run -> on-disk checkpoint: status running, call 1 preserved, no finished_at")
        for f in J.CACHE_DIR.glob("jrfx*"):
            f.unlink()
    # NO-MODE REFUSAL: bare invocation must print help and exit non-zero (never start paid work)
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "pipeline" / "judge_run.py")], capture_output=True, text=True)
    check(r.returncode == 2 and "--full" in r.stdout, "bare invocation -> help + exit 2 (no paid default)")
    r2 = subprocess.run([sys.executable, str(ROOT / "pipeline" / "judge_run.py"), "--canary", "--full"],
                        capture_output=True, text=True)
    check(r2.returncode != 0, "mutually exclusive modes rejected (--canary --full)")
    r3 = subprocess.run([sys.executable, str(ROOT / "pipeline" / "judge_run.py"), "--dry-run", "--delay", "-1"],
                        capture_output=True, text=True)
    check(r3.returncode != 0 and "delay" in r3.stderr, "negative --delay rejected")
    print("\n" + ("JUDGE-RUN E1 SELFTEST PASSED ✓ (offline; canonical files untouched; no network)"
                  if ok else "SELFTEST FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(
        description="Gated real judge run. Network modes (--canary/--full) cost Gemini quota and "
                    "require the frozen-snapshot gate to be open. Paid work is NEVER the default.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--selftest", action="store_true", help="offline mock-client tests (no network)")
    mode.add_argument("--dry-run", action="store_true", help="show the gate + plan, call nothing")
    mode.add_argument("--canary", action="store_true", help="REAL: first 2 manifest calls -> out/judge_canary.json")
    mode.add_argument("--full", action="store_true", help="REAL: all manifest calls -> out/judge_results.json")
    ap.add_argument("--delay", type=float, default=1.0, help="seconds between non-cached API requests (>=0)")
    if len(sys.argv) == 1:                              # bare invocation must never start paid work
        ap.print_help()
        sys.exit(2)
    args = ap.parse_args()
    if args.delay < 0:
        ap.error("--delay must be >= 0")
    if args.selftest:
        sys.exit(selftest())
    if args.dry_run:
        manifest, csv_sha, man_sha, snap = gate()
        print(f"GATE OPEN — plan: {manifest['total']} manifest calls × (5 dims + 1 outcome) "
              f"= {manifest['total'] * 6} judgments (cache-resumable, delay {args.delay}s)")
        print(f"frozen: csv {csv_sha[:16]}… manifest {man_sha[:16]}… "
              f"({snap['binary']} binary: {snap['success']}s/{snap['fail']}f, {snap['unsure']} unsure)")
        return
    manifest, csv_sha, man_sha, snap = gate()
    try:
        if args.canary:
            order = manifest["order"][:2]
            print(f"GATE OPEN — CANARY: {order} -> out/judge_canary.json")
            payload = run(J.get_client(), order, csv_sha, man_sha, OUT_CANARY, delay=args.delay, mode="canary")
        else:
            print(f"GATE OPEN — judging all {manifest['total']} manifest calls (delay {args.delay}s)…")
            payload = run(J.get_client(), manifest["order"], csv_sha, man_sha, OUT_REAL, delay=args.delay, mode="full")
    except KeyboardInterrupt:
        print("\nINTERRUPTED — last checkpoint is on disk with status 'running'; validated judgments "
              "are cached, so re-running resumes from cache.", file=sys.stderr)
        sys.exit(130)
    r = payload["run"]
    print(f"\nstatus {r['status'].upper()} — {r['n_calls']} calls, "
          f"{r['validated_judgments']}/{r['expected_judgments']} validated judgments "
          f"({r['cache_hits']} cached), {r['failures']} failures, {r['elapsed_s']}s")
    print("kappa calibrates the BINARY outcome judge only; the 5 semantic dims remain uncalibrated diagnostics.")


if __name__ == "__main__":
    main()
