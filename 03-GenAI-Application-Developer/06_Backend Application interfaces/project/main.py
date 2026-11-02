"""Example application: AI Chat API, with a browser UI, streaming, auth and rate limits.

Run:   python -m uvicorn project.main:app --reload --port 8000
Open:  http://localhost:8000          (chat UI; the demo API key is dev-key-123)
Docs:  http://localhost:8000/docs     (generated OpenAPI documentation)
"""

import json
import logging
import os
import secrets
import threading
import time
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Annotated, Literal

from fastapi import BackgroundTasks, Depends, FastAPI, Header, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from genai_kit import LLMClient, get_llm

logger = logging.getLogger("chat_api")
STATIC = Path(__file__).resolve().parent / "static"
SYSTEM_PROMPT = "You are the Acme Retail assistant. Answer briefly and helpfully."


# ---------------------------------------------------------------- Contracts


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)
    max_tokens: int = Field(default=500, ge=1, le=2000)


class ChatResponse(BaseModel):
    id: str
    message: ChatMessage
    model: str
    input_tokens: int
    output_tokens: int


class JobRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)


class Job(BaseModel):
    id: str
    status: Literal["queued", "running", "completed", "failed"]
    result: str | None = None
    error: str | None = None


# ---------------------------------------------------------------- Cross-cutting pieces


class TokenBucket:
    """Allows short bursts, while limiting the average rate per client."""

    def __init__(self, rate_per_s: float, capacity: int) -> None:
        self.rate = rate_per_s
        self.capacity = capacity
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str) -> tuple[bool, float]:
        with self._lock:
            now = time.monotonic()
            tokens, updated = self._buckets.get(key, (float(self.capacity), now))
            tokens = min(self.capacity, tokens + (now - updated) * self.rate)
            if tokens < 1:
                self._buckets[key] = (tokens, now)
                return False, (1 - tokens) / self.rate
            self._buckets[key] = (tokens - 1, now)
            return True, 0.0


def problem(status: int, title: str, detail: str, request_id: str = "") -> JSONResponse:
    """One error shape for the whole API, following RFC 9457 problem details."""
    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        content={"status": status, "title": title, "detail": detail, "request_id": request_id},
    )


def create_app(
    llm: LLMClient | None = None,
    api_keys: set[str] | None = None,
    rate_per_s: float = 5.0,
    burst: int = 10,
) -> FastAPI:
    app = FastAPI(title="AI Chat API", version="1.0.0")
    client = llm or get_llm(mock_handler=lambda messages, system, tools: f"[mock reply] You said: {messages[-1]['content'][:200]}")
    keys = api_keys if api_keys is not None else set(os.getenv("SERVICE_API_KEYS", "dev-key-123").split(","))
    limiter = TokenBucket(rate_per_s, burst)
    jobs: dict[str, Job] = {}

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        request.state.request_id = request_id
        start = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            json.dumps(
                {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "ms": round((time.perf_counter() - start) * 1000, 1),
                }
            )
        )
        return response

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException):
        response = problem(error.status_code, "Request failed", str(error.detail), request.state.request_id)
        for name, value in (error.headers or {}).items():
            response.headers[name] = value
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, error: RequestValidationError):
        issues = "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in error.errors())
        return problem(422, "Invalid request", issues, request.state.request_id)

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, error: Exception):
        # Full detail goes to the logs. The client never sees internals.
        logger.exception("Unhandled error on %s", request.url.path)
        return problem(500, "Internal error", "Something went wrong.", request.state.request_id)

    def authenticate(x_api_key: Annotated[str | None, Header()] = None) -> str:
        # compare_digest takes constant time, so response timing does not reveal the key.
        if not x_api_key or not any(secrets.compare_digest(x_api_key, key) for key in keys):
            raise HTTPException(status_code=401, detail="Missing or invalid API key.")
        return x_api_key

    def rate_limited(api_key: Annotated[str, Depends(authenticate)]) -> str:
        allowed, retry_after = limiter.allow(api_key)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded.",
                headers={"Retry-After": str(max(1, round(retry_after)))},
            )
        return api_key

    Client = Annotated[str, Depends(rate_limited)]

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC / "index.html")

    @app.get("/healthz", tags=["ops"])
    def healthz() -> dict:
        """Liveness: the process is up."""
        return {"status": "ok"}

    @app.get("/readyz", tags=["ops"])
    def readyz() -> dict:
        """Readiness: dependencies are configured, so the service can take traffic."""
        return {"status": "ready", "provider": client.provider, "model": client.model}

    # These are plain 'def' on purpose. The LLM client is synchronous, and FastAPI runs
    # plain functions in a thread pool, so a slow model call does not block the event loop.
    @app.post("/v1/chat", response_model=ChatResponse, tags=["chat"])
    def chat(body: ChatRequest, _: Client) -> ChatResponse:
        """Return the complete reply in one response."""
        response = client.complete(
            [message.model_dump() for message in body.messages],
            system=SYSTEM_PROMPT,
            max_tokens=body.max_tokens,
        )
        return ChatResponse(
            id=uuid.uuid4().hex,
            message=ChatMessage(role="assistant", content=response.text or "(empty reply)"),
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )

    @app.post("/v1/chat/stream", tags=["chat"])
    def chat_stream(body: ChatRequest, _: Client) -> StreamingResponse:
        """Stream the reply as Server-Sent Events: delta events, then done."""

        def events() -> Iterator[str]:
            try:
                messages = [message.model_dump() for message in body.messages]
                for delta in client.stream(messages, system=SYSTEM_PROMPT, max_tokens=body.max_tokens):
                    yield f"data: {json.dumps({'delta': delta})}\n\n"
                yield f"data: {json.dumps({'done': True})}\n\n"
            except Exception:
                # Headers have already gone out, so errors must travel in the stream.
                logger.exception("Stream failed")
                yield f"data: {json.dumps({'error': 'The stream was interrupted.'})}\n\n"

        return StreamingResponse(
            events(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    def run_summary(job_id: str, text: str) -> None:
        jobs[job_id].status = "running"
        try:
            response = client.complete(
                [{"role": "user", "content": text}],
                system="Summarise the user's text in three bullet points.",
                max_tokens=400,
            )
            jobs[job_id].result = response.text
            jobs[job_id].status = "completed"
        except Exception:
            logger.exception("Job %s failed", job_id)
            jobs[job_id].error = "Summarisation failed."
            jobs[job_id].status = "failed"

    @app.post("/v1/jobs/summarize", response_model=Job, status_code=202, tags=["jobs"])
    def create_job(body: JobRequest, tasks: BackgroundTasks, _: Client) -> Job:
        """For long work: reply 202 at once, and let the client poll for the result."""
        job = Job(id=uuid.uuid4().hex, status="queued")
        jobs[job.id] = job
        tasks.add_task(run_summary, job.id, body.text)
        return job

    @app.get("/v1/jobs/{job_id}", response_model=Job, tags=["jobs"])
    def get_job(job_id: str, _: Annotated[str, Depends(authenticate)]) -> Job:
        job = jobs.get(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found.")
        return job

    return app


app = create_app()
