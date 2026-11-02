"""Check the real provider with a few very small API calls. THIS SPENDS A LITTLE MONEY.

Needs a key in .env. Run: python scripts/live_check.py
"""

from __future__ import annotations

import sys

from pydantic import BaseModel

from genai_kit import get_embedder, get_llm, get_settings


class Capital(BaseModel):
    country: str
    capital: str


TOOL = {
    "name": "get_weather",
    "description": "Get the weather for a city.",
    "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
}


def main() -> int:
    settings = get_settings()
    if settings.provider == "mock":
        print("No API key found. Copy .env.example to .env and add one first.")
        return 2

    llm = get_llm()
    print(f"Provider: {llm.provider}, model: {llm.model}\n")
    failed = 0

    def check(name, function) -> None:
        nonlocal failed
        try:
            print(f"ok    {name}: {function()}")
        except Exception as error:
            failed += 1
            print(f"FAIL  {name}: {type(error).__name__}: {error}")

    user = [{"role": "user", "content": "Reply with the single word: ready"}]

    check("complete", lambda: llm.complete(user, max_tokens=50).text)
    check("stream", lambda: "".join(llm.stream(user, max_tokens=50)))
    check("parse", lambda: llm.parse([{"role": "user", "content": "France and its capital"}], Capital, max_tokens=100))

    def tool_round_trip() -> str:
        question = {"role": "user", "content": "What is the weather in Lisbon? Use the tool."}
        first = llm.complete([question], tools=[TOOL], max_tokens=200)
        if not first.tool_calls:
            raise RuntimeError("The model did not call the tool.")
        call = first.tool_calls[0]
        result = {"role": "tool", "tool_call_id": call.id, "name": call.name, "content": "22C and sunny"}
        return llm.complete([question, first.as_message(), result], tools=[TOOL], max_tokens=200).text

    check("tool round trip", tool_round_trip)

    embedder = get_embedder()
    check(f"embeddings ({embedder.name})", lambda: embedder.embed(["hello"]).shape)

    print(f"\n{'All live checks passed.' if not failed else f'{failed} live check(s) failed.'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
