"""Includes real SDK requests against fake HTTP servers, to check the wire format with no key."""

import base64
import json
import wave
from pathlib import Path

import httpx2
import pymupdf
import pytest
from anthropic import Anthropic
from openai import OpenAI
from PIL import Image

from genai_kit.testing import load_lesson
from project.expense_assistant import LineItem, Receipt, apply_policy, make_sample_receipt, process_receipt
from project.media import encode_image, extract_from_image, generate_image, synthesize_speech, transcribe, write_test_tone

LESSONS = Path(__file__).resolve().parents[1] / "lessons"


@pytest.fixture
def mock_mode(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")


def receipt(category="meal", total=45.0, items=None) -> Receipt:
    return Receipt(merchant="X", category=category, total=total, items=items or [])


def test_policy_approves_within_limit():
    decision = apply_policy(receipt(total=45))
    assert decision.status == "approve" and decision.reimbursable == 45


def test_policy_removes_alcohol():
    items = [LineItem(description="Fish", amount=20), LineItem(description="Glass of wine", amount=8)]
    decision = apply_policy(receipt(total=28, items=items))
    assert decision.reimbursable == 20 and "alcohol" in decision.reasons[0]


def test_policy_caps_at_limit():
    assert apply_policy(receipt(category="hotel", total=250)).reimbursable == 180


def test_policy_flags_math_mismatch_for_review():
    items = [LineItem(description="Fish", amount=20)]
    decision = apply_policy(receipt(total=99, items=items))
    assert decision.status == "needs_review" and "Possible misread" in decision.reasons[0]


def test_policy_rejects_when_nothing_is_reimbursable():
    items = [LineItem(description="Beer", amount=10)]
    assert apply_policy(receipt(total=10, items=items)).status == "reject"


def test_encode_image_resizes(tmp_path):
    path = tmp_path / "big.png"
    Image.new("RGB", (3000, 2000), "white").save(path)
    media_type, data = encode_image(path, max_side=500)
    decoded = tmp_path / "out.jpg"
    decoded.write_bytes(base64.b64decode(data))
    assert media_type == "image/jpeg"
    with Image.open(decoded) as image:
        assert max(image.size) == 500


def test_end_to_end_mock(tmp_path, mock_mode):
    extracted, decision = process_receipt(make_sample_receipt(tmp_path / "r.png"))
    assert extracted.merchant == "Harbour Bistro"
    assert decision.reimbursable == 36.5


def test_mock_without_sidecar_fails_clearly(tmp_path, mock_mode):
    path = tmp_path / "x.png"
    Image.new("RGB", (10, 10)).save(path)
    with pytest.raises(FileNotFoundError, match="set an API key"):
        extract_from_image(path, "p", Receipt)


def test_openai_vision_request_shape(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    captured = []
    body = json.dumps({"merchant": "M", "category": "meal", "total": 5.0})

    def handler(request):
        captured.append(json.loads(request.content))
        return httpx2.Response(
            200,
            json={
                "id": "r",
                "object": "response",
                "created_at": 0,
                "model": "m",
                "status": "completed",
                "parallel_tool_calls": True,
                "tool_choice": "auto",
                "tools": [],
                "output": [
                    {
                        "id": "m1",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [{"type": "output_text", "text": body, "annotations": []}],
                    }
                ],
            },
        )

    client = OpenAI(api_key="k", http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))
    path = make_sample_receipt(tmp_path / "r.png")
    assert extract_from_image(path, "read", Receipt, client=client).merchant == "M"
    parts = captured[0]["input"][0]["content"]
    assert parts[1]["type"] == "input_image" and parts[1]["image_url"].startswith("data:image/jpeg;base64,")


def test_anthropic_vision_request_shape(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    captured = []

    def handler(request):
        captured.append(json.loads(request.content))
        return httpx2.Response(
            200,
            json={
                "id": "m",
                "type": "message",
                "role": "assistant",
                "model": "c",
                "stop_reason": "tool_use",
                "stop_sequence": None,
                "usage": {"input_tokens": 1, "output_tokens": 1},
                "content": [
                    {"type": "tool_use", "id": "t", "name": "record", "input": {"merchant": "M", "category": "meal", "total": 5.0}}
                ],
            },
        )

    client = Anthropic(api_key="k", http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))
    path = make_sample_receipt(tmp_path / "r.png")
    assert extract_from_image(path, "read", Receipt, client=client).total == 5.0
    assert captured[0]["messages"][0]["content"][0]["source"]["type"] == "base64"
    assert captured[0]["tool_choice"]["name"] == "record"


def test_openai_image_generation_decodes_result(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    raw = b"png-bytes"

    def handler(request):
        return httpx2.Response(200, json={"created": 0, "data": [{"b64_json": base64.b64encode(raw).decode()}]})

    client = OpenAI(api_key="k", http_client=httpx2.Client(transport=httpx2.MockTransport(handler)))
    assert generate_image("x", tmp_path / "a.png", client=client).read_bytes() == raw


def test_mock_image_is_a_labelled_placeholder(tmp_path, mock_mode):
    with Image.open(generate_image("a cat", tmp_path / "a.png")) as image:
        assert image.size == (640, 360)


def test_audio_plumbing_mock(tmp_path, mock_mode):
    path = write_test_tone(tmp_path / "a.wav", seconds=0.5)
    with wave.open(str(path), "rb") as handle:
        assert handle.getframerate() == 16_000
    assert "0.5 second" in transcribe(path)
    assert synthesize_speech("hello there", tmp_path / "b.wav").exists()


def test_vision_routing_rules():
    routing = load_lesson(LESSONS / "04_document_vision_routing.py")
    assert routing.route_page(50, 0.9) == "vision"
    assert routing.route_page(2000, 0.5) == "text+vision"
    assert routing.route_page(2000, 0.0) == "text"
    assert routing.route_page(10, 0.0) == "skip"
    assert routing.route_page(10, 0.04) == "skip"


def test_vision_routing_on_the_real_pdf_sends_most_pages_to_text():
    routing = load_lesson(LESSONS / "04_document_vision_routing.py")
    if not routing.PDF.exists():
        pytest.skip("Sample PDF not present")
    with pymupdf.open(routing.PDF) as document:
        routes = [routing.route_page(*routing.analyse_page(page)) for page in document]
    assert routes.count("text") > len(routes) * 0.8
    assert routes[0] == "vision"
