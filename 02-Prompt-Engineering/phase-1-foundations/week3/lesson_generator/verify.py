"""Deterministic verification of a generated lesson.

These rules are what "consistent" means for this product. They run in
milliseconds, cost nothing, and never disagree with themselves — so they run
first, and the (expensive, fuzzier) LLM critic only judges what code can't.
"""
from __future__ import annotations

import re

from ..readability import analyze
from .prompts import SECTIONS

MIN_WORDS, MAX_WORDS = 300, 750
MIN_FLESCH = 55
MAX_AVG_SENTENCE = 18


def split_sections(md: str) -> dict[str, str]:
    parts = re.split(r"^##\s+(.+?)\s*$", md, flags=re.MULTILINE)
    # parts = [preamble, heading1, body1, heading2, body2, ...]
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def verify_lesson(md: str, plan: dict) -> list[str]:
    issues: list[str] = []

    if not re.match(r"^#\s+\S", md.lstrip()):
        issues.append("The lesson must start with a '# Title' line.")

    sections = split_sections(md)
    headings = list(sections)
    if headings != SECTIONS:
        missing = [s for s in SECTIONS if s not in sections]
        extra = [h for h in headings if h not in SECTIONS]
        detail = []
        if missing:
            detail.append(f"missing {missing}")
        if extra:
            detail.append(f"unexpected {extra}")
        if not missing and not extra:
            detail.append("wrong order")
        issues.append(f"Section headings must be exactly {SECTIONS} in order: {'; '.join(detail)}.")

    learn = sections.get("What you'll learn", "")
    n_obj = len(re.findall(r"^\s*[-*]\s+", learn, flags=re.MULTILINE))
    if learn and n_obj != 3:
        issues.append(f"'What you'll learn' must have exactly 3 bullet points (has {n_obj}).")

    quiz = sections.get("Quick check", "")
    n_q = len([ln for ln in quiz.splitlines() if ln.strip().endswith("?")])
    if quiz and n_q != 3:
        issues.append(f"'Quick check' must have exactly 3 questions ending with '?' (has {n_q}).")

    r = analyze(md)
    if not MIN_WORDS <= r.words <= MAX_WORDS:
        issues.append(f"Length is {r.words} words; must be {MIN_WORDS}-{MAX_WORDS}.")
    if r.flesch < MIN_FLESCH:
        issues.append(f"Reading ease {r.flesch} is below {MIN_FLESCH}: use shorter sentences "
                      "and simpler words.")
    if r.avg_sentence_len > MAX_AVG_SENTENCE:
        issues.append(f"Average sentence length {r.avg_sentence_len} words; keep it under "
                      f"{MAX_AVG_SENTENCE}.")

    for kt in plan.get("key_terms", []):
        term = kt.get("term", "") if isinstance(kt, dict) else str(kt)
        if term and term.lower() not in md.lower():
            issues.append(f"Key term '{term}' from the plan is never explained.")

    return issues


def verify_plan(plan: object) -> list[str]:
    if not isinstance(plan, dict):
        return ["Plan is not a JSON object."]
    issues = []
    for key in ("title", "objectives", "key_terms", "analogy", "example", "exercise"):
        if not plan.get(key):
            issues.append(f"Plan is missing '{key}'.")
    if isinstance(plan.get("objectives"), list) and len(plan["objectives"]) != 3:
        issues.append(f"Plan must have exactly 3 objectives (has {len(plan['objectives'])}).")
    return issues
