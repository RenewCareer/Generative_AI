"""Checks the shared kit, including the real provider adapters against fake HTTP servers.

The adapter tests prove that our code sends valid wire-format requests and parses
provider-shaped responses, with no API key and no network.
"""

import json

import httpx2
import numpy as np
import pytest
from pydantic import BaseModel

from genai_kit import (
    AnthropicClient,
    BM25Index,
    Chunk,
    HashingEmbedder,
    MockClient,
    OpenAIClient,
    SearchHit,
    Settings,
    ToolCall,
    VectorIndex,
    format_context,
    load_course_chunks,
    load_course_docs,
    recursive_chunk,
    reciprocal_rank_fusion,
)
from genai_kit.config import get_settings
from genai_kit.llm import MOCK_REFUSAL
from genai_kit.retrieval import load_golden

SETTINGS = Settings("openai", "key", "gpt-test", "embed-test", "key", "claude-test", 5.0, 0)
TOOLS = [
    {
        "name": "get_order",
        "description": "Look up an order",
        "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}},
    }
]


class Answer(BaseModel):
    answer: str


def client_for(payload: dict, captured: list) -> httpx2.Client:
    def handler(request: httpx2.Request) -> httpx2.Response:
        captured.append(json.loads(request.content))
        return httpx2.Response(200, json=payload)

    return httpx2.Client(transport=httpx2.MockTransport(handler))


def openai_payload(output: list[dict]) -> dict:
    return {
        "id": "resp_1",
        "object": "response",
        "created_at": 0,
        "model": "gpt-test",
        "status": "completed",
        "output": output,
        "parallel_tool_calls": True,
        "tool_choice": "auto",
        "tools": [],
        "usage": {
            "input_tokens": 11,
            "output_tokens": 7,
            "total_tokens": 18,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens_details": {"reasoning_tokens": 0},
        },
    }


def openai_message(text: str) -> dict:
    return {
        "id": "msg_1",
        "type": "message",
        "role": "assistant",
        "status": "completed",
        "content": [{"type": "output_text", "text": text, "annotations": []}],
    }


def anthropic_payload(content: list[dict]) -> dict:
    return {
        "id": "msg_1",
        "type": "message",
        "role": "assistant",
        "model": "claude-test",
        "content": content,
        "stop_reason": "end_turn",
        "stop_sequence": None,
        "usage": {"input_tokens": 11, "output_tokens": 7},
    }


def test_openai_text_request_and_response():
    captured: list = []
    http = client_for(openai_payload([openai_message("hello")]), captured)
    response = OpenAIClient(SETTINGS, http_client=http).complete(
        [{"role": "user", "content": "hi"}], system="be brief", max_tokens=50
    )
    assert response.text == "hello"
    assert response.usage.total_tokens == 18
    assert captured[0]["instructions"] == "be brief"
    assert captured[0]["input"] == [{"role": "user", "content": "hi"}]
    assert captured[0]["max_output_tokens"] == 50
    assert "temperature" not in captured[0]


def test_openai_tool_round_trip():
    captured: list = []
    item = {
        "id": "fc_1",
        "type": "function_call",
        "call_id": "call_1",
        "name": "get_order",
        "arguments": '{"order_id": "A-1001"}',
        "status": "completed",
    }
    client = OpenAIClient(SETTINGS, http_client=client_for(openai_payload([item]), captured))
    first = client.complete([{"role": "user", "content": "where?"}], tools=TOOLS)
    assert first.tool_calls[0].arguments == {"order_id": "A-1001"}
    assert captured[0]["tools"][0]["type"] == "function"

    history = [
        {"role": "user", "content": "where?"},
        first.as_message(),
        {"role": "tool", "tool_call_id": "call_1", "name": "get_order", "content": "delivered"},
    ]
    client.complete(history, tools=TOOLS)
    types = [entry.get("type") for entry in captured[1]["input"]]
    assert types == [None, "function_call", "function_call_output"]
    assert captured[1]["input"][2]["call_id"] == "call_1"


def test_openai_parse_sends_json_schema():
    captured: list = []
    http = client_for(openai_payload([openai_message('{"answer": "42"}')]), captured)
    result = OpenAIClient(SETTINGS, http_client=http).parse([{"role": "user", "content": "q"}], Answer)
    assert result.answer == "42"
    assert captured[0]["text"]["format"]["type"] == "json_schema"


