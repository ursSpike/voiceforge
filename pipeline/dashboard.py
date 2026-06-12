#!/usr/bin/env python3
"""VoiceForge dashboard — ONE self-contained glossy HTML (out/dashboard.html). No server, no CDN,
no network: data embedded at build time from generated artifacts only.

    .venv/bin/python pipeline/dashboard.py

Views: Overview · Calls · Call detail · Failure clusters · Improvement queue.

HONESTY + BLINDNESS:
- Reads out/analytics.json, out/demo_report_data.json, out/calls.json, out/judge_results.json (optional).
- BLINDNESS GUARD: while blind labeling is incomplete (<FLOOR binary in out/label_validation.json),
  per-call rows (call list, transcripts, per-call outcomes) are NOT embedded at all — those views render
  a gated notice. This prevents the annotator anchoring on heuristic outcomes mid-labeling.
- Calibration section appears only when the report computed it; otherwise explicit PENDING.
- Heuristic / estimated / uncalibrated / single-rater caveats are rendered, not footnoted away.
"""
import html as H
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
FLOOR = 40


def jload(p):
    return json.loads(p.read_text()) if p.exists() else None


def build():
    A = jload(OUT / "analytics.json")
    R = jload(OUT / "demo_report_data.json")
    calls = jload(OUT / "calls.json") or []
    judge = jload(OUT / "judge_results.json")
    val = jload(OUT / "label_validation.json") or {}
    if not (A and R):
        sys.exit("run pipeline/score.py and pipeline/demo_report.py first")

    gate_open = val.get("binary", 0) >= FLOOR
    cal = R.get("calibration")

    # per-call data: embedded ONLY when the blind gate is open
    rows = []
    if gate_open:
        jcalls = (judge or {}).get("calls", {})
        for c in calls:
            man = c["call_id"] in set((R.get("manifest_total") and jload(ROOT / "eval" / "label_manifest.json")["order"]) or [])
            rows.append({
                "id": c["call_id"], "source": c["source"], "lang": c["language"],
                "profile": c["stress_profile"], "wf": c["workflow_type"], "turns": len(c["turns"]),
                "outcome": c["outcome"]["task_completed"], "overall": c["scorecard"]["overall"],
                "dims": c["scorecard"]["dimensions"], "failures": c["failures"],
                "transcript": [{"s": t["speaker"], "x": t["text"]} for t in c["turns"]],
                "judge": jcalls.get(c["call_id"]), "in_manifest": man,
            })

    data = {"gate_open": gate_open, "floor": FLOOR, "val": {"binary": val.get("binary", 0),
            "unsure": val.get("unsure", 0)}, "analytics": A, "report": R,
            "judge_run": (judge or {}).get("run"), "rows": rows}
    return data


