import json
import logging
from collections import Counter
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from genai_kit import MockClient, load_course_chunks
from project.main import create_app
from project.observability import JsonFormatter
from project.release import BudgetExceeded, BudgetGuard, PromptRegistry, VariantStats, promotion_decision

KEY = {"X-API-Key": "test"}
HOTEL = {"question": "What is the hotel limit per night?"}
UNIT = Path(__file__).resolve().parents[1]


class Down(MockClient):
    def complete(self, *args, **kwargs):
        raise TimeoutError("secret-detail")


def client_for(llm=None, budget=None) -> TestClient:
    return TestClient(create_app(llm or MockClient(), load_course_chunks(), budget=budget, api_keys={"test"}))


def test_ask_success_and_auth():
    with client_for() as client:
        response = client.post("/v1/ask", json=HOTEL, headers=KEY)
        assert response.status_code == 200
        assert "180 dollars" in response.json()["answer"]
        assert client.post("/v1/ask", json=HOTEL).status_code == 401


def test_readiness_and_liveness():
    app = create_app(MockClient(), load_course_chunks(), api_keys={"test"})
    before = TestClient(app)
    assert before.get("/healthz").status_code == 200
    assert before.get("/readyz").status_code == 503
    with TestClient(app) as started:
        assert started.get("/readyz").json()["status"] == "ready"


def test_metrics_count_requests_tokens_and_cost():
    with client_for() as client:
        client.post("/v1/ask", json=HOTEL, headers=KEY)
        text = client.get("/metrics").text
    assert 'outcome="ok"' in text
    assert 'genai_tokens_total{direction="input"' in text
    assert "genai_cost_usd_total" in text
    assert "genai_request_seconds_bucket" in text


def test_provider_failure_is_502_counted_and_safe():
    with client_for(Down()) as client:
        response = client.post("/v1/ask", json=HOTEL, headers=KEY)
        assert response.status_code == 502 and "secret-detail" not in response.text
        assert 'outcome="error"' in client.get("/metrics").text


def test_budget_blocks_with_503():
    budget = BudgetGuard(0.0, 1, 1)
    with client_for(budget=budget) as client:
        response = client.post("/v1/ask", json=HOTEL, headers=KEY)
        assert response.status_code == 503
        assert 'outcome="budget_exceeded"' in client.get("/metrics").text


def test_budget_resets_each_day():
    today = [date(2026, 1, 1)]
    guard = BudgetGuard(0.001, 1000, 1000, today=lambda: today[0])
    guard.record(10, 10)
    with pytest.raises(BudgetExceeded):
        guard.check()
    today[0] = date(2026, 1, 2)
    guard.check()
    assert guard.spent_usd == 0


def test_canary_split_is_stable_and_near_target():
    registry = PromptRegistry()
    registry.configure("1.0.0", "1.1.0", 10)
    counts = Counter(registry.select(f"user-{number}").version for number in range(10_000))
    assert 800 < counts["1.1.0"] < 1200
    assert registry.select("sam").version == registry.select("sam").version


def test_rollback_and_validation():
    registry = PromptRegistry()
    registry.configure("1.0.0")
    assert all(registry.select(f"u{n}").version == "1.0.0" for n in range(100))
    with pytest.raises(ValueError):
        registry.configure("9.9.9")
    with pytest.raises(ValueError):
        registry.configure("1.0.0", "1.1.0", 150)


@pytest.mark.parametrize(
    "canary,expected",
    [
        (VariantStats(50, 0, 1000, 0.9), "wait"),
        (VariantStats(1000, 5, 1000, 0.9), "promote"),
        (VariantStats(1000, 100, 1000, 0.9), "rollback"),
        (VariantStats(1000, 5, 5000, 0.9), "rollback"),
        (VariantStats(1000, 5, 1000, 0.5), "rollback"),
        (VariantStats(50, 40, 1000, 0.9), "rollback"),
    ],
)
def test_promotion_rules(canary, expected):
    baseline = VariantStats(9000, 45, 1000, 0.9)
    assert promotion_decision(baseline, canary)[0] == expected


def test_json_log_format():
    record = logging.LogRecord("x", logging.INFO, "f", 1, "hello", None, None)
    record.fields = {"request_id": "abc"}
    data = json.loads(JsonFormatter().format(record))
    assert data["message"] == "hello" and data["request_id"] == "abc" and data["level"] == "INFO"


def test_dockerfile_follows_basic_hardening():
    text = (UNIT / "Dockerfile").read_text("utf-8")
    assert "USER appuser" in text and "HEALTHCHECK" in text and "AS build" in text
    assert "ENV OPENAI_API_KEY" not in text and ".env" not in text
