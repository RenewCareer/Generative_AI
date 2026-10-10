"""Lesson 02 — Inspect the full response object.

Run:  python -m week1.lesson_02_inspect_response

A response is NOT just a string. `response.output` is a list of items:
  - "reasoning" items (reasoning models think before answering; you pay for these
     tokens as output tokens even though you don't see the text)
  - "message" items, whose `content` is a list of parts (type "output_text")
  - later in the course: "function_call", "file_search_call", ... items

Senior habit: when anything surprises you, dump the raw object before guessing.
"""
import json

from openai import OpenAI

from ai_core.config import get_settings, require_api_key

settings = get_settings()
client = OpenAI(api_key=require_api_key(settings))

response = client.responses.create(
    model=settings.model,
    input="Give me two fun facts about octopuses, one line each.",
)

print("=== Walk the output items ===")
for i, item in enumerate(response.output):
    print(f"[{i}] type={item.type}")
    if item.type == "message":
        for part in item.content:
            print(f"     part type={part.type}: {getattr(part, 'text', '')!r}")

print("\n=== Usage ===")
u = response.usage
print(f"input_tokens      = {u.input_tokens}")
print(f"  cached          = {u.input_tokens_details.cached_tokens}")
print(f"output_tokens     = {u.output_tokens}")
print(f"  reasoning       = {u.output_tokens_details.reasoning_tokens}  <- billed, invisible")
print(f"total_tokens      = {u.total_tokens}")

print("\n=== Full JSON (trimmed) ===")
raw = json.loads(response.model_dump_json())
print(json.dumps({k: raw[k] for k in ("id", "model", "status", "output", "usage")}, indent=2)[:3000])
