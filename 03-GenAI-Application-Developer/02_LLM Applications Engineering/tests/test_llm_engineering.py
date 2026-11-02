import random
from pathlib import Path

import pytest

from genai_kit import MockClient, Usage
from genai_kit.testing import load_lesson
from project.review_analyzer import analyze, mock_analysis, run_batch, summarise

LESSONS = Path(__file__).resolve().parents[1] / "lessons"
templates = load_lesson(LESSONS / "01_prompt_templates.py")
structured = load_lesson(LESSONS / "02_structured_output.py")
memory = load_lesson(LESSONS / "03_streaming_and_memory.py")
reliability = load_lesson(LESSONS / "04_reliability_and_cost.py")


def test_template_renders_and_fails_on_missing_variable():
    system, user = templates.SUMMARISE_V2.render(ticket="hello")
    assert "<ticket>\nhello\n</ticket>" in user and "untrusted" in system
    with pytest.raises(KeyError):
        templates.SUMMARISE_V2.render(wrong="x")


def test_repair_loop_recovers_then_gives_up():
    good = '{"category": "billing", "priority": 1, "summary": "Double charge"}'
    outputs = iter(['{"category": "nope"}', good])
    assert structured.parse_with_repair(lambda feedback: next(outputs)).category == "billing"
    with pytest.raises(ValueError):
        structured.parse_with_repair(lambda feedback: "not json", attempts=2)


def test_repair_loop_feeds_back_the_error():
    seen = []
    outputs = iter(['{"category": "nope"}', '{"category": "other", "priority": 3, "summary": "ok"}'])

    def generate(feedback):
        seen.append(feedback)
        return next(outputs)

    structured.parse_with_repair(generate)
    assert seen[0] is None and "invalid" in seen[1]


def test_memory_stays_within_budget_and_keeps_latest():
    conversation = memory.ConversationMemory(max_tokens=20)
    for number in range(10):
        conversation.add("user", f"question {number} " * 5)
        conversation.add("assistant", f"answer {number} " * 5)
    assert conversation.dropped > 0
    assert conversation.messages[0]["role"] == "user"
    assert "answer 9" in conversation.messages[-1]["content"]


def test_retries_recover_and_permanent_errors_do_not_retry():
    attempts = []

    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise reliability.RetryableError("429")
        return "ok"

    assert reliability.call_with_retries(flaky, rng=random.Random(0)) == "ok"
    assert len(attempts) == 3

    calls = []

    def bad():
        calls.append(1)
        raise reliability.PermanentError("400")

    with pytest.raises(reliability.PermanentError):
        reliability.call_with_retries(bad)
    assert len(calls) == 1


def test_backoff_never_exceeds_cap():
    for attempt in range(12):
        assert 0 <= reliability.backoff_delay(attempt, base=1, cap=5) <= 5


def test_cost_ledger_enforces_budget():
    ledger = reliability.CostLedger(1.0, 2.0, budget_usd=0.003)
    ledger.record(Usage(1000, 500))
    assert ledger.spent_usd == pytest.approx(0.002)
    with pytest.raises(RuntimeError):
        ledger.record(Usage(1000, 500))


def test_analyzer_validates_empty_input():
    client = MockClient(parse_handler=mock_analysis)
    assert analyze(client, "Terrible, it broke.").sentiment == "negative"
    with pytest.raises(ValueError):
        analyze(client, "   ")


def test_batch_isolates_failures_and_preserves_order():
    rows = [
        {"review_id": "1", "product": "A", "review": "Great and easy"},
        {"review_id": "2", "product": "B", "review": "   "},
        {"review_id": "3", "product": "C", "review": "Terrible, it broke"},
    ]
    results = run_batch(MockClient(parse_handler=mock_analysis), rows)
    assert [result["review_id"] for result in results] == ["1", "2", "3"]
    assert [result["ok"] for result in results] == [True, False, True]
    summary = summarise(results)
    assert summary["failed"] == 1 and summary["follow_up"] == 1
