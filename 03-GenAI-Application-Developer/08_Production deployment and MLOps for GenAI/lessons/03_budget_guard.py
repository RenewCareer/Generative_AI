"""Lesson 3: a hard spending limit, because LLM bills scale with traffic and with bugs.

Run: python lessons/03_budget_guard.py
"""

import logging
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient, load_course_chunks  # noqa: E402
from project.main import create_app  # noqa: E402
from project.release import BudgetGuard  # noqa: E402

KEY = {"X-API-Key": "demo"}


def main() -> None:
    # An unrealistically small budget and example prices, so that the limit is reached quickly.
    budget = BudgetGuard(daily_limit_usd=0.0002, input_per_m=0.40, output_per_m=1.60)
    app = create_app(MockClient(), load_course_chunks(), budget=budget, api_keys={"demo"})

    with TestClient(app) as client:
        logging.disable(logging.CRITICAL)  # Keep the classroom output readable.
        for number in range(1, 7):
            response = client.post("/v1/ask", json={"question": "What is the hotel limit per night?"}, headers=KEY)
            print(f"Request {number}: HTTP {response.status_code}, spent ${budget.spent_usd:.6f} of ${budget.daily_limit_usd}")
            if response.status_code != 200:
                print(f"  {response.json()['detail']}")
                break
        logging.disable(logging.NOTSET)

    print("\nA stopped service is annoying. A runaway bill can be far worse. In production, alert at")
    print("50% and 80%, keep the counter in a shared store such as Redis so all replicas see it,")
    print("and set per-user limits too.")


if __name__ == "__main__":
    main()
