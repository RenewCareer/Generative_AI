"""Run every test suite and every lesson in offline mode. Exit code 0 means all is well.

Run: python scripts/check_all.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAG = "03_ Data ingestion and RAG"
UNITS = [
    "01_GenAI Application foundations",
    "02_LLM Applications Engineering",
    f"{RAG}/01_data Ingestion",
    f"{RAG}/02_Document_processing_chunking",
    f"{RAG}/03_embedding_vector_search",
    f"{RAG}/04_building_rag_application",
    f"{RAG}/05_advnced_retrieval_evaluation",
    f"{RAG}/06_production-grade_RAG",
    "04_Tool Calling and AI Agents",
    "05_multimodal AI",
    "06_Backend Application interfaces",
    "07_Evaluations security and reliability",
    "08_Production deployment and MLOps for GenAI",
]
# Example applications, run non-interactively: (unit index, arguments)
APPS = [
    (0, ["project/study_buddy.py", "--question", "What is a token?"]),
    (1, ["project/review_analyzer.py"]),
    (2, ["project/ingest.py", "--state", "output/check_all_kb"]),
    (3, ["main.py"]),
    (4, ["project/faq_search.py", "build"]),
    (4, ["project/faq_search.py", "search", "warranty on electronics"]),
    (5, ["project/policy_assistant.py", "--question", "How many days do customers have to return an item?"]),
    (6, ["project/benchmark.py"]),
    (8, ["project/helpdesk_agent.py", "--message", "Where is my order A-1002?"]),
    (9, ["project/expense_assistant.py"]),
    (11, ["project/assistant.py", "--question", "What is the hotel limit per night?"]),
    (11, ["project/evaluate.py"]),
]


def run(command: list[str], cwd: Path) -> tuple[bool, str]:
    environment = {
        **os.environ,
        "LLM_PROVIDER": "mock",  # Never spend real money during a check.
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "PYTHONIOENCODING": "utf-8",
    }
    process = subprocess.run(
        [sys.executable, *command],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    return process.returncode == 0, process.stdout + process.stderr


def main() -> int:
    failures: list[tuple[str, str]] = []
    passed = 0

    def check(label: str, command: list[str], cwd: Path) -> None:
        nonlocal passed
        start = time.perf_counter()
        ok, output = run(command, cwd)
        print(f"  {'ok  ' if ok else 'FAIL'} {label} ({time.perf_counter() - start:.1f}s)", flush=True)
        if ok:
            passed += 1
        else:
            failures.append((label, output))

    print("Shared kit")
    check("genai_kit tests", ["-m", "pytest", "tests"], ROOT)

    for index, unit in enumerate(UNITS):
        print(unit)
        directory = ROOT / unit
        check("tests", ["-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"], directory)
        for lesson in sorted((directory / "lessons").glob("*.py")):
            check(lesson.name, [str(lesson.relative_to(directory))], directory)
        for app_index, arguments in APPS:
            if app_index == index:
                check(" ".join(arguments[:2]), arguments, directory)

    print(f"\n{passed} checks passed, {len(failures)} failed.")
    for label, output in failures:
        print(f"\n===== {label} =====\n{output[-2500:]}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
