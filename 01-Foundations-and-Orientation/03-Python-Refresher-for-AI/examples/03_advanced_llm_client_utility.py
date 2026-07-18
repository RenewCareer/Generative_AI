"""
Advanced example: a small, reusable LLM client wrapper class.

Requires: anthropic (see requirements.txt) and an ANTHROPIC_API_KEY
environment variable. Get a key at https://console.anthropic.com

This is the single most reusable piece of code in Track 1 -- a thin class
around the Anthropic API that:
  1. Reads its API key from an environment variable (never hard-code keys).
  2. Validates configuration up front with a clear error message.
  3. Retries automatically on transient failures (rate limits, server
     errors, network blips) using exponential backoff, instead of
     crashing on the first hiccup.
  4. Exposes a simple `.ask(prompt)` method that hides all of the above.

You will see this exact class (with more features) reappear in Track 2 and
Track 3 -- building it once here, deliberately, means you'll recognize the
pattern immediately later instead of re-deriving it under time pressure.

Run it with:
    python 03_advanced_llm_client_utility.py
"""

import os
import random
import time

import anthropic

MODEL = "claude-opus-4-8"


class LLMClient:
    """A minimal, production-shaped wrapper around the Anthropic API."""

    def __init__(self, model: str = MODEL, max_retries: int = 3) -> None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Get a key at https://console.anthropic.com and set it before "
                "constructing LLMClient."
            )
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._max_retries = max_retries

    def ask(self, prompt: str, max_tokens: int = 300) -> str:
        """Send `prompt` to the model and return the text reply.

        Retries with exponential backoff on rate limits and transient
        server errors. Raises immediately on non-retryable errors (e.g. a
        malformed request) -- retrying those would just fail again.
        """
        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                response = self._client.messages.create(
                    model=self._model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                return next(block.text for block in response.content if block.type == "text")

            except anthropic.RateLimitError as exc:
                last_error = exc
                print(f"  [retry {attempt + 1}/{self._max_retries}] rate limited, backing off...")

            except anthropic.APIConnectionError as exc:
                last_error = exc
                print(f"  [retry {attempt + 1}/{self._max_retries}] network error, backing off...")

            except anthropic.APIStatusError as exc:
                if exc.status_code >= 500:
                    last_error = exc
                    print(f"  [retry {attempt + 1}/{self._max_retries}] server error {exc.status_code}, backing off...")
                else:
                    # 4xx (other than 429) won't succeed on retry -- fail fast.
                    raise

            # Exponential backoff with jitter: 1s, 2s, 4s, ... plus a little randomness
            # so many parallel clients don't all retry at the exact same moment.
            delay = min(2 ** attempt + random.uniform(0, 1), 10)
            time.sleep(delay)

        raise RuntimeError(f"LLM request failed after {self._max_retries} attempts") from last_error


def main() -> None:
    try:
        client = LLMClient()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return

    print("=" * 70)
    print("Reusable LLMClient demo")
    print("=" * 70)

    questions = [
        "In one sentence, what is the difference between AI and machine learning?",
        "In one sentence, what does 'generative' mean in Generative AI?",
    ]

    for question in questions:
        print(f"\nQ: {question}")
        answer = client.ask(question, max_tokens=100)
        print(f"A: {answer}")

    print("\n" + "=" * 70)
    print("Why this class design matters")
    print("=" * 70)
    print(
        "Notice the calling code (main()) never touches API keys, retry\n"
        "logic, or error types directly -- it just calls client.ask(question).\n"
        "That separation (config/reliability concerns INSIDE the class,\n"
        "business logic OUTSIDE it) is what makes code maintainable as an\n"
        "application grows from a script into a real system. You'll extend\n"
        "this exact class with conversation history in Track 2, and with\n"
        "retrieval-augmented context in Track 3."
    )


if __name__ == "__main__":
    main()
