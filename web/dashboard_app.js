const D = window.__DATA__;
const $ = s => document.querySelector(s);
const esc = x => String(x ?? "").replace(/[&<>"']/g, c => (
  {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]
));
const fmt = x => x == null ? "—" : (typeof x === "number" ? (Number.isInteger(x) ? x : x.toFixed(3)) : x);
const pct = x => x == null ? "—" : Math.round(x * 100) + "%";
const money = x => x == null ? "—" : "$" + Number(x).toFixed(x < 0.1 ? 3 : 2);
const pretty = x => String(x || "").replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
const prov = (kind, label) => `<span class="prov ${kind}">${label}</span>`;

let view = "overview";
let detail = null;
let demoOpen = false;
let demoStep = -1;

function nav(v) {
  view = v;
  detail = null;
  render();
}

function openCall(id) {
  view = "calls";
  detail = id;
  render();
}

function bars(obj, cls = "") {
  const entries = Object.entries(obj || {});
  const max = Math.max(1, ...entries.map(([, value]) => value));
  return entries.map(([key, value]) => `
    <div class="bar">
      <span class="bl" title="${esc(key)}">${esc(pretty(key))}</span>
      <span class="bar-track"><span class="bf ${cls}" style="width:${Math.max(3, 100 * value / max)}%"></span></span>
      <b>${value}</b>
    </div>`).join("");
}

function gated(message) {
  return `<div class="pending">${message}</div>`;
}

function pipeline() {
  const cal = D.report.calibration;
  const stages = [
    ["Measured", `${D.analytics.n_calls} calls · timing on ${D.analytics.timing_coverage.timed}`],
    ["Human-labeled", `${D.val.binary} binary · ${D.val.unsure} unsure`],
    ["Judge-calibrated", cal ? `κ ${cal.kappa} · n=${cal.n}` :
      (D.judge_run ? `${D.judge_run.status} · ${D.judge_run.n_calls}/46 calls` : "pending")],
    ["Phenotyped", `${Object.values(D.report.archetypes.counts).reduce((a, b) => a + b, 0)} labeled calls`],
    ["Prioritized", `${(D.report.improvement_queue || []).length} candidate fixes`],
  ];
  return `<div class="pipeline">${stages.map(([title, subtitle], index) =>
    `${index ? '<span class="flow">→</span>' : ""}
    <div class="stage"><div class="st">${title}</div><div class="ss">${subtitle}</div></div>`).join("")}</div>`;
}

function toggleEvidence() {
  $("#evidence-list")?.classList.toggle("open");
}

function sponsorBlock() {
  const proof = D.sponsor_proof;
  return `<section class="section" id="sponsor">
    <article class="panel">
      <div class="section-head"><h2>Bolna × Cartesia proof chain</h2>
        ${proof ? prov("measured", "Cached configuration proof") : prov("not-observed", "Proof unavailable")}
      </div>
      <div class="sponsor-flow">
        <div class="sponsor-node">Bolna agent<small>orchestration</small></div><span>→</span>
        <div class="sponsor-node">Cartesia synthesizer
          <small>${proof ? `${esc(proof.cartesia_voice)} · ${esc(proof.cartesia_model)}` : "configured inside Bolna"}</small>
        </div><span>→</span>
        <div class="sponsor-node">Cached execution<small>offline replay</small></div><span>→</span>
        <div class="sponsor-node final">VoiceForge evaluation<small>provider-neutral</small></div>
      </div>
      <p class="kv" style="margin:12px 0 0">Cartesia runs inside the Bolna agent’s synthesizer configuration.
      VoiceForge evaluates cached artifacts; the demo requires no live Cartesia API.</p>
    </article>
  </section>`;
}

