# Bolna Agent Builder — THE Field Reference (Hinglish restaurant booking)

> **SOURCING NOTE (this revision):** Now sourced from the **OFFICIAL per-tab
> agent-setup docs** (`bolna.ai/docs/agent-setup/*`) — the authoritative pages that
> describe the live no-code builder UI tab-by-tab. The prior pass leaned on the API
> reference + open-source Pydantic models, which were stale/incomplete for the UI. Every
> field below cites the official agent-setup doc URL it came from. Where the official doc
> CONTRADICTED the prior reference, it's flagged inline as **[CHANGED]** and summarized in
> the changelog at the bottom.

**Research date:** 2026-06-13. **Use case this is optimized for:** INBOUND restaurant
table-booking + enquiry voice agent · **Hinglish (Hindi primary + English, mid-call
switching)** · **Cartesia** `sonic-3-preview` voice · India · scored on the hackathon
rubric (Cartesia+Bolna usage · Multilinguality · Agent Quality tested live · Scale-Up).

This is the **field bible Spike keeps open while building in the no-code builder**
(platform.bolna.ai). It is organized by the **8 live builder UI tabs**, in the exact
order and with the exact subtitles the official overview page lists them:

1. **Agent** — "Prompts & welcome message"
2. **LLM** — "Model & knowledge base"
3. **Audio** — "Voice & transcription"
4. **Engine** — "Latency & interruptions"
5. **Call** — "Telephony & voicemail"
6. **Tools** — "Functions & APIs"
7. **Analytics** — "Webhooks & extraction"
8. **Inbound** — "Caller matching"

Plus the **Call History** view (not a tab — a separate logs page).

Row format: **field · what it does (from the official doc) · type / options · default ·
RECOMMENDED for us · why.** CONFIRMED-from-live-screenshot values are kept verbatim and
marked **[SCREENSHOT]**.

---

## ⭐ The 8 fields that win / lose points (high-leverage box)

| # | Field (tab) | Set it to | Why it scores |
|---|---|---|---|
| 1 | **TTS Provider + Voice + Model** (Audio) | Cartesia · a warm Indian voice · `sonic-3-preview` | Cartesia usage is a scored axis; the voice is the judge's first impression. Audio tab confirms **Cartesia** is a first-class TTS provider in the picker. |
| 2 | **Primary + Secondary Language** (Audio) | Primary **Hindi**, secondary **English**, each with its own per-language STT/TTS tab | Multilinguality axis. The Audio tab has explicit "+ Add Language" and **per-language STT/TTS tabs** — an official UI affordance. |
| 3 | **STT Provider + Model** (Audio) | Deepgram `nova-3`, language `multi` (or `hi`) | nova-3 `multi` does real-time Hindi↔English code-switching — biggest Hinglish lever. Audio tab lists Deepgram in the provider dropdown. |
| 4 | **Language Switching Instructions** (Agent) | "mirror caller's language; never switch to one they haven't used" | Official Agent-tab field: "a single shared field… describes when agent switches languages mid-call." Makes the demo switch fire. |
| 5 | **Total Call Timeout** (Call) | **300s** **[SCREENSHOT]** | Doc's own guidance: "300s (5 min) for support." A truncated live call tanks Agent Quality. |
| 6 | **Tokens Generated / max tokens** (LLM) | **300** (doc recommends 300–500 for concise) | Official LLM-tab recommendation is 300–500; keeps a 5-field booking read-back complete. |
| 7 | **Interruption Threshold + Endpointing + Linear Delay** (Engine) | interruption **2** · endpointing **300ms** · linear delay **500ms** **[SCREENSHOT]** | The "feels human" trio. Engine-tab doc recommends endpointing 200–300ms, linear delay 400–500ms. Matches our live screenshot. |
| 8 | **Welcome Message + Canvas prompt + Extraction** (Agent/Analytics) | Hinglish greeting, mirror-language canvas, booking-field extractions | Welcome primes the multilingual switch from word one; Analytics-tab extractions give VoiceForge clean booking-outcome data. |

---

## TAB 1 — Agent ("Prompts & welcome message")

Source: https://www.bolna.ai/docs/agent-setup/agent-tab (and overview for header).

