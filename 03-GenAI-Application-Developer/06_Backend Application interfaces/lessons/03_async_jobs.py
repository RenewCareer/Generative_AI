"""Lesson 3: long tasks use the job pattern: 202 Accepted, then poll for the result.

Run: python lessons/03_async_jobs.py
"""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient  # noqa: E402
from project.main import create_app  # noqa: E402

KEY = {"X-API-Key": "demo"}


def main() -> None:
    llm = MockClient(lambda messages, system, tools: "- Point one\n- Point two\n- Point three")
    client = TestClient(create_app(llm, api_keys={"demo"}))

    created = client.post("/v1/jobs/summarize", json={"text": "A very long report..."}, headers=KEY)
    job = created.json()
    print(f"POST /v1/jobs/summarize -> HTTP {created.status_code}: {job['status']}")

    # The test client finishes background tasks before returning. Real clients poll with a delay.
    polled = client.get(f"/v1/jobs/{job['id']}", headers=KEY).json()
    print(f"GET  /v1/jobs/<id>      -> {polled['status']}\n{polled['result']}\n")

    print("BackgroundTasks runs in this process, so jobs vanish on restart. Production systems use")
    print("a durable queue and worker (Celery, RQ, SQS, Temporal), and store job state in a database.")


if __name__ == "__main__":
    main()