function calibrationBlock() {
  const cal = D.report.calibration;
  if (!cal) {
    return gated(D.judge_run ?
      `Binary calibration is pending a complete judged run. Current status: ${D.judge_run.status}, ${D.judge_run.n_calls}/46 calls.` :
      "Binary calibration is pending the complete judged run.");
  }
  const cm = cal.confusion;
  const cell = (key, agree, human, judge) => `<div class="cell ${agree ? "agree" : "disagree"}">
    <div class="cv">${cm[key] || 0}</div><div class="cl">human ${human} · judge ${judge}</div></div>`;
  return `<section class="section" id="calibration">
    <div class="section-head"><h2>Human ↔ judge calibration</h2>
      <span class="hint">The dedicated binary outcome judgment only.</span></div>
    ${cal.caption ? `<p class="kappa-note reveal">${esc(cal.caption)}</p>` : ""}
    <div class="split">
      <div class="panel"><div class="cmx">
        <div></div><div class="ax">judge: success</div><div class="ax">judge: fail</div>
        <div class="ax side">human: success</div>
        ${cell("h_success|j_success", true, "success", "success")}
        ${cell("h_success|j_fail", false, "success", "fail")}
        <div class="ax side">human: fail</div>
        ${cell("h_fail|j_success", false, "fail", "success")}
        ${cell("h_fail|j_fail", true, "fail", "fail")}
      </div></div>
      <div class="panel"><div class="kstats">
        <div class="kstat"><div class="kv2 num">${cal.kappa}</div><div class="kl">Cohen’s κ</div>
          <div class="kv">bootstrap 95% CI ${cal.ci95[0]}–${cal.ci95[1]}</div></div>
        <div class="kstat"><div class="kv2 num">${pct(cal.raw_agreement)}</div><div class="kl">Raw agreement</div>
          <div class="kv">n=${cal.n} blind binary labels</div></div>
      </div><p class="kv">Disagreements, where not to trust the judge:</p>
      <div>${cal.disagreements.map(id => `<button class="btn" onclick="openCall('${esc(id)}')">${esc(id)}</button>`).join(" ") || "none"}</div>
      </div>
    </div>
  </section>`;
}

