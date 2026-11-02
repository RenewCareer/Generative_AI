"""Example application: a deployable RAG service, with metrics, canary prompts and a budget.

Run locally:  python -m uvicorn project.main:app --port 8080
Run in Docker: see the README in this folder.
"""

import logging
import os
import secrets
import time
import uuid
from collections.abc import Sequence
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, Field

from genai_kit import (
    BM25Index,
    Chunk,
    LLMClient,
    VectorIndex,
    format_context,
    get_embedder,
    get_llm,
    load_course_chunks,
    reciprocal_rank_fusion,
)
from project.observability import Metrics, configure_logging
from project.release import BudgetExceeded, BudgetGuard, PromptRegistry

logger = logging.getLogger("service")
VERSION = os.getenv("APP_VERSION", "dev")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    user_id: str = Field(default="anonymous", max_length=100)


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    prompt_version: str
    request_id: str


def create_app(
    llm: LLMClient | None = None,
    chunks: Sequence[Chunk] | None = None,
    registry: PromptRegistry | None = None,
    budget: BudgetGuard | None = None,
    api_keys: set[str] | None = None,
) -> FastAPI:
    state: dict = {"ready": False}
    keys = api_keys if api_keys is not None else set(filter(None, os.getenv("SERVICE_API_KEYS", "dev-key-123").split(",")))
    metrics = Metrics()
    prompts = registry or PromptRegistry()
    guard = budget or BudgetGuard(
        daily_limit_usd=float(os.getenv("DAILY_BUDGET_USD", "10")),
        input_per_m=float(os.getenv("PRICE_INPUT_PER_M", "0.40")),
        output_per_m=float(os.getenv("PRICE_OUTPUT_PER_M", "1.60")),
    )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Load before accepting traffic. Readiness stays false until this finishes.
        configure_logging(os.getenv("LOG_LEVEL", "INFO"))
        state["llm"] = llm or get_llm()
        data = list(chunks) if chunks is not None else load_course_chunks()
        state["vector"] = VectorIndex(get_embedder()).add(data)
        state["keyword"] = BM25Index(data)
        state["ready"] = True
        metrics.budget_remaining.set(guard.remaining_usd)
        logger.info("started", extra={"fields": {"version": VERSION, "chunks": len(data)}})
        yield
        state["ready"] = False  # Stop taking new work during a graceful shutdown.
        logger.info("stopping")

    app = FastAPI(title="GenAI Service", version=VERSION, lifespan=lifespan)

    def authenticate(x_api_key: Annotated[str | None, Header()] = None) -> None:
        if not x_api_key or not any(secrets.compare_digest(x_api_key, key) for key in keys):
            raise HTTPException(status_code=401, detail="Missing or invalid API key.")

    @app.get("/healthz")
    def healthz() -> dict:
        """Liveness. A failure means that the orchestrator should restart this container."""
        return {"status": "ok", "version": VERSION}

    @app.get("/readyz")
    def readyz(response: Response) -> dict:
        """Readiness. A failure means: send no traffic here yet, but do not restart it."""
        if not state["ready"]:
            response.status_code = 503
            return {"status": "starting"}
        return {"status": "ready", "active_prompt": prompts.active, "canary": prompts.canary}

    @app.get("/metrics", include_in_schema=False)
    def prometheus_metrics() -> Response:
        return Response(generate_latest(metrics.registry), media_type=CONTENT_TYPE_LATEST)

    @app.post("/v1/ask", response_model=AskResponse, dependencies=[Depends(authenticate)])
    def ask(body: AskRequest, request: Request) -> AskResponse:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
        prompt = prompts.select(body.user_id)
        start = time.perf_counter()
        fields = {"request_id": request_id, "prompt_version": prompt.version}

        try:
            guard.check()
            rankings = [state["vector"].search(body.question, k=20), state["keyword"].search(body.question, k=20)]
            hits = reciprocal_rank_fusion(rankings, k=4)
            user_prompt = f"Sources:\n{format_context(hits)}\n\nQuestion: {body.question}"
            response = state["llm"].complete(
                [{"role": "user", "content": user_prompt}], system=prompt.system, max_tokens=400
            )
        except BudgetExceeded as error:
            metrics.requests.labels(prompt.version, "budget_exceeded").inc()
            logger.warning("budget exceeded", extra={"fields": fields})
            raise HTTPException(status_code=503, detail=str(error)) from error
        except Exception as error:
            metrics.requests.labels(prompt.version, "error").inc()
            logger.exception("request failed", extra={"fields": fields})
            raise HTTPException(status_code=502, detail="The AI provider is unavailable.") from error

        elapsed = time.perf_counter() - start
        cost = guard.record(response.usage.input_tokens, response.usage.output_tokens)
        metrics.requests.labels(prompt.version, "ok").inc()
        metrics.latency.labels(prompt.version).observe(elapsed)
        metrics.tokens.labels("input", response.model).inc(response.usage.input_tokens)
        metrics.tokens.labels("output", response.model).inc(response.usage.output_tokens)
        metrics.cost.labels(response.model).inc(cost)
        metrics.budget_remaining.set(guard.remaining_usd)
        # Log sizes and IDs, not content: prompts may contain personal data.
        logger.info(
            "answered",
            extra={
                "fields": {
                    **fields,
                    "ms": round(elapsed * 1000, 1),
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "cost_usd": round(cost, 6),
                }
            },
        )
        return AskResponse(
            answer=response.text,
            sources=[hit.chunk.id for hit in hits],
            prompt_version=prompt.version,
            request_id=request_id,
        )

    return app


app = create_app()
