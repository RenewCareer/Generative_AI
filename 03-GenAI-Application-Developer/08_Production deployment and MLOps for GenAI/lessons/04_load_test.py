"""Lesson 4: load test a real HTTP server, and read the percentiles, not the average.

Starts the service on a local port. The mock model sleeps 50 ms to imitate a provider, so
these numbers show this service's overhead on this machine, not a real model's speed.

Run: python lessons/04_load_test.py
"""

import logging
import socket
import statistics
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from genai_kit import MockClient, load_course_chunks  # noqa: E402
from project.main import create_app  # noqa: E402


class SlowMock(MockClient):
    def complete(self, *args, **kwargs):
        time.sleep(0.05)
        return super().complete(*args, **kwargs)


def percentile(values: list[float], share: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * share))]


def run_level(url: str, concurrency: int, total: int) -> dict:
    payload = {"question": "What is the hotel limit per night?"}
    headers = {"X-API-Key": "demo"}

    with httpx.Client(timeout=30) as client:
        def one(_: int) -> tuple[int, float]:
            start = time.perf_counter()
            status = client.post(f"{url}/v1/ask", json=payload, headers=headers).status_code
            return status, (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=concurrency) as pool:
            results = list(pool.map(one, range(total)))
        elapsed = time.perf_counter() - start

    latencies = [ms for _, ms in results]
    return {
        "rps": total / elapsed,
        "p50": statistics.median(latencies),
        "p95": percentile(latencies, 0.95),
        "errors": sum(status != 200 for status, _ in results),
    }


def main() -> None:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]

    app = create_app(SlowMock(), load_course_chunks(), api_keys={"demo"})
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="critical"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.05)
    logging.disable(logging.CRITICAL)  # Keep the classroom output readable.

    url = f"http://127.0.0.1:{port}"
    print(f"{'concurrent':>11}{'req/s':>9}{'p50 ms':>10}{'p95 ms':>10}{'errors':>8}")
    for concurrency in (1, 5, 20):
        result = run_level(url, concurrency, total=60)
        print(f"{concurrency:>11}{result['rps']:>9.1f}{result['p50']:>10.0f}{result['p95']:>10.0f}{result['errors']:>8}")

    server.should_exit = True
    thread.join(timeout=5)
    print("\nWatch p95 as concurrency grows: that is what your slowest users feel. Also test")
    print("streaming and retries, and watch provider rate limits, which usually hit you first.")


if __name__ == "__main__":
    main()
