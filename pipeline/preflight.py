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


# ---------- DoD 3: >=10 DPO pairs in valid TRL JSONL ----------
def dpo():
    q = ROOT / "out/queue.jsonl"
    if not q.exists():
        return check("dpo: out/queue.jsonl >=10 valid pairs", "FAIL", "not built (Block 5)")
    good = bad = 0
    for line in q.read_text().splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            assert isinstance(row["prompt"], list) and row["chosen"] and row["rejected"]
            assert row["chosen"] != row["rejected"]
            good += 1
        except Exception:
            bad += 1
    check("dpo: out/queue.jsonl >=10 valid pairs", "PASS" if good >= 10 and bad == 0 else "FAIL",
          f"{good} valid, {bad} malformed")
    mirror = ROOT / "out/queue_openai.jsonl"
    check("dpo: OpenAI mirror", "PASS" if mirror.exists() else "FAIL",
          "" if mirror.exists() else "queue_openai.jsonl missing")


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
    kp = next(iter((ROOT / "out").glob("kappa*.json")), None) or next(iter((ROOT / "reports").glob("kappa*")), None)
    if kp:
        check("kappa: number + CI + disagreements", "PASS", kp.name)
    else:
        check("kappa: number + CI + disagreements", "FAIL", "not computed (Block 7)")


# ---------- DoD 5: business-value chart ----------
def charts():
    an = ROOT / "out/analytics.json"
    pngs = list((ROOT / "reports/charts").glob("*.png")) + list((ROOT / "reports/charts").glob("*.svg"))
    check("charts: analytics.json + >=1 chart image",
          "PASS" if an.exists() and pngs else "FAIL",
          f"analytics={an.exists()}, images={len(pngs)} (Block 8)")


# ---------- DoD 6: demo script + fallback recording ----------
def package():
    fb = list((ROOT / "reports").glob("fallback*"))
    check("fallback: money-shot recording", "PASS" if fb else "FAIL",
          fb[0].name if fb else "record at ~20:30 Jun 12 (Block 11) — NEVER cut")
    ds = ROOT / "docs/demo-script.md"
    check("demo script exists", "PASS" if ds.exists() else "WARN", "")
    slides = list((ROOT / "reports").glob("*slide*")) + list((ROOT / "reports").glob("*.pdf")) + list((ROOT / "reports").glob("*.pptx"))
    check("slides", "PASS" if slides else "WARN", "not made yet (Block 11)" if not slides else slides[0].name)


# ---------- rules: Bolna at core ----------
def bolna_core():
    pool = [jload(p) for p in (ROOT / "data/normalized").glob("*.json")]
    n_bolna = sum(1 for c in pool if c.get("source") == "bolna")
    check("rule: Bolna call ingested into pipeline", "PASS" if n_bolna else "FAIL",
          f"{n_bolna} bolna-source calls in pool (Block 10 — now CORE)")
    check("pool: >=9 normalized calls", "PASS" if len(pool) >= 9 else "FAIL", f"{len(pool)} calls")


# ---------- rules: live agent still Cartesia-voiced ----------
def cartesia_live():
    if OFFLINE:
        return check("rule: live agent voice = cartesia", "SKIP", "--offline")
    load_env()
    key = os.environ.get("BOLNA_API_KEY")
    if not key:
        return check("rule: live agent voice = cartesia", "SKIP", "no key")
    try:
        import urllib.request
        req = urllib.request.Request(f"https://api.bolna.ai/v2/agent/{AGENT_ID}",
                                     headers={"Authorization": f"Bearer {key}"})
        with urllib.request.urlopen(req, timeout=15) as r:
            cfg = json.loads(r.read().decode())
        syn = cfg["tasks"][0]["tools_config"]["synthesizer"]
        ok = syn.get("provider") == "cartesia"
        check("rule: live agent voice = cartesia", "PASS" if ok else "FAIL",
              f"{syn.get('provider')}/{syn.get('provider_config', {}).get('voice')}")
    except Exception as e:
        check("rule: live agent voice = cartesia", "SKIP", f"network: {type(e).__name__}")


# ---------- repo hygiene ----------
def git_state():
    dirty = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                           cwd=ROOT).stdout.strip()
    ahead = subprocess.run(["git", "rev-list", "@{u}..HEAD", "--count"], capture_output=True,
                           text=True, cwd=ROOT).stdout.strip()
    check("git: committed", "PASS" if not dirty else "WARN", f"{len(dirty.splitlines())} dirty files" if dirty else "")
    check("git: pushed", "PASS" if ahead in ("", "0") else "WARN", f"{ahead} unpushed commits" if ahead not in ("", "0") else "")


def main():
    for fn in (hero, scored, dpo, calibration, charts, package, bolna_core, cartesia_live, git_state):
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
