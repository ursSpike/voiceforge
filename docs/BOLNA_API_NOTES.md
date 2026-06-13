# Bolna API Notes (live-call ingestion)

Research date: 2026-06-13. Every fact below is cited to a doc URL or to the cached
real payload at `data/provider_logs/bolna_246cd9f3.json`. Where the public docs are
silent, it is marked **not found in docs — ask the Buddy**.

Docs note: `docs.bolna.ai/*` 308-redirects to `www.bolna.ai/docs/*`. Use the
`www.bolna.ai/docs` host directly.

---

## 1. Auth + Base URL

- **Base URL:** `https://api.bolna.ai` — confirmed on the make-call and
  get-all-executions reference pages.
- **Auth:** `Authorization: Bearer <BOLNA_API_KEY>` plus `Content-Type: application/json`.
  Docs: "include this key in the `Authorization` header of all your HTTP requests
  using the `Bearer` scheme." Subaccount keys are prefixed `sa-`.
  - [api-reference/introduction](https://www.bolna.ai/docs/api-reference/introduction)

**Verdict:** our `BASE = "https://api.bolna.ai"` and
`{"Authorization": f"Bearer {key}"}` are correct.

---

## 2. Endpoints we need

| Purpose | Method | Path | Auth | Source |
|---|---|---|---|---|
| Trigger outbound call | `POST` | `/call` | Bearer | [calls/make](https://www.bolna.ai/docs/api-reference/calls/make), [making-outgoing-calls](https://www.bolna.ai/docs/making-outgoing-calls) |
| Get one execution | `GET` | `/executions/{execution_id}` | Bearer | [executions/get_execution](https://www.bolna.ai/docs/api-reference/executions/get_execution) |
| Get turn-by-turn log | `GET` | `/executions/{execution_id}/log` | Bearer | [llms-full.txt](https://www.bolna.ai/docs/llms-full.txt) (no standalone rendered page found) |
| List agent executions | `GET` | `/v2/agent/{agent_id}/executions` | Bearer | [agent/v2/get_all_agent_executions](https://www.bolna.ai/docs/api-reference/agent/v2/get_all_agent_executions) |

### POST /call (trigger outbound call)
Request body ([calls/make](https://www.bolna.ai/docs/api-reference/calls/make)):
- **required:** `agent_id` (UUID), `recipient_phone_number` (E.164)
- optional: `from_phone_number`, `scheduled_at` (ISO 8601),
  `user_data` (object — **this is the "variables" slot**: "additional user dynamic
  variables as defined in the agent prompt"), `agent_data` (overrides; supports
  `voice_id`), `retry_config`, `bypass_call_guardrails`.

Response (200):
```json
{ "message": "done", "status": "queued",
  "execution_id": "123e4567-e89b-12d3-a456-426614174000" }
```
The returned `execution_id` is the id you then feed to `/executions/{id}` and
`/executions/{id}/log`. (Docs call it "`execution_id` or `call_id`".)

### GET /v2/agent/{agent_id}/executions (list — the `--latest` stub)
Query params: `page_number` (default 1), `page_size` (default 20, max 50),
`status`, `call_type`, `provider`, `answered_by_voice_mail`, `batch_id`,
`from`, `to` (ISO 8601 UTC).
Response: `{ page_number, page_size, total, has_more, data: [ {execution}, ... ] }`.
Each execution object has an `id` (UUID). Sort/most-recent ordering is **not
explicitly documented — ask the Buddy** whether `data[0]` is newest or whether a
`from`/`to` window is required.
([agent/v2/get_all_agent_executions](https://www.bolna.ai/docs/api-reference/agent/v2/get_all_agent_executions))

---

## 3. Real call-data field map

### `GET /executions/{execution_id}` — execution object
Top-level keys (confirmed against the cached real payload
`data/provider_logs/bolna_246cd9f3.json`, and cross-checked with
[executions/get_execution](https://www.bolna.ai/docs/api-reference/executions/get_execution)):

`id`, `agent_id`, `batch_id`, `scheduled_at`, `answered_by_voice_mail`,
`conversation_duration` (sec, float), `total_cost` (cents, float), `transcript`,
`usage_breakdown`, `cost_breakdown`, `extracted_data`, `summary`, `error_message`,
`status`, `agent_extraction`, `workflow_retries`, `custom_extractions`,
`campaign_id`, `smart_status`, `user_number`, `agent_number`, `initiated_at`,
`retry_config`, `retry_count`, `retry_history`, `created_at`, `updated_at`,
`lid_data`, `telephony_data`, `transfer_call_data`, `context_details`,
`agent_context_details`, `batch_run_details`, `provider`, `latency_data`,
`tool_call_logs`.

- **`transcript` is a single flat STRING**, not an array of turns:
  `"assistant: Hello from Bolna\nuser:  hello\nassistant:  Hi! How can I assist..."`.
  No per-turn timestamps, no per-turn speaker objects, no interruption markers.
  Confirmed by docs ("transcript: String, Transcription of the execution") and by
  the cached payload.
- **`cost_breakdown`** (cents): `llm`, `network`, `platform`, `synthesizer`,
  `transcriber`, plus nested `llm_breakdown` / `synthesizer_breakdown` /
  `transcriber_breakdown` (e.g. `synthesizer_breakdown.conversation`). This is the
  STT/TTS/LLM split we want.
- **`telephony_data`** (object, or `null` for web-calls): `duration`, `to_number`,
  `from_number`, `recording_url`, `call_type`, `provider`, `hangup_reason`,
  `ring_duration`. **Recording URL lives here** as `telephony_data.recording_url`.
  In the cached web-call it is `null` (no telephony leg) — matches our
  `audio_path: None`.
- **`provider`**: conversation channel, e.g. `"web-call"` (cached) — NOT the
  synthesizer/TTS provider.
- **`latency_data`**: present as a field, `null` in the cached web-call. Shape
  **not documented publicly — ask the Buddy** what populates it on a telephony call.
- **`context_details` / `agent_context_details`**: the injected dynamic variables.
- **Synthesizer/voice/provider config (cartesia + voice id):** the execution object
  does **NOT** expose `synthesizer.provider` or a `voice_id`. Confirmed via
  [executions/get_execution](https://www.bolna.ai/docs/api-reference/executions/get_execution)
  ("no fields like `synthesizer.provider` or `voice_id`"); cost only shows
  *spend* on the synthesizer, not its name. To prove "Cartesia voice", you must
  read the **agent config** (`GET /v2/agent/{agent_id}`), not the execution — which
  is exactly what `cache_bolna_cartesia_proof.py` is for. Keep
  `synthesizer_verified=False` until then.

### `GET /executions/{execution_id}/log` — turn-by-turn component events
Response is an object `{ "data": [ ...events... ], "status": ... }`. Each event has:
`created_at`, `component`, `type`, `provider`, `data` (confirmed in cached payload).
Component/type pairs observed in the real log:
`transcriber/response`, `synthesizer/request`, `synthesizer/response`,
`llm/request`, `llm/response`, `llm_language_detection/request|response`.
This is the **only source of per-turn timing** — derived from `created_at` diffs —
since the top-level `transcript` string carries no timestamps. Our
`ingest_bolna.reconstruct_turns` already maps exactly these events. The standalone
rendered doc page for this endpoint 404s, but `llms-full.txt` confirms it exists
("includes prompts, requests, responses, and optional LLM reasoning summaries").

---

## 4. Per-turn timestamps + interruption / barge-in (gates the barge-in claim)

- **Per-turn timestamps:** exist only INDIRECTLY, via the `/log` `data[].created_at`
  event timestamps. They are per-EVENT (transcriber-response, synth-request,
  synth-response), not labelled per-turn start/end. Our pipeline already
  reconstructs start/end_ms from these diffs — that is the honest method and it is
  the only one available. There is **no per-turn `start_ms`/`end_ms` field in the
  API**.
- **Interruption / barge-in:** **NO explicit interruption or barge-in field/token
  exists** in either the execution object or the `/log` payload. Searched the full
  cached payload for `interrupt`, `barge`, `overlap` — zero hits. Docs expose no
  such field either. **The "precise" transcript mode actually SCRUBS interrupted
  content** (already noted in `ingest_bolna.py` header), so barge-ins are *removed*,
  not signalled.

  **Barge-in defensibility:** a live barge-in claim from Bolna data is **NOT
  directly supported by the API.** There is no interruption telemetry. Any barge-in
  signal must be inferred deterministically (e.g. overlapping spans), and for
  web-calls there is no overlap data to infer from — which is why
  `ingest_bolna.normalize` hard-codes `stress_profile: "clean"` and the metadata
  says overlap is NOT computed for web-calls. **Do not claim API-provided barge-in
  telemetry.** A telephony call *might* differ (separate audio legs) but that is
  **not found in docs — ask the Buddy.**

---

## 5. List executions (the `--latest` stub)

Endpoint exists: `GET /v2/agent/{agent_id}/executions` (see §2). The repo's
`fetch_latest()` currently refuses and the code's guessed path
`/agent/{id}/executions?limit=1` is **wrong on two counts**:
1. Missing the `/v2` prefix → should be `/v2/agent/{agent_id}/executions`.
2. `limit=1` is not a valid param → use `page_size=1` (and `page_number=1`).
The id field is `data[0]["id"]` (correct in the stub comment). Whether `data[0]`
is the newest is **not documented — ask the Buddy** (may need `from`/`to` or a sort).

---

## VERDICT: does `ingest_live.fetch_raw` match the real API?

**Mostly YES — `fetch_raw` is correct as written.** It calls:
- `GET /executions/{execution_id}` → assigns to `execution`  ✅ correct path.
- `GET /executions/{execution_id}/log` → assigns to `log`, expects `{"data":[...],
  "status":...}`  ✅ correct path and shape (matches cached payload + llms-full.txt).
- Base URL `https://api.bolna.ai` and `Authorization: Bearer`  ✅ correct.

The assembled `{"execution": {...}, "log": {"data":[...]}}` shape that
`ingest_bolna.normalize` / `reconstruct_turns` consume **matches the real API
responses exactly.** No change needed to `fetch_raw` or the normalize path.

### Minimal change needed (NOT applied — description only)

Only `fetch_latest()` is wrong. Precise diff:

- In `pipeline/ingest_live.py`, `fetch_latest()` (the commented stub lines ~94-95):
  - change the URL from
    `f"/agent/{AGENT_ID}/executions?limit=1"`
    to
    `f"/v2/agent/{AGENT_ID}/executions?page_size=1&page_number=1"`
  - keep `execution_id = listing["data"][0]["id"]` (the id field is correct).
  - Caveat to verify on-site: confirm `data[0]` is the most-recent execution
    (ordering not documented). If not, add `&from=...&to=...` or a sort param —
    **ask the Buddy.**

No other code change is required. The `--execution` path already works against the
real API.

### Flags for the barge-in claim
- **Per-turn timestamps: do NOT exist as API fields.** They are reconstructed from
  `/log` event `created_at` diffs — honest, but it is reconstruction, not a
  native per-turn start/end. Phrase claims accordingly.
- **Interruption / barge-in telemetry: does NOT exist in the Bolna payload.** No
  field, no token; "precise" transcript mode even deletes interrupted text. **A
  barge-in claim cannot cite Bolna API telemetry.** For web-calls there is also no
  overlap to infer from. Treat any barge-in number as deterministically inferred,
  not provider-reported. Telephony-call behavior unverified — **ask the Buddy.**

---

## Sources
- https://www.bolna.ai/docs/api-reference/introduction
- https://www.bolna.ai/docs/api-reference/calls/make
- https://www.bolna.ai/docs/making-outgoing-calls
- https://www.bolna.ai/docs/api-reference/executions/get_execution
- https://www.bolna.ai/docs/api-reference/agent/v2/get_all_agent_executions
- https://www.bolna.ai/docs/llms-full.txt
- Cached real payload: `data/provider_logs/bolna_246cd9f3.json`
