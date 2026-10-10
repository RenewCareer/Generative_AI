"""Lesson 03 — Trigger every common failure on purpose, and see what it looks like.

Run:  python -m week1.lesson_03_errors

You will meet all of these in production. Better to meet them today, deliberately.
Each case uses max_retries=0 so failures come back immediately.
"""
import openai
from openai import OpenAI

from ai_core.config import get_settings, require_api_key

settings = get_settings()
key = require_api_key(settings)


def attempt(title: str, fn) -> None:
    print(f"\n### {title}")
    try:
        r = fn()
        print(f"status={r.status} incomplete_details={r.incomplete_details}")
        print(f"output_text={r.output_text!r}")
    except openai.APIStatusError as e:  # server answered with an HTTP error
        print(f"{type(e).__name__}  http={e.status_code}  request_id={e.request_id}")
        print(f"message: {e.message[:200]}")
    except openai.APIConnectionError as e:  # never got an HTTP answer (incl. timeouts)
        print(f"{type(e).__name__}: {e}")


good = OpenAI(api_key=key, max_retries=0)

attempt("1. Wrong API key -> AuthenticationError (401)",
        lambda: OpenAI(api_key="sk-wrong", max_retries=0).responses.create(
            model=settings.model, input="hi"))

attempt("2. Model that doesn't exist -> NotFoundError (404) / BadRequestError (400)",
        lambda: good.responses.create(model="gpt-does-not-exist", input="hi"))

attempt("3. Timeout too short -> APITimeoutError",
        lambda: OpenAI(api_key=key, max_retries=0, timeout=0.01).responses.create(
            model=settings.model, input="hi"))

# Not an exception! The call "succeeds" but the answer is cut off.
# This is the most dangerous failure because naive code never checks for it.
attempt("4. max_output_tokens too small -> status='incomplete' (no exception!)",
        lambda: good.responses.create(
            model=settings.model, input="Write a 300-word story.", max_output_tokens=20))

# Reasoning models (gpt-5 family) reject sampling params like temperature.
# On a non-reasoning model (e.g. gpt-4.1-mini) this succeeds — which is the point:
# valid parameters depend on the model, so switching models can break working code.
attempt("5. Parameter the model may not support -> BadRequestError (400)",
        lambda: good.responses.create(model=settings.model, input="hi", temperature=1.7))

print("""
Takeaways
- 4xx = your request is wrong: fix it, don't retry (except 408/409/429).
- 429 + 5xx + connection errors = transient: retry with backoff (the SDK does this).
- ALWAYS check response.status. 'incomplete' does not raise.
- Log e.request_id — OpenAI support needs it to investigate.
- 429 'insufficient_quota' is a billing problem, not a rate problem; retrying won't help.
""")
