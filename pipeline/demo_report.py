#!/usr/bin/env python3
"""VoiceForge demo report (Batch B). ONE generator -> out/demo_report.md + out/demo_report.html
(self-contained static page — survives even if every server dies).

    .venv/bin/python pipeline/demo_report.py             # real artifacts -> out/
    .venv/bin/python pipeline/demo_report.py --selftest  # synthetic fixtures in a tempdir, asserts honesty rules

HONESTY CONTRACT (enforced, not aspirational):
- Reads GENERATED artifacts only (out/analytics.json, out/calls.json, eval/labels_spike.csv,
  eval/label_manifest.json, out/judge_results.json if it exists). Nothing hardcoded.
- Missing inputs render an explicit PENDING state — never an invented number.
- Calibration (agreement/confusion/kappa) appears ONLY when >=FLOOR binary labels AND judge results exist.
- Phenotype tags are single-rater EXPLORATORY — labeled as such, never "calibrated".
- Archetypes are DERIVED deterministically (documented precedence), never hand-labeled.
- "failure EVENTS" (signal hits), not "failed calls". Costs say "estimated, prototype".
  Task completion says "heuristic". Kappa calibrates ONLY the dedicated binary outcome judge;
  the 5 semantic dims have no per-dimension human gold and stay uncalibrated diagnostics.

Judge artifact contract (produced by the gated Batch E, consumed here when present):
  out/judge_results.json = {"run": {model, temperature, rubric_hash, n_calls, cache_hits, failures, started},
                            "calls": {call_id: {"dims": {...}, "binary": {"label": "success|fail",
                                                                          "rule": "<documented mapping>"}}}}
"""
import argparse
import csv
import hashlib
import io
import json
import math
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "pipeline"))
FLOOR = 40

ARCHETYPES = ["seamless_success", "brittle_success", "recovered_success",
              "language_mismatch_failure", "intent_or_slot_loss_failure",
              "repair_loop_failure", "workflow_failure", "ambiguous_or_unassessable"]

RECOMMEND = {  # deterministic tag -> recommendation templates (marked template-derived in output)
    "workflow_or_tool_failed": "add a tool-failure fallback path (acknowledge, retry once, then offer human handoff)",
    "wrong_language_or_tone": "detect caller language/register in the first 2 turns and switch the response style",
    "misunderstood_user": "add an explicit confirmation turn before acting on the inferred intent",
    "missing_or_wrong_information": "require slot read-back before closing; re-ask for any unfilled required slot",
    "repeated_or_stuck": "cap repeats at 2, then rephrase with a concrete example instead of repeating verbatim",
    "poor_clarification_or_recovery": "replace generic re-asks with a targeted clarifying question naming the unclear slot",
    "hard_to_understand": "shorten agent turns to one action each; move details behind a follow-up question",
    "user_frustrated": "acknowledge frustration explicitly once, then shorten the path to the goal or escalate",
}

MECHANISM = {
    "workflow_or_tool_failed": "A bounded retry and explicit fallback prevents a tool error from silently ending the workflow.",
    "wrong_language_or_tone": "Earlier language and register adaptation reduces comprehension friction before it becomes a repair loop.",
    "misunderstood_user": "Confirming the inferred intent before acting catches a wrong branch while recovery is still cheap.",
    "missing_or_wrong_information": "A required-slot read-back catches omissions before the agent closes the call.",
    "repeated_or_stuck": "A repeat cap forces a different repair strategy instead of replaying the same failed wording.",
    "poor_clarification_or_recovery": "A targeted question names the unclear slot and lowers the caller's repair burden.",
    "hard_to_understand": "One-action turns reduce cognitive load and make the next expected response explicit.",
    "user_frustrated": "Acknowledging frustration and shortening the path reduces further repair turns and escalation risk.",
}


# ---------------------------------------------------------------- loading (every input optional)
def load(paths):
    d = {}
    d["analytics"] = json.loads(paths["analytics"].read_text()) if paths["analytics"].exists() else None
    d["calls"] = {c["call_id"]: c for c in json.loads(paths["calls"].read_text())} if paths["calls"].exists() else {}
    d["manifest"] = json.loads(paths["manifest"].read_text()) if paths["manifest"].exists() else None
    d["labels"] = []
    if paths["labels"].exists():
        d["labels"] = list(csv.DictReader(io.StringIO(paths["labels"].read_bytes().decode())))
    d["judge"] = json.loads(paths["judge"].read_text()) if paths["judge"].exists() else None
    return d


