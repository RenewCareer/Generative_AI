import openai
import pytest

from ai_core import Assistant, AssistantError, estimate_cost, extract_json
from conftest import fake_response


def test_ask_sends_instructions_and_remembers_history(make_client):
    client = make_client(["Hi Desmond!", "Your name is Desmond."])
    bot = Assistant(instructions="Be brief.", client=client)

    bot.ask("My name is Desmond")
    reply = bot.ask("What is my name?")

    assert reply.text == "Your name is Desmond."
    second = client.calls[1]
    assert second["instructions"] == "Be brief."
    assert [m["role"] for m in second["input"]] == ["user", "assistant", "user"]
    assert len(bot.history) == 4


def test_failed_call_does_not_corrupt_history(make_client, make_error):
    client = make_client([make_error(openai.InternalServerError, 500), "ok"])
    bot = Assistant(client=client)

    with pytest.raises(AssistantError):
        bot.ask("first")
    assert bot.history == []
    bot.ask("second")
    assert len(bot.history) == 2


def test_optional_params_only_sent_when_set(make_client):
    client = make_client(["a", "b"])
    bot = Assistant(client=client)
    bot.complete("x")
    assert "temperature" not in client.calls[0]
    assert "reasoning" not in client.calls[0]

    bot.complete("x", temperature=0, reasoning_effort="low")
    assert client.calls[1]["temperature"] == 0
    assert client.calls[1]["reasoning"] == {"effort": "low"}


def test_unknown_override_is_rejected(make_client):
    with pytest.raises(TypeError):
        Assistant(client=make_client([])).complete("x", temprature=0)


@pytest.mark.parametrize("cls,status,expected", [
    (openai.AuthenticationError, 401, "OPENAI_API_KEY"),
    (openai.NotFoundError, 404, "model"),
    (openai.RateLimitError, 429, "Rate limited"),
])
def test_errors_are_translated_with_hints(make_client, make_error, cls, status, expected):
    bot = Assistant(client=make_client([make_error(cls, status)]))
    with pytest.raises(AssistantError, match=expected):
        bot.complete("x")


def test_insufficient_quota_is_reported_as_billing(make_client, make_error):
    err = make_error(openai.RateLimitError, 429, "You exceeded your quota: insufficient_quota")
    with pytest.raises(AssistantError, match="credit"):
        Assistant(client=make_client([err])).complete("x")


def test_incomplete_status_is_surfaced(make_client):
    client = make_client([fake_response("cut o", status="incomplete", reason="max_output_tokens")])
    reply = Assistant(client=client).complete("x")
    assert reply.status == "incomplete"
    assert reply.incomplete_reason == "max_output_tokens"


def test_usage_totals_accumulate(make_client):
    bot = Assistant(client=make_client(["a", "b", "c"]))
    for _ in range(3):
        bot.complete("x")
    assert bot.usage.calls == 3
    assert bot.usage.input_tokens == 30
    assert bot.usage.cost_usd > 0


def test_cost_uses_longest_prefix_for_snapshots():
    # gpt-5-mini: $0.25 in / $2.00 out per 1M
    assert estimate_cost("gpt-5-mini-2025-08-07", 1_000_000, 1_000_000) == pytest.approx(2.25)
    assert estimate_cost("some-unknown-model", 100, 100) is None


@pytest.mark.parametrize("text", [
    '{"a": 1}',
    'Sure! Here you go:\n```json\n{"a": 1}\n```',
    'Result: {"a": 1} hope that helps',
])
def test_extract_json_tolerates_chatter(text):
    assert extract_json(text) == {"a": 1}


def test_extract_json_raises_on_garbage():
    with pytest.raises(ValueError):
        extract_json("no json here")
