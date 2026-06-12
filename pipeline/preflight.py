#!/usr/bin/env python3
"""Submission preflight — the executable checklist for docs/SUBMISSION-PLAN.md.

    .venv/bin/python pipeline/preflight.py [--offline]

Checks every Definition-of-Done item (SPEC §2.5) and every hackathon rule (Sonam's email)
deterministically. FAIL = required for submission and missing. WARN = should fix. SKIP =
network check skipped. Run it any time; run it for real before submitting Jun 12 night.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OFFLINE = "--offline" in sys.argv
AGENT_ID = "199b03e7-06c6-40e5-8741-37c5c9598061"
RESULTS = []


def check(name, status, detail=""):
    RESULTS.append((name, status, detail))


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def jload(p):
    return json.loads(Path(p).read_text())


# ---------- DoD 1: hero call audio + failure table with hard ms ----------
def hero():
    wav = ROOT / "data/hero/hero_001.wav"
    tj = ROOT / "data/hero/turns.json"
    if not (wav.exists() and tj.exists()):
        return check("hero: wav + turns.json", "FAIL", "missing artifact")
    sys.path.insert(0, str(ROOT / "pipeline"))
    from signals import analyze, load_rubric
    r = analyze(jload(tj)["turns"], load_rubric(ROOT / "rubric.yaml"))
    kinds = {f["dimension"] for f in r["failures"]}
    ok = "barge_in" in kinds and "latency_gap" in kinds
    check("hero: wav + turns.json", "PASS", f"{wav.stat().st_size//1024}KB wav")
    check("hero: both engineered failures detected", "PASS" if ok else "FAIL",
          ", ".join(f"{f['label']} {f['detail']}" for f in r["failures"]))
    tl = jload(ROOT / "data/hero/timeline.json")
    check("hero: Cartesia voice (rule: mandatory)", "PASS" if tl.get("cartesia") else "FAIL",
          (tl.get("cartesia") or {}).get("voice", "no cartesia block in timeline"))


# ---------- DoD 2: >=9 calls scored end-to-end with reasons ----------
def scored():
    calls_json = ROOT / "out/calls.json"
    if not calls_json.exists():
        return check("scored: out/calls.json >=9 calls w/ reasons", "FAIL", "not built (Block 3b)")
    try:
        data = jload(calls_json)
        items = data if isinstance(data, list) else data.get("calls", [])
        n = len(items)
        missing_reason = 0
        for c in items:
            # dimensions live under the nested scorecard per the call_record contract
            for d in (c.get("scorecard") or {}).get("dimensions", []):
                if not d.get("reason") or "evidence_turn_ids" not in d:
                    missing_reason += 1
        ok = n >= 9 and missing_reason == 0
        check("scored: out/calls.json >=9 calls w/ reasons", "PASS" if ok else "FAIL",
              f"{n} calls, {missing_reason} dims missing reason/evidence")
    except Exception as e:
        check("scored: out/calls.json >=9 calls w/ reasons", "FAIL", f"unreadable: {e}")


# ---------- DoD 3: real judge run + evidence-backed improvement queue ----------
# (DPO PAIR export is roadmap, not this sprint — the shipped deliverable is the evidence-backed
#  improvement queue in out/demo_report_data.json, and the real judged run in out/judge_results.json.)
def judge_run_check():
    j = jload(ROOT / "out/judge_results.json")
    if not j:
        return check("judge: real run complete (0 failures)", "FAIL", "out/judge_results.json missing")
    r = j.get("run", {})
    ok = r.get("status") == "complete" and r.get("failures") == 0 and r.get("n_calls", 0) >= 40
    check("judge: real run complete (0 failures)", "PASS" if ok else "FAIL",
          f"status={r.get('status')} · {r.get('n_calls')}/46 calls · {r.get('failures')} failures · {r.get('model')}")


def improvement_queue():
    R = jload(ROOT / "out/demo_report_data.json") or {}
    q = R.get("improvement_queue") or []
    check("improvement queue: >=1 evidence-backed entry", "PASS" if q else "FAIL",
          f"{len(q)} entries (DPO pair export is roadmap, not this sprint)")


# ---------- DoD 4: >=40 blind labels + kappa + 2 disagreements ----------
def calibration():
    lab = ROOT / "eval/labels_spike.csv"
    if lab.exists():
        import csv as _csv
        usable = set()   # distinct call_ids with a binary primary (unsure excluded; csv-parsed, not line-counted)
        with lab.open(newline="") as f:
            for row in _csv.DictReader(f):
                if row.get("primary_label") in ("success", "fail"):
                    usable.add(row["call_id"])
        n = len(usable)
        check("labels: >=40 usable binary (excl unsure)", "PASS" if n >= 40 else "FAIL",
              f"{n} usable success/fail")
    else:
        check("labels: >=40 usable binary (excl unsure)", "FAIL", "not collected (Block 4 — HIS task, blind!)")
    # calibration now lives in out/demo_report_data.json (NOT a separate kappa*.json)
    cal = (jload(ROOT / "out/demo_report_data.json") or {}).get("calibration")
    if cal and cal.get("kappa") is not None and cal.get("ci95") and cal.get("disagreements") is not None:
        check("kappa: number + CI + disagreements", "PASS",
              f"κ={cal['kappa']} CI{cal['ci95']} n={cal['n']} · {len(cal['disagreements'])} disagreements")
    else:
        check("kappa: number + CI + disagreements", "FAIL", "calibration absent from out/demo_report_data.json")


# ---------- DoD 5: business-value chart ----------
def charts():
    an = ROOT / "out/analytics.json"
    pngs = list((ROOT / "reports/charts").glob("*.png")) + list((ROOT / "reports/charts").glob("*.svg"))
    check("charts: analytics.json + >=1 chart image",
          "PASS" if an.exists() and pngs else "FAIL",
          f"analytics={an.exists()}, images={len(pngs)} (Block 8)")


# ---------- dashboard self-containment (the primary demo surface) ----------
def dashboard_check():
    h = ROOT / "out/dashboard.html"
    if not h.exists():
        return check("dashboard: self-contained html built", "FAIL", "out/dashboard.html missing (run pipeline/dashboard.py)")
    txt = h.read_text()
    # real external LOADING constructs only (not prose like the skin's "no @import" comment)
    ext = any(s in txt for s in ('src="http', "src='http", 'src="//', 'href="http', "href='http",
                                 'url(http', 'url("http', "url('http", '@import url', '@import "', "@import '"))
    check("dashboard: self-contained (offline)", "PASS" if not ext else "FAIL",
          f"{len(txt) // 1024}KB · external refs: {'none ✓' if not ext else 'FOUND ⚠'}")


# ---------- Phase H packaging (offline fallback exists = dashboard.html; recording/screenshots pending) ----------
def package():
    fb = list((ROOT / "reports").glob("fallback*")) + list((ROOT / "reports").glob("*.mov")) + list((ROOT / "reports").glob("*.mp4"))
    shots = [p for p in (ROOT / "reports/screenshots").glob("*") if p.suffix.lower() in (".png", ".jpg", ".jpeg")]
    check("fallback: money-shot recording", "PASS" if fb else "WARN",
          fb[0].name if fb else "pending — Spike records the /shot audio backup (dashboard.html is the offline visual fallback)")
    check("screenshots captured", "PASS" if shots else "WARN", f"{len(shots)} in reports/screenshots" if shots else "pending Phase H capture")
    ds = ROOT / "docs/demo_script.md"
    check("demo script exists", "PASS" if ds.exists() else "WARN", "")


# ---------- rules: Bolna at core ----------
def bolna_core():
    pool = [jload(p) for p in (ROOT / "data/normalized").glob("*.json")]
    n_bolna = sum(1 for c in pool if c.get("source") == "bolna")
    check("rule: Bolna call ingested into pipeline", "PASS" if n_bolna else "FAIL",
          f"{n_bolna} bolna-source calls in pool (Block 10 — now CORE)")
    check("pool: >=9 normalized calls", "PASS" if len(pool) >= 9 else "FAIL", f"{len(pool)} calls")


# ---------- rule: Cartesia is configured inside the Bolna agent's synthesizer ----------
# Cartesia runs INSIDE Bolna (synthesizer.provider == cartesia) — verified through the Bolna agent
# endpoint with BOLNA_API_KEY. We never call api.cartesia.ai. Offline mode validates the cached
# sponsor-proof artifact (out/bolna_cartesia_proof.json) instead of the live endpoint.
PROOF = ROOT / "out" / "bolna_cartesia_proof.json"


def cartesia_live():
    if OFFLINE:
        if PROOF.exists():
            sys.path.insert(0, str(ROOT / "pipeline"))
            from cache_bolna_cartesia_proof import validate_proof
            try:
                p = json.loads(PROOF.read_text())
            except Exception as e:
                return check("rule: Bolna synthesizer = cartesia (cached proof)", "FAIL", f"unreadable: {e}")
            ok, problem = validate_proof(p)   # strict: exact keys, agent_id, provider, voice, tz, model type
            return check("rule: Bolna synthesizer = cartesia (cached proof)", "PASS" if ok else "FAIL",
                         f"{p.get('synthesizer_provider')}/{p.get('cartesia_voice')}/{p.get('cartesia_model')} · captured {p.get('fetched_at')}"
                         if ok else problem)
        return check("rule: Bolna synthesizer = cartesia", "SKIP", "--offline (no cached proof yet)")
    load_env()
    key = os.environ.get("BOLNA_API_KEY")
    if not key:
        return check("rule: Bolna synthesizer = cartesia", "SKIP", "no BOLNA_API_KEY")
    try:
        import urllib.request
        sys.path.insert(0, str(ROOT / "pipeline"))
        from cache_bolna_cartesia_proof import build_proof, validate_proof
        req = urllib.request.Request(f"https://api.bolna.ai/v2/agent/{AGENT_ID}",
                                     headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=15) as r:
            cfg = json.loads(r.read().decode())
        proof = build_proof(cfg)                          # SAME strict extraction as the proof fetch
        ok, problem = validate_proof(proof)               # missing agent id / missing voice -> FAIL
        check("rule: Bolna synthesizer = cartesia", "PASS" if ok else "FAIL",
              f"{proof.get('synthesizer_provider')}/{proof.get('cartesia_voice')}/{proof.get('cartesia_model')}"
              if ok else problem)
    except Exception as e:
        check("rule: Bolna synthesizer = cartesia", "SKIP", f"network: {type(e).__name__}")


# ---------- repo hygiene ----------
def git_state():
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                           cwd=ROOT).stdout.strip()
    ahead = subprocess.run(["git", "rev-list", "@{u}..HEAD", "--count"], capture_output=True,
                           text=True, cwd=ROOT).stdout.strip()
    check("git: committed", "PASS" if not dirty else "WARN", f"{len(dirty.splitlines())} dirty files" if dirty else "")
    check("git: pushed", "PASS" if ahead in ("", "0") else "WARN", f"{ahead} unpushed commits" if ahead not in ("", "0") else "")


def main():
    for fn in (hero, scored, judge_run_check, calibration, improvement_queue, charts, dashboard_check,
               package, bolna_core, cartesia_live, git_state):
        try:
            fn()
        except Exception as e:
            check(fn.__name__, "FAIL", f"checker crashed: {type(e).__name__}: {e}")
    width = max(len(n) for n, _, _ in RESULTS) + 2
    fails = warns = 0
    print(f"{'check':<{width}}{'status':<7}detail")
    print("-" * (width + 40))
    for n, s, d in RESULTS:
        fails += s == "FAIL"
        warns += s == "WARN"
        print(f"{n:<{width}}{s:<7}{d}")
    print("-" * (width + 40))
    print(f"PREFLIGHT: {fails} FAIL · {warns} WARN · "
          f"{'READY TO SUBMIT' if fails == 0 else 'NOT READY — the FAILs are the to-do list'}")
    sys.exit(min(fails, 1))


if __name__ == "__main__":
    main()