| Field | What it does (official) | Type / options | Default | RECOMMENDED | Why |
|---|---|---|---|---|---|
| **Agent Welcome Message** | "The first thing callers hear when they connect." Supports dynamic variables `{variable_name}`. | text input + `{var}` | not specified | `"Namaste! Spice Garden, main Aarti bol rahi hoon. Table book karni hai ya koi aur help chahiye?"` | Warm Hinglish open primes the language-mirror from word one. |
| **Canvas (System Prompt)** | Per-language prompt editor: "Agent activates the matching prompt when speaking in that language." Rich-text editor with a **token counter** (bottom-right). Suggested structure sections: **Personality, Context, Instructions, Guardrails**. Supports `{variable_name}` for variables and **`@` for modules/functions**. | rich-text, per-language | required | The "Aarti" prompt structured as Personality / Context / Instructions / Guardrails: identity + capture 5 fields + availability rules + mirror-language + no-payment guardrail + clean exit. | This + extraction is the Agent-Quality core. Use the doc's 4-section structure. |
| **Language Tabs** | Separate prompt tab per language; "+ Add Language" adds one; **crown icon** sets the primary (marked "(Primary)"); "x" removes. **Languages sync between Agent and Audio tabs.** | language tabs | — | Primary **Hindi** (crown), add **English** | Hinglish = Hindi + English. Inbound Indian diner → Hindi-first open. |
| **Agent Name** (per-language) | "Name the agent uses to identify itself in this language." | string per lang | — | "Aarti" (both langs) | identity consistency. |
| **Handoff Message** (per-language) | "Message spoken when switching **away from** this language." Supports `{agent_name}`, `{language}`. | string per lang | — | optional; add a Hindi line if time | nice-to-have. |
| **Language Switching Instructions** | "A **single shared field** that applies to all languages." Describes when the agent switches languages mid-call; includes trigger conditions, fallback behavior, default rules. | string (one shared) | — | `"Always mirror the caller's language. Hindi→Hindi, English→English, mixed→mix. Never switch to a language the caller hasn't used."` | The field that makes the **mid-call switch** fire — the demo moment. |
| **Prompt Variables (testing)** | Auto-populated from `{var}` in the prompt; editable for preview; includes a **Timezone selector** (e.g. "Asia/Kolkata UTC+05:30"). | per-var inputs | — | set timezone **Asia/Kolkata** | correct timezone for booking read-backs in preview. |
| **Hangup Using Prompt** | Toggle for context-aware call termination; define completion conditions with multilingual closing lines; "prevents reliance on silence detection or timeouts." | toggle + condition(s) | off | **ON** — condition: "booking read back and caller agreed, or caller declined"; closing line in hi/en | Clean prompt-driven hangup reads as polished in the live test. |

### Modules library (the `@` / "Browse Modules" feature)
Source: agent-tab doc + https://www.bolna.ai/docs/prompting-guide (the per-tab page points here for the full list).

- Type **`@`** in the canvas to "browse and select existing modules, functions, or variables. You cannot create new items with `@`." Or click **"Browse Modules"** (top-right of the prompt section) to open the full library.
- Modules are organized by category: **Collection · Optional · Flow · Sector · Universal.**
- **[CHANGED]** The prior reference invented module names ("Flow: Inbound Booking", "Identity and Persona", "Guardrails Core", "Acknowledgement Style"). **Those do NOT exist in the docs.** The actual documented modules are:
  - **Collection:** Email Collection · Number Collection · Name Collection
  - **Optional:** Persuasion · Variables Reference · Pricing and Plans · Objection Handling · Knowledge Base · **Hang Up Prompt** · Handover and Escalation · **FAQ Block** · **Extraction Schema** · Eligibility Criteria · Compliance Healthcare · Compliance Finance · Closing Branches
  - **Flow:** Outbound Survey · Outbound Lead · **Inbound Verification** (← there is NO "Inbound Booking" Flow module; **Inbound Verification** is the closest)
  - **Sector / Universal:** category buckets; specific names not enumerated in the docs.
- **RECOMMENDED modules for us:** **Name Collection** + **Number Collection** (capture caller name/phone), **FAQ Block** (hours/menu enquiries), **Extraction Schema** (booking-outcome fields), **Hang Up Prompt** (clean close), optionally **Handover and Escalation** (pairs with Transfer Call). Build the booking flow in the canvas yourself — no prebuilt "Inbound Booking" module exists.

