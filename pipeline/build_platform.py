#!/usr/bin/env python3
"""Generate the OPERATOR workspace surface at out/platform/.

This is a NEW generator (sibling of build_surface.py). It does NOT touch
out/surface/*, voiceforge_design/*, dashboard.html, or any frozen artifact.

INPUTS (read-only):
  out/surface/design_data.js   -> window.__DATA__ : the real 76-call data
                                   (rows w/ transcript/dims/judge/human, analytics,
                                    report/calibration/metric_trap).
  out/demo_report_data.json    -> archetypes, representatives, improvement_queue,
                                   metric_trap, tags, product matrix.
  out/live_calls.json          -> OPTIONAL live slice (graceful empty state if absent).

OUTPUT:
  out/platform/platform_data.js   (assembled, self-contained, zero network refs)
  out/platform/index.html
  out/platform/app.js
  out/platform/styles.css

The operator surface is a workspace, not a presentation: a fixed left call
directory rail (search + filters), a Frozen Pilot <-> Live Today switch,
aggregate clusters + individual-call evidence views, and a live empty state
near the top with an execution-id command helper (display only).

Run:  python3 pipeline/build_platform.py
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SURFACE = OUT / "surface"
PLATFORM = OUT / "platform"

DESIGN_DATA_JS = SURFACE / "design_data.js"
DEMO_REPORT = OUT / "demo_report_data.json"
LIVE_CALLS = OUT / "live_calls.json"
CLINIC_STATE = OUT / "clinic_agent_state.json"   # sidecar; agent + KB + before-improvement metadata


def _load_design_data():
    """Parse window.__DATA__ = {...}; out of design_data.js (read-only)."""
    txt = DESIGN_DATA_JS.read_text()
    m = re.search(r"window\.__DATA__\s*=\s*(\{.*\})\s*;?\s*$", txt, re.S)
    if not m:
        raise SystemExit("could not parse window.__DATA__ from design_data.js")
    return json.loads(m.group(1))


def _load_demo_report():
    if not DEMO_REPORT.exists():
        return {}
    try:
        return json.loads(DEMO_REPORT.read_text())
    except Exception:
        return {}


def _load_clinic():
    """Read clinic_agent_state.json sidecar if present. Returns None if absent — the
    platform falls back to the generic 'Live Today' label. Read-only; the sidecar is
    the source of truth for the agent + KB + before-improvement metadata Codex confirmed."""
    if not CLINIC_STATE.exists():
        return None
    try:
        return json.loads(CLINIC_STATE.read_text())
    except Exception as e:
        return {"_unreadable": str(e)}


def _load_live():
    """Read live_calls.json if present; tolerate absence/corruption."""
    if not LIVE_CALLS.exists():
        return {"live": False, "calls": [], "note": "No live calls yet — ingest on-site."}
    try:
        data = json.loads(LIVE_CALLS.read_text())
    except Exception as e:
        return {"live": False, "calls": [], "note": f"live_calls.json unreadable: {e}"}
    if isinstance(data, list):
        return {"live": bool(data), "calls": data}
    if isinstance(data, dict):
        data.setdefault("calls", [])
        data.setdefault("live", bool(data.get("calls")))
        return data
    return {"live": False, "calls": [], "note": "live_calls.json has unexpected shape."}


def _index_by_id(items, key="call_id"):
    out = {}
    for it in items or []:
        cid = it.get(key)
        if cid is not None:
            out[cid] = it
    return out


def assemble():
    dd = _load_design_data()
    dr = _load_demo_report()
    live = _load_live()
    clinic = _load_clinic()  # sidecar w/ agent + KB; tags before-improvement call if present

    rows = dd.get("rows", [])

    # Side tables keyed by call id, to attach phenotype/recommendation/provenance.
    reps = _index_by_id(dr.get("representatives", []))
    queue = _index_by_id(dr.get("improvement_queue", []))

    # fix_first phenotype evidence (for provenance + recommendation cross-link)
    fix_first = (dr.get("product") or {}).get("fix_first", {}) or {}
    fix_first_ids = set(fix_first.get("evidence_call_ids", []) or [])

    calls = []
    for r in rows:
        cid = r.get("id")
        rep = reps.get(cid, {})
        q = queue.get(cid, {})
        human = r.get("human")  # may be None (unlabeled / outside manifest)

        # archetype / phenotype: prefer representative, then queue.
        archetype = rep.get("archetype") or q.get("archetype")
        recommendation = rep.get("recommendation") or q.get("recommendation")

        # provenance string
        prov_bits = [f"source={r.get('source')}"]
        prov_bits.append("in_manifest" if r.get("in_manifest") else "outside_blind_slice")
        if human:
            prov_bits.append(f"human={human.get('label')}/{human.get('confidence')} (single-rater)")
        jb = (r.get("judge") or {}).get("binary") or {}
        if jb:
            prov_bits.append(f"judge_binary={jb.get('label')} ({jb.get('provenance','uncalibrated')})")
        if cid in fix_first_ids:
            prov_bits.append("fix_first_evidence")

        calls.append({
            "id": cid,
            "source": r.get("source"),
            "lang": r.get("lang"),
            "profile": r.get("profile"),
            "wf": r.get("wf"),
            "turns": r.get("turns"),
            "outcome": r.get("outcome"),
            "overall": r.get("overall"),
            "in_manifest": bool(r.get("in_manifest")),
            "archetype": archetype,
            "recommendation": recommendation,
            "human": human,
            "dims": r.get("dims", []),          # deterministic signals
            "failures": r.get("failures", []),  # deterministic failure events
            "transcript": r.get("transcript", []),
            "judge": r.get("judge", {}),        # judge.dims (cited) + judge.binary (cited)
            "provenance": " · ".join(b for b in prov_bits if b),
            "fix_first_evidence": cid in fix_first_ids,
        })

    # Identify the "before improvement" live call by id from the sidecar, so the
    # rail can badge it without re-deriving the link in JS.
    before_id = ((clinic or {}).get("executions") or {}).get("before_improvement", {}).get("call_id")

    payload = {
        "generated_from": "pipeline/build_platform.py",
        "data_basis": ("Aarogya Clinic & Diagnostics — Aarav · LIVE clinic agent (uncalibrated)"
                       " · frozen 46-call calibration: methodology proof (κ measured-not-assumed)"
                       if clinic else "frozen pilot: 76 scored calls, 46 timed, 45-call blind-labeled slice"),
        "analytics": dd.get("analytics", {}),
        "report": dd.get("report", {}),
        "calibration": (dd.get("report") or {}).get("calibration", {}),
        "metric_trap": dr.get("metric_trap") or (dd.get("report") or {}).get("metric_trap", {}),
        "archetypes": dr.get("archetypes", {}),
        "product": dr.get("product", {}),
        "improvement_queue": dr.get("improvement_queue", []),
        "fix_first": fix_first,
        "privacy_note": dd.get("privacy_note", ""),
        "sponsor_proof": dd.get("sponsor_proof", {}),
        "calls": calls,
        "live": live,
        "clinic": clinic,                       # None when sidecar absent → JS falls back to generic Live Today
        "before_improvement_call_id": before_id,
    }
    return payload


def write_outputs(payload):
    PLATFORM.mkdir(parents=True, exist_ok=True)
    data_js = (
        "/* GENERATED by pipeline/build_platform.py — operator workspace data.\n"
        "   Self-contained, zero network references. Do not hand-edit. */\n"
        "window.__PLATFORM__ = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )
    (PLATFORM / "platform_data.js").write_text(data_js, encoding="utf-8")
    (PLATFORM / "index.html").write_text(INDEX_HTML, encoding="utf-8")
    (PLATFORM / "styles.css").write_text(STYLES_CSS, encoding="utf-8")
    (PLATFORM / "app.js").write_text(APP_JS, encoding="utf-8")

    print(f"wrote {PLATFORM/'platform_data.js'} ({len(data_js):,} bytes, {len(payload['calls'])} calls)")
    print(f"wrote {PLATFORM/'index.html'}")
    print(f"wrote {PLATFORM/'styles.css'}")
    print(f"wrote {PLATFORM/'app.js'}")
    live = payload["live"]
    print(f"live: {'present' if live.get('live') else 'EMPTY'} ({len(live.get('calls',[]))} calls)")


# ----------------------------------------------------------------------------
# Static assets. Kept inline so the generator is a single self-contained file.
# ----------------------------------------------------------------------------

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>VoiceForge — Operator Workspace</title>
<link rel="stylesheet" href="styles.css">
</head>
<body>
<div id="app">
  <aside id="rail" aria-label="Call directory">
    <header class="rail-head">
      <div class="brand"><span class="brand-dot"></span> VoiceForge <span class="brand-sub">operator</span></div>
      <div class="mode-switch" role="tablist" aria-label="Data set">
        <button id="mode-frozen" class="mode-btn active" role="tab" aria-selected="true">Frozen Pilot</button>
        <button id="mode-live" class="mode-btn" role="tab" aria-selected="false"><span id="mode-live-label">Live Today</span> <span id="live-pip" class="live-pip" hidden></span></button>
      </div>
      <input id="search" class="search" type="search" placeholder="Search call id, language, workflow…" autocomplete="off">
      <div id="filters" class="filters"></div>
      <div id="rail-count" class="rail-count"></div>
    </header>
    <div id="rail-list" class="rail-list" role="listbox" aria-label="Calls"></div>
  </aside>
  <main id="main">
    <div id="detail" class="detail"></div>
  </main>
</div>
<script src="platform_data.js"></script>
<script src="app.js"></script>
</body>
</html>
"""

