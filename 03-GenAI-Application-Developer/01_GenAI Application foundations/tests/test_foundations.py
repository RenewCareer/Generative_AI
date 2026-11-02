from pathlib import Path

import numpy as np
import pytest

from genai_kit import MockClient
from genai_kit.testing import load_lesson
from project.study_buddy import answer_once, ask, validate_question

LESSONS = Path(__file__).resolve().parents[1] / "lessons"
tokens = load_lesson(LESSONS / "01_tokens_and_context.py")
sampling = load_lesson(LESSONS / "03_temperature_sampling.py")
attention = load_lesson(LESSONS / "04_attention_toy.py")


def test_token_estimate_and_cost():
    assert tokens.estimate_tokens("a" * 400) == 100
    assert tokens.request_cost(1_000_000, 1_000_000, 1.0, 2.0) == pytest.approx(3.0)


def test_context_budget_remaining():
    budget = tokens.ContextBudget(1000, 100, 200, 300, 100)
    assert budget.used == 700
    assert budget.remaining == 300


def test_temperature_zero_is_greedy_and_high_temperature_flattens():
    logits = sampling.LOGITS
    assert sampling.softmax_with_temperature(logits, 0.0)[0] == 1.0
    low = sampling.softmax_with_temperature(logits, 0.5)
    high = sampling.softmax_with_temperature(logits, 2.0)
    assert low[0] > high[0]
    assert high.sum() == pytest.approx(1.0)


def test_attention_pulls_bank_towards_water():
    weights, contextual = attention.self_attention(attention.EMBEDDINGS)
    assert np.allclose(weights.sum(axis=1), 1.0)
    bank_before, bank_after = attention.EMBEDDINGS[1], contextual[1]
    assert bank_after[1] - bank_after[0] > bank_before[1] - bank_before[0]


def test_validation_rejects_bad_questions():
    assert validate_question("  hi ") == "hi"
    with pytest.raises(ValueError):
        validate_question("   ")
    with pytest.raises(ValueError):
        validate_question("x" * 2001)


def test_ask_returns_usage():
    response = ask(MockClient(), "What is a token?")
    assert response.text and response.usage.total_tokens > 0


def test_cli_exit_codes(capsys):
    assert answer_once(MockClient(), "What is a token?", stream=True) == 0
    assert answer_once(MockClient(), "   ", stream=False) == 2

    class Broken(MockClient):
        def complete(self, *args, **kwargs):
            raise RuntimeError("secret upstream detail")

    assert answer_once(Broken(), "hello", stream=False) == 1
    assert "secret upstream detail" not in capsys.readouterr().err