### Agent header / testing affordances (overview page)
Source: https://www.bolna.ai/docs/agent-setup/overview.
**Agent Name · Agent ID** (copyable, for API) **· Share · Cost per min · Routing (region) · Provider Status** (Transcriber/LLM/Voice/Telephony indicators). Testing: **Chat with agent** (text test), **Get call from agent** (test call to your phone), **Test via browser** (in-browser call), **Save agent**, **See all call logs**. New agents start in **"draft"** status until saved. **+ New Agent** supports **Auto Build / Pre-built templates / from scratch**; **Import** by agent ID.

---

## TAB 2 — LLM ("Model & knowledge base")

Source: https://www.bolna.ai/docs/agent-setup/llm-tab.

| Field | What it does (official) | Type / options | Default | RECOMMENDED | Why |
|---|---|---|---|---|---|
| **Provider** | "Chooses the AI service provider." | dropdown: **Azure, OpenAI, Anthropic, Groq, and others** | not specified | **OpenAI** | reliable, Hinglish-fluent, default-supported. |
| **Model** | "Picks the specific language model variant." Doc example: "gpt-4.1-mini cluster". | dropdown (varies by provider) | not specified | **gpt-4.1-mini** | strong Hinglish, cheap, fast. The doc's own example model. |
| **Tokens Generated** | "Max tokens per LLM output." | slider / numeric | not specified | **300** (doc recommends **300–500** "for concise responses") | **[CHANGED]** prior ref said default 100 / use 150. Official doc recommends **300–500**. 300 keeps a 5-field read-back complete. |
| **Temperature** | "Controls creativity/randomness." | slider / numeric | not specified | **0.3** (doc recommends **0.3–0.5** "for balanced responses") | **[CHANGED]** prior ref said default 0.1. Doc recommends 0.3–0.5; 0.3 = warm but obedient. |
| **Knowledge Base (multi-select)** | "Connects knowledge bases to provide accurate, contextual information." **Multiple KBs can be connected simultaneously.** Supported formats: **PDFs, URLs.** | multi-select dropdown | none | **attach the hours/menu/policy KB** (PDF + URL) | Confirms the live screenshot: **KB is connected in the LLM tab** (PDF/URL). Grounds enquiries, no hallucinated hours. |

> No other fields are documented on the official LLM-tab page. The prior reference's
> `top_p / top_k / min_p / presence_penalty / frequency_penalty / request_json /
> base_url / reasoning_effort / verbosity / routes / agent_type` are **API/OSS-level
> knobs, not surfaced on this builder tab** — moved to the honesty ledger.

---

## TAB 3 — Audio ("Voice & transcription")

Source: https://www.bolna.ai/docs/agent-setup/audio-tab.

### 3a. Languages section
| Field | What it does (official) | Type / options | Default | RECOMMENDED | Why |
|---|---|---|---|---|---|
| **Primary Language** | "The language your agent uses at the start of every conversation." | dropdown, **18 supported languages** | **English** | **Hindi** | Hindi-first inbound open. |
| **Secondary Languages** | "Allow agent to understand/respond when caller switches languages mid-call." Add via **"+ Add Language"**. | add button | none | add **English** | the second half of Hinglish. |
| **Crown Icon** | "Make a secondary language primary." | toggle | — | crown on **Hindi** | matches Agent-tab primary. |

> **Note:** STT and TTS are each configured **per language** via independent **Language Tabs** in this section — set Deepgram nova-3 + Cartesia for BOTH `hi` and `en`.

### 3b. Speech-to-Text (Transcriber)
| Field | What it does (official) | Type / options | Default | RECOMMENDED | Why |
|---|---|---|---|---|---|
| **Provider** | "Transcription provider." | **AssemblyAI, Azure, Deepgram, ElevenLabs, Gladia, Google, OpenAI, Sarvam, Smallest** | not specified | **Deepgram** | nova-3 has the strongest code-switching. |
| **Model** | Specific transcription model. | varies by provider | not specified | **nova-3** (language `multi`, fallback `hi`) | nova-3 `multi` = real-time Hindi↔English code-switching, the biggest STT lever. |
| **Keywords** | "Boost recognition accuracy for specific words." Format **`word:boost_value`**. **Deepgram only.** | text (Deepgram only) | none | `Spice Garden:2,booking:1,table:1,paanch:2,saat:2,aath:2` | **[CHANGED]** prior ref used a bare comma list. Official format is **`word:boost_value`**. Boosts brand + Hindi numerals. |
| **Language Tab** | "Configure STT settings per language independently." | per-lang tabs | — | set nova-3 on both hi + en | per-language STT is an explicit UI affordance. |

