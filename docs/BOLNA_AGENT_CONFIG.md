# Bolna — Create & Configure an Agent Programmatically (Hinglish restaurant booking)

Research date: 2026-06-13. Our use case: **INBOUND restaurant table-booking + enquiry voice agent, Hinglish (Hindi+English, mid-call switch), Cartesia voice, India.** Optimized for the hackathon rubric (Cartesia+Bolna usage · Multilinguality · Agent Quality tested live).

Sources are cited inline. Where a field is only in the open-source models (not the rendered API ref), it's marked `[OSS]`. Where nothing is documented publicly, it says **not in docs — confirm with Buddy / check the builder's network tab.** This complements `BOLNA_API_NOTES.md` (which covers calls + executions, not agent creation).

---

## 0. TL;DR recommendation for a solo builder under a 3.5h clock

**Use the no-code builder (platform.bolna.ai) to BUILD the agent, not the API.** Honest tradeoff:

- The create-agent JSON is deeply nested (`agent_config → tasks → tools_config → {llm_agent, synthesizer, transcriber}` + `task_config` + `agent_prompts.task_1`). One wrong enum (e.g. `provider:"cartesia"` vs the API-ref's stale `[polly, elevenlabs, deepgram, styletts]` enum) → 400, and you burn clock debugging a schema you can't see.
- **Cartesia voice picking, the language pair, and the language-switch instruction are all UI affordances** (Audio Tab / Agent Tab). Picking a warm voice by ear in the Playground is faster and is itself a scored decision.
- The builder writes exactly this JSON under the hood. After it works, you can `GET /v2/agent/{id}` to read back the config (that's the `cache_bolna_cartesia_proof.py` path — and it's how you *prove* "Cartesia voice" for the rubric).

**Use the API for:** triggering test calls (`POST /call`) and pulling executions into VoiceForge — already built. Build in UI, prove + ingest via API. The schema below is your fallback / verification reference if the UI hides a flag you need.

---

## 1. Create-agent endpoint

- **Method + path:** `POST /v2/agent`
  ([api-reference/agent/v2/create](https://www.bolna.ai/docs/api-reference/agent/v2/create))
- **Base URL:** `https://api.bolna.ai`
- **Auth:** `Authorization: Bearer <BOLNA_API_KEY>` + `Content-Type: application/json` (subaccount keys prefixed `sa-`). ([introduction](https://www.bolna.ai/docs/api-reference/introduction))
- **Body (two required top-level fields):**
  - `agent_config` — `AgentConfigV2`
  - `agent_prompts` — keyed by task (`task_1`, `task_2`, …), each `{ "system_prompt": "..." }`
- **Response 200:** `{ "agent_id": "<uuid>", "status": "created" }`. Save `agent_id` — it's what `POST /call` and all execution endpoints take. ([create](https://www.bolna.ai/docs/api-reference/agent/v2/create))

### Structure (single request, not multi-part)

```
agent_config:
  agent_name, agent_welcome_message, agent_type, webhook_url,
  ingest_source_config, calling_guardrails,
  tasks: [ { task_type, toolchain, tools_config:{ llm_agent, synthesizer, transcriber, input, output }, task_config } ]
agent_prompts:
  task_1: { system_prompt }
```

Creation is **one POST** — agent + prompt + voice/ASR config all go in together. (No separate prompt/voice endpoints.) ([create](https://www.bolna.ai/docs/api-reference/agent/v2/create))

---

## 2. Grouped flag reference (flag · what · allowed/default · OUR value · why)

### 2.1 `agent_config` (top level)

| Field | What | Allowed / default | OUR value | Why |
|---|---|---|---|---|
| `agent_name` | label | string, required | `Aarti — Spice Garden Bookings` | identity |
| `agent_welcome_message` | first line the agent speaks (inbound: plays on pickup) | string | `Namaste! Spice Garden, main Aarti bol rahi hoon. Table book karni hai?` | warm Hinglish open = instant multilingual + warmth signal for the live test |
| `agent_type` | category | default `"other"` | `"other"` | cosmetic |
| `webhook_url` | post-call POST of conversation data | URI / null | leave null (we pull via `/executions`) | VoiceForge ingests by execution_id; webhook optional |
| `calling_guardrails` | `{call_start_hour, call_end_hour}` 0–23 | object | omit (inbound, 24/7 for demo) | don't gate live test calls |
| `ingest_source_config` | data source for outbound batches | api/csv/google_sheet | omit | inbound agent, N/A |
| `tasks` | pipeline (see 2.2) | array, required | one `conversation` task | single-task booking flow |

### 2.2 `tasks[0]` — task & toolchain

| Field | What | Allowed / default | OUR value | Why |
|---|---|---|---|---|
| `task_type` | task kind | `conversation` / `extraction` / `summarization` | `"conversation"` | it's a live dialog |
| `toolchain` | execution order | `{execution: "sequential", pipelines: [["transcriber","llm","synthesizer"]]}` | that default chain | standard STT→LLM→TTS |
| `tools_config` | the 3 engines + I/O | see 2.3–2.6 | — | — |
| `task_config` | realism/timing (ConversationConfig) | see 2.7 | tuned (below) | this is the "feels human" lever |

### 2.3 LLM / brain — `tools_config.llm_agent` (`LlmAgentV2` → `SimpleLlmAgent`)
Source: [create](https://www.bolna.ai/docs/api-reference/agent/v2/create), [OSS models.py](https://github.com/bolna-ai/bolna/blob/master/bolna/models.py)

| Field | What | Allowed / default | OUR value | Why |
|---|---|---|---|---|
| `agent_type` | brain type | `simple_llm_agent` / `knowledgebase_agent` (default simple) | `knowledgebase_agent` **if** you load the KB; else `simple_llm_agent` | RAG for hours/menu/policy (rubric: grounded answers) |
| `agent_flow_type` | streaming | `streaming` (default) | `streaming` | low latency |
| `provider` / `family` | LLM vendor | default `openai`/`openai` | `openai` | reliable; Hinglish-fluent |
| `model` | LLM | default `gpt-4.1-mini` (ref) / `gpt-4o-mini` (OSS) | `gpt-4o-mini` (or `gpt-4.1-mini`) | strong Hinglish + cheap + fast; bigger model only if booking logic slips |
| `max_tokens` | reply cap | int, default `100` | **`150`** | default 100 truncates a read-back of 5 booking fields; 150 keeps replies tight but complete |
| `temperature` | randomness | float, default `0.1` | **`0.3`** | 0.1 = robotic; 0.3 = warmer, still obedient to booking rules |
| `top_p` / `top_k` / `min_p` | sampling | 0.9 / 0 / 0.1 | defaults | fine |
| `presence_penalty`/`frequency_penalty` | repetition | 0 / 0 | defaults | fine |
| `request_json` | force JSON out | bool, default false | `false` | we want speech, not JSON |
| `extraction_details` | **what to pull post-call** | string, default null | set it (see §4) | structured booking capture for our eval |
| `summarization_details` | summary spec | string, null | optional short spec | feeds `summary` field |
| `routes` | semantic routing layer | object | omit | not needed for one flow |
| KB: `vector_store.provider` = `lancedb`, `provider_config.vector_id` (single) or `vector_ids` (array of UUIDs) | attach knowledge base | UUID(s) | the KB id from your uploaded hours/menu/policy docs | grounds enquiries; no hallucinated availability |

### 2.4 Synthesizer (Cartesia) — `tools_config.synthesizer`
Sources: [providers/voice/cartesia](https://www.bolna.ai/docs/providers/voice/cartesia), [OSS `CartesiaConfig`](https://github.com/bolna-ai/bolna/blob/master/bolna/models.py), [Cartesia Hinglish](https://www.cartesia.ai/india)

> **Provider-enum caveat:** the rendered API-ref enum lists only `[polly, elevenlabs, deepgram, styletts]`, but the **OSS validator accepts** `elevenlabs, pixa, cartesia, polly, azuretts, deepgram, openai, smallest, sarvam, rime` and there is a dedicated Cartesia provider doc. So `provider:"cartesia"` IS valid — the API-ref enum is stale. If a `POST /v2/agent` 400s on the provider, **confirm with Buddy / check the builder's network tab** for the exact string.

| Field | What | Allowed / default | OUR value | Why |
|---|---|---|---|---|
| `provider` | TTS vendor | `cartesia` (see caveat) | **`"cartesia"`** | rubric requires Cartesia |
| `stream` | stream audio | bool, default true | `true` | low latency |
| `buffer_size` | TTS buffer | int (~100–250) | `100` | snappier first audio |
| `audio_format` | format | `wav` (default) | `wav` | telephony default |
| `provider_config.voice_id` | **the voice** | Cartesia voice UUID | **pick a warm Indian voice in the Voice Library, paste its UUID** (see note) | first impression = scored; warm hospitality tone |
| `provider_config.voice` | display name | string | the voice's name | label only |
| `provider_config.model` | Sonic model | `sonic`, `sonic-3-preview` (both confirmed on Bolna's Cartesia page) | **`"sonic-3-preview"`** | latest, most natural/expressive; Cartesia markets it as best Hinglish/quality. Fall back to `"sonic"` if latency/stability dips live |
| `provider_config.language` | TTS language | `en`, `hi`, … `[OSS]` | **`"hi"`** for the Hindi/Hinglish path; `"en"` for the English path | Cartesia Sonic does native Hinglish — Hindi-tagged voice softens English consonants correctly. Use per-language config (§3) |
| `provider_config.speed` | rate | float, default `1.0` `[OSS]` | `1.0` (try `0.95` if it rushes) | natural pace |

**Voice pick (concrete):** Cartesia advertises native **Hinglish** in Sonic and ships an "Indian Lady" voice plus many Indian-English/Hindi voices. The **exact voice_id UUID is not published in docs** — pick a warm female Indian voice at <https://play.cartesia.ai/voices> and paste its UUID. Example UUID *format* only: `e07c00bc-4134-4eae-9ea4-1a55fb45746b`. **Do not ship a guessed UUID — copy the real one from the Voice Library / builder.** ([Cartesia Hinglish](https://www.cartesia.ai/india), [Voices](https://www.cartesia.ai/voices/))

### 2.5 Transcriber (ASR) — `tools_config.transcriber`
Sources: [create](https://www.bolna.ai/docs/api-reference/agent/v2/create), [OSS `Transcriber`](https://github.com/bolna-ai/bolna/blob/master/bolna/models.py)

| Field | What | Allowed / default | OUR value | Why |
|---|---|---|---|---|
| `provider` | STT vendor | `deepgram` (default) / `bodhi` (+ UI: assemblyai, azure, google, openai, sarvam) | **`"deepgram"`** | `nova-3` is the strongest multilingual/code-switch STT here |
| `model` | STT model | deepgram: `nova-3`, `nova-2`, `nova-2-phonecall`, … ; default `nova-2` | **`"nova-3"`** | nova-3 has the best multilingual + code-switching; `nova-2-phonecall` only if on a noisy telephony leg |
| `language` | ASR language | `en`, `hi`, `es`, `fr` (deepgram) | **`"hi"`** (covers Hindi + Hinglish) or `multi` if builder offers it | Hindi model transcribes Hinglish; see §3 caveat |
| `stream` | streaming | bool | `true` | live latency |
| `sampling_rate` | Hz | int, default 16000 | `16000` | standard |
| `encoding` | audio enc | `linear16` (default) | `linear16` | standard |
| `endpointing` | ms of silence = end of turn | int, default 500 (OSS) / 250 (ref) | **`300`** | snappier turns without chopping a thinking caller |
| `keywords` | boost terms | string / null | `"Spice Garden,booking,table,paanch,saat,reservation"` | boosts brand + Hindi numerals it might mishear |
| `task` | transcribe vs translate | `"transcribe"` (default) | `"transcribe"` | keep original language (translate would flatten Hinglish) |

> **Bodhi alternative:** for a Hindi-first agent, `provider:"bodhi"`, `model:"hi-general-v2-8khz"`, `language:"hi"` is an Indian-tuned option. **Tradeoff:** Bodhi is Hindi-only (no English path) → worse for *code-switching*. For Hinglish, **Deepgram nova-3 is the better default.** ([create](https://www.bolna.ai/docs/api-reference/agent/v2/create))

### 2.6 Telephony / call — `tools_config.input` / `output`
| Field | What | Allowed / default | OUR value | Why |
|---|---|---|---|---|
| `input`/`output.provider` | telephony | `twilio` / `plivo` / `exotel` | whatever Buddy provisioned (likely `plivo`/`twilio` for India) | inbound number routing |
| inbound vs outbound | direction | inbound = number receives calls | **inbound** | our use case |
| recording | on/off | telephony provider flag; recording_url surfaces in `telephony_data` | **on** | rubric live test + VoiceForge audio; **not a documented agent-config field — set in builder / confirm with Buddy** |
| recipient number | outbound only | E.164 in `POST /call` | N/A | inbound doesn't dial out |

### 2.7 Conversation realism — `tools_config...task_config` (`ConversationConfig`)
Source: [OSS `ConversationConfig`](https://github.com/bolna-ai/bolna/blob/master/bolna/models.py) (full field list; defaults verbatim)

| Field | What | Default | OUR value | Why (Agent Quality) |
|---|---|---|---|---|
| `optimize_latency` | latency mode | `true` | `true` | snappier |
| `hangup_after_silence` | sec of dead air → hang up | `20` | **`12`** | caller-gone cleanup without cutting a thinker |
| `incremental_delay` | ms wait on interim ASR before speaking | `900` | **`600`** | lower = more responsive; too low cuts the caller off |
| `number_of_words_for_interruption` | words from caller before agent yields (barge-in) | `1` | **`2`** | 1 = agent stops on every "haan/um"; 2 = barge-in works but ignores backchannel |
| `interruption_backoff_period` | ms pause after being interrupted | `100` | `100` | natural recovery |
| `backchanneling` | agent says "mm-hm/achha" while listening | `false` | **`true`** | huge warmth/human-feel win for the live test |
| `backchanneling_message_gap` | sec between backchannels | `5` | `5` | not spammy |
| `backchanneling_start_delay` | sec before first backchannel | `5` | `5` | default |
| `use_fillers` | filler words ("umm", "let me see") | `false` | **`true`** | sounds human while it "checks availability" |
| `ambient_noise` | low background track | `false` | `false` (or `true` for call-center realism) | optional; off is safer/clearer |
| `check_if_user_online` | ping silent caller | `true` | `true` | recovers stalls |
| `trigger_user_online_message_after` | sec silence → ping | `10` | `10` | default |
| `check_user_online_message` | the ping line | "Hey, are you still there" | `"Hello, aap line par hain?"` | Hinglish-consistent |
| `call_terminate` | hard max call length (sec) | `90` | **`300`** | 90s cuts a real booking; 300 = safe ceiling |
| `hangup_after_LLMCall` | end after a tool/LLM call | `false` | `false` | multi-turn |
| `call_cancellation_prompt` | end-call trigger phrase | null | optional | lets caller end cleanly |
| `dtmf_enabled` | keypad input | `false` | `false` | voice-only |
| `voicemail` (+ detection fields) | voicemail handling | `false` | `false` | inbound; caller is live |

---

## 3. Multilingual / Hinglish — the EXACT fields (scored criterion)

Sources: [multilingual-languages-support](https://www.bolna.ai/docs/customizations/multilingual-languages-support), [create](https://www.bolna.ai/docs/api-reference/agent/v2/create), [Cartesia Hinglish](https://www.cartesia.ai/india)

**Hard constraint (documented):** a Bolna multilingual agent supports **English + exactly ONE other language**, and switches dynamically *between those two*. For us that pair is **English + Hindi** = Hinglish. Don't try to add a third. ([multilingual](https://www.bolna.ai/docs/customizations/multilingual-languages-support))

What to set:
1. **Primary language:** Hindi (`hi`) — set via the crown/primary toggle in the Audio Tab. Second language: English (`en`). (UI; the API encodes this in the per-task synthesizer/transcriber `language` + a languages map.)
2. **Per-language STT/TTS** (each language gets its own): English → Deepgram `nova-3` + Cartesia `sonic-3-preview` `en`; Hindi → Deepgram `nova-3` (`hi`) + Cartesia `sonic-3-preview` `hi`. Cartesia Sonic does **native Hinglish** so the same Cartesia voice family carries both.
3. **Transcriber language:** set `hi` (Hindi model handles Hinglish utterances) — or `multi`/code-switch mode **if the builder exposes it** (not in the rendered API enum — **confirm with Buddy / check the network tab**; the API enum only lists `en, hi, es, fr`).
4. **Language Switching Instructions** (single shared field, Agent Tab): instruct *"Always mirror the caller's language. If they speak Hindi, reply in Hindi; English, English; mixed, mix. Never switch to a language they haven't used."* This is the field that makes the **mid-call switch** work — it's already baked into our system prompt.
5. **Welcome message** in Hinglish (above) primes the switch from word one.

> The exact JSON key for the languages map / switching-instruction field is **not in the public API ref** — the no-code builder writes it. **Confirm the field name via the builder's network tab if you must POST it directly.** For the 3.5h clock: set this in the UI.

**Test that scores points:** start a call in English, switch to Hindi mid-sentence (scenario 2 in `AGENT_BUILD.md`). Save that execution_id → VoiceForge.

---

## 4. Post-call data for our eval (keep honest)

Two agent-level levers improve what VoiceForge can extract — set both:

- **`llm_agent.extraction_details`** (string): tell the agent what structured fields to pull. For us:
  `"Extract: party_size (int), date, time, customer_name, phone_number, booking_confirmed (yes/no), outcome (booked/full/declined/enquiry_only)."`
  These surface in the execution's `extracted_data` / `agent_extraction` / `custom_extractions` fields (per `BOLNA_API_NOTES.md §3`). This is the cleanest signal for **booking-completion rate**.
- **`summarization_details`** (string): a one-line spec → populates the execution `summary` field for quick human review.

**Honesty guardrails (from `BOLNA_API_NOTES.md`, do NOT over-claim):**
- The `transcript` is a **flat string**, no per-turn timestamps. VoiceForge reconstructs turn timing from `/executions/{id}/log` event `created_at` diffs — that's reconstruction, not a native API field.
- **No interruption/barge-in telemetry exists** in the payload; "precise" transcript mode even scrubs interrupted text. We tune barge-in (`number_of_words_for_interruption`) for *behavior*, but cannot claim API-provided barge-in metrics.
- "Cartesia voice" is **proven by reading the agent config** (`GET /v2/agent/{id}`), not the execution object (which only shows synth *spend*, not provider name). Keep `synthesizer_verified=False` until that GET confirms `provider:"cartesia"`.

---

## 5. READY-TO-POST example — `POST /v2/agent`

Fill the two `<...>` placeholders (real Cartesia `voice_id` from the Voice Library; your KB `vector_id` if using RAG). System prompt is verbatim from `AGENT_BUILD.md §2`.

```json
{
  "agent_config": {
    "agent_name": "Aarti — Spice Garden Bookings",
    "agent_welcome_message": "Namaste! Spice Garden, main Aarti bol rahi hoon. Table book karni hai ya koi aur help chahiye?",
    "agent_type": "other",
    "tasks": [
      {
        "task_type": "conversation",
        "toolchain": {
          "execution": "sequential",
          "pipelines": [["transcriber", "llm", "synthesizer"]]
        },
        "tools_config": {
          "llm_agent": {
            "agent_type": "simple_llm_agent",
            "agent_flow_type": "streaming",
            "llm_config": {
              "provider": "openai",
              "family": "openai",
              "model": "gpt-4o-mini",
              "max_tokens": 150,
              "temperature": 0.3,
              "top_p": 0.9,
              "request_json": false,
              "extraction_details": "Extract: party_size (int), date, time, customer_name, phone_number, booking_confirmed (yes/no), outcome (booked/full/declined/enquiry_only).",
              "summarization_details": "One-line summary of the call outcome and the booking details captured."
            }
          },
          "synthesizer": {
            "provider": "cartesia",
            "stream": true,
            "buffer_size": 100,
            "audio_format": "wav",
            "provider_config": {
              "voice_id": "<PASTE_CARTESIA_INDIAN_VOICE_UUID>",
              "voice": "Indian Lady",
              "model": "sonic-3-preview",
              "language": "hi",
              "speed": 1.0
            }
          },
          "transcriber": {
            "provider": "deepgram",
            "model": "nova-3",
            "language": "hi",
            "stream": true,
            "sampling_rate": 16000,
            "encoding": "linear16",
            "endpointing": 300,
            "keywords": "Spice Garden,booking,table,reservation,paanch,saat,aath",
            "task": "transcribe"
          },
          "input": { "provider": "twilio" },
          "output": { "provider": "twilio" }
        },
        "task_config": {
          "optimize_latency": true,
          "hangup_after_silence": 12,
          "incremental_delay": 600,
          "number_of_words_for_interruption": 2,
          "interruption_backoff_period": 100,
          "backchanneling": true,
          "backchanneling_message_gap": 5,
          "backchanneling_start_delay": 5,
          "use_fillers": true,
          "check_if_user_online": true,
          "trigger_user_online_message_after": 10,
          "check_user_online_message": "Hello, aap abhi bhi line par hain?",
          "call_terminate": 300
        }
      }
    ]
  },
  "agent_prompts": {
    "task_1": {
      "system_prompt": "Identity: You are Aarti, the friendly booking assistant for Spice Garden, a popular multi-cuisine family restaurant in Bengaluru. You speak natural Hinglish and ALWAYS mirror the caller's language — if they speak Hindi, reply in Hindi; English, English; mixed, mix. Warm, quick, never robotic.\nObjective: Book a table. You must capture: party size, date, time, name, and phone number. Confirm availability, then read the full booking back and get a yes before ending.\nConversation paths:\n- If the requested slot is available -> confirm details, read back, get confirmation.\n- If full -> say so warmly and offer the two nearest available slots.\n- If the request is unclear or missing info -> ask ONE specific question at a time (don't ask everything at once, don't assume).\n- If they only want info (hours, location, cuisine) -> answer from the knowledge base, then offer to book.\nGuardrails: Never invent availability — use only the rules given. Never take payment or card details. Never promise anything beyond a table booking. If asked something off-topic (delivery, complaints, jobs) -> politely say you only handle table bookings and offer to note their number. Don't switch to a language the caller hasn't used.\nExit: Once the booking is confirmed and read back (or the caller declines), thank them by name and end the call cleanly."
    }
  }
}
```

**To use the knowledge base** instead of `simple_llm_agent`: set `llm_agent.agent_type:"knowledgebase_agent"` and add inside `llm_config`: `"vector_store": {"provider":"lancedb","provider_config":{"vector_id":"<KB_UUID>"}}` (upload the hours/menu/policy docs first; KB-create endpoint — **confirm path with Buddy / builder network tab**).

**Telephony providers** (`input`/`output.provider`): use whatever Buddy provisioned for the inbound India number (`twilio`/`plivo`/`exotel`). Recording is set on the telephony number, not this body — **confirm with Buddy.**

---

## 6. Field-name honesty ledger (what is NOT publicly documented)

- `voice_id` UUID for a specific Cartesia Indian voice — **pick from <https://play.cartesia.ai/voices>; don't guess.**
- `provider:"cartesia"` accepted by OSS validator + has a dedicated doc, but the **rendered API-ref synth enum is stale** — **confirm exact string via builder network tab if it 400s.**
- The **languages map / "Language Switching Instructions" JSON key** for direct POST — **not in the API ref; UI-only doc. Confirm via network tab.**
- Transcriber `multi`/code-switch language value — API enum only lists `en,hi,es,fr`; **confirm with Buddy** whether a code-switch value exists, else use `hi`.
- KB-create endpoint path / `vector_id` provisioning — **confirm with Buddy.**
- Recording on/off as an agent-config field — set on telephony number; **confirm with Buddy.**
- `toolchain.pipelines` exact default shape — inferred standard STT→LLM→TTS; **confirm via a GET on a UI-built agent.**

---

## Sources
- Create endpoint + schema: https://www.bolna.ai/docs/api-reference/agent/v2/create
- Auth/base URL: https://www.bolna.ai/docs/api-reference/introduction
- Cartesia provider (sonic / sonic-3-preview): https://www.bolna.ai/docs/providers/voice/cartesia
- Multilingual / language switching: https://www.bolna.ai/docs/customizations/multilingual-languages-support
- OSS Pydantic models (CartesiaConfig, Transcriber, ConversationConfig, provider list): https://github.com/bolna-ai/bolna/blob/master/bolna/models.py
- OSS API.md (synthesizer/transcriber/llm/task example shapes): https://github.com/bolna-ai/bolna/blob/master/API.md
- Cartesia native Hinglish: https://www.cartesia.ai/india · Voices: https://www.cartesia.ai/voices/ · play.cartesia.ai/voices
- Companion (calls/executions): docs/BOLNA_API_NOTES.md
