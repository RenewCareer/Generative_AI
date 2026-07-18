"""
Advanced example: a miniature "Responsible AI" guardrail pipeline around a
real Anthropic API call.

Requires: anthropic (see requirements.txt) and an ANTHROPIC_API_KEY
environment variable (same as sub-topics 1.1 and 1.3).

This combines every idea from this sub-topic into one pipeline, mirroring
(at toy scale) what a real production GenAI application does before
showing a user any model output:

  1. Scan the USER'S INPUT for PII before it's ever sent to the model --
     the earliest point you can catch a privacy leak.
  2. Send a (redacted) prompt to Claude.
  3. Scan the MODEL'S OUTPUT for biased/exclusionary language.
  4. Scan the MODEL'S OUTPUT for PII the model might have generated.
  5. Fact-check specific, checkable claims in the output against a small
     trusted knowledge base.
  6. Print a single consolidated report.

Run it with:
    python 03_advanced_responsible_ai_pipeline.py
"""

import os
import re
import sys

import anthropic

MODEL = "claude-opus-4-8"

# Reuse the same flagged-terms idea from script 01 (trimmed for this demo).
FLAGGED_TERMS = {
    "ninja": "gender-coded (masculine-coded)",
    "rockstar": "gender-coded (masculine-coded)",
    "guys": "gendered group term",
    "young and energetic": "age discrimination risk",
    "digital native": "age discrimination risk",
    "crazy fast": "ableist / mental-health-stigmatizing",
}

# Reuse the same extract-then-verify idea from script 02.
KNOWLEDGE_BASE = {
    "eiffel_tower_completion_year": "1889",
    "python_first_release_year": "1991",
}

EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b")


def scan_bias(text: str) -> list[str]:
    text_lower = text.lower()
    return [term for term in FLAGGED_TERMS if term in text_lower]


def scan_pii(text: str) -> dict[str, list[str]]:
    return {
        "emails": EMAIL_PATTERN.findall(text),
        "phone_numbers": PHONE_PATTERN.findall(text),
    }


def redact_pii(text: str) -> str:
    text = EMAIL_PATTERN.sub("[REDACTED EMAIL]", text)
    text = PHONE_PATTERN.sub("[REDACTED PHONE]", text)
    return text


def fact_check(text: str, knowledge_base: dict[str, str]) -> dict[str, bool]:
    """For each fact in the knowledge base, check whether its trusted
    value literally appears in the text. This is a simplified version of
    script 02's extract-then-verify -- here we check PRESENCE of the
    correct value rather than extracting and comparing a specific claimed
    value, since we don't control the model's exact phrasing."""
    return {fact_key: (true_value in text) for fact_key, true_value in knowledge_base.items()}


def print_report(title: str, lines: list[str]) -> None:
    print(f"\n--- {title} ---")
    if not lines:
        print("  (none found)")
    else:
        for line in lines:
            print(f"  - {line}")


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: Set the ANTHROPIC_API_KEY environment variable first.")
        sys.exit(1)

    client = anthropic.Anthropic()

    # -----------------------------------------------------------------
    # Step 1: scan the USER'S raw input for PII before it's sent anywhere.
    # -----------------------------------------------------------------
    raw_user_input = (
        "Hi, I'm researching famous landmarks and early programming "
        "languages for a report. My contact is jane.doe@example.com or "
        "555-123-4567 if you need to follow up. Can you tell me, in two "
        "short sentences, the year the Eiffel Tower was completed and the "
        "year Python was first released to the public?"
    )

    print("=" * 70)
    print("STEP 1: Scan user input for PII before sending anything to the model")
    print("=" * 70)
    input_pii = scan_pii(raw_user_input)
    print_report("PII found in user input", input_pii["emails"] + input_pii["phone_numbers"])

    redacted_input = redact_pii(raw_user_input)
    print(f"\nRedacted prompt that will actually be sent:\n  {redacted_input!r}")

    # -----------------------------------------------------------------
    # Step 2: send the redacted prompt to Claude.
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 2: Send redacted prompt to Claude")
    print("=" * 70)
    response = client.messages.create(
        model=MODEL,
        max_tokens=150,
        messages=[{"role": "user", "content": redacted_input}],
    )
    model_output = next(block.text for block in response.content if block.type == "text")
    print(f"\nModel response:\n  {model_output}")

    # -----------------------------------------------------------------
    # Step 3-5: run the model's OUTPUT through the guardrail checks.
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("STEP 3-5: Guardrail checks on the model's response")
    print("=" * 70)

    bias_hits = scan_bias(model_output)
    print_report("Flagged bias/exclusionary terms", bias_hits)

    output_pii = scan_pii(model_output)
    print_report("PII found in model output", output_pii["emails"] + output_pii["phone_numbers"])

    fact_results = fact_check(model_output, KNOWLEDGE_BASE)
    fact_lines = [
        f"{fact_key}: {'confirmed present' if found else 'NOT found -- verify before trusting'}"
        for fact_key, found in fact_results.items()
    ]
    print_report("Fact check against trusted knowledge base", fact_lines)

    # -----------------------------------------------------------------
    # Step 6: consolidated report.
    # -----------------------------------------------------------------
    print("\n" + "=" * 70)
    print("RESPONSIBLE AI REPORT")
    print("=" * 70)
    all_clear = not bias_hits and not output_pii["emails"] and not output_pii["phone_numbers"]
    facts_confirmed = sum(fact_results.values())
    print(f"  Bias terms flagged:        {len(bias_hits)}")
    print(f"  PII found in output:       {len(output_pii['emails']) + len(output_pii['phone_numbers'])}")
    print(f"  Facts confirmed:           {facts_confirmed}/{len(KNOWLEDGE_BASE)}")
    print(f"  Overall:                   {'PASS' if all_clear else 'REVIEW RECOMMENDED'}")
    print(
        "\nThis is a TOY pipeline -- real production guardrail systems use\n"
        "far more sophisticated bias classifiers, PII detectors (often\n"
        "trained models, not just regex), and grounding via retrieval\n"
        "(Track 3) rather than a hand-maintained knowledge base. But the\n"
        "SHAPE of the pipeline -- check input, check output, check facts,\n"
        "report before trusting -- is exactly what production systems do."
    )


if __name__ == "__main__":
    main()