def test_anthropic_text_request_and_response():
    captured: list = []
    http = client_for(anthropic_payload([{"type": "text", "text": "hello"}]), captured)
    response = AnthropicClient(SETTINGS, http_client=http).complete(
        [{"role": "user", "content": "hi"}], system="be brief"
    )
    assert response.text == "hello"
    assert response.usage.input_tokens == 11
    assert captured[0]["system"] == "be brief"
    assert captured[0]["max_tokens"] == 1024


def test_anthropic_tool_round_trip_merges_parallel_results():
    captured: list = []
    block = {"type": "tool_use", "id": "t1", "name": "get_order", "input": {"order_id": "A-1"}}
    client = AnthropicClient(SETTINGS, http_client=client_for(anthropic_payload([block]), captured))
    first = client.complete([{"role": "user", "content": "where?"}], tools=TOOLS)
    assert first.tool_calls[0].name == "get_order"
    assert "input_schema" in captured[0]["tools"][0]

    history = [
        {"role": "user", "content": "where?"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [ToolCall("t1", "get_order", {}), ToolCall("t2", "get_order", {})],
        },
        {"role": "tool", "tool_call_id": "t1", "name": "get_order", "content": "a"},
        {"role": "tool", "tool_call_id": "t2", "name": "get_order", "content": "b"},
    ]
    client.complete(history, tools=TOOLS)
    sent = captured[1]["messages"]
    assert [message["role"] for message in sent] == ["user", "assistant", "user"]
    assert [block["tool_use_id"] for block in sent[2]["content"]] == ["t1", "t2"]


def test_anthropic_parse_forces_tool():
    captured: list = []
    block = {"type": "tool_use", "id": "t1", "name": "record_result", "input": {"answer": "42"}}
    client = AnthropicClient(SETTINGS, http_client=client_for(anthropic_payload([block]), captured))
    assert client.parse([{"role": "user", "content": "q"}], Answer).answer == "42"
    assert captured[0]["tool_choice"] == {"type": "tool", "name": "record_result"}


def test_mock_answers_from_context_and_refuses_without_it():
    prompt = "[1] (source: x)\nThe sky is green on Mars.\n\nQuestion: What color is the sky on Mars?"
    assert "green" in MockClient().complete([{"role": "user", "content": prompt}]).text
    unrelated = "[1] (source: x)\nCats sleep a lot.\n\nQuestion: What is the hotel limit?"
    assert MockClient().complete([{"role": "user", "content": unrelated}]).text == MOCK_REFUSAL


def test_settings_auto_detection(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    assert get_settings().provider == "mock"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    assert get_settings().provider == "anthropic"
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    assert get_settings().provider == "openai"
    monkeypatch.setenv("LLM_PROVIDER", "bogus")
    with pytest.raises(ValueError):
        get_settings()


def test_recursive_chunk_respects_size_and_overlap():
    text = " ".join(f"Sentence number {i} is here." for i in range(200))
    chunks = recursive_chunk(text, max_chars=300, overlap=40)
    assert len(chunks) > 5
    assert all(len(chunk) <= 360 for chunk in chunks)
    assert chunks[0][-20:].strip() in chunks[1]


def test_course_data_loads_with_metadata():
    docs = load_course_docs()
    assert len(docs) == 8
    assert {doc["metadata"]["access"] for doc in docs} == {"public", "internal"}
    assert len(load_course_chunks()) >= 8
    assert len(load_golden()) == 20


def test_hashing_embedder_is_normalised_and_deterministic():
    embedder = HashingEmbedder()
    first = embedder.embed(["refund policy", "refund policy", "water resistance"])
    assert np.allclose(np.linalg.norm(first, axis=1), 1.0)
    assert first[0] @ first[1] == pytest.approx(1.0)
    assert first[0] @ first[2] < 0.5


def test_search_and_fusion_find_expected_doc():
    chunks = load_course_chunks()
    vector_hits = VectorIndex().add(chunks).search("hotel limit per night", k=3)
    keyword_hits = BM25Index(chunks).search("SHP-404", k=3)
    assert vector_hits[0].chunk.doc_id == "expense_policy"
    assert keyword_hits[0].chunk.doc_id == "shipping_policy"
    fused = reciprocal_rank_fusion([vector_hits, keyword_hits], k=2)
    assert len(fused) == 2


def test_filter_blocks_internal_documents():
    chunks = load_course_chunks()
    hits = VectorIndex().add(chunks).search("annual leave", k=3, where=lambda m: m["access"] == "public")
    assert hits and all(hit.chunk.metadata["access"] == "public" for hit in hits)


def test_format_context_numbers_sources():
    hit = SearchHit(Chunk("a#0", "a", "text"), 1.0)
    assert format_context([hit]) == "[1] (source: a)\ntext"