CSS = """
:root{--bg:#f6f7f9;--panel:#ffffff;--ink:#16202c;--mut:#5d6b7c;--faint:#94a0ae;--line:#e4e8ee;
--brand:#0f8a62;--brand2:#0b6d8f;--red:#c2484f;--amber:#a86f16;--glow:0 10px 34px rgba(22,32,44,.07);
--mono:ui-monospace,'SF Mono',Menlo,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:14.5px/1.55 -apple-system,'Segoe UI',Inter,sans-serif}
.shell{display:grid;grid-template-columns:218px 1fr;min-height:100vh}
nav{background:linear-gradient(180deg,#0d1722,#101e2c);color:#cfd8e3;padding:22px 14px;position:sticky;top:0;height:100vh}
.logo{font-size:18px;font-weight:750;color:#fff;letter-spacing:.2px;padding:0 10px}
.logo b{color:#3ddca5}.tag{font-size:10.5px;color:#7e93a8;padding:2px 10px 18px}
nav a{display:flex;gap:9px;align-items:center;padding:9px 12px;border-radius:9px;color:#b9c6d4;
text-decoration:none;font-size:13.5px;font-weight:550;margin:2px 0;cursor:pointer}
nav a.on{background:rgba(61,220,165,.13);color:#3ddca5}nav a:hover{background:rgba(255,255,255,.06)}
.gatechip{margin-top:18px;padding:10px 12px;border-radius:10px;font-size:11.5px;line-height:1.5;
background:rgba(255,255,255,.05);color:#8fa3b8}
main{padding:30px 38px 70px;max-width:1180px}
h1{font-size:22px;margin:0 0 4px}.sub{color:var(--mut);margin:0 0 24px;max-width:720px;font-size:13.5px}
h2{font-size:12.5px;letter-spacing:.8px;text-transform:uppercase;color:var(--mut);margin:32px 0 12px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(158px,1fr));gap:13px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:15px 17px;box-shadow:var(--glow)}
.card .v{font-size:25px;font-weight:760;letter-spacing:-.3px}.card .v small{font-size:13px;color:var(--faint);font-weight:600}
.card .l{font-size:12px;color:var(--mut);margin-top:3px}.card .n{font-size:10.5px;color:var(--faint);margin-top:5px}
.pending{padding:12px 16px;border:1px solid #ecd9b9;background:#fdf6e8;border-radius:12px;color:#8d5c10;
font-size:13px;margin:12px 0}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;box-shadow:var(--glow)}
.split{display:grid;grid-template-columns:1fr 1fr;gap:14px}@media(max-width:980px){.split{grid-template-columns:1fr}}
.bar{display:flex;align-items:center;gap:10px;margin:7px 0;font-size:12.5px}
.bar .bl{width:215px;color:var(--mut)}.bar .bf{height:13px;border-radius:7px;background:linear-gradient(90deg,#c2484f,#d97076)}
.bar .bf.g{background:linear-gradient(90deg,#0f8a62,#33b388)}.bar .bf.b{background:linear-gradient(90deg,#0b6d8f,#3a96b8)}
.bar b{font-size:12px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{font-size:10.5px;text-transform:uppercase;letter-spacing:.6px;color:var(--faint);text-align:left;
padding:8px 10px;border-bottom:1px solid var(--line)}
td{padding:8px 10px;border-bottom:1px solid #f0f2f6}tr.row{cursor:pointer}tr.row:hover td{background:#f3faf7}
.pill{display:inline-block;padding:2px 9px;border-radius:99px;font-size:11px;font-weight:650}
.pill.ok{background:#e7f6ef;color:#0f8a62}.pill.no{background:#fbeaea;color:#c2484f}
.pill.um{background:#eef3f8;color:#5d6b7c}.pill.man{background:#e8f1fb;color:#0b6d8f}
.mono{font:11.5px var(--mono);color:var(--mut)}
.msg{max-width:78%;margin:7px 0}.msg .who{font:10.5px var(--mono);color:var(--faint);margin:0 6px 2px}
.msg .bub{padding:8px 13px;border-radius:13px;background:#f4f6f9;border:1px solid var(--line);font-size:13px}
.msg.agent .bub{border-left:3px solid #7ba6cb;border-bottom-left-radius:4px}
.msg.user{margin-left:auto}.msg.user .bub{border-right:3px solid #58a587;background:#f1f9f5;border-bottom-right-radius:4px}
.dim{display:flex;justify-content:space-between;gap:10px;padding:7px 0;border-bottom:1px solid #f0f2f6;font-size:12.5px}
.dim .sc{font-weight:700}.dim .rs{color:var(--mut);font-size:11.5px}
.crumb{color:var(--brand2);cursor:pointer;font-size:12.5px;margin-bottom:10px;display:inline-block}
.rec{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--brand);border-radius:12px;
padding:12px 16px;margin:9px 0;font-size:13px;box-shadow:var(--glow)}
.rec .why{color:var(--mut);font-size:12px;margin-top:3px}.rec .fix{color:var(--brand);margin-top:5px;font-weight:550}
.search{padding:9px 13px;border:1px solid var(--line);border-radius:10px;width:280px;font:13px inherit;margin-bottom:12px;background:#fff}
.foot{margin-top:44px;border-top:1px solid var(--line);padding-top:14px;font-size:11px;color:var(--faint)}
.kv{font-size:12.5px;color:var(--mut)}.kv b{color:var(--ink)}
"""

