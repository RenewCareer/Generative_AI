"""Pull JSON out of model text.

This is the Phase 1 approach: ask for JSON in the prompt, then parse defensively.
It works most of the time — and "most of the time" is exactly why Week 4 replaces
it with schema-constrained Structured Outputs + Pydantic.
"""
from __future__ import annotations

import json
import re
from typing import Any

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(text: str) -> Any:
    """Parse JSON from raw model output, tolerating ```json fences and chatter
    around the payload. Raises ValueError if nothing parseable is found."""
    candidates = [text.strip()]
    candidates += [m.strip() for m in _FENCE.findall(text)]
    # Fallback: the outermost {...} or [...] span.
    for open_, close in (("{", "}"), ("[", "]")):
        start, end = text.find(open_), text.rfind(close)
        if start != -1 and end > start:
            candidates.append(text[start : end + 1])
    for c in candidates:
        try:
            return json.loads(c)
        except json.JSONDecodeError:
            continue
    raise ValueError(f"No valid JSON found in model output:\n{text[:500]}")