### 3c. Text-to-Speech (Synthesizer)
| Field | What it does (official) | Type / options | Default | RECOMMENDED | Why |
|---|---|---|---|---|---|
| **Provider** | "TTS service selection." | **AzureTTS, Cartesia, ElevenLabs, Sarvam** | not specified | **Cartesia** | rubric requires Cartesia; it's a first-class option in the official picker. |
| **Model** | Specific voice synthesis model. | varies by provider | not specified | **sonic-3-preview** | latest/most natural Cartesia model; native Hinglish. Fall back to `sonic` if latency dips. |
| **Voice** | "Choose a Voice" dropdown with **preview buttons** and gender filters (**All / Male / Female / Neutral** tabs). | searchable dropdown | not specified | **a warm Indian voice** (preview a few; pick by ear) | first impression = scored. Use the in-builder preview to choose; don't ship a guessed UUID. |
| **Buffer Size** | "Audio buffered before playback begins" — smoothness vs. delay. | numeric slider (**150–250 recommended**) | not specified | **150** | snappier first audio within the recommended band. |
| **Speed Rate** | "Speaking speed. `1` is natural pace." (>1 faster, <1 slower) | numeric | **1** | **1** (try **0.95** if it rushes Hindi numerals) | natural pace. |
| **Similarity Boost** | "How closely the output matches the original voice sample." | slider | not specified | default | leave unless the voice drifts. |
| **Stability** | "Voice consistency across sentences." | slider | not specified | default | leave default. |
| **Style Exaggeration** | "Emphasis on stylistic characteristics. `0` is neutral." | slider | **0** | **0** | neutral, safe for the demo. |
| **Preview Welcome Message** | "Test selected voice with agent's welcome prompt." | button | — | **use it** | hear the Hinglish welcome in the chosen voice before saving. |
| **Add Voice +** | "Add a custom voice by ID or clone one from an audio sample." Add-by-ID tab (**Voice ID** text input) or Clone tab (**Voice Name, Description, Sample Language** [18 langs], **Audio Upload** max **10 MB**). | dialog | — | **skip** (use library voices) | cloning is out of scope for the sprint. |
| **Language Tab** | "Configure TTS settings per language independently." | per-lang tabs | — | set Cartesia sonic-3-preview on both hi + en | per-language TTS is an explicit UI affordance. |

> **[CHANGED] / honesty:** the official Audio-tab doc does **NOT** expose
> `voice_id` / `buffer_size` (chars) / `audio_format` / `stream` / `caching` /
> `sampling_rate` / `encoding` / `endpointing` (STT) as named fields — those were
> from the API/OSS models. The UI uses **Voice** (picker), **Buffer Size** (150–250),
> **Speed Rate**, and the ElevenLabs-style **Similarity Boost / Stability / Style**
> sliders. **Endpointing lives in the ENGINE tab, not Audio** (see Tab 4).

---

## TAB 4 — Engine ("Latency & interruptions")

Source: https://www.bolna.ai/docs/agent-setup/engine-tab.