JS = """
const D = window.__DATA__;
const $ = s => document.querySelector(s);
const fmt = x => x==null ? '—' : (typeof x==='number' ? (Number.isInteger(x)?x:x.toFixed(3)) : x);
let view='overview', detail=null;
function nav(v){ view=v; detail=null; render(); }
function bars(obj, cls, max){ const m = max||Math.max(1,...Object.values(obj));
  return Object.entries(obj).map(([k,v])=>`<div class="bar"><span class="bl">${k}</span>
  <span class="bf ${cls}" style="width:${Math.max(8,Math.round(330*v/m))}px"></span><b>${v}</b></div>`).join(''); }
function gated(msg){ return `<div class="pending">🔒 ${msg}</div>`; }

function overview(){
  const A=D.analytics, R=D.report, c=R.corpus, t=A.timing_coverage||{}, cal=R.calibration;
  const cards = [
    ['calls scored', A.n_calls, 'deterministic pipeline'],
    ['timing observed', `${t.timed??'—'}<small>/${A.n_calls}</small>`, 'text-only timing honestly omitted'],
    ['task success', A.success_rate, 'HEURISTIC keyword match'],
    ['cost / success', '$'+fmt(A.cost_per_successful_call), 'ESTIMATED, prototype'],
    ['blind labels', `${D.val.binary}<small>+${D.val.unsure} unsure</small>`, `floor ≥${D.floor} binary`],
    ["Cohen's κ", cal?cal.kappa:'pending', cal?`CI ${cal.ci95[0]}–${cal.ci95[1]} · n=${cal.n}`:'gated: labels + judged run'],
  ].map(([l,v,n])=>`<div class="card"><div class="v">${v}</div><div class="l">${l}</div><div class="n">${n}</div></div>`).join('');
  const arch = Object.fromEntries(Object.entries(R.archetypes.counts).filter(([,v])=>v));
  const neg = R.tags.negative;
  return `<h1>Voice<b style="color:var(--brand)">Forge</b> — eval lab</h1>
  <p class="sub">Most voice-agent demos show a cherry-picked call. VoiceForge shows the <b>failure
  distribution</b>: deterministic signals → blind human labels → calibrated judge → call phenotypes → an improvement queue.</p>
  <div class="cards">${cards}</div>
  ${cal?'':gated('Calibration pending — requires ≥'+D.floor+' blind binary labels and the quarantined judge run. Nothing is faked while it waits.')}
  <div class="split"><div class="panel"><h2 style="margin-top:0">Failure phenotypes <span class="mono">(single-rater exploratory)</span></h2>
  ${Object.keys(neg).length?bars(neg,''):'<div class="kv">pending blind labels</div>'}</div>
  <div class="panel"><h2 style="margin-top:0">Call archetypes <span class="mono">(derived deterministically)</span></h2>
  ${Object.keys(arch).length?bars(arch,'b'):'<div class="kv">derived once labels exist</div>'}</div></div>
  <h2>Deterministic failure events <span class="mono">(signal hits — NOT failed calls)</span></h2>
  <div class="panel">${bars(Object.fromEntries((A.failure_clusters||[]).map(c=>[c.dimension,c.count])),'')}</div>
  ${calblock()}`;
}
function calblock(){
  const cal=D.report.calibration; if(!cal) return '';
  const cm=cal.confusion;
  return `<h2>Human ↔ judge calibration</h2><div class="panel">
  <div class="kv">raw agreement <b>${cal.raw_agreement}</b> · Cohen's κ <b>${cal.kappa}</b>
  (bootstrap 95% CI ${cal.ci95[0]}–${cal.ci95[1]}) · n=<b>${cal.n}</b></div>
  <table style="max-width:430px;margin-top:10px"><tr><th></th><th>judge: success</th><th>judge: fail</th></tr>
  <tr><td><b>human: success</b></td><td>${cm['h_success|j_success']||0}</td><td>${cm['h_success|j_fail']||0}</td></tr>
  <tr><td><b>human: fail</b></td><td>${cm['h_fail|j_success']||0}</td><td>${cm['h_fail|j_fail']||0}</td></tr></table>
  <div class="kv" style="margin-top:8px">disagreements: ${cal.disagreements.map(d=>`<span class="mono">${d}</span>`).join(', ')||'none'}</div></div>`;
}
function callsView(){
  if(!D.gate_open) return `<h1>Calls</h1>`+gated(`Per-call rows are hidden until blind labeling completes
  (${D.val.binary}/${D.floor} binary) — prevents anchoring on heuristic outcomes mid-labeling. Regenerate after labels.`);
  const q=(window.__q||'').toLowerCase();
  const rows=D.rows.filter(r=>!q||r.id.includes(q)||r.lang.includes(q)||r.profile.includes(q)||r.wf.includes(q));
  return `<h1>Calls <span class="mono">(${rows.length})</span></h1>
  <input class="search" placeholder="filter: id, language, profile, workflow…" value="${window.__q||''}"
   oninput="window.__q=this.value;render()">
  <div class="panel" style="padding:6px 8px"><table><tr><th>call</th><th>src</th><th>lang</th><th>profile</th>
  <th>turns</th><th>outcome*</th><th>overall</th><th></th></tr>
  ${rows.map((r,i)=>`<tr class="row" onclick="detail='${r.id}';render()"><td class="mono">${r.id}</td>
  <td>${r.source}</td><td>${r.lang}</td><td><span class="pill ${r.profile==='unmeasured'?'um':'man'}">${r.profile}</span></td>
  <td>${r.turns}</td><td><span class="pill ${r.outcome?'ok':'no'}">${r.outcome?'completed':'not completed'}</span></td>
  <td>${fmt(r.overall)}</td><td class="mono">→</td></tr>`).join('')}</table></div>
  <div class="kv" style="margin-top:8px">*outcome = HEURISTIC keyword task-completion, not gold · overall = weighted mean over PRESENT dims</div>`;
}
function detailView(id){
  const r=D.rows.find(x=>x.id===id); if(!r) return callsView();
  const dims=r.dims.map(d=>`<div class="dim"><span>${d.name} <span class="mono">${d.type}</span></span>
  <span style="text-align:right"><span class="sc">${fmt(d.score)}</span><div class="rs">${d.reason}</div></span></div>`).join('');
  const jd=r.judge? r.judge.dims.map(d=>`<div class="dim"><span>${d.name} <span class="mono">judge · ${d.provenance}</span></span>
  <span style="text-align:right"><span class="sc">${fmt(d.score)}</span><div class="rs">${d.reason}</div></span></div>`).join('')
   + `<div class="dim"><span>outcome <span class="mono">judge · ${r.judge.binary.provenance}</span></span>
  <span style="text-align:right"><span class="sc">${r.judge.binary.label}</span><div class="rs">${r.judge.binary.reason}</div></span></div>`
  : '<div class="kv">judge output pending (quarantined until blind labels)</div>';
  return `<span class="crumb" onclick="detail=null;render()">← all calls</span>
  <h1 class="mono" style="font-size:18px">${r.id}</h1>
  <div class="kv">${r.source} · ${r.lang} · ${r.profile} · ${r.wf} · ${r.turns} turns ·
  <span class="pill ${r.outcome?'ok':'no'}">${r.outcome?'completed':'not completed'} (heuristic)</span></div>
  <div class="split" style="margin-top:16px"><div class="panel" style="max-height:560px;overflow:auto">
  ${r.transcript.map(t=>`<div class="msg ${t.s}"><div class="who">${t.s}</div><div class="bub">${t.x||'<i>(silence)</i>'}</div></div>`).join('')}
  </div><div><div class="panel"><h2 style="margin-top:0">Deterministic scorecard</h2>${dims}</div>
  <div class="panel" style="margin-top:14px"><h2 style="margin-top:0">Semantic judge</h2>${jd}</div>
  ${r.failures.length?`<div class="panel" style="margin-top:14px"><h2 style="margin-top:0">Failure events</h2>
  ${r.failures.map(f=>`<div class="dim"><span>${f.dimension} · ${f.label}</span><span class="rs">${f.detail}</span></div>`).join('')}</div>`:''}
  </div></div>`;
}
function clustersView(){
  const A=D.analytics,R=D.report;
  const arch=Object.fromEntries(Object.entries(R.archetypes.counts).filter(([,v])=>v));
  return `<h1>Failure clusters</h1>
  <p class="sub">Two lenses: deterministic failure EVENTS (timestamp math — these are signal hits, not failed calls)
  and phenotype ARCHETYPES (derived from blind labels — ${R.archetypes.derivation}).</p>
  <div class="split"><div class="panel"><h2 style="margin-top:0">Deterministic events</h2>
  ${bars(Object.fromEntries((A.failure_clusters||[]).map(c=>[c.dimension,c.count])),'')}
  <div class="kv" style="margin-top:8px">${(A.failure_clusters||[]).map(c=>`<div><span class="mono">${c.dimension}</span>: e.g. ${c.example_call_ids.slice(0,3).join(', ')}</div>`).join('')}</div></div>
  <div class="panel"><h2 style="margin-top:0">Labeled archetypes</h2>
  ${Object.keys(arch).length?bars(arch,'b'):'<div class="kv">pending blind labels</div>'}
  <div class="kv" style="margin-top:10px">co-occurring tags: ${(R.tags.co_occurrence_top||[]).map(x=>`<span class="mono">${x.pair.join(' + ')}</span> ×${x.n}`).join(' · ')||'—'}</div></div></div>
  <h2>By stress profile</h2><div class="panel"><table><tr><th>profile</th><th>n</th><th>success*</th><th>cost/success†</th></tr>
  ${(A.by_stress_profile||[]).map(b=>`<tr><td>${b.stress_profile}</td><td>${b.n}</td><td>${fmt(b.success_rate)}</td>
  <td>${b.cost_per_successful_call==null?'n/a':'$'+fmt(b.cost_per_successful_call)}</td></tr>`).join('')}</table>
  <div class="kv" style="margin-top:6px">*heuristic · †estimated, prototype</div></div>`;
}
function queueView(){
  const Q=D.report.improvement_queue||[];
  return `<h1>Improvement queue</h1>
  <p class="sub">Evidence-backed: every entry traces to a blind-labeled call and its observed tags.
  Recommendations are template-derived from tags — engineering backlog, not vibes.</p>
  ${Q.length?Q.map(q=>`<div class="rec"><b class="mono">${q.call_id}</b> · ${q.human} · <i>${q.archetype.replace(/_/g,' ')}</i>
  <div class="why">evidence: ${q.evidence_tags.join(', ')}</div><div class="fix">→ ${q.recommendation}</div></div>`).join('')
  :gated('Built from labeled calls carrying negative tags — pending blind labels.')}`;
}
function render(){
  document.querySelectorAll('nav a').forEach(a=>a.classList.toggle('on',a.dataset.v===view));
  $('#main').innerHTML = detail?detailView(detail):
    {overview,calls:callsView,clusters:clustersView,queue:queueView}[view]();
  window.scrollTo(0,0);
}
window.detail=null; render();
"""


