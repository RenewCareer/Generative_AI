"""One small interface over OpenAI, Anthropic and an offline mock.

Messages use a neutral format:

    {"role": "user", "content": "..."}
    {"role": "assistant", "content": "...", "tool_calls": [ToolCall, ...]}
    {"role": "tool", "tool_call_id": "...", "name": "...", "content": "..."}

Each adapter translates that format into its provider's wire format.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import Any, Protocol, TypeVar, get_args, get_origin

from pydantic import BaseModel

from genai_kit.config import Settings, get_settings
from genai_kit.text import analyze

T = TypeVar("T", bound=BaseModel)
Message = dict[str, Any]


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    text: str
    model: str
    provider: str
    usage: Usage = field(default_factory=Usage)
    tool_calls: list[ToolCall] = field(default_factory=list)
    provider_items: list[Any] = field(default_factory=list)

    def as_message(self) -> Message:
        """The assistant turn to append to the conversation history."""
        message: Message = {"role": "assistant", "content": self.text, "tool_calls": self.tool_calls}
        if self.provider_items:
            message["provider_items"] = self.provider_items
        return message


class LLMClient(Protocol):
    provider: str
    model: str

    def complete(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        temperature: float | None = None,
        max_tokens: int = 1024,
    ) -> LLMResponse: ...

    def stream(
        self,
        messages: list[Message],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> Iterator[str]: ...

    def parse(
        self,
        messages: list[Message],
        schema: type[T],
        *,
        system: str | None = None,
        max_tokens: int = 1024,
    ) -> T: ...


# ---------------------------------------------------------------- OpenAI


class OpenAIClient:
    """Uses the Responses API."""

    provider = "openai"

    def __init__(self, settings: Settings, **client_kwargs: Any) -> None:
        from openai import OpenAI

        self.model = settings.openai_model
        self._client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.request_timeout_s,
            max_retries=settings.max_retries,
            **client_kwargs,
        )

    @staticmethod
    def _to_input(messages: list[Message]) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for message in messages:
            if message["role"] == "tool":
                items.append(
                    {
                        "type": "function_call_output",
                        "call_id": message["tool_call_id"],
                        "output": message["content"],
                    }
                )
            elif message.get("provider_items"):
                # Replay the model's own output items. Reasoning models require this.
                items.extend(message["provider_items"])
            else:
                items.append({"role": message["role"], "content": message["content"]})
        return items

    def complete(self, messages, *, system=None, tools=None, temperature=None, max_tokens=1024):
        request: dict[str, Any] = {
            "model": self.model,
            "input": self._to_input(messages),
            "max_output_tokens": max_tokens,
        }
        if system:
            request["instructions"] = system
        if temperature is not None:
            request["temperature"] = temperature
        if tools:
            request["tools"] = [
                {
                    "type": "function",
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                }
                for tool in tools
            ]

        response = self._client.responses.create(**request)
        calls = [
            ToolCall(item.call_id, item.name, json.loads(item.arguments))
            for item in response.output
            if item.type == "function_call"
        ]
        return LLMResponse(
            text=response.output_text or "",
            model=response.model,
            provider=self.provider,
            usage=Usage(response.usage.input_tokens, response.usage.output_tokens),
            tool_calls=calls,
            provider_items=[item.model_dump(exclude_none=True) for item in response.output],
        )

    def stream(self, messages, *, system=None, max_tokens=1024):
        request: dict[str, Any] = {
            "model": self.model,
            "input": self._to_input(messages),
            "max_output_tokens": max_tokens,
            "stream": True,
        }
        if system:
            request["instructions"] = system
        for event in self._client.responses.create(**request):
            if event.type == "response.output_text.delta":
                yield event.delta

    def parse(self, messages, schema, *, system=None, max_tokens=1024):
        request: dict[str, Any] = {
            "model": self.model,
            "input": self._to_input(messages),
            "text_format": schema,
            "max_output_tokens": max_tokens,
        }
        if system:
            request["instructions"] = system
        response = self._client.responses.parse(**request)
        if response.output_parsed is None:
            raise ValueError("The model did not return output matching the schema.")
        return response.output_parsed


# ---------------------------------------------------------------- Anthropic


class AnthropicClient:
    """Uses the Messages API."""

    provider = "anthropic"

    def __init__(self, settings: Settings, **client_kwargs: Any) -> None:
        from anthropic import Anthropic

        self.model = settings.anthropic_model
        self._client = Anthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.request_timeout_s,
            max_retries=settings.max_retries,
            **client_kwargs,
        )

    @staticmethod
    def _to_messages(messages: list[Message]) -> list[dict[str, Any]]:
        converted: list[dict[str, Any]] = []
        for message in messages:
            if message["role"] == "tool":
                block = {
                    "type": "tool_result",
                    "tool_use_id": message["tool_call_id"],
                    "content": message["content"],
                }
                # Parallel tool results must share a single user turn.
                last = converted[-1] if converted else None
                if last and last["role"] == "user" and isinstance(last["content"], list):
                    last["content"].append(block)
                else:
                    converted.append({"role": "user", "content": [block]})
            elif message["role"] == "assistant" and message.get("tool_calls"):
                blocks: list[dict[str, Any]] = []
                if message.get("content"):
                    blocks.append({"type": "text", "text": message["content"]})
                blocks.extend(
                    {"type": "tool_use", "id": call.id, "name": call.name, "input": call.arguments}
                    for call in message["tool_calls"]
                )
                converted.append({"role": "assistant", "content": blocks})
            else:
                converted.append({"role": message["role"], "content": message["content"]})
        return converted

    def _request(self, messages, system, max_tokens) -> dict[str, Any]:
        request: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": self._to_messages(messages),
        }
        if system:
            request["system"] = system
        return request

    def complete(self, messages, *, system=None, tools=None, temperature=None, max_tokens=1024):
        request = self._request(messages, system, max_tokens)
        if temperature is not None:
            request["temperature"] = temperature
        if tools:
            request["tools"] = [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "input_schema": tool["parameters"],
                }
                for tool in tools
            ]

        response = self._client.messages.create(**request)
        return LLMResponse(
            text="".join(block.text for block in response.content if block.type == "text"),
            model=response.model,
            provider=self.provider,
            usage=Usage(response.usage.input_tokens, response.usage.output_tokens),
            tool_calls=[
                ToolCall(block.id, block.name, dict(block.input))
                for block in response.content
                if block.type == "tool_use"
            ],
        )

    def stream(self, messages, *, system=None, max_tokens=1024):
        with self._client.messages.stream(**self._request(messages, system, max_tokens)) as stream:
            yield from stream.text_stream

    def parse(self, messages, schema, *, system=None, max_tokens=1024):
        # Forcing a tool call is how we get schema-shaped JSON back from Claude.
        request = self._request(messages, system, max_tokens)
        request["tools"] = [
            {
                "name": "record_result",
                "description": "Record the structured result.",
                "input_schema": schema.model_json_schema(),
            }
        ]
        request["tool_choice"] = {"type": "tool", "name": "record_result"}
        response = self._client.messages.create(**request)
        for block in response.content:
            if block.type == "tool_use":
                return schema.model_validate(block.input)
        raise ValueError("The model did not return output matching the schema.")


# ---------------------------------------------------------------- Mock


MockHandler = Callable[[list[Message], str | None, list[dict[str, Any]] | None], "str | LLMResponse"]
MOCK_REFUSAL = "I don't know based on the provided documents."


def _terms(text: str) -> set[str]:
    return set(analyze(text))


def _extractive_answer(prompt: str) -> str:
    """Answer a RAG prompt by quoting the best-matching context sentence."""
    question_match = re.search(r"Question:\s*(.+)", prompt)
    question = question_match.group(1) if question_match else prompt
    wanted = _terms(question)

    best_sentence, best_source, best_score = "", "", 0.0
    for source, body in re.findall(r"\[(\d+)\][^\n]*\n(.*?)(?=\n\[\d+\]|\nQuestion:|\Z)", prompt, re.S):
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", body):
            terms = _terms(sentence)
            if not terms:
                continue
            score = len(wanted & terms) / max(len(wanted), 1)
            if score > best_score:
                best_sentence, best_source, best_score = sentence.strip(), source, score
    if best_score < 0.34:
        return MOCK_REFUSAL
    return f"{best_sentence} [{best_source}]"


def _fake_value(annotation: Any) -> Any:
    origin = get_origin(annotation)
    if origin is not None and "Literal" in str(origin):
        return get_args(annotation)[0]
    if origin in (list, set, tuple):
        return []
    if origin is dict:
        return {}
    if origin is not None:  # Optional[X], X | None
        args = [arg for arg in get_args(annotation) if arg is not type(None)]
        return _fake_value(args[0]) if args else None
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return {name: _fake_value(f.annotation) for name, f in annotation.model_fields.items()}
    return {str: "mock value", int: 0, float: 0.0, bool: False}.get(annotation)


class MockClient:
    """Deterministic, offline stand-in for a real model.

    It does not generate language. It quotes RAG context, follows a lesson's scripted
    handler, or echoes. It lets every lesson run in class without keys, and makes tests
    reproducible. Pass a ``handler`` to script tool calls for a specific lesson.
    """

    provider = "mock"
    model = "mock-1"

    def __init__(self, handler: MockHandler | None = None, parse_handler: Callable[..., Any] | None = None):
        self.handler = handler
        self.parse_handler = parse_handler

    @staticmethod
    def _usage(messages: list[Message], system: str | None, output: str) -> Usage:
        text = (system or "") + "".join(str(m.get("content", "")) for m in messages)
        return Usage(max(1, len(text) // 4), max(1, len(output) // 4))

    def complete(self, messages, *, system=None, tools=None, temperature=None, max_tokens=1024):
        result = self.handler(messages, system, tools) if self.handler else None
        if isinstance(result, LLMResponse):
            result.usage = self._usage(messages, system, result.text)
            return result
        if result is None:
            prompt = str(messages[-1].get("content", ""))
            if "Question:" in prompt and re.search(r"\[\d+\]", prompt):
                result = _extractive_answer(prompt)
            else:
                result = f"[mock answer] You asked: {prompt[:200]}"
        return LLMResponse(result, self.model, self.provider, self._usage(messages, system, result))

    def stream(self, messages, *, system=None, max_tokens=1024):
        text = self.complete(messages, system=system).text
        for word in re.findall(r"\S+\s*", text):
            yield word

    def parse(self, messages, schema, *, system=None, max_tokens=1024):
        if self.parse_handler:
            return schema.model_validate(self.parse_handler(messages, schema))
        return schema.model_validate(
            {name: _fake_value(f.annotation) for name, f in schema.model_fields.items()}
        )


# ---------------------------------------------------------------- Factory

_warned = False


def get_llm(
    mock_handler: MockHandler | None = None,
    mock_parse_handler: Callable[..., Any] | None = None,
) -> LLMClient:
    """Build the client selected by the environment. Falls back to the mock, loudly."""
    global _warned
    settings = get_settings()
    if settings.provider == "openai":
        return OpenAIClient(settings)
    if settings.provider == "anthropic":
        return AnthropicClient(settings)
    if not _warned:
        print(
            "[genai_kit] MOCK MODE: no API key found, so answers are simulated, not from a real "
            "model.\n[genai_kit] For real answers, copy .env.example to .env and add a key.\n",
            file=sys.stderr,
        )
        _warned = True
    return MockClient(mock_handler, mock_parse_handler)
