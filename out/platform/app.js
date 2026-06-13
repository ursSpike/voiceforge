(function(){
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

function updateSelectedHighlight(){
  document.querySelectorAll(".call-card").forEach(function(el){
    el.classList.toggle("sel", el.querySelector(".cid") && el.querySelector(".cid").textContent.indexOf(state.selected) >= 0);
  });
}

/* Session calls — live executions fetched via /api/fetch_execution this browser session.
   Persisted in localStorage so the demo can compare multiple calls and refresh-safely. */
var SESSION_KEY = "vf_session_calls";
function loadSession(){
  try { return JSON.parse(localStorage.getItem(SESSION_KEY) || "[]"); }
  catch(e) { return []; }
}
function saveSession(arr){
  try { localStorage.setItem(SESSION_KEY, JSON.stringify(arr.slice(-30))); } catch(e){}
}
function pushSessionCall(d){
  var arr = loadSession();
  // upsert by execution_id
  var idx = arr.findIndex(function(x){ return x.execution_id === d.execution_id; });
  var entry = {
    execution_id: d.execution_id,
    turns: d.turns || [],
    signals: d.signals || null,
    judge: d.judge || null,
    extracted_data: d.extracted_data || null,
    cost_breakdown: d.cost_breakdown || null,
    fetched_at: new Date().toISOString(),
  };
  if (idx >= 0) arr[idx] = entry; else arr.push(entry);
  saveSession(arr);
}
function sessionCallsAsRail(){
  return loadSession().map(function(e){
    var j = e.judge || {};
    var outcome = j.outcome === "success" ? true : j.outcome === "fail" ? false : null;
    var lat = (e.signals && e.signals.latency) || {};
    return {
      id: "live_" + e.execution_id.slice(0,8),
      _exec: e.execution_id,
      source: "bolna_live", lang: "hi-en", profile: "clinic",
      wf: "appointment_booking", turns: (e.signals && e.signals.n_turns) || e.turns.length,
      outcome: outcome, overall: null, in_manifest: false, live: true,
      archetype: outcome===false ? (j.reason ? "judge_flagged_failure" : null) : (lat.n_over_800ms > 0 ? "slow_response" : null),
      recommendation: j.reason || null,
      human: null, dims: [], failures: [],
      transcript: e.turns.map(function(t,i){ return {id:"t"+(i+1), s:t.role==="user"?"user":"agent", x:t.text}; }),
      judge: { binary: outcome!=null ? { label: outcome?"success":"fail", reason: j.reason||"", evidence_turn_ids: j.evidence_turn_ids||[] } : {} },
      provenance: "LIVE · UNCALIBRATED · session=browser",
      fix_first_evidence: false,
      _session: true, _raw: e,
    };
  });
}

function activeCalls(){
  if (state.mode !== "live") return CALLS;
  // Combine: any pre-baked live_calls.json entries + this-session fetched executions.
  var base = liveCalls();
  var sess = sessionCallsAsRail();
  // de-dup by execution prefix
  var baseExecPrefixes = new Set(base.map(function(c){ return (c.id||"").replace("bolna_live_",""); }));
  return base.concat(sess.filter(function(c){ return !baseExecPrefixes.has(c._exec.slice(0,8)); }));
}

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
      list.appendChild(clinicCallTriggerCard());      // tester's first action — pin to TOP
      var metrics = sessionMetricsCard();
      if(metrics) list.appendChild(metrics);
      list.appendChild(clinicAgentCard());
      list.appendChild(clinicKbCard());
    } else {
      var hint=el("div","live-empty");
      hint.style.borderStyle="solid";
      hint.innerHTML='<h3>Live · uncalibrated</h3><p>These calls were ingested today. No human label or kappa applies yet — treat scores as diagnostic only.</p>';
      list.appendChild(hint);
    }
  }
  // Hide rail search/filters in tester mode (live + clinic sidecar present) — they don't need to filter.
  var searchEl = document.getElementById("search");
  var filtersEl = document.getElementById("filters");
  if(searchEl && filtersEl){
    var testerMode = (state.mode==="live" && CLINIC);
    searchEl.style.display = testerMode ? "none" : "";
    filtersEl.style.display = testerMode ? "none" : "";
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
    card.onclick=function(){
      // Session calls re-render via renderLiveExecution from cache (no network).
      if(c._session && c._raw){ renderLiveExecution(c._raw); state.selected=c.id; updateSelectedHighlight(); return; }
      state.selected=c.id; render();
    };
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
/* Session metrics — aggregates over calls fetched in this browser session. */
function sessionMetricsCard(){
  var sess = loadSession();
  if(!sess.length) return null;
  var n = sess.length;
  var nSuccess = 0, nFail = 0, nUnknown = 0;
  var latencies = [];
  var totalTurns = 0, totalDur = 0, nDur = 0;
  sess.forEach(function(e){
    var j = e.judge || {};
    if(j.outcome === "success") nSuccess++;
    else if(j.outcome === "fail") nFail++;
    else nUnknown++;
    var lat = e.signals && e.signals.latency || {};
    if(lat.median_ms != null) latencies.push(lat.median_ms);
    if(e.signals && typeof e.signals.n_turns === "number") totalTurns += e.signals.n_turns;
    if(e.signals && e.signals.duration_s != null){ totalDur += e.signals.duration_s; nDur++; }
  });
  var latLabel = latencies.length
    ? Math.round(latencies.reduce(function(a,b){return a+b;},0) / latencies.length) + " ms"
    : "—";
  var avgTurns = n ? Math.round(totalTurns/n*10)/10 : 0;
  var avgDur = nDur ? Math.round(totalDur/nDur*10)/10 + "s" : "—";
  var rate = n ? Math.round(nSuccess/(nSuccess+nFail || 1)*100) : 0;
  return htmlEl(
    '<div class="cl-card cl-metrics">'+
      '<div class="cl-head"><span class="cl-kicker">Your test session</span><span class="cl-prov uncal">UNCALIBRATED</span></div>'+
      '<div class="cl-title">'+n+' call'+(n===1?"":"s")+' this session</div>'+
      '<div class="cl-meta">'+
        '<div><span class="cl-k">judge outcome</span><span class="cl-v"><span class="pill ok">'+nSuccess+' ok</span> <span class="pill bad">'+nFail+' fail</span>'+(nUnknown?' <span class="pill uncal">'+nUnknown+' pending</span>':"")+'</span></div>'+
        '<div><span class="cl-k">avg latency</span><span class="cl-v">'+esc(latLabel)+'</span></div>'+
        '<div><span class="cl-k">avg duration</span><span class="cl-v">'+esc(avgDur)+'</span></div>'+
        '<div><span class="cl-k">avg turns</span><span class="cl-v">'+esc(avgTurns)+'</span></div>'+
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

/* ---------- live-call trigger card (operator-backend only — graceful on static Pages) ---------- */
function clinicCallTriggerCard(){
  var el = htmlEl(
    '<div class="cl-card cl-trigger">'+
      '<div class="cl-head"><span class="cl-kicker">Test the agent</span><span class="cl-prov uncal">LIVE</span></div>'+
      '<div class="cl-title">Aarav · Aarogya Clinic appointment scheduler</div>'+
      '<ol class="cl-steps">'+
        '<li>Type your phone with <code>+91…</code> below.</li>'+
        '<li>Tap <b>Call my phone</b> · your phone rings in ~10s.</li>'+
        '<li>Try one: book a blood test · switch English↔Hindi mid-call · ask for medical advice (the agent must refuse and offer a consultation).</li>'+
        '<li>Hang up. Open this call from the list to see transcript, extracted fields, signals, and judge evidence.</li>'+
      '</ol>'+
      '<input class="cl-input" id="cl-phone" type="tel" placeholder="+91 98765 43210" autocomplete="off">'+
      '<button class="cl-btn" id="cl-start">Call my phone</button>'+
      '<div class="cl-status" id="cl-status" hidden></div>'+
    '</div>'
  );
  // Wire the button after insertion (the htmlEl returns a node already; the listeners attach immediately).
  setTimeout(function(){ wireCallTrigger(); }, 0);
  return el;
}

function wireCallTrigger(){
  var btn = document.getElementById("cl-start");
  var input = document.getElementById("cl-phone");
  var status = document.getElementById("cl-status");
  if(!btn || !input || !status) return;
  function show(html, kind){
    status.hidden = false;
    status.className = "cl-status " + (kind || "");
    status.innerHTML = html;
  }
  btn.onclick = async function(){
    var phone = (input.value || "").trim();
    if(!phone){ show("Enter a phone number first.", "err"); return; }
    btn.disabled = true;
    show("Starting call…", "info");
    try {
      var r = await fetch("/api/start_call", {
        method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify({phone: phone})
      });
      if(r.status === 503){
        show("Live trigger needs the operator backend (BOLNA_API_KEY). " +
             "This static page only renders calls — to actually start one, run the local " +
             "<code>pipeline/serve_surface.py</code> from the operator console. " +
             "<a href=\"https://github.com/ursSpike/voiceforge#start-the-platform-locally\" target=\"_blank\">how</a>", "warn");
        btn.disabled = false;
        return;
      }
      var data = await r.json();
      if(!r.ok || !data.execution_id){
        show("Could not start: " + esc(data.error || ("HTTP "+r.status)) + (data.detail?" — "+esc(data.detail).slice(0,140):""), "err");
        btn.disabled = false;
        return;
      }
      var execId = data.execution_id;
      show('Call queued · exec <span class="mono">'+esc(execId)+'</span> · your phone should ring shortly. After you hang up, ingest the result below (works locally; on the deployed site it prints the command to run).', "ok");
      var go = document.createElement("button");
      go.className = "cl-btn cl-btn-secondary";
      go.textContent = "See call results";
      go.onclick = async function(){
        go.disabled = true;
        show("Fetching call results…", "info");
        try {
          // On Netlify (prod): fetch + render inline.
          var rf = await fetch("/api/fetch_execution", {
            method: "POST", headers: {"Content-Type":"application/json"},
            body: JSON.stringify({execution_id: execId})
          });
          if(rf.ok){
            var df = await rf.json();
            renderLiveExecution(df);
            var nturns = (df.turns||[]).length;
            if(nturns === 0){
              show('Bolna still processing the call log — click <b>See call results</b> again in a few seconds.', "warn");
            } else {
              pushSessionCall(df);                // persist this fetch in the rail
              show('Loaded '+nturns+' turns. Saved to <b>Session calls</b> in the rail.', "ok");
              renderRail();                       // pull the new call into the list
            }
            go.disabled = false;
            return;
          }
          // Localhost fallback: full ingest+judge.
          var r2 = await fetch("/api/ingest_and_judge", {
            method: "POST", headers: {"Content-Type":"application/json"},
            body: JSON.stringify({execution_id: execId})
          });
          if(r2.status === 404){
            show('Ingest runs locally. Paste in your terminal:<br><code>python pipeline/ingest_live.py --execution '+esc(execId)+' &amp;&amp; python pipeline/judge_live.py</code><br>Then refresh this page.', "warn");
            return;
          }
          var d2 = await r2.json();
          if(!r2.ok || !d2.ok){
            show("Pipeline failed: " + esc(d2.error || ("HTTP "+r2.status)) + ". Try again or run locally.", "err");
            go.disabled = false;
            return;
          }
          show("Done. Reloading workspace…", "ok");
          setTimeout(function(){ location.reload(); }, 800);
        } catch(e){
          show("Could not fetch results: " + esc(String(e)).slice(0,140), "err");
          go.disabled = false;
        }
      };
      // Append the button as a SIBLING of status (status.innerHTML rewrites would otherwise destroy it).
      if(status.parentNode) status.parentNode.appendChild(go);
    } catch(e){
      show("Live trigger backend not reachable on this host (static GitHub Pages).<br>" +
           "On stage Spike runs <code>serve_surface.py</code> locally — clone + run to try.", "warn");
      btn.disabled = false;
    }
  };
}

/* ---------- inline render of a freshly-fetched live execution (no ingest pipeline needed) ---------- */
function renderLiveExecution(d){
  var main = document.getElementById("main");
  if(!main) return;
  var turns = (d.turns || []).map(function(t){
    var who = t.role === "user" ? "user" : "agent";
    var label = who === "user" ? "USER" : "AARAV";
    return '<div class="turn '+who+'"><div class="who">'+label+'</div><div class="bubble">'+esc(t.text)+'</div></div>';
  }).join("");
  if(!turns){
    turns = '<div class="placeholder">No turns in /log yet — Bolna may still be processing. Click <b>See call results</b> again in a few seconds.</div>';
  }
  var extracted = "";
  if(d.extracted_data && typeof d.extracted_data === "object"){
    var rows = [];
    Object.keys(d.extracted_data).forEach(function(cat){
      var fields = d.extracted_data[cat] || {};
      Object.keys(fields).forEach(function(name){
        var f = fields[name] || {};
        var val = f.subjective || f.objective || "—";
        var conf = f.confidence_label || (f.confidence != null ? Math.round(f.confidence*100)+"%" : "");
        rows.push('<div class="ex-row"><div class="ex-k">'+esc(name)+'</div><div class="ex-v">'+esc(String(val))+'</div><div class="ex-c">'+esc(conf)+'</div></div>');
      });
    });
    if(rows.length){
      extracted = '<div class="section"><h2>Extracted fields <span class="cl-prov uncal">FROM BOLNA</span></h2><div class="ex-grid">'+rows.join("")+'</div></div>';
    }
  }
  var signalsHtml = "";
  if(d.signals){
    var s = d.signals;
    var lat = s.latency || {};
    signalsHtml =
      '<div class="section"><h2>Deterministic signals <span class="cl-prov ok">MEASURED</span></h2>'+
        '<div class="ex-grid">'+
          '<div class="ex-row"><div class="ex-k">turns</div><div class="ex-v">'+esc(s.n_turns)+'</div><div class="ex-c"></div></div>'+
          '<div class="ex-row"><div class="ex-k">duration</div><div class="ex-v">'+(s.duration_s!=null?esc(s.duration_s)+' s':"—")+'</div><div class="ex-c"></div></div>'+
          '<div class="ex-row"><div class="ex-k">median latency</div><div class="ex-v">'+(lat.median_ms!=null?esc(lat.median_ms)+' ms':"—")+'</div><div class="ex-c">'+esc(lat.n_gaps||0)+' gaps</div></div>'+
          '<div class="ex-row"><div class="ex-k">p90 latency</div><div class="ex-v">'+(lat.p90_ms!=null?esc(lat.p90_ms)+' ms':"—")+'</div><div class="ex-c">'+esc(lat.n_over_800ms||0)+' over 800ms</div></div>'+
          '<div class="ex-row"><div class="ex-k">barge-in</div><div class="ex-v unmeasured">not observed (Bolna /log has no overlap signal)</div><div class="ex-c"></div></div>'+
        '</div>'+
      '</div>';
  }
  var judgeHtml = "";
  var fixHtml = "";
  if(d.judge){
    var j = d.judge;
    if(j.outcome){
      var verdict = j.outcome === "success" ? "ok" : "bad";
      judgeHtml =
        '<div class="section"><h2>Judge evidence <span class="cl-prov uncal">UNCALIBRATED</span></h2>'+
          '<div class="rec"><div class="rh">OUTCOME</div><div class="rt"><span class="pill '+verdict+'">'+esc(j.outcome.toUpperCase())+'</span> '+esc(j.reason||"")+'</div>'+
          (j.evidence_turn_ids && j.evidence_turn_ids.length ? '<div class="prov" style="margin-top:8px;border-top:0;padding-top:0">cited turns: '+esc(j.evidence_turn_ids.join(", "))+'</div>' : "")+
          '<div class="prov" style="margin-top:6px;border-top:0;padding-top:0">'+esc(j.provenance||"uncalibrated · live")+'</div>'+
          '</div>'+
        '</div>';
      // Auto-derived improvement recommendation — surfaced only for failures + slow-latency successes.
      var rec = "";
      var lat = (d.signals && d.signals.latency) || {};
      if(j.outcome === "fail" && j.reason){
        rec = '<b>The agent didn\'t complete the task.</b> ' + esc(j.reason) +
              ' <br><i>Likely prompt fix:</i> tighten the conversation-path block for this branch; ensure the agent confirms partial info before changing topic.';
      } else if(j.outcome === "success" && lat.n_over_800ms > 1){
        rec = '<b>Task succeeded but with friction:</b> ' + esc(lat.n_over_800ms) + ' response gaps over 800ms (slow).'+
              ' <br><i>Likely fix:</i> shorten system-prompt scaffolding, lower max-tokens cap, reduce KB top-k.';
      } else if(j.outcome === "success") {
        rec = 'Clean call. No prompt change recommended yet — re-test with a harder scenario (mid-call language switch, vague date, medical-advice probe).';
      }
      if(rec){
        fixHtml = '<div class="section"><h2>Improvement recommendation <span class="cl-prov uncal">auto-derived</span></h2>'+
                    '<div class="rec" style="border-color:var(--ember);background:var(--ember-soft)"><div class="rh">FIX FIRST</div><div class="rt">'+rec+'</div></div>'+
                  '</div>';
      }
    } else {
      var msg = j.skipped || j.pending || j.error || JSON.stringify(j).slice(0,140);
      judgeHtml = '<div class="section"><h2>Judge evidence <span class="cl-prov uncal">UNCALIBRATED</span></h2><p class="caption" style="margin:0;border:0;padding:0">'+esc(msg)+'</p></div>';
    }
  }
  var cost = "";
  if(d.cost_breakdown){
    var c = d.cost_breakdown;
    cost = '<div class="section"><h2>Cost breakdown</h2><pre class="json-mini">'+esc(JSON.stringify(c, null, 2)).slice(0,800)+'</pre></div>';
  }
  main.innerHTML =
    '<div class="view-wrap">'+
      '<h1 class="view-title">Your call '+esc(d.execution_id.slice(0,8))+'…</h1>'+
      '<p class="subtitle">Live · <b>LIVE · UNCALIBRATED</b>. Reconstructed from Bolna /log + Bolna extractions + a live Gemini judge — uncalibrated diagnostics only.</p>'+
      '<div class="grid2">'+
        '<div class="section"><h2>Transcript</h2><div class="transcript">'+turns+'</div></div>'+
        '<div>'+fixHtml+signalsHtml+judgeHtml+extracted+cost+'</div>'+
      '</div>'+
    '</div>';
  // scroll to it so the tester sees the result instantly
  main.scrollIntoView({behavior:"smooth", block:"start"});
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
