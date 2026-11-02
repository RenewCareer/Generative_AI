"""Lesson 2: turn free text into validated data, and recover when validation fails.

Native structured output is the first choice. The repair loop here is the fallback for
business rules that a JSON schema cannot express, or models without schema support.

Run: python lessons/02_structured_output.py
"""

import json
from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, field_validator


class TicketTriage(BaseModel):
    category: Literal["billing", "shipping", "technical", "other"]
    priority: int = Field(ge=1, le=3, description="1 is the most urgent")
    summary: str = Field(max_length=120)

    @field_validator("summary")
    @classmethod
    def summary_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("summary must not be blank")
        return value


def parse_with_repair(generate: Callable[[str | None], str], attempts: int = 3) -> TicketTriage:
    """Call the model, validate, and feed any validation error back so it can self-correct."""
    feedback = None
    for attempt in range(1, attempts + 1):
        raw = generate(feedback)
        try:
            result = TicketTriage.model_validate_json(raw)
            print(f"  attempt {attempt}: valid")
            return result
        except ValidationError as error:
            feedback = f"Your last output was invalid: {error.errors(include_url=False)}. Return only JSON."
            print(f"  attempt {attempt}: rejected, {len(error.errors())} error(s) fed back to the model")
    raise ValueError(f"No valid output after {attempts} attempts")


def main() -> None:
    print("The JSON schema we give to the model:")
    print(json.dumps(TicketTriage.model_json_schema()["properties"]["category"], indent=2), "\n")

    # A scripted model that makes realistic mistakes, then corrects itself.
    responses = iter(
        [
            '{"category": "urgent", "priority": 1, "summary": "Wi-Fi drops"}',
            '{"category": "technical", "priority": 9, "summary": "Wi-Fi drops"}',
            '{"category": "technical", "priority": 2, "summary": "Nimbus speaker keeps dropping Wi-Fi"}',
        ]
    )
    print("Repair loop:")
    triage = parse_with_repair(lambda feedback: next(responses))
    print(f"\nTyped result your code can trust:\n  {triage!r}")


if __name__ == "__main__":
    main()
