"""Structured logs and Prometheus metrics."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


class JsonFormatter(logging.Formatter):
    """One JSON object per line, which log platforms can search and aggregate."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        entry.update(getattr(record, "fields", {}))
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
    # HTTP clients log every request at INFO, which would drown out the application's own lines.
    for noisy in ("httpx", "httpx2", "openai", "anthropic"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


class Metrics:
    """The GenAI golden signals: traffic, errors, latency, plus tokens and cost."""

    def __init__(self) -> None:
        self.registry = CollectorRegistry()
        self.requests = Counter(
            "genai_requests_total", "Requests handled", ["prompt_version", "outcome"], registry=self.registry
        )
        self.latency = Histogram(
            "genai_request_seconds",
            "End-to-end latency",
            ["prompt_version"],
            buckets=(0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10, 30),
            registry=self.registry,
        )
        self.tokens = Counter("genai_tokens_total", "Tokens used", ["direction", "model"], registry=self.registry)
        self.cost = Counter("genai_cost_usd_total", "Estimated spend", ["model"], registry=self.registry)
        self.budget_remaining = Gauge("genai_budget_remaining_usd", "Daily budget left", registry=self.registry)
