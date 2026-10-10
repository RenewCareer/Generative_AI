"""Deterministic output checks — cheap, fast, repeatable "unit tests" for prompts.

Each check takes (output, spec) and returns (passed, detail). A spec is a dict
from a template's TOML, e.g. {type = "max_words", value = 50}.

Deterministic checks can't judge "is this a good explanation?" (Week 3 uses an
LLM critic for that; Week 6 formalises evaluation). But they catch the failures
that break software: wrong format, wrong label, too long, forbidden content.
"""
from __future__ import annotations

import json
import re
from typing import Callable

from ai_core.jsonutil import extract_json

Result = tuple[bool, str]


def _words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _lines(text: str) -> list[str]:
    return [ln for ln in text.strip().splitlines() if ln.strip()]


def _json(text: str):
    try:
        return extract_json(text)
    except ValueError:
        return None


def _norm(s: str) -> str:
    return s.strip().strip(".!\"'`").lower()


def max_words(out: str, s: dict) -> Result:
    n = _words(out)
    return n <= s["value"], f"{n} words (max {s['value']})"


def min_words(out: str, s: dict) -> Result:
    n = _words(out)
    return n >= s["value"], f"{n} words (min {s['value']})"


def max_lines(out: str, s: dict) -> Result:
    n = len(_lines(out))
    return n <= s["value"], f"{n} non-empty lines (max {s['value']})"


def line_count(out: str, s: dict) -> Result:
    n = len(_lines(out))
    return n == s["value"], f"{n} non-empty lines (expected {s['value']})"


def contains_all(out: str, s: dict) -> Result:
    missing = [v for v in s["value"] if v.lower() not in out.lower()]
    return not missing, f"missing {missing}" if missing else "all present"


def contains_any(out: str, s: dict) -> Result:
    hit = [v for v in s["value"] if v.lower() in out.lower()]
    return bool(hit), f"found {hit}" if hit else f"none of {s['value']}"


def contains_none(out: str, s: dict) -> Result:
    hit = [v for v in s["value"] if v.lower() in out.lower()]
    return not hit, f"forbidden {hit}" if hit else "clean"


def regex(out: str, s: dict) -> Result:
    ok = re.search(s["value"], out, re.MULTILINE | re.IGNORECASE) is not None
    return ok, f"/{s['value']}/ {'matched' if ok else 'not found'}"


def one_of(out: str, s: dict) -> Result:
    v = _norm(out)
    return v in [x.lower() for x in s["value"]], f"got {v!r}"


def equals(out: str, s: dict) -> Result:
    return _norm(out) == _norm(s["value"]), f"got {_norm(out)!r}, expected {_norm(s['value'])!r}"


def json_valid(out: str, s: dict) -> Result:
    # Strict: the whole output must be JSON (fences allowed). Chatter = fail,
    # because code consuming this would have to clean it up.
    stripped = re.sub(r"^```(?:json)?\s*|\s*```$", "", out.strip())
    try:
        json.loads(stripped)
        return True, "valid JSON"
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e.msg}"


def json_keys(out: str, s: dict) -> Result:
    data = _json(out)
    if not isinstance(data, dict):
        return False, "not a JSON object"
    missing = [k for k in s["value"] if k not in data]
    return not missing, f"missing keys {missing}" if missing else "all keys present"


def json_array_len(out: str, s: dict) -> Result:
    data = _json(out)
    if isinstance(data, dict) and s.get("key"):
        data = data.get(s["key"])
    if not isinstance(data, list):
        return False, "not a JSON array"
    lo, hi = s.get("min", 0), s.get("max", 10**9)
    return lo <= len(data) <= hi, f"{len(data)} items (expected {lo}..{hi})"


def ends_with_question(out: str, s: dict) -> Result:
    lines = _lines(out)
    qs = [ln for ln in lines if ln.rstrip().endswith("?")]
    need = s.get("min", 1)
    return len(qs) >= need, f"{len(qs)} question lines (min {need})"


CHECKS: dict[str, Callable[[str, dict], Result]] = {
    f.__name__: f for f in (
        max_words, min_words, max_lines, line_count, contains_all, contains_any,
        contains_none, regex, one_of, equals, json_valid, json_keys, json_array_len,
        ends_with_question,
    )
}


def run_check(output: str, spec: dict) -> Result:
    fn = CHECKS.get(spec["type"])
    if fn is None:
        raise KeyError(f"Unknown check type {spec['type']!r}. Known: {sorted(CHECKS)}")
    return fn(output, spec)