function overview() {
  const R = D.report;
  const P = R.product || {};
  const F = P.fix_first;
  const mx = P.matrix || {};
  const n = mx.n || 1;
  const quadrants = [
    ["seamless", "Seamless success", mx.seamless_success || 0, "Completed without labeled friction."],
    ["recovered", "Recovered success", mx.recovered_success || 0, "Friction occurred; the agent recovered and completed."],
    ["brittle", "Brittle success", mx.brittle_success || 0, "Completed, but one or more negative phenotypes remained."],
    ["failure", "Failure", mx.failure || 0, "Goal not completed in the blind human label."],
  ];
  const band = quadrants.map(([id, label, count]) =>
    `<span class="seg ${id}" style="width:${100 * count / n}%" title="${label}: ${count}"></span>`).join("");
  const quadCards = quadrants.map(([id, label, count, definition]) => `
    <article class="quad ${id === "brittle" ? "hot" : ""}">
      <div class="qh"><span>${label}</span><span>${Math.round(100 * count / n)}%</span></div>
      <div class="qc num">${count} <small>calls</small></div>
      <p class="qd">${definition}</p>
      <div class="dots">${Array.from({length: count}, () => `<span class="dot ${id}"></span>`).join("")}</div>
    </article>`).join("");

  const fixFirst = F ? `<section class="section reveal" id="fix-first">
    <div class="section-head"><h2>What to fix first</h2>
      <span class="hint">Ranked by estimated cost exposure in the frozen labeled slice</span></div>
    <article class="spotlight">
      <div class="spot-grid"><div>${prov("human", "Human-labeled")}
        <h3 class="spot-title">${pretty(F.phenotype_id)}</h3>
        <div class="spot-stats">
          <div class="spot-stat"><div class="v num">${F.affected_calls}</div><div class="l">affected calls</div></div>
          <div class="spot-stat"><div class="v num">${money(F.estimated_spend_usd)}</div><div class="l">estimated affected spend</div></div>
          <div class="spot-stat"><div class="v num">≈${money(F.modeled_exposure_per_1k_usd)}</div><div class="l">modeled / 1,000 calls</div></div>
        </div></div>
        <div class="spot-copy"><h3>Recommended change</h3><p class="action">${esc(F.recommendation || "Human review required.")}</p>
          <h3>Expected mechanism</h3><p>${esc(F.expected_mechanism || "Validate on a held-out replay before claiming lift.")}</p>
        </div>
      </div>
      <div class="spot-foot"><button class="btn evidence" onclick="toggleEvidence()">View affected calls</button>
        ${prov("exploratory", "Needs human review")} ${prov("estimated", "Modeled, not observed savings")}</div>
      <div class="evidence-list" id="evidence-list">${F.evidence_call_ids.map(id =>
        `<button onclick="openCall('${esc(id)}')">${esc(id)}</button>`).join("")}</div>
    </article>
  </section>` : "";

  const T = R.metric_trap;
  const metricTrap = T ? `<section class="section reveal" id="metric-trap">
    <div class="section-head"><h2>The metric trap</h2>
      <span class="hint">Does the completion heuristic agree with the blind human label?</span></div>
    <article class="spotlight trap">
      <div class="spot-grid">
        <div>${prov("estimated", "Heuristic vs blind labels")}
          <h3 class="spot-title">A success-rate dashboard is blind where it costs.</h3>
          <div class="spot-stats">
            <div class="spot-stat"><div class="v num">${T.agree}/${T.n}</div><div class="l">heuristic agrees with human</div></div>
            <div class="spot-stat"><div class="v num">${T.missed_successes}</div><div class="l">real successes it missed</div></div>
            <div class="spot-stat"><div class="v num">${T.false_passes}/${T.human_failures}</div><div class="l">real failures it passed</div></div>
          </div></div>
        <div class="spot-copy"><p class="action">${esc(T.caption)}</p></div>
      </div>
    </article>
  </section>` : "";

  const cal = R.calibration;
  const metrics = [
    ["Human-confirmed success", pct(P.human_success_rate), `${P.human_successes || 0} success · ${P.human_failures || 0} fail`, "human", "Human-labeled", ""],
    ["Brittle success share", pct(P.brittle_share_of_successes), `${mx.brittle_success || 0} of ${P.human_successes || 0} successes`, "human", "Human-labeled", "flag"],
    ["Human ↔ judge agreement", cal ? `κ ${cal.kappa}` : "Pending",
      cal ? `${pct(cal.raw_agreement)} raw · n=${cal.n}` :
        (D.judge_run ? `${D.judge_run.status} · ${D.judge_run.n_calls}/46 calls` : "judge run absent"),
      "judge", cal ? "Binary calibrated" : "Not yet calibrated", ""],
    ["Cost / confirmed success", money(P.cost_per_human_success_est),
      `all binary-call spend ÷ ${P.human_successes || 0} successes`, "estimated", "Estimated prototype", ""],
  ].map(([label, value, detailText, kind, provenance, cls]) => `
    <article class="card metric ${cls}"><span class="label">${label}</span><span class="value num">${value}</span>
      <span class="detail">${detailText}</span>${prov(kind, provenance)}</article>`).join("");

  return `${D.fixture ? '<div class="pending">Synthetic fixture preview. Do not demo this file.</div>' : ""}
    <section class="hero reveal" id="thesis"><div class="eyebrow">Voice-agent evaluation · deterministic first · evidence on every judgment</div>
      <h1><span class="muted">Success rate tells you whether calls finished.</span>
      VoiceForge tells you how they finished, what failures cost, and what to fix first.</h1></section>
    ${metricTrap}
    ${fixFirst}
    <section class="section"><div class="metrics">${metrics}</div></section>
    <section class="section reveal" id="matrix"><div class="section-head"><h2>Success × Friction</h2>
      <span class="hint">Why one success-rate number is not enough · n=${mx.n || 0} binary labels · ${mx.unsure_excluded || 0} unsure excluded</span></div>
      <article class="matrix-card"><div class="band">${band}</div><div class="quads">${quadCards}</div></article></section>
    <section class="section reveal" id="pipeline"><div class="section-head"><h2>Evaluation pipeline</h2>
      <span class="hint">Every number traces to a committed stage.</span></div>${pipeline()}</section>
    <section class="section split">
      <article class="panel"><div class="section-head"><h2>Failure phenotypes</h2>${prov("exploratory", "Single-rater")}</div>
        ${bars(R.tags.negative)}</article>
      <article class="panel"><div class="section-head"><h2>Call archetypes</h2>${prov("human", "Derived")}</div>
        ${bars(Object.fromEntries(Object.entries(R.archetypes.counts).filter(([, value]) => value)), "blue")}</article>
    </section>
    ${calibrationBlock()}${sponsorBlock()}`;
}

