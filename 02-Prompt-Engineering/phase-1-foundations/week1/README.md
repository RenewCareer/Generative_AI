# Week 1 — OpenAI API and Python

**Goal:** by Friday you can call a model from Python, read everything it sends back, survive every common failure, and say what a call costs before you make it.

**Practical:** a reusable Python AI assistant → [`ai_core/assistant.py`](../ai_core/assistant.py) + terminal UI [`chat.py`](chat.py)

---

## Day 1 — Keys, environment, billing

### Concepts
| Thing | What it is | Senior rule |
|---|---|---|
| **API key** | A password that bills your account | Lives in `.env` locally, a secret manager in prod. Never in code, never in a notebook you push. |
| **Project** | Container for keys, limits and usage on platform.openai.com | One project per app, so you can see (and cap) each app's spend. |
| **Billing / credit** | Prepaid balance | Set a **monthly budget + email alert** on day one. |
| **Rate limits** | RPM (requests/min) and TPM (tokens/min) per model, by usage tier | Hitting them = HTTP 429. Higher tier with more spend history. |

### Do it
1. https://platform.openai.com → create a project → create a key **scoped to that project**.
2. Settings → Limits → set a budget (e.g. $10/month) and an alert.
3. In `phase-1-foundations/`:
   ```bash
   pip install -r requirements.txt
   cp .env.example .env      # Windows PowerShell: Copy-Item .env.example .env
   # edit .env and paste your key
   ```
4. Confirm git ignores it: `git check-ignore -v .env` must print a match.

> ⚠️ If a key ever lands in git, **revoke it first**, then clean history. Bots scrape GitHub for keys within minutes.

---

## Day 2 — First call & the response object

```bash
python -m week1.lesson_01_hello
python -m week1.lesson_02_inspect_response
```

The Responses API call in one picture:

```
client.responses.create(
    model        = "gpt-5-mini",            # which brain
    instructions = "You are a tutor...",    # developer-level rules (system prompt)
    input        = "user's request"         # or a list of {role, content} messages
)
→ Response
   ├── status          "completed" | "incomplete" | ...
   ├── output[]        reasoning items, message items (content parts), tool calls...
   ├── output_text     SDK shortcut: all text parts joined
   └── usage           input_tokens, output_tokens (+ cached, reasoning details)
```

**Key insight:** the model is stateless. "Memory" in a chat app is just *you re-sending the previous turns every call* (see `Assistant.ask`). That's why long chats get slower and more expensive — every turn re-pays for all earlier turns. (The API can also chain turns server-side with `previous_response_id`; same billing logic applies.)

---

## Day 3 — Errors

```bash
python -m week1.lesson_03_errors
```

| Error | HTTP | Retry? | Typical cause |
|---|---|---|---|
| `AuthenticationError` | 401 | ❌ | wrong/revoked key |
| `PermissionDeniedError` | 403 | ❌ | no access to model/region |
| `NotFoundError` | 404 | ❌ | typo in model name |
| `BadRequestError` | 400 | ❌ | invalid param for this model, input too long |
| `RateLimitError` | 429 | ✅ backoff — *unless* `insufficient_quota` (billing) | too many requests/tokens |
| `InternalServerError` | 5xx | ✅ | OpenAI side |
| `APITimeoutError` / `APIConnectionError` | — | ✅ | network, slow response |
| **`status="incomplete"`** | 200 ✅ | — | **no exception!** hit `max_output_tokens` |

The SDK retries the ✅ rows for you (`max_retries`, exponential backoff). Your job: configure it, translate errors into something a human can act on, and **always check `status`**.

---

## Day 4 — Tokens, latency, cost

```bash
python -m week1.lesson_04_tokens_cost_latency gpt-5-mini gpt-5-nano
```

- **Cost** = input_tokens × input_price + output_tokens × output_price (cached input is discounted). Prices in [`ai_core/pricing.py`](../ai_core/pricing.py) — verify them on the pricing page.
- **Latency** ≈ fixed overhead + (output tokens ÷ generation speed). Long answers are slow answers.
- **Reasoning models** spend hidden *reasoning tokens*: billed as output, add latency, often improve hard tasks. Control with `reasoning={"effort": ...}`.
- **Model choice** is a 3-way trade: quality ↔ latency ↔ cost. Start with a small model, move up only when you've *measured* it isn't good enough.

---

## Day 5 — Practical: the reusable assistant

```bash
python -m week1.chat
python -m week1.chat --model gpt-5-nano --system "You are a strict SQL tutor."
python -m pytest -q          # offline tests, no API key needed
```

Read [`ai_core/assistant.py`](../ai_core/assistant.py) top to bottom. The five design decisions in its docstring are the actual lesson — they're what separates a script from something you can reuse and trust.

---

## ✅ Exercises (do them — this is where learning happens)

1. **Budget guard.** Add `max_session_cost_usd` to `Assistant`; raise `AssistantError` *before* a call once the session total exceeds it. Write a test with the fake client.
2. **History window.** Long chats get expensive. Keep only the last N turns in `ask()`. Test that the 5th call sends ≤ N×2 messages.
3. **Measure it.** Run chat for 10 turns. Plot (or just print) input tokens per turn from `logs/chat.jsonl`. Explain the curve in one sentence.
4. **Model shoot-out.** Pick 3 questions you care about. Run them on 2–3 models with lesson 04. Fill a table: quality (1–5, your judgement), latency, cost. Which would you ship, and why?
5. **Break it.** Set `OPENAI_TIMEOUT_S=1` and a long prompt. What does the user see? Is the message actionable?

**Self-check — you should be able to answer without notes:**
- Why is an `incomplete` response more dangerous than a 500 error?
- What do you re-send on every chat turn, and what does that do to cost?
- Which errors should you retry, and which never?
- Why does `Assistant` accept a `client` argument?