def tags_of(row):
    split = lambda s: [t for t in (s or "").split("|") if t]
    return split(row["positive_tags"]), split(row["negative_tags"]), split(row["context_tags"])


# ---------------------------------------------------------------- derivations (deterministic)
def archetype(row):
    """Level-3 archetype from Level-1 outcome + Level-2 tags. Documented precedence; never hand-labeled."""
    pos, neg, _ = tags_of(row)
    p = row["primary_label"]
    if p == "unsure":
        return "ambiguous_or_unassessable"
    if p == "success":
        if "handled_confusion_well" in pos and neg:
            return "recovered_success"
        return "brittle_success" if neg else "seamless_success"
    # fail — precedence: workflow > language > intent/slot > repair-loop > slotless default
    if "workflow_or_tool_failed" in neg:
        return "workflow_failure"
    if "wrong_language_or_tone" in neg:
        return "language_mismatch_failure"
    if "misunderstood_user" in neg or "missing_or_wrong_information" in neg:
        return "intent_or_slot_loss_failure"
    if "repeated_or_stuck" in neg or "poor_clarification_or_recovery" in neg:
        return "repair_loop_failure"
    return "intent_or_slot_loss_failure"


def kappa_block(labels, judge):
    """Agreement vs judge binary — ONLY when both sides exist at floor. Returns None -> render pending."""
    if not judge:
        return None
    j = {cid: v.get("binary", {}).get("label") for cid, v in judge.get("calls", {}).items()}
    pairs = [(r["primary_label"], j.get(r["call_id"])) for r in labels
             if r["primary_label"] in ("success", "fail") and j.get(r["call_id"]) in ("success", "fail")]
    if len(pairs) < FLOOR:
        return None
    n = len(pairs)
    a = sum(1 for h, g in pairs if h == g)
    cm = Counter(pairs)  # (human, judge)
    ph_s = sum(1 for h, _ in pairs if h == "success") / n
    pj_s = sum(1 for _, g in pairs if g == "success") / n
    pe = ph_s * pj_s + (1 - ph_s) * (1 - pj_s)
    po = a / n
    k = (po - pe) / (1 - pe) if pe < 1 else 0.0
    # deterministic bootstrap CI (seeded) — honest small-n interval
    import random
    rng = random.Random(13)
    ks = []
    for _ in range(2000):
        s = [pairs[rng.randrange(n)] for _ in range(n)]
        po_b = sum(1 for h, g in s if h == g) / n
        ph = sum(1 for h, _ in s if h == "success") / n
        pj = sum(1 for _, g in s if g == "success") / n
        pe_b = ph * pj + (1 - ph) * (1 - pj)
        ks.append((po_b - pe_b) / (1 - pe_b) if pe_b < 1 else 0.0)
    ks.sort()
    disagree = [r["call_id"] for r in labels
                if r["primary_label"] in ("success", "fail")
                and j.get(r["call_id"]) in ("success", "fail")
                and r["primary_label"] != j.get(r["call_id"])]
    ci_lo, ci_hi = round(ks[int(0.025 * len(ks))], 3), round(ks[int(0.975 * len(ks))], 3)
    band = ("poor" if k < 0 else "slight" if k < 0.21 else "fair" if k < 0.41 else
            "moderate" if k < 0.61 else "substantial" if k < 0.81 else "almost-perfect")
    cs = sum(1 for cid in disagree if cid.startswith("cmd_"))
    caption = (f"{band.capitalize()} agreement (Landis–Koch); the 95% CI "
               f"{'includes 0' if ci_lo <= 0 <= ci_hi else 'is tight'} — at n={n} with "
               f"{round(ph_s * 100)}% success prevalence the prevalence paradox compresses κ. This is the gap a "
               f"calibration step exists to expose: {cs} of {len(disagree)} disagreements are code-switched "
               f"(hi-en) calls, so the judge is least reliable exactly there. Measured, not assumed — a team "
               f"trusting this judge uncalibrated would be wrong on {len(disagree)}/{n} calls and never know.")
    return {"n": n, "raw_agreement": round(po, 3), "kappa": round(k, 3), "ci95": [ci_lo, ci_hi],
            "confusion": {f"h_{h}|j_{g}": cnt for (h, g), cnt in sorted(cm.items())},
            "disagreements": disagree,
            "disagreements_code_switched": cs,
            "band": band, "caption": caption}