function callsView() {
  if (!D.gate_open) return `<h1>Calls</h1>` + gated(`Per-call rows remain hidden until blind labeling completes.`);
  const query = (window.__q || "").toLowerCase();
  const rows = D.rows.filter(row => !query || [row.id, row.lang, row.profile, row.wf, row.source].some(x => String(x).toLowerCase().includes(query)));
  return `<section class="hero"><div class="eyebrow">Evidence explorer</div><h1>Calls <span class="mono">(${rows.length})</span></h1>
    <p class="sub">Open any call to compare the blind human outcome, deterministic measurements, semantic diagnostics, and cited transcript turns.</p></section>
    <input class="search" placeholder="Filter by ID, language, profile, workflow…" value="${esc(window.__q || "")}"
      oninput="window.__q=this.value;render()">
    <div class="panel" style="padding:6px 8px;overflow:auto"><table><tr><th>call</th><th>source</th><th>lang</th><th>profile</th>
      <th>turns</th><th>human</th><th>heuristic*</th><th>overall</th><th></th></tr>
      ${rows.map(row => `<tr class="row" onclick="openCall('${esc(row.id)}')"><td class="mono">${esc(row.id)}</td>
        <td>${esc(row.source)}</td><td>${esc(row.lang)}</td><td><span class="pill ${row.profile === "unmeasured" ? "um" : "man"}">${esc(row.profile)}</span></td>
        <td>${row.turns}</td><td>${row.human ? `<span class="pill ${row.human.label === "success" ? "ok" : row.human.label === "fail" ? "no" : "um"}">${row.human.label}</span>` : "—"}</td>
        <td><span class="pill ${row.outcome ? "ok" : "no"}">${row.outcome ? "completed" : "not completed"}</span></td>
        <td>${fmt(row.overall)}</td><td>→</td></tr>`).join("")}
    </table></div><p class="kv">*Heuristic keyword task-completion, not gold. Overall is the weighted mean over present dimensions.</p>`;
}

function dimensionRow(dimension, kind) {
  const ids = JSON.stringify(dimension.evidence_turn_ids || []);
  return `<div class="dim" onclick='highlightEvidence(${ids})'>
    <div class="dim-head"><span>${pretty(dimension.name)} ${prov(kind === "judge" ? "exploratory" : "measured",
      kind === "judge" ? "Uncalibrated diagnostic" : "Deterministic")}</span><span class="sc">${fmt(dimension.score)}</span></div>
    <div class="rs">${esc(dimension.reason)} · click to highlight evidence</div></div>`;
}

