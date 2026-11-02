"""Lesson 2: generating images, with a prompt structure that gives consistent results.

Offline, or with Claude (which does not generate images), this draws a labelled placeholder.

Run: python lessons/02_image_generation.py
"""

import sys
from pathlib import Path

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT))

from genai_kit import get_settings  # noqa: E402
from project.media import generate_image  # noqa: E402


def build_prompt(subject: str, setting: str, style: str, details: str) -> str:
    """Subject, setting, style and details: a structure you can vary one part at a time."""
    return f"{subject}, {setting}. Style: {style}. Details: {details}."


def main() -> None:
    prompt = build_prompt(
        subject="A pair of teal wireless headphones",
        setting="on a clean white desk beside a notebook",
        style="soft natural light, product photography",
        details="no text, no logos, no people",
    )
    print(f"Prompt: {prompt}")
    path = generate_image(prompt, UNIT / "output" / "generated_product.png")
    print(f"Saved : {path}")
    if get_settings().provider != "openai":
        print("Note  : this is a placeholder image. Set an OpenAI key to generate a real one.")

    print("\nProduction checklist: moderate prompts, keep rights and consent in mind, label AI")
    print("images where required, store the prompt with the output, and have people review")
    print("anything that will be published.")


if __name__ == "__main__":
    main()
