"""Lesson 04 — Measure tokens, latency and cost. Build intuition with numbers.

Run:  python -m week1.lesson_04_tokens_cost_latency
      python -m week1.lesson_04_tokens_cost_latency gpt-5-mini gpt-5-nano gpt-4.1-mini

Experiments:
  A. Same question, different models  -> quality vs latency vs cost
  B. Short vs long answer              -> output tokens drive latency AND cost
  C. Streaming                         -> time-to-first-token vs total time
"""
import sys
import time

from openai import OpenAI

from ai_core import Assistant, AssistantError
from ai_core.config import get_settings, require_api_key

models = sys.argv[1:] or [get_settings().model]
QUESTION = "Explain what a token is in the context of LLMs."

print("=== A. Model comparison ===")
print(f"{'model':<28}{'in':>6}{'out':>6}{'reason':>8}{'secs':>7}{'cost $':>11}")
for m in models:
    try:
        r = Assistant(model=m).complete(QUESTION + " Two sentences.")
    except AssistantError as e:
        print(f"{m:<28} FAILED: {e}")
        continue
    cost = f"{r.cost_usd:.6f}" if r.cost_usd is not None else "n/a"
    print(f"{r.model:<28}{r.input_tokens:>6}{r.output_tokens:>6}{r.reasoning_tokens:>8}"
          f"{r.latency_s:>7.2f}{cost:>11}")

print("\n=== B. Output length drives cost and latency ===")
bot = Assistant()
for length in ("one sentence", "about 300 words"):
    r = bot.complete(f"{QUESTION} Answer in {length}.")
    print(f"{length:<16} -> {r.stats()}")

print("\n=== C. Streaming: time to first token ===")
settings = get_settings()
client = OpenAI(api_key=require_api_key(settings))
start = time.perf_counter()
first = None
stream = client.responses.create(model=settings.model, input=QUESTION + " ~150 words.", stream=True)
for event in stream:
    if event.type == "response.output_text.delta":
        if first is None:
            first = time.perf_counter() - start
        print(event.delta, end="", flush=True)
total = time.perf_counter() - start
print(f"\n\nfirst token after {first:.2f}s, finished after {total:.2f}s")

print("""
Rules of thumb
- ~1 token ≈ 4 characters of English ≈ 0.75 words. Other languages/code use more.
- Output tokens cost 4-8x input tokens. Asking for shorter answers is the cheapest optimisation.
- Reasoning tokens are billed as output. More reasoning effort = slower + pricier (+ often better).
- Streaming doesn't make the answer faster; it makes the user *wait less to see something*.
- Estimated monthly cost = calls/day x 30 x avg cost per call. Do this maths BEFORE launching.
""")