STYLES_CSS = r""":root{
  --paper:#FAF6EE; --paper-deep:#F2EBDD; --ink:#221B12; --ink-soft:#6B6052;
  --ink-faint:#998D7C; --line:#E3D9C6; --line-soft:#ECE4D3; --card:#FFFDF8;
  --ember:#B4541C; --ember-deep:#8D3E10; --ember-soft:#F3DECB;
  --ok:#2E6B4F; --ok-soft:#E2EDE4; --bad:#A23A2A; --bad-soft:#F2E0DA; --unsure:#8A7A5C;
  --prov-measured:#3E5F73; --prov-human:#2E6B4F; --prov-calibrated:#5B4E84;
  --prov-uncal:#8A6A2F; --prov-estimated:#B4541C; --prov-notobs:#8B8478;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  --mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --rail-w:312px; --radius:12px;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{font-family:var(--sans);color:var(--ink);background:var(--paper)}
#app{display:flex;height:100vh;overflow:hidden}

/* ---- rail ---- */
#rail{width:var(--rail-w);flex:0 0 var(--rail-w);background:var(--paper-deep);
  border-right:1px solid var(--line);display:flex;flex-direction:column;height:100vh}
.rail-head{padding:14px 14px 10px;border-bottom:1px solid var(--line);flex:0 0 auto}
.brand{font-family:var(--serif);font-size:18px;font-weight:600;display:flex;align-items:center;gap:8px}
.brand-dot{width:10px;height:10px;border-radius:50%;background:var(--ember);box-shadow:0 0 0 4px var(--ember-soft)}
.brand-sub{font-family:var(--sans);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--ember);font-weight:700;margin-left:auto}
.mode-switch{display:flex;gap:0;margin:12px 0 10px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:3px}
.mode-btn{flex:1;border:0;background:transparent;font-family:var(--sans);font-size:12px;font-weight:600;
  color:var(--ink-soft);padding:7px 6px;border-radius:7px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:5px}
.mode-btn.active{background:var(--ink);color:var(--paper)}
.live-pip{width:7px;height:7px;border-radius:50%;background:var(--bad);box-shadow:0 0 0 3px var(--bad-soft)}
.search{width:100%;border:1px solid var(--line);background:var(--card);border-radius:8px;
  padding:8px 10px;font-size:13px;font-family:var(--sans);color:var(--ink);margin-bottom:8px}
.search:focus{outline:2px solid var(--ember-soft);border-color:var(--ember)}
.filters{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:6px}
.filter-group{display:flex;flex-wrap:wrap;gap:4px}
.chip{font-size:10.5px;border:1px solid var(--line);background:var(--card);color:var(--ink-soft);
  padding:3px 8px;border-radius:20px;cursor:pointer;font-weight:600;letter-spacing:.02em}
.chip.on{background:var(--ember);border-color:var(--ember);color:#fff}
.rail-count{font-size:11px;color:var(--ink-faint);margin-top:4px;font-variant-numeric:tabular-nums}
.rail-list{overflow-y:auto;flex:1 1 auto;padding:6px 8px}
.call-card{border:1px solid var(--line);background:var(--card);border-radius:10px;padding:9px 11px;margin-bottom:7px;cursor:pointer;transition:border-color .12s,box-shadow .12s}
.call-card:hover{border-color:var(--ember);box-shadow:0 1px 0 var(--ember-soft)}
.call-card.sel{border-color:var(--ember);box-shadow:0 0 0 2px var(--ember-soft)}
.call-card .cid{font-family:var(--mono);font-size:12px;font-weight:600;display:flex;align-items:center;gap:6px}
.call-card .meta{font-size:11px;color:var(--ink-soft);margin-top:3px;display:flex;flex-wrap:wrap;gap:6px}
.call-card .ph{font-size:10.5px;color:var(--ink-faint);margin-top:3px}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;flex:0 0 auto}
.dot.ok{background:var(--ok)} .dot.bad{background:var(--bad)} .dot.unsure{background:var(--unsure)}
.live-tag{font-size:9px;font-weight:800;letter-spacing:.08em;color:#fff;background:var(--bad);padding:1px 5px;border-radius:4px}
.empty-rail{padding:18px 12px;color:var(--ink-faint);font-size:12px;text-align:center}

/* ---- live empty state (rail top) ---- */
.cl-card{margin:8px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--card)}
.cl-card.cl-agent{border-left:3px solid var(--ember)}
.cl-card.cl-kb{border-left:3px solid var(--prov-measured)}
.cl-card .cl-head{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:6px}
.cl-card .cl-kicker{font-size:9px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-faint)}
.cl-card .cl-prov{font-family:var(--mono);font-size:9px;font-weight:800;letter-spacing:.08em;padding:2px 6px;border-radius:4px;border:1px solid currentColor}
.cl-card .cl-prov.ok{color:var(--ok)}
.cl-card .cl-prov.uncal{color:var(--prov-uncal)}
.cl-card .cl-title{font-size:13px;font-weight:700;color:var(--ink);margin-bottom:8px;line-height:1.3}
.cl-card .cl-meta{display:flex;flex-direction:column;gap:4px}
.cl-card .cl-meta > div{display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-size:11px}
.cl-card .cl-k{color:var(--ink-faint);text-transform:lowercase;letter-spacing:.02em}
.cl-card .cl-v{color:var(--ink);font-weight:600}
.cl-card .cl-v.mono{font-family:var(--mono);font-size:10.5px}
.cl-card .cl-v.prov.ok{color:var(--ok)}
.cl-card .cl-v.prov.uncal{color:var(--prov-uncal)}
.before-tag{font-size:8.5px;font-weight:800;letter-spacing:.08em;color:#fff;background:var(--prov-uncal);padding:1px 5px;border-radius:4px;margin-left:4px}
.live-empty{margin:8px;padding:14px;border:1px dashed var(--bad);border-radius:10px;background:var(--bad-soft)}
.live-empty h3{margin:0 0 4px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--bad)}
.live-empty p{margin:0 0 10px;font-size:12px;color:var(--ink-soft);line-height:1.5}
.cmd-helper label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.07em;color:var(--ink-faint);margin-bottom:4px}
.cmd-helper input{width:100%;border:1px solid var(--line);border-radius:6px;padding:6px 8px;font-family:var(--mono);font-size:12px;margin-bottom:6px}
.cmd-box{background:var(--ink);color:#F4ECD8;font-family:var(--mono);font-size:11px;line-height:1.6;
  padding:9px 10px;border-radius:7px;white-space:pre-wrap;word-break:break-all;position:relative}
.cmd-box .copy{position:absolute;top:6px;right:6px;background:var(--ember);color:#fff;border:0;border-radius:5px;font-size:9.5px;font-weight:700;padding:3px 7px;cursor:pointer;letter-spacing:.05em}
.cmd-note{font-size:10px;color:var(--ink-faint);margin-top:6px;line-height:1.45}

/* ---- main / detail ---- */
#main{flex:1 1 auto;overflow-y:auto;height:100vh;background:var(--paper)}
.detail{max-width:980px;margin:0 auto;padding:26px 30px 80px}
.banner{display:flex;align-items:center;gap:10px;padding:9px 14px;border-radius:10px;font-size:12px;font-weight:600;margin-bottom:20px}
.banner.frozen{background:var(--paper-deep);border:1px solid var(--line);color:var(--ink-soft)}
.banner.live{background:var(--bad-soft);border:1px solid var(--bad);color:var(--bad)}
.banner .big{font-size:13px;letter-spacing:.1em;text-transform:uppercase;font-weight:800}

h1.view-title{font-family:var(--serif);font-size:26px;margin:0 0 2px}
.subtitle{color:var(--ink-soft);font-size:13px;margin:0 0 22px}

/* aggregate */
.agg-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-bottom:24px}
.metric{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:15px 16px}
.metric .k{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-faint);margin-bottom:6px}
.metric .v{font-family:var(--serif);font-size:28px;font-weight:600;line-height:1}
.metric .v.warn{color:var(--ember)}
.metric .sub{font-size:11.5px;color:var(--ink-soft);margin-top:6px;line-height:1.45}
.section{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;margin-bottom:18px}
.section h2{font-family:var(--serif);font-size:18px;margin:0 0 12px}
.cluster-row{display:flex;align-items:center;gap:10px;padding:8px 0;border-top:1px solid var(--line-soft)}
.cluster-row:first-of-type{border-top:0}
.cluster-row .name{flex:0 0 200px;font-size:13px;font-weight:600}
.bar{flex:1 1 auto;height:9px;background:var(--paper-deep);border-radius:5px;overflow:hidden}
.bar>i{display:block;height:100%;background:var(--ember);border-radius:5px}
.bar.good>i{background:var(--ok)}
.cluster-row .num{flex:0 0 auto;font-variant-numeric:tabular-nums;font-size:12px;color:var(--ink-soft);min-width:64px;text-align:right}
.cluster-row .ex{flex:0 0 auto}
.linkid{font-family:var(--mono);font-size:11px;color:var(--ember);cursor:pointer;text-decoration:underline;margin-left:6px}
.caption{font-size:11.5px;color:var(--ink-soft);line-height:1.5;margin-top:10px;border-top:1px solid var(--line-soft);padding-top:10px}
table.coverage{width:100%;border-collapse:collapse;font-size:12.5px}
table.coverage th,table.coverage td{text-align:left;padding:6px 8px;border-top:1px solid var(--line-soft)}
table.coverage th{font-size:10.5px;text-transform:uppercase;letter-spacing:.05em;color:var(--ink-faint);border-top:0}
table.coverage td.num{text-align:right;font-variant-numeric:tabular-nums}

/* individual call */
.call-head{display:flex;align-items:flex-start;gap:14px;flex-wrap:wrap;margin-bottom:6px}
.call-head .id{font-family:var(--mono);font-size:20px;font-weight:700}
.pills{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 18px}
.pill{font-size:11px;font-weight:600;border-radius:20px;padding:3px 10px;border:1px solid var(--line);background:var(--card);color:var(--ink-soft)}
.pill.ok{background:var(--ok-soft);border-color:var(--ok);color:var(--ok)}
.pill.bad{background:var(--bad-soft);border-color:var(--bad);color:var(--bad)}
.pill.uncal{background:#FBF1DD;border-color:var(--prov-uncal);color:var(--prov-uncal)}
.pill.arch{background:var(--ember-soft);border-color:var(--ember);color:var(--ember-deep)}
.grid2{display:grid;grid-template-columns:1.05fr .95fr;gap:18px;align-items:start}
@media (max-width:1100px){.grid2{grid-template-columns:1fr}}
.transcript{max-height:560px;overflow-y:auto;padding-right:6px}
.turn{display:flex;gap:8px;margin-bottom:8px;font-size:13px;line-height:1.45}
.turn .tid{font-family:var(--mono);font-size:10px;color:var(--ink-faint);flex:0 0 30px;padding-top:3px}
.turn .bubble{border-radius:10px;padding:7px 11px;max-width:100%}
.turn.agent .bubble{background:var(--paper-deep)}
.turn.user .bubble{background:var(--ember-soft)}
.turn .who{font-size:9.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--ink-faint);font-weight:700;margin-bottom:2px}
.turn.cited .bubble{box-shadow:0 0 0 2px var(--prov-calibrated)}
.turn.cited .who::after{content:" · cited";color:var(--prov-calibrated)}
.dim{border-top:1px solid var(--line-soft);padding:9px 0}
.dim:first-child{border-top:0}
.dim .dh{display:flex;align-items:center;gap:8px}
.dim .dn{font-size:12.5px;font-weight:600}
.dim .dscore{margin-left:auto;font-variant-numeric:tabular-nums;font-size:12px;font-weight:700}
.dim .dtype{font-size:9px;text-transform:uppercase;letter-spacing:.06em;padding:1px 6px;border-radius:4px;font-weight:700}
.dtype.deterministic{background:#E3EAF0;color:var(--prov-measured)}
.dtype.judge{background:#FBF1DD;color:var(--prov-uncal)}
.dim .dr{font-size:11.5px;color:var(--ink-soft);margin-top:4px;line-height:1.45}
.dim .cites{font-size:10px;color:var(--prov-calibrated);margin-top:3px;cursor:pointer}
.rec{background:var(--ember-soft);border:1px solid var(--ember);border-radius:10px;padding:12px 14px;margin-top:14px}
.rec .rh{font-size:10.5px;text-transform:uppercase;letter-spacing:.07em;color:var(--ember-deep);font-weight:700;margin-bottom:4px}
.rec .rt{font-size:13.5px;line-height:1.5}
.prov{font-family:var(--mono);font-size:10.5px;color:var(--ink-faint);margin-top:16px;line-height:1.6;border-top:1px solid var(--line-soft);padding-top:10px}
.placeholder{color:var(--ink-faint);font-size:14px;text-align:center;padding:80px 20px}
.unmeasured{color:var(--ink-faint);font-style:italic}
"""

