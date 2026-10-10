"""Week 3 PRACTICAL — AI lesson generator.

    python -m week3.lesson_generator "What is an API?"
    python -m week3.lesson_generator "How Wi-Fi works" --audience "secondary school students"
    python -m week3.lesson_generator --batch week3/lesson_generator/topics.txt

Writes output/<slug>.md and output/<slug>.report.json. --batch prints a
consistency table across topics — the real test of "consistent lessons".
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from ai_core import Assistant, AssistantError, MissingAPIKeyError

from .pipeline import LessonResult, generate_lesson

OUT = Path("output")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def save(result: LessonResult) -> Path:
    OUT.mkdir(exist_ok=True)
    path = OUT / f"{slugify(result.topic)}.md"
    path.write_text(result.markdown, encoding="utf-8")
    path.with_suffix(".report.json").write_text(
        json.dumps(result.report(), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("topic", nargs="?")
    p.add_argument("--audience", default="complete beginners")
    p.add_argument("--batch", type=Path, help="file with one topic per line")
    p.add_argument("--model")
    p.add_argument("--max-revisions", type=int, default=2)
    args = p.parse_args()

    if args.batch:
        topics = [t.strip() for t in args.batch.read_text(encoding="utf-8").splitlines() if t.strip()]
    elif args.topic:
        topics = [args.topic]
    else:
        p.error("give a topic or --batch FILE")

    try:
        bot = Assistant(model=args.model, remember_history=False, log_path="logs/lesson_generator.jsonl")
    except MissingAPIKeyError as e:
        raise SystemExit(str(e))

    results: list[LessonResult] = []
    for topic in topics:
        before = bot.usage.cost_usd
        try:
            result = generate_lesson(topic, args.audience, bot=bot, max_revisions=args.max_revisions)
        except AssistantError as e:
            print(f"!! {topic}: {e}")
            continue
        print(f"   saved {save(result)}  (${bot.usage.cost_usd - before:.4f})\n")
        results.append(result)

    if len(results) > 1:
        print(f"{'topic':<34}{'rounds':>7}{'words':>7}{'flesch':>8}{'result':>9}")
        for r in results:
            last = r.rounds[-1]
            print(f"{r.topic[:33]:<34}{len(r.rounds):>7}{last.words:>7}{last.flesch:>8}"
                  f"{'PASS' if r.passed else 'REVIEW':>9}")
        n_pass = sum(r.passed for r in results)
        print(f"\n{n_pass}/{len(results)} passed first-time-or-after-revision | {bot.usage}")


if __name__ == "__main__":
    main()
