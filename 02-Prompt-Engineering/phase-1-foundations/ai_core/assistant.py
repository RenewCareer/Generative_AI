"""A small, reusable wrapper around the OpenAI Responses API.

Design decisions worth noticing (these are the "senior" parts):

1. Dependency injection: `client` can be passed in, so tests use a fake client
   and never hit the network or spend money.
2. One place for error handling: SDK exceptions are translated into a single
   `AssistantError` with a human-readable hint. Callers handle one type.
3. Every call is measured: tokens, latency, cost. You can't optimise what you
   don't measure, and surprise bills come from not measuring.
4. State is only mutated after success: a failed call never leaves half a
   conversation in `history`.
5. Optional parameters are only sent when set. Reasoning models (gpt-5 family)
   reject `temperature`, so we don't send it unless you ask for it.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import openai
from openai import OpenAI

from .config import get_settings, require_api_key
from .jsonutil import extract_json
from .pricing import estimate_cost

Message = dict[str, Any]


class AssistantError(RuntimeError):
    """Raised for any failed model call. `hint` tells the user what to do."""

    def __init__(self, message: str, hint: str, original: Exception | None = None):
        super().__init__(f"{message}\n  -> {hint}")
        self.hint = hint
        self.original = original


@dataclass
class Reply:
    text: str
    model: str
    status: str  # "completed" or "incomplete"
    incomplete_reason: str | None
    input_tokens: int
    output_tokens: int
    cached_tokens: int
    reasoning_tokens: int
    latency_s: float
    cost_usd: float | None
    response_id: str

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def stats(self) -> str:
        cost = f"${self.cost_usd:.6f}" if self.cost_usd is not None else "cost n/a"
        extra = f" (reasoning {self.reasoning_tokens})" if self.reasoning_tokens else ""
        return (
            f"[{self.model} | in {self.input_tokens} / out {self.output_tokens}{extra} tok"
            f" | {self.latency_s:.2f}s | {cost} | {self.status}]"
        )


@dataclass
class UsageTotals:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_s: float = 0.0

    def add(self, r: Reply) -> None:
        self.calls += 1
        self.input_tokens += r.input_tokens
        self.output_tokens += r.output_tokens
        self.cost_usd += r.cost_usd or 0.0
        self.latency_s += r.latency_s

    def __str__(self) -> str:
        avg = self.latency_s / self.calls if self.calls else 0
        return (
            f"{self.calls} calls | {self.input_tokens} in / {self.output_tokens} out tokens"
            f" | ~${self.cost_usd:.5f} | avg latency {avg:.2f}s"
        )


@dataclass
class Assistant:
    instructions: str = "You are a helpful, concise assistant."
    model: str | None = None
    temperature: float | None = None
    max_output_tokens: int | None = None
    reasoning_effort: str | None = None  # "minimal" | "low" | "medium" | "high"
    remember_history: bool = True
    log_path: str | Path | None = None
    client: Any = None

    history: list[Message] = field(default_factory=list, init=False)
    usage: UsageTotals = field(default_factory=UsageTotals, init=False)

    def __post_init__(self) -> None:
        settings = get_settings()
        self.model = self.model or settings.model
        if self.client is None:
            self.client = OpenAI(
                api_key=require_api_key(settings),
                timeout=settings.timeout_s,
                # The SDK already retries 408/409/429/5xx and connection errors with
                # exponential backoff. Configure it rather than writing your own loop.
                max_retries=settings.max_retries,
            )

    # ---- public API -------------------------------------------------------

    def ask(self, prompt: str) -> Reply:
        """Conversational call. Sends prior turns if `remember_history` is on."""
        user_msg: Message = {"role": "user", "content": prompt}
        messages = [*self.history, user_msg] if self.remember_history else [user_msg]
        reply = self.complete(messages)
        if self.remember_history:
            self.history += [user_msg, {"role": "assistant", "content": reply.text}]
        return reply

    def complete(self, input: str | list[Message], **overrides: Any) -> Reply:
        """Stateless one-off call. Any constructor setting can be overridden
        per call, e.g. `complete(prompt, instructions="...", temperature=0)`."""
        params = self._build_params(input, overrides)
        start = time.perf_counter()
        try:
            response = self.client.responses.create(**params)
        except openai.OpenAIError as e:
            raise _translate_error(e, params["model"]) from e
        reply = _to_reply(response, time.perf_counter() - start)
        self.usage.add(reply)
        self._log(params, reply)
        return reply

    def complete_json(self, input: str, retries: int = 1, **overrides: Any) -> tuple[Any, Reply]:
        """Like `complete`, but parses JSON from the output. On a parse failure it
        retries, showing the model its own bad output and the parser error —
        a simple self-correction loop. Week 4 replaces this with Structured Outputs."""
        messages: list[Message] = [{"role": "user", "content": input}]
        for attempt in range(retries + 1):
            reply = self.complete(messages, **overrides)
            try:
                return extract_json(reply.text), reply
            except ValueError as e:
                if attempt == retries:
                    raise AssistantError("Model did not return valid JSON.",
                                         "Tighten the format instructions or use Structured Outputs.", e)
                messages += [
                    {"role": "assistant", "content": reply.text},
                    {"role": "user", "content": "That was not valid JSON. Reply again with ONLY "
                                                "the JSON, no prose and no code fences."},
                ]
        raise AssertionError("unreachable")

    def reset(self) -> None:
        self.history.clear()

    # ---- internals --------------------------------------------------------

    def _build_params(self, input: str | list[Message], overrides: dict) -> dict:
        opts = {
            "instructions": self.instructions,
            "model": self.model,
            "temperature": self.temperature,
            "max_output_tokens": self.max_output_tokens,
            "reasoning_effort": self.reasoning_effort,
            **overrides,
        }
        unknown = set(opts) - {
            "instructions", "model", "temperature", "max_output_tokens", "reasoning_effort",
        }
        if unknown:
            raise TypeError(f"Unknown option(s): {sorted(unknown)}")

        params: dict[str, Any] = {"model": opts["model"], "input": input}
        if opts["instructions"]:
            params["instructions"] = opts["instructions"]
        if opts["temperature"] is not None:
            params["temperature"] = opts["temperature"]
        if opts["max_output_tokens"] is not None:
            params["max_output_tokens"] = opts["max_output_tokens"]
        if opts["reasoning_effort"] is not None:
            params["reasoning"] = {"effort": opts["reasoning_effort"]}
        return params

    def _log(self, params: dict, reply: Reply) -> None:
        if not self.log_path:
            return
        path = Path(self.log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        record = {"ts": time.time(), "request": params, "reply": asdict(reply)}
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def _to_reply(response: Any, latency_s: float) -> Reply:
    usage = response.usage
    in_details = getattr(usage, "input_tokens_details", None)
    out_details = getattr(usage, "output_tokens_details", None)
    cached = getattr(in_details, "cached_tokens", 0) or 0
    reasoning = getattr(out_details, "reasoning_tokens", 0) or 0
    incomplete = getattr(response, "incomplete_details", None)
    return Reply(
        # `output_text` is an SDK convenience that joins all text parts of all
        # message items in `response.output`. Lesson 02 shows the raw structure.
        text=response.output_text,
        model=response.model,
        status=response.status,
        incomplete_reason=getattr(incomplete, "reason", None),
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cached_tokens=cached,
        reasoning_tokens=reasoning,
        latency_s=latency_s,
        cost_usd=estimate_cost(response.model, usage.input_tokens, usage.output_tokens, cached),
        response_id=response.id,
    )


def _translate_error(e: openai.OpenAIError, model: str) -> AssistantError:
    # Order matters: APITimeoutError is a subclass of APIConnectionError.
    if isinstance(e, openai.AuthenticationError):
        return AssistantError("Authentication failed (401).",
                              "Check OPENAI_API_KEY in your .env — it may be wrong or revoked.", e)
    if isinstance(e, openai.PermissionDeniedError):
        return AssistantError("Permission denied (403).",
                              "Your project/org may not have access to this model or region.", e)
    if isinstance(e, openai.NotFoundError):
        return AssistantError(f"Model or resource not found (404): {model!r}.",
                              "Check the model name, or whether your account has access to it.", e)
    if isinstance(e, openai.RateLimitError):
        if "insufficient_quota" in str(e):
            return AssistantError("Out of credit (429 insufficient_quota).",
                                  "Add billing credit at https://platform.openai.com/settings/organization/billing", e)
        return AssistantError("Rate limited (429) even after retries.",
                              "Slow down, reduce concurrency, or raise your usage tier.", e)
    if isinstance(e, openai.BadRequestError):
        return AssistantError(f"Bad request (400): {e.message}",
                              "A parameter is invalid for this model (e.g. temperature on a reasoning model).", e)
    if isinstance(e, openai.APITimeoutError):
        return AssistantError("Request timed out.",
                              "Increase OPENAI_TIMEOUT_S, shorten the prompt, or lower max_output_tokens.", e)
    if isinstance(e, openai.APIConnectionError):
        return AssistantError("Could not reach the API.", "Check your internet connection / proxy / VPN.", e)
    if isinstance(e, openai.APIStatusError):
        return AssistantError(f"API error {e.status_code}: {e.message}",
                              "Server-side problem; retry later and check https://status.openai.com", e)
    return AssistantError(f"Unexpected OpenAI error: {e}", "See the original exception.", e)
