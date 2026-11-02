"""Lesson 1: see what your service is doing: structured logs and Prometheus metrics.

Run: python lessons/01_logs_and_metrics.py
"""

import logging
import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient, load_course_chunks  # noqa: E402
from project.main import create_app  # noqa: E402

KEY = {"X-API-Key": "demo"}


def main() -> None:
    app = create_app(MockClient(), load_course_chunks(), api_keys={"demo"})
    with TestClient(app) as client:
        print("STRUCTURED LOG LINES (each one can be searched and aggregated):")
        for number in range(3):
            client.post("/v1/ask", json={"question": "What is the hotel limit per night?", "user_id": f"user-{number}"}, headers=KEY)
        logging.shutdown()

        print("\nMETRICS, what Prometheus reads from /metrics:")
        for line in client.get("/metrics").text.splitlines():
            if line.startswith(("genai_requests_total", "genai_tokens_total", "genai_cost_usd_total{", "genai_budget")):
                print(f"  {line}")

    print("\nAlert on symptoms users feel: error rate, p95 latency, spend rate, and quality scores.")


if __name__ == "__main__":
    main()
