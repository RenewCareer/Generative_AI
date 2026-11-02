"""Twelve-factor style settings: everything configurable comes from the environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
COURSE_DATA = ROOT / "course_data"

load_dotenv(ROOT / ".env")


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


@dataclass(frozen=True)
class Settings:
    provider: str
    openai_api_key: str
    openai_model: str
    openai_embedding_model: str
    anthropic_api_key: str
    anthropic_model: str
    request_timeout_s: float
    max_retries: int


def get_settings() -> Settings:
    """Read settings on each call so tests and lessons can change the environment."""
    openai_key = _env("OPENAI_API_KEY")
    anthropic_key = _env("ANTHROPIC_API_KEY")
    provider = _env("LLM_PROVIDER").lower()

    if not provider:
        provider = "openai" if openai_key else "anthropic" if anthropic_key else "mock"
    if provider not in {"openai", "anthropic", "mock"}:
        raise ValueError(f"LLM_PROVIDER must be openai, anthropic or mock, got {provider!r}")
    if provider == "openai" and not openai_key:
        raise EnvironmentError("LLM_PROVIDER=openai but OPENAI_API_KEY is not set.")
    if provider == "anthropic" and not anthropic_key:
        raise EnvironmentError("LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set.")

    return Settings(
        provider=provider,
        openai_api_key=openai_key,
        openai_model=_env("OPENAI_MODEL", "gpt-4.1-mini"),
        openai_embedding_model=_env("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        anthropic_api_key=anthropic_key,
        anthropic_model=_env("ANTHROPIC_MODEL", "claude-opus-5-5"),
        request_timeout_s=float(_env("LLM_TIMEOUT_S", "60")),
        max_retries=int(_env("LLM_MAX_RETRIES", "3")),
    )