| Field | What it does (official) | Type / options | Default | RECOMMENDED | Why |
|---|---|---|---|---|---|
| **Generate Precise Transcript** | "Enable for higher accuracy transcription. Essential for compliance and call analytics." | toggle | not specified | **ON** | cleaner transcript for VoiceForge eval. |
| **Interruption Threshold** | "Number of words to wait before considering user input as an interruption." Stopwords ("Stop", "Wait", "Hold On") always pause the agent immediately. | slider (numeric words) | not specified | **2** **[SCREENSHOT]** | 1 = stops on every "haan/um"; 2 = real barge-in, ignores backchannel. Matches live screenshot. |
| **Response Rate** | Latency preset. | **Balanced / Fast / Custom** | not specified | **Custom** | so we can set endpointing + linear delay to our screenshot values. |
| **Endpointing (ms)** | "Wait time before generating response." | slider (ms), doc rec **200–300ms** | not stated | **300ms** **[SCREENSHOT]** | snappy turns without chopping a thinking caller. **[CHANGED]** — this is an **Engine-tab** field, not Audio/transcriber as the prior ref placed it. |
| **Linear Delay (ms)** | "Accounts for mid-sentence pauses." | slider (ms), doc rec **400–500ms** | not stated | **500ms** **[SCREENSHOT]** | **[CHANGED]** prior ref called this `incremental_delay` and recommended 600. Official name is **Linear Delay**, recommended 400–500; live screenshot = 500. |
| **User Online Detection** | "Detect when users go silent and automatically re-engage them." | toggle | not specified | **ON** **[SCREENSHOT]** | recovers stalls; live screenshot confirms ON. |
| **Detection Message** | Customizable re-engagement prompt; supports multi-language. | text (per-lang) | not specified | `"Hello, aap line par hain?"` | Hinglish-consistent re-engagement. |
| **Invoke message after (seconds)** | "Control when the check triggers." | numeric (s), doc rec **8–15s** | not specified | **10** | within the recommended band. |

> **[CHANGED] / honesty:** the official Engine-tab page documents **only** the fields
> above. **Backchanneling, use_fillers, ambient_noise, call_terminate, and voicemail
> are NOT on the Engine tab** — the prior reference put them here. Per the official docs:
> **ambient noise + voicemail + DTMF + total call timeout + hangup-on-silence live on the
> CALL tab** (Tab 5). Backchanneling/fillers are not surfaced as named Engine-tab fields
> in the official doc (API/OSS only — see ledger).

---

## TAB 5 — Call ("Telephony & voicemail")

Source: https://www.bolna.ai/docs/agent-setup/call-tab.

| Field | What it does (official) | Type / options | Default | RECOMMENDED | Why |
|---|---|---|---|---|---|
| **Telephony Provider** | "Set up your telephony provider." | dropdown: **Plivo, Twilio, Vobiz** (and others) | not specified | **Vobiz** **[SCREENSHOT]** | the carrier on our inbound India number, confirmed in the live builder. |
| **Noise Cancellation** | "Filter background noise for clearer calls." | slider 0–100 (example 70) | not specified | **70** | restaurant ambient noise on the caller's side; 70 is the doc's example. |
| **Voicemail Detection** | "Detect voicemail systems to avoid awkward messages." | toggle | Off (implied) | **OFF** | inbound; caller is live. |
| **Keypad Input (DTMF)** | "Accept touch-tone input for IVR-style menus." | toggle | Off (implied) | **OFF** | voice-only booking. |
| **Auto Reschedule** | "Automatically retry failed calls later." | toggle | Off (implied) | **OFF** | inbound; no outbound retries. |
| **Ambient Noise** | "Add background ambient noise… for a more natural, human-like experience." | dropdown: **None / Coffee Shop / Office Ambience / Call Center / Custom**; WAV/MP3 max 10 MB | **None** | **None** (or Call Center only if you want realism) | clearer is safer for the demo. **[CHANGED]** ambient noise is a **Call-tab** field, not Engine. |
| **Final Call Message & Language** | "Configure the last message your agent says before disconnecting." Multi-language. | text + lang selector | not specified | `"Shukriya! Aapki booking confirm ho gayi. Have a great day!"` (hi/en) | polished close; pairs with Hangup-Using-Prompt. |
| **Hangup on User Silence** | "Auto-hangup after X seconds of silence." | slider (s), doc rec **6–10s** | not specified | **15s** **[SCREENSHOT]** | live screenshot = 15s (slightly above the doc's 6–10 band — we keep the confirmed value; a thinking diner shouldn't be cut). |
| **Total Call Timeout** | "Maximum call duration in seconds." | slider (s), doc rec **300s (5 min) for support, higher for sales** | not specified | **300s** **[SCREENSHOT]** | ⚠️ a short cap cuts a real booking mid-confirmation; 300s = doc's recommended support ceiling, matches screenshot. |
| **Outbound Call Timing Restrictions** | "Restrict outbound calls to a specific time window" (Allowed Time Window start/end, validated against recipient local timezone). | toggle + time range | Off | **OFF (N/A)** | inbound agent doesn't dial out. |

---

## TAB 6 — Tools ("Functions & APIs")

Source: https://www.bolna.ai/docs/agent-setup/tools-tab · transfer-calls doc · custom-function-calls doc.

