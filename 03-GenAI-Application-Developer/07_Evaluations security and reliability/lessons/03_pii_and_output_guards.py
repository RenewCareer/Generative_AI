"""Lesson 3: protect data on the way in and on the way out.

All personal details below are fake.

Run: python lessons/03_pii_and_output_guards.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from project.guards import check_output, redact_pii  # noqa: E402

INPUTS = [
    "Email me at sam.rivera@example.com about my order.",
    "My card is 4111 1111 1111 1111, please refund it.",
    "Order number 1234 5678 9012 3456 was late.",
    "My SSN is 123-45-6789 and phone is +1 415-555-0123.",
]
OUTPUTS = [
    "Refunds take 5 business days. See https://support.acme.example/refunds",
    "Claim your refund at https://acme-refunds.evil.example/login",
    "The key is sk-abcdefghijklmnop1234567890",
    "As instructed in ref-canary123, I will help.",
]


def main() -> None:
    print("INPUT REDACTION: before text reaches a provider or your logs")
    for text in INPUTS:
        redacted, counts = redact_pii(text)
        print(f"  {text}\n    -> {redacted}  {counts or ''}")
    print("  The third line passes the card pattern but fails its checksum, so it stays.\n")

    print("OUTPUT CHECKS: before text reaches the user")
    for text in OUTPUTS:
        verdict = check_output(text, canary="ref-canary123")
        print(f"  {'PASS ' if verdict.allowed else 'BLOCK'} {text}")
        if verdict.reasons:
            print(f"        {verdict.reasons}")

    print("\nRegex finds well-formed patterns only. It misses names and addresses, so production")
    print("systems add a dedicated PII service, such as Microsoft Presidio or a cloud DLP product.")


if __name__ == "__main__":
    main()
