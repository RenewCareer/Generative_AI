"""Lesson 01 — Your first Responses API call, with nothing hidden.

Run from phase-1-foundations/:
    python -m week1.lesson_01_hello

What to notice:
- The client reads OPENAI_API_KEY from the environment automatically.
- `instructions` = developer/system-level guidance. `input` = the user's request.
- `response.output_text` is a convenience; lesson 02 shows the full object.
"""
from openai import OpenAI

from ai_core.config import get_settings, require_api_key

settings = get_settings()
client = OpenAI(api_key=require_api_key(settings))

response = client.responses.create(
    model=settings.model,
    instructions="You are a patient tutor. Answer in at most 3 sentences.",
    input="What actually happens when I call an LLM API?",
)

print(response.output_text)
print("\n--- metadata ---")
print("id:     ", response.id)
print("model:  ", response.model)  # note: often a dated snapshot of what you asked for
print("status: ", response.status)
print("tokens: ", response.usage.input_tokens, "in /", response.usage.output_tokens, "out")