function detailView(id) {
  const row = D.rows.find(item => item.id === id);
  if (!row) return callsView();
  const deterministic = row.dims.map(d => dimensionRow(d, "deterministic")).join("");
  const judged = row.judge ? row.judge.dims.map(d => dimensionRow(d, "judge")).join("") +
    `<div class="dim" onclick='highlightEvidence(${JSON.stringify(row.judge.binary.evidence_turn_ids || [])})'>
      <div class="dim-head"><span>Binary outcome ${prov("judge", "Compared with human")}</span>
      <span class="sc">${row.judge.binary.label}</span></div><div class="rs">${esc(row.judge.binary.reason)}</div></div>` :
    `<div class="kv">Judge output pending or incomplete for this call.</div>`;
  const human = row.human ? `<div class="panel"><div class="section-head"><h2>Blind human label</h2>
      ${prov("human", row.human.confidence + " confidence")}</div><p class="kv"><b>${row.human.label}</b><br>
      ${row.human.negative.map(pretty).join(" · ") || "No negative phenotype"}<br>
      <span class="muted">${row.human.positive.map(pretty).join(" · ")}</span></p></div>` : "";
  return `<button class="btn" onclick="detail=null;render()">← All calls</button>
    <section class="hero" style="padding-bottom:16px"><div class="eyebrow">Call detail · evidence-cited</div>
      <h1 class="mono" style="font-size:22px">${esc(row.id)}</h1><p class="sub">${esc(row.source)} · ${esc(row.lang)} ·
      ${esc(row.profile)} · ${esc(row.wf)} · ${row.turns} turns</p></section>
    <div class="detail-grid"><div class="panel transcript">${row.transcript.map(turn =>
      `<div class="msg ${turn.s}" data-turn="${esc(turn.id)}"><div class="who">${esc(turn.id)} · ${esc(turn.s)}</div>
      <div class="bub">${esc(turn.x) || "<i>(silence)</i>"}</div></div>`).join("")}</div>
      <div>${human}<div class="panel"><div class="section-head"><h2>Deterministic scorecard</h2>${prov("measured", "Measured")}</div>
        ${deterministic}</div><div class="panel"><div class="section-head"><h2>Semantic judge</h2>${prov("exploratory", "5 dims uncalibrated")}</div>
        ${judged}</div>${row.failures.length ? `<div class="panel"><h2>Failure events</h2>${row.failures.map(f =>
          `<div class="dim"><div class="dim-head"><span>${pretty(f.dimension)} · ${esc(f.label)}</span></div>
          <div class="rs">${esc(f.detail)}</div></div>`).join("")}</div>` : ""}</div>
    </div>`;
}

function highlightEvidence(ids) {
  document.querySelectorAll(".msg.evidence").forEach(node => node.classList.remove("evidence"));
  ids.forEach(id => document.querySelector(`[data-turn="${CSS.escape(id)}"]`)?.classList.add("evidence"));
  document.querySelector(".msg.evidence")?.scrollIntoView({behavior:"smooth", block:"center"});
}

function clustersView() {
  const A = D.analytics;
  const R = D.report;
  return `<section class="hero"><div class="eyebrow">Failure intelligence</div><h1>Failures have shapes.</h1>
    <p class="sub">Timestamp-derived events and human-labeled phenotypes are shown separately so signal hits are never mistaken for failed calls.</p></section>
    <div class="split"><article class="panel"><div class="section-head"><h2>Deterministic events</h2>${prov("measured","Signal hits")}</div>
      ${bars(Object.fromEntries((A.failure_clusters || []).map(cluster => [cluster.dimension, cluster.count])))}</article>
      <article class="panel"><div class="section-head"><h2>Labeled archetypes</h2>${prov("human","Derived")}</div>
      ${bars(Object.fromEntries(Object.entries(R.archetypes.counts).filter(([, value]) => value)), "blue")}</article></div>
    <article class="panel"><div class="section-head"><h2>By stress profile</h2>${prov("estimated","Prototype cost")}</div>
      <table><tr><th>profile</th><th>n</th><th>heuristic success</th><th>cost / success</th></tr>
      ${(A.by_stress_profile || []).map(item => `<tr><td>${pretty(item.stress_profile)}</td><td>${item.n}</td>
        <td>${pct(item.success_rate)}</td><td>${item.cost_per_successful_call == null ? "Not observed" : money(item.cost_per_successful_call)}</td></tr>`).join("")}
      </table></article>`;
}