Click **"+ Add"** next to any tool to enable it. Three **built-in** tools + **Custom Functions**.

### Built-in tools
| Tool | What it does (official) | Config fields | RECOMMENDED |
|---|---|---|---|
| **Calendar Availability** | "Check open meeting slots from **Cal.com** in real-time during a call." | The tools-tab page does **not enumerate** the config fields; in the builder it's the Cal.com-backed availability check (pairs with Book Appointment; shares Cal.com connection: API key + event type + timezone). | **Add it** — this is the live "table free?" check. Confirm exact field labels in the builder (API key / event type / timezone). |
| **Book Appointment** | "Create calendar bookings directly via **Cal.com** during the conversation." | Same — page doesn't enumerate fields; in the builder this is the Cal.com **API key + event (event type) + timezone** trio (confirmed from live screenshots). | **Add it** — this is how a confirmed table booking is written to Cal.com. |
| **Transfer Call** | "Route the call to a human agent or another phone number." | **Description (Prompt)** — "Tell the LLM when to trigger the transfer" (e.g. transfer to a human/sales). **Transfer to phone number** — destination in international format (`+19876543210`). **Pre-tool message** — what the agent says while transferring (multi-language via "+ Add"). | **Add it** — restaurant manager handoff for complex/large-party requests. Description: "Transfer when the caller asks for a manager or a party larger than we can book." |

> Note: tools-tab doc says the official **Cal.com config field list is not enumerated on
> the agent-setup page** — it points to the dedicated tool-calling guides. The
> **API key / event / timezone** trio is **CONFIRMED from the live screenshots**, so we
> keep it; confirm exact labels when wiring.

### Custom Functions
| Field | What it does (official) | Type | RECOMMENDED | Why |
|---|---|---|---|---|
| **Write Manually** | "Open a JSON editor where you define the function schema from scratch." | mode | use for `save_booking` if not using Cal.com Book Appointment | full control. |
| **Generate from cURL** | "Paste an existing cURL command. Bolna will parse the request and auto-generate a function schema." | mode | fastest if you already have a booking endpoint as a cURL | one-paste setup. |
| **name** (mandatory) | Unique fn id. | string | `check_availability`, `save_booking` | the LLM calls it by name. |
| **description** (mandatory) | When to call it. | string | "Check if a table is free for the given date/time/party_size." | a good description = reliable triggering. |
| **key** (mandatory) | "Must be `custom_task` — Do not change this value." | const `custom_task` | **`custom_task`** | required exact value. |
| **method** (mandatory) | HTTP verb. | GET/POST/… | GET for check, POST for save | semantics. |
| **parameters** | Property definitions (JSON-Schema). | object | `party_size` (int), `date`, `time`, `customer_name`, `phone_number` | what the agent collects. |
| **pre_call_message** | Spoken while the API runs. | string | `"Ek minute, main check karti hoon..."` | covers latency, sounds human. |
| **url** | Your endpoint. | URL | your availability/booking API | where the call goes. |
| **api_token** | Auth header. | string | `Bearer <token>` if needed | secures the endpoint. |
| **headers** | Extra HTTP headers. | object | `{}` or `{"Content-Type":"application/json"}` | optional. |
| **Pre-call webhook URL / parameters** | Optional notify-before-main-call hook; params use **`%(field)s`** substitution (JSON template). | URL / object | omit for booking | not needed. |

> For our build, **prefer the built-in Cal.com Book Appointment + Calendar Availability**
> over hand-rolled custom functions — fewer moving parts, and they're the documented,
> first-class booking path. Keep a Custom Function only if you need a non-Cal.com endpoint.

---

## TAB 7 — Analytics ("Webhooks & extraction")

Source: https://www.bolna.ai/docs/agent-setup/analytics-tab.

