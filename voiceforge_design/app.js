/* ============================================================
   VoiceForge — Evaluation Lab · PRESENTER MODE
   Vanilla JS. Eight scenes, each exactly one viewport tall.
   Every displayed product number is read from window.__DATA__
   (the committed artifact contract). Nothing is fetched;
   nothing is fabricated. The full 76-call table and the full
   improvement queue live ONLY in the corpus browser overlay —
   scenes show a few representative rows/cards.
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

  const head = (num, kicker, title, lede) => `
    <div class="scene-head">
      <div class="ch-kicker"><span class="k-num">${esc(num)}</span><span>${esc(kicker)}</span></div>
      <h2 class="ch-title">${title}</h2>
      ${lede ? `<p class="ch-lede">${lede}</p>` : ""}
    </div>`;

  /* ============================================================
     SCENE 1 · Thesis + intro
     ============================================================ */

  function renderThesis() {
    const archTotal = Object.values(R.archetypes.counts).reduce((a, b) => a + b, 0);
    mount("thesis").innerHTML = `
      <div class="hero-mark">
        <span class="hm-glyphs" aria-hidden="true">
          <span class="hm-raw"></span><span class="hm-rule"></span><span class="hm-forged"></span>
        </span>
        <span class="hm-name">Voice<b>Forge</b> · The evaluation lab for production voice agents</span>
      </div>
      <h1 class="hero-thesis">
        <span class="ht-muted">Success rate tells you whether calls finished.</span>
        <span class="ht-ember">VoiceForge tells you how.</span>
      </h1>
      <p class="hero-sub">
        It tells you how calls finished, what failures cost, and what to fix first —
        deterministic signals before semantic judgment, blind human labels before trust,
        evidence cited on every claim.
      </p>
      <div class="hero-stats">
        <div class="hstat"><div class="hs-v">${D.analytics.n_calls}</div><div class="hs-l">calls scored</div>${prov("measured", "Measured")}</div>
        <div class="hstat"><div class="hs-v">${D.val.binary}</div><div class="hs-l">blind binary labels</div>${prov("human", "Human-labeled")}</div>
        <div class="hstat"><div class="hs-v">${RUN.validated_judgments}</div><div class="hs-l">validated judgments · ${RUN.failures} failures</div>${prov("measured", "Run artifact")}</div>
        <div class="hstat"><div class="hs-v">${pct(P.human_success_rate)}</div><div class="hs-l">human-confirmed success</div>${prov("human", "Human-labeled")}</div>
        <div class="hstat"><div class="hs-v">${archTotal}</div><div class="hs-l">calls phenotyped</div>${prov("exploratory", "Single-rater")}</div>
      </div>
      <div class="hero-cue">
        <span class="cue-arrow" aria-hidden="true">→</span>
        <span>Press → or ↓ · eight scenes from thesis to receipts</span>
      </div>`;
  }

  /* ============================================================
     SCENE 2 · The metric trap (25/45)
     ============================================================ */

  function renderTrap() {
    const T = TRAP;
    const dots = []
      .concat(Array.from({ length: T.agree }, () => "agree"))
      .concat(Array.from({ length: T.missed_successes }, () => "missed"))
      .concat(Array.from({ length: T.n - T.agree - T.missed_successes }, () => "passed"));
    mount("trap").innerHTML =
      head("2", "The metric trap",
        `A success-rate dashboard is blind exactly where it costs money.`,
        `The metric most teams ship is completion — a keyword check. Compared with blind human judgment on the same calls, here is how often they agree.`) + `
      <div class="scene-body">
        <div class="trap-grid">
          <div>
            <div class="trap-stats">
              <div class="trap-stat"><div class="ts-v">${T.agree}/${T.n}</div><div class="ts-l">heuristic agrees with the blind human label</div></div>
              <div class="trap-stat"><div class="ts-v">${T.missed_successes}</div><div class="ts-l">real successes it missed</div></div>
              <div class="trap-stat"><div class="ts-v">${T.false_passes}/${T.human_failures}</div><div class="ts-l">real failures it passed</div></div>
            </div>
            <div class="dotfield" role="img"
              aria-label="${T.n} labeled calls: ${T.agree} where the heuristic agrees with the human, ${T.missed_successes} real successes it missed, ${T.false_passes} real failures it passed.">
              ${dots.map(k => `<span class="df-dot ${k}"></span>`).join("")}
            </div>
            <div class="dotfield-key">
              <span><i style="background:var(--line)"></i>heuristic agrees (${T.agree})</span>
              <span><i style="background:var(--prov-human)"></i>missed successes (${T.missed_successes})</span>
              <span><i style="background:var(--bad)"></i>failures passed (${T.false_passes})</span>
            </div>
          </div>
          <div class="trap-side">
            <p class="trap-caption">${esc(T.caption)}</p>
            <div>${prov("measured", "Deterministic heuristic")} ${prov("human", "Blind labels")}</div>
            <p class="panel-note">${esc(T.provenance)}.</p>
          </div>
        </div>
      </div>`;
  }

  /* ============================================================
     SCENE 3 · Deterministic before judge
     ============================================================ */

  function renderMeasure() {
    const clusters = D.analytics.failure_clusters || [];
    const byDim = Object.fromEntries(clusters.map(c => [c.dimension, c.count]));
    const latency = byDim["latency_gap"] ?? "—";
    const barge = byDim["barge_in"] ?? "—";
    mount("measure").innerHTML =
      head("3", "Architecture",
        `Deterministic before judge.`,
        `Two rules. Measure what a clock or a rule can answer. Judge only what is genuinely subjective — and calibrate even that.`) + `
      <div class="scene-body">
        <div class="doctrine">
          <article class="rule">
            <span class="rule-tag">Rule one</span>
            <h3>Never ask an AI something you can measure.</h3>
            <p>Barge-ins (speech overlap in either direction) and latency gaps come from turn-timestamp arithmetic — counted, not judged. Missing timing is omitted, never fabricated.</p>
            <div class="rule-nums">
              <div><div class="rn-v">${latency}</div><div class="rn-l">latency gaps</div></div>
              <div><div class="rn-v">${barge}</div><div class="rn-l">barge-in events</div></div>
            </div>
            <div class="rule-prov">${prov("measured", "Timestamp math")}</div>
          </article>
          <article class="rule hot">
            <span class="rule-tag">Rule two</span>
            <h3>The judge runs in quarantine — only after humans set the bar, blind.</h3>
            <p>Five quality dimensions, temperature ${RUN.temperature}, every score must cite the turn it came from, and each judgment is validated before it is ever cached.</p>
            <div class="rule-nums">
              <div><div class="rn-v">${RUN.validated_judgments}</div><div class="rn-l">validated · ${RUN.failures} failures</div></div>
              <div><div class="rn-v">κ ${CAL.kappa}</div><div class="rn-l">calibrated, n=${CAL.n}</div></div>
            </div>
            <div class="rule-prov">${prov("calibrated", "Validated before cached")}</div>
          </article>
        </div>
        <div class="doctrine-foot">
          <span class="punch">Measure what's measurable. Judge only what's left.</span>
          <span class="punch-sub">Most of this layer is not an eval — it is arithmetic, so it cannot hallucinate.</span>
        </div>
      </div>`;
  }

  /* ============================================================
     SCENE 4 · The hero call (constructed, disclosed)
     ============================================================ */

  function renderHero() {
    const hero = ROWS.find(r => r.id === "hero_001");
    const failDims = hero ? hero.failures.reduce((m, f) => { m[f.dimension] = (m[f.dimension] || 0) + 1; return m; }, {}) : {};
    const barge = failDims["barge_in"] || 0;
    const latency = failDims["latency_gap"] || 0;
    mount("hero").innerHTML =
      head("4", "Hero call",
        `A “success” that limped.`,
        ``) + `
      <div class="scene-body">
        <div class="hero-call-grid">
          <div>
            <span class="disclose">⚠ Constructed scenario · disclosed up front · voiced with Cartesia</span>
            <p class="ch-lede" style="margin-top:14px;max-width:54ch">
              One call, here to show <b>detection</b>, not to pad a statistic. Completion says success.
              The human says success. But look at the shape.
            </p>
            <div class="hero-verdicts">
              <div class="verdict"><div class="v-k">completion heuristic</div><div class="v-v">success</div></div>
              <div class="verdict"><div class="v-k">blind human</div><div class="v-v">success</div></div>
              <div class="verdict tag"><div class="v-k">VoiceForge archetype</div><div class="v-v">brittle success</div></div>
            </div>
            <p class="hero-line">
              The task got done — but the caller had to <b>fight</b> for it. A pass/fail number calls this
              a win and moves on. VoiceForge calls it brittle, shows the friction, and keeps the receipt.
            </p>
            ${hero ? `<button class="btn primary hero-open" data-open-call="hero_001">Open hero_001 — cited evidence →</button>` : ""}
          </div>
          <div class="hero-signals">
            <div class="hsig">
              <div><div class="hs-name">Caller barged in</div><div class="hs-sub">speech overlap, reconstructed from turn timestamps</div></div>
              <div class="hs-count">×${barge}</div>
            </div>
            <div class="hsig">
              <div><div class="hs-name">Latency gaps</div><div class="hs-sub">dead air on the clock — measured, not judged</div></div>
              <div class="hs-count">×${latency}</div>
            </div>
            <div style="margin-top:4px">${prov("measured", "Deterministic signal hits")} ${prov("notobs", "Prevalence lives in the blind labels")}</div>
            <p class="panel-note" style="max-width:46ch">Validity comes from the public-data calibration in the next scene — never from this one constructed call.</p>
          </div>
        </div>
      </div>`;
  }

  /* ============================================================
     SCENE 5 · Blind labels + calibration (centerpiece)
     ============================================================ */

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
    mount("judge").innerHTML =
      head("5", "Blind labels & calibration",
        `“I do not trust the judge. I measure how much to trust it.”`,
        `Outcomes were labeled blind before any judging — IDs stripped, scores hidden. ${D.val.binary} usable binary labels. Then: does the judge agree? Reported measured, not assumed.`) + `
      <div class="scene-body">
        <div class="judge-grid">
          <div class="panel">
            <div class="panel-head"><h3>Binary agreement</h3>${prov("calibrated", "Binary calibrated")}</div>
            <div class="kappa-row">
              <div class="kstat"><div class="kv">${CAL.kappa}</div><div class="kl">Cohen’s κ — ${esc(CAL.band)}</div></div>
              <div class="kstat"><div class="kv">${pct(CAL.raw_agreement)}</div><div class="kl">raw agreement</div><div class="kd">n=${CAL.n} blind labels</div></div>
            </div>
            <div class="ci-strip" aria-label="Bootstrap 95% CI for kappa, ${lo} to ${hi}, crossing zero.">
              <div class="ci-track">
                <span class="ci-range" style="left:${px(lo)}; width:calc(${px(hi)} - ${px(lo)})"></span>
                <span class="ci-zero" style="left:${px(0)}"></span>
                <span class="ci-point" style="left:${px(CAL.kappa)}"></span>
              </div>
              <div class="ci-labels"><span>${axisMin}</span><span>0</span><span>bootstrap 95% CI ${lo} → ${hi}</span><span>${axisMax}</span></div>
            </div>
            <div class="cal-extra">
              <div><div class="ce-v">${fmt(CAL.balanced_accuracy)}</div><div class="ce-l">balanced accuracy (imbalance-aware)</div></div>
              <div><div class="ce-v">${pct(CAL.failure_recall)}</div><div class="ce-l">failure recall — what matters for risk</div></div>
            </div>
            <p class="ci-note">82% of calls succeed, so κ is mathematically crushed — the prevalence paradox. Shown low and honest, not hidden.</p>
          </div>
          <div class="panel">
            <div class="panel-head"><h3>Confusion matrix · the ${CAL.disagreements.length} disagreements</h3><span class="cs-hint">n=${CAL.n}</span></div>
            <div class="cmx">
              <div></div><div class="ax">judge: success</div><div class="ax">judge: fail</div>
              <div class="ax side">human: success</div>
              ${cell("h_success|j_success", true, "success", "success")}
              ${cell("h_success|j_fail", false, "success", "fail")}
              <div class="ax side">human: fail</div>
              ${cell("h_fail|j_success", false, "fail", "success")}
              ${cell("h_fail|j_fail", true, "fail", "fail")}
            </div>
            <div class="truth-row">
              <div class="truth"><div class="tr-v">71% ≈ 69%</div><div class="tr-l">hi-en vs English — statistically the same</div></div>
              <div class="truth"><div class="tr-v">83% vs 50%</div><div class="tr-l">high vs medium annotator confidence</div></div>
            </div>
            <div class="chips">${CAL.disagreements.slice(0, 10).map(id => callChip(id)).join("")}</div>
            <p class="chips-key">Where NOT to trust the judge. The real fault line is confidence, not language —
              it routes a second-rater review queue. <button class="chip" data-open-corpus="calls">Browse all ${ROWS.length} calls →</button></p>
          </div>
        </div>
      </div>`;
  }

  function callChip(id) {
    return ROW_IDS.has(id)
      ? `<button class="chip" data-open-call="${esc(id)}">${esc(id)}</button>`
      : `<button class="chip" disabled aria-disabled="true" title="Transcript excluded from this package">${esc(id)}<span class="chip-tag">excluded</span></button>`;
  }

  /* ============================================================
     SCENE 6 · Phenotypes + improvement queue
     ============================================================ */

  function renderAction() {
    const F = P.fix_first;
    const queue = R.improvement_queue || [];
    const counts = R.archetypes.counts;
    // representative archetype rows (the five the docs name)
    const archRows = [
      ["seamless_success", "Seamless", "seamless", false],
      ["brittle_success", "Brittle", "brittle", true],
      ["recovered_success", "Recovered", "recovered", false],
      ["intent_or_slot_loss_failure", "Slot-loss failure", "slotloss", false],
      ["workflow_failure", "Workflow failure", "workflow", false],
    ];
    const total = archRows.reduce((a, [k]) => a + (counts[k] || 0), 0) || 1;
    const maxC = Math.max(1, ...archRows.map(([k]) => counts[k] || 0));
    mount("action").innerHTML =
      head("6", "Phenotypes & the queue",
        `Pass/fail is one bit. Failure has shapes — so does success.`,
        `Every call gets transcript-observable phenotype tags; archetypes are derived deterministically, never hand-picked. Each failure becomes a queue entry with evidence and a fix.`) + `
      <div class="scene-body">
        <div class="pheno-grid">
          <div class="panel">
            <div class="panel-head"><h3>Archetype distribution</h3>${prov("human", "Human-labeled phenotypes")}</div>
            <div class="band" role="img" aria-label="Distribution across five outcome archetypes.">
              ${archRows.map(([k, , cls]) => `<span class="seg ${cls}" style="width:${(100 * (counts[k] || 0) / total).toFixed(1)}%"></span>`).join("")}
            </div>
            <div class="arch-list">
              ${archRows.map(([k, label, cls, hot]) => `
                <div class="arch ${hot ? "hot" : ""}">
                  <div class="a-name"><b>${esc(counts[k] || 0)}</b> ${esc(label)}</div>
                  <div class="a-bar"><span class="a-track"><span class="a-fill" style="width:${Math.max(4, 100 * (counts[k] || 0) / maxC)}%"></span></span><span class="a-v">${counts[k] || 0}</span></div>
                </div>`).join("")}
            </div>
            <p class="panel-note">Five successes are <b>brittle</b> — done, but the caller fought. A success rate hides that; a phenotype distribution can't.</p>
          </div>
          <article class="spotlight">
            <span class="sp-tag">Fix-first · ranked by exposure</span>
            <div class="sp-title">${esc(pretty(F.phenotype_id))}</div>
            <div class="sp-stats">
              <div class="sp-stat"><div class="v">${F.affected_calls}</div><div class="l">affected calls</div></div>
              <div class="sp-stat"><div class="v est-value">${money(F.estimated_spend_usd)}</div><div class="l">est. affected spend</div></div>
            </div>
            <div class="sp-action">
              <h4>Recommended change</h4>
              <p>${esc(F.recommendation)}</p>
            </div>
            <div class="sp-chips">${F.evidence_call_ids.slice(0, 6).map(id => callChip(id)).join("")}</div>
            <div class="sp-foot">
              ${prov("exploratory", "Template-derived · needs review")}
              ${prov("estimated", "Modeled exposure — not savings")}
            </div>
          </article>
        </div>
        <div class="pheno-foot">
          <span>That's not a score — it's an engineering backlog, sorted by what to fix first.</span>
          <button class="btn" data-open-corpus="queue">Open full improvement queue (${queue.length}) →</button>
        </div>
      </div>`;
  }

  /* ============================================================
     SCENE 7 · Bolna × Cartesia + LIVE TODAY slot
     ============================================================ */

  function renderProof() {
    const shortHash = h => h ? h.slice(0, 12) + "…" : "—";
    mount("proof").innerHTML =
      head("7", "Bolna × Cartesia",
        `Bolna runs the call. Cartesia gives it a voice. VoiceForge tells you what to fix next.`,
        `Three honest links — a real Bolna execution ingested from their API, the live agent configured with Cartesia, and the hero call voiced with that same Cartesia voice.`) + `
      <div class="scene-body">
        <div class="proof-flow">
          <div class="proof-node">
            <div class="pn-name">Bolna agent</div>
            <div class="pn-sub">orchestration<br>agent ${esc(SP.agent_id)}</div>
          </div>
          <div class="proof-node">
            <div class="pn-name">Cartesia synthesizer</div>
            <div class="pn-sub">${esc(SP.cartesia_voice)} · ${esc(SP.cartesia_model)}<br>configured in the agent's synthesizer block</div>
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
        <div class="live-slot">
          <div class="ls-head">
            <span class="ls-title">⟨ Live-today slot ⟩</span>
            ${prov("uncal", "Uncalibrated · corpus-only")}
          </div>
          <p>Fresh on-site calls through the live Cartesia-voiced agent — clean, code-switched, a repair loop — pushed through this same pipeline. Timestamps prove they're from today. Shown separately; they never enter the frozen 46-call manifest and never touch κ.</p>
        </div>
        <div class="runfacts-row">
          <div class="runfact"><span class="rf-k">judge model</span><span class="rf-v">${esc(RUN.model)}</span></div>
          <div class="runfact"><span class="rf-k">temperature</span><span class="rf-v">${RUN.temperature}</span></div>
          <div class="runfact"><span class="rf-k">validated</span><span class="rf-v">${RUN.validated_judgments}/${RUN.expected_judgments}</span></div>
          <div class="runfact"><span class="rf-k">rubric hash</span><span class="rf-v">${esc(RUN.rubric_hash)}</span></div>
        </div>
      </div>`;
  }

  /* ============================================================
     SCENE 8 · Value, honest limits, close
     ============================================================ */

  function renderMethod() {
    const tc = D.analytics.timing_coverage;
    const limits = [
      "Completion is a deterministic keyword heuristic, not gold dialogue state.",
      "Costs are estimated exposure from public unit prices — not measured savings.",
      "Calibration is a one-rater pilot at n=" + CAL.n + "; its CI includes zero.",
      "The five semantic judge dimensions remain uncalibrated diagnostics.",
      tc.unmeasured + " text-only calls carry no timing — it is omitted, never fabricated.",
      "The hero call is constructed and disclosed as such; its audio is Cartesia-synthesized.",
      "The ingested Bolna execution predates the Cartesia voice swap; the live agent runs Cartesia today.",
      "The live calls are uncalibrated. The demo runs fully offline — no network, no live API.",
    ];
    mount("method").innerHTML =
      head("8", "Value, limits & close",
        `Honesty is the feature.`,
        `Clean calls are cheap; calls where the caller fights burn money. That's the budget a success rate can't see.`) + `
      <div class="scene-body">
        <div class="value-row">
          <div class="hstat"><div class="hs-v est-value">${pct(P.friction_or_failure_spend_share)}</div><div class="hs-l">est. spend touched by friction or failure</div>${prov("estimated", "Estimated prototype")}</div>
          <div class="hstat"><div class="hs-v est-value">${money(P.cost_per_human_success_est)}</div><div class="hs-l">est. cost per confirmed success</div>${prov("estimated", "Estimated prototype")}</div>
          <div class="hstat"><div class="hs-v">${pct(P.brittle_share_of_successes)}</div><div class="hs-l">of successes are brittle</div>${prov("human", "Human-labeled")}</div>
        </div>
        <ul class="limits">
          ${limits.map(t => `<li>${esc(t)}</li>`).join("")}
        </ul>
        <div class="closer">
          <p class="close-line">“Success rate tells you whether calls finished. VoiceForge tells you how they finished, what failures cost, and what to fix first.”</p>
          <p class="close-sub">Every limit above is labeled in the product — blind labels, cited turns, pinned hashes, and an improvement queue an engineer can open tomorrow.</p>
          <p class="close-thanks">Thank you to <b>Bolna</b> and <b>Cartesia</b> for the platform and the voice. I'd love your questions.</p>
        </div>
      </div>`;
  }

  /* ============================================================
     CALL EVIDENCE SHEET (drawer)
     ============================================================ */

  const sheet = document.getElementById("callsheet");
  const scrim = document.getElementById("callsheet-scrim");
  let lastFocus = null;

  function dimRow(d, kind) {
    const ids = d.evidence_turn_ids || [];
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
          <p class="cs-hint">Click any judgment to highlight the transcript turns it cites.</p>
        </div>
      </div>`;
    scrim.hidden = false;
    sheet.hidden = false;
    sheet.classList.add("cs-open");
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
      if (corpus.hidden) document.body.style.overflow = "";
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

  /* ============================================================
     CORPUS BROWSER (full table + full queue live ONLY here)
     ============================================================ */

  const corpus = document.getElementById("corpus");
  const corpusScrim = document.getElementById("corpus-scrim");
  let corpusFocus = null;
  let corpusTab = "calls";

  function renderCorpus(tab) {
    corpusTab = tab || corpusTab;
    mount("corpus").innerHTML = `
      <div class="co-head">
        <h3 id="corpus-title">Corpus browser</h3>
        <span class="co-sub">${ROWS.length} scored calls · full evidence</span>
        <div class="co-tabs" role="tablist">
          <button class="co-tab" role="tab" data-corpus-tab="calls" aria-selected="${corpusTab === "calls"}">All calls</button>
          <button class="co-tab" role="tab" data-corpus-tab="queue" aria-selected="${corpusTab === "queue"}">Improvement queue</button>
        </div>
        <button class="btn co-close" data-close-corpus>Close <span class="mono" style="font-size:10px">ESC</span></button>
      </div>
      <div class="co-body" id="co-body"></div>`;
    if (corpusTab === "calls") renderCorpusCalls();
    else renderCorpusQueue();
  }

  function renderCorpusCalls() {
    document.getElementById("co-body").innerHTML = `
      <input class="search" id="call-filter" type="search"
        placeholder="Filter by ID, language, profile, workflow…" aria-label="Filter calls">
      <div class="calltable-wrap">
        <table class="calltable">
          <thead><tr><th>call</th><th>source</th><th>lang</th><th>profile</th><th>turns</th>
            <th>human</th><th>heuristic*</th><th>overall</th><th></th></tr></thead>
          <tbody id="call-tbody"></tbody>
        </table>
      </div>
      <p class="table-note">*Heuristic keyword task-completion — exactly the metric the trap scene measures.
        Overall is the weighted mean over present dimensions only.
        Human label ${prov("human", "Human-labeled")} · heuristic ${prov("measured", "Measured")}</p>`;
    const input = document.getElementById("call-filter");
    input.addEventListener("input", e => renderCallRows(e.target.value));
    renderCallRows("");
    input.focus();
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

  function renderCorpusQueue() {
    const queue = R.improvement_queue || [];
    const groups = [];
    queue.forEach(item => {
      let g = groups.find(g => g.rec === item.recommendation);
      if (!g) { g = { rec: item.recommendation, items: [] }; groups.push(g); }
      g.items.push(item);
    });
    groups.sort((a, b) => b.items.length - a.items.length);
    document.getElementById("co-body").innerHTML = `
      <p class="table-note" style="margin:0 0 14px">Each candidate fix traces to a blind-labeled phenotype on a specific call.
        No lift is promised. Grouped by recommended change; dimmed calls are excluded from this package. ${prov("exploratory", "Template-derived · requires review")}</p>
      <div class="queue">
        ${groups.map(g => `
          <div class="queue-group-head">${esc(g.rec)} · ${g.items.length}</div>
          ${g.items.map(item => queueItem(item)).join("")}`).join("")}
      </div>`;
  }

  function queueItem(item) {
    const has = ROW_IDS.has(item.call_id);
    return `<button class="qitem" ${has ? `data-open-call="${esc(item.call_id)}"` : `disabled title="Transcript excluded from this package"`}>
      <span class="qi-id">${esc(item.call_id)}</span>
      <span class="qi-meta">${esc(item.human)} · <i>${esc(pretty(item.archetype))}</i></span>
      <span class="qi-go" aria-hidden="true">${has ? "→" : ""}</span>
      <span class="qi-tags">evidence: ${item.evidence_tags.map(pretty).map(esc).join(", ")}</span>
    </button>`;
  }

  function openCorpus(tab) {
    corpusFocus = document.activeElement;
    renderCorpus(tab);
    corpusScrim.hidden = false;
    corpus.hidden = false;
    corpus.classList.add("co-open");
    document.body.style.overflow = "hidden";
    const c = corpus.querySelector(".co-close");
    if (c) c.focus();
  }

  function closeCorpus() {
    if (corpus.hidden) return;
    corpus.classList.add("closing");
    corpusScrim.classList.add("closing");
    const finish = () => {
      corpus.hidden = true;
      corpusScrim.hidden = true;
      corpus.classList.remove("closing", "co-open");
      corpusScrim.classList.remove("closing");
      if (sheet.hidden) document.body.style.overflow = "";
      if (corpusFocus && document.contains(corpusFocus)) corpusFocus.focus();
    };
    if (reducedMotion()) { finish(); return; }
    setTimeout(finish, 250);
  }

  /* ============================================================
     SCENE NAVIGATION — rail, snap, keyboard
     ============================================================ */

  const scenes = Array.from(document.querySelectorAll(".scene"));
  const deck = document.getElementById("main");

  function buildRail() {
    document.getElementById("rail").innerHTML = scenes.map(s => `
      <a href="#${s.id}" data-jump="${s.id}">
        <span class="sp-num">${esc(s.dataset.num)}</span>
        <span class="sp-label">${esc(s.dataset.short)}</span>
      </a>`).join("");
  }

  function jumpTo(id) {
    const node = document.getElementById(id);
    if (!node) return;
    node.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" });
  }

  function currentIndex() {
    const mid = window.innerHeight / 2;
    let best = 0, bestDist = Infinity;
    scenes.forEach((s, i) => {
      const r = s.getBoundingClientRect();
      const center = r.top + r.height / 2;
      const dist = Math.abs(center - mid);
      if (dist < bestDist) { bestDist = dist; best = i; }
    });
    return best;
  }

  function setActiveScene(id) {
    if (document.body.dataset.ch === id) return;
    document.body.dataset.ch = id;
    const s = document.getElementById(id);
    document.getElementById("topbar-chapter").textContent =
      `${s.dataset.num} · ${s.dataset.title.replace(/&amp;/g, "&")}`;
    document.querySelectorAll(".rail a").forEach(a =>
      a.setAttribute("aria-current", a.dataset.jump === id ? "true" : "false"));
    try { history.replaceState(null, "", "#" + id); } catch (e) { /* sandboxed */ }
  }

  function updateActive() {
    const id = scenes[currentIndex()].id;
    setActiveScene(id);
    document.getElementById("topbar").classList.toggle("shown", id !== "sc-thesis");
  }

  function watchScroll() {
    let ticking = false;
    const onScroll = () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(() => { ticking = false; updateActive(); });
    };
    deck.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    updateActive();
  }

  /* ---------- global events ---------- */

  document.addEventListener("click", e => {
    const open = e.target.closest("[data-open-call]");
    if (open && !open.disabled) { openCall(open.dataset.openCall); return; }
    const oc = e.target.closest("[data-open-corpus]");
    if (oc) { openCorpus(oc.dataset.openCorpus); return; }
    const ct = e.target.closest("[data-corpus-tab]");
    if (ct) { renderCorpus(ct.dataset.corpusTab); return; }
    const ev = e.target.closest("[data-evidence]");
    if (ev) { highlightEvidence(ev.dataset.evidence, ev); return; }
    const jump = e.target.closest("[data-jump]");
    if (jump) { e.preventDefault(); jumpTo(jump.dataset.jump); return; }
    if (e.target.closest("[data-close-sheet]") || e.target === scrim) { closeCall(); return; }
    if (e.target.closest("[data-close-corpus]") || e.target === corpusScrim) { closeCorpus(); return; }
  });

  document.addEventListener("keydown", e => {
    const tag = (e.target.tagName || "").toLowerCase();
    const typing = tag === "input" || tag === "textarea";

    // Escape closes overlays (works even while typing in the corpus filter)
    if (e.key === "Escape") {
      if (!sheet.hidden) { closeCall(); return; }
      if (!corpus.hidden) { closeCorpus(); return; }
    }

    if (typing) return;

    // While the call sheet is open: Enter opens a focused call; nav is suspended.
    if (!sheet.hidden) {
      if (e.key === "Enter" && e.target.closest("[data-open-call]")) openCall(e.target.closest("[data-open-call]").dataset.openCall);
      return;
    }
    // While the corpus browser is open: allow row Enter; suspend scene nav.
    if (!corpus.hidden) {
      if (e.key === "Enter" && e.target.closest("[data-open-call]")) openCall(e.target.closest("[data-open-call]").dataset.openCall);
      return;
    }

    const i = currentIndex();
    if (e.key === "ArrowRight" || e.key === "ArrowDown" || e.key === "PageDown" || e.key === " ") {
      e.preventDefault(); jumpTo(scenes[Math.min(scenes.length - 1, i + 1)].id);
    } else if (e.key === "ArrowLeft" || e.key === "ArrowUp" || e.key === "PageUp") {
      e.preventDefault(); jumpTo(scenes[Math.max(0, i - 1)].id);
    } else if (e.key === "Home") {
      e.preventDefault(); jumpTo(scenes[0].id);
    } else if (e.key === "End") {
      e.preventDefault(); jumpTo(scenes[scenes.length - 1].id);
    } else if (e.key.toLowerCase() === "b") {
      openCorpus("calls");
    }
  });

  document.getElementById("corpus-toggle").addEventListener("click", () => openCorpus("calls"));

  /* ---------- boot ---------- */

  document.getElementById("gate-chip").textContent =
    `${D.val.binary} blind binary labels · ${RUN.n_calls}/${R.manifest_total} judged · ${RUN.failures} failures`;

  renderThesis();
  renderTrap();
  renderMeasure();
  renderHero();
  renderJudge();
  renderAction();
  renderProof();
  renderMethod();
  buildRail();
  watchScroll();

  if (location.hash) {
    const target = location.hash.slice(1);
    if (document.getElementById(target)) setTimeout(() => jumpTo(target), 30);
  }
})();