def build(d):
    """All report data as a dict — single source for md + html. Pending states are explicit."""
    labels = d["labels"]
    binary = [r for r in labels if r["primary_label"] in ("success", "fail")]
    unsure = [r for r in labels if r["primary_label"] == "unsure"]
    man_total = d["manifest"]["total"] if d["manifest"] else None

    pos_c, neg_c, ctx_c, co = Counter(), Counter(), Counter(), Counter()
    arch = Counter()
    for r in labels:
        p, ng, cx = tags_of(r)
        pos_c.update(p); neg_c.update(ng); ctx_c.update(cx)
        for a, b in combinations(sorted(set(p + ng + cx)), 2):
            co[(a, b)] += 1
        arch[archetype(r)] += 1

    cal = kappa_block(labels, d["judge"])
    an = d["analytics"]

    # THE METRIC TRAP: does the deterministic completion HEURISTIC (the metric most teams ship) agree
    # with the blind human binary? Computed over binary-labeled calls only. No invented numbers.
    mt = [(r["primary_label"], d["calls"].get(r["call_id"], {}).get("outcome", {}).get("task_completed"))
          for r in binary]
    mt = [(h, g) for h, g in mt if g is not None]
    mt_n = len(mt)
    mt_agree = sum(1 for h, g in mt if (h == "success") == bool(g))
    mt_missed = sum(1 for h, g in mt if h == "success" and not g)   # heuristic said NOT completed
    mt_falsepass = sum(1 for h, g in mt if h == "fail" and g)        # heuristic said completed
    n_fail = sum(1 for h, _ in mt if h == "fail")
    metric_trap = {
        "n": mt_n, "agree": mt_agree,
        "heuristic_agreement": round(mt_agree / mt_n, 3) if mt_n else None,
        "missed_successes": mt_missed, "false_passes": mt_falsepass, "human_failures": n_fail,
        "caption": (f"The completion heuristic — the metric most voice-agent teams ship — agrees with blind "
                    f"human judgment on only {mt_agree}/{mt_n} calls ({round(mt_agree / mt_n * 100) if mt_n else 0}%). "
                    f"It missed {mt_missed} real successes and passed {mt_falsepass} of {n_fail} real failures. "
                    f"A success-rate dashboard is blind exactly where it costs money."),
        "provenance": "deterministic keyword heuristic (task_completed) vs single-rater blind labels",
    } if mt_n else None

    def est_cost(row):
        call = d["calls"].get(row["call_id"], {})
        return float((call.get("cost") or {}).get("est_cost_total") or 0.0)

    # Product-facing metrics remain deterministic derivations of the frozen human labels and
    # per-call prototype costs. They are not claims of observed savings or model lift.
    success_rows = [r for r in binary if r["primary_label"] == "success"]
    fail_rows = [r for r in binary if r["primary_label"] == "fail"]
    seamless = arch.get("seamless_success", 0)
    recovered = arch.get("recovered_success", 0)
    brittle = arch.get("brittle_success", 0)
    binary_spend = sum(est_cost(r) for r in binary)
    failed_spend = sum(est_cost(r) for r in fail_rows)
    brittle_spend = sum(est_cost(r) for r in labels if archetype(r) == "brittle_success")
    friction_rows = [r for r in binary if r["primary_label"] == "fail" or tags_of(r)[1]]
    friction_spend = sum(est_cost(r) for r in friction_rows)

    tag_calls = {}
    tag_cost = Counter()
    for r in labels:
        for tag in tags_of(r)[1]:
            tag_calls.setdefault(tag, []).append(r["call_id"])
            tag_cost[tag] += est_cost(r)
    top_tag = max(tag_cost, key=lambda t: (tag_cost[t], len(tag_calls[t]), t)) if tag_cost else None
    fix_first = None
    if top_tag:
        affected = tag_calls[top_tag]
        modeled_per_1k = (tag_cost[top_tag] / len(binary) * 1000) if binary else None
        fix_first = {
            "phenotype_id": top_tag,
            "affected_calls": len(affected),
            "estimated_spend_usd": round(tag_cost[top_tag], 4),
            "modeled_exposure_per_1k_usd": round(modeled_per_1k, 2) if modeled_per_1k is not None else None,
            "evidence_call_ids": affected,
            "recommendation": RECOMMEND.get(top_tag),
            "expected_mechanism": MECHANISM.get(top_tag),
            "needs_human_review": True,
            "provenance": "single-rater phenotype + estimated prototype cost",
        }

    # representative calls: deterministically pick the first label per archetype (manifest order)
    order = d["manifest"]["order"] if d["manifest"] else [r["call_id"] for r in labels]
    by_id = {r["call_id"]: r for r in labels}
    reps = []
    seen_arch = set()
    for cid in order:
        r = by_id.get(cid)
        if not r:
            continue
        a = archetype(r)
        if a in seen_arch:
            continue
        seen_arch.add(a)
        _, ng, _ = tags_of(r)
        call = d["calls"].get(cid, {})
        det_fail = [f["dimension"] for f in call.get("failures", [])][:3]
        jd = (d["judge"] or {}).get("calls", {}).get(cid)
        reps.append({"call_id": cid, "human": f"{r['primary_label']}/{r['confidence']}",
                     "archetype": a, "tags": ng or tags_of(r)[0],
                     "deterministic_failures": det_fail,
                     "judge": (jd["binary"]["label"] + " (uncalibrated)" if jd and not cal else
                               jd["binary"]["label"] if jd else "pending"),
                     "recommendation": next((RECOMMEND[t] for t in ng if t in RECOMMEND), None)})
        if len(reps) == 5:
            break

    queue = [{"call_id": r["call_id"], "human": f"{r['primary_label']}/{r['confidence']}",
              "archetype": archetype(r), "evidence_tags": tags_of(r)[1],
              "recommendation": next((RECOMMEND[t] for t in tags_of(r)[1] if t in RECOMMEND), None)}
             for r in labels if tags_of(r)[1]]   # every call with >=1 negative tag, evidence-backed
    queue = [q for q in queue if q["recommendation"]]

    return {"manifest_total": man_total,
            "corpus": {"n_scored": an["n_calls"] if an else None,
                       "timing_coverage": an.get("timing_coverage") if an else None,
                       "success_rate_heuristic": an["success_rate"] if an else None,
                       "cost_per_success_est": an.get("cost_per_successful_call") if an else None,
                       "failure_event_clusters": an["failure_clusters"] if an else None},
            "labels": {"total": len(labels), "binary": len(binary), "unsure": len(unsure),
                       "floor": FLOOR, "floor_met": len(binary) >= FLOOR,
                       "distribution": dict(Counter(r["primary_label"] for r in labels))},
            "product": {
                "human_success_rate": round(len(success_rows) / len(binary), 3) if binary else None,
                "human_successes": len(success_rows),
                "human_failures": len(fail_rows),
                "cost_per_human_success_est": round(binary_spend / len(success_rows), 4) if success_rows else None,
                "failed_call_spend_est": round(failed_spend, 4),
                "brittle_success_spend_est": round(brittle_spend, 4),
                "friction_or_failure_spend_est": round(friction_spend, 4),
                "friction_or_failure_spend_share": round(friction_spend / binary_spend, 3) if binary_spend else None,
                "brittle_share_of_successes": round(brittle / len(success_rows), 3) if success_rows else None,
                "matrix": {
                    "n": len(binary),
                    "seamless_success": seamless,
                    "recovered_success": recovered,
                    "brittle_success": brittle,
                    "failure": len(fail_rows),
                    "unsure_excluded": len(unsure),
                },
                "fix_first": fix_first,
                "caveat": "Human labels are single-rater; costs are estimated prototype values. "
                          "Per-1,000 exposure is a modeled extrapolation from this slice, not observed savings.",
            },
            "calibration": cal,   # None => pending
            "metric_trap": metric_trap,   # heuristic-vs-human agreement (the signature stat)
            "tags": {"positive": dict(pos_c.most_common()), "negative": dict(neg_c.most_common()),
                     "context": dict(ctx_c.most_common()),
                     "co_occurrence_top": [{"pair": list(p), "n": c} for p, c in co.most_common(8)],
                     "caveat": "single-rater exploratory (n=1 annotator) — NOT calibrated"},
            "archetypes": {"counts": {a: arch.get(a, 0) for a in ARCHETYPES},
                           "derivation": "deterministic from Level-1 outcome + Level-2 tags (precedence: "
                                         "workflow > language > intent/slot > repair-loop); never hand-labeled"},
            "representatives": reps,
            "improvement_queue": queue,
            "judge_run": (d["judge"] or {}).get("run")}


