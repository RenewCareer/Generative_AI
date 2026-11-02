# Module 06: Backend Application Interfaces

**Slides:** [presentation.pptx](presentation.pptx) | **Time:** 3 hours | **Next:** [Module 07](../07_Evaluations%20security%20and%20reliability/README.md)

## Learning outcomes

By the end, students can:

- Design clear API contracts with FastAPI and Pydantic
- Stream tokens to a browser with Server-Sent Events
- Add authentication, rate limits, consistent errors, and background jobs
- Explain why a blocking model call inside `async def` hurts every user

## Session plan

| Time | Activity | Material |
|---|---|---|
| 15 min | Slides | `presentation.pptx` |
| 30 min | Request lifecycle | `lessons/01_request_lifecycle.py` |
| 30 min | Streaming | `lessons/02_streaming_sse.py`, `project/static/index.html` |
| 15 min | Background jobs | `lessons/03_async_jobs.py` |
| 30 min | Run the app, use the UI and docs | `project/main.py` |
| 45 min | Lab | Below |

## Concepts

**Cheap checks first.** Authentication, rate limits and validation all run before the model, so that bad requests
cost nothing. Authentication runs first, so that unknown callers cannot use up anyone's rate limit.

**Contracts.** Pydantic models define what the API accepts, and they generate the `/docs` page.
`role: Literal["user", "assistant"]` is a real security control: clients cannot send a `system` message
and rewrite your instructions. Limits on `max_tokens` and message size bound what a request can cost.

**Three response patterns.**

| Pattern | Use for | Note |
|---|---|---|
| Request/response | Short calls, classifiers | Simple for clients |
| Streaming (SSE) | Chat | One-way over plain HTTP, and simpler than WebSockets |
| Background job | Work taking minutes | 202, then poll. Needs a durable queue in production |

Use WebSockets only for two-way real-time needs, such as voice.

**Errors while streaming.** Once streaming starts, the status is already 200, so a failure must travel as an event inside the
stream. A client should treat a stream with no `done` event as incomplete.

**Sync and async.** The LLM client here is synchronous, so the endpoints are plain `def`, which FastAPI runs in a thread
pool. An `async def` calling a sync client blocks the event loop, and freezes every other user. This is one of the most common
FastAPI bugs.

**Keys stay on the server.** A browser must never see your provider key, since anyone can read it from browser code.

## Run it

```powershell
python lessons/01_request_lifecycle.py
python lessons/02_streaming_sse.py
python lessons/03_async_jobs.py
python -m pytest tests
python -m uvicorn project.main:app --reload --port 8000
```

Then open http://localhost:8000 for the chat UI (API key `dev-key-123`), and http://localhost:8000/docs for the API docs.

Try it from a terminal:

```powershell
curl.exe -N -X POST http://localhost:8000/v1/chat/stream -H "Content-Type: application/json" -H "X-API-Key: dev-key-123" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hello\"}]}"
```

### What to expect

```
data: {"delta": "Streaming "}

data: {"delta": "makes "}

data: {"done": true}
```

## A real bug to discuss

The first version of `main.py` started with `from __future__ import annotations`. That turned the local `Client` annotation into
a string FastAPI could not resolve, so it treated the dependency as a required query parameter, named `_`. **Every request returned 422.**
The server started normally. Only running real requests revealed it. Teaching points: read your error messages (`query._: Field
required` is the clue), and test endpoints, not just functions.

## Code walkthrough: `project/main.py`

| Part | Teaching point |
|---|---|
| `request_context` | A request ID in each response and log line |
| `problem` | One error shape, following RFC 9457 |
| `unexpected_error` | Details go to logs, and never to clients |
| `authenticate` | `compare_digest` takes constant time |
| `TokenBucket` | Allows bursts, and limits the average rate |
| `chat_stream` | SSE format, and errors inside the stream |
| `create_job`, `run_summary` | The job pattern |
| `create_app(llm=...)` | Passing dependencies in makes testing easy |

**Limits of this demo, and what production uses:**

| Here | In production |
|---|---|
| API keys in the environment | OAuth2 or JWT, with an identity provider |
| Rate limiter in memory, per process | A shared store such as Redis |
| Jobs in memory, lost on restart | A durable queue: Celery, RQ, SQS, Temporal |
| Requests per second | Token-based limits as well |

## Industry standards

- OpenAPI documentation, generated from code
- Versioned routes (`/v1/`)
- RFC 9457 problem details for errors
- Correlation IDs across logs and traces
- 429 with `Retry-After`

## Lab

1. Add a `/v1/usage` endpoint that reports tokens used per API key.
2. Add a token-based rate limit, since one huge request can cost more than 100 small ones.
3. Connect the Policy Assistant from Module 03.4, so the chat answers from documents, with sources.

**Marking notes.** Task 1: record usage in `chat`, and protect the endpoint. Streaming needs a token estimate, which is a good
discussion point. Task 2: estimate before the call, and correct afterwards. Task 3 joins two modules, so have students keep all existing
tests passing. Import paths need care, because each module has its own `project` package.

## Check for understanding

1. Why can a client not send a `system` message? *The `Literal` type rejects it with a 422.*
2. Why do errors move inside the stream? *The 200 status has already been sent.*
3. What happens to `async def` with a blocking model call? *It blocks the event loop, and all other requests wait.*
4. Why should a browser never call the provider directly? *The key would be exposed.*
