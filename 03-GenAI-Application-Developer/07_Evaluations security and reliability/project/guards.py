"""Input and output guardrails. Each returns a verdict that the application can act on."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

INJECTION_PATTERNS = {
    "override": r"\b(ignore|disregard|forget|override)\b.{0,30}\b(previous|prior|above|earlier|system|your)\b.{0,20}\b(instructions?|rules?|prompts?|guidelines?)\b",
    "prompt_extraction": r"\b(reveal|show|print|repeat|tell me|what (is|are))\b.{0,30}\b(system prompt|hidden (prompt|instructions)|your instructions)\b",
    "role_hijack": r"\b(you are now|pretend (to be|you are)|act as)\b.{0,40}\b(unrestricted|no rules|dan|jailbroken|without (any )?(rules|restrictions))\b",
    "fake_delimiter": r"<\s*/?\s*(system|instructions?)\s*>|\[\s*/?\s*system\s*\]",
}
PII_PATTERNS = {
    "EMAIL": r"[\w.+-]+@[\w-]+\.[\w.-]+",
    "CARD": r"\b(?:\d[ -]?){13,19}\b",
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    # The lookarounds stop this from matching a slice of a longer digit sequence.
    "PHONE": r"(?<![\w-])(?<!\d[ .-])\+?\d{1,3}[ .-]?\(?\d{2,4}\)?[ .-]?\d{3,4}[ .-]?\d{3,4}\b(?![ .-]?\d)",
}
SECRET_PATTERNS = {
    "api_key": r"\b(sk|pk|rk)-[A-Za-z0-9_-]{16,}\b",
    "aws_key": r"\bAKIA[0-9A-Z]{16}\b",
    "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
}
ALLOWED_DOMAINS = {"acme.example"}


@dataclass
class Verdict:
    allowed: bool
    reasons: list[str] = field(default_factory=list)
    text: str = ""


def normalize(text: str) -> str:
    """Defeat simple evasion: full-width characters, zero-width characters, extra spacing."""
    text = unicodedata.normalize("NFKC", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Cf")
    return re.sub(r"\s+", " ", text)


def luhn_valid(digits: str) -> bool:
    """Card numbers have a check digit. This avoids redacting ordinary long numbers."""
    total = 0
    for index, char in enumerate(reversed(digits)):
        value = int(char)
        if index % 2:
            value = value * 2 - 9 if value > 4 else value * 2
        total += value
    return total % 10 == 0


def redact_pii(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}

    def replace(kind: str):
        def inner(match: re.Match) -> str:
            if kind == "CARD" and not luhn_valid(re.sub(r"\D", "", match.group())):
                return match.group()
            counts[kind] = counts.get(kind, 0) + 1
            return f"[{kind}]"

        return inner

    for kind, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, replace(kind), text)
    return text, counts


def check_input(text: str, max_chars: int = 4000) -> Verdict:
    if not text.strip():
        return Verdict(False, ["empty_input"])
    if len(text) > max_chars:
        return Verdict(False, ["too_long"])
    normalized = normalize(text)
    reasons = [f"injection:{name}" for name, pattern in INJECTION_PATTERNS.items() if re.search(pattern, normalized, re.I)]
    if reasons:
        return Verdict(False, reasons)
    # Redact before sending to the provider or writing to logs.
    redacted, counts = redact_pii(text)
    return Verdict(True, [f"redacted:{kind}" for kind in counts], redacted)


def check_output(text: str, canary: str | None = None) -> Verdict:
    reasons: list[str] = []
    if canary and canary in text:
        reasons.append("system_prompt_leak")
    reasons.extend(f"secret:{name}" for name, pattern in SECRET_PATTERNS.items() if re.search(pattern, text))
    for domain in re.findall(r"https?://([\w.-]+)", text):
        if not any(domain == allowed or domain.endswith("." + allowed) for allowed in ALLOWED_DOMAINS):
            reasons.append(f"untrusted_link:{domain}")
    if reasons:
        return Verdict(False, reasons)
    redacted, counts = redact_pii(text)
    return Verdict(True, [f"redacted:{kind}" for kind in counts], redacted)
