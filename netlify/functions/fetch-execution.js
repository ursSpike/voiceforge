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
    return new Response(JSON.stringify({
      execution_id: id,
      status: execution.status,
      transcript: execution.transcript || "",
      turns,
      extracted_data: execution.extracted_data || null,
      cost_breakdown: execution.cost_breakdown || null,
      telephony: execution.telephony_data || null,
      raw_status: execution.status,
    }), { status: 200, headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: "bolna_request_failed", detail: String(e).slice(0, 200) }), {
      status: 502, headers: { "Content-Type": "application/json" }
    });
  }
};

export const config = { path: "/api/fetch_execution" };
