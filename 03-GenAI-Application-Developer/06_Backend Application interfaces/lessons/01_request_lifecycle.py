"""Lesson 1: what your API does with good requests and bad ones, without starting a server.

Run: python lessons/01_request_lifecycle.py
"""

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient  # noqa: E402
from project.main import create_app  # noqa: E402

KEY = {"X-API-Key": "demo"}
GOOD = {"messages": [{"role": "user", "content": "Hello"}]}


def show(label: str, response) -> None:
    print(f"{label}\n  HTTP {response.status_code}, request id {response.headers.get('X-Request-ID')}")
    print(f"  {json.dumps(response.json())[:170]}\n")


def main() -> None:
    client = TestClient(create_app(MockClient(), api_keys={"demo"}, rate_per_s=0.01, burst=3))

    show("1. Valid request", client.post("/v1/chat", json=GOOD, headers=KEY))
    show("2. No API key: authentication", client.post("/v1/chat", json=GOOD))
    show("3. Wrong shape: validation", client.post("/v1/chat", json={"messages": []}, headers=KEY))
    show("4. Your tracing ID is echoed", client.post("/v1/chat", json=GOOD, headers={**KEY, "X-Request-ID": "trace-42"}))

    client.post("/v1/chat", json=GOOD, headers=KEY)
    response = client.post("/v1/chat", json=GOOD, headers=KEY)
    show(f"5. Too many requests: Retry-After={response.headers.get('Retry-After')}", response)

    print("Every error has the same shape, and validation happens before any model is called,")
    print("so bad requests cost nothing.")


if __name__ == "__main__":
    main()