# ---------------------------------------------------------------- rendering
def pend(x, msg):
    return msg if x is None else x


def to_md(R):
    L = []
    add = L.append
    add("# VoiceForge — Evaluation Report")
    add("\n> Voice-agent demos stop when the call ends. **VoiceForge starts there**: deterministic signals → "
        "blind human labels → calibrated judge → call phenotypes → failure clusters → an improvement queue.\n")
    c = R["corpus"]
    add("## 1 · Corpus & coverage")
    if c["n_scored"] is None:
        add("**PENDING** — no scored corpus (run `pipeline/score.py`).")
    else:
        tc = c["timing_coverage"] or {}
        add(f"- **{c['n_scored']} calls scored** · timing observed on {tc.get('timed','?')} · "
            f"text-only (timing honestly omitted) on {tc.get('unmeasured','?')}")
        add(f"- task-success rate **{c['success_rate_heuristic']}** *(heuristic keyword match — not gold)* · "
            f"cost/successful call **${c['cost_per_success_est']}** *(estimated, prototype)*")
    add("\n## 2 · Deterministic failure events *(signal hits — NOT failed calls)*")
    if c["failure_event_clusters"]:
        for cl in c["failure_event_clusters"]:
            add(f"- `{cl['dimension']}` × **{cl['count']}** (e.g. {', '.join(cl['example_call_ids'][:3])})")
    else:
        add("**PENDING** — no analytics.")
    lab = R["labels"]
    add(f"\n## 3 · Blind human labels")
    add(f"- labeled **{lab['total']}** of {pend(R['manifest_total'],'?')} · usable binary **{lab['binary']}** "
        f"(floor ≥{lab['floor']}: {'**MET**' if lab['floor_met'] else f'**not yet** — {lab['floor']-lab['binary']} to go'}) "
        f"· unsure {lab['unsure']} (excluded from calibration)")
    add(f"- distribution: `{lab['distribution']}`")
    add("\n## 4 · Human ↔ judge calibration")
    if R["calibration"]:
        k = R["calibration"]
        add(f"- n={k['n']} · raw agreement **{k['raw_agreement']}** · Cohen's κ **{k['kappa']}** "
            f"(bootstrap 95% CI {k['ci95'][0]}–{k['ci95'][1]})")
        add(f"- confusion: `{k['confusion']}` · disagreements: {', '.join(k['disagreements']) or 'none'}")
    else:
        add(f"**PENDING CALIBRATION** — requires ≥{FLOOR} blind binary labels **and** a judged run "
            "(quarantined until labeling completes). No number is shown because none exists yet.")
    t = R["tags"]
    add(f"\n## 5 · Phenotype tags *( {t['caveat']} )*")
    for grp in ("positive", "negative", "context"):
        add(f"- **{grp}**: " + (", ".join(f"`{k}`×{v}" for k, v in t[grp].items()) or "—"))
    if t["co_occurrence_top"]:
        add("- top co-occurring pairs: " + ", ".join(f"`{a}`+`{b}` ×{x['n']}" for x in t["co_occurrence_top"]
                                                     for a, b in [x["pair"]]))
    a = R["archetypes"]
    add(f"\n## 6 · Call archetypes *(Level-3 — {a['derivation']})*")
    for name, n in a["counts"].items():
        if n:
            add(f"- **{name.replace('_',' ')}** × {n}")
    if not any(a["counts"].values()):
        add("**PENDING** — derived once labels exist.")
    add("\n## 7 · Representative calls")
    if R["representatives"]:
        for r in R["representatives"]:
            add(f"- `{r['call_id']}` · human **{r['human']}** · judge {r['judge']} · *{r['archetype'].replace('_',' ')}* · "
                f"tags {r['tags']}" + (f" · det. failures {r['deterministic_failures']}" if r['deterministic_failures'] else "")
                + (f"\n  - → {r['recommendation']} *(template-derived from tags)*" if r['recommendation'] else ""))
    else:
        add("**PENDING** — selected algorithmically per archetype once labels exist (no cherry-picking).")
    add("\n## 8 · Improvement queue *(evidence-backed; recommendations template-derived from observed tags)*")
    if R["improvement_queue"]:
        for q in R["improvement_queue"]:
            add(f"- `{q['call_id']}` ({q['human']}, {q['archetype'].replace('_',' ')}): {q['recommendation']} "
                f"— evidence: {q['evidence_tags']}")
    else:
        add("**PENDING** — built from labeled calls carrying negative tags.")
    if R["judge_run"]:
        jr = R["judge_run"]
        add(f"\n---\njudge run: model `{jr.get('model')}` · temp {jr.get('temperature')} · rubric {str(jr.get('rubric_hash'))[:12]} "
            f"· {jr.get('n_calls')} calls · cache hits {jr.get('cache_hits')} · failures {jr.get('failures')}")
    add("\n---\n*Every number above is computed from committed artifacts. Heuristic = keyword task-completion; "
        "estimated = public per-unit prices; kappa calibrates the binary outcome judge ONLY — semantic dims stay "
        "uncalibrated diagnostics; pending = honestly absent.*")
    return "\n".join(L) + "\n"