| Field | What it does (official) | Type / options | Default | RECOMMENDED | Why |
|---|---|---|---|---|---|
| **Webhook URL** | "Receive all execution data for the agent in real-time… essential for CRM integrations and live dashboards." | URL endpoint | none | **VoiceForge ingest webhook URL** | live booking-outcome ingest the moment a call ends. |
| **Summarization (toggle)** | "Automatically generate a summary of every conversation." | boolean | **Off** | **ON** | one-line outcome into the execution summary. |
| **Extraction Categories** | "Organize related data capture templates." Doc examples: Agent Handover, Lead Qualification, Visit Details, Customer Sentiment. | text grouping | none | a **"Booking"** category | groups our extractions. |
| **Extraction Name** | "Descriptive identifier for captured data point." | text | user-defined | `party_size`, `date`, `time`, `customer_name`, `phone_number`, `booking_confirmed`, `outcome` | becomes the key in `extracted_data`. |
| **Extraction Prompt** | "Instructions guiding the LLM on what to extract." | text | none | e.g. "Extract the number of guests the caller booked for." | guides extraction. |
| **Answer Type** | Response format. | **Free Text** (open-ended) / **Pre-defined** (categorical) | not specified | **Pre-defined** for `outcome` & `booking_confirmed`; **Free Text** for name/date/time | **[CHANGED]** the UI labels are **Free Text / Pre-defined**, not "subjective / objective" (those are the API-level keys in the result payload). |
| **Model** | LLM doing the extraction. | model selector | **gpt-4.1-mini** | default | default is fine. |

> **Confirms live screenshot:** extractions live in the **Analytics tab**, and the result
> surfaces as **`extracted_data`** on `GET /executions/{id}` (and the webhook). In that
> payload each extraction carries `subjective` / `objective` / `confidence` /
> `confidence_label` / `reasoning_*` keys — those are the **API result keys**, distinct
> from the **UI's "Free Text / Pre-defined"** Answer-Type selector above.

**Recommended extraction set:** under a **Booking** category — `party_size`, `date`,
`time`, `customer_name`, `phone_number` (Free Text) + `booking_confirmed` (Pre-defined
yes/no) + `outcome` (Pre-defined: booked / full / declined / enquiry_only). Plus
**Summarization ON**.

---

## TAB 8 — Inbound ("Caller matching")

Source: https://www.bolna.ai/docs/agent-setup/inbound-tab.

| Field | What it does (official) | Type / options | Default | RECOMMENDED | Why |
|---|---|---|---|---|---|
| **Database for Inbound Phone Numbers** | "Match incoming calls to users and preload their data before call starts." | **Internal APIs / CSV Upload / Google Sheet** | not specified | **skip for demo** (no caller DB) | personalization is optional; judges may call cold. |
| **API Endpoint URL** (Internal APIs) | "Receives caller data requests." Auto-passed params: `contact_number`, `agent_id`, `execution_id`. | URL | none | N/A | no caller DB for the demo. |
| **Auth Token** (Internal APIs) | "Secure authentication via Bearer token." | string | none | N/A | — |
| **CSV File Upload** | "Upload user database file." Required column **`contact_number`**. | CSV | none | optional | preload demo callers if you want personalization. |
| **Google Sheet URL + Sheet Name** | "Connect public spreadsheet as database" + exact tab name. | URL + text | none | optional | alternative to CSV. |
| **"Allow Calls Only from Database"** | "Restrict calls to database phone numbers only." | toggle | **Off (not restricted)** | **OFF** | judges may call from any number — must not be restricted. |
| **Maximum Calls per Phone Number** | "Limit repeated calls from single number." `-1` = unlimited. | integer | not specified | **-1** | don't throttle live test calls. |
| **Always-Allow List** | "Phone numbers that bypass all call limits." | phone list | **empty** | add the demo phones | guarantees your test calls connect. |

> **Binding the number:** the Inbound tab is about *caller matching*; the actual
> **assign-a-phone-number-to-this-agent** step is done via the inbound setup (UI button /
> `POST /inbound/setup`). Confirm the India inbound number is bound before the live test.

---

## Call History (logs view — not a tab)

Source: https://www.bolna.ai/docs/call-history. (Note: there is **no**
`agent-setup/call-history` page — that slug **404s**; the official content lives at
`/docs/call-history`, reachable via "See all call logs" / the left-nav "Call History".)

