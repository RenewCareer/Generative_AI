"""Settings come from environment variables, never from source code.

Why: a key in source code ends up in git history, screenshots, and chat logs.
`.env` is loaded for local development; in production the same variables are
set by the platform (Docker, CI secrets, cloud config) and no code changes.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Searches upward from this file for a `.env`, so it works from any working dir.
load_dotenv()

DEFAULT_MODEL = "gpt-5-mini"


class MissingAPIKeyError(RuntimeError):
    pass


@dataclass(frozen=True)
class Settings:
    api_key: str | None
    model: str
    timeout_s: float
    max_retries: int


def get_settings() -> Settings:
    return Settings(
        api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_MODEL", DEFAULT_MODEL),
        timeout_s=float(os.getenv("OPENAI_TIMEOUT_S", "60")),
        max_retries=int(os.getenv("OPENAI_MAX_RETRIES", "3")),
    )


def require_api_key(settings: Settings) -> str:
    """Fail fast with an actionable message instead of a stack trace later."""
    if not settings.api_key or settings.api_key.startswith("sk-..."):
        raise MissingAPIKeyError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env in "
            "phase-1-foundations/ and paste your key from "
            "https://platform.openai.com/api-keys"
        )
    return settings.api_key
