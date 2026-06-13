// Netlify Function — POST /api/start_call → Bolna POST /call
// BOLNA_API_KEY + BOLNA_AGENT_ID come from Netlify env vars (Site settings → Environment).
// Browser never sees the key.

export default async (req) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "method not allowed" }), { status: 405, headers: { "Content-Type": "application/json" } });
  }
  let body;
  try { body = await req.json(); } catch { body = {}; }
  const phone = (body.phone || "").trim();
  if (!phone) {
    return new Response(JSON.stringify({ error: "phone required (E.164, e.g. +91xxxxxxxxxx)" }), { status: 400, headers: { "Content-Type": "application/json" } });
  }
  const key = process.env.BOLNA_API_KEY;
  const agentId = process.env.BOLNA_AGENT_ID || "cb7dee37-fe1b-43fb-a669-4f56a46eeb46";
  if (!key) {
    return new Response(JSON.stringify({ error: "BOLNA_API_KEY not configured on Netlify — set it under Site settings → Environment variables." }), { status: 503, headers: { "Content-Type": "application/json" } });
  }
  try {
    const r = await fetch("https://api.bolna.ai/call", {
      method: "POST",
      headers: { "Authorization": `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify({ agent_id: agentId, recipient_phone_number: phone }),
    });
    const text = await r.text();
    let data; try { data = JSON.parse(text); } catch { data = { raw: text.slice(0, 300) }; }
    if (!r.ok) {
      return new Response(JSON.stringify({ error: `bolna_http_${r.status}`, detail: data }), { status: r.status, headers: { "Content-Type": "application/json" } });
    }
    return new Response(JSON.stringify({
      execution_id: data.execution_id,
      status: data.status,
      message: data.message || "queued",
    }), { status: 200, headers: { "Content-Type": "application/json" } });
  } catch (e) {
    return new Response(JSON.stringify({ error: "bolna_request_failed", detail: String(e).slice(0, 200) }), { status: 502, headers: { "Content-Type": "application/json" } });
  }
};

export const config = { path: "/api/start_call" };