APP_JS = r"""(function(){
"use strict";
var D = window.__PLATFORM__ || {};
var CALLS = D.calls || [];
var LIVE = D.live || {live:false,calls:[]};
var CLINIC = D.clinic || null;                    // sidecar: agent + KB + before-improvement metadata
var BEFORE_ID = D.before_improvement_call_id || null;

var state = { mode:"frozen", q:"", filters:{source:null,outcome:null,profile:null}, selected:null };

var $ = function(s,r){return (r||document).querySelector(s);};
function el(tag,cls,txt){var e=document.createElement(tag);if(cls)e.className=cls;if(txt!=null)e.textContent=txt;return e;}
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[c];});}
function pct(x){return (x==null)?"—":Math.round(x*100)+"%";}
function fnum(x,d){return (x==null)?"—":Number(x).toFixed(d==null?2:d);}

/* ---------- LIVE call normalization (tolerant shapes) ---------- */
function normLive(c, i){
  var id = c.call_id || c.id || ("live_"+i);
  var oc = c.outcome;
  if(oc && typeof oc==="object") oc = oc.task_completed;
  // The live call's turn list lives under `turns` (Bolna normalized shape) — fall back to transcript
  // for older fixtures. Turn objects use {turn_id, speaker, text}.
  var turnList = Array.isArray(c.turns) ? c.turns : (Array.isArray(c.transcript) ? c.transcript : []);
  var turnCount = (typeof c.turns === "number") ? c.turns : turnList.length;
  return {
    id:id, source:c.source||c.provider||"live", lang:c.language||c.lang||"—",
    profile:c.stress_profile||c.profile||"—", wf:c.workflow_type||c.wf||"—",
    turns:turnCount,
    outcome: oc===true?true:oc===false?false:null,
    overall:c.overall!=null?c.overall:null, in_manifest:false, live:true,
    archetype:c.archetype||null, recommendation:c.recommendation||null,
    human:c.human||null,
    dims:c.dims||c.deterministic||[], failures:c.failures||[],
    transcript:turnList.map(function(t,j){
      return {
        id:t.id||t.turn_id||("t"+(j+1)),
        s:t.s||t.speaker||t.role||"agent",
        x:t.x||t.text||t.utterance||""
      };
    }),
    judge:c.judge||{},
    provenance:"LIVE · UNCALIBRATED · source="+(c.source||c.provider||"live"),
    fix_first_evidence:false
  };
}
function liveCalls(){ return (LIVE.calls||[]).map(normLive); }

function activeCalls(){ return state.mode==="live" ? liveCalls() : CALLS; }

/* ---------- filtering ---------- */
function matches(c){
  var f=state.filters;
  if(f.source && c.source!==f.source) return false;
  if(f.profile && c.profile!==f.profile) return false;
  if(f.outcome==="completed" && c.outcome!==true) return false;
  if(f.outcome==="failed" && c.outcome!==false) return false;
  if(f.outcome==="pending" && c.outcome!=null) return false;
  if(state.q){
    var q=state.q.toLowerCase();
    var hay=[c.id,c.lang,c.wf,c.source,c.profile,c.archetype].join(" ").toLowerCase();
    if(hay.indexOf(q)<0) return false;
  }
  return true;
}

/* ---------- rail ---------- */
function outcomeDot(c){
  if(c.outcome===true) return '<span class="dot ok"></span>';
  if(c.outcome===false) return '<span class="dot bad"></span>';
  return '<span class="dot unsure"></span>';
}
function renderFilters(){
  var box=$("#filters"); box.innerHTML="";
  var calls=activeCalls();
  function uniq(key){var s={};calls.forEach(function(c){if(c[key]!=null&&c[key]!=="")s[c[key]]=1;});return Object.keys(s).sort();}
  function group(label, key, values, stateKey, valueMap){
    var g=el("div","filter-group");
    values.forEach(function(v){
      var disp = valueMap ? valueMap(v) : v;
      var chip=el("button","chip", disp);
      var on = state.filters[stateKey]===v;
      if(on) chip.className="chip on";
      chip.onclick=function(){ state.filters[stateKey] = on?null:v; render(); };
      g.appendChild(chip);
    });
    if(values.length) box.appendChild(g);
  }
  group("outcome","outcome",["completed","failed","pending"],"outcome");
  group("source","source",uniq("source"),"source");
  group("profile","profile",uniq("profile"),"profile");
}

function renderRail(){
  var list=$("#rail-list"); list.innerHTML="";
  var calls=activeCalls().filter(matches);

  // LIVE empty state pinned to TOP of rail.
  if(state.mode==="live" && (!LIVE.live || liveCalls().length===0)){
    list.appendChild(liveEmptyEl());
    $("#rail-count").textContent="live · 0 calls ingested";
    return;
  }
  if(state.mode==="live"){
    if(CLINIC){
      list.appendChild(clinicAgentCard());
      list.appendChild(clinicKbCard());
    }
    var hint=el("div","live-empty");
    hint.style.borderStyle="solid";
    hint.innerHTML='<h3>Live · uncalibrated</h3><p>These calls were ingested today. No human label or kappa applies yet — treat scores as diagnostic only.</p>';
    list.appendChild(hint);
  }

  $("#rail-count").textContent = (state.mode==="live"?"live":"frozen pilot")+" · "+calls.length+" of "+activeCalls().length+" calls";
  if(!calls.length){ list.appendChild(el("div","empty-rail","No calls match your search / filters.")); return; }

  calls.forEach(function(c){
    var card=el("div","call-card");
    if(state.selected===c.id) card.className="call-card sel";
    var live = c.live ? ' <span class="live-tag">LIVE</span>' : "";
    var beforeBadge = (c.live && BEFORE_ID && c.id===BEFORE_ID)
      ? ' <span class="before-tag" title="Defects in this call were repaired in the final agent — kept as the honest baseline.">BEFORE IMPROVEMENT</span>' : "";
    card.innerHTML =
      '<div class="cid">'+outcomeDot(c)+esc(c.id)+live+beforeBadge+'</div>'+
      '<div class="meta"><span>'+esc(c.lang)+'</span><span>'+esc(c.profile)+'</span><span>'+(c.turns!=null?c.turns+" turns":"")+'</span></div>'+
      (c.archetype?'<div class="ph">'+esc(c.archetype.replace(/_/g," "))+'</div>':'');
    card.onclick=function(){ state.selected=c.id; render(); };
    list.appendChild(card);
  });
}

/* ---------- clinic agent + KB cards (top of live rail when sidecar present) ---------- */
function clinicAgentCard(){
  var a = (CLINIC && CLINIC.agent) || {};
  var s = (CLINIC && CLINIC.synthesizer) || {};
  var voiceLabel = s.verified ? (s.label_when_verified || "Cartesia · Devansh · sonic-3 (verified)")
                              : "Cartesia · provider unverified";
  var voiceClass = s.verified ? "prov ok" : "prov uncal";
  var langs = (a.languages || []).join(" + ") || "—";
  var idShort = a.id ? (a.id.slice(0,8)+"…") : "—";
  return htmlEl(
    '<div class="cl-card cl-agent" title="'+esc(a.id||"")+'">'+
      '<div class="cl-head"><span class="cl-kicker">Agent</span><span class="cl-prov uncal">LIVE · UNCALIBRATED</span></div>'+
      '<div class="cl-title">'+esc(a.name||"Live agent")+'</div>'+
      '<div class="cl-meta">'+
        '<div><span class="cl-k">agent_id</span><span class="cl-v mono">'+esc(idShort)+'</span></div>'+
        '<div><span class="cl-k">voice</span><span class="cl-v '+voiceClass+'">'+esc(voiceLabel)+'</span></div>'+
        '<div><span class="cl-k">languages</span><span class="cl-v">'+esc(langs)+'</span></div>'+
        '<div><span class="cl-k">status</span><span class="cl-v">'+esc(a.deployment_status||a.bolna_status||"—")+'</span></div>'+
      '</div>'+
    '</div>'
  );
}
function clinicKbCard(){
  var k = (CLINIC && CLINIC.knowledge_base) || {};
  var idShort = k.vector_id ? (k.vector_id.slice(0,8)+"…") : "—";
  var processed = k.status==="processed";
  var attached = k.attached_to_llm===true;
  return htmlEl(
    '<div class="cl-card cl-kb">'+
      '<div class="cl-head"><span class="cl-kicker">Knowledge base</span><span class="cl-prov '+(processed?'ok':'uncal')+'">'+esc((k.status||"unknown").toUpperCase())+'</span></div>'+
      '<div class="cl-title">'+esc(k.scope||"Connected knowledge base")+'</div>'+
      '<div class="cl-meta">'+
        '<div><span class="cl-k">vector_id</span><span class="cl-v mono">'+esc(idShort)+'</span></div>'+
        '<div><span class="cl-k">attached to LLM</span><span class="cl-v '+(attached?'prov ok':'prov uncal')+'">'+(attached?'yes':'no')+'</span></div>'+
      '</div>'+
    '</div>'
  );
}

/* ---------- live empty state + command helper ---------- */
function liveEmptyEl(){
  var box=el("div","live-empty");
  var note = esc(LIVE.note || "No live calls yet — ingest on-site.");
  box.innerHTML =
    '<h3>Live Today · empty</h3>'+
    '<p>'+note+' Paste a provider execution id below to get the exact ingest + judge command. This panel only DISPLAYS the command — nothing runs from the browser.</p>'+
    '<div class="cmd-helper">'+
      '<label for="exec-id">Execution id</label>'+
      '<input id="exec-id" type="text" placeholder="e.g. exec_1a2b3c…" autocomplete="off">'+
      '<div class="cmd-box" id="cmd-out"><button class="copy" id="cmd-copy">COPY</button><span id="cmd-text"></span></div>'+
      '<div class="cmd-note">Run in the repo root, then switch back to Live Today. Live cards appear as <b>LIVE · UNCALIBRATED</b>; no human label or kappa applies until calibration.</div>'+
    '</div>';
  var input = box.querySelector("#exec-id");
  var out = box.querySelector("#cmd-text");
  function build(){
    var id=(input.value||"").trim() || "<execution-id>";
    out.textContent = "python pipeline/ingest_live.py --execution "+id+" && python pipeline/judge_live.py";
  }
  build();
  input.addEventListener("input", build);
  box.querySelector("#cmd-copy").addEventListener("click", function(){
    var t=out.textContent;
    if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(t).catch(function(){}); }
    var btn=box.querySelector("#cmd-copy"); var old=btn.textContent; btn.textContent="COPIED"; setTimeout(function(){btn.textContent=old;},1200);
  });
  return box;
}

/* ---------- detail: aggregate ---------- */
function aggregateView(){
  var wrap=el("div");
  var live=state.mode==="live";
  var d=el("div", live?"banner live":"banner frozen");
  d.innerHTML = live
    ? '<span class="big">Live · uncalibrated</span><span>Today’s ingested calls. Diagnostic scores only — no human label or kappa yet.</span>'
    : '<span class="big">Frozen pilot</span><span>'+esc(D.data_basis||"")+'</span>';
  wrap.appendChild(d);

  if(live){
    var liveTitle = CLINIC ? "Live Clinic Agent" : "Live Today";
    var liveSub = CLINIC
      ? "Live calls from the Aarogya appointment agent. <b>LIVE · UNCALIBRATED</b> — no human label or κ applies. Frozen 46-call calibration stays separate as the methodology proof."
      : "Select a live call from the rail to open its full evidence view.";
    wrap.appendChild(htmlEl('<h1 class="view-title">'+liveTitle+'</h1><p class="subtitle">'+liveSub+'</p>'));
    if(!LIVE.live || liveCalls().length===0){
      wrap.appendChild(htmlEl('<div class="section"><h2>No live calls yet</h2><p class="caption" style="border:0;padding:0;margin:0">Use the execution-id helper in the left rail to generate the ingest command, then re-open Live Today.</p></div>'));
      return wrap;
    }
    // simple live aggregate
    var lc=liveCalls();
    var done=lc.filter(function(c){return c.outcome===true;}).length;
    wrap.appendChild(metricsGrid([
      ["Calls ingested today", lc.length, null, ""],
      ["Completed (heuristic)", done+" / "+lc.length, null, "Deterministic outcome — uncalibrated."],
    ]));
    return wrap;
  }

  var a=D.analytics||{}, rep=D.report||{}, prod=D.product||{}, cal=D.calibration||{}, mt=D.metric_trap||{};
  wrap.appendChild(htmlEl('<h1 class="view-title">Aggregate</h1><p class="subtitle">Success / friction / failure across the frozen pilot. Click any call id to open its evidence.</p>'));

  wrap.appendChild(metricsGrid([
    ["Scored calls", a.n_calls!=null?a.n_calls:CALLS.length, null, (a.timing_coverage?a.timing_coverage.timed+" timed · "+a.timing_coverage.unmeasured+" unmeasured":"")],
    ["Human success rate", pct(prod.human_success_rate), null, "Blind single-rater, "+(prod.matrix?prod.matrix.n:"—")+" calls"],
    ["Friction or failure spend", pct(prod.friction_or_failure_spend_share)+" warn", "warn", "$"+fnum(prod.friction_or_failure_spend_est)+" of estimated spend"],
    ["Judge vs human κ", fnum(cal.kappa)+" ("+(cal.band||"—")+")", null, "raw agreement "+pct(cal.raw_agreement)+"; CI includes 0"],
  ]));

  // archetype clusters
  var arch=(D.archetypes&&D.archetypes.counts)||{};
  var archMax=Math.max(1, Math.max.apply(null, Object.values(arch).map(Number).concat([1])));
  var sec=el("div","section");
  sec.appendChild(htmlEl('<h2>Outcome clusters</h2>'));
  Object.keys(arch).forEach(function(k){
    if(arch[k]===0) return;
    var good = /success/.test(k) && !/failure/.test(k);
    var row=el("div","cluster-row");
    row.innerHTML='<span class="name">'+esc(k.replace(/_/g," "))+'</span>'+
      '<span class="bar'+(good?" good":"")+'"><i style="width:'+(arch[k]/archMax*100)+'%"></i></span>'+
      '<span class="num">'+arch[k]+'</span>';
    sec.appendChild(row);
  });
  sec.appendChild(htmlEl('<div class="caption">'+esc((D.archetypes&&D.archetypes.derivation)||"")+'</div>'));
  wrap.appendChild(sec);

  // failure clusters (deterministic events) w/ jump links
  var fc=a.failure_clusters||(rep.corpus&&rep.corpus.failure_event_clusters)||[];
  if(fc.length){
    var fmax=Math.max.apply(null, fc.map(function(x){return x.count;}).concat([1]));
    var fsec=el("div","section");
    fsec.appendChild(htmlEl('<h2>Friction signal clusters (deterministic)</h2>'));
    fc.forEach(function(c){
      var row=el("div","cluster-row");
      var ex=(c.example_call_ids||[]).slice(0,4).map(function(id){return '<span class="linkid" data-id="'+esc(id)+'">'+esc(id)+'</span>';}).join("");
      row.innerHTML='<span class="name">'+esc(c.dimension.replace(/_/g," "))+'</span>'+
        '<span class="bar"><i style="width:'+(c.count/fmax*100)+'%"></i></span>'+
        '<span class="num">'+c.count+' events</span>';
      var exwrap=el("div"); exwrap.style.cssText="flex-basis:100%;font-size:11px;color:var(--ink-faint);padding-left:0;margin-top:-2px";
      exwrap.innerHTML="examples: "+ex;
      fsec.appendChild(row); fsec.appendChild(exwrap);
    });
    wrap.appendChild(fsec);
  }

  // cost-quality by stress profile
  var bsp=a.by_stress_profile||[];
  if(bsp.length){
    var csec=el("div","section");
    csec.appendChild(htmlEl('<h2>Cost &amp; quality by stress profile</h2>'));
    var t='<table class="coverage"><thead><tr><th>profile</th><th class="num">n</th><th class="num">success</th><th class="num">cost</th><th class="num">$/success</th></tr></thead><tbody>';
    bsp.forEach(function(r){
      t+='<tr><td>'+esc(r.stress_profile)+'</td><td class="num">'+r.n+'</td><td class="num">'+pct(r.success_rate)+'</td><td class="num">$'+fnum(r.cost)+'</td><td class="num">$'+fnum(r.cost_per_successful_call)+'</td></tr>';
    });
    t+='</tbody></table>';
    csec.appendChild(htmlEl(t));
    wrap.appendChild(csec);
  }

  // timing coverage
  if(a.timing_coverage){
    var tc=a.timing_coverage;
    wrap.appendChild(htmlEl('<div class="section"><h2>Timing coverage</h2><table class="coverage"><tbody>'+
      '<tr><td>Timed (latency-measured)</td><td class="num">'+tc.timed+'</td></tr>'+
      '<tr><td>Unmeasured (no per-turn timestamps)</td><td class="num">'+tc.unmeasured+'</td></tr>'+
      '</tbody></table><div class="caption">avg overall is computed over TIMED calls only for a consistent dimension basis.</div></div>'));
  }

  // metric trap
  if(mt && mt.caption){
    wrap.appendChild(htmlEl('<div class="section"><h2>The metric trap</h2><div class="caption" style="border:0;padding:0;font-size:13px;color:var(--ink)">'+esc(mt.caption)+'</div><div class="caption">'+esc(mt.provenance||"")+'</div></div>'));
  }

  // improvement queue -> jump links
  var iq=D.improvement_queue||[];
  if(iq.length){
    var qsec=el("div","section");
    qsec.appendChild(htmlEl('<h2>Improvement queue ('+iq.length+')</h2>'));
    iq.slice(0,20).forEach(function(q){
      var row=el("div","cluster-row");
      row.innerHTML='<span class="name"><span class="linkid" data-id="'+esc(q.call_id)+'">'+esc(q.call_id)+'</span></span>'+
        '<span style="flex:1 1 auto;font-size:12px;color:var(--ink-soft)">'+esc(q.recommendation||"")+'</span>'+
        '<span class="num">'+esc((q.archetype||"").replace(/_/g," "))+'</span>';
      qsec.appendChild(row);
    });
    wrap.appendChild(qsec);
  }
  return wrap;
}

/* ---------- detail: individual ---------- */
function callView(c){
  var wrap=el("div");
  var live=!!c.live;
  var d=el("div", live?"banner live":"banner frozen");
  d.innerHTML = live
    ? '<span class="big">Live · uncalibrated</span><span>Ingested today — diagnostic only, no human label / kappa.</span>'
    : '<span class="big">Frozen pilot</span><span>'+esc(c.provenance||"")+'</span>';
  wrap.appendChild(d);

  var oc = c.outcome===true?'<span class="pill ok">task completed</span>':c.outcome===false?'<span class="pill bad">task not completed</span>':'<span class="pill">outcome pending</span>';
  var hu = c.human?'<span class="pill">human: '+esc(c.human.label)+'/'+esc(c.human.confidence)+'</span>':'';
  var arch = c.archetype?'<span class="pill arch">'+esc(c.archetype.replace(/_/g," "))+'</span>':'';
  var jb = (c.judge&&c.judge.binary)||null;
  var jbpill = jb?'<span class="pill uncal">judge: '+esc(jb.label)+' · '+(live?"uncalibrated":esc(jb.provenance||"uncalibrated"))+'</span>':'';
  var head=el("div");
  head.innerHTML='<div class="call-head"><span class="id">'+esc(c.id)+'</span>'+(live?'<span class="live-tag" style="font-size:11px;padding:2px 7px">LIVE · UNCALIBRATED</span>':'')+'</div>'+
    '<div class="pills"><span class="pill">'+esc(c.source)+'</span><span class="pill">'+esc(c.lang)+'</span><span class="pill">'+esc(c.profile)+'</span><span class="pill">'+esc(c.wf)+'</span><span class="pill">'+(c.turns!=null?c.turns+' turns':'—')+'</span>'+oc+arch+hu+jbpill+'</div>';
  wrap.appendChild(head);

  var grid=el("div","grid2");

  // transcript (left)
  var cited={};
  (c.dims||[]).concat(((c.judge&&c.judge.dims)||[])).forEach(function(dm){(dm.evidence_turn_ids||[]).forEach(function(t){cited[t]=1;});});
  if(jb)(jb.evidence_turn_ids||[]).forEach(function(t){cited[t]=1;});
  var tcol=el("div","section");
  tcol.appendChild(htmlEl('<h2>Transcript</h2>'));
  var tlist=el("div","transcript");
  (c.transcript||[]).forEach(function(t){
    var who=(t.s==="user")?"user":"agent";
    var turn=el("div","turn "+who+(cited[t.id]?" cited":""));
    turn.id="turn-"+esc(t.id);
    turn.innerHTML='<span class="tid">'+esc(t.id)+'</span><div><div class="who">'+who+'</div><div class="bubble">'+esc(t.x)+'</div></div>';
    tlist.appendChild(turn);
  });
  if(!(c.transcript||[]).length) tlist.appendChild(htmlEl('<div class="placeholder">No transcript turns.</div>'));
  tcol.appendChild(tlist);
  grid.appendChild(tcol);

  // signals + judge (right)
  var rcol=el("div");
  var detSec=el("div","section");
  detSec.appendChild(htmlEl('<h2>Deterministic signals</h2>'));
  (c.dims||[]).forEach(function(dm){ detSec.appendChild(dimEl(dm)); });
  if(!(c.dims||[]).length) detSec.appendChild(htmlEl('<div class="unmeasured">No deterministic dims for this call.</div>'));
  rcol.appendChild(detSec);

  var jdims=(c.judge&&c.judge.dims)||[];
  var jSec=el("div","section");
  jSec.appendChild(htmlEl('<h2>Judge evidence <span style="font-size:11px;color:var(--prov-uncal);font-weight:600">· uncalibrated diagnostics</span></h2>'));
  if(jb){
    jSec.appendChild(htmlEl('<div class="dim"><div class="dh"><span class="dn">Outcome judgment</span><span class="dscore '+(jb.label==="success"?"":"")+'">'+esc(jb.label)+'</span><span class="dtype judge">binary</span></div><div class="dr">'+esc(jb.reason||"")+'</div>'+citesEl(jb.evidence_turn_ids)+'</div>'));
  }
  jdims.forEach(function(dm){ jSec.appendChild(dimEl(dm)); });
  if(!jdims.length && !jb) jSec.appendChild(htmlEl('<div class="unmeasured">No judge output for this call.</div>'));
  rcol.appendChild(jSec);

  if(c.recommendation){
    rcol.appendChild(htmlEl('<div class="rec"><div class="rh">Recommendation</div><div class="rt">'+esc(c.recommendation)+'</div></div>'));
  }
  rcol.appendChild(htmlEl('<div class="prov">provenance: '+esc(c.provenance||"")+'</div>'));
  grid.appendChild(rcol);

  wrap.appendChild(grid);
  return wrap;
}

function dimEl(dm){
  var d=el("div","dim");
  var sc = (dm.score!=null)? (Number(dm.score).toFixed(2)) : "—";
  d.innerHTML='<div class="dh"><span class="dn">'+esc((dm.name||"").replace(/_/g," "))+'</span>'+
    '<span class="dscore">'+sc+'</span><span class="dtype '+esc(dm.type||"deterministic")+'">'+esc(dm.type||"")+'</span></div>'+
    '<div class="dr">'+esc(dm.reason||"")+'</div>'+citesEl(dm.evidence_turn_ids);
  return d;
}
function citesEl(ids){
  if(!ids||!ids.length) return "";
  return '<div class="cites" data-cites="'+esc(ids.join(","))+'">cited turns: '+ids.map(esc).join(", ")+'</div>';
}

/* ---------- helpers ---------- */
function metricsGrid(items){
  var g=el("div","agg-grid");
  items.forEach(function(it){
    var m=el("div","metric");
    var vcls = it[2]==="warn"?"v warn":"v";
    var v=String(it[1]).replace(/ warn$/,"");
    m.innerHTML='<div class="k">'+esc(it[0])+'</div><div class="'+vcls+'">'+esc(v)+'</div>'+(it[3]?'<div class="sub">'+esc(it[3])+'</div>':"");
    g.appendChild(m);
  });
  return g;
}
function htmlEl(h){var d=document.createElement("div");d.innerHTML=h;return d.firstChild;}

/* ---------- jump-to-call wiring (event delegation) ---------- */
function wireJumps(root){
  root.addEventListener("click", function(e){
    var lk=e.target.closest&&e.target.closest(".linkid");
    if(lk){ var id=lk.getAttribute("data-id"); if(state.mode!=="frozen"){state.mode="frozen";} state.selected=id; render(); return; }
    var ct=e.target.closest&&e.target.closest(".cites");
    if(ct){
      var first=(ct.getAttribute("data-cites")||"").split(",")[0];
      var node=document.getElementById("turn-"+first);
      if(node){ node.scrollIntoView({behavior:"smooth",block:"center"}); node.style.transition="box-shadow .3s"; node.querySelector(".bubble").style.boxShadow="0 0 0 3px var(--ember)"; setTimeout(function(){var b=node.querySelector(".bubble"); if(b)b.style.boxShadow="";},900); }
    }
  });
}

/* ---------- render ---------- */
function render(){
  // mode buttons
  var mf=$("#mode-frozen"), ml=$("#mode-live");
  mf.classList.toggle("active", state.mode==="frozen");
  mf.setAttribute("aria-selected", state.mode==="frozen");
  ml.classList.toggle("active", state.mode==="live");
  ml.setAttribute("aria-selected", state.mode==="live");
  var pip=$("#live-pip"); pip.hidden = !(LIVE.live && liveCalls().length);

  renderFilters();
  renderRail();

  var detail=$("#detail");
  detail.innerHTML="";
  var calls=activeCalls();
  var sel = state.selected!=null ? calls.filter(function(c){return c.id===state.selected;})[0] : null;
  if(sel){ detail.appendChild(callView(sel)); }
  else { detail.appendChild(aggregateView()); }
}

function init(){
  if(CLINIC){
    var ll = $("#mode-live-label"); if(ll) ll.textContent = "Live Clinic Agent";
    // Open straight to the live lane when the clinic sidecar is present — this is the demo surface.
    state.mode = "live";
    if(BEFORE_ID) state.selected = BEFORE_ID;     // pre-open the before-improvement call
  }
  $("#mode-frozen").onclick=function(){ state.mode="frozen"; state.selected=null; render(); };
  $("#mode-live").onclick=function(){ state.mode="live"; state.selected=null; render(); };
  $("#search").addEventListener("input", function(e){ state.q=e.target.value; renderRail(); });
  wireJumps($("#main"));
  wireJumps($("#rail-list"));
  render();
}
if(document.readyState==="loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
"""


def main():
    if not DESIGN_DATA_JS.exists():
        raise SystemExit("missing out/surface/design_data.js — run pipeline/build_surface.py first")
    payload = assemble()
    write_outputs(payload)
    print("done.")


if __name__ == "__main__":
    main()
