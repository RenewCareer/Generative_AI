"""Lesson 2: Server-Sent Events, the standard way to stream LLM output to a browser.

Run: python lessons/02_streaming_sse.py
"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient  # noqa: E402
from project.main import create_app  # noqa: E402


def main() -> None:
    llm = MockClient(lambda messages, system, tools: "Streaming makes slow models feel fast.")
    client = TestClient(create_app(llm, api_keys={"demo"}))

    print("What actually travels over the wire:\n")
    with client.stream(
        "POST",
        "/v1/chat/stream",
        json={"messages": [{"role": "user", "content": "Why stream?"}]},
        headers={"X-API-Key": "demo"},
    ) as response:
        print(f"Content-Type: {response.headers['content-type']}\n")
        for line in response.iter_lines():
            if line:
                print(line)

    print("\nA stream cannot change its HTTP status once it has started, so errors are sent as an")
    print("event inside the stream. See project/static/index.html for the browser side.")


if __name__ == "__main__":
    main()