def active_css():
    """Claude-design skin drop-in: if web/dashboard_skin.css exists it RE PLACES the built-in CSS
    (same DOM contract — classes documented in the design prompt). Delete the file to revert."""
    skin = ROOT / "web" / "dashboard_skin.css"
    if skin.exists() and skin.read_text().strip():
        return skin.read_text(), "skin: web/dashboard_skin.css"
    return CSS, "skin: built-in"


def render(data):
    jr = data["judge_run"]
    gate_note = ("labels complete — full per-call drill-down" if data["gate_open"] else
                 f"blind labeling in progress ({data['val']['binary']}/{data['floor']} binary) — "
                 "per-call rows hidden to protect blindness")
    jr_note = (f"judge run: {jr['model']} · t={jr['temperature']} · {jr['n_calls']} calls · "
               f"{jr['failures']} failures" if jr else "judge: quarantined (no real-call output yet)")
    css, _ = active_css()
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>VoiceForge — eval lab</title>
<style>{css}</style></head><body><div class="shell">
<nav><div class="logo">Voice<b>Forge</b></div><div class="tag">eval lab for voice agents</div>
<a data-v="overview" onclick="nav('overview')">◈ Overview</a>
<a data-v="calls" onclick="nav('calls')">☰ Calls</a>
<a data-v="clusters" onclick="nav('clusters')">⌬ Failure clusters</a>
<a data-v="queue" onclick="nav('queue')">↗ Improvement queue</a>
<div class="gatechip">{H.escape(gate_note)}<br><br>{H.escape(jr_note)}</div></nav>
<main><div id="main"></div>
<div class="foot">every number traces to a committed artifact · heuristic = keyword task-completion ·
estimated = public per-unit prices · uncalibrated = judge before kappa · failure events ≠ failed calls ·
single-rater tags are exploratory · generated offline, no network</div></main></div>
<script>window.__DATA__ = {json.dumps(data)};</script>
<script>{JS}</script></body></html>"""


def main():
    data = build()
    out = OUT / "dashboard.html"
    out.write_text(render(data))
    _, skin = active_css()
    print(f"wrote out/dashboard.html — gate_open={data['gate_open']} "
          f"({data['val']['binary']}/{data['floor']} binary), rows embedded: {len(data['rows'])}, "
          f"judge: {'present' if data['judge_run'] else 'pending'} · {skin}")


if __name__ == "__main__":
    main()