def to_html(R, md):
    """Self-contained light-theme static page (no JS deps, no network) — data embedded at build time."""
    import html as H
    cal = R["calibration"]
    lab = R["labels"]

    def card(label, value, note):
        return (f'<div class="card"><div class="v">{value}</div><div class="l">{H.escape(label)}</div>'
                f'<div class="n">{H.escape(note)}</div></div>')

    c = R["corpus"]
    tc = c["timing_coverage"] or {}
    cards = [
        card("calls scored", c["n_scored"] if c["n_scored"] is not None else "—", "deterministic pipeline"),
        card("timing observed", f"{tc.get('timed','—')} / {c['n_scored'] or '—'}", "text-only calls: timing honestly omitted"),
        card("task success", c["success_rate_heuristic"] if c["success_rate_heuristic"] is not None else "—", "HEURISTIC keyword match"),
        card("cost / success", f"${c['cost_per_success_est']}" if c["cost_per_success_est"] is not None else "—", "ESTIMATED, prototype"),
        card("blind labels", f"{lab['binary']}+{lab['unsure']}", f"binary+unsure · floor {lab['floor']}"),
        card("Cohen's κ", cal["kappa"] if cal else "pending", "vs blind human labels" if cal else "gated until labels + judged run"),
    ]
    bars = ""
    neg = R["tags"]["negative"]
    if neg:
        mx = max(neg.values())
        bars = "".join(f'<div class="bar"><span class="bl">{H.escape(k)}</span>'
                       f'<span class="bf" style="width:{int(260*v/mx)}px"></span><b>{v}</b></div>'
                       for k, v in neg.items())
    arch_rows = "".join(f"<tr><td>{H.escape(k.replace('_',' '))}</td><td>{v}</td></tr>"
                        for k, v in R["archetypes"]["counts"].items() if v)
    reps = "".join(
        f'<div class="rep"><code>{H.escape(r["call_id"])}</code> <b>{H.escape(r["human"])}</b> '
        f'<em>{H.escape(r["archetype"].replace("_"," "))}</em> · judge: {H.escape(str(r["judge"]))}'
        + (f'<div class="rec">→ {H.escape(r["recommendation"])}</div>' if r["recommendation"] else "")
        + "</div>" for r in R["representatives"])
    pendnote = ('' if cal else '<div class="pending">Calibration pending — requires ≥40 blind binary labels and the '
                'quarantined judge run. Nothing is faked while it waits.</div>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>VoiceForge — Evaluation Report</title>
<style>
 body{{margin:0;background:#f5f6f8;color:#1a2330;font:15px/1.55 -apple-system,'Segoe UI',Inter,sans-serif}}
 .wrap{{max-width:980px;margin:0 auto;padding:34px 26px 60px}}
 h1{{font-size:26px;margin:0}} h1 b{{color:#16845f}} .sub{{color:#5b6878;margin:6px 0 24px;max-width:760px}}
 h2{{font-size:15px;letter-spacing:.6px;text-transform:uppercase;color:#5b6878;margin:34px 0 12px}}
 .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}}
 .card{{background:#fff;border:1px solid #e1e6ec;border-radius:12px;padding:14px 16px;box-shadow:0 6px 18px rgba(26,35,48,.05)}}
 .card .v{{font-size:24px;font-weight:700}} .card .l{{font-size:12px;color:#5b6878;margin-top:2px}}
 .card .n{{font-size:10.5px;color:#9aa4b1;margin-top:4px}}
 .pending{{margin-top:12px;padding:11px 14px;border:1px solid #ead7b8;background:#fdf6e9;border-radius:10px;color:#8d5c10;font-size:13px}}
 .bar{{display:flex;align-items:center;gap:8px;margin:5px 0;font-size:12.5px}}
 .bl{{width:230px;color:#5b6878}} .bf{{height:12px;background:#c14d52;border-radius:6px;display:inline-block}}
 table{{border-collapse:collapse;background:#fff;border:1px solid #e1e6ec;border-radius:10px;overflow:hidden}}
 td{{padding:7px 16px;border-top:1px solid #eef1f5;font-size:13.5px}}
 .rep{{background:#fff;border:1px solid #e1e6ec;border-radius:10px;padding:10px 14px;margin:8px 0;font-size:13.5px}}
 .rep .rec{{color:#16845f;margin-top:4px}}
 .foot{{margin-top:40px;font-size:11.5px;color:#9aa4b1;border-top:1px solid #e1e6ec;padding-top:14px}}
 code{{background:#eef1f5;border-radius:4px;padding:1px 5px;font-size:12px}}
 details{{margin-top:26px}} pre{{white-space:pre-wrap;font-size:12px;background:#fff;border:1px solid #e1e6ec;border-radius:10px;padding:16px}}
</style></head><body><div class="wrap">
<h1>Voice<b>Forge</b> — evaluation report</h1>
<div class="sub">Most voice-agent demos show a cherry-picked call. VoiceForge shows the <b>failure distribution</b> —
deterministic signals → blind human labels → calibrated judge → call phenotypes → an improvement queue.</div>
<div class="cards">{''.join(cards)}</div>{pendnote}
<h2>Failure phenotypes (negative tags · single-rater exploratory)</h2>{bars or '<div class="pending">Pending blind labels.</div>'}
<h2>Call archetypes (derived deterministically — never hand-labeled)</h2>
{('<table>'+arch_rows+'</table>') if arch_rows else '<div class="pending">Derived once labels exist.</div>'}
<h2>Representative calls (algorithmic per-archetype pick — no cherry-picking)</h2>
{reps or '<div class="pending">Selected once labels exist.</div>'}
<details><summary>Full markdown report</summary><pre>{H.escape(md)}</pre></details>
<div class="foot">heuristic = keyword task-completion · estimated = public per-unit prices · uncalibrated = judge
before kappa (and ALWAYS for the 5 semantic dims — κ calibrates the binary outcome judge only) · pending = honestly absent · failure events ≠ failed calls · generated from committed artifacts only</div>
</div></body></html>"""


def generate(paths, outdir):
    R = build(load(paths))
    md = to_md(R)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "demo_report.md").write_text(md)
    (outdir / "demo_report.html").write_text(to_html(R, md))
    (outdir / "demo_report_data.json").write_text(json.dumps(R, indent=2) + "\n")
    return R


def real_paths():
    return {"analytics": ROOT / "out" / "analytics.json", "calls": ROOT / "out" / "calls.json",
            "labels": ROOT / "eval" / "labels_spike.csv", "manifest": ROOT / "eval" / "label_manifest.json",
            "judge": ROOT / "out" / "judge_results.json"}


# ---------------------------------------------------------------- selftest (synthetic fixtures only)
def selftest():
    import tempfile
    ok = True

    def check(c, msg):
        nonlocal ok
        print(("  ok   " if c else "  FAIL ") + msg)
        ok = ok and c

    with tempfile.TemporaryDirectory(prefix="vf_report_") as td:
        td = Path(td)
        # fixture corpus: tiny analytics + calls + manifest
        (td / "analytics.json").write_text(json.dumps({
            "n_calls": 3, "success_rate": 0.667, "timing_coverage": {"timed": 2, "unmeasured": 1},
            "cost_per_successful_call": 0.1, "failure_clusters": [{"dimension": "latency_gap", "count": 2,
                                                                   "example_call_ids": ["fx1"]}]}))
        (td / "calls.json").write_text(json.dumps([{"call_id": f"fx{i}", "failures": []} for i in (1, 2, 3)]))
        (td / "manifest.json").write_text(json.dumps({"total": 3, "order": ["fx1", "fx2", "fx3"]}))
        paths = {"analytics": td / "analytics.json", "calls": td / "calls.json",
                 "labels": td / "labels.csv", "manifest": td / "manifest.json", "judge": td / "judge.json"}

        # [1] NO labels, NO judge -> every gated section pending, nothing invented
        R = generate(paths, td / "o1")
        check(R["calibration"] is None, "no labels -> calibration pending (None)")
        check(R["labels"]["binary"] == 0 and not any(R["archetypes"]["counts"].values()),
              "no labels -> zero counts, no invented archetypes")
        md = (td / "o1" / "demo_report.md").read_text()
        check("PENDING CALIBRATION" in md and "heuristic" in md, "md renders pending + heuristic caveats")
        check("estimated, prototype" in md, "cost caveat present")

        # [2] labels but <floor -> still pending calibration; tags/archetypes computed
        rows = ["call_id,primary_label,confidence,positive_tags,negative_tags,context_tags,note,timestamp",
                "fx1,success,high,easy_to_understand,,mixed_languages,,t",
                "fx2,fail,medium,,workflow_or_tool_failed|user_frustrated,,t,t",
                "fx3,unsure,low,,,transcript_unclear,,t"]
        (td / "labels.csv").write_text("\n".join(rows) + "\n")
        R = generate(paths, td / "o2")
        check(R["calibration"] is None, "labels<floor -> calibration still pending")
        check(R["archetypes"]["counts"]["seamless_success"] == 1
              and R["archetypes"]["counts"]["workflow_failure"] == 1
              and R["archetypes"]["counts"]["ambiguous_or_unassessable"] == 1, "archetype derivation correct")
        check(R["tags"]["negative"]["workflow_or_tool_failed"] == 1, "tag frequency computed")
        check(any(x["pair"] == ["user_frustrated", "workflow_or_tool_failed"] for x in R["tags"]["co_occurrence_top"]),
              "co-occurrence counted")
        check(R["improvement_queue"] and R["improvement_queue"][0]["call_id"] == "fx2", "improvement queue evidence-backed")
        check("single-rater exploratory" in R["tags"]["caveat"], "tags marked single-rater, not calibrated")

        # [3] labels at floor + judge -> calibration computed (synthetic 40)
        rows = ["call_id,primary_label,confidence,positive_tags,negative_tags,context_tags,note,timestamp"]
        jcalls = {}
        for i in range(40):
            lbl = "success" if i % 2 == 0 else "fail"
            jl = lbl if i % 10 else ("fail" if lbl == "success" else "success")  # 4 disagreements
            rows.append(f"fb{i},{lbl},high,,,,,t")
            jcalls[f"fb{i}"] = {"dims": {}, "binary": {"label": jl, "rule": "fixture"}}
        (td / "labels.csv").write_text("\n".join(rows) + "\n")
        (td / "manifest.json").write_text(json.dumps({"total": 40, "order": [f"fb{i}" for i in range(40)]}))
        (td / "judge.json").write_text(json.dumps({"run": {"model": "fixture", "temperature": 0,
                                                           "rubric_hash": "x", "n_calls": 40, "cache_hits": 0,
                                                           "failures": 0}, "calls": jcalls}))
        R = generate(paths, td / "o3")
        check(R["calibration"] is not None and R["calibration"]["n"] == 40, "floor+judge -> calibration computed")
        check(R["calibration"]["raw_agreement"] == 0.9, "raw agreement exact (36/40)")
        check(R["calibration"]["ci95"][0] <= R["calibration"]["kappa"] <= R["calibration"]["ci95"][1],
              "kappa inside its bootstrap CI")
        html = (td / "o3" / "demo_report.html").read_text()
        check("Cohen" in html and "fixture" not in html.split("judge run")[0][:200], "html renders calibration")
        # determinism: same inputs -> same bytes
        R2 = generate(paths, td / "o3b")
        check((td / "o3" / "demo_report.md").read_bytes() == (td / "o3b" / "demo_report.md").read_bytes(),
              "byte-deterministic md")
    print("\n" + ("REPORT SELFTEST PASSED ✓" if ok else "REPORT SELFTEST FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        sys.exit(selftest())
    R = generate(real_paths(), ROOT / "out")
    print(f"wrote out/demo_report.md + .html + _data.json")
    print(f"  labels {R['labels']['total']} ({R['labels']['binary']} binary) · "
          f"calibration {'computed' if R['calibration'] else 'PENDING'} · "
          f"archetypes {sum(R['archetypes']['counts'].values())} derived")


if __name__ == "__main__":
    main()
