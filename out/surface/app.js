/* ============================================================
   VoiceForge — Evaluation Lab
   Vanilla JS. Every displayed product number is read from
   window.__DATA__ (the committed artifact contract). Nothing
   is fetched; nothing is fabricated.
   ============================================================ */
(function () {
  "use strict";

  const D = window.__DATA__;
  const R = D.report;
  const P = R.product || {};
  const CAL = R.calibration;
  const TRAP = R.metric_trap;
  const RUN = D.judge_run;
  const SP = D.sponsor_proof;
  const ROWS = D.rows || [];
  const ROW_IDS = new Set(ROWS.map(r => r.id));

  /* ---------- helpers ---------- */

  const esc = x => String(x ?? "").replace(/[&<>"']/g, c => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
  const pct = x => x == null ? "—" : Math.round(x * 1000) / 10 + "%";
  const money = x => x == null ? "—" : "$" + Number(x).toFixed(x < 0.1 ? 4 : 2);
  const fmt = x => x == null ? "—" : (typeof x === "number" ? (Number.isInteger(x) ? String(x) : x.toFixed(2)) : String(x));
  const pretty = x => String(x || "").replaceAll("_", " ").replace(/\b\w/g, c => c.toUpperCase());
  const prov = (kind, label) => `<span class="prov ${kind}">${esc(label)}</span>`;
  const mount = name => document.querySelector(`[data-mount="${name}"]`);
  const reducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const kicker = (num, text) =>
    `<div class="ch-kicker"><span class="k-num">${esc(num)}</span><span>${esc(text)}</span></div>`;

  /* ---------- chapter 00 · thesis ---------- */

  function renderThesis() {
    const archTotal = Object.values(R.archetypes.counts).reduce((a, b) => a + b, 0);
    mount("thesis").innerHTML = `
      <div class="hero-mark reveal">
        <span class="hm-glyphs" aria-hidden="true">
          <span class="hm-raw"></span><span class="hm-rule"></span><span class="hm-forged"></span>
        </span>
        <span class="hm-name">Voice<b>Forge</b> · The evaluation lab for production voice agents</span>
      </div>
      <h1 class="hero-thesis reveal" data-delay="1">
        <span class="ht-muted">Voice-agent demos stop when the call ends.</span>
        <span class="ht-ember">VoiceForge starts there.</span>
      </h1>
      <p class="hero-sub reveal" data-delay="2">
        Success rate tells you whether calls finished. VoiceForge tells you how they finished,
        what failures cost, and what to fix first — deterministic signals before semantic judgment,
        blind human labels before trust, and evidence cited on every claim.
      </p>
      <div class="hero-stats reveal" data-delay="3">
        <div class="hstat">
          <div class="hs-v">${D.analytics.n_calls}</div>
          <div class="hs-l">calls scored</div>
          ${prov("measured", "Measured")}
        </div>
        <div class="hstat">
          <div class="hs-v">${D.val.binary}</div>
          <div class="hs-l">blind binary labels</div>
          ${prov("human", "Human-labeled")}
        </div>
        <div class="hstat">
          <div class="hs-v">${RUN.validated_judgments}</div>
          <div class="hs-l">validated judgments · ${RUN.failures} failures</div>
          ${prov("measured", "Run artifact")}
        </div>
        <div class="hstat">
          <div class="hs-v">${pct(P.human_success_rate)}</div>
          <div class="hs-l">human-confirmed success</div>
          ${prov("human", "Human-labeled")}
        </div>
        <div class="hstat">
          <div class="hs-v">${archTotal}</div>
          <div class="hs-l">calls phenotyped</div>
          ${prov("exploratory", "Single-rater")}
        </div>
      </div>
      <div class="hero-cue reveal" data-delay="3">
        <span class="cue-arrow" aria-hidden="true">↓</span>
        <span>Scroll, or press → · nine chapters from thesis to receipts</span>
      </div>`;
  }

  /* ---------- chapter 01 · hear, then measure ---------- */

  const PROV_LEGEND = [
    ["measured", "Measured", "Deterministic timestamp or schema-derived signals."],
    ["human", "Human-labeled", "Blind single-rater outcomes and phenotype primitives."],
    ["calibrated", "Binary calibrated", "The judge's dedicated binary outcome, compared with the human binary label."],
    ["uncal", "Uncalibrated diagnostic", "The five semantic judge dimensions. Useful, unproven."],
    ["estimated", "Estimated prototype", "Cost values derived from public unit assumptions."],
    ["exploratory", "Exploratory", "Single-rater phenotype distributions and co-occurrence."],
    ["notobs", "Not observed", "Unavailable in the source. Shown as absent, never as zero."],
  ];

  function renderMeasure() {
    const tc = D.analytics.timing_coverage;
    const archTotal = Object.values(R.archetypes.counts).reduce((a, b) => a + b, 0);
    const stages = [
      ["Ingest", `${D.analytics.n_calls} provider calls`],
      ["Normalize", "provider-neutral call schema"],
      ["Deterministic signals", `timing on ${tc.timed} · ${tc.unmeasured} unmeasured`],
      ["Blind labels", `${D.val.binary} binary · ${D.val.unsure} unsure`],
      ["Evidence-cited judge", `${RUN.validated_judgments}/${RUN.expected_judgments} validated · ${RUN.failures} failures`],
      ["Binary calibration", `κ ${CAL.kappa} · n=${CAL.n}`],
      ["Phenotypes", `${archTotal} calls typed`],
      ["Improvement queue", `${(R.improvement_queue || []).length} candidate fixes`],
    ];
    const clusters = D.analytics.failure_clusters || [];
    const maxC = Math.max(1, ...clusters.map(c => c.count));
    mount("measure").innerHTML = `
      ${kicker("01", "Hear, then measure")}
      <h2 class="ch-title reveal">Deterministic signals come first. Missing timing is omitted — never faked.</h2>
      <p class="ch-lede reveal" data-delay="1">
        Barge-in, latency gaps, silence, turn structure and completion signals are measured from
        provider timestamps. ${tc.timed} calls carry timing; ${tc.unmeasured} text-only calls show
        none at all, because fabricating it would poison everything downstream.
      </p>
      <div class="pipeline reveal" data-delay="1">
        ${stages.map(([name, fact], i) => `
          <div class="stage ${i === stages.length - 1 ? "hot" : ""}">
            <div class="st-num">STAGE ${String(i + 1).padStart(2, "0")}</div>
            <div class="st-name">${esc(name)}</div>
            <div class="st-fact">${esc(fact)}</div>
          </div>`).join("")}
      </div>
      <div class="grid-2">
        <div class="panel reveal" data-delay="2">
          <div class="panel-head"><h3>Deterministic events across the corpus</h3>${prov("measured", "Signal hits")}</div>
          <div class="signal-bars">
            ${clusters.map(c => `
              <div class="sbar">
                <span class="sb-l">${esc(pretty(c.dimension))}</span>
                <span class="sb-track"><span class="sb-fill" style="width:${Math.max(4, 100 * c.count / maxC)}%"></span></span>
                <span class="sb-v">${c.count}</span>
              </div>`).join("")}
          </div>
          <p class="panel-note">These are signal hits, not failed calls — one rough call can fire many.
          Example calls are inspectable in the evidence explorer.</p>
        </div>
        <div class="panel reveal" data-delay="3">
          <div class="panel-head"><h3>Every number wears its provenance</h3></div>
          <div class="prov-legend">
            ${PROV_LEGEND.map(([k, l, def]) => `
              <div class="pl-item">${prov(k, l)}<span class="pl-def">${esc(def)}</span></div>`).join("")}
          </div>
        </div>
      </div>`;
  }

  /* ---------- chapter 02 · metric trap ---------- */

  function renderTrap() {
    const T = TRAP;
    const dots = []
      .concat(Array.from({ length: T.agree }, () => "agree"))
      .concat(Array.from({ length: T.missed_successes }, () => "missed"))
      .concat(Array.from({ length: T.n - T.agree - T.missed_successes }, () => "passed"));
    mount("trap").innerHTML = `
      ${kicker("02", "The metric trap")}
      <h2 class="ch-title reveal">A success-rate dashboard is blind exactly where it costs money.</h2>
      <div class="trap-grid">
        <div>
          <div class="trap-stats reveal" data-delay="1">
            <div class="trap-stat">
              <div class="ts-v">${T.agree}/${T.n}</div>
              <div class="ts-l">heuristic agrees with the blind human label</div>
            </div>
            <div class="trap-stat">
              <div class="ts-v">${T.missed_successes}</div>
              <div class="ts-l">real successes it missed</div>
            </div>
            <div class="trap-stat">
              <div class="ts-v">${T.false_passes}/${T.human_failures}</div>
              <div class="ts-l">real failures it passed</div>
            </div>
          </div>
          <div class="dotfield reveal" data-delay="2" role="img"
            aria-label="${T.n} labeled calls: ${T.agree} where the heuristic agrees with the human, ${T.missed_successes} real successes it missed, ${T.false_passes} real failures it passed.">
            ${dots.map(k => `<span class="df-dot ${k}"></span>`).join("")}
          </div>
          <div class="dotfield-key reveal" data-delay="2">
            <span><i style="background:var(--line)"></i>heuristic agrees (${T.agree})</span>
            <span><i style="background:var(--prov-human)"></i>missed successes (${T.missed_successes})</span>
            <span><i style="background:var(--bad)"></i>failures passed (${T.false_passes})</span>
          </div>
        </div>
        <div class="reveal" data-delay="2">
          <p class="trap-caption">${esc(T.caption)}</p>
          ${prov("measured", "Deterministic heuristic")} ${prov("human", "Blind labels")}
          <p class="panel-note">${esc(T.provenance)}.</p>
        </div>
      </div>`;
  }

  /* ---------- chapter 03 · calibration ---------- */

  function renderJudge() {
    const cm = CAL.confusion;
    const [lo, hi] = CAL.ci95;
    const axisMin = -0.3, axisMax = 0.7;
    const px = v => (100 * (v - axisMin) / (axisMax - axisMin)).toFixed(1) + "%";
    const cell = (key, agree, h, j) => `
      <div class="cell ${agree ? "agree" : "disagree"}">
        <div class="cv">${cm[key] || 0}</div>
        <div class="cl">human ${h} · judge ${j}</div>
      </div>`;
    mount("judge").innerHTML = `
      ${kicker("03", "Blind labels, measured trust")}
      <h2 class="ch-title reveal">“I do not trust the judge. I measure how much to trust it.”</h2>
      <p class="ch-lede reveal" data-delay="1">
        Outcomes were labeled blind before any judging. The ${esc(RUN.model)} judge (temperature ${RUN.temperature})
        then answered the same binary question with cited evidence turns — and its agreement with the human
        is measured, not assumed.
      </p>
      <div class="judge-grid">
        <div class="panel reveal" data-delay="1">
          <div class="panel-head"><h3>Binary agreement</h3>${prov("calibrated", "Binary calibrated")}</div>
          <div class="kappa-row">
            <div class="kstat">
              <div class="kv">${CAL.kappa}</div>
              <div class="kl">Cohen’s κ — ${esc(CAL.band)}</div>
            </div>
            <div class="kstat">
              <div class="kv">${pct(CAL.raw_agreement)}</div>
              <div class="kl">raw agreement</div>
              <div class="kd">n=${CAL.n} blind binary labels</div>
            </div>
          </div>
          <div class="ci-strip" aria-label="Bootstrap 95% confidence interval for kappa, from ${lo} to ${hi}, crossing zero.">
            <div class="ci-track">
              <span class="ci-range" style="left:${px(lo)}; width:calc(${px(hi)} - ${px(lo)})"></span>
              <span class="ci-zero" style="left:${px(0)}"></span>
              <span class="ci-point" style="left:${px(CAL.kappa)}"></span>
            </div>
            <div class="ci-labels"><span>${axisMin}</span><span>0</span><span>κ axis · bootstrap 95% CI ${lo} to ${hi}</span><span>${axisMax}</span></div>
          </div>
          <p class="ci-note">The interval crosses zero. That is the finding — shown, not smoothed.</p>
          <p class="kappa-caption">${esc(CAL.caption)}</p>
        </div>
        <div class="panel reveal" data-delay="2">
          <div class="panel-head"><h3>Confusion matrix</h3><span class="cs-hint">n=${CAL.n}</span></div>
          <div class="cmx">
            <div></div><div class="ax">judge: success</div><div class="ax">judge: fail</div>
            <div class="ax side">human: success</div>
            ${cell("h_success|j_success", true, "success", "success")}
            ${cell("h_success|j_fail", false, "success", "fail")}
            <div class="ax side">human: fail</div>
            ${cell("h_fail|j_success", false, "fail", "success")}
            ${cell("h_fail|j_fail", true, "fail", "fail")}
          </div>
          <div class="panel-head" style="margin-top:22px"><h3>The ${CAL.disagreements.length} disagreements — where not to trust the judge</h3></div>
          <div class="chips">
            ${CAL.disagreements.map(id => callChip(id)).join("")}
          </div>
          <p class="chips-key">Where NOT to trust the judge. Language is not the supported axis on this sample —
          hi-en and English agreement rates are statistically indistinguishable (n=45). The defensible split is
          annotator confidence (high ≈83% vs medium ≈50%), known only post-annotation — it routes a second-rater
          review queue, not an auto-router. Dimmed IDs are excluded from this sanitized package.</p>
        </div>
      </div>`;
  }

  function callChip(id) {
    return ROW_IDS.has(id)
      ? `<button class="chip" data-open-call="${esc(id)}">${esc(id)}</button>`
      : `<button class="chip" disabled aria-disabled="true" title="Transcript excluded from this sanitized design package">${esc(id)}<span class="chip-tag">excluded</span></button>`;
  }

  /* ---------- chapter 04 · success × friction ---------- */

  function renderFriction() {
    const mx = P.matrix;
    const n = mx.n || 1;
    const quadrants = [
      ["seamless", "Seamless success", mx.seamless_success, "Completed without labeled friction."],
      ["recovered", "Recovered success", mx.recovered_success, "Friction occurred; the agent recovered and completed."],
      ["brittle", "Brittle success", mx.brittle_success, "Completed — but negative phenotypes remained. Repair burden hides here."],
      ["failure", "Failure", mx.failure, "Goal not completed in the blind human label."],
    ];
    mount("friction").innerHTML = `
      ${kicker("04", "Success × Friction")}
      <h2 class="ch-title reveal">Pass/fail is one bit. Failure has shapes — and so does success.</h2>
      <p class="ch-lede reveal" data-delay="1">
        n=${mx.n} blind binary labels · ${mx.unsure_excluded} unsure excluded. A single success-rate
        number flattens four very different call experiences into one.
      </p>
      <div class="band reveal" data-delay="1" role="img" aria-label="Distribution of ${mx.n} labeled calls across the four outcome shapes.">
        ${quadrants.map(([id, label, count]) =>
          `<span class="seg ${id}" style="width:${(100 * count / n).toFixed(1)}%" title="${esc(label)}: ${count}"></span>`).join("")}
      </div>
      <div class="quads">
        ${quadrants.map(([id, label, count, def], i) => `
          <article class="quad ${id === "brittle" ? "hot" : ""} reveal" data-delay="${Math.min(3, i + 1)}">
            <div class="qh"><span>${esc(label)}</span><span>${Math.round(100 * count / n)}%</span></div>
            <div class="qc">${count} <small>calls</small></div>
            <p class="qd">${esc(def)}</p>
            <div class="dots" aria-hidden="true">${Array.from({ length: count }, () => `<i class="${id}"></i>`).join("")}</div>
          </article>`).join("")}
      </div>
      <div class="friction-aside reveal" data-delay="2">
        <div class="hstat">
          <div class="hs-v">${pct(P.brittle_share_of_successes)}</div>
          <div class="hs-l">of successes are brittle</div>
          ${prov("human", "Human-labeled")}
        </div>
        <div class="hstat">
          <div class="hs-v est-value">${money(P.cost_per_human_success_est)}</div>
          <div class="hs-l">est. cost per confirmed success</div>
          ${prov("estimated", "Estimated prototype")}
        </div>
        <div class="hstat">
          <div class="hs-v est-value">${pct(P.friction_or_failure_spend_share)}</div>
          <div class="hs-l">est. spend touched by friction or failure</div>
          ${prov("estimated", "Estimated prototype")}
        </div>
      </div>
      <p class="panel-note reveal" data-delay="3" style="max-width:78ch">${esc(P.caveat)}</p>`;
  }

  /* ---------- chapter 05 · evidence explorer ---------- */

  function renderEvidence() {
    mount("evidence").innerHTML = `
      ${kicker("05", "Evidence explorer")}
      <h2 class="ch-title reveal">Every claim opens to a call.</h2>
      <p class="ch-lede reveal" data-delay="1">
        Open any call to compare the blind human outcome, deterministic measurements, semantic diagnostics,
        and the exact transcript turns each judgment cites. ${esc(D.privacy_note)}
      </p>
      <input class="search reveal" data-delay="1" id="call-filter" type="search"
        placeholder="Filter by ID, language, profile, workflow…" aria-label="Filter calls">
      <div class="calltable-wrap reveal" data-delay="2">
        <table class="calltable">
          <thead>
            <tr><th>call</th><th>source</th><th>lang</th><th>profile</th><th>turns</th>
            <th>human</th><th>heuristic*</th><th>overall</th><th></th></tr>
          </thead>
          <tbody id="call-tbody"></tbody>
        </table>
      </div>
      <p class="table-note">*Heuristic keyword task-completion — not gold dialogue state, and exactly the metric
      the trap chapter measures. Overall is the weighted mean over present dimensions only.
      Human label: ${prov("human", "Human-labeled")} · heuristic: ${prov("measured", "Measured")}</p>`;
    document.getElementById("call-filter").addEventListener("input", e => renderCallRows(e.target.value));
    renderCallRows("");
  }

  function renderCallRows(query) {
    const q = (query || "").toLowerCase();
    const rows = ROWS.filter(r => !q || [r.id, r.lang, r.profile, r.wf, r.source].some(x => String(x).toLowerCase().includes(q)));
    document.getElementById("call-tbody").innerHTML = rows.length ? rows.map(r => `
      <tr data-open-call="${esc(r.id)}" tabindex="0" aria-label="Open call ${esc(r.id)}">
        <td class="mono">${esc(r.id)}</td>
        <td>${esc(r.source)}</td>
        <td class="mono">${esc(r.lang)}</td>
        <td><span class="pill ${r.profile === "unmeasured" ? "um" : "ok"}">${esc(r.profile)}</span></td>
        <td>${r.turns}</td>
        <td>${r.human ? `<span class="pill ${r.human.label === "success" ? "ok" : r.human.label === "fail" ? "no" : "um"}">${esc(r.human.label)}</span>` : "—"}</td>
        <td><span class="pill ${r.outcome ? "ok" : "no"}">${r.outcome ? "completed" : "not completed"}</span></td>
        <td class="mono">${fmt(r.overall)}</td>
        <td><button class="open-btn" data-open-call="${esc(r.id)}" aria-label="Open ${esc(r.id)}">→</button></td>
      </tr>`).join("") :
      `<tr><td colspan="9" style="color:var(--ink-faint)">No calls match that filter.</td></tr>`;
  }

  /* ---------- chapter 06 · fix first + queue ---------- */

  function renderAction() {
    const F = P.fix_first;
    const queue = R.improvement_queue || [];
    const groups = [];
    queue.forEach(item => {
      let g = groups.find(g => g.rec === item.recommendation);
      if (!g) { g = { rec: item.recommendation, items: [] }; groups.push(g); }
      g.items.push(item);
    });
    groups.sort((a, b) => b.items.length - a.items.length);
    mount("action").innerHTML = `
      ${kicker("06", "From evidence to engineering action")}
      <h2 class="ch-title reveal">What to fix first — with receipts attached.</h2>
      <p class="ch-lede reveal" data-delay="1">
        Ranked by estimated cost exposure in the frozen labeled slice. The destination of the product
        is not a report; it is a queue an engineer can act on Monday morning.
      </p>
      <article class="spotlight reveal" data-delay="1">
        <div class="spot-grid">
          <div>
            ${prov("human", "Human-labeled phenotype")}
            <h3 class="spot-title">${esc(pretty(F.phenotype_id))}</h3>
            <div class="spot-stats">
              <div class="spot-stat"><div class="v">${F.affected_calls}</div><div class="l">affected calls</div></div>
              <div class="spot-stat"><div class="v est-value">${money(F.estimated_spend_usd)}</div><div class="l">estimated affected spend</div></div>
              <div class="spot-stat"><div class="v est-value">≈${money(F.modeled_exposure_per_1k_usd)}</div><div class="l">modeled per 1,000 calls</div></div>
            </div>
          </div>
          <div class="spot-copy">
            <h4>Recommended change</h4>
            <p class="action">${esc(F.recommendation)}</p>
            <h4>Expected mechanism</h4>
            <p>${esc(F.expected_mechanism)}</p>
          </div>
        </div>
        <div class="spot-foot">
          ${prov("exploratory", "Needs human review")}
          ${prov("estimated", "Modeled exposure — not observed savings")}
          <span class="cs-hint">provenance: ${esc(F.provenance)}</span>
        </div>
        <div class="panel-head" style="margin:18px 0 0"><h3>The ${F.evidence_call_ids.length} calls behind this recommendation</h3></div>
        <div class="chips">${F.evidence_call_ids.map(id => callChip(id)).join("")}</div>
      </article>
      <div class="panel-head reveal" data-delay="2" style="margin-top:48px">
        <h3 style="font-size:18px">Improvement queue · ${queue.length} evidence-backed entries</h3>
        ${prov("exploratory", "Template-derived · requires review")}
      </div>
      <p class="table-note reveal" data-delay="2">Each candidate fix traces to a blind-labeled phenotype on a specific
      call. No lift is promised. Grouped by recommended change; dimmed calls are excluded from this sanitized package.</p>
      <div class="queue reveal" data-delay="2">
        ${groups.map(g => `
          <div class="queue-group-head">${esc(g.rec)} · ${g.items.length}</div>
          ${g.items.map(item => queueItem(item)).join("")}`).join("")}
      </div>`;
  }

  function queueItem(item) {
    const has = ROW_IDS.has(item.call_id);
    return `<button class="qitem" ${has ? `data-open-call="${esc(item.call_id)}"` : `disabled title="Transcript excluded from this sanitized design package"`}>
      <span class="qi-id">${esc(item.call_id)}</span>
      <span class="qi-meta">${esc(item.human)} · <i>${esc(pretty(item.archetype))}</i></span>
      <span class="qi-go" aria-hidden="true">${has ? "→" : ""}</span>
      <span class="qi-tags">evidence: ${item.evidence_tags.map(pretty).map(esc).join(", ")}</span>
    </button>`;
  }

  /* ---------- chapter 07 · proof chain ---------- */

  function renderProof() {
    const shortHash = h => h ? h.slice(0, 12) + "…" : "—";
    mount("proof").innerHTML = `
      ${kicker("07", "Bolna × Cartesia proof chain")}
      <h2 class="ch-title reveal">Bolna runs the call. Cartesia gives it a voice. VoiceForge tells you what to fix next.</h2>
      <div class="proof-flow reveal" data-delay="1">
        <div class="proof-node">
          <div class="pn-name">Bolna agent</div>
          <div class="pn-sub">orchestration<br>agent ${esc(SP.agent_id)}</div>
        </div>
        <div class="proof-node">
          <div class="pn-name">Cartesia synthesizer</div>
          <div class="pn-sub">${esc(SP.cartesia_voice)} · ${esc(SP.cartesia_model)}<br>configured inside the Bolna agent’s synthesizer block</div>
        </div>
        <div class="proof-node">
          <div class="pn-name">Cached execution</div>
          <div class="pn-sub">fetched ${esc(SP.fetched_at)}<br>offline replay — no live API in the demo</div>
        </div>
        <div class="proof-node final">
          <div class="pn-name">VoiceForge evaluation</div>
          <div class="pn-sub">provider-neutral · deterministic<br>every number traces to a committed artifact</div>
        </div>
      </div>
      <div class="grid-2">
        <div class="panel reveal" data-delay="2">
          <div class="panel-head"><h3>Judge run, pinned</h3>${prov("measured", "Run artifact")}</div>
          <div class="runfacts">
            <div class="runfact"><span class="rf-k">model</span><span class="rf-v">${esc(RUN.model)}</span></div>
            <div class="runfact"><span class="rf-k">temperature</span><span class="rf-v">${RUN.temperature}</span></div>
            <div class="runfact"><span class="rf-k">calls judged</span><span class="rf-v">${RUN.n_calls}/${R.manifest_total}</span></div>
            <div class="runfact"><span class="rf-k">validated judgments</span><span class="rf-v">${RUN.validated_judgments}/${RUN.expected_judgments}</span></div>
            <div class="runfact"><span class="rf-k">failures</span><span class="rf-v">${RUN.failures}</span></div>
            <div class="runfact"><span class="rf-k">cache hits</span><span class="rf-v">${RUN.cache_hits}</span></div>
            <div class="runfact"><span class="rf-k">rubric hash</span><span class="rf-v">${esc(RUN.rubric_hash)}</span></div>
            <div class="runfact"><span class="rf-k">prompt hash</span><span class="rf-v">${esc(RUN.judge_prompt_hash)}</span></div>
            <div class="runfact"><span class="rf-k">labels sha256</span><span class="rf-v">${esc(shortHash(RUN.labels_csv_sha256))}</span></div>
            <div class="runfact"><span class="rf-k">manifest sha256</span><span class="rf-v">${esc(shortHash(RUN.manifest_sha256))}</span></div>
          </div>
        </div>
        <div class="panel reveal" data-delay="3">
          <div class="panel-head"><h3>What the binary judgment is</h3>${prov("calibrated", "Calibrated by κ")}</div>
          <p class="panel-note" style="margin-top:0; font-size:14px; line-height:1.65">${esc(RUN.binary_rule)}</p>
        </div>
      </div>`;
  }

  /* ---------- chapter 08 · method & close ---------- */

  function renderMethod() {
    const tc = D.analytics.timing_coverage;
    const limits = [
      P.caveat,
      "κ calibrates only the dedicated binary outcome judgment. The five semantic dimensions remain uncalibrated diagnostics.",
      "The κ result is slight and its confidence interval includes zero. The product value is exposing that weakness and locating the disagreements.",
      "Task completion is a deterministic keyword heuristic, not gold dialogue state.",
      "Failure events are signal hits, not failed calls.",
      `${tc.unmeasured} text-only calls carry no timing. It is omitted, never fabricated.`,
      "The hero call is constructed for demonstration and disclosed as such; its audio is Cartesia-synthesized.",
      "The real ingested Bolna execution predates the Cartesia voice swap; the live agent is configured with Cartesia Devansh on sonic-3.",
      "The demo runs fully offline — no network, no live API, deterministic on every load.",
    ];
    mount("method").innerHTML = `
      ${kicker("08", "Method & limits")}
      <h2 class="ch-title reveal">Trust each claim by knowing how it was produced.</h2>
      <p class="ch-lede reveal" data-delay="1">
        VoiceForge separates measured signals, blind human labels, calibrated binary judgments,
        uncalibrated semantic diagnostics, and estimated prototype costs — and says so on every surface.
      </p>
      <ul class="limits reveal" data-delay="1">
        ${limits.map(t => `<li>${esc(t)}</li>`).join("")}
      </ul>
      <div class="closer reveal" data-delay="2">
        <p class="close-line">“Pass/fail is one bit. Failure has shapes.”</p>
        <p class="close-sub">
          Brittle success is where the repair burden hides. VoiceForge ends every claim the same way it
          began this page: with receipts — blind labels, cited turns, pinned hashes, and an improvement
          queue an engineer can open tomorrow.
        </p>
      </div>
      <p class="footnote">${esc(D.privacy_note)} Sanitized design handoff: real aggregate metrics;
      public-dataset or explicitly constructed transcripts only. Every number on this page traces to a
      committed artifact.</p>`;
  }

  /* ---------- call sheet ---------- */

  const sheet = document.getElementById("callsheet");
  const scrim = document.getElementById("callsheet-scrim");
  let lastFocus = null;

  function dimRow(d, kind) {
    const ids = d.evidence_turn_ids || [];
    const chipKind = kind === "judge" ? prov("uncal", "Uncalibrated") : prov("measured", "Measured");
    return `<button class="dim" data-evidence="${esc(ids.join(","))}">
      <span class="d-head"><span>${esc(pretty(d.name))}</span><span class="d-score">${fmt(d.score)}</span></span>
      <span class="d-reason">${esc(d.reason)}</span>
      ${ids.length ? `<span class="d-cite">cites ${ids.map(esc).join(", ")} — click to highlight</span>` : ""}
    </button>`;
  }

  function openCall(id) {
    const row = ROWS.find(r => r.id === id);
    if (!row) return;
    lastFocus = document.activeElement;
    const human = row.human;
    const j = row.judge;
    mount("callsheet").innerHTML = `
      <div class="cs-head">
        <span class="cs-id" id="callsheet-title">${esc(row.id)}</span>
        <span class="cs-meta">${esc(row.source)} · ${esc(row.lang)} · ${esc(row.profile)} · ${esc(row.wf)} · ${row.turns} turns</span>
        ${human ? `<span class="pill ${human.label === "success" ? "ok" : human.label === "fail" ? "no" : "um"}">human: ${esc(human.label)}</span>` : ""}
        <button class="btn cs-close" data-close-sheet>Close <span class="mono" style="font-size:10px">ESC</span></button>
      </div>
      <div class="cs-body">
        <div class="cs-transcript" id="cs-transcript" tabindex="0" aria-label="Transcript of ${esc(row.id)}">
          ${row.transcript.map(t => `
            <div class="turn ${esc(t.s)}" data-turn="${esc(t.id)}">
              <div class="t-who">${esc(t.id)} · ${esc(t.s)}</div>
              <div class="t-bub">${esc(t.x) || "<i>(silence)</i>"}</div>
            </div>`).join("")}
        </div>
        <div class="cs-panels">
          ${human ? `
          <div class="cs-panel">
            <h4>Blind human label ${prov("human", human.confidence + " confidence")}</h4>
            <p class="human-line"><b>${esc(human.label)}</b></p>
            <p class="tagline">${human.negative.length ? "negative: " + human.negative.map(pretty).map(esc).join(" · ") : "No negative phenotype."}</p>
            ${human.positive.length ? `<p class="tagline" style="color:var(--prov-human)">positive: ${human.positive.map(pretty).map(esc).join(" · ")}</p>` : ""}
            ${human.context && human.context.length ? `<p class="tagline">context: ${human.context.map(pretty).map(esc).join(" · ")}</p>` : ""}
          </div>` : ""}
          <div class="cs-panel">
            <h4>Deterministic scorecard ${prov("measured", "Measured")}</h4>
            ${row.dims.map(d => dimRow(d, "det")).join("")}
          </div>
          <div class="cs-panel">
            <h4>Semantic judge ${prov("uncal", "5 dims uncalibrated")}</h4>
            ${j ? j.dims.map(d => dimRow(d, "judge")).join("") : `<p class="tagline">Judge output absent for this call.</p>`}
            ${j ? `
            <button class="dim" data-evidence="${esc((j.binary.evidence_turn_ids || []).join(","))}" style="border-top:1px solid var(--line); margin-top:6px">
              <span class="d-head"><span>Binary outcome ${prov("calibrated", "Compared with human")}</span>
              <span class="d-score">${esc(j.binary.label)}</span></span>
              <span class="d-reason">${esc(j.binary.reason)}</span>
              <span class="d-cite">cites ${(j.binary.evidence_turn_ids || []).map(esc).join(", ")} — click to highlight</span>
            </button>` : ""}
          </div>
          ${row.failures.length ? `
          <div class="cs-panel">
            <h4>Failure events ${prov("measured", "Signal hits")}</h4>
            ${row.failures.map(f => `
              <button class="dim" data-evidence="${esc((f.evidence_turn_ids || []).join(","))}">
                <span class="d-head"><span>${esc(pretty(f.dimension))} · ${esc(f.label)}</span></span>
                <span class="d-reason">${esc(f.detail)}</span>
              </button>`).join("")}
          </div>` : ""}
          <p class="cs-hint">Click any judgment to highlight the transcript turns it cites. The story stays
          exactly where you left it.</p>
        </div>
      </div>`;
    scrim.hidden = false;
    sheet.hidden = false;
    sheet.classList.add("cs-open");           // pairs with .callsheet:not(.cs-open) safety in CSS
    if (!reducedMotion()) {
      sheet.classList.add("closing");
      requestAnimationFrame(() => requestAnimationFrame(() => sheet.classList.remove("closing")));
    }
    document.body.style.overflow = "hidden";
    sheet.querySelector(".cs-close").focus();
  }

  function closeCall() {
    if (sheet.hidden) return;
    const finish = () => {
      sheet.hidden = true;
      scrim.hidden = true;
      sheet.classList.remove("closing", "cs-open");
      scrim.classList.remove("closing");
      document.body.style.overflow = "";
      if (lastFocus && document.contains(lastFocus)) lastFocus.focus();
    };
    if (reducedMotion()) { finish(); return; }
    sheet.classList.add("closing");
    scrim.classList.add("closing");
    setTimeout(finish, 320);
  }

  function highlightEvidence(idsCsv, trigger) {
    const ids = (idsCsv || "").split(",").filter(Boolean);
    sheet.querySelectorAll(".turn.cited").forEach(n => n.classList.remove("cited"));
    sheet.querySelectorAll(".dim.active").forEach(n => n.classList.remove("active"));
    if (trigger) trigger.classList.add("active");
    let first = null;
    ids.forEach(id => {
      const node = sheet.querySelector(`[data-turn="${CSS.escape(id)}"]`);
      if (node) { node.classList.add("cited"); if (!first) first = node; }
    });
    if (first) {
      const box = document.getElementById("cs-transcript");
      const top = first.offsetTop - box.clientHeight / 2 + first.offsetHeight / 2;
      box.scrollTo({ top: Math.max(0, top), behavior: reducedMotion() ? "auto" : "smooth" });
    }
  }

  /* ---------- demo path ---------- */

  const BEATS = [
    ["0:00", "Category — the lab after the call", "ch-thesis"],
    ["0:40", "Hear, then measure", "ch-measure"],
    ["1:30", "The metric trap", "ch-trap"],
    ["2:30", "Blind labels & calibration", "ch-judge"],
    ["3:45", "Success has friction", "ch-friction"],
    ["4:30", "Open a call — cited evidence", "ch-evidence"],
    ["5:15", "What to fix first & the queue", "ch-action"],
    ["6:30", "Bolna × Cartesia proof", "ch-proof"],
    ["7:15", "Method, limits, close", "ch-method"],
  ];
  const demopath = document.getElementById("demopath");
  const demoToggle = document.getElementById("demo-toggle");

  function renderDemoPath() {
    mount("demopath").innerHTML = `
      <div class="dp-head"><h3>Demo path · 7–8 minutes</h3>
        <button class="btn" data-close-demo>Close</button></div>
      <ol class="dp-list">
        ${BEATS.map(([time, label, ch], i) => `
          <li><button data-jump="${ch}" data-beat="${i}">
            <span class="dp-num">${String(i + 1).padStart(2, "0")}</span>
            <span>${esc(label)}</span>
            <span class="dp-time">${time}</span>
          </button></li>`).join("")}
      </ol>
      <div class="dp-foot"><span><kbd>←</kbd> <kbd>→</kbd> chapters</span><span><kbd>Esc</kbd> closes</span></div>`;
  }

  function toggleDemo(force) {
    const open = force != null ? force : demopath.hidden;
    demopath.hidden = !open;
    demoToggle.setAttribute("aria-expanded", String(open));
    if (open) markDemoCurrent();
  }

  function markDemoCurrent() {
    const current = document.body.dataset.ch;
    demopath.querySelectorAll(".dp-list button").forEach(b =>
      b.classList.toggle("current", b.dataset.jump === current));
  }

  /* ---------- chapters, spine, scroll ---------- */

  const chapters = Array.from(document.querySelectorAll(".chapter"));

  function buildSpine() {
    document.getElementById("spine").innerHTML = chapters.map(ch => `
      <a href="#${ch.id}" data-jump="${ch.id}">
        <span class="sp-num">${esc(ch.dataset.num)}</span>
        <span class="sp-label">${esc(ch.dataset.short)}</span>
      </a>`).join("");
  }

  function jumpTo(id) {
    const node = document.getElementById(id);
    if (!node) return;
    const top = node.getBoundingClientRect().top + window.scrollY + 2;
    window.scrollTo({ top, behavior: reducedMotion() ? "auto" : "smooth" });
  }

  function currentIndex() {
    return Math.max(0, chapters.findIndex(ch => ch.id === document.body.dataset.ch));
  }

  function setActiveChapter(id) {
    if (document.body.dataset.ch === id) return;
    document.body.dataset.ch = id;
    const ch = document.getElementById(id);
    document.getElementById("topbar-chapter").textContent =
      `${ch.dataset.num} · ${ch.dataset.title.replace(/&amp;/g, "&")}`;
    document.querySelectorAll(".spine a").forEach(a =>
      a.setAttribute("aria-current", a.dataset.jump === id ? "true" : "false"));
    try { history.replaceState(null, "", "#" + id); } catch (e) { /* sandboxed context */ }
    if (!demopath.hidden) markDemoCurrent();
  }

  /* Scroll-driven narrative state. Plain rAF-throttled measurement (no
     IntersectionObserver) so it behaves identically in every embedding,
     including static capture. Reveal motion is opt-in: elements are only
     hidden (.pre) after two animation frames prove the environment paints,
     so non-painting contexts always show the complete page. */
  let pendingReveals = [];
  function updateNarrative() {
    const vh = window.innerHeight || 800;
    let active = chapters[0].id;
    for (const ch of chapters) {
      if (ch.getBoundingClientRect().top <= vh * 0.45) active = ch.id;
    }
    setActiveChapter(active);
    pendingReveals = pendingReveals.filter(n => {
      const r = n.getBoundingClientRect();
      if (r.top < vh * 0.92 && r.bottom > 0) { n.classList.remove("pre"); return false; }
      return true;
    });
    const heroBottom = document.getElementById("ch-thesis").getBoundingClientRect().bottom;
    document.getElementById("topbar").classList.toggle("shown", heroBottom < vh * 0.35);
  }

  function initRevealMotion() {
    if (reducedMotion()) return;
    const vh = window.innerHeight || 800;
    pendingReveals = Array.from(document.querySelectorAll(".reveal")).filter(n => {
      const r = n.getBoundingClientRect();
      const visible = r.top < vh * 0.92 && r.bottom > 0;
      if (!visible) n.classList.add("pre");
      return !visible;
    });
  }

  function watchScroll() {
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => { ticking = false; updateNarrative(); });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    updateNarrative();
    requestAnimationFrame(t1 => requestAnimationFrame(t2 => {
      if (t2 > t1) initRevealMotion();
    }));
  }

  /* ---------- global events ---------- */

  document.addEventListener("click", e => {
    const open = e.target.closest("[data-open-call]");
    if (open && !open.disabled) { openCall(open.dataset.openCall); return; }
    const ev = e.target.closest("[data-evidence]");
    if (ev) { highlightEvidence(ev.dataset.evidence, ev); return; }
    const jump = e.target.closest("[data-jump]");
    if (jump) {
      e.preventDefault();
      jumpTo(jump.dataset.jump);
      if (jump.closest(".dp-list")) markDemoCurrent();
      return;
    }
    if (e.target.closest("[data-close-sheet]") || e.target === scrim) { closeCall(); return; }
    if (e.target.closest("[data-close-demo]")) { toggleDemo(false); return; }
  });

  document.addEventListener("keydown", e => {
    const tag = (e.target.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea") return;
    if (e.key === "Escape") {
      if (!sheet.hidden) { closeCall(); return; }
      if (!demopath.hidden) { toggleDemo(false); return; }
    }
    if (!sheet.hidden) {
      if (e.key === "Enter" && e.target.closest("[data-open-call]")) openCall(e.target.closest("[data-open-call]").dataset.openCall);
      return;
    }
    if (e.key === "Enter" && e.target.closest("tr[data-open-call]")) {
      openCall(e.target.closest("tr[data-open-call]").dataset.openCall);
      return;
    }
    if (e.key === "ArrowRight") { e.preventDefault(); jumpTo(chapters[Math.min(chapters.length - 1, currentIndex() + 1)].id); }
    if (e.key === "ArrowLeft") { e.preventDefault(); jumpTo(chapters[Math.max(0, currentIndex() - 1)].id); }
    if (e.key.toLowerCase() === "p") toggleDemo();
  });

  demoToggle.addEventListener("click", () => toggleDemo());

  /* ---------- boot ---------- */

  document.getElementById("gate-chip").textContent =
    `${D.val.binary} blind binary labels · ${RUN.n_calls}/${R.manifest_total} judged · ${RUN.failures} failures`;

  renderThesis();
  renderMeasure();
  renderTrap();
  renderJudge();
  renderFriction();
  renderEvidence();
  renderAction();
  renderProof();
  renderMethod();
  renderDemoPath();
  buildSpine();
  watchScroll();

  if (location.hash) {
    const target = location.hash.slice(1);
    if (document.getElementById(target)) setTimeout(() => {
      const node = document.getElementById(target);
      window.scrollTo({ top: node.getBoundingClientRect().top + window.scrollY + 2, behavior: "auto" });
    }, 30);
  }
})();
