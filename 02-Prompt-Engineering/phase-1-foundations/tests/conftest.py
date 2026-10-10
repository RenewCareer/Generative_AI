"""A fake OpenAI client: tests run offline, instantly, and for free.

`FakeClient(["reply 1", "reply 2", SomeError(...)])` returns scripted replies in
order and records every request in `.calls` so tests can assert on what was sent.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import openai
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def fake_response(text: str, model: str = "gpt-5-mini", status: str = "completed",
                  reason: str | None = None, in_tok: int = 10, out_tok: int = 5):
    return SimpleNamespace(
        id="resp_fake", model=model, status=status, output_text=text,
        incomplete_details=SimpleNamespace(reason=reason) if reason else None,
        usage=SimpleNamespace(
            input_tokens=in_tok, output_tokens=out_tok, total_tokens=in_tok + out_tok,
            input_tokens_details=SimpleNamespace(cached_tokens=0),
            output_tokens_details=SimpleNamespace(reasoning_tokens=0),
        ),
    )


class FakeClient:
    def __init__(self, script):
        self.script = list(script)
        self.calls: list[dict] = []
        self.responses = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        if not self.script:
            raise AssertionError("FakeClient ran out of scripted replies")
        item = self.script.pop(0)
        if isinstance(item, Exception):
            raise item
        if callable(item):  # dynamic reply based on the request
            item = item(kwargs)
        return item if not isinstance(item, str) else fake_response(item, model=kwargs["model"])


def api_error(cls, status: int, message: str = "boom"):
    req = httpx.Request("POST", "https://api.openai.com/v1/responses")
    return cls(message, response=httpx.Response(status, request=req), body=None)


@pytest.fixture
def make_client():
    return FakeClient


@pytest.fixture
def make_error():
    return api_error


@pytest.fixture(autouse=True)
def _no_real_key(monkeypatch):
    # Guarantee tests can never accidentally use a real key.
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-not-real")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5-mini")
    assert openai  # imported for side effects in error helpers
