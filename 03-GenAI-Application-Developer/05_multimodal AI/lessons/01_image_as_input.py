"""Lesson 1: how an image reaches a model, and why you resize it first.

Run: python lessons/01_image_as_input.py
"""

import json
import sys
from pathlib import Path

from PIL import Image

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT))

from project.expense_assistant import make_sample_receipt  # noqa: E402
from project.media import anthropic_vision_content, encode_image, openai_vision_input  # noqa: E402


def main() -> None:
    path = make_sample_receipt(UNIT / "output" / "sample_receipt.png")
    big = UNIT / "output" / "big_receipt.png"
    with Image.open(path) as image:
        image.resize((image.width * 8, image.height * 8)).save(big)

    print("Resizing keeps requests small:")
    for label, source, max_side in [("original small", path, 1024), ("large photo", big, 4096), ("large, resized", big, 1024)]:
        _, data = encode_image(source, max_side)
        print(f"  {label:<16} base64 payload {len(data) / 1024:>8.0f} KB")

    media_type, data = encode_image(path)
    short = data[:32] + "..."
    print("\nOpenAI Responses API, the request input:")
    print(json.dumps(openai_vision_input("Read this receipt.", media_type, short), indent=2))
    print("\nAnthropic Messages API, the message content:")
    print(json.dumps(anthropic_vision_content("Read this receipt.", media_type, short), indent=2))

    print("\nSame idea, different wire format. Providers also accept hosted image URLs or file IDs,")
    print("and they charge for images in tokens, so check each provider's image pricing.")


if __name__ == "__main__":
    main()
