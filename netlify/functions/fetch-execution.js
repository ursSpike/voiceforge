// Netlify Function — POST /api/fetch_execution {execution_id}
// Returns Bolna's execution payload + per-turn /log so the page can render the call inline.
// Browser never sees the API key.

export default async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "method not allowed" }), {
      status: 405, headers: { "Content-Type": "application/json" }
    });
  }
  let body;
  try { body = await req.json(); } catch { body = {}; }
  const id = (body.execution_id || "").trim();
  if (!id) {
    return new Response(JSON.stringify({ error: "execution_id required" }), {
      status: 400, headers: { "Content-Type": "application/json" }
    });
  }
  const key = process.env.BOLNA_API_KEY;
  if (!key) {
    return new Response(JSON.stringify({ error: "BOLNA_API_KEY not configured" }), {
      status: 503, headers: { "Content-Type": "application/json" }
    });
  }
  try {
    const auth = { "Authorization": `Bearer ${key}` };
    const [exR, logR] = await Promise.all([
      fetch(`https://api.bolna.ai/executions/${id}`, { headers: auth }),
      fetch(`https://api.bolna.ai/executions/${id}/log`, { headers: auth }),
    ]);
    const execution = exR.ok ? await exR.json() : { _error: `exec_${exR.status}` };
    const log = logR.ok ? await logR.json() : { _error: `log_${logR.status}` };
    // Reconstruct ordered turns from /log component events.
    // Real Bolna shape: data is a STRING; component=synthesizer (response) → agent spoken text;
    // component=transcriber (response) → user spoken text. De-dup adjacent same-role same-text.
    const events = Array.isArray(log.data) ? log.data : [];
    const turns = [];
    for (const e of events) {
      const data = typeof e.data === "string" ? e.data.trim() : "";
      if (!data) continue;
      let role = null;
      if (e.component === "synthesizer" && e.type === "response") role = "agent";
      else if (e.component === "transcriber" && e.type === "response") role = "user";
      else continue;
      const last = turns[turns.length - 1];
      if (last && last.role === role && last.text === data) continue;
      turns.push({ role, text: data, t: e.created_at });
    }
    // Deterministic signals — latency gaps between user end & next agent start, in ms.
    // Pulled from /log created_at (ISO-ish strings); no barge-in (Bolna doesn't expose overlap).
    const parseT = (s) => { const d = new Date((s || "").replace(" ", "T") + "Z"); return isFinite(d) ? d.getTime() : null; };
    const ordered = events.map(e => ({ ...e, _t: parseT(e.created_at) })).filter(e => e._t != null).sort((a,b)=>a._t-b._t);
    const gaps = [];
    for (let i = 0; i < ordered.length - 1; i++) {
      const cur = ordered[i], nxt = ordered[i+1];
      if (cur.component === "transcriber" && cur.type === "response" &&
          nxt.component === "synthesizer" && (nxt.type === "request" || nxt.type === "response")) {
        const g = nxt._t - cur._t;
        if (g >= 0 && g < 30000) gaps.push(g);
      }
    }
    gaps.sort((a,b)=>a-b);
    const median = gaps.length ? gaps[Math.floor(gaps.length/2)] : null;
    const p90 = gaps.length ? gaps[Math.min(gaps.length-1, Math.floor(gaps.length*0.9))] : null;
    const slowGaps = gaps.filter(g => g > 800).length;
    const callDurationMs = ordered.length ? (ordered[ordered.length-1]._t - ordered[0]._t) : null;
    const signals = {
      n_turns: turns.length,
      duration_s: callDurationMs != null ? Math.round(callDurationMs/100)/10 : null,
      latency: {
        n_gaps: gaps.length,
        median_ms: median,
        p90_ms: p90,
        n_over_800ms: slowGaps,
      },
      barge_in: { observed: false, note: "Bolna /log exposes no overlap signal." },
    };

    // Judge — minimal Gemini call for binary outcome on the live transcript.
    // Uses GEMINI_API_KEY if present; gracefully skips otherwise.
    let judge = null;
    const gkey = process.env.GEMINI_API_KEY;
    if (gkey && turns.length) {
      try {
        const conv = turns.map((t,i) => `${(i+1)}. ${t.role.toUpperCase()}: ${t.text}`).join("\n");
        const prompt = `You judge a voice agent call. Agent: Aarav, appointment scheduler for Aarogya Clinic & Diagnostics (Hinglish). Caller is the user.

Transcript:
${conv}

Goal: did the agent COMPLETE the user's task this call (book an appointment, or correctly handle the user declining/asking-info, or correctly refuse medical advice + offer a consult)?

Reply ONLY with strict JSON:
{"outcome":"success"|"fail","reason":"<one short sentence>","evidence_turn_ids":[<integers from transcript>]}`;
        const gr = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${gkey}`, {
          method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            contents: [{ parts: [{ text: prompt }] }],
            generationConfig: { temperature: 0.0, responseMimeType: "application/json" },
          }),
        });
        if (gr.ok) {
          const gj = await gr.json();
          const raw = gj?.candidates?.[0]?.content?.parts?.[0]?.text || "";
          try { judge = JSON.parse(raw); judge.provenance = "uncalibrated · gemini-flash-latest · live"; }
          catch { judge = { _raw: raw.slice(0, 200), error: "judge_parse_failed" }; }
        } else {
          judge = { error: `gemini_http_${gr.status}` };
        }
      } catch (e) {
        judge = { error: "judge_request_failed", detail: String(e).slice(0, 120) };
      }
    } else if (!turns.length) {
      judge = { pending: "no turns yet — try again in a few seconds" };
    } else {
      judge = { skipped: "GEMINI_API_KEY not configured on Netlify" };
    }

    return new Response(JSON.stringify({
      execution_id: id,
      status: execution.status,
      transcript: execution.transcript || "",
      turns,
      extracted_data: execution.extracted_data || null,
      cost_breakdown: execution.cost_breakdown || null,
      telephony: execution.telephony_data || null,
      signals,
      judge,
      raw_status: execution.status,
    }), { status: 200, headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: "bolna_request_failed", detail: String(e).slice(0, 200) }), {
      status: 502, headers: { "Content-Type": "application/json" }
    });
  }
};

export const config = { path: "/api/fetch_execution" };