function queueView() {
  const queue = D.report.improvement_queue || [];
  return `<section class="hero"><div class="eyebrow">From evidence to engineering backlog</div><h1>Improvement queue</h1>
    <p class="sub">Each candidate fix traces to a blind-labeled phenotype. Recommendations are template-derived and require human review; no lift is promised.</p></section>
    ${queue.length ? queue.map(item => `<article class="rec" onclick="openCall('${esc(item.call_id)}')" style="cursor:pointer">
      <b class="mono">${esc(item.call_id)}</b> · ${esc(item.human)} · <i>${pretty(item.archetype)}</i>
      <div class="why">evidence: ${item.evidence_tags.map(pretty).join(", ")}</div>
      <div class="fix">→ ${esc(item.recommendation)}</div></article>`).join("") : gated("No evidence-backed queue entries.")}`;
}

function methodView() {
  const P = D.report.product || {};
  const run = D.judge_run;
  return `<section class="hero"><div class="eyebrow">Method and provenance</div>
    <h1>Trust each claim by knowing how it was produced.</h1>
    <p class="sub">VoiceForge separates measured signals, blind human labels, calibrated binary judgments,
    uncalibrated semantic diagnostics, and estimated prototype costs.</p></section>
    ${sponsorBlock()}
    <section class="section split"><article class="panel"><h2>Current judge run</h2><p class="kv">
      ${run ? `${esc(run.model)} · status ${run.status} · ${run.n_calls}/46 calls · ${run.failures} failures` : "No judge artifact"}<br>
      rubric <span class="mono">${run?.rubric_hash || "—"}</span><br>prompt <span class="mono">${run?.judge_prompt_hash || "—"}</span></p></article>
      <article class="panel"><h2>Honest limits</h2><p class="kv">${esc(P.caveat || "Costs are estimates and labels are single-rater.")}<br>
      Timing is omitted for text-only calls, never fabricated. Semantic dimensions remain uncalibrated diagnostics.</p></article></section>`;
}

const demoSteps = [
  ["Overview", "overview", "#thesis"],
  ["What to fix first", "overview", "#fix-first"],
  ["Success × Friction", "overview", "#matrix"],
  ["Calibration", "overview", "#calibration"],
  ["Call evidence", "calls", null],
  ["Improvement queue", "queue", null],
  ["Sponsor proof", "method", "#sponsor"],
];

function toggleDemo() {
  demoOpen = !demoOpen;
  $("#demo-panel").classList.toggle("open", demoOpen);
  if (demoOpen && demoStep < 0) goDemo(0);
}

function goDemo(index) {
  demoStep = Math.max(0, Math.min(demoSteps.length - 1, index));
  const [label, targetView, selector] = demoSteps[demoStep];
  view = targetView;
  detail = null;
  render();
  setTimeout(() => {
    const element = selector ? document.querySelector(selector) : $("#main");
    element?.scrollIntoView({behavior:"smooth", block:"start"});
    element?.classList.add("target-ring");
    setTimeout(() => element?.classList.remove("target-ring"), 1900);
    $("#demo-current").textContent = `${demoStep + 1}. ${label}`;
  }, 0);
}

function render() {
  document.querySelectorAll("nav a").forEach(link => link.classList.toggle("on", link.dataset.v === view));
  $("#main").innerHTML = detail ? detailView(detail) :
    ({overview, calls:callsView, clusters:clustersView, queue:queueView, method:methodView}[view]());
  window.scrollTo(0, 0);
}

document.addEventListener("keydown", event => {
  if (!demoOpen) return;
  if (event.key === "Escape") toggleDemo();
  if (event.key === "ArrowRight") goDemo(demoStep + 1);
  if (event.key === "ArrowLeft") goDemo(demoStep - 1);
});

window.detail = null;
render();