- **Performance metrics:** Total Executions · Total Cost · Total Duration · Status Breakdown (Error / Completed / No-Answer) · Avg Cost · Avg Duration.
- **Filters:** Agent · Batch · Date Range · Group By · Call Type (inbound/outbound) · Status · Provider · **Search by Execution ID**.
- **Table columns:** Execution ID · User Number · Conversation Type (e.g. "plivo outbound", "twilio inbound") · Duration (s) · **Hangup By** (Callee / Carrier / Plivo …) · Batch · Timestamp · Cost · Status.
- **Call details:** **Conversation Data** → Recording (waveform, play/copy/download) + Transcript (Assistant/User). **Trace Data** → Timestamp · Log Data · Direction (request/response) · **Component** (synthesizer/transcriber/llm) · Provider · Reasoning Content. **Raw Data** → full JSON matching the Get Execution API response.
- **Quick actions:** Refresh · **Stop Queued Calls** · **Download Records** (CSV export).

> This confirms VoiceForge's read path: recording + transcript + per-component trace +
> raw execution JSON are all available; the **Raw Data** view == the `GET /executions/{id}`
> shape that carries `extracted_data`.

---

## Honesty ledger — undocumented / unverifiable / UI-vs-API gaps

| Item | Status |
|---|---|
| **Cal.com config fields** (API key / event type / timezone) for Calendar Availability + Book Appointment | The official tools-tab page does **NOT enumerate** them; it points to the tool-calling guides. The trio is **CONFIRMED from live screenshots** — confirm exact labels when wiring. |
| **Transcriber `language: multi`** selectable in the builder | Deepgram nova-3 supports `multi`; the audio-tab doc lists Deepgram + per-language tabs but does **not explicitly list `multi`** as a selectable value — **confirm in builder; else use `hi`.** |
| **A specific Cartesia voice_id** | The audio-tab UI uses a **Voice picker with preview**, not a raw UUID field — **pick by ear in the builder; don't ship a guessed UUID.** |
| **Backchanneling / use_fillers** | **NOT documented on the Engine-tab (or any agent-setup) page.** API/OSS-only. The prior ref claimed they were Engine-tab toggles — **unverified in the official UI docs.** |
| **call_terminate / hangup_after_silence as ENGINE fields** | **[CHANGED]** these are on the **CALL tab** (Total Call Timeout / Hangup on User Silence), not Engine. |
| **LLM-tab extra knobs** (top_p, penalties, request_json, base_url, agent_type, routes, reasoning_effort) | **NOT on the official LLM-tab page** — API/OSS only. Don't expect them in the builder. |
| **Audio low-level knobs** (voice_id, audio_format, stream, caching, sampling_rate, encoding) | **NOT named on the official Audio-tab page** — API/OSS only. UI exposes Voice/Buffer Size/Speed/Similarity/Stability/Style instead. |
| **"Inbound Booking" Flow module** | **Does NOT exist.** Documented Flow modules are Outbound Survey / Outbound Lead / **Inbound Verification**. Build the booking flow in the canvas. |
| **Sector / Universal module names** | Categories exist; **individual names not enumerated** in the docs — browse in-builder. |
| **`agent-setup/call-history` page** | **404** — content lives at `/docs/call-history`. |
| **Custom-function synchronous/blocking behavior** | Not stated on agent-setup pages; the function result is fed to the LLM, but authoritative-sync behavior — **confirm in builder.** |

---

## Sources (master list — official agent-setup docs)
- Overview: https://www.bolna.ai/docs/agent-setup/overview
- Agent tab: https://www.bolna.ai/docs/agent-setup/agent-tab
- LLM tab: https://www.bolna.ai/docs/agent-setup/llm-tab
- Audio tab: https://www.bolna.ai/docs/agent-setup/audio-tab
- Engine tab: https://www.bolna.ai/docs/agent-setup/engine-tab
- Call tab: https://www.bolna.ai/docs/agent-setup/call-tab
- Tools tab: https://www.bolna.ai/docs/agent-setup/tools-tab
- Analytics tab: https://www.bolna.ai/docs/agent-setup/analytics-tab
- Inbound tab: https://www.bolna.ai/docs/agent-setup/inbound-tab
- Call History: https://www.bolna.ai/docs/call-history  (NB: `agent-setup/call-history` 404s)
- Supporting (module list / tool config): Prompting Guide https://www.bolna.ai/docs/prompting-guide · Transfer Calls https://www.bolna.ai/docs/tool-calling/transfer-calls · Custom Functions https://www.bolna.ai/docs/tool-calling/custom-function-calls
- Companions in this repo: docs/BOLNA_API_NOTES.md (calls/executions) · docs/BOLNA_AGENT_CONFIG.md (raw create JSON)
