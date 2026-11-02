"""Example application: Production RAG API.

Run:   python -m uvicorn project.service:app --port 8010
Try:   curl -X POST localhost:8010/v1/ask -H "Content-Type: application/json" \
            -H "X-Role: employee" -d "{\"question\": \"What is the hotel limit per night?\"}"
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import get_embedder, get_llm, load_course_chunks  # noqa: E402
from project.pipeline import ProductionRag  # noqa: E402


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


def create_app(rag: ProductionRag | None = None) -> FastAPI:
    app = FastAPI(title="Production RAG API", version="1.0.0")
    pipeline = rag or ProductionRag(load_course_chunks(), get_llm(), get_embedder())

    @app.get("/healthz")
    def health() -> dict:
        return {"status": "ok", "index_version": pipeline.index_version}

    @app.post("/v1/ask")
    def ask(request: AskRequest, x_role: str = Header(default="customer")) -> dict:
        # Demo only: a real service derives the role from a verified token, never from
        # a header the caller controls. Module 06 shows authentication.
        try:
            return asdict(pipeline.ask(request.question, role=x_role))
        except PermissionError as error:
            raise HTTPException(status_code=403, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error

    @app.get("/v1/stats")
    def stats() -> dict:
        return {"cache_hits": pipeline.cache.hits, "cache_misses": pipeline.cache.misses}

    return app


app = create_app()
