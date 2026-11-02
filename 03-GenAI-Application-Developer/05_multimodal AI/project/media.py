"""Provider calls for images and audio. Offline, each one returns a clearly marked stand-in.

Model names come from the environment, because these change more often than anything else.
"""

from __future__ import annotations

import base64
import io
import json
import math
import os
import struct
import wave
from pathlib import Path
from typing import TypeVar

from PIL import Image, ImageDraw
from pydantic import BaseModel

from genai_kit import get_settings

T = TypeVar("T", bound=BaseModel)


def encode_image(path: str | Path, max_side: int = 1024) -> tuple[str, str]:
    """Resize and base64-encode an image. Bigger images cost more and are often no better."""
    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail((max_side, max_side))
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=85)
    return "image/jpeg", base64.b64encode(buffer.getvalue()).decode("ascii")


def openai_vision_input(prompt: str, media_type: str, data: str) -> list[dict]:
    return [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:{media_type};base64,{data}"},
            ],
        }
    ]


def anthropic_vision_content(prompt: str, media_type: str, data: str) -> list[dict]:
    return [
        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": data}},
        {"type": "text", "text": prompt},
    ]


def extract_from_image(path: str | Path, prompt: str, schema: type[T], client=None) -> T:
    """Send an image with a prompt, and get validated structured data back."""
    settings = get_settings()
    media_type, data = encode_image(path)

    if settings.provider == "openai":
        from openai import OpenAI

        client = client or OpenAI(api_key=settings.openai_api_key, timeout=settings.request_timeout_s)
        response = client.responses.parse(
            model=os.getenv("OPENAI_VISION_MODEL", settings.openai_model),
            input=openai_vision_input(prompt, media_type, data),
            text_format=schema,
        )
        if response.output_parsed is None:
            raise ValueError("The model did not return data matching the schema.")
        return response.output_parsed

    if settings.provider == "anthropic":
        from anthropic import Anthropic

        client = client or Anthropic(api_key=settings.anthropic_api_key, timeout=settings.request_timeout_s)
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1024,
            messages=[{"role": "user", "content": anthropic_vision_content(prompt, media_type, data)}],
            tools=[{"name": "record", "description": "Record the data.", "input_schema": schema.model_json_schema()}],
            tool_choice={"type": "tool", "name": "record"},
        )
        return schema.model_validate(next(block.input for block in response.content if block.type == "tool_use"))

    # Mock: read the values from a sidecar file instead of looking at the image.
    sidecar = Path(path).with_suffix(".mock.json")
    if not sidecar.exists():
        raise FileNotFoundError(f"Mock mode needs {sidecar.name}, or set an API key for real vision.")
    return schema.model_validate(json.loads(sidecar.read_text(encoding="utf-8")))


def generate_image(prompt: str, output: Path, client=None) -> Path:
    settings = get_settings()
    output.parent.mkdir(parents=True, exist_ok=True)
    if settings.provider == "openai":
        from openai import OpenAI

        client = client or OpenAI(api_key=settings.openai_api_key, timeout=120)
        response = client.images.generate(
            model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1"), prompt=prompt, size="1024x1024"
        )
        output.write_bytes(base64.b64decode(response.data[0].b64_json))
        return output

    # Mock, and also Claude, which does not generate images: draw a labelled placeholder.
    image = Image.new("RGB", (640, 360), "#1f2a44")
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 624, 344), outline="#5eead4", width=3)
    draw.text((36, 40), "PLACEHOLDER: NOT AI GENERATED", fill="#5eead4", font_size=24)
    draw.text((36, 110), f"Prompt: {prompt[:60]}", fill="white", font_size=16)
    draw.text((36, 140), prompt[60:120], fill="white", font_size=16)
    image.save(output)
    return output


def write_test_tone(path: Path, seconds: float = 1.0, rate: int = 16_000) -> Path:
    """Write a real WAV file, so the audio plumbing can run with no recording."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(
            b"".join(
                struct.pack("<h", int(12_000 * math.sin(2 * math.pi * 440 * n / rate)))
                for n in range(int(rate * seconds))
            )
        )
    return path


def transcribe(path: Path, client=None) -> str:
    settings = get_settings()
    if settings.provider == "openai":
        from openai import OpenAI

        client = client or OpenAI(api_key=settings.openai_api_key, timeout=120)
        with path.open("rb") as handle:
            return client.audio.transcriptions.create(
                model=os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe"), file=handle
            ).text
    with wave.open(str(path), "rb") as handle:
        seconds = handle.getnframes() / handle.getframerate()
    return f"[mock transcript of a {seconds:.1f} second recording] My order A-1002 has not arrived yet."


def synthesize_speech(text: str, output: Path, client=None) -> Path:
    settings = get_settings()
    output.parent.mkdir(parents=True, exist_ok=True)
    if settings.provider == "openai":
        from openai import OpenAI

        client = client or OpenAI(api_key=settings.openai_api_key, timeout=120)
        response = client.audio.speech.create(
            model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
            voice="alloy",
            input=text,
            response_format="wav",
        )
        output.write_bytes(response.content)
        return output
    # Mock: a tone whose length follows the text, not speech.
    return write_test_tone(output, seconds=min(5.0, 0.05 * len(text)))
